"""One Field, parts 2 and 4 (plan 3.4; review 12 and its review's blockers): with ONE_FIELD, what a world proved and
believed is laid into its situation's things and rings back by itself; no possibilities store, no 'recall' move;
the talk's reliability is held in the Field."""
import math

import pytest

from sera import crutches as CR, lang as L, one as O, phi as P, tasks as T

N = L.node
QUIET = lambda *a, **k: None  # noqa: E731


@pytest.fixture
def one_field(monkeypatch):
    monkeypatch.setattr(O, 'ONE_FIELD', True)


def _rail(i=0):
    w, signs = T.rail_world(3, 80301 + i, (('position', 'cubic'),), 1)
    return T.Rail(w, f'rail {i}', (), signs)


def test_cues_are_the_perceived_context_in_coarse_units():
    cues = O.Sera._cues([-0.1, math.nan, 0.26, 0.9, -2.4, 3.0, 0.01])
    assert cues == [('sense', 'strengths', 0, 0.0), ('sense', 'strengths', 2, 0.5), ('sense', 'strengths', 3, 1.0),
                    ('sense', 'strengths', 4, -2.0), ('sense', 'strengths', 5, 2.0), ('sense', 'strengths', 6, -3.0)]
    assert repr(cues[0][3]) == '0.0'                    # -0.0 is 0.0: one identity
    assert O.Sera._cues(None) == []


def test_a_newborn_rail_rings_what_a_world_like_it_laid_in(one_field):
    """S12 F1: a language-free newborn - no sentence read - still hears its rail cues."""
    s = O.Sera(1, P.Field(1))
    task = _rail()
    ctx = task.context()
    law = (('position', 'curve', 33),)
    s._lay_in_world(task, ctx, dict(refuters=set()), [law], {law: 0.0}, {s._idea_key(task, law): 1.0}, [])
    ideas = s._ideas()
    assert ideas.read_n == 0 and ideas.worlds_n == 1
    extra = {}
    s._ring_first(task, s._concepts(), extra, QUIET, (), ctx)
    assert extra == {law: ('rang', ('idea', law))}


def test_refutation_proof_and_belief_are_laid_in_once_each(one_field):
    """S12 F2 and F5: the laws inside counterexamples -REFUTE_ECHO once; a proof +1 once (not +1+p); tentative
    beliefs together at most TENTATIVE_MOST; a judge not yet sure refutes nothing."""
    s = O.Sera(1, P.Field(1))
    task = _rail()
    ctx = task.context()
    a, b, c, d = ((('position', 'curve', 9),), (('speed', 'curve', 9),), (('time', 'curve', 9),),
                  (('position', 'curve', 17),))
    st = dict(refuters={('input', a, 'x1'), ('misfit', a), ('teacher', a, 4)}, adequate={a, b, c, d})
    phi = {a: math.log(0.9), b: math.log(0.6), c: math.log(0.6), d: math.log(0.6)}
    s._lay_in_world(task, ctx, st, [a, b, c, d], phi, {s._idea_key(task, b): 1.0}, [])
    cue = s._things(task, ctx)[0]
    got = {h: s._ideas().bound(cue, s._idea_key(task, h)) for h in (a, b, c, d)}
    assert got[a] == pytest.approx(-O.REFUTE_ECHO, abs=0.06)
    assert got[b] == pytest.approx(1.0, abs=0.06)
    assert got[c] == pytest.approx(0.5, abs=0.06) and got[d] == pytest.approx(0.5, abs=0.06)   # 1.2 > 1: halved
    s2 = O.Sera(1, P.Field(1))
    phi = {h: math.log(0.6) for h in (b, c, d)}
    s2._lay_in_world(task, ctx, dict(refuters=set(), adequate={b, c, d}), [b, c, d], phi, None, [])
    assert sum(s2._ideas().bound(cue, s2._idea_key(task, h)) for h in (b, c, d)) == pytest.approx(1.0, abs=0.1)
    s3 = O.Sera(1, P.Field(1))                         # refused for a band not yet tight: no counterexample
    s3._lay_in_world(task, ctx, dict(refuters=set(), adequate={a}), [a], {a: math.log(0.9)}, None, [])
    assert s3._ideas().bound(cue, s3._idea_key(task, a)) > 0
    s4 = O.Sera(1, P.Field(1))                         # S15 F2: never found adequate - no belief laid in
    s4._lay_in_world(task, ctx, dict(refuters=set()), [a], {a: 0.0}, None, [])
    assert abs(s4._ideas().bound(cue, s4._idea_key(task, a))) < 0.05


def test_eligibility_comes_before_loudness(one_field):
    """S12 F6: three loud concepts of the wrong type do not hide a fitting fourth."""
    s = O.Sera(1, P.Field(1))
    task = T.lesson_where(1)
    var = next(iter(task.inputs))
    ideas = s._ideas()
    for x, _ in task.data:
        for sent in task.sentences(x):
            ideas.read(sent, task.name)
    wrong = [s.field.invent(N('var', payload='_'), ('num', 'num'), 'math', 'w', ()) for _ in range(3)]
    right = s.field.invent(N('var', payload='_'), (task.inputs[var], task.out), 'language', 'r', ())
    for t in s._situation_things(task):
        for c in wrong:
            ideas.bind(t, ('concept', c['id']), 3.0)
        ideas.bind(t, ('concept', right['id']), 1.0)
    extra = {}
    s._ring_first(task, s._concepts(), extra, QUIET, (), None)
    assert list(extra) == [N('c', N('var', payload=var), payload=right['id'])]


def test_the_frame_holds_its_reliability_across_a_reload(one_field, monkeypatch, tmp_path):
    """S12 F3: 'what is' and 'what is ladder' are different things; the record survives saving; a frameless question
    uses only its talk's tally; with the crutch off, the tally as before."""
    s = O.Sera(1, P.Field(1))
    ideas = s._ideas()
    f1, f2 = frozenset({'what', 'is'}), frozenset({'what', 'is', 'ladder'})
    for _ in range(3):
        ideas.bind(('frame', tuple(sorted(f1, key=repr))), ('right', 7), 1.0)
    ideas.bind(('frame', tuple(sorted(f2, key=repr))), ('right', 7), -1.0)
    assert s._reliable(7, f1, {}) and not s._reliable(7, f2, {})
    assert not s._reliable(7, frozenset(), {}) and s._reliable(7, frozenset(), {(7, frozenset()): [2, 3]})
    s.field.save(tmp_path / 'f.pkl')
    s2 = O.Sera(1, P.Field.load(tmp_path / 'f.pkl'))
    assert s2._reliable(7, f1, {}) and not s2._reliable(7, f2, {})
    monkeypatch.setattr(CR, 'OFF', {'frame_identity'})
    assert not s2._reliable(7, f1, {})


class _Poison:
    def __iter__(self):
        raise AssertionError('the possibilities store was read')

    def append(self, x):
        raise AssertionError('the possibilities store was written')

    def __len__(self):
        return 0


def test_a_world_lived_uses_neither_the_store_nor_recall(one_field, monkeypatch):
    s = O.Sera(1, P.Field(1))
    s.field.possibilities = _Poison()
    moves = []
    base = O.Sera._moves_available

    def seen(self, *a, **k):
        out = base(self, *a, **k)
        moves.append(set(out))
        return out
    monkeypatch.setattr(O.Sera, '_moves_available', seen)
    r = s.live(T.number_task('one more', lambda n: n + 1, 1, 4), teaching=True, max_steps=30)
    assert r['proven'] and not any('recall' in m for m in moves)


def test_one_identity_and_one_write_per_proven_program(one_field):
    """S15 F1: a program that is a concept is that concept, and a proof lays in +1 once, its inner concepts 0.5."""
    s = O.Sera(1, P.Field(1))
    task = T.lesson_where(1)
    var = next(iter(task.inputs))
    a = s.field.invent(N('var', payload='_'), (task.inputs[var], task.out), 'language', 'a', ())
    twice = N('c', N('c', N('var', payload='_'), payload=a['id']), payload=a['id'])
    b = s.field.invent(twice, (task.inputs[var], task.out), 'language', 'b', ())
    law = N('c', N('var', payload=var), payload=a['id'])
    assert s._idea_key(task, law) == ('concept', a['id'])
    assert s._idea_key(task, N('c', N('var', payload=var), payload=a['id'])) == ('concept', a['id'])
    wrapped = N('c', N('var', payload=var), payload=b['id'])
    assert s._proof_amounts(task, wrapped, wrapped, {}, True) == {('concept', b['id']): 1.0}
    raw = s.field.concepts[1]['body']                   # b's body, a(a(_)), written out: b itself
    assert s._idea_key(task, _subst_in(raw, var)) == ('concept', b['id'])
    assert s._proof_amounts(task, law, law, {}, False) == {}


def _subst_in(body, var):
    return O._subst(body, '_', var)


def test_hidden_dependencies_laws_as_sera_forms_them_and_the_empty_law(one_field):
    """S15 F3-F5: a concept whose body uses a hidden one is no thought; two free curves, two parts on one input are
    no law of SERA's; the empty law (no force) has an identity and comes back."""
    s = O.Sera(1, P.Field(1))
    task = T.lesson_where(1)
    var = next(iter(task.inputs))
    a = s.field.invent(N('var', payload='_'), (task.inputs[var], task.out), 'language', 'a', ())
    b = s.field.invent(N('c', N('var', payload='_'), payload=a['id']), (task.inputs[var], task.out), 'language', 'b', ())
    hidden = s._concepts(masked=(a['id'],))
    assert s._from_key(task, ('concept', b['id']), s._concepts(), ()) is not None
    assert s._from_key(task, ('concept', b['id']), hidden, ()) is None
    rail = _rail()
    assert s._idea_key(rail, ()) == ('idea', ())
    assert s._from_key(rail, ('idea', ()), s._concepts(), ()) == ()
    assert s._from_key(rail, ('idea', (('position', 'curve', 9), ('speed', 'curve', 9))), s._concepts(), ()) is None
    assert s._from_key(rail, ('idea', (('position', 'curve', 9), ('position@1:1', 'curve', 9))), s._concepts(),
                       ()) is None


def test_recall_has_nothing_to_give(one_field):
    """S15 F6: called directly, the recall move finds no store."""
    s = O.Sera(1, P.Field(1))
    s.field.possibilities = _Poison()
    task = T.number_task('one more', lambda n: n + 1, 1, 4)
    assert s._move('recall', task, O.kind_of(task), None, s._concepts(), (), None, {}, [], {}, QUIET) == []


def test_a_law_part_that_is_a_concept_is_that_concept(one_field):
    """b1 (2026-10-02): on ripple 2, the concept made of 's' and the expression 's' rang as two thoughts."""
    s = O.Sera(1, P.Field(1))
    rail = _rail()
    c = s.field.invent(N('var', payload='_'), ('num', 'num'), 'physics', 'spring', ())
    raw = (('position', 'expr', N('var', payload='s')),)
    assert s._idea_key(rail, raw) == s._idea_key(rail, (('position', 'concept', c['id']),))
