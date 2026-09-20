"""Timed source/loss extension of the qualified finite canonical field.

Only reversible trajectories are echoed. Covariance relaxation and verified
capture happen outside each trajectory and keep their own chain rules.
"""
import torch

from .reversible_field import CanonicalState, FullSheafFlow


class TimedSheafFlow:
    def __init__(self, sources, restrictions, prior, stiffness, strength, *, steps=8):
        if sources.ndim != 4 or not 1 <= len(sources) <= 64:
            raise ValueError('A finite [time,batch,node,blade] source history is required')
        self.sources = sources
        self.fixed = (restrictions, prior, stiffness, strength)
        self.steps = steps

    def part(self, t):
        return FullSheafFlow(self.sources[t], *self.fixed, steps=self.steps)

    def evolve(self, q, p):
        state = self.part(0).initial(q, p)
        positions = []
        for t in range(len(self.sources)):
            state = self.part(t).evolve(state)
            positions.append(state.q)
        return torch.stack(positions), state

    def reference(self, q, p):
        # Ordinary autograd over the same discrete equations is an independent
        # derivative control, not the teaching backend.
        return self.evolve(q, p)[0]

    @torch.no_grad()
    def reverse_with_losses(self, final, derivatives, epsilon):
        state = final
        source_integrals = [None] * len(self.sources)
        for t in reversed(range(len(self.sources))):
            state = CanonicalState(state.q, state.p-epsilon*derivatives[t], state.credit)
            before = state.credit[0]
            state = self.part(t).evolve(state.reverse()).reverse()
            source_integrals[t] = state.credit[0]-before
        return state, torch.stack(source_integrals)

    @torch.no_grad()
    def gradients(self, final, derivatives, epsilon=1e-4):
        if derivatives.shape != self.sources.shape or not torch.isfinite(derivatives).all():
            raise ValueError('Finite timed loss derivatives with matching coordinates required')
        plus, input_plus = self.reverse_with_losses(final, derivatives, epsilon)
        minus, input_minus = self.reverse_with_losses(final, derivatives, -epsilon)
        credit = [(m-p)/(2*epsilon) for p,m in zip(plus.credit, minus.credit)]
        result = ((minus.p-plus.p)/(2*epsilon), (plus.q-minus.q)/(2*epsilon),
                  (input_minus-input_plus)/(2*epsilon), credit[1].sum(0),
                  credit[2].sum(0), credit[3].sum(), credit[4].sum())
        if any(not torch.isfinite(x).all() for x in result):
            raise ValueError('Divergent temporal credit')
        return result


class TimedEcho(torch.autograd.Function):
    @staticmethod
    def forward(ctx, q, p, sources, restrictions, prior, stiffness, strength, steps):
        tensors = tuple(x.detach().double() for x in
                        (q,p,sources,restrictions,prior,stiffness,strength))
        flow = TimedSheafFlow(*tensors[2:], steps=steps)
        positions, final = flow.evolve(*tensors[:2])
        ctx.save_for_backward(*tensors,final.q,final.p,*final.credit)
        ctx.steps, ctx.dtype = steps, q.dtype
        return positions.to(q.dtype)

    @staticmethod
    @torch.autograd.function.once_differentiable
    def backward(ctx, derivatives):
        ts = ctx.saved_tensors
        flow = TimedSheafFlow(*ts[2:7], steps=ctx.steps)
        final = CanonicalState(ts[7],ts[8],tuple(ts[9:]))
        return (*[x.to(ctx.dtype) for x in flow.gradients(final,derivatives.double())],None)


def timed_positions(q,p,sources,restrictions,prior,stiffness,strength,*,steps=8,backend='echo'):
    if backend == 'echo':
        return TimedEcho.apply(q,p,sources,restrictions,prior,stiffness,strength,steps)
    if backend != 'autograd':
        raise ValueError('Explicit temporal credit backend required')
    tensors = [x.double() for x in (q,p,sources,restrictions,prior,stiffness,strength)]
    return TimedSheafFlow(*tensors[2:],steps=steps).reference(*tensors[:2]).to(q.dtype)
