"""Explicit finite stalks and restrictions for representation attachment.

This operator is not imported by the active GENRE-017 experiment. Its graph
topology is supplied engineering; a learner choosing a useful new topology needs
its own observed task evidence. All states remain ordinary numerical tensors.
"""
from dataclasses import dataclass
import math

import torch


@dataclass(frozen=True)
class Edge:
    left: int
    right: int
    left_map: torch.Tensor
    right_map: torch.Tensor


class FiniteSheaf:
    """A degree-zero real cellular sheaf with heterogeneous stalk dimensions."""

    def __init__(self, dimensions, edges):
        self.dimensions = tuple(dimensions)
        self.edges = tuple(edges)
        if not self.dimensions or any(type(d) is not int or d <= 0 for d in self.dimensions):
            raise ValueError('Every vertex needs a positive integer stalk dimension')
        if not self.edges:
            raise ValueError('Supply at least one explicit restriction edge')
        example = self.edges[0].left_map
        if example.dtype not in (torch.float32, torch.float64):
            raise ValueError('Use a real float32 or float64 sheaf')
        self.dtype, self.device = example.dtype, example.device
        for edge in self.edges:
            if any(type(i) is not int or not 0 <= i < len(self.dimensions)
                   for i in (edge.left, edge.right)) or edge.left == edge.right:
                raise ValueError('An edge must join two distinct existing vertices')
            a, b = edge.left_map, edge.right_map
            if (a.ndim != 2 or b.ndim != 2 or not a.shape[0] or a.shape[0] != b.shape[0]
                    or a.shape[1] != self.dimensions[edge.left]
                    or b.shape[1] != self.dimensions[edge.right]):
                raise ValueError('Restriction maps must share their edge stalk and match their vertices')
            if any(m.dtype != self.dtype or m.device != self.device or not torch.isfinite(m).all()
                   for m in (a, b)):
                raise ValueError('Finite restrictions with one dtype and device are required')
        self.offsets = (0, *torch.tensor(self.dimensions).cumsum(0).tolist())
        self.size = sum(self.dimensions)
        self.edge_dimensions = tuple(edge.left_map.shape[0] for edge in self.edges)
        self.edge_size = sum(self.edge_dimensions)

    def _state(self, value, size):
        if (value.ndim < 1 or value.shape[-1] != size or value.dtype != self.dtype
                or value.device != self.device or not torch.isfinite(value).all()):
            raise ValueError('A finite state in this sheaf coordinate space is required')

    def vertex(self, state, index):
        return state[..., self.offsets[index]:self.offsets[index + 1]]

    def coboundary(self, state):
        self._state(state, self.size)
        return torch.cat([self.vertex(state, e.right) @ e.right_map.T
                          - self.vertex(state, e.left) @ e.left_map.T for e in self.edges], -1)

    def adjoint(self, edge_values):
        self._state(edge_values, self.edge_size)
        vertices = [edge_values.new_zeros(*edge_values.shape[:-1], d) for d in self.dimensions]
        for edge, value in zip(self.edges, edge_values.split(self.edge_dimensions, -1)):
            vertices[edge.left] = vertices[edge.left] - value @ edge.left_map
            vertices[edge.right] = vertices[edge.right] + value @ edge.right_map
        return torch.cat(vertices, -1)

    def laplacian(self, state):
        return self.adjoint(self.coboundary(state))

    def energy(self, state):
        return .5 * self.coboundary(state).square().sum(-1)

    def matrix(self):
        """Dense diagnostic only; ordinary residual application uses edge maps."""
        return self.coboundary(torch.eye(self.size, dtype=self.dtype, device=self.device)).T

    def specification(self):
        return {'type': 'finite-cellular-sheaf-018', 'dimensions': list(self.dimensions),
                'dtype': str(self.dtype).removeprefix('torch.'),
                'edges': [{'left': e.left, 'right': e.right,
                           'left_map': e.left_map.detach().cpu().tolist(),
                           'right_map': e.right_map.detach().cpu().tolist()} for e in self.edges]}

    @classmethod
    def from_specification(cls, specification):
        if (specification.get('type') != 'finite-cellular-sheaf-018'
                or specification.get('dtype') not in ('float32', 'float64')):
            raise ValueError('Use an explicit supported sheaf specification')
        dtype = getattr(torch, specification['dtype'])
        return cls(specification['dimensions'],
                   [Edge(e['left'], e['right'], torch.tensor(e['left_map'], dtype=dtype),
                         torch.tensor(e['right_map'], dtype=dtype)) for e in specification['edges']])

    def spectral_bound(self):
        # The infinity norm bounds every eigenvalue of the symmetric Laplacian.
        d = self.matrix()
        return (d.T @ d).abs().sum(-1).max()

    def polynomial(self, state, coefficients, *, rho=None):
        """Convex Chebyshev filter with a checked fixed-operator bound.

        Degree K has at most K-edge dependence for these fixed restrictions and
        coefficients. Globally conditioned maps/coefficients have extra input
        dependencies and are outside this statement.
        """
        self._state(state, self.size)
        c = torch.as_tensor(coefficients, dtype=self.dtype, device=self.device)
        if (c.ndim != 1 or not c.numel() or not torch.isfinite(c).all()
                or bool((c < 0).any()) or not torch.allclose(c.sum(), c.new_tensor(1.), atol=1e-7, rtol=1e-7)):
            raise ValueError('A finite convex polynomial combination is required')
        required = self.spectral_bound().detach()
        rho = required if rho is None else torch.as_tensor(rho, dtype=self.dtype, device=self.device)
        if rho.ndim or not torch.isfinite(rho) or rho < required or rho < 0:
            raise ValueError('The declared spectral bound is below the verified bound')
        if float(rho) == 0:
            return state * c.sum()
        apply = lambda x: x - 2 * self.laplacian(x) / rho
        previous = state
        output = c[0] * previous
        if len(c) == 1:
            return output
        current = apply(state)
        output = output + c[1] * current
        for coefficient in c[2:]:
            following = 2 * apply(current) - previous
            output = output + coefficient * following
            previous, current = current, following
        return output


class CellAttachment:
    """Attach k free coordinates using the full-row-rank chart R=[I,A].

    B and A may be differentiable learned tensors. The chart guarantees rank,
    but not useful semantics, good conditioning for arbitrary values, or a
    task benefit. Intrinsic ordering is (old state, free eta, disagreement w).
    """

    def __init__(self, old, vertex, b, a):
        if type(vertex) is not int or not 0 <= vertex < len(old.dimensions):
            raise ValueError('Attachment needs an existing vertex')
        if (b.ndim != 2 or a.ndim != 2 or not b.shape[0] or not a.shape[1]
                or b.shape[0] != a.shape[0] or b.shape[1] != old.dimensions[vertex]):
            raise ValueError('B and A must define a nonempty edge and new free coordinates')
        if any(m.dtype != old.dtype or m.device != old.device or not torch.isfinite(m).all() for m in (a, b)):
            raise ValueError('Attachment restrictions must share the old finite coordinate space')
        self.old, self.vertex, self.b, self.a = old, vertex, b, a
        self.r, self.k = a.shape
        self.new_dimension = self.r + self.k
        self.size = old.size + self.new_dimension
        restriction = torch.cat((torch.eye(self.r, dtype=old.dtype, device=old.device), a), -1)
        self.enlarged = FiniteSheaf((*old.dimensions, self.new_dimension),
            (*old.edges, Edge(vertex, len(old.dimensions), b, restriction)))

    def encode(self, old_state, free=None, disagreement=None):
        self.old._state(old_state, self.old.size)
        shape = old_state.shape[:-1]
        free = old_state.new_zeros(*shape, self.k) if free is None else free
        disagreement = old_state.new_zeros(*shape, self.r) if disagreement is None else disagreement
        self.old._state(free, self.k)
        self.old._state(disagreement, self.r)
        if free.shape[:-1] != shape or disagreement.shape[:-1] != shape:
            raise ValueError('Attachment coordinates require the same explicit batch shape')
        constrained = self.old.vertex(old_state, self.vertex) @ self.b.T - free @ self.a.T + disagreement
        return torch.cat((old_state, constrained, free), -1)

    def decode(self, state):
        self.enlarged._state(state, self.size)
        old_state, constrained, free = state.split((self.old.size, self.r, self.k), -1)
        disagreement = constrained + free @ self.a.T - self.old.vertex(old_state, self.vertex) @ self.b.T
        return old_state, free, disagreement

    def transform(self, intrinsic):
        self.enlarged._state(intrinsic, self.size)
        return self.encode(*intrinsic.split((self.old.size, self.k, self.r), -1))

    def inverse(self, state):
        return torch.cat(self.decode(state), -1)

    def _scatter(self, values):
        start, stop = self.old.offsets[self.vertex:self.vertex + 2]
        return torch.cat((values.new_zeros(*values.shape[:-1], start), values,
                          values.new_zeros(*values.shape[:-1], self.old.size - stop)), -1)

    def transpose(self, state_covector):
        """Apply T^T, including the old-coordinate contribution of the new edge."""
        self.enlarged._state(state_covector, self.size)
        old, constrained, free = state_covector.split((self.old.size, self.r, self.k), -1)
        return torch.cat((old + self._scatter(constrained @ self.b),
                          free - constrained @ self.a, constrained), -1)

    def inverse_transpose(self, intrinsic_covector):
        self.enlarged._state(intrinsic_covector, self.size)
        old, free, disagreement = intrinsic_covector.split((self.old.size, self.k, self.r), -1)
        return torch.cat((old - self._scatter(disagreement @ self.b), disagreement,
                          free + disagreement @ self.a), -1)

    def metric(self, state):
        return self.inverse_transpose(self.inverse(state))

    def inverse_metric(self, covector):
        return self.transform(self.transpose(covector))

    def metric_gradient(self, state):
        return self.inverse_metric(self.enlarged.laplacian(state))

    def implicit_step(self, state, duration):
        """Backward Euler for precisely the uncoupled metric consistency flow.

        This step is dissipative. It is not a reversible echo or the complete
        owner's dynamics. Old-flow preservation is for this stated transition.
        """
        if not isinstance(duration, (float, int)) or not math.isfinite(duration) or duration < 0:
            raise ValueError('Use a finite nonnegative step duration')
        old, free, disagreement = self.decode(state)
        d = self.old.matrix()
        system = torch.eye(self.old.size, dtype=old.dtype, device=old.device) + duration * d.T @ d
        evolved = torch.linalg.solve(system, old.reshape(-1, self.old.size).T).T.reshape_as(old)
        return self.encode(evolved, free, disagreement / (1 + duration))

    def matrix(self):
        return self.transform(torch.eye(self.size, dtype=self.old.dtype, device=self.old.device)).T

    def storage(self):
        return {
            'old_state_scalars': self.old.size,
            'new_state_scalars': self.size,
            'added_free_scalars': self.k,
            'new_state_bytes_per_case': self.size * self.a.element_size(),
            'new_restriction_bytes': (self.a.numel() + self.b.numel()) * self.a.element_size(),
            'dense_transform_bytes_if_requested': self.size ** 2 * self.a.element_size(),
            'scope': 'state and new restrictions only; excludes gradients, solver workspace and process memory',
        }

    def specification(self):
        return {'type': 'full-row-rank-attachment-018', 'old': self.old.specification(),
                'vertex': self.vertex, 'b': self.b.detach().cpu().tolist(),
                'a': self.a.detach().cpu().tolist()}

    @classmethod
    def from_specification(cls, specification):
        if specification.get('type') != 'full-row-rank-attachment-018':
            raise ValueError('Use an explicit supported attachment specification')
        old = FiniteSheaf.from_specification(specification['old'])
        return cls(old, specification['vertex'],
                   torch.tensor(specification['b'], dtype=old.dtype),
                   torch.tensor(specification['a'], dtype=old.dtype))


def from_clifford_field(field, *, dtype=None):
    """Use the actual retained owner's maps; do not construct a substitute model."""
    from .clifford_sheaf import lift_rotation
    from .gauge import adjoint_rotations

    restriction = lift_rotation(adjoint_rotations(field.links).transpose(-1, -2))
    if dtype is not None:
        restriction = restriction.to(dtype=dtype)
    n = field.nodes
    identity = torch.eye(8, dtype=restriction.dtype, device=restriction.device)
    return FiniteSheaf((8,) * n,
        [Edge(i, (i + 1) % n, restriction[i], identity) for i in range(n)])
