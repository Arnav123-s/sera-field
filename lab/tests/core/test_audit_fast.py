"""T3-b2 (plan rev 3, T3 item 3): the universe audit's exact speed-ups - E1 skip a superset its best in-space member
already keeps within the threshold, E2 stop a superset's fit at the first start above q_A - thr, E3 never fit the same
start twice - leave everything recorded unchanged. Written before the code.
  - golden: universe_audit with AUDIT_FAST on and off gives the same rival list, the same e-values bit for bit, the
    same first rival not ruled out and the same reason - on a world where the claim passes (drag, pushes both ways)
    and one where it is refused (forward pushes: |v| is v), and for a two-term claim;
  - E3: sup_fit with a start given twice returns exactly the fit of the old code (every start fitted), with fewer fits.
"""
import numpy as np
import pytest

from ccops5.core import grammar, likelihood as L, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
DRAG = (('speed', 'straight'),)
SPRING_DRAG = grammar.canonical((('position', 'straight'), ('speed', 'straight')))


def _world(family, coef, pushes, seed=3, situations=3, hold=1.2):
    kk, aa, bb = grammar.codes(family)
    rng = np.random.default_rng(seed)
    throws = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            act = W.Action(((0.0, hold, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, np.array(coef), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            throws.append(W.Throw(k, len(throws), act, xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    return throws


def _audit(throws, claim, fast, monkeypatch, counts=None):
    monkeypatch.setattr(truth, 'AUDIT_FAST', fast)
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for t in throws:
        ledger.add(t)
    claim = grammar.canonical(claim)
    thr = grammar.log_threshold(claim, 1e-3)
    if counts is None:
        return truth.universe_audit(ledger, claim, thr, workers=0)
    bar = ledger.q_claim(claim) - thr + 1e-6
    children, best_member, sup_fit, fit = truth.audit_children, truth._best_member, L.sup_fit, L.fit
    last_fit = {}

    def counted_children(node):
        kids = children(node)
        counts['split'] += bool(kids)
        return kids

    def counted_best(*args, **kwargs):
        best = best_member(*args, **kwargs)
        counts['E1'] += best is not None and best[1].loglik > bar
        return best

    def counted_fit(*args, **kwargs):
        last_fit['iters'] = kwargs.get('iters')
        return fit(*args, **kwargs)

    def counted_sup_fit(*args, **kwargs):
        last_fit.clear()
        result = sup_fit(*args, **kwargs)
        stop = kwargs.get('stop_above')
        # A hit before the 200-iteration retry is sup_fit's actual early return.
        counts['E2'] += (stop is not None and result.ok and result.loglik > stop
                         and last_fit.get('iters') == 40)
        return result

    with monkeypatch.context() as observed:
        observed.setattr(truth, 'audit_children', counted_children)
        observed.setattr(truth, '_best_member', counted_best)
        observed.setattr(L, 'fit', counted_fit)
        observed.setattr(L, 'sup_fit', counted_sup_fit)
        return truth.universe_audit(ledger, claim, thr, workers=0)


CASES = {'drag both ways': (DRAG, (-0.5,), (4.0, 0.3, -4.0, -0.3), DRAG),
         'drag forward only': (DRAG, (-0.5,), (4.0, 0.8, 0.3, 1.5), DRAG),
         'spring and drag': (SPRING_DRAG, (-2.0, -0.5), (4.0, -4.0), SPRING_DRAG)}


def _compare_audits(case, monkeypatch, counts=None):
    family, coef, pushes, claim = CASES[case]
    throws = _world(family, coef, pushes)
    old = _audit(throws, claim, False, monkeypatch)
    new = _audit(throws, claim, True, monkeypatch, counts)
    (r_old, w_old, why_old), (r_new, w_new, why_new) = old, new
    assert list(r_new) == list(r_old), case                       # the same rivals, in the same order
    assert all(r_new[b] == r_old[b] or (np.isnan(r_new[b]) and np.isnan(r_old[b])) for b in r_old), case
    assert (w_new, why_new) == (w_old, why_old), case
    print(f'{case}: {len(r_old)} rivals; first not ruled out: {grammar.name(w_old) if w_old else None} ({why_old})')
    _assert_outcome(case, w_new, why_new)


def _assert_outcome(case, weak, why):
    if case == 'drag forward only':
        assert weak == (('piece', 'speed', 'abs', 0.0),), (weak, why)
        assert why == 'weak', why
    else:
        assert (weak, why) == (None, None), (case, weak, why)


def test_the_fast_audit_records_exactly_what_the_old_one_did(small_audit_universe, monkeypatch):
    # Equality alone must not pass on a subset that loses the speed-ups or
    # refuses both accepting controls. Count real branch hits across all worlds.
    counts = {'split': 0, 'E1': 0, 'E2': 0}
    for case in CASES:
        _compare_audits(case, monkeypatch, counts)
    print('small-universe branch hits:', counts)
    assert all(counts[name] > 0 for name in ('split', 'E1', 'E2')), counts


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.parametrize('case', list(CASES))
def test_full_universe_fast_audit_equivalence(case, full_audit_universe, monkeypatch):
    _compare_audits(case, monkeypatch)


def _old_sup_fit(model, throws, sigma, mu, starts=()):
    """sup_fit as it was before T3-b2 (every start fitted), the reference for E3."""
    start = L.pooled_start(model, throws, mu)
    fits = [L.fit(model, throws, sigma, start=s, iters=40) for s in (start,) + tuple(starts)]
    plain = L.fit(model, throws, sigma, start=start, iters=40, robust=False)
    if np.all(np.isfinite(plain.coef)):
        post = L.Post(np.concatenate([plain.coef, [plain.mu[s] for s in plain.order]]), start.prec, plain.order)
        fits.append(L.fit(model, throws, sigma, start=post, iters=40))
    ok = [f for f in fits if f.ok]
    if not ok:
        return fits[0]
    best = max(ok, key=lambda f: f.loglik)
    if not best.converged:
        again = L.fit(model, throws, sigma, start=L.Post(np.concatenate([best.coef, [best.mu[s] for s in best.order]]),
                                                         start.prec, best.order), iters=200)
        if again.ok and again.loglik >= best.loglik:
            best = again
    return best


def test_a_start_given_twice_is_fitted_once_with_the_same_result(monkeypatch):
    throws = _world(DRAG, (-0.5,), (4.0, -4.0), situations=2)
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for t in throws:
        ledger.add(t)
    wide = grammar.canonical((('piece', 'speed', 'abs', 0.0), ('position', 'straight')))
    starts = truth.embedded_starts(ledger, wide)
    assert starts
    starts = starts + starts[:1]                                   # the same start twice
    mu = ledger.mle(DRAG).mu
    calls = []
    real = L.fit
    monkeypatch.setattr(L, 'fit', lambda *a, **k: calls.append(1) or real(*a, **k))
    ref = _old_sup_fit(truth.model_of(wide), ledger.throws, SIGMA, mu, starts)
    n_old = len(calls)
    got = L.sup_fit(truth.model_of(wide), ledger.throws, SIGMA, mu, starts)
    assert got.loglik == ref.loglik and np.array_equal(got.coef, ref.coef)
    # at least the planted repeat is skipped (first run, 2026-09-25: 6 fits -> 4 - another start coincided too; the
    # result is the same either way, which is what the line above checks)
    assert len(calls) - n_old <= n_old - 1
