"""Independent observation generator and intervention receipts for CONNECTED-003.

This module never imports the learner. These are labeled simulations, not real
measurements. Supplied physics families and measurement channels are explicit.
"""
from dataclasses import dataclass
import hashlib
import json
import numpy as np


def stable_seed(*parts):
    return int.from_bytes(hashlib.sha256(json.dumps(parts).encode()).digest()[:8], 'little')


@dataclass(frozen=True)
class Environment:
    gain: float
    linear_drag: float
    quadratic_drag: float
    offset: float
    omitted: float = 0.

    def observe(self, velocity, force_per_mass):
        v, f = np.asarray(velocity), np.asarray(force_per_mass)
        # Implemented independently of the learned coefficient decoder/basis.
        acceleration = self.gain * f + self.offset
        acceleration = acceleration - self.linear_drag * v - self.quadratic_drag * np.abs(v) * v
        return acceleration + self.omitted * np.sin(2 * v)

    def intervene(self, requested, *, actuator_scale=1.):
        velocity, force = map(float, requested)
        performed = [velocity, force * actuator_scale]
        return {'requested': [velocity, force], 'performed': performed,
                'observation': [*performed, float(self.observe(*performed))],
                'actuation_matched': performed == [velocity, force],
                'origin': 'independent_simulation'}


def draw(seed, index, split, *, inquiry=False, omitted=False, with_targets=True):
    rng = np.random.default_rng(stable_seed('CONNECTED-003-world', seed, index, split))
    family = int(rng.integers(3))
    world = Environment(float(rng.uniform(.7, 1.3)), float(rng.uniform(0, .9)) if family != 1 else 0.,
                        float(rng.uniform(0, .45)) if family != 0 else 0., float(rng.uniform(-.6, .6)),
                        float(rng.uniform(.4, 1)) if omitted else 0.)
    n = int(rng.integers(1, 7)) if not inquiry else 2
    support = rng.uniform(-2, 2, (n, 2))
    if inquiry:
        support[:, 0] *= .12
        support[:, 1] *= .12
    observations = np.column_stack((support, world.observe(support[:, 0], support[:, 1])))
    # These queried outcomes are hidden from the learner until independent audit.
    queries = rng.uniform(-2, 2, (12, 2))
    if inquiry:
        center = rng.uniform(-1.5, 1.5, 2)
        queries = np.clip(center + rng.normal(0, .25, (12, 2)), -2, 2)
    targets = world.observe(queries[:, 0], queries[:, 1]).astype('float32') if with_targets else None
    return world, observations.astype('float32'), queries.astype('float32'), targets


def probes():
    return np.asarray([(v, f) for v in (-2., -1., 0., 1., 2.) for f in (-2., 0., 2.)], dtype='float32')


def analytic_probe(observations, options, goals):
    """Classical information control, with the same supplied basis and no truth."""
    def features(x):
        v, f = x[:, 0], x[:, 1]
        return np.column_stack((f, v, v * np.abs(v), np.ones(len(v))))
    old = features(observations)
    covariance = np.linalg.inv(np.eye(4) * .1 + old.T @ old)
    phi, goal = features(options), features(goals)
    reduction = np.sum((goal @ covariance @ phi.T) ** 2, axis=0) / (1 + np.sum(phi * (phi @ covariance), axis=1))
    return int(reduction.argmax())


def trajectory(world, *, velocity, force_per_mass, duration):
    """Independent DOP853 trajectory evidence; never used as learner prediction."""
    from scipy.integrate import solve_ivp
    result = solve_ivp(lambda t, y: [y[1], world.observe(y[1], force_per_mass)],
                       (0, duration), [0., velocity], method='DOP853', rtol=1e-10, atol=1e-12)
    if not result.success:
        raise ValueError(result.message)
    return result.y[:, -1].tolist()
