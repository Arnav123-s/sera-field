"""SU(2) adjoint representations and local frame transport, in complex128."""

import torch


def pauli():
    return torch.tensor([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]],
                         [[1, 0], [0, -1]]], dtype=torch.complex128)


def encode(vector):
    return torch.einsum("...a,aij->...ij", vector.to(torch.complex128), pauli())


def decode(matrix):
    return (torch.einsum("...ij,aji->...a", matrix, pauli()).real / 2).to(torch.float64)


def conjugate(group, matrix):
    return group @ matrix @ group.mH


def transport(link, local_field):
    return conjugate(link, local_field)


def trace_inner(left, right):
    return torch.diagonal(left @ right, dim1=-2, dim2=-1).sum(-1).real / 2


def random_su2(count, generator):
    q = torch.randn(count, 4, generator=generator, dtype=torch.float64)
    q = q / torch.linalg.vector_norm(q, dim=-1, keepdim=True)
    return q[:, 0, None, None] * torch.eye(2, dtype=torch.complex128) + 1j * encode(q[:, 1:])


def reframe(root, local, vector):
    """An independent local frame and the exact link back to the root frame."""
    return root @ local.mH, conjugate(local, encode(vector))


def physical_invariants(velocity_matrix, force_matrix):
    return (trace_inner(velocity_matrix, velocity_matrix),
            trace_inner(force_matrix, force_matrix),
            trace_inner(velocity_matrix, force_matrix))


def group_from_coordinates(coordinates):
    """Exponential SU(2) weights; the stored coordinates start randomly, not pretrained."""
    radius = coordinates.square().sum(-1).add(1e-16).sqrt()
    identity = torch.eye(2, dtype=torch.complex128)
    return (radius.cos()[..., None, None] * identity
            + 1j * torch.sinc(radius / torch.pi)[..., None, None] * encode(coordinates))


def adjoint_rotations(coordinates):
    group = group_from_coordinates(coordinates)
    transported_basis = group[..., None, :, :] @ pauli() @ group[..., None, :, :].mH
    return decode(transported_basis).transpose(-1, -2).to(coordinates.dtype)


def wilson_loop(first, second, third, fourth):
    loop = first @ second.mH @ third @ fourth.mH
    return torch.diagonal(loop, dim1=-2, dim2=-1).sum(-1).real / 2
