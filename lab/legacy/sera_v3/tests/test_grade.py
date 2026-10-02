"""SERA v3.1 grading (sera.grade): learn from every imagination, fairly (plan revision 2, the credit ladder).

Written before the module. The author (2026-09-24, 23:50): grade fairly and prevent bias; reward better imaginations
even when wrong, more for correct ones; wider imagination and questions are good, right ones even better. Every grade
comes from the judge's own numbers (the ledger's evidence, the certificate), never from the imagination's beliefs."""
import math
import types

import numpy as np
import pytest
import torch

from ccops5.core import grammar
from legacy.sera_v3 import dreams as D, grade as G, imagine as I

A = grammar.canonical((('speed', 'straight'),))                               # the proven law in these tests
CLOSE = grammar.canonical((('speed', 'wave'),))
PART = grammar.canonical((('speed', 'straight'), ('position', 'cubic')))       # wrong, with a right part
PLAUS = grammar.canonical((('position', 'growing'),))
FAR = grammar.canonical((('position', 'steps'),))
UNTESTED = grammar.canonical((('position', 'wave'),))


def _ledger(gaps):
    """A stand-in with what grade reads: the families and their prequential scores (leader at 0)."""
    fams = list(gaps)
    return types.SimpleNamespace(families=fams, Q={f: -g for f, g in gaps.items()})


def _grade(proven=True, taught=None, gaps=None):
    gaps = gaps or {A: 0.0, CLOSE: 2.0, PART: 4.0, PLAUS: 9.0, FAR: 200.0}
    cert = types.SimpleNamespace(family=A, accepted=proven, alpha=1e-3)
    return G.grade(_ledger(gaps), cert, verified=proven, taught=taught)


def test_soft_target_is_the_tempered_posterior_over_tested_laws_only():
    g = _grade()
    t = g.soft
    tested = [f for f in (A, CLOSE, PART, PLAUS, FAR)]
    idx = [D.FAMILY_INDEX[f] for f in tested]
    lp = np.array([grammar.log_prior(f) for f in tested])
    q = np.array([0.0, -2.0, -4.0, -9.0, -200.0])
    cutoff = grammar.log_threshold(A, 1e-3)
    w = np.exp((q + lp) / G.TEMPERATURE) * (np.array([0.0, 2.0, 4.0, 9.0, 200.0]) < cutoff)
    assert np.allclose(t[idx], w / w.sum(), atol=1e-9)
    assert g.mask[D.FAMILY_INDEX[UNTESTED]] == False and t[D.FAMILY_INDEX[UNTESTED]] == 0.0    # neither rewarded nor penalized
    assert t[D.FAMILY_INDEX[FAR]] == 0.0                                                        # refuted: nothing


def test_the_credit_ladder_is_strictly_ordered():
    proven = _grade(proven=True)
    unproven = _grade(proven=False, taught=A)                  # the caretaker marks A; A is not proven here
    c = lambda g, f: g.credit(f)
    assert c(proven, A) > c(unproven, A)                       # proven > right but unproven
    assert c(unproven, A) > c(proven, CLOSE)                   # right but unproven > close
    assert c(proven, CLOSE) > c(proven, PLAUS) > 0.0           # close > plausible and creative > nothing
    assert c(proven, FAR) == 0.0                               # refuted earns nothing
    assert c(proven, UNTESTED) == 0.0 and not proven.graded(UNTESTED)


def test_a_wrong_law_with_a_right_part_earns_part_credit():
    g = _grade()
    parts = g.parts                                            # per-term target inclusion (terms of tested laws only)
    right = G.term_index(('speed', 'straight'))
    wrong = G.term_index(('position', 'steps'))
    assert parts[right] > parts[wrong]
    assert g.part_mask[right] and g.part_mask[wrong]


def test_questions_answered_are_credited():
    """A law plausible after the teacher's throws and ruled out by SERA's own experiments was a good question."""
    start = {A: 0.0, CLOSE: 1.0, FAR: 150.0}
    end = {A: 0.0, CLOSE: 40.0, FAR: 200.0}
    cert = types.SimpleNamespace(family=A, accepted=True, alpha=1e-3)
    g = G.grade(_ledger(end), cert, verified=True, q_start={f: -v for f, v in start.items()}, pushes=13)
    assert g.questions[CLOSE] == pytest.approx(39.0 / 13)              # per own push (independent review Gr-1)
    assert g.questions.get(FAR, 0.0) == 0.0                    # already refuted before: nothing asked


def test_the_ladder_loss_teaches_the_order():
    torch.manual_seed(0)
    model = I.Imagination()
    feats = torch.randn(1, 270, 8)
    world = torch.randn(1, 7)
    g = _grade()
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    for _ in range(60):
        loss = G.loss(model, feats, world, [g])
        opt.zero_grad()
        loss.backward()
        opt.step()
    p = torch.softmax(model(feats, world), -1)[0]
    pi = lambda f: float(p[D.FAMILY_INDEX[f]])
    assert pi(A) > pi(CLOSE) > pi(PLAUS) > pi(FAR)


def test_the_bias_monitor_flags_a_planted_preference():
    rng = np.random.default_rng(0)
    biased, fair = G.BiasMonitor(), G.BiasMonitor()
    products = [i for i, t in enumerate(G.TERMS) if t[0] == 'product']
    for _ in range(200):
        truth_has_product = rng.random() < 0.1
        incl = np.full(len(G.TERMS), 0.01)
        incl_b = incl.copy()
        incl_b[products] = 0.6 / len(products) * 10                 # always leans to products
        label = np.zeros(len(G.TERMS), bool)
        if truth_has_product:
            label[rng.choice(products)] = True
        fair_incl = incl.copy()
        fair_incl[products] = 0.1 / len(products)
        biased.update(incl_b, label)
        fair.update(fair_incl, label)
    assert 'product' in biased.flags()
    assert 'product' not in fair.flags()


def test_no_evidence_imitation_when_something_else_is_here():
    """R1: when the alarm fired, the truth may lie outside every tested law; only proof or the caretaker teach."""
    cert = types.SimpleNamespace(family=A, accepted=False, alpha=1e-3)
    g = G.grade(_ledger({A: 0.0, CLOSE: 2.0}), cert, verified=False, taught=CLOSE, alarm=True)
    assert g.soft.sum() == 0.0 and not g.part_mask.any()
    assert g.credit(CLOSE) == G.W_TAUGHT and g.credit(A) == 0.0


def test_the_bias_monitor_catches_a_kind_never_imagined():
    """R1 sentinel: 8 verified product laws, none among the imagined ones -> recall 0 < 0.5 is flagged."""
    m = G.BiasMonitor()
    products = [i for i, t in enumerate(G.TERMS) if t[0] == 'product']
    for i in range(8):
        label = np.zeros(len(G.TERMS), bool)
        label[products[i % len(products)]] = True
        proposed = np.zeros(len(G.TERMS), bool)
        proposed[G.term_index(('speed', 'straight'))] = True          # it only ever imagines base laws
        m.update(np.full(len(G.TERMS), 1.0 / len(G.TERMS)), label, proposed)
    assert 'product:recall' in m.flags()



def test_recall_is_flagged_only_when_improbable():
    """independent review Gr-2: 3 hits of 8 happens 36% of the time at recall 0.5 and must not be flagged; 0 of 8 must."""
    def monitor(hits):
        m = G.BiasMonitor()
        products = [i for i, t in enumerate(G.TERMS) if t[0] == 'product']
        for i in range(8):
            label = np.zeros(len(G.TERMS), bool)
            label[products[i]] = True
            proposed = np.zeros(len(G.TERMS), bool)
            if i < hits:
                proposed[products[i]] = True
            m.update(np.full(len(G.TERMS), 1.0 / len(G.TERMS)), label, proposed)
        return m.flags()
    assert 'product:recall' not in monitor(3)
    assert 'product:recall' in monitor(0)


def test_a_proven_law_that_differs_from_the_caretaker_is_flagged():
    cert = types.SimpleNamespace(family=A, accepted=True, alpha=1e-3)
    g = G.grade(_ledger({A: 0.0, CLOSE: 30.0}), cert, verified=True, taught=CLOSE)
    assert g.conflict
