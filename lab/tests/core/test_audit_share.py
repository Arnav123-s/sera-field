"""T3-b3 (plan rev 3, T3 item 3: cached fits; T-S on Colab 2026-09-26: masked-term lives take hours because each
'new rival' round rebuilds the ledger and the universe audit starts from nothing). A superset's fit is a function of
the throws, the superset, the claim, the early-exit level and the in-space laws inside the superset (they give its
embedded starts and its best member) - nothing else. A world-level cache keyed by exactly those inputs, shared by the
ledgers the mind rebuilds, returns the same fit for the same inputs. Written before the code.
  - exact: after a rebuild that adds a new term, the audit with the shared cache records exactly what a fresh audit
    records (the same rivals in the same order, every e-value bit for bit, the same first weak rival and reason), and
    fits fewer supersets;
  - independent: a ledger has no shared cache unless one is given, and the checker never gives one.
"""
import inspect

import numpy as np
import pytest

from ccops5.core import checker, grammar, likelihood as L, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
DRAG = (('speed', 'straight'),)
NEW = ('piece', 'speed', 'tanh', 0.5)          # a term that joins the ledger between the two audits


def _world(seed=3, situations=3, pushes=(4.0, 0.3, -4.0, -0.3), hold=1.2):
    kk, aa, bb = grammar.codes(DRAG)
    rng = np.random.default_rng(seed)
    throws = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            act = W.Action(((0.0, hold, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, np.array([-0.5]), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            throws.append(W.Throw(k, len(throws), act, xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    return throws


def _ledger(throws, inventions=(), shared=None):
    ledger = truth.Ledger(grammar.space(inventions=inventions), SIGMA)
    if shared is not None:
        ledger.audit_shared = shared
    for t in throws:
        ledger.add(t)
    return ledger


def _counting(monkeypatch):
    calls = []
    real = L.sup_fit
    monkeypatch.setattr(L, 'sup_fit', lambda *a, **k: calls.append(1) or real(*a, **k))
    return calls


SUPERSET = (('speed', 'cubic'), NEW)          # a law outside the space without the claim's term, as the audit fits


def test_the_shared_key_holds_the_fitting_policy_and_the_throws_bytes(monkeypatch):
    """V37E (independent review): a fit made under one knock mode is never served under the other, and a throw changed
    in place (same count) is never served a fit of the old throws."""
    throws = _world(situations=1, pushes=(4.0, -4.0))
    claim = grammar.canonical(DRAG)
    mu = {0: 0.8}
    shared = {}
    calls = _counting(monkeypatch)
    truth.audit_fit(_ledger(throws, shared=shared), SUPERSET, mu, claim)
    truth.audit_fit(_ledger(throws, shared=shared), SUPERSET, mu, claim)
    assert len(calls) == 1                                          # the same inputs: served from the cache
    monkeypatch.setattr(L, 'KNOCK', 'object')
    truth.audit_fit(_ledger(throws, shared=shared), SUPERSET, mu, claim)
    assert len(calls) == 2                                          # another fitting policy: fitted again
    monkeypatch.setattr(L, 'KNOCK', 'throw')
    led = _ledger(throws, shared=shared)
    led.throws[0].x[3] += 1e-3                                      # changed in place, same number of throws
    led._audit.clear()
    truth.audit_fit(led, SUPERSET, mu, claim)
    assert len(calls) == 3


def test_the_shared_cache_hands_out_copies(monkeypatch):
    throws = _world(situations=1, pushes=(4.0, -4.0))
    claim = grammar.canonical(DRAG)
    mu = {0: 0.8}
    shared = {}
    first = truth.audit_fit(_ledger(throws, shared=shared), SUPERSET, mu, claim)
    kept = first.loglik
    first.loglik = 1e9                                              # a caller that edits what it was given
    again = truth.audit_fit(_ledger(throws, shared=shared), SUPERSET, mu, claim)
    assert again.loglik == kept


def test_a_ledger_has_no_shared_cache_unless_given_and_the_checker_never_gives_one():
    assert getattr(truth.Ledger(grammar.space(), SIGMA), 'audit_shared', None) is None
    assert 'audit_shared' not in inspect.getsource(checker)


@pytest.mark.slow
def test_the_shared_cache_records_exactly_what_a_fresh_audit_does(monkeypatch):
    throws = _world()
    claim = grammar.canonical(DRAG)
    thr = grammar.log_threshold(claim, 1e-3)
    shared = {}
    truth.universe_audit(_ledger(throws, shared=shared), claim, thr)          # round 1 fills the cache
    assert shared
    calls = []
    real = L.sup_fit
    monkeypatch.setattr(L, 'sup_fit', lambda *a, **k: calls.append(1) or real(*a, **k))
    cached = truth.universe_audit(_ledger(throws, (NEW,), shared=shared), claim, thr)   # round 2: NEW joined
    n_cached = len(calls)
    fresh = truth.universe_audit(_ledger(throws, (NEW,)), claim, thr)
    n_fresh = len(calls) - n_cached
    (r_c, w_c, why_c), (r_f, w_f, why_f) = cached, fresh
    assert list(r_c) == list(r_f)
    assert all(r_c[b] == r_f[b] for b in r_f)
    assert (w_c, why_c) == (w_f, why_f)
    assert n_cached < n_fresh, (n_cached, n_fresh)
    print(f'round 2 superset/member fits: {n_cached} with the shared cache, {n_fresh} fresh; {len(r_f)} rivals')
