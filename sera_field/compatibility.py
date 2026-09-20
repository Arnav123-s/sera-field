"""One prospective covariance-based compatibility study, using new development evidence."""

import json
import shutil

import torch

from .model import CalibratedOwner, weight_hash
from .observatory import context_episodes, observations
from .records import sha256, source_manifest, utc, write_json
from .training import CONFIG, ROOT, load_model, predict, supervised


def main():
    supervised()
    output = ROOT / "runs/FIELD-001"
    if (output / "FINALS_OPENED.json").exists():
        raise RuntimeError("Do not qualify against opened finals")
    original = output / "selection.json"
    preserved = output / "selection-before-covariance.json"
    if preserved.exists():
        raise RuntimeError("This prospective study has already been attempted")
    shutil.copyfile(original, preserved)
    freeze = ROOT / "reports/FIELD-001-COMPATIBILITY-FREEZE.json"
    write_json(freeze, {"created_utc": utc(), "sources": source_manifest(ROOT),
                        "prior_selection_sha256": sha256(preserved), "finals_opened": False})
    selection = json.loads(original.read_text())
    calibration = observations(4096 * 6, 79092027, rotated=True, haar=True)
    development = context_episodes(1024, 89092026, haar=True)
    vacuum = development["resistance_for_audit_only"][:, 0] == 0
    report = {"calibration_identity": calibration["identity"], "development_identity": development["identity"],
              "quantile": .995, "diagonal_shrinkage": .05, "seeds": {}}
    for seed in CONFIG["seeds"]:
        chosen = selection["refinement_selection"][str(seed)]
        successor, saved = load_model(ROOT / chosen["selected"]["path"])
        with torch.no_grad():
            context = successor.context(*(calibration[k].reshape(4096, 6, -1) for k in ("v", "f", "m", "a"))).double()
            center = context.mean(0)
            centered = context - center
            covariance = centered.T @ centered / (len(centered) - 1)
            covariance += .05 * torch.diag(covariance.diag()) + 1e-14 * torch.eye(3)
            precision = torch.linalg.inv(covariance)
            distance = torch.einsum("ni,ij,nj->n", centered, precision, centered)
            threshold = float(torch.quantile(distance, .995))
            owner = CalibratedOwner(successor, threshold, center, precision)
            raw, actual = predict(successor, development)
            gated, _ = predict(owner, development)
            prior = successor.base(development["v"][:, -1], development["f"][:, -1], development["m"][:, -1])
            rows = {}
            for label, mask in (("vacuum", vacuum), ("novel", ~vacuum)):
                rows[label] = {name: float((value[mask] - actual[mask]).square().mean())
                               for name, value in (("base", prior), ("ungated", raw), ("gated", gated))}
            accepted = (rows["novel"]["gated"] < .5 * rows["novel"]["base"]
                        and rows["novel"]["gated"] <= 1.05 * rows["novel"]["ungated"]
                        and rows["vacuum"]["gated"] <= 1.25 * rows["vacuum"]["base"])
        record = {"threshold": threshold, "accepted": accepted, "development": rows,
                  "raw_checkpoint": chosen["selected"], "mechanism": "calibrated context covariance",
                  "base_preserved": weight_hash(owner.base) == weight_hash(successor.base)}
        path = output / f"calibrated-{seed}.pt"
        torch.save({"schema": "sera-field.qualified-owner.2", "specification": owner.specification(),
                    "model": owner.state_dict(), "weight_sha256": weight_hash(owner), "step": saved["step"],
                    "metadata": {"qualification": record, "origin": saved["metadata"],
                                 "calibration_identity": calibration["identity"], "additional_gradient_updates": 0}}, path)
        record["checkpoint"] = {"path": str(path.relative_to(ROOT)), "sha256": sha256(path),
                                 "weight_sha256": weight_hash(owner), "step": saved["step"]}
        chosen["qualification_attempts"] = [chosen["qualified_owner"], record]
        if accepted:
            chosen["qualified_owner"] = record
        report["seeds"][str(seed)] = record
    write_json(output / "compatibility.json", report)
    selection["compatibility_freeze_sha256"] = sha256(freeze)
    write_json(original, selection)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
