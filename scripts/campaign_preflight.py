"""Read-only campaign reconciliation; no models, finals or other jobs are started."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, utc, write_json


def git(root, *args):
    # These user-designated local repositories may be owned by the other Windows
    # sandbox account. Trust only this exact path for this read-only invocation;
    # never change global safe.directory or suppress unrelated ownership checks.
    exact = Path(root).resolve().as_posix()
    return subprocess.check_output(["git", "-c", "safe.directory=" + exact, "-C", exact, *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    failures = []
    if ROOT.resolve() != Path(manifest["workspace"]).resolve():
        failures.append("Wrong workspace")
    branch = git(ROOT, "branch", "--show-current")
    if branch != manifest["branch"]:
        failures.append("Wrong branch")
    source_checks = []
    for item in manifest["immutable_inputs"]:
        path = Path(item["path"])
        actual = sha256(path) if path.is_file() else None
        source_checks.append({"path": str(path), "expected": item["sha256"], "actual": actual,
                              "matches": actual == item["sha256"]})
        if actual != item["sha256"]:
            failures.append("Changed/missing immutable input: " + str(path))
    protected = [{"path": path, "head": git(path, "rev-parse", "HEAD"),
                  "dirty": git(path, "status", "--porcelain")} for path in manifest["protected_repositories"]]
    lease = Path(manifest["shared_lease"])
    state = {"checked_utc": utc(), "workspace": str(ROOT), "head": git(ROOT, "rev-parse", "HEAD"),
             "branch": branch, "dirty": git(ROOT, "status", "--porcelain"), "inputs": source_checks,
             "protected": protected, "lease_present": lease.exists(),
             "lease": json.loads(lease.read_text()) if lease.exists() else None,
             "failures": failures, "ready_for_engineering": not failures,
             "training_ready": False,
             "training_gate": "Subject adapters, goal memory, verifiers, learning controls and finite implementation protocol must pass before long training."}
    write_json(args.output, state)
    print(json.dumps({k: state[k] for k in ("workspace", "head", "branch", "lease_present", "failures", "ready_for_engineering", "training_ready")}, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
