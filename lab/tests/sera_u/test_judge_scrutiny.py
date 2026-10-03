"""U4 caller contracts and saved-claim replay, with short deterministic stubs."""
import copy
import json
import pickle
from types import SimpleNamespace

import numpy as np
import pytest

from sera import crutches as CR, lang as LG, one as ONE, tasks as TS
from scripts import judge_scrutiny_regression as regression


@pytest.fixture(autouse=True)
def switches(monkeypatch):
    monkeypatch.setattr(CR, 'ON', {'judge_scrutiny'})
    monkeypatch.setattr(CR, 'OFF', set())
    monkeypatch.setattr(TS.S, 'audit_size', lambda bits: 2)
    monkeypatch.setattr(LG, 'DEADLINE', [float('inf')])


def exact(target=lambda x: x):
    return TS.Exact('math', 'stub', target, {'x': 'num'}, 'num', [0], [],
                    lambda r: int(r.integers(1, 10000)))


def variable():
    return LG.node('var', payload='x')


def test_baseline_exact_refusal_is_never_accepted():
    off, on = exact(lambda x: x+1), exact(lambda x: x+1)
    CR.OFF.add('judge_scrutiny')
    before = off.verify(variable(), {}, 1, np.random.default_rng(8))
    CR.OFF.clear()
    after = on.verify(variable(), {}, 1, np.random.default_rng(8))
    assert before == after and not after[0]
    assert off.data == on.data
    assert on._scrutiny_last['used'] == 0
    assert len(on._scrutiny_policy.history[TS.JudgeScrutiny.kind(on)]) == 1


def test_extra_counterexample_after_untouched_baseline_and_rng():
    r = np.random.default_rng(81)
    old_inputs = [int(r.integers(1, 10000)) for _ in range(2)]
    bad = int(r.integers(1, 10000))
    assert bad not in old_inputs
    target = lambda x: x+1 if x == bad else x
    off, on = exact(target), exact(target)
    roff, ron = np.random.default_rng(81), np.random.default_rng(81)
    CR.OFF.add('judge_scrutiny')
    assert off.verify(variable(), {}, 1, roff) == (True, 2, None)
    CR.OFF.clear()
    accepted, n, fail = on.verify(variable(), {}, 1, ron)
    assert not accepted and fail == (bad, bad+1) and n == 3
    assert roff.bit_generator.state == ron.bit_generator.state
    assert on._scrutiny_last['counterexample']['actual'] == bad


def test_history_targets_fresh_inputs_and_inner_overconfidence_is_bounded(monkeypatch):
    task, policy = exact(), TS.JudgeScrutiny()
    kind = policy.kind(task)
    for x in range(100):
        policy.remember(kind, policy.region(x))
    assert len(policy.history[kind]) == TS.SCRUTINY_HISTORY
    calibration = [[0, 0., 0] for _ in range(10)]
    calibration[9] = [10, 9.5, 1]
    record = policy.begin(task, .95, calibration)
    task._scrutiny_prepared = True
    assert record['overconfidence'] == pytest.approx(.85)
    assert record['budget'] == TS.SCRUTINY_PROBES
    visited = []
    original = task._value
    monkeypatch.setattr(task, '_value', lambda e, x, c: (visited.append(x), original(e, x, c))[1])
    rng = np.random.default_rng(21)
    draws = copy.deepcopy(rng)
    for _ in range(2):
        task._fresh(draws)
    candidates = [task._fresh(draws) for _ in range(4*record['budget'])]
    ranked = sorted(range(len(candidates)), key=lambda j: (policy.distance(kind, policy.region(candidates[j])), j))
    assert task.verify(variable(), {}, 1, rng)[0]
    assert visited == [candidates[j] for j in ranked[:record['budget']]]
    assert record['used'] <= record['budget'] <= TS.SCRUTINY_PROBES
    assert record['candidates'] <= 4*TS.SCRUTINY_PROBES
    for j in range(100):
        policy.remember(str(j), (0, 0, 0))
    assert len(policy.history) == TS.SCRUTINY_KINDS


def test_poor_record_only_increases_budget_when_probability_is_high():
    policy, task = TS.JudgeScrutiny(), exact()
    bins = [[20, 18., 0] for _ in range(10)]
    low = policy.begin(task, .4, bins)['budget']
    high = policy.begin(task, .9, bins)['budget']
    assert low == 4 and high > low
    assert policy.begin(task, .9, ())['budget'] == 4


def test_off_matches_literal_old_audit_records_and_rng():
    CR.ON.clear()
    CR.OFF.add('judge_scrutiny')
    task, ref = exact(), exact()
    a, b = np.random.default_rng(5), np.random.default_rng(5)
    settings_before = CR.settings()
    actual = task.verify(variable(), {}, 1, a)
    n = TS.S.audit_size(1)
    for _ in range(n):
        x = ref._fresh(b)
        y = ref._y(x)
        assert LG.safe(variable(), {ref.var: x}, {}) == y
    assert actual == (True, n, None) and task.data == ref.data
    assert a.bit_generator.state == b.bit_generator.state
    assert CR.settings() == settings_before
    assert not hasattr(task, '_scrutiny_last')
    assert not hasattr(task, '_scrutiny_policy')


def test_story_uses_its_perceived_input_for_extra_audits():
    task = object.__new__(TS.Story)
    task._y = lambda x: x
    TS.Exact.__init__(task, 'language', 'story stub', lambda x: x, {'g': 'num'}, 'num', [0], [],
                      lambda r: int(r.integers(1, 10000)))
    task.mind = None
    candidate = LG.node('var', payload='g')
    assert task.verify(candidate, {}, 1, np.random.default_rng(6)) == (True, 6, None)
    assert task._scrutiny_last['used'] == 4


def stub_rail(monkeypatch, results):
    task = object.__new__(TS.Rail)
    task.world = SimpleNamespace(n_situations=2)
    task._ledger = object()
    task.throws, task.pushes = [], 0
    calls = []
    results = iter(results)
    def verify(family):
        calls.append(family)
        ok, band, why = next(results)
        TS.truth.LAST_WHERE.update(x=1., v=1., t=0.)
        return ok, SimpleNamespace(band=band, accepted=ok), why
    task._verify_plain = verify
    task.act = lambda action: (task.throws.append(action), SimpleNamespace(x=np.array([0., 1.]),
                                                                         v=np.array([0., 1.])))[1]
    # Positive commands visit the widest-band point; negative commands are far away.
    monkeypatch.setattr(TS.DS, '_own_numbers', lambda led, fam, k, a:
                        (np.array([1., 1.]) if a.u > 0 else np.array([-5., -5.]), None, None))
    monkeypatch.setattr(TS.truth, 'LAST_WHERE', {})
    return task, calls


@pytest.mark.parametrize('after', [(True, .05, None), (True, .15, None),
                                   (False, .3, 'something else could be as large as .3')])
def test_rail_narrows_or_refuses_and_records_each_witness(monkeypatch, after):
    task, calls = stub_rail(monkeypatch, [(True, .1, None), after])
    accepted, cert, why = task.verify(())
    assert accepted == (after[0] and after[1] <= .1)
    assert cert.band == after[1]  # The certificate is the real second result, never edited.
    record = task._scrutiny_last
    assert len(calls) == 2 and 0 < record['used'] <= record['budget'] <= TS.SCRUTINY_THROWS
    assert record['candidates'] <= TS.SCRUTINY_CANDIDATES
    assert task.throws[0][2].u > 0
    if not accepted:
        assert record['counterexample']['throws'] and record['counterexample']['where']
        assert record['counterexample']['kind'] == 'uncertainty'


def test_rail_refusal_is_not_retried_and_off_is_literal_call(monkeypatch):
    task, calls = stub_rail(monkeypatch, [(False, .3, 'not narrow')])
    assert task.verify(())[0] is False
    assert len(calls) == 1 and not task.throws and task._scrutiny_last['used'] == 0
    CR.OFF.add('judge_scrutiny')
    off, calls = stub_rail(monkeypatch, [(True, .1, None)])
    assert off.verify(())[0] is True
    assert len(calls) == 1 and not off.throws and not hasattr(off, '_scrutiny_last')


def test_rail_refutation_locates_observed_residual_without_hidden_truth(monkeypatch):
    task = object.__new__(TS.Rail)
    throw = TS.W.Throw(0, 0, TS.W.push_of(1.), np.array([1., 5.]), np.array([0., 0.]))
    task.throws, task.sigma = [throw], (1., 1.)
    fit = SimpleNamespace(ok=True, coef=np.zeros(0), mu={0: 1.}, knocks={})
    task._ledger = SimpleNamespace(mle=lambda family: fit, _models={(): object()})
    monkeypatch.setattr(TS.L, '_scale', lambda sigma: np.ones(4))
    monkeypatch.setattr(TS.L, '_sim', lambda *args: np.zeros(4))
    policy = TS.JudgeScrutiny()
    record = policy.begin(task)
    witness = task._scrutiny_misfit((), policy, record)
    assert witness['where'] == dict(x=5., v=0., t=TS.paths.DT_OBS)
    assert witness['residual_sigmas'] == 5.
    assert record['residual_probes'] == 1
    assert policy.history[policy.kind(task)] == [(5., 0., TS.paths.DT_OBS)]


def test_prove_binds_saved_history_and_reuses_pre_verdict_inner_read():
    task, candidate = exact(), variable()
    kind = ONE.kind_of(task)
    bins = [[10, 9., 1] for _ in range(10)]
    inner = SimpleNamespace(probability=lambda k, x: .9, curves={kind: bins})
    mind = object.__new__(ONE.Sera)
    mind.field = SimpleNamespace(inner=inner)
    mind._u_predictions = {(kind, candidate): np.zeros(65)}
    mind._u_on = lambda name: name == 'inner_judge'
    mind.field.judge_scrutiny = TS.JudgeScrutiny()
    mind.field.judge_scrutiny.remember(kind, TS.JudgeScrutiny.region(7))
    mind._scrutiny_begin(task, candidate, remaining=2)
    assert task._scrutiny_last['inner_probability'] == .9 and task._scrutiny_last['budget'] == 2
    assert task.verify(candidate, {}, 1, np.random.default_rng(3))[0]
    st = {}
    mind._scrutiny_record(task, candidate, st)
    assert st['scrutiny'][0]['used'] == 2
    # Field serialization includes history; no transient candidate read goes into this policy.
    assert pickle.loads(pickle.dumps(mind.field.judge_scrutiny)).history == mind.field.judge_scrutiny.history
    assert task._scrutiny_policy is mind.field.judge_scrutiny


def saved_rows(n=306):
    return [dict(seed=i, world=0, family='()', accepted=i % 5 == 0,
                 checker=True if i % 5 == 0 else None, band=.1) for i in range(n)]


def stub_runner(row, enabled):
    accepted = regression.saved_accepted(row)
    refused_extra = enabled and row['seed'] == 0
    return dict(accepted=accepted and not refused_extra, band=.09 if enabled else .1,
                scrutiny=dict(budget=1, used=1, candidates=4,
                              counterexample={'kind': 'input', 'input': 7, 'expected': 1, 'actual': 0}
                              if refused_extra else None))


def test_saved_regression_cli_runs_two_306_claim_stubs(tmp_path):
    files = [tmp_path/'a.jsonl', tmp_path/'b.jsonl']
    for path in files:
        path.write_text(''.join(json.dumps(row)+'\n' for row in saved_rows()), encoding='utf-8')
    out = tmp_path/'report.json'
    assert regression.main(['--claims', str(files[0]), '--claims', str(files[1]), '--out', str(out)],
                           runner_factory=lambda: stub_runner) == 0
    report = json.loads(out.read_text())
    assert report['passed'] and all(arm['claims'] == 306 for arm in report['arms'])
    assert all(len(arm['extra_refusals']) == 1 for arm in report['arms'])


def test_regression_rejects_rescue_widening_and_missing_witness():
    rows = saved_rows(6)
    def unsafe(row, enabled):
        return dict(accepted=True if enabled else regression.saved_accepted(row), band=.2 if enabled else .1)
    result = regression.replay(rows, unsafe)
    assert not result['passed']
    assert any(v['reason'] == 'a refused claim was accepted' for v in result['violations'])
    assert any(v['reason'] == 'accepted band widened or is not finite' for v in result['violations'])
    def unwitnessed(row, enabled):
        return dict(accepted=False if enabled else regression.saved_accepted(row), band=.1)
    assert not regression.replay(rows, unwitnessed)['passed']


def test_summary_is_not_a_saved_replay_and_incomplete_claims_fail(tmp_path):
    (tmp_path/'summary.txt').write_text('REGRESSION DONE 306', encoding='utf-8')
    out = tmp_path/'missing.json'
    assert regression.main(['--saved', str(tmp_path), '--out', str(out)],
                           runner_factory=lambda: stub_runner) == 1
    assert 'summary.txt is insufficient' in json.loads(out.read_text())['error']
    path = tmp_path/'incomplete.jsonl'
    path.write_text(json.dumps(saved_rows(1)[0])+'\n', encoding='utf-8')
    with pytest.raises(ValueError, match='306 unique'):
        regression.load_claims(path)
