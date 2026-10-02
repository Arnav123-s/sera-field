"""The observer's printer (2026-09-30): SERA's programs as Python, faithful wherever its program answers."""
import numpy as np

from sera import lang as L, phi as P, pyprint as PP, tasks as T

N = L.node
X = N('var', payload='x')
E = N('var', payload='e')
A = N('var', payload='a')
I = N('var', payload='i')


def _agree(prog, inputs, concepts=None, names=None, words=False):
    concepts = concepts or {}
    src = PP.to_python(prog, concepts, names or {}, arg='x', words=words)
    n = 0
    for x in inputs:
        v = L.safe(prog, {'x': x}, concepts)
        if v is None:
            continue
        n += 1
        assert PP.run(src, PP.as_words(x)) == PP.as_words(v), (L.show(prog), x, v)
    return n


def test_every_form_of_its_language_prints_to_python_that_answers_as_it_does():
    rng = np.random.default_rng(1)
    lists = [tuple(int(v) for v in rng.integers(-5, 9, size=int(rng.integers(0, 7)))) for _ in range(60)]
    progs = [
        N('map', N('lam', N('mul', E, E), payload='e'), X),
        N('filter', N('lam', N('lt', N('zero'), E), payload='e'), X),
        N('mapi', N('lam', N('add', I, E), payload='ie'), X),
        N('filteri', N('lam', N('lt', N('one'), I), payload='ie'), X),
        N('foldn', N('lam', N('add', A, E), payload='ae'), N('zero'), X),
        N('foldl', N('lam', N('cons', E, A), payload='ae'), N('nil'), X),        # reverse
        N('cons', N('head', X), N('tail', N('tail', X))),
        N('range', N('head', X)),
        N('if', N('eq', N('head', X), N('one')), N('lit', payload=7), N('sub', N('head', X), N('one'))),
        N('map', N('lam', N('map', N('lam', N('add', E, N('one')), payload='e'), N('range', E)), payload='e'),
          N('filter', N('lam', N('lt', N('zero'), E), payload='e'), X)),         # nested λs: the inner e shadows
    ]
    for p in progs:
        assert _agree(p, lists) > 10, L.show(p)


def test_its_ideas_print_as_named_functions_even_a_keyword_and_words_as_words():
    f = P.Field(1)
    last = N('foldn', N('lam', E, payload='ae'), N('lit', payload=3), N('var', payload='_'))
    c = f.invent(last, ('list', 'num'), 'language', 'last', [])
    who = N('head', N('head', N('filter', N('lam', N('eq', N('c', E, payload=c['id']),
                                                     N('c', N('head', N('var', payload='_')), payload=c['id'])),
                                            payload='e'), N('tail', N('var', payload='_')))))
    d = f.invent(who, ('list(list)', 'num'), 'language', 'who', [])
    names = {c['id']: 'in', d['id']: 'head'}                       # a keyword and a helper's name
    sy = lambda ws: tuple(T.sym(w) for w in ws.split())             # noqa: E731
    stories = [(sy('who is in the kitchen'), sy('mary went to the garden'), sy('john moved to the kitchen')),
               (sy('who is in the office'), sy('sandra went to the office')),
               (sy('who is in the hallway'), sy('daniel went to the bathroom'))]
    prog = N('c', X, payload=d['id'])
    src = PP.to_python(prog, f.concept_table(), names, words=True)
    assert 'def in_(' in src and 'def head_(' in src
    assert _agree(prog, stories, f.concept_table(), names, words=True) == 2    # nobody in the hallway: its program
    assert L.safe(prog, {'x': stories[2]}, f.concept_table()) is None           # gives no answer, nor is one printed
    assert PP.run(src, PP.as_words(stories[0])) == 'john'
    assert "'yes'" in PP.to_python(N('lit', payload=T.sym('yes')), {}, {}, words=True)


def test_a_job_given_by_examples_is_proven_on_them_and_written_as_python():
    from sera import one as O
    task = T.Given('add one', [(1, 2), (4, 5), (0, 1), (9, 10), (6, 7), (2, 3)], words=['add', 'one'])
    assert task.held == 2 and len(task.data) == 4 and task.actions(None, [], [], {}) == []   # it cannot ask
    s = O.Sera(1, P.Field(1))
    old = O.MAX_WALL
    O.MAX_WALL = 120.0
    try:
        rec = s.live(task, teaching=False)
    finally:
        O.MAX_WALL = old
    assert rec['proven'] and rec['verdict'] == 'proven right'
    src = PP.to_python(rec['answer'], s.field.concept_table(), s.field.names(), arg=task.var)
    assert all(PP.run(src, x) == y for x, y in [(1, 2), (4, 5), (0, 1), (9, 10), (6, 7), (2, 3)])
    try:
        T.Given('one', [(1, 2)])
        raise AssertionError('one example cannot be both learned from and checked')
    except ValueError:
        pass
