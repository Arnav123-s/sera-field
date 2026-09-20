"""Learned dynamics; no simulator, known force law or pretrained owner import."""

import copy
import hashlib
import json

import torch
from torch import nn

from .gauge import adjoint_rotations, encode, physical_invariants


def weight_hash(model):
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        digest.update(name.encode())
        if not isinstance(tensor, torch.Tensor):
            digest.update(b'canonical-extra-state:')
            digest.update(json.dumps(tensor,sort_keys=True,allow_nan=False).encode())
            continue
        digest.update(str(tuple(tensor.shape)).encode())
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def features(velocity, force, mass, kind="field", matrix_backend=True):
    lm = mass.log()
    if kind == "dense":
        return torch.cat((lm, velocity / 2, force / 3,
                          torch.log1p(velocity.square().sum(-1, keepdim=True))), -1)
    if kind == "field" and matrix_backend:
        # The native representation is used from initialization, including training.
        vv, ff, vf = physical_invariants(encode(velocity), encode(force))
        vv, ff, vf = (x.to(velocity.dtype).unsqueeze(-1) for x in (vv, ff, vf))
    else:
        metric = velocity.new_tensor([1., .2, 3.]) if kind == "scrambled" else 1.
        vv = (velocity.square() * metric).sum(-1, keepdim=True)
        ff = (force.square() * metric).sum(-1, keepdim=True)
        vf = (velocity * force * metric).sum(-1, keepdim=True)
    return torch.cat((lm, torch.log1p(vv), torch.log1p(ff),
                      vf / ((1 + vv) * (1 + ff)).sqrt(), lm.square(),
                      vv / (1 + vv), ff / (1 + ff),
                      (vv * ff - vf.square()) / (1 + vv * ff)), -1)


class GaugeBulk(nn.Module):
    """Persistent SU(2) link weights, transient adjoint fields, invariant readout.

    Every link has three learned Lie-algebra coordinates. There is no pretrained
    dense hidden network underneath these connection weights. Scalar radial gains
    and scalar readout weights are also learned from scratch.
    """
    def __init__(self, inputs=8, width=12):
        super().__init__()
        self.inputs, self.width = inputs, width
        self.links_in = nn.Parameter(torch.randn(12, inputs, 3) * .4)
        self.links_out = nn.Parameter(torch.randn(width, 12, 3) * .4)
        self.gain_in = nn.Parameter(torch.zeros(12))
        self.gain_out = nn.Parameter(torch.zeros(width))
        self.readout = nn.Linear(width, 3)

    @staticmethod
    def activate(field, gain):
        radius = field.square().sum(-1, keepdim=True).add(1e-12).sqrt()
        return field * torch.tanh(radius * gain.exp()[..., None]) / radius

    def forward(self, scalars):
        axes = torch.eye(3, dtype=scalars.dtype)[torch.arange(self.inputs) % 3]
        field = scalars[..., :, None] * axes
        hidden = torch.einsum("ijab,...jb->...ia", adjoint_rotations(self.links_in), field)
        hidden = self.activate(hidden / self.inputs ** .5, self.gain_in)
        boundary = torch.einsum("ijab,...jb->...ia", adjoint_rotations(self.links_out), hidden)
        boundary = self.activate(boundary / 12 ** .5, self.gain_out)
        invariants = boundary.square().sum(-1).add(1e-12).sqrt()
        return self.readout(invariants)

    def expanded(self, extra=16):
        if extra <= 0:
            raise ValueError("Expansion must add actual channels")
        grown = GaugeBulk(self.inputs, self.width + extra)
        with torch.no_grad():
            grown.links_in.copy_(self.links_in)
            grown.gain_in.copy_(self.gain_in)
            grown.links_out[:self.width].copy_(self.links_out)
            grown.gain_out[:self.width].copy_(self.gain_out)
            grown.readout.weight.zero_()
            grown.readout.weight[:, :self.width].copy_(self.readout.weight)
            grown.readout.bias.copy_(self.readout.bias)
        return grown


class Dynamics(nn.Module):
    def __init__(self, kind="field", width=12):
        super().__init__()
        if kind not in {"field", "scrambled", "dense", "invariant"}:
            raise ValueError("Unknown architecture")
        self.kind, self.width = kind, width
        if kind in {"dense", "invariant"}:
            # 783 genuine trainable parameters, exactly matching the 12-channel gauge core.
            self.net = nn.Sequential(nn.Linear(8, 20), nn.Tanh(),
                                     nn.Linear(20, 25), nn.Tanh(), nn.Linear(25, 3))
        else:
            self.net = GaugeBulk(8, width)

    def forward(self, velocity, force, mass):
        coefficients = self.net(features(velocity, force, mass, self.kind))
        if self.kind == "dense":
            return coefficients
        return (coefficients[..., :1] * force + coefficients[..., 1:2] * velocity
                + coefficients[..., 2:3] * torch.linalg.cross(force, velocity))

    def specification(self):
        return {"type": "base", "kind": self.kind, "width": self.width}


class Refinement(nn.Module):
    """One persistent owner, immutable base and a learned context-dependent residual.

    Context is computed from observed support errors, never a hidden environment ID.
    Its dimensions and the residual family are explicit supplied engineering.
    """
    def __init__(self, base, width=12):
        super().__init__()
        self.base = copy.deepcopy(base)
        self.base.requires_grad_(False)
        self.width = width
        self.residual = GaugeBulk(11, width)
        nn.init.zeros_(self.residual.readout.weight)
        nn.init.zeros_(self.residual.readout.bias)

    def context(self, velocity, force, mass, observed_acceleration):
        with torch.no_grad():
            error = observed_acceleration - self.base(velocity, force, mass)
            vv = velocity.square().sum(-1, keepdim=True)
            ff = force.square().sum(-1, keepdim=True)
            stats = torch.cat(((error * velocity).sum(-1, keepdim=True) / (1 + vv),
                               (error * force).sum(-1, keepdim=True) / (1 + ff),
                               error.square().sum(-1, keepdim=True) / (1 + vv + ff)), -1)
            return stats.mean(-2)

    def forward(self, velocity, force, mass, context=None):
        if context is None:
            return self.base(velocity, force, mass)
        context = torch.broadcast_to(context, (*velocity.shape[:-1], 3))
        coefficients = self.residual(torch.cat((features(velocity, force, mass), context), -1))
        correction = (coefficients[..., :1] * force + coefficients[..., 1:2] * velocity
                      + coefficients[..., 2:3] * torch.linalg.cross(force, velocity))
        return self.base(velocity, force, mass) + correction

    def expanded(self, extra=16):
        if extra <= 0:
            raise ValueError("Expansion must add actual channels")
        expanded = Refinement(self.base, self.width + extra)
        expanded.residual = self.residual.expanded(extra)
        return expanded

    def specification(self):
        return {"type": "refinement", "width": self.width, "base": self.base.specification()}


class QualifiedOwner(nn.Module):
    def __init__(self, successor, threshold):
        super().__init__()
        self.successor = copy.deepcopy(successor)
        self.register_buffer("compatibility_threshold", torch.tensor(float(threshold)))

    @property
    def base(self):
        return self.successor.base

    def context(self, *observations):
        return self.successor.context(*observations)

    def forward(self, velocity, force, mass, context=None):
        if context is None:
            return self.base(velocity, force, mass)
        prior = self.base(velocity, force, mass)
        revised = self.successor(velocity, force, mass, context)
        active = context[..., 2:3] > self.compatibility_threshold
        return torch.where(active, revised, prior)

    def specification(self):
        return {"type": "qualified", "successor": self.successor.specification(),
                "threshold": float(self.compatibility_threshold)}


class CalibratedOwner(QualifiedOwner):
    def __init__(self, successor, threshold, center, precision):
        super().__init__(successor, threshold)
        self.register_buffer("context_center", torch.as_tensor(center, dtype=torch.float32))
        self.register_buffer("context_precision", torch.as_tensor(precision, dtype=torch.float32))

    def forward(self, velocity, force, mass, context=None):
        if context is None:
            return self.base(velocity, force, mass)
        centered = context - self.context_center
        distance = torch.einsum("...i,ij,...j->...", centered, self.context_precision, centered)
        prior = self.base(velocity, force, mass)
        revised = self.successor(velocity, force, mass, context)
        return torch.where((distance > self.compatibility_threshold)[..., None], revised, prior)

    def specification(self):
        return {"type": "calibrated", "successor": self.successor.specification(),
                "threshold": float(self.compatibility_threshold), "center": self.context_center.tolist(),
                "precision": self.context_precision.tolist()}


def construct(specification):
    if specification["type"] == "calibrated":
        return CalibratedOwner(construct(specification["successor"]), specification["threshold"],
                               specification["center"], specification["precision"])
    if specification["type"] == "qualified":
        return QualifiedOwner(construct(specification["successor"]), specification["threshold"])
    if specification["type"] == "base":
        return Dynamics(specification["kind"], specification["width"])
    return Refinement(construct(specification["base"]), specification["width"])


def parameters(model):
    return {"total": sum(p.numel() for p in model.parameters()),
            "trainable": sum(p.numel() for p in model.parameters() if p.requires_grad),
            "persistent_tensor_bytes": sum(t.numel() * t.element_size()
                                           for t in model.state_dict().values() if isinstance(t,torch.Tensor))}
