import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


CAPABILITIES = {
    "L0": "Honest truth, independent checker",
    "L1": "Designs its own experiments",
    "L2": "Knows when its maths is inadequate",
    "L3": "Grows new representation",
    "L4": "Learns to discover, zero-shot",
    "L5": "Grounded caretaker words",
    "L6": "Open-ended ideas",
    "L7": "Invents hidden quantities, curiosity",
    "L8": "Unifies across fields",
    "L9": "Recursive self-improvement with guarantees",
}
CORE_L0 = ("C1", "C6", "C10", "C11")


def _read_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def _check_files(results):
    candidates = {}
    all_paths = sorted(Path(results).rglob("core_check_seed*.json"))
    for path in all_paths:
        # Seed identity is carried by the filename, as in core_check_seed<N>.json.
        import re
        match = re.search(r"core_check_seed(\d+)\.json$", path.name)
        if not match:
            continue
        seed = int(match.group(1))
        try:
            stamp = path.stat().st_mtime_ns
        except OSError:
            continue
        if seed not in candidates or (stamp, str(path)) > candidates[seed][0]:
            candidates[seed] = ((stamp, str(path)), path)
    return {seed: _read_json(pair[1]) for seed, pair in sorted(candidates.items())}


def _evidence_files(results):
    folder = Path(results) / "ladder"
    paths = sorted(folder.rglob("*.json")) if folder.exists() else []
    entries = []
    for path in paths:
        payload = _read_json(path)
        if isinstance(payload, list):
            entries.extend((entry, path) for entry in payload if isinstance(entry, dict))
    return entries


def _detail(checks, name, key, default=None):
    item = checks.get(name, {})
    return item.get("detail", {}).get(key, default)


def _passed(checks, name):
    return checks.get(name, {}).get("pass") is True


def _fmt_num(value):
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def build_ladder(results, generated=None):
    checks_by_seed = _check_files(results)
    evidence = _evidence_files(results)
    rows = {}

    def _count(v):
        """core_check writes the accepted forgeries as a list of names; older files may hold a number."""
        return len(v) if isinstance(v, (list, tuple)) else (v or 0)

    seeds = list(checks_by_seed.values())
    nseeds = len(seeds)

    # L0
    holders = [s for s in seeds if all(_passed(s, name) for name in CORE_L0)]
    c6_wrong = sum((_detail(s, "C6", "sure_and_wrong", 0) or 0) for s in seeds)
    c11_forgery = sum(_count(_detail(s, "C11", "forgeries_accepted", 0)) for s in seeds)
    coverages = [_detail(s, "C1", "coverage") for s in seeds]
    coverages = [v for v in coverages if isinstance(v, (int, float))]
    metrics0 = f"holders {len(holders)}/{nseeds}; C6 sure_and_wrong {c6_wrong}; C11 forgeries_accepted {c11_forgery}"
    if coverages:
        metrics0 += f"; C1 coverage { _fmt_num(min(coverages))}-{_fmt_num(max(coverages))}"
    status0 = ("pass" if len(holders) == nseeds and nseeds >= 10 else
               "partial" if holders else "fail" if nseeds else "not measured")

    c8_present = [s for s in seeds if "C8" in s]
    c8_pass = [s for s in c8_present if _passed(s, "C8")]
    alarm_rates = [_detail(s, "C8", "alarm_rate") for s in c8_present]
    alarm_rates = [v for v in alarm_rates if isinstance(v, (int, float))]
    eligible_sum = sum((_detail(s, "C8", "eligible_worlds", 0) or 0) for s in seeds)
    noise_sum = sum((_detail(s, "C1", "noise_worlds_alarms", 0) or 0) for s in seeds)
    metrics2 = f"C8 alarm_rate min { _fmt_num(min(alarm_rates)) if alarm_rates else 'n/a'}; eligible_worlds {eligible_sum}; C1 noise_worlds_alarms {noise_sum}; C8 passes {len(c8_pass)}/{len(c8_present)}"
    status2 = ("pass" if c8_present and len(c8_pass) == len(seeds) and noise_sum == 0 and nseeds >= 10 else
               "partial" if c8_pass else "fail" if c8_present else "not measured")

    evidence_by_rung = {rung: [] for rung in CAPABILITIES}
    for entry, path in evidence:
        rung = entry.get("rung")
        if rung in evidence_by_rung:
            evidence_by_rung[rung].append((entry, path))

    for rung in CAPABILITIES:
        if rung == "L0":
            status, metrics = status0, metrics0
        elif rung == "L2":
            status, metrics = status2, metrics2
        else:
            items = evidence_by_rung[rung]
            if items:
                passed = sum(entry.get("pass") is True for entry, _ in items)
                status = "pass" if passed == len(items) else "partial" if passed else "fail"
                metrics = "; ".join(
                    f"{entry.get('metric', '?')}={entry.get('value', '?')} (bar {entry.get('bar', '?')})"
                    for entry, _ in items
                )
            else:
                status, metrics = "not measured", "—"
        items = evidence_by_rung[rung]
        if rung in ("L0", "L2") and status == "pass" and any(e.get("pass") is False for e, _ in items):
            status = "partial"
        source_paths = sorted({str(path.relative_to(results)) for _, path in items})
        if rung == "L0" or rung == "L2":
            source_paths += sorted({str(p.relative_to(results)) for p in _selected_check_paths(results)})
        rows[rung] = {
            "rung": rung,
            "capability": CAPABILITIES[rung],
            "evidence": ", ".join(source_paths) if source_paths else "—",
            "metrics": metrics,
            "status": status,
        }

    now = generated or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    check_count = len(checks_by_seed)
    evidence_count = len(evidence)
    table = [
        "| Rung | Capability | Evidence (files) | Metrics | Status |",
        "|---|---|---|---|---|",
    ]
    for rung in CAPABILITIES:
        row = rows[rung]
        cells = [row[k].replace("|", "\\|").replace("\n", " ") for k in ("rung", "capability", "evidence", "metrics", "status")]
        table.append("| " + " | ".join(cells) + " |")
    output = "\n".join(table) + f"\n\nGenerated {now} from {check_count} check files and {evidence_count} evidence files."
    return rows, output, check_count, evidence_count


def _selected_check_paths(results):
    paths = sorted(Path(results).rglob("core_check_seed*.json"))
    selected = {}
    import re
    for path in paths:
        match = re.search(r"core_check_seed(\d+)\.json$", path.name)
        if match:
            seed = int(match.group(1))
            stamp = path.stat().st_mtime_ns
            if seed not in selected or (stamp, str(path)) > selected[seed][0]:
                selected[seed] = ((stamp, str(path)), path)
    return [v[1] for _, v in sorted(selected.items())]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="core-results")
    parser.add_argument("--out", default="core-results/LADDER.md")
    args = parser.parse_args(argv)
    _, output, _, _ = build_ladder(args.results)
    print(output)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(output + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
