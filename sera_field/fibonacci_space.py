"""Finite chiral Fibonacci fusion spaces for conditional branch computation.

Conventions: 0 is the vacuum, 1 is tau; counterclockwise right-handed R phases
are exp(-4 pi i/5), exp(3 pi i/5). F is real in the pinned gauge of
Bseiso et al., arXiv:2407.21761v2, section II.1. This is a CPU simulation.
The class constructs every represented measurement outcome. It has no factual
memory write or knowledge-verification authority.
"""
import math
from itertools import product

import torch


def fusion(a, b):
    if a not in (0, 1) or b not in (0, 1):
        raise ValueError('Fibonacci charges are vacuum=0 and tau=1')
    return (b,) if a == 0 else ((a,) if b == 0 else (0, 1))


def f_symbol(a, b, c, total, left, right):
    """((a b)_left c)_total -> (a (b c)_right)_total."""
    if (left not in fusion(a, b) or total not in fusion(left, c)
            or right not in fusion(b, c) or total not in fusion(a, right)):
        return 0.
    if a == b == c == total == 1:
        phi = (1 + math.sqrt(5)) / 2
        return (-1 if left == right == 1 else 1) / (phi if left == right else math.sqrt(phi))
    return 1.


def leaves(tree):
    if type(tree) is int:
        return (tree,)
    if not isinstance(tree, tuple) or len(tree) != 2:
        raise ValueError('An ordered binary fusion tree is required')
    return leaves(tree[0]) + leaves(tree[1])


def fusion_basis(tree, charges, total):
    if leaves(tree) != tuple(range(len(charges))):
        raise ValueError('Each ordered leaf must occur exactly once')
    if total not in (0, 1) or any(c not in (0, 1) for c in charges):
        raise ValueError('Use explicit Fibonacci charges')
    def expand(node):
        key = leaves(node)
        if type(node) is int:
            return [{key: charges[node]}]
        result = []
        for left, right in product(expand(node[0]), expand(node[1])):
            for charge in fusion(left[leaves(node[0])], right[leaves(node[1])]):
                result.append({**left, **right, key: charge})
        return result
    return [state for state in expand(tree) if state[leaves(tree)] == total]


def recouple_right(tree, charges, total, path=()):
    """An explicit one-edge F move, including unchanged surrounding channels.

    Return the target tree and the target-basis-by-source-basis matrix. This
    permits an independent pentagon check across different fusion trees.
    """
    node = tree
    for step in path:
        if type(node) is int or step not in (0, 1):
            raise ValueError('Invalid fusion-tree path')
        node = node[step]
    if type(node) is int or type(node[0]) is int:
        raise ValueError('A right F move needs ((A,B),C) at the selected node')
    a, b = node[0]; c = node[1]
    replacement = (a, (b, c))
    def replace(current, remaining):
        if not remaining:
            return replacement
        children = list(current)
        children[remaining[0]] = replace(children[remaining[0]], remaining[1:])
        return tuple(children)
    target = replace(tree, path)
    before = fusion_basis(tree, charges, total); after = fusion_basis(target, charges, total)
    matrix = torch.zeros(len(after), len(before), dtype=torch.float64)
    for j, old in enumerate(before):
        for i, new in enumerate(after):
            shared = old.keys() & new.keys()
            if any(old[key] != new[key] for key in shared):
                continue
            matrix[i, j] = f_symbol(old[leaves(a)], old[leaves(b)], old[leaves(c)],
                old[leaves(node)], old[leaves((a, b))], new[leaves((b, c))])
    return target, matrix


class FibonacciSpace:
    """All left-associated fusion paths for 2..10 tau anyons and fixed total."""
    def __init__(self, count=4, total=1, *, handedness=1):
        if type(count) is not int or not 2 <= count <= 10 or total not in (0, 1):
            raise ValueError('Use 2..10 tau anyons and an explicit total charge')
        if handedness not in (-1, 1):
            raise ValueError('Handedness must be +1 or -1')
        self.count, self.total, self.handedness = count, total, handedness
        paths = [(0,)]
        for _ in range(count):
            paths = [p + (c,) for p in paths for c in fusion(p[-1], 1)]
        self.paths = tuple(p for p in paths if p[-1] == total)
        self.dimension = len(self.paths)

    def projectors(self, pair):
        """Charge of adjacent anyons pair,pair+1; pair is one-based."""
        if type(pair) is not int or not 1 <= pair < self.count:
            raise ValueError('An adjacent pair inside this fusion space is required')
        result = []
        for outcome in (0, 1):
            matrix = torch.zeros(self.dimension, self.dimension, dtype=torch.complex128)
            for j, old in enumerate(self.paths):
                for i, new in enumerate(self.paths):
                    if old[:pair] != new[:pair] or old[pair+1:] != new[pair+1:]:
                        continue
                    a, total = old[pair-1], old[pair+1]
                    matrix[i, j] = (f_symbol(a, 1, 1, total, new[pair], outcome)
                                    * f_symbol(a, 1, 1, total, old[pair], outcome))
            result.append(matrix)
        return tuple(result)

    def braid(self, pair, *, inverse=False):
        projectors = self.projectors(pair)
        sign = self.handedness * (-1 if inverse else 1)
        phases = torch.exp(torch.tensor([-4j*math.pi/5, 3j*math.pi/5], dtype=torch.complex128) * sign)
        return sum(phase * projector for phase, projector in zip(phases, projectors))

    def validate_density(self, density):
        if (density.ndim != 2 or density.shape != (self.dimension, self.dimension)
                or density.dtype not in (torch.complex64, torch.complex128)
                or not bool(torch.isfinite(density).all())):
            raise ValueError('One finite density matrix in the declared fusion basis is required')
        tolerance = 2e-6 if density.dtype == torch.complex64 else 1e-11
        if (not torch.allclose(density, density.mH, atol=tolerance, rtol=0)
                or abs(complex(density.trace().detach())-1) > tolerance
                or float(torch.linalg.eigvalsh(density).min().detach()) < -tolerance):
            raise ValueError('The input must already be Hermitian, positive and trace one')

    def measure(self, density, pair):
        """Return both qualified conditional branches and the unread channel.

        A zero-probability outcome has no normalized conditional state. The
        unread state describes a performed measurement whose result is withheld;
        no measurement is represented simply by retaining the original density.
        No probability, clipping or renormalization repairs an invalid input.
        """
        self.validate_density(density)
        branches = []
        for outcome, p in enumerate(self.projectors(pair)):
            p = p.to(dtype=density.dtype, device=density.device)
            substate = p @ density @ p
            probability = substate.trace().real
            # Exact basis-impossible channels are explicit. Tiny negative roundoff
            # is retained in the substate/probability diagnostics, not hidden.
            conditional = substate / probability if float(probability.detach()) > 0 else None
            branches.append({'charge': outcome, 'probability': probability,
                             'substate': substate, 'conditional': conditional})
        return {'outcomes': branches, 'unread': sum(b['substate'] for b in branches),
                'no_measurement': density.clone()}

    def specification(self):
        return {'type': 'finite-chiral-fibonacci', 'anyons': self.count,
                'total_charge': self.total, 'handedness': self.handedness,
                'dimension': self.dimension, 'paths': self.paths,
                'complex128_vector_bytes': 16*self.dimension,
                'complex128_density_bytes': 16*self.dimension**2,
                'source': 'https://arxiv.org/html/2407.21761v2#S2.SS1'}
