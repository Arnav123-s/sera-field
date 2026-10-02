"""Deterministic school worlds and the order in which the mind meets them."""
import dataclasses

import numpy as np

from .. import puzzles as P
from . import grammar, paths, worlds


STAGES = (('S0', ('none',)),
          ('S1', ('rubbing', 'spring', 'slope')),
          ('S2', ('water drag', 'dry friction', 'tight spring', 'stiff spring', 'swing')),
          ('S3', ('rubbing+spring', 'slope+dry friction', 'water drag+spring')),
          ('S4', ('swing small', 'faint rubbing')))
EXAM_NEVER_SHOWN = ('thick oil', 'valley')
KINDS = tuple(kind for _, kinds in STAGES for kind in kinds) + EXAM_NEVER_SHOWN
KIND_TRUTH = {
    kind: (grammar.canonical(tuple(P.FORCES[part][0] for part in kind.split('+')))
           if '+' in kind else
           (() if kind == 'none' else (P.FORCES[{'swing small': 'swing',
                                              'faint rubbing': 'rubbing'}.get(kind, kind)][0],)))
    for kind in KINDS
}
PRACTICE_KINDS = KINDS[:-len(EXAM_NEVER_SHOWN)]
SURPRISES = ('x*v force', 'v^p drag', 'motor')
KIND_TRUTH.update({kind: None for kind in SURPRISES})


@dataclasses.dataclass
class MultiWorld(worlds.World):
    ideas: tuple = ()
    coefs: tuple = ()
    hidden_terms: tuple = ()
    hidden_coefs: tuple = ()

    def _codes(self):
        terms = self.hidden_terms or self.ideas
        coefs = self.hidden_coefs or self.coefs
        codes = [grammar.code(idea) for idea in terms]
        return (np.array([c[0] for c in codes], np.int64),
                np.array([c[1] for c in codes], np.int64),
                np.array([c[2] for c in codes], np.int64),
                np.array(coefs, float))

    def true_force(self, x, v, t=None):
        x = np.ravel(np.asarray(x, float))
        v = np.ravel(np.asarray(v, float))
        t = np.zeros_like(x) if t is None else np.ravel(np.asarray(t, float))
        kinds, a, b, coefs = self._codes()
        return np.array([sum(coefs[i] * paths.term_t(kinds[i], a[i], b[i], xi, vi, ti, 1.0, 1.0)
                             for i in range(len(coefs))) for xi, vi, ti in zip(x, v, t)])


def _build(seed, index, ideas, coefs, situations, noise, tricks, push_choices, terms=None, term_coefs=None):
    """Build a world using the same draw order as worlds.make."""
    rng = np.random.default_rng([seed, 7, index])
    masses3 = [float(m) for m in rng.uniform(0.6, 2.5, size=3)]
    strengths = []
    for idea, limits in zip(ideas, coefs):
        sign = float(rng.choice([-1.0, 1.0])) if idea[0] == 'nothing' else 1.0
        strengths.append(-sign * float(rng.uniform(*limits)))
    hidden_terms = tuple(terms or ())
    hidden_coefs = []
    if term_coefs:
        for limits in term_coefs:
            hidden_coefs.append(-float(rng.uniform(*limits)))
        sampled_terms = []
        for term in hidden_terms:
            if term[0] == 'power' and term[2] is None:
                # p in 0.2-0.4 (development note, 2026-09-24): measured effect beyond every base pair is about 0.25 there,
                # but 0.07 at p = 0.5 and <= 0.05 for p >= 0.7 (pairs of base ideas mimic them), so only sub-linear
                # drag needs invention at eps 0.1.
                sampled_terms.append(('power', term[1], round(float(rng.uniform(0.2, 0.4)), 1)))
            elif term[0] == 'drive' and term[2] is None:
                sampled_terms.append(('drive', term[1], round(float(rng.uniform(2.0, 6.0)), 1)))
                hidden_coefs[len(sampled_terms) - 1] *= float(rng.choice([-1.0, 1.0]))
            else:
                sampled_terms.append(term)
        hidden_terms = tuple(sampled_terms)
    sigma = (0.001 * noise, 0.001 * noise)
    w = MultiWorld(seed, index, '+'.join(str(i) for i in ideas), grammar.canonical(ideas),
                   strengths[0] if strengths else 0.0, 0, ideas[0] if ideas else None,
                   [], [], sigma, [], [], ideas=tuple(ideas), coefs=tuple(strengths),
                   hidden_terms=hidden_terms, hidden_coefs=tuple(hidden_coefs))
    for k in range(situations):
        m = float(rng.choice(masses3))
        bump = None
        if rng.random() < tricks:
            bump = (float(rng.choice([0.6, 0.8, 1.0, 1.2])), float(rng.choice([-1.5, 1.5])))
        pushes = (float(rng.choice(push_choices)), -float(rng.choice(push_choices)))
        check_u = float(rng.choice((-0.9, -0.5, 0.5, 0.9)))
        w.masses.append(m)
        w.bumps.append(bump)
        w.teacher_pushes.append(pushes)
        kinds, a, b, strengths_array = w._codes()
        for j, u in enumerate(pushes + (check_u,)):
            t0, amp = bump if bump else (0.0, 0.0)
            xs, vs = paths.simulate(worlds.hand(u), 1.0 / m, kinds, a, b, strengths_array,
                                    1.0, 1.0, t0, amp)
            noise_rng = np.random.default_rng([seed, 7, index, k, j])
            throw = worlds.Throw(k, len(w.throws) if j < 2 else -1, worlds.push_of(u),
                                 xs + noise_rng.normal(0, sigma[0], xs.size),
                                 vs + noise_rng.normal(0, sigma[1], vs.size),
                                 'teacher' if j < 2 else 'check')
            (w.throws if j < 2 else w.held_out).append(throw)
    return w


def make_world(seed, kind, index, *, situations=8, noise=1.0, tricks=0.05, template='default'):
    if kind not in KINDS and kind not in SURPRISES:
        raise ValueError(kind)
    if template not in ('default', 'fast', 'large'):
        raise ValueError(template)
    if kind in SURPRISES:
        terms = {'x*v force': (('product', 'straight', 'straight'),),
                 'v^p drag': (('power', 'speed', None),),
                 'motor': (('drive', 'sin', None),)}[kind]
        # x*v strength 0.5-1.5 (development note, 2026-09-24): with 1-4 the force feeds energy in when x < 0 and 3 of 5
        # seeds ran away. A world that still runs away is rebuilt from the next index (deterministic).
        limits = {'x*v force': ((0.5, 1.5),), 'v^p drag': ((1.0, 3.0),),
                  'motor': ((0.5, 1.5),)}[kind]
        for attempt in range(10):
            w = _build(seed, index + 100_000 * attempt, (), (), situations, noise, tricks,
                       (1.0,) if template == 'fast' else (0.6, 1.0), terms, limits)
            if all(np.all(np.isfinite(t.x)) and np.max(np.abs(t.x)) < 50 and np.max(np.abs(t.v)) < 50
                   for t in w.throws + w.held_out):
                break
        w.force = kind
        w.truth = None
    elif template == 'default' and kind not in ('swing small', 'faint rubbing') and '+' not in kind:
        w = worlds.make(seed, kind, index=index, situations=situations, noise=noise, tricks=tricks)
    else:
        names = kind.split('+') if '+' in kind else [kind]
        names = [{'swing small': 'swing', 'faint rubbing': 'rubbing'}.get(n, n) for n in names]
        ideas = tuple(P.FORCES[n][0] for n in names) if kind != 'none' else ()
        limits = tuple((0.1, 0.3) if kind == 'faint rubbing' else P.FORCES[n][1]
                       for n in names) if kind != 'none' else ()
        choices = (1.0,) if template == 'fast' else ((0.2, 0.3) if kind == 'swing small' else (0.6, 1.0))
        w = _build(seed, index, ideas, limits, situations, noise, tricks, choices)
        w.force = kind
    w.tools = ({'durations': (0.2, 0.4, 0.8, 1.2, 1.6),
                'commands': (-1.5, -1.0, -0.5, 0.5, 1.0, 1.5)} if template == 'large' else None)
    w.kind_name = kind
    w.template = template
    return w


class Curriculum:
    def __init__(self, order, seed, stage_cap=12, explore=0.2):
        if order not in ('ladder', 'progress', 'random'):
            raise ValueError(order)
        self.order, self.seed = order, seed
        self.stage_cap, self.explore = stage_cap, explore
        self.calls = 0
        self.history = {kind: [] for kind in PRACTICE_KINDS}
        self.mastered = set()
        self.round_robin = {name: 0 for name, _ in STAGES}

    def _finished(self, stage):
        name, kinds = STAGES[stage]
        return all(k in self.mastered for k in kinds) or sum(len(self.history[k]) for k in kinds) >= self.stage_cap

    def _unlocked(self):
        count = 1
        while count < len(STAGES) and self._finished(count - 1):
            count += 1
        return count

    def next_kind(self, board=None, placement=False):
        rng = np.random.default_rng([self.seed, 31, self.calls])
        self.calls += 1
        if self.order == 'random':
            kind = str(rng.choice(PRACTICE_KINDS))
        elif self.order == 'ladder':
            unlocked = self._unlocked()
            stage = next((i for i in range(unlocked) if not self._finished(i)), unlocked - 1)
            name, kinds = STAGES[stage]
            choices = tuple(k for k in kinds if k not in self.mastered) or kinds
            pos = self.round_robin[name]
            kind = choices[pos % len(choices)]
            self.round_robin[name] = pos + 1
        else:
            choices = tuple(k for _, ks in STAGES[:self._unlocked()] for k in ks)
            if rng.random() < self.explore:
                kind = str(rng.choice(choices))
            else:
                def progress(k):
                    tries = [h['tries'] for h in self.history[k]]
                    if len(tries) < 2:
                        return float('inf')
                    return abs(float(np.mean(tries[-3:])) - float(np.mean(tries[-6:-3]))) if len(tries) > 3 else 0.0
                kind = max(choices, key=progress)
        template = 'default'
        if placement and board is not None:
            hint = board.placement_hint()
            if hint is not None:
                suggested_template, suggested_kind = hint
                if suggested_template in ('large', 'fast'):
                    template = suggested_template
                    if suggested_template == 'large' and suggested_kind in PRACTICE_KINDS:
                        kind = suggested_kind
        return kind, template

    def record(self, kind, tries, correct_unaided, hinted):
        if kind not in PRACTICE_KINDS:
            raise ValueError(kind)
        self.history[kind].append({'tries': int(tries), 'correct_unaided': bool(correct_unaided),
                                   'hinted': bool(hinted)})
        if correct_unaided and not hinted:
            self.mastered.add(kind)

    def state(self):
        return {'order': self.order, 'seed': self.seed, 'stage_cap': self.stage_cap,
                'explore': self.explore, 'calls': self.calls,
                'unlocked_stages': [name for name, _ in STAGES[:self._unlocked()]],
                'mastered_kinds': [k for k in PRACTICE_KINDS if k in self.mastered],
                'counts_per_kind': {k: len(self.history[k]) for k in PRACTICE_KINDS},
                'history': self.history, 'round_robin': self.round_robin}

    @classmethod
    def from_state(cls, state):
        obj = cls(state['order'], state['seed'], state['stage_cap'], state['explore'])
        obj.calls = state['calls']
        obj.history = {k: list(state['history'][k]) for k in PRACTICE_KINDS}
        obj.mastered = set(state['mastered_kinds'])
        obj.round_robin = dict(state['round_robin'])
        return obj


def validate(seed, kind, index=0):
    w = make_world(seed, kind, index, tricks=0.0)
    max_x = max_acc = 0.0
    finite = True
    for throw in w.throws + w.held_out:
        x, v = throw.x, throw.v
        time = np.arange(x.size) * paths.DT_OBS
        hand_force = np.where(time < paths.T_PUSH - 1e-9, worlds.hand(throw.u), 0.0)
        acc = (w.true_force(x, v, time) + hand_force) / w.masses[throw.situation]
        finite = finite and bool(np.all(np.isfinite(x)) and np.all(np.isfinite(v)) and np.all(np.isfinite(acc)))
        max_x = max(max_x, float(np.max(np.abs(x))))
        max_acc = max(max_acc, float(np.max(np.abs(acc))))
    return {'ok': bool(finite and max_x < 50 and max_acc < paths.CLIP),
            'max_abs_x': max_x, 'max_abs_acc': max_acc, 'truth': KIND_TRUTH[kind]}
