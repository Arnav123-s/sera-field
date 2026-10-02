"""The honesty fix (plan Phase 3.1, 2026-10-01; review 11): a physics proof credits what the judge certified. A free
cell on the dimension SERA's expression is said as proves some curve of that coordinate - x^3 and the wrong 1 + x^3
are both accepted on stiff 2 (sera-runs/judge-channel-1001/s10_false_credit.out) - so neither becomes a formula
SERA believes. The fitted table composed with that dimension is kept (S17); a 33-knot cell proves a curve of its
input, kept as that curve; a registered shape proves the drawing of its concept, which is reused."""
import time
from types import SimpleNamespace

import numpy as np
import pytest

from sera import lang as L, one as O, phi as P, tasks as T

N = L.node
S = N('var', payload='s')
CUBE = N('mul', S, N('mul', S, S))


@pytest.fixture
def stiff2(monkeypatch):
    from ccops5.core import grammar, truth
    monkeypatch.setattr(grammar, 'SHAPES_POLICY', 'library')     # the judge's policies as the runs set them
    monkeypatch.setattr(grammar, 'SHAPE_WEIGHT', 0.01)           # (Decisions 8, 12, 13; as test_s09)
    monkeypatch.setattr(truth, 'BAND', 'claim')
    monkeypatch.setattr(truth, 'CLAIM', 'functional')
    w, signs = T.rail_world(3, 80301, (('position', 'cubic'),), 1)
    return T.Rail(w, 'rail: stiff 2', (), signs)


def _live(s, task, law, library=(), proven=None, after_prove=None):
    """Prove the law with the real judge, then keep what the proof lets it keep (alone: its own proof decides)."""
    from ccops5.core import grammar
    grammar.use_library(s.field.shapes())
    concepts = s._concepts()
    st = dict(tested=set(), steps=1, proven=None, judge_short=0., judge_where=None, misfit=False, level=0, asked=0,
              explored=0, time={}, peak=[0], peak_by={}, memory_stops=0, origins={}, footholds={})
    assert s._prove(task, law, concepts, library, st, lambda *a, **k: None), 'the judge accepts it'
    if proven is not None:
        proven.update(st['proven'])
    if after_prove is not None:
        after_prove()
    return s._finish(task, O.kind_of(task), task.context(), concepts, library, st, law, [law], {law: 0.},
                     {law: 0.}, {}, [], [], [], False, time.time(), time.process_time())


@pytest.mark.parametrize('expr, dim', [(CUBE, 'dim:x.x.x.mul.mul@4'),
                                       (N('add', N('one'), CUBE), 'dim:1.x.x.x.mul.mul.add@6')])
def test_a_curve_on_its_dimension_credits_the_curve_not_its_formula(stiff2, monkeypatch, expr, dim):
    monkeypatch.setattr(T, 'RAMP', False)                       # the curve alone (before Decision 16)
    s = O.Sera(1, P.Field(1))
    law = (('position', 'expr', expr),)
    proven = {}
    r = _live(s, stiff2, law, proven=proven)
    assert r['proven'] and r['verdict'] == 'proven right'
    assert r['certified'] == [{'part': 0, 'as': 'curve', 'on': dim}]
    assert len(r['invented']) == len(s.field.concepts) == 1 and r['reused'] == []
    assert r['invented'][0]['how'] == 'curve' and r['invented'][0]['input'] == dim
    c = s.field.concepts[0]
    assert c['body'][0] == 'tab' and c['body'][2] == O._subst(expr, 's', '_')
    assert c['input'] == dim and c['argument_input'] == 'position' and c['certified'] == 'curve'
    assert c['parts'] == [('input', dim), ('curve', dim)]                       # no formula part gets credit
    assert L.infer(c['body'], s._concepts()) == ('num', 'num')
    assert s.field.standing.get(((dim, 'curve', 9),)) == [1, 0]                   # what it believes: the curve
    assert law not in s.field.standing                                            # its formula: no standing
    kept = [p for p in s.field.possibilities if p['key'] == law]
    assert kept and kept[0]['why'] == 'a curve of it proven'                      # only an idea it may try again
    assert s.field.standing == {((dim, 'curve', T.DIM_K),): [1, 0]}
    fam = s.field.familiarity(O.kind_of(stiff2), stiff2.context())[0]
    assert not any(fam.get(('sym', op), 0.) for op in ('add', 'one', 'mul'))

    from ccops5.core import grammar as G, truth
    term = ('cell', dim, T.DIM_K)
    assert proven['family'] == (term,)
    cert = proven['cert']
    assert c['proof'] == dict(claim=G.name((term,)), term=repr(term), digest=cert.digest,
                              eps=cert.eps, band=cert.band, throws=proven['n'], at=0)
    assert c['proof']['digest'] == truth.digest(stiff2.throws)
    assert c['proof']['throws'] == len(stiff2.throws)
    fit = proven['fit']
    coef = fit.coef[G.coef_slice(proven['family'], term)]
    call = N('c', S, payload=c['id'])
    xs = (-3., -1.25, -0.6, 0., 0.37, 0.91, 1.6, 3.)                         # interior and both clamped tails
    us = np.array([L.evaluate(expr, {'s': x}, {}) for x in xs], float)
    expected = T.hats(dim, us, T.DIM_K) @ coef                                 # the fitted cell's own basis
    actual = [L.evaluate(call, {'s': x}, s._concepts()) for x in xs]
    assert actual == pytest.approx(expected, rel=0., abs=1e-9)                 # including the fitted scale
    assert np.max(np.abs(np.asarray(actual) - us)) > 1e-6                     # it is not the formula itself

    assert [sh[1] for sh in c['shapes']] == list(T.CHANNELS)
    for sh in c['shapes']:                                                    # Decision 12: position, speed, time
        us = np.array([L.evaluate(expr, {'s': float(x)}, {}) for x in T.grid(sh[1])], float)
        vals = T.hats(dim, us, T.DIM_K) @ coef
        # draw_knots rounds evaluated values to nine decimals before normalizing, for every concept.
        vals = np.array([round(float(v), 9) for v in vals])
        assert sh[4] == pytest.approx(vals / np.max(np.abs(vals)), rel=0., abs=1e-9)
    idea = ('idea', (('position', 'concept', c['id']),))
    assert s._proof_amounts(stiff2, law, ((dim, 'curve', T.DIM_K),), {0: c['id']}, True) == {idea: 1.}


def test_its_formula_is_credited_only_by_its_own_ramp(stiff2):
    """Decision 16: x^3 said as one strength times x^3 is accepted - its formula, invented; 1 + x^3's ramp is
    refused (its constant is not there), so it is said as a curve and gets a curve's credit only."""
    s = O.Sera(1, P.Field(1))
    r = _live(s, stiff2, (('position', 'expr', CUBE),))
    assert r['certified'] == [{'part': 0, 'as': 'formula', 'on': 'dim:x.x.x.mul.mul@4'}]
    assert [i['body'] for i in r['invented']] == ['mul(_, mul(_, _))']
    s = O.Sera(1, P.Field(1))
    r = _live(s, stiff2, (('position', 'expr', N('add', N('one'), CUBE)),))
    assert r['certified'] == [{'part': 0, 'as': 'curve', 'on': 'dim:1.x.x.x.mul.mul.add@6'}]
    assert len(r['invented']) == len(s.field.concepts) == 1
    assert r['invented'][0]['how'] == 'curve' and s.field.concepts[0]['body'][0] == 'tab'
    assert s.field.concepts[0]['certified'] == 'curve'
    assert (('position', 'expr', N('add', N('one'), CUBE)),) not in s.field.standing


def test_a_curve_of_its_input_is_kept_as_that_curve_and_then_reused_as_its_drawing(stiff2):
    s = O.Sera(1, P.Field(1))
    law = (('position', 'expr', N('mul', N('lit', payload=3), S)),)      # a literal no dimension can say
    r = _live(s, stiff2, law)
    assert r['certified'] == [{'part': 0, 'as': 'curve', 'on': 'position'}]
    assert len(r['invented']) == 1 and r['invented'][0]['how'] == 'curve'         # a table of the fitted curve
    c = s.field.concepts[0]
    assert c['body'][0] == 'tab' and c.get('shapes')                             # not 3 * s; drawn for the judge
    library = tuple(c['shapes'])
    again = _live(s, stiff2, (('position', 'concept', c['id']),), library)
    assert again['certified'][0]['as'] == 'drawing'
    assert again['reused'] == [c['id']] and again['invented'] == []


def test_s11b_a_coordinate_makes_no_formula_part_familiar_and_attribution_fails_closed():
    """review 11b F1 and F5: a curve on 1 + x^3's dimension does not make add, one or mul familiar; without a complete
    attribution nothing is kept."""
    s = O.Sera(1, P.Field(1))
    law = (('position', 'expr', N('add', N('one'), CUBE)),)
    d = 'dim:1.x.x.x.mul.mul.add@6'
    kept, how = s._certified(law, ((('cell', d, 9), 'curve'),))
    assert kept == ((d, 'curve', 9),) and how == [{'part': 0, 'as': 'curve', 'on': d}]
    s.field.understand('witness', [0.], kept, s._hparts(kept, 'strengths'), True, 1., 'witness')
    fam = s.field.familiarity('witness', [0.])[0]
    assert not any(fam.get(('sym', op), 0.) for op in ('add', 'one', 'mul'))
    assert s._certified(law, None)[0] is None
    assert s._certified(law + law, ((('cell', d, 9), 'curve'),))[0] is None


def test_s11b_a_drawing_credits_the_concept_that_owns_the_shape_the_judge_saw():
    """review 11b F2: two concepts with one drawing; the judge saw a's registered shape, so a is credited, not b."""
    from ccops5.core import grammar as G
    s = O.Sera(1, P.Field(1))
    a = s.field.invent(L.node('var', payload='_'), ('num', 'num'), 'physics', 'a', ())
    b = s.field.invent(L.node('var', payload='_'), ('num', 'num'), 'physics', 'b', ())
    sh = G.shape_term('position', 33, 1, T.draw_knots(('position', 'concept', a['id']), s._concepts()))
    a['shapes'] = [sh]
    part = ('position', 'concept', b['id'])
    kept, how = s._certified((part,), ((sh, 'drawing'),))
    assert kept == (('position', 'concept', a['id']),) and how[0]['concept'] == a['id']
    alien = G.shape_term('position', 33, 7, sh[4])                    # a shape no concept of its owns
    assert s._certified((part,), ((alien, 'drawing'),))[0] is None


def test_s11b_a_dimension_gives_no_direction():
    """review 11b F4: the sign of a curve on a dimension is its coordinate's convention, not the push's direction."""
    from types import SimpleNamespace
    negx = 'dim:0.x.sub@4'
    assert negx not in O.Sera._signs((('cell', negx, 9),), SimpleNamespace(coef=T.grid(negx, 9)))


def test_s14_formula_credit_needs_its_own_ramp_and_the_accepted_family():
    """review 14 F1: 1 + x^3 labelled with x^3's ramp is not credited; nor is a credit that is not the accepted family."""
    s = O.Sera(1, P.Field(1))
    wrong = (('position', 'expr', N('add', N('one'), CUBE)),)
    ramp = ('ramp', 'dim:x.x.x.mul.mul@4', 9)
    assert s._certified(wrong, ((ramp, 'formula'),))[0] is None
    right = (('position', 'expr', CUBE),)
    assert s._certified(right, ((ramp, 'formula'),), (ramp,))[0] == right
    assert s._certified(right, ((ramp, 'formula'),), (('cell', 'position', 33),))[0] is None


def test_a_curve_on_a_dimension_that_is_only_its_input_becomes_a_table(monkeypatch):
    """A spring said as 's' is a curve on dim:x - position itself: the fitted curve is a curve of position, kept as a
    table concept (phys-ec5d2ec-s3: spring 2, ripple 1 and 2 invented nothing)."""
    from ccops5.core import grammar, truth
    monkeypatch.setattr(grammar, 'SHAPES_POLICY', 'library')
    monkeypatch.setattr(grammar, 'SHAPE_WEIGHT', 0.01)
    monkeypatch.setattr(truth, 'BAND', 'claim')
    monkeypatch.setattr(truth, 'CLAIM', 'functional')
    monkeypatch.setattr(T, 'RAMP', False)
    w, signs = T.rail_world(3, 80302, (('position', 'straight'),), 1)
    task = T.Rail(w, 'rail: spring', (), signs)
    s = O.Sera(1, P.Field(1))
    r = _live(s, task, (('position', 'expr', S),))
    assert r['certified'][0]['as'] == 'curve' and r['certified'][0]['on'].startswith('dim:x@')
    assert len(r['invented']) == 1 and s.field.concepts[0]['body'][0] == 'tab'


@pytest.mark.parametrize('channel, dim, expr', [
    ('position', 'dim:0.x.sub@4', N('sub', N('zero'), S)),
    ('speed', 'dim:1.v.v.mul.add@6', N('add', N('one'), N('mul', S, S))),
    ('time', 'dim:t.1.sub@4', N('sub', S, N('one'))),
])
@pytest.mark.parametrize('K', [9, 17, 33])
def test_s17_composed_tables_keep_their_cell_in_a_mixed_family(channel, dim, expr, K):
    """A non-ramp cell, on each original input: its own coefficient slice, scale, grid and clamped tails survive."""
    from ccops5.core import grammar as G
    s = O.Sera(1, P.Field(1))
    task = SimpleNamespace(name='composed cell', form='strengths')
    term = ('cell', dim, K)
    other = ('nothing', 'steady')                            # a primitive sorts before the cell
    family = G.canonical((other, term))
    assert G.coef_slice(family, term).start == 1
    coef = np.full(G.n_coef(family), 123.)
    values = 3. + np.cos(np.arange(K))
    coef[G.coef_slice(family, term)] = values
    c = s._invent_part(task, (dim, 'curve', K), family, SimpleNamespace(coef=coef), s._concepts(), [0.])
    assert c is not None and len(s.field.concepts) == 1
    assert c['body'] == N('tab', O._subst(expr, 's', '_'), payload=(tuple(T.grid(dim, K)), tuple(values)))
    assert c['input'] == dim and c['argument_input'] == channel and c['certified'] == 'curve'
    xs = (-4., -0.43, 0., 0.29, 1.17, 4.)
    us = np.array([L.evaluate(expr, {'s': x}, {}) for x in xs], float)
    call = N('c', S, payload=c['id'])
    actual = [L.evaluate(call, {'s': x}, s._concepts()) for x in xs]
    assert actual == pytest.approx(T.hats(dim, us, K) @ values, rel=0., abs=1e-9)
    idea = ('idea', ((channel, 'concept', c['id']),))
    assert s._proof_amounts(task, ((channel, 'expr', expr),), ((dim, 'curve', K),), {0: c['id']}, True) == {idea: 1.}


@pytest.mark.parametrize('channel', ['position', 'dim:x@4', 'dim:v@4', 'dim:t@4'])
def test_s17_plain_input_tables_keep_their_existing_normalization(channel):
    """S17 changes composed coordinates only: a single input still becomes a plain, normalized 33-knot table."""
    s = O.Sera(1, P.Field(1))
    family = (('cell', channel, 9),)
    coef = np.array([2., -3., 4., 1., 0., -2., 3., -4., 2.])
    c = s._invent_part(SimpleNamespace(name='input cell'), (channel, 'curve', 9), family,
                       SimpleNamespace(coef=coef), s._concepts(), [0.])
    vals = np.interp(T.grid(channel), T.grid(channel, 9), coef)
    assert c is not None and c['body'] == N('tab', payload=(tuple(T.grid(channel)), tuple(vals / max(abs(vals)))))
    assert 'argument_input' not in c


def test_s17_a_mixed_coordinate_is_not_kept_as_a_function_of_one_number():
    """Using the same scalar for x and v would invent the wrong function; retain the existing no-invention case."""
    s = O.Sera(1, P.Field(1))
    dim = 'dim:x.v.mul@6'
    family = (('cell', dim, 9),)
    c = s._invent_part(SimpleNamespace(name='mixed coordinate'), (dim, 'curve', 9), family,
                       SimpleNamespace(coef=np.arange(9.)), s._concepts(), [0.])
    assert c is None and s.field.concepts == []


def test_s17_a_table_keeps_the_fit_from_its_proof_when_more_throws_arrive(monkeypatch):
    """Unit test of proof-state retention; the stiff2 tests above exercise the real judge."""
    from unittest.mock import Mock
    monkeypatch.setattr(T, 'RAMP', False)
    monkeypatch.setattr(O, 'ONE_FIELD', False)
    monkeypatch.setattr(O.truth, 'functional_prior', lambda family: 0.)
    dim = 'dim:x.x.x.mul.mul@4'
    term = ('cell', dim, 9)
    family = (term,)
    cert = SimpleNamespace(eps=0.2, band=0.1, digest='the certified throws')
    fit = SimpleNamespace(coef=np.arange(9., dtype=float), order=())
    task = SimpleNamespace(name='proof fit', subject='physics', form='strengths', inputs={'s': 'num'},
                           out='num', words=[], throws=[object()], context=lambda: [0.], teacher_truth=lambda w: False,
                           claim_terms=lambda *a, **k: (family, ((term, 'curve'),)),
                           verify=Mock(return_value=(True, cert, None)),
                           ledger=Mock(return_value=SimpleNamespace(mle=Mock(return_value=fit))),
                           grade=Mock(return_value={'verdict': 'proven right'}))

    def later_throw():
        task.throws.append(object())
        task.ledger.side_effect = AssertionError('a later fit is not the certified fit')

    s = O.Sera(1, P.Field(1))
    proven = {}
    r = _live(s, task, (('position', 'expr', CUBE),), proven=proven, after_prove=later_throw)
    assert proven['fit'] is fit and proven['n'] == 1 and len(task.throws) == 2
    task.ledger.assert_called_once_with([family])
    task.grade.assert_called_once_with(cert, True, n_throws=1)
    assert r['certified'] == [{'part': 0, 'as': 'curve', 'on': dim}]
    assert len(r['invented']) == len(s.field.concepts) == 1
    c = s.field.concepts[0]
    assert c['body'][1][1] == tuple(fit.coef)
    assert c['proof']['digest'] == cert.digest and c['proof']['throws'] == 1
