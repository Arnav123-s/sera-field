"""truth-v2 (B4, docs/B4_GROWTH.md): the new term kinds the judge's simulator can grow into, written before the code.

kind 7 cell knot: a = input (0 x, 1 v, 2 t), b = G * 100 + k; K = (9, 17, 33)[G] knots on the fixed range of the
       input (x [-3, 3], v [-6, 6], t [0, 2]); hat_k(s) = max(0, 1 - |s - c_k| / h), the end hats constant beyond the
       range, so the K hats sum to 1 everywhere (a cell spans constants and lines of s over its range, nothing more).
kind 8 one-variable piece: a = input, b = op * 16 + i: op 0 |s|, 1 tanh(s / C[i]), 2 exp(-s^2 / C[i]).
kind 9 product of an x-part and a v-part: a, b = part codes: 0-4 the grammar's shapes, 5 |s|, 6-14 tanh(s / C[i]),
       15-23 exp(-s^2 / C[i]).
"""
import math

import numpy as np
import pytest

from ccops5.core import paths

C = (0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0)
RANGES = {0: (-3.0, 3.0), 1: (-6.0, 6.0), 2: (0.0, 2.0)}
KS = (9, 17, 33)


def hat(inp, G, k, s):
    lo, hi = RANGES[inp]
    K = KS[G]
    h = (hi - lo) / (K - 1)
    c = lo + k * h
    if k == 0 and s <= c:
        return 1.0
    if k == K - 1 and s >= c:
        return 1.0
    return max(0.0, 1.0 - abs(s - c) / h)


def part(code, s):
    if code < 5:
        return [s, s * abs(s), math.tanh(s / 0.05), s ** 3, math.sin(s)][code]
    if code == 5:
        return abs(s)
    if code < 15:
        return math.tanh(s / C[code - 6])
    return math.exp(-s * s / C[code - 15])


def value(kind, a, b, x, v, t):
    return paths.term_t(kind, a, b, x, v, t, 1.0, 1.0)


@pytest.mark.parametrize('inp', [0, 1, 2])
@pytest.mark.parametrize('G', [0, 1, 2])
def test_cell_hats(inp, G):
    rng = np.random.default_rng(inp * 10 + G)
    lo, hi = RANGES[inp]
    for s in list(rng.uniform(lo - 2, hi + 2, 60)) + [lo, hi, lo - 5, hi + 5]:
        x, v, t = (s, 0.3, 0.1) if inp == 0 else (0.3, s, 0.1) if inp == 1 else (0.3, 0.2, s)
        vals = [value(7, inp, G * 100 + k, x, v, t) for k in range(KS[G])]
        assert all(abs(vv - hat(inp, G, k, s)) < 1e-12 for k, vv in enumerate(vals))
        assert abs(sum(vals) - 1.0) < 1e-12                       # a partition of unity: constants are in the span


def test_one_variable_pieces_and_products():
    rng = np.random.default_rng(3)
    for _ in range(200):
        x, v, t = rng.uniform(-4, 4), rng.uniform(-7, 7), rng.uniform(0, 2)
        for inp, s in ((0, x), (1, v), (2, t)):
            assert abs(value(8, inp, 0, x, v, t) - abs(s)) < 1e-12
            for i, c in enumerate(C):
                assert abs(value(8, inp, 16 + i, x, v, t) - math.tanh(s / c)) < 1e-12
                assert abs(value(8, inp, 32 + i, x, v, t) - math.exp(-s * s / c)) < 1e-12
        for pa in range(24):
            for pb in (0, 5, 9, 20):
                assert abs(value(9, pa, pb, x, v, t) - part(pa, x) * part(pb, v)) < 1e-12


def test_state_derivatives_match_central_differences():
    rng = np.random.default_rng(5)
    cases = [(7, 0, 1 * 100 + 4), (7, 1, 0 * 100 + 3), (8, 0, 0), (8, 1, 16 + 2), (8, 0, 32 + 4), (9, 0, 5),
             (9, 7, 17), (9, 3, 12)]
    for kind, a, b in cases:
        for _ in range(40):
            x, v = rng.uniform(-2.5, 2.5), rng.uniform(-5, 5)
            if kind == 7 or (kind in (8, 9) and (abs(x) < 1e-3 or abs(v) < 1e-3)):
                # hats have kinks at knots; |s| at 0: test away from them
                lo, hi = RANGES[a] if kind == 7 else (0, 0)
                if kind == 7:
                    K = KS[b // 100]
                    h = (hi - lo) / (K - 1)
                    s = x if a == 0 else v
                    if min(abs((s - lo) / h - round((s - lo) / h)), 1.0) < 1e-3:
                        continue
            dx, dv = paths._dterm(kind, a, b, x, v, 1.0, 1.0)
            e = 1e-6
            nx = (paths.term(kind, a, b, x + e, v, 1.0, 1.0) - paths.term(kind, a, b, x - e, v, 1.0, 1.0)) / (2 * e)
            nv = (paths.term(kind, a, b, x, v + e, 1.0, 1.0) - paths.term(kind, a, b, x, v - e, 1.0, 1.0)) / (2 * e)
            assert abs(dx - nx) <= 1e-5 * max(1.0, abs(nx)) and abs(dv - nv) <= 1e-5 * max(1.0, abs(nv)), (kind, a, b)


def test_old_kinds_unchanged():
    """Every truth-v1 term kind gives the same numbers as before (the new kinds are added, nothing else moves)."""
    rng = np.random.default_rng(9)
    for _ in range(100):
        x, v, t = rng.uniform(-3, 3), rng.uniform(-5, 5), rng.uniform(0, 2)
        assert value(0, 1, 1, x, v, t) == v * abs(v)
        assert value(5, 1, 25, x, v, t) == np.sign(v) * abs(v) ** 2.5
        assert value(6, 0, 25, x, v, t) == np.sin(2.5 * t)
        assert value(6, 1, 40, x, v, t) == np.cos(4.0 * t)
