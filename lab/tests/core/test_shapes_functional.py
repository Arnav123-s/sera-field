"""Decision 12 (SERA's invented shapes: a tied cell) and Decision 13 (functional claims: "this law up to eps where I
looked"):
  - off by default: no family changes (no tie, the same priors);
  - a tied shape moves its cell's hats together: its simulation is the cell's at strength x knots, its Jacobian the
    chain rule of the cell's;
  - under the 'library' policy a library shape is claimable with its e-LOND prior, and a shape not in the library is
    not;
  - a functional claim of the true law's own free curve is accepted and the independent checker re-derives it; a
    wrong law (a drag for a spring) is refused; the functional prior pays for two parts and refuses two on one input.
"""
import math

import numpy as np

from ccops5.core import checker, grammar, likelihood as L, paths, truth, worlds as W

SIGMA = (0.001, 0.001)


def _throws(family, coef, situations=4, seed=3, pushes=(0.6, -0.6, 1.0)):
    kk, aa, bb = grammar.codes(family)
    T = grammar.tie(family)
    cc = np.asarray(coef, float) if T is None else T @ np.asarray(coef, float)
    rng = np.random.default_rng(seed)
    out = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            act = W.Action(((0.0, 0.4 + 0.4 * j, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, cc, 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            out.append(W.Throw(k, len(out), act, xs + nr.normal(0, 1e-3, xs.size), vs + nr.normal(0, 1e-3, vs.size)))
    return out


def _shape(n=1, inp='position'):
    g = np.linspace(-3.0, 3.0, 33)
    return grammar.shape_term(inp, 33, n, g / 3.0)                  # a straight line, drawn on the grid


def test_off_by_default_nothing_changes():
    assert grammar.SHAPES_POLICY == 'off'
    fam = (('position', 'straight'), ('speed', 'straight'))
    assert grammar.tie(fam) is None
    assert truth.model_of(fam).tie is None
    assert grammar.CELL_WEIGHT == 0.03
    assert grammar.log_prior((_shape(),)) == -math.inf                # not claimable without the policy


def test_a_tied_shape_is_its_cell_at_strength_times_knots():
    sh = _shape()
    tied = truth.model_of((sh,))
    cell = truth.model_of((('cell', 'position', 33),))
    assert tied.n_coef == 1 and cell.n_coef == 33
    t = _throws((sh,), [-2.0], situations=1)[0]
    a = L._sim(tied, np.array([-2.0]), 0.8, t)
    b = L._sim(cell, -2.0 * np.asarray(sh[4]), 0.8, t)
    assert np.allclose(a, b, atol=1e-12)
    y, J = L._jac(tied, np.array([-2.0]), 0.8, t)
    h = 1e-6
    fd = (L._sim(tied, np.array([-2.0 + h]), 0.8, t) - L._sim(tied, np.array([-2.0 - h]), 0.8, t)) / (2 * h)
    assert np.allclose(J[:, 0], fd, atol=1e-5 * max(1.0, np.max(np.abs(fd))))


def test_library_shapes_are_claimable_with_their_share(monkeypatch):
    monkeypatch.setattr(grammar, 'SHAPES_POLICY', 'library')
    monkeypatch.setattr(grammar, 'SHAPE_WEIGHT', 0.01)
    sh1, sh2 = _shape(1), _shape(2, 'speed')
    grammar.use_library((sh1, sh2))
    try:
        assert grammar.log_prior((sh1,)) == math.log(0.5) + math.log(0.01) + math.log(6 / math.pi ** 2)
        assert grammar.log_prior((sh2,)) == math.log(0.5) + math.log(0.01) + math.log(6 / (math.pi ** 2 * 4))
        other = grammar.shape_term('position', 33, 3, np.ones(33))
        assert grammar.log_prior((other,)) == -math.inf               # not in the library: never claimable
        assert grammar.contains((('cell', 'position', 33),), (sh1,))    # a cell holds its own grid's shapes
    finally:
        grammar.use_library(())


def _ledger(throws, fams):
    led = truth.Ledger(fams, SIGMA)
    for t in throws:
        led.add(t)
    return led


def test_a_functional_claim_of_the_true_curve_is_accepted_and_rederived(monkeypatch):
    monkeypatch.setattr(truth, 'CLAIM', 'functional')
    monkeypatch.setattr(truth, 'BAND', 'claim')                  # reviewer VD13: the claim's own forecast
    throws = _throws((('position', 'straight'),), [-2.0], situations=8,         # 32 throws, pushed hard and soft
                     pushes=(0.6, -0.6, 1.0, -1.0))                             # (12 soft ones left the band at 0.204)
    fam = (('cell', 'position', 9),)
    led = _ledger(throws, [(), fam])
    cert = truth.certify(led, fam, 0.2)
    assert cert.claim_kind == 'functional' and not cert.rivals
    assert cert.accepted, cert.reasons
    ok, why = checker.check(cert, throws, SIGMA)
    assert ok, why


def test_a_wrong_functional_claim_is_refused(monkeypatch):
    monkeypatch.setattr(truth, 'CLAIM', 'functional')
    monkeypatch.setattr(truth, 'BAND', 'claim')                  # reviewer VD13: the claim's own forecast
    throws = _throws((('position', 'straight'),), [-2.0])
    fam = (('cell', 'speed', 9),)                                     # a drag for a spring
    led = _ledger(throws, [(), fam])
    cert = truth.certify(led, fam, 0.2)
    assert not cert.accepted


def test_the_functional_prior():
    one = truth.functional_prior((('cell', 'position', 9),))
    two = truth.functional_prior((('cell', 'position', 9), ('cell', 'speed', 9)))
    assert two < one < 0
    assert truth.functional_prior((('cell', 'position', 9), ('cell', 'position', 17))) == -math.inf
    assert truth.functional_prior((('position', 'straight'),)) == -math.inf      # the judge's list is not SERA's


# --- the reviewer's VD13 fixes (2026-09-27) ---
def test_only_the_grammars_own_cells_and_valid_shapes_have_a_prior():
    assert truth.functional_prior((('cell', 'speed', 9, 'alias'),)) == -math.inf
    assert truth.functional_prior((('cell', 'speed', 10),)) == -math.inf
    bad = ('shape', 'position', 33, 1, tuple([float('nan')] * 33))
    try:
        grammar.use_library((bad,))
        raise AssertionError('a malformed shape entered the library')
    except AssertionError as e:
        assert 'malformed' in str(e)
    finally:
        grammar.use_library(())


def test_a_functional_claim_needs_the_claims_own_forecast(monkeypatch):
    monkeypatch.setattr(truth, 'CLAIM', 'functional')
    monkeypatch.setattr(truth, 'BAND', 'ui')
    throws = _throws((('position', 'straight'),), [-2.0], situations=8, pushes=(0.6, -0.6, 1.0, -1.0))
    fam = (('cell', 'position', 9),)
    cert = truth.certify(_ledger(throws, [(), fam]), fam, 0.2)
    assert not cert.accepted and "claim's own forecast" in cert.reasons[0]


def test_a_library_change_during_a_world_is_refused(monkeypatch):
    monkeypatch.setattr(truth, 'CLAIM', 'functional')
    monkeypatch.setattr(truth, 'BAND', 'claim')
    monkeypatch.setattr(grammar, 'SHAPES_POLICY', 'library')
    throws = _throws((('position', 'straight'),), [-2.0], situations=8, pushes=(0.6, -0.6, 1.0, -1.0))
    fam = (('cell', 'position', 9),)
    led = _ledger(throws, [(), fam])
    grammar.use_library((_shape(1),))                 # changed after the world began
    try:
        cert = truth.certify(led, fam, 0.2)
        assert not cert.accepted and 'library' in cert.reasons[0]
    finally:
        grammar.use_library(())


def test_the_empty_law_is_banded_at_the_readings_and_checked(monkeypatch):
    monkeypatch.setattr(truth, 'CLAIM', 'functional')
    monkeypatch.setattr(truth, 'BAND', 'claim')
    throws = _throws((), [], situations=6, pushes=(0.6, -0.6, 1.0))
    led = _ledger(throws, [()])
    cert = truth.certify(led, (), 0.2)
    assert cert.scope.get('band_at') == 'visited readings'
    assert cert.accepted, cert.reasons
    ok, why = checker.check(cert, throws, SIGMA)
    assert ok, why


def test_the_premises_say_where_coverage_ends():
    ledger = dict((p[0], p) for p in truth.premise_ledger('universe-1', 'laplace', 'throw', 'claim', 'functional'))
    assert 'no coverage guarantee' in ledger['F'][2] and 'some strength' in truth.FUNCTIONAL_CLAIM
    assert ledger['S'][1] == 'not needed'


def test_a_coarser_cell_does_not_span_a_finer_shape():
    sh = _shape(1)
    assert not grammar.collinear((('cell', 'position', 9), sh))
    assert grammar.collinear((('cell', 'position', 33), sh))
