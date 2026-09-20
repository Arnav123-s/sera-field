"""Stable stationary Fitzhugh-Nagumo member on a transported vector field.

Temporal equations: u_dot=-L u-a u-|u|^2 u-v+I,
v_dot=epsilon*(u-b v). At equilibrium v=u/b. With a,b>0 the
reduced energy is strictly convex and supports a self-adjoint implicit adjoint.
This does not reverse dissipative temporal dynamics.
"""
import torch
from .clifford_sheaf import sheaf_laplacian


def operator_matrix(restrictions):
    n,d=restrictions.shape[-2:]
    # restrictions shape [vertices,3,3]; this matrix acts on [vertex,coordinate].
    nodes=restrictions.shape[0];width=nodes*d
    eye=torch.eye(width,dtype=restrictions.dtype).reshape(width,nodes,d)
    return sheaf_laplacian(eye,restrictions).reshape(width,width).T


def stationary_solution(source,restrictions,coefficient,*,steps=10):
    b,n,d=source.shape
    linear=operator_matrix(restrictions)+coefficient*torch.eye(n*d,dtype=source.dtype)
    state=torch.linalg.solve(linear,source.flatten(1).T).T.reshape_as(source)
    for _ in range(steps):
        r=state.square().sum(-1,keepdim=True)
        gradient=(state.flatten(1)@linear.T).reshape_as(state)+r*state-source
        blocks=r[...,None]*torch.eye(d,dtype=source.dtype)+2*state[..., :,None]*state[...,None,:]
        hessian=linear[None].expand(b,-1,-1).clone()
        for i in range(n):hessian[:,i*d:(i+1)*d,i*d:(i+1)*d]+=blocks[:,i]
        delta=torch.linalg.solve(hessian,gradient.flatten(1)[...,None]).reshape_as(state)
        state=state-delta
    return state,hessian


class StationaryField(torch.autograd.Function):
    @staticmethod
    def forward(ctx,source,restrictions,coefficient):
        x,r,c=[v.detach().double() for v in (source,restrictions,coefficient)]
        state,hessian=stationary_solution(x,r,c)
        residual=sheaf_laplacian(state,r)+c*state+state.square().sum(-1,keepdim=True)*state-x
        if float(residual.abs().max())>1e-9:
            raise ValueError('Stationary residual failed; no implicit credit is qualified')
        ctx.save_for_backward(state,r,c,hessian);ctx.dtype=source.dtype
        return state.to(source.dtype)

    @staticmethod
    @torch.autograd.function.once_differentiable
    def backward(ctx,derivative):
        state,r,c,hessian=ctx.saved_tensors
        adjoint=torch.linalg.solve(hessian,derivative.double().flatten(1)[...,None]).reshape_as(state)
        # Differentiate only the local stationary residual, not an unrolled solve.
        with torch.enable_grad():
            rr=r.detach().requires_grad_();cc=c.detach().requires_grad_()
            residual=sheaf_laplacian(state,rr)+cc*state
            gr,gc=torch.autograd.grad((residual*adjoint).sum(),(rr,cc))
        return adjoint.to(ctx.dtype),-gr.to(ctx.dtype),-gc.to(ctx.dtype)


def stationary(source,restrictions,coefficient):
    return StationaryField.apply(source,restrictions,coefficient)
