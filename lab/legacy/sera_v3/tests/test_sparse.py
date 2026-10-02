"""The Field's sparse proposer (the author, 2026-09-25 20:00: compressed sensing - Candes, Romberg & Tao 2006 - to find
the few terms the data wants among many, with no bookkeeping; recorded in the plan's memory). Written before the code.

An L1 path over the whole term dictionary - the 11 base ideas and every universe term (truth-v1's invented terms, the
grown pieces and piece products: 878 columns) - computed from the evidence table's sufficient statistics alone. It
proposes; it never proves (look-alike columns such as v, |v| and tanh(v/3) are nearly collinear, far from the
incoherence the recovery theorems need), and the judge never reads it.
  - the solver is exact: its answer meets the lasso's optimality (KKT) conditions, and on an orthogonal design it is
    soft thresholding;
  - its statistics agree with the Field's own evidence table on the Field's 270 columns;
  - pre-registered recall bar (fixed before any run): on 12 fixed worlds made with the judge's simulator (8 objects,
    pushes both ways held 1.2 s, noise 1e-3, masses known), the true law's non-base term - or a column the data cannot
    tell from it (cosine >= 0.995 in the evidence metric) - is among the first 10 terms the path lets in, in >= 11 of
    12; and one proposal costs < 1 s CPU. Seven of the 12 laws lie outside the Field's LAWS (pieces, piece products),
    where the exact belief cannot see them at all.
"""
import time

import numpy as np
import pytest

from ccops5.core import grammar, paths, worlds as W

HOLD = 1.2
PUSHES = (4.0, 0.3, -4.0, -0.3)

RECALL_LAWS = [                                                     # (family, strengths), fixed before any run
    ((('piece', 'speed', 'abs', 0.0), ('position', 'straight')), None),
    ((('piece', 'speed', 'tanh', 0.5), ('position', 'straight')), None),
    ((('piece', 'position', 'bell', 1.0),), None),
    ((('pprod', 'straight', 'tanh1'),), None),
    ((('pprod', 'bell1', 'straight'),), None),
    ((('piece', 'speed', 'bell', 0.5), ('speed', 'straight')), None),
    ((('piece', 'position', 'tanh', 0.3), ('speed', 'straight')), None),
    ((('power', 'speed', 1.5), ('position', 'straight')), None),
    ((('drive', 'sin', 2.3),), None),
    ((('power', 'position', 2.5),), None),
    ((('position', 'straight'), ('speed', 'straight')), None),
    ((('position', 'cubic'),), None),
]


def _strengths(family):
    """A fixed, mild strength per term: restoring for position parts, damping for speed parts, 1.5 otherwise."""
    out = []
    for term in family:
        text = repr(term)
        out.append(-2.0 if 'position' in text or 'bell1' in text else -0.8 if 'speed' in text or 'tanh' in text
                   else 1.5)
    return out


def _world(family, seed):
    family = grammar.canonical(family)
    kk, aa, bb = grammar.codes(family)
    coef = []
    for term, c in zip(family, _strengths(family)):
        coef += [c] * grammar.n_coef((term,))
    rng = np.random.default_rng(seed)
    throws, mu = [], {}
    for k in range(8):
        m = float(rng.uniform(0.6, 2.5))
        mu[k] = 1 / m
        for j, u in enumerate(PUSHES):
            act = W.Action(((0.0, HOLD, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, np.array(coef), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            throws.append(W.Throw(k, len(throws), act, xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    return family, throws, mu


def test_the_lasso_meets_its_optimality_conditions():
    from legacy.sera_v3 import sparse as S
    rng = np.random.default_rng(0)
    X = rng.normal(size=(60, 25))
    X[:, 3] = X[:, 2] + 0.01 * rng.normal(size=60)                  # a look-alike pair, as in the dictionary
    y = X[:, [2, 7, 11]] @ np.array([1.5, -2.0, 0.7]) + 0.1 * rng.normal(size=60)
    G, b = X.T @ X, X.T @ y
    w = np.sqrt(np.diag(G))
    for lam in (5.0, 1.0, 0.1):
        c = S.lasso(G, b, lam, w)
        g = G @ c - b
        on = np.abs(c) > 0
        assert np.allclose(g[on], -lam * w[on] * np.sign(c[on]), atol=1e-6 * max(1.0, lam))
        assert np.all(np.abs(g[~on]) <= lam * w[~on] * (1 + 1e-6) + 1e-9)


def test_the_lasso_is_soft_thresholding_on_an_orthogonal_design():
    from legacy.sera_v3 import sparse as S
    g = np.array([1.0, 4.0, 0.25, 9.0])
    b = np.array([3.0, -1.0, 0.1, 12.0])
    w = np.sqrt(g)
    lam = 0.5
    want = np.sign(b) * np.maximum(np.abs(b) - lam * w, 0.0) / g
    assert np.allclose(S.lasso(np.diag(g), b, lam, w), want, atol=1e-12)


def test_its_statistics_agree_with_the_fields_evidence_table():
    from legacy.sera_v3 import compact as C, field as F, sparse as S
    family, throws, mu = _world(RECALL_LAWS[10][0], 1)
    full, small = S.stats(throws, mu), F.evidence(throws, mu)
    n = len(C.TERMS)
    assert len(S.DICT) == len(grammar.IDEAS) + 259 + 57 + 551 and S.DICT[:n] == C.TERMS
    assert np.allclose(full.G[:n, :n], small.G, rtol=1e-12, atol=1e-9)
    assert np.allclose(full.b[:n], small.b, rtol=1e-12, atol=1e-9)
    assert full.zz == pytest.approx(small.zz, rel=1e-12)


@pytest.mark.slow
def test_the_path_finds_the_true_term_among_its_first_ten():
    from legacy.sera_v3 import sparse as S
    hits, rows, cpu = 0, [], []
    for i, (family, _) in enumerate(RECALL_LAWS):
        family, throws, mu = _world(family, 100 + i)
        st = S.stats(throws, mu)
        t0 = time.process_time()
        entered = S.path(st, 10)
        cpu.append(time.process_time() - t0)
        target = [t for t in family if t not in grammar.IDEAS] or list(family)
        j = S.INDEX[target[0]]
        d = np.sqrt(np.diag(st.G))
        cos = np.abs(st.G[j] / (d[j] * d + 1e-300))
        hit = any(e == j or cos[e] >= 0.995 for e in entered)
        hits += hit
        rows.append((grammar.name(family), hit, [grammar.term_name(S.DICT[e]) for e in entered[:4]]))
    print('\n'.join(f'{name}: {"hit" if h else "MISS"}; first in: {first}' for name, h, first in rows))
    print(f'sparse proposer recall {hits}/12; CPU per proposal max {max(cpu):.3f} s')
    assert hits >= 11, rows
    assert max(cpu) < 1.0
