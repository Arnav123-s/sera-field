"""Hamiltonian echo of the coupled energy's explicitly frozen canonical subflow.

Log covariance and other slow coordinates are constant during this subflow.
Their conjugate credit momenta, and those of source/parameters, accumulate the
local derivatives of the SAME energy. Symmetric positive/negative terminal
impulses recover its first derivatives. Dissipation is never reversed.
"""
import math

import torch
from torch.func import functional_call


FIXED = ('log_covariance', 'fast', 'slow', 'bulk')


def fixed_names(core):
    return FIXED + (('extension', 'disagreement') if core.extension_size else ())


class FrozenCanonical:
    def __init__(self, core, names, values, *, dt, steps):
        if not math.isfinite(dt) or not 0 < abs(dt) <= .02 or type(steps) is not int or not 1 <= steps <= 64:
            raise ValueError('Finite reversible interval and bounded substeps required')
        self.core, self.names, self.values = core, names, values
        self.dt, self.steps = dt/steps, steps

    def partials(self, phase, *, kinetic, complete, graph):
        with torch.enable_grad():
            # All arguments are independent partial-derivative nodes. Outer
            # history remains connected in the ordinary-autograd control.
            x = phase.clone() if phase.requires_grad else phase.detach().clone().requires_grad_(True)
            fixed = [v.clone() if v.requires_grad else v.detach().clone().requires_grad_(True) for v in self.values]
            if kinetic:
                logs = .5*(fixed[0]+fixed[0].transpose(-1, -2))
                vector = x[..., [1, 2, 4]]
                metric = torch.matrix_exp(-logs)
                value = .5*(x.square().sum()-vector.square().sum()
                            +(vector[..., None, :] @ metric @ vector[..., None]).sum())
            else:
                count = len(fixed_names(self.core))
                state = {**dict(zip(fixed_names(self.core), fixed[:count])), 'q': x, 'p': torch.zeros_like(x)}
                parameters = dict(zip(self.names, fixed[count+1:]))
                value = functional_call(self.core, parameters, (state, fixed[count]))[0].sum()
            targets = (x, *fixed) if complete else (x,)
            raw = torch.autograd.grad(value, targets, create_graph=graph, allow_unused=True)
            derivatives = tuple(torch.zeros_like(t) if g is None else g for g, t in zip(raw, targets))
        return derivatives if graph else tuple(g.detach() for g in derivatives)

    def evolve(self, q, p, *, complete=False, graph=False):
        credit = tuple(torch.zeros_like(v) for v in self.values) if complete else ()
        for _ in range(self.steps):
            force = self.partials(q, kinetic=False, complete=complete, graph=graph)
            p = p-.5*self.dt*force[0]
            credit = tuple(r-.5*self.dt*f for r, f in zip(credit, force[1:]))
            velocity = self.partials(p, kinetic=True, complete=complete, graph=graph)
            q = q+self.dt*velocity[0]
            credit = tuple(r-self.dt*f for r, f in zip(credit, velocity[1:]))
            force = self.partials(q, kinetic=False, complete=complete, graph=graph)
            p = p-.5*self.dt*force[0]
            credit = tuple(r-.5*self.dt*f for r, f in zip(credit, force[1:]))
        if any(not bool(torch.isfinite(v).all()) for v in (q, p, *credit)):
            raise ValueError('Nonfinite reversible trajectory or echo credit')
        return q, p, credit


class CoupledEcho(torch.autograd.Function):
    @staticmethod
    def forward(ctx, core, names, dt, steps, q, p, *values):
        detached = tuple(v.detach().double() for v in (q, p, *values))
        flow = FrozenCanonical(core, names, detached[2:], dt=dt, steps=steps)
        final_q, final_p, _ = flow.evolve(*detached[:2])
        ctx.save_for_backward(final_q, final_p, *detached[2:])
        ctx.core, ctx.names, ctx.dt, ctx.steps = core, names, dt, steps
        ctx.dtypes = [v.dtype for v in (q, p, *values)]
        return final_q.to(q.dtype), final_p.to(p.dtype)

    @staticmethod
    @torch.autograd.function.once_differentiable
    def backward(ctx, grad_q, grad_p):
        final_q, final_p, *values = ctx.saved_tensors
        reverse = FrozenCanonical(ctx.core, ctx.names, values, dt=-ctx.dt, steps=ctx.steps)
        epsilon = 1e-4
        # A loss depending on both terminal coordinates applies J grad(L).
        # Shared-parameter credit is already summed over the case batch by
        # the partial derivative; state/source credit stays per case.
        plus = reverse.evolve(final_q+epsilon*grad_p.double(), final_p-epsilon*grad_q.double(), complete=True)
        minus = reverse.evolve(final_q-epsilon*grad_p.double(), final_p+epsilon*grad_q.double(), complete=True)
        gradients = ((minus[1]-plus[1])/(2*epsilon), (plus[0]-minus[0])/(2*epsilon),
                     *((m-p)/(2*epsilon) for p, m in zip(plus[2], minus[2])))
        return (None, None, None, None, *(g.to(dtype) for g, dtype in zip(gradients, ctx.dtypes)))


def canonical(core, state, source, *, dt=.01, steps=1, backend='echo'):
    names, parameters = zip(*core.named_parameters())
    values = tuple(state[k] for k in fixed_names(core))+(source, *parameters)
    if backend == 'echo':
        q, p = CoupledEcho.apply(core, names, dt, steps, state['q'], state['p'], *values)
    elif backend == 'autograd':
        # Use identical float64 integration in the independent derivative
        # control so a dtype change is not confused with an echo discrepancy.
        flow = FrozenCanonical(core, names, tuple(v.double() for v in values), dt=dt, steps=steps)
        q, p, _ = flow.evolve(state['q'].double(), state['p'].double(), graph=torch.is_grad_enabled())
        q, p = q.to(state['q']), p.to(state['p'])
    else:
        raise ValueError('Declare echo or ordinary-autograd canonical credit')
    return {**state, 'q': q, 'p': p}
