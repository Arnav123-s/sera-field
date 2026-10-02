"""Short S24 checks. Worlds/searches are stubbed; no long physics certificate is run."""
import copy
import math
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sera import crutches as CR, lang as L, one as O, phi as P, tasks as T
import sera_teach_crutches as R
import test_s06 as S06


@pytest.fixture
def enabled(monkeypatch):
    monkeypatch.setattr(CR, "ON", {"teach_rechecking"})
    monkeypatch.setattr(CR, "OFF", set())


def legacy_loop():
    loop = P.LoopField()
    loop.migrate_features(P.LEGACY_FEATURES)
    del loop.feature_names
    del loop.feature_schema
    d = loop.d
    q = np.random.default_rng(22).normal(size=(d, d))
    A, b = q.T @ q, np.arange(d, dtype=float)
    loop.kinds = {"k": {"prove": [A.copy(), b.copy()]}}
    loop.taught = {"k": {"prove": [2 * A.copy(), 3 * b.copy()]}}
    loop.task = {"prove": [4 * A.copy(), 5 * b.copy()]}
    return loop


def test_migration_preserves_named_cross_terms_and_zero_new_prior(enabled):
    loop = legacy_loop()
    old = copy.deepcopy((loop.kinds, loop.taught, loop.task))
    # Inspect the legacy posterior before expanding (no teacher/default guesses).
    loop.feature_names = P.LEGACY_FEATURES
    mean, covariance = loop.posterior("k", "prove")
    del loop.feature_names
    loop.migrate_features()
    indices = [loop.feature_names.index(name) for name in P.LEGACY_FEATURES]
    new_index = loop.feature_names.index("shown")
    for rows, saved in zip((loop.kinds, loop.taught, loop.task), old):
        current = rows["prove"] if "prove" in rows else rows["k"]["prove"]
        previous = saved["prove"] if "prove" in saved else saved["k"]["prove"]
        assert np.array_equal(current[0][np.ix_(indices, indices)], previous[0])
        assert np.array_equal(current[1][indices], previous[1])
        assert not np.any(current[0][new_index]) and current[1][new_index] == 0
    expanded_mean, expanded_cov = loop.posterior("k", "prove")
    assert np.allclose(expanded_mean[indices], mean)
    assert np.allclose(expanded_cov[np.ix_(indices, indices)], covariance)
    assert expanded_mean[new_index] == 0
    assert expanded_cov[new_index, new_index] == pytest.approx(1 / (P.W_L / loop.prior**2 + 1e-9))
    assert not np.any(expanded_cov[new_index, indices])
    # A reordered named schema must move estimate columns and cross terms, not append blindly.
    saved = copy.deepcopy(loop.kinds)
    loop.migrate_features(tuple(reversed(P.FEATURES)))
    loop.migrate_features(P.FEATURES)
    assert np.array_equal(loop.kinds["k"]["prove"][0], saved["k"]["prove"][0])
    assert np.array_equal(loop.kinds["k"]["prove"][1], saved["k"]["prove"][1])


def test_saved_field_migration_and_live_trace_mapping(enabled, monkeypatch, tmp_path):
    field = P.Field(3)
    field.loop = legacy_loop()
    x = np.arange(field.loop.d, dtype=float)
    field.trace(("loop", "prove", x, 2.0))
    field.migrate_loop()
    mapped = field.traces[0][0][2]
    assert mapped[field.loop.feature_names.index("shown")] == 0
    assert np.array_equal(mapped[[field.loop.feature_names.index(n) for n in P.LEGACY_FEATURES]], x)
    field.loop = legacy_loop()
    path = tmp_path / "old.pkl"
    field.save(path)
    before = R.file_hash(path)
    loaded = P.Field.load(path)
    assert loaded.loop.feature_names == P.FEATURES and loaded.loop.feature_schema == 2
    assert R.file_hash(path) == before  # migration never rewrites the input snapshot
    loaded.save(tmp_path / "new.pkl")
    again = P.Field.load(tmp_path / "new.pkl")
    assert np.array_equal(again.loop.kinds["k"]["prove"][0], loaded.loop.kinds["k"]["prove"][0])
    monkeypatch.setattr(CR, "OFF", {"teach_rechecking"})
    disabled = P.Field.load(tmp_path / "new.pkl")
    assert disabled.loop.feature_names == P.FEATURES
    assert np.array_equal(disabled.loop.kinds["k"]["prove"][0], loaded.loop.kinds["k"]["prove"][0])
    bad = legacy_loop()
    bad.d += 1
    with pytest.raises(ValueError, match="unknown dimension"):
        bad.migrate_features()


def test_defaults_keep_legacy_rng_draws_and_values(monkeypatch):
    monkeypatch.setattr(CR, "ON", set())
    monkeypatch.setattr(CR, "OFF", set())
    loop = P.LoopField()
    assert loop.d == len(P.LEGACY_FEATURES)
    moment = dict(doubt=.7, tension=.4, steps=1., shown=999.)
    est = {fac: i / 10 for i, fac in enumerate(P.FACULTIES)}
    legacy_x = np.asarray([1.] + [moment.get(n, 0.) for n in P.LEGACY_MOMENT[1:]] +
                          [est[f] for f in P.FACULTIES])
    reference, actual = np.random.default_rng(88), np.random.default_rng(88)
    draws = {}
    for fac in P.FACULTIES:
        A0 = np.eye(loop.d) / loop.prior**2
        m0 = np.zeros(loop.d)
        m0[P.LEGACY_FEATURES.index("est_" + fac)] = 1.
        cov = np.linalg.inv(P.W_L * A0 + 1e-9 * np.eye(loop.d))
        mean = cov @ (P.W_L * A0 @ m0)
        w = reference.multivariate_normal(mean, (cov + cov.T) / 2)
        draws[fac] = (float(w @ legacy_x), float(mean @ legacy_x))
    order = sorted(draws, key=lambda f: (-draws[f][0], f))
    expected = [f for f in order if draws[f][0] > 0][:P.MAX_AT_ONCE] or order[:1]
    if "leave" in expected and expected[0] != "leave":
        expected.remove("leave")
    if expected and expected[0] == "leave":
        expected = ["leave"]
    config, values = loop.choose("k", moment, est, set(P.FACULTIES), actual)
    assert config == expected
    assert values == draws
    assert actual.bit_generator.state == reference.bit_generator.state
    assert np.array_equal(loop.features(moment, est, "prove"), legacy_x)
    assert not CR.on("teach_rechecking") and CR.on("convince_halving")


def test_switch_enable_names_are_validated_and_off_has_priority(enabled, monkeypatch):
    monkeypatch.setenv("SERA_CRUTCH_ON", "teach_rechecking")
    assert CR._on() == {"teach_rechecking"}
    monkeypatch.setenv("SERA_CRUTCH_ON", "unknown")
    with pytest.raises(ValueError):
        CR._on()
    monkeypatch.setattr(CR, "OFF", {"teach_rechecking"})
    assert not CR.on("teach_rechecking") and CR.on("convince_halving")


def test_teacher_only_advice_and_natural_fade(enabled):
    moment = dict(proven=0, misfit=0, doubt=0)
    available = {"convince", "ask", "prove", "imagine"}
    st = dict(teaching=True, recheck_advice=True, pushes_since_report=1, judge_short=8,
              level=0, explored=0, none_fit=False)
    assert O.Sera.teacher_way(moment, available, st, ("closer",)) == ["prove"]
    for change in (dict(teaching=False), dict(recheck_advice=False), dict(pushes_since_report=0)):
        assert O.Sera.teacher_way(moment, available, dict(st, **change), None) == ["convince", "ask"]
    assert O.Sera.teacher_way(moment, {"convince", "ask"}, st) == ["convince", "ask"]
    loop = P.LoopField()
    loop.teach("k", dict(moment, shown=math.log1p(1)), {}, available, ["prove"])
    before = copy.deepcopy(loop.taught)
    loop.end_task("k")
    for fac in sorted(available):
        assert np.allclose(loop.taught["k"][fac][0], P.TAUGHT_FADE * before["k"][fac][0])
        assert np.allclose(loop.taught["k"][fac][1], P.TAUGHT_FADE * before["k"][fac][1])


def drive(teaching=False):
    sera = O.Sera(3)
    task = T.number_task("S24 constant fixture", lambda x: 1, 3, 0)
    estimates, moments = [], []
    choices = iter((["prove"], ["convince"], ["convince"]))
    def choose(kind, moment, est, available, rng):
        estimates.append(dict(est))
        moments.append(dict(moment))
        return next(choices), {f: (1., 1.) for f in P.FACULTIES}
    def uncertain(task, leader, concepts, library, st, speak):
        st["tested"].add((leader, len(task.data)))
        st.update(judge_short=8., judge_where=dict(x=0., v=0., t=0.), shown=0)
        O.Sera._observe_report(st)
        return False
    with patch.object(sera, "_generate", return_value=[L.node("one")]), \
            patch.object(sera, "_moves_available", return_value=set()), \
            patch.object(sera, "_cost", return_value=1.), patch.object(sera, "_spend"), \
            patch.object(sera, "_prove", side_effect=uncertain), \
            patch.object(sera, "_closeness", return_value=1.), \
            patch.object(sera, "_doubt_after", return_value=0.), \
            patch.object(task, "actions", return_value=[
                dict(action=("ask", 9), info=1., novel=0., predicted=1)]), \
            patch.object(sera.field.loop, "choose", side_effect=choose), \
            patch.object(sera, "_finish", side_effect=lambda *a: a[5]), \
            patch.object(sera.field.loop, "teach", wraps=sera.field.loop.teach) as teach:
        st = sera.live(task, teaching=teaching, max_steps=3)
    return sera, st, estimates, moments, teach.call_count


def test_live_never_writes_advice_without_teacher_and_switches_are_isolated(enabled, monkeypatch):
    _, st, estimates, moments, writes = drive()
    assert writes == 0 and st["pushes_since_report"] == 2
    assert moments[2]["shown"] == math.log1p(1)
    assert estimates[2]["convince"] == 4.0
    monkeypatch.setattr(CR, "OFF", {"convince_halving"})
    _, _, off_estimates, off_moments, writes = drive(teaching=True)
    assert writes == 3
    assert off_estimates[2]["convince"] == 8.0
    assert off_moments[2]["shown"] == moments[2]["shown"]
    monkeypatch.setattr(CR, "OFF", {"teach_rechecking"})
    _, st, old_estimates, old_moments, _ = drive()
    assert st["pushes_since_report"] == 0 and old_moments[2]["shown"] == 0
    assert old_estimates[2]["convince"] == 4.0  # turning off the seam does not turn off halving


def test_observation_and_refutation_credit_semantics(enabled):
    st = {"pushes_since_report": 0, "shown": 7, "counter": ("fixture",)}
    O.Sera._observe_push(st)
    O.Sera._observe_push(st)
    assert st["pushes_since_report"] == 2
    O.Sera._observe_report(st)
    assert st == {"pushes_since_report": 0, "shown": 7, "counter": ("fixture",)}
    fam = (("position", "straight"),)
    task = SimpleNamespace(form="strengths", throws=[None],
                           claim_terms=lambda *a, **k: (fam, ((fam[0], "curve"),)),
                           verify=lambda family: (False, SimpleNamespace(band=2., eps=1.),
                                                  "something else could be as large as 2 > 1"))
    st = dict(S06._state(), pushes_since_report=8)
    with patch.object(O.truth, "functional_prior", return_value=0.):
        assert not O.Sera(3)._prove(task, (("position", "shape", "fixture"),), {}, (), st,
                                     lambda *a, **k: None)
    assert st["pushes_since_report"] == 0 and st["judge_short"] > 0
    assert not st["misfit"] and "counter" not in st
    # Reuse the unchanged correctness assertions under the new seam.
    S06.test_only_a_counterexample_refutes()
    S06.test_a_reproof_is_no_new_evidence_and_what_came_after_the_proof_is_not_credited()
    S06.test_the_echo_is_sure_as_its_signal_in_the_units_of_returns()


def test_mask_removes_advice_only_and_preserves_snapshot(enabled, tmp_path):
    field = P.Field(3)
    field.loop.teach("k", dict(shown=1), {}, {"prove"}, ["prove"])
    field.loop.learn("prove", field.loop.features(dict(shown=1), {}, "prove"), 2.)
    field.loop.end_task("k")
    field.methods.teach("k", ("closer",), {})
    field.methods.learn("k", ("closer",), {}, 2.)
    field.steps.teach([1, 0, 0, 0, 0], 1.)
    field.steps.learn([1, 0, 0, 0, 0], 1.)
    field.invent(L.node("one"), ("num", "num"), "fixture", "S24", [])
    field.lexicon.hear(["fixture"], [("concept", 1)])
    T.sym("s24-vocabulary-fixture")
    path = tmp_path / "taught.pkl"
    field.save(path)
    saved_hash = R.file_hash(path)
    clone = P.Field.load(path)
    before = R.field_audit(clone)
    R.mask_advice(clone)
    after = R.field_audit(clone)
    for key in ("vocabulary", "concepts", "standing", "knowledge", "loop_own", "method_own", "step_own"):
        assert before[key] == after[key]
    assert not clone.loop.taught and not clone.methods.taught
    assert after["loop_taught_norm"] == after["step_taught_norm"] == 0
    assert R.file_hash(path) == saved_hash
    assert P.Field.load(path).loop.taught  # original prior is still available to an unmasked probe


def test_withheld_inputs_keep_examples_and_independent_verification():
    example = ((("who",),), 42)
    task = SimpleNamespace(words=["teacher"], _worked={"x": 3}, _worked_of={"q": 1},
                           worked=lambda x: 3, data=[example], verify=lambda: "unchanged")
    R.withhold_teacher(task)
    assert task.words == [] and task.worked(None) is None and not task._worked
    assert task.data == [example] and task.verify() == "unchanged"
    a = {"story": ["mary went to kitchen"], "question": ["where", "mary"]}
    b = dict(a, story=["mary went to garden"])
    assert R.digest(a) != R.digest(b)  # whole inputs, not question/name alone


def gate_fixture():
    manifest = dict(entries={"eval": [dict(id="eval:0", input_digest="full-input")]},
                    verdict_policy=dict(reproof_cost_ratio=1.25, reproof_extra_seconds=30))
    results = {}
    for arm, waste in (("U+", 8), ("U-", 6), ("T+", 5), ("T-", 1)):
        results[arm] = dict(source_sha256=arm[0], settings=dict(
            teaching=False, teacher_priors_masked=True, one_field=0,
            crutches_effective=dict(teach_rechecking=True, convince_halving=arm.endswith("+"))),
            rows=[dict(id="eval:0", input_digest="full-input", actual_input_digest="full-input",
                       status="proven", record=dict(verdict="proven right"),
                       metrics=dict(unproductive_repeats=waste, rechecks=1, report_wall=10))])
    for name in ("U", "T"):
        results[name] = dict(final=dict(shown_own_precision=1, shown_own_return=1),
                             rows=[dict(metrics=dict(opportunities=1, demonstrations=1, rechecks=1))])
    return manifest, results


def test_verdict_is_per_item_and_cannot_pass_missing_learning_or_coverage():
    manifest, results = gate_fixture()
    assert R.verdict(manifest, results)["verdict"] == "PASS"
    bad = copy.deepcopy(results)
    bad["T-"]["rows"][0]["status"] = "censored in progress"
    assert R.verdict(manifest, bad)["verdict"] == "FAIL"  # required retained item is missing
    missing = copy.deepcopy(results)
    for name in R.ARM_NAMES:
        missing[name]["rows"][0]["status"] = "not reached"
    assert R.verdict(manifest, missing)["verdict"] == "INCOMPLETE"
    bad = copy.deepcopy(results)
    bad["T-"]["rows"][0]["actual_input_digest"] = "changed-story"
    assert R.verdict(manifest, bad)["verdict"] == "FAIL"
    bad = copy.deepcopy(results)
    bad["T"]["final"]["shown_own_return"] = 0
    assert R.verdict(manifest, bad)["verdict"] == "INCOMPLETE"
    bad = copy.deepcopy(results)
    bad["T-"]["rows"][0]["metrics"]["checker_failures"] = 1
    assert R.verdict(manifest, bad)["verdict"] == "FAIL"
    bad = copy.deepcopy(results)
    bad["T-"]["source_sha256"] = "different"
    assert R.verdict(manifest, bad)["verdict"] == "FAIL"


def test_deadline_terminates_and_reaps_before_next_child(monkeypatch, tmp_path):
    calls = []
    class Process:
        returncode = None
        def wait(self, timeout=None):
            calls.append(("wait", timeout))
            if self.returncode is None:
                raise subprocess.TimeoutExpired("stub", timeout)
            return self.returncode
        def terminate(self):
            calls.append(("terminate",))
            self.returncode = -15
        def kill(self):
            calls.append(("kill",))
            self.returncode = -9
    monkeypatch.setattr(R.subprocess, "Popen", lambda *a, **k: Process())
    result = R.run_child(["stub"], 1, tmp_path / "child.log", R.child_env(False))
    assert result["timeout"] and result["returncode"] == -15
    assert calls == [("wait", 1), ("terminate",), ("wait", 5)]
    assert R.child_env(False)["SERA_CRUTCH_OFF"] == "convince_halving"
    assert R.child_env(True)["SERA_CRUTCH_OFF"] == ""
    assert R.child_env(False)["SERA_CRUTCH_ON"] == "teach_rechecking"


def test_runner_serial_manifest_and_archive_logic_on_stub(monkeypatch, tmp_path):
    manifest, fixtures = gate_fixture()
    run_out = tmp_path / "run"
    uptime = tmp_path / "uptime"
    uptime.write_text("1234.00 123.00")
    real_path = R.Path
    monkeypatch.setattr(R, "Path", lambda p: uptime if str(p) == "/proc/uptime" else real_path(p))
    calls = []
    def child(argv, seconds, log, env):
        assert seconds > 0
        if "--worker" not in argv:
            calls.append("preflight")
            return dict(returncode=0, timeout=False, wall=0)
        stage = argv[argv.index("--worker") + 1]
        if stage == "prepare":
            R.write_json(run_out / "manifest.json", manifest)
            (run_out / "newborn.pkl").write_bytes(b"newborn")
            calls.append("prepare")
        else:
            arm = argv[argv.index("--arm") + 1]
            base = arm.split("-masked")[0].split("-unmasked")[0]
            result = copy.deepcopy(fixtures[base])
            if stage == "teach":
                assert env["SERA_CRUTCH_OFF"] == "convince_halving"
            else:
                assert env["SERA_CRUTCH_OFF"] == ("" if base.endswith("+") else "convince_halving")
                result["settings"]["teacher_priors_masked"] = "--masked" in argv
            target = run_out / arm
            target.mkdir()
            R.write_json(target / "result.json", result)
            (target / "field.pkl").write_bytes(base[0].encode())
            calls.append(arm)
        return dict(returncode=0, timeout=False, wall=0)
    monkeypatch.setattr(R, "run_child", child)
    monkeypatch.setattr(sys, "argv", ["sera_teach_crutches.py", "--out", str(run_out),
                                   "--train-seconds", "1", "--eval-seconds", "1",
                                   "--probe-seconds", "1", "--wall-seconds", "60"])
    assert R.main() == 0
    assert calls == ["preflight"] * 3 + ["prepare", "U", "T", *R.ARM_NAMES] + [
        name + suffix for name in R.ARM_NAMES for suffix in ("-masked", "-unmasked")]
    assert R.read_json(run_out / "verdict.json")["verdict"] == "PASS"
    assert "manifest.json" in R.read_json(run_out / "checksums.json")
    with pytest.raises(SystemExit):
        R.main()  # refuse reuse, never silently skip a successful world


def test_worker_checkpoints_and_masks_on_stub(enabled, monkeypatch, tmp_path):
    """Exercise the real worker, recorder, identity check and save/reload with a tiny world."""
    for name in R.THREADS:
        monkeypatch.setenv(name, "1")
    monkeypatch.setattr(O, "ONE_FIELD", False)
    monkeypatch.setattr(CR, "OFF", {"convince_halving"})
    def build():
        return SimpleNamespace(subject="math", form="exact", inputs={"n": "num"}, out="num",
                               words=["label"], data=[(1, 1)], pool=[2, 3],
                               probes=lambda: [{"n": 1}, {"n": 2}],
                               _y=lambda x: 1, act=lambda action: (action[1], 1),
                               verify=lambda *args, **kwargs: (True, 1, None))
    descriptor = dict(id="eval:0", seed=3, name="stub", index=0)
    frozen = dict(descriptor, input_digest=R.digest(R.input_record(R.withhold_teacher(build()))))
    manifest = dict(package_files={}, book=None, book_files={},
                    entries={"eval": [frozen]})
    R.write_json(tmp_path / "manifest.json", manifest)
    monkeypatch.setattr(R, "package_files", lambda: {})
    monkeypatch.setattr(R, "schedule", lambda *args: [(descriptor, build)])
    field = P.Field(3)
    field.loop.teach("math", {"shown": 1}, {}, {"prove"}, ["prove"])
    source = tmp_path / "source.pkl"
    field.save(source)
    source_hash = R.file_hash(source)
    observed = []
    class Mind:
        def __init__(self, seed, field):
            self.field = field
        def live(self, task, **kwargs):
            observed.append(kwargs)
            assert task.words == []
            task.act(("ask", 2))
            kwargs["on_schedule"](dict(pushes_since_report=1, available=["prove"], advice=None,
                                       moment={"shown": math.log1p(1)}, config=["prove"]))
            assert task.verify(L.node("one")) == (True, 1, None)
            self.field.loop.learn("prove", self.field.loop.features({"shown": 1}, {}, "prove"), 1.)
            self.field.loop.end_task("math")
            return dict(proven=True, verdict="proven right")
    monkeypatch.setattr(O, "Sera", Mind)
    config = dict(book=None, seed=3, teach_seeds=[1, 2], world_seconds=1)
    assert R.worker(config, tmp_path, "eval", "T-", source, 20, True) == 0
    result = R.read_json(tmp_path / "T-" / "result.json")
    assert result["rows"][0]["status"] == "proven"
    assert result["rows"][0]["actual_input_digest"] == frozen["input_digest"]
    assert result["rows"][0]["metrics"]["accepted_new_proofs"] == 1
    assert result["rows"][0]["metrics"]["pending_pushes"] == 0
    assert result["cloned"]["loop_taught_norm"] == 0
    assert result["initial"]["loop_taught_norm"] > 0
    assert not observed[0]["teaching"] and not observed[0]["recheck_advice"]
    assert R.file_hash(source) == source_hash
    assert (tmp_path / "T-" / "input.pkl").exists() and (tmp_path / "T-" / "field.pkl").exists()


def test_partial_progress_never_manufactures_a_proof(tmp_path):
    target = tmp_path / "T-"
    target.mkdir()
    row = dict(id="eval:0", input_digest="same", status="censored in progress")
    R.write_json(target / "result.json", dict(rows=[row]))
    R.write_json(target / "progress.json", dict(id="eval:0", actual_input_digest="same",
                                              metrics=dict(reports=1, accepted_claims=1)))
    result = R.collect(tmp_path, "T-")
    assert result["rows"][0]["metrics"]["accepted_claims"] == 1
    assert result["rows"][0]["status"] == "censored in progress"
    assert "record" not in result["rows"][0] and "final" not in result


def test_frozen_source_and_failed_preflight_cannot_be_ignored(monkeypatch, tmp_path):
    monkeypatch.setattr(R, "package_files", lambda: {"sera/one.py": "changed"})
    with pytest.raises(RuntimeError, match="source changed"):
        R.verify_frozen(dict(package_files={"sera/one.py": "frozen"}, book=None, book_files={}))
    uptime = tmp_path / "uptime"
    uptime.write_text("1234.00 123.00")
    real_path = R.Path
    monkeypatch.setattr(R, "Path", lambda p: uptime if str(p) == "/proc/uptime" else real_path(p))
    calls = []
    def timed_out(*args):
        calls.append("preflight")
        return dict(returncode=-15, timeout=True, wall=1)
    monkeypatch.setattr(R, "run_child", timed_out)
    out = tmp_path / "stopped"
    monkeypatch.setattr(sys, "argv", ["sera_teach_crutches.py", "--out", str(out)])
    assert R.main() == 2 and calls == ["preflight"]
    assert R.read_json(out / "verdict.json")["verdict"] == "INCOMPLETE"
    assert (out / "summary.txt").exists() and not (out / "manifest.json").exists()
