"""U3 CPU contracts; real Field reads are limited to one boundary smoke."""
import copy
import json
import math
import pickle
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import Engine, U1_CRUTCHES, U2_CRUTCHES, U3_CRUTCHES, arm_settings
from sera_u.ports import TaskView


@pytest.fixture(autouse=True)
def deterministic(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


def entity(**switches):
    mask = {**arm_settings('full'), **{k: False for k in U3_CRUTCHES}, **switches}
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=mask)


def task():
    return TS.Exact('math', 'public', lambda x: x+2, {'x': 'num'}, 'num', [-2, 0, 1, 4],
                    [], lambda rng: int(rng.integers(-8, 9)))


def programs():
    x, one = LG.node('var', payload='x'), LG.node('one')
    step = LG.node('add', x, one)
    return x, step, LG.node('add', step, one)


def fake_reads(views, concepts=None):
    # Same public content gives the same stub settled context. No hidden grade.
    return [(torch.zeros(3, 64), torch.ones(3)/3) for _ in views]


def factual(mind):
    ideas = mind.field.ideas
    return ({k: v.clone() for k, v in mind.state.items()},
            copy.deepcopy(ideas._row), ideas._M[:ideas._n].copy(),
            copy.deepcopy(mind.field.concepts), copy.deepcopy(mind.field.senses))


def assert_factual_same(before, mind):
    after = factual(mind)
    assert before[0].keys() == after[0].keys()
    assert all(torch.equal(before[0][k], after[0][k]) for k in before[0])
    assert before[1] == after[1]
    np.testing.assert_array_equal(before[2], after[2])
    assert before[3:] == after[3:]


class MeanDraw:
    def multivariate_normal(self, mean, covariance):
        return mean.copy()


def test_field_ways_teacher_fades_and_actual_returns_change_values():
    f = PH.FieldWays()
    f.bind(np.ones((3, 64)))
    available = {'ask', 'grow', 'imagine'}
    f.teach('k', {}, {}, available, ['ask'])
    taught = copy.deepcopy(f.taught)
    x = f.features({}, {}, 'grow')
    before = f.posterior('k', 'grow')[0] @ x
    for _ in range(8):
        f.learn('grow', x, 8.)
    f.end_task('k')
    assert f.posterior('k', 'grow')[0] @ x > before
    for fac in sorted(available):
        np.testing.assert_array_equal(f.taught['k'][fac][0], taught['k'][fac][0]*PH.TAUGHT_FADE)
        np.testing.assert_array_equal(f.taught['k'][fac][1], taught['k'][fac][1]*PH.TAUGHT_FADE)
    # Multiple faculties can run; neutral estimates do not disable them.
    for fac in sorted(available):
        for _ in range(8):
            f.learn(fac, f.features({}, {}, fac), 8.)
    chosen, _ = f.choose('k', {}, {}, available, MeanDraw())
    assert set(chosen) == available
    f.bind(-np.ones((3, 64)))
    assert not np.array_equal(x, f.features({}, {}, 'grow'))


def test_field_method_and_step_returns_and_teacher_fade():
    methods = PH.FieldMethods()
    methods.bind(np.ones((3, 64)))
    methods.teach('k', ('compose',), {})
    taught = copy.deepcopy(methods.taught)
    methods.choose('k', {'compose'}, {}, MeanDraw())
    x = methods.features({})
    before = methods._post('k', ('compose',))[0] @ x
    for _ in range(3):
        methods.learn('k', ('compose',), {}, 12.)
    assert methods._post('k', ('compose',))[0] @ x > before
    methods.end_task()
    for key in taught:
        np.testing.assert_array_equal(methods.taught[key][0], taught[key][0]*PH.TAUGHT_FADE)
    sf = PH.FieldSteps()
    sf.bind(np.ones((3, 64)))
    features = (.5, .4, .2, 1., .3)
    sf.teach(features, 1.)
    taught = sf.At.copy()
    before = sf.score(features)
    sf.learn(features, 1.)
    assert sf.score(features) > before
    sf.end_task()
    np.testing.assert_array_equal(sf.At, taught*PH.TAUGHT_FADE)


@pytest.mark.parametrize('method', ['compose', 'recall', 'dream', 'step', 'back',
                                   'wish', 'closer', 'dimension', 'question'])
def test_each_method_drives_all_three_branches_without_fact_writes(monkeypatch, method):
    mind = entity(field_methods=True)
    engine, t = mind.engine, task()
    engine._built, engine._task_senses = [], []
    engine._footholds, engine._open_steps, engine._dims_cache = {}, [], None
    engine._step_cut = False
    monkeypatch.setattr(engine, '_u_reads', fake_reads)
    calls = []
    def move(self, selected, world, *args, **kwargs):
        calls.append(selected)
        self.field.senses.append(dict(name='temporary'))
        self.field.ideas.read((TS.sym('hypothetical'),))
        args[2].setdefault('_sig', {})[999] = ('num', 'num')
        self._footholds['hypothetical'] = True
        return [(programs()[2], ('stub-method', selected))]
    monkeypatch.setattr(ONE.Sera, '_move', move)
    monkeypatch.setattr(mind.proposer, 'beam', lambda *a, **k: [programs()[2]])
    monkeypatch.setattr(engine, '_backward', lambda *a, **k: (programs()[2], programs()[0], programs()[1]))
    monkeypatch.setattr(ONE, 'ONE_FIELD', False)
    st = dict(moved=set(), steps=0, level=0, trig={}, teaching=False)
    before = factual(mind)
    supplied = engine._concepts()
    footholds = engine._footholds
    selected = mind.field.methods.choose('k', {method}, {}, MeanDraw())
    assert selected == [(method,)]*3
    for chosen in selected:
        out = engine._imagine(chosen, t, 'k', programs()[0], supplied, {}, None,
                              st, [], {}, lambda *a, **k: None)
        assert programs()[2] in out
    assert [row['branch'] for row in st['u_branches']] == [0, 1, 2]
    assert all(row['hypothetical'] and row['field'] == [0.]*64 for row in st['u_branches'])
    assert_factual_same(before, mind)
    assert programs()[2] in mind.proposer.imagined
    assert 999 not in supplied['_sig'] and 'hypothetical' not in footholds
    if method not in ('dream', 'back'):
        assert calls == [method]*3


def prepare_roadmap(monkeypatch):
    mind = entity(field_roadmap=True)
    t = task()
    reads = []
    def read(views, concepts=None):
        reads.extend(views)
        return fake_reads(views)
    monkeypatch.setattr(mind.engine, '_u_reads', read)
    verdicts = []
    def prove(world, p, concepts, library, st, speak):
        verdicts.append(p)
        assert world.consistent(p, concepts)
        st['proven'] = dict(law=p)
        return True
    monkeypatch.setattr(mind.engine, '_prove', prove)
    return mind, t, reads, verdicts


def test_roadmap_correct_whole_goes_to_outer_at_once(monkeypatch):
    mind, t, reads, verdicts = prepare_roadmap(monkeypatch)
    monkeypatch.setattr(mind.engine, '_dream_roadmap', lambda *a: [programs()[2]])
    def no_step(*a, **k):
        raise AssertionError('A consistent whole must not be decomposed')
    monkeypatch.setattr(mind.engine, '_step_candidates', no_step)
    st = dict(steps=0, teaching=False)
    before = factual(mind)
    got = mind.engine._step(t, mind.engine._concepts(), lambda *a, **k: None, (), st)
    assert got[0][0] == programs()[2] and verdicts == [programs()[2]]
    assert [row['what'] for row in st['u_roadmap']] == ['dream']
    assert len(reads) == 1
    assert_factual_same(before, mind)


def test_wrong_roadmap_takes_one_step_then_redreams_without_writing(monkeypatch):
    mind, t, reads, verdicts = prepare_roadmap(monkeypatch)
    x, step, full = programs()
    dreams = []
    def dream(view, concepts, read, until):
        dreams.append(view)
        if len(dreams) == 1:
            return [x]
        return [LG.node('add', LG.node('var', payload='u_next'), LG.node('one'))]
    monkeypatch.setattr(mind.engine, '_dream_roadmap', dream)
    def candidates(ctx, inputs, probes, until):
        assert len(dreams) == 1
        vals = [LG.safe(step, p, ctx['concepts']) for p in probes]
        made = [vals[j] for j in ctx['where']]
        return [(step, 'num', vals, made, (.5, .3, 1., 1., 1./3))]
    monkeypatch.setattr(mind.engine, '_step_candidates', candidates)
    st = dict(steps=0, teaching=False)
    before = factual(mind)
    got = mind.engine._step(t, mind.engine._concepts(), lambda *a, **k: None, (), st)
    assert got[0][0] == full and verdicts == [full]
    assert [row['what'] for row in st['u_roadmap']] == ['dream', 'next', 'dream']
    assert len(reads) == 3 and len(st['u_steps']) == 1
    assert 'hypothetical-output' in repr(reads[1].hypotheses) and reads[1].queries == reads[0].queries
    assert dict(dreams[1].inputs)['u_next'] == 'num'
    for bindings, y in dreams[1].examples:
        values = dict(bindings)
        assert values['u_next'] == values['x']+1
    assert_factual_same(before, mind)


def judge_x(sign=0.):
    z = np.zeros((3, 64))
    z[:, 0] = sign
    return PH.InnerJudge.features(z)


def test_inner_probability_calibration_and_adaptive_bar_both_directions():
    inner, x = PH.InnerJudge(), judge_x()
    assert inner.decide('k', 'a', x)[0]
    initial = inner.bar('k')
    for _ in range(24):
        inner.decide('k', 'a', x)
        inner.verdict('k', 'a', x, False, 'proof')
    high = inner.bar('k')
    assert high > initial and not inner.decide('k', 'a', x)[0]
    # Every later verdict, including withheld candidates, can repair trust.
    for _ in range(40):
        inner.decide('k', 'a', x)
        inner.verdict('k', 'a', x, True, 'teacher')
    assert inner.bar('k') < high and inner.decide('k', 'a', x)[0]
    rows = inner.report()['calibration']['k']
    assert sum(row['n'] for row in rows) == 64
    assert rows[5]['predicted'] is not None  # birth probability .5, before update
    assert any(row['over_abstention'] for row in inner.report()['bars']['k'])
    assert sum(row['n']*row['observed'] for row in rows if row['n']) == pytest.approx(40)


def test_contrastive_correction_distinguishes_right_and_wrong_and_rejects_observer():
    inner, wrong, right = PH.InnerJudge(), judge_x(-1.), judge_x(1.)
    for _ in range(20):
        inner.correct('k', 'wrong', wrong, 'right', right)
    assert inner.probability('k', right) > inner.probability('k', wrong)
    assert inner.contrasts == 20
    saved = pickle.dumps(inner)
    for source in ('observer', 'test3', 'hidden', 'held-out', 'grade'):
        with pytest.raises(ValueError):
            inner.verdict('k', 'a', wrong, True, source)
    assert pickle.dumps(inner) == saved
    assert not hasattr(inner, 'certify') and not hasattr(inner, 'standing')


def test_actual_outer_refusal_cannot_be_certified_by_inner(monkeypatch):
    mind, t = entity(inner_judge=True), task()
    monkeypatch.setattr(mind.engine, '_u_candidate_inputs', lambda *a: [judge_x()])
    inner = mind.field.inner
    for _ in range(30):
        inner.verdict(ONE.kind_of(t), programs()[2], judge_x(), True, 'proof')
    assert inner.probability(ONE.kind_of(t), judge_x()) > .8
    calls = []
    def refused(*a):
        calls.append(a[0])
        return False, 4, None
    monkeypatch.setattr(t, 'verify', refused)
    st = dict(tested=set(), steps=0, proven=None)
    assert not mind.engine._prove(t, programs()[2], mind.engine._concepts(), {}, st, lambda *a, **k: None)
    assert calls == [programs()[2]] and st['proven'] is None
    assert not mind.field.concepts
    assert inner.bars[ONE.kind_of(t)][-1]['right'] is False


def talk_stub(y, n=1):
    q = tuple(TS.sym(w) for w in ('what', 'is', 'ladder'))
    x = (q,)
    return SimpleNamespace(name='stub talk', items=[(x, y, 'observer-only-kind')]*n,
                           sentences=lambda x: (), perceive=lambda x: x)


def install_talk_stub(monkeypatch):
    for w in ('what', 'is', 'ladder'):
        TS.sym(w)
    wrong = tuple(TS.sym(w) for w in ('wrong',))
    right = tuple(TS.sym(w) for w in ('right',))
    monkeypatch.setattr(ONE.Sera, 'reply', lambda self, g, q=None: (wrong, 7, [(7, 1.)]))
    monkeypatch.setattr(ONE.Sera, '_situation_ideas', lambda self: [])
    monkeypatch.setattr(ONE.Sera, '_correct', lambda *a, **k: [])
    monkeypatch.setattr(Engine, '_u_talk_inputs', lambda self, g, q, candidates:
                        [judge_x(-1. if v == wrong else 1.) for c, v in candidates])
    return wrong, right


def test_what_is_wrong_verdicts_abstain_and_persist_save_load(monkeypatch):
    wrong, right = install_talk_stub(monkeypatch)
    mind = entity(inner_judge=True)
    taught = mind.converse(talk_stub(right, 30), teaching=True)
    assert taught['rows'][0]['said'] is not None
    assert taught['rows'][-1]['response'] == "I don't know"
    assert mind.field.inner.contrasts == 30
    restored = SeraU.loads(mind.dumps())
    assert restored.learning_hash() == mind.learning_hash()
    before = pickle.dumps((restored.field.inner.weights, restored.field.inner.costs,
                           restored.field.inner.curves, restored.field.inner.bars))
    alone = restored.converse(talk_stub(wrong), teaching=False)
    assert alone['rows'][0]['response'] == "I don't know"
    # An untaught observer's 'right' for the withheld candidate does not train.
    assert before == pickle.dumps((restored.field.inner.weights, restored.field.inner.costs,
                                  restored.field.inner.curves, restored.field.inner.bars))
    assert not any(isinstance(k, tuple) and k and k[0] == 'frame'
                   for k in restored.field.ideas._row)
    json.dumps(alone['u3'])


def test_hostile_observer_grades_do_not_enter_candidate_view_or_teach(monkeypatch):
    mind, t = entity(inner_judge=True), task()
    seen = []
    def reads(views, concepts=None):
        seen.extend(views)
        return fake_reads(views)
    monkeypatch.setattr(mind.engine, '_u_reads', reads)
    def forbidden(*a, **k):
        raise AssertionError('Observer grade was consulted')
    monkeypatch.setattr(t, 'grade', forbidden)
    monkeypatch.setattr(t, 'teacher_check', forbidden)
    before = pickle.dumps(mind.field.inner)
    first = mind.engine._u_candidate_inputs(t, list(programs()))
    t._target, t.subject, t.name = 'HIDDEN', 'HOSTILE', 'PRIVATE'
    second = mind.engine._u_candidate_inputs(t, list(programs()))
    for a, b in zip(first, second):
        np.testing.assert_array_equal(a, b)
    assert seen[:3] == seen[3:] and 'HIDDEN' not in repr(seen)
    assert before == pickle.dumps(mind.field.inner)
    with pytest.raises(ValueError):
        mind.engine.course_verdict(t, programs()[2], True, 'test3')


def test_batched_hypothetical_reads_do_not_commit_native_or_holographic_memory():
    mind, t = entity(inner_judge=True), task()
    with mind.scope():
        view = TaskView.from_task(t)
        mind.memory.begin(view)
        before = factual(mind)
        xs = mind.engine._u_candidate_inputs(t, [programs()[0], programs()[2]])
        assert all(x.shape == (65,) and np.isfinite(x).all() for x in xs)
        assert_factual_same(before, mind)


def _order_as_given(task, order):
    return order


def _no_bind(task):
    return None


def _no_verdict(*args):
    return None


def test_u3_off_uses_exact_u2_faculties_steps_and_logical_records(monkeypatch):
    # Reference engine disables ONLY the optional U3 hooks, retaining the real
    # U2 memory adapters and observation hooks on both sides.
    first = entity(field_proposer=False)
    second = SeraU.loads(first.dumps())
    assert type(first.field.loop) is PH.LoopField
    assert type(first.field.methods) is PH.MethodField
    assert type(first.field.steps) is PH.StepField
    assert not hasattr(first.field, 'inner')
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 0.)
    # Module-level stand-ins: live() snapshots the entity for rollback, and pickle refuses local lambdas.
    monkeypatch.setattr(second.engine, '_u_order', _order_as_given)
    monkeypatch.setattr(second.engine, '_u_bind', _no_bind)
    monkeypatch.setattr(second.engine, '_u_verdict', _no_verdict)
    records = [m.live(task(), task_wall=math.inf, max_steps=2) for m in (first, second)]
    def logical(value):
        if isinstance(value, dict):
            return {k: logical(v) for k, v in value.items() if k not in (
                'wall', 'cpu', 'timing', 'thinking_wall', 'thinking_cpu', 'finish_cpu',
                'peak_mb', 'peak_mb_by', 'gain_rate', 'phases')}
        if isinstance(value, list):
            return [logical(v) for v in value]
        return value
    assert logical(records[0]) == logical(records[1])
    assert 'u3' not in records[0]
    assert set(records[0]['sera_u']['crutches']) == set(U1_CRUTCHES+U2_CRUTCHES)

def test_calibration_captures_the_pre_counterexample_field_read(monkeypatch):
    mind, t = entity(inner_judge=True), task()
    sizes = []
    def inputs(world, candidates):
        sizes.append(len(world.data))
        return [judge_x(float(len(world.data)-4))]
    monkeypatch.setattr(mind.engine, '_u_candidate_inputs', inputs)
    def refused(*a):
        t.data.append((10, 12))
        return False, 4, (10, 12)
    monkeypatch.setattr(t, 'verify', refused)
    st = dict(tested=set(), steps=0, proven=None)
    mind.engine._prove(t, programs()[0], mind.engine._concepts(), {}, st, lambda *a, **k: None)
    assert sizes == [4]
    weight = mind.field.inner.weights[ONE.kind_of(t)]
    assert weight[0] < 0 and np.count_nonzero(weight[1:]) == 0


def test_teacher_corrected_answer_trains_both_halves_and_persists(monkeypatch):
    mind, t = entity(inner_judge=True), task()
    views = []
    def read(batch, concepts=None):
        views.extend(batch)
        return fake_reads(batch)
    monkeypatch.setattr(mind.engine, '_u_reads', read)
    monkeypatch.setattr(ONE.Sera, 'course_verdict', lambda *a, **k: None)
    mind.engine.course_verdict(t, programs()[0], False, 'teacher')
    assert mind.field.inner.contrasts == 1
    rows = mind.field.inner.report()['calibration'][ONE.kind_of(t)]
    assert sum(row['n'] for row in rows) == 2
    assert views[0].examples == views[1].examples
    assert views[0].hypotheses != views[1].hypotheses and views[0].queries == views[1].queries
    monkeypatch.undo()                   # the engine's patched local reader cannot be pickled into a checkpoint
    restored = SeraU.loads(mind.dumps())
    assert restored.field.inner.report() == mind.field.inner.report()


def test_taught_next_step_is_evidence_only_and_learns_from_actual_outer_solution(monkeypatch):
    mind, t, reads, verdicts = prepare_roadmap(monkeypatch)
    # The literal worked values teach a candidate; they do not supply its code.
    t.worked = lambda x: (x+1, x+2)
    x, step, full = programs()
    calls = []
    def dream(view, *args):
        calls.append(view)
        return [x] if len(calls) == 1 else [LG.node('add', LG.node('var', payload='u_next'), LG.node('one'))]
    monkeypatch.setattr(mind.engine, '_dream_roadmap', dream)
    def candidates(ctx, inputs, probes, until):
        vals = [p['x']+1 for p in probes]
        return [(step, 'num', vals, [vals[j] for j in ctx['where']], (.5, .2, 1., 1., 1./3))]
    monkeypatch.setattr(mind.engine, '_step_candidates', candidates)
    st = dict(steps=0, teaching=True)
    mind.engine._step(t, mind.engine._concepts(), lambda *a, **k: None, (), st)
    assert np.linalg.norm(mind.field.steps.At) > 0
    assert mind.field.steps.tried == 0  # stub outer did not teach a fake solution
    # Exercise the actual verdict-to-step seam with a stubbed real verifier.
    monkeypatch.setattr(ONE.Sera, '_prove', lambda *a, **k: True)
    del mind.engine.__dict__['_prove']  # remove prepare_roadmap's per-instance stub
    mind.engine._prove(t, full, mind.engine._concepts(), {}, st, lambda *a, **k: None)
    assert mind.field.steps.tried == 1 and mind.field.steps.found == 1

def test_all_readouts_resume_their_next_thompson_draw_exactly():
    mind = entity(**{k: True for k in U3_CRUTCHES})
    bound = np.arange(192, dtype=float).reshape(3, 64)/192
    mind.field.loop.bind(bound)
    mind.field.methods.bind(bound)
    mind.field.steps.bind(bound)
    mind.field.loop.teach('k', {}, {}, {'ask', 'imagine'}, ['imagine'])
    mind.field.loop.learn('ask', mind.field.loop.features({}, {}, 'ask'), 3.)
    mind.field.loop.end_task('k')
    mind.field.methods.teach('k', ('dream',), {})
    mind.field.methods.learn('k', ('dream',), {}, 5.)
    mind.field.steps.teach((.1, .2, .3, 1., .5), 1.)
    mind.field.steps.learn((.1, .2, .3, 1., .5), 1.)
    restored = SeraU.loads(mind.dumps())
    assert restored.learning_hash() == mind.learning_hash()
    configs = [m.field.loop.choose('k', {}, {}, {'ask', 'imagine'}, np.random.default_rng(17))
               for m in (mind, restored)]
    assert configs[0] == configs[1]
    methods = [m.field.methods.choose('k', {'dream', 'compose'}, {}, np.random.default_rng(19))
               for m in (mind, restored)]
    assert methods[0] == methods[1]
    scores = [m.field.steps.score((.1, .2, .3, 1., .5), np.random.default_rng(23))
              for m in (mind, restored)]
    assert scores[0] == scores[1]


def test_no_proposer_cannot_emit_field_beam_dreams(monkeypatch):
    mind = entity(field_methods=True, field_roadmap=True, field_proposer=False)
    t = task()
    def forbidden(*a, **k):
        raise AssertionError('No-proposer control emitted a neural beam')
    monkeypatch.setattr(mind.proposer, 'beam', forbidden)
    assert mind.engine._dream_roadmap(TaskView.from_task(t), mind.engine._concepts(), None, math.inf) == []
    args = ('k', programs()[0], mind.engine._concepts(), {}, None,
            dict(moved=set()), [], {}, lambda *a, **k: None)
    assert mind.engine._move('dream', t, *args) == []

def test_imagined_sense_is_kept_only_for_its_outer_accepted_law(monkeypatch):
    mind = entity(field_methods=True)
    law = (('new-dimension', 'expr', LG.node('one')),)
    row = dict(name='new-dimension', uses=0, born='stub', at=0)
    world = SimpleNamespace(form='strengths')
    st = dict(u_sense_proposals={law: [row]})
    monkeypatch.setattr(ONE.Sera, '_prove', lambda *a, **k: False)
    assert not mind.engine._prove(world, law, {}, {}, st, lambda *a, **k: None)
    assert mind.field.senses == []
    monkeypatch.setattr(ONE.Sera, '_prove', lambda *a, **k: True)
    assert mind.engine._prove(world, law, {}, {}, st, lambda *a, **k: None)
    assert mind.field.senses == [row] and mind.engine._task_senses == ['new-dimension']

def test_layer_b_recall_drives_branches_with_one_field_knob_off(monkeypatch):
    mind, t = entity(field_methods=True), task()
    concepts = {3: (LG.node('add', LG.node('var', payload='_'), LG.node('one')), '_'),
                '_sig': {3: ('num', 'num')}}
    monkeypatch.setattr(ONE, 'ONE_FIELD', False)
    monkeypatch.setattr(mind.field, 'proven_ideas', lambda: {3})
    mind.engine.memory = SimpleNamespace(b=True)
    cues = []
    def evoked(tokens, keys):
        cues.extend(tokens)
        assert keys == [('concept', 3)]
        return [(('concept', 3), 1.)]
    monkeypatch.setattr(mind.field.ideas, 'evoked', evoked)
    before = factual(mind)
    got = mind.engine._move('recall', t, 'k', programs()[0], concepts, {}, None,
                            dict(moved=set()), [], {}, lambda *a, **k: None)
    assert got[0][0] == LG.node('c', LG.node('var', payload='x'), payload=3)
    assert 'role:pair' in cues and 'int:4' in cues
    assert_factual_same(before, mind)
