"""T1 (independent review review of truth-v2, 20:50 and 21:00): a grown formula claim needs a SIZE bound on any further curve
along its input, not only a zero-inside test. Isolated on a ledger whose space is the base laws plus the claim, so no
rival can block it.

  bump world:    3 * exp(-x^2/1) - 0.4 * hat(x; 33-knot grid, knot 22 at x = 1.125, +-0.1875)  -> must NOT certify
  control world: 3 * exp(-x^2/1)                                                                -> must certify
Written before the fix. On bcc4081 both worlds were refused: the bump by the adequacy test (the 1e-3 sensors see a 2-eps
bump on every throw), the control by the smooth band (0.21 > 0.2, the bell and the Legendre basis trade off). A first
size bound (revision 5 draft, reverted) inverted the near-singular information matrix and reported 2.9e5 on the
control. truth.grown_band measures the curve the claim leaves out, with the variances from the SVD of the whitened
Jacobian: the band itself must see the bump (at least 1.5 eps), stay stable and below eps on the control.
"""
import math

import numpy as np
import pytest

from ccops5.core import grammar, paths, truth, worlds as W

BELL = ('piece', 'position', 'bell', 1.0)
SIGMA = (0.001, 0.001)


def _world(bump, seed=3, situations=6, height=0.4, knot=22):
    kinds = [8, 7] if bump else [8]
    a = [0, 0] if bump else [0]
    b = [grammar.code(BELL)[2], 2 * 100 + knot] if bump else [grammar.code(BELL)[2]]
    cf = [3.0, -height] if bump else [3.0]
    kinds, a, b, cf = np.array(kinds), np.array(a), np.array(b), np.array(cf, float)
    rng = np.random.default_rng(seed)
    throws = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate((1.0, -1.0, 0.6, -0.6)):
            xs, vs = paths.simulate(W.hand(u), 1 / m, kinds, a, b, cf, 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            throws.append(W.Throw(k, len(throws), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    return throws


def _certify(throws):
    ledger = truth.Ledger(grammar.space() + [(BELL,)], SIGMA)
    for t in throws:
        ledger.add(t)
    return truth.certify(ledger, (BELL,), 0.2)


def _band(throws):
    return truth.grown_band(throws, (BELL,), SIGMA, truth.scope_of(throws), 1e-3 / (len(grammar.space()) + 1))


@pytest.mark.slow
def test_the_band_sees_a_narrow_extra_curve():
    band = _band(_world(bump=True))
    assert 0.3 <= band < math.inf, band


@pytest.mark.slow
def test_the_band_is_stable_and_small_without_the_curve():
    band = _band(_world(bump=False))
    assert band <= 0.2, band


@pytest.mark.slow
def test_a_narrow_extra_curve_is_refused():
    cert = _certify(_world(bump=True))
    assert not cert.accepted
    assert cert.band is None or cert.band > 0.2, cert.band


@pytest.mark.slow
def test_control_without_the_curve_still_certifies():
    cert = _certify(_world(bump=False))
    assert cert.accepted, cert.reasons
