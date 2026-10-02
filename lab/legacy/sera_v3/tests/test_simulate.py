"""The batched simulator moves every term kind exactly as the judge's own simulator (ccops5.core.paths)."""
import numpy as np
import torch

from ccops5.core import grammar, paths
from legacy.sera_v3 import simulate as S


def _case(rng):
    """A random 1-2 term law over every kind, a push program of 1-2 segments, maybe a bump."""
    kinds = []
    for _ in range(int(rng.integers(1, 3))):
        k = int(rng.choice([0, 1, 2, 3, 4, 5, 6]))
        a = {0: rng.integers(0, 3), 1: rng.integers(0, 3), 4: rng.integers(0, 5), 5: rng.integers(0, 2),
             6: rng.integers(0, 2)}.get(k, 0)
        b = {0: rng.integers(0, 5), 1: rng.integers(0, 3), 4: rng.integers(0, 5), 5: rng.integers(1, 41),
             6: rng.integers(1, 81)}.get(k, 0)
        kinds.append((k, int(a), int(b), float(rng.uniform(-3, 3))))
    nseg = int(rng.integers(1, 3))
    t0 = np.sort(rng.uniform(0, 1.2, nseg))
    t1 = t0 + rng.choice([0.2, 0.4, 0.8], nseg)
    force = rng.uniform(-3, 3, nseg)
    bump = (float(rng.choice([0.6, 1.0])), float(rng.choice([-1.5, 1.5]))) if rng.random() < 0.3 else (0.0, 0.0)
    return kinds, float(rng.uniform(0.4, 1.6)), t0, t1, force, bump


def test_matches_paths_float64():
    rng = np.random.default_rng(11)
    cases = [_case(rng) for _ in range(300)]
    T, Smax = 2, 2
    B = len(cases)
    kind = torch.zeros(B, T, dtype=torch.int64); a = torch.zeros_like(kind); b = torch.zeros_like(kind)
    coef = torch.zeros(B, T, dtype=torch.float64)
    t0 = torch.zeros(B, Smax, dtype=torch.float64); t1 = torch.zeros_like(t0); force = torch.zeros_like(t0)
    mu = torch.zeros(B, dtype=torch.float64); bt = torch.zeros_like(mu); ba = torch.zeros_like(mu)
    for i, (terms, m, s0, s1, f, bump) in enumerate(cases):
        for j, (k, aa, bb, c) in enumerate(terms):
            kind[i, j], a[i, j], b[i, j], coef[i, j] = k, aa, bb, c
        t0[i, :len(s0)] = torch.tensor(s0); t1[i, :len(s1)] = torch.tensor(s1); force[i, :len(f)] = torch.tensor(f)
        mu[i], bt[i], ba[i] = m, bump[0], bump[1]
    xs, vs = S.simulate(kind, a, b, coef, mu, t0, t1, force, bt, ba)
    worst = 0.0
    for i, (terms, m, s0, s1, f, bump) in enumerate(cases):
        k = np.array([t[0] for t in terms], np.int64); aa = np.array([t[1] for t in terms], np.int64)
        bb = np.array([t[2] for t in terms], np.int64); cc = np.array([t[3] for t in terms])
        ex, ev = paths.simulate_program(s0, s1, f, m, k, aa, bb, cc, 1.0, 1.0, bump[0], bump[1])
        scale = max(1.0, float(np.max(np.abs(ex))), float(np.max(np.abs(ev))))
        worst = max(worst, float(np.max(np.abs(xs[i].numpy() - ex))) / scale,
                    float(np.max(np.abs(vs[i].numpy() - ev))) / scale)
    assert worst <= 1e-9, worst


def test_family_codes_roundtrip():
    """grammar.codes gives the (kind, a, b) the batched simulator reads, for every family the judge can claim."""
    fam = (('speed', 'straight'), ('power', 'speed', 0.3))
    k, a, b = grammar.codes(grammar.canonical(fam))
    assert list(k) == [0, 5] and list(b) == [0, 3]
