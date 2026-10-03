"""Worlds whose law is in no list (the author, 2026-09-27: "NOT A LIST but discovering on its own"; "first demonstrated
invention and discovery without support").

The hidden force is a smooth shape along one input that no term of the judge's dictionary is. It is drawn on the
judge's own 17-knot grid (paths' cell hats), so the world's simulator moves it exactly, and a free curve on that grid
(the cell ('cell', input, 17)) is its exact family: SERA can find it only by shaping a curve from its own
measurements, never by picking an entry of a list.

Each world is checked to be new: every law of the dictionary a claim can name (every truth-v1 law, and every grown
piece or piece product alone and with each simple idea) misses the true force by more than NOVEL_GAP somewhere in the
region SERA can reach (least squares on the noise-free force), or the world is drawn again.

Where it can reach (the first probe, 2026-09-27 17:45 UTC): on the teacher's throws alone no shape was new - the
teacher's gentle pushes keep every object at low speed and near the middle, where each shape is one straight piece of
its grid (a list law matched it to 1e-16). So the region is the teacher's throws plus, on every object, the strongest
pushes SERA's own hand can make (command +-1 for 1.2 s and for the whole 2 s): the new law shows only where SERA
goes itself. Nothing here is shown to SERA; the probe throws are the observer's.
"""
import math
import types

import numpy as np

from ccops5.core import curriculum, grammar, paths, worlds as W
from . import worlds as SW

K = 17
NOVEL_GAP = 0.4                  # 2 eps: no list law comes within this of the truth where the teacher's throws go

# The hidden shapes (never shown to SERA; names for the observer only). Each is a function of one input, scaled to
# at most 1 in size on the rail, times a strength drawn per world.
SHAPES = {
    'fading drag': ('speed', lambda s: -s * np.exp(-s * s / 4.0) / 1.3),        # drags, then lets go at speed
    'dead zone': ('speed', lambda s: -np.sign(s) * np.maximum(0.0, np.abs(s) - 1.0) / 2.0),   # nothing below |v| 1
    'soft wall': ('position', lambda s: -np.sign(s) * np.maximum(0.0, np.abs(s) - 0.8) ** 2),  # a wall past |x| 0.8
    'ripple': ('position', lambda s: -np.sin(2.5 * s) * np.exp(-s * s / 3.0)),   # a washboard that fades out
}


class NovelWorld(curriculum.MultiWorld):
    """A MultiWorld whose hidden law is one 17-knot cell (its knot values the shape's, times the strength)."""

    def _codes(self):
        codes = grammar.term_codes(self.hidden_terms[0])
        return (np.array([c[0] for c in codes], np.int64), np.array([c[1] for c in codes], np.int64),
                np.array([c[2] for c in codes], np.int64), np.array(self.hidden_coefs, float))


def knots(shape):
    inp, f = SHAPES[shape]
    j = grammar.CELL_INPUTS.index(inp)
    return inp, f(np.linspace(paths.CELL_LO[j], paths.CELL_HI[j], K))


def novel_world(shape, seed, n, tries=40, *, known=None):
    """World n of a hidden shape (deterministic in seed, shape and n): 8 objects, the teacher's 2 pushes each, M-1
    knocks at the usual rate; drawn again until no list law comes within NOVEL_GAP. known=(attempt, gap, nearest): an
    observer that already measured this world's novelty rebuilds that same attempt without measuring it again."""
    inp, w = knots(shape)
    reasons = []
    for attempt in (range(tries) if known is None else (known[0],)):
        rng = np.random.default_rng([seed, 83, list(SHAPES).index(shape), n, attempt])
        strength = float(rng.uniform(1.5, 2.5))
        term = ('cell', inp, K)
        coefs = tuple(float(c) for c in strength * w)
        masses3 = [float(m) for m in rng.uniform(0.6, 2.5, size=3)]
        index = 8000 + 100 * list(SHAPES).index(shape) + n + 10000 * attempt
        world = NovelWorld(seed, index, shape, (term,), coefs[0], 0, None, [], [], (0.001, 0.001), [], [],
                           ideas=(), coefs=(), hidden_terms=(term,), hidden_coefs=coefs)
        kinds, a, b, cf = world._codes()
        for k in range(8):
            m = float(rng.choice(masses3))
            bump = ((float(rng.choice([0.6, 0.8, 1.0, 1.2])), float(rng.choice([-1.5, 1.5])))
                    if rng.random() < 0.05 else None)
            pushes = (float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0])))
            world.masses.append(m)
            world.bumps.append(bump)
            world.teacher_pushes.append(pushes)
            for j, u in enumerate(pushes):
                t0, amp = bump if bump else (0.0, 0.0)
                xs, vs = paths.simulate(W.hand(u), 1.0 / m, kinds, a, b, cf, 1.0, 1.0, t0, amp)
                nr = np.random.default_rng([seed, 31, 0, index, k, j])
                world.throws.append(W.Throw(k, len(world.throws), W.push_of(u), xs + nr.normal(0, 0.001, xs.size),
                                            vs + nr.normal(0, 0.001, vs.size), 'teacher'))
        world.level = 8
        world.spec = types.SimpleNamespace(seed=seed, index=index, level=8, family=(term,), coefs=coefs,
                                           sigma=(0.001, 0.001), shape=shape)
        gap, nearest = list_gap(world) if known is None else known[1:]
        if gap >= NOVEL_GAP:
            world.novelty = dict(gap=gap, nearest=nearest, attempt=attempt)
            return world
        reasons.append(f'{nearest} comes within {gap:.2g}')
    raise RuntimeError(f'no novel world of {shape}: {reasons[-3:]}')


REACH = tuple(W.Action(((0.0, d, u),)) for u in (1.0, -1.0) for d in (1.2, 2.0))   # the strongest pushes it can make


def reach_throws(world):
    """Noise-free readings of the strongest pushes on every object (the observer's, never SERA's)."""
    kinds, a, b, cf = world._codes()
    out = []
    for k, m in enumerate(world.masses):
        for act in REACH:
            xs, vs = paths.simulate_program(*act.arrays(), 1.0 / m, kinds, a, b, cf, 1.0, 1.0, 0.0, 0.0)
            out.append(W.Throw(k, -1, act, xs, vs, 'probe'))
    return out


def list_gap(world):
    """(the smallest largest-gap of any list law to the true force where SERA can reach, that law's name)."""
    xs, vs, ts = SW._states(world, reach_throws(world))
    F = world.true_force(xs, vs, ts)
    gaps = SW.rival_gaps(world, xs, vs, ts)                              # every truth-v1 certifiable law
    for g in grammar.GROWN_TERMS:
        if g[0] == 'cell':
            continue
        for fam in [(g,)] + [(g, i) for i in grammar.IDEAS]:
            cols = [np.array([paths.term_t(k, a, b, x, v, t, 1.0, 1.0) for x, v, t in zip(xs, vs, ts)])
                    for tm in fam for k, a, b in grammar.term_codes(tm)]
            X = np.stack(cols, 1)
            c, *_ = np.linalg.lstsq(X, F, rcond=None)
            gaps[grammar.canonical(fam)] = float(np.max(np.abs(F - X @ c)))
    best = min(gaps, key=gaps.get)
    return gaps[best], grammar.name(best)
