"""S22's nine Phase 3 regressions. Cheap witnesses plus the real combined judge/finalizer/writer path."""
import copy
import json
import math
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from sera import crutches as CR, lang as L, one as O, phi as P, tasks as T
from scripts import ab_compare as AB, sera_one as RUN, sera_steps_ab as STEPS
from tests.sera.test_honest_credit import CUBE, S, _live, stiff2  # noqa: F401

N = L.node
QUIET = lambda *a, **k: None  # noqa: E731
CTX = [0., 0., 0., 0., 0., 1., 1.]


def _words(text):
    return tuple(T.sym(word) for word in text.split())


@pytest.fixture
def on(monkeypatch):
    monkeypatch.setattr(O, 'ONE_FIELD', True)
    monkeypatch.setattr(P, 'FIELD_ECHO', True)
    monkeypatch.setattr(L, 'DEADLINE', [math.inf])


def _state():
    return dict(tested=set(), steps=1, proven=None, judge_short=0., judge_where=None, misfit=False, level=0,
                asked=0, explored=0, time={}, peak=[0.], peak_by={}, memory_stops=0, origins={}, footholds={})


def _rail():
    return SimpleNamespace(form='strengths', inputs={'s': 'num'}, out='num', throws=[], subject='physics',
                           name='fixture rail', words=[], context=lambda: CTX)


def _finish(s, task, st, law, choices=()):
    return s._finish(task, O.kind_of(task), CTX, s._concepts(), (), st, law, [law], {law: 0.}, {law: 0.},
                     {}, list(choices), [], [], False, 0., 0.)


@pytest.mark.parametrize('physics', [False, True])
def test_identity_survives_invention_refutation_and_saved_field(on, tmp_path, physics):
    s = O.Sera(1, P.Field(1))
    task = _rail() if physics else T.number_task('identity', lambda n: n, 1, 4)
    var = 's' if physics else next(iter(task.inputs))
    raw = (('position', 'expr', S),) if physics else N('var', payload=var)
    old = s._idea_key(task, raw)
    cue = ('sense', 'strengths', 0, 0.) if physics else 12345
    s._ideas().bind(cue, old, 1.)
    vector = s._ideas()._E[s._ideas()._row[old]].copy()
    c = s.field.invent(N('var', payload='_'), ('num', 'num'), task.subject, 'later', ())
    d = s.field.invent(N('var', payload='_'), ('num', 'num'), task.subject, 'duplicate', ())
    explicit = (('position', 'concept', d['id']),) if physics else N('c', N('var', payload=var), payload=d['id'])
    new = s._idea_key(task, raw)
    assert new == s._idea_key(task, explicit)
    assert new == (('idea', (('position', 'concept', c['id']),)) if physics else ('concept', c['id']))
    assert np.array_equal(vector, s._ideas()._E[s._ideas()._row[new]])
    assert s._ideas().bound(cue, new) == pytest.approx(1., abs=1e-5)
    s._ideas().bind(cue, new, -O.REFUTE_ECHO)
    assert s._ideas().bound(cue, old) == pytest.approx(1. - O.REFUTE_ECHO, abs=1e-5)
    s.field.save(tmp_path / 'field.pkl')
    loaded = O.Sera(1, P.Field.load(tmp_path / 'field.pkl'))
    assert loaded._idea_key(task, explicit) == new
    assert loaded._ideas().bound(cue, old) == pytest.approx(1. - O.REFUTE_ECHO, abs=1e-5)
    assert old not in loaded._ideas().identities(('concept', 'idea'))


def test_old_checkpoint_with_multiple_vectors_migrates_them(on, tmp_path):
    field = P.Field(1)
    c = field.invent(N('var', payload='_'), ('num', 'num'), 'physics', 'first', ())
    d = field.invent(N('var', payload='_'), ('num', 'num'), 'physics', 'second', ())
    raw = ('idea', (('position', 'expr', S),))
    first = ('idea', (('position', 'concept', c['id']),))
    second = ('idea', (('position', 'concept', d['id']),))
    field.ideas = P.Ideas()
    cue = ('sense', 'strengths', 0, 0.)
    for key, amount in ((raw, 1.), (first, .5), (second, .25)):
        field.ideas.bind(cue, key, amount)
    field.save(tmp_path / 'old.pkl')                     # pre-redirect state, as a Phase 3 checkpoint stored it
    s = O.Sera(1, P.Field.load(tmp_path / 'old.pkl'))
    assert s._idea_key(_rail(), raw[1]) == first
    assert s._ideas().bound(cue, first) == pytest.approx(1.75, abs=1e-5)
    assert s._ideas().identities(('idea',)) == [first]
    s._lay_in_world(_rail(), CTX, {'refuters': {('misfit', raw[1])}}, [], {}, None, [])
    assert s._ideas().bound(cue, raw) == pytest.approx(1.75 - O.REFUTE_ECHO, abs=1e-5)
    s.field.save(tmp_path / 'new.pkl')
    again = O.Sera(1, P.Field.load(tmp_path / 'new.pkl'))
    assert again._ideas().bound(cue, second) == pytest.approx(1.75 - O.REFUTE_ECHO, abs=1e-5)


def test_future_duplicate_bind_and_query_use_same_vector(on):
    s = O.Sera(1, P.Field(1))
    task = T.number_task('identity', lambda n: n, 1, 4)
    a = s.field.invent(N('var', payload='_'), ('num', 'num'), 'math', 'a', ())
    b = s.field.invent(N('var', payload='_'), ('num', 'num'), 'math', 'b', ())
    canonical = s._idea_key(task, N('var', payload=task.var))
    alias = ('concept', b['id'])
    s._ideas().bind('cue', alias, 1.)
    assert canonical == ('concept', a['id'])
    assert s._ideas().bound('cue', canonical) == s._ideas().bound('cue', alias) == pytest.approx(1., abs=1e-5)
    assert s._ideas().identities(('concept',)) == [canonical]
    raw_a = N('add', N('c', N('var', payload=task.var), payload=a['id']), N('one'))
    raw_b = N('add', N('c', N('var', payload=task.var), payload=b['id']), N('one'))
    assert s._idea_key(task, raw_a) == s._idea_key(task, raw_b)


@pytest.mark.parametrize('expr', [N('mul', N('lit', payload=3), S), N('add', N('one'), CUBE)])
def test_real_prove_finish_writer_does_not_credit_curve_as_source(on, stiff2, expr):
    s = O.Sera(1, P.Field(1))
    law = (('position', 'expr', expr),)
    # Inspect exact writes: cue projections include the accepted curve's ordinary holographic crosstalk.
    writes = []
    bind = s._ideas().bind

    def watch(thing, key, amount):
        writes.append((thing, key, amount))
        bind(thing, key, amount)

    s._ideas().bind = watch
    rec = _live(s, stiff2, law)
    assert rec['proven'] and rec['attributed'] and rec['certified'][0]['as'] == 'curve'
    assert writes and all(key != s._idea_key(stiff2, law) for _, key, _ in writes)
    assert any(amount == 1. for _, _, amount in writes)


def test_unassignable_proof_cannot_leak_source_support(on, stiff2, monkeypatch):
    s = O.Sera(1, P.Field(1))
    law = (('position', 'expr', CUBE),)
    writes = Mock()
    monkeypatch.setattr(s._ideas(), 'bind', writes)

    def corrupt_attribution():
        monkeypatch.setattr(s, '_certified', lambda *a, **k: (None, []))

    rec = _live(s, stiff2, law, after_prove=corrupt_attribution)
    assert rec['proven'] and not rec['attributed'] and not rec['invented']
    writes.assert_not_called()


def test_support_keeps_representation_and_snapshot_and_expires_on_new_throw(on, monkeypatch):
    s, task, st = O.Sera(1, P.Field(1)), _rail(), _state()
    law = (('position', 'expr', S),)
    ramp = ('ramp', 'dim:x@4', 9)
    family = (ramp,)
    task.throws = [1]
    monkeypatch.setattr(O.truth, 'digest', lambda throws: O._digest(tuple(throws)))
    task.claim_terms = lambda *a, **k: (family, ((ramp, 'formula'),))
    task.verify = lambda f: (False, SimpleNamespace(band=2., eps=1.), 'band too wide')
    monkeypatch.setattr(O.truth, 'functional_prior', lambda f: 0.)
    assert not s._prove(task, law, {}, (), st, QUIET)
    assert st['support'] == {(law, s._support_snapshot(task), family): law}
    bind = Mock()
    monkeypatch.setattr(s._ideas(), 'bind', bind)
    s._lay_in_world(task, CTX, st, [law], {law: 0.}, None, [])
    assert bind.call_count == len(s._things(task, CTX))
    bind.reset_mock()
    task.throws.append(2)                               # exposing push, cap before a second proof
    s._lay_in_world(task, CTX, st, [law], {law: 0.}, None, [])
    bind.assert_not_called()
    task.throws[:] = [3]                                # same count, replaced readings also do not support it
    s._lay_in_world(task, CTX, st, [law], {law: 0.}, None, [])
    bind.assert_not_called()


def test_unscoped_adequate_marker_does_not_support_formula(on, monkeypatch):
    s, task = O.Sera(1, P.Field(1)), _rail()
    law = (('position', 'expr', S),)
    bind = Mock()
    monkeypatch.setattr(s._ideas(), 'bind', bind)
    s._lay_in_world(task, CTX, {'adequate': {law}}, [law], {law: 0.}, None, [])
    bind.assert_not_called()


@pytest.mark.parametrize('one_field', [False, True])
@pytest.mark.parametrize('echo', [False, True])
def test_echo_switch_controls_both_automatic_paths(monkeypatch, one_field, echo):
    monkeypatch.setattr(O, 'ONE_FIELD', one_field)
    monkeypatch.setattr(P, 'FIELD_ECHO', echo)
    monkeypatch.setattr(L, 'DEADLINE', [math.inf])
    s = O.Sera(1, P.Field(1))
    task = T.lesson_where(1)
    var = next(iter(task.inputs))
    for x, _ in task.data:
        for sentence in task.sentences(x):
            s._ideas().read(sentence, task.name)
    c = s.field.invent(N('var', payload='_'), (task.inputs[var], task.out), 'language', 'identity', ())
    law = N('c', N('var', payload=var), payload=c['id'])
    things = s._things(task, task.context())
    for thing in things:
        s._ideas().bind(thing, ('concept', c['id']), 1.)
    extra = {}
    s._evoke(task, s._concepts(), extra, QUIET, (), task.context())
    assert bool(extra) == echo
    bind = Mock()
    monkeypatch.setattr(s._ideas(), 'bind', bind)
    if one_field:
        s._lay_in_world(task, task.context(), {'refuters': set()}, [], {}, {('concept', c['id']): 1.}, [])
    else:
        s._bind_proven(task, law, {})
    assert bool(bind.call_count) == echo


def test_steps_switches_and_settings_are_effective(monkeypatch):
    monkeypatch.setattr(O, 'BACK_ON', False)
    monkeypatch.setattr(P, 'FIELD_ECHO', True)
    monkeypatch.setenv('SERA_KNOBS', 'BACK_ON=0')
    STEPS.apply_switches(SimpleNamespace(no_back=False, no_echo=False))
    assert not O.BACK_ON and CR.settings()['effective']['BACK_ON'] is False
    STEPS.apply_switches(SimpleNamespace(no_back=True, no_echo=True))
    assert not P.FIELD_ECHO and CR.settings()['field_echo'] is False


@pytest.mark.parametrize('value', ['BACK_ON=maybe', 'BACK_ON=', 'PART_SIZES=35', 'TOP=1.5', 'TOP=-1',
                                   'TALK_RATE=nan', 'TALK_RATE=inf', 'BACK_ON', 'NOPE=1'])
def test_malformed_knobs_refused_atomically(monkeypatch, value):
    knobs = dict(BACK_ON=True, PART_SIZES=(3, 5), TOP=4, TALK_RATE=.25)
    before = dict(knobs)
    monkeypatch.setenv('SERA_KNOBS', 'TOP=2,' + value)
    with pytest.raises(ValueError):
        CR.set_knobs(knobs)
    assert knobs == before


def test_live_uses_current_max_steps(monkeypatch):
    monkeypatch.setattr(O, 'ONE_FIELD', False)
    monkeypatch.setattr(O, 'MAX_STEPS', 0)
    monkeypatch.setattr(O, 'MAX_WALL', math.inf)
    s = O.Sera(1, P.Field(1))
    task = T.number_task('one more', lambda n: n + 1, 1, 4)
    law = N('add', N('var', payload=task.var), N('one'))
    monkeypatch.setattr(s, '_generate', lambda *a, **k: [law])
    rec = s.live(task)                                  # frozen 1,000,000 default would take a step
    assert rec['steps'] == 0 and not rec['choices']
    assert CR.settings()['effective']['MAX_STEPS'] == 0


def test_finish_time_and_learning_rate_include_writer_cost(on, monkeypatch):
    clock = [10.]
    monkeypatch.setattr(O.time, 'time', lambda: clock[0])
    monkeypatch.setattr(O.time, 'process_time', lambda: clock[0])
    s, task = O.Sera(1, P.Field(1)), _rail()

    def costly_writer(*args):
        clock[0] += 5.

    monkeypatch.setattr(s, '_lay_in_world', costly_writer)
    rec = _finish(s, task, _state(), None, [dict(gain=30., config=['ask'])])
    assert rec['thinking_wall'] == rec['thinking_cpu'] == 10.
    assert rec['wall'] == rec['cpu'] == 15.
    assert rec['timing']['finish'] == rec['finish_cpu'] == 5.
    assert s.field.rates[-1] == 2.
    assert s.field.log[-1]['wall'] == 15.
    assert rec['gain_rate'] == s._world_rate() == 2.
    monkeypatch.setattr(O, 'ONE_FIELD', False)
    assert s._world_rate() == 3.                         # the explicit off-arm policy-preservation requirement


def _talks(path, rows):
    path.mkdir(exist_ok=True)
    (path / 'CONVERSE.json').write_text(json.dumps({key: {'rows': copy.deepcopy(rows)}
                                                   for key in sorted(AB.TALK_ARMS)}), encoding='utf-8')


def test_observer_digest_distinguishes_story_target_and_absence(on, monkeypatch):
    s = O.Sera(1, P.Field(1))
    monkeypatch.setattr(s, 'reply', lambda *a: (None, None, []))
    q = _words('where is mary')
    kitchen, garden = _words('mary went to kitchen'), _words('mary went to garden')

    def row(story, target, kind='where'):
        task = SimpleNamespace(name='talk', items=[((q, story), target, kind)],
                               sentences=lambda x: x[1:], perceive=lambda x: x)
        return s.converse(task, teaching=False)['rows'][0]

    a = row(kitchen, _words('kitchen'))
    assert a['observer_digest'] == row(kitchen, _words('kitchen'))['observer_digest']
    assert len({a['observer_digest'], row(garden, _words('garden'))['observer_digest'],
                row(kitchen, _words('garden'))['observer_digest'], row(kitchen, None, 'absent')['observer_digest']}) == 4


def test_talk_comparison_refuses_missing_arms_rows_and_b1_digests(tmp_path):
    off, on = tmp_path / 'off', tmp_path / 'on'
    row = dict(question='where is mary', observer_digest='kitchen-story-and-target', kind='where', right=True, said='kitchen')
    _talks(off, [row])
    _talks(on, [row])
    assert AB.gate({'talks': AB.talks(off, on)})['verdict'] == 'PASS'
    changed = dict(row, observer_digest='garden-story-and-target')
    _talks(on, [changed])
    assert all('refused' in result for result in AB.talks(off, on).values())
    assert AB.gate({'talks': AB.talks(off, on)})['verdict'] == 'FAIL'
    for changed in (dict(row, kind='absent'), dict(row, question='where is john')):
        _talks(on, [changed])
        assert AB.gate({'talks': AB.talks(off, on)})['verdict'] == 'FAIL'
    _talks(on, [])
    assert AB.gate({'talks': AB.talks(off, on)})['verdict'] == 'FAIL'
    changed = dict(row, right=False, said=None)
    _talks(on, [changed])
    assert all(result['lost'] == [0] for result in AB.talks(off, on).values())
    changed.pop('observer_digest')
    _talks(on, [changed])
    assert all('missing observer digests' in result['refused'] for result in AB.talks(off, on).values())
    data = json.loads((on / 'CONVERSE.json').read_text())
    data.pop('taught: the fresh talk')
    (on / 'CONVERSE.json').write_text(json.dumps(data))
    assert 'refused' in AB.talks(off, on)
    (on / 'CONVERSE.json').write_text('{}')
    assert AB.gate({'talks': AB.talks(off, on)})['verdict'] == 'FAIL'


def test_b1_without_talk_files_refuses_explicitly(tmp_path):
    missing = AB.talks(tmp_path / 'b1-off', tmp_path / 'b1-on')
    assert 'observer digests' in missing['refused']
    assert AB.gate({'talks': missing})['verdict'] == 'FAIL'


def _unit(stage, name, proven=True, parts=()):
    return dict(task=name, stage=stage, subject='physics', form='strengths', proven=proven,
                verdict='proven right' if proven else 'not proven', certified=[{'as': p} for p in parts])


def test_physics_counts_empty_laws_and_separates_stages_and_saved_units(tmp_path):
    units = [_unit('teach', 'empty'), _unit('alone', 'main', parts=('formula', 'curve')),
             _unit('twin', 'twin', parts=('drawing',)),
             dict(_unit('teach', 'not physics', parts=('curve',)), subject='language', form='exact')]
    # Reused JSON units without the newly added form still use their saved answer kind.
    units[0]['kind'] = 'strengths:s:num->num'
    units[0].pop('form')
    result = RUN.save_physics(tmp_path, json.loads(json.dumps(units)), {'effective': {'ONE_FIELD': True}})
    assert result['groups']['teach']['worlds'] == 1
    assert result['groups']['teach']['curves_proven'] == 0
    assert result['groups']['alone'] == dict(worlds=1, curves_proven=1, drawings_proven=0, formulas_proven=1)
    assert result['groups']['twin']['worlds'] == result['groups']['twin']['drawings_proven'] == 1
    assert json.loads((tmp_path / 'PHYSICS.json').read_text()) == result


def test_physics_comparison_reports_world_losses_and_gate(tmp_path):
    off, on = tmp_path / 'off', tmp_path / 'on'
    off.mkdir()
    on.mkdir()
    units = [_unit('teach', 'empty'), _unit('alone', 'main', parts=('formula',))]
    RUN.save_physics(off, units, {})
    RUN.save_physics(on, [units[0], _unit('alone', 'main', proven=False)], {})
    result = AB.physics(off, on)
    assert result['alone']['lost'] == ['main'] and result['alone']['delta']['worlds'] == -1
    assert result['alone']['delta']['formulas_proven'] == -1
    assert AB.gate({'physics': result})['verdict'] == 'FAIL'
    RUN.save_physics(on, units, {})
    assert AB.gate({'physics': AB.physics(off, on)})['verdict'] == 'PASS'
    RUN.save_physics(on, units[:1], {})
    assert 'refused' in AB.physics(off, on)


def test_loaded_trigger_checks_expired_deadline_before_decoding(on, tmp_path, monkeypatch):
    field = P.Field(1)
    field.ideas = P.Ideas()
    for i in range(20):
        field.ideas.bind(('sense', 'strengths', 0, 0.), ('idea', (('position', 'curve', 9 + i),)), 1.)
    field.save(tmp_path / 'field.pkl')
    s = O.Sera(1, P.Field.load(tmp_path / 'field.pkl'))
    decoder = Mock(side_effect=AssertionError('expired trigger decoded a candidate'))
    monkeypatch.setattr(s, '_from_key', decoder)
    monkeypatch.setattr(L, 'DEADLINE', [O.time.time() - 1.])
    extra = {}
    s._ring_first(_rail(), s._concepts(), extra, QUIET, (), CTX)
    decoder.assert_not_called()
    assert extra == {}


def test_chunked_projection_matches_full_projection_and_discards_cutoff(on, monkeypatch):
    ideas = P.Ideas()
    cue = ('sense', 'strengths', 0, 0.)
    keys = [('idea', (('position', 'curve', i),)) for i in range(700)]
    for key in keys:
        ideas._at(key)
    ideas.bind(cue, keys[-1], 10.)
    ideas.perceive_world([cue])
    full = ideas.evoked([cue], keys)
    assert full and full[0][0] == keys[-1]
    chunked = ideas.evoked([cue], keys, deadline=math.inf, chunk_size=16)
    assert [k for k, _ in full] == [k for k, _ in chunked]
    assert [v for _, v in full] == pytest.approx([v for _, v in chunked], abs=1e-4)
    calls = [0]

    def advancing_clock():
        calls[0] += 1
        return float(calls[0])

    monkeypatch.setattr(P.time, 'time', advancing_clock)
    assert ideas.evoked([cue], keys, deadline=3., chunk_size=16) == []
    assert calls[0] == 3                            # stops during projection, not after the full vocabulary


def test_trigger_discards_partial_selection_when_validation_expires(on, monkeypatch):
    s, task = O.Sera(1, P.Field(1)), _rail()
    law = (('position', 'curve', 9),)
    key = s._idea_key(task, law)
    s._ideas().bind(s._things(task, CTX)[0], key, 1.)
    s._ideas().perceive_world(s._things(task, CTX))
    clock = [0.]
    monkeypatch.setattr(O.time, 'time', lambda: clock[0])
    monkeypatch.setattr(L, 'DEADLINE', [1.])
    task.claim_terms = lambda *a, **k: ((('cell', 'position', 9),), ())
    original = s._from_key
    validated = []

    def expires(*args, **kwargs):
        if kwargs.get('judge', True):
            validated.append(True)
            clock[0] = 2.
        return original(*args, **kwargs)

    monkeypatch.setattr(s, '_from_key', expires)
    extra = {}
    s._ring_first(task, s._concepts(), extra, QUIET, (), CTX)
    assert validated and extra == {}
