"""Decision 14 (plan revision 6.2; the author: "it can improve its own drawing skills and get more abilities to
perceive"): a lens looks at one input 2^j times closer, at a window of the lattice of half windows, and a curve on it
has its knots across the window (constant beyond it):
  - its name, the simulator's input code and its window agree (grammar, paths), and malformed names are no input;
  - the checker's own drawing of a lens curve equals the simulator's, and the simulator's slope is its derivative;
  - the lens code is a code: with the whole inputs' curves, the functional code of one-term laws stays within its half;
  - a law on a lens is checked on the window and on its whole input (less the hats inside the window).
"""
import math

import numpy as np

from ccops5.core import checker, grammar, paths, truth


def test_lens_names_codes_and_windows_agree_with_the_simulator():
    for inp in ('speed@4:16', 'position@1:0', 'time@6:128', 'speed@6:64', 'position@3:5'):
        base, j, m = grammar.lens(inp)
        a = grammar.input_code(inp)
        lo, hi = grammar.input_range(inp)
        plo, phi_ = paths._lens(a)
        assert abs(lo - plo) < 1e-12 and abs(hi - phi_) < 1e-12
        assert a % 3 == grammar.CELL_INPUTS.index(base) and grammar.is_lens(inp)
    assert grammar.input_range('speed@4:16') == (-0.375, 0.375)
    assert grammar.input_range('speed') == (-6.0, 6.0) and not grammar.is_lens('speed')
    for bad in ('speed@7:0', 'speed@0:0', 'speed@4:33', 'speed@04:16', 'spin@1:1', 'speed@4', 'speed@4:-1',
                'speed@4:16 ', ('speed',), None):
        assert not grammar.is_input(bad), bad


def _sim_cols(term, X, V, T):
    return [np.array([paths.term_t(k, a, b, x, v, t, 1.0, 1.0) for x, v, t in zip(X, V, T)])
            for k, a, b in grammar.term_codes(term)]


def test_the_checker_draws_lens_curves_as_the_simulator_does():
    rng = np.random.default_rng(0)
    for inp in ('speed@4:16', 'position@2:3', 'time@3:0', 'speed@6:127'):
        lo, hi = grammar.input_range(inp)
        s = np.concatenate([np.linspace(lo - 0.2 * (hi - lo), hi + 0.2 * (hi - lo), 97), rng.uniform(lo, hi, 50)])
        base = grammar.base_input(inp)
        X = s if base == 'position' else rng.uniform(-3, 3, s.size)
        V = s if base == 'speed' else rng.uniform(-6, 6, s.size)
        T = s if base == 'time' else rng.uniform(0, 2, s.size)
        for K in (9, 17, 33):
            term = ('cell', inp, K)
            mine = checker._grown_np(term, X, V, T)
            theirs = _sim_cols(term, X, V, T)
            assert len(mine) == len(theirs) == K
            assert all(np.max(np.abs(a - b)) < 1e-12 for a, b in zip(mine, theirs))
            assert np.allclose(sum(mine), 1.0)                         # its hats sum to one, beyond the window too


def test_a_lens_hat_moves_with_its_input():
    a = grammar.input_code('speed@4:16')
    b = 2 * 100 + 17                                                    # the 33-knot grid, knot 17 (v = 0.0234)
    for v in (0.03, 0.01, -0.1, 0.2):
        h = 1e-7
        fd = (paths.term_t(7, a, b, 0.5, v + h, 0.3, 1.0, 1.0) - paths.term_t(7, a, b, 0.5, v - h, 0.3, 1.0, 1.0)) / (2 * h)
        dx, dv = paths._dterm(7, a, b, 0.5, v, 1.0, 1.0)
        assert dx == 0.0 and abs(dv - fd) < 1e-5 * max(1.0, abs(fd))
    at = grammar.input_code('time@2:1')
    assert paths._dterm(7, at, 5, 0.5, 0.5, 1.0, 1.0) == (0.0, 0.0)     # time does not move with the state


def test_the_lens_code_is_a_code():
    for base in grammar.CELL_INPUTS:
        total = sum(grammar.lens_prior(grammar.lens_name(base, j, m)) for j in grammar.LENS_J
                    for m in range(2 ** (j + 1) + 1))
        assert total <= 63 / 64 + 1e-12
    whole = sum(truth._functional_term(('cell', i, K)) for i in grammar.CELL_INPUTS for K in grammar.CELL_KS)
    lensed = sum(truth._functional_term(('cell', grammar.lens_name(i, j, m), K)) for i in grammar.CELL_INPUTS
                 for K in grammar.CELL_KS for j in grammar.LENS_J for m in range(2 ** (j + 1) + 1))
    assert whole + lensed <= 0.5 + 1e-12                                # the free curves' half of the code
    assert truth.functional_prior((('cell', 'speed@4:16', 33),)) > -math.inf
    assert truth.functional_prior((('cell', 'speed@4:16', 33), ('cell', 'speed', 9))) == -math.inf   # one input
    assert truth.functional_prior((('cell', 'speed@4:16', 33), ('cell', 'position', 9))) > -math.inf
    assert truth.functional_prior((('cell', 'speed@9:16', 33),)) == -math.inf
    assert truth.functional_prior((('cell', 'speed@4:16', 10),)) == -math.inf
    assert grammar.log_prior((('cell', 'speed@4:16', 33),)) == -math.inf       # never a rival in the old space


def test_a_lens_law_is_checked_on_its_window_and_its_whole_input():
    checks = truth.functional_checks((('cell', 'speed@4:16', 9),))
    assert checks[0] == ('hats', 'speed@4:16', 33, tuple(range(0, 33, 4)))
    assert checks[1] == ('hats', 'speed', 33, (16,))       # the whole input's hat at 0 lies inside [-0.375, 0.375]
    assert truth.functional_checks((('cell', 'speed@4:16', 33),)) == [('hats', 'speed', 33, (16,))]
    assert truth.functional_checks((('cell', 'speed@6:64', 33),)) == [('hats', 'speed', 33, ())]
    both = truth.functional_checks((('cell', 'position', 9), ('cell', 'speed@4:16', 33)))
    assert ('hats', 'speed', 33, (16,)) in both and any(c[1] == 'position' for c in both)


# --- Decision 15 (the author: "more dimensions of perception; let SERA improve the number of dimensions it thinks in") ---
DIMS = ('dim:x.v.mul@6', 'dim:v.t.add@7', 'dim:x.v.lt.x.v.if@6', 'dim:x.1.add.v.mul@8', 'dim:t.x.sub@5')


def test_dimension_names_are_well_formed_programs():
    for d in DIMS:
        toks, r = grammar.dim(d)
        assert grammar.is_input(d) and grammar.is_dim(d) and not grammar.is_lens(d) and grammar.base_input(d) == d
        assert grammar.input_range(d) == (-2.0 ** (r - 4), 2.0 ** (r - 4))
        assert grammar.input_code(d) >= paths.DIM_FLAG
    for bad in ('dim:x.mul@6', 'dim:x.v.mul@11', 'dim:0.1.add@4', 'dim:x.v.pow@4', 'dim:x.v@4', 'dim:x.v.mul@06',
                'dim:@4', 'dim:' + '.'.join(['x'] * 8 + ['add'] * 7) + '@6'):
        assert not grammar.is_input(bad), bad
    assert grammar.describe_input('dim:x.v.mul@6') == '(position x speed)'


def test_a_dimension_is_the_same_program_in_the_simulator_the_grammar_and_the_checker():
    rng = np.random.default_rng(1)
    x, v, t = rng.uniform(-3, 3, 200), rng.uniform(-6, 6, 200), rng.uniform(0, 2, 200)
    for d in DIMS:
        a = grammar.input_code(d)
        sim = np.array([paths._dim(a, xi, vi, ti)[0] for xi, vi, ti in zip(x, v, t)])
        assert np.allclose(sim, grammar.dim_eval(d, x, v, t), atol=1e-12)
        assert np.allclose(sim, checker._dim_np(d[4:].split('@')[0], x, v, t), atol=1e-12)
        for K in (9, 33):
            term = ('cell', d, K)
            mine = checker._grown_np(term, x, v, t)
            theirs = _sim_cols(term, x, v, t)
            assert all(np.max(np.abs(p - q)) < 1e-12 for p, q in zip(mine, theirs))


def test_a_dimension_moves_with_the_state_by_the_chain_rule():
    for d in ('dim:x.v.mul@6', 'dim:x.1.add.v.mul@8'):
        a = grammar.input_code(d)
        for (x, v, t) in ((0.7, -1.3, 0.4), (-1.1, 2.2, 1.5)):
            for b in (2 * 100 + 10, 2 * 100 + 20, 5):
                h = 1e-7
                fx = (paths.term_t(7, a, b, x + h, v, t, 1.0, 1.0) - paths.term_t(7, a, b, x - h, v, t, 1.0, 1.0)) / (2 * h)
                fv = (paths.term_t(7, a, b, x, v + h, t, 1.0, 1.0) - paths.term_t(7, a, b, x, v - h, t, 1.0, 1.0)) / (2 * h)
                dx, dv = paths._dterm(7, a, b, x, v, 1.0, 1.0, t)
                assert abs(dx - fx) < 1e-5 * max(1.0, abs(fx)) and abs(dv - fv) < 1e-5 * max(1.0, abs(fv))


def test_the_code_with_dimensions_and_more_parts_is_still_a_code():
    assert grammar.dim_prior('dim:x.v.mul@6') == 11.0 ** -4 / len(grammar.DIM_R)
    assert truth.functional_prior((('cell', 'dim:x.v.mul@6', 17),)) > -math.inf
    three = (('cell', 'dim:x.v.mul@6', 17), ('cell', 'position', 9), ('cell', 'time', 9))
    assert truth.functional_prior(three) > -math.inf
    assert truth.functional_prior(three + (('cell', 'speed', 9), ('shape', 'speed', 33, 1, (0.0,) * 33))) == -math.inf
    assert sum(truth.FUNCTIONAL_PARTS.values()) + truth.FUNCTIONAL_EMPTY <= 1.0 + 1e-12
    assert truth.functional_checks((('cell', 'dim:x.v.mul@6', 9),)) == [('hats', 'dim:x.v.mul@6', 33,
                                                                          tuple(range(0, 33, 4)))]


def test_review_vd14_fixes():
    """reviewer VD14: no zero or non-integer library shapes; no certificates on dimensions with a switch (lt, if) yet; exact
    integer grids only."""
    for bad in ((('shape', 'speed', 33, 1, (0.0,) * 33),), (('shape', 'speed', 33.0, 1, (1.0,) * 33),),
                (('shape', 'speed', 33, 1.0, (1.0,) * 33),)):
        try:
            grammar.use_library(bad)
            raise RuntimeError('a malformed shape entered the library')
        except AssertionError as e:
            assert 'malformed' in str(e)
        finally:
            grammar.use_library(())
    assert truth.functional_prior((('cell', 'dim:x.v.lt.x.v.if@6', 17),)) == -math.inf
    assert truth.functional_prior((('cell', 'dim:x.v.mul@6', 17),)) > -math.inf
    assert truth.functional_prior((('cell', 'speed', 9.0),)) == -math.inf
