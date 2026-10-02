"""Understanding that does not depend on where a word sits (plan 7.11 step 3; review 8, design D). The observer's own
check that the lessons are solvable and consistent: small programs of SERA's language (hand-built here, never given
to SERA) fit every lesson's examples and the evaluation - where, the name anywhere, in frames taught and not, and
with words never read."""
from sera import lang as L, tasks as T

N = L.node
V = lambda s: N('var', payload=s)          # noqa: E731
C = lambda i, x: N('c', x, payload=i)      # noqa: E731
lam = lambda k, b: N('lam', b, payload=k)  # noqa: E731
W, E = V('_'), V('e')


def _d():
    """Design D's pieces (S08): last, hit, has, rows about, latest row, where, yes/no."""
    b = {1: N('foldn', lam('ae', E), N('zero'), W),
         2: N('head', N('filter', lam('e', N('eq', E, N('head', W))), N('tail', W)))}
    b[3] = N('eq', C(2, W), N('head', W))
    b[4] = N('filter', lam('e', C(3, N('cons', N('head', E), N('head', W, payload='list')))), N('tail', W))
    b[5] = N('foldl', lam('ae', E), N('nil'), C(4, W))
    b[6] = C(1, C(5, W))
    b[7] = N('if', C(3, N('cons', C(6, W), N('head', W, payload='list'))), N('lit', payload=T.sym('yes')),
             N('lit', payload=T.sym('no')))
    sig = {1: ('list', 'num'), 2: ('list', 'num'), 3: ('list', 'bool'), 4: ('list(list)', 'list(list)'),
           5: ('list(list)', 'list'), 6: ('list(list)', 'num'), 7: ('list(list)', 'num')}
    cs = {i: (p, '_') for i, p in b.items()}
    cs['_sig'] = sig
    return cs


def test_the_small_abilities_fit_their_lessons():
    cs = _d()
    for build, cid, var in ((T.lesson_among, 2, 'w'), (T.lesson_is_among, 3, 'w'), (T.lesson_rows_about, 4, 'g'),
                            (T.lesson_latest_row, 5, 'g')):
        t = build(1)
        prog = C(cid, V(var))
        assert t.consistent(prog, cs), t.name
        assert all(t._value(prog, x, cs) == t._y(x) for x in t.pool), t.name      # and on the world's own inputs
        ys = [y for _, y in t.data] + [t._y(x) for x in t.pool]
        assert len({repr(y) for y in ys}) > 1, t.name                            # not one answer for all


def test_where_with_the_name_anywhere_and_yes_or_no():
    cs = _d()
    t = T.lesson_where_any(1)
    assert t.consistent(C(6, V('g')), cs)
    frames = {' '.join(T.text(w) for w in x[0][:2]) for x, _ in t.data + [(x, None) for x in t.pool]}
    assert len(frames) >= 2                                                       # asked in more than one way
    for renamed in (False, True):
        ev = T.where_any_eval(3, renamed=renamed)
        assert len(ev) == 80 and {f for _, _, f in ev} >= {'unseen'}
        assert all(L.safe(C(6, V('g')), {'g': x}, cs) == y for x, y, _ in ev)     # in every frame, new words too
    yn = T.lesson_is_in_any(1)
    assert yn.consistent(C(7, V('g')), cs)
    assert {T.text(y) for _, y in yn.data + [(x, yn._y(x)) for x in yn.pool]} == {'yes', 'no'}
    assert set(yn.words) == {'is', 'yes', 'no'}                                   # the answers it may say: heard
