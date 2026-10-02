"""truth-v3 T2 (S4 §6.6; docs/SERA_FIELD_THEORY.md v1.1 §15): the refutation API. Premise U says each rival's computed
best fit reaches its true best; anyone may attack it with a witness - a rival law and numbers - and a certificate is
refuted when the witness's likelihood beats Q_A - thr(A) (then that rival was not ruled out). One likelihood
evaluation, so U becomes publicly attackable. Written before the code."""
import numpy as np

import dataclasses

from ccops5.core import grammar, likelihood as L, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
DRAG = (('speed', 'straight'),)
TWIN = (('piece', 'speed', 'abs', 0.0),)       # |v|: the same law as v when every reading has v >= 0


def _world(pushes, seed=3, situations=4):
    kk, aa, bb = grammar.codes(DRAG)
    rng = np.random.default_rng(seed)
    throws = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            xs, vs = paths.simulate(W.hand(u), 1 / m, kk, aa, bb, np.array([-0.8]), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            throws.append(W.Throw(k, len(throws), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    return throws


def _cert(throws):
    return truth.Certificate(family=DRAG, alpha=1e-3, delta=1e-3, eps=0.2, n_space=67, inventions=(),
                             digest=truth.digest(throws), rivals={}, nested={}, band=None, adequacy=None, scope={},
                             accepted=True, reasons=(), numerator=truth.NUMERATOR, audit=truth.AUDIT, knock=L.KNOCK)


def _witness(throws):
    ledger = truth.Ledger([DRAG], SIGMA)
    for t in throws:
        ledger.add(t)
    fit = ledger.mle(DRAG)
    return fit.coef.copy(), dict(fit.mu)


def test_a_look_alike_witness_refutes():
    throws = _world((1.0, 0.6, 1.5, 0.8))                        # forward only: |v| = v on every reading
    coef, mu = _witness(throws)
    refuted, margin = truth.challenge(_cert(throws), TWIN, coef, mu, throws, SIGMA)
    assert refuted and margin < 0, margin


def test_the_same_witness_fails_when_the_data_tell_them_apart():
    throws = _world((1.0, 0.6, -1.0, -0.6))                      # both ways: |v| and v differ
    coef, mu = _witness(throws)
    refuted, margin = truth.challenge(_cert(throws), TWIN, coef, mu, throws, SIGMA)
    assert not refuted and margin > 0, margin


def test_only_a_rival_on_the_certificates_own_throws_can_refute():
    throws = _world((1.0, 0.6, 1.5, 0.8))
    coef, mu = _witness(throws)
    bigger = grammar.canonical(DRAG + (('position', 'straight'),))      # contains the claim: not a rival
    refuted, why = truth.challenge(_cert(throws), bigger, np.append(coef, 0.0), mu, throws, SIGMA)
    assert not refuted and 'rival' in why
    refuted, why = truth.challenge(_cert(throws), TWIN, coef, mu, throws[:-1], SIGMA)
    assert not refuted and 'throws' in why


def test_a_certificate_made_under_another_policy_is_not_challenged():
    """independent review T2/T4 review M1: Q_A is recomputed under the current policy, so a certificate of another knock model,
    numerator or audit cannot be scored - refused, as the checker refuses it."""
    throws = _world((1.0, 0.6, 1.5, 0.8))
    coef, mu = _witness(throws)
    for field, other in (('knock', 'object' if L.KNOCK == 'throw' else 'throw'),
                         ('audit', 'wide' if truth.AUDIT == 'universe-1' else 'universe-1'),
                         ('numerator', 'mu' if truth.NUMERATOR == 'laplace' else 'laplace')):
        cert = dataclasses.replace(_cert(throws), **{field: other})
        refuted, why = truth.challenge(cert, TWIN, coef, mu, throws, SIGMA)
        assert not refuted and 'policy' in why, (field, why)
