"""the reviewer's S06 review (2026-09-30), its confirmations turned into checks of the repairs: a refusal is not a refutation,
a re-proof is no new evidence, the echo credits only what led to a result, a teacher's word decides what a taught
proof keeps (the hidden grade never reaches an alone SERA), and the talk says only words, from proven ideas."""
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))

from sera import lang as L, one as O, phi as P, tasks as T  # noqa: E402

N = L.node


def _state():
    return dict(tested=set(), steps=1, proven=None, judge_short=0., judge_where=None, misfit=False)


def test_only_a_counterexample_refutes():
    s = O.Sera(1, P.Field(1))
    leader = (('position', 'shape', 'fixture'),)
    judge = Mock()                                   # a claim the judge cannot take: no judge, nothing refuted
    t = SimpleNamespace(form='strengths', throws=[None], claim_terms=lambda *a, **k: None, verify=judge)
    st = _state()
    assert s._prove(t, leader, {}, (), st, lambda *a, **k: None) is False
    judge.assert_not_called()
    assert 'counter' not in st
    fam = (('position', 'straight'),)                # a band not yet narrow enough: not sure is not wrong
    t.claim_terms = lambda *a, **k: (fam, ((fam[0], 'curve'),))
    t.verify = lambda family: (False, SimpleNamespace(band=2., eps=1.), 'something else could be as large as 2 > 1')
    st = _state()
    with patch.object(O.truth, 'functional_prior', return_value=0.):
        assert s._prove(t, leader, {}, (), st, lambda *a, **k: None) is False
    assert st['judge_short'] > 0 and not st['misfit'] and 'counter' not in st
    t.verify = lambda family: (False, SimpleNamespace(band=2., eps=1.), 'something else is here')
    st = _state()                                    # a force its law misses: that refutes it
    with patch.object(O.truth, 'functional_prior', return_value=0.):
        assert s._prove(t, leader, {}, (), st, lambda *a, **k: None) is False
    assert st['misfit'] and st['counter'] == ('misfit', leader)
    t = T.Exact('code', 's06 exact witness', lambda x: x[0], {'l': 'list'}, 'num', [(1, 2)], [(5, 7)], lambda r: (5, 7))
    st = _state()                                    # an input it gets wrong: that refutes it
    assert s._prove(t, N('one'), {}, (), st, lambda *a, **k: None) is False
    assert st['counter'][0] == 'input'


def _run(configs, generated):
    s = O.Sera(1, P.Field(1))
    t = T.number_task('s06 gate', lambda x: 1, 1, 4)
    laws = iter(generated)
    echoes, updates, offered = [], [], []
    original_echo, original_learn = s.field.echo, s.field.loop.learn

    def echo(signal):
        echoes.append((signal, [part[:2] for part, w in s.field.traces]))
        return original_echo(signal)

    def learn(fac, x, y, weight=1.):
        updates.append((fac, y, weight))
        return original_learn(fac, x, y, weight)

    def prove(task, law, cs, lib, st, speak):
        st['tested'].add((law, len(task.data)))
        st['proven'] = dict(law=law, key=(law, len(task.data)), audit=1)
        return True

    it = iter(configs)

    def choose(kind, moment, est, available, rng):
        offered.append(set(available))
        return next(it), {f: (1., 1.) for f in ('prove', 'grow', 'ask', 'leave')}

    candidate = dict(action=('ask', 9), info=1., novel=0., predicted=1)
    with patch.object(s, '_generate', side_effect=lambda *a: [next(laws)]), \
            patch.object(s, '_moves_available', return_value=set()), \
            patch.object(t, 'actions', return_value=[candidate]), \
            patch.object(s, '_prove', side_effect=prove), \
            patch.object(s, '_doubt_after', return_value=0.), \
            patch.object(s, '_cost', return_value=1.), patch.object(s, '_spend'), \
            patch.object(s.field.loop, 'choose', side_effect=choose), \
            patch.object(s.field.loop, 'learn', side_effect=learn), \
            patch.object(s.field, 'echo', side_effect=echo), \
            patch.object(s, '_finish', side_effect=lambda *a: dict(st=a[5], choices=a[11])):
        r = s.live(t, max_steps=10)
    return r, echoes, updates, offered


def test_a_reproof_is_no_new_evidence_and_what_came_after_the_proof_is_not_credited():
    a = N('one')
    r, echoes, updates, offered = _run([['prove'], ['grow', 'ask'], ['prove'], ['leave']], [a, a])
    assert [sig for sig, _ in echoes] == [1.]
    assert sum(f == 'prove' and y == P.V_DONE for f, y, w in updates) == 1     # one proof, one reward
    assert 'prove' not in offered[2]                  # what it proved needs no proof again, even with a new example
    assert echoes[0][1] == []                         # the proving has its own return: not traced twice
    r, echoes, updates, offered = _run([['prove', 'grow'], ['leave']], [a, a])
    assert echoes[0][1] == []                         # the grow after the proof did not lead to it
    r, echoes, updates, offered = _run([['grow'], ['prove'], ['leave']], [a, a])
    assert echoes[0][1] == [('loop', 'grow')]         # the grow before it did


def test_the_echo_is_sure_as_its_signal_in_the_units_of_returns():
    x = np.zeros(P.Field(1).loop.d)
    x[0] = 1.
    up, down = P.Field(1), P.Field(1)
    for field, signal in ((up, 1.), (down, -.25)):
        field.loop.learn('prove', x, 2.)
        A0 = field.loop.task['prove'][0].copy()
        field.trace(('loop', 'prove', x, 4.0))
        field.echo(signal)
        field.dA = field.loop.task['prove'][0] - A0
    assert np.allclose(down.dA, 0.25 * up.dA)        # a softer echo is less sure evidence
    b = up.loop.task['prove'][1]
    assert np.allclose(b, (2. + P.V_DONE / 4.0) * x / up.loop.noise ** 2)    # a proof's worth per second (cost 4)
    A0 = down.loop.task['prove'][0].copy()
    down.trace(('loop', 'prove', x, 1.0))
    assert down.echo(0.) == 0 and np.array_equal(down.loop.task['prove'][0], A0)   # no result: nothing changes


def _finish(teaching):
    s = O.Sera(1, P.Field(1))
    t = T.number_task('s06 grade failure', lambda x: x + 1, 1, 4, words=['increment'])
    law = L.node('add', L.node('var', payload='n'), L.node('one'))
    st = dict(proven=dict(law=law, audit=100), steps=0, level=0, asked=0, explored=0, time={}, peak=[0], peak_by={},
              memory_stops=0, origins={}, footholds={})
    with patch.object(t, 'grade', return_value={'verdict': 'SURE AND WRONG'}), \
            patch.object(s, '_register'), patch.object(s, '_inner_ability', return_value=[]), \
            patch.object(s, '_bind_proven') as bind:
        r = s._finish(t, O.kind_of(t), t.context(), s._concepts(), (), st, law, [law], {law: 0.}, {law: 0.}, {}, [],
                      [], [], teaching, time.time(), time.process_time())
    return s, r, bind


def test_a_taught_proof_the_teacher_says_is_wrong_is_not_kept():
    s, r, bind = _finish(teaching=True)
    assert r['teacher_says'] == 'wrong' and not r['invented'] and not s.field.concepts
    assert not s.field.lexicon.heard.get('increment')
    bind.assert_not_called()


def test_alone_its_own_proof_is_its_belief_and_the_hidden_grade_does_not_reach_it():
    s, r, bind = _finish(teaching=False)
    assert 'teacher_says' not in r and r['invented'] and s.field.concepts
    bind.assert_called_once()


def test_a_wished_ability_is_tentative_until_a_proof_uses_it():
    f = P.Field(1)
    made = f.invent(N('one'), ('list(list)', 'num'), 'language', 'lesson', [])
    wished = f.invent(N('zero'), ('list(list)', 'num'), 'language', 'lesson (wished)', [], extra=dict(built='x'))
    assert f.proven_ideas() == {made['id']}
    f.audited_by(wished['id'], 'another lesson')
    assert f.proven_ideas() == {made['id'], wished['id']}
    g = P.Field(1)                                   # a Field saved before audited_by: a proven idea made of it
    w = g.invent(N('zero'), ('list', 'num'), 'language', 'last 1 (wished)', [], extra=dict(built='x'))
    u = g.invent(N('c', N('var', payload='_'), payload=w['id']), ('list', 'num'), 'language', 'last 1',
                 [('concept', w['id'])])
    assert g.proven_ideas() == {u['id'], w['id']}


def test_a_refuted_idea_spends_the_memories_it_rested_on_without_weakening_them():
    s = O.Sera(1, P.Field(1))
    i = s.field.ideas

    def sy(ws):
        return tuple(T.sym(w) for w in ws.split())
    bad = sy('mary did not visit the kitchen')
    cue = T.sym('mary')
    i.read(bad)
    i.came([cue], [bad])
    t = SimpleNamespace(data=[((sy('where is mary'),), T.sym('kitchen'))], perceive=lambda x: x)
    before = i._M[i._row[cue]].copy()
    s._echo(t, -.25, lambda *a, **k: None)
    assert bad not in getattr(i, '_came', {}) and np.array_equal(i._M[i._row[cue]], before)
    s._echo(t, 1., lambda *a, **k: None)             # a later proof does not credit what it no longer rests on
    assert np.array_equal(i._M[i._row[cue]], before)


def test_the_talk_says_only_words_from_proven_ideas_and_holds_what_its_language_can():
    import sera_talk as ST

    def emit(body, sig, told=(), born='s06'):
        """(its words or None, the idea's word or None): the idea rings for the question when it may answer at all."""
        f = P.Field(1)
        s = O.Sera(1, f)
        c = f.invent(body, sig, 'fixture', born, [])

        def evoked(things, keys):
            return [(k, 1.0) for k in keys if k == ('concept', c['id'])]
        with patch.object(f.ideas, 'evoked', side_effect=evoked):
            said, idea, rang, came = ST.answer(s, list(told), (T.sym('s06_cue'),))
        return said, idea
    assert emit(N('lit', payload=2.5), ('list(list)', 'num'))[0] is None           # a number is not a word
    assert emit(N('lit', payload=2), ('list(list)', 'num'))[0] is None
    assert emit(N('one'), ('real', 'num')) == (None, None)                          # not an idea of a situation
    assert emit(N('lit', payload=T.sym('mary')), ('list(list)', 'num'))[0] == 'mary'
    assert emit(N('lit', payload=T.sym('mary')), ('list(list)', 'num'), born='s06 (wished)') == (None, None)
    g = N('var', payload='_')
    story = [tuple(T.sym(w) for w in 'mary went to the kitchen'.split())] * (L.MAX_LEN + 5)
    got = emit(N('head', N('head', g)), ('list(list)', 'num'), told=story)         # a long talk still fits in
    assert got[0] == 's06_cue'                                                      # what its language holds
