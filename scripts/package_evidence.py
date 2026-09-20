"""Package the completed, immutable study without changing any scientific state."""

import hashlib
import json
from pathlib import Path
import statistics
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    if (ROOT / 'checkpoints/SCFE-004/SELECTION.json').exists():
        raise SystemExit('FIELD-001 historical packaging would overwrite newer research state. '
                         'Its existing archive is preserved; use the connected delivery scripts for the current owner.')
    final = read("runs/FIELD-001/final.json")
    selected = read("runs/FIELD-001/selection.json")
    audit = read("runs/delivery-audit-001/audit.json")
    replay = read("runs/replay-002/replay.json")
    assert replay["exact_equal"]
    assert final == read("runs/replay-001/replayed-report.json")
    assert final["selection_sha256"] == digest(ROOT / "runs/FIELD-001/selection.json")
    assert "29 passed" in (ROOT / "runs/contracts-007/process.log").read_text()
    reference = ROOT.parent.parent / "projects/sera/runs/sera-intervention-live/revisions/000000-b29d8cccea6a.json"
    reference_digest = digest(reference)
    assert reference_digest == "b29d8cccea6a7b8b9e0f0bbc28432d146a6388bca7716a828c446b3b42036d95"

    attempts = []
    for path in sorted((ROOT / "runs").glob("*/state.json")):
        state = json.loads(path.read_text())
        assert state["status"] in {"PASS", "FAILED"}, path
        assert state.get("lease_released") and state["resources"]["active_processes"] == 0
        attempts.append({key: value for key, value in state.items() if key != "sources"})
    costs = {"scope": "All supervised numerical jobs, including failed replay, tests and demos",
             "attempts": attempts, "wall_seconds": sum(a["wall_seconds"] for a in attempts),
             "cpu_seconds": sum(a["resources"]["cpu_seconds"] for a in attempts),
             "peak_process_tree_committed_bytes": max(a["resources"]["peak_committed_bytes"] for a in attempts),
             "limit_bytes": 2147483648, "numerical_threads": 1, "paid_compute": False,
             "excludes": "Unmetered reading, engineering, downloads and file packaging; wall sum is job time, not total project duration"}
    write("reports/COSTS.json", costs)

    summary = {"schema": final["schema"], "selection_sha256": final["selection_sha256"],
               "final_identities": final["final_identities"],
               "refinement_final_identity": final["refinement_final_identity"],
               "base": {}, "refinement": final["refinement"],
               "strong_classical_power_control": dict(final["strong_classical_power_control"])}
    for name, result in final["base"].items():
        summary["base"][name] = {**result, "planning": {k: v for k, v in result["planning"].items() if k != "cases"}}
    summary["strong_classical_power_control"]["planning"] = {
        k: v for k, v in final["strong_classical_power_control"]["planning"].items() if k != "cases"}
    write("reports/FIELD-001/summary.json", summary)
    write("reports/FIELD-001/delivery-audit.json", audit)
    write("reports/FIELD-001/replay.json", replay)
    write("reports/FIELD-001/demo.json", audit["demo"])

    initial_sources = read("runs/final-001/state.json")["sources"]
    changes = {path: {"at_final": old, "at_delivery": digest(ROOT / path)}
               for path, old in initial_sources.items() if digest(ROOT / path) != old}
    assert set(changes) == {"sera_field/cli.py", "sera_field/evaluation.py"}
    write("reports/FIELD-001/post-final-engineering.json", {
        "changes": changes, "model_training_and_selection_changed": False,
        "reason": "Canonical JSON replay comparison and CLI horizon/finite-input handling; no fitting or final-based selection",
        "additional_audit_code": ["sera_field/delivery_audit.py", "tests/test_interface.py", "scripts/package_evidence.py"]})

    checkpoints = {}
    for name, record in {
        "field-11.pt": selected["results"]["field-11"]["selected"],
        "calibrated-11.pt": selected["refinement_selection"]["11"]["qualified_owner"]["checkpoint"],
    }.items():
        assert digest(ROOT / "checkpoints/FIELD-001" / name) == record["sha256"]
        checkpoints[name] = {**record, "release_path": "checkpoints/FIELD-001/" + name}
    write("checkpoints/FIELD-001/manifest.json", {
        "default_seed": 11, "selection_basis": "Fixed seed named before final evaluation",
        "files": checkpoints, "earlier_SERA_weights_imported": False,
        "initializations": audit["lineage"]})

    records = sorted(path for path in (ROOT / "runs").rglob("*") if path.is_file())
    archive = ROOT / "reports/FIELD-001/raw-evidence.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in records:
            bundle.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
    write("reports/FIELD-001/artifacts.json", {
        "archive": {"path": archive.relative_to(ROOT).as_posix(), "sha256": digest(archive),
                    "bytes": archive.stat().st_size, "file_count": len(records)},
        "members": {p.relative_to(ROOT).as_posix(): {"sha256": digest(p), "bytes": p.stat().st_size} for p in records},
        "final_report_sha256": digest(ROOT / "runs/FIELD-001/final.json"),
        "proposal_sha256": "b0be4b4aea776bcdfd580e000aebbb1bd7b56523e6b0df32f0c1fdb89fbfc9cd",
        "reference_checkpoint_sha256": reference_digest})

    lines = ["# FIELD-001 — from-scratch shared physical field", "",
        "I trained a new field core from fresh initial weights, reused its learned physical mechanism across four task views, and trained an evidence-qualified correction. The original SERA repository and owner remain intact. This report distinguishes supplied structure, learned weights and independently checked outcomes.", "",
        "## Training and evidence", "",
        "Twelve base models (four mechanisms × three seeds) and six residual successors each received 3,000 optimizer updates: **54,000 gradient updates and 6,912,000 minibatch query presentations** in total. Each minibatch contained 128 queries. There were 8,192 unique base observations and 8,192 refinement windows containing six supports and one query: **65,536 unique physical observation records** in the gradient curriculum. Repeated presentations are not counted as new observations.", "",
        "The data are generated physical diagnostic observations. Central differences of simulated positions supply velocity and acceleration targets. Calibrated mass and actual force are inputs. The simulator formula, hidden resistance coefficient and query outcome are excluded from the model's context inputs. Pauli features, the equivariant vector basis, context statistics, training families and task algorithms are supplied engineering. Coefficient functions and residual responses are learned.", "",
        "All twelve base initializations were reconstructed exactly from seeds 11, 29 and 47. Initial SU(2) tensors changed during training. Every saved intermediate checkpoint, loss curve, optimizer state, sampler state and RNG state is in the evidence archive. The base is frozen inside each successor. Twelve split collections have distinct content identities and zero duplicate input rows across all 66 pairwise comparisons.", "",
        "Checkpoint selection used development data only. A stronger invariant control and two qualification studies were frozen before the final marker was opened. The final mixture had **664 novel-context and 360 vacuum queries**; the frozen prose has one conflicting count, documented in the [post-build audit](../docs/POST_BUILD_AUDIT.md). No additional cases were added to alter these results.", "",
        "## Matched neural controls", "",
        "All base candidates have 783 trainable scalars, matched data, updates, optimizer and seeds. The table reports the mean of three initializations. NMSE is mean squared acceleration error divided by target mean square; it is not a classification accuracy. Lower is better.", "",
        "| Mechanism | Interpolation NMSE | Rotated NMSE | Mass-extension NMSE | Plan successes by seed | Inverse mass mean relative error |", "|---|---:|---:|---:|---|---:|"]
    labels = {"field": "SU(2) field", "scrambled": "Symmetry-broken field", "dense": "Raw-input classical network", "invariant": "Invariant classical network"}
    for kind in labels:
        rows = [final["base"][f"{kind}-{seed}"] for seed in (11, 29, 47)]
        metrics = [statistics.mean(r["finals"][k]["nmse"] for r in rows) for k in ("interpolation", "rotation", "mass_extension")]
        success = ", ".join(str(r["planning"]["success_at_5cm_and_5cm_per_s"]) + "/24" for r in rows)
        inverse = statistics.mean(r["cross_use"]["inverse_mass_relative_error"]["mean"] for r in rows)
        lines.append(f"| {labels[kind]} | {metrics[0]:.7g} | {metrics[1]:.7g} | {metrics[2]:.7g} | {success} | {100 * inverse:.3f}% |")
    lines += ["", "Interpolation and rotation each use 2,048 cases, and mass extension uses 1,024 cases. The 128 cross-use cases are a subset of the rotated cohort. Planning uses the same 24 cases across mechanisms and seeds: the three repeats are not 72 independently sampled tasks. Success requires both endpoint distance and speed below 0.05 simulator units after one second. A separate DOP853 solver checks applied controls.", "",
        "The SU(2) field improved transfer relative to the symmetry-broken and raw-input controls. The invariant classical network achieved lower errors and all 24 planning successes in each initialization. These results support the value of the supplied physical invariants on this task; they favor the simpler invariant network over the tested group-link network for this vacuum family.", "",
        "A separate strong classical control receives a supplied isotropic power-law family and fits two coefficients to the same 8,192 observations. It recovers a mass exponent of -1, reaches rotated NMSE about 3.34e-15 and passes 24/24 plans. Its stronger equation-family prior and least-squares fit differ from neural training; it is recorded as a mechanism control, not hidden or presented as independent discovery.", "",
        "## Reuse of the learned field", "",
        "| Field seed | Mean forward position error | Mean inverse mass relative error | Mean half-mass position error | Half-mass median position error |", "|---|---:|---:|---:|---:|"]
    for seed in (11, 29, 47):
        row = final["base"][f"field-{seed}"]["cross_use"]
        lines.append(f"| {seed} | {row['forward_position_endpoint']['mean']:.6f} | {100*row['inverse_mass_relative_error']['mean']:.3f}% | {row['mass_halving_position_endpoint']['mean']:.6f} | {row['mass_halving_position_endpoint']['median']:.6f} |")
    lines += ["", "All four task views use the same checkpoint with zero task-specific weight updates. Inverse inference and control optimization are engineered algorithms operating through the learned function. Of the 128 half-mass cases, 28 move below the taught mass range; these cases remain in the aggregate and explain why the tail must be reported alongside the median. Full maxima and 95th percentiles are in `FIELD-001/summary.json`.", "",
        "## Acquired correction and retention", "",
        "The residual curriculum adds nonlinear velocity-dependent resistance. At inference, six measured support outcomes summarize the context; a seventh query outcome is withheld from the predictor. Development selection chose the wider successor for seeds 11 and 29 and the smaller one for seed 47. No final selection changed this choice.", "",
        "| Seed | Width | New-context base MSE | Qualified MSE | Reduction | Vacuum base MSE | Qualified vacuum MSE |", "|---|---:|---:|---:|---:|---:|---:|"]
    for seed in (11, 29, 47):
        chosen = final["refinement"][f"selected-{seed}"]
        raw = final["refinement"][f"{chosen['selection']['method']}-{seed}"]["finals"]
        gated = chosen["qualified_context_finals"]
        base, revised = raw["new_context"]["base_mse"], gated["new_context"]["mse"]
        lines.append(f"| {seed} | {28 if chosen['selection']['method']=='expanded' else 12} | {base:.7f} | {revised:.7f} | {100*(1-revised/base):.3f}% | {raw['vacuum_context']['base_mse']:.7f} | {gated['vacuum_context']['mse']:.7f} |")
    lines += ["", "The raw residuals increased vacuum MSE to 0.00755, 0.01311 and 0.02466. The first energy-only compatibility test failed two development qualifications. The replacement uses the mean and covariance of measured residual statistics, calibrated on fresh vacuum observations, and a separately checked threshold. Final familiar-context MSE stayed within 2.06% of the base across all seeds. With no new context, the successor returns its byte-identical retained base. This protection is explicit, not an inferred guarantee of topological memory.", "",
        "Each selected successor then faced a fresh chosen intervention. A fixed disagreement-per-cost policy compared alternatives, applied a force and checked the outcome with DOP853. All three improved their original-goal response and earned one evidence-bound credit. Duplicate credit was rejected, and a separate 25% actuator attenuation was detected in each case. Credit is recorded verification; no policy-weight update is claimed in this cycle.", "",
        "## Actual task demonstration", "",
        "The designated seed-11 field predicts position 0.49943 after one second for mass 2 under force 2, and 1.01341 when the mass is changed to 1. It estimates mass 1.93346 from force 2 and acceleration 1. For a target displacement of 0.20, it proposes forces +1.65669 and -1.69002; independent simulation reaches 0.20500 with final speed 0.00833. The original situation and weights remain unchanged. These examples and their full identities are in `FIELD-001/demo.json`.", "",
        "## Verification and costs", "",
        "The final contract suite passes **29 tests**, including actual link-weight updates, local-frame operations, expansion identity, retained weights, branch integrity, reward integrity, context leakage protection, checkpoint reload and task-interface regressions. Fresh-process replay matches every serialized final value and case exactly. The earlier replay comparator failure is preserved: tuple/list normalization was an engineering repair, not a numerical tolerance or model change.", "",
        f"All supervised numerical attempts consumed **{costs['wall_seconds']/60:.3f} wall minutes and {costs['cpu_seconds']/60:.3f} CPU minutes**. Peak committed process-tree memory was **{costs['peak_process_tree_committed_bytes']/2**20:.2f} MiB**, below the 2 GiB cap. One numerical CPU thread was used. Costs include both replay attempts, failed scientific candidates, all tests and the packaged CLI smoke check. No paid compute was used. Reading, engineering, downloads and packaging are outside these measured numerical totals.", "",
        "The summed model-fit wall times across three seeds were 51.29 s for the field, 49.41 s for the broken-symmetry field, 11.20 s for the raw-input network and 14.02 s for the invariant network. Equal updates did not imply equal computation. Residual training and evaluation costs are also included in the full supervisor ledger.", "",
        "Base tensors occupy 3,132 bytes. The selected qualified owners occupy 9,308 bytes for seeds 11 and 29, and 6,748 bytes for seed 47, including calibration buffers. These figures exclude optimizer state, serialized evidence and temporary allocations; the measured process-tree peak is reported separately.", "",
        "## Retained deliverables and continuation", "",
        "[Evidence index](INDEX.md) · [Usable commands](../docs/USAGE.md) · [Source audit](../docs/POST_BUILD_AUDIT.md) · [Exact costs](COSTS.json) · [Continuation state](STATE.json). All failed qualifications, comparison weights, initializations, intermediate checkpoints and scientific results remain available. The next capability package is a from-scratch human-language-to-situation encoder, retaining field and invariant classical controls and using fresh prospective cohorts. FIELD-001 finals stay closed to further tuning."]
    (ROOT / "reports/FIELD-001.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write("reports/STATE.json", {
        "completed": "FIELD-001 trained, evaluated, replayed and audited",
        "full_vision": "Persistent grounded understanding, imagination, investigation and learning across language and domains",
        "full_vision_completed": False, "work_delegated": False, "publication": "local independent Git repository",
        "default_checkpoint": checkpoints["field-11.pt"],
        "qualified_successor": checkpoints["calibrated-11.pt"],
        "selection_sha256": final["selection_sha256"], "sealed_finals_opened": True,
        "ongoing_owned_jobs": [], "numerical_lease_released": True,
        "resume_training": "All scheduled FIELD-001 training is completed; do not restart",
        "next_executable_user_task": ".\\.venv\\Scripts\\python.exe scripts/supervise.py --attempt my-imagination-001 -- -m sera_field.cli imagine --mass 2 --force 2,0,0 --counterfactual-mass 1",
        "next_research_gate": "FIELD-002: freeze human-source identities, language grounding curriculum, matched controls and untouched transfer cohort before new training",
        "preserved_reference_head": "0dcbcb902706f3d299cd38a433fcf1f26a357efd",
        "preserved_reference_checkpoint_sha256": reference_digest})
    print(json.dumps({"archive_bytes": archive.stat().st_size, "archive_members": len(records),
                      "numerical_wall_minutes": costs["wall_seconds"]/60,
                      "numerical_cpu_minutes": costs["cpu_seconds"]/60,
                      "peak_mib": costs["peak_process_tree_committed_bytes"]/2**20}, indent=2))


if __name__ == "__main__":
    main()
