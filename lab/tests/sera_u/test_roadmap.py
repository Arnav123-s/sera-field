"""U13 CPU contracts. Existing suites remain untouched; costly seams are stubbed."""
import copy
import json
import math
import pickle
import random
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, phi as PH
from sera_u import SeraU
from sera_u.discovery import CRUTCHES as U9, Certification, Discovery, WorldView, generation_report
from sera_u.einstein import CRUTCHES as U10, Einstein, nodes
from sera_u.scientists import CRUTCHES as U11, Scientists
from sera_u.darwin import CRUTCHES as U12, Darwin
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import Engine, arm_settings
from sera_u.ports import TaskView, digest
from sera_u.proposer import legal
from sera_u.roadmap import CRUTCHES, Roadmap, RoadmapMethods, checked_operation, signed_order
from sera_u.sleep import Receipt, expand, independent, substitute
from scripts import sera_u_roadmap as observer
from scripts import sera_u_discovery as base_observer
from tests.sera_u.test_scientists import Pool, read, var


@pytest.fixture(autouse=True)
def defaults(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


def switches(**overrides):
    return {**dict.fromkeys(CRUTCHES, True), **overrides}


def entity(habits=None, *, ancestors=False):
    settings = arm_settings('full')
    settings.update(memory_layer_a=False, memory_layer_b=False)
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=settings,
        discovery=dict.fromkeys(U9, True), einstein=dict.fromkeys(U10, ancestors),
        scientists=dict.fromkeys(U11, ancestors), darwin=dict.fromkeys(U12, ancestors), roadmap=habits)


def stub(habits=None):
    field = PH.Field(3)
    learner = SimpleNamespace(field=field, random=random.Random(3), numpy=np.random.default_rng(3),
        engine=SimpleNamespace(_u_reads=read), crutches=dict(sleep_library=True),
        proposer=SimpleNamespace(admitted=lambda table: table, changed=lambda: None),
        sleep=SimpleNamespace(replay=[], reserved=set(), reserved_sources=set()))
    discovery = Discovery(dict.fromkeys(U9, True), einstein=dict.fromkeys(U10, False),
        scientists=dict.fromkeys(U11, False), darwin=dict.fromkeys(U12, False), roadmap=habits or switches())
    discovery.register_worlds((WorldView('w0', 'exact'), WorldView('w1', 'exact')))
    learner.discovery = discovery
    discovery.roadmap.attach(field)
    return learner, discovery, discovery.roadmap


def cheap_ticks(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', lambda self, views, concepts=None: read(views))
    monkeypatch.setattr(Discovery, 'propose', lambda *args: ())
    monkeypatch.setattr(Einstein, 'run', lambda *args, **kwargs: ([], dict(doubt=0.), []))
    monkeypatch.setattr(Einstein, 'target', lambda *args: None)
    monkeypatch.setattr(Scientists, 'run', lambda *args, **kwargs: ([], {}, [], None))
    monkeypatch.setattr(Scientists, 'feedback', lambda *args, **kwargs: None)
    monkeypatch.setattr(Darwin, 'run', lambda *args, **kwargs: ([], {}, False, np.zeros(65)))
    monkeypatch.setattr(Darwin, 'feedback', lambda *args: None)
    monkeypatch.setattr('sera_u.discovery.time.perf_counter', lambda: 10.)
    monkeypatch.setattr('sera_u.discovery.time.time', lambda: 100.)
    monkeypatch.setattr(RoadmapMethods, 'choose', lambda *args: [('rough_estimates',)])


def test_default_off_is_exact_u12_path(monkeypatch):
    for name in CRUTCHES:
        assert not CR.on(name)
        assert name not in CR.settings()['crutches_effective']
    implicit, explicit = entity(ancestors=True), entity(dict.fromkeys(CRUTCHES, False), ancestors=True)
    assert not hasattr(implicit.discovery, 'roadmap')
    assert not hasattr(implicit.field, 'roadmap_readout')
    assert implicit._payload().keys() == explicit._payload().keys()
    assert implicit.learning_hash() == explicit.learning_hash()
    cheap_ticks(monkeypatch)
    for _ in range(3):
        assert implicit.discover(Pool()) == explicit.discover(Pool())
        assert implicit.learning_hash() == explicit.learning_hash()
    assert implicit.numpy.bit_generator.state == explicit.numpy.bit_generator.state
    assert pickle.dumps(implicit.discovery.learning_state()) == pickle.dumps(explicit.discovery.learning_state())
    assert generation_report(implicit.discovery.events) == generation_report(explicit.discovery.events)


@pytest.mark.parametrize('missing', CRUTCHES)
def test_each_switch_removes_only_its_habit(missing):
    learner, discovery, controller = stub(switches(**{missing: False}))
    assert controller.methods.candidates() == [('observe',)] + [(key,) for key in CRUTCHES if key != missing]
    if missing == 'own_operations':
        controller.wish(('num', 'num'), 'w0')
        assert controller.wishes == {}
        assert controller.build(learner, deadline=math.inf) == 0.
    elif missing == 'rederive_concepts':
        assert controller.rebuild(learner, discovery, object(), deadline=math.inf) == 0.
        assert controller.rebuilds == {}
    else:
        assert controller.predict(learner, discovery, 'w0', ('ask', 1)) is None
        assert controller.estimates == []


def acquired_receipts(learner):
    part = LG.node('add', var(), LG.node('one'))
    base = LG.node('mul', part, part)
    for index in range(2):
        program = LG.node('add', base, LG.node('lit', payload=index+2))
        rows = tuple((((('x', x),)), independent(program, {'x': x}, {})) for x in (-2, -1, 1, 3))
        view = TaskView((('x', 'num'),), 'num', rows)
        receipt = Receipt.make(view, (program,), {}, scope='exact-audit', origin='taught', source='own-'+str(index))
        learner.sleep.replay.append((receipt, {}))
    return part


def test_new_operation_requires_repeated_wish_and_received_sources():
    learner, _, controller = stub()
    acquired_receipts(learner)
    controller.wish(('num', 'num'), 'w0')
    assert controller.build(learner, deadline=math.inf) == 0.
    assert learner.field.concepts == []
    controller.wish(('num', 'num'), 'w1')
    controller.build(learner, deadline=math.inf)
    admitted = [entry for entry in controller.operations.values() if entry['admitted']]
    assert len(admitted) == 1
    c = learner.field.concepts[-1]
    assert all(part[0] in LG.INNATE or part[0] in ('var', 'lit', 'lam') for part in nodes(c['body']))
    table = learner.field.concept_table()
    assert c['id'] in learner.field.proven_ideas()
    assert any(p.sym == 'c' and p.pay == c['id'] for p in legal('num', {'x': 'num'}, table, (), ('num',)))
    expanded = expand(LG.node('c', var(), payload=c['id']), table)
    assert independent(expanded, {'x': 7}, {}) == LG.evaluate(expanded, {'x': 7}, {})
    assert admitted[0]['certificate']['kind'] == 'exact checked substitution'
    assert len(admitted[0]['certificate']['sources']) == 2


@pytest.mark.parametrize('failure', ('independent', 'substitution', 'checked-test'))
def test_operation_failure_is_atomic(monkeypatch, failure):
    learner, _, controller = stub()
    acquired_receipts(learner)
    controller.wish(('num', 'num'), 'w0')
    controller.wish(('num', 'num'), 'w1')
    if failure == 'independent':
        def refuse(*args, **kwargs):
            raise ValueError('executor disagreement')
        monkeypatch.setattr('sera_u.roadmap.independent', refuse)
    elif failure == 'substitution':
        monkeypatch.setattr('sera_u.roadmap.rewrite', lambda program, candidate: program)
    else:
        def refuse_check(*args, **kwargs):
            raise ValueError('checked substitution failed')
        monkeypatch.setattr('sera_u.roadmap.checked_substitution', refuse_check)
    assert controller.build(learner, deadline=math.inf) == -1.
    assert learner.field.concepts == []
    assert not any(row['admitted'] for row in controller.operations.values())


def test_checked_operation_refuses_unknown_production_and_dangling_concept():
    with pytest.raises(ValueError):
        checked_operation(LG.node('new_semantics', var()), LG.node('var', payload='_'), ('num', 'num'), (1,), {}, 1)
    with pytest.raises(ValueError):
        checked_operation(LG.node('c', var(), payload=99), LG.node('var', payload='_'), ('num', 'num'), (1,), {}, 1)


def test_no_library_cannot_build_or_rebuild():
    learner, discovery, controller = stub()
    learner.crutches['sleep_library'] = False
    acquired_receipts(learner)
    controller.wish(('num', 'num'), 'w0')
    controller.wish(('num', 'num'), 'w1')
    assert controller.build(learner, deadline=math.inf) == 0.
    assert controller.rebuild(learner, discovery, object(), deadline=math.inf) == 0.
    assert learner.field.concepts == []


def test_primitives_reconstruction_audited_on_inputs_it_did_not_choose(monkeypatch):
    learner, discovery, controller = stub()
    simple = LG.node('add', var(), LG.node('one'))
    original = LG.node('if', LG.node('lt', var(), LG.node('lit', payload=9)), simple, LG.node('zero'))
    c = learner.field.invent(substitute(original, 'x', var('_')), ('num', 'num'), 'math', 'own-audit',
        LG.parts(original), extra=dict(proof={'record': 'original-certificate'}))
    before = copy.deepcopy(c)
    def hidden_search(tin, tout, own, concepts, **kwargs):
        assert concepts == {}
        assert all(y == x+1 for x, y in own)
        assert 'body' not in kwargs
        return [simple], dict(nodes=5, seconds=0., solved=True, size=3)
    monkeypatch.setattr('sera_u.roadmap.search_cost', hidden_search)
    class Audit:
        def audit_relation(self, lhs, rhs, tin, tout, concepts, own):
            assert 53 not in [x for x, _ in own]
            assert independent(lhs, {'x': 53}, concepts) != independent(rhs, {'x': 53}, {})
            return Certification(False, 'formula', (('audit_n', 1),), 'fresh-refutation', True)
    assert controller.rebuild(learner, discovery, Audit(), deadline=math.inf) == -1.
    assert learner.field.concepts == [before]
    row = next(iter(controller.rebuilds.values()))
    assert row['body_hidden'] and row['primitives_only'] and row['audited']
    assert not row['kept'] and row['original_preserved']


def test_better_rebuild_keeps_original_certificate_and_learns_later_reuse(monkeypatch):
    learner, discovery, controller = stub()
    simple = LG.node('add', var(), LG.node('one'))
    original = LG.node('add', simple, LG.node('zero'))
    c = learner.field.invent(substitute(original, 'x', var('_')), ('num', 'num'), 'math', 'own-audit',
        LG.parts(original), extra=dict(proof={'record': 'original-certificate'}))
    before = copy.deepcopy(c)
    seen = []
    def search(tin, tout, own, table, *, label, **kwargs):
        seen.append((label, copy.deepcopy(table)))
        return [simple], dict(nodes=20 if label[0] == 'original' else 5, seconds=.001, solved=True, size=3)
    monkeypatch.setattr('sera_u.roadmap.search_cost', search)
    class Audit:
        def audit_relation(self, lhs, rhs, tin, tout, table, own):
            assert all(independent(lhs, {'x': x}, table) == independent(rhs, {'x': x}, {}) for x in (53, -51))
            return Certification(True, 'formula', (('audit_n', 2),), 'fresh-sampled')
    controller.rebuild(learner, discovery, Audit(), deadline=math.inf)
    row = next(iter(controller.rebuilds.values()))
    assert seen[0][1] == {}
    assert row['kept'] and row['audited']
    assert row['evidence'] == 'sampled equivalence, not proof'
    assert row['composition']['rebuilt']['nodes'] < row['composition']['original']['nodes']
    assert learner.field.concepts[0] == before
    assert learner.field.concepts[0]['proof']['record'] == 'original-certificate'
    program = LG.node('c', var(), payload=row['concept'])
    controller.reused(program, 'later-world')
    controller.reused(program, 'later-world')
    assert row['reuse'] == 1
    controller.reused(LG.node('c', var(), payload=c['id']), 'original-later-world')
    assert row['original_reuse'] == 1
    from sera_u.proposer import Proposer
    proposer = Proposer.__new__(Proposer)
    proposer.field = learner.field
    active = proposer.admitted(learner.field.concept_table())
    assert c['id'] in active and c['id'] not in active['_sig']
    assert row['concept'] in active['_sig']
    assert independent(LG.node('c', var(), payload=c['id']), {'x': 53}, active) == 54
    assert ('roadmap', ('rederive_concepts',)) in controller.methods.stats


def test_later_operation_cost_uses_paired_searches_and_old_basis(monkeypatch):
    learner, discovery, controller = stub()
    acquired_receipts(learner)
    controller.wish(('num', 'num'), 'w0')
    controller.wish(('num', 'num'), 'w1')
    discovery.observations['w1'] = [(x, x+1) for x in range(4)]
    controller.build(learner, deadline=math.inf)
    controller.serial += 1
    entry = next(row for row in controller.operations.values() if row['admitted'])
    discovery.observations['w0'] = [(x, x+1) for x in (0, 1, 2, 3)]
    tables = []
    def search(tin, tout, own, table, **kwargs):
        tables.append(copy.deepcopy(table))
        return [], dict(nodes=10 if len(tables) == 1 else 4, seconds=.01, solved=True, size=3)
    monkeypatch.setattr('sera_u.roadmap.search_cost', search)
    controller.later_search(learner, discovery, 'w1', deadline=math.inf)
    assert tables == []
    controller.later_search(learner, discovery, 'w0', deadline=math.inf)
    assert entry['later'][0]['new_composition']
    assert entry['concept'] not in tables[0]
    assert entry['concept'] in tables[1]
    assert entry['later'][0]['nodes_cut'] == 6
    assert ('roadmap', ('own_operations',)) in controller.methods.stats


def test_signed_orders_and_finite_interval():
    assert signed_order(0) == 0.
    assert signed_order(-99) == -2.
    assert signed_order(999) == 3.
    with pytest.raises(ValueError):
        signed_order(math.inf)
    learner, discovery, controller = stub()
    pid = controller.predict(learner, discovery, 'w0', ('ask', -1))
    assert pid == 0 and controller.estimates[0]['result'] is None
    assert all(math.isfinite(v) for v in controller.estimates[0]['signed_log_interval'])
    controller.settle(pid, (-1, -99))
    with pytest.raises(ValueError):
        controller.settle(pid, (-1, -99))


def test_calibration_earns_then_loses_pruning_with_real_results():
    learner, discovery, controller = stub()
    assert not controller.calibrated()
    for _ in range(12):
        pid = controller.predict(learner, discovery, 'w0', ('ask', 0))
        controller.settle(pid, (0, 1))
    assert controller.calibrated()
    precision = controller.precision.copy()
    for _ in range(12):
        pid = controller.predict(learner, discovery, 'w0', ('ask', 0))
        controller.settle(pid, (0, -10**12))
    assert not controller.calibrated()
    assert not np.array_equal(precision, controller.precision)
    assert controller.report()['calibration']['coverage'] < .8


def test_no_pruning_before_calibration_and_every_recovered_error_is_recorded():
    learner, discovery, controller = stub()
    good, wrong = LG.node('add', var(), LG.node('one')), LG.node('zero')
    controller.predict(learner, discovery, 'w0', ('ask', 2))
    original, trial = controller.order(learner, discovery, 'w0', (good, wrong))
    assert original == (good, wrong) and trial is None
    controller.errors = [(True, 0.)]*12
    controller.estimates[-1]['signed_log_interval'] = (-.1, .1)
    controller.estimate_choice.pick = lambda *args: 'prune'
    ordered, trial = controller.order(learner, discovery, 'w0', (good, wrong))
    assert ordered == (wrong,) and trial['original'] == (good, wrong) and trial['fallback']
    controller.checked(trial, wrong, Certification(False, 'formula', (('audit_n', 1),), 'bad'))
    controller.checked(trial, good, Certification(True, 'formula', (('audit_n', 1),), 'correct'))
    assert len(controller.mistakes) == 1
    assert controller.mistakes[0]['recovered_by_fallback']
    assert controller.mistakes[0]['record'] == 'correct'


def test_estimate_precedes_actual_act_and_exact_resume(monkeypatch):
    cheap_ticks(monkeypatch)
    learner = entity(switches())
    class BeforeAct(Pool):
        def act(self, wid, action):
            estimate = learner.discovery.roadmap.estimates[-1]
            assert estimate['action'] == action and estimate['result'] is None
            return super().act(wid, action)
    learner.discover(BeforeAct())
    assert learner.discovery.roadmap.estimates[-1]['result'] is not None
    restored = SeraU.loads(learner.dumps())
    assert restored.field.roadmap_readout is restored.discovery.roadmap
    assert restored.field.roadmap_methods is restored.discovery.roadmap.methods
    assert restored.learning_hash() == learner.learning_hash()
    assert learner.discover(Pool()) == restored.discover(Pool())
    assert restored.learning_hash() == learner.learning_hash()
    assert learner.numpy.bit_generator.state == restored.numpy.bit_generator.state


def test_failed_unit_rolls_back_estimate_and_field_alias(monkeypatch):
    cheap_ticks(monkeypatch)
    learner = entity(switches())
    before = learner.learning_hash()
    class Broken(Pool):
        def act(self, wid, action):
            raise RuntimeError('failed act')
    with pytest.raises(RuntimeError):
        learner.discover(Broken())
    assert learner.learning_hash() == before
    assert learner.field.roadmap_readout is learner.discovery.roadmap
    assert learner.discovery.roadmap.estimates == []


def test_learning_hash_ignores_elapsed_diagnostics(monkeypatch):
    cheap_ticks(monkeypatch)
    learner = entity(switches())
    learner.discover(Pool())
    controller = learner.discovery.roadmap
    before = learner.learning_hash()
    controller.estimates[-1]['recorded_at'] += 1000.
    controller.estimates[-1]['performed_at'] += 2000.
    controller.costs['own_operations'] += 888.
    controller.searches.append(dict(seconds=123.))
    controller.operations['diagnostic'] = dict(admitted=False, seconds=1., seconds_cut=2.)
    with_diagnostic = learner.learning_hash()
    controller.operations['diagnostic']['seconds'] = 1234.
    controller.operations['diagnostic']['seconds_cut'] = -555.
    assert learner.learning_hash() == with_diagnostic
    del controller.operations['diagnostic']
    assert learner.learning_hash() == before


def test_teacher_phase_fading_and_untaught_rejection():
    learner, discovery, controller = stub()
    view = TaskView((('x', 'num'),), 'num', (((('x', 0),), 1),))
    for origin, phase in (('explore', 'lesson'), ('assessment', 'test1'), ('taught', 'test2'), ('taught', 'test3')):
        with pytest.raises(ValueError):
            controller.demonstrate(learner, view, origin=origin, phase=phase)
    assert controller.demonstrate(learner, view, origin='taught', phase='lesson') == CRUTCHES
    key = ('roadmap', ('own_operations',))
    a = controller.methods.taught[key][0].copy()
    controller.methods.end_task()
    assert np.allclose(controller.methods.taught[key][0], a*PH.TAUGHT_FADE)
    controller.phase('rsi')
    assert np.allclose(controller.methods.taught[key][0], a*PH.TAUGHT_FADE*.4)
    controller.phase('test3')
    assert not controller.methods.taught[key][0].any()


def test_report_is_strict_json_and_histories_are_bounded():
    learner, discovery, controller = stub()
    for _ in range(132):
        pid = controller.predict(learner, discovery, 'w0', ('ask', 0))
        controller.settle(pid, (0, 1))
    assert len(controller.estimates) == 128
    assert len(controller.errors) == 32
    assert len(controller.report()['estimates']) == 4
    assert controller.report()['estimate_counts']['settled'] == 132
    json.dumps(controller.report(), allow_nan=False)


def test_roadmap_freeze_is_disjoint_deterministic_and_never_taught(monkeypatch):
    program = LG.node('add', var(), LG.node('one'))
    baseline = dict(schema=base_observer.SCHEMA, split='fixture', worlds=[dict(
        id='old', form='exact', tin='num', tout='num', seed=3, index=1,
        program=program, family=observer.family(program, {}))])
    monkeypatch.setattr(observer, 'freeze_lineage', lambda *args: copy.deepcopy(baseline))
    suite = {label: [] for label in ('retention', 'wake', 'assessment')}
    manifest = observer.freeze_roadmap(None, suite, 3)
    assert manifest == observer.freeze_roadmap(None, suite, 3)
    assert manifest['roadmap_suite'] == observer.SCHEMA
    assert {row['observer_habit'] for row in manifest['worlds'] if 'observer_habit' in row} == set(CRUTCHES)
    assert all('given' not in row for row in manifest['worlds'])
    pending = [row for row in manifest['worlds'] if row.get('observer_requires')]
    assert pending and all(len(row['observer_requires']) == 2 for row in pending)
    scales = [row for row in manifest['worlds'] if row.get('observer_habit') == 'rough_estimates' and row['tin'] == 'num']
    values = [independent(row['program'], {'x': 1}, {}) for row in scales]
    assert min(values) < 0 < max(values) and max(map(abs, values)) >= 10000


def test_later_worlds_hidden_and_public_interface_has_no_category(monkeypatch):
    pool = observer.RoadmapPool.__new__(observer.RoadmapPool)
    pool.specs = {'seed': {}, 'later': {'observer_requires': ('seed',), 'observer_habit': 'own_operations'}}
    pool.met_certified = set()
    monkeypatch.setattr(observer.LineagePool, 'public', lambda self: (WorldView('seed', 'exact'), WorldView('later', 'exact')))
    assert [world.id for world in pool.public()] == ['seed']
    pool.met_certified.add('seed')
    assert [world.id for world in pool.public()] == ['seed', 'later']
    assert all(set(world.__dict__) == set(WorldView('seed', 'exact').__dict__) for world in pool.public())


def test_comparison_rejects_false_credit_and_keeps_censored_controls(monkeypatch, tmp_path):
    case = tmp_path/'u-darwin'
    case.mkdir()
    state = dict(protocol={'discovery': {}}, discovery_generations=[])
    (case/'state.json').write_text(json.dumps(state), encoding='utf-8')
    (case/'observer-discovery.json').write_text('{}', encoding='utf-8')
    monkeypatch.setattr(observer, 'validate_roadmap', lambda manifest: manifest)
    monkeypatch.setattr(observer, 'compare_lineage', lambda paths: dict(cases={case.name: {'completed': False}},
        zero_false_credit=False, false_credit=1, limits='censored'))
    result = observer.compare_runs([case])
    assert not result['zero_false_credit'] and result['false_credit'] == 1
    assert result['cases'][case.name]['roadmap'] == {} and result['cases'][case.name]['u13_control']
    assert not result['cases'][case.name]['completed']


def test_dangling_acquired_definition_is_refused_before_execution(monkeypatch):
    learner, discovery, controller = stub()
    body = LG.node('c', var('_'), payload=999)
    c = learner.field.invent(body, ('num', 'num'), 'math', 'old-ablation', LG.parts(body))
    original = copy.deepcopy(c)
    def never_execute(*args, **kwargs):
        raise AssertionError('A dangling definition was executed')
    monkeypatch.setattr('sera_u.roadmap.LG.evaluate', never_execute)
    assert controller.rebuild(learner, discovery, SimpleNamespace(audit_relation=lambda *args: None), deadline=math.inf) == -1.
    assert learner.field.concepts == [original]


def test_real_tick_runs_unpruned_fallback_with_same_outer_judge(monkeypatch):
    cheap_ticks(monkeypatch)
    learner = entity(switches())
    discovery, controller = learner.discovery, learner.discovery.roadmap
    discovery.register_worlds(Pool().public())
    discovery.active = 'w0'
    discovery.observations['w0'] = [(x, x+1) for x in range(4)]
    discovery.policy.pick = lambda choices, *args: 'stay' if 'stay' in choices else sorted(choices)[0]
    good, wrong = LG.node('add', var(), LG.node('one')), LG.node('zero')
    monkeypatch.setattr(Discovery, 'propose', lambda *args: (good, wrong))
    monkeypatch.setattr(Discovery, 'experiment_menu', lambda *args: [dict(action=('ask', 2), predicted=None, info=0., surprise=0.)])
    monkeypatch.setattr(Discovery, 'transfer', lambda *args: [])
    controller.errors = [(True, 0.)]*12
    controller.estimate_choice.pick = lambda *args: 'prune'
    predict = controller.predict
    def narrow(*args):
        pid = predict(*args)
        controller.estimates[-1]['signed_log_interval'] = (-.1, .1)
        return pid
    controller.predict = narrow
    # Instance-bound test callbacks must not enter a checkpoint envelope.
    # Call the completed-unit engine seam directly here; rollback has its own test.
    audits = []
    class Judge(Pool):
        def certify(self, wid, p, concepts, rows, **kwargs):
            audits.append(p)
            assert p == good
            return Certification(True, 'formula', (('audit_n', 1),), 'unchanged-judge')
    with learner.scope():
        row = discovery.tick(learner, Judge())
    assert row['certified']['record'] == 'unchanged-judge'
    assert audits == [good]
    assert controller.mistakes[-1]['program'] == good
    assert controller.mistakes[-1]['recovered_by_fallback']


def test_all_off_lives_are_step_bounded_and_equal(monkeypatch):
    from sera import tasks as TS
    from sera_u.proposer import Proposer
    cheap_ticks(monkeypatch)
    monkeypatch.setattr('sera_u.mind.time.time', lambda: 100.)
    monkeypatch.setattr('sera_u.mind.time.process_time', lambda: 100.)
    program = LG.node('add', var(), LG.node('one'))
    monkeypatch.setattr(Proposer, 'beam', lambda *args, **kwargs: [program])
    monkeypatch.setattr(LG, 'search', lambda *args, **kwargs: [(program, 3)])
    monkeypatch.setattr(TS.Exact, 'verify', lambda *args: (True, 1, None))
    task = TS.Exact('math', 'bounded off parity', lambda x: x+1, {'x': 'num'}, 'num',
                    [-2, -1, 0, 1], [], lambda rng: int(rng.integers(-8, 9)))
    implicit = entity(ancestors=True)
    explicit = entity(dict.fromkeys(CRUTCHES, False), ancestors=True)

    def logical(value):
        # Measurements of the machine, not logical records: One Field on, the process peak moved 332.9 -> 333.5 MB.
        if isinstance(value, dict):
            return {k: logical(v) for k, v in value.items()
                    if k not in ('wall', 'time', 'seconds', 'timing', 'execution', 'peak_mb', 'memory_mb')}
        if isinstance(value, list):
            return [logical(v) for v in value]
        return value
    assert logical(implicit.live(copy.deepcopy(task), task_wall=math.inf, max_steps=2)) == logical(explicit.live(
        copy.deepcopy(task), task_wall=math.inf, max_steps=2))
    assert implicit.learning_hash() == explicit.learning_hash()


def test_checkpoint_restores_built_operation_and_audited_reconstruction(monkeypatch):
    learner = entity(switches())
    controller = learner.discovery.roadmap
    acquired_receipts(learner)
    controller.wish(('num', 'num'), 'w0')
    controller.wish(('num', 'num'), 'w1')
    controller.build(learner, deadline=math.inf)
    assert any(row['admitted'] for row in controller.operations.values())
    monkeypatch.setattr('sera_u.roadmap.search_cost', lambda *args, **kwargs: (
        [LG.node('zero')], dict(nodes=5, seconds=.01, solved=True, size=1)))
    class Audit:
        def audit_relation(self, *args):
            return Certification(False, 'formula', (('audit_n', 1),), 'saved-refutation', True)
    controller.rebuild(learner, learner.discovery, Audit(), deadline=math.inf)
    assert any(row['audited'] for row in controller.rebuilds.values())
    restored = SeraU.loads(learner.dumps())
    assert restored.learning_hash() == learner.learning_hash()
    assert restored.discovery.roadmap.operations.keys() == controller.operations.keys()
    assert restored.discovery.roadmap.report()['rebuilds'] == controller.report()['rebuilds']
    moment = dict(doubt=1., misfit=0., proven=1)
    candidates = {'observe'} | set(CRUTCHES)
    assert controller.methods.choose('roadmap', candidates, moment, learner.numpy) == restored.discovery.roadmap.methods.choose(
        'roadmap', candidates, moment, restored.numpy)
    assert restored.learning_hash() == learner.learning_hash()
