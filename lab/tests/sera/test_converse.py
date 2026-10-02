"""The conversation world (2026-09-30): which of its proven ideas a question calls for is learned by its Field in a
talk with a teacher, and graded alone on a fresh talk; about someone it was never told of, it does not know."""
from sera import lang as L, one as O, phi as P, tasks as T

N = L.node
G = N('var', payload='_')


def _last(x):
    return N('foldn', N('lam', N('var', payload='e'), payload='ae'), N('zero'), x)


def _sera():
    """A SERA with two proven ideas of a situation, as its lessons would leave them (hand-built here): where someone
    is (the last word of the first sentence about them) and who is in a place (the first word of the sentence ending
    there) - and nothing laid into its Field yet: nothing rings."""
    f = P.Field(1)
    name = _last(N('head', G))
    where = _last(N('head', N('filter', N('lam', N('eq', N('head', N('var', payload='e')), name), payload='e'), G)))
    who = N('head', N('head', N('filter', N('lam', N('eq', _last(N('var', payload='e')), name), payload='e'),
                                N('tail', G))))
    a = f.invent(where, ('list(list)', 'num'), 'language', 'where 1', [])
    b = f.invent(who, ('list(list)', 'num'), 'language', 'who in 1', [])
    return O.Sera(1, f), a['id'], b['id']


def test_its_field_learns_which_idea_a_question_calls_for_and_it_does_not_know_what_it_was_never_told():
    sera, where, who = _sera()
    kinds = (T.lesson_where, T.lesson_who_in)
    before = sera.converse(T.Talk('talk', kinds, 11, n=40), teaching=False)
    absent = sum(r['kind'] == 'absent' for r in before['rows'])
    assert absent > 0 and before['right'] == absent          # nothing rings yet: it does not know - right only there
    assert all(r['said'] is None for r in before['rows'])
    taught = sera.converse(T.Talk('talk', kinds, 12, n=40), teaching=True)
    assert taught['learned']
    after = sera.converse(T.Talk('talk', kinds, 13, n=40), teaching=False)   # a fresh talk, alone
    assert after['right'] >= 0.9 * after['n'], after['by_kind']
    for r in after['rows']:
        if r['kind'] == 'absent':
            assert r['said'] is None                       # never another idea's word for someone it was not told of


def test_a_talk_corrects_a_wrong_association_and_two_talks_do_not_make_it_twice_as_true():
    sera, where, who = _sera()
    ideas = sera._ideas()
    w = T.sym('where')
    ideas.bind(w, ('concept', who), 1.0)                      # a wrong association it came with (S07 F5, reviewer)
    kinds = (T.lesson_where, T.lesson_who_in)
    sera.converse(T.Talk('talk', kinds, 12, n=40), teaching=True)
    q = [w, T.sym('is'), T.sym('mary')]                        # the whole question rings: corrected, by a margin
    rang = dict(ideas.evoked(q, [('concept', where), ('concept', who)]))
    assert rang.get(('concept', where), 0.0) > 2 * rang.get(('concept', who), 0.0)
    before = {t: ideas.bound(t, ('concept', where)) for t in q[:2]}
    again = sera.converse(T.Talk('talk', kinds, 14, n=40), teaching=True)
    assert len(again['learned']) <= 8                          # what agrees with what it holds changes little
    assert all(abs(ideas.bound(t, ('concept', where)) - v) <= 0.25 + 1e-6 for t, v in before.items())
    names = [T.sym(n) for n in T.NAMES] + [T.sym(p) for p in T.PLACES]
    for c in (where, who):                                     # nothing laid into the names and places its stories
        assert all(abs(ideas.bound(t, ('concept', c))) < 0.1 for t in names)   # tell of
    after = sera.converse(T.Talk('talk', kinds, 13, n=40), teaching=False)
    assert after['right'] >= 0.9 * after['n'], after['by_kind']


def test_the_teacher_answers_a_taught_proof_as_it_is_made():
    s = O.Sera(1, P.Field(1))
    t = T.number_task('s07 teacher', lambda x: x + 1, 1, 4)
    law = N('add', N('var', payload=t.var), N('one'))
    before = len(t.data)
    assert s._teacher_says_wrong(t, law, s._concepts(), {}) is None and len(t.data) == before
    bad = N('mul', N('var', payload=t.var), N('one'))           # right only where x + 1 == x: never
    got = s._teacher_says_wrong(t, bad, s._concepts(), {})
    assert got is not None and got[0] == 'input' and len(t.data) == before + 1   # an example it gets wrong, shown


def test_a_wished_ability_does_not_answer_and_a_talk_alone_learns_nothing():
    sera, where, who = _sera()
    wished = sera.field.invent(N('head', N('head', G)), ('list(list)', 'num'), 'language', 'x (wished)', [])
    assert wished['id'] not in sera._situation_ideas()
    rec = sera.converse(T.Talk('talk', (T.lesson_where,), 21, n=10), teaching=False)
    assert rec['learned'] == [] and all('teacher' not in r for r in rec['rows'])   # the grade never reaches it


def test_answering_where_nobody_said_is_corrected():
    """An idea that always gives a word (here: the first word of the last sentence) learns from 'nobody said' that a
    question about someone it was never told of is not its to answer - taught on known facts alone it answered them
    all (the general SERA, 2026-10-01: 13/13 'I do not know' before the talk, 0/13 after)."""
    f = P.Field(1)
    latest = N('foldl', N('lam', N('var', payload='e'), payload='ae'), N('nil'), N('tail', G))
    always = f.invent(N('head', latest), ('list(list)', 'num'), 'language', 'shortcut 1', [])
    s = O.Sera(1, f)
    ideas = s._ideas()
    for w in ('where', 'is'):
        ideas.bind(T.sym(w), ('concept', always['id']), 1.0)      # it rings for where-questions
    t = T.Talk('talk', (T.lesson_where,), 31, n=40, absent=0.5)
    before = sum(r['said'] is not None for r in s.converse(T.Talk('talk', (T.lesson_where,), 32, n=20, absent=1.0),
                                                             teaching=False)['rows'])
    s.converse(t, teaching=True)
    after = s.converse(T.Talk('talk', (T.lesson_where,), 33, n=20, absent=1.0), teaching=False)
    assert before > 0 and sum(r['said'] is not None for r in after['rows']) < before
