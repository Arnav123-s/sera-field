"""T3-a (profile 2026-09-25: 552 of 710 s of a Field-mind world were from-scratch ledger rebuilds): reusing each
family's running state across rebuilds must be exact - the same Q and the same posterior, bit for bit, as a ledger
built from scratch on the same throws - including after the mind added throws to the last ledger directly, and when
new terms bring new families. Written before the code."""
import numpy as np
import pytest

from ccops5.core import grammar, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
LAW = (('position', 'straight'), ('speed', 'straight'))


def _throws(n_obj=3, pushes=(1.0, -0.6), seed=4):
    kk, aa, bb = grammar.codes(LAW)
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n_obj):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            xs, vs = paths.simulate(W.hand(u), 1 / m, kk, aa, bb, np.array([-2.0, -0.8]), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            out.append(W.Throw(k, len(out), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                               vs + nr.normal(0, 1e-3, vs.size)))
    return out


def _same(a, b):
    assert a.families == b.families and len(a.throws) == len(b.throws)
    for f in a.families:
        assert a.Q[f] == b.Q[f], grammar.name(f)                             # bit for bit
        pa, pb = a.post[f], b.post[f]
        assert np.array_equal(pa.mean, pb.mean) and np.array_equal(pa.prec, pb.prec) and pa.order == pb.order


@pytest.mark.slow
def test_a_rebuilt_ledger_equals_one_built_from_scratch(monkeypatch):
    from legacy.sera_v3 import mind as SM
    throws = _throws()
    m = SM.Mind(None, SIGMA)
    m._family_cache, m._last_ledger = {}, None
    first = m._ledger((), throws[:3])
    for t in throws[3:5]:                                   # the mind adds to the live ledger directly
        first.add(t)
    terms = (('product', 'straight', 'straight'),)
    rebuilt = m._ledger(terms, throws)                     # new terms: new families; old ones reused
    monkeypatch.setattr(SM, 'LEDGER_REUSE', False)
    scratch = SM.Mind(None, SIGMA)._ledger(terms, throws)
    _same(rebuilt, scratch)
    assert set(scratch.families) - set(first.families)     # the rebuild really added families
