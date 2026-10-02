"""ccops5 lab | the ball-throw world: throws in a vacuum room, air, a windy yard, a water tank,
and the moon, with balls that have a hidden mass.

This file is the world only. The robot's mind is in ballmind.py and never reads a ball's mass:
it sees positions every 0.05 s (with small noise), a ball's visible size, its look, and the
speed a known push gives it on a rail.

Physics (hidden from the robot):
  vacuum   pulled down by g
  air      g, plus drag 0.05·size²·|v|·v / mass
  windy    the same drag, but relative to air moving sideways at a hidden speed
  water    g, minus buoyancy 9.8·size³/mass, plus drag 0.3·size²·|v|·v / mass
  moon     pulled down by 1.62, nothing else (only in the exam)

The drag numbers are smaller than in the earlier drafts, so a throw changes slowly enough to
be measured every 0.05 s. Sizes span 0.3 to 1.2 and are measured to 0.2%, so that size squared
and size cubed can be told apart, and the true size does not act as a second hidden number
(see README, changes).

Built as an isolated experiment. Not part of sera-field.
(The simulator is from an earlier draft; the rest was rewritten during development.)
"""
import math

import numpy as np

PLACES = ('vacuum', 'air', 'windy', 'water', 'moon')
TRAINING = ('vacuum', 'air', 'windy', 'water')
DT_SIM = 0.005
DT_OBS = 0.05
T_END = 2.0
N_OBS = int(round(T_END / DT_OBS)) + 1
SIGMA_POS = 0.001                                   # position noise (metres)
GRAVITY = 9.8
MOON_GRAVITY = 1.62
AIR_DRAG = 0.05
WATER_DRAG = 0.3
WATER_BUOYANCY = 9.8
PUSH = 10.0                                         # the known push on the rail
PUSH_NOISE = 0.02                                   # noise of the measured rail speed
SIZE_NOISE = 0.002                                  # relative noise of the measured size (a caliper)
N_BALLS = 8
TAGS = {'teacher': 1, 'own': 2, 'check': 3, 'moon': 4, 'throwback': 5, 'extra': 6}


def get_accel(place, ball, vx, vy, wind_vx):
    """The true acceleration of a ball."""
    if place == 'vacuum':
        return 0.0, -GRAVITY
    if place == 'moon':
        return 0.0, -MOON_GRAVITY
    ay = -GRAVITY
    drag_c = WATER_DRAG if place == 'water' else AIR_DRAG
    if place == 'water':
        ay += WATER_BUOYANCY * ball['size'] ** 3 / ball['mass']
    rx, ry = vx - (wind_vx if place == 'windy' else 0.0), vy
    k = drag_c * ball['size'] ** 2 * math.hypot(rx, ry) / ball['mass']
    return -k * rx, ay - k * ry


def simulate(place, ball, speed, angle, wind_vx, rng):
    """One throw: positions every DT_OBS, with noise. RK4 at DT_SIM."""
    x = y = 0.0
    vx, vy = speed * math.cos(angle), speed * math.sin(angle)
    xs, ys = [x], [y]
    h, per = DT_SIM, int(round(DT_OBS / DT_SIM))
    for _ in range(N_OBS - 1):
        for _ in range(per):
            k1x, k1y = vx, vy
            k1vx, k1vy = get_accel(place, ball, vx, vy, wind_vx)
            k2x, k2y = vx + .5 * h * k1vx, vy + .5 * h * k1vy
            k2vx, k2vy = get_accel(place, ball, k2x, k2y, wind_vx)
            k3x, k3y = vx + .5 * h * k2vx, vy + .5 * h * k2vy
            k3vx, k3vy = get_accel(place, ball, k3x, k3y, wind_vx)
            k4x, k4y = vx + h * k3vx, vy + h * k3vy
            k4vx, k4vy = get_accel(place, ball, k4x, k4y, wind_vx)
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            y += h / 6 * (k1y + 2 * k2y + 2 * k3y + k4y)
            vx += h / 6 * (k1vx + 2 * k2vx + 2 * k3vx + k4vx)
            vy += h / 6 * (k1vy + 2 * k2vy + 2 * k3vy + k4vy)
        xs.append(x)
        ys.append(y)
    return (np.array(xs) + rng.normal(0, SIGMA_POS, N_OBS),
            np.array(ys) + rng.normal(0, SIGMA_POS, N_OBS))


def throw_rng(seed, place, ball_id, tag, k):
    """The world's noise for one throw, the same for every robot that makes this throw."""
    return np.random.default_rng([seed, PLACES.index(place), ball_id, TAGS[tag], k])


def make_life(seed):
    """The balls, the hidden wind, and which (ball, place) pairs are never shown."""
    rng = np.random.default_rng([seed, 2026])
    balls = []
    for i in range(N_BALLS):
        mass, size = float(rng.uniform(0.5, 3.0)), float(rng.uniform(0.3, 1.2))
        balls.append({'id': i, 'mass': mass, 'size': size,
                      'seen_size': size * (1 + float(rng.normal(0, SIZE_NOISE))),
                      'look': [size + float(rng.normal(0, 0.3))] + [float(v) for v in rng.normal(0, 1, 3)],
                      'rail_speed': PUSH / mass + float(rng.normal(0, PUSH_NOISE))})
    heavy = float(np.median([b['mass'] for b in balls]))
    for b in balls:
        b['word'] = 'heavy' if b['mass'] > heavy else 'light'
    offset = int(rng.integers(4))
    held_out = {b['id']: TRAINING[(b['id'] + offset) % 4] for b in balls}
    return {'seed': seed, 'balls': balls, 'wind': float(rng.uniform(-4.0, 4.0)),
            'held_out': held_out, 'named': sorted(int(i) for i in rng.permutation(N_BALLS)[:N_BALLS // 2])}


def wind_of(life, place):
    return life['wind'] if place == 'windy' else 0.0
