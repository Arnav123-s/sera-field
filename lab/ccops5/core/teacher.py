"""The teacher (M1_DESIGN.md §4b and §4d.5): the author's "correct it, teach it why, master it, then surprise it".

Help per kind of world fades by skill:
  level 2  show the right family before the world (the world counts as hinted);
  level 1  say its input ("along speed") before the world (hinted);
  level 0  no help.
A kind drops one level after each world the mind certifies correctly at that level.

Arms:
  none    no teacher;
  answer  after every world, the right family (the school's way);
  why     only when the mind is not sure (or, impossibly, sure and wrong): the right family and why, namely the
          deciding throw (where its leading idea and the truth separate most), the shape of the leftover there, and
          the evidence against its idea; the kind is repeated until mastered.
Every correction gets an id in a registry shared with the board, so only real corrections can leave a trace.
"""
import itertools

import numpy as np

from . import grammar, gut as G

_IDS = itertools.count(1)


class Teacher:
    def __init__(self, arm, registry=None):
        assert arm in ('none', 'answer', 'why')
        self.arm = arm
        self.level = {}
        self.registry = registry if registry is not None else set()
        self.mastered = set()

    def help_for(self, kind):
        if self.arm == 'none':
            return 0
        return self.level.setdefault(kind, 2)

    def apply_hint(self, ranking, truth, level):
        """The ranking the mind uses after the hint: level 2 puts the truth first; level 1 puts first the
        families whose ideas all use the truth's input(s), keeping the gut's order within each group."""
        if level >= 2:
            return [truth] + [f for f in ranking if f != truth]
        if level == 1:
            inputs = {i[0] for i in truth}
            good = [f for f in ranking if f and {i[0] for i in f} <= inputs]
            return good + [f for f in ranking if f not in good]
        return ranking

    def after_world(self, kind, truth, report, correct):
        """Returns a correction dict or None, and updates help levels and mastery."""
        level = self.help_for(kind)
        if correct:
            if level == 0:
                self.mastered.add(kind)
            self.level[kind] = max(level - 1, 0)
        if self.arm == 'none':
            return None
        if self.arm == 'answer' or (self.arm == 'why' and not correct):
            cid = f'c{next(_IDS)}'
            self.registry.add(cid)
            out = {'id': cid, 'family': tuple(truth), 'issued_by': 'teacher'}
            if self.arm == 'why':
                out['why'] = explain(report, truth)
            return out
        return None


def explain(report, truth):
    """The deciding evidence: the throw where the mind's leading idea and the truth part most (by the fast
    tier's misfit), the leftover's shape there, and the log e-value of the truth against its idea."""
    ledger = report.ledger
    lead = tuple(report.claim)
    best, gap = None, -1.0
    for t in ledger.throws:
        g = G.fit_gains([t])
        j_lead, j_truth = G.FAMILIES.index(grammar.canonical(lead)), G.FAMILIES.index(grammar.canonical(truth))
        d = g[j_truth] - g[j_lead]
        if d > gap:
            best, gap = t, d
    x, v, f, a = G.accelerations([best])
    shape = 'rising' if abs(np.corrcoef(np.abs(v), np.abs(a - a.mean()))[0, 1]) > 0.5 else 'steady'
    along = 'speed' if abs(np.corrcoef(v, a)[0, 1]) >= abs(np.corrcoef(x, a)[0, 1]) else 'position'
    try:
        log_e = float(ledger.Q[grammar.canonical(truth)] - ledger.mle(lead).loglik)
    except Exception:                                   # a missing family (outside the grammar): no number
        log_e = None
    return {'throw_index': best.index, 'situation': best.situation, 'along': along, 'shape': shape,
            'log_e_truth_vs_claim': log_e, 'deciding_throw': best}
