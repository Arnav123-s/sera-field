"""U6 CPU contracts: public views, own outcomes, stubs for expensive Field reads."""
import copy
import json
import math
import random
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import Engine, U1_CRUTCHES, U2_CRUTCHES, U3_CRUTCHES, U6_CRUTCHES, arm_settings
from sera_u.ports import TaskView
from sera_u.sleep import Curiosity, GAP_CHECKS, Receipt, Sleep, Syndrome, gap_parts, independent, walk, aimed_compositions


@pytest.fixture(autouse=True)
def deterministic(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


def programs():
    x = LG.node('var', payload='x')
    return x, LG.node('mul', x, x), LG.node('add', x, LG.node('one'))


def view():
    return TaskView((('x', 'num'),), 'num', (((('x', 0),), 0),),
                    queries=tuple((('x', x),) for x in (0, 1, 2, 3)), words=('square',))


def signal(value=1.):
    return Syndrome('committee', value, (('production', 'mul'),), .01, ((('x', 2),),))


def gap(c=None):
    c = c or Curiosity()
    return c.decode(view(), (signal(),), np.zeros((3, 64)))


def logical(rows):
    return [(r.check, r.value, r.parts, r.inputs) for r in rows]


class PublicTask:
    form = 'exact'
    inputs = {'x': 'num'}
    out = 'num'
    words = []
    data = [(0, 0)]
    var = 'x'
    def probes(self):
        return [{'x': x} for x in (0, 1, 2, 3)]
    def __getattr__(self, name):
        if name in ('grade', '_target', 'held_out', 'observer', '_fresh', '_truth_words'):
            raise AssertionError('Private observer access: '+name)
        raise AttributeError(name)


def test_no_leak_private_state_does_not_enter_any_check():
    x, square, plus = programs()
    task = PublicTask()
    task.hidden_target = object()
    a = TaskView.from_task(task)
    before = logical(Curiosity().checks(a, (x, square, plus), {}))
    task.hidden_target = lambda _: 'changed hidden target'
    task.held_out = [999]
    task.observer_grades = {'right': False}
    b = TaskView.from_task(task)
    assert a == b
    assert logical(Curiosity().checks(b, (x, square, plus), {})) == before
    with pytest.raises(TypeError):
        Curiosity().checks(task, (x, square), {})


def test_two_fitting_programs_locate_exactly_unlabeled_disagreements_and_parts():
    x, square, plus = programs()
    rows = Curiosity().checks(view(), (x, square, plus), {})
    committee = rows[0]
    assert tuple(r.check for r in rows) == GAP_CHECKS
    assert committee.value == 1.
    assert committee.inputs == ((('x', 2),), (('x', 3),))
    assert committee.parts == gap_parts((x, square), view())
    assert ('production', 'add') not in committee.parts
    assert all(r.cost >= 0 for r in rows)


def test_all_other_checks_are_signed_and_located(monkeypatch):
    x, square, _ = programs()
    c = Curiosity()
    c.verdict('exact:num->num', .9, False)
    c.observe('role:pair', 2.)
    c.observe('role:pair', -2.)
    rows = c.checks(view(), (x, square), {}, memories=((('production', 'mul'), 0., 3.),),
                    roadmap=((square, (('x', 2),), 3, 4),),
                    log_u={x: math.log(.1), square: math.log(.9)},
                    log_b={x: math.log(.9), square: math.log(.1)},
                    surest=('production', 'add'), accepted=x)
    values = {r.check: r.value for r in rows}
    assert values['memories'] < 0
    assert values['roadmap'] == 1
    assert values['calibration'] == pytest.approx(.9)
    assert values['surprise'] < 0
    assert values['familiar_failure'] == pytest.approx(.8)
    assert values['proposer_search'] == 1
    concept = LG.node('c', x, payload=1)
    concepts = {1: (square, 'x'), '_sig': {1: ('num', 'num')}}
    assert c.checks(view(), (concept,), concepts)[-1].value == 0
    original = LG.safe
    monkeypatch.setattr(LG, 'safe', lambda p, env, table: -999 if p[0] == 'c' else original(p, env, table))
    bug = c.checks(view(), (concept,), concepts)[-1]
    assert bug.value == 1 and ('concept', 1) in bug.parts


def test_decoder_adapts_both_checks_and_contextual_paths():
    c = Curiosity()
    assert set(c.weights.values()) == {1.}
    g = gap(c)
    c.reinforce(g, 1.)
    assert c.weights['committee'] > 1.
    path = c.paths[('committee', ('production', 'mul'))].copy()
    c.reinforce(g, 0.)
    assert c.weights['committee'] < c.weight_paths['committee'][-2]
    assert c.paths[('committee', ('production', 'mul'))][0] < path[0]
    c.decode(view(), tuple(Syndrome(k, 0., (), 0.) for k in GAP_CHECKS), np.zeros((3, 64)))
    assert c.weights['memories'] < 1.
    assert c.gap is None
    assert all(len(v) > 1 for v in c.weight_paths.values())


def test_returns_use_new_solves_speed_and_checks_that_stop():
    c = Curiosity()
    g = gap(c)
    c.finish(view().identity, g, (signal(),), solved=False, search=4.)
    low = c.weights['committee']
    c.finish(view().identity, None, (signal(0.),), solved=True, search=2.)
    assert c.weights['committee'] > low
    assert c.report()['gaps_later_solved'] == 1
    c.finish(view().identity, None, (signal(0.),), solved=True, search=1.)
    assert c.returns[-1]['reward'] == pytest.approx(.5)
    c.finish(view().identity, g, (signal(),), solved=True, search=2.)
    assert c.returns[-1]['reward'] == 0


def dream_mind(*, syndromes=True, aimed=True):
    _, _, plus = programs()
    c = Curiosity()
    gap(c)
    field = SimpleNamespace(concepts=[], concept_table=lambda: {}, proven_ideas=lambda: set(), curiosity=c)
    mind = SimpleNamespace(field=field, random=random.Random(3), checked_wake=set(),
                           crutches=dict(program_dreams=True, sleep_library=False,
                                         gap_syndromes=syndromes, aimed_dreams=aimed))
    sleep = Sleep(mind)
    v = TaskView((('x', 'num'),), 'num', tuple(((('x', x),), x+1) for x in (-2, 0, 1, 4)))
    r = Receipt.make(v, (plus,), {}, scope='exact-audit', origin='alone', source='public:seed')
    mind.checked_wake.add(r.id)
    sleep.admit(r, {})
    return mind, sleep


def test_aimed_dreams_contain_gap_part_and_pass_both_interpreters():
    mind, sleep = dream_mind()
    before = mind.field.curiosity.dream_share
    receipts = sleep.dream(8, attempts=32)
    admitted = [row for row in mind.field.curiosity.dream_log if row['admitted']]
    assert before == .5
    assert {row['route'] for row in admitted} == {'aimed', 'random'}
    lookup = {r.id: r for r in receipts}
    for row in admitted:
        r = lookup[row['receipt']]
        assert r.check({})
        if row['route'] == 'aimed':
            assert row['part'] in gap_parts(r.targets, r.view)
            for bindings, expected in r.view.examples:
                assert independent(r.targets[0], dict(bindings), {}) == expected
    # Admission alone does not increase the share. Actual later progress does.
    assert mind.field.curiosity.dream_share == before
    c = mind.field.curiosity
    c.finish(view().identity, c.gap, (signal(0.),), solved=True, search=1.)
    assert c.dream_share > before  # random +1 compositions lacked the located mul


def test_aimed_interpreter_disagreement_never_admitted(monkeypatch):
    mind, sleep = dream_mind()
    original = LG.evaluate
    def mismatching(p, env, concepts):
        if any(part[0] == 'mul' for part in walk(p)):
            return -999
        return original(p, env, concepts)
    monkeypatch.setattr(LG, 'evaluate', mismatching)
    receipts = sleep.dream(8, attempts=16)
    assert receipts
    assert not any(('production', 'mul') in gap_parts(r.targets, r.view) for r in receipts)
    assert not any(row['admitted'] for row in mind.field.curiosity.dream_log if row['route'] == 'aimed')


@pytest.mark.parametrize('phase,allowed', [('lesson', True), ('test1', True), ('talk', True),
                                          ('world', True), ('study', False), ('test2', False), ('test3', False)])
def test_course_boundary_questions_and_priority(phase, allowed):
    c = Curiosity()
    gap(c)
    engine = Engine.__new__(Engine)
    engine.u_switches = {'gap_syndromes': True}
    engine.field = SimpleNamespace(curiosity=c)
    engine._u_gap_context = dict(phase=phase)
    actions = [dict(action=('ask', 1), info=10.), dict(action=('ask', 2), info=.1)]
    chosen = engine._u_actions(PublicTask(), actions)
    assert chosen == ([actions[1]] if allowed else [])
    # Selection alone never calls teacher functions or mutates examples.
    assert PublicTask.data == [(0, 0)]
    engine.u_switches['gap_syndromes'] = False
    assert engine._u_actions(PublicTask(), actions) is actions


def test_study_order_reads_matching_public_words_and_kinds_first():
    c = Curiosity()
    gap(c)
    books = [TaskView((('x', 'list'),), 'list', words=('history',)),
             TaskView((('x', 'num'),), 'num', words=('mul square',)),
             TaskView((('x', 'num'),), 'num', words=('mul square',))]
    assert c.study_order(books) == [1, 2, 0]


def test_aimed_switch_off_and_both_off_preserve_unaimed_receipts_and_rng():
    a, asleep = dream_mind(syndromes=False, aimed=False)
    b, bsleep = dream_mind(syndromes=True, aimed=False)
    # U3 had no U6 mask entries at all.
    del a.crutches['gap_syndromes']
    del a.crutches['aimed_dreams']
    assert asleep.dream(4, attempts=16) == bsleep.dream(4, attempts=16)
    assert a.random.getstate() == b.random.getstate()
    assert not any(row['route'] == 'aimed' for row in b.field.curiosity.dream_log)


def test_both_off_preserve_legacy_live_records(monkeypatch):
    _, _, plus = programs()
    monkeypatch.setattr(ONE.time, 'time', lambda: 100.)
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 100.)
    monkeypatch.setattr(ONE, '_peak_mb', lambda: 10.)
    monkeypatch.setattr(LG, '_rss_mb', lambda: 10.)
    monkeypatch.setattr(ONE.Sera, '_generate', lambda self, task, level, concepts: [plus])
    monkeypatch.setattr(ONE.Sera, '_evoke', lambda *args, **kwargs: None)
    monkeypatch.setattr(PH.LoopField, 'choose', lambda *args, **kwargs: (['prove'], {'prove': (1., 0.)}))
    field = PH.Field(3)
    legacy = ONE.Sera(3, copy.deepcopy(field), library_enabled=False)
    new = Engine(3, copy.deepcopy(field), library_enabled=False)
    new.u_switches = {k: False for k in U3_CRUTCHES+U6_CRUTCHES}
    def task():
        return TS.Exact('math', 'public', lambda x: x+1, {'x': 'num'}, 'num', [0, 1, 2, 3],
                        [], lambda rng: 4)
    assert legacy.live(task(), max_steps=1) == new.live(task(), max_steps=1)


def test_decoder_and_pending_dream_returns_survive_entity_checkpoint():
    mask = {k: False for k in U1_CRUTCHES+U2_CRUTCHES+U3_CRUTCHES+U6_CRUTCHES}
    mask.update(gap_syndromes=True, aimed_dreams=True, field_input_ports=True)
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=mask)
    g = gap(mind.field.curiosity)
    mind.field.curiosity.reinforce(g, 1.)
    mind.field.curiosity.dream_trial(g, 'aimed', False)
    clone = SeraU.loads(mind.dumps())
    assert clone.learning_hash() == mind.learning_hash()
    for c in (mind.field.curiosity, clone.field.curiosity):
        c.finish(view().identity, c.gap, (signal(0.),), solved=True, search=1.)
    assert clone.learning_hash() == mind.learning_hash()


def test_pair_uses_identical_u3_settings_and_report_has_censored_denominators(tmp_path):
    a, b = arm_settings('aimed'), arm_settings('unaimed')
    assert all(a[k] == b[k] for k in U1_CRUTCHES+U2_CRUTCHES+U3_CRUTCHES)
    assert all(a[k] and not b[k] for k in U6_CRUTCHES)
    from scripts.sera_u_rsi import report
    state = dict(protocol=dict(arms=['aimed', 'unaimed'], generations=3, eval_tasks=48),
                 rows=[], stage='incomplete', started=0, deadline=21600)
    (tmp_path/'state.json').write_text(json.dumps(state), encoding='utf-8')
    r = report(tmp_path)
    assert r['missing_rows'] == 384
    assert all(r['time_to_learn'][arm]['censored'] == 48 for arm in ('aimed', 'unaimed'))
    assert not r['complete'] and not r['pilot_pass']


def test_engine_syndrome_uses_stub_settled_read_and_private_fields_are_inert():
    x, square, _ = programs()
    task = PublicTask()
    engine = Engine.__new__(Engine)
    engine.u_switches = {'gap_syndromes': True}
    engine.library_enabled = False
    engine.memory = None
    engine.field = SimpleNamespace(curiosity=Curiosity())
    engine.proposer = SimpleNamespace(_gap_surest=('production', 'add'))
    engine._u_reads = lambda views, concepts=None: [(torch.zeros(3, 64), torch.ones(3)/3)]
    engine._u_gap_context = dict(view=TaskView.from_task(task), candidates=(), roadmap=[],
                                 fingerprint=None, gap=None)
    a = engine._u_syndrome(task, [x, square], {}, {}, accepted=x)
    task.observer_grades = {'right': True}
    task.hidden_target = lambda _: 999
    b = engine._u_syndrome(task, [x, square], {}, {}, accepted=x, final=True)
    assert logical(a) == logical(b)
    assert engine.field.curiosity.gap['inputs'] == ((('x', 2),), (('x', 3),))
    assert next(r for r in b if r.check == 'proposer_search').value == 1


def test_small_positive_progress_strengthens_decoder_paths():
    c = Curiosity()
    g = gap(c)
    c.reinforce(g, .01)
    assert c.weights['committee'] > 1.
    assert c.paths[('committee', ('production', 'mul'))][0] > 0.


def test_no_return_after_aimed_work_reduces_its_share():
    c = Curiosity()
    g = gap(c)
    c.dream_trial(g, 'aimed', False)
    c.finish(view().identity, g, (signal(),), solved=False, search=2.)
    assert c.dream_share < .5


@pytest.mark.parametrize('allowed', [False, True])
def test_talk_questions_use_heard_inputs_and_only_existing_teacher_answer_seam(allowed):
    engine = Engine.__new__(Engine)
    engine.u_switches = {'gap_syndromes': True}
    engine.library_enabled = True
    engine._u_talk_allowed = allowed
    engine.field = PH.Field(3)
    engine.field.curiosity = Curiosity()
    g = ((101,), (102,))
    concepts = {1: (LG.node('one'), '_'), 2: (LG.node('zero'), '_'),
                '_sig': {1: ('list(list)', 'list'), 2: ('list(list)', 'list')}}
    # Stub concept bodies with list outputs, preserving the real call boundary.
    concepts[1] = (LG.node('cons', LG.node('one'), LG.node('nil')), '_')
    concepts[2] = (LG.node('cons', LG.node('zero'), LG.node('nil')), '_')
    engine._concepts = lambda: concepts
    engine._u_reads = lambda views, concepts=None: [(torch.zeros(3, 64), torch.ones(3)/3)]
    engine._u_talk_gap(g, g[0], [(1, 1.), (2, .9)])
    assert bool(engine.field.inbox) == allowed
    if allowed:
        question = engine.field.inbox[0]
        assert question['numbers']['inputs'] == ((('g', g),),)
        engine._u_talk_correct(g, g[0], (1,), (1,), 1, {1: (1,), 2: (0,)})
        assert question['id'] in engine.field.answers
        assert engine.field.curiosity.returns[-1]['reward'] == 1.
    assert engine.field.standing == {}


def test_aimed_grafts_can_combine_mixed_types_and_known_lambda_bodies():
    _, _, plus = programs()
    xs = LG.node('var', payload='x')
    tail = LG.node('tail', xs)
    options = aimed_compositions([(plus, 'num', 'num'), (tail, 'list', 'list')], {}, ('production', 'map'))
    assert options
    p, tin, tout = options[0]
    assert tin == 'list' and tout == 'list'
    assert independent(p, {'x': (1, 2, 3)}, {}) == LG.evaluate(p, {'x': (1, 2, 3)}, {})
    assert ('production', 'map') in gap_parts((p,), TaskView((('x', tin),), tout))


def test_study_actually_visits_matching_book_items_first_without_question_permission():
    mind = SeraU.__new__(SeraU)
    mind.crutches = dict(gap_syndromes=True)
    mind.field = SimpleNamespace(curiosity=Curiosity())
    gap(mind.field.curiosity)
    books = [TaskView((('x', 'list'),), 'list', words=('history',)),
             TaskView((('x', 'num'),), 'num', words=('square mul',))]
    mind.live = lambda item, **kwargs: (item.words, kwargs)
    records = mind.study(books)
    assert records[0][0] == ('square mul',)
    assert all(row[1]['phase'] == 'study' and row[1]['origin'] == 'book' for row in records)


def test_observer_verdict_source_is_rejected_before_calibration_changes():
    c = Curiosity()
    with pytest.raises(ValueError, match='received'):
        c.verdict('exact:num->num', .9, True, 'observer')
    assert c.calibration == {}


def test_historical_suite_validation_stays_on_observer_side():
    from scripts.sera_u_rsi import validate_frozen_suite
    with pytest.raises(ValueError, match='48/16'):
        validate_frozen_suite(dict(assessment=[], wake=[], retention=[], seed_count=0))


def test_actual_beam_confidence_is_retained_for_accepted_program_comparison(monkeypatch):
    from sera_u import proposer as PP
    proposer = PP.Proposer.__new__(PP.Proposer)
    proposer.memory = None
    proposer.stats = dict(proposal=0.)
    choices = (PP.Production('zero', None, (), 'num'), PP.Production('one', None, (), 'num'))
    monkeypatch.setattr(PP, 'legal', lambda *args: choices)
    monkeypatch.setattr(CR, 'ON', {'gap_syndromes'})
    proposer.distribution = lambda features, weights, options: (
        options, torch.tensor([[math.log(.1), math.log(.9)]]*3), weights)
    v = TaskView((('x', 'num'),), 'num', (((('x', 0),), 0),), queries=((('x', 1),),))
    proposer.beam(v, {}, nodes=3, read=(torch.zeros(3, 64), torch.ones(3)/3))
    assert proposer._gap_surest == ('production', 'one')
    rows = Curiosity().checks(v, (LG.node('zero'),), {}, surest=proposer._gap_surest,
                              accepted=LG.node('zero'))
    assert next(r for r in rows if r.check == 'proposer_search').value == 1.
