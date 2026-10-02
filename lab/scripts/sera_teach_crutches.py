"""S24 bounded dev experiment: one child at a time, immutable training snapshots.
PASS is only the frozen development gate, and never authorizes retirement.
The parent uses only stdlib; each life/probe starts in a fresh interpreter.
"""
import argparse
import dataclasses
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STATUSES = ("proven", "failed", "censored in progress", "not reached")
ARM_NAMES = ("U+", "U-", "T+", "T-")
RECHECK_RAILS = ("rail: wind 1", "rail: spring 1", "rail: stiff 1",
                 "rail: wind 2", "rail: spring 2", "rail: stiff 2")
THREADS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMBA_NUM_THREADS")
TESTS = ("tests/sera/test_crutches.py", "tests/sera/test_s06.py", "tests/sera/test_teach_crutches.py")


def normalize(value):
    """Stable full input serialization, never an object's address."""
    if dataclasses.is_dataclass(value):
        return normalize(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (tuple, list)):
        return [normalize(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return [normalize(v) for v in sorted(value, key=repr)]
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if hasattr(value, "tolist"):
        return normalize(value.tolist())
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"no stable serialization for {type(value).__name__}")


def encoded(value):
    return json.dumps(normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(normalize(value), indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def package_files():
    paths = []
    for directory in ("sera", "ccops5"):
        paths.extend((ROOT / directory).rglob("*.py"))
    paths.extend((ROOT / "scripts" / "sera_one.py", Path(__file__).resolve()))
    paths.extend(ROOT / p for p in TESTS)
    paths.extend(ROOT / p for p in ("requirements.txt", "requirements-sera.lock", "pyproject.toml"))
    return {p.relative_to(ROOT).as_posix(): file_hash(p) for p in sorted(set(paths)) if p.is_file()}


def book_files(book):
    if not book:
        return {}
    directory = Path(book).resolve()
    if not (directory / "data.noun").is_file():
        raise ValueError("the requested dictionary has no data.noun")
    return {p.relative_to(directory).as_posix(): file_hash(p) for p in sorted(directory.rglob("*")) if p.is_file()}


def child_env(halving):
    env = os.environ.copy()
    env.update(PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1",
               CCOPS5_SHAPES="library", CCOPS5_CLAIM="functional", CCOPS5_BAND="claim",
               SERA_KNOBS="ONE_FIELD=0", SERA_CRUTCH_ON="teach_rechecking",
               SERA_CRUTCH_OFF="" if halving else "convince_halving")
    for name in THREADS:
        env[name] = "1"
    return env


def run_child(argv, seconds, log, env):
    """Always reap before returning; a second SERA child cannot overlap."""
    if seconds <= 0:
        return dict(returncode=None, timeout=True, wall=0.0)
    start = time.monotonic()
    with Path(log).open("w", encoding="utf-8") as stream:
        proc = subprocess.Popen([sys.executable] + list(argv), cwd=ROOT, env=env,
                                stdout=stream, stderr=subprocess.STDOUT)
        try:
            proc.wait(timeout=seconds)
            timeout = False
        except subprocess.TimeoutExpired:
            timeout = True
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        except BaseException:
            proc.kill()
            proc.wait()
            raise
    return dict(returncode=proc.returncode, timeout=timeout, wall=time.monotonic() - start)


def schedule(seeds, stage):
    """Frozen names/builders: six repeated diagnostic rails, then the complete
    sera_one.teaching order for each seed. Dev seeds are not fresh evidence."""
    from sera_one import teaching
    out = []
    for seed in seeds:
        ordinary = teaching(seed)
        by_name = dict(ordinary)
        entries = [(name, by_name[name]) for name in RECHECK_RAILS] + ordinary
        for index, (name, build) in enumerate(entries):
            out.append((dict(id=f"{stage}:s{seed}:{index:03d}", seed=seed, name=name,
                             builder="sera_one.teaching", index=index), build))
    return out


def withhold_teacher(task):
    """Keep observations/examples/questions/audit; remove labels and worked advice."""
    task.words = []
    if hasattr(task, "_worked"):
        task._worked = {}
    if hasattr(task, "_worked_of"):
        task._worked_of = {}
    if hasattr(task, "worked"):
        task.worked = lambda x: None
    return task


def input_record(task):
    visible = dict(subject=task.subject, form=task.form, inputs=task.inputs, out=task.out,
                   words=task.words)
    if task.form == "strengths":
        visible.update(sigma=task.sigma, throws=task.throws)
        observer = dict(spec=task.world.spec, held_out=task.world.held_out)
    else:
        visible.update(data=task.data, pool=task.pool, probes=task.probes())
        observer = dict(pool_answers=[task._y(x) for x in task.pool])
    # The runner owns observer data; none is installed in the Field.
    return normalize(dict(visible=visible, observer=observer))


def mask_advice(field):
    """Only the three fading advice stores. Own evidence, concepts and vocabulary survive."""
    field.loop.taught = {}
    field.methods.taught = {}
    field.steps.At[...] = 0
    field.steps.bt[...] = 0


def field_audit(field):
    import numpy as np
    from sera import tasks as TS
    def statistics(rows):
        return digest({repr(k): [A, b] for k, (A, b) in sorted(rows.items(), key=lambda kv: repr(kv[0]))})
    idx = field.loop.feature_names.index("shown")
    own = sum(float(A[idx, idx]) for rows in field.loop.kinds.values() for A, b in rows.values())
    own_y = sum(abs(float(b[idx])) for rows in field.loop.kinds.values() for A, b in rows.values())
    taught = sum(float(np.linalg.norm(A) + np.linalg.norm(b))
                 for rows in field.loop.taught.values() for A, b in rows.values())
    return dict(vocabulary=digest(dict(TS.VOCAB)), concepts=digest(field.concepts),
                standing=digest(field.standing), account=field.account(),
                knowledge=digest([list(field.understood), list(field.possibilities),
                                  {k: v for k, v in field.lexicon.__dict__.items() if k != "_rng"},
                                  field.lexicon._rng.bit_generator.state]),
                loop_own=digest({k: statistics(v) for k, v in sorted(field.loop.kinds.items())}),
                method_own=statistics(field.methods.stats), step_own=digest([field.steps.A, field.steps.b]),
                loop_taught_norm=taught, method_taught=statistics(field.methods.taught),
                step_taught_norm=float(np.linalg.norm(field.steps.At) + np.linalg.norm(field.steps.bt)),
                features=list(field.loop.feature_names), schema=field.loop.feature_schema,
                shown_own_precision=own, shown_own_return=own_y)


def reload_checkpoint(field, path):
    from sera import phi as PH
    field.save(path)
    before = field_audit(field)
    after = field_audit(PH.Field.load(path))
    if before != after:
        raise RuntimeError("save/reload audit differs")
    return before


def verify_frozen(manifest):
    if package_files() != manifest["package_files"]:
        raise RuntimeError("source changed after manifest freeze")
    if book_files(manifest["book"]) != manifest["book_files"]:
        raise RuntimeError("dictionary changed after manifest freeze")


def prepare(config, out):
    from sera import crutches as CR, dictionary as DICT, one as ONE, phi as PH, talk as TK
    TK.BOOK = DICT.load(config["book"])
    package = package_files()
    entries, inputs = {}, {}
    for stage, seeds in (("teach", config["teach_seeds"]), ("eval", [config["seed"]])):
        rows = []
        for descriptor, build in schedule(seeds, stage):
            task = build()
            if stage == "eval":
                withhold_teacher(task)
            identity = input_record(task)
            inputs[descriptor["id"]] = identity
            rows.append(dict(descriptor, input_digest=digest(identity)))
        entries[stage] = rows
    packages = {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()}
    manifest = dict(version=1, protocol="S24-dev-rechecking", config=config, entries=entries,
                    package_files=package, package_digest=digest(package), book=config["book"],
                    book_files=book_files(config["book"]), python=sys.version,
                    packages=dict(sorted(packages.items())), settings=CR.settings(),
                    one_field=ONE.ONE_FIELD, input_identities="inputs.json",
                    rng="Sera(seed=3); live default_rng([seed,7,Field.tasks]); fresh builder per entry",
                    verdict_policy=dict(reproof_cost_ratio=1.25, reproof_extra_seconds=30,
                                        require_strict_waste_reduction=True),
                    dev_seeds=True, retirement_authorized=False)
    write_json(out / "inputs.json", inputs)
    write_json(out / "manifest.json", manifest)
    field = PH.Field(config["seed"])
    audit = reload_checkpoint(field, out / "newborn.pkl")
    write_json(out / "newborn.json", dict(audit=audit, sha256=file_hash(out / "newborn.pkl")))
    for relative in package:
        target = out / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    return 0


class Observer:
    """Wrap the public world interface without changing its result."""
    def __init__(self, task, emit):
        self.emit = emit
        self.since, self.locations, self.repeats, self.short = 0, {}, 0, 0.0
        self.region = None
        self.accepted_keys = set()
        self.metrics = dict(pushes=0, reports=0, rechecks=0, opportunities=0, demonstrations=0,
                            repeats=0, unproductive_repeats=0, report_wall=0.0, report_cpu=0.0,
                            checker_failures=0, accepted_claims=0, accepted_new_proofs=0)
        act, verify = task.act, task.verify

        def observed_act(action):
            result = act(action)
            key = digest(action)
            self.repeats += int(key in self.locations)
            self.locations[key] = self.locations.get(key, 0) + 1
            self.since += 1
            self.metrics["pushes"] += 1
            self.emit("push", action=normalize(action), since_report=self.since, judge_where=self.region)
            return result

        def observed_verify(*args, **kwargs):
            from sera import one as ONE
            start, cpu = time.monotonic(), time.process_time()
            self.emit("report_start", since_report=self.since, claim=normalize(args[0]))
            result = verify(*args, **kwargs)
            wall, cost = time.monotonic() - start, time.process_time() - cpu
            ok, cert, why = result
            rail = task.form == "strengths"
            checker_failure = rail and bool(getattr(cert, "accepted", False)) and not ok
            if rail:
                band, eps = getattr(cert, "band", None), getattr(cert, "eps", None)
                short = 0.0 if ok else ONE.S_MISS if why and "something else is here" in why else (
                    5.0 if band is None or not math.isfinite(band) else
                    ONE.BAND_NATS * max(math.log(band / eps), 0.0))
            else:
                band, eps, short = None, None, 0.0
            self.metrics["reports"] += 1
            self.metrics["rechecks"] += int(self.since > 0 and self.short > 0)
            self.metrics["repeats"] += self.repeats
            if rail and self.short > 0 and not ok and short >= self.short:
                self.metrics["unproductive_repeats"] += self.repeats
            self.metrics["report_wall"] += wall
            self.metrics["report_cpu"] += cost
            self.metrics["checker_failures"] += int(checker_failure)
            self.metrics["accepted_claims"] += int(bool(ok))
            claim_key = digest([args[0], len(task.throws) if rail else None])
            new_proof = bool(ok) and claim_key not in self.accepted_keys
            if new_proof:
                self.accepted_keys.add(claim_key)
                self.metrics["accepted_new_proofs"] += 1
            since, repeats = self.since, self.repeats
            self.since, self.locations, self.repeats, self.short = 0, {}, 0, short
            self.emit("report", accepted=bool(ok), reason=why, band=band, eps=eps, short=short,
                      since_report=since, repeats=repeats, checker_failure=checker_failure,
                      new_proof=new_proof, wall=wall, cpu=cost)
            return result
        task.act, task.verify = observed_act, observed_verify

    def scheduling(self, event):
        self.region = event.get("judge_where")
        opportunity = event["pushes_since_report"] > 0 and self.short > 0 and "prove" in event["available"]
        self.metrics["opportunities"] += int(opportunity)
        self.metrics["demonstrations"] += int(opportunity and event["advice"] == ["prove"])
        self.emit("schedule", **event)

    def finish(self):
        return dict(self.metrics, pending_pushes=self.since, pending_repeats=self.repeats)


def worker(config, out, stage, arm, source, seconds, masked):
    from sera import crutches as CR, dictionary as DICT, one as ONE, phi as PH, talk as TK
    manifest = read_json(out / "manifest.json")
    verify_frozen(manifest)
    TK.BOOK = DICT.load(config["book"])
    target = out / arm
    target.mkdir()
    field = PH.Field.load(source)
    source_hash = file_hash(source)
    initial = field_audit(field)
    if masked:
        mask_advice(field)
    cloned = field_audit(field)
    immutable = ("vocabulary", "concepts", "standing", "knowledge", "loop_own", "method_own", "step_own")
    if any(initial[k] != cloned[k] for k in immutable):
        raise RuntimeError("mask changed own evidence or knowledge")
    teaching = stage == "teach"
    advice = teaching and arm == "T"
    sera = ONE.Sera(config["seed"], field)
    settings = dict(CR.settings(), teaching=teaching, recheck_advice=advice, teacher_priors_masked=masked,
                    one_field=ONE.ONE_FIELD, thread_limits={k: os.environ[k] for k in THREADS})
    audit = reload_checkpoint(field, target / "input.pkl")
    rows = [dict(d, status="not reached") for d in manifest["entries"][stage]]
    result = dict(arm=arm, stage=stage, settings=settings, source_sha256=source_hash, initial=initial,
                  cloned=audit, rows=rows, error=None, completed=False)
    write_json(target / "result.json", result)
    deadline = time.monotonic() + seconds
    builders = schedule(config["teach_seeds"] if teaching else [config["seed"]], stage)
    events = (target / "events.jsonl").open("w", encoding="utf-8")
    active_id = None
    active_observer = None

    def emit(kind, **data):
        events.write(json.dumps(normalize(dict(kind=kind, id=active_id, t=time.monotonic(), data=data))) + "\n")
        events.flush()
        if active_observer is not None and kind in ("push", "report", "schedule"):
            # Survive an external interruption with the observations that actually returned.
            rows[index]["metrics"] = active_observer.finish()
            write_json(target / "progress.json", dict(
                id=active_id, metrics=rows[index]["metrics"],
                actual_input_digest=rows[index].get("actual_input_digest")))

    try:
        for index, (descriptor, build) in enumerate(builders):
            if time.monotonic() >= deadline:
                break
            active_id = descriptor["id"]
            row = rows[index]
            row["status"], row["started"] = "censored in progress", time.time()
            write_json(target / "result.json", result)
            task = build()
            if not teaching:
                withhold_teacher(task)
            actual = digest(input_record(task))
            if actual != row["input_digest"]:
                raise RuntimeError("full world input differs from frozen manifest")
            row["actual_input_digest"] = actual
            observer = Observer(task, emit)
            active_observer = observer
            allowance = min(config["world_seconds"], max(0.0, deadline - time.monotonic() - 5))
            if allowance <= 0:
                break
            ONE.MAX_WALL = allowance
            emit("start", settings=settings, allowance=allowance)
            before = field_audit(sera.field)
            start = time.monotonic()
            rec = sera.live(task, teaching=teaching, recheck_advice=advice,
                            on_schedule=observer.scheduling, on_say=lambda speech: emit("say", **speech))
            elapsed = time.monotonic() - start
            row.update(status="proven" if rec["proven"] else
                       "censored in progress" if elapsed >= allowance else "failed",
                       world_wall=elapsed, record=rec, metrics=observer.finish())
            after = reload_checkpoint(sera.field, target / "field.pkl")
            row["advice_fade"] = dict(before=before["loop_taught_norm"], after=after["loop_taught_norm"])
            row["advice_fade"]["per_task_factor"] = PH.TAUGHT_FADE
            row["field_after"] = after
            row["checkpoint_sha256"] = file_hash(target / "field.pkl")
            write_json(target / f"world-{index:03d}.json", row)
            write_json(target / "result.json", result)
            emit("end", status=row["status"], metrics=row["metrics"])
            if rec.get("verdict") == "SURE AND WRONG" or row["metrics"]["checker_failures"]:
                result["error"] = "tripwire: incorrect accepted claim or checker failure"
                break
        result["completed"] = all(r["status"] in ("proven", "failed") for r in rows)
        result["final"] = reload_checkpoint(sera.field, target / "field.pkl")
        result["output_sha256"] = file_hash(target / "field.pkl")
        if file_hash(source) != source_hash:
            raise RuntimeError("training/input snapshot changed")
        write_json(target / "result.json", result)
        return 3 if result["error"] else 0
    except BaseException:
        result["error"] = traceback.format_exc()
        write_json(target / "result.json", result)
        raise
    finally:
        events.close()


def totals(result):
    names = ("unproductive_repeats", "pending_repeats", "reports", "rechecks", "opportunities",
             "demonstrations", "report_wall", "report_cpu", "checker_failures", "accepted_claims",
             "accepted_new_proofs")
    return {k: sum(row.get("metrics", {}).get(k, 0) for row in result.get("rows", [])) for k in names}


def verdict(manifest, results):
    """Missing retained item is FAIL; incomplete coverage or learning is INCOMPLETE."""
    failed, incomplete = [], []
    expected = manifest["entries"]["eval"]
    for name in ARM_NAMES:
        arm = results.get(name)
        if not arm:
            incomplete.append(f"{name}: missing arm")
            continue
        rows = arm.get("rows", [])
        if [r["id"] for r in rows] != [r["id"] for r in expected]:
            failed.append(f"{name}: manifest identities/order differ")
            continue
        settings = arm.get("settings", {})
        if not settings.get("teacher_priors_masked") or settings.get("teaching"):
            failed.append(f"{name}: advice was not masked or evaluation was taught")
        effective = settings.get("crutches_effective", {})
        if effective.get("convince_halving") != name.endswith("+") or not effective.get("teach_rechecking"):
            failed.append(f"{name}: switches differ from the protocol")
        if settings.get("one_field") != 0:
            failed.append(f"{name}: ONE_FIELD must be off")
        for row, entry in zip(rows, expected):
            if row.get("input_digest") != entry["input_digest"] or (
                    row.get("actual_input_digest", entry["input_digest"]) != entry["input_digest"]):
                failed.append(f"{name}:{row['id']}: full input differs")
            if row["status"] not in STATUSES:
                failed.append(f"{name}:{row['id']}: invalid status")
            if row["status"] in STATUSES[2:]:
                incomplete.append(f"{name}:{row['id']}: {row['status']}")
            if row.get("record", {}).get("verdict") == "SURE AND WRONG":
                failed.append(f"{name}:{row['id']}: incorrect accepted claim")
        if totals(arm)["checker_failures"]:
            failed.append(f"{name}: checker failure")
        if arm.get("error"):
            failed.append(f"{name}: child error")
    for teacher in ("U", "T"):
        plus, minus = results.get(teacher + "+"), results.get(teacher + "-")
        if plus and minus and plus.get("source_sha256") != minus.get("source_sha256"):
            failed.append(f"{teacher}: pair did not clone the same Field")
    if "T+" in results and "T-" in results:
        minus = {r["id"]: r for r in results["T-"]["rows"]}
        for row in results["T+"]["rows"]:
            if row["status"] == "proven" and minus.get(row["id"], {}).get("status") != "proven":
                failed.append(f"T- lost required T+ item {row['id']}")
    for name in ("U", "T"):
        taught = results.get(name, {})
        if not taught or not taught.get("final"):
            incomplete.append(f"{name}: missing completed training checkpoint audit")
        if taught.get("error") or totals(taught)["checker_failures"] or any(
                r.get("record", {}).get("verdict") == "SURE AND WRONG" for r in taught.get("rows", [])):
            failed.append(f"{name}: training tripwire/child error")
    taught = results.get("T", {})
    train = totals(taught)
    if not train["opportunities"] or not train["demonstrations"] or not train["rechecks"]:
        incomplete.append("T: no real demonstrated/experienced recheck opportunity")
    audit = taught.get("final", {})
    if audit.get("shown_own_precision", 0) <= 0 or audit.get("shown_own_return", 0) <= 0:
        incomplete.append("T: no usable own evidence at shown>0")
    comparisons = {}
    if all(k in results for k in ARM_NAMES):
        measures = {k: totals(results[k]) for k in ARM_NAMES}
        policy = manifest["verdict_policy"]
        base, replacement = measures["T+"], measures["T-"]
        if replacement["unproductive_repeats"] >= base["unproductive_repeats"]:
            incomplete.append("T-: no measured reduction of unproductive repeated pushes")
        if replacement["pending_repeats"]:
            incomplete.append("T-: repeated pushes with no later report")
        if not replacement["rechecks"]:
            incomplete.append("T-: no autonomous recheck")
        if replacement["report_wall"] > (base["report_wall"] * policy["reproof_cost_ratio"]
                                          + policy["reproof_extra_seconds"]):
            failed.append("T-: excessive report cost")
        for control in ("U-", "U+"):
            control_proven = {r["id"] for r in results[control]["rows"] if r["status"] == "proven"}
            replacement_proven = {r["id"] for r in results["T-"]["rows"] if r["status"] == "proven"}
            comparisons[control + "_vs_T-"] = dict(lost=sorted(control_proven - replacement_proven),
                                                  gained=sorted(replacement_proven - control_proven))
        if (not comparisons["U-_vs_T-"]["gained"] and
                measures["T-"]["unproductive_repeats"] >= measures["U-"]["unproductive_repeats"]):
            incomplete.append("U- already matches T-: teaching benefit unresolved; investigate removal")
        comparisons["metrics"] = measures
    return dict(verdict="FAIL" if failed else "INCOMPLETE" if incomplete else "PASS",
                failures=failed, incomplete=incomplete, comparisons=comparisons,
                development_only=True, retirement_authorized=False)


def collect(out, arm):
    path = out / arm / "result.json"
    if not path.exists():
        return None
    result = read_json(path)
    progress_path = out / arm / "progress.json"
    if progress_path.exists():
        progress = read_json(progress_path)
        for row in result["rows"]:
            if row["id"] == progress["id"] and row["status"] == "censored in progress":
                row["metrics"] = progress["metrics"]
                row["actual_input_digest"] = progress["actual_input_digest"]
                # A returned report is an observation, not a completed world/proof result.
    return result


def archive(out):
    files = [p for p in sorted(out.rglob("*")) if p.is_file() and p.name != "checksums.json"]
    write_json(out / "checksums.json", {p.relative_to(out).as_posix(): file_hash(p) for p in files})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--experiment", choices=("convince",), default="convince")
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--teach-seeds", default="1,2")
    ap.add_argument("--one-field", type=int, choices=(0,), default=0)
    ap.add_argument("--teacher-priors", choices=("zero",), default="zero")
    ap.add_argument("--train-seconds", type=float, default=1800)
    ap.add_argument("--eval-seconds", type=float, default=3300)
    ap.add_argument("--probe-seconds", type=float, default=150)
    ap.add_argument("--world-seconds", type=float, default=180)
    ap.add_argument("--wall-seconds", type=float, default=21600)
    ap.add_argument("--book", default=os.environ.get("SERA_BOOK"))
    ap.add_argument("--worker", choices=("prepare", "teach", "eval"), help=argparse.SUPPRESS)
    ap.add_argument("--arm", help=argparse.SUPPRESS)
    ap.add_argument("--source", help=argparse.SUPPRESS)
    ap.add_argument("--seconds", type=float, help=argparse.SUPPRESS)
    ap.add_argument("--masked", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    out = Path(args.out).resolve()
    if args.worker:
        config = read_json(out / "config.json")
        return prepare(config, out) if args.worker == "prepare" else worker(
            config, out, args.worker, args.arm, Path(args.source), args.seconds, args.masked)
    seeds = [int(s) for s in args.teach_seeds.split(",")]
    if seeds != [1, 2] or args.seed != 3:
        ap.error("this first development batch uses teaching 1,2 and evaluation 3")
    for key in ("train_seconds", "eval_seconds", "probe_seconds", "world_seconds", "wall_seconds"):
        if not math.isfinite(getattr(args, key)) or getattr(args, key) <= 0:
            ap.error(f"{key} must be finite and positive")
    if args.train_seconds > 1800 or args.eval_seconds > 3300 or args.probe_seconds > 150:
        ap.error("first batch permits at most 30m/life, 55m/arm and 2.5m/probe (eight probes)")
    if args.wall_seconds > 21600:
        ap.error("the first batch cannot exceed six hours")
    if out.exists():
        ap.error("output already exists; this runner never resumes or skips worlds")
    out.mkdir(parents=True)
    start = time.monotonic()
    # Last thirty minutes belong to archive/overrun, not another evaluation.
    deadline = start + args.wall_seconds - min(1800, args.wall_seconds / 12)
    config = dict(seed=args.seed, teach_seeds=seeds, book=str(Path(args.book).resolve()) if args.book else None,
                  train_seconds=args.train_seconds, eval_seconds=args.eval_seconds, probe_seconds=args.probe_seconds,
                  world_seconds=args.world_seconds, wall_seconds=args.wall_seconds, one_field=0)
    write_json(out / "config.json", config)
    summary = dict(verdict="INCOMPLETE", failures=[], incomplete=[], processes={}, results={})
    try:
        uptime = Path("/proc/uptime")
        if not uptime.exists():
            raise RuntimeError("Colab/Linux /proc/uptime is required for the batch")
        summary["uptime_start"] = uptime.read_text().strip()
        preflight_end = min(deadline, start + 1200)
        for index, test in enumerate(TESTS):
            env = child_env(False)
            env["SERA_CRUTCH_ON"], env["SERA_CRUTCH_OFF"] = "", ""
            run = run_child(["-m", "pytest", "-q", "-p", "no:cacheprovider", test],
                            min(180, preflight_end - time.monotonic()), out / f"preflight-{index}.log", env)
            summary["processes"][test] = run
            if run["returncode"] != 0 or run["timeout"]:
                summary["incomplete"].append(f"preflight failed or exceeded budget: {test}")
                return 2
        script = str(Path(__file__).resolve())

        def launch(stage, arm, source=None, seconds=0, masked=False):
            capacity = min(seconds, deadline - time.monotonic() - 5)
            argv = [script, "--out", str(out), "--worker", stage]
            if stage != "prepare":
                argv += ["--arm", arm, "--source", str(source), "--seconds", str(max(0, capacity - 5))]
                if masked:
                    argv += ["--masked"]
            run = run_child(argv, capacity, out / f"{arm}.log", child_env(arm.endswith("+")))
            summary["processes"][arm] = run
            if run["timeout"]:
                summary["incomplete"].append(f"{arm}: external deadline; no proof result manufactured")
            elif run["returncode"] != 0:
                summary["failures"].append(f"{arm}: child exited {run['returncode']}")
            return run

        preparation = launch("prepare", "prepare", seconds=min(600, preflight_end - time.monotonic()))
        if preparation["returncode"] != 0 or preparation["timeout"]:
            return 1 if summary["failures"] else 2
        manifest = read_json(out / "manifest.json")
        for arm in ("U", "T"):
            run = launch("teach", arm, out / "newborn.pkl", args.train_seconds)
            summary["results"][arm] = collect(out, arm)
            if run["returncode"] not in (0, None) and not run["timeout"]:
                return 1
        for arm in ARM_NAMES:
            source = out / arm[0] / "field.pkl"
            if not source.exists():
                summary["incomplete"].append(f"{arm}: training checkpoint unavailable")
                continue
            run = launch("eval", arm, source, args.eval_seconds, masked=True)
            result = collect(out, arm)
            if result:
                summary["results"][arm] = result
            if run["returncode"] == 3:
                return 1
        # Matched short masked/unmasked probes from original snapshots, never main arm outputs.
        for arm in ARM_NAMES:
            source = out / arm[0] / "field.pkl"
            if source.exists():
                for masked in (True, False):
                    probe = arm + ("-masked" if masked else "-unmasked")
                    capacity = min(args.probe_seconds, deadline - time.monotonic() - 5)
                    argv = [script, "--out", str(out), "--worker", "eval", "--arm", probe,
                            "--source", str(source), "--seconds", str(max(0, capacity - 5))]
                    if masked:
                        argv += ["--masked"]
                    run = run_child(argv, capacity, out / f"{probe}.log", child_env(arm.endswith("+")))
                    summary["processes"][probe] = run
                    result = collect(out, probe)
                    summary.setdefault("probes", {})[probe] = result
                    if run["returncode"] == 3:
                        summary["failures"].append(f"{probe}: safety tripwire")
                        return 1
                    if run["timeout"] or run["returncode"] != 0 or result is None:
                        summary["incomplete"].append(f"{probe}: probe incomplete")
        summary["probe_comparisons"] = {}
        for arm in ARM_NAMES:
            probes = summary.get("probes", {})
            masked, unmasked = probes.get(arm + "-masked"), probes.get(arm + "-unmasked")
            if masked and unmasked:
                if masked["source_sha256"] != unmasked["source_sha256"]:
                    summary["failures"].append(f"{arm}: probe sources differ")
                masked_rows = {r["id"]: r for r in masked["rows"]}
                unmasked_rows = {r["id"]: r for r in unmasked["rows"]}
                if set(masked_rows) != set(unmasked_rows):
                    summary["failures"].append(f"{arm}: probe manifests differ")
                ids = sorted(set(masked_rows) & set(unmasked_rows))
                summary["probe_comparisons"][arm] = dict(
                    per_world=[dict(id=k, masked=masked_rows[k]["status"], unmasked=unmasked_rows[k]["status"])
                               for k in ids],
                    masked_metrics=totals(masked), unmasked_metrics=totals(unmasked))
        decision = verdict(manifest, {k: v for k, v in summary["results"].items() if v})
        summary["comparisons"] = decision["comparisons"]
        summary["failures"] += decision["failures"]
        summary["incomplete"] += decision["incomplete"]
        summary["verdict"] = ("FAIL" if summary["failures"] else
                              "INCOMPLETE" if summary["incomplete"] else "PASS")
        return {"PASS": 0, "INCOMPLETE": 2, "FAIL": 1}[summary["verdict"]]
    except BaseException:
        summary["incomplete"].append(traceback.format_exc())
        return 1 if summary["failures"] else 2
    finally:
        summary.update(wall=time.monotonic() - start, development_only=True, retirement_authorized=False)
        if summary["failures"]:
            summary["verdict"] = "FAIL"
        write_json(out / "verdict.json", summary)
        (out / "summary.txt").write_text(
            summary["verdict"] + " (development gate only; no retirement)\n" +
            "\n".join(summary["failures"] + summary["incomplete"]) +
            f"\nwall {summary['wall']:.1f}s\n", encoding="utf-8")
        archive(out)


if __name__ == "__main__":
    sys.exit(main())
