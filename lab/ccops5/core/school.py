"""The School (M1_DESIGN.md §4d): one persistent mind lives many worlds and learns to discover.

A life has three phases:
  taught  the curriculum chooses worlds; the teacher helps (per arm); the caretaker speaks; the board keeps marks;
  alone   the teacher has left; worlds of every practised kind at random; it still learns from its own
          certificates (only checked outcomes);
  exam    fixed worlds, the same for every arm: never-shown kinds (thick oil, valley) and practised kinds, half of
          them with the regime word said before any throw ("word only"). Nothing learns during the exam.
Nothing here can make a claim sure: that is the checker's job (Library.record). Scoring uses the hidden truth.
"""
import dataclasses
import math
import time
from collections import Counter

import numpy as np

from . import board as B, caretaker as CT, curriculum as CU, evidence as EV, grammar, gut as G, lexicon as LX
from . import teacher as TE, truth

ARMS = {
    #            teacher   words     learn  trace  board  placement  order
    'untaught':  ('none',   'none',   False, False, False, False, 'ladder'),
    'self':      ('none',   'none',   True,  True,  False, False, 'ladder'),
    'answer':    ('answer', 'none',   True,  False, False, False, 'ladder'),
    'why':       ('why',    'none',   True,  True,  False, False, 'ladder'),
    'why+timed': ('why',    'timed',  True,  True,  False, False, 'ladder'),
    'why+random': ('why',   'random', True,  True,  False, False, 'ladder'),
    'why+trails': ('why',   'none',   True,  True,  True,  False, 'ladder'),
    'full':      ('why',    'timed',  True,  True,  True,  True,  'progress'),
    # T2: the 'why' arm with a different credit rule (what the gut may learn from); every other setting the same
    'credit-outside': ('why', 'none', True,  True,  False, False, 'ladder'),
    'credit-self':    ('why', 'none', True,  True,  False, False, 'ladder'),
    'credit-none':    ('why', 'none', False, True,  False, False, 'ladder'),
}
CREDIT = {'credit-outside': 'outside', 'credit-self': 'self', 'credit-none': 'none'}   # every other arm: 'checked'


def credit_outcome(mode, claim, correction, report):
    """(family, source) the gut may learn from after a world, under a credit rule (T2):
    checked = an accepted certificate, else the teacher's correction; outside = the teacher's correction only;
    self = the mind's own leading idea, whether or not anything checked it; none = nothing."""
    if mode == 'checked':
        if claim is not None:
            return grammar.canonical(claim.family), 'certificate'
        mode = 'outside'
    if mode == 'outside':
        return (grammar.canonical(correction['family']), 'teacher') if correction is not None else (None, None)
    if mode == 'self':
        return (grammar.canonical(report.claim), 'self') if report.claim is not None else (None, None)
    return None, None
EXAM = (('thick oil', True), ('valley', True), ('rubbing', False), ('spring', False), ('thick oil', True),
        ('valley', True), ('water drag', False), ('swing', False), ('thick oil', True), ('valley', True),
        ('dry friction', False), ('stiff spring', False))
SIGMA = (0.001, 0.001)


@dataclasses.dataclass
class Settings:
    n_taught: int = 50
    n_alone: int = 30
    situations: int = 5
    eps: float = 0.5
    budget: int = 2
    repeats: int = 2              # the 'why' teacher repeats an unmastered kind up to this many times in a row
    n_exam: int = len(EXAM)


class _Library(truth.Library):
    """truth.Library whose record() can take the checker's verdict on these exact inputs, computed once per world by
    the evidence cache (evidence.py). The verdict is still the checker's own: nothing else can make a claim sure."""

    def record(self, certificate, throws, verdict=None):
        if verdict is None:
            return super().record(certificate, throws)
        if verdict:
            self._claims.append(truth.Claim(tuple(certificate.family), certificate, True))
        return verdict


def _misfit_cells(report, brd):
    """Board cells (normalized position, speed) where the leading idea's best fit misses most (top 10%)."""
    ledger, lead = report.ledger, tuple(report.claim)
    fit = ledger.mle(lead)
    if not fit.ok:
        return []
    model = ledger._models[grammar.canonical(lead)]
    xs = np.concatenate([t.x for t in ledger.throws])
    vs = np.concatenate([t.v for t in ledger.throws])
    xm, vm = max(np.max(np.abs(xs)), 1e-9), max(np.max(np.abs(vs)), 1e-9)
    heat = np.zeros((brd.grid, brd.grid))
    from . import likelihood as L
    n = xs.size // len(ledger.throws)
    for t in ledger.throws:
        f = L._sim(model, fit.coef, fit.mu[t.situation], t)
        r2 = ((t.x - f[:n]) / SIGMA[0]) ** 2 + ((t.v - f[n:]) / SIGMA[1]) ** 2
        for x, v, e in zip(t.x, t.v, r2):
            heat[brd.cell_of(x / xm, v / vm)] += e
    flat = np.argsort(heat.ravel())[::-1]
    k = max(1, int(round(0.1 * heat.size)))
    return [divmod(int(i), brd.grid) for i in flat[:k] if heat.ravel()[i] > 0]


def live_life(seed, arm_name, settings=None, progress=None, cache=None):
    """`cache`: an evidence.Cache shared across arms (speed only; the numbers are the same without it)."""
    st = settings or Settings()
    cache = cache if cache is not None else EV.Cache(None)
    t_arm, w_arm, learn, use_trace, use_board, placement, order = ARMS[arm_name]
    credit = CREDIT.get(arm_name, 'checked')
    cur = CU.Curriculum(order, seed)
    registry = set()
    teach = TE.Teacher(t_arm, registry)
    talk = CT.Caretaker(w_arm, seed)
    lex = LX.Lexicon(CT.VOCABULARY)
    brd = B.Board(corrections_registry=registry) if use_board else None
    gut = G.Gut()
    library = _Library(SIGMA)
    rng = np.random.default_rng([seed, 57])
    heard_checked, grounded_at = Counter(), {}
    log = []
    last = {'kind': None, 'repeats': 0}
    total = st.n_taught + st.n_alone + st.n_exam
    for n in range(total):
        started = time.perf_counter()
        if n < st.n_taught:
            phase = 'taught'
            if (t_arm == 'why' and last['kind'] is not None and not last['correct']
                    and last['repeats'] < st.repeats):
                kind, template = last['kind'], last['template']
                last['repeats'] += 1
            else:
                kind, template = cur.next_kind(board=brd, placement=placement)
                last['repeats'] = 0
            word_only, never, index = False, False, n
        elif n < st.n_taught + st.n_alone:
            phase = 'alone'
            kind = str(rng.choice(CU.PRACTICE_KINDS))
            template = 'default'
            if placement and brd is not None:
                hint = brd.placement_hint()
                if hint is not None:
                    template = hint[0]
            word_only, never, index = False, False, n
        else:
            phase = 'exam'
            e = n - st.n_taught - st.n_alone
            kind, never = EXAM[e]
            template, word_only, index = 'default', e % 2 == 0, 10_000 + e
        w = CU.make_world(seed, kind, index, situations=st.situations, template=template)
        talk.start_world(n, w, word_only=word_only)

        def on_event(k, event, n=n, w=w):
            if event == 'end':
                talk.on_situation(n, w, k)
            else:
                talk.on_event(n, w, k, event)

        report, verdict = cache.live(('school', seed, kind, index, template, st.situations), w, eps=st.eps,
                                     budget=st.budget, check_sigma=SIGMA, on_event=on_event)
        heard_all = talk.heard(n)
        heard_early = sorted({u.word for u in talk.log if u.world_no == n and u.situation <= 0})
        truth_fam = grammar.canonical(w.truth)
        gains = G.fit_gains(w.situations()[0])
        F = gut.features(gains, brd, lex, heard_early)
        F0 = gut.features(gains, brd, lex, (), use_words=False)
        ranking, ranking_nw = gut.ranking(F), gut.ranking(F0)
        brier = G.brier(gut.probabilities(F), truth_fam)      # its bet before the world, scored (T2)
        level = teach.help_for(kind) if phase == 'taught' else 0
        used = teach.apply_hint(ranking, truth_fam, level) if level else ranking
        rank, rank_nw = used.index(truth_fam) + 1, ranking_nw.index(truth_fam) + 1

        claim = None
        if report.sure and library.record(report.certificate, report.ledger.throws, verdict=verdict):
            claim = library.claims[-1]
        correct = claim is not None and grammar.canonical(claim.family) == truth_fam
        wrong = claim is not None and not correct
        correction = teach.after_world(kind, truth_fam, report, correct) if phase == 'taught' else None
        outcome, source = credit_outcome(credit, claim, correction, report)

        if phase != 'exam' and learn and outcome is not None:
            target = np.zeros(len(G.FAMILIES))
            target[G.FAMILIES.index(outcome)] = 1.0
            if use_trace:
                target = 0.5 * target + 0.5 * G.trace_targets(report.ledger)
            gut.train(F, target)
            if correction is not None and 'why' in correction:
                dt = correction['why']['deciding_throw']
                gut.train(gut.features(G.fit_gains([dt]), brd, lex, heard_early), outcome)
        if phase != 'exam' and outcome is not None:
            lex.update(heard_all, grammar.name(outcome))
            for word in heard_all:
                heard_checked[word] += 1
            post = report.ledger.post.get(outcome)
            for u in talk.log:
                if u.world_no == n and u.word in CT.MASS_WORDS and u.situation >= 0 and post is not None \
                        and u.situation in post.order:
                    nc = len(outcome)
                    lex.update_mass(u.word, math.log(max(post.mean[nc + post.order.index(u.situation)], 1e-6)))
            for word in lex.grounded_words():
                grounded_at.setdefault(word, n)
        if brd is not None and phase != 'exam':
            if claim is not None:
                brd.deposit_certificate(library, claim)
            if correction is not None:
                brd.deposit_correction(correction)
            if report.alarm:
                fired, log_e = truth.something_else(report.ledger, report.claim)
                thr = math.log(report.ledger.n_space / 1e-3)
                cells = _misfit_cells(report, brd)
                if fired and cells:
                    brd.deposit_alarm(log_e, thr, cells)
            if not report.sure and report.certificate.rivals:
                weak = [b for b, e in report.certificate.rivals.items()
                        if e < grammar.log_threshold(report.claim, 1e-3)]
                if weak:
                    brd.mark_lookalike(tuple(report.claim), weak[0])
            brd.evaporate()
        if phase == 'taught':
            cur.record(kind, rank, correct and not level, level > 0)
        last.update(kind=kind, template=template, correct=correct)

        why = correction.get('why') if correction else None
        log.append({
            'n': n, 'phase': phase, 'kind': kind, 'template': template, 'never_shown': never, 'word_only': word_only,
            'truth': grammar.name(truth_fam), 'rank': rank, 'rank_no_words': rank_nw, 'help': level, 'hinted': level > 0,
            'top3': [grammar.name(f) for f in ranking[:3]], 'brier': round(brier, 4), 'claim': grammar.name(report.claim), 'sure': report.sure,
            'checked': claim is not None, 'correct': correct, 'sure_and_wrong': wrong, 'alarm': report.alarm,
            'throws': report.throws, 'own': report.own_pushes, 'outcome': None if outcome is None else grammar.name(outcome),
            'outcome_source': source, 'heard': sorted(heard_all), 'heard_early': heard_early,
            'why': None if why is None else {k: v for k, v in why.items() if k != 'deciding_throw'},
            'open': list(report.open)[:2], 'seconds': round(time.perf_counter() - started, 1)})
        if progress:
            progress(log[-1])
    return {
        'seed': seed, 'arm_name': arm_name, 'arm': dict(zip(('teacher', 'words', 'learn', 'trace', 'board',
                                                             'placement', 'order'), ARMS[arm_name])),
        'credit': credit,
        'settings': dataclasses.asdict(st), 'worlds': log,
        'lexicon': {'grounded': lex.grounded_words(), 'log_e': {w: round(lex.log_e(w), 3) for w in lex.vocabulary},
                    'threshold': round(lex.threshold(), 3), 'heard_checked': dict(heard_checked),
                    'grounded_at': grounded_at},
        'gut': gut.state(), 'curriculum': cur.state(), 'mastered': sorted(teach.mastered),
        'board': None if brd is None else {'trails': {grammar.name((i,)): round(v, 3) for i, v in brd.trails.items()},
                                           'lookalikes': {' | '.join(k): round(v, 3) for k, v in brd.lookalikes.items()}},
        'library_claims': len(library.claims), 'evidence': {'hits': cache.hits, 'misses': cache.misses}}
