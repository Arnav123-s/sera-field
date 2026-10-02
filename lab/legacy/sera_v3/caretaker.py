"""The caretaker (plan revision 5, WP3): the caretaker's code, the author's delegated teacher.

It knows the hidden law of the world SERA is in, and nothing SERA has not yet caused: condition R-P of the playroom
design (docs/SERA_PLAYROOM.md §2, reviewed by independent review). Everything it says or does is a function of the hidden
state, the throws so far and its own random numbers, never of the noise of throws still to come. So the judge's
guarantee is untouched: the judge never reads a word, and a demonstrated push is one more throw chosen from the past.

What it does, by stage:
- 'teach' (Stage 1): describe (one sentence per word slot about the law, after the teacher's throws); demonstrate
  (the push that best tells the law from its nearest look-alike); and, after the world, name the law.
- 'practice' (Stage 2): a hint when SERA is stuck (at most sera.mind.MAX_HINTS per world, one word about the law);
  after the world, name the law (the correction).
- 'alone' (Stage 3): nothing. There is no caretaker.

Its sentences follow sera.words' likelihood exactly: a word uniformly among the words true of the law, a slip with
probability words.EPS, a uniformly random word when none is true. Its own lexicon is the true one (word i names
property i of the slot); SERA's prior over lexicons is symmetric, so the order tells SERA nothing.
"""
import math

import numpy as np

from ccops5.core import grammar, mind as M1, truth
from . import design as DS, words as W, worlds as SW

STAGES = ('teach', 'practice', 'alone')


class Caretaker:
    def __init__(self, world, stage, seed=0):
        assert stage in STAGES
        self._world = world                                   # the hidden state (its law and masses)
        self._law = grammar.canonical(world.spec.family)
        self.stage = stage
        self._rng = np.random.default_rng([seed, 19, world.spec.index, world.spec.level])
        self._said = 0

    def _sentence(self, slot):
        tv = W.truth(slot, self._law)
        true = [i for i, b in enumerate(tv) if b]
        if not true or self._rng.random() < W.EPS:
            w = int(self._rng.integers(5))
        else:
            w = int(true[int(self._rng.integers(len(true)))])
        self._said += 1
        return slot, w

    def describe(self):
        """Stage 1: one sentence per slot about the law."""
        if self.stage != 'teach':
            return []
        return [self._sentence(slot) for slot in W.SLOTS]

    def hint(self, why, own):
        """Stage 2: one sentence about the law when SERA is stuck (`why` and `own` are the mind's event, not data; the
        slot is drawn by the caretaker's own random numbers)."""
        if self.stage != 'practice':
            return None
        return self._sentence(W.SLOTS[int(self._rng.integers(len(W.SLOTS)))])

    def demonstrate(self, throws, sigma):
        """Stage 1: (object, push program) that best tells the law from its nearest look-alike, by the surviving gap
        (sera.design) on a ledger of the two laws over the throws so far. None when it cannot be computed."""
        if self.stage != 'teach' or not self._law:
            return None
        w = self._world
        xs, vs, ts = SW._states(w)
        try:
            gaps = SW.rival_gaps(w, xs, vs, ts)
        except (ValueError, np.linalg.LinAlgError):
            return None
        gaps = {f: g for f, g in gaps.items() if f and grammar.log_prior(f) > -math.inf}
        if not gaps:
            return None
        look = min(gaps, key=gaps.get)
        ledger = truth.Ledger([self._law, look], sigma)
        for t in throws:
            ledger.add(t)
        model, post = ledger._models[self._law], ledger.post[self._law]
        nc = model.n_coef
        best, best_s = None, -math.inf
        for k in range(w.n_situations):
            mu = post.mean[nc + post.order.index(k)] if k in post.order else 1.0
            for a in DS.programs(model, post.mean[:nc], mu, np.random.default_rng([w.spec.index, k, 5]),
                                 M1.DURATIONS, M1.COMMANDS):
                s = DS.surviving_separation(ledger, self._law, look, k, a)
                if np.isfinite(s) and s > best_s:
                    best, best_s = (k, a), s
        return best

    def name(self):
        """After the world (Stages 1-2): the law, named."""
        return self._law if self.stage in ('teach', 'practice') else None


def grade(report, verified, world, eps=0.2):
    """The caretaker's grade of one world, by a script (the answer is known; the author: a deterministic script beats any model
    where it can judge): the verdict, the right, missing and extra terms, the part score and where it looked.
    The verdicts use the P2 gate's definitions (scripts/sera_check.py, pre-registered 2026-09-25):
      proven right     sure, checker-verified, the exact law
      proven, surface  sure, verified, not the exact law, but the true force it left out is within eps everywhere the
                       certificate speaks for (a correct surface: "even a correct law may be only its surface")
      SURE AND WRONG   sure, and neither (the tripwire)
      checker refused  sure, and the independent checker did not re-derive the certificate (the tripwire)
      right, unsure / unsure, wrong   not sure; its best guess was / was not the law
    `wrong_frozen` (core_check.wrong, stricter: any claim but the exact law) is recorded beside it."""
    import core_check
    truth_law = grammar.canonical(world.spec.family)
    claim = grammar.canonical(report.claim)
    exact = claim == truth_law
    outside = world.residual_outside(report.certificate) if report.sure else None
    if report.sure and not verified:
        verdict = 'checker refused'
    elif report.sure and exact:
        verdict = 'proven right'
    elif report.sure and outside is not None and outside <= eps:
        verdict = 'proven, surface'
    elif report.sure:
        verdict = 'SURE AND WRONG'
    else:
        verdict = 'right, unsure' if exact else 'unsure, wrong'
    wrong_frozen = bool(report.sure and core_check.wrong(report.certificate, world))
    both = set(claim) | set(truth_law)
    scope = report.certificate.scope or {}
    return dict(verdict=verdict, wrong_frozen=wrong_frozen, outside=outside, truth=grammar.name(truth_law),
                answer=grammar.name(claim),
                right_terms=sorted(grammar.term_name(t) for t in set(claim) & set(truth_law)),
                missing_terms=sorted(grammar.term_name(t) for t in set(truth_law) - set(claim)),
                extra_terms=sorted(grammar.term_name(t) for t in set(claim) - set(truth_law)),
                part_score=round(len(set(claim) & set(truth_law)) / len(both), 3) if both else 1.0,
                where=dict(x=scope.get('x'), v=scope.get('v')) if scope else None)
