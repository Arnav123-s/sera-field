"""Prospectively added invariant-input classical control; preserves the original run."""

import json
import shutil

import torch

from .model import Dynamics
from .observatory import observations
from .records import sha256, source_manifest, utc, write_json
from .training import CONFIG, ROOT, fit, supervised


def main():
    supervised()
    output = ROOT / "runs/FIELD-001"
    if (output / "FINALS_OPENED.json").exists():
        raise RuntimeError("Cannot add or select controls after opening finals")
    selection_file = output / "selection.json"
    preserved = output / "selection-before-control.json"
    if not preserved.exists():
        shutil.copyfile(selection_file, preserved)
    manifest_path = ROOT / "reports/FIELD-001-ADDENDUM-FREEZE.json"
    if not manifest_path.exists():
        write_json(manifest_path, {"created_utc": utc(), "sources": source_manifest(ROOT),
                                   "prior_selection_sha256": sha256(preserved), "finals_opened": False})
    selection = json.loads(selection_file.read_text())
    train = observations(CONFIG["train_count"], CONFIG["base_train_seed"])
    dev = {"interpolation": observations(1024, CONFIG["base_dev_seed"]),
           "rotation": observations(1024, CONFIG["base_dev_seed"] + 1, rotated=True)}
    assert train["identity"] == selection["results"]["field-11"]["metadata"]["training_identity"]
    for seed in CONFIG["seeds"]:
        torch.manual_seed(seed)
        result = fit(Dynamics("invariant"), train, dev, output / f"invariant-{seed}", seed)
        selection["results"][f"invariant-{seed}"] = result
    selection["control_addendum"] = {"freeze_sha256": sha256(manifest_path),
                                      "prior_selection_sha256": sha256(preserved), "created_utc": utc()}
    write_json(selection_file, selection)
    print("Matched invariant control completed; all final cohorts remain unopened.")


if __name__ == "__main__":
    main()
