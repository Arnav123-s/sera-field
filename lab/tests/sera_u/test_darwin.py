"""U12 short CPU contracts; no existing test is changed."""
import copy
import json
import math
import pickle
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, phi as PH
from sera_u import SeraU
from sera_u.darwin import CRUTCHES, Darwin, clean, distance, distribution, distribution_loss, tree_code
from sera_u.discovery import CRUTCHES as U9, Discovery, WorldView, generation_report
from sera_u.einstein import CRUTCHES as U10, Einstein
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import Engine, arm_settings
from sera_u.ports import TaskView
from sera_u.scientists import CRUTCHES as U11, Scientists
from scripts import sera_u_darwin as observer
from tests.sera_u.test_scientists import Ideas, Pool, law, mind, read, var


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


def entity(habits=None):
    settings = arm_settings('full')
    settings.update(memory_layer_a=False, memory_layer_b=False)
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=settings,
                 discovery=dict.fromkeys(U9, True), einstein=dict.fromkeys(U10, True),
                 scientists=dict.fromkeys(U11, True), darwin=habits)


def stub(concepts=None, habits=None, worlds=16):
    learner = mind(concepts)
    discovery = Discovery(dict.fromkeys(U9, True), einstein=dict.fromkeys(U10, False),
        scientists=dict.fromkeys(U11, False), darwin=habits or switches())
    discovery.register_worlds(tuple(WorldView('w'+str(index), 'exact') for index in range(worlds)))
    learner.discovery = discovery
    discovery.darwin.attach(learner.field)
    return learner, discovery, discovery.darwin


def population(learner, discovery, values=(0, 1, 2, 3), *, offset=0, complex_base=False):
    base = var()
    if complex_base:
        for _ in range(5):
            base = LG.node('mul', base, var())
    for index, parameter in enumerate(values, offset):
        wid = 'w'+str(index)
        program = LG.node('add', base, LG.node('lit', payload=parameter))
        discovery.laws[wid] = law(program, wid)
        discovery.observations[wid] = [(0, parameter)]
        discovery.darwin.receive(learner, discovery, wid, ('ask', 0), (0, parameter))


def predicate_concepts():
    argument = LG.node('var', payload='_')
    lower = LG.node('if', LG.node('lt', LG.node('lit', payload=-1), argument), LG.node('one'), LG.node('zero'))
    upper = LG.node('if', LG.node('lt', argument, LG.node('lit', payload=4)), LG.node('one'), LG.node('zero'))
    predicate = LG.node('eq', LG.node('mul', lower, upper), LG.node('one'))
    return {0: (predicate, '_'), '_sig': {0: ('num', 'bool')}}


def cheap_ticks(monkeypatch):
    monkeypatch.setattr(Engine, '_u_reads', lambda self, views, concepts=None: read(views))
    monkeypatch.setattr(Discovery, 'propose', lambda *args: ())
    monkeypatch.setattr(Einstein, 'run', lambda *args, **kwargs: ([], dict(doubt=0.), []))
    monkeypatch.setattr(Einstein, 'target', lambda *args: None)
    monkeypatch.setattr(Scientists, 'run', lambda *args, **kwargs: ([], {}, [], None))
    monkeypatch.setattr(Scientists, 'feedback', lambda *args, **kwargs: None)
    monkeypatch.setattr('sera_u.discovery.time.perf_counter', lambda: 10.)


def test_registered_default_off_exact_u11_path(monkeypatch):
    for name in CRUTCHES:
        assert not CR.on(name)
        assert name not in CR.settings()['crutches_effective']
    implicit, explicit = entity(), entity(dict.fromkeys(CRUTCHES, False))
    assert not hasattr(implicit.discovery, 'darwin')
    assert not hasattr(implicit.field, 'hologram')
    assert implicit.learning_hash() == explicit.learning_hash()
    assert implicit._payload().keys() == explicit._payload().keys()
    cheap_ticks(monkeypatch)
    for _ in range(2):
        assert implicit.discover(Pool()) == explicit.discover(Pool())
        assert implicit.learning_hash() == explicit.learning_hash()
    assert pickle.dumps(implicit.discovery.learning_state()) == pickle.dumps(explicit.discovery.learning_state())
    assert implicit.numpy.bit_generator.state == explicit.numpy.bit_generator.state
    assert generation_report(implicit.discovery.events) == generation_report(explicit.discovery.events)


@pytest.mark.parametrize('missing', CRUTCHES)
def test_each_ablation_removes_its_candidate_only(missing):
    controller = Darwin(switches(**{missing: False}))
    assert controller.methods.candidates() == [('observe',)] + [(name,) for name in CRUTCHES if name != missing]
    learner, discovery, controller = stub(habits=switches(**{missing: False}))
    population(learner, discovery, complex_base=True)
    region = controller.region(discovery, 'w0')
    if missing == 'patient_observation':
        assert not learner.field.hologram['notebook']
    if missing == 'world_hologram':
        assert not learner.field.hologram['regions']
        assert controller.imagine(learner, discovery, region) is None
        assert controller.tree(learner, discovery, region) is not None
    if missing == 'lineage_trees':
        assert controller.tree(learner, discovery, region) is None
    if missing == 'change_mechanisms':
        assert controller.imagine(learner, discovery, region) is None
        assert not learner.field.hologram['mechanisms']


def test_imagination_is_only_received_material_and_never_certifies():
    learner, discovery, controller = stub(predicate_concepts())
    population(learner, discovery)
    before = copy.deepcopy(discovery.laws)
    key = controller.imagine(learner, discovery, controller.region(discovery, 'w0'), generations=8)
    assert key is not None
    assert learner.field.hologram['dreams']
    assert all(row['imagined'] and not row['certified'] for row in learner.field.hologram['dreams'])
    assert pickle.dumps(before) == pickle.dumps(discovery.laws)
    retained = repr(learner.field.hologram)
    for forbidden in ('observer_parent', 'observer_edit', 'observer_sorting', 'frozen_samples'):
        assert forbidden not in retained
    assert not hasattr(controller, 'pool')
    assert not hasattr(controller, 'regions')


def test_hologram_fresh_prediction_improves_and_thin_regions_are_less_sure():
    learner, discovery, controller = stub()
    controller.receive(learner, discovery, 'w0', ('ask', 0), (0, 2))
    first = controller.forecast(learner, discovery, 'w1', ('ask', 0))
    assert first['probability'] < .5
    discovery.laws['own'] = law(LG.node('add', var(), LG.node('lit', payload=2)), 'w0')
    for index in range(1, 8):
        wid = 'w'+str(index)
        forecast = controller.forecast(learner, discovery, wid, ('ask', 0))
        controller.receive(learner, discovery, wid, ('ask', 0), (0, 2), forecast)
    later = controller.forecast(learner, discovery, 'w8', ('ask', 7))
    assert later['predicted'] == 9
    assert later['probability'] > first['probability']
    region = controller.region(discovery, 'w0')
    state = learner.field.hologram['regions'][region]
    assert state['correct'] == state['trials'] == 7
    assert sum(bucket[0] for bucket in state['bins'].values()) == 7
    assert state['brier']/state['trials'] < .5
    assert later['baseline'] is None


def test_wrong_picture_opens_not_yet_and_curiosity_without_revoking_laws():
    learner, discovery, controller = stub()
    learner.crutches['gap_syndromes'] = True
    learner.field.curiosity = SimpleNamespace(observe=lambda *args: seen.append(args),
        decode=lambda view, checks, reads: decoded.extend(checks))
    decoded = []
    seen = []
    population(learner, discovery, (0,))
    forecast = controller.forecast(learner, discovery, 'w1', ('ask', 0))
    controller.receive(learner, discovery, 'w1', ('ask', 0), (0, 999), forecast)
    assert any(row['world'] == 'w1' for row in discovery.pending)
    assert any(row['discovery_world'] == 'w1' for row in learner.field.revisit_queue)
    assert seen == [('hologram-misfit', 1.)]
    assert decoded[0].check == 'surprise' and decoded[0].parts[0][0] == 'hologram-region'
    assert 'w0' in discovery.laws


def test_patient_notebook_spans_generations_and_delayed_eligibility_moves_both_ways():
    learner, discovery, controller = stub()
    feature = np.r_[1., np.zeros(64)]
    controller.receive(learner, discovery, 'w0', ('ask', 0), (0, 1))
    entry = learner.field.hologram['notebook'][0]
    entry['eligibility'] = [('keep', feature)]
    learner.field.hologram['generation'] = 2
    controller.receive(learner, discovery, 'w1', ('ask', 0), (0, 2))
    assert [row['generation'] for row in learner.field.hologram['notebook']] == [0, 2]
    positive = dict(world='w0', seconds=1., certified=dict(accepted=True))
    controller.feedback(learner, discovery, ([], {}, False, feature), positive, 0.)
    assert 'certificate' in entry['settled']
    before = controller.watch.posterior('keep')[0] @ feature
    for _ in range(32):
        controller.watch.learn('keep', feature, -1., 1.)
    assert controller.watch.posterior('keep')[0] @ feature < before
    assert pickle.loads(pickle.dumps(learner.field.hologram))['notebook'][0]['settled'] == ['certificate']


def test_related_tree_compresses_unrelated_worlds_have_no_credit():
    learner, discovery, controller = stub()
    population(learner, discovery, complex_base=True)
    result = controller.tree(learner, discovery, controller.region(discovery, 'w0'))
    assert result['compression_credit'] > 0
    assert result['dictionary'] and len(result['edges']) == 3
    assert 'hypothesis' in result['claim']
    unrelated = [var(), LG.node('lit', payload=7), LG.node('one')]
    baseline, code, dictionary = tree_code(unrelated, {})
    assert baseline == code and not dictionary
    assert distance(LG.node('add', var(), LG.node('lit', payload=1)),
                    LG.node('add', var(), LG.node('lit', payload=2))) == 1


def test_mechanism_matches_predicts_later_worlds_and_audits_sorting():
    learner, discovery, controller = stub(predicate_concepts())
    population(learner, discovery)
    key = controller.imagine(learner, discovery, controller.region(discovery, 'w0'), generations=8)
    mechanism = learner.field.hologram['mechanisms'][key]
    assert mechanism['distribution_loss'] == 0.
    assert mechanism['imagined_generations'] == 8
    assert mechanism['rejected'] > 0 and mechanism['status'] == 'conjecture'
    feature = np.r_[1., np.zeros(64)]
    prediction = controller.predict_population(learner, key, feature, '8', .01)
    assert prediction is not None
    issued = learner.field.hologram['predictions'][0]['issued']
    population(learner, discovery, offset=4)
    assert all(learner.field.hologram['arrivals']['w'+str(index)] > issued for index in range(4, 8))
    assert controller.settle_populations(learner, discovery) == 1.
    record = learner.field.hologram['predictions'][0]
    assert record['confirmed'] is True and set(record['contributors']) == {'w4', 'w5', 'w6', 'w7'}
    assert mechanism['audits'][0]['sorting_matches'] == mechanism['audits'][0]['sorting_tested'] == 4
    assert mechanism['status'] == 'supported' and not mechanism['certified']


def test_failed_population_prediction_gets_no_credit_and_opens_not_yet():
    learner, discovery, controller = stub(predicate_concepts())
    population(learner, discovery)
    key = controller.imagine(learner, discovery, controller.region(discovery, 'w0'))
    controller.predict_population(learner, key, np.zeros(65), '1', .01)
    population(learner, discovery, (10, 11, 12, 13), offset=4)
    assert controller.settle_populations(learner, discovery) == 0.
    assert learner.field.hologram['predictions'][0]['confirmed'] is False
    assert any(row['world'] == 'w4' for row in discovery.pending)


def test_noise_without_reusable_edits_or_predicates_keeps_no_mechanism():
    learner, discovery, controller = stub(predicate_concepts())
    population(learner, discovery, (1, 7, 19, 43))
    assert controller.imagine(learner, discovery, controller.region(discovery, 'w0')) is None
    assert not learner.field.hologram['mechanisms']
    learner, discovery, controller = stub()
    population(learner, discovery)
    assert controller.imagine(learner, discovery, controller.region(discovery, 'w0')) is None


def test_deep_time_no_teacher_or_world_calls_and_negative_returns():
    learner, discovery, controller = stub(predicate_concepts())
    population(learner, discovery)
    before = copy.deepcopy(discovery.observations)
    controller.imagine(learner, discovery, controller.region(discovery, 'w0'), generations=64)
    assert discovery.observations == before
    feature = np.r_[1., np.zeros(64)]
    controller.time_choice.learn('64', feature, 1., 1.)
    positive = controller.time_choice.posterior('64')[0] @ feature
    controller.time_choice.learn('64', feature, -1., 1.)
    assert controller.time_choice.posterior('64')[0] @ feature < positive


def test_teaching_fades_by_taught_fade_and_u5_phase_weights():
    learner, discovery, controller = stub()
    view = TaskView((('x', 'num'),), 'num', (((('x', 0),), 1),))
    assert controller.demonstrate(learner, view, phase='lesson', origin='taught') == CRUTCHES
    before = {key: value[0].copy() for key, value in controller.methods.taught.items()}
    controller.methods.end_task()
    for key, value in controller.methods.taught.items():
        np.testing.assert_allclose(value[0], before[key]*PH.TAUGHT_FADE)
    controller.phase('study')
    for key, value in controller.methods.taught.items():
        np.testing.assert_allclose(value[0], before[key]*PH.TAUGHT_FADE*.6)
    controller.phase('test3')
    assert all(not np.any(value[0]) for value in controller.methods.taught.values())
    with pytest.raises(ValueError):
        controller.demonstrate(learner, view, phase='test3', origin='explore')


def test_checkpoint_exact_resume_and_no_elapsed_in_learning_hash(monkeypatch):
    cheap_ticks(monkeypatch)
    original = entity(switches())
    original.discover(Pool())
    original.field.hologram['predictions'].append(dict(recorded_at=1., performed_at=2., seconds=3., result=()))
    before = original.learning_hash()
    original.field.hologram['predictions'][0].update(recorded_at=999., performed_at=888., seconds=777.)
    original.discovery.darwin.costs.update(real=333., imagined=444.)
    assert original.learning_hash() == before
    original.field.hologram['predictions'].clear()
    resumed = SeraU.loads(original.dumps())
    assert resumed.learning_hash() == original.learning_hash()
    assert resumed.field.darwin_methods is resumed.discovery.darwin.methods
    for _ in range(2):
        assert original.discover(Pool()) == resumed.discover(Pool())
        assert original.learning_hash() == resumed.learning_hash()
        assert original.numpy.bit_generator.state == resumed.numpy.bit_generator.state


def test_distribution_finite_bounded_and_cleanup_recursive():
    assert distribution_loss(distribution([1, 2]), distribution([2, 1])) == 0.
    assert distribution_loss(distribution([1]), distribution([9])) == 1.
    assert clean(dict(nested=(dict(seconds=2., recorded_at=3., value=4),))) == dict(nested=({'value': 4},))
    json.dumps(dict(loss=distribution_loss((), distribution([1]))), allow_nan=False)


def test_observer_held_back_release_and_boundary(monkeypatch):
    program = LG.node('add', var(), LG.node('lit', payload=2))
    rows = []
    for index in range(2):
        row = dict(id='a'+str(index), form='exact', tin='num', tout='num', program=program,
            family='unused-stub', seed=3, index=index, observer_birth=index,
            observer_parent=None if index == 0 else 'a0', observer_parameter=2,
            observer_edit=0, observer_population='num', observer_sorting='secret',
            frozen_samples=((0, 2), (1, 3), (2, 4), (3, 5)))
        rows.append(row)
    manifest = dict(lineage_suite=observer.SCHEMA, worlds=rows)
    pool = observer.LineagePool(manifest, generation=0)
    assert [world.id for world in pool.public()] == ['a0']
    assert all(type(world) is WorldView for world in pool.public())
    with pytest.raises(ValueError):
        pool.act('a1', ('ask', 0))
    learner, discovery, controller = stub(worlds=0)   # only the pool's worlds: sync reads each registered world's spec
    discovery.register_worlds(pool.public())
    wid, samples = pool.next_specimen(discovery)
    assert wid == 'a0' and samples == rows[0]['frozen_samples']
    assert pool.next_specimen(discovery) is None
    discovery.observations[wid] = list(samples)
    pool.sync(discovery)
    assert pool.next_specimen(discovery) is None
    pool.generation = 1
    assert pool.next_specimen(discovery)[0] == 'a1'
    assert 'observer_parent' not in repr(pool.public())


def test_freeze_deterministic_disjoint_and_no_student_hidden_lineage(monkeypatch):
    suite = dict(retention=[], wake=[], assessment=[])
    base = dict(schema='u9-discovery-1', scientists_suite='u11-scientists-1', worlds=[], split='stub')
    monkeypatch.setattr(observer, 'freeze_scientists', lambda *args: copy.deepcopy(base))
    first = observer.freeze_lineage(None, suite, 3)
    second = observer.freeze_lineage(None, suite, 3)
    assert first == second
    assert first['lineage_suite'] == observer.SCHEMA
    assert len(first['worlds']) == 80
    assert {row['observer_birth'] for row in first['worlds']} == {0, 1, 2, 3}
    assert all(row['frozen_samples'] for row in first['worlds'])
    corrupt = copy.deepcopy(first)
    corrupt['worlds'][8]['observer_parent'] = 'missing'
    with pytest.raises(ValueError):
        observer.validate_lineage(corrupt)


def test_fitted_rail_picture_and_parameter_tree_never_read_true_parameters():
    learner, discovery, controller = stub()
    worlds = tuple(WorldView('r'+str(index), 'strengths') for index in range(4))
    discovery.register_worlds(worlds)
    for index, world in enumerate(worlds):
        for force in (-.5, .5):
            action = ('push', 0, ((0., 1., force),))
            intercept = 10.+.01*index
            values = (intercept+force, intercept+2*force)
            observation = (0, action[2], values, values)
            discovery.observations[world.id].append(observation)
            controller.receive(learner, discovery, world.id, action, observation)
    region = controller.region(discovery, 'r0')
    picture = controller.picture(learner, discovery, region)
    assert len(picture['material']) == 4
    assert all(row['fitted'] and not row['certified'] for row in picture['material'])
    tree = controller.tree(learner, discovery, region)
    assert tree['compression_credit'] > 0
    vectors = {0: tree['root']}
    for parent, child, delta in tree['deltas']:
        vectors[child] = tuple(before+change for before, change in zip(vectors[parent], delta))
    assert len(vectors) == 4
    before = copy.deepcopy(discovery.observations)
    controller.imagine(learner, discovery, region)
    assert learner.field.hologram['dreams']
    assert discovery.observations == before
    assert not any(row['certified'] for row in learner.field.hologram['dreams'])


def test_tree_dictionary_reconstructs_received_programs():
    learner, discovery, controller = stub()
    population(learner, discovery, complex_base=True)
    tree = controller.tree(learner, discovery, controller.region(discovery, 'w0'))
    def decode(program):
        if program[0] == 'shared-subtree':
            return tree['dictionary'][program[1]]
        return program[:2]+tuple(decode(child) for child in program[2:])
    expected = tuple(row['program'] for row in controller.material(discovery, controller.region(discovery, 'w0')))
    assert tuple(decode(program) for program in tree['residual_programs']) == expected


def test_report_strict_json_and_prediction_snapshot_prevents_retrospective_change():
    learner, discovery, controller = stub(predicate_concepts())
    population(learner, discovery)
    key = controller.imagine(learner, discovery, controller.region(discovery, 'w0'))
    controller.predict_population(learner, key, np.zeros(65), '1', .01)
    recorded = learner.field.hologram['predictions'][0]
    before = copy.deepcopy(recorded['population'])
    learner.field.hologram['mechanisms'][key]['population'] = ()
    assert recorded['population'] == before
    report = controller.report(learner.field)
    assert 'feature' not in report['predictions'][0]
    json.dumps(report, allow_nan=False, sort_keys=True)


def test_checkpoint_failed_unit_rolls_back_u12_state(monkeypatch):
    cheap_ticks(monkeypatch)
    original = entity(switches())
    before = original.learning_hash()
    class Broken(Pool):
        def act(self, *args):
            raise RuntimeError('stub body failure')
    with pytest.raises(RuntimeError):
        original.discover(Broken())
    assert original.learning_hash() == before
    assert not original.field.hologram['arrivals']


def test_fitted_parameter_mechanism_runs_and_predicts_fresh_sensor_specimens():
    learner, discovery, controller = stub(predicate_concepts())
    discovery.register_worlds(tuple(WorldView('r'+str(index), 'strengths') for index in range(8)))
    def receive(first, last):
        for index in range(first, last):
            wid = 'r'+str(index)
            for force in (-.5, .5):
                action = ('push', 0, ((0., 1., force),))
                parameter = (index % 4)*.001
                observation = (0, action[2], (parameter+force,), (parameter+force,))
                discovery.observations[wid].append(observation)
                controller.receive(learner, discovery, wid, action, observation)
    receive(0, 4)
    region = controller.region(discovery, 'r0')
    key = controller.imagine(learner, discovery, region, generations=8)
    assert key is not None
    mechanism = learner.field.hologram['mechanisms'][key]
    assert mechanism['parameter_rule'] and mechanism['rejected']
    controller.predict_population(learner, key, np.zeros(65), '8', .01)
    receive(4, 8)
    assert controller.settle_populations(learner, discovery) == 1.
    prediction = learner.field.hologram['predictions'][0]
    assert prediction['confirmed'] and prediction['parameter_rule']
    assert prediction['contributors'] == ['r4', 'r5', 'r6', 'r7']
    assert all(prediction['sorting_checks']) and not mechanism['certified']


def test_hologram_superposition_owns_its_write_without_reenabling_generic_memory():
    learner = entity(switches())
    discovery = learner.discovery
    discovery.register_worlds((WorldView('w', 'exact'),))
    with learner.scope():
        discovery.darwin.receive(learner, discovery, 'w', ('ask', 0), (0, 1))
        region = discovery.darwin.region(discovery, 'w')
        assert ('hologram-region', region) in learner.field.ideas._row
        assert not learner.memory.b and not learner.memory.a
