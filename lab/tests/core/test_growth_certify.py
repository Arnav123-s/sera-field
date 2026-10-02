"""truth-v2 end to end: a law the frozen truth-v1 judge could not even state (x times |v|) is certified, and the
independent checker agrees; its sub-laws and a neighbouring grown term are rivals it had to beat."""
import numpy as np
import pytest

from ccops5.core import checker, curriculum, grammar, paths, truth, worlds as W


def _world(terms, coefs, seed=1, situations=4, pushes=(1.0, -1.0, 0.6), returns=()):
    """The teacher's pushes, then `returns`: push-pull programs (command u for 0.4 s, then -1.5 u from 0.6 to 1.0 s)
    that bring an object back while it is still out - position and speed of opposite signs."""
    w = curriculum.MultiWorld(seed, 0, 'grown', grammar.canonical(terms), coefs[0], 0, None, [], [], (0.001, 0.001),
                              [], [], ideas=(), coefs=(), hidden_terms=tuple(terms), hidden_coefs=tuple(coefs))
    rng = np.random.default_rng(seed)
    kinds, a, b, cf = w._codes()
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        w.masses.append(m)
        w.bumps.append(None)
        for j, u in enumerate(pushes):
            xs, vs = paths.simulate(W.hand(u), 1 / m, kinds, a, b, cf, 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            w.throws.append(W.Throw(k, len(w.throws), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                                    vs + nr.normal(0, 1e-3, vs.size)))
        for j, u in enumerate(returns, start=len(pushes)):
            act = W.Action(((0.0, 0.4, float(u)), (0.6, 1.0, -1.5 * float(u))))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kinds, a, b, cf, 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            w.throws.append(W.Throw(k, len(w.throws), act, xs + nr.normal(0, 1e-3, xs.size),
                                    vs + nr.normal(0, 1e-3, vs.size)))
    return w


@pytest.mark.slow
@pytest.mark.integration
def test_x_times_abs_v_is_certified_and_checked(monkeypatch):
    # S19 records a 6,158 s pass; the slow runner allows 7,200 s for this node.
    monkeypatch.setattr(truth, 'AUDIT_WORKERS', 0)
    term = ('pprod', 'straight', 'abs')
    # 2026-09-25: the old 4 x 3 teacher world left grown_band's Jacobian at rank 29 of 80, so the band was inf by
    # design since ab56937 (it never passed; diagnosed on truth-v2 c1f907d and sera-v4). 8 objects x 6 pushes both
    # ways resolve both 33-knot cells over the visited readings (gb_probe: band 0.061 <= eps 0.2). The judge is
    # unchanged; the world is richer.
    # 2026-09-26 (Colab, universe-1 policy): refused - 'a rival family is not ruled out: |x| v'. A pushed object slides
    # out and stops, never turning back, so x and v always share a sign and x|v| = |x|v on every reading: a correct
    # refusal (the two-swap look-alike truth-v2's wide rivals left out by design; the universe audit covers it). Two
    # push-pull throws per object bring it back while still out (x, v of opposite signs), where the two laws push
    # opposite ways. The judge and its bars are unchanged; the world can now tell the claim from its look-alike.
    w = _world((term,), [-1.2], situations=8, pushes=(1.0, -1.0, 0.6, -0.6, 0.3, -0.3), returns=(1.0, -1.0))
    rivals = (term, ('pprod', 'straight', 'tanh0.3'), ('product', 'straight', 'straight'))
    ledger = truth.Ledger(grammar.space(inventions=rivals), w.sigma)
    for t in w.throws:
        ledger.add(t)
    assert ledger.best_family() == (term,)
    cert = truth.certify(ledger, (term,), 0.2)
    assert cert.accepted, cert.reasons
    ok, why = checker.check(cert, ledger.throws, w.sigma)
    assert ok, why
