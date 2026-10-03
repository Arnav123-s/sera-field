"""U7 CPU contracts: public-only stubs; Python execution belongs to development review."""
import ast
import copy
import math
import pickle
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import Engine, U3_CRUTCHES, U6_CRUTCHES, U7_CRUTCHES, arm_settings
from sera_u.ports import TaskView


class MeanDraw:
    def multivariate_normal(self, mean, covariance):
        return mean.copy()


def x(sign=0.):
    return np.r_[1., sign, np.zeros(63)]


def world():
    # Both candidates fit the public inputs; only one passes the independent audit.
    return TS.Exact('math', 'same item', lambda v: v+1, {'x': 'num'}, 'num',
                    [0, 0, 0, 0], [1, 2], lambda rng: 2)


def candidates():
    one = LG.node('one')
    return one, LG.node('add', LG.node('var', payload='x'), one)


def read_stub(self, views, concepts=None):
    return [(torch.zeros(3, 64), torch.ones(3)/3) for _ in views]


def candidate_stub(self, task, programs):
    return [x(1. if p == candidates()[1] else -1.) for p in programs]


def generate_stub(self, task, level, concepts):
    return [candidates()[0]]


def evoke_stub(*args, **kwargs):
    pass


def imagine_stub(self, method, task, kind, leader, concepts, library, mu, st, *args, **kwargs):
    st.setdefault('u_stub_methods', []).append(method)
    return {candidates()[1]: (('stub',), method)}


def deterministic_pick(self, kind, f, probability, available, rng, spent=0.):
    return ORIGINAL_PICK(self, kind, f, probability, available, MeanDraw(), spent)


ORIGINAL_PICK = PH.NotYetWays.pick


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    monkeypatch.setattr(PH.NotYetWays, 'pick', deterministic_pick)
    monkeypatch.setattr(Engine, '_u_reads', read_stub)
    monkeypatch.setattr(Engine, '_u_candidate_inputs', candidate_stub)
    # Keep controller tests short; method order still comes from real posteriors.
    monkeypatch.setattr(PH.FieldMethods, 'candidates', lambda self: [('dream',), ('back',), ('step',)])
    LG.forget_searches()
    yield
    LG.forget_searches()


def entity(**switches):
    mask = {**arm_settings('full'), **{k: False for k in U3_CRUTCHES+U6_CRUTCHES},
            **{k: False for k in U7_CRUTCHES}, 'taught_not_yet': True, 'inner_judge': True,
            'field_proposer': False, 'memory_layer_a': False, 'memory_layer_b': False,
            'field_understanding': False, **switches}
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=mask)


def teach_choice(mind, kind, sign, shown, available=('answer', 'method', 'step', 'grow')):
    f = mind.field.loop.choice_features(x(sign), .5)
    for _ in range(12):
        mind.field.loop.demonstrate(kind, f, available, shown)


def stub_live(monkeypatch):
    monkeypatch.setattr(Engine, '_generate', generate_stub)
    monkeypatch.setattr(Engine, '_evoke', evoke_stub)
    monkeypatch.setattr(Engine, '_imagine', imagine_stub)


def test_not_yet_uses_next_method_then_proves_later_candidate_in_same_item(monkeypatch):
    stub_live(monkeypatch)
    mind, task = entity(abstain_bar=True), world()
    kind = ONE.kind_of(task)
    teach_choice(mind, kind, -1., 'method')
    teach_choice(mind, kind, 1., 'answer')
    # A taught-on run must never use the bar, even if both switches are enabled.
    monkeypatch.setattr(PH.InnerJudge, 'decide', lambda *a: pytest.fail('U7 used cost-bar decision'))
    record = mind.live(task, max_steps=4, task_wall=math.inf)
    assert record['proven'] and record['answer'] == candidates()[1]
    assert record['u7']['state'] == 'right'
    # Unsure, it keeps going: a method first, never an answer while the distrusted candidate leads, the answer last.
    # (The imagined candidate does not lead at once - the lab prefers the simpler one that fits the same examples -
    # so a further continuation, e.g. asking the world, may come between; any continuation is "not yet".)
    actions = [m['action'] for m in record['u7']['moments']]
    assert actions[0] == 'method' and actions[-1] == 'answer' and 'answer' not in actions[:-1]
    assert record['u7']['time_to_right'] is not None
    assert mind.field.tasks == 1 and not mind.field.revisit_queue


def test_method_ranking_skips_methods_already_tried_and_step_remains_available():
    mind, task = entity(), world()
    methods = mind.field.methods
    methods.teach(ONE.kind_of(task), ('dream',), {}, y=10.)
    ranking = methods.ranking(ONE.kind_of(task), {'dream', 'back'}, {}, {('dream',)})
    assert ranking == [('back',)]
    kind = ONE.kind_of(task)
    teach_choice(mind, kind, -1., 'step')
    st = dict(proven=None, steps=0, teaching=False, u_tried_methods={('dream',), ('back',)})
    config, _ = mind.engine._u_configuration(task, candidates()[0], {'prove', 'grow'},
                                             {'dream', 'back'}, {}, {}, st, MeanDraw(), 0.)
    assert config == ['imagine'] and st['u_next_method'] == ('step',)
    assert st['u_not_yet'][0]['action'] == 'step'


def test_budget_end_is_pending_and_queue_is_checkpointed(monkeypatch):
    stub_live(monkeypatch)
    mind, task = entity(), world()
    record = mind.live(task, task_wall=0., max_steps=8)
    assert not record['proven'] and record['answer'] is None
    assert record['verdict'] == record['u7']['state'] == 'not-yet'
    assert len(mind.field.revisit_queue) == 1
    assert not any('give' in event['what'] for event in record['say'])
    item = mind.field.revisit_queue[0]
    assert type(item['view']) is TaskView and '_target' not in repr(item)
    restored = SeraU.loads(mind.dumps())
    assert restored.field.revisit_queue == mind.field.revisit_queue
    assert restored.learning_hash() == mind.learning_hash()


def test_queued_item_is_solved_after_an_intervening_item(monkeypatch):
    stub_live(monkeypatch)
    mind, task = entity(), world()
    mind.live(task, task_wall=0., max_steps=0)
    # Another completed moment separates the attempts; the candidate is then taught.
    other = world()
    other.data = [(0, 3)]*4
    mind.live(other, task_wall=0., max_steps=0)
    teach_choice(mind, ONE.kind_of(task), -1., 'method')
    teach_choice(mind, ONE.kind_of(task), 1., 'answer')
    records = mind.revisit([task], task_wall=math.inf, max_steps=4)
    assert len(records) == 1 and records[0]['proven']
    assert records[0]['u7']['solved_on_revisit'] is True
    assert mind.field.u7_revisits_solved == 1


def test_teacher_choice_fades_then_returns_move_answering_both_ways():
    ways = PH.NotYetWays()
    f = ways.choice_features(x(), .5)
    ways.demonstrate('k', f, {'answer', 'method'}, 'method')
    assert ways.pick('k', x(), .5, {'answer', 'method'}, MeanDraw())[0] == 'method'
    taught = copy.deepcopy(ways.choice_taught)
    ways.end_task('k')
    for key, (A, b) in taught.items():
        np.testing.assert_array_equal(ways.choice_taught[key][0], A*PH.TAUGHT_FADE)
        np.testing.assert_array_equal(ways.choice_taught[key][1], b*PH.TAUGHT_FADE)
    for j in range(30):
        ways.remember('k', j, 'method', f, 'method')
        ways.returned('k', j, True, source='proof')
    assert ways.pick('k', x(), .5, {'answer', 'method'}, MeanDraw())[0] == 'answer'
    for j in range(30, 110):
        ways.remember('k', j, 'answer', f, 'method')
        ways.returned('k', j, False, source='proof')
    assert ways.pick('k', x(), .5, {'answer', 'method'}, MeanDraw())[0] == 'method'
    before = pickle.dumps(ways.choice_stats)
    with pytest.raises(ValueError):
        ways.returned('k', 200, True, source='observer')
    assert pickle.dumps(ways.choice_stats) == before


def talk_item():
    q = tuple(TS.sym(w) for w in ('what', 'now'))
    y = (TS.sym('heard'),)
    talk = SimpleNamespace(name='turn', items=[((q,), y, 'observer-kind')],
                           sentences=lambda item: (), perceive=lambda item: item)
    return talk, q, y


def silent_reply(self, g, q=None):
    return None, None, []


def heard_reply(self, g, q=None):
    return (TS.sym('heard'),), 7, []


def talk_read_stub(self, g, q, candidates):
    return [x() for _ in candidates]


def test_talk_pending_answers_on_later_turn_and_uses_only_taught_words(monkeypatch):
    talk, q, y = talk_item()
    mind = entity()
    monkeypatch.setattr(ONE.Sera, 'reply', silent_reply)
    monkeypatch.setattr(Engine, '_u_talk_inputs', talk_read_stub)
    first = mind.converse(talk, teaching=False)
    assert first['rows'][0]['response'] == 'not-yet'
    assert first['rows'][0]['said'] is None
    assert mind.field.u7_talk_pending[0]['asked_turn'] == 1
    # A pending question and its delay survive a checkpoint.
    mind = SeraU.loads(mind.dumps())
    mind.teach_not_yet('still considering')
    silent = mind.converse(talk, teaching=False)
    assert silent['rows'][0]['response'] == 'still considering'
    assert {'still', 'considering'} <= set(mind.field.lexicon.heard)
    kind = ('talk', q[:2])
    teach_choice(mind, kind, 0., 'answer', ('answer', 'recall'))
    monkeypatch.setattr(ONE.Sera, 'reply', heard_reply)
    before = pickle.dumps(mind.field.inner)
    delivered = []
    third = mind.converse(talk, teaching=False, on_say=delivered.append)
    event = third['u7']['delayed'][0]
    assert event['asked_turn'] == 1 and event['answered_turn'] == 3 and event['delay_turns'] == 2
    assert event['said'] == 'heard' and event in delivered
    assert not mind.field.u7_talk_pending
    assert pickle.dumps(mind.field.inner) == before


def test_talk_teacher_rewards_a_right_withheld_answer(monkeypatch):
    talk, q, y = talk_item()
    mind = entity()
    monkeypatch.setattr(ONE.Sera, 'reply', heard_reply)
    monkeypatch.setattr(Engine, '_u_talk_inputs', talk_read_stub)
    monkeypatch.setattr(ONE.Sera, '_situation_ideas', lambda self: [])
    monkeypatch.setattr(ONE.Sera, '_correct', lambda *a, **k: [])
    kind = ('talk', q[:2])
    teach_choice(mind, kind, 0., 'recall', ('answer', 'recall'))
    f = mind.field.loop.choice_features(x(), .5)
    before_answer = mind.field.loop.choice_post(kind, 'answer')[0] @ f
    before_recall = mind.field.loop.choice_post(kind, 'recall')[0] @ f
    first = mind.converse(talk, teaching=True)
    assert first['rows'][0]['status'] == 'not-yet'
    assert mind.field.loop.choice_post(kind, 'answer')[0] @ f > before_answer
    assert mind.field.loop.choice_post(kind, 'recall')[0] @ f < before_recall


def test_no_fixed_phrase_in_active_code_and_bar_is_a_registered_fixed_crutch():
    root = Path(__file__).resolve().parents[2]
    forbidden = CR.REGISTRY['abstain_bar']['response']
    for path in (root/'sera_u/mind.py', root/'sera/one.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        assert not any(isinstance(node, ast.Constant) and node.value == forbidden for node in ast.walk(tree))
    assert CR.REGISTRY['abstain_bar']['status'] == 'fixed'
    assert CR.REGISTRY['taught_not_yet']['status'] == 'learned'


@pytest.mark.parametrize('phase', ['test2', 'test3'])
def test_exam_attempt_receives_no_new_examples_or_help(monkeypatch, phase):
    stub_live(monkeypatch)
    mind, task = entity(), world()
    teach_choice(mind, ONE.kind_of(task), -1., 'answer')
    original = copy.deepcopy(task.data)
    record = mind.live(task, phase=phase, teaching=True, task_wall=math.inf, max_steps=1)
    assert task.data == original and task.asked == 0
    assert not record['proven']
    assert not mind.field.inner.contrasts
    assert record['u7']['state'] == 'not-yet'
    if phase == 'test3':
        assert not mind.field.revisit_queue
    # Verdict-only test2 feedback supplies no positive correction half.
    if phase == 'test2':
        before = sum(r[0] for r in mind.field.inner.curves[ONE.kind_of(task)])
        mind.engine.course_verdict(task, candidates()[0], False, 'test2')
        assert sum(r[0] for r in mind.field.inner.curves[ONE.kind_of(task)]) == before+1
        assert mind.field.inner.contrasts == 0
        assert mind.revisit([task]) == []
    else:
        with pytest.raises(ValueError):
            mind.engine.course_verdict(task, candidates()[0], False, 'test3')


@pytest.mark.parametrize('bar', [True, False])
def test_switches_restore_u3_bar_or_u2_answer_if_candidate_fits(monkeypatch, bar):
    talk, q, y = talk_item()
    monkeypatch.setattr(ONE.Sera, 'reply', heard_reply)
    monkeypatch.setattr(Engine, '_u_talk_inputs', talk_read_stub)
    mind = entity(taught_not_yet=False, abstain_bar=bar)
    kind = ('talk', q[:2])
    for _ in range(30):
        mind.field.inner.verdict(kind, (7, y), x(), False, 'talk')
    result = mind.converse(talk, teaching=False)
    assert 'u7' not in result
    assert result['rows'][0]['response'] == (CR.REGISTRY['abstain_bar']['response'] if bar else 'heard')
    assert (result['rows'][0]['said'] is not None) == (not bar)
    assert type(mind.field.loop) is PH.LoopField


def test_old_u3_masks_retain_implicit_bar_and_u6_arms_do_not_enable_u7():
    old = {**arm_settings('full'), **{k: False for k in U3_CRUTCHES+U6_CRUTCHES}, 'inner_judge': True}
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=old)
    assert mind.crutches['abstain_bar'] and not mind.crutches['taught_not_yet']
    assert not mind.u7_declared
    assert not any(k in arm_settings('aimed') for k in U7_CRUTCHES)


def test_saved_taught_readout_resumes_next_draw_and_pending_choices():
    mind = entity()
    kind = 'k'
    teach_choice(mind, kind, -1., 'method')
    f = mind.field.loop.choice_features(x(-1.), .5)
    mind.field.loop.remember(kind, 'public-candidate', 'method', f, 'method')
    restored = SeraU.loads(mind.dumps())
    assert mind.learning_hash() == restored.learning_hash()
    first = ORIGINAL_PICK(mind.field.loop, kind, x(-1.), .5, {'answer', 'method'}, np.random.default_rng(19))
    second = ORIGINAL_PICK(restored.field.loop, kind, x(-1.), .5, {'answer', 'method'}, np.random.default_rng(19))
    assert first[0] == second[0] and first[2] == second[2]
    np.testing.assert_array_equal(first[1], second[1])


def test_smallest_step_redreams_whole_and_waits_for_taught_submission(monkeypatch):
    mind, task = entity(), world()
    sketches = []
    def dream(view, *args):
        sketches.append(view)
        return [LG.node('var', payload='x' if len(sketches) == 1 else 'u_next')]
    def steps(ctx, inputs, probes, until):
        vals = [p['x']+1 for p in probes]
        return [(candidates()[1], 'num', vals, [vals[j] for j in ctx['where']], (.5, .2, 1., 1., .3))]
    monkeypatch.setattr(mind.engine, '_dream_roadmap', dream)
    monkeypatch.setattr(mind.engine, '_step_candidates', steps)
    monkeypatch.setattr(mind.engine, '_prove', lambda *a: pytest.fail('Roadmap bypassed taught submission'))
    st = dict(steps=0, teaching=False)
    made = mind.engine._step(task, mind.engine._concepts(), lambda *a, **k: None, (), st)
    assert made[0][0] == candidates()[1]
    assert [row['what'] for row in st['u_roadmap']] == ['dream', 'next', 'dream']
    assert len(sketches) == 2 and len(sketches[1].inputs) == 2
    assert not mind.field.standing and mind.field.steps.tried == 0


@pytest.mark.parametrize('inner,bar', [(True, True), (False, False)])
def test_u7_off_logical_live_records_match_legacy_u3_or_u2(monkeypatch, inner, bar):
    stub_live(monkeypatch)
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 0.)
    old_mask = {**arm_settings('full'), **{k: False for k in U3_CRUTCHES+U6_CRUTCHES},
                'field_proposer': False, 'inner_judge': inner,
                'memory_layer_a': False, 'memory_layer_b': False, 'field_understanding': False}
    first = SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=old_mask)
    second = SeraU(3, config=NativeConfig(nodes=3, rounds=1),
                   crutches={**old_mask, 'taught_not_yet': False, 'abstain_bar': bar})
    records = [mind.live(world(), max_steps=2, task_wall=math.inf) for mind in (first, second)]
    clocks = {'wall', 'cpu', 'timing', 'thinking_wall', 'thinking_cpu', 'finish_cpu',
              'peak_mb', 'peak_mb_by', 'gain_rate', 'phases'}
    def logical(value):
        if isinstance(value, dict):
            return {k: logical(v) for k, v in value.items() if k not in clocks and k not in U7_CRUTCHES}
        if isinstance(value, list):
            return [logical(v) for v in value if not isinstance(v, str) or v not in U7_CRUTCHES]
        return value
    assert logical(records[0]) == logical(records[1])
    assert not any('u7' in record for record in records)


def test_exam_queue_and_observer_results_never_become_learning(monkeypatch):
    stub_live(monkeypatch)
    mind, task = entity(), world()
    before = mind.learning_hash()
    result = mind.assess(task, task_wall=0., max_steps=0)
    assert result['status'] == 'not-yet' and not result['solved']
    assert before == result['before'] == result['after'] == mind.learning_hash()
    assert not mind.field.revisit_queue


def test_course_demonstrations_teach_answer_or_step_without_a_bar():
    mind, task = entity(), world()
    mind.teach_answer_choice(task, candidates()[0], False, continuation='step')
    kind = ONE.kind_of(task)
    assert mind.field.loop.pick(kind, x(-1.), .5, {'answer', 'step'}, MeanDraw())[0] == 'step'
    mind.teach_answer_choice(task, candidates()[1], True, continuation='step')
    assert mind.field.loop.pick(kind, x(1.), .5, {'answer', 'step'}, MeanDraw())[0] == 'answer'
    with pytest.raises(ValueError):
        mind.teach_answer_choice(task, candidates()[1], True, phase='test2')
    with pytest.raises(ValueError):
        mind.teach_answer_choice(task, candidates()[1], True, phase='test3')


def force_first_audit(self, *args, **kwargs):
    return ['prove'], {'prove': (1., 1.)}


def test_revisit_preserves_added_public_counterexample_and_original_training_port(monkeypatch):
    stub_live(monkeypatch)
    mind, task = entity(), world()
    choose = Engine._u_configuration
    monkeypatch.setattr(Engine, '_u_configuration', force_first_audit)
    first = mind.live(task, task_wall=math.inf, max_steps=1)
    assert not first['proven'] and len(task.data) == 5
    queued = mind.field.revisit_queue[0]
    assert len(queued['view'].examples) == 4 and len(queued['current_view'].examples) == 5
    other = world()
    other.data = [(0, 3)]*4
    mind.live(other, task_wall=0., max_steps=0)
    monkeypatch.setattr(Engine, '_u_configuration', choose)
    teach_choice(mind, ONE.kind_of(task), -1., 'method')
    teach_choice(mind, ONE.kind_of(task), 1., 'answer')
    later = mind.revisit([task], task_wall=math.inf, max_steps=4)
    assert later[0]['proven'] and later[0]['u7']['solved_on_revisit']
    assert len(task.data) == 5 and mind.field.u7_revisits_solved == 1
