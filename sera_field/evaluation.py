"""One-opening final evaluation and fixed-checkpoint independent replay."""

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from .investigation import CreditBook, Evidence, choose_probe, evidence_identity
from .model import parameters, weight_hash
from .observatory import context_episodes, independent_outcome, observations
from .records import sha256, utc, write_json
from .tasks import infer_mass, plan, rollout
from .training import CONFIG, ROOT, load_model, predict, scores, supervised


class PowerLawControl(torch.nn.Module):
    """A deliberately strong two-parameter classical structure fitted on the same observations."""
    def __init__(self, data):
        super().__init__()
        force, target = data["f"].double(), data["a"].double()
        gain = ((force * target).sum(-1) / force.square().sum(-1)).clamp_min(1e-12)
        design = torch.cat((torch.ones_like(data["m"].double()), data["m"].double().log()), -1)
        coefficients = torch.linalg.lstsq(design, gain.log()).solution.float()
        self.register_buffer("coefficients", coefficients)

    def forward(self, v, f, m):
        return (self.coefficients[0] + self.coefficients[1] * m.log()).exp() * f


def error_summary(value):
    flat = value.detach().cpu().numpy().reshape(-1)
    return {"mean": float(flat.mean()), "median": float(np.median(flat)),
            "p95": float(np.percentile(flat, 95)), "max": float(flat.max()), "count": len(flat)}


def cross_use(model, data):
    v, f, m, a, x = (data[k][:128] for k in ("v", "f", "m", "a", "x"))
    horizon, dt = 20, .05
    forces = f[:, None, :].expand(-1, horizon, -1)
    before = weight_hash(model)
    with torch.no_grad():
        xp, vp = rollout(model, x, v, forces, m, dt)
        time_axis = torch.arange(horizon + 1)[None, :, None] * dt
        # Closed-form independent reference for the supplied vacuum simulator.
        xt = x[:, None] + v[:, None] * time_axis + .5 * (f / m)[:, None] * time_axis.square()
        vt = v[:, None] + (f / m)[:, None] * time_axis
        inverse = infer_mass(model, v, f, a)
        xc, vc = rollout(model, x, v, forces, m / 2, dt)
        xct = x[:, None] + v[:, None] * time_axis + (f / m)[:, None] * time_axis.square()
        vct = v[:, None] + (2 * f / m)[:, None] * time_axis
    assert before == weight_hash(model)
    return {"forward_position_endpoint": error_summary((xp[:, -1] - xt[:, -1]).norm(dim=-1)),
            "forward_velocity_endpoint": error_summary((vp[:, -1] - vt[:, -1]).norm(dim=-1)),
            "inverse_mass_relative_error": error_summary((inverse["mass"] - m[:, 0]).abs() / m[:, 0]),
            "inverse_boundary_hits": int(inverse["boundary_hit"].sum()),
            "mass_halving_position_endpoint": error_summary((xc[:, -1] - xct[:, -1]).norm(dim=-1)),
            "mass_halving_velocity_endpoint": error_summary((vc[:, -1] - vct[:, -1]).norm(dim=-1)),
            "mass_halving_outside_taught_range": int((m[:, 0] / 2 < .8).sum()),
            "predictor_unchanged": True, "task_specific_training_updates": 0}


def planning_evaluation(model, seed):
    g = torch.Generator().manual_seed(seed)
    count = 24
    x = torch.randn(count, 3, generator=g) * .15
    v = torch.randn(count, 3, generator=g) * .15
    m = torch.rand(count, 1, generator=g) * 1.2 + 1.
    target = torch.randn(count, 3, generator=g) * .15
    proposed = plan(model, x, v, m, target)
    observed = []
    for i in range(count):
        outcome = independent_outcome(x[i].numpy(), v[i].numpy(), proposed["controls"][i].numpy(), float(m[i, 0]))
        observed.append(outcome["states"][-1])
    observed = torch.tensor(np.asarray(observed), dtype=torch.float32)
    position_error = (observed[:, :3] - target).norm(dim=-1)
    velocity_error = observed[:, 3:].norm(dim=-1)
    return {"position_error": error_summary(position_error), "velocity_error": error_summary(velocity_error),
            "success_at_5cm_and_5cm_per_s": int(((position_error < .05) & (velocity_error < .05)).sum()),
            "count": count, "force_limit": 8., "iterations": 120,
            "independent_solver": "DOP853", "controls_optimized_not_predictor_weights": True,
            "cases": [{"initial_position": x[i].tolist(), "initial_velocity": v[i].tolist(),
                        "mass": float(m[i, 0]), "target": target[i].tolist(),
                        "forces": proposed["controls"][i].tolist(),
                        "actual_endpoint": observed[i].tolist()} for i in range(count)]}


def investigation_cycle(base, successor, seed):
    """A fresh finite quest: a fitted model faces an independent new intervention."""
    support = observations(6, seed, rotated=True, resistance=.4)
    context = successor.context(*(support[k][None] for k in ("v", "f", "m", "a")))
    v, m = torch.tensor([[1.1, -.7, .5]]), torch.tensor([[1.7]])
    controls = torch.cat((torch.eye(3), -torch.eye(3), 3 * torch.eye(3), -3 * torch.eye(3)))
    probe = choose_probe([base, successor], v, m, controls, [None, context])
    f = torch.tensor(probe["force"])[None]
    requested = f.expand(2, 3).numpy()
    measured = independent_outcome(np.zeros(3), v[0].numpy(), requested, float(m[0, 0]), dt=.01, resistance=.4)
    with torch.no_grad():
        _, before_v = rollout(base, torch.zeros_like(v), v, f[:, None].expand(1, 2, 3), m, dt=.01)
        _, after_v = rollout(successor, torch.zeros_like(v), v, f[:, None].expand(1, 2, 3), m, dt=.01, context=context)
    actual = torch.tensor(measured["states"][-1, 3:], dtype=torch.float32)
    before_error = float((before_v[0, -1] - actual).square().mean())
    after_error = float((after_v[0, -1] - actual).square().mean())
    goal = "Predict this object's response and explain the missing influence using observed consequences"
    identity = evidence_identity({"seed": seed, "probe": probe, "source": measured["source"]})
    evidence = Evidence(identity, goal, "chosen-probe", weight_hash(base), weight_hash(successor),
                        measured["source"], True, before_error, after_error, tuple(probe["force"]),
                        tuple(measured["actual_controls"][0]))
    book = CreditBook()
    credit = book.award(evidence, current_predictor=weight_hash(successor), original_goal=goal)
    repeated = book.award(evidence, current_predictor=weight_hash(successor), original_goal=goal)
    # Check actuation explicitly; this control tests a performed but weakened intervention.
    faulty = independent_outcome(np.zeros(3), v[0].numpy(), requested, float(m[0, 0]), dt=.01,
                                  resistance=.4, actuator_gain=.75)
    actuation_error = float(np.max(np.abs(faulty["actual_controls"] - faulty["requested_controls"])))
    return {"goal": goal, "support_identity": support["identity"], "probe": probe,
            "before_error": before_error, "after_error": after_error,
            "evidence": evidence.__dict__, "credit": credit, "duplicate_credit": repeated,
            "actuation_fault_detected": actuation_error > 1e-9,
            "returned_answer": {"velocity": after_v[0, -1].tolist(),
                                "independent_velocity": actual.tolist(),
                                "qualification": "independent simulated intervention in this observed context",
                                "explanation": "The successor uses measured support residuals to condition the same learned physical field. Its new prediction was checked against a separately integrated intervention."}}


def evaluate(output, *, replay=False):
    selection_path = output / "selection.json"
    selection = json.loads(selection_path.read_text())
    selection_hash = sha256(selection_path)
    marker = output / "FINALS_OPENED.json"
    if marker.exists():
        opened = json.loads(marker.read_text())
        if not replay or opened["selection_sha256"] != selection_hash:
            raise RuntimeError("Finals already opened; only exact fixed-checkpoint replay is allowed")
    elif replay:
        raise RuntimeError("Nothing to replay")
    else:
        write_json(marker, {"opened_utc": utc(), "selection_sha256": selection_hash,
                            "policy": "fixed checkpoint evaluation; no subsequent selection on these finals"})
    seed = CONFIG["base_final_seed"]
    finals = {"interpolation": observations(2048, seed),
              "rotation": observations(2048, seed + 1, rotated=True, haar=True),
              "mass_extension": observations(1024, seed + 2, rotated=True, extension=True, haar=True)}
    refinements = context_episodes(1024, CONFIG["refine_final_seed"], haar=True)
    report = {"schema": "sera-field.evaluation.1", "selection_sha256": selection_hash,
              "final_identities": {k: d["identity"] for k, d in finals.items()},
              "refinement_final_identity": refinements["identity"], "base": {}, "refinement": {}}
    for seed in CONFIG["seeds"]:
        for kind in ("field", "scrambled", "dense", "invariant"):
            name = f"{kind}-{seed}"
            record = selection["results"][name]["selected"]
            if sha256(ROOT / record["path"]) != record["sha256"]:
                raise RuntimeError("Selected checkpoint bytes changed")
            model, _ = load_model(ROOT / record["path"])
            report["base"][name] = {"checkpoint": record, "parameters": parameters(model),
                                    "finals": {k: scores(model, d) for k, d in finals.items()},
                                    "cross_use": cross_use(model, finals["rotation"]),
                                    "planning": planning_evaluation(model, 770012)}
            print(json.dumps({"evaluated": name, "finals": report["base"][name]["finals"],
                              "plans_passed": report["base"][name]["planning"]["success_at_5cm_and_5cm_per_s"]}), flush=True)
            if not replay:
                write_json(output / "final-progress.json", report)
        base, _ = load_model(ROOT / selection["results"][f"field-{seed}"]["selected"]["path"])
        for kind in ("fixed", "expanded"):
            name = f"{kind}-{seed}"
            record = selection["results"][name]["selected"]
            model, _ = load_model(ROOT / record["path"])
            pred, target = predict(model, refinements)
            with torch.no_grad():
                baseline = base(refinements["v"][:, -1], refinements["f"][:, -1], refinements["m"][:, -1])
            vacuum = refinements["resistance_for_audit_only"][:, 0] == 0
            rows = {}
            for label, mask in (("vacuum_context", vacuum), ("new_context", ~vacuum)):
                mse = float((pred[mask] - target[mask]).square().mean().detach())
                baseline_mse = float((baseline[mask] - target[mask]).square().mean())
                rows[label] = {"mse": mse, "base_mse": baseline_mse, "count": int(mask.sum()),
                               "reduction_percent": 100 * (1 - mse / max(baseline_mse, 1e-12))}
            report["refinement"][name] = {"checkpoint": record, "parameters": parameters(model),
                                          "finals": rows, "base_hash_preserved": weight_hash(model.base) == weight_hash(base),
                                          "retained_without_new_context": scores(model.base, finals["rotation"])}
        chosen = selection["refinement_selection"][str(seed)]
        qualified = chosen["qualified_owner"]
        model, _ = load_model(ROOT / qualified["checkpoint"]["path"])
        with torch.no_grad():
            predicted, target = predict(model, refinements)
            rows = {}
            for label, mask in (("vacuum_context", vacuum), ("new_context", ~vacuum)):
                rows[label] = {"mse": float((predicted[mask] - target[mask]).square().mean()), "count": int(mask.sum())}
        report["refinement"][f"selected-{seed}"] = {"selection": chosen,
                                                      "qualified_context_finals": rows,
                                                      "investigation": investigation_cycle(base, model, 880021 + seed)}
    control = PowerLawControl(observations(8192, CONFIG["base_train_seed"]))
    report["strong_classical_power_control"] = {"learned_coefficients": control.coefficients.tolist(),
        "parameters_fitted": 2, "supplied_structure": "isotropic scalar power law, least-squares log fit",
        "finals": {k: scores(control, d) for k, d in finals.items()},
        "cross_use": cross_use(control, finals["rotation"]), "planning": planning_evaluation(control, 770012)}
    if replay:
        previous = json.loads((output / "final.json").read_text())
        # Compare the serialized contract: Evidence has tuples in memory, while
        # JSON stores those sequences as lists. Numerical values remain exact.
        equal = previous == json.loads(json.dumps(report, allow_nan=False))
        destination = Path(__import__("os").environ["SERA_FIELD_ATTEMPT"]) / "replay.json"
        write_json(destination, {"exact_equal": equal, "selection_sha256": selection_hash,
                                  "replayed_final_sha256": sha256(output / "final.json")})
        if not equal:
            write_json(destination.with_name("replayed-report.json"), report)
            raise RuntimeError("Replay differs; inspect before publication")
    else:
        write_json(output / "final.json", report)
    print("Independent evaluation complete" + ("; exact replay matched" if replay else ""), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "runs/FIELD-001")
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    supervised()
    evaluate(args.output.resolve(), replay=args.replay)


if __name__ == "__main__":
    main()
