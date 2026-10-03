"""U9 short CPU contracts. Expensive Field reads/rail certificates use stubs.

Run by development review with PYTHONHASHSEED=0; no Python was run by the development tool worker.
"""
import ast
import copy
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.discovery import (CRUTCHES, DEFAULT_SHARE, Certification, Discovery,
    OwnQuestion, Readout, WorldView, compression_credit, generation_report,
    hidden_quantity, public_rail, residual_code, split_score)
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import Engine, U_CRUTCHES, arm_settings
from sera_u.ports import TaskView, digest
from sera_u.sleep import Receipt, expand, family, independent
from scripts.sera_u_discovery import WorldPool, report, validate


@pytest.fixture(autouse=True)
def deterministic(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


def switches(**overrides):
    return {**dict.fromkeys(CRUTCHES, True), **overrides}


def entity(**overrides):
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1),
                 discovery=switches(**overrides))


def plus():
    return LG.node('add', LG.node('var', payload='x'), LG.node('one'))


def read_stub(self, views, concepts=None):
    return [(torch.zeros(3, 64), torch.ones(3)/3) for _ in views]


def fixed_policy(self, choices, x, rng):
    # Always select the same rule, with no installed domain program.
    for name in ('stay', 'question', 'split', 'quantity'):
        if name in choices:
            return name
    return sorted(choices)[0]


class StubPool:
    def __init__(self):
        self.private_world = object()
        self.private_program = object()
        self.held_out = object()
        self.seen, self.judged = [], []

    def public(self):
        return (WorldView('w0', 'exact'), WorldView('w1', 'exact'), WorldView('w2', 'exact'))

    def act(self, wid, action):
        self.seen.append((wid, action))
        return action[1], action[1]+(2 if wid == 'w2' else 1)

    def certify(self, wid, hyp, concepts, observations, *, library=()):
        self.judged.append((wid, hyp, observations))
        right = hyp == plus() and wid != 'w2'
        return Certification(right, 'formula', (('eps', .05), ('delta', .01)),
                             digest((wid, hyp, observations)), not right)


def own_rows(d, wid, offset=1):
    d.observations[wid] = [(x, x+offset) for x in (-2, 0, 1, 4)]


def reachable(root, forbidden):
    stack, visited = [root], set()
    while stack:
        obj = stack.pop()
        assert not any(obj is item for item in forbidden), 'Private observer state reached learner'
        if id(obj) in visited:
            continue
        visited.add(id(obj))
        if type(obj) in (str, bytes, int, float, bool, type(None)) or isinstance(obj, (torch.Tensor, np.ndarray)):
            continue
        if isinstance(obj, dict):
            stack.extend(obj.keys()); stack.extend(obj.values())
        elif isinstance(obj, (tuple, list, set)):
            stack.extend(obj)
        elif hasattr(obj, '__dict__') and not isinstance(obj, type):
            stack.extend(obj.__dict__.values())


def test_registered_removable_default_off_and_old_payload(monkeypatch):
    assert DEFAULT_SHARE == .10
    for name in CRUTCHES:
        assert name in CR.REGISTRY and not CR.on(name)
        assert name not in CR.settings()['crutches_effective']
    baseline = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    off = entity(open_worlds=False)
    assert off.discovery is None and off.discover(object()) is None
    assert 'discovery' not in baseline._payload() and 'discovery' not in off._payload()
    assert baseline.learning_hash() == off.learning_hash()
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    task1 = TS.number_task('old', lambda x: x, 3, 1)
    task2 = TS.number_task('old', lambda x: x, 3, 1)
    a = baseline.live(task1, max_steps=1)
    b = off.live(task2, max_steps=1)
    def logical(value):
        if isinstance(value, dict):
            # 'execution' counts interpreter work, which shared search caches change between two lives (Colab,
            # 2026-10-03: 118664 against 118648 primitive calls); like time, it is not a logical record.
            return {k: logical(v) for k, v in value.items()
                    if k not in ('wall', 'time', 'seconds', 'timing', 'execution')}
        if isinstance(value, list):
            return [logical(v) for v in value]
        return value
    # Exact disabled path has no U9 metadata even when the other U9 flags are on.
    assert set(a) == set(b) and 'discovery' not in b
    assert a['proven'] == b['proven'] and a['answer'] == b['answer']
    assert logical(a['sera_u']) == logical(b['sera_u'])


def test_question_only_own_observations_and_no_object_leak(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    monkeypatch.setattr(Readout, 'pick', fixed_policy)
    monkeypatch.setattr(Discovery, 'propose', lambda self, mind, wid, deadline: (plus(),))
    mind, pool = entity(), StubPool()
    d = mind.discovery
    d.register_worlds(pool.public())
    own_rows(d, 'w0')
    q = d.own_question('w0', 'surprise')
    assert type(q) is OwnQuestion and q.scope == 'own-question' and q.origin == 'explore'
    assert q.view.examples == tuple(((('x', x),), y) for x, y in d.observations['w0'])
    assert q.view.words == () and q.view.queries == ()
    original = q.view.identity
    pool.private_program, pool.held_out = object(), object()
    assert d.own_question('w0', 'surprise').view.identity == original
    row = mind.discover(pool)
    assert row['certified']['accepted'] and row['discovered']
    forbidden = (pool, pool.private_program, pool.private_world, pool.held_out)
    reachable(mind._payload(), forbidden)
    receipt = mind.sleep.replay[0][0]
    assert receipt.origin == 'explore' and receipt.acceptance[0] == row['certified']['record']
    assert receipt.view.words == () and receipt.view.measurements == ()
    assert len(receipt.view.examples) == 4
    mind.sleep.abstract()
    mind.sleep.dream(2, attempts=8)
    reachable((mind.owner, mind.field, mind.sleep, mind.discovery), forbidden)


def test_source_ast_has_no_private_observer_access_in_discovery():
    path = Path(__file__).resolve().parents[2]/'sera_u'/'discovery.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    private = {'_target', '_fresh', 'hidden', 'truth', 'held_out', 'spec', 'true_force', 'grade'}
    assert not any(isinstance(n, ast.Attribute) and n.attr in private for n in ast.walk(tree))
    # Runner world owners cannot be imported into the entity implementation.
    assert 'scripts.sera_u_discovery' not in path.read_text(encoding='utf-8')


def test_designed_split_beats_random_after_learning_and_off_is_random():
    d = Discovery(switches())
    x = np.r_[1., np.zeros(64)]
    menu = [dict(action=('ask', j), info=float(j == 9), surprise=0., predicted=None) for j in range(10)]
    # Received own gains, no privileged teacher answer or programmed prior.
    for _ in range(40):
        d.policy.learn('split', x, 1., .1)
        d.policy.learn('surprise', x, 0., .1)
        d.policy.learn('random', x, 0., .1)
    rng = np.random.default_rng(9)
    designed = [d.choose_experiment(menu, x, rng)[0]['info'] for _ in range(30)]
    d.switches['designed_experiments'] = False
    rng = np.random.default_rng(9)
    random = [d.choose_experiment(menu, x, rng)[0]['info'] for _ in range(30)]
    assert sum(designed) > 2*sum(random)
    assert split_score((0, 0)) == 0 and split_score((0, 1)) == 1


def test_neutral_priors_and_teacher_fades_with_phase_gate():
    p, x = Readout(), np.r_[1., np.zeros(64)]
    for name in ('question', 'split', 'random', 'unify', 'quantity'):
        mean, cov = p.posterior(name)
        np.testing.assert_array_equal(mean, np.zeros(65))
        np.testing.assert_array_equal(cov, np.eye(65))
    p.demonstrate('quantity', x, 'lesson')
    original = p.taught['quantity'][0].copy()
    p.learn('random', x, 0., 1.)
    np.testing.assert_allclose(p.taught['quantity'][0], original*PH.TAUGHT_FADE)
    with pytest.raises(ValueError, match='U5'):
        p.demonstrate('quantity', x, 'test3')


def test_unification_code_one_law_beats_two_independent_fits():
    shared = compression_credit(20., {'w0': (100., 10.), 'w1': (100., 10.)})
    separate = compression_credit(20., {'w0': (100., 10.)})+compression_credit(20., {'w1': (100., 10.)})
    assert shared > separate
    d = Discovery(switches())
    d.laws['shared'] = dict(bits=20., coverage={'w0': (100., 10.), 'w1': (100., 10.)}, features=np.zeros(65))
    d.laws['one'] = dict(bits=20., coverage={'w0': (100., 10.)}, features=np.zeros(65))
    assert d.standing('shared') > d.standing('one')
    d.switches['unification_credit'] = False
    assert d.standing('shared') == 2.


def test_hidden_numbers_only_when_code_saves_and_units_are_not_named():
    objects = np.repeat(np.arange(3), 32)
    drives = np.tile(np.r_[np.ones(16), -np.ones(16)], 3)
    quantities = np.repeat((1., .5, 1/3), 32)
    result = hidden_quantity(objects, drives*quantities, drives, .01)
    assert result and result['bits_saved'] > 0
    assert result['representation'] == 'shared-scale'
    np.testing.assert_allclose([v for _, v in result['values']], (1., .5, 1/3))
    assert hidden_quantity(objects, drives, drives, .01) is None
    assert hidden_quantity(objects, drives*quantities, drives, 100.) is None
    assert hidden_quantity(objects, drives*quantities, drives, 10., bits_per_number=1e12) is None
    d = Discovery(switches())
    assert d.demonstrate_quantity(objects, drives*quantities, drives, .01)
    assert not d.demonstrate_quantity(objects, drives*quantities, drives, .01)
    d.switches['hidden_quantities'] = False
    assert d.fit_quantity(SimpleNamespace(), 'not-a-world', np.zeros(65)) is None


def test_cross_world_transfer_and_anomaly_preserves_other_standing(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    mind, pool = entity(), StubPool()
    d = mind.discovery
    d.register_worlds(pool.public())
    own_rows(d, 'w0'); own_rows(d, 'w1'); own_rows(d, 'w2', 2)
    verdict = pool.certify('w0', plus(), {}, tuple(d.observations['w0']))
    key, fresh = d.admit(mind, 'w0', plus(), verdict, np.zeros(65), 1.)
    assert fresh
    rows = d.transfer(mind, pool, key, math.inf)
    assert [r['accepted'] for r in rows] == [True, False]
    assert set(d.laws[key]['coverage']) == {'w0', 'w1'}
    assert d.laws[key]['certificates']['w0'] == verdict
    assert d.pending[0]['world'] == 'w2' and d.pending[0]['status'] == 'not-yet'
    assert d.questions[-1].reason == 'anomaly'
    assert len(d.laws[key]['concept_ids']) == 1
    before = copy.deepcopy(d.laws[key]['certificates'])
    refusal = Certification(False, 'formula', (('eps', .05),), 'uncertain', False)
    assert d.anomaly(mind, 'w1', key, refusal) is None
    assert d.laws[key]['certificates'] == before


def test_anomaly_opens_u7_public_not_yet_item(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1), discovery=switches(),
                 crutches={**dict.fromkeys(U_CRUTCHES, False), **arm_settings('full'),
                           'taught_not_yet': True, 'abstain_bar': False})
    d, pool = mind.discovery, StubPool()
    d.register_worlds(pool.public())
    own_rows(d, 'w0'); own_rows(d, 'w2', 2)
    verdict = pool.certify('w0', plus(), {}, tuple(d.observations['w0']))
    key, _ = d.admit(mind, 'w0', plus(), verdict, np.zeros(65), 1.)
    d.anomaly(mind, 'w2', key, pool.certify('w2', plus(), {}, tuple(d.observations['w2'])))
    item = mind.field.revisit_queue[-1]
    assert item['status'] == 'not-yet' and item['origin'] == 'explore'
    assert item['view'] == d.view('w2') and item['discovery_world'] == 'w2'
    assert 'w0' in d.laws[key]['coverage']


def test_no_question_switch_disables_question_records_and_random_closes_policy():
    d = Discovery(switches(own_questions=False, designed_experiments=False))
    menu = [dict(action=('ask', 1), info=10., surprise=0., predicted=None)]
    experiment, route = d.choose_experiment(menu, np.zeros(65), np.random.default_rng(3))
    assert route == 'random' and experiment == menu[0]
    assert d.questions == [] and d.policy.own == {}


def test_bound_receipts_and_drawings_remain_honest():
    examples = tuple(((('x', v),), v+1) for v in (-2, 0, 1, 4))
    view = TaskView((('x', 'num'),), 'num', examples)
    with pytest.raises(ValueError, match='judge record'):
        Receipt.make(view, (plus(),), {}, scope='exact-audit', origin='explore', source='explore:w')
    r = Receipt.make(view, (plus(),), {}, scope='exact-audit', origin='explore', source='explore:w',
                     acceptance=('record', 'formula', (('eps', .05),)))
    assert r.check({})
    forged = copy.deepcopy(r)
    object.__setattr__(forged, 'acceptance', ('record', 'curve', (('eps', .05),)))
    with pytest.raises(ValueError, match='Corrupted'):
        forged.check({})
    body = LG.node('tab', payload=((-2., 0., 2.), (1., 0., 1.)))
    concepts = {1: (body, '_'), '_sig': {1: ('num', 'num')}}
    p = LG.node('c', LG.node('var', payload='x'), payload=1)
    for x in (-3., -1., 0., 1., 3.):
        assert independent(p, {'x': x}, concepts) == LG.evaluate(p, {'x': x}, concepts)
        assert independent(expand(p, concepts), {'x': x}, {}) == LG.evaluate(p, {'x': x}, concepts)


def test_checkpoint_exact_next_unit_and_hash_excludes_elapsed_logs(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    monkeypatch.setattr(Readout, 'pick', fixed_policy)
    monkeypatch.setattr(Discovery, 'propose', lambda self, mind, wid, deadline: ())
    # Fixed measured cost makes two actual next decisions directly comparable;
    # learned gain/sec legitimately changes when a real computation costs more.
    monkeypatch.setattr('sera_u.discovery.time.perf_counter', lambda: 1.)
    a, pool = entity(), StubPool()
    a.discover(pool)
    b = SeraU.loads(a.dumps())
    assert a.learning_hash() == b.learning_hash()
    row_a, row_b = a.discover(pool), b.discover(StubPool())
    assert row_a == row_b
    assert a.learning_hash() == b.learning_hash()
    before = a.learning_hash()
    a.discovery.events[0]['seconds'] = 999999.
    assert a.learning_hash() == before
    a.discovery.policy.learn('question', np.r_[1., np.zeros(64)], 1., 1.)
    assert a.learning_hash() != before


@pytest.mark.parametrize('name', CRUTCHES[1:])
def test_component_off_roundtrip_preserves_mask(name):
    mind = entity(**{name: False})
    loaded = SeraU.loads(mind.dumps())
    assert loaded.discovery.switches[name] is False
    assert mind.learning_hash() == loaded.learning_hash()


def test_discovery_failure_rolls_back(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    class Broken(StubPool):
        def act(self, *args):
            raise ValueError('broken body')
    mind = entity()
    before = mind.learning_hash()
    with pytest.raises(ValueError, match='broken body'):
        mind.discover(Broken())
    assert mind.learning_hash() == before and not mind._active


def test_owner_audit_does_not_return_failing_fresh_input():
    p = plus()
    manifest = dict(schema='u9-discovery-1', worlds=[dict(id='d0', form='exact', program=p,
        tin='num', tout='num', family=family(p, {}), seed=3, index=1)])
    pool = WorldPool(manifest)
    data = [pool.act('d0', ('ask', x)) for x in (-2, 0, 1, 4)]
    good = pool.certify('d0', p, {}, tuple(data))
    bad = pool.certify('d0', LG.node('zero'), {}, tuple(data))
    assert good.accepted and not bad.accepted and bad.refuted
    assert set(bad.__dict__) == {'accepted', 'kind', 'bound', 'record', 'refuted'}
    assert not pool.audit_records[0]['false_credit']
    assert pool.body('d0').data == []
    old_suite = dict(assessment=[], wake=[], retention=[])
    assert validate(manifest, old_suite) is manifest
    old_suite['assessment'].append(dict(family=family(p, {})))
    with pytest.raises(ValueError, match='overlaps'):
        validate(manifest, old_suite)


def test_rail_audit_uses_observer_throws_without_public_leak(monkeypatch):
    from ccops5.core import paths
    from ccops5.core.worlds import Action, Throw
    observed_throw = (0, ((0., .5, 1.),), (0.,)*paths.N_OBS, (0.,)*paths.N_OBS)
    hidden_throw = Throw(0, -1, Action(((0., .5, -.9),)),
                         np.full(paths.N_OBS, 999.), np.full(paths.N_OBS, 999.), 'check')
    body = SimpleNamespace(sigma=(.001, .001), n_situations=8,
        spec=SimpleNamespace(family=()), held_out=[hidden_throw], situations=lambda: {}, made={}, log=[])
    seen = []
    def verify(self, fam):
        seen.extend(self.throws)
        cert = SimpleNamespace(family=fam, band=.1, eps=.2)
        return True, cert, None
    monkeypatch.setattr(TS.Rail, 'claim_terms', lambda *args, **kwargs: ((), ()))
    monkeypatch.setattr(TS.Rail, 'verify', verify)
    monkeypatch.setattr(TS.Rail, 'grade', lambda *args, **kwargs: dict(verdict='proven right'))
    pool = WorldPool(dict(worlds=[dict(id='r', form='strengths', seed=3, index=1)]))
    pool.bodies['r'] = body
    verdict = pool.certify('r', (), {}, (observed_throw,))
    assert verdict.accepted and len(seen) == 2
    assert float(seen[1].x[0]) == 999.
    d = Discovery(switches())
    d.register_worlds(pool.public())
    d.observations['r'] = [observed_throw]
    assert all(999. not in row for row in d.view('r').measurements)
    reachable(d, (pool, body, hidden_throw))


def test_public_rail_body_contains_no_world_and_push_hand_rejects_bad():
    from ccops5.core import paths
    n = paths.N_OBS
    own = ((0, ((0., .5, 1.),), (0.,)*n, (0.,)*n),)
    task = public_rail(WorldView('rail', 'strengths', objects=2), own)
    assert task.world.__dict__ == {'n_situations': 2}
    assert not hasattr(task, 'hidden') and not hasattr(task, 'spec')
    assert task.throws[0].tag == 'own'
    pool = WorldPool(dict(worlds=[dict(id='r', form='strengths')]))
    pool.bodies['r'] = SimpleNamespace(n_situations=1)
    with pytest.raises(ValueError, match='hand limits'):
        pool.act('r', ('push', 0, ((0., 2., 2.),)))
    assert residual_code((0., 1.), .1) >= 0


def test_reports_zero_false_credit_and_improvement_are_observer_only():
    trial = dict(seconds=2., experiment=('ask', 0), discovered=True,
                 certified=dict(kind='formula'), reused=False)
    a, b = generation_report([trial]), generation_report([{**trial, 'seconds': 1.}])
    result = report([dict(arm='full', generation=0, **a), dict(arm='full', generation=1, **b)], [])
    assert result['false_credit'] == 0
    assert result['generations'][1]['seconds_per_law_improved'] is True
    assert generation_report([])['seconds_per_law'] is None
    assert 'rediscovery' in a['credit']


def test_legacy_receipt_has_no_discovery_slot():
    view = TaskView((('x', 'num'),), 'num', tuple(((('x', x),), x+1) for x in (-2, 0, 1, 4)))
    r = Receipt.make(view, (plus(),), {}, scope='exact-audit', origin='alone', source='old')
    assert 'acceptance' not in r.__dict__ and r.acceptance == ()
    assert r.check({})


def test_self_made_question_conditions_search_without_answers(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    monkeypatch.setattr(Readout, 'pick', fixed_policy)
    seen = []
    def propose(self, mind, wid, deadline):
        seen.append(self.search_view(wid))
        return ()
    monkeypatch.setattr(Discovery, 'propose', propose)
    mind, pool = entity(), StubPool()
    d = mind.discovery
    d.register_worlds(pool.public())
    own_rows(d, 'w0')
    d.active = 'w0'
    d.rivals['w0'] = (plus(),)
    mind.discover(pool)
    assert seen[0].queries and not seen[0].hypotheses
    assert seen[0].examples == tuple(((('x', x),), y) for x, y in d.observations['w0'][:4])
    assert all(tuple(k for k, _ in q) == ('x',) for q in seen[0].queries)
    assert d.questions[0].view == seen[0]
    assert d.questions[0].scope == 'own-question'


def test_rival_search_uses_unanswered_probes(monkeypatch):
    mind = entity()
    d = mind.discovery
    d.register_worlds((WorldView('w', 'exact'),))
    own_rows(d, 'w')
    mind.proposer.enabled = False
    seen = []
    def search(inputs, out, probes, *args, **kwargs):
        seen.extend(probes)
        return []
    monkeypatch.setattr(LG, 'search', search)
    with mind.scope():
        d.propose(mind, 'w', math.inf)
    assert len(seen) == 12
    assert all(set(p) == {'x'} for p in seen)
    assert split_score((1, 2), (10000., 10000.)) == 1.


def test_dream_partition_is_observer_owned_and_allows_only_certified_reuse(monkeypatch):
    p = plus()
    manifest = dict(schema='u9-discovery-1', worlds=[dict(id='d0', form='exact', program=p,
        tin='num', tout='num', family=family(p, {}), seed=3, index=1)])
    pool, mind = WorldPool(manifest), entity()
    assert not pool.dream_allowed(p, {})
    mind.discovery.register_worlds(pool.public())
    own_rows(mind.discovery, 'd0')
    verdict = pool.certify('d0', p, {}, tuple(mind.discovery.observations['d0']))
    with mind.scope():
        mind.discovery.admit(mind, 'd0', p, verdict, np.zeros(65), 1.)
        pool.sync(mind.discovery)
        assert pool.dream_allowed(p, mind.field.concept_table())
        mind.sleep.dream(2, attempts=4, filter_program=pool.dream_allowed)
    assert not hasattr(mind.sleep, 'discovery_held')
    reachable(mind._payload(), (pool, pool.manifest, pool.specs, pool.dream_allowed))


def test_unseen_curve_fits_never_unify_by_free_curve_syntax(monkeypatch):
    mind = entity()
    d = mind.discovery
    d.register_worlds((WorldView('r0', 'strengths'), WorldView('r1', 'strengths')))
    monkeypatch.setattr(Discovery, 'observation_code', lambda *args: (100., 20.))
    monkeypatch.setattr(Discovery, '_keep_physics', lambda *args: None)
    hyp = (('speed', 'curve', 17),)
    v = Certification(True, 'curve', (('eps', .2), ('band', .1)), 'curve-record')
    a, _ = d.admit(mind, 'r0', hyp, v, np.zeros(65), 1.)
    b, _ = d.admit(mind, 'r1', hyp, v, np.zeros(65), 1.)
    assert a != b
    assert set(d.laws[a]['coverage']) == {'r0'}
    assert set(d.laws[b]['coverage']) == {'r1'}
    # The same protection applies to a formula offered only as a free curve.
    expr = (('speed', 'expr', LG.node('var', payload='s')),)
    a, _ = d.admit(mind, 'r0', expr, v, np.zeros(65), 1.)
    b, _ = d.admit(mind, 'r1', expr, v, np.zeros(65), 1.)
    assert a != b
    d.observations['r0'] = [(0, (), (), ())]
    d.observations['r1'] = [(0, (), (), ())]
    class NoAudit:
        def certify(self, *args, **kwargs):
            raise AssertionError('A flexible class cannot be transferred')
    # A retained explicit free-curve class without a fixed drawing is skipped.
    key = next(k for k, e in d.laws.items() if e['hypothesis'] == hyp)
    assert d.transfer(mind, NoAudit(), key, math.inf) == []


def test_curve_certificate_keeps_fitted_cell_instead_of_coordinate_formula(monkeypatch):
    mind = entity()
    d = mind.discovery
    d.register_worlds((WorldView('r', 'strengths'),))
    expr = LG.node('add', LG.node('one'), LG.node('var', payload='s'))
    hyp = (('speed', 'expr', expr),)
    cell = ('cell', 'speed', 17)
    task = SimpleNamespace(claim_terms=lambda *args, **kwargs: ((cell,), ((cell, 'curve'),)),
        ledger=lambda *args: SimpleNamespace(mle=lambda *args: SimpleNamespace(ok=True)), context=lambda: [0.]*7)
    monkeypatch.setattr('sera_u.discovery.public_rail', lambda *args: task)
    seen = []
    def invent(*args, **kwargs):
        seen.append(args[1])
        return None
    monkeypatch.setattr(mind.engine, '_invent_part', invent)
    entry = dict(concept_ids=[], bits=1.)
    d._keep_physics(mind, 'r', hyp, Certification(True, 'curve', (('eps', .2),), 'r'), entry)
    assert seen == [('speed', 'curve', 17)]


def test_rail_design_gets_own_uncertainty_gain(monkeypatch):
    from ccops5.core import paths
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    monkeypatch.setattr(Readout, 'pick', fixed_policy)
    h = (('speed', 'curve', 17),)
    monkeypatch.setattr(Discovery, 'propose', lambda *args: (h,))
    monkeypatch.setattr(Discovery, 'rival_entropy', lambda self, mind, wid: 1. if len(self.observations[wid]) == 2 else .2)
    monkeypatch.setattr(Discovery, 'experiment_menu', lambda *args: [dict(action=('push', 0, ((0., .5, 1.),)),
        info=1., surprise=0., predicted=None)])
    d = Discovery(switches(hidden_quantities=False))
    mind = entity(hidden_quantities=False)
    mind.discovery = d
    d.register_worlds((WorldView('r', 'strengths'),))
    d.observations['r'] = [(0, ((0., .5, 1.),), (0.,)*paths.N_OBS, (0.,)*paths.N_OBS)]*2
    class RailPool:
        def public(self):
            return (WorldView('r', 'strengths'),)
        def act(self, wid, action):
            return action[1], action[2], (0.,)*paths.N_OBS, (0.,)*paths.N_OBS
        def certify(self, *args, **kwargs):
            return Certification(False, 'curve', (('eps', .2),), 'refused')
    row = mind.discover(RailPool())
    assert row['progress'] == pytest.approx(.8)
    assert np.linalg.norm(d.policy.own['split'][1]) > 0


def test_judge_extra_pushes_do_not_advance_world_noise(monkeypatch):
    from ccops5.core import paths
    own = (0, ((0., .5, 1.),), (0.,)*paths.N_OBS, (0.,)*paths.N_OBS)
    body = SimpleNamespace(sigma=(.001, .001), n_situations=8,
        spec=SimpleNamespace(family=()), held_out=[], situations=lambda: {}, made={0: 2}, log=[])
    pool = WorldPool(dict(worlds=[dict(id='r', form='strengths', seed=3, index=1)]))
    pool.bodies['r'] = body
    monkeypatch.setattr(TS.Rail, 'claim_terms', lambda *args, **kwargs: ((), ()))
    def verify(self, *args):
        self.world.made[0] += 10
        return False, SimpleNamespace(band=None, eps=.2), 'refused'
    monkeypatch.setattr(TS.Rail, 'verify', verify)
    pool.certify('r', (), {}, (own,))
    assert body.made == {0: 2} and body.log == []


def test_verdict_and_body_allowlists_reject_hidden_objects():
    private = object()
    with pytest.raises(TypeError):
        Certification(True, 'formula', (private,), 'record')
    with pytest.raises(ValueError):
        Certification(True, 'formula', (('eps', .05),), private)
    with pytest.raises(ValueError):
        WorldView('world', 'exact', tin='a hidden program')


def test_frozen_pool_checks_actual_acquired_course_overlap():
    p = plus()
    manifest = dict(schema='u9-discovery-1', worlds=[dict(id='w', form='exact', program=p,
        tin='num', tout='num', family=family(p, {}), seed=3, index=1)])
    suite = dict(assessment=[], wake=[], retention=[])
    mind = entity()
    view = TaskView((('x', 'num'),), 'num', tuple(((('x', x),), x+1) for x in (-2, 0, 1, 4)))
    r = Receipt.make(view, (p,), {}, scope='exact-audit', origin='taught', source='lesson')
    mind.checked_wake.add(r.id)
    mind.sleep.admit(r, {})
    with pytest.raises(ValueError, match='overlaps'):
        validate(manifest, suite, mind)


def test_certified_knowledge_survives_exact_resume_and_can_train(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    monkeypatch.setattr(Readout, 'pick', fixed_policy)
    monkeypatch.setattr(Discovery, 'propose', lambda self, mind, wid, deadline: (plus(),))
    monkeypatch.setattr('sera_u.discovery.time.perf_counter', lambda: 1.)
    a, pool = entity(), StubPool()
    a.discovery.register_worlds(pool.public())
    own_rows(a.discovery, 'w0')
    a.discover(pool)
    b = SeraU.loads(a.dumps())
    assert a.learning_hash() == b.learning_hash()
    assert a.discovery.laws.keys() == b.discovery.laws.keys()
    assert a.sleep.replay[0][0].acceptance == b.sleep.replay[0][0].acceptance
    # A real tiny CPU update checks the recursive bridge, rather than merely
    # asserting that a receipt was appended.
    a.train(1, 2)
    b.train(1, 2)
    assert a.learning_hash() == b.learning_hash()


def test_rail_pool_noise_counters_restore_from_own_acts_only():
    manifest = dict(worlds=[dict(id='r', form='strengths')])
    a, b = WorldPool(manifest), WorldPool(manifest)
    bodies = [SimpleNamespace(made={0: 999}, log=['judge-only']) for _ in range(2)]
    a.bodies['r'], b.bodies['r'] = bodies
    d = Discovery(switches())
    d.register_worlds((WorldView('r', 'strengths'),))
    d.observations['r'] = [(0, (), (), ()), (1, (), (), ()), (0, (), (), ())]
    a.sync(d)
    b.sync(copy.deepcopy(d))
    assert bodies[0].made == bodies[1].made == {0: 2, 1: 1}
    assert bodies[0].log == bodies[1].log == []
