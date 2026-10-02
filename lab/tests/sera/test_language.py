import numpy as np

from sera import lang as LG, tasks as TS


BUILDERS = (TS.lesson_first, TS.lesson_last, TS.lesson_who, TS.lesson_where, TS.lesson_where_now,
            TS.lesson_who_in, TS.lesson_is_in, TS.lesson_what_is, TS.lesson_where_first,
            TS.lesson_who_went, TS.lesson_what_is_alone)


def _tokens(values):
    return [TS.text(v) for v in values]


def _check_story(task, x, y):
    q, *sentences = [_tokens(s) for s in x]
    answer = TS.text(y)
    name = task.name
    if name in ('first', 'last'):
        words = sentences[0]
        assert answer == (words[0] if name == 'first' else words[-1])
    elif name == 'who':
        assert answer == sentences[0][0]
    elif name == 'where':
        assert answer in [s[-1] for s in sentences if s[0] == q[-1]]
    elif name == 'where now':
        assert answer == next(s[-1] for s in reversed(sentences) if s[0] == q[-1])
    elif name == 'who in':
        assert answer in [s[0] for s in sentences if s[-1] == q[-1]]
    elif name == 'is in':
        found = any(s[0] == q[1] and s[-1] == q[4] for s in sentences)
        assert answer == ('yes' if found else 'no')
    elif name in ('what is', 'what is alone', 'book what is'):
        assert answer.split() in [s[2:] for s in sentences if s[0] == q[-1]]
    elif name == 'where first':
        assert answer == next(s[-1] for s in sentences if s[0] == q[-1])
    elif name == 'who went':
        assert answer in [s[0] for s in sentences if s[-1] == q[-1]]


def test_all_language_lessons_build_and_examples_match_their_rule():
    for i, build in enumerate(BUILDERS):
        task = build(31 + i)
        assert len(task.data) == 4
        assert len(task.pool) == 40
        assert task.subject == 'language'
        assert task.inputs == {'g': 'list(list)'} and task.var == 'g'
        for x, y in task.data:
            assert task._y(x) == y
            _check_story(task, x, y)
            shown = task.show(x)
            assert shown.startswith('story: ') and ' | question: ' in shown


def test_alone_lessons_have_no_teacher_words():
    for build in (TS.lesson_where_first, TS.lesson_who_went, TS.lesson_what_is_alone):
        assert build(4).words == []


def test_first_and_last_programs_are_accepted_and_graded_right():
    first = TS.lesson_first(7)
    g = LG.node('var', payload='g')
    first_program = LG.node('head', LG.node('head', LG.node('tail', g)))
    assert first.consistent(first_program, {})
    ok, n, failure = first.verify(first_program, {}, LG.bits(first_program, {}), np.random.default_rng(10))
    assert ok and n > 0 and failure is None
    assert first.grade(first_program, {}, True)['verdict'] == 'proven right'

    last = TS.lesson_last(8)
    fold = LG.node('lam', LG.node('var', payload='e'), payload='ae')
    last_program = LG.node('foldn', fold, LG.node('zero'), LG.node('head', LG.node('tail', g)))
    assert last.consistent(last_program, {})
    ok, n, failure = last.verify(last_program, {}, LG.bits(last_program, {}), np.random.default_rng(11))
    assert ok and n > 0 and failure is None
    assert last.grade(last_program, {}, True)['verdict'] == 'proven right'


def test_book_what_is_world_uses_caller_sentences():
    task = TS.book_what_is([['river', 'is', 'moving', 'water', 'in', 'a', 'channel'],
                            ['cloud', 'is', 'a', 'visible', 'mass', 'of', 'water']], 5)
    for x, y in task.data:
        assert task._y(x) == y
        _check_story(task, x, y)


def test_a_proven_program_leaves_both_halves_as_concepts():
    """Abstraction (sera.one Sera._inner_ability): what a program does to its part, and the part itself - a way of
    learning, the same in every subject. From 'where is', the part is 'the sentence about the one the question names',
    and with it 'what is' is a 4-node program."""
    from sera import one as ONE, phi as PH
    sera = ONE.Sera(1, PH.Field(1))
    node, var = LG.node, (lambda x: LG.node('var', payload=x))
    last = node('foldn', node('lam', var('e'), payload='ae'), node('lit', payload=5), node('head', node('tail', var('g'))))
    kept = sera._inner_ability(last, 'g', TS.lesson_last(1), sera._concepts())
    assert [c['built'] for c in kept] == ['what it does to its part', 'the part it works on']
    sare = kept[0]['id']
    heads = lambda x: node('head', x, payload='list')          # a head of lists, as the search writes it
    where = node('c', heads(node('filter', node('lam', node('eq', node('head', var('e')),
                                                             node('c', heads(var('g')), payload=sare)),
                                                 payload='e'), var('g'))), payload=sare)
    task = TS.lesson_where(1)
    assert task.consistent(where, sera._concepts())
    part = sera._inner_ability(where, 'g', task, sera._concepts())
    assert [c['built'] for c in part] == ['the part it works on']
    assert ('var', 'g') not in LG.parts(part[0]['body'])
    what = node('tail', node('tail', node('c', var('g'), payload=part[0]['id'])))
    assert TS.lesson_what_is(1).consistent(what, sera._concepts())


def test_taught_steps_break_where_is_into_pieces():
    """The move 'step' (sera.one Sera._step): with the teacher's worked steps (who it is about; their sentence),
    a SERA with grown seeing breaks 'where is' into steps and the rest follows, and the judge accepts the answer.
    What makes a good step is learned (sera.phi.StepField), neutral at birth; the steps are its own programs."""
    import time
    from sera import one as ONE, phi as PH
    sera = ONE.Sera(1, PH.Field(1))
    sera.field.grown = {'see around'}
    task = TS.lesson_where(301)
    sera._level, sera._open_steps = 3, []
    LG.DEADLINE[0] = time.time() + 600
    try:
        out = sera._step(task, sera._concepts(), lambda *a, **k: None, set(), dict(steps=0, teaching=True))
    finally:
        LG.DEADLINE[0] = float('inf')
    assert out, 'no step worked'
    prog = out[0][0]
    ok, n, _ = task.verify(prog, sera._concepts(), LG.bits(prog, sera._concepts()), np.random.default_rng(3))
    assert ok and n > 100
    assert task.grade(prog, sera._concepts(), True)['verdict'] == 'proven right'


def test_a_story_lesson_offers_the_words_heard_and_is_in_is_asked_as_we_ask():
    """2026-09-30 (the author: "I want to be able to converse"): SERA can say the words it heard in a lesson, as it uses
    the numbers it sees in a task; 'is mary in the kitchen?' is asked as we ask, and its answer is solvable."""
    import numpy as np
    t = TS.lesson_is_in(801)
    q = t.data[0][0][0]
    assert [TS.text(w) for w in q][0] == 'is' and len(q) == 5
    assert [TS.text(w) for w in t.numbers()] == ['is', 'yes', 'no']
    N = LG.node
    g, e = N('var', payload='g'), N('var', payload='e')
    last = lambda x: N('foldn', N('lam', e, payload='ae'), N('lit', payload=4), x)        # noqa: E731
    name = N('head', N('tail', N('head', g)))
    theirs = N('head', N('filter', N('lam', N('eq', N('head', e), name), payload='e'), g))
    prog = N('if', N('eq', last(theirs), last(N('head', g))), N('lit', payload=TS.sym('yes')),
             N('lit', payload=TS.sym('no')))
    assert t.consistent(prog, {})
    assert t.verify(prog, {}, LG.bits(prog, {}), np.random.default_rng(3))[0]
