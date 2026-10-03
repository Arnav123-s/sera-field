"""Lists that hold lists (2026-09-28, the author: "i want sera to build the abilities it needs, not us building every
smallest thing"): the one change to SERA's language - a list may hold lists, every list mechanism works at every
depth, a concept has the most general type its body allows - and SERA building a grid ability from a puzzle it proved,
then the next one on it. Nothing about grids is given.
"""
import numpy as np

from sera import lang as LG, one as ONE, tasks as TS

G = LG.node('var', payload='g')
E = LG.node('var', payload='e')
A = LG.node('var', payload='a')
U = LG.node('var', payload='_')
REV = LG.node('foldl', LG.node('lam', LG.node('cons', E, A), payload='ae'), LG.node('nil'), U)     # its own reverse


def test_lists_hold_lists_and_nothing_about_grids_is_given():
    for word in ('flip', 'rotate', 'transpose', 'grid', 'row', 'column', 'reverse', 'mirror', 'tile', 'crop'):
        assert word not in LG.INNATE
    assert LG.universe(['list(list)']) == ['num', 'bool', 'list', 'list(list)', 'real']
    assert LG.universe(['list']) == ['num', 'bool', 'list', 'real']
    g = [[1, 2], [3, 4], [5, 6]]
    assert LG.safe(LG.node('head', G, payload='list'), {'g': g}, {}) == (1, 2)
    assert LG.safe(LG.node('head', LG.node('nil'), payload='list'), {}, {}) == ()
    assert LG.safe(LG.node('head', LG.node('nil')), {}, {}) == 0                  # as it always was for numbers
    assert LG.safe(LG.node('cons', LG.node('head', G, payload='list'), G), {'g': g}, {}) == ((1, 2), (1, 2), (3, 4),
                                                                                           (5, 6))
    cs = {1: (REV, '_'), '_sig': {1: ('list(T)', 'list(T)')}}
    mirror = LG.node('map', LG.node('lam', LG.node('c', E, payload=1), payload='e'), G)
    assert LG.safe(mirror, {'g': g}, cs) == ((2, 1), (4, 3), (6, 5))
    assert LG.safe(LG.node('c', G, payload=1), {'g': g}, cs) == ((5, 6), (3, 4), (1, 2))
    # A call of a concept the mind does not hold (U pilot, no-library arm: KeyError 4) is a bad program, not a crash.
    assert LG.safe(LG.node('c', G, payload=4), {'g': g}, cs) is None
    assert LG.safe(LG.node('c', G, payload=1), {'g': g}, {}) is None


def test_a_concept_has_the_most_general_type_its_body_allows():
    assert LG.infer(REV, {}) == ('list(T)', 'list(T)')
    total = LG.node('foldn', LG.node('lam', LG.node('add', A, E), payload='ae'), LG.node('zero'), U)
    count = LG.node('foldn', LG.node('lam', LG.node('add', A, LG.node('one')), payload='ae'), LG.node('zero'), U)
    assert LG.infer(total, {}) == ('list', 'num')
    assert LG.infer(count, {}) == ('list(T)', 'num')
    assert LG.infer(LG.node('mul', U, U), {}) == ('num', 'num')
    assert LG.infer(LG.node('tab', payload=((0.0, 1.0), (0.0, 1.0))), {}) == ('num', 'num')
    assert LG.infer(LG.node('add', U, LG.node('nil')), {}) is None              # no type: never a concept's
    cs = {1: (REV, '_'), '_sig': {1: ('list(T)', 'list(T)')}}
    rows = LG.node('map', LG.node('lam', LG.node('c', E, payload=1), payload='e'), U)
    assert LG.infer(rows, cs) == ('list(list(T))', 'list(list(T))')
    assert LG.fits(('list(T)', 'list(T)'), 'list(list)', 'list(list)') and LG.fits(('list(T)', 'list(T)'), 'list', 'list')
    assert not LG.fits(('list(T)', 'list(T)'), 'list', 'num')


def test_values_made_from_parts_are_what_evaluation_gives():
    probes = [{'l': l} for l in ([1, 2, 3], [], [5, -1], [2, 2, 7, 0])]
    for e, _, vals in LG.search({'l': 'list'}, 'list', probes, 7, values=True):
        assert tuple(LG.seen_as(v) for v in vals) == tuple(LG.safe(e, p, {}) for p in probes), LG.show(e)
    grids = [{'g': g} for g in ([[1, 2], [3, 4]], [[0, 5, 5]], [[1], [2], [3]], [[7, 0], [0, 7], [1, 1]])]
    for e, _, vals in LG.search({'g': 'list(list)'}, 'list(list)', grids, 7, values=True):
        assert tuple(vals) == tuple(LG.safe(e, p, {}) for p in grids), LG.show(e)


def test_its_search_finds_a_flip_of_a_list_of_lists_and_a_learned_reverse_works_on_its_rows():
    gs = ([[1, 2], [3, 4]], [[0, 5, 5]], [[1], [2], [3]], [[7, 0], [0, 7], [1, 1]])
    grids = [{'g': g} for g in gs]
    found = [e for e, _ in LG.search({'g': 'list(list)'}, 'list(list)', grids, 7)]
    assert any(all(LG.safe(e, p, {}) == tuple(tuple(r) for r in p['g'][::-1]) for p in grids) for e in found)
    cs = {1: (REV, '_'), '_sig': {1: ('list(T)', 'list(T)')}}
    found = [e for e, _ in LG.search({'g': 'list(list)'}, 'list(list)', grids, 5, cs)]   # map(λe. c1(e), g): 5 nodes
    want = [tuple(tuple(r[::-1]) for r in g) for g in gs]
    assert any(all(LG.safe(e, p, cs) == w for p, w in zip(grids, want)) for e in found)


def test_a_size_cut_short_is_finished_before_a_bigger_one():
    """ARC 6fa7a44f: the program (the grid, then its flip) was 9 nodes; the search at 9 nodes was cut by its work bound
    before reaching it and was never looked at again, however long SERA thought. Now a size cut short is continued when
    it thinks again with a larger bound, and nothing bigger is begun before it is finished."""
    probes = [{'l': l} for l in ([1, 2, 3], [], [5, -1], [2, 2, 7, 0])]
    LG._TABLES.clear()
    cut = LG.search({'l': 'list'}, 'list', probes, 7, work=40)
    assert max(s for _, s in cut) < 7                                  # stopped inside a smaller size
    more = LG.search({'l': 'list'}, 'list', probes, 7, work=10 ** 9)   # thinking again, harder: it continues
    LG._TABLES.clear()
    whole = LG.search({'l': 'list'}, 'list', probes, 7, work=10 ** 9)
    assert more == whole and len(whole) > len(cut)


def puzzle(f, grids, test):
    return dict(train=[dict(input=g, output=f(g)) for g in grids], test=[dict(input=test, output=f(test))])


def test_sera_builds_a_grid_ability_from_a_puzzle_then_builds_the_next_on_it(monkeypatch):
    monkeypatch.setattr(ONE, 'MAX_WALL', 600.0)
    gs = ([[1, 2, 0], [3, 4, 0]], [[0, 5], [5, 5], [6, 0]], [[7, 7, 1]], [[2, 0], [0, 3], [1, 1], [4, 4]])
    test = [[1, 0, 2], [0, 3, 4], [5, 6, 0]]
    flip = lambda g: [list(r) for r in g[::-1]]
    mirror = lambda g: [list(r[::-1]) for r in g]
    half = lambda g: [list(r[::-1]) for r in g[::-1]]
    sera = ONE.Sera(1)
    r1 = sera.live(TS.Puzzle('flip', puzzle(flip, gs, test)))
    assert r1['proven'] and r1['verdict'] == 'proven right', r1.get('verdict')
    assert r1['invented'], 'the flip it proved became a concept'
    c1 = next(c for c in sera.field.concepts if c['id'] == r1['invented'][0]['id'])
    assert tuple(c1['sig']) == ('list(T)', 'list(T)')                   # its reverse, for any list
    r2 = sera.live(TS.Puzzle('mirror', puzzle(mirror, gs, test)))
    assert r2['proven'] and r2['verdict'] == 'proven right', r2.get('verdict')
    assert c1['id'] in r2['reused']                                    # built on its own flip, now on the rows
    r3 = sera.live(TS.Puzzle('half turn', puzzle(half, gs, test)))
    assert r3['proven'] and r3['verdict'] == 'proven right', r3.get('verdict')
    assert r3['reused'], 'a half turn from what it made'
    assert np.isinf(LG.DEADLINE[0])                                    # a world's time box ends with it


def test_it_wishes_for_the_ability_it_lacks_builds_it_and_uses_it(monkeypatch):
    """The author, 2026-09-28: "if sera figures out it could solve the problem if it could do this or that, then sera
    builds that ability and uses it". A colour changed to another, cell by cell, needs an iteration inside an
    iteration, which its λ bodies cannot hold: it sees the puzzle element by element all the way down (a cell decides
    what it becomes: each colour is seen many times), builds that one ability, and proves the puzzle with it, used
    inside maps inside maps. Nothing about colours or cells is given."""
    monkeypatch.setattr(ONE, 'MAX_WALL', 600.0)
    gs = ([[1, 7, 0], [7, 7, 2]], [[0, 5], [7, 3], [6, 7]], [[7, 1, 7, 4]], [[2, 0], [0, 7], [1, 1], [7, 7]])
    test = [[7, 0, 2], [0, 7, 4], [5, 6, 7]]
    swap = lambda g: [[5 if v == 7 else v for v in r] for r in g]
    sera = ONE.Sera(1)
    r = sera.live(TS.Puzzle('colour', puzzle(swap, gs, test)))
    assert r['proven'] and r['verdict'] == 'proven right', r.get('verdict')
    assert r['built'], 'it built the ability it lacked'
    cell = next(c for c in sera.field.concepts if c['id'] == r['built'][0]['id'])
    assert tuple(cell['sig']) == ('num', 'num')
    ids = {c['id'] for c in sera.field.concepts}
    assert all(b['id'] in ids for b in r['built'])                   # what it kept, it used


def test_it_builds_an_ability_for_each_element_of_a_list(monkeypatch):
    monkeypatch.setattr(ONE, 'MAX_WALL', 600.0)
    sera = ONE.Sera(1)
    t = TS.list_task('list: three to nine', lambda l: [9 if x == 3 else x for x in l], 'list', 1, 7)
    r = sera.live(t)
    assert r['proven'] and r['verdict'] == 'proven right', r.get('verdict')
    assert any(b['words'] == 'make each element what it becomes' for b in r['built'])   # among what it built: it
    #   may first build another ability of its own (5e058d6 on Colab: "handle eq(w, 3) (it gives 9), then the rest", a
    #   case split whose rest is the element unchanged) - which comes first depends on the time each wish gets
