"""Task views over the exact same learned weights, without task-specific fitting."""

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math

import torch

from .model import weight_hash


@dataclass(frozen=True)
class Situation:
    position: tuple[float, float, float]
    velocity: tuple[float, float, float]
    force: tuple[float, float, float]
    mass: float
    goal: str = "understand this situation"
    status: str = "observed"
    source: str = "user measured input"

    def __post_init__(self):
        if self.mass <= 0 or not all(math.isfinite(float(a)) for a in
                                    (*self.position, *self.velocity, *self.force, self.mass)):
            raise ValueError("Finite vectors and strictly positive mass are required")
        if any(len(v) != 3 for v in (self.position, self.velocity, self.force)):
            raise ValueError("Three-dimensional vectors are required")
        if self.status not in {"observed", "hypothetical"}:
            raise ValueError("Unknown evidence status")

    def branch(self, **changes):
        if "goal" in changes and changes["goal"] != self.goal:
            raise ValueError("An imagined branch preserves the original goal")
        return replace(self, **changes, status="hypothetical")

    def identity(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()


def step(model, x, v, f, m, dt, context=None):
    def acceleration(at_v):
        return model(at_v, f, m) if context is None else model(at_v, f, m, context)
    k1 = acceleration(v)
    k2 = acceleration(v + .5 * dt * k1)
    k3 = acceleration(v + .5 * dt * k2)
    k4 = acceleration(v + dt * k3)
    return (x + dt * v + dt * dt * (k1 + k2 + k3) / 6,
            v + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6)


def rollout(model, x, v, forces, mass, dt=.05, context=None):
    positions, velocities = [x], [v]
    for t in range(forces.shape[-2]):
        x, v = step(model, x, v, forces[..., t, :], mass, dt, context)
        positions.append(x)
        velocities.append(v)
    return torch.stack(positions, -2), torch.stack(velocities, -2)


def imagine(model, situation, *, steps=20, dt=.05, context=None):
    if not 1 <= steps <= 1000 or not 0 < dt <= .25:
        raise ValueError("Use a positive bounded imagination horizon")
    before = weight_hash(model)
    with torch.no_grad():
        x = torch.tensor(situation.position, dtype=torch.float32)[None]
        v = torch.tensor(situation.velocity, dtype=torch.float32)[None]
        f = torch.tensor(situation.force, dtype=torch.float32).expand(1, steps, 3)
        m = torch.tensor([[situation.mass]], dtype=torch.float32)
        positions, velocities = rollout(model, x, v, f, m, dt, context)
    if weight_hash(model) != before:
        raise RuntimeError("Imagination modified persistent weights")
    return {"status": "model-conditional", "goal": situation.goal,
            "situation_sha256": situation.identity(), "predictor_sha256": before,
            "position": positions[0].tolist(), "velocity": velocities[0].tolist(),
            "dt": dt, "assumptions": ["measured force is applied", "calibrated positive mass",
                                       "model applicability matches the observed context"]}


def infer_mass(model, velocity, force, acceleration, *, force_known=True, low=.25, high=8.):
    if not force_known:
        return {"status": "equivalence-class", "reason": "force and mass are jointly unidentified"}
    if float(force.square().sum()) < 1e-10:
        return {"status": "uninformative", "reason": "this control does not identify mass"}
    with torch.no_grad():
        grid = torch.linspace(low, high, 512)
        batch, count = velocity.shape[0], len(grid)
        masses = grid[None, :, None].expand(batch, count, 1)
        prediction = model(velocity[:, None].expand(batch, count, 3),
                           force[:, None].expand(batch, count, 3), masses)
        error = (prediction - acceleration[:, None]).square().mean(-1)
        index = error.argmin(-1)
        return {"status": "conditional-estimate", "mass": grid[index],
                "residual": error.gather(1, index[:, None]).squeeze(1),
                "boundary_hit": (index == 0) | (index == count - 1)}


def plan(model, position, velocity, mass, target, *, iterations=120, steps=20, dt=.05,
         force_limit=8., context=None):
    """Optimize controls only. Model parameters are frozen and restored on exit."""
    before = weight_hash(model)
    original_flags = [p.requires_grad for p in model.parameters()]
    model.requires_grad_(False)
    raw = torch.zeros(len(position), 2, 3, requires_grad=True)
    optimizer = torch.optim.Adam([raw], lr=.08)
    try:
        for _ in range(iterations):
            controls = (force_limit * torch.tanh(raw)).repeat_interleave(steps // 2, dim=1)
            x, v = rollout(model, position, velocity, controls, mass, dt, context)
            loss = ((x[:, -1] - target).square().sum(-1) + v[:, -1].square().sum(-1)).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
        controls = (force_limit * torch.tanh(raw)).repeat_interleave(steps // 2, dim=1).detach()
        with torch.no_grad():
            x, v = rollout(model, position, velocity, controls, mass, dt, context)
    finally:
        for parameter, flag in zip(model.parameters(), original_flags):
            parameter.requires_grad_(flag)
    if weight_hash(model) != before:
        raise RuntimeError("Planning modified predictor weights")
    return {"controls": controls, "position": x[:, -1], "velocity": v[:, -1],
            "predictor_sha256": before, "iterations": iterations}
