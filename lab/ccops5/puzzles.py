"""ccops5 lab | puzzle worlds: practice at discovering.

Each puzzle world is a small new universe with one hidden extra force acting
on its objects. The learner already knows its own hand (it learned that as a
baby, in the main lab) and has to find the extra force. Laws found in one
world are not carried to the next: what can carry over is the skill of
finding them.

Every learner with the same seed lives exactly the same worlds: same objects,
same pushes, same sensor noise. Only the mind differs.

Built as an isolated experiment. Not part of sera-field.
"""
import numpy as np

from . import world as W

INPUTS = ('position', 'speed')
SHAPES = ('straight', 'growing', 'steps', 'cubic', 'wave')
# Every explanation the learner can imagine: a shape along one input, or a
# steady push that depends on nothing.
IDEAS = tuple((i, s) for i in INPUTS for s in SHAPES) + (('nothing', 'steady'),)


def shape_of(shape, s):
    if shape == 'straight':
        return s
    if shape == 'growing':
        return s * np.abs(s)
    if shape == 'steps':
        return np.tanh(s / 0.05)
    if shape == 'cubic':
        return s ** 3
    if shape == 'wave':
        return np.sin(s)
    raise ValueError(shape)


def idea_value(idea, x, v):
    source, shape = idea
    if source == 'nothing':
        return np.ones_like(np.asarray(x, dtype=float))
    return shape_of(shape, x if source == 'position' else v)


# Hidden forces: the idea that explains each one, and how strong it can be.
# Each pushes back against the motion or the position, except the slope,
# which always pushes one way.
FORCES = {
    'rubbing': (('speed', 'straight'), (0.5, 1.5)),
    'water drag': (('speed', 'growing'), (1.0, 3.0)),
    'dry friction': (('speed', 'steps'), (0.5, 1.2)),
    'thick oil': (('speed', 'cubic'), (1.0, 4.0)),
    'spring': (('position', 'straight'), (3.0, 9.0)),
    'tight spring': (('position', 'growing'), (3.0, 10.0)),
    'stiff spring': (('position', 'cubic'), (5.0, 20.0)),
    'swing': (('position', 'wave'), (6.0, 12.0)),
    'valley': (('position', 'steps'), (1.0, 3.0)),
    'slope': (('nothing', 'steady'), (0.5, 1.5)),
}
PRACTICE = ('rubbing', 'water drag', 'dry friction', 'spring', 'tight spring', 'stiff spring', 'swing', 'slope')
# Each is a shape it practised, along the other input: speed-cubic (practised
# only on position) and position-steps (practised only on speed).
NEVER_SHOWN = ('thick oil', 'valley')
PRACTICE_WORLDS = 40
SITUATIONS = 10
TRICKS = 0.05


def simulate(world, m, u, rng, trick=None):
    """Push the object from rest with command u; noisy readings, as in the nursery."""
    idea = FORCES[world['force']][0]
    strength, sign = world['strength'], world['sign']

    def accel(x, v, f):
        return (f - sign * strength * float(idea_value(idea, x, v))) / m

    x = v = 0.0
    xs, vs = [x], [v]
    per, step = int(round(W.DT_OBS / W.DT_SIM)), 0
    for _ in range(W.N_OBS - 1):
        for _ in range(per):
            t = step * W.DT_SIM
            f = W.hand_force(u) if t < W.T_PUSH - 1e-9 else 0.0
            if trick and trick[0] - 1e-9 <= t < trick[1] - 1e-9:
                f += trick[2]
            h = W.DT_SIM
            k1x, k1v = v, accel(x, v, f)
            k2x, k2v = v + .5 * h * k1v, accel(x + .5 * h * k1x, v + .5 * h * k1v, f)
            k3x, k3v = v + .5 * h * k2v, accel(x + .5 * h * k2x, v + .5 * h * k2v, f)
            k4x, k4v = v + h * k3v, accel(x + h * k3x, v + h * k3v, f)
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            step += 1
        xs.append(x)
        vs.append(v)
    return (np.array(xs) + rng.normal(0, W.SIGMA_X, W.N_OBS),
            np.array(vs) + rng.normal(0, W.SIGMA_V, W.N_OBS))


def school_plan(seed):
    """40 practice worlds (5 of each practised force), then a 12-world exam:
    every practised force once and each never-shown force twice."""
    rng = np.random.default_rng([seed, 2026])
    practice = [PRACTICE[i % len(PRACTICE)] for i in range(PRACTICE_WORLDS)]
    rng.shuffle(practice)
    exam = list(PRACTICE) + list(NEVER_SHOWN) * 2
    rng.shuffle(exam)
    worlds = []
    for part, forces in (('practice', practice), ('exam', exam)):
        for force in forces:
            lo, hi = FORCES[force][1]
            world = {'part': part, 'force': force, 'strength': float(rng.uniform(lo, hi)),
                     'sign': float(rng.choice([-1.0, 1.0])) if force == 'slope' else 1.0,
                     'masses': [float(m) for m in rng.uniform(0.6, 2.5, size=3)], 'situations': []}
            for _ in range(SITUATIONS):
                trick = None
                if rng.random() < TRICKS:
                    start = float(rng.choice([0.6, 0.8, 1.0, 1.2]))
                    trick = (start, start + 0.2, float(rng.choice([-1.5, 1.5])))
                # Its habit: push once each way, then a test push it will not learn from.
                world['situations'].append({
                    'm': float(rng.choice(world['masses'])), 'trick': trick,
                    'pushes': (float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0]))),
                    'check_u': float(rng.choice(W.CHECK_COMMANDS))})
            worlds.append(world)
    return worlds


def explain(idea):
    source, shape = idea
    return 'a steady push' if source == 'nothing' else f'{shape} with {source}'
