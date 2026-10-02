"""Decision 16 (the author, 2026-10-01; review 11): a ramp ('ramp', dimension, 9) - one strength times SERA's own
expression, clipped at its range - as a direct simulator column (kind 10), checked independently, functional only."""
import math

import numpy as np
import pytest

from ccops5.core import checker, grammar as G, paths, truth

DIMS = ['dim:x@4', 'dim:x.x.x.mul.mul@4', 'dim:1.x.x.x.mul.mul.add@6', 'dim:x.v.mul@6', 'dim:t@4',
        'dim:0.x.sub@4']


def _states(n=400, seed=0):
    r = np.random.default_rng(seed)
    return r.uniform(-3.5, 3.5, n), r.uniform(-7, 7, n), r.uniform(0, 2.2, n)


def test_the_schema_is_exact():
    assert G.is_ramp(('ramp', 'dim:x.x.x.mul.mul@4', 9))
    for bad in (('ramp', 'position', 9), ('ramp', 'dim:x.x.x.mul.mul@4', 33), ('ramp', 'dim:x.x.x.mul.mul@4', True),
                ('ramp', 'dim:x.x.x.mul.mul@4', 9.0), ('ramp', 'dim:x.x.x.mul.mul@4', 9, 0), ('ramp', 'dim:x.1.lt@4', 9),
                ('ramp', 'dim:x.x.1.if@4', 9), ('ramp', 'dim:x.y@4', 9), ['ramp', 'dim:x@4', 9]):
        assert not G.is_ramp(bad), bad
        assert truth._functional_term(bad) == 0.0
    with pytest.raises(ValueError):
        G.code(('ramp', 'position', 9))
    assert G.log_prior((('ramp', 'dim:x@4', 9),)) == -math.inf          # functional claims only


def test_its_prior_is_its_own_share_and_no_old_prior_changes():
    d = 'dim:x.x.x.mul.mul@4'
    assert truth._functional_term(('ramp', d, 9)) == pytest.approx(truth.RAMP_WEIGHT * G.dim_prior(d))
    assert truth._functional_term(('cell', d, 9)) == pytest.approx(0.5 * G.CELL_K_WEIGHT[9] * truth.DIM_SHARE
                                                                    * G.dim_prior(d))
    assert truth.functional_prior((('ramp', d, 9), ('cell', d, 9))) == -math.inf     # one input, one term
    assert truth.functional_prior((('ramp', d, 9), ('cell', 'speed', 9))) > -math.inf


def test_the_direct_column_is_the_clipped_expression_three_ways():
    x, v, t = _states()
    for d in DIMS:
        R = G.input_range(d)[1]
        want = np.clip(G.dim_eval(d, x, v, t), -R, R)
        sim = np.array([paths.term_t(10, G.input_code(d), 0, a, b, c, 1.0, 1.0) for a, b, c in zip(x, v, t)])
        mine = checker._grown_np(('ramp', d, 9), x, v, t)[0]
        assert np.max(np.abs(sim - want)) < 1e-12 and np.max(np.abs(mine - want)) < 1e-12, d
        knots = np.linspace(-R, R, 9)[1:-1]            # every former interior knot: the slope is the line's
        if d == 'dim:x@4':
            for k in knots:
                assert paths._dterm(10, G.input_code(d), 0, k, 0.3, 1.0, 1.0, 0.0) == (1.0, 0.0)
    assert checker._grown_terms_agree(tuple(('ramp', d, 9) for d in DIMS), dict(x=(-3, 3), v=(-6, 6)))


def test_its_slope_is_the_chain_rule_inside_and_nothing_beyond():
    x, v, t = _states(200, 1)
    for d in DIMS:
        a = G.input_code(d)
        R = G.input_range(d)[1]
        for xi, vi, ti in zip(x, v, t):
            u = float(G.dim_eval(d, np.array([xi]), np.array([vi]), np.array([ti]))[0])
            dx, dv = paths._dterm(10, a, 0, xi, vi, 1.0, 1.0, ti)
            if abs(abs(u) - R) < 1e-3 * max(1.0, R):
                continue                                # the kink at the ends: the convention, not tested here
            h = 1e-6
            fx = (paths.term_t(10, a, 0, xi + h, vi, ti, 1., 1.) - paths.term_t(10, a, 0, xi - h, vi, ti, 1., 1.)) / 2 / h
            fv = (paths.term_t(10, a, 0, xi, vi + h, ti, 1., 1.) - paths.term_t(10, a, 0, xi, vi - h, ti, 1., 1.)) / 2 / h
            assert abs(dx - fx) < 1e-5 * max(1.0, abs(fx)) and abs(dv - fv) < 1e-5 * max(1.0, abs(fv)), (d, xi, vi)
            if abs(u) > R:
                assert (dx, dv) == (0.0, 0.0)


def test_32_hats_and_the_ramp_span_the_whole_33_knot_curve():
    d = 'dim:x.x.x.mul.mul@4'
    fam = (('ramp', d, 9),)
    assert truth.functional_checks(fam) == [('hats', d, 33, (0,))]
    R = G.input_range(d)[1]
    u = np.linspace(-1.3 * R, 1.3 * R, 400)
    x = np.cbrt(u)
    z = np.zeros_like(x)
    cols = checker._column_np(('ramp', d, 9), x, z, z) + checker._column_np(('hats', d, 33, (0,)), x, z, z)
    assert np.linalg.matrix_rank(np.stack(cols, 1), tol=1e-9) == 33
    assert G.collinear((('ramp', d, 9), ('cell', d, 17)))
    assert G.contains((('cell', d, 33),), (('ramp', d, 9),)) and not G.contains((('ramp', d, 9),), (('cell', d, 33),))


def test_a_reading_outside_its_range_refuses_it_in_the_judge_and_in_the_checker():
    class Throw:                                        # two readings: the second beyond x^3's range at r=4 (1)
        def __init__(self, x):
            self.x, self.v = np.array(x, float), np.zeros(len(x))
    fam = (('ramp', 'dim:x.x.x.mul.mul@4', 9),)
    inside, outside = [Throw([0.5, 0.9])], [Throw([0.5, 1.2])]
    assert truth.ramp_outside(inside, fam) == [] and truth.ramp_outside(outside, fam) == list(fam)
    assert not checker._ramp_outside_np(fam, inside) and checker._ramp_outside_np(fam, outside)


def test_a_nan_or_infinite_ramp_value_fails_the_agreement_check():
    """review 14 F2: a simulator column that is not finite fails, and infinity is no clipped value."""
    from unittest.mock import patch
    family = (('ramp', 'dim:x@4', 9),)
    with patch.object(paths, 'term_t', return_value=np.nan):
        assert not checker._grown_terms_agree(family, dict(x=(-0.1, 0.1), v=(-0.1, 0.1)))
    big = 'dim:x.x.x.x.x.x.x.mul.mul.mul.mul.mul.mul@10'
    col = checker._grown_np(('ramp', big, 9), np.array([1e50]), np.zeros(1), np.zeros(1))[0]
    assert np.isnan(col[0])
