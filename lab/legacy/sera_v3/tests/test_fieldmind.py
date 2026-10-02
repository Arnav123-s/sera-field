"""T4: SERA's mind driven by the Field (field=True). The exact belief picks the laws the judge weighs, Box-Hill among
the most believed laws picks each push (designed programs plus SERA's own), and the world's final belief joins the
faded memory. Everything the judge decides is unchanged; a sure claim is re-checked by the independent checker."""
import math

import pytest

from ccops5.core import checker, grammar


@pytest.mark.slow
def test_the_field_mind_lives_a_world_and_remembers_it():
    from legacy.sera_v3 import field as F, mind as SM, worlds as SW
    w = SW.make(1, 9001, 1, 'dream')
    mem = F.Memory()
    r = SM.Mind(None, w.sigma, eps=0.2, budget=2 * w.n_situations, design=True, field=True, memory=mem).live(w)
    assert r.proposals and sum(p for _, p in r.proposals) <= 1 + 1e-9
    assert all(math.isfinite(p) for _, p in r.proposals)
    assert mem.protos, 'the world was not remembered'
    if r.sure:
        ok, why = checker.check(r.certificate, r.ledger.throws, w.sigma)
        assert ok, why
        assert grammar.contains(grammar.canonical(w.spec.family), grammar.canonical(r.claim))
    print(f'field mind: truth {grammar.name(w.spec.family)}; claim {grammar.name(r.claim)} sure={r.sure}; '
          f'{r.own_pushes} own pushes; top belief {grammar.name(r.proposals[0][0])} {r.proposals[0][1]:.3f}')


def test_a_knocked_object_stays_out_of_the_fields_evidence(monkeypatch):
    """independent review T2/T4 review M3: with per-object knocks (M-1) a knocked object is in the leader's posterior; its throws
    must not enter the Field's evidence table as if unknocked."""
    import numpy as np
    from ccops5.core import likelihood as L, paths, truth, worlds as W
    from legacy.sera_v3 import field as F, mind as SM
    monkeypatch.setattr(L, 'KNOCK', 'object')
    law = grammar.canonical((('position', 'straight'), ('speed', 'straight')))
    kk, aa, bb = grammar.codes(law)
    rng = np.random.default_rng(5)
    throws = []
    for k in range(3):
        m = float(rng.uniform(0.6, 2.5))
        t0, amp = (0.8, 1.5) if k == 1 else (0.0, 0.0)
        for j, u in enumerate((1.0, -0.6)):
            xs, vs = paths.simulate(W.hand(u), 1 / m, kk, aa, bb, np.array([-2.0, -0.8]), 1.0, 1.0, t0, amp)
            nr = np.random.default_rng([5, k, j])
            throws.append(W.Throw(k, len(throws), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    ledger = truth.Ledger([law], (0.001, 0.001))
    for t in throws:
        ledger.add(t)
    assert 1 in ledger.post[law].order                    # the knocked object is in the judge's posterior ...
    mind = SM.Mind(None, (0.001, 0.001), field=True)
    mind._prior = F.normalize(F.prior_logp())
    mind._belief(ledger)
    assert 1 not in mind._mu and {0, 2} <= set(mind._mu)  # ... but not in the Field's evidence
