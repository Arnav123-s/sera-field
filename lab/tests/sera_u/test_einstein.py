"""U10 short CPU contracts; slow neural/world seams use stubs.

Written for development review to execute with PYTHONHASHSEED=0. Existing tests unchanged.
"""
import ast
import copy
import inspect
import math
import pickle
import random
from types import SimpleNamespace
import textwrap

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, phi as PH
from sera_u import SeraU
from sera_u.discovery import CRUTCHES as U9, Certification, Discovery, SCHEMA, WorldView, generation_report
from sera_u.einstein import CRUTCHES, Einstein, EinsteinMethods
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import Engine, arm_settings
from sera_u.ports import digest
from scripts import sera_u_einstein as observer
from scripts.sera_u_discovery import WorldPool, validate


@pytest.fixture(autouse=True)
def neutral(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


def switches(**overrides):
    return {**dict.fromkeys(CRUTCHES, True), **overrides}


def discovery(**overrides):
    d = Discovery(dict.fromkeys(U9, True), einstein=switches(**overrides))
    d.register_worlds(tuple(WorldView('w'+str(j), 'exact') for j in range(3)))
    return d


def x():
    return LG.node('var', payload='x')


def square():
    return LG.node('mul', x(), x())


def plus(p, n=1):
    return LG.node('add', p, LG.node('one') if n == 1 else LG.node('lit', payload=n))


def law(p, wid):
    return dict(hypothesis=p, form='exact', signature=('num', 'num'), bits=LG.bits(p, {}),
        kind='formula', coverage={wid: (100., 0.)}, certificates={}, features=np.zeros(65), concept_ids=[])


class Ideas:
    def __init__(self):
        self.bindings = []

    def bind(self, *args):
        self.bindings.append(args)


def reads(self, views, concepts=None):
    return [(torch.zeros(3, 64), torch.ones(3)/3) for _ in views]


def fast_entity():
    settings = arm_settings('full')
    settings.update(memory_layer_a=False, memory_layer_b=False)
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=settings,
                 discovery=dict.fromkeys(U9, True), einstein=switches())


def mind(concepts=None, *, not_yet=False):
    concepts = concepts or {}
    return SimpleNamespace(field=SimpleNamespace(concept_table=lambda: concepts,
        concepts=[], shapes=lambda: (), ideas=Ideas(), standing={}, tasks=0, revisit_queue=[]),
        engine=SimpleNamespace(_u_reads=lambda views: reads(None, views)),
        proposer=SimpleNamespace(memory=None), numpy=np.random.default_rng(3), random=random.Random(3),
        crutches=dict(sleep_library=False, taught_not_yet=not_yet, inner_judge=False))


class Pool:
    def __init__(self, d=None, *, refuse=None):
        self.acts, self.judges = [], []
        self.d, self.refuse = d, refuse
        self.private_law, self.private_world, self.private_audit = object(), object(), object()

    def public(self):
        return tuple(WorldView('w'+str(j), 'exact') for j in range(3))

    def act(self, wid, action):
        if self.d is not None and hasattr(self.d, 'einstein'):
            pending = [p for p in self.d.einstein.predictions if p['action'] == action and p['result'] is None]
            if pending:
                assert pending[-1]['recorded_at'] is not None
                assert pending[-1]['performed_at'] is None
        self.acts.append((wid, action))
        return action[1], action[1]+1

    def certify(self, wid, hyp, concepts, observations, *, library=()):
        self.judges.append((wid, hyp))
        return Certification(wid != self.refuse, 'formula', (('eps', .05),), digest((wid, hyp)))


def test_registered_default_off_and_absent_u9_state():
    for name in CRUTCHES:
        assert name in CR.REGISTRY and not CR.on(name)
        assert name not in CR.settings()['crutches_effective']
    a = Discovery(dict.fromkeys(U9, True))
    b = Discovery(dict.fromkeys(U9, True), einstein=dict.fromkeys(CRUTCHES, False))
    assert not hasattr(a, 'einstein') and not hasattr(b, 'einstein')
    assert pickle.dumps(a.learning_state()) == pickle.dumps(b.learning_state())
    config = NativeConfig(nodes=3, rounds=1)
    first = SeraU(3, config=config, discovery=dict.fromkeys(U9, True))
    second = SeraU(3, config=config, discovery=dict.fromkeys(U9, True), einstein=dict.fromkeys(CRUTCHES, False))
    assert first.learning_hash() == second.learning_hash()
    assert first._payload().keys() == second._payload().keys()
    assert not hasattr(second.field, 'einstein_methods')


def test_off_ticks_equal_u9_records_payload_state_and_hash(monkeypatch):
    monkeypatch.setattr('sera_u.discovery.time.perf_counter', lambda: 10.)
    monkeypatch.setattr(Discovery, 'propose', lambda *args: ())
    a = Discovery(dict.fromkeys(U9, True))
    b = Discovery(dict.fromkeys(U9, True), einstein=dict.fromkeys(CRUTCHES, False))
    ma, mb = mind(), mind()
    ra, rb = a.tick(ma, Pool()), b.tick(mb, Pool())
    assert ra == rb and 'einstein' not in ra and 'bold_prediction' not in ra
    assert pickle.dumps(a.learning_state()) == pickle.dumps(b.learning_state())
    assert ma.numpy.bit_generator.state == mb.numpy.bit_generator.state
    assert generation_report([ra]) == generation_report([rb])


@pytest.mark.parametrize('disabled', CRUTCHES)
def test_each_switch_removes_only_its_method(disabled):
    e = Einstein(switches(**{disabled: False}))
    assert set(e.methods.candidates()) == {('observe',)} | {(k,) for k in CRUTCHES if k != disabled}
    d = discovery(**{disabled: False})
    m = mind()
    if disabled == 'thought_experiments':
        assert d.einstein.thought(m, d, 'w0') == ()
        assert d.einstein.target(d, 'w0') is None
    elif disabled == 'symmetry_principles':
        assert d.einstein.invariance(m, d, 'w0') == 0
        assert d.einstein.priority(m, d, 'w0', x()) == 0
    elif disabled == 'doubt_assumptions':
        assert d.einstein.doubt(d, 'w0', (), source='test') is None
        assert d.einstein.revise(m, d, Pool(), 'w0', deadline=math.inf) == 0
    else:
        assert d.einstein.predict(m, d, 'w0', ('ask', 20)) is None
        assert d.einstein.settle(m, d, None, (20, 1)) == 0


def test_thought_extreme_paradox_and_real_experiment_at_its_location():
    d, m = discovery(), mind()
    p = square()
    rival = LG.node('if', LG.node('lt', x(), LG.node('lit', payload=10)), p, plus(p))
    d.laws = {'a': law(p, 'w0'), 'b': law(rival, 'w1')}
    d.observations['w0'] = [(2, 4), (3, 9)]
    pool = Pool()
    found = d.einstein.thought(m, d, 'w0')
    assert found and not pool.acts and not pool.judges
    paradox = d.einstein.paradoxes[found[0]]
    assert paradox['input'] >= 10 and paradox['confirmed'] is None
    assert d.questions[-1].reason == 'paradox'
    target = d.einstein.target(d, 'w0')
    assert target['action'] == ('ask', paradox['input'])
    observation = (paradox['input'], paradox['predictions'][0])
    d.einstein.confirm(m, d, 'w0', target['action'], observation)
    assert paradox['confirmed'] and paradox['experiments'][0][1] == target['action']
    assert d.einstein.doubts
    assert all(row not in d.observations['w0'] for row in (observation,))


def test_agreeing_laws_no_paradox_and_imagination_has_no_oracle_seam():
    d = discovery()
    d.observations['w0'] = [(2, 4), (3, 9)]
    d.laws = {'a': law(square(), 'w0'), 'b': law(LG.node('add', square(), LG.node('zero')), 'w1')}
    assert not d.einstein.thought(mind(), d, 'w0')
    assert not d.questions and not d.einstein.paradoxes
    tree = ast.parse(textwrap.dedent(inspect.getsource(Einstein.thought)))
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not attrs & {'act', 'certify', 'body', 'verify', 'grade', 'teacher_truth'}
    assert 'pool' not in inspect.signature(Einstein.thought).parameters


def negation_concepts():
    body = LG.node('sub', LG.node('zero'), LG.node('var', payload='_'))
    return {7: (body, '_'), '_sig': {7: ('num', 'num')}}


def test_acquired_inverse_only_principle_standing_search_and_break_question():
    d = discovery()
    d.observations['w0'] = [(-2, 4), (-1, 1), (1, 1), (2, 4)]
    d.laws = {'a': law(square(), 'w0'), 'b': law(plus(square()), 'w1')}
    assert not d.einstein.transforms(d, 'w0', {})
    m = mind(negation_concepts())
    transforms = d.einstein.transforms(d, 'w0', m.field.concept_table())
    assert transforms and all(t['program'][0] == 'c' and t['program'][1] == 7 for t in transforms)
    assert d.einstein.invariance(m, d, 'w0') == 1
    principle = next(iter(d.einstein.principles.values()))
    assert principle['standing'] == 2 and principle['status'] == 'fallible'
    assert m.field.ideas.bindings
    assert d.einstein.order(m, d, 'w0', (x(), square())) == (square(), x())
    assert any(q.reason == 'principle' for q in d.questions)
    assert d.laws['a']['coverage'] == {'w0': (100., 0.)}
    d.laws['c'] = law(x(), 'w2')
    d.einstein.thought(m, d, 'w0')
    assert any(p['principle'] is not None for p in d.einstein.paradoxes.values())


def test_observed_inverse_must_be_nontrivial_and_hold_both_orders():
    d = discovery()
    d.observations['w0'] = [(1, 1), (2, 2)]
    identity = {1: (LG.node('var', payload='_'), '_'), '_sig': {1: ('num', 'num')}}
    assert not d.einstein.transforms(d, 'w0', identity)
    noninvertible = {1: (LG.node('mul', LG.node('var', payload='_'), LG.node('zero')), '_'),
                     '_sig': {1: ('num', 'num')}}
    assert not d.einstein.transforms(d, 'w0', noninvertible)


@pytest.mark.parametrize('refuse', [None, 'w1'])
def test_shared_wrong_part_revised_first_and_certified_on_both(monkeypatch, refuse):
    d = discovery()
    shared = square()
    d.laws = {'a': law(plus(shared), 'w0'), 'b': law(plus(shared, 2), 'w1')}
    d.observations['w0'] = [(0, 1), (2, 5), (3, 7)]
    d.observations['w1'] = [(0, 2), (2, 6)]
    double = LG.node('add', LG.node('var', payload='_'), LG.node('var', payload='_'))
    m = mind({8: (double, '_'), '_sig': {8: ('num', 'num')}})
    dk = d.einstein.doubt(d, 'w0', ('a', 'b'), source='confirmed-paradox')
    assert d.einstein.doubts[dk]['shared'][0] == shared
    admitted = []
    monkeypatch.setattr(d, 'admit', lambda *args, **kwargs: admitted.append(args[1]))
    pool = Pool(refuse=refuse)
    gain = d.einstein.revise(m, d, pool, 'w0', deadline=math.inf)
    assert [wid for wid, _ in pool.judges] == ['w0', 'w1']
    revision = d.einstein.revisions[-1]
    assert revision['part'] == shared and revision['replacement'][0] == 'c'
    assert revision['certified'] == (refuse is None)
    assert gain == int(refuse is None)
    assert admitted == (['w0', 'w1'] if refuse is None else [])
    assert len(d.laws) == 2


def test_failure_world_also_required_for_revision(monkeypatch):
    d = discovery()
    d.laws = {'a': law(plus(square()), 'w0'), 'b': law(plus(square(), 2), 'w1')}
    d.observations['w0'] = [(0, 1), (2, 5)]
    d.observations['w1'] = [(0, 2), (2, 6)]
    d.observations['w2'] = [(3, 7)]
    double = LG.node('add', LG.node('var', payload='_'), LG.node('var', payload='_'))
    m = mind({8: (double, '_'), '_sig': {8: ('num', 'num')}})
    d.einstein.doubt(d, 'w2', ('a', 'b'), source='anomaly')
    monkeypatch.setattr(d, 'admit', lambda *args, **kwargs: None)
    pool = Pool(refuse='w2')
    assert d.einstein.revise(m, d, pool, 'w2', deadline=math.inf) == 0
    assert [wid for wid, _ in pool.judges] == ['w0', 'w1', 'w2']
    assert not d.einstein.revisions[-1]['certified']


@pytest.mark.parametrize('right', [True, False])
def test_prediction_precedes_experiment_credit_or_not_yet(right, monkeypatch):
    d, m = discovery(), mind(not_yet=True)
    d.laws['a'] = law(plus(x()), 'w0')
    d.observations['w0'] = [(1, 2), (2, 3)]
    monkeypatch.setattr('sera_u.einstein.time.time', lambda: 100.)
    pid = d.einstein.predict(m, d, 'w0', ('ask', 40))
    p = d.einstein.predictions[-1]
    assert pid and p['recorded_at'] == 100. and p['result'] is None
    pool = Pool(d)
    observation = pool.act('w0', ('ask', 40))
    if not right:
        observation = (40, 42)
    monkeypatch.setattr('sera_u.einstein.time.time', lambda: 101.)
    d.einstein.settle(m, d, pid, observation)
    assert p['performed_at'] >= p['recorded_at'] and p['confirmed'] == right
    assert d.einstein.law_credit['a'] == (1. if right else -1.)
    assert bool(d.pending) == (not right)
    assert bool(m.field.revisit_queue) == (not right)
    assert bool(d.einstein.doubts) == (not right)
    assert len(d.laws['a']['coverage']) == 1
    with pytest.raises(ValueError, match='already'):
        d.einstein.settle(m, d, pid, observation)
    d.observations['w1'] = [(50, 1)]
    assert d.einstein.predict(m, d, 'w0', ('ask', 50)) is None


def test_bold_principle_credit_is_not_proof():
    d, m = discovery(), mind(negation_concepts())
    d.observations['w0'] = [(1, 1), (2, 4)]
    d.laws = {'a': law(square(), 'w0'), 'b': law(plus(square()), 'w1')}
    d.einstein.invariance(m, d, 'w0')
    pid = d.einstein.predict(m, d, 'w0', ('ask', 20))
    p = d.einstein.predictions[-1]
    assert p['principles']
    d.einstein.settle(m, d, pid, (20, p['predicted']))
    principle = d.einstein.principles[p['principles'][0]]
    assert principle['credit'] == 1 and principle['standing'] == 2
    assert d.einstein.principle_credit[p['principles'][0]] == 1
    assert len(d.laws) == 2


def test_neutral_field_methods_thompson_returns_teacher_fade_and_phase():
    head = EinsteinMethods(switches())
    for method in head.candidates():
        mean, cov = head._post('discovery', method)
        assert not mean.any()
        np.testing.assert_array_equal(cov, np.eye(head.d))
    e = Einstein(switches())
    moment = dict(doubt=1.)
    e.methods.demonstrate('thought_experiments', moment, phase='lesson', origin='taught')
    arrays = e.methods.taught[('discovery', ('thought_experiments',))]
    before = arrays[0].copy()
    e.methods.end_task()
    np.testing.assert_allclose(arrays[0], before*PH.TAUGHT_FADE)
    e.phase('rsi')
    np.testing.assert_allclose(arrays[0], before*PH.TAUGHT_FADE*.4)
    e.methods.learn('discovery', ('thought_experiments',), moment, 2.)
    own = copy.deepcopy(e.methods.stats)
    e.phase('test3')
    assert not arrays[0].any() and not arrays[1].any()
    np.testing.assert_array_equal(own[('discovery', ('thought_experiments',))][0],
                                  e.methods.stats[('discovery', ('thought_experiments',))][0])
    for phase, origin in [('test2', 'taught'), ('test3', 'taught'), ('lesson', 'explore')]:
        with pytest.raises(ValueError, match='rediscovery'):
            e.methods.demonstrate('bold_predictions', moment, phase=phase, origin=origin)


def test_checkpoint_exact_next_draw_hash_excludes_timestamps_and_costs(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', reads)
    entity = fast_entity()
    d = entity.discovery
    d.register_worlds((WorldView('w0', 'exact'),))
    d.observations['w0'] = [(1, 2), (2, 3)]
    d.laws['a'] = law(plus(x()), 'w0')
    d.einstein.predict(entity, d, 'w0', ('ask', 40))
    before = entity.learning_hash()
    d.einstein.predictions[0]['recorded_at'] += 1000.
    d.einstein.predictions[0]['performed_at'] = 9999.
    d.einstein.events.append(dict(seconds=100.))
    d.events.append(dict(seconds=100.))
    assert entity.learning_hash() == before
    restarted = SeraU.loads(entity.dumps())
    assert restarted.field.einstein_methods is restarted.discovery.einstein.methods
    assert restarted.learning_hash() == before
    moment = dict(doubt=1.)
    candidates = {'observe'} | set(CRUTCHES)
    a = d.einstein.methods.choose('discovery', candidates, moment, entity.numpy)
    b = restarted.discovery.einstein.methods.choose('discovery', candidates, moment, restarted.numpy)
    assert a == b
    assert entity.learning_hash() == restarted.learning_hash()


def test_tick_prediction_is_appended_before_act(monkeypatch):
    d, m = discovery(), mind()
    d.active = 'w0'
    d.observations['w0'] = [(1, 2), (2, 3)]
    d.laws['a'] = law(plus(x()), 'w0')
    monkeypatch.setattr(d.policy, 'pick', lambda choices, *args: 'stay' if 'stay' in choices else sorted(choices)[0])
    monkeypatch.setattr(d.einstein.methods, 'choose', lambda *args: [('bold_predictions',)])
    monkeypatch.setattr(d, 'experiment_menu', lambda *args: [dict(action=('ask', 40), predicted=41, info=0., surprise=0.)])
    row = d.tick(m, Pool(d))
    assert row['bold_prediction'] and d.einstein.predictions[-1]['confirmed']
    assert 'einstein_records' in row


def test_frozen_observer_suite_never_teaches_and_worldview_has_no_law(monkeypatch):
    suite = dict(retention=[], wake=[], assessment=[])
    monkeypatch.setattr(observer, 'freeze', lambda *args: dict(schema=SCHEMA, worlds=[], split='frozen'))
    manifest = observer.freeze_einstein(None, suite, 3)
    assert manifest == observer.freeze_einstein(None, suite, 3)
    assert len(manifest['worlds']) == 7
    assert {r['observer_category'] for r in manifest['worlds']} >= {'conflict', 'differences', 'imagined-extreme'}
    assert manifest['einstein_suite'] == 'u10-einstein-1'
    pool = WorldPool(manifest)
    d = discovery()
    d.register_worlds(pool.public())
    # U14 adds opaque public body identities (the same object seen in two worlds); the Einstein suite declares none.
    assert all(set(w.__dict__) == {'id', 'form', 'tin', 'tout', 'objects', 'sigma', 'object_ids'} and w.object_ids == ()
               for w in pool.public())
    assert observer.teach_einstein_once(SimpleNamespace(discovery=d, sleep=SimpleNamespace(replay=[]))) is False
    assert not d.einstein.teacher_shown
    bad = copy.deepcopy(manifest)
    bad['worlds'][0]['audit_range'] = [1, 1]
    with pytest.raises(ValueError, match='scope'):
        validate(bad, suite)
    # Finite extreme separates two independently valid scoped candidate laws.
    a, b = manifest['worlds'][0]['program'], manifest['worlds'][1]['program']
    assert all(LG.safe(a, {'x': v}, {}) == LG.safe(b, {'x': v}, {}) for v in range(-6, 7))
    assert LG.safe(a, {'x': 20}, {}) != LG.safe(b, {'x': 20}, {})


def test_report_cumulative_counts_not_double_summed_and_false_credit_visible():
    records = [dict(arm='full', generation=0, einstein=dict(predictions=2)),
               dict(arm='full', generation=1, einstein=dict(predictions=3))]
    result = observer.report_einstein(records, [dict(false_credit=False)])
    assert result['arms']['full']['einstein']['predictions'] == 3
    assert result['zero_false_credit'] and result['false_credit'] == 0
    assert not observer.report_einstein(records, [dict(false_credit=True)])['zero_false_credit']
    assert "not a claim of Einstein's insight" in result['claim']


def test_observer_laws_and_audit_state_are_not_reachable_from_learner():
    d, m, pool = discovery(), mind(), Pool()
    d.tick(m, pool)
    forbidden = (pool, pool.private_law, pool.private_world, pool.private_audit)
    stack, seen = [d], set()
    while stack:
        item = stack.pop()
        assert not any(item is private for private in forbidden)
        if id(item) in seen:
            continue
        seen.add(id(item))
        if isinstance(item, (str, bytes, int, float, bool, type(None), np.ndarray, torch.Tensor)):
            continue
        if isinstance(item, dict):
            stack.extend(item.keys())
            stack.extend(item.values())
        elif isinstance(item, (tuple, list, set)):
            stack.extend(item)
        elif hasattr(item, '__dict__') and not isinstance(item, type):
            stack.extend(item.__dict__.values())


def test_failed_unit_rolls_back_prediction_and_next_choice(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', reads)
    monkeypatch.setattr(EinsteinMethods, 'choose', lambda *args: [('bold_predictions',)])
    monkeypatch.setattr(Discovery, 'experiment_menu', lambda *args: [dict(action=('ask', 40), predicted=41, info=0., surprise=0.)])
    entity = fast_entity()
    entity.discovery.register_worlds((WorldView('w0', 'exact'),))
    entity.discovery.observations['w0'] = [(1, 2), (2, 3)]
    entity.discovery.laws['a'] = law(plus(x()), 'w0')
    before = entity.learning_hash()
    class Broken(Pool):
        def act(self, wid, action):
            raise RuntimeError('world action interrupted')
    with pytest.raises(RuntimeError, match='interrupted'):
        entity.discover(Broken())
    assert entity.learning_hash() == before
    assert not entity.discovery.einstein.predictions
    assert entity.field.einstein_methods is entity.discovery.einstein.methods


def test_small_real_scoped_judge_has_zero_false_credit(monkeypatch):
    suite = dict(retention=[], wake=[], assessment=[])
    monkeypatch.setattr(observer, 'freeze', lambda *args: dict(schema=SCHEMA, worlds=[], split='frozen'))
    manifest = observer.freeze_einstein(None, suite, 3)
    pool = WorldPool(manifest)
    for wid in ('e0', 'e1'):
        hyp = pool.specs[wid]['program']  # OBSERVER test code only; never a learner label
        observations = tuple(pool.act(wid, ('ask', v)) for v in (-3, -1, 1, 3))
        verdict = pool.certify(wid, hyp, {}, observations)
        assert verdict.accepted
    observations = tuple(pool.act('e2', ('ask', v)) for v in (12, 15, 18, 21))
    refused = pool.certify('e2', pool.specs['e0']['program'], {}, observations)
    assert not refused.accepted and refused.refuted
    assert all(not r['false_credit'] for r in pool.audit_records)


def test_generation_denominator_includes_dual_revision_laws():
    row = dict(seconds=2., experiment=None, discovered=False, einstein_law_kinds=['formula', 'formula'],
               einstein=dict(dual_world_revisions=1), einstein_records={})
    report = generation_report([row])
    assert report['laws'] == 2 and report['seconds_per_law'] == 1.
    assert report['by_kind']['formula'] == 2


def test_freezer_uses_structural_families_not_changed_constants(monkeypatch):
    from sera_u.sleep import family
    base = plus(square(), 5)
    suite = dict(retention=[dict(family=family(base, {}))], wake=[], assessment=[])
    monkeypatch.setattr(observer, 'freeze', lambda *args: dict(schema=SCHEMA, worlds=[], split='frozen'))
    manifest = observer.freeze_einstein(None, suite, 3)
    assert all(row['family'] != family(base, {}) for row in manifest['worlds'])
    assert LG.safe(manifest['worlds'][0]['program'], {'x': 3}, {}) == 14
    assert LG.size(manifest['worlds'][1]['program']) <= 40


def test_teacher_uses_only_taught_receipts_once_and_never_assessment():
    d, m = discovery(), mind()
    m.discovery = d
    m.sleep = SimpleNamespace(replay=[(SimpleNamespace(origin='explore', view=d.view('w0')), {})])
    assert not observer.teach_einstein_once(m)
    m.sleep.replay = [(SimpleNamespace(origin='taught', view=d.view('w0')), {})]
    assert observer.teach_einstein_once(m)
    assert not observer.teach_einstein_once(m)
    assert d.einstein.phase_weight == .4
    assert d.events[-1]['world'] == 'taught-method-context'
    m.discovery = discovery()
    m.progress = dict(assessment=True)
    with pytest.raises(ValueError, match='assessment'):
        observer.teach_einstein_once(m)


def test_paired_rates_check_frozen_scope_and_do_not_invent_speed(monkeypatch):
    from scripts import sera_u_rsi as rsi
    from pathlib import Path
    states = {name: dict(suite_sha256='same-u1', discovery_suite_sha256='same-einstein',
        protocol=dict(device='cpu', seed=3)) for name in ('u-einstein', 'u-einstein-no-symmetry-principles')}
    def generation(seconds):
        return dict(arm='full', generation=1, laws=2, seconds=seconds, experiments=4,
                    einstein=dict(principles=1))
    reports = {'u-einstein': dict(complete=True, discovery=dict(generations=[generation(4.)], false_credit=0)),
               'u-einstein-no-symmetry-principles': dict(complete=True,
                    discovery=dict(generations=[generation(8.)], false_credit=0))}
    def read(path):
        path = Path(path)
        return (states if path.name == 'state.json' else reports)[path.parent.name]
    monkeypatch.setattr(rsi, 'read', read)
    paths = ['/content/u-einstein', '/content/u-einstein-no-symmetry-principles']
    result = observer.compare_runs(paths)
    assert result['zero_false_credit']
    assert result['cases']['einstein']['arms']['full']['principles_sped_later_search'] is True
    reports['u-einstein-no-symmetry-principles']['complete'] = False
    assert observer.compare_runs(paths)['cases']['einstein']['arms']['full']['principles_sped_later_search'] is None
    states['u-einstein']['discovery_suite_sha256'] = 'changed'
    with pytest.raises(ValueError, match='identical frozen'):
        observer.compare_runs(paths)


def test_full_tick_performs_designed_extreme_without_judging_imagination(monkeypatch):
    d, m = discovery(), mind()
    rival = LG.node('if', LG.node('lt', x(), LG.node('lit', payload=10)), square(), plus(square()))
    d.laws = {'a': law(square(), 'w0'), 'b': law(rival, 'w1')}
    d.active = 'w0'
    d.observations['w0'] = [(2, 4), (3, 9)]
    monkeypatch.setattr(d.policy, 'pick', lambda choices, *args: 'stay' if 'stay' in choices else sorted(choices)[0])
    monkeypatch.setattr(d.einstein.methods, 'choose', lambda *args: [('thought_experiments',)])
    class Squared(Pool):
        def act(self, wid, action):
            assert not self.judges
            assert d.einstein.paradoxes  # already found before this first act
            self.acts.append((wid, action))
            return action[1], action[1]*action[1]
    pool = Squared()
    row = d.tick(m, pool)
    assert row['experiment'][1] >= 10
    assert pool.acts == [('w0', row['experiment'])]
    assert d.einstein.report()['paradoxes_confirmed'] == 1
    assert not pool.judges


def test_strengths_context_skips_exact_imagination_without_unpacking_throws(monkeypatch):
    d, m = discovery(), mind()
    d.register_worlds((WorldView('rail', 'strengths'),))
    d.observations['rail'] = [(0, ((0., .5, 1.),), (0., 1.), (0., 1.))]
    monkeypatch.setattr(d.einstein.methods, 'choose', lambda *args: [(k,) for k in CRUTCHES])
    chosen, moment, outcomes = d.einstein.run(m, d, Pool(), 'rail', deadline=math.inf)
    assert len(chosen) == 4 and not d.einstein.paradoxes and not d.einstein.principles
    assert all(row['gain'] == 0 for row in outcomes)


def test_checkpoint_resumes_a_complete_next_tick_exactly(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', reads)
    monkeypatch.setattr(Discovery, 'propose', lambda *args: ())
    monkeypatch.setattr('sera_u.discovery.time.perf_counter', lambda: 10.)
    monkeypatch.setattr('sera_u.einstein.time.time', lambda: 100.)
    entity = fast_entity()
    d = entity.discovery
    d.register_worlds((WorldView('w0', 'exact'),))
    d.observations['w0'] = [(1, 2), (2, 3)]
    d.laws['a'] = law(plus(x()), 'w0')
    entity.discover(Pool())
    restarted = SeraU.loads(entity.dumps())
    a = entity.discover(Pool())
    b = restarted.discover(Pool())
    assert a == b
    assert entity.learning_hash() == restarted.learning_hash()
