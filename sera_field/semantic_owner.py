"""Human semantic alternatives and actual holonomy tags in the continuing field."""
import torch
from torch import nn

from .condensate import CondensateMemory
from .gauge import adjoint_rotations
from .inquiry_owner import InquiryOwner
from .learned_extension import StationaryCoupledField


def skew(vector):
    x, y, z = vector.unbind(-1); zero = x * 0
    return torch.stack((zero, -z, y, z, zero, -x, -y, x, zero), -1).reshape(*vector.shape[:-1], 3, 3)


def rotation(vector):
    theta = torch.linalg.vector_norm(vector, dim=-1)
    k = skew(vector)
    return (torch.eye(3, dtype=vector.dtype) + torch.sinc(theta / torch.pi)[..., None, None] * k +
            .5 * torch.sinc(theta / (2 * torch.pi)).square()[..., None, None] * (k @ k))


def curvature_tags(source, transport, epsilon):
    """Closed-loop holonomy, with each product based in its own vertex frame."""
    dynamic = transport[None] @ rotation(epsilon * source)
    tags, loops = [], []
    for start in range(source.shape[-2]):
        loop = torch.eye(3, dtype=source.dtype).expand(source.shape[0], 3, 3)
        for offset in range(source.shape[-2]):
            loop = dynamic[:, (start + offset) % source.shape[-2]] @ loop
        antisymmetric = .5 * (loop - loop.transpose(-1, -2))
        tags.append(torch.stack((antisymmetric[:, 2, 1], antisymmetric[:, 0, 2], antisymmetric[:, 1, 0]), -1))
        loops.append(loop)
    return torch.stack(tags, 1), torch.stack(loops, 1)


class CurvatureField(StationaryCoupledField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_curvature = nn.Parameter(torch.tensor(0.))
        self.raw_curvature_recall = nn.Parameter(torch.tensor(-2.))
        self.curvature_memory = CondensateMemory(self.nodes)
        self.curvature_preview = None
        self.last_curvature = None
        self.last_holonomy = None
        self.curvature_disconnected = False

    def imagine(self, source, previous=None, *, use_imagination=True):
        transport = adjoint_rotations(self.links).transpose(-1, -2)
        tag, holonomy = curvature_tags(source, transport, .05 + .25 * self.raw_curvature.sigmoid())
        self.last_curvature = tag.detach().clone(); self.last_holonomy = holonomy.detach().clone()
        recalled = self.curvature_memory.recall(tag, self.curvature_preview)
        gain = 0. if self.curvature_disconnected else .1 * self.raw_curvature_recall.sigmoid()
        return super().imagine(source + gain * recalled, previous, use_imagination=use_imagination)

    @torch.no_grad()
    def consolidate(self):
        return {'activation_region': self.memory.sleep(), 'curvature_region': self.curvature_memory.sleep()}


class SemanticOwner(InquiryOwner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        n, w = self.config['nodes'], self.config['width']
        self.field = CurvatureField(n, self.config['rounds'], backend=self.field.backend, steps=self.field.steps)
        self.semantic_observed = nn.Linear(w, n * 3)
        self.semantic_proposed = nn.Linear(4 * w, n * 3)
        self.semantic_branches = nn.Parameter(torch.randn(3, n, 3) * .03)
        self.semantic_readout = nn.Sequential(nn.Linear(n * 8 + n + 1, 64), nn.Tanh(), nn.Linear(64, 3))

    def specification(self):
        return {**super().specification(), 'type': 'curvature-semantic-015'}

    def semantic(self, premises, hypotheses, *, ablation=None):
        if len(premises) != len(hypotheses) or not premises:
            raise ValueError('Paired nonempty premise/hypothesis batches required')
        if ablation == 'hypothesis_only':
            premises = [''] * len(premises)
        p = self.encode_texts(premises); h = self.encode_texts(hypotheses)
        n = self.config['nodes']
        observed = self.semantic_observed(p).reshape(-1, n, 3).tanh()
        state, _ = self.field.imagine(observed)
        proposed = self.semantic_proposed(torch.cat((p, h, p * h, (p - h).abs()), -1)).reshape(-1, n, 3).tanh()
        batch = len(premises)
        source = (proposed[:, None] + .2 * self.semantic_branches.tanh()[None]).reshape(batch * 3, n, 3)
        previous = state[:, None].expand(-1, 3, -1, -1).reshape(batch * 3, n, 8)
        imagined, features = self.field.imagine(source, previous, use_imagination=ablation != 'no_imagination')
        logits = self.semantic_readout(torch.cat((imagined.flatten(1), features), -1)).reshape(batch, 3, 3)
        return logits


def extend_semantic(parent, seed=15115):
    torch.manual_seed(seed)
    spec = dict(parent.specification()); spec.pop('type')
    owner = SemanticOwner(**spec)
    result = owner.load_state_dict(parent.state_dict(), strict=False)
    allowed = ('semantic_', 'field.raw_curvature', 'field.curvature_memory.')
    if result.unexpected_keys or any(not k.startswith(allowed) for k in result.missing_keys):
        raise ValueError('Unexpected semantic parent incompatibility')
    return owner
