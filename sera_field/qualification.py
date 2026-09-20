"""Diagnose old-context drift, calibrate compatibility and qualify on development only."""

import json
from pathlib import Path
import shutil

import torch

from .model import QualifiedOwner, weight_hash
from .observatory import context_episodes, observations
from .records import sha256, source_manifest, utc, write_json
from .training import CONFIG, ROOT, load_model, predict, supervised


def main():
    supervised()
    output = ROOT / "runs/FIELD-001"
    if (output / "FINALS_OPENED.json").exists():
        raise RuntimeError("Qualification is a development operation, never a final-based edit")
    selection_path = output / "selection.json"
    before_selection = output / "selection-before-qualification.json"
    if before_selection.exists():
        raise RuntimeError("Qualification already attempted; preserve the result")
    shutil.copyfile(selection_path, before_selection)
    freeze_path = ROOT / "reports/FIELD-001-QUALIFICATION-FREEZE.json"
    write_json(freeze_path, {"created_utc": utc(), "sources": source_manifest(ROOT),
                             "prior_selection_sha256": sha256(before_selection), "finals_opened": False})
    selection = json.loads(selection_path.read_text())
    calibration = observations(2048 * 6, 79092026, rotated=True, haar=True)
    dev = context_episodes(512, CONFIG["refine_dev_seed"])
    vacuum = dev["resistance_for_audit_only"][:, 0] == 0
    report = {"calibration_identity": calibration["identity"], "development_identity": dev["identity"],
              "quantile": .995, "query_outcomes_used_for_gating": False, "seeds": {}}
    for seed in CONFIG["seeds"]:
        chosen = selection["refinement_selection"][str(seed)]
        successor, saved = load_model(ROOT / chosen["selected"]["path"])
        with torch.no_grad():
            context = successor.context(*(calibration[k].reshape(2048, 6, -1) for k in ("v", "f", "m", "a")))
            threshold = float(torch.quantile(context[:, 2], .995))
            owner = QualifiedOwner(successor, threshold)
            raw, actual = predict(successor, dev)
            gated, _ = predict(owner, dev)
            prior = successor.base(dev["v"][:, -1], dev["f"][:, -1], dev["m"][:, -1])
            rows = {}
            for label, mask in (("vacuum", vacuum), ("novel", ~vacuum)):
                rows[label] = {name: float((value[mask] - actual[mask]).square().mean())
                               for name, value in (("base", prior), ("ungated", raw), ("gated", gated))}
            accepted = (rows["novel"]["gated"] < .5 * rows["novel"]["base"]
                        and rows["novel"]["gated"] <= 1.05 * rows["novel"]["ungated"]
                        and rows["vacuum"]["gated"] <= 1.25 * rows["vacuum"]["base"])
        record = {"threshold": threshold, "accepted": accepted, "development": rows,
                  "raw_checkpoint": chosen["selected"], "base_preserved": weight_hash(owner.base) == weight_hash(successor.base)}
        path = output / f"qualified-{seed}.pt"
        torch.save({"schema": "sera-field.qualified-owner.1", "specification": owner.specification(),
                    "model": owner.state_dict(), "weight_sha256": weight_hash(owner),
                    "step": saved["step"], "metadata": {"qualification": record, "origin": saved["metadata"],
                    "calibration_identity": calibration["identity"], "additional_gradient_updates": 0}}, path)
        record["checkpoint"] = {"path": str(path.relative_to(ROOT)), "sha256": sha256(path),
                                 "weight_sha256": weight_hash(owner), "step": saved["step"]}
        chosen["qualified_owner"] = record
        report["seeds"][str(seed)] = record
    write_json(output / "qualification.json", report)
    selection["qualification_freeze_sha256"] = sha256(freeze_path)
    write_json(selection_path, selection)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
