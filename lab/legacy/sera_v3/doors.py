"""Where SERA's worlds come from (plan revision 5, WP4): the doors it may choose, the teaching list, the yardstick,
and the rule by which it chooses (learning progress).

A door is an opaque name over a world generator; SERA never sees what is behind it, only what it proves there (its
door map). Physics doors (Stage 5 adds rooms and code):
  door 1   one or two simple ideas (L1-L2)
  door 2   an invented term, alone or with an idea (L3-L4)
  door 3   a straight term hiding a weak, deeper one (L5)
  door 4   a grown piece, alone or with an idea (L6-L7)
  door 5   doors 1-2's laws with twice the sensor noise
Choosing (Stage 3; docs/SERA_PLAYROOM.md §5, reviewed by independent review): competence on a door is the share of verified
proofs among its last 8 worlds; learning progress LP = |competence of the last 8 - of the 8 before|; a door with
fewer than 16 worlds has LP = 0.5 (optimism, so every door is tried). Every 4 worlds a door is drawn with
probability proportional to LP + 0.05 (the same door may be drawn again). The playroom design's "keep it until its
LP falls below the median" was dropped before any run: with most doors at LP 0 the median is 0, and a door at 0 is
never below it, so SERA would stay forever in a door where it learns nothing (found by the unit test). Its own goals
(sera.agent) add to a door's value what its door map says about meeting them there.
"""
import numpy as np

from ccops5.core import grammar
from . import worlds as SW

DOORS = {1: dict(levels=(1, 2)), 2: dict(levels=(3, 4)), 3: dict(levels=(5,)), 4: dict(levels=(6, 7)),
         5: dict(levels=(1, 2, 3, 4), noise=2.0)}
WINDOW, OPTIMISM, EPS_LP, RECHECK = 8, 0.5, 0.05, 4
STAGE_BASE = {'teach': 60_000, 'practice': 61_000, 'alone': 62_000, 'yardstick': 70_000, 'check': 69_000,
              'newdoors': 63_000}
NEW_DOORS = {6: 'rooms', 7: 'code'}                 # Stage 5 (sera.rooms, sera.codedoor): opened, never explained


def new_door_world(door, seed, n):
    """World n behind a Stage 5 door: a playroom room (door 6) or a code task (door 7)."""
    if door == 6:
        from . import rooms
        return rooms.room_world(seed, n)
    from . import codedoor
    return codedoor.code_world(seed, n)


def door_world(door, seed, n, stage):
    """World n behind a door (deterministic in seed, door and n)."""
    spec = DOORS[door]
    rng = np.random.default_rng([seed, 23, door, n, STAGE_BASE[stage]])
    level = int(rng.choice(spec['levels']))
    index = STAGE_BASE[stage] + 100 * n + door
    return SW.make(seed, index, level, 'any', noise=spec.get('noise', 1.0))


def make_with(seed, index, family, level, noise=1.0, tries=60):
    """A validated world of a given law (for the teaching list): the first valid draw of strengths, masses and
    pushes, index, index + 100000, ..."""
    family = grammar.canonical(family)
    reasons = []
    for attempt in range(tries):
        rng = np.random.default_rng([seed, 31, level, index + 100_000 * attempt])
        coefs = SW.sample_coefs(rng, family, level)
        masses3 = [float(m) for m in rng.uniform(0.6, 2.5, size=3)]
        masses, bumps, pushes, checks = [], [], [], []
        for _ in range(8):
            masses.append(float(rng.choice(masses3)))
            bumps.append((float(rng.choice([0.6, 0.8, 1.0, 1.2])), float(rng.choice([-1.5, 1.5])))
                         if rng.random() < 0.05 else None)
            pushes.append((float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0]))))
            checks.append(float(rng.choice((-0.9, -0.5, 0.5, 0.9))))
        w = SW.build(SW.Spec(seed, index + 100_000 * attempt, level, family, coefs, masses, bumps, pushes, checks,
                             noise))
        ok, why = SW.validate(w)
        if ok:
            return w
        reasons.append(why)
    raise RuntimeError(f'no valid world of {grammar.name(family)}: {reasons[-3:]}')


# Stage 1 (17 worlds; cut from 34 before any Stage 1 run, because Stage 0 measured a proof at 7-18 minutes: the
# simple ideas are innate, so their worlds mostly ground words, and every world carries three sentences anyway)
TEACH_IDEAS = (('position', 'straight'), ('speed', 'straight'), ('speed', 'steps'), ('nothing', 'steady'),
               ('position', 'cubic'), ('speed', 'growing'))
# Revision 5.1 (2026-09-27, colab-upload/teach_probe.py): |v|^1.5 and sin 2t cannot be built as valid worlds - their
# dictionary neighbours (|v|^1.4 plus a wave, sin 2.1t) mimic them within 0.005, so no world of a power or a drive is
# identifiable - and the first Stage 1 run stopped on it. Two products take their places; x * sin v stays untaught
# (SERA found it itself in Stage 0: it remains a test of its own discovery).
TEACH_LAWS = ([((t,), 1) for t in TEACH_IDEAS]
              + [((('position', 'straight'), ('speed', 'straight')), 2), ((('nothing', 'steady'), ('speed', 'steps')), 2),
                 ((('position', 'cubic'), ('speed', 'straight')), 2)]
              + [((('product', 'straight', 'straight'),), 3), ((('product', 'cubic', 'straight'),), 3),
                 ((('product', 'straight', 'steps'),), 3)] * 2
              + [((('piece', 'speed', 'abs', 0.0),), 6)] * 2)
TEACH_TERMS = (('product', 'straight', 'straight'), ('product', 'cubic', 'straight'), ('product', 'straight', 'steps'),
               ('piece', 'speed', 'abs', 0.0))


def teaching_worlds(seed):
    """Stage 1's 17 worlds, in a fixed shuffled order (so no kind comes all at once): (n, a function that builds
    world n) - a world is built only when it is lived (a build takes about 20 s)."""
    order = np.random.default_rng([seed, 47]).permutation(len(TEACH_LAWS))
    for n, i in enumerate(order):
        fam, level = TEACH_LAWS[i]
        yield n, (lambda n=n, fam=fam, level=level: make_with(seed, STAGE_BASE['teach'] + n, fam, level))


YARDSTICK = [(1, 1)] * 4 + [(1, 2)] * 4 + [(2, 3)] * 4 + [(2, 4)] * 4 + [(3, 5)] * 2 + [(4, 6)] * 2 + [(4, 7)] * 2 + \
            [(5, 2)] * 2


def yardstick_worlds(seed):
    """The frozen 24-world yardstick (dev seed: `seed`; the final run uses a fresh seed): (n, door, a function that
    builds world n)."""
    for n, (door, level) in enumerate(YARDSTICK):
        yield n, door, (lambda n=n, door=door, level=level: SW.make(seed, STAGE_BASE['yardstick'] + n, level, 'any',
                                                                    noise=DOORS[door].get('noise', 1.0)))


class Curriculum:
    """Learning progress over doors (Stage 3)."""

    def __init__(self, doors=tuple(DOORS), seed=0):
        self.doors = tuple(doors)
        self.outcomes = {d: [] for d in self.doors}
        self.current, self.since = None, 0
        self.rng = np.random.default_rng([seed, 29])

    def competence(self, d, back=0):
        o = self.outcomes[d]
        w = o[len(o) - back - WINDOW:len(o) - back] if len(o) - back >= WINDOW else []
        return float(np.mean(w)) if w else None

    def lp(self, d):
        if len(self.outcomes[d]) < 2 * WINDOW:
            return OPTIMISM
        return abs(self.competence(d) - self.competence(d, WINDOW))

    def choose(self, bonus=None):
        """The next door, and why (LP of every door, whether it drew again)."""
        lps = {d: self.lp(d) for d in self.doors}
        switch = self.current is None or self.since >= RECHECK
        if switch:
            v = np.array([lps[d] + EPS_LP + (bonus or {}).get(d, 0.0) for d in self.doors])
            self.current = self.doors[int(self.rng.choice(len(self.doors), p=v / v.sum()))]
            self.since = 0
        self.since += 1
        return self.current, dict(lp={d: round(x, 3) for d, x in lps.items()}, switched=bool(switch))

    def add_doors(self, doors):
        """Stage 5: new doors open; their optimism (OPTIMISM until 2 * WINDOW tries) makes SERA try them."""
        for d in doors:
            if d not in self.outcomes:
                self.doors = self.doors + (d,)
                self.outcomes[d] = []

    def record(self, door, proved):
        self.outcomes[door].append(1.0 if proved else 0.0)
