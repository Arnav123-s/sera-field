"""SERA expresses itself (plan revision 2, P2c): every sentence of its self-report states a claim it can back with a
number from its own records, and the statement checker re-derives every number from the raw sources (the ledger,
the certificate, its foresight, its grade). Written before the module."""
import dataclasses
import types

import numpy as np

from ccops5.core import grammar
from legacy.sera_v3 import express as E, grade as G

A = grammar.canonical((('speed', 'straight'),))
B = grammar.canonical((('speed', 'wave'),))
C = grammar.canonical((('position', 'steps'),))


def _report(accepted=True, verified=None, alarm=False):
    ledger = types.SimpleNamespace(families=[A, B, C], Q={A: 0.0, B: -25.0, C: -300.0}, throws=[None] * 30)
    cert = types.SimpleNamespace(family=A, accepted=accepted, alpha=1e-3, rivals={B: 25.0, C: 300.0}, band=0.12,
                                 eps=0.2, reasons=() if accepted else ('something else could be as large as 0.31 > eps 0.2',),
                                 scope={'x': (-1.0, 2.0), 'v': (-0.5, 1.5)})
    foresight = [dict(situation=0, leader=A, leader_rms=1.1, rival=B, rival_rms=6.0),
                 dict(situation=3, leader=A, leader_rms=250.0, rival=B, rival_rms=240.0),
                 dict(situation=1, leader=A, leader_rms=0.9)]
    r = types.SimpleNamespace(claim=A, sure=accepted, certificate=cert, ledger=ledger, alarm=False,
                              foresight=foresight, q_start={A: 0.0, B: -2.0, C: -150.0},
                              proposals=[(A, 0.6), (B, 0.3), (C, 0.1)], events=((3, 'disturbed'),))
    g = G.grade(ledger, cert, verified=accepted if verified is None else verified, q_start=r.q_start, alarm=alarm)
    return r, g


def test_every_statement_is_verified_against_the_records():
    r, g = _report()
    statements = E.self_report(r, g)
    kinds = {s.kind for s in statements}
    assert {'belief', 'sureness', 'ruled_out', 'question', 'band', 'foresight', 'disturbed', 'imaginations',
            'assumption', 'rests_on'} <= kinds
    for s in statements:
        ok, why = E.check(s, r, g)
        assert ok, (s.text, why)
    text = E.words(statements)
    assert 'wave with speed' in text and 'straight with speed' in text


def test_a_false_statement_is_caught():
    r, g = _report()
    for s in E.self_report(r, g):
        if s.kind == 'ruled_out':
            forged = dataclasses.replace(s, numbers={**s.numbers, 'evidence': s.numbers['evidence'] + 10.0})
            assert not E.check(forged, r, g)[0]
        if s.kind == 'belief':
            forged = dataclasses.replace(s, numbers={**s.numbers, 'sure': not s.numbers['sure']})
            assert not E.check(forged, r, g)[0]


def test_when_unsure_it_says_why_and_claims_no_certainty():
    r, g = _report(accepted=False)
    statements = E.self_report(r, g)
    assert any(s.kind == 'unsure' for s in statements)
    assert not any(s.kind == 'belief' and s.numbers['sure'] for s in statements)
    assert all(E.check(s, r, g)[0] for s in statements)


def test_it_says_where_a_look_alike_parts_and_the_sentence_checks():
    """A sin world pushed gently: sin x and a cubic polynomial stay alike where the pushes reached. SERA must say
    where they part, and that sentence must check against the two laws' fits."""
    from ccops5.core import paths, truth, worlds as W
    wave = grammar.canonical((('position', 'wave'),))
    kk, aa, bb = grammar.codes(wave)
    rng = np.random.default_rng(9)
    ledger = truth.Ledger(grammar.space(), (1e-3, 1e-3))
    for k, mu in enumerate((0.7, 1.0, 1.4, 1.8)):
        for j, u in enumerate((0.5, -0.5)):
            xs, vs = paths.simulate(W.hand(u), mu, kk, aa, bb, np.array([-2.0]), 1.0, 1.0, 0.0, 0.0)
            ledger.add(W.Throw(k, 2 * k + j, W.push_of(u), xs + rng.normal(0, 1e-3, xs.size),
                               vs + rng.normal(0, 1e-3, vs.size)))
    cert = truth.certify(ledger, wave, 0.2)
    r = types.SimpleNamespace(claim=wave, sure=cert.accepted, certificate=cert, ledger=ledger, alarm=False,
                              foresight=[], q_start=dict(ledger.Q), proposals=[(wave, 1.0)], events=())
    g = G.grade(ledger, cert, verified=cert.accepted)
    statements = E.self_report(r, g)
    parting = [s for s in statements if s.kind == 'parting']
    assert not cert.accepted and parting, [s.text for s in statements]
    assert all(E.check(s, r, g)[0] for s in statements), [(s.text, E.check(s, r, g)) for s in statements]


def test_a_certificate_the_checker_did_not_confirm_is_not_claimed():
    """independent review Ex-1: "sure" only for a PROVEN law (certified and confirmed by the independent checker)."""
    r, g = _report(accepted=True, verified=False)
    statements = E.self_report(r, g)
    belief = next(s for s in statements if s.kind == 'belief')
    assert not belief.numbers['sure'] and 'not sure' in belief.text
    assert any(s.kind == 'unverified' for s in statements) and not any(s.kind == 'sureness' for s in statements)
    assert all(E.check(s, r, g)[0] for s in statements)
    forged = dataclasses.replace(belief, numbers={**belief.numbers, 'sure': True})
    forged = dataclasses.replace(forged, text=E.render('belief', forged.numbers))
    assert not E.check(forged, r, g)[0]


def test_words_that_do_not_say_what_the_numbers_say_are_caught():
    """independent review Ex-2: the numbers alone are not enough; the words are re-rendered and must match."""
    r, g = _report()
    for s in E.self_report(r, g):
        if s.kind == 'assumption':
            continue
        assert not E.check(dataclasses.replace(s, text=s.text.replace('I ', 'We ', 1) + ' Certainly.'), r, g)[0], s.text


def test_after_an_alarm_imaginations_are_not_graded_against_each_other():
    """independent review Ex-3: when something outside every tested law is here, the report must not count laws as close or
    ruled out by the ladder (their evidence is not a target), and a forged count fails."""
    r, g = _report(alarm=True)
    s = next(s for s in E.self_report(r, g) if s.kind == 'imaginations')
    assert s.numbers['gated'] and s.numbers['close'] is None and 'do not grade' in s.text
    assert E.check(s, r, g)[0]
    n = {**s.numbers, 'gated': False, 'close': 1, 'refuted': s.numbers['tested'] - 1}
    assert not E.check(E.Statement('imaginations', n, E.render('imaginations', n)), r, g)[0]


def test_a_knocked_object_is_described_by_the_push_that_showed_it():
    """P2 gate L3-01 (2026-09-25): an object's earlier pushes were predicted well (the knock showed later), so the
    minimum over ALL its pushes (18 and 6 sigmas) contradicted "missed by more than 20". The sentence must quote the
    push that set the flag."""
    r, g = _report()
    r.foresight = [dict(situation=3, leader=A, leader_rms=1.2, rival=B, rival_rms=3.0)] + r.foresight
    s = [x for x in E.self_report(r, g) if x.kind == 'disturbed']
    assert len(s) == 1 and s[0].numbers['rms'] > E.DISTURBED and E.check(s[0], r, g)[0], [x.text for x in s]
