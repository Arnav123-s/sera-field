"""A finite Cl(3,0) graph-sheaf field with an explicit condensation action.

Multivectors have geometric type; their coefficients still use ordinary numerical
storage. This implements neither holographic duality nor topological truth.
"""
import torch
from torch import nn

from .gauge import adjoint_rotations, group_from_coordinates
from .situation_core import loop_feature


def product_table(dtype=torch.float64):
    table = torch.zeros(8, 8, 8, dtype=dtype)
    for a in range(8):
        for b in range(8):
            inversions = sum(bool(a & (1 << i)) * sum(bool(b & (1 << j)) for j in range(i))
                             for i in range(3))
            table[a, b, a ^ b] = -1 if inversions % 2 else 1
    return table


def geometric_product(left, right):
    return torch.einsum('...i,...j,ijk->...k', left, right, product_table(left.dtype))


def reverse(value):
    # Reversal sign (-1)^(grade*(grade-1)/2), bit-mask basis order.
    signs = value.new_tensor([1, 1, 1, -1, 1, -1, -1, -1])
    return value * signs


def clifford_rotor(coordinates):
    radius = coordinates.square().sum(-1).add(1e-16).sqrt()
    vector = torch.sinc(radius / torch.pi)[..., None] * coordinates
    result = torch.zeros(*coordinates.shape[:-1], 8, dtype=coordinates.dtype)
    result[..., 0] = radius.cos()
    result[..., 6] = vector[..., 0]
    result[..., 5] = -vector[..., 1]
    result[..., 3] = vector[..., 2]
    return result


def lift_rotation(rotation):
    """Induced rotor action on scalar, vector, bivector and trivector grades."""
    matrix = torch.zeros(*rotation.shape[:-2], 8, 8, dtype=rotation.dtype)
    matrix[..., 0, 0] = 1
    matrix[..., 7, 7] = 1
    vector, bivector, signs = (1, 2, 4), (6, 5, 3), (1, -1, 1)
    for i in range(3):
        for j in range(3):
            matrix[..., vector[i], vector[j]] = rotation[..., i, j]
            matrix[..., bivector[i], bivector[j]] = signs[i] * signs[j] * rotation[..., i, j]
    return matrix


def transport(matrix, value):
    return torch.einsum('nij,...nj->...ni', matrix, value)


def coboundary(state, restrictions):
    # Edge i is framed at vertex i+1; both terms live in that same stalk.
    return state.roll(-1, -2) - transport(restrictions, state)


def sheaf_laplacian(state, restrictions):
    difference = coboundary(state, restrictions)
    # delta^T maps each edge discrepancy back to both incident vertex frames.
    return difference.roll(1, -2) - transport(restrictions.transpose(-1, -2), difference)


def sheaf_action(state, source, restrictions, prior, stiffness, strength, radius=.5):
    discrepancy = coboundary(state, restrictions)
    radius_error = state.square().sum(-1) - radius**2
    return (.5 * discrepancy.square().sum((-1, -2))
            + .5 * stiffness * (state-prior).square().sum((-1, -2))
            + .25 * strength * radius_error.square().sum(-1)
            - (source*state).sum((-1, -2)))


def sheaf_gradient(state, source, restrictions, prior, stiffness, strength, radius=.5):
    radial = (state.square().sum(-1, keepdim=True) - radius**2) * state
    return sheaf_laplacian(state, restrictions) + stiffness*(state-prior) + strength*radial - source


def typed_source(vectors, restrictions):
    """Observable graded lift; no correctness or mechanism labels are supplied."""
    lifted = torch.zeros(*vectors.shape[:-1], 8, dtype=vectors.dtype)
    for i, blade in enumerate((1, 2, 4)):
        lifted[..., blade] = vectors[..., i]
    # Neighbor fields are first transported into the same frame.
    local_next = transport(restrictions.transpose(-1, -2), lifted.roll(-1, -2))
    other = local_next[..., [1, 2, 4]]
    cross = torch.linalg.cross(vectors, other) / 3
    lifted[..., 0] = vectors.square().sum(-1) / 3
    lifted[..., 6], lifted[..., 5], lifted[..., 3] = cross[..., 0], -cross[..., 1], cross[..., 2]
    next_other = transport(restrictions.transpose(-1, -2), local_next.roll(-1, -2))[..., [1, 2, 4]]
    lifted[..., 7] = (cross*next_other).sum(-1) / 3
    return lifted


class CliffordSheafField(nn.Module):
    def __init__(self, nodes=8, rounds=4, *, source_field=None):
        super().__init__()
        self.nodes, self.rounds = nodes, rounds
        self.links = nn.Parameter(torch.randn(nodes, 3)*.15)
        self.prior = nn.Parameter(torch.zeros(nodes, 8))
        self.raw_stiffness = nn.Parameter(torch.tensor(0.))
        self.raw_condensation = nn.Parameter(torch.tensor(0.))
        if source_field is not None:
            # Copies only this owner's freshly initialized geometric coordinates.
            with torch.no_grad():
                self.links.copy_(source_field.links)
                self.prior[:, [1,2,4]] = source_field.prior
                self.raw_stiffness.copy_(source_field.raw_stiffness)

    def imagine(self, source, previous=None, *, use_imagination=True):
        # The old connection maps next->current. Restrictions map current->next.
        restrictions = lift_rotation(adjoint_rotations(self.links).transpose(-1, -2))
        injection = typed_source(source, restrictions)
        state = self.prior.expand(source.shape[0], -1, -1) if previous is None else previous
        stiffness = .1 + .9*self.raw_stiffness.sigmoid()
        strength = .05 + .2*self.raw_condensation.sigmoid()
        if use_imagination:
            for _ in range(self.rounds):
                energy = sheaf_action(state, injection, restrictions, self.prior, stiffness, strength)
                gradient = sheaf_gradient(state, injection, restrictions, self.prior, stiffness, strength)
                dt = torch.full_like(energy, .1)
                candidate = state - dt[:, None, None]*gradient
                for _ in range(8):
                    changed = sheaf_action(candidate, injection, restrictions, self.prior, stiffness, strength)
                    bad = changed > energy + 1e-7
                    if not bool(bad.any()):
                        break
                    dt = torch.where(bad, .5*dt, dt)
                    candidate = state - dt[:, None, None]*gradient
                # A failed line search retains the valid prior transient state.
                valid = sheaf_action(candidate, injection, restrictions, self.prior, stiffness, strength) <= energy + 1e-7
                state = torch.where(valid[:, None, None], candidate, state)
        else:
            state = injection
        loop = loop_feature(group_from_coordinates(self.links), source).to(state.dtype)
        features = torch.cat((state.square().sum(-1).add(1e-8).sqrt(), loop[:, None]), -1)
        return state, features


def parameter_bytes(module):
    return sum(p.numel()*p.element_size() for p in module.parameters())
