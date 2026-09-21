"""Measured prediction errors and a local, explicitly Gaussian scale diagnostic.

The Hessian is a three-direction restriction of this owner's actual action at
its current situation. A negative/indefinite curvature is reported. Only a
positive regulated quadratic is integrated; it is not the full interacting RG.
"""
import torch


def action_scale_diagnostic(owner, state, source):
    if len(source) != 1:
        raise ValueError('One scoped situation per curvature audit')
    state = {k: v.detach() for k, v in state.items()}
    source = source.detach()
    # Fixed supplied directions in the scalar blade at three distinct nodes.
    # These are diagnostic coordinates, not claimed learned physical variables.
    directions = source.new_zeros(3, owner.config.nodes, 8)
    for i in range(3): directions[i, i, 0] = 1
    with torch.enable_grad():
        def action(z):
            q = state['q']+torch.einsum('k,knd->nd', z, directions)[None]
            return owner.core.energy({**state, 'q': q}, source)[0].sum()
        hessian = torch.autograd.functional.hessian(action, source.new_zeros(3))
    hessian = .5*(hessian+hessian.T)
    eigen = torch.linalg.eigvalsh(hessian.double())
    if not bool(torch.isfinite(eigen).all()):
        raise ValueError('Nonfinite restricted action curvature')
    permitted = bool((eigen+.25 > 0).all())
    scales = eigen.new_tensor([2., 1., .5])
    derivatives = ((scales[:, None]/(eigen[None]+scales[:, None].square())).sum(-1)
                   if permitted else None)
    integral = (.5*torch.log((eigen+4)/(eigen+.25)).sum() if permitted else None)
    return {'hessian': hessian.detach().tolist(), 'eigenvalues': eigen.tolist(),
            'quadratic_regulated_domain_valid': permitted, 'scales': scales.tolist(),
            'derivative': None if derivatives is None else derivatives.tolist(),
            'integral': None if integral is None else float(integral),
            'scope': 'three scalar-blade directions; local quadratic; R(k)=k^2 I; fixed current observation and weights'}


def adequacy_features(residuals, variances, diagnostic, reference):
    if len(residuals) != len(variances) or any(not torch.isfinite(reference.new_tensor(v)) for v in (*residuals, *variances)):
        raise ValueError('Aligned finite pre-observation errors and branch variances required')
    r = reference.new_tensor(residuals)
    v = reference.new_tensor(variances)
    evidence = [len(r)/(len(r)+1), float(r.abs().mean()) if len(r) else 0.,
                float(r.square().mean()) if len(r) else 0., float(v.mean()) if len(v) else 0.]
    eigen = diagnostic['eigenvalues']
    curvature = [min(eigen), max(eigen), float(diagnostic['quadratic_regulated_domain_valid']),
                 0. if diagnostic['integral'] is None else diagnostic['integral']]
    return reference.new_tensor([evidence+curvature])
