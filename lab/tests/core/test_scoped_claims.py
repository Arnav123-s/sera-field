"""Decision 11 (docs/SCOPED_CLAIMS.md), scoped claims - "A up to eps where it looked":
  - the penalty: without one, fit is unchanged bit for bit; with one, the pushed coefficient reaches the bound and the
    likelihood is never above the unpenalized best (the recorded value is the likelihood alone);
  - scoped_sup: a rival whose best fit already differs from the claim by eps somewhere keeps the plain rule (no
    record); a look-alike gets a record and a bound never above its own best likelihood;
  - the checker's own re-derivation refuses a look-alike record whose gap is not the one its numbers give.
"""
import types

import numpy as np

from ccops5.core import checker, grammar, likelihood as L, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
SPRING = (('position', 'straight'),)
WAVE_X = (('position', 'wave'),)
DRAG = (('speed', 'straight'),)


def _throws(family, coef, pushes=(0.4, -0.4), situations=3, seed=5):
    kk, aa, bb = grammar.codes(family)
    rng = np.random.default_rng(seed)
    out = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            act = W.Action(((0.0, 0.4, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, np.array(coef), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            out.append(W.Throw(k, len(out), act, xs + nr.normal(0, 1e-3, xs.size), vs + nr.normal(0, 1e-3, vs.size)))
    return out


def _ledger(throws):
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for t in throws:
        ledger.add(t)
    return ledger


def test_the_penalty_pushes_one_coefficient_and_reports_the_likelihood_alone():
    ledger = _ledger(_throws(SPRING, [-1.0]))
    model, post = ledger._models[SPRING], ledger.post[SPRING]
    free = L.fit(model, ledger.throws, SIGMA, start=post, iters=40)
    again = L.fit(model, ledger.throws, SIGMA, start=post, iters=40, penalty=None)
    assert again.loglik == free.loglik and np.array_equal(again.coef, free.coef)          # no penalty: unchanged
    b = float(free.coef[0]) + 0.5
    lam = 1e4 / float(free.cov[0, 0])                        # 10^4 times the likelihood's own curvature there
    pushed = L.fit(model, ledger.throws, SIGMA, start=post, iters=80, penalty=(np.array([1.0]), b, lam))
    assert abs(float(pushed.coef[0]) - b) < 1e-3                                           # it reached the bound
    assert pushed.loglik < free.loglik                                                     # the likelihood alone


def test_a_rival_that_already_differs_keeps_the_plain_rule_and_a_look_alike_gets_a_bound():
    ledger = _ledger(_throws(SPRING, [-1.0]))                # small pushes: x stays near 0, where sin x ~ x
    sc = truth.scope_context(ledger, SPRING, 0.2)
    far = ledger.mle(DRAG)                                   # a drag cannot be a spring
    bound, rec = truth.scoped_sup(ledger, DRAG, far, sc)
    assert rec is None and bound == far.loglik
    near = ledger.mle(WAVE_X)
    bound, rec = truth.scoped_sup(ledger, WAVE_X, near, sc)
    assert rec is not None and rec['gap'] < 0.2                                            # a look-alike here
    assert bound <= near.loglik + 1e-6                        # W's best is never above the rival's own best


def test_the_checker_refuses_a_look_alike_record_its_numbers_do_not_give():
    throws = _throws(SPRING, [-1.0])
    ledger = _ledger(throws)
    sc = truth.scope_context(ledger, SPRING, 0.2)
    near = ledger.mle(WAVE_X)
    _, rec = truth.scoped_sup(ledger, WAVE_X, near, sc)
    good = dict(rec, coef_claim=sc['coef_a'])
    cert = types.SimpleNamespace(family=SPRING, eps=0.2, lookalikes={WAVE_X: good})
    assert checker.lookalike_reason(cert, throws) is None
    cert.lookalikes = {WAVE_X: dict(good, gap=good['gap'] + 0.01)}
    assert 'does not re-derive' in checker.lookalike_reason(cert, throws)
    cert.lookalikes = {WAVE_X: dict(good, coef=tuple(c + 5.0 for c in good['coef']))}      # not a look-alike at all
    assert 'does not re-derive' in checker.lookalike_reason(cert, throws)


def test_the_premise_ledger_of_a_scoped_claim_adds_T_and_says_what_S_covers():
    exact = truth.premise_ledger('universe-1', 'laplace', 'throw', 'claim')
    scoped = truth.premise_ledger('universe-1', 'laplace', 'throw', 'claim', 'scoped')
    assert [p[0] for p in scoped] == [p[0] for p in exact] + ['T']
    assert 'at least eps' in dict((p[0], p[2]) for p in scoped)['S']
