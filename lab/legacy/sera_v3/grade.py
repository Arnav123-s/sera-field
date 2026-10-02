"""Grading every imagination (SERA v3.1, plan revision 2): learn from every law it imagined, the wrong ones included.

The judge already scores every law in the ledger on the same throws (its prequential evidence Q). A world therefore
grades far more than its one certified law, and all of it comes from the judge's own numbers (the ledger, the
certificate, the independent checker, the caretaker's mark), never from what the imagination believed.

The credit ladder (the author, 2026-09-24: "reward better imaginations even when wrong, more for correct ones; wider
imagination, creativity and questions are good, right ones even better"). The constants are fixed before any data.

| rung | what | how it enters the loss |
|---|---|---|
| 1 | the law proven: certified and checker-verified | W_PROVEN on it, cross-entropy over all laws |
| 2 | right but unproven: the caretaker's mark when not proven | W_TAUGHT on it, cross-entropy over all laws |
| 3 | close or partly right | W_EVIDENCE times a tempered posterior over the TESTED laws (temperature ln 1/alpha), plus W_PART per term |
| 4 | creative and plausible: behind the leader by less than its threshold | the same posterior; small but not zero |
| - | refuted: behind by the threshold or more | nothing |
| 5 | good questions | evidence its own experiments gained against laws that were plausible after the teacher's throws; recorded for the question head |

Fairness:
- **Only tested laws are graded.** A law the ledger never weighed is neither rewarded nor penalized (the masked
  cross-entropy), so no law profits from rivals going untested, and none is punished for not being tried.
- **The log score is proper.** Confidence is rewarded only where it is earned.
- **Evidence never outranks proof.** The soft targets are capped: W_EVIDENCE < W_TAUGHT < W_PROVEN, so a best guess
  that is merely likely cannot entrench itself above a proven or taught law.
- **BiasMonitor** compares what the imagination expects with what is verified, per kind of term (base, product,
  power, drive), and flags a systematic lean.
- **No evidence imitation when something else is here** (research R1, reviewer, 2026-09-25). When the world's alarm fired
  (the law it weighed misfits beyond chance), the truth may lie outside every tested law, so the posterior over them is
  not a target: the soft and part credit are switched off for that world (proof and the caretaker's mark still teach).
- **Recall, not only calibration** (R1). If the evidence is biased the same way as the imagination (the ledger holds
  only laws it imagined, plus the fixed base space), calibration can look fine. So the monitor also tracks whether
  the verified law's kind of term was among the K imagined laws at all. Its sentinel flags a kind when its hits among
  8+ verified laws fall below the 1% binomial tail at recall 0.5 (0 of 8 has probability 0.5^8 = 0.0039; independent review
  Gr-2: a plain "< 0.5" flagged 3 of 8, which happens 36% of the time).
"""
import dataclasses
import math

import numpy as np
import torch
import torch.nn.functional as F

from ccops5.core import grammar
from . import compact as C, dreams as D, imagine as I

W_PROVEN, W_TAUGHT, W_EVIDENCE, W_PART = 1.5, 0.75, 0.5, 0.25
ALPHA = 1e-3
TEMPERATURE = math.log(1 / ALPHA)
TERMS = C.TERMS
NF, NT = len(D.FAMILIES), len(TERMS)

_INC = np.zeros((NF, NT), np.float32)
for _f, (_i, _j) in enumerate(zip(I._FI, I._FJ)):
    if _i >= 0:
        _INC[_f, _i] = 1.0
    if _j >= 0:
        _INC[_f, _j] = 1.0
INCIDENCE = torch.tensor(_INC)                       # law -> its terms


def term_index(term):
    return C.TERM_INDEX[term]


@dataclasses.dataclass
class Grade:
    hard: np.ndarray            # (F,) cross-entropy weights over all laws: rungs 1 and 2
    soft: np.ndarray            # (F,) tempered posterior over the tested laws (0 elsewhere): rungs 3 and 4
    mask: np.ndarray            # (F,) bool, the tested (graded) laws
    parts: np.ndarray           # (T,) evidence probability that each term is in the law
    part_mask: np.ndarray       # (T,) bool, terms of tested laws
    questions: dict             # law -> evidence its own experiments gained against it (rung 5)
    leader: tuple
    proven: object              # the proven law, or None
    taught: object              # the caretaker's mark, or None
    flaw: bool                  # the best guess was right (the caretaker says so) but not proven
    gated: bool = False         # the alarm fired: no evidence imitation for this world (R1)
    conflict: bool = False      # proven law differs from the caretaker's mark (independent review Gr-4): must never happen

    def credit(self, family):
        i = D.FAMILY_INDEX.get(grammar.canonical(family))
        return 0.0 if i is None else float(self.hard[i] + W_EVIDENCE * self.soft[i])

    def graded(self, family):
        i = D.FAMILY_INDEX.get(grammar.canonical(family))
        return bool(i is not None and self.mask[i])


def grade(ledger, cert, verified, taught=None, q_start=None, alpha=ALPHA, alarm=False, pushes=1):
    """The grade of one world: `ledger` (families and prequential scores Q), the final certificate, whether the
    independent checker verified it, the caretaker's mark (or None), and the scores after the teacher's throws only
    (q_start, for the question credit)."""
    tested = [f for f in ledger.families if f in D.FAMILY_INDEX]
    qmax = max(ledger.Q[f] for f in tested)
    leader = max(tested, key=lambda f: (ledger.Q[f], -len(f)))
    cutoff = grammar.log_threshold(leader, alpha)
    soft, mask = np.zeros(NF), np.zeros(NF, bool)
    logw = {}
    for f in tested:
        mask[D.FAMILY_INDEX[f]] = True
        gap, lp = qmax - ledger.Q[f], grammar.log_prior(f)
        if gap < cutoff and math.isfinite(lp):
            logw[f] = (ledger.Q[f] - qmax + lp) / TEMPERATURE
    if logw:
        top = max(logw.values())
        for f, lw in logw.items():
            soft[D.FAMILY_INDEX[f]] = math.exp(lw - top)
        soft /= soft.sum()
    hard = np.zeros(NF)
    proven = grammar.canonical(cert.family) if (cert.accepted and verified) else None
    if proven in D.FAMILY_INDEX:
        hard[D.FAMILY_INDEX[proven]] = W_PROVEN
    taught = grammar.canonical(taught) if taught is not None else None
    if taught is not None and taught != proven and taught in D.FAMILY_INDEX:
        hard[D.FAMILY_INDEX[taught]] = W_TAUGHT
    if alarm:                                               # the truth may be outside every tested law (R1)
        soft[:] = 0.0
    parts = soft @ _INC
    part_mask = ((mask.astype(np.float32) @ _INC) > 0) & (not alarm)
    questions = {}
    if q_start:
        known = [f for f in tested if f in q_start]
        if known:
            qmax0 = max(q_start[f] for f in known)
            for f in known:
                g0, g1 = qmax0 - q_start[f], qmax - ledger.Q[f]
                if g0 < cutoff <= g1:                        # plausible before its own experiments, refuted after
                    questions[f] = (g1 - g0) / max(int(pushes), 1)      # per own push (independent review Gr-1: raw evidence
                                                                        # would reward making more pushes)
    flaw = bool(taught is not None and leader == taught and proven != taught)
    conflict = bool(taught is not None and proven is not None and proven != taught)
    return Grade(hard, soft, mask, parts, part_mask, questions, leader, proven, taught, flaw, bool(alarm), conflict)


def loss(model, feats, world, grades):
    """The ladder loss for a batch of graded worlds (feats (B, 270, 8), world (B, 7))."""
    logits = model(feats, world)
    logq = F.log_softmax(logits, -1)
    hard = torch.tensor(np.stack([g.hard for g in grades]), dtype=logits.dtype)
    soft = torch.tensor(np.stack([g.soft for g in grades]), dtype=logits.dtype)
    mask = torch.tensor(np.stack([g.mask for g in grades]))
    logq_m = F.log_softmax(logits.masked_fill(~mask, -1e9), -1)
    l_hard = -(hard * logq).sum(-1)
    l_soft = -W_EVIDENCE * torch.where(soft > 0, soft * logq_m, torch.zeros_like(soft)).sum(-1)
    incl = (torch.softmax(logits, -1) @ INCIDENCE.to(logits.dtype)).clamp(1e-6, 1 - 1e-6)
    parts = torch.tensor(np.stack([g.parts for g in grades]), dtype=logits.dtype).clamp(0, 1)
    pmask = torch.tensor(np.stack([g.part_mask for g in grades]))
    l_part = W_PART * torch.where(pmask, F.binary_cross_entropy(incl, parts, reduction='none'),
                                  torch.zeros_like(incl)).sum(-1) / pmask.sum(-1).clamp(min=1)
    return (l_hard + l_soft + l_part).mean()


GROUPS = {'base': [i for i, t in enumerate(TERMS) if t in grammar.IDEAS]}
for _kind in ('product', 'power', 'drive'):
    GROUPS[_kind] = [i for i, t in enumerate(TERMS) if t[0] == _kind]


def _binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


class BiasMonitor:
    """Per kind of term: the imagination's expected number of such terms in the law against the verified number, over
    worlds. A lean beyond Z standard errors (and at least MIN_GAP terms per world) is flagged."""
    Z, MIN_GAP, MIN_N = 4.0, 0.05, 30

    def __init__(self):
        self.n = 0
        self.pred = {g: 0.0 for g in GROUPS}
        self.obs = {g: 0.0 for g in GROUPS}
        self.obs2 = {g: 0.0 for g in GROUPS}
        self.seen = {g: 0 for g in GROUPS}
        self.hit = {g: 0 for g in GROUPS}
        self.d = {g: 0.0 for g in GROUPS}
        self.d2 = {g: 0.0 for g in GROUPS}

    def update(self, inclusion, label, proposed=None):
        """inclusion (T,): the imagination's probability each term is in the law; label (T,) bool: the verified law's
        terms; proposed (T,) bool: the terms of its K imagined laws (for recall)."""
        self.n += 1
        label = np.asarray(label, bool)
        for g, idx in GROUPS.items():
            k = float(np.sum(label[idx]))
            self.pred[g] += float(np.sum(np.asarray(inclusion)[idx]))
            self.obs[g] += k
            self.obs2[g] += k * k
            dd = float(np.sum(np.asarray(inclusion)[idx])) - k        # independent review Gr-3: the spread of the DIFFERENCE
            self.d[g] += dd
            self.d2[g] += dd * dd
            if proposed is not None and k:
                self.seen[g] += int(np.sum(label[idx]))
                self.hit[g] += int(np.sum(label[idx] & np.asarray(proposed, bool)[idx]))

    def report(self):
        out = {}
        for g in GROUPS:
            if not self.n:
                continue
            p, o = self.pred[g] / self.n, self.obs[g] / self.n
            md = self.d[g] / self.n
            var = max(self.d2[g] / self.n - md * md, 1e-4)
            out[g] = dict(expected=round(p, 4), verified=round(o, 4), z=round(md / math.sqrt(var / self.n), 2))
        return out

    SENTINEL = 8                  # verified laws of a kind before its recall is judged
    MIN_RECALL = 0.5
    RECALL_P = 0.01               # independent review Gr-2: flag only when so few hits have probability < 1% at recall 0.5
                                  # (a plain "< 0.5" flagged 3 of 8, which happens 36% of the time)

    def recall(self):
        return {g: (self.hit[g] / self.seen[g] if self.seen[g] else None) for g in GROUPS}

    def flags(self):
        out = []
        if self.n >= self.MIN_N:
            out += [g for g, r in self.report().items()
                    if abs(r['z']) > self.Z and abs(r['expected'] - r['verified']) > self.MIN_GAP]
        out += [f'{g}:recall' for g in GROUPS if self.seen[g] >= self.SENTINEL
                and _binom_cdf(self.hit[g], self.seen[g], self.MIN_RECALL) < self.RECALL_P]
        return out
