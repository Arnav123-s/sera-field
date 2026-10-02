"""Single-process timing and cProfile report for the M1 truth layer."""

import cProfile
import json
import os
import platform
import pstats
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
if os.environ.get("PYTHONHASHSEED") != "0":
    raise SystemExit("Set PYTHONHASHSEED=0 before running this benchmark")
cache_dir = ROOT / "core-results" / "bench" / "numba-cache"
cache_dir.mkdir(parents=True, exist_ok=True)
os.environ["NUMBA_CACHE_DIR"] = str(cache_dir)

import numba
from ccops5.core import grammar, truth, checker, worlds


FORCES = ("rubbing", "spring", "water drag", "swing", "x*v force", "motor", "none")


def one_world(force, index, situations, profile=None):
    w = worlds.make(1, force, index=index, situations=situations, tricks=0.05)
    start = time.perf_counter()
    truth.Ledger(grammar.space(), w.sigma).add(w.throws[0])
    warmup = time.perf_counter() - start
    if profile is not None:
        profile.enable()
    try:
        times = {}
        start = time.perf_counter()
        ledger = truth.Ledger(grammar.space(), w.sigma)
        for throw in w.throws:
            ledger.add(throw)
        times["ledger"] = time.perf_counter() - start
        times["per_throw"] = times["ledger"] / len(w.throws)
        fam = ledger.best_family()
        start = time.perf_counter()
        cert = truth.certify(ledger, fam, eps=0.1)
        times["certify_best"] = time.perf_counter() - start
        if w.truth is not None:
            start = time.perf_counter()
            truth.certify(ledger, w.truth, eps=0.1)
            times["certify_truth"] = time.perf_counter() - start
        else:
            times["certify_truth"] = None
        start = time.perf_counter()
        truth.band_of(ledger.throws, fam, ledger.sigma, truth.scope_of(ledger.throws),
                      1e-3 / ledger.n_space)
        times["band_of"] = time.perf_counter() - start
        start = time.perf_counter()
        truth.something_else(ledger, fam)
        times["something_else"] = time.perf_counter() - start
        start = time.perf_counter()
        checker.check(cert, ledger.throws, w.sigma)
        times["checker"] = time.perf_counter() - start
    finally:
        if profile is not None:
            profile.disable()
    times["total"] = sum(value for key, value in times.items()
                         if key not in ("per_throw",) and value is not None)
    return {"force": force, "index": index, "situations": situations,
            "throws": len(w.throws), "best_family": repr(fam), "truth_family": repr(w.truth),
            "warmup_seconds": warmup, "timings_seconds": times}


def profile_rows(profile, sort_key):
    stats = pstats.Stats(profile)
    rows = []
    for (filename, line, function), (primitive, calls, own, cumulative, _callers) in stats.stats.items():
        rows.append({"file_line": f"{filename}:{line}", "function": function,
                     "ncalls": str(calls) if calls == primitive else f"{calls}/{primitive}",
                     "tottime": own, "cumtime": cumulative})
    return sorted(rows, key=lambda row: (-row[sort_key], row["file_line"], row["function"]))[:40]


def git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                       stderr=subprocess.DEVNULL, text=True).strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def fmt(value):
    return "—" if value is None else f"{value:.3f}"


def profile_table(rows):
    lines = ["| File:line | Function | Calls | Own s | Cumulative s |",
             "|---|---|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['file_line']} | {row['function']} | {row['ncalls']} | "
                     f"{row['tottime']:.3f} | {row['cumtime']:.3f} |")
    return lines


def main():
    sha = git_sha()
    # A slow six-situation world triggers a complete, consistent four-situation run.
    for situations in (6, 4):
        results = []
        slow = False
        for i, force in enumerate(FORCES):
            print(f"Benchmarking {force} ({situations} situations)", flush=True)
            row = one_world(force, 900 + i, situations)
            results.append(row)
            print(f"  timed steps: {row['timings_seconds']['total']:.1f} s", flush=True)
            if situations == 6 and row["timings_seconds"]["total"] > 240:
                slow = True
                break
        if not slow:
            break
        print("A world exceeded four minutes; restarting all worlds with four situations", flush=True)

    print("Profiling spring", flush=True)
    profiler = cProfile.Profile()
    spring_profile = one_world("spring", 901, situations, profiler)
    own = profile_rows(profiler, "tottime")
    cumulative = profile_rows(profiler, "cumtime")
    profile_total = sum(value for (primitive, calls, value, cum, callers) in
                        pstats.Stats(profiler).stats.values())
    data = {"git_short_sha": sha, "cpu_count": os.cpu_count(),
            "python_version": platform.python_version(), "numba_version": numba.__version__,
            "situations": situations, "worlds": results, "spring_profile_run": spring_profile,
            "profile_total_seconds": profile_total,
            "profile_top_40_tottime": own, "profile_top_40_cumtime": cumulative}
    out = ROOT / "core-results" / "bench"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"bench-{sha}.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    lines = ["# B1-01 truth-layer benchmark", "",
             f"Git: `{sha}`. Python {data['python_version']}; Numba {data['numba_version']}; "
             f"CPUs: {data['cpu_count']}. One process; {situations} situations per world.", "",
             "All values below are seconds. The first-world warm-up includes Numba compilation and is "
             "excluded from timed steps. The spring profile is a separate run.", "",
             "| World | Throws | Ledger | Per throw | Cert best | Cert truth | Band | Else | Checker | Total |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in results:
        t = row["timings_seconds"]
        lines.append(f"| {row['force']} | {row['throws']} | {fmt(t['ledger'])} | "
                     f"{t['per_throw']:.4f} | {fmt(t['certify_best'])} | "
                     f"{fmt(t['certify_truth'])} | {fmt(t['band_of'])} | "
                     f"{fmt(t['something_else'])} | {fmt(t['checker'])} | {fmt(t['total'])} |")
    lines += ["", f"First-world warm-up and compilation: {results[0]['warmup_seconds']:.3f} s.",
              "", "## Spring profile: top 40 by own time", ""]
    lines += profile_table(own)
    lines += ["", "## Spring profile: top 40 by cumulative time", ""]
    lines += profile_table(cumulative)
    lines += ["", "## Observations", ""]
    spring = results[1]["timings_seconds"]
    for key, label in (("ledger", "Ledger build"), ("certify_best", "Best-family certification"),
                       ("band_of", "Explicit band"), ("checker", "Independent checker")):
        lines.append(f"- {label} takes {spring[key]:.3f} s, "
                     f"{spring[key] / spring['total'] * 100:.1f}% of spring's timed steps.")
    for row in own[:2]:
        lines.append(f"- `{row['function']}` at `{row['file_line']}` uses "
                     f"{row['tottime']:.3f} s of own time, "
                     f"{row['tottime'] / profile_total * 100:.1f}% of the spring profile.")
    report = ROOT / "reports" / "B1-01-profile.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out / f'bench-{sha}.json'} and {report}", flush=True)


if __name__ == "__main__":
    main()
