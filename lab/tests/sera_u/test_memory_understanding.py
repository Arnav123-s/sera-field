"""U2's short CPU contracts. No hidden labels are supplied to memory."""
import copy
import math
import pickle
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.memory import MemoryField, add_count, counts, context_pattern, pair, public_context, roles
from sera_u.mind import Engine, U1_CRUTCHES, U2_CRUTCHES, arm_settings
from sera_u.ports import TaskView
from sera_u.sleep import Receipt


@pytest.fixture(autouse=True)
def deterministic(monkeypatch):
    torch.set_num_threads(1)
    torch.manual_seed(3)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


def view():
    return TaskView((('x', 'num'),), 'num', tuple((((('x', x),)), x+1) for x in (-2, 0, 1, 4)),
                    queries=((('x', 6),),), words=('heard',))


def program():
    return LG.node('add', LG.node('var', payload='x'), LG.node('one'))


def mind(**switches):
    knobs = arm_settings('full')
    knobs.update(switches)
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=knobs)


def state_equal(a, b):
    return a.keys() == b.keys() and all(torch.equal(a[k], b[k]) for k in a)


def bstate(entity):
    ideas = entity.field.ideas
    return tuple(ideas._row.items()), ideas._M[:ideas._n].copy(), copy.deepcopy(ideas.of), ideas.read_n


def assert_b_equal(a, b):
    assert a[0] == b[0] and a[2:] == b[2:]
    np.testing.assert_array_equal(a[1], b[1])


@pytest.mark.parametrize('a,b', [(True, True), (True, False), (False, True), (False, False)])
def test_each_write_ablation_uses_only_its_layer(a, b):
    entity = mind(memory_layer_a=a, memory_layer_b=b)
    old_a = copy.deepcopy(entity.state)
    old_b = bstate(entity)
    with entity.scope():
        entity.memory.begin(view())
        entity.field.understand('ignored', [999.], program(), LG.parts(program()), True, 1., 'ignored')
    assert state_equal(old_a, entity.state) == (not a)
    if b:
        assert bstate(entity)[0] != old_b[0]
        assert entity.field.standing_counts(program()) == (1, 0)
    else:
        assert_b_equal(old_b, bstate(entity))
        assert entity.field.standing_counts(program()) == (0, 0)


def test_ablation_read_paths_and_reciprocal_cue(monkeypatch):
    entity = mind()
    with entity.scope():
        entity.memory.begin(view())
        initial_state = copy.deepcopy(entity.state)
        initial_b = bstate(entity)
        both = entity.memory.features(view())[0]
        entity.crutches['memory_layer_a'] = False
        no_a = entity.memory.features(view())[0]
        # Erasing A while A is off cannot affect recall.
        entity.state = entity.owner.empty(1)
        assert torch.equal(no_a, entity.memory.features(view())[0])
        entity.state = initial_state
        entity.crutches['memory_layer_a'] = True
        reciprocal = entity.memory.ring(view())
        entity.state = entity.owner.empty(1)
        assert not torch.equal(reciprocal, entity.memory.ring(view()))
        entity.state = initial_state
        entity.crutches['memory_layer_b'] = False
        assert entity.memory.ring(view()) is None
        no_b = entity.memory.features(view())[0]
        entity.field.ideas._M[:entity.field.ideas._n] *= 37.
        assert torch.equal(no_b, entity.memory.features(view())[0])
        entity.crutches['memory_layer_a'] = False
        neither = entity.memory.features(view())[0]
        direct = entity.owner.task_features(view(), state=entity.owner.empty(1))[0]
        assert torch.equal(neither, direct)
        assert not torch.equal(both, no_a) and not torch.equal(both, no_b)
        # All reads above leave A unchanged; B was changed only by our hostile mutation.
        assert state_equal(initial_state, entity.state)
        assert initial_b[0] == tuple(entity.field.ideas._row.items())


def test_b_off_also_closes_original_sentence_and_first_thought_readers():
    entity = mind()
    with entity.scope():
        ideas = entity.field.ideas
        ideas.read(('unique-name', 'went', 'home'))
        ideas.bind('unique-name', ('concept', 7), 1.)
        assert ideas.bound('unique-name', ('concept', 7)) > .9
        before = bstate(entity)
        entity.crutches['memory_layer_b'] = False
        assert ideas.evoked(('unique-name',), [('concept', 7)]) == []
        assert ideas.comes_to_mind(('unique-name',)) == []
        assert ideas.bound('unique-name', ('concept', 7)) == 0.
        ideas.read(('new', 'words'))
        ideas.bind('unique-name', ('concept', 7), 1.)
        ideas.role('home', 'where')
        ideas.perceive_world((('rail-cue', 1),))
        assert ideas.consolidate(1., lambda *args: True) == 0
        assert_b_equal(before, bstate(entity))


def test_learned_projection_and_gate_are_the_only_b_to_boundary_port():
    entity = mind()
    with entity.scope():
        entity.memory.begin(view())
        entity.optimizer.zero_grad(set_to_none=True)
        entity.memory.checked_loss(view(), LG.parts(program())).backward()
        assert entity.owner.memory_projection.weight.grad.abs().sum() > 0
        assert entity.owner.memory_gate.grad.abs() > 0
        with torch.no_grad():
            entity.owner.memory_projection.weight.zero_()
            coupled = entity.memory.features(view())[0]
            native = entity.owner.task_features(view(), state=entity.state)[0]
            assert torch.equal(coupled, native)


def test_imagined_events_hypothetical_reads_and_dreams_do_not_write_facts():
    entity = mind()
    with entity.scope():
        entity.memory.begin(view())
        before_a, before_b = copy.deepcopy(entity.state), bstate(entity)
        entity.memory.event('checked-proof', program(), progress=1., imagined=True)
        entity.memory.features(replace(view(), examples=()))
        with torch.no_grad():
            entity.owner.conditional(entity.state, entity.owner.encode_texts(['imagined']))
        assert state_equal(before_a, entity.state)
        assert_b_equal(before_b, bstate(entity))
    receipt = Receipt.make(view(), (program(),), {}, scope='exact-audit', origin='alone', source='fixture')
    entity.checked_wake.add(receipt.id)
    entity.sleep.admit(receipt, {})
    before_a, before_b = copy.deepcopy(entity.state), bstate(entity)
    entity.sleep.dream(1, attempts=4)
    assert state_equal(before_a, entity.state)
    assert_b_equal(before_b, bstate(entity))


def test_hostile_hidden_metadata_and_context_never_reach_either_memory():
    task = TS.number_task('first', lambda x: x+1, 3, 0)
    first = TaskView.from_task(task)
    task.name, task.subject = 'private answer', 'code'
    task._target = lambda x: 997
    task._truth_words = {'private-answer'}
    task.grade = lambda *a, **k: {'verdict': 'SURE AND WRONG', 'secret': 997}
    task.context = lambda: [997.]*7
    assert first == TaskView.from_task(task)
    a, b = mind(), mind()
    for entity, shown in ((a, first), (b, TaskView.from_task(task))):
        with entity.scope():
            entity.memory.begin(shown)
            entity.field.understand('hidden-kind', task.context(), program(), LG.parts(program()), True, 1., task.name)
    assert state_equal(a.state, b.state)
    assert_b_equal(bstate(a), bstate(b))
    assert public_context(first)[1][0] == 0.             # Exact's subject feature is excluded


def test_untaught_talk_grades_stay_out_and_teacher_verdict_is_observed():
    x = (('where', 'name'), ('name', 'went', 'home'))
    def talk(target, kind):
        return SimpleNamespace(name='talk', items=[(x, target, kind)],
                               sentences=lambda value: value[1:], perceive=lambda value: value)
    entities = [mind(), mind()]
    for entity, target in zip(entities, (('private-a',), ('private-b',))):
        entity.converse(talk(target, target[0]), teaching=False)
    assert state_equal(entities[0].state, entities[1].state)
    assert_b_equal(bstate(entities[0]), bstate(entities[1]))
    events = int(entities[0].state['events'][0])
    entities[0].converse(talk(('actually-taught',), 'observer-kind'), teaching=True)
    assert int(entities[0].state['events'][0]) > events+1
    assert 'role:teacher-verdict' in entities[0].field.ideas._row


def test_refresh_writes_new_public_examples_once_including_after_four():
    entity = mind()
    with entity.scope():
        shown = view()
        entity.memory.begin(shown)
        before = int(entity.state['events'][0])
        extended = replace(shown, examples=shown.examples+((((('x', 8),)), 9),))
        entity.memory.refresh(extended)
        assert int(entity.state['events'][0]) == before+1
        entity.memory.refresh(extended)
        assert int(entity.state['events'][0]) == before+1
        # The context is the public context frozen at entry, as in S18.
        assert entity.memory.context == public_context(shown)


def test_rail_context_keeps_s18_continuous_senses_without_hidden_world_access():
    from ccops5.core import paths
    time = np.arange(paths.N_OBS)*paths.DT_OBS
    command = SimpleNamespace(arrays=lambda: (np.array([0.]), np.array([.4]), np.array([1.])))
    throws = [SimpleNamespace(situation=obj, action=command,
                              x=np.linspace(-1., 1., paths.N_OBS)+rep*.2,
                              v=np.sin(time)+obj*.3+rep*.2)
              for obj in range(2) for rep in range(2)]
    task = SimpleNamespace(form='strengths', inputs={'s': 'num'}, out='num', words=(),
                           throws=throws, world=SimpleNamespace(n_situations=2))
    shown = TaskView.from_task(task)
    np.testing.assert_allclose(public_context(shown)[1], TS.Rail.context(task), rtol=1e-12, atol=1e-12)
    task.world = object()                              # no spec, masses, teacher or hidden law
    task.grade = lambda *args: 'hidden-grade'
    task.context = lambda: [997.]*7
    assert shown == TaskView.from_task(task)
    assert len(shown.records(max_records=None)) > 128   # streamed, never silently truncated


def test_untaught_live_observer_grade_mutation_cannot_change_memory(monkeypatch):
    # Freeze the independent audit; only the observer grade is changed.
    monkeypatch.setattr(ONE, 'MAX_WALL', math.inf)
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 0.)
    tasks = [TS.Exact('math', 'same', lambda x: x, {'x': 'num'}, 'num', [-2, 0, 1, 4],
                      [], lambda rng: int(rng.integers(-8, 9))) for _ in range(2)]
    tasks[1].grade = lambda *args, **kwargs: {'verdict': 'SURE AND WRONG', 'secret': 'hidden'}
    entities = [mind(field_proposer=False), mind(field_proposer=False)]
    for entity, task in zip(entities, tasks):
        entity.live(task, teaching=False, task_wall=math.inf, max_steps=3)
    assert state_equal(entities[0].state, entities[1].state)
    assert_b_equal(bstate(entities[0]), bstate(entities[1]))


def test_s18_part_multisets_pairs_contexts_and_cumulative_state():
    field = MemoryField.adopt(PH.Field(3), True)
    p, q = ('sym', 'add'), ('sym', 'one')
    field.understand('exact', [.5, -.25], 'h', (p, p, q), True, 1., 'never-retained')
    parts, pairs = field.familiarity('exact', [.5, -.25], (p, q), (pair(p, p), pair(p, q)))
    assert parts[p] == pytest.approx(2., abs=1e-6) and parts[q] == pytest.approx(1., abs=1e-6)
    assert pairs[tuple(sorted((repr(p), repr(q))))] == pytest.approx(2., abs=1e-6)
    assert pairs[(repr(p), repr(p))] == pytest.approx(1., abs=1e-6)
    assert field.familiarity('other-kind', [.5, -.25], (p,), ())[0][p] == 0.
    assert field.familiarity('exact', [.5], (p,), ())[0][p] == 0.
    assert not hasattr(field, 'understood') and not hasattr(field, 'standing')
    assert not any(k[0] in ('u-part', 'u-pair', 'hypothesis') for k in field.ideas.of)
    n, rev = field.ideas._n, field.ideas.rev
    assert field.familiarity('exact', [.5, -.25], (('sym', 'unseen'),), ())[0][('sym', 'unseen')] == 0.
    assert (n, rev) == (field.ideas._n, field.ideas.rev)
    # No FIFO store: >1024 repeated events still use the same structural rows.
    for _ in range(1025):
        field.understand('empty', (), 'tentative', (p,), False, .3, 'discarded')
    assert field.familiarity('empty', (), (p,), ())[0][p] == pytest.approx(307.5, abs=.01)
    assert not any('discarded' in repr(k) or 'never-retained' in repr(k) for k in field.ideas._row)


def test_separately_seen_parts_do_not_invent_pair_and_context_totals_decode():
    field = MemoryField.adopt(PH.Field(3), True)
    p, q = ('sym', 'add'), ('sym', 'one')
    field.understand('x', [], 'p', (p,), True, 1., 'ignored')
    field.understand('x', [], 'q', (q,), False, .3, 'ignored')
    parts, pairs = field.familiarity('x', [], (p, q), (pair(p, q),))
    assert parts[p] == pytest.approx(1.) and parts[q] == pytest.approx(.3)
    assert pairs[tuple(sorted((repr(p), repr(q))))] == 0.
    assert field.context_density('x', []) == pytest.approx(1.)
    assert field.context_density('x', [], 'credited') == pytest.approx(1.)
    assert field.context_density('unseen', [], 'credited') == 0.
    totals = field.account()['understanding_events']
    assert list(totals.values()) == [dict(all=2, credited=1)]


def test_zeroing_hrr_erases_u_l_but_preserves_explicit_concept_authority(monkeypatch):
    field = MemoryField.adopt(PH.Field(3), True)
    body = LG.node('add', LG.node('var', payload='_'), LG.node('one'))
    concept = field.invent(body, ('num', 'num'), 'math', 'checked', LG.parts(body))
    field.understand('x', [], 'h', LG.parts(body), True, 1., 'ignored')
    field.ideas._M[:field.ideas._n] = 0.
    monkeypatch.setattr(field, '_near', lambda *args: pytest.fail('retired record read'))
    u, l, _, _, _ = field.layers('x', [], {'h': LG.parts(body), 'r': ()}, {'h': 0., 'r': 0.}, {'h': 1., 'r': 1.})
    assert u == l and l['h'] == l['r']
    assert field.standing_counts('h') == (0, 0)
    assert concept['id'] in field.proven_ideas()


def test_s18_exact_standing_and_description_length():
    field = MemoryField.adopt(PH.Field(3), True)
    add_count(field.ideas, ('hypothesis', 'h'), 2, 1)
    add_count(field.ideas, ('hypothesis', 'r'), 1, 0)
    assert field.standing_counts('h') == (2, 1)
    assert field.standing_counts('r') == (1, 0)
    # Check S18's inverse Gram formula against the exact two-group decoder.
    _, a, b = roles(field.ideas)
    m = field.ideas._M[field.ideas._row[('hypothesis', 'h')]].astype(np.float64)
    rho = float(a @ b)/PH.IDEA_DIM
    pa, pb = float(a @ m)/PH.IDEA_DIM, float(b @ m)/PH.IDEA_DIM
    assert (pa-rho*pb)/(1-rho*rho) == pytest.approx(2.)
    assert (pb-rho*pa)/(1-rho*rho) == pytest.approx(1.)
    u, l, evidence, phi, _ = field.layers('x', (), {'h': (), 'r': ()}, {'h': 0., 'r': 0.}, {'h': 3., 'r': 3.})
    assert math.exp(l['h']-l['r']) == pytest.approx(.75)
    assert u == l
    assert phi == PH.pool(u, l, evidence)
    # Hypothesis aliases do not share standing, and familiarity is no certificate.
    assert field.standing_counts(('concept', 1)) == (0, 0)
    assert field.proven_ideas() == set()


def test_standing_schema_capacity_and_reserved_rows_are_enforced():
    field = MemoryField.adopt(PH.Field(3), True)
    add_count(field.ideas, ('hypothesis', 'full'), 2**24, 0)
    with pytest.raises(ValueError, match='capacity'):
        field.refute('full')
    with pytest.raises(ValueError, match='Reserved'):
        field.ideas.bind(('hypothesis', 'h'), ('concept', 1), 100.)
    with pytest.raises(ValueError, match='Reserved'):
        field.ideas.read((('hypothesis', 'h'),))
    add_count(field.ideas, ('hypothesis', 'bad'), 1, 0)
    field.ideas._M[field.ideas._row[('hypothesis', 'bad')], 0] += .25
    with pytest.raises(ValueError, match='Malformed'):
        field.standing_counts('bad')
    before = field.ideas._M[:field.ideas._n].copy()
    with pytest.raises(ValueError):
        field.understand('x', [], 'h', (), True, float('nan'), 'ignored')
    np.testing.assert_array_equal(before, field.ideas._M[:field.ideas._n])


def test_invalid_context_still_allows_exact_standing_and_zero_u():
    field = MemoryField.adopt(PH.Field(3), True)
    field.understand('x', [float('nan')], 'h', (('sym', 'one'),), True, 1., 'ignored')
    assert field.standing_counts('h') == (1, 0)
    assert field.familiarity('x', [float('nan')]) == ({}, {})
    assert np.isfinite(field.ideas._M[:field.ideas._n]).all()


def test_migration_is_independent_idempotent_and_survives_word_reading_aliases():
    field = PH.Field(3)
    field.understand('x', [], 'h', (('sym', 'one'),), True, 1., 'old')
    field.refute('h')
    field = MemoryField.adopt(field, True)
    assert field.standing_counts('h') == (1, 1)
    before = field.ideas._M[:field.ideas._n].copy()
    restored = MemoryField.adopt(pickle.loads(pickle.dumps(field)), True)
    np.testing.assert_array_equal(before, restored.ideas._M[:restored.ideas._n])
    restored.ideas.read(('ordinary', 'words'))
    restored.ideas.bind('cue', ('idea', 1), 1.)
    restored.ideas.bind('cue', ('idea', 2), 1.)
    restored.ideas.redirect({('idea', 1): ('concept', 9), ('idea', 2): ('concept', 9)})
    assert restored.standing_counts('h') == (1, 1)
    np.testing.assert_array_equal(before, restored.ideas._M[:len(before)])
    qid = restored.ask('ignored', 'check', 'question', key='h')
    assert restored.answer(qid, 'right') and not restored.answer(qid, 'right')
    assert restored.standing_counts('h') == (2, 1)


def test_bad_migration_preserves_source_and_on_to_off_conversion_is_refused():
    source = PH.Field(3)
    source.standing['bad'] = [1.5, 0]
    with pytest.raises(ValueError, match='integer'):
        MemoryField.adopt(source, True)
    assert type(source) is PH.Field and source.standing == {'bad': [1.5, 0]}
    on = MemoryField.adopt(PH.Field(3), True)
    with pytest.raises(ValueError, match='fresh'):
        SeraU(3, field=on, crutches={**arm_settings('full'), 'field_understanding': False})


def test_every_new_switch_off_ignores_stale_native_state_in_proposer():
    entity = mind(**{k: False for k in U2_CRUTCHES})
    with entity.scope(), torch.no_grad():
        expected = entity.owner.task_features(view())[0]
        altered, _ = entity.owner.observe(entity.state, entity.owner.encode_texts(['stale past']))
        entity.state = altered
        entity.proposer.retained = altered
        got, _ = entity.proposer.features(view(), {})
        assert torch.equal(expected, got)


@pytest.mark.parametrize('form', ['exact', 'strengths'])
def test_u_starts_at_b_and_checked_learning_moves_neural_mix(form, monkeypatch):
    entity = mind()
    shown = replace(view(), form=form)
    with entity.scope():
        entity.memory.begin(shown)
        entity.field.understand('x', [], program(), LG.parts(program()), True, 1., 'ignored')
        assert entity.memory.mix() == 0.
        hyps = {'h': (('sym', 'add'),), 'other': (('sym', 'mul'),)}
        on = entity.field.layers('ignored', [999.], hyps, {h: 0. for h in hyps}, {h: 1. for h in hyps})
        entity.crutches['memory_layer_a'] = False
        b = entity.field.layers('ignored', [], hyps, {h: 0. for h in hyps}, {h: 1. for h in hyps})
        assert on == b
        entity.crutches['memory_layer_a'] = True
        original = entity.field.familiarity
        def checked_familiarity(kind, context, parts=None, pairs=None, **kwargs):
            assert kwargs['version'] == ('context-v1' if form == 'strengths' else 'u2-public-v1')
            return original(kind, context, parts, pairs, **kwargs)
        monkeypatch.setattr(entity.field, 'familiarity', checked_familiarity)
        entity.optimizer.zero_grad(set_to_none=True)
        loss = entity.memory.checked_loss(shown, LG.parts(program()))
        loss.backward()
        assert entity.owner.understanding_mix.grad < 0
        assert entity.owner.understanding_query.weight.grad.abs().sum() > 0
        entity.optimizer.step()
        assert 0. < entity.memory.mix() < 1.
        after = entity.field.layers('ignored', [], hyps, {h: 0. for h in hyps}, {h: 1. for h in hyps})
        assert on[0] != after[0]


def test_phi_ranks_full_programs_and_partial_fragments():
    entity = mind()
    one, zero = LG.node('one'), LG.node('zero')
    shown = replace(view(), examples=())
    with entity.scope():
        entity.memory.begin(shown)
        entity.field.understand('x', [], one, (('sym', 'one'),), True, 1., 'ignored')
        assert entity.memory.rank(shown, [zero, one], {}) == [one, zero]
        hole = ('@hole', 'num', (('x', 'num'),))
        add = LG.node('add', hole, one)
        mul = LG.node('mul', hole, zero)
        # Equal exact prefix costs, with familiarity selecting the observed part.
        assert entity.memory.rank(shown, [mul, add], {}, partial=True)[0] == add


def test_resume_matches_next_memory_write_read_and_checked_optimizer_update(tmp_path):
    entity = mind()
    with entity.scope():
        entity.memory.begin(view())
        entity.field.understand('x', [], program(), LG.parts(program()), True, 1., 'ignored')
    path = tmp_path/'u2.pt'
    entity.save(path)
    restored = SeraU.load(path)
    assert entity.learning_hash() == restored.learning_hash()
    for value in (entity, restored):
        with value.scope():
            value.memory.begin(view())
            value.memory.event('teacher-verdict', ('wrong', program()), progress=-1.)
            value.optimizer.zero_grad(set_to_none=True)
            value.memory.checked_loss(view(), LG.parts(program())).backward()
            value.optimizer.step()
    assert state_equal(entity.state, restored.state)
    assert_b_equal(bstate(entity), bstate(restored))
    for key in entity.owner.state_dict():
        assert torch.equal(entity.owner.state_dict()[key], restored.owner.state_dict()[key]), key
    assert entity.learning_hash() == restored.learning_hash()


def test_all_new_switches_off_retains_u1_record_keys_and_base_engine(monkeypatch):
    # U1's no-proposer seam is exactly ONE.Sera. Reference it directly, with the
    # same scoped switches/RNG; compare all nonmeasurement fields recursively.
    entity = mind(field_proposer=False, **{k: False for k in U2_CRUTCHES})
    assert type(entity.field) is PH.Field and type(entity.field.ideas) is PH.Ideas
    task = TS.Exact('math', 'identity', lambda x: x, {'x': 'num'}, 'num', [-2, 0, 1, 4],
                    [], lambda rng: int(rng.integers(-8, 9)))
    monkeypatch.setattr(ONE, 'MAX_WALL', math.inf)
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 0.)
    with entity.scope():
        reference = ONE.Sera(3, copy.deepcopy(entity.field), library_enabled=True)
        expected = reference.live(copy.deepcopy(task), teaching=False, max_steps=3)
    got = entity.live(copy.deepcopy(task), task_wall=math.inf, max_steps=3)
    assert set(got['sera_u']['crutches']) == set(U1_CRUTCHES)
    assert entity.proposer.memory is None and not entity.owner.understanding_ids
    def logical(value):
        if isinstance(value, dict):
            return {k: logical(v) for k, v in value.items() if k not in (
                'sera_u', 'wall', 'cpu', 'timing', 'thinking_wall', 'thinking_cpu', 'finish_cpu',
                'peak_mb', 'peak_mb_by', 'gain_rate', 'phases')}         # phases: the ring observer's timed costs
        if isinstance(value, list):
            return [logical(v) for v in value]
        return value
    assert logical(got) == logical(expected)


def test_understanding_off_keeps_legacy_phi_counts():
    entity = mind(field_understanding=False)
    expected = PH.Field(3)
    for field in (entity.field, expected):
        field.understand('x', [0.], 'h', (('sym', 'one'),), True, 1., 'public')
        field.refute('r')
    hyps = {'h': (('sym', 'one'),), 'r': (('sym', 'zero'),)}
    args = ('x', [0.], hyps, {'h': 0., 'r': -1.}, {'h': 1., 'r': 1.})
    assert entity.field.layers(*args) == expected.layers(*args)
