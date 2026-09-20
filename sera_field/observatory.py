"""Supplied diagnostic world and independent measurements; never imported by model.py.

Synthetic experiments are clearly distinguished from human-authored training sources.
"""

import hashlib

import numpy as np
import torch
from scipy.integrate import solve_ivp


def physical_acceleration(v, f, mass, resistance=0.):
    speed = np.sqrt(np.sum(v * v, axis=-1, keepdims=True) + 1e-30)
    return (f - np.asarray(resistance) * speed * v) / mass


def microstep(x, v, f, m, dt, resistance):
    # Independent observation generator in float64; four substeps per sensor interval.
    h = dt / 4
    for _ in range(4):
        k1 = physical_acceleration(v, f, m, resistance)
        k2 = physical_acceleration(v + h * k1 / 2, f, m, resistance)
        k3 = physical_acceleration(v + h * k2 / 2, f, m, resistance)
        k4 = physical_acceleration(v + h * k3, f, m, resistance)
        x = x + h * v + h * h * (k1 + k2 + k3) / 6
        v = v + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return x, v


def proper_rotations(rng, count, *, haar=False):
    q, r = np.linalg.qr(rng.normal(size=(count, 3, 3)))
    if haar:
        signs = np.sign(np.diagonal(r, axis1=-2, axis2=-1))
        signs[signs == 0] = 1
        q = q * signs[:, None, :]
    q[:, :, 0] *= np.linalg.det(q)[:, None]
    return q


def observations(count, seed, *, rotated=False, extension=False, resistance=0., haar=False):
    rng = np.random.default_rng(seed)
    mass = rng.uniform(4.2, 6.0, (count, 1)) if extension else rng.uniform(.8, 4., (count, 1))
    velocity = rng.normal(0, 1.25, (count, 3))
    force = rng.normal(0, 2., (count, 3))
    velocity[:, 2] *= .08
    force[:, 2] *= .08
    if rotated:
        q = proper_rotations(rng, count, haar=haar)
        velocity = np.einsum("nij,nj->ni", q, velocity)
        force = np.einsum("nij,nj->ni", q, force)
    position = rng.normal(size=(count, 3))
    dt = .002
    previous, _ = microstep(position.copy(), velocity.copy(), force, mass, -dt, resistance)
    following, _ = microstep(position.copy(), velocity.copy(), force, mass, dt, resistance)
    measured_v = (following - previous) / (2 * dt)
    measured_a = (following - 2 * position + previous) / dt ** 2
    values = {"v": measured_v, "f": force, "m": mass, "a": measured_a, "x": position}
    result = {key: torch.tensor(value, dtype=torch.float32) for key, value in values.items()}
    digest = hashlib.sha256()
    for key, value in sorted(values.items()):
        digest.update(key.encode())
        digest.update(value.tobytes())
    result["identity"] = digest.hexdigest()
    result["seed"] = seed
    return result


def context_episodes(count, seed, supports=6, *, haar=False):
    rng = np.random.default_rng(seed)
    resistance = rng.uniform(.1, .65, (count, 1))
    resistance[rng.random(count) < .35] = 0.
    flat_resistance = np.repeat(resistance, supports + 1, axis=0)
    flat = observations(count * (supports + 1), seed + 1, rotated=True,
                        resistance=flat_resistance, haar=haar)
    result = {key: value.reshape(count, supports + 1, -1) for key, value in flat.items()
              if isinstance(value, torch.Tensor)}
    result["identity"] = flat["identity"]
    result["seed"] = seed
    # These oracle values are evaluation-only; train.py explicitly whitelists measured fields.
    result["resistance_for_audit_only"] = torch.tensor(resistance, dtype=torch.float32)
    return result


def independent_outcome(position, velocity, force_schedule, mass, dt=.05, resistance=0., actuator_gain=1.):
    """DOP853 solver, independently implemented from the learned-model RK4 rollout."""
    state = np.r_[position, velocity].astype(np.float64)
    history = [state.copy()]
    actual_controls = np.asarray(force_schedule, dtype=np.float64) * actuator_gain
    for control in actual_controls:
        def rhs(_, s):
            a = (control - resistance * np.linalg.norm(s[3:]) * s[3:]) / float(mass)
            return np.r_[s[3:], a]
        result = solve_ivp(rhs, (0, dt), state, method="DOP853", rtol=1e-10, atol=1e-11)
        if not result.success:
            raise RuntimeError(result.message)
        state = result.y[:, -1]
        history.append(state.copy())
    return {"states": np.asarray(history), "actual_controls": actual_controls,
            "requested_controls": np.asarray(force_schedule), "actuator_gain": actuator_gain,
            "source": "synthetic independent DOP853 physical oracle"}
