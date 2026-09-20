"""Prospective, checkpointed training from random initialization."""

import argparse
import json
import os
from pathlib import Path
import time

import numpy as np
import torch

from .model import Dynamics, QualifiedOwner, Refinement, construct, parameters, weight_hash
from .observatory import context_episodes, observations
from .records import sha256, source_manifest, utc, write_json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = {"seeds": [11, 29, 47], "steps": 3000, "batch": 128,
          "base_train_seed": 19092026, "base_dev_seed": 29092026,
          "base_final_seed": 39092026, "refine_train_seed": 49092026,
          "refine_dev_seed": 59092026, "refine_final_seed": 69092026,
          "train_count": 8192, "dev_count": 1024, "refine_dev_count": 512,
          "lr_start": .002, "lr_end": .0002, "width": 12, "extra_channels": 16}


def supervised():
    if not os.environ.get("SERA_FIELD_SUPERVISED"):
        raise RuntimeError("Launch numerical work through scripts/supervise.py")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)


def load_model(path):
    saved = torch.load(path, map_location="cpu", weights_only=True)
    model = construct(saved["specification"])
    model.load_state_dict(saved["model"])
    model.eval()
    if weight_hash(model) != saved["weight_sha256"]:
        raise RuntimeError("Checkpoint model identity mismatch")
    return model, saved


def predict(model, data, indices=None):
    v, f, m, a = (data[k] if indices is None else data[k][indices] for k in ("v", "f", "m", "a"))
    if isinstance(model, (Refinement, QualifiedOwner)):
        context = model.context(v[:, :-1], f[:, :-1], m[:, :-1], a[:, :-1])
        return model(v[:, -1], f[:, -1], m[:, -1], context), a[:, -1]
    return model(v, f, m), a


def scores(model, data):
    with torch.no_grad():
        prediction, target = predict(model, data)
        mse = float((prediction - target).square().mean())
        denom = float(target.square().mean())
        return {"mse": mse, "nmse": mse / max(denom, 1e-12),
                "finite": bool(torch.isfinite(prediction).all())}


def save_checkpoint(path, model, optimizer, scheduler, generator, step, metadata):
    path = Path(path)
    relative = path.resolve().relative_to(ROOT.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    value = {"schema": "sera-field.checkpoint.1", "specification": model.specification(),
             "model": model.state_dict(), "weight_sha256": weight_hash(model),
             "optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict(),
             "sampler_rng": generator.get_state(), "torch_rng": torch.random.get_rng_state(),
             "step": step, "metadata": metadata}
    temp = path.with_suffix(".tmp")
    torch.save(value, temp)
    temp.replace(path)
    return {"path": str(relative), "sha256": sha256(path),
            "weight_sha256": value["weight_sha256"], "step": step}


def fit(model, train, devs, path, seed, *, steps=3000):
    path.mkdir(parents=True, exist_ok=True)
    if (path / "result.json").exists():
        result = json.loads((path / "result.json").read_text())
        if sha256(ROOT / result["selected"]["path"]) != result["selected"]["sha256"]:
            raise RuntimeError("Completed checkpoint changed")
        return result
    optimizer = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=.002)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, steps, eta_min=.0002)
    generator = torch.Generator().manual_seed(seed + 9000)
    metadata = {"seed": seed, "training_identity": train["identity"],
                "development_identities": {k: d["identity"] for k, d in devs.items()},
                "config": CONFIG, "parameters": parameters(model), "initial_weight_sha256": weight_hash(model)}
    cursor = 0
    best = None
    if (path / "cursor.json").exists():
        progress = json.loads((path / "cursor.json").read_text())
        saved = torch.load(ROOT / progress["last"]["path"], weights_only=True)
        if saved["metadata"]["training_identity"] != train["identity"]:
            raise RuntimeError("Resume dataset changed")
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
        scheduler.load_state_dict(saved["scheduler"])
        generator.set_state(saved["sampler_rng"])
        torch.random.set_rng_state(saved["torch_rng"])
        metadata = saved["metadata"]
        cursor, best = saved["step"], progress["best"]
    start = time.perf_counter()
    initial = {name: scores(model, data) for name, data in devs.items()}
    if cursor > 0:
        initial = json.loads((path / "initial.json").read_text())["scores"]
    if cursor == 0:
        write_json(path / "initial.json", {"metadata": metadata, "scores": initial})
        save_checkpoint(path / "step-00000.pt", model, optimizer, scheduler, generator, 0, metadata)
    with (path / "learning.jsonl").open("a", encoding="utf-8") as log:
        for step in range(cursor + 1, steps + 1):
            indices = torch.randint(len(train["v"]), (128,), generator=generator)
            prediction, target = predict(model, train, indices)
            loss = (prediction - target).square().mean()
            if not torch.isfinite(loss):
                raise RuntimeError("Nonfinite training loss; preserve this attempt")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            gradient_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 5.))
            optimizer.step()
            scheduler.step()
            if step % 100 == 0 or step == 1:
                record = {"step": step, "mse": float(loss.detach()), "gradient_norm": gradient_norm,
                          "lr": scheduler.get_last_lr()[0], "elapsed_seconds": time.perf_counter() - start}
                log.write(json.dumps(record) + "\n")
                log.flush()
            if step % 500 == 0 or step == steps:
                measured = {name: scores(model, data) for name, data in devs.items()}
                primary = sum(s["nmse"] for s in measured.values()) / len(measured)
                checkpoint = save_checkpoint(path / f"step-{step:05}.pt", model, optimizer,
                                             scheduler, generator, step, metadata)
                if best is None or primary < best["score"]:
                    best = {"score": primary, "checkpoint": checkpoint, "development": measured}
                write_json(path / "cursor.json", {"last": checkpoint, "best": best})
                print(json.dumps({"model": path.name, "step": step, "development": measured}), flush=True)
    result = {"selected": best["checkpoint"], "development": best["development"],
              "initial": initial, "training_seconds_this_invocation": time.perf_counter() - start,
              "updates": steps, "examples_presented": steps * 128, "metadata": metadata}
    write_json(path / "result.json", result)
    return result


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    freeze_path = ROOT / "reports" / "FIELD-001-FREEZE.json"
    current_sources = source_manifest(ROOT)
    if freeze_path.exists():
        freeze = json.loads(freeze_path.read_text())
        if freeze["sources"] != current_sources:
            raise RuntimeError("Frozen code/protocol changed; record a prospective revision")
    else:
        write_json(freeze_path, {"created_utc": utc(), "sources": current_sources, "config": CONFIG,
                                 "finals_opened": False, "training_from_scratch": True})
    if (output / "FINALS_OPENED.json").exists():
        raise RuntimeError("This cohort is already opened; no training against it")
    train = observations(CONFIG["train_count"], CONFIG["base_train_seed"])
    dev = {"interpolation": observations(1024, CONFIG["base_dev_seed"]),
           "rotation": observations(1024, CONFIG["base_dev_seed"] + 1, rotated=True)}
    all_results = {}
    for seed in CONFIG["seeds"]:
        for kind in ("field", "scrambled", "dense"):
            torch.manual_seed(seed)
            model = Dynamics(kind)
            result = fit(model, train, dev, output / f"{kind}-{seed}", seed)
            all_results[f"{kind}-{seed}"] = result
    refine_train = context_episodes(8192, CONFIG["refine_train_seed"])
    refine_dev = {"mixed_context": context_episodes(512, CONFIG["refine_dev_seed"])}
    selection = {}
    for seed in CONFIG["seeds"]:
        base, _ = load_model(ROOT / all_results[f"field-{seed}"]["selected"]["path"])
        base_before = weight_hash(base)
        torch.manual_seed(seed + 100)
        narrow = Refinement(base)
        wide = narrow.expanded(16)
        for name, model in (("fixed", narrow), ("expanded", wide)):
            result = fit(model, refine_train, refine_dev, output / f"{name}-{seed}", seed + 100)
            all_results[f"{name}-{seed}"] = result
        fixed = all_results[f"fixed-{seed}"]
        expanded = all_results[f"expanded-{seed}"]
        winner = "expanded" if expanded["development"]["mixed_context"]["mse"] < .8 * fixed["development"]["mixed_context"]["mse"] else "fixed"
        with torch.no_grad():
            d = refine_dev["mixed_context"]
            unchanged = ((base(d["v"][:, -1], d["f"][:, -1], d["m"][:, -1]) - d["a"][:, -1]) ** 2).mean()
        chosen = all_results[f"{winner}-{seed}"]
        selected_model, _ = load_model(ROOT / chosen["selected"]["path"])
        with torch.no_grad():
            predicted, actual = predict(selected_model, d)
            novel = d["resistance_for_audit_only"][:, 0] > 0
            baseline_novel = ((base(d["v"][novel, -1], d["f"][novel, -1], d["m"][novel, -1]) - actual[novel]) ** 2).mean()
            selected_novel = (predicted[novel] - actual[novel]).square().mean()
        selection[str(seed)] = {"method": winner,
                                "qualified": float(selected_novel) < .5 * float(baseline_novel),
                                "new_context_base_mse": float(baseline_novel),
                                "new_context_selected_mse": float(selected_novel),
                                "baseline_development_mse": float(unchanged),
                                "selected": chosen["selected"], "base_preserved": weight_hash(base) == base_before}
    write_json(output / "selection.json", {"created_utc": utc(), "results": all_results,
                                            "refinement_selection": selection, "config": CONFIG,
                                            "freeze_sha256": sha256(freeze_path), "finals_seen": False})
    print("Training and development selection complete. Final evaluation remains closed.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "runs/FIELD-001")
    args = parser.parse_args()
    supervised()
    run(args.output.resolve())


if __name__ == "__main__":
    main()
