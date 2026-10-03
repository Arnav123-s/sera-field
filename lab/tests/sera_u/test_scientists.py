"""U11 short CPU contracts. development review runs these; no old test is changed."""
import copy
import itertools
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
from sera_u.einstein import CRUTCHES as U10, Einstein
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import Engine, arm_settings
from sera_u.ports import TaskView, digest
from sera_u.scientists import CRUTCHES, Scientists, conserved_fit, motion_probes, one_change_actions, state_body
from scripts import sera_u_scientists as observer
from scripts.sera_u_discovery import validate


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


def var(name='x'):
    return LG.node('var', payload=name)


def plus(n):
    return LG.node('add', LG.node('mul', var(), var()), LG.node('lit', payload=n))


def law(p, wid):
    return dict(hypothesis=p, form='exact', signature=('num', 'num'), bits=LG.bits(p, {}),
        kind='formula', coverage={wid: (200., 0.)}, certificates={}, features=np.zeros(65), concept_ids=[])


class Ideas:
    def __init__(self):
        self.bindings = []

    def bind(self, *args):
        self.bindings.append(args)


def read(views):
    return [(torch.zeros(3, 64), torch.ones(3)/3) for _ in views]


def mind(concepts=None):
    concepts = concepts or {}
    return SimpleNamespace(field=SimpleNamespace(concept_table=lambda: concepts,
        concepts=[], shapes=lambda: (), ideas=Ideas(), standing={}, tasks=0, revisit_queue=[]),
        engine=SimpleNamespace(_u_reads=read), proposer=SimpleNamespace(memory=None),
        numpy=np.random.default_rng(3), random=random.Random(3),
        crutches=dict(sleep_library=False, taught_not_yet=True, inner_judge=False))


def discovery(**overrides):
    d = Discovery(dict.fromkeys(U9, True), einstein=dict.fromkeys(U10, False), scientists=switches(**overrides))
    d.register_worlds(tuple(WorldView('w'+str(j), 'exact') for j in range(4)))
    return d


def entity(science=None):
    settings = arm_settings('full')
    settings.update(memory_layer_a=False, memory_layer_b=False)
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=settings,
                 discovery=dict.fromkeys(U9, True), einstein=dict.fromkeys(U10, True), scientists=science)


class Pool:
    def public(self):
        return tuple(WorldView('w'+str(j), 'exact') for j in range(4))

    def act(self, wid, action):
        return action[1], action[1]+1

    def certify(self, wid, p, concepts, rows, *, library=()):
        return Certification(True, 'formula', (('audit_n', 100),), digest((wid, p)))


def test_registered_off_parity_and_no_extra_rng_or_payload(monkeypatch):
    for name in CRUTCHES:
        assert not CR.on(name) and name not in CR.settings()['crutches_effective']
    a, b = entity(), entity(dict.fromkeys(CRUTCHES, False))
    assert not hasattr(a.discovery, 'scientists') and not hasattr(b.field, 'scientist_methods')
    assert a.learning_hash() == b.learning_hash()
    assert a._payload().keys() == b._payload().keys()
    monkeypatch.setattr(Engine, '_u_reads', lambda self, views, concepts=None: read(views))
    monkeypatch.setattr(Discovery, 'propose', lambda *args: ())
    monkeypatch.setattr(Einstein, 'run', lambda *args, **kw: ([], dict(doubt=0.), []))
    monkeypatch.setattr(Einstein, 'target', lambda *args: None)
    monkeypatch.setattr('sera_u.discovery.time.perf_counter', lambda: 10.)
    assert a.discover(Pool()) == b.discover(Pool())
    assert a.learning_hash() == b.learning_hash()
    assert pickle.dumps(a.discovery.learning_state()) == pickle.dumps(b.discovery.learning_state())
    assert a.numpy.bit_generator.state == b.numpy.bit_generator.state
    assert generation_report(a.discovery.events) == generation_report(b.discovery.events)


@pytest.mark.parametrize('disabled', CRUTCHES)
def test_each_switch_only_removes_its_habit(disabled):
    d, m = discovery(**{disabled: False}), mind()
    assert set(d.scientists.methods.candidates()) == {('observe',)} | {(k,) for k in CRUTCHES if k != disabled}
    assert d.scientists.switches == switches(**{disabled: False})
    if disabled == 'gap_predictions':
        assert d.scientists.gap(m, d) == 0
    elif disabled == 'number_conjectures':
        assert d.scientists.conjecture(m, d, Pool(), 'w0') == 0
    elif disabled == 'conserved_quantities':
        assert d.scientists.conservation(m, d, Pool(), 'w0') == 0
    elif disabled == 'anomaly_pursuit':
        assert d.scientists.anomaly(d, 'w0', 'old', Certification(False, 'formula', (('audit_n', 1),), 'r', True)) is None


def test_one_change_exact_list_and_push_coordinates():
    world = WorldView('list', 'exact', 'list')
    rows = [((2, 4, -1), 0)]
    actions = one_change_actions(world, rows, [])
    assert len(actions) == 6
    for row in actions:
        a = row['action'][1]
        assert len(a) == 3 and sum(x != y for x, y in zip(a, rows[-1][0])) == 1
    rail = WorldView('r', 'strengths')
    segments = ((0., .5, -.5), (.5, 1., .5))
    actions = one_change_actions(rail, [(0, segments, (0.,), (0.,))], [])
    assert actions
    for row in actions:
        _, k, changed = row['action']
        assert k == 0 and len(changed) == 2
        assert sum(a[2] != b[2] for a, b in zip(changed, segments)) == 1
        assert all(a[:2] == b[:2] for a, b in zip(changed, segments))


def test_experiment_choice_and_return_learn_both_directions():
    d = discovery()
    d.observations['w0'] = [(2, 3)]
    x = np.r_[1., np.zeros(64)]
    d.policy.pick = lambda *args: 'one-change'
    row, route = d.scientists.choose_experiment(d, [], 'w0', x, np.random.default_rng(1))
    assert route == 'one-change' and row['one_change']
    d.policy.learn(route, x, 1., 1.)
    high = float(d.policy.posterior(route)[0] @ x)
    d.policy.learn(route, x, -4., 1.)
    assert float(d.policy.posterior(route)[0] @ x) < high
    assert one_change_actions(d.worlds['w1'], [], []) == ()


def test_gap_before_meeting_then_outer_confirmation(monkeypatch):
    d, m = discovery(), mind()
    for j, n in enumerate((2, 4, 8)):
        d.laws[str(j)] = law(plus(n), 'w'+str(j))
        d.observations['w'+str(j)] = [(1, n+1), (2, n+4)]
    pattern = LG.node('add', LG.node('mul', var(), LG.node('lit', payload=2)), LG.node('lit', payload=2))
    monkeypatch.setattr(LG, 'search', lambda *args, **kw: [(pattern, LG.size(pattern))])
    m.discovery = d
    assert d.scientists.gap(m, d) == 1
    p = d.scientists.predictions[0]
    assert p['hypothesis'] == plus(6) and p['world'] is None and p['performed_at'] is None
    assert not d.observations['w3'] and 'w3' not in p['seen_worlds']
    action, result = ('ask', 3), (3, 15)
    d.scientists.meet(d, 'w3', action, result)
    assert p['checks'][0]['matches'] and p['confirmed'] is None
    d.observations['w3'] = [result]
    verdict = Pool().certify('w3', plus(6), {}, (result,))
    d.admit(m, 'w3', plus(6), verdict, np.zeros(65), 1.)
    assert p['confirmed'] and p['recorded_at'] <= p['performed_at']
    assert p['result'] in d.laws


def test_irregular_family_has_no_gap_prediction(monkeypatch):
    d = discovery()
    for j, n in enumerate((2, 5, 10)):
        d.laws[str(j)] = law(plus(n), 'w'+str(j))
    monkeypatch.setattr(LG, 'search', lambda *a, **k: pytest.fail('irregular pattern must not be fitted'))
    assert d.scientists.gap(mind(), d) == 0
    assert not d.scientists.predictions


def acquired(body0, body1):
    return {0: (body0, '_'), 1: (body1, '_'), '_sig': {0: ('num', 'num'), 1: ('num', 'num')}}


def test_conjectures_own_values_exact_audit_and_no_false_proof(monkeypatch):
    u = var('_')
    table = acquired(LG.node('add', u, u), LG.node('mul', u, LG.node('lit', payload=2)))
    d, m = discovery(), mind(table)
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [])
    pool = observer.ScientistsPool(dict(worlds=[]))
    assert d.scientists.conjecture(m, d, pool, 'w0') == 1
    r = next(iter(d.scientists.relations.values()))
    assert r['own_values'] and r['standing'] == 1
    assert all(y == LG.safe(r['lhs'], {'x': x}, table) for x, y in r['own_values'])
    assert r['evidence'] == 'strong sampled evidence, not proof'
    assert pool.audit_records[0]['judge']['audit_n'] > 8
    assert not pool.audit_records[0]['false_credit']
    assert m.field.standing[r['key']][0] == 1


def test_false_conjecture_refuted_opens_not_yet(monkeypatch):
    u = var('_')
    square = LG.node('mul', u, u)
    conditional = LG.node('if', LG.node('lt', u, LG.node('lit', payload=2)), square,
                          LG.node('add', square, LG.node('one')))
    table = acquired(conditional, square)
    d, m = discovery(), mind(table)
    probes = itertools.cycle((-1, 0, 1))
    monkeypatch.setattr('sera_u.scientists.sample_input', lambda *a: next(probes))
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [])
    assert d.scientists.conjecture(m, d, observer.ScientistsPool(dict(worlds=[])), 'w0') == -1
    r = next(iter(d.scientists.relations.values()))
    assert r['status'] == 'refuted' and r['standing'] == 0
    assert d.pending and m.field.revisit_queue and not m.field.standing


def test_identical_expanded_checked_rewrite_is_exact(monkeypatch):
    u = var('_')
    table = acquired(LG.node('mul', u, u), LG.node('mul', u, u))
    d, m = discovery(), mind(table)
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [])
    assert d.scientists.conjecture(m, d, observer.ScientistsPool(dict(worlds=[])), 'w0') == 1
    assert next(iter(d.scientists.relations.values()))['evidence'] == 'exact checked rewrite'


def motion_spec(wid='r', conserved=True):
    return dict(id=wid, form='strengths', motion_sensor=True, has_conserved=conserved, seed=3, index=11)


def own_motion(body):
    from ccops5.core.worlds import Action
    return observer.throw_rows([body.push(0, Action(((0., .5, u),))) for u in (-1., 1.)])


def test_conserved_nontrivial_quantity_held_audit_and_across_worlds(monkeypatch):
    p = LG.node('rsub', var('v'), var('x'))
    d, m = discovery(), mind()
    pool = observer.ScientistsPool(dict(worlds=[motion_spec('r0'), motion_spec('r1')]))
    d.register_worlds(pool.public())
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [(LG.node('rone'), 1), (p, 3)])
    for wid in ('r0', 'r1'):
        d.observations[wid] = list(own_motion(pool.body(wid)))
        assert d.scientists.conservation(m, d, pool, wid) == 1
    entry = next(iter(d.scientists.conserved.values()))
    assert entry['worlds'] == ['r0', 'r1'] and entry['standing'] == 2
    assert m.field.standing[entry['key']][0] == 2
    assert all(not r['false_credit'] for r in pool.audit_records)
    assert not conserved_fit(LG.node('rone'), motion_probes(d.observations['r0']), {}, (.001, .001))
    assert not hasattr(d.scientists, 'pool')
    assert 'has_conserved' not in json.dumps(d.scientists.records())


def test_no_conserved_quantity_and_held_refutation(monkeypatch):
    p = LG.node('rsub', var('v'), var('x'))
    d = discovery()
    pool = observer.ScientistsPool(dict(worlds=[motion_spec(conserved=False)]))
    d.register_worlds(pool.public())
    d.observations['r'] = list(own_motion(pool.body('r')))
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [(p, 3)])
    assert d.scientists.conservation(mind(), d, pool, 'r') == 0
    assert not d.scientists.conserved
    assert not pool.audit_conserved('r', p, {}, None).accepted


def test_conservation_links_its_fitted_u9_hidden_quantity(monkeypatch):
    p = LG.node('rsub', var('v'), LG.node('rmul', var('q'), var('x')))
    d, m = discovery(), mind()
    pool = observer.ScientistsPool(dict(worlds=[motion_spec()]))
    d.register_worlds(pool.public())
    d.observations['r'] = list(own_motion(pool.body('r')))
    key = ('quantity', 'r', 'own-fit')
    d.quantities[key] = dict(values=tuple((k, 1.) for k in range(8)))
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [(p, 5)])
    assert d.scientists.conservation(m, d, pool, 'r') == 1
    entry = next(iter(d.scientists.conserved.values()))
    assert entry['quantity_keys'] == [key]
    assert (key, entry['key'], 1.) in m.field.ideas.bindings


def test_conserved_quantity_is_reusable_typed_state_concept(monkeypatch):
    p = LG.node('rsub', var('v'), var('x'))
    d, m = discovery(), mind()
    m.field = PH.Field(3)
    m.crutches['sleep_library'] = True
    m.proposer.changed = lambda: None
    pool = observer.ScientistsPool(dict(worlds=[motion_spec()]))
    d.register_worlds(pool.public())
    d.observations['r'] = list(own_motion(pool.body('r')))
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [(p, 3)])
    assert d.scientists.conservation(m, d, pool, 'r') == 1
    entry = next(iter(d.scientists.conserved.values()))
    concept = next(c for c in m.field.concepts if c['id'] == entry['concept_id'])
    assert concept['sig'] == ['list(real)', 'real']
    assert concept['audit_scope'] == 'sampled conservation, not a universal proof'
    env = dict(x=2., v=3., t=.5, q=1.)
    packed = tuple(env[k] for k in ('x', 'v', 't', 'q'))
    assert independent_state(concept['body'], packed) == LG.safe(p, env, {})


def independent_state(body, packed):
    from sera_u.sleep import independent
    return independent(body, {'_': packed}, {})


def test_anomaly_persists_across_items_and_returns_both_ways():
    d, m = discovery(), mind()
    d.active = 'w0'
    d.laws['old'] = law(plus(2), 'w1')
    verdict = Certification(False, 'formula', (('audit_n', 10),), 'odd', True)
    d.anomaly(m, 'w0', 'old', verdict)
    key = next(iter(d.scientists.chases))
    d.scientists.persistence.pick = lambda choices, *args: 'keep' if 'keep' in choices else key
    for serial in (1, 2):
        d.scientists.serial = serial
        assert d.scientists.pursue(m, d) == key
        row = dict(world='w0', seconds=1., experiment=('ask', serial), certified=None, progress=0.)
        d.scientists.feedback(d, [], {}, [], row, key)
    chase = d.scientists.chases[key]
    assert chase['status'] == 'active' and len(chase['attempts']) == 2
    x = np.r_[1., np.zeros(64)]
    low = float(d.scientists.persistence.posterior('keep')[0] @ x)
    assert low < 0
    d.laws['new'] = law(plus(6), 'w0')
    d.scientists.admitted(m, d, 'w0', 'new', True)
    assert chase['status'] == 'explained' and chase['explained_by'] == 'new'
    assert float(d.scientists.persistence.posterior('keep')[0] @ x) > low
    assert chase['seconds'] == 2. and chase['ended'] == 2
    original_gain = chase['gains'][-1]
    d.laws['new']['coverage']['w2'] = (200., 0.)
    d.scientists.admitted(m, d, 'w2', 'new', True)
    assert chase['also_explained'] == ['w2'] and chase['gains'][-1] > 0
    assert chase['compression_credit'] > original_gain-1.


def test_teacher_restricted_fades_and_conservation_once(monkeypatch):
    d, m = discovery(), mind()
    m.discovery = d
    view = observer.taught_motion_view(3)
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [(LG.node('rsub', var('v'), var('x')), 3)])
    shown = d.scientists.demonstrate(m, view, phase='lesson', origin='taught')
    assert set(shown) == set(CRUTCHES)
    assert ('scientists', ('gap_predictions',)) in d.scientists.methods.taught
    again = d.scientists.demonstrate(m, view, phase='lesson', origin='taught')
    assert 'conserved_quantities' not in again
    taught = sum(float(a.sum()) for a, _ in d.scientists.methods.taught.values())
    d.scientists.methods.end_task()
    assert sum(float(a.sum()) for a, _ in d.scientists.methods.taught.values()) < taught
    d.scientists.phase('test3', d)
    assert all(not np.any(a) and not np.any(b) for a, b in d.scientists.methods.taught.values())
    for phase, origin in (('lesson', 'explore'), ('test2', 'taught'), ('test3', 'taught')):
        with pytest.raises(ValueError):
            d.scientists.demonstrate(m, view, phase=phase, origin=origin)


def test_checkpoint_next_draw_and_timestamp_free_hash():
    a = entity(switches())
    s = a.discovery.scientists
    s.predictions.append(dict(id='p', recorded_at=10., performed_at=20., hypothesis=plus(6)))
    s.chases['c'] = dict(seconds=3., status='active', attempts=[], eligibility=[])
    h = a.learning_hash()
    s.predictions[0].update(recorded_at=999., performed_at=1000.)
    s.chases['c']['seconds'] = 600.
    s.metrics['gap_predictions']['seconds'] = 500.
    assert a.learning_hash() == h
    b = SeraU.loads(a.dumps())
    assert b.learning_hash() == a.learning_hash()
    assert b.field.scientist_methods is b.discovery.scientists.methods
    assert b.field.einstein_methods is b.discovery.einstein.methods
    moment = dict(doubt=1., misfit=0., proven=0)
    assert a.discovery.scientists.methods.choose('scientists', set(CRUTCHES)|{'observe'}, moment, a.numpy) == \
           b.discovery.scientists.methods.choose('scientists', set(CRUTCHES)|{'observe'}, moment, b.numpy)


def test_checkpoint_resume_next_ticks_and_failed_unit_rollback(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', lambda self, views, concepts=None: read(views))
    monkeypatch.setattr(Discovery, 'propose', lambda *args: ())
    monkeypatch.setattr(Einstein, 'run', lambda *args, **kw: ([], dict(doubt=0.), []))
    monkeypatch.setattr(Einstein, 'target', lambda *args: None)
    monkeypatch.setattr('sera_u.discovery.time.perf_counter', lambda: 10.)
    a = entity(switches())
    a.discover(Pool())
    b = SeraU.loads(a.dumps())
    for _ in range(2):
        assert a.discover(Pool()) == b.discover(Pool())
        assert a.learning_hash() == b.learning_hash()
        assert a.numpy.bit_generator.state == b.numpy.bit_generator.state
    class Broken(Pool):
        def act(self, *args):
            raise RuntimeError('failed performed unit')
    h = a.learning_hash()
    with pytest.raises(RuntimeError):
        a.discover(Broken())
    assert a.learning_hash() == h
    assert a.field.scientist_methods is a.discovery.scientists.methods


def test_noether_off_runs_no_teacher_search(monkeypatch):
    d, m = discovery(conserved_quantities=False), mind()
    m.discovery = d
    monkeypatch.setattr(LG, 'search', lambda *a, **k: pytest.fail('disabled habit searched'))
    shown = d.scientists.demonstrate(m, observer.taught_motion_view(3), phase='lesson', origin='taught')
    assert 'conserved_quantities' not in shown and not d.scientists.conservation_shown


def test_audit_failure_does_not_grant_conserved_standing(monkeypatch):
    p = LG.node('rsub', var('v'), var('x'))
    d, m = discovery(), mind()
    pool = observer.ScientistsPool(dict(worlds=[motion_spec()]))
    d.register_worlds(pool.public())
    d.observations['r'] = list(own_motion(pool.body('r')))
    monkeypatch.setattr(LG, 'search', lambda *a, **k: [(p, 3)])
    monkeypatch.setattr(pool, 'audit_conserved', lambda *a: Certification(False, 'formula', (('held_throws', 24),), 'no', True))
    assert d.scientists.conservation(m, d, pool, 'r') == -1
    assert not d.scientists.conserved and not m.field.standing
    assert d.pending and m.field.revisit_queue


def test_record_deltas_preserve_chase_history():
    from sera_u.discovery import scientist_records
    d, m = discovery(), mind()
    d.anomaly(m, 'w0', 'old', Certification(False, 'formula', (('audit_n', 1),), 'odd', True))
    key = next(iter(d.scientists.chases))
    first = d.scientists.records()
    d.scientists.chases[key]['attempts'].append(dict(item=1))
    d.scientists.chases[key]['gains'].append(-.01)
    second = d.scientists.records_delta(first)
    previous = d.scientists.records()
    d.scientists.chases[key]['attempts'].append(dict(item=2))
    d.scientists.chases[key]['gains'].append(1.)
    third = d.scientists.records_delta(previous)
    merged = scientist_records([dict(scientist_records=first), dict(scientist_records=second), dict(scientist_records=third)])
    assert merged['chases'][key]['attempts'] == [dict(item=1), dict(item=2)]
    assert merged['chases'][key]['gains'] == [-.01, 1.]


def test_withheld_observer_members_only_after_seed_certification():
    specs = [dict(id='w'+str(j), form='exact', program=plus(2+2*c), tin='num', tout='num',
                  observer_group='g', observer_coordinate=c, withheld=c == 2, seed=3, index=j)
             for j, c in enumerate((0, 1, 3, 2))]
    pool = observer.ScientistsPool(dict(worlds=specs))
    assert 'w3' not in {w.id for w in pool.public()}
    with pytest.raises(ValueError):
        pool.act('w3', ('ask', 0))
    pool.met_certified = {'w0', 'w1', 'w2'}
    assert 'w3' in {w.id for w in pool.public()}
    d = discovery()
    for j in range(3):
        d.laws[str(j)] = law(plus(j), 'w'+str(j))
    pool.sync(d)
    assert pool.available('w3')


def test_scientists_observer_freezes_and_validates_without_teaching(monkeypatch):
    suite = {k: [] for k in ('retention', 'wake', 'assessment')}
    monkeypatch.setattr(observer, 'freeze_einstein', lambda *a: dict(schema='u9-discovery-1',
        einstein_suite='u10-einstein-1', seed=3, worlds=[], dropped=[], split='stub'))
    a = observer.freeze_scientists(None, suite, 3)
    b = observer.freeze_scientists(None, suite, 3)
    assert a == b and a['scientists_suite'] == observer.SCIENTISTS_SCHEMA
    assert len([r for r in a['worlds'] if r.get('withheld')]) == 2
    assert len([r for r in a['worlds'] if r.get('motion_sensor')]) == 3
    assert validate(a, suite) == a
    d = discovery()
    pool = observer.ScientistsPool(a)
    d.register_worlds(pool.public())
    public = pickle.dumps(d.learning_state())
    assert b'has_conserved' not in public and b'observer_group' not in public
    assert all(type(w) is WorldView for w in pool.public())


def test_reports_keep_counts_false_credit_and_plain_claim():
    d = discovery()
    row = dict(seconds=1., experiment=None, certified=None, discovered=False,
               scientists=d.scientists.report(), scientist_records=d.scientists.records())
    generation = dict(arm='full', generation=0, **generation_report([row]))
    report = observer.report_scientists([generation], [dict(false_credit=False)])
    assert report['zero_false_credit'] and 'hidden structure' in report['claim']
    assert observer.report_scientists([generation], [dict(false_credit=True)])['false_credit'] == 1
    assert report['arms']['full']['scientists']['chases_started'] == 0
    json.dumps(d.scientists.records(), allow_nan=False)
