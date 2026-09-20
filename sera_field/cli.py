"""Use a saved learned field model for explicit physical tasks."""

import argparse
import json
import math
from pathlib import Path

import torch

from .model import weight_hash
from .tasks import Situation, imagine, infer_mass, plan
from .training import ROOT, load_model, supervised


def vector(value):
    components = tuple(float(v) for v in value.split(","))
    if len(components) != 3 or not all(math.isfinite(v) for v in components):
        raise argparse.ArgumentTypeError("Use three finite comma-separated numbers")
    return components


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=["imagine", "infer-mass", "plan"])
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--position", type=vector, default=(0., 0., 0.))
    parser.add_argument("--velocity", type=vector, default=(0., 0., 0.))
    parser.add_argument("--force", type=vector, default=(2., 0., 0.))
    parser.add_argument("--mass", type=float, default=2.)
    parser.add_argument("--counterfactual-mass", type=float)
    parser.add_argument("--acceleration", type=vector, default=(1., 0., 0.))
    parser.add_argument("--target", type=vector, default=(.2, 0., 0.))
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--dt", type=float, default=.05)
    args = parser.parse_args()
    if not 1 <= args.steps <= 1000 or not 0 < args.dt <= .25:
        parser.error("Use 1..1000 steps and a time step in (0, 0.25]")
    if args.task == "plan" and (args.steps < 2 or args.steps % 2):
        parser.error("The two-part control plan requires an even number of steps")
    supervised()
    if args.checkpoint is None:
        # Fixed seed named prospectively; no final-based choice of the best seed.
        selection = ROOT / "runs/FIELD-001/selection.json"
        if selection.exists():
            selected = json.loads(selection.read_text())
            args.checkpoint = ROOT / selected["results"]["field-11"]["selected"]["path"]
        else:
            args.checkpoint = ROOT / "checkpoints/FIELD-001/field-11.pt"
    model, metadata = load_model(args.checkpoint)
    situation = Situation(args.position, args.velocity, args.force, args.mass,
                          goal=f"user task: {args.task}")
    if args.task == "imagine":
        result = imagine(model, situation, steps=args.steps, dt=args.dt)
        if args.counterfactual_mass is not None:
            result["alternative"] = imagine(model, situation.branch(mass=args.counterfactual_mass),
                                              steps=args.steps, dt=args.dt)
    else:
        x, v, f, m = (torch.tensor([args.position]), torch.tensor([args.velocity]),
                      torch.tensor([args.force]), torch.tensor([[args.mass]]))
        if args.task == "infer-mass":
            result = infer_mass(model, v, f, torch.tensor([args.acceleration]))
        else:
            result = plan(model, x, v, m, torch.tensor([args.target]), steps=args.steps, dt=args.dt)
            result["status"] = "model-conditional control proposal"
        result = {k: value.tolist() if isinstance(value, torch.Tensor) else value for k, value in result.items()}
    result["learned_weight_sha256"] = weight_hash(model)
    result["learned_from_step"] = metadata["step"]
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
