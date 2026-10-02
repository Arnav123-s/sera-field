"""Stage 5's rooms door (plan revision 5, B3 Stage 5): the playroom (ccops5.core.playroom) as a world SERA's mind can
live, and what SERA learns there about things.

A room holds 4-6 things. SERA sees each thing's look (three integer codes: material, size, shape, through a fixed
secret coding; never the words) and throws it; the thing's mass is hidden and set by its kind. The room's law is one
of the curriculum's regimes (a simple idea or a pair). In Stage 5 the caretaker is silent.

The world is the same kind of object the judge and the mind already use (a curriculum.MultiWorld built as
sera.worlds.build builds one): the teacher's two pushes per thing, fresh noise for every push, M-1 knocks per thing.
It also carries `looks` (what SERA sees) and `room` (the hidden room, for the observer only).

Kinds: a look predicts a mass. SERA keeps, per look, the log masses of the things it weighed itself (the leading
law's inverse mass for each thing, never the hidden truth), and predicts a new thing's mass from its look before
throwing it: the look's mean shrunk toward the mean of everything it weighed (a normal model, prior strength K0
things). Nobody tells it that iron is heavy; if its predictions improve room after room, it found that out itself.
The kinds never reach the judge.
"""
import math
import types

import numpy as np

from ccops5.core import curriculum, grammar, paths, playroom as PL, worlds as W

K0 = 2.0                         # prior strength (things) of the mean over every look


def room_world(seed, n):
    """Room n of this seed as a world the mind can live (deterministic)."""
    room = PL.make_room(seed, 5000 + n)
    rng = np.random.default_rng([seed, 97, n])
    fam = grammar.canonical(room.terms)
    w = curriculum.MultiWorld(seed, 5000 + n, room.regime, fam, room.coefs[0] if room.coefs else 0.0, 0, None, [], [],
                              room.sigma, [], [], ideas=(), coefs=(), hidden_terms=tuple(room.terms),
                              hidden_coefs=tuple(room.coefs))
    kinds, a, b, coefs = w._codes()
    for k, thing in enumerate(room.things):
        w.masses.append(thing.mass)
        w.bumps.append(thing.bump)
        pushes = (float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0])))
        w.teacher_pushes.append(pushes)
        for j, u in enumerate(pushes):
            t0, amp = thing.bump if thing.bump else (0.0, 0.0)
            xs, vs = paths.simulate(W.hand(u), 1.0 / thing.mass, kinds, a, b, coefs, 1.0, 1.0, t0, amp)
            nr = np.random.default_rng([seed, 31, 0, 5000 + n, k, j])
            w.throws.append(W.Throw(k, len(w.throws), W.push_of(u), xs + nr.normal(0, room.sigma[0], xs.size),
                                    vs + nr.normal(0, room.sigma[1], vs.size), 'teacher'))
    w.level = 0
    w.spec = types.SimpleNamespace(seed=seed, index=5000 + n, level=0, family=fam, sigma=room.sigma)
    w.looks = [tuple(int(c) for c in t.look) for t in room.things]
    w.room = room
    return w


def measured_masses(report):
    """{thing: mass} from SERA's own fit (the claimed law's posterior inverse mass); knocked things are left out."""
    ledger, fam = report.ledger, grammar.canonical(report.claim)
    if fam not in ledger.post:
        return {}
    post, nc = ledger.post[fam], ledger._models[fam].n_coef
    out = {}
    for i, s in enumerate(post.order):
        if int(np.argmax(post.knock.get(s, (0.0,)))) != 0:
            continue
        mu = float(post.mean[nc + i])
        if mu > 0 and math.isfinite(mu):
            out[int(s)] = 1.0 / mu
    return out


class Kinds:
    """Per look: the log masses SERA weighed itself."""

    def __init__(self):
        self.obs = {}

    def predict(self, look):
        """(predicted mass, how many things of this look it has weighed); None before anything was weighed."""
        every = [m for ms in self.obs.values() for m in ms]
        if not every:
            return None, 0
        mine = self.obs.get(tuple(look), [])
        g = float(np.mean(every))
        est = (K0 * g + sum(mine)) / (K0 + len(mine))
        return math.exp(est), len(mine)

    def learn(self, look, mass):
        self.obs.setdefault(tuple(look), []).append(math.log(mass))

    def statements(self, k=4):
        """Its lesson in words: the looks it has weighed most, heaviest first (read off its own table)."""
        rows = sorted(((look, math.exp(float(np.mean(ms))), len(ms)) for look, ms in self.obs.items() if len(ms) >= 2),
                      key=lambda r: -r[2])[:k]
        return [f'Things that look like {list(look)} weigh about {m:.2g} (from {n} I weighed).'
                for look, m, n in sorted(rows, key=lambda r: -r[1])]
