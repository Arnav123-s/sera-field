"""T3-b1 (plan rev 3, T3 item 3; ua-slow3 2026-09-25: with the universe audit one checker call re-derives a certificate
for about 33 minutes, and tests/core/test_universe_audit.py makes three): the checker refuses a certificate that fails
a cheap policy or coverage test at once, before re-deriving it. Accepted iff no reason, as before - a re-derivation
can only add reasons - so only a refused certificate's list of reasons can get shorter. Written before the code."""
import dataclasses

import numpy as np
import pytest

from ccops5.core import checker, grammar, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
DRAG = (('speed', 'straight'),)


@pytest.fixture(scope='module')
def made():
    kk, aa, bb = grammar.codes(DRAG)
    rng = np.random.default_rng(3)
    throws = []
    for k in range(4):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate((1.0, -1.0)):
            act = W.push_of(u)
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, np.array([-0.8]), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([3, k, j])
            throws.append(W.Throw(k, len(throws), act, xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for t in throws:
        ledger.add(t)
    return truth.certify(ledger, DRAG, 0.2, audit='wide'), throws


def _no_rederiving(monkeypatch):
    def refuse(*a, **k):
        raise AssertionError('the checker re-derived a certificate a cheap test already refuses')
    monkeypatch.setattr(truth, 'certify', refuse)


@pytest.mark.parametrize('forge', ['no audit', 'other audit', 'hole', 'premises', 'laxer alpha'])
def test_a_cheap_reason_refuses_without_re_deriving(made, monkeypatch, forge):
    cert, throws = made
    universe = dataclasses.replace(cert, audit='universe-1', premises=truth.premise_ledger(
        'universe-1', cert.numerator, cert.knock))
    bad = {'no audit': dataclasses.replace(universe, audit='none'),
           'other audit': cert,                                      # made under 'wide': not the policy audit
           'hole': universe,                                         # no universe rival recorded: every pair a hole
           'premises': dataclasses.replace(universe, premises=()),
           'laxer alpha': dataclasses.replace(universe, alpha=0.01)}[forge]
    _no_rederiving(monkeypatch)
    ok, why = checker.check(bad, throws, SIGMA)
    assert not ok and why, forge
