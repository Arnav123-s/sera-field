"""Log-group SPD stalks with the owner's orthogonal restriction maps."""
import torch


def congruence(rotation, symmetric):
    return rotation @ symmetric @ rotation.transpose(-1,-2)


def log_lift(vectors):
    # Exact log(I + vv^T), including its removable zero-norm singularity.
    radius = vectors.square().sum(-1,keepdim=True)
    scale = torch.where(radius > 1e-7, torch.log1p(radius)/radius.clamp_min(1e-30),
                        1-radius/2+radius.square()/3)
    return scale[...,None] * vectors[..., :,None] * vectors[...,None,:]


def covariance_coboundary(log_stalks, restrictions):
    return log_stalks.roll(-1,-3)-congruence(restrictions,log_stalks)


def covariance_adjoint(edges, restrictions):
    return edges.roll(1,-3)-congruence(restrictions.transpose(-1,-2),edges)


def covariance_sequence(source, restrictions, coupling, *, frames=4):
    observed = log_lift(source)
    state = observed
    sequence = []
    for _ in range(frames):
        gradient = covariance_adjoint(covariance_coboundary(state,restrictions),restrictions)
        state = state-.08*(gradient+coupling*(state-observed))
        state = .5*(state+state.transpose(-1,-2))
        sequence.append(state)
    return torch.stack(sequence)


def covariance_drive(log_stalks, vectors):
    covariance = torch.matrix_exp(log_stalks)
    # Bound injection without discarding the orientation of the covariance.
    transformed = (covariance @ vectors[...,None]).squeeze(-1)
    scale = covariance.diagonal(dim1=-2,dim2=-1).sum(-1,keepdim=True)/3
    return transformed/scale.clamp_min(1e-6),covariance
