"""Decision 8 (plan revision 4, R4-2; docs/D8_BAND_TEST.md): the band as a test with the claim's own forecast. Written
before the code.

The band says: anything else acting here is at most `band` in size, at the visited cells, at confidence 1 - delta.
Until now its confidence radius came from the flexible model's own forecast score Q_f, which pays the Occam cost of the
nine basis coefficients (about 75 nats). Decision 8 tests H_> ("somewhere in the visited cells the extra force exceeds
the bound") with the claim's forecast Q_A in the numerator. Under the same quadratic approximation the band already
uses (premise Q), the constrained sup has a closed form and the test is the same band formula with
    radius^2 = 2 (log L_f - Q_A + log(1 / delta))   instead of   2 (log L_f - Q_f + log(1 / delta)).
Tests:
  - the claim test's band is narrower than the flexible-score band on a clean world (the claim is right);
  - the band shrinks as the reference score rises, and is infinite (fail-closed) when the radius would be negative;
  - coverage: on worlds with a planted extra force in the basis span (a spring k x under the claim "drag"), the band
    is at least the planted force's largest size over the visited cells, every time (T-D8 (b), small);
  - policy: a certificate records the band test it used, and the checker refuses one made under another."""
import math

import numpy as np
import pytest

from ccops5.core import checker, grammar, likelihood as L, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
DRAG = grammar.canonical((('speed', 'straight'),))
SPRING_DRAG = grammar.canonical((('speed', 'straight'), ('position', 'straight')))


def _throws(k=0.0, seed=0, situations=3, pushes=(4.0, -2.5, 1.5, -4.0)):
    """Throws of drag (-0.5 v) plus a spring (k x), several objects."""
    fam = SPRING_DRAG
    kk, aa, bb = grammar.codes(fam)
    coef = np.array([-0.5 if t == ('speed', 'straight') else k for t in fam])
    rng = np.random.default_rng(seed)
    out = []
    for s in range(situations):
        m = float(rng.uniform(0.8, 2.0))
        for j, u in enumerate(pushes):
            act = W.Action(((0.0, 1.2, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, coef, 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, s, j])
            out.append(W.Throw(s, len(out), act, xs + nr.normal(0, 1e-3, xs.size), vs + nr.normal(0, 1e-3, vs.size)))
    return out


def _q_claim(throws, fam=DRAG):
    return truth.prequential(truth.model_of(fam), throws, SIGMA)[0]


def test_the_claim_test_band_is_narrower_when_the_claim_is_right():
    throws = _throws(k=0.0)
    scope = truth.scope_of(throws)
    ui = truth.band_of(throws, DRAG, SIGMA, scope, 1e-4)
    claim = truth.band_of(throws, DRAG, SIGMA, scope, 1e-4, q_ref=_q_claim(throws))
    assert 0 < claim < ui, (claim, ui)
    print(f'clean drag world: band {ui:.4g} with the flexible score, {claim:.4g} with the claim test '
          f'(ratio {claim / ui:.3f})')


def test_the_band_shrinks_as_the_reference_score_rises_and_fails_closed():
    throws = _throws(k=0.0, seed=1)
    scope = truth.scope_of(throws)
    q = _q_claim(throws)
    lo, hi = (truth.band_of(throws, DRAG, SIGMA, scope, 1e-4, q_ref=q + d) for d in (0.0, 20.0))
    assert hi < lo
    assert truth.band_of(throws, DRAG, SIGMA, scope, 1e-4, q_ref=q + 1e6) == math.inf    # negative radius: refuse


def test_a_planted_force_in_the_basis_span_is_always_covered():
    """T-D8 (b), small: 12 worlds with a spring k x under the claim "drag" (x is P1 of the basis); k is set from a
    first look at the visited cells so the spring's largest size there is 1-3 x eps (where coverage matters)."""
    eps = 0.2
    rng = np.random.default_rng(7)
    for seed in range(12):
        probe = _throws(k=0.0, seed=100 + seed)
        sc = truth.scope_of(probe)
        xs = np.linspace(sc['x'][0], sc['x'][1], truth.GRID)
        xmax = max(abs(xs[i]) for i, _ in sc['cells'])
        k = float(rng.uniform(1.0, 3.0)) * eps / xmax * rng.choice([-1.0, 1.0])
        throws = _throws(k=k, seed=100 + seed)
        scope = truth.scope_of(throws)
        xs = np.linspace(scope['x'][0], scope['x'][1], truth.GRID)
        planted = max(abs(k * xs[i]) for i, _ in scope['cells'])
        band = truth.band_of(throws, DRAG, SIGMA, scope, 1e-4, q_ref=_q_claim(throws))
        assert band >= planted, (seed, k, band, planted)


def test_the_certificate_records_its_band_test_and_the_checker_holds_to_the_policy(monkeypatch):
    monkeypatch.setattr(truth, 'AUDIT', 'wide')              # the audit is not under test here (and costs minutes)
    throws = _throws(k=0.0, seed=2)
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for t in throws:
        ledger.add(t)
    monkeypatch.setattr(truth, 'BAND', 'claim')
    cert = truth.certify(ledger, DRAG, 0.2)
    assert cert.band_test == 'claim'
    monkeypatch.setattr(truth, 'BAND', 'ui')
    ok, why = checker.check(cert, throws, SIGMA)
    assert not ok and any('band test' in w for w in why), why


def test_a_claim_mode_certificate_passes_the_checker_and_states_its_premises(monkeypatch):
    """reviewer VD8 5: an accepted claim-mode certificate is re-derived and accepted by the checker under the same policy,
    and its premise ledger states D8's one-sided Q and the cell limit L (the 'ui' ledger is unchanged)."""
    monkeypatch.setattr(truth, 'AUDIT', 'wide')
    monkeypatch.setattr(truth, 'BAND', 'claim')
    throws = _throws(k=0.0, seed=2)
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for t in throws:
        ledger.add(t)
    cert = truth.certify(ledger, DRAG, 0.2)
    assert cert.accepted, cert.reasons
    ok, why = checker.check(cert, throws, SIGMA)
    assert ok, why
    q = dict((k, w) for k, _, w in cert.premises)['Q']
    assert 'one-sided' in q and 'lattice points' in q
    assert dict((k, w) for k, _, w in truth.premise_ledger('wide', 'laplace'))['Q'] == \
        'the band uses the ellipsoid (quadratic) approximation'


def test_nonfinite_scores_fail_closed():
    """reviewer VD8 5: a nan or infinite reference score gives an infinite band (refuse), never a finite one."""
    throws = _throws(k=0.0, seed=3)
    scope = truth.scope_of(throws)
    for q in (math.nan, -math.inf, math.inf):
        assert truth.band_of(throws, DRAG, SIGMA, scope, 1e-4, q_ref=q) == math.inf, q


def test_an_unknown_band_policy_is_refused_at_import():
    """reviewer VD8 5: CCOPS5_BAND other than 'ui' or 'claim' must not silently compute the 'ui' band."""
    import os
    import subprocess
    import sys
    env = dict(os.environ, CCOPS5_BAND='Claim')
    r = subprocess.run([sys.executable, '-c', 'import ccops5.core.truth'], env=env, capture_output=True, text=True)
    assert r.returncode != 0 and 'CCOPS5_BAND' in r.stderr
