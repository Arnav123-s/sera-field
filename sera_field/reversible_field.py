"""Full-coordinate echo credit without a trajectory autograd tape.

Encoders, readouts and constrained rotor algebra retain local chain rules.
The direct-autograd path is a qualification control of the same discrete flow.
"""
from dataclasses import dataclass
import torch
from .clifford_sheaf import (CliffordSheafField, coboundary, lift_rotation,
                            sheaf_gradient, typed_source)
from .gauge import adjoint_rotations, group_from_coordinates
from .situation_core import loop_feature


@dataclass
class CanonicalState:
    q: torch.Tensor
    p: torch.Tensor
    credit: tuple

    def reverse(self):
        return CanonicalState(self.q, -self.p, tuple(-r for r in self.credit))


class FullSheafFlow:
    def __init__(self, source, restrictions, prior, stiffness, strength, *, dt=.025, steps=32):
        if not 0 < dt <= .05 or not isinstance(steps, int) or not 1 <= steps <= 256:
            raise ValueError('Finite positive integration parameters required')
        self.source, self.restrictions, self.prior = source, restrictions, prior
        self.stiffness, self.strength = stiffness, strength
        self.dt, self.steps = dt, steps

    def initial(self, q, p):
        b, n, d = q.shape
        return CanonicalState(q, p, (torch.zeros_like(q), q.new_zeros(b,n,d,d),
                                    torch.zeros_like(q), q.new_zeros(b), q.new_zeros(b)))

    def force(self, q):
        return -sheaf_gradient(q, self.source, self.restrictions, self.prior,
                               self.stiffness, self.strength)

    def local_credit_forces(self, q):
        delta = coboundary(q, self.restrictions)
        deviation = q-self.prior
        radius_error = q.square().sum(-1)-.25
        return (q, delta[..., :, None]*q[..., None, :], self.stiffness*deviation,
                -.5*deviation.square().sum((-1,-2)), -.25*radius_error.square().sum(-1))

    def evolve(self, state):
        q, p, credit = state.q, state.p, state.credit
        force, local = self.force(q), self.local_credit_forces(q)
        for _ in range(self.steps):
            half_p = p+.5*self.dt*force
            half_credit = tuple(r+.5*self.dt*f for r,f in zip(credit,local))
            q = q+self.dt*half_p
            force, local = self.force(q), self.local_credit_forces(q)
            p = half_p+.5*self.dt*force
            credit = tuple(r+.5*self.dt*f for r,f in zip(half_credit,local))
        return CanonicalState(q,p,credit)

    def reference_position(self, q, p):
        force = self.force(q)
        for _ in range(self.steps):
            half = p+.5*self.dt*force
            q = q+self.dt*half
            force = self.force(q)
            p = half+.5*self.dt*force
        return q

    @torch.no_grad()
    def echo(self, final, terminal_gradient, epsilon):
        kicked = CanonicalState(final.q, final.p-epsilon*terminal_gradient, final.credit)
        return self.evolve(kicked.reverse()).reverse()

    @torch.no_grad()
    def gradients(self, final, terminal_gradient, epsilon=1e-4):
        if not 0 < epsilon <= .01 or terminal_gradient.shape != final.q.shape:
            raise ValueError('Qualified finite impulse and matching terminal derivative required')
        if not torch.isfinite(terminal_gradient).all():
            raise ValueError('Nonfinite terminal derivative')
        plus = self.echo(final,terminal_gradient,epsilon)
        minus = self.echo(final,terminal_gradient,-epsilon)
        fixed = tuple((m-p)/(2*epsilon) for p,m in zip(plus.credit,minus.credit))
        gradients = ((minus.p-plus.p)/(2*epsilon), (plus.q-minus.q)/(2*epsilon),
                     fixed[0], fixed[1].sum(0), fixed[2].sum(0), fixed[3].sum(), fixed[4].sum())
        if any(not torch.isfinite(g).all() for g in gradients):
            raise ValueError('Divergent echo credit; no update is qualified')
        return gradients


class EchoFlow(torch.autograd.Function):
    @staticmethod
    def forward(ctx, q, p, source, restrictions, prior, stiffness, strength, steps):
        tensors = tuple(t.detach().double() for t in (q,p,source,restrictions,prior,stiffness,strength))
        if any(not torch.isfinite(t).all() for t in tensors):
            raise ValueError('Finite canonical coordinates required')
        flow = FullSheafFlow(*tensors[2:],steps=steps)
        final = flow.evolve(flow.initial(*tensors[:2]))
        ctx.save_for_backward(*tensors,final.q,final.p,*final.credit)
        ctx.steps, ctx.dtype = steps, q.dtype
        return final.q.to(q.dtype)

    @staticmethod
    @torch.autograd.function.once_differentiable
    def backward(ctx, terminal_gradient):
        tensors = ctx.saved_tensors
        flow = FullSheafFlow(*tensors[2:7],steps=ctx.steps)
        final = CanonicalState(tensors[7],tensors[8],tuple(tensors[9:]))
        gradients = flow.gradients(final,terminal_gradient.double())
        return (*[g.to(ctx.dtype) for g in gradients],None)


def position(q,p,source,restrictions,prior,stiffness,strength,*,steps=32,backend='echo'):
    if backend == 'echo':
        return EchoFlow.apply(q,p,source,restrictions,prior,stiffness,strength,steps)
    if backend != 'autograd':
        raise ValueError('Explicit echo or autograd backend required')
    coordinates = [t.double() for t in (q,p,source,restrictions,prior,stiffness,strength)]
    return FullSheafFlow(*coordinates[2:],steps=steps).reference_position(*coordinates[:2]).to(q.dtype)


class EchoSheafField(CliffordSheafField):
    def __init__(self,nodes=8,rounds=4,*,backend='echo',steps=32):
        super().__init__(nodes,rounds)
        if backend not in ('echo','autograd','no_core_credit'):
            raise ValueError('Unknown credit arm')
        self.backend,self.steps=backend,steps

    def imagine(self,source,previous=None,*,use_imagination=True):
        restrictions=lift_rotation(adjoint_rotations(self.links).transpose(-1,-2))
        injection=typed_source(source,restrictions)
        q=self.prior.expand(source.shape[0],-1,-1) if previous is None else previous
        if use_imagination:
            state=position(q,torch.zeros_like(q),injection,restrictions,self.prior,
                           .1+.9*self.raw_stiffness.sigmoid(),
                           .05+.2*self.raw_condensation.sigmoid(),steps=self.steps,
                           backend='autograd' if self.backend=='autograd' else 'echo')
        else:
            state=injection
        loop=loop_feature(group_from_coordinates(self.links),source).to(state.dtype)
        features=torch.cat((state.square().sum(-1).add(1e-8).sqrt(),loop[:,None]),-1)
        if self.backend=='no_core_credit':
            return state.detach(),features.detach()
        return state,features


from .scfe_owner import ScfeOwner


class EchoOwner(ScfeOwner):
    def __init__(self,width=48,nodes=8,rounds=4,*,backend='echo',steps=32):
        super().__init__(width,nodes,rounds)
        self.field=EchoSheafField(nodes,rounds,backend=backend,steps=steps)

    def specification(self):
        return {'type':'echo-sheaf-field-007',**self.config,
                'backend':self.field.backend,'steps':self.field.steps}
