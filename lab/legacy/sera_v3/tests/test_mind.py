"""SERA's mind lives a world end to end with the frozen judge (mechanics only; skill is measured by sera_check)."""
import torch

from ccops5.core import checker, grammar
from legacy.sera_v3 import imagine as I, mind as SM, worlds as SW


def test_lives_a_world_and_the_checker_agrees():
    torch.manual_seed(0)
    model = I.Imagination().eval()                     # untrained: the judge must still keep "sure" honest
    w = SW.make(6, 0, 1, situations=3)
    r = SM.Mind(model, w.sigma, budget=4).live(w)
    assert r.throws >= 6 and r.own_pushes <= 4
    assert r.families_tracked >= len(grammar.space())
    if r.sure:
        ok, why = checker.check(r.certificate, r.ledger.throws, w.sigma)
        assert ok, why
        assert grammar.canonical(r.claim) == grammar.canonical(w.spec.family)
    assert isinstance(r.gap, str) and r.gap


def test_open_terms_follow_imagined_mass():
    props = [((('product', 'straight', 'straight'),), 0.5), ((('speed', 'straight'),), 0.3),
             ((('power', 'speed', 0.4),), 0.1), ((('drive', 'sin', 2.5),), 0.01)]
    terms = SM._open_terms(props)
    assert ('product', 'straight', 'straight') in terms
    assert ('power', 'speed', 0.4) in terms and ('power', 'speed', 0.3) in terms     # exponent neighbours
    assert ('drive', 'sin', 2.5) not in terms                                         # below OPEN_MASS


def test_screen_only_skips_certificates_that_would_fail():
    """independent review review F5: whenever the cheap screen says no, the judge's own certify must also say no."""
    from ccops5.core import truth
    checked = 0
    for level, idx, extra in ((1, 3, ()), (2, 4, ()), (3, 5, ('power', 'speed', 0.4))):
        w = SW.make(7, idx, level, situations=2)
        inv = tuple(t for t in w.spec.family if t[0] in ('product', 'power', 'drive')) + ((extra,) if extra else ())
        ledger = truth.Ledger(grammar.space(inventions=inv), w.sigma)
        for n, t in enumerate(w.throws):
            ledger.add(t)
            if n not in (1, len(w.throws) - 1):
                continue
            top = sorted(ledger.families, key=lambda f: -ledger.Q[f])[:3]
            for fam in top:
                if not SM._screen(ledger, fam):
                    assert not truth.certify(ledger, fam, 0.2).accepted, (level, n, fam)
                    checked += 1
    assert checked > 0



def test_the_final_certificate_is_on_the_final_ledger(monkeypatch):
    """P2 gate diagnosis (2026-09-25, L2-02): when the last screen said no, live() kept a certificate made on fewer
    throws, so the self-report explained an earlier state. The final certificate must be on every throw made."""
    from ccops5.core import truth
    torch.manual_seed(0)
    calls = []

    def screen_once(ledger, leader):
        calls.append(1)
        return len(calls) == 1                       # certify once, early; the later screens all say no

    monkeypatch.setattr(SM, '_screen', screen_once)
    w = SW.make(6, 0, 1, situations=3)
    r = SM.Mind(I.Imagination().eval(), w.sigma, budget=4).live(w)
    assert r.own_pushes >= 1
    assert r.certificate.digest == truth.digest(r.ledger.throws)
