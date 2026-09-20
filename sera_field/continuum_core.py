"""Finite coupled flow, separated traces and active conserved memory.

The state is explicit so a conditional rollout cannot mutate factual history.
These are numerical mechanisms; independent outcomes still qualify learning.
"""
import torch
from torch import nn


def connection_laplacian(transport):
    """D*D for oriented local-vector restrictions on one periodic ring."""
    nodes = len(transport)
    eye = torch.eye(3, dtype=transport.dtype, device=transport.device)
    rows = []
    for edge in range(nodes):
        blocks = [torch.zeros_like(eye) for _ in range(nodes)]
        blocks[edge] = -transport[edge]
        blocks[(edge + 1) % nodes] = eye
        rows.append(torch.cat(blocks, -1))
    difference = torch.cat(rows, -2)
    return difference.transpose(-1, -2) @ difference


class ConditionalGaugeFlow(nn.Module):
    """An exact conditional linear CNF on vector fibers, with learned rates.

    The conditioning variables are invariant observed summaries, held fixed for
    inversion and density accounting. This is not a CNF on the group links.
    """
    def __init__(self, nodes):
        super().__init__(); self.nodes = nodes
        self.rates = nn.Sequential(nn.Linear(4, 16), nn.Tanh(), nn.Linear(16, nodes + 1))
        nn.init.zeros_(self.rates[-1].weight); nn.init.zeros_(self.rates[-1].bias)

    def generator(self, context, transport):
        values = self.rates(context)
        diagonal = (.15 * values[..., :self.nodes].tanh()).repeat_interleave(3, -1)
        diffusion = .06 * values[..., -1].sigmoid()
        return torch.diag_embed(diagonal) - diffusion[..., None, None] * connection_laplacian(transport)

    def forward(self, value, context, transport, *, reverse=False):
        if value.shape[-2:] != (self.nodes, 3) or context.shape != (*value.shape[:-2], 4):
            raise ValueError('One invariant context per local-vector field required')
        generator = self.generator(context, transport)
        signed = -generator if reverse else generator
        evolution = torch.matrix_exp(signed)
        mapped = (evolution @ value.flatten(-2)[..., None]).squeeze(-1).reshape_as(value)
        logdet = signed.diagonal(dim1=-2, dim2=-1).sum(-1)
        return mapped, logdet

    def gaussian_reverse_kl(self, context, transport):
        """KL(flow N(0,I) || N(0,I)), conditional on the recorded context."""
        generator = self.generator(context, transport)
        evolution = torch.matrix_exp(generator)
        dimension = generator.shape[-1]
        return .5 * (evolution.square().sum((-2, -1)) - dimension -
                     2 * generator.diagonal(dim1=-2, dim2=-1).sum(-1))


def bulk_laplacian(value):
    return sum(value.roll(1, dim) + value.roll(-1, dim) - 2 * value for dim in (-3, -2))


def nrch_step(fields, target, *, alpha, dt=.01, rho=.15, kappa=(.08, .16), mobility=(1., .5), pin=.5):
    """Two conserved scalar concentration fields; periodic depth/node axes.

    Bulk coordinates are stored in their checkpoint frame. Conservation applies
    to relaxation, not evidence-driven writes. Interfacial stiffness is implicit;
    the double-well, pinning and nonreciprocal terms are explicit. Active dynamics
    need not decrease the passive free energy.
    """
    if fields.shape != target.shape or fields.shape[-4] != 2:
        raise ValueError('Two same-shaped conserved fields and explicit targets required')
    first, second = fields.unbind(-4)
    target_first, target_second = target.unbind(-4)
    nonlinear = (-.5 * first + first.pow(3) - (rho + alpha) * second + pin * (first - target_first),
                 -.5 * second + second.pow(3) - (rho - alpha) * first + pin * (second - target_second))
    depth, nodes = first.shape[-3:-1]
    kd = 4 * torch.sin(torch.pi * torch.fft.fftfreq(depth, device=fields.device, dtype=fields.dtype)).square()
    kn = 4 * torch.sin(torch.pi * torch.fft.fftfreq(nodes, device=fields.device, dtype=fields.dtype)).square()
    eigen = kd[:, None, None] + kn[None, :, None]
    updates = []
    for value, chemical, stiffness, rate in zip((first, second), nonlinear, kappa, mobility):
        numerator = torch.fft.fftn(value, dim=(-3, -2)) - dt * rate * eigen * torch.fft.fftn(chemical, dim=(-3, -2))
        update = torch.fft.ifftn(numerator / (1 + dt * rate * stiffness * eigen.square()), dim=(-3, -2)).real
        updates.append(update)
    return torch.stack(updates, -4)


def passive_bulk_energy(fields, target, *, rho=.15, kappa=(.08, .16), pin=.5):
    first, second = fields.unbind(-4)
    energy = -.25 * fields.square() + .25 * fields.pow(4) + .5 * pin * (fields - target).square()
    result = energy.sum((-4, -3, -2, -1)) - rho * (first * second).sum((-3, -2, -1))
    for value, stiffness in zip((first, second), kappa):
        result = result + .5 * stiffness * sum((value.roll(-1, d) - value).square().sum((-3, -2, -1)) for d in (-3, -2))
    return result


def bulk_spectral_length(fields):
    """Power-weighted spatial wavelength, with zero for a uniform field.

    This is a finite-lattice diagnostic, not a memory-capacity or forgetting
    measure. Remove each channel's mean before measuring domain structure.
    """
    centered = fields - fields.mean((-3, -2), keepdim=True)
    power = torch.fft.fftn(centered, dim=(-3, -2)).abs().square()
    depth, nodes = fields.shape[-3:-1]
    kd = 2 * torch.pi * torch.fft.fftfreq(depth, device=fields.device, dtype=fields.dtype)
    kn = 2 * torch.pi * torch.fft.fftfreq(nodes, device=fields.device, dtype=fields.dtype)
    magnitude = (kd[:, None].square() + kn[None, :].square()).sqrt()[..., None]
    total = power.sum((-3, -2, -1))
    weighted = (power * magnitude).sum((-3, -2, -1))
    nonuniform = total > torch.finfo(fields.dtype).eps
    length = torch.where(nonuniform, 2 * torch.pi * total / weighted.clamp_min(
        torch.finfo(fields.dtype).tiny), torch.zeros_like(total))
    return length, total


class MemoryContinuum(nn.Module):
    """Learnable fast/slow traces and NRCH state feeding one boundary source.

    Call `advance` on a copied state to imagine a write. Commit the returned state
    only after the existing independent assessment accepts that exact proposal.
    """
    def __init__(self, nodes, depth=4):
        super().__init__(); self.nodes = nodes; self.depth = depth
        self.flow = ConditionalGaugeFlow(nodes)
        self.raw_fast = nn.Parameter(torch.tensor(0.))
        self.raw_slow = nn.Parameter(torch.tensor(-1.))
        self.raw_feedback = nn.Parameter(torch.tensor(-1.))
        self.raw_activity = nn.Parameter(torch.tensor(.25))
        self.raw_readout = nn.Parameter(torch.zeros(3))

    def empty(self, batch, *, dtype=None, device=None):
        reference = self.raw_fast
        kwargs = {'dtype': dtype or reference.dtype, 'device': device or reference.device}
        return {'fast': torch.zeros(batch, self.nodes, 3, **kwargs),
                'slow': torch.zeros(batch, self.nodes, 3, **kwargs),
                'marks': torch.zeros(batch, 2, **kwargs),
                'bulk': torch.zeros(batch, 2, self.depth, self.nodes, 3, **kwargs),
                'flow_context': torch.zeros(batch, 4, **kwargs),
                'events': 0}

    def context(self, state, stimulus):
        return torch.stack((stimulus.square().mean((-2, -1)),
            state['fast'].square().mean((-2, -1)), state['marks'][:, 0], state['marks'][:, 1]), -1)

    def advance(self, state, stimulus, checked_progress, transport, *, relaxation_steps=8, reciprocal=False, equal_rates=False):
        if stimulus.shape != state['fast'].shape or checked_progress.shape != stimulus.shape[:1]:
            raise ValueError('Explicit per-event checked progress and field stimulus required')
        # This proposal is a pure function. Previous factual tensors are untouched.
        context = self.context(state, stimulus)
        encoded, logdet = self.flow(stimulus, context, transport)
        eta = .02 + .48 * self.raw_fast.sigmoid()
        # Keep the slow rate strictly below the fast rate for every learned
        # parameter, rather than merely giving their initial values that order.
        beta = .002 + .08 * eta * self.raw_slow.sigmoid()
        if equal_rates:
            beta = eta
        feedback = .02 + .08 * self.raw_feedback.sigmoid()
        fast = state['fast'] + eta * (encoded - state['fast']) + feedback * (state['slow'] - state['fast'])
        slow = state['slow'] + beta * (state['fast'] - state['slow'])
        support = checked_progress.clamp_min(0); opposition = (-checked_progress).clamp_min(0)
        marks = .95 * state['marks'] + .05 * torch.stack((support, opposition), -1)
        # The paired concentration target is driven by both timescales. Opposed
        # evidence remains in its own trace rather than vanishing into a mean.
        support_gain = 1 / (1 + marks[:, 1])
        opposed_gain = 1 / (1 + marks[:, 0])
        targets = torch.stack((support_gain[:, None, None] * fast.tanh(),
                               opposed_gain[:, None, None] * slow.tanh()), 1)
        target = targets[:, :, None].expand(-1, -1, self.depth, -1, -1)
        # Evidence injects a reservoir increment; subsequent relaxation conserves
        # each field's mass. Both changes are separately measurable.
        injected = state['bulk'] + .08 * (target - state['bulk'])
        value = injected
        alpha = self.raw_activity * 0 if reciprocal else .8 * self.raw_activity.tanh()
        for _ in range(relaxation_steps):
            value = nrch_step(value, target, alpha=alpha)
        if not bool(torch.isfinite(value).all()) or bool(value.detach().abs().max() > 4):
            raise ValueError('Active memory left its frozen numerical range; preserve the previous state')
        updated = {'fast': fast, 'slow': slow, 'marks': marks, 'bulk': value,
                   'flow_context': context, 'events': state['events'] + 1}
        length_before, power_before = bulk_spectral_length(injected)
        length_after, power_after = bulk_spectral_length(value)
        diagnostics = {'conditional_logdet': logdet,
            'reverse_kl': self.flow.gaussian_reverse_kl(context, transport),
            'write_mass_change': (injected - state['bulk']).sum((-3, -2)),
            'relaxation_mass_error': (value - injected).sum((-3, -2)),
            'passive_energy_before': passive_bulk_energy(injected, target),
            'passive_energy_after': passive_bulk_energy(value, target),
            'spectral_length_before': length_before, 'spectral_length_after': length_after,
            'spatial_power_before': power_before, 'spatial_power_after': power_after,
            'current_signal_retrieval_mse': (self.recall(updated, transport) - stimulus).square().mean((-2, -1)),
            'activity': alpha, 'fast_rate': eta, 'slow_rate': beta,
            'support': support, 'opposition': opposition}
        return updated, diagnostics

    def recall(self, state, transport):
        # Decode with the event's stored context. Parameter changes require the
        # ordinary checkpoint-qualified replay; no timeless inverse is assumed.
        values = torch.stack((state['fast'], state['slow'], state['bulk'].mean((-4, -3))), 1)
        mixture = (self.raw_readout.softmax(0)[None, :, None, None] * values).sum(1)
        decoded, _ = self.flow(mixture, state['flow_context'], transport, reverse=True)
        return decoded
