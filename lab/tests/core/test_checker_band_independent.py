"""independent review T1-b: the checker re-derives a grown claim's band by other numerics (finite-difference sensitivities, QR
projection, minimum-norm variances, columns from their definitions). Written before the fix.

2026-09-25: the first version also asked the whole check to pass on the T1 test ledger (base laws plus the claim).
That ledger is not the checker's idea space (grammar.space with the claim's invention adds every pair with it), so the
check refused it for "idea space size is wrong" before the band. It also halved the band, which the plain re-run
catches first. The fault T1-b guards against is one SHARED by certify and its re-run, so it is planted here the same
way: the certificate states half the band that its own definition gives, and the independent path must refuse it."""
import dataclasses

import pytest

from ccops5.core import checker, grammar, truth
from tests.core import test_curve_size_bound as T1


@pytest.mark.slow
def test_the_independent_band_agrees_and_an_understated_band_is_refused():
    throws = T1._world(bump=False)
    ledger = truth.Ledger(grammar.space() + [(T1.BELL,)], T1.SIGMA)
    for t in throws:
        ledger.add(t)
    cert = truth.certify(ledger, (T1.BELL,), 0.2)
    n = ledger.n_space                                   # the test ledger's space (the checker's policy delta)
    own = checker._band_independent(cert, throws, T1.SIGMA, n)
    assert abs(own - cert.band) <= checker.BAND_AGREE * cert.band, (own, cert.band)
    assert checker.band_reason(cert, throws, T1.SIGMA, n) is None
    low = dataclasses.replace(cert, band=cert.band * 0.5)
    assert 'does not re-derive independently' in (checker.band_reason(low, throws, T1.SIGMA, n) or '')


@pytest.mark.slow
def test_the_independent_band_agrees_on_the_bump_world():
    """B (ebecb4c review): agreement also where the band is large (the narrow 2-eps bump T1 must refuse)."""
    throws = T1._world(bump=True)
    ledger = truth.Ledger(grammar.space() + [(T1.BELL,)], T1.SIGMA)
    for t in throws:
        ledger.add(t)
    cert = truth.certify(ledger, (T1.BELL,), 0.2)
    own = checker._band_independent(cert, throws, T1.SIGMA, ledger.n_space)
    assert cert.band is not None and abs(own - cert.band) <= checker.BAND_AGREE * cert.band, (own, cert.band)
