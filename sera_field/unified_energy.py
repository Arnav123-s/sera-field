"""One finite energy coupling boundary, covariance, traces and active bulk.

This is the CORE-022 engineering equation, not a trained owner. A fixed observed
source is an external port. Passive loss goes to an explicit reservoir; active
nonreciprocal forcing has a separately measured work term. Continuous identities
are not silently assigned to the finite-step integrator.
"""
import torch
from torch import nn

from .clifford_sheaf import lift_rotation, sheaf_action, typed_source
from .continuum_core import bulk_laplacian, passive_bulk_energy
from .finite_neural_action import exact_action_and_score, FiniteNeuralAction
from .gauge import adjoint_rotations
from .spd_sheaf import log_lift, covariance_coboundary


COORDINATES = ('q', 'p', 'log_covariance', 'fast', 'slow', 'bulk')


class UnifiedEnergy(nn.Module):
    def __init__(self, nodes=8, depth=4):
        super().__init__()
        if type(nodes) is not int or nodes < 3 or type(depth) is not int or depth < 2:
            raise ValueError('Use at least three boundary nodes and two bulk layers')
        self.nodes, self.depth = nodes, depth
        self.links = nn.Parameter(.15 * torch.randn(nodes, 3))
        self.anchors = nn.Parameter(.05 * torch.randn(nodes, 3))
        self.prior = nn.Parameter(torch.zeros(nodes, 8))
        self.action = FiniteNeuralAction(nodes)
        self.raw_rates = nn.Parameter(torch.zeros(5))
        self.raw_couplings = nn.Parameter(torch.zeros(4))
        self.raw_activity = nn.Parameter(torch.tensor(.25))

    def empty(self, batch):
        ref = self.prior
        def zeros(*shape): return ref.new_zeros(batch, *shape)
        return {'q': zeros(self.nodes, 8), 'p': zeros(self.nodes, 8),
                'log_covariance': zeros(self.nodes, 3, 3),
                'fast': zeros(self.nodes, 3), 'slow': zeros(self.nodes, 3),
                'bulk': zeros(2, self.depth, self.nodes, 3), 'reservoir': zeros()}

    def geometry(self):
        return (adjoint_rotations(self.links).transpose(-1, -2),
                adjoint_rotations(self.anchors))

    def energy(self, state, source):
        q, p, logs, fast, slow, bulk = (state[k] for k in COORDINATES)
        vector = q[..., [1, 2, 4]]; momentum = p[..., [1, 2, 4]]
        transport, anchors = self.geometry(); restrictions = lift_rotation(transport)
        injection = typed_source(source, restrictions)
        logs = .5 * (logs + logs.transpose(-1, -2))
        metric_inverse = torch.matrix_exp(-logs)
        kinetic = .5 * (p.square().sum((-1, -2)) - momentum.square().sum((-1, -2))
            + (momentum[..., None, :] @ metric_inverse @ momentum[..., None]).sum((-1, -2, -3)))
        boundary = sheaf_action(q, injection, restrictions, self.prior, .55, .15)
        coupling = .02 + .18 * self.raw_couplings.sigmoid()
        discrepancy = covariance_coboundary(logs, transport)
        covariance = .5 * coupling[0] * ((logs-log_lift(vector)).square().sum((-1, -2, -3))
                                       + discrepancy.square().sum((-1, -2, -3)))
        # Bulk channels stay in the checkpoint frame. Anchors map their decoded
        # vectors into each boundary frame; they transform with that frame.
        remembered_bulk = (anchors[None] @ bulk.mean((1, 2))[..., None]).squeeze(-1)
        recalled = (fast + slow + remembered_bulk) / 3
        alignment = .5 * coupling[1] * (vector-recalled).square().sum((-1, -2))
        traces = .5 * coupling[2] * (fast-slow).square().sum((-1, -2))
        framed = torch.stack((fast, slow), 1)
        decoded = (anchors.transpose(-1, -2)[None, None] @ framed[..., None]).squeeze(-1)
        targets = decoded.tanh()[:, :, None].expand(-1, -1, self.depth, -1, -1)
        condensate = coupling[3] * passive_bulk_energy(bulk, targets)
        features = self.action.features(source, transport)
        sigma = .2 + .6 * self.action.raw_sigma.sigmoid()
        neural, _ = exact_action_and_score(vector.flatten(1), features, sigma)
        neural = (.01 + .09 * self.action.raw_gain.sigmoid()) * neural
        pieces = {'kinetic': kinetic, 'boundary': boundary, 'covariance': covariance,
                  'alignment': alignment, 'traces': traces, 'condensate': condensate,
                  'neural_action': neural}
        return sum(pieces.values()), pieces

    def rhs(self, state, source, *, active=True, create_graph=None):
        """Full derivatives in every coupled coordinate; no detached memory force."""
        if create_graph is None:
            create_graph = torch.is_grad_enabled()
        with torch.enable_grad():
            coordinates = {k: v if v.requires_grad else v.detach().requires_grad_(True)
                           for k, v in state.items() if k in COORDINATES}
            value, _ = self.energy(coordinates, source)
            raw = torch.autograd.grad(value.sum(), tuple(coordinates[k] for k in COORDINATES),
                                      create_graph=create_graph)
            gradient = dict(zip(COORDINATES, raw))
            rate = .01 + .09 * self.raw_rates.sigmoid()
            damping, covariance_rate, fast_rate, slow_fraction, bulk_rate = rate
            slow_rate = .002 + fast_rate * slow_fraction
            passive_bulk = bulk_rate * bulk_laplacian(gradient['bulk'])
            alpha = .05 * self.raw_activity.tanh() if active else self.raw_activity*0
            first, second = coordinates['bulk'].unbind(1)
            active_bulk = torch.stack((-alpha*bulk_laplacian(second),
                                       alpha*bulk_laplacian(first)), 1)
            derivative = {'q': gradient['p'], 'p': -gradient['q']-damping*gradient['p'],
                'log_covariance': -covariance_rate*gradient['log_covariance'],
                'fast': -fast_rate*gradient['fast'], 'slow': -slow_rate*gradient['slow'],
                'bulk': passive_bulk+active_bulk}
            def inner(a, b): return (a*b).flatten(1).sum(-1)
            dissipation = (damping*inner(gradient['p'], gradient['p'])
                + covariance_rate*inner(gradient['log_covariance'], gradient['log_covariance'])
                + fast_rate*inner(gradient['fast'], gradient['fast'])
                + slow_rate*inner(gradient['slow'], gradient['slow'])
                - inner(gradient['bulk'], passive_bulk))
            derivative['reservoir'] = dissipation
            active_work = inner(gradient['bulk'], active_bulk)
            h_rate = sum(inner(gradient[k], derivative[k]) for k in COORDINATES)
            diagnostics = {'energy': value, 'active_work': active_work,
                           'dissipation': dissipation,
                           'energy_balance_residual': h_rate+dissipation-active_work,
                           'bulk_mass_rate': derivative['bulk'].sum((-3, -2))}
        if not create_graph:
            derivative = {k: v.detach() for k, v in derivative.items()}
            diagnostics = {k: v.detach() for k, v in diagnostics.items()}
        return derivative, diagnostics

    def step(self, state, source, *, dt=.01, active=True):
        """Pure Heun step; report rather than erase its energy-balance defect."""
        if not 0 < dt <= .02:
            raise ValueError('The engineering integrator requires 0 < dt <= .02')
        first, before = self.rhs(state, source, active=active)
        predicted = {k: v+dt*first[k] for k, v in state.items()}
        second, following = self.rhs(predicted, source, active=active)
        result = {k: v+.5*dt*(first[k]+second[k]) for k, v in state.items()}
        if any(not bool(torch.isfinite(v).all()) for v in result.values()):
            raise ValueError('Nonfinite coupled step; retain the preceding state')
        energy, _ = self.energy(result, source)
        defect = (energy+result['reservoir']-before['energy']-state['reservoir']
                  -.5*dt*(before['active_work']+following['active_work']))
        return result, {**before, 'discrete_balance_defect': defect,
                        'bulk_mass_change': (result['bulk']-state['bulk']).sum((-3, -2))}
