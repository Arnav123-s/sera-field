"""S27 channel/checkpoint checks: stub the search, never run a physics certificate."""
import copy
import json
import pickle
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import sera_course as R
from sera import crutches as C, lang as L, one as O, phi as P, tasks as T

N = L.node
X = N('var', payload='n')
TWICE = N('add', X, X)


@pytest.fixture(autouse=True)
def legacy(monkeypatch):
    monkeypatch.setattr(C, 'OFF', set())
    monkeypatch.setattr(C, 'ON', set())
    monkeypatch.setattr(O, 'ONE_FIELD', False)


def tiny(name='tiny', target=lambda n: 2 * n):
    return T.Exact('math', name, target, {'n': 'num'}, 'num', [0, 1], [2, 3],
                   lambda r: int(r.integers(0, 6)), words=('twice',), worked=lambda n: (2 * n,))


def finish(s, task, law=TWICE, channel=None, proven=True, teaching=False):
    st = dict(steps=1, proven=dict(law=law, audit=1) if proven else None, level=0, asked=0,
              explored=0, time={}, peak=[0], peak_by={}, memory_stops=0, origins={}, footholds={})
    s._task_senses, s._built = [], []
    return s._finish(task, O.kind_of(task), task.context(), s._concepts(), (), st, law, [law], {law: 0.},
                     {law: 0.}, {}, [], [], [], teaching, time.time(), time.process_time(), answer_channel=channel)


def stub_search(monkeypatch, law=TWICE, seen=None):
    monkeypatch.setattr(O.Sera, '_inner_ability', lambda *args: [])
    def search(self, task, teaching=False, answer_channel=None, **kwargs):
        if seen is not None:
            seen.append(dict(teaching=teaching, words=list(task.words),
                             worked=task.worked(task.data[0][0])))
        return finish(self, task, law, answer_channel, teaching=teaching)
    monkeypatch.setattr(O.Sera, 'live', search)


def test_study_checks_its_book_without_teacher_or_demonstrations(monkeypatch):
    seen = []
    stub_search(monkeypatch, seen=seen)
    s = O.Sera(3)
    task = R.strip_teacher(tiny())
    before = copy.deepcopy(task.data)
    u = R.live(s, task, 'study', time.time() + 2, 3)
    assert seen == [dict(teaching=False, words=[], worked=None)]
    assert u['status'] == 'right' and u['feedback'] == dict(verdict='right', source='book')
    assert task.data == before and 'correction' not in u
    answers = list(s.field.answers.values())
    assert len(answers) == 1 and answers[0]['source'] == 'book' and answers[0]['words'] == []
    assert 'course_tally' not in s.field.__dict__


def test_book_fail_uses_refutation_and_no_answer_or_steps(monkeypatch):
    stub_search(monkeypatch, law=N('one'))
    s = O.Sera(3)
    task = R.strip_teacher(tiny())
    data = copy.deepcopy(task.data)
    u = R.live(s, task, 'study', time.time() + 2, 3)
    assert u['status'] == 'wrong' and u['feedback']['source'] == 'book'
    assert s.field.standing[N('one')] == [0, 1]
    assert not s.field.concepts and task.data == data and task.worked(0) is None


@pytest.mark.parametrize('one_field', [False, True])
def test_test2_only_verdict_refutes_and_decreases_reliability(monkeypatch, one_field):
    monkeypatch.setattr(O, 'ONE_FIELD', one_field)
    stub_search(monkeypatch, law=N('one'))
    s = O.Sera(3)
    task = R.strip_teacher(tiny())
    # One prior successful teacher verdict, then two wrong replies of the same perceived kind.
    s.course_verdict(task, TWICE, True, 'teacher', reliability=True)
    assert s.course_reliable(task)
    data = copy.deepcopy(task.data)
    u = R.live(s, task, 'test2', time.time() + 2, 3)
    assert u['feedback'] == dict(verdict='wrong', source='teacher')
    assert 'correction' not in u and task.data == data and task.words == []
    assert task.worked(0) is None and s.field.standing[N('one')][1] == 1
    assert all(a['words'] == [] for a in s.field.answers.values())
    s.course_verdict(task, N('one'), False, 'teacher', reliability=True)
    assert not s.course_reliable(task)
    retry = R.live(s, task, 'test2', time.time() + 2, 3)
    assert retry['status'] == 'abstained' and retry['response'] == "I don't know"
    assert retry['feedback'] is None
    assert ('course_tally' in s.field.__dict__) is not one_field


def test_test2_switch_off_keeps_refutation_without_reliability(monkeypatch):
    monkeypatch.setattr(C, 'OFF', {'course_told_wrong'})
    stub_search(monkeypatch, law=N('one'))
    s = O.Sera(3)
    task = R.strip_teacher(tiny())
    for _ in range(3):
        assert R.live(s, task, 'test2', time.time() + 2, 3)['status'] == 'wrong'
    assert s.field.standing[N('one')][1] == 3
    assert 'course_tally' not in s.field.__dict__


def test_test1_one_correction_supplies_values_and_retry_can_use_them(monkeypatch):
    seen = []
    stub_search(monkeypatch, law=N('one'), seen=seen)
    s = O.Sera(3)
    task = R.strip_teacher(tiny())
    first = R.live(s, task, 'test1', time.time() + 2, 3)
    c = first['correction']
    assert c['answer'] == 2 * c['input'] and c['steps'] == (c['answer'],)
    assert seen[0] == dict(teaching=False, words=[], worked=None)
    restored = R.strip_teacher(tiny())
    R.restore_observations(restored, json.loads(json.dumps(first)))
    assert restored.data == task.data and restored.worked(2) == (4,)
    retry = R.live(s, restored, 'test1', time.time() + 2, 3, corrected=True)
    assert seen[1]['teaching'] and seen[1]['worked'] is not None
    assert 'correction' not in retry


@pytest.mark.parametrize('right', [True, False])
def test_test3_grade_only_after_live_and_never_in_field(monkeypatch, right):
    stub_search(monkeypatch)
    s = O.Sera(3)
    task = R.strip_teacher(tiny(target=lambda n: 2 * n if right else 2 * n + 1))
    def grade_guard(self, *args, **kwargs):
        # _finish has already completed; grading on a detached task is the only call.
        assert s.field.tasks == 1 and self is not task
        self.mind = 'observer cache mutation'
        T.sym('observer-only-word')
        return dict(verdict='proven right' if right else 'SURE AND WRONG')
    monkeypatch.setattr(T.Exact, 'grade', grade_guard)
    u = R.live(s, task, 'test3', time.time() + 2, 3)
    assert u['status'] == ('right' if right else 'wrong') and u['feedback'] is None
    assert task.words == [] and task.worked(0) is None
    assert 'correction' not in u and s.field.answers == {} and s.field.inbox == []
    assert s.field.log[-1]['verdict'] == 'proven'
    assert s.field.standing[TWICE] == [1, 0]  # its own proof, independent of observer truth
    assert 'course_tally' not in s.field.__dict__ and 'observer-only-word' not in T.VOCAB
    assert not hasattr(task, 'mind')


def test_isolated_grader_cannot_mutate_live_memory_or_task(monkeypatch):
    s = O.Sera(3)
    task = tiny()
    task.mind = s.field.ideas
    original = pickle.dumps(s.field)
    data = copy.deepcopy(task.data)
    def malicious(self, *args, **kwargs):
        self.mind.read((100, 101), 'observer')
        self.data.clear()
        T.sym('private-grade-word')
        return dict(verdict='SURE AND WRONG')
    monkeypatch.setattr(T.Exact, 'grade', malicious)
    assert not R.isolated_grade(task, TWICE, s._concepts(), dict(law=TWICE), 3)
    assert pickle.dumps(s.field) == original and task.data == data
    assert 'private-grade-word' not in T.VOCAB


def test_story_grade_rebinds_fresh_generator_without_mutating_original():
    task = R.strip_teacher(T.lesson_first(3))
    g = N('var', payload='g')
    first_word = N('head', N('head', N('tail', g), payload='list(num)'))
    before = copy.deepcopy((task.data, task._key, task._worked, task._seen, T.VOCAB))
    assert R.isolated_grade(task, first_word, {}, dict(law=first_word), 3)
    assert (task.data, task._key, task._worked, task._seen, T.VOCAB) == before


def test_optional_worked_values_and_switch(monkeypatch):
    name, build = R.composed(3)[0]
    task = build()
    assert task.worked((2, -1)) == ((3, 0), (0, 3))
    row = dict(name=name, builder=build, number_seed=3, digest=R.input_digest(task))
    on = R.materialize(row, 'lesson')
    on_steps = on.worked((2, -1))
    monkeypatch.setattr(C, 'OFF', {'course_worked_steps'})
    off = R.materialize(row, 'lesson')
    assert on.data == off.data and on.words == off.words
    assert on_steps is not None and off.worked((2, -1)) is None
    assert R.materialize(row, 'study').worked((2, -1)) is None
    monkeypatch.setattr(C, 'OFF', set())
    for n, b in R.composed(3):
        t = b()
        x = t.data[0][0]
        steps = t.worked(x)
        assert len(steps) == 2 and steps[-1] == t._y(x)
        def values_only(v):
            return isinstance(v, (int, float)) or (isinstance(v, tuple) and all(values_only(x) for x in v))
        assert values_only(steps), n  # no op names, callable objects, or language ASTs
    assert C.REGISTRY['course_worked_steps']['status'] == 'taught'
    assert C.REGISTRY['course_told_wrong']['status'] == 'taught'
    assert tiny().worked(2) == (4,)
    bare = T.Exact('math', 'bare', lambda n: n, {'n': 'num'}, 'num', [0], [], lambda r: 0)
    assert bare.worked(0) is None
    p = T.Puzzle('tiny', dict(train=[dict(input=[[0]], output=[[0]])], test=[dict(input=[[0]])]))
    assert p.worked(((0,),)) is None  # subclasses that do not call Exact.__init__ stay compatible


def test_worked_candidate_is_taught_through_existing_stepfield_then_fades(monkeypatch):
    s = O.Sera(3)
    task = tiny()
    sf = s._stepfield()
    feature = [1.0] * len(P.STEP_FEATURES)
    vals = (0, 2)
    monkeypatch.setattr(s, '_step_candidates', lambda *a: [(TWICE, 'num', vals, vals, feature)])
    monkeypatch.setattr(s, '_rest', lambda *a: (N('var', payload='w1'), True))
    ctx = dict(sf=sf, rng=np.random.default_rng(3), task=task, teaching=True, xs=[0, 1], pairs=task.data)
    s._open_steps = []
    got = s._steps_from(ctx, task.inputs, task.probes()[:2], 0, time.time() + 2)
    assert got is not None and np.any(sf.At) and np.any(sf.bt)
    before = sf.At.copy(), sf.bt.copy()
    sf.end_task()
    assert np.allclose(sf.At, before[0] * P.TAUGHT_FADE)
    assert np.allclose(sf.bt, before[1] * P.TAUGHT_FADE)
    sf.At.fill(0)
    sf.bt.fill(0)
    ctx['teaching'] = False
    s._steps_from(ctx, task.inputs, task.probes()[:2], 0, time.time() + 2)
    assert not np.any(sf.At) and not np.any(sf.bt)


def test_disjoint_actual_inputs_and_transfer_curriculum(monkeypatch):
    taught, alone = R.BASE.teaching, R.BASE.alone
    monkeypatch.setattr(R.BASE, 'teaching', lambda seed: [(n, b) for n, b in taught(seed) if not n.startswith('rail:')])
    monkeypatch.setattr(R.BASE, 'alone', lambda seed: [(n, b) for n, b in alone(seed) if not n.startswith('rail:')])
    plan = R.make_plan(3)
    digests = [row['digest'] for p in R.PHASES for row in plan[p]]
    assert len(digests) == len(set(digests))
    lesson = {r['digest'] for r in plan['lesson']}
    for p in ('test1', 'test2', 'test3'):
        assert lesson.isdisjoint(r['digest'] for r in plan[p])
    assert set(R.COMPOSED_LISTS).isdisjoint(R.BASE.ALONE_LISTS)
    assert set(R.COMPOSED_NUMBERS).isdisjoint(R.BASE.ALONE_NUMBERS)
    assert 'story: story_before_last' in {r['name'] for r in plan['test3']}
    assert 'story: story_before_last' not in {r['name'] for r in plan['lesson']}
    story = R.story_before_last(3)
    assert story.words == [] and all(story.worked(x) is None for x, _ in story.data)
    # Assert the fix is about real inputs, not names or seed metadata.
    a, b = tiny('first'), tiny('second')
    assert R.input_digest(a) == R.input_digest(b)
    R.refresh_numbers(a, 3)
    R.refresh_numbers(b, 100_003)
    assert R.input_digest(a) != R.input_digest(b)


def tiny_plan(monkeypatch):
    monkeypatch.setattr(R, 'phase_builders', lambda seed, phase: [(phase, lambda phase=phase: tiny(phase))])
    return R.make_plan(3)


def test_resume_checkpoint_schema_and_phase_isolation(monkeypatch, tmp_path):
    plan = tiny_plan(monkeypatch)
    seen = []
    stub_search(monkeypatch, seen=seen)
    one = R.run(tmp_path, seed=3, hours=.01, phase='lesson', plan=plan)
    assert len(seen) == 1 and seen[0]['teaching']
    assert one['phases']['test3']['counts']['not reached'] == 1
    saved = P.Field.load(tmp_path / 'field.pkl')
    assert saved.tasks == 1 and saved.course_progress['committed'] == ['lesson-000-a1']
    assert 'status' not in repr(saved.course_progress) and 'observer_right' not in repr(saved.course_progress)
    resumed = R.run(tmp_path, seed=3, hours=.01, phase='all', plan=plan)
    assert len(seen) == 5 and all(not x['teaching'] and x['words'] == [] and x['worked'] is None for x in seen[1:])
    assert resumed['schema_version'] == 1 and tuple(resumed['phases']) == R.PHASES
    assert json.loads((tmp_path / 'COURSE.json').read_text()) == resumed
    for p in R.PHASES:
        phase = resumed['phases'][p]
        assert set(phase['counts']) == set(R.STATUSES)
        assert phase['counts']['right'] == 1 and phase['finished'] and phase['field_size']['tasks'] >= 1
        item = phase['items'][0]
        assert item['attempts'] == 1 and item['wall'] >= 0 and len(item['input_digest']) == 64
    before = P.Field.load(tmp_path / 'field.pkl').tasks
    R.run(tmp_path, seed=3, hours=.01, phase='all', plan=plan)
    assert len(seen) == 5 and P.Field.load(tmp_path / 'field.pkl').tasks == before


def test_resume_after_attempt_commit_does_not_repeat_feedback(monkeypatch, tmp_path):
    plan = tiny_plan(monkeypatch)
    seen = []
    stub_search(monkeypatch, seen=seen)
    real_report = R.report
    def interrupted(*args):
        raise RuntimeError('after field commit, before report')
    monkeypatch.setattr(R, 'report', interrupted)
    with pytest.raises(RuntimeError, match='after field commit'):
        R.run(tmp_path, seed=3, hours=.01, phase='lesson', plan=plan)
    assert P.Field.load(tmp_path / 'field.pkl').tasks == 1
    monkeypatch.setattr(R, 'report', real_report)
    result = R.run(tmp_path, seed=3, hours=.01, phase='lesson', plan=plan)
    assert len(seen) == 1 and result['phases']['lesson']['items'][0]['attempts'] == 1


def test_uncommitted_unit_is_ignored_and_retried(monkeypatch, tmp_path):
    plan = tiny_plan(monkeypatch)
    stub_search(monkeypatch)
    real_save = P.Field.save
    def fail_commit(self, path):
        if self.tasks:
            raise RuntimeError('before field commit')
        return real_save(self, path)
    monkeypatch.setattr(P.Field, 'save', fail_commit)
    with pytest.raises(RuntimeError, match='before field commit'):
        R.run(tmp_path, seed=3, hours=.01, phase='lesson', plan=plan)
    assert (tmp_path / 'units' / 'lesson-000-a1.json').exists()
    assert P.Field.load(tmp_path / 'field.pkl').tasks == 0
    monkeypatch.setattr(P.Field, 'save', real_save)
    result = R.run(tmp_path, seed=3, hours=.01, phase='lesson', plan=plan)
    assert P.Field.load(tmp_path / 'field.pkl').tasks == 1
    assert result['phases']['lesson']['attempts'] == 1


def test_resume_rejects_changed_arm_or_seed(monkeypatch, tmp_path):
    plan = tiny_plan(monkeypatch)
    stub_search(monkeypatch)
    R.run(tmp_path, seed=3, hours=.01, phase='lesson', plan=plan)
    monkeypatch.setattr(C, 'OFF', {'course_worked_steps'})
    with pytest.raises(ValueError, match='resume configuration'):
        R.run(tmp_path, seed=3, hours=.01, plan=plan)


def test_deadlines_reserve_each_phase_and_bound_retries(monkeypatch, tmp_path):
    plan = tiny_plan(monkeypatch)
    now, calls = [100.0], []
    def clock():
        return now[0]
    def live(s, task, phase, deadline, seed, corrected=False):
        calls.append((phase, corrected, deadline - now[0]))
        # Every answer is wrong, and each takes half of the available attempt box.
        now[0] += (deadline - now[0]) / 2
        s.field.tasks += 1
        return dict(phase=phase, status='wrong', observations=list(task.data), feedback=None,
                    correction=dict(input=0, answer=0, steps=(0,)) if phase == 'test1' and not corrected else None)
    monkeypatch.setattr(R, 'live', live)
    result = R.run(tmp_path, seed=3, hours=.01, retries=2, plan=plan, clock=clock)
    assert [p for p, _, _ in calls] == ['lesson', 'study', 'test1', 'test1', 'test2', 'test2', 'test2', 'test3']
    assert all(box > 0 for _, _, box in calls)
    assert result['phases']['test1']['attempts'] == 2 and result['phases']['test2']['attempts'] == 3
    assert result['phases']['test3']['attempts'] == 1


def test_legacy_finish_still_uses_existing_observer_record(monkeypatch):
    monkeypatch.setattr(O.Sera, '_inner_ability', lambda *a: [])
    s = O.Sera(3)
    r = finish(s, tiny(), channel=None)
    assert r['verdict'] == s.field.log[-1]['verdict'] == 'proven right'
    assert s.field.answers == {} and not hasattr(s.field, 'course_tally')
    assert 'course_worked_steps' not in C.settings()['crutches_effective']
    assert 'course_worked_steps' in C.settings(include_course=True)['crutches_effective']


@pytest.mark.parametrize('right', [True, False])
def test_real_live_defers_success_echo_until_permitted_verdict(monkeypatch, right):
    s = O.Sera(3)
    task = tiny()
    signals, proved_returns = [], []
    monkeypatch.setattr(s, '_inner_ability', lambda *a: [])
    monkeypatch.setattr(s, '_generate', lambda *a: [TWICE])
    monkeypatch.setattr(s, '_moves_available', lambda *a: set())
    monkeypatch.setattr(task, 'actions', lambda *a: [])
    monkeypatch.setattr(s, '_doubt_after', lambda *a: 0.)
    monkeypatch.setattr(s, '_cost', lambda *a: 1.)
    monkeypatch.setattr(s, '_spend', lambda *a: None)
    configs = iter([['prove'], ['leave']])
    monkeypatch.setattr(s.field.loop, 'choose', lambda *a: (next(configs),
                        {f: (1., 1.) for f in ('prove', 'grow', 'ask', 'leave')}))
    def prove(task, law, concepts, library, st, speak):
        st['tested'].add((law, len(task.data)))
        st['proven'] = dict(law=law, key=(law, len(task.data)), audit=1)
        return True
    monkeypatch.setattr(s, '_prove', prove)
    real_echo, real_learn = s.field.echo, s.field.loop.learn
    def echo(signal):
        signals.append(signal)
        return real_echo(signal)
    def learn(fac, x, y, **kwargs):
        if fac == 'prove':
            proved_returns.append(y)
        return real_learn(fac, x, y, **kwargs)
    monkeypatch.setattr(s.field, 'echo', echo)
    monkeypatch.setattr(s.field.loop, 'learn', learn)
    def channel(*args):
        assert signals == [] and proved_returns == []
        return dict(right=right, source='teacher')
    rec = s.live(task, max_steps=2, answer_channel=channel)
    assert rec['proven']
    assert any(v > 0 for v in signals) is right
    assert bool(s.field.concepts) is right
    assert proved_returns == [min(20., P.V_DONE) if right else 0.]


def test_rail_verdict_refutes_without_a_judge_or_shown_answer():
    s = O.Sera(3)
    task = SimpleNamespace(name='rail channel', form='strengths', inputs={'s': 'num'}, out='num',
                           context=lambda: [0.] * 7)
    law = (('position', 'expr', N('var', payload='s')),)
    s.course_verdict(task, law, False, 'teacher', reliability=True)
    assert s.field.standing[law] == [0, 1] and not s.course_reliable(task)
    assert list(s.field.answers.values())[0]['words'] == []


def test_course_rail_success_cannot_credit_an_unattributed_formula(monkeypatch):
    s = O.Sera(3)
    law = (('position', 'expr', N('var', payload='s')),)
    task = SimpleNamespace(name='rail uncredited', subject='physics', form='strengths', inputs={'s': 'num'},
                           out='num', words=[], context=lambda: [0.] * 7)
    proof = dict(law=law, cert=SimpleNamespace(band=.1), family=(('position', 'straight'),), fit=object(), credit=None)
    st = dict(steps=1, proven=proof, level=0, asked=0, explored=0, time={}, peak=[0], peak_by={},
              memory_stops=0, origins={}, footholds={})
    monkeypatch.setattr(s, '_certified', lambda *a: (None, []))
    monkeypatch.setattr(s, '_signs', lambda *a: [])
    monkeypatch.setattr(s, '_what_is_mass', lambda *a: None)
    s._task_senses, s._built = [], []
    r = s._finish(task, O.kind_of(task), task.context(), s._concepts(), (), st, law, [law], {law: 0.},
                  {law: 0.}, {}, [], [], [], False, time.time(), time.process_time(),
                  answer_channel=lambda *a: dict(right=True, source='book'))
    assert r['proven'] and not r['attributed'] and r['invented'] == []
    assert s.field.standing == {} and s.field.answers == {} and not s.field.concepts
