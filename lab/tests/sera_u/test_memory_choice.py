"""U8 CPU contracts. Slow native settles/searches are replaced by public stubs."""
import copy
import math
import pickle
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from scripts import sera_u_course as UC
from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.memory import add_count, counts, memory_records, public_context
from sera_u.mind import AssessmentTask, Engine, U3_CRUTCHES, U6_CRUTCHES, U7_CRUTCHES, arm_settings
from sera_u.ports import TaskView


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


class MeanDraw:
    def multivariate_normal(self, mean, covariance):
        return mean.copy()


def feature(sign=0., spent=0.):
    branches = np.zeros((3, 64))
    branches[:, 0] = sign
    return PH.MemoryChoice.features(branches, spent)


def entity(**switches):
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1),
                 crutches={**arm_settings('full'), 'memory_choice': True, **switches})


def world():
    return TS.Exact('math', 'public numbers', lambda v: v+1, {'x': 'num'}, 'num',
                    [0, 1, 2, 3], [4, 5], lambda rng: 6)


def cheap_owner(monkeypatch, mind):
    calls = []
    def observe(state, source, **kwargs):
        return {**state, 'fast': .75*state['fast']+.25*source,
                'events': state['events']+1}, {'energy_defect': source.new_zeros(len(source))}
    def read(view, *, state=None, ring=None, **kwargs):
        state = mind.owner.empty(1) if state is None else state
        value = float(state['events'][0]) + (100. if ring is not None else 0.)
        calls.append((view, value))
        return torch.full((3, 64), value), torch.ones(3)/3, state
    def many(views, *, states=None, rings=None, **kwargs):
        return [read(v, state=None if states is None else states[j],
                     ring=None if rings is None else rings[j], **kwargs) for j, v in enumerate(views)]
    monkeypatch.setattr(mind.owner, 'observe', observe)
    monkeypatch.setattr(mind.owner, 'remembered', lambda state: state['fast'])
    monkeypatch.setattr(mind.owner, 'task_features', read)
    monkeypatch.setattr(mind.owner, 'task_features_many', many)
    monkeypatch.setattr(mind.owner, 'read_features_many', many)   # US3's reader (merged after U8 was written)
    return calls


def force_options(monkeypatch, *, consult='both', remember='both'):
    def pick(self, kind, decision, f, available, rng):
        option = consult if decision == 'consult' else remember
        assert option in available
        self.taken[decision][option] = self.taken[decision].get(option, 0)+1
        return option, {o: (0., 0.) for o in available}
    monkeypatch.setattr(PH.MemoryChoice, 'pick', pick)


def test_neutral_prior_and_contextual_returns_choose_memory_more_then_less():
    head = PH.MemoryChoice()
    positive, negative = feature(1.), feature(-1.)
    mean, cov = head.posterior('kind', 'consult', 'a')
    assert not mean.any() and np.array_equal(cov, np.eye(head.DIM))
    def share(f):
        rng = np.random.default_rng(37)
        return sum(head.pick('kind', 'consult', f, ('plain', 'a'), rng)[0] == 'a' for _ in range(32))
    before = share(positive)
    for _ in range(24):
        head.learn('kind', 'consult', 'a', positive, 3.)
        head.learn('kind', 'consult', 'plain', positive, .1)
        head.learn('kind', 'consult', 'a', negative, -3.)
        head.learn('kind', 'consult', 'plain', negative, .1)
    assert share(positive) > before > share(negative)
    for _ in range(72):
        head.learn('kind', 'consult', 'a', positive, -3.)
    assert head.pick('kind', 'consult', positive, ('plain', 'a'), MeanDraw())[0] == 'plain'


def test_teacher_evidence_moves_choice_then_fades_and_learned_evidence_survives():
    head, f = PH.MemoryChoice(), feature()
    for _ in range(12):
        head.demonstrate('kind', 'consult', f, ('plain', 'b'), 'b')
    assert head.pick('kind', 'consult', f, ('plain', 'b'), MeanDraw())[0] == 'b'
    before = copy.deepcopy(head.taught)
    head.learn('kind', 'remember', 'b', f, 2.)
    learned = copy.deepcopy(head.stats)
    head.end_item()
    for key in before:
        for a, b in zip(head.taught[key], before[key]):
            np.testing.assert_array_equal(a, b*PH.TAUGHT_FADE)
    for _ in range(100):
        head.end_item()
    assert abs(head.posterior('kind', 'consult', 'b')[0] @ f) < .001
    for key in learned:
        for a, b in zip(head.stats[key], learned[key]):
            np.testing.assert_array_equal(a, b)


@pytest.mark.parametrize('a,b,expected', [
    (False, False, ('plain',)), (True, False, ('plain', 'a')),
    (False, True, ('plain', 'b')), (True, True, ('plain', 'a', 'b', 'both'))])
def test_layer_ablations_remove_actions(a, b, expected):
    mind = entity(memory_layer_a=a, memory_layer_b=b)
    assert mind.field.memory_choice.options(a, b) == expected
    for seed in range(4):
        assert mind.field.memory_choice.pick('kind', 'consult', feature(), expected,
                                             np.random.default_rng(seed))[0] in expected
    assert not CR.REGISTRY['memory_choice']['default_on']
    assert CR.REGISTRY['memory_choice']['status'] == 'learned'


@pytest.mark.parametrize('remember', ['plain', 'a', 'b', 'both'])
def test_current_public_records_wait_until_post_item_remember(monkeypatch, remember):
    mind, shown = entity(), TaskView.from_task(world())
    cheap_owner(monkeypatch, mind)
    force_options(monkeypatch, consult='plain', remember=remember)
    with mind.scope(), torch.no_grad():
        before_a, before_b = mind.state['events'].clone(), mind.field.ideas.read_n
        mind.memory.start_choice(shown, wall=10., phase='world')
        mind.field.ideas.read(('actually', 'heard'))
        mind.field.ideas.bind('heard', ('concept', 0), .5)
        mind.field.understand(*public_context(shown), ('law', 'p'), (('sym', 'add'),), True, 1., 'public')
        assert torch.equal(mind.state['events'], before_a)
        assert mind.field.ideas.read_n == before_b
        assert ('hypothesis', ('law', 'p')) not in mind.field.ideas._row
        mind.memory.consult(shown)
        report = mind.memory.finish_choice(shown, right=True)
        a, b = PH.MemoryChoice.LAYERS[remember]
        assert bool((mind.state['events'] > before_a).all()) == a
        assert (mind.field.ideas.read_n > before_b) == b
        assert (('hypothesis', ('law', 'p')) in mind.field.ideas._row) == b
        if b:
            assert counts(mind.field.ideas, ('hypothesis', ('law', 'p'))) == (1, 0)
        assert report['remember']['option'] == remember
        assert report['consult'][0]['moment'] == 'start'
        assert report['consult'][1]['moment'] == 'ways'
        assert report['remember']['seconds'] >= 0.


@pytest.mark.parametrize('batch', [False, True])
@pytest.mark.parametrize('sequence', [('both', 'plain', 'both'), ('plain', 'both', 'plain')])
def test_no_read_cache_crosses_chosen_layers(monkeypatch, batch, sequence):
    mind, shown = entity(), TaskView.from_task(world())
    calls = cheap_owner(monkeypatch, mind)
    with mind.scope(), torch.no_grad():
        # Pre-existing memory, before the item. No new write during the test.
        mind.memory.begin(shown)
        mind.memory.choosing = True
        reads = []
        for option in sequence:
            mind.memory.selected = PH.MemoryChoice.LAYERS[option]
            read = (mind.memory.features_many([shown, shown])[0] if batch else mind.memory.features(shown))
            reads.append(read[0])
        assert len(calls) == 2
        assert not torch.equal(reads[0], reads[1])
        assert torch.equal(reads[0], reads[2])
        assert (shown, True, False, False) in mind.memory._feature_cache
        assert (shown, True, True, True) in mind.memory._feature_cache


def test_delayed_remember_credit_requires_later_successful_touch_and_is_bounded():
    head, f = PH.MemoryChoice(), feature()
    head.learn('kind', 'remember', 'b', f, -1.)
    head.retain('kind', 'b', f, ('heard',))
    initial = float(head.posterior('kind', 'remember', 'b')[0] @ f)
    assert head.later_return(set(), True, .1) == []
    assert head.later_return({1}, False, .1) == []
    assert float(head.posterior('kind', 'remember', 'b')[0] @ f) == initial
    assert head.later_return({1}, True, .1) == [1]
    assert head.pick('kind', 'remember', f, ('plain', 'b'), MeanDraw())[0] == 'b'
    for _ in range(40):
        head.learn('kind', 'remember', 'b', f, -3.)
    assert head.pick('kind', 'remember', f, ('plain', 'b'), MeanDraw())[0] == 'plain'
    for _ in range(300):
        head.retain('kind', 'a', f, ())
    assert len(head.eligible) == 256 and head.eligible[-1]['id'] == head.serial


@pytest.mark.parametrize('layer', ['a', 'b'])
def test_consult_touches_only_earlier_remembered_items(monkeypatch, layer):
    mind, shown = entity(), TaskView.from_task(world())
    cheap_owner(monkeypatch, mind)
    force_options(monkeypatch, consult=layer, remember=layer)
    with mind.scope(), torch.no_grad():
        mind.memory.start_choice(shown, wall=10., phase='world')
        first = mind.memory.finish_choice(shown, right=True)
        assert first['touched'] == [] and first['credited'] == []
        mind.memory.start_choice(shown, wall=10., phase='world')
        mind.memory.features(shown)
        mind.memory.features(shown)
        second = mind.memory.finish_choice(shown, right=True)
        assert second['touched'] == [1] and second['credited'] == [1]
        assert 2 not in second['credited']


def stub_item(self, task, **kwargs):
    self._u_bind(task)
    self.memory.event('public-event', 'heard')
    self.memory.refresh(TaskView.from_task(task))
    return dict(proven=False, answer=None, verdict='not proven')


def test_off_reproduces_fixed_u2_logical_records_and_memory(monkeypatch):
    monkeypatch.setattr(Engine, 'live', stub_item)
    implicit = SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=arm_settings('full'))
    explicit = entity(memory_choice=False)
    for mind in (implicit, explicit):
        cheap_owner(monkeypatch, mind)
    records = [m.live(world(), task_wall=math.inf) for m in (implicit, explicit)]
    for record in records:
        assert 'memory_choice' not in record
        record['sera_u'].pop('wall')
        record['sera_u']['crutches'].pop('memory_choice', None)
    assert records[0] == records[1]
    assert torch.equal(implicit.state['events'], explicit.state['events'])
    np.testing.assert_array_equal(implicit.field.ideas._M[:implicit.field.ideas._n],
                                  explicit.field.ideas._M[:explicit.field.ideas._n])
    assert implicit.field.ideas.read_n == explicit.field.ideas.read_n


def test_checkpoint_exact_next_choice_and_hash_excludes_transient_clocks():
    mind = entity()
    head, f = mind.field.memory_choice, feature(1., .5)
    head.learn('kind', 'consult', 'both', f, 2.)
    head.demonstrate('kind', 'remember', f, ('plain', 'b'), 'b')
    head.retain('kind', 'b', f, ('public',))
    before = mind.learning_hash()
    mind.memory.item_started, mind.memory.read_seconds = 12345., 999.
    assert mind.learning_hash() == before
    resumed = SeraU.loads(mind.dumps())
    assert resumed.learning_hash() == before
    for decision in ('consult', 'remember'):
        a = head.pick('kind', decision, f, tuple(head.LAYERS), mind.numpy)
        b = resumed.field.memory_choice.pick('kind', decision, f, tuple(head.LAYERS), resumed.numpy)
        assert a == b
    assert mind.learning_hash() == resumed.learning_hash()
    head.learn('kind', 'consult', 'plain', f, -1.)
    assert mind.learning_hash() != resumed.learning_hash()


def test_live_checkpoint_resume_keeps_next_item_choices_and_learning(monkeypatch):
    from sera_u.proposer import FieldOwner
    monkeypatch.setattr(Engine, 'live', stub_item)
    monkeypatch.setattr('time.perf_counter', lambda: 1.)
    def observe(self, state, source, **kwargs):
        return {**state, 'fast': .75*state['fast']+.25*source,
                'events': state['events']+1}, {'energy_defect': source.new_zeros(len(source))}
    def read(self, view, **kwargs):
        return torch.zeros(3, 64), torch.ones(3)/3, self.empty(1)
    monkeypatch.setattr(FieldOwner, 'observe', observe)
    monkeypatch.setattr(FieldOwner, 'task_features', read)
    monkeypatch.setattr(FieldOwner, 'remembered', lambda self, state: state['fast'])
    mind = entity()
    mind.live(world(), task_wall=math.inf)
    resumed = SeraU.loads(mind.dumps())
    a = mind.live(world(), task_wall=math.inf)
    b = resumed.live(world(), task_wall=math.inf)
    assert a['memory_choice'] == b['memory_choice']
    assert mind.learning_hash() == resumed.learning_hash()


@pytest.mark.parametrize('late', [False, True])
def test_time_to_right_is_outer_acceptance_and_late_acceptance_earns_no_solution(monkeypatch, late):
    mind, task = entity(), world()
    cheap_owner(monkeypatch, mind)
    force_options(monkeypatch, consult='plain', remember='plain')
    monkeypatch.setattr(ONE.Sera, '_prove', lambda *args, **kwargs: True)
    monkeypatch.setattr('time.perf_counter', lambda: 6.)
    with mind.scope(), torch.no_grad():
        mind.memory.start_choice(TaskView.from_task(task), wall=10., phase='world', started=1.)
        LG.DEADLINE[0] = 0. if late else math.inf
        st = {'proven': {'law': LG.node('one')}}
        result = mind.engine._prove(task, LG.node('one'), {}, (), st)
        assert result is (not late)
        assert mind.memory.time_to_right == (None if late else 5.)
        if late:
            assert st['proven'] is None


@pytest.mark.parametrize('phase', ['test2', 'test3'])
def test_exam_has_no_demonstrations_corrections_or_new_observer_state(monkeypatch, phase):
    mind = entity()
    cheap_owner(monkeypatch, mind)
    force_options(monkeypatch, consult='plain', remember='plain')
    with pytest.raises(ValueError, match='forbidden'):
        mind.teach_memory_choice(world(), 'plain', phase=phase)
    seen = []
    def exam(self, task, *, teaching, **kwargs):
        assert isinstance(task, AssessmentTask) and not teaching
        assert task.actions() == [] and not task.teacher_truth('word')
        original = copy.deepcopy(task.data)
        assert task.verify(LG.node('one'), self._concepts(), 1., np.random.default_rng(3))[2] is None
        assert task.data == original
        self._u_bind(task)
        seen.append(task)
        return dict(proven=False, answer=None, verdict='not proven')
    monkeypatch.setattr(Engine, 'live', exam)
    taught = pickle.dumps(mind.field.memory_choice.taught)
    rec = mind.live(world(), phase=phase, teaching=True, task_wall=math.inf)
    assert seen and pickle.dumps(mind.field.memory_choice.taught) == taught
    assert rec['memory_choice']['remember']['option'] == 'plain'


def test_assessment_preparation_never_pre_writes_choosing_clone(monkeypatch):
    mind, shown = entity(), TaskView.from_task(world())
    cheap_owner(monkeypatch, mind)
    before = mind.learning_hash()
    assert SeraU._prepare_assessments([mind], [shown]) == 0.
    assert mind.learning_hash() == before and mind.memory._prepared is None


def test_assess_discards_all_memory_choice_learning_and_eligibility(monkeypatch):
    mind = entity()
    force_options(monkeypatch, consult='plain', remember='plain')
    monkeypatch.setattr(Engine, 'live', stub_item)
    # Class patch reaches the assessment clone without serializing closures.
    from sera_u.proposer import FieldOwner
    def read(self, view, **kwargs):
        return torch.zeros(3, 64), torch.ones(3)/3, self.empty(1)
    monkeypatch.setattr(FieldOwner, 'task_features', read)
    before = mind.learning_hash()
    result = mind.assess(world(), task_wall=math.inf)
    assert result['record']['memory_choice']['taken']['consult']['plain'] == 2
    assert not mind.field.memory_choice.stats and mind.learning_hash() == before
    assert result['before'] == result['after'] == before


def test_course_phase_schedule_scales_only_teacher_and_counts_each_option(monkeypatch):
    mind = entity()
    cheap_owner(monkeypatch, mind)
    head, f = mind.field.memory_choice, feature()
    with UC.evidence_weight(.25):
        head.demonstrate('kind', 'consult', f, ('plain', 'b'), 'b')
    np.testing.assert_array_equal(head.taught[('kind', 'consult', 'b')][0], .25*np.outer(f, f))
    head.learn('kind', 'consult', 'b', f, 2.)
    before = copy.deepcopy(head.stats)
    UC.fade(mind.field, 1., .6)
    np.testing.assert_array_equal(head.taught[('kind', 'consult', 'b')][0], .15*np.outer(f, f))
    UC.fade(mind.field, .6, 0.)
    assert all(not a.any() for a in UC.teacher_arrays(mind.field))
    for key in before:
        for a, b in zip(before[key], head.stats[key]):
            np.testing.assert_array_equal(a, b)
    backend = object.__new__(UC.UBackend)
    backend.mind = mind
    state = {}
    with UC.Meter(state).measure(backend):
        head.pick('kind', 'consult', f, ('plain',), MeanDraw())
        head.pick('kind', 'remember', f, ('plain',), MeanDraw())
    assert state['memory_choices'] == {'consult': {'plain': 1}, 'remember': {'plain': 1}}
    assert state['meter']['memory_choice']['calls'] == 2
    assert not UC.u_switches()['memory_choice']
    CR.ON.add('memory_choice')
    assert UC.u_switches()['memory_choice']
    assert not UC.u_switches(('memory_choice',))['memory_choice']


def test_course_demonstrates_resemblance_using_public_cues_only(monkeypatch):
    mind = entity()
    cheap_owner(monkeypatch, mind)
    backend = object.__new__(UC.UBackend)
    backend.mind = mind
    shown = []
    original = PH.MemoryChoice.demonstrate
    def demonstrate(self, kind, decision, f, available, option):
        shown.append(option)
        return original(self, kind, decision, f, available, option)
    monkeypatch.setattr(PH.MemoryChoice, 'demonstrate', demonstrate)
    backend.demonstrate(world())
    kind, cue = public_context(TaskView.from_task(world()))
    mind.field.memory_choice.retain(kind, 'both', feature(), ('public',), cue)
    backend.demonstrate(world())
    assert shown == ['plain', 'both']
    assert not mind.field.memory_choice.stats


@pytest.mark.parametrize('consult', ['plain', 'b'])
def test_imagination_copy_respects_chosen_layers_without_factual_writes(monkeypatch, consult):
    # A partial U3 mask is refused (SeraU's mask normalization): declare U3, U6 and U7, with only methods on.
    mind, task = entity(**{k: k == 'field_methods' for k in U3_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES}), world()
    cheap_owner(monkeypatch, mind)
    force_options(monkeypatch, consult=consult, remember='plain')
    def imagine(self, *args, **kwargs):
        gate = self.field._bridge
        assert not gate.a and gate.b == (consult == 'b')
        before = self.field.ideas.read_n
        self.field.ideas.read(('hypothetical', 'only'))
        assert (self.field.ideas.read_n > before) == (consult == 'b')
        if consult == 'plain':
            assert self.field.familiarity(*public_context(TaskView.from_task(task))) == ({}, {})
        return {}
    monkeypatch.setattr(ONE.Sera, '_imagine', imagine)
    with mind.scope(), torch.no_grad():
        mind.memory.start_choice(TaskView.from_task(task), wall=10., phase='world')
        before_b = mind.field.ideas.read_n
        pending = len(mind.memory.pending)
        original_field = mind.field
        mind.engine._imagine(('dream',), task, ONE.kind_of(task), None,
                             mind.engine._concepts(), (), None, {}, [], {}, lambda *a, **k: None)
        assert mind.engine.field is original_field and mind.field.ideas.read_n == before_b
        assert len(mind.memory.pending) == pending


@pytest.mark.parametrize('pays', [False, True])
def test_measured_item_returns_raise_useful_memory_and_lower_cost_only_memory(monkeypatch, pays):
    mind, shown = entity(memory_layer_a=False), TaskView.from_task(world())
    cheap_owner(monkeypatch, mind)
    clock = SimpleNamespace(value=0.)
    monkeypatch.setattr('time.perf_counter', lambda: clock.value)
    original_read = mind.owner.task_features
    def timed_read(*args, **kwargs):
        if kwargs.get('ring') is not None:
            clock.value += .01 if pays else 4.
        return original_read(*args, **kwargs)
    monkeypatch.setattr(mind.owner, 'task_features', timed_read)
    original_pick = PH.MemoryChoice.pick
    force_options(monkeypatch, consult='b', remember='plain')
    with mind.scope(), torch.no_grad():
        mind.memory.start_choice(shown, wall=10., phase='world')
        mind.memory.features(shown)
        record = mind.memory.finish_choice(shown, right=pays)
    kind = public_context(shown)[0]
    next_option = original_pick(mind.field.memory_choice, kind, 'consult', feature(),
                               ('plain', 'b'), MeanDraw())[0]
    assert next_option == ('b' if pays else 'plain')
    assert record['consult'][0]['read_seconds'] == (.01 if pays else 4.)
