"""Read-only checkpoint lineage, split integrity and usable-task audit.

This runs after final selection. It changes no predictor or selection and does
not use evaluation outcomes to choose an architecture or seed.
"""

import hashlib
import json
import os
from pathlib import Path

import torch

from .model import Dynamics, parameters, weight_hash
from .observatory import context_episodes, independent_outcome, observations
from .records import sha256, write_json
from .tasks import Situation, imagine, infer_mass, plan
from .training import CONFIG, ROOT, load_model, supervised


def row_identities(data):
    values = torch.cat([data[k].reshape(-1, data[k].shape[-1])
                        for k in ("v", "f", "m")], -1).contiguous().numpy()
    return {hashlib.sha256(row.tobytes()).hexdigest() for row in values}


def main():
    supervised()
    output = Path(os.environ["SERA_FIELD_ATTEMPT"])
    directory = ROOT / "runs/FIELD-001"
    selected = json.loads((directory / "selection.json").read_text())
    before = sha256(directory / "selection.json")
    lineage = {}
    for name, result in selected["results"].items():
        initial, saved = load_model(directory / name / "step-00000.pt")
        final, _ = load_model(ROOT / result["selected"]["path"])
        assert saved["step"] == 0
        assert saved["weight_sha256"] == result["metadata"]["initial_weight_sha256"]
        assert sha256(ROOT / result["selected"]["path"]) == result["selected"]["sha256"]
        assert weight_hash(initial) != weight_hash(final)
        row = {"initial_sha256": sha256(directory / name / "step-00000.pt"),
               "initial_weight_sha256": weight_hash(initial),
               "selected_weight_sha256": weight_hash(final),
               "updates": result["updates"], "selected_step": result["selected"]["step"],
               "parameters": parameters(final)}
        if name.split("-")[0] in {"field", "scrambled", "dense", "invariant"}:
            torch.manual_seed(result["metadata"]["seed"])
            regenerated = Dynamics(initial.kind, initial.width)
            assert weight_hash(regenerated) == weight_hash(initial)
            row["random_initialization_reconstructed_exactly"] = True
        if name.startswith("field-"):
            row["connection_weight_change_l2"] = float(
                (final.net.links_in - initial.net.links_in).detach().norm())
            assert row["connection_weight_change_l2"] > 0
        if name.startswith(("fixed-", "expanded-")):
            base_record = selected["results"]["field-" + name.split("-")[1]]["selected"]
            assert weight_hash(final.base) == base_record["weight_sha256"]
            row["base_weight_identity_preserved"] = True
        lineage[name] = row

    splits = {
        "base_train": observations(8192, CONFIG["base_train_seed"]),
        "base_dev": observations(1024, CONFIG["base_dev_seed"]),
        "rotation_dev": observations(1024, CONFIG["base_dev_seed"] + 1, rotated=True),
        "base_final": observations(2048, CONFIG["base_final_seed"]),
        "rotation_final": observations(2048, CONFIG["base_final_seed"] + 1, rotated=True, haar=True),
        "mass_final": observations(1024, CONFIG["base_final_seed"] + 2, rotated=True,
                                   extension=True, haar=True),
        "refine_train": context_episodes(8192, CONFIG["refine_train_seed"]),
        "refine_dev": context_episodes(512, CONFIG["refine_dev_seed"]),
        "refine_final": context_episodes(1024, CONFIG["refine_final_seed"], haar=True),
        "energy_calibration": observations(2048 * 6, 79092026, rotated=True, haar=True),
        "compatibility_calibration": observations(4096 * 6, 79092027, rotated=True, haar=True),
        "compatibility_dev": context_episodes(1024, 89092026, haar=True),
    }
    hashes = {name: row_identities(data) for name, data in splits.items()}
    split_rows = {name: {"identity": data["identity"], "unique_input_rows": len(hashes[name]),
                         "rows": data["v"].numel() // 3} for name, data in splits.items()}
    overlaps = {}
    names = list(splits)
    for i, name in enumerate(names):
        assert split_rows[name]["rows"] == split_rows[name]["unique_input_rows"]
        for other in names[i + 1:]:
            count = len(hashes[name] & hashes[other])
            overlaps[name + " | " + other] = count
            assert count == 0

    record = selected["results"]["field-11"]["selected"]
    model, _ = load_model(ROOT / record["path"])
    situation = Situation((0., 0., 0.), (0., 0., 0.), (2., 0., 0.), 2.,
                          goal="Compare motion when the same force acts on two masses")
    fact_hash = situation.identity()
    weight_before = weight_hash(model)
    normal = imagine(model, situation)
    alternative = imagine(model, situation.branch(mass=1.))
    inverse = infer_mass(model, torch.zeros(1, 3), torch.tensor([[2., 0., 0.]]),
                         torch.tensor([[1., 0., 0.]]))
    proposed = plan(model, torch.zeros(1, 3), torch.zeros(1, 3), torch.tensor([[2.]]),
                    torch.tensor([[.2, 0., 0.]]))
    verified = independent_outcome([0., 0., 0.], [0., 0., 0.],
                                   proposed["controls"][0].numpy(), 2.)
    assert fact_hash == situation.identity() and weight_before == weight_hash(model)
    demo = {"checkpoint": record, "mass_2_after_1_second": {
                "position": normal["position"][-1], "velocity": normal["velocity"][-1]},
            "mass_1_after_1_second": {"position": alternative["position"][-1],
                                      "velocity": alternative["velocity"][-1]},
            "inferred_mass_given_force_2_acceleration_1": inverse["mass"].tolist(),
            "plan_target": [.2, 0., 0.],
            "plan_first_force": proposed["controls"][0, 0].tolist(),
            "plan_second_force": proposed["controls"][0, -1].tolist(),
            "plan_predicted_position": proposed["position"][0].tolist(),
            "plan_independent_endpoint": verified["states"][-1].tolist(),
            "facts_and_weights_unchanged": True,
            "evidence_type": "new supplied synthetic diagnostic examples; not an additional final cohort"}
    owners = {}
    for seed in (11, 29, 47):
        owner_record = selected["refinement_selection"][str(seed)]["qualified_owner"]["checkpoint"]
        owner, _ = load_model(ROOT / owner_record["path"])
        base_hash = selected["results"][f"field-{seed}"]["selected"]["weight_sha256"]
        assert weight_hash(owner.base) == base_hash
        owners[str(seed)] = {"checkpoint": owner_record, "parameters": parameters(owner),
                             "base_preserved": True}
    assert sha256(directory / "selection.json") == before
    report = {"schema": "sera-field.delivery-audit.1", "status": "PASS",
              "selection_sha256": before, "lineage": lineage, "splits": split_rows,
              "pairwise_duplicate_input_rows": overlaps, "owners": owners,
              "total_gradient_updates": sum(v["updates"] for v in lineage.values()),
              "random_base_initializations_reconstructed": 12,
              "all_selected_weight_identities_changed_from_initialization": True,
              "demo": demo}
    write_json(output / "audit.json", report)
    print(json.dumps({"status": "PASS", "updates": report["total_gradient_updates"],
                      "exact_initializations": 12, "overlapping_input_rows": sum(overlaps.values()),
                      "demo": demo}, indent=2), flush=True)


if __name__ == "__main__":
    main()
