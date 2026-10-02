"""Connect the original puzzle school to the core mind without changing its observations."""

import numpy as np

from .. import inventor, puzzles, world
from . import gaps, grammar, worlds


def legacy_school_world(seed, i):
    """Return school world i with the exact teacher and check readings of the legacy school."""
    plan = puzzles.school_plan(seed)
    source = plan[i]
    idea = puzzles.FORCES[source['force']][0]
    result = worlds.World(seed, i, source['force'], (idea,),
                          -source['sign'] * source['strength'], 0, idea,
                          [], [], (world.SIGMA_X, world.SIGMA_V), [], [])
    result.part = source['part']
    for k, sit in enumerate(source['situations']):
        result.masses.append(sit['m'])
        trick = sit['trick']
        result.bumps.append((trick[0], trick[2]) if trick is not None else None)
        result.teacher_pushes.append(sit['pushes'])
        rng = np.random.default_rng([seed, i, k])
        for u in sit['pushes']:
            x, v = puzzles.simulate(source, sit['m'], u, rng, trick)
            result.throws.append(worlds.Throw(k, len(result.throws), worlds.push_of(u), x, v, 'teacher'))
        x, v = puzzles.simulate(source, sit['m'], sit['check_u'], rng, trick)
        result.held_out.append(worlds.Throw(k, -1, worlds.push_of(sit['check_u']), x, v, 'check'))
    return result


class _InventorWorld(worlds.World):
    """Preserve the inventor's size products, which the core simulator cannot encode."""

    def true_force(self, x, v, t=None):
        if self.representable:
            return super().true_force(x, v, t)
        return self.coef * inventor.idea_value(self.legacy_idea, np.ravel(np.asarray(x, float)),
                                                np.ravel(np.asarray(v, float)))

    def push(self, k, action, tag='own'):
        if self.representable:
            return super().push(k, action, tag)
        j = self.made.get(k, 0)
        self.made[k] = j + 1
        trick = self.legacy_tricks[k]
        m = self.masses[k]
        x = v = 0.0
        xs, vs = [x], [v]
        step = 0

        def accel(px, pv, hand):
            raw = (hand + self.coef * float(inventor.idea_value(self.legacy_idea, px, pv))) / m
            return float(np.clip(raw, -100, 100))

        for _ in range(world.N_OBS - 1):
            for _ in range(int(round(world.DT_OBS / world.DT_SIM))):
                t = step * world.DT_SIM
                hand = sum(world.hand_force(u) for start, end, u in action.segments
                           if start - 1e-9 <= t < end - 1e-9)
                if trick and trick[0] - 1e-9 <= t < trick[1] - 1e-9:
                    hand += trick[2]
                h = world.DT_SIM
                k1x, k1v = v, accel(x, v, hand)
                k2x, k2v = v + .5 * h * k1v, accel(x + .5 * h * k1x, v + .5 * h * k1v, hand)
                k3x, k3v = v + .5 * h * k2v, accel(x + .5 * h * k2x, v + .5 * h * k2v, hand)
                k4x, k4v = v + h * k3v, accel(x + h * k3x, v + h * k3v, hand)
                x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
                v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
                step += 1
            xs.append(x)
            vs.append(v)
        rng = np.random.default_rng([self.seed, 7, self.index, k, 100 + j])
        throw = worlds.Throw(k, len(self.log), action,
                             np.array(xs) + rng.normal(0, self.sigma[0], len(xs)),
                             np.array(vs) + rng.normal(0, self.sigma[1], len(vs)), tag)
        self.log.append(throw)
        return throw


def legacy_inventor_world(seed, i):
    """Return inventor world i with the exact legacy teacher and check readings."""
    source = inventor.school_plan(seed)[i]
    idea = inventor.FORCES[source['force']][0]
    term = (('product', idea[0][1], idea[1][1]) if isinstance(idea[0], tuple) else idea)
    truth = grammar.canonical((term,))
    representable = truth in grammar.space(inventions=(term,) if term in gaps.open_terms() else ())
    result = _InventorWorld(seed, i, source['force'], truth if representable else None,
                            -source['sign'] * source['strength'], 4 if isinstance(idea[0], tuple) else 0,
                            term if representable else None, [], [], (world.SIGMA_X, world.SIGMA_V), [], [])
    result.part = ('never_shown' if source['part'] == 'exam' and source['force'] in inventor.NEVER_SHOWN
                   else source['part'])
    result.representable = representable
    result.legacy_idea = idea
    result.legacy_tricks = []
    for k, sit in enumerate(source['situations']):
        result.masses.append(sit['m'])
        trick = sit['trick']
        result.legacy_tricks.append(trick)
        result.bumps.append((trick[0], trick[2]) if trick is not None else None)
        result.teacher_pushes.append(sit['pushes'])
        rng = np.random.default_rng([seed, i, k])
        for u in sit['pushes']:
            x, v = inventor.simulate(source, sit['m'], u, rng, trick)
            result.throws.append(worlds.Throw(k, len(result.throws), worlds.push_of(u), x, v, 'teacher'))
        x, v = inventor.simulate(source, sit['m'], sit['check_u'], rng, trick)
        result.held_out.append(worlds.Throw(k, -1, worlds.push_of(sit['check_u']), x, v, 'check'))
    return result
