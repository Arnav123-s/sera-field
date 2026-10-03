"""U5 runner contracts. Native inference/search/judges are stubbed."""
import copy
from contextlib import nullcontext
import json
from pathlib import Path
import pickle
from types import SimpleNamespace

import numpy as np
import pytest

from scripts import sera_u_course as UC, sera_bakeoff as BO, crutch_ledger as LEDGER
from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u.ports import PortBudget, digest


@pytest.fixture(autouse=True)
def switches(monkeypatch):
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', set())
    monkeypatch.setenv('SERA_CRUTCH_ON', '')
    monkeypatch.setenv('SERA_CRUTCH_OFF', '')
    monkeypatch.delenv('SERA_BOOK', raising=False)


class Clock:
    value = 0.

    def __call__(self):
        return self.value


class Field:
    def __init__(self):
        self.tasks = 0

    def account(self):
        return dict(tasks=self.tasks)


class Backend:
    kind = 'U'

    def __init__(self, clock=None):
        self.field = Field()
        self.clock = clock
        self.feedback = []
        self.seen = []

    def settings(self):
        return {k: k != 'lesson_words' for k in sorted(CR.REGISTRY)}

    def save(self, path):
        Path(path).write_bytes(pickle.dumps(self.field))

    def load(self, path):
        self.field = pickle.loads(Path(path).read_bytes())

    def live(self, task, phase, wall, channel, teaching=False):
        self.seen.append((phase, teaching, list(task.words), task))
        program = LG.node('var', payload='x')
        result = channel(task, program, {}, dict(law=program))
        self.feedback.append(result)
        self.field.tasks += 1
        return dict(answer=program, claim=None, proven=True, verdict='proven', say=[], configs={})


def task(value=1):
    # Exact takes the inputs and computes each output itself: data == [(value, value)]
    return TS.Exact('math', 'stub', lambda x: x, {'x': 'num'}, 'num',
                    [value], [value+1], lambda rng: value+2, words=['heard'])


def plan():
    result = {}
    for pi, phase in enumerate(UC.PHASES):
        rows = []
        for j in range(2):
            value = pi*10+j+1
            builder = lambda value=value: task(value)
            rows.append(dict(id=f'{phase}-{j:03d}', name=f'number: {j}', builder=builder,
                             digest=UC.C.input_digest(builder()), number_seed=0))
        result[phase] = rows
    return result


@pytest.mark.parametrize('phase,source', [('lesson', 'teacher'), ('study', 'book'),
                                          ('test1', 'teacher'), ('test2', 'test2'), ('test3', None)])
def test_phase_boundaries(monkeypatch, phase, source):
    backend = Backend()
    world = task()
    if phase != 'lesson':
        UC.C.strip_teacher(world)
    called = []
    def grade(*args):
        called.append(len(backend.seen))
        return True
    monkeypatch.setattr(UC.C, 'isolated_grade', grade)
    unit = UC.attempt(backend, world, phase, 1., 3)
    received = backend.feedback[-1]
    assert (None if received is None else received['source']) == source
    assert unit['status'] == 'right'
    assert (unit['feedback'] is None) == (phase == 'test3')
    if phase != 'lesson':
        assert backend.seen[-1][2] == []
    if phase in ('study', 'test2', 'test3'):
        public = backend.seen[-1][3]
        assert public.actions() == [] and public.worked(1) is None
        with pytest.raises(AttributeError):
            public._y(1)
    if phase == 'test3':
        assert called == [1]  # hidden grade only after live returns


def test_verdict_only_detaches_audit_data_and_hides_output():
    class MutatingWorld:
        form = 'exact'
        data = [(1, 1)]
        def verify(self, *args):
            self.data.append((7, 123456))
            TS.sym('private_audit_token_u5')
            return False, 4, (7, 123456)
        def consistent(self, p, concepts):
            return True
    live = MutatingWorld()
    public = UC.CourseWorld(live, 'test2')
    vocab = copy.deepcopy((TS.VOCAB, TS.WORDS, TS._NEXT))
    assert public.verify(None, {}, 1, None) == (False, 4, None)
    assert live.data == [(1, 1)]
    assert (TS.VOCAB, TS.WORDS, TS._NEXT) == vocab
    exam = UC.CourseWorld(live, 'test3')
    assert exam.verify(None, {}, 1, None) == (False, 4, None)
    assert live.data == [(1, 1)] and (TS.VOCAB, TS.WORDS, TS._NEXT) == vocab
    assert copy.deepcopy(public).world.data == [(1, 1)]


def test_suite_validation_defers_only_port_limits(monkeypatch):
    views = [UC.TaskView.from_task(task()), UC.TaskView.from_task(task())]
    calls = []
    def records(view, *args, **kwargs):
        calls.append(view)
        raise PortBudget('too large')
    monkeypatch.setattr(UC.TaskView, 'records', records)
    def validate(suite):
        for view in views:
            assert view.records() == ()
        if suite.get('bad_identity'):
            raise ValueError('identity changed')
        return suite
    monkeypatch.setattr(UC.RSI, 'validate_frozen_suite', validate)
    assert UC.validate_suite({'ok': True}) == {'ok': True}
    assert len(calls) == 2 and UC.TaskView.records is records
    with pytest.raises(ValueError, match='identity changed'):
        UC.validate_suite({'bad_identity': True})
    assert UC.TaskView.records is records


def test_class_answer_seam_restores_and_is_not_checkpoint_state(monkeypatch):
    class Engine:
        def live(self, task, **kwargs):
            return kwargs['answer_channel'](task, 'law', {}, None)
        def course_verdict(self, *args, **kwargs):
            raise AssertionError('no teacher-output hook allowed')
        def _u_verdict(self, task, law, right, source):
            self.bit = (right, source)
        def _u_on(self, name):
            return name == 'inner_judge'
    original = Engine.live
    original_verdict = Engine.course_verdict
    mind = SimpleNamespace(engine=Engine())
    monkeypatch.setattr(ONE.Sera, 'course_verdict', lambda engine, *a: setattr(engine, 'base', a))
    with UC.answer_seam(mind, lambda *a: dict(right=False, source='test2'), 'test2'):
        assert mind.engine.live(None)['right'] is False
        assert 'live' not in mind.engine.__dict__
        mind.engine.course_verdict(None, 'law', False, 'test2', True)
        assert mind.engine.bit == (False, 'teacher')
        assert mind.engine.base[-1] is False
    assert Engine.live is original and Engine.course_verdict is original_verdict


def test_revisit_until_right_and_single_exam_attempt(monkeypatch, tmp_path):
    clock = Clock()
    backend = Backend(clock)
    seen, counts = [], {}
    def attempt(b, world, phase, wall, seed, corrected=False, reliability=True):
        identity = (phase, world.data[0][0])
        n = counts.get(identity, 0)+1
        counts[identity] = n
        seen.append(identity)
        clock.value += 1.
        b.field.tasks += 1
        status = 'not-yet' if identity[1] % 10 == 1 and n == 1 else 'right'
        return dict(status=status, observations=world.data)
    monkeypatch.setattr(UC, 'attempt', attempt)
    monkeypatch.setattr(UC, 'runner_identity', lambda: 'runner')
    result = UC.run(tmp_path, hours=.02, task_wall=1., batches=0, plan=plan(),
                    backend_factory=lambda: backend, clock=clock)
    for p in ('lesson', 'study', 'test2'):
        selected = [i[1] % 10 for i in seen if i[0] == p]
        assert selected == [1, 2, 1]
        item = result['phases'][p]['items'][0]
        assert item['attempts_to_right'] == 2 and item['time_to_right'] == 2.
    assert [r['attempts'] for r in result['phases']['test3']['items']] == [1, 1]
    before = len(seen)
    UC.run(tmp_path, hours=.02, task_wall=1., batches=0, plan=plan(),
           backend_factory=lambda: backend, clock=clock)
    assert len(seen) == before
    ledger = [json.loads(line) for line in (tmp_path/'LEDGER.jsonl').read_text().splitlines()]
    assert [(r['phase'], r['boundary']) for r in ledger] == [(p, edge) for p in UC.ORDER for edge in ('enter', 'leave')]
    assert all(set(r['crutches']) == set(CR.REGISTRY) for r in ledger)
    for row in ledger:
        for name, entry in row['crutches'].items():
            assert entry['teacher_weight'] == (UC.WEIGHTS[row['phase']] if CR.REGISTRY[name]['status'] == 'taught' else None)
    assert 'not measured' in LEDGER.run_ledger(tmp_path)


def test_port_budget_miss_is_revisited_not_a_run_stop(monkeypatch, tmp_path):
    clock, backend = Clock(), Backend()
    hits = []
    def attempt(b, world, phase, wall, seed, **kwargs):
        clock.value += 1
        hits.append((phase, world.data[0][0]))
        if phase == 'lesson' and hits.count(('lesson', 1)) == 1:
            raise PortBudget('stub port miss')
        return dict(status='right', observations=world.data)
    monkeypatch.setattr(UC, 'attempt', attempt)
    result = UC.run(tmp_path, hours=.02, task_wall=1., batches=0, plan=plan(),
                    backend_factory=lambda: backend, clock=clock)
    assert result['complete'] and not result['stop']
    assert result['phases']['lesson']['items'][0]['attempts'] == 2
    first = UC.committed_units(tmp_path, UC.read(tmp_path/'STATE.json'))[0]
    assert first['failure']['kind'] == 'port-budget'


def test_fade_only_teacher_statistics_and_new_demonstrations():
    loop = PH.NotYetWays()
    features = np.ones(67)
    loop.demonstrate('kind', features, ('answer', 'method'), 'method')
    loop.choice_learn('kind', 'answer', features, 1.)
    before_learned = copy.deepcopy(loop.choice_stats)
    field = SimpleNamespace(loop=loop, u7_words=(1, 2))
    initial = [a.copy() for a in UC.teacher_arrays(field)]
    UC.fade(field, 1., .6)
    assert all(np.array_equal(a, b*.6) for a, b in zip(UC.teacher_arrays(field), initial))
    for key in before_learned:
        assert all(np.array_equal(a, b) for a, b in zip(loop.choice_stats[key], before_learned[key]))
    UC.fade(field, .6, 0.)
    assert all(not a.any() for a in UC.teacher_arrays(field)) and field.u7_words == ()
    with UC.evidence_weight(.25):
        loop.demonstrate('kind', features, ('answer', 'method'), 'answer')
    assert np.allclose(loop.choice_taught[('kind', 'answer')][0], .25*np.outer(features, features))
    with UC.evidence_weight(0.):
        empty = PH.StepField()
        empty.teach(np.ones(empty.d), 1.)
    assert not empty.At.any() and not empty.bt.any()


def test_no_taught_ways_keeps_separate_not_yet_demonstration():
    steps, loop = PH.StepField(), PH.NotYetWays()
    with UC.evidence_weight(.6, taught_ways=False):
        steps.teach(np.ones(steps.d), 1.)
        loop.demonstrate('kind', np.ones(67), ('answer', 'method'), 'method')
    assert not steps.At.any() and not steps.bt.any()
    assert loop.choice_taught[('kind', 'method')][0].any()


def test_only_retired_switch_forced_and_all_ablation_sets():
    CR.OFF.add('memory_layer_b')
    UC.retire_lesson_words()
    assert CR.OFF == {'lesson_words', 'memory_layer_b'}
    for arm in BO.ARMS:
        with BO.arm_environment(arm):
            if arm == 'Phi':
                assert CR.on('lesson_words')
            else:
                assert not CR.on('lesson_words')
            assert CR.on('judge_scrutiny') == (arm == 'U-scrutiny')
            if arm.startswith('U'):
                mask = UC.u_switches(BO.ABLATIONS.get(arm, ()))
                assert mask['taught_not_yet'] == (arm != 'U-no-not-yet')
                assert mask['abstain_bar'] == (arm == 'U-no-not-yet')
                for name in BO.ABLATIONS.get(arm, ()):
                    assert not mask[name]
    assert CR.OFF == {'lesson_words', 'memory_layer_b'}


def test_native_unsupported_port_is_explicit_without_constructing_owner():
    native = object.__new__(BO.NativeBackend)
    native.field = BO.NativeAccount()
    world = TS.Exact('code', 'list', lambda x: x, {'x': 'list'}, 'list',
                     [((1,), (1,))], [(2,)], lambda rng: (3,))
    unit = UC.attempt(native, world, 'test3', 1., 3)
    assert unit['status'] == 'not-yet' and unit['unsupported'] and unit['feedback'] is None


def test_phi_calls_literal_s27_engine_and_keeps_legacy_default(monkeypatch):
    backend = object.__new__(BO.PhiBackend)
    backend.engine = object()
    seen = []
    def live(engine, world, phase, deadline, seed, corrected=False):
        seen.append((engine, world, phase, CR.on('lesson_words')))
        return dict(status='abstained', response="I don't know", feedback=None)
    monkeypatch.setattr(BO.C, 'live', live)
    world = task()
    with BO.arm_environment('Phi'):
        unit = UC.attempt(backend, world, 'test3', 1., 3)
    assert seen == [(backend.engine, world, 'test3', True)]
    assert unit['status'] == 'not-yet' and unit['response'] == "I don't know"


def test_rsi_port_misses_preserve_all_generations(monkeypatch, tmp_path):
    saved = []
    monkeypatch.setattr(UC, 'commit', lambda out, backend, state, unit=None: saved.append(unit))
    monkeypatch.setattr(UC.RSI, 'build_task', lambda spec: task())
    def miss(*args, **kwargs):
        raise PortBudget('stub RSI miss')
    suite = dict(wake=[{}], assessment=[dict(source='reserved-source')], reserved=['reserved-family'])
    state = dict(rsi_suite=suite, spent={'rsi': 0.}, committed=[])
    backend = object.__new__(UC.UBackend)
    backend.mind = SimpleNamespace(live=miss, scope=nullcontext, train=miss,
                                  assess=lambda *a, **k: dict(solved=False),
                                  sleep=SimpleNamespace(abstract=miss, dream=miss, replay=[object()]))
    UC.rsi_phase(tmp_path, backend, state, 100., 1., 1, clock=lambda: 0.)
    assert backend.mind.sleep.reserved == {'reserved-family'}
    assert backend.mind.sleep.reserved_sources == {'reserved-source'}
    assert [u['generation'] for u in saved if u['measure'] == 'rsi'] == [0, 1, 2, 3]
    assert len([u for u in saved if u.get('work') == 'wake' and u['failure']]) == 3
    assert all(u['port_misses']['abstract'] and u['port_misses']['dream']
               for u in saved if u.get('work') == 'abstract-dream')
    assert len([u for u in saved if u.get('work') == 'train' and u['failure']]) == 3


def test_baseline_rsi_wake_port_miss_is_an_item_record(monkeypatch, tmp_path):
    saved = []
    monkeypatch.setattr(UC, 'commit', lambda out, backend, state, unit=None: saved.append(unit))
    monkeypatch.setattr(BO.RSI, 'build_task', lambda spec: task())
    monkeypatch.setattr(BO.time, 'time', lambda: 0.)
    def attempt(backend, world, phase, *args):
        if phase == 'study':
            raise PortBudget('baseline wake miss')
        return dict(status='not-yet')
    monkeypatch.setattr(UC, 'attempt', attempt)
    backend = SimpleNamespace(kind='Phi', seed=3, snapshot=lambda: SimpleNamespace())
    state = dict(rsi_suite=dict(wake=[{}], assessment=[{}]), spent={'rsi': 0.}, committed=[])
    BO.baseline_rsi(backend, tmp_path, state, 100., 1., 0)
    assert len([u for u in saved if u['measure'] == 'rsi']) == 4
    wakes = [u for u in saved if u.get('work') == 'wake']
    assert len(wakes) == 3 and all(u['record']['failure']['kind'] == 'port-budget' for u in wakes)


def saved_course(path, course_plan, status='right'):
    (path/'units').mkdir(parents=True)
    state = dict(protocol={}, plan=course_plan, committed=[], finished=list(UC.ORDER),
                 spent={p: 1. for p in UC.ORDER}, budgets={p: 2. for p in UC.ORDER},
                 rsi_suite={}, dictionary={}, settings={k: False for k in CR.REGISTRY}, ledger=[])
    row = course_plan['test3'][0]
    unit = dict(item_id=row['id'], unit_id='saved', input_digest=row['digest'], phase='test3',
                status=status, attempt_wall=1., phase_elapsed=1.)
    UC.C.write_json(path/'units'/'saved.json', unit)
    state['committed'] = [dict(id='saved', sha256=UC.sha(path/'units'/'saved.json'))]
    UC.C.write_json(path/'STATE.json', state)
    return state


def test_report_rebuilds_from_committed_units_and_rejects_corruption(tmp_path):
    pp = UC.public_plan(plan())
    saved_course(tmp_path, pp)
    UC.C.write_json(tmp_path/'COURSE.json', dict(invented_result=999))
    UC.C.write_json(tmp_path/'units'/'orphan.json', dict(status='right'))
    result = UC.report(tmp_path)
    assert result['phases']['test3']['counts']['right'] == 1
    assert result['phases']['test3']['counts']['not reached'] == 1
    assert result['phases']['test3']['items'][0]['time_to_right'] == 1.
    (tmp_path/'units'/'saved.json').write_text('{}')
    with pytest.raises(ValueError, match='committed unit'):
        UC.report(tmp_path)


def test_bakeoff_saved_reports_require_identical_actual_input_digests(tmp_path):
    pp = UC.public_plan(plan())
    frozen = dict(course=pp, lists={}, arc={}, talk=[], inputs_digest='same')
    suite_path = tmp_path/'suite.json'
    UC.C.write_json(suite_path, frozen)
    roots = []
    for arm, actual in (('F', 'input-a'), ('U', 'input-a')):
        root = tmp_path/arm
        roots.append(root)
        saved_course(root/'course', pp)
        (root/'units').mkdir()
        unit = dict(unit_id='world-test3-000', measure='unseen-number', status='right',
                    input_digest=actual, wall=2., peak_mb=10.)
        UC.C.write_json(root/'units'/'world-test3-000.json', unit)
        UC.C.write_json(root/'ARM.json', dict(protocol=dict(arm=arm, suite_sha256=UC.sha(suite_path), inputs_digest='same'),
                    evaluations=[dict(id='world-test3-000', sha256=UC.sha(root/'units'/'world-test3-000.json'))], finished=False))
    result = BO.report(tmp_path/'report', suite_path, roots)
    assert not result['complete'] and result['arms']['U']['measures']['unseen-number']['N'] == 2
    assert (tmp_path/'report'/'BAKEOFF.json').exists()
    assert '| U |' in (tmp_path/'report'/'BAKEOFF.md').read_text()
    upath = roots[1]/'units'/'world-test3-000.json'
    unit = UC.read(upath)
    unit['input_digest'] = 'input-b'
    UC.C.write_json(upath, unit)
    arm_state = UC.read(roots[1]/'ARM.json')
    arm_state['evaluations'][0]['sha256'] = UC.sha(upath)
    UC.C.write_json(roots[1]/'ARM.json', arm_state)
    with pytest.raises(ValueError, match='Different actual inputs'):
        BO.report(tmp_path/'report', suite_path, roots)


def test_stop_records_traceback_and_committed_attempt_survives(monkeypatch, tmp_path):
    clock, backend = Clock(), Backend()
    n = [0]
    def attempt(b, world, phase, wall, seed, **kwargs):
        n[0] += 1
        if n[0] == 2:
            raise RuntimeError('stub stop')
        clock.value += 1
        return dict(status='right', observations=world.data)
    monkeypatch.setattr(UC, 'attempt', attempt)
    with pytest.raises(RuntimeError, match='stub stop'):
        UC.run(tmp_path, hours=.02, task_wall=1., batches=0, plan=plan(),
               backend_factory=lambda: backend, clock=clock)
    state = UC.read(tmp_path/'STATE.json')
    assert len(state['committed']) == 1
    assert 'RuntimeError' in state['stop']['traceback']
    assert len(UC.committed_units(tmp_path, state)) == 1


def test_checkpoint_failure_cannot_commit_an_orphan_unit(monkeypatch, tmp_path):
    clock, backend = Clock(), Backend()
    saves = [0]
    original_save = backend.save
    def save(path):
        saves[0] += 1
        if saves[0] == 3:  # initial state, phase entry, then first unit commit
            raise OSError('checkpoint write interrupted')
        original_save(path)
    monkeypatch.setattr(backend, 'save', save)
    def attempt(b, world, phase, wall, seed, **kwargs):
        clock.value += 1.
        b.field.tasks += 1
        return dict(status='right', observations=world.data)
    monkeypatch.setattr(UC, 'attempt', attempt)
    with pytest.raises(OSError, match='checkpoint write interrupted'):
        UC.run(tmp_path, hours=.02, task_wall=1., batches=0, plan=plan(),
               backend_factory=lambda: backend, clock=clock)
    state = UC.read(tmp_path/'STATE.json')
    assert not state['committed'] and UC.committed_units(tmp_path, state) == []
    assert (tmp_path/'units'/'lesson-000-a0001.json').is_file()
    assert UC.sha(tmp_path/state['checkpoint']) == state['checkpoint_sha256']
    backend.load(tmp_path/state['checkpoint'])
    assert backend.field.tasks == 0
