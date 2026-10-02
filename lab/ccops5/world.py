"""ccops5 lab | the nursery world.

The world keeps its physics hidden. The learner only sees appearances, its
own commands, a caretaker's words, and noisy position and velocity readings.

Built as an isolated experiment. Not part of sera-field.
"""
import math

import numpy as np

DT_SIM = 0.005          # world integration step (seconds)
DT_OBS = 0.05           # time between readings
T_PUSH = 0.4            # how long a push lasts
T_END = 2.0             # how long each trial is watched
SIGMA_X = 0.001         # position sensor noise
SIGMA_V = 0.001         # velocity sensor noise
APP_DIM = 8             # numbers describing what a thing looks like
N_OBS = int(round(T_END / DT_OBS)) + 1
PUSH_INTERVALS = int(round(T_PUSH / DT_OBS))
SCENES = ('body', 'ice', 'carpet', 'water', 'spring', 'swing')
COMMANDS = (-1.0, -0.6, -0.3, 0.3, 0.6, 1.0)
CHECK_COMMANDS = (-0.9, -0.5, 0.5, 0.9)
WORDS = ('heavy', 'light', 'rough', 'smooth', 'flat', 'round')
STAGES = ('0 own hand', '1 toys on ice', '2 toys on carpet', '3 toys in water',
          '4 springs', '5 swings', '6 new toys, words only', '7 stuck together', '8 final check')


def hand_force(u):
    """Hidden muscle law: the force a command u in [-1, 1] really produces."""
    return 3.0 * math.tanh(1.6 * u)


def _accel(p, x, v, f):
    if p['swing']:
        return (f - p['b'] * v) / p['m'] - p['gl'] * math.sin(x)
    return (f - p['b'] * v - p['c'] * v * abs(v) - p['k'] * x) / p['m']


def simulate(p, u, rng):
    """Put the object at rest, push with command u, return noisy readings."""
    x = v = 0.0
    xs, vs = [x], [v]
    per_obs = int(round(DT_OBS / DT_SIM))
    trick = p.get('trick')
    step = 0
    for _ in range(N_OBS - 1):
        for _ in range(per_obs):
            t = step * DT_SIM
            f = hand_force(u) if t < T_PUSH - 1e-9 else 0.0
            if trick and trick[0] - 1e-9 <= t < trick[1] - 1e-9:
                f += trick[2]
            h = DT_SIM
            k1x, k1v = v, _accel(p, x, v, f)
            k2x, k2v = v + .5 * h * k1v, _accel(p, x + .5 * h * k1x, v + .5 * h * k1v, f)
            k3x, k3v = v + .5 * h * k2v, _accel(p, x + .5 * h * k2x, v + .5 * h * k2v, f)
            k4x, k4v = v + h * k3v, _accel(p, x + h * k3x, v + h * k3v, f)
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            step += 1
        xs.append(x)
        vs.append(v)
    return (np.array(xs) + rng.normal(0, SIGMA_X, N_OBS),
            np.array(vs) + rng.normal(0, SIGMA_V, N_OBS))


def _toys(rng, n, prefix):
    return [{'name': f'{prefix}{i}', 'app': rng.normal(size=APP_DIM),
             'm': float(rng.uniform(0.6, 2.5)), 'b': float(rng.uniform(0.3, 1.5)),
             'c': float(rng.uniform(2.0, 4.0))} for i in range(n)]


def _springs(rng, n):
    kinds = []
    for i in range(n):
        m = float(rng.uniform(0.6, 2.0))
        kinds.append({'name': f'spring{i}', 'app': rng.normal(size=APP_DIM), 'm': m,
                      'k': float(rng.uniform(3.0, 9.0)) * m})
    return kinds


def _swings(rng, n):
    return [{'name': f'swing{i}', 'app': rng.normal(size=APP_DIM), 'm': float(rng.uniform(1.5, 3.0)),
             'gl': float(rng.uniform(6.0, 12.0))} for i in range(n)]


def params(kind, scene):
    """The hidden physics of one object in one place."""
    p = {'m': kind['m'], 'b': 0.0, 'c': 0.0, 'k': 0.0, 'gl': 0.0, 'swing': False}
    if scene == 'carpet':
        p['b'] = kind['b']
    elif scene == 'water':
        p['b'], p['c'] = 0.05, kind['c']
    elif scene == 'spring':
        p['k'] = kind['k']
    elif scene == 'swing':
        p['swing'], p['gl'] = True, kind['gl']
    return p


def describe(kind, rng, chance):
    """What a caretaker might say about a toy. Words never state a law."""
    if 'b' not in kind or rng.random() >= chance:
        return []
    words = []
    if kind['m'] >= 1.9:
        words.append('heavy')
    elif kind['m'] <= 1.1:
        words.append('light')
    words.append('rough' if kind['b'] >= 0.9 else 'smooth')
    words.append('flat' if kind['c'] >= 3.0 else 'round')
    return words


def life_plan(seed):
    """One ordered childhood. Every learner with this seed lives the same one."""
    rng = np.random.default_rng(seed)
    hand = {'name': 'hand', 'app': np.full(APP_DIM, 3.0), 'm': 1.0}
    toys, springs, swings = _toys(rng, 6, 'toy'), _springs(rng, 4), _swings(rng, 4)
    new_toys = _toys(rng, 6, 'new')
    plan = []

    def add(stage, scene, kinds, n, *, speak=0.7, tricks=0.05, shuffle=True):
        order = [kinds[i % len(kinds)] for i in range(n)]
        if shuffle:
            rng.shuffle(order)
        for kind in order:
            p = params(kind, scene)
            if tricks and rng.random() < tricks:
                # Someone else secretly bumps the object: a contradiction the
                # learner must not turn into knowledge.
                start = float(rng.choice([0.6, 0.8, 1.0, 1.2]))
                p['trick'] = (start, start + 0.2, float(rng.choice([-1.5, 1.5])))
            plan.append({'stage': stage, 'scene': scene, 'kind': kind['name'],
                         'app': kind['app'] + rng.normal(0, 0.05, APP_DIM), 'params': p,
                         'words': describe(kind, rng, speak),
                         'check_u': float(rng.choice(CHECK_COMMANDS)),
                         'trick': 'trick' in p})

    add(STAGES[0], 'body', [hand], 12, speak=0, tricks=0)
    add(STAGES[1], 'ice', toys, 36)
    add(STAGES[2], 'carpet', toys, 42)
    add(STAGES[3], 'water', toys, 42)
    add(STAGES[4], 'spring', springs, 24, speak=0)
    add(STAGES[5], 'swing', swings, 24, speak=0)
    tests = [(kind, scene) for kind in new_toys for scene in ('ice', 'carpet', 'water')]
    rng.shuffle(tests)
    for kind, scene in tests:
        add(STAGES[6], scene, [kind], 1, speak=1.0, tricks=0, shuffle=False)
    # Old toys glued together, on ice: pairs first, then triples it has never
    # seen. The learner can recognise each part, but nobody tells it how the
    # parts' numbers make the whole's numbers.
    for n in (2,) * 8 + (3,) * 8:
        chosen = [toys[i] for i in rng.choice(len(toys), n, replace=False)]
        glued = {'m': sum(t['m'] for t in chosen)}
        plan.append({'stage': STAGES[7], 'scene': 'ice', 'kind': '+'.join(t['name'] for t in chosen),
                     'app': np.mean([t['app'] for t in chosen], 0) + rng.normal(0, 0.05, APP_DIM),
                     'parts': [t['app'] + rng.normal(0, 0.05, APP_DIM) for t in chosen],
                     'params': params(glued, 'ice'), 'words': [],
                     'check_u': float(rng.choice(CHECK_COMMANDS)), 'trick': False})
    finals = [(kind, scene) for kind in toys for scene in ('ice', 'carpet', 'water')]
    rng.shuffle(finals)
    for kind, scene in finals:
        add(STAGES[8], scene, [kind], 1, speak=0.7, tricks=0, shuffle=False)
    return plan
