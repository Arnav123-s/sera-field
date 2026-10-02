"""N-2 (docs/N2_EXACT_NUMERATOR.md): the lattice numerator is sub-normalized by construction. Written before the code.

Two facts carry the proof:
- the lattice cells partition the whitened space, so their prior masses sum to exactly 1;
- any subset of a normalized mixture, even one chosen after seeing y, is sub-normalized.

The toy here has 2 numbers and 2 readings, so the integral over y can be done by quadrature. The same toy measures
the Laplace numerator's integral: printed, not asserted (that is N-1's question)."""
import math

import numpy as np

from ccops5.core import likelihood as L


def test_cell_masses_partition_the_line():
    for s in (0.007, 0.07, 0.7, 3.0):
        K = np.arange(-int(45 / s) - 1, int(45 / s) + 2)
        total = float(np.exp(L._log_cell_mass(K.astype(float), s)).sum())
        assert abs(total - 1.0) < 1e-12, (s, total)
    far = L._log_cell_mass(np.array([60.0, -60.0]), 0.7)             # deep tails stay finite and symmetric
    assert np.all(np.isfinite(far)) and abs(far[0] - far[1]) < 1e-9


SIG = 0.3
M = np.array([0.2, -0.1])
C = np.diag([0.5 ** 2, 0.4 ** 2])


def _f(th):
    th = np.atleast_2d(th)
    return np.stack([np.sin(2 * th[:, 0]) + th[:, 1], th[:, 0] * th[:, 1] + 0.5 * th[:, 1] ** 2], axis=1)


def _jac(th, h=1e-6):
    return np.stack([(_f(th + e) - _f(th - e))[0] / (2 * h) for e in np.eye(2) * h], axis=1)


SCALE = np.full(2, 1 / SIG)
G0 = _jac(M) * SCALE[:, None]


def _mode(y):
    """A few Gauss-Newton steps from the prior mean: only a guide for which cells to sum (any choice is valid)."""
    th, Ci = M.copy(), np.linalg.inv(C)
    for _ in range(25):
        Gs = _jac(th) * SCALE[:, None]
        r = (y - _f(th)[0]) * SCALE
        H = Gs.T @ Gs + Ci
        th = th + np.linalg.solve(H, Gs.T @ r - Ci @ (th - M))
    Gs = _jac(th) * SCALE[:, None]
    return th, Gs.T @ Gs + Ci


def _laplace(y, th, H):
    r = (y - _f(th)[0]) * SCALE
    d = th - M
    return (-0.5 * float(r @ r) + float(np.log(SCALE).sum()) - math.log(2 * math.pi)
            - 0.5 * float(d @ np.linalg.inv(C) @ d) - 0.5 * np.linalg.slogdet(C)[1] - 0.5 * np.linalg.slogdet(H)[1])


def test_the_lattice_numerator_integrates_to_at_most_one():
    step = 0.04
    grid = np.arange(-3.2, 3.2 + 1e-9, step)
    z_n2 = z_lap = 0.0
    for y0 in grid:
        for y1 in grid:
            y = np.array([y0, y1])
            th, H = _mode(y)
            z_n2 += math.exp(L.lattice_logq(_f, M, C, G0, y, SCALE, th, H)) * step ** 2
            z_lap += math.exp(_laplace(y, th, H)) * step ** 2
    print(f'integral over y: lattice {z_n2:.5f}, Laplace {z_lap:.5f}')
    assert z_n2 <= 1.0 + 2e-3, z_n2                     # quadrature error only; exact bound is 1
    assert z_n2 >= 0.9, z_n2                            # and it is not trivially small (power)


def test_a_subset_chosen_after_seeing_y_never_exceeds_the_whole_mixture():
    """Fact 2, directly: for any y and ANY guide point (even a wrong one) the lattice numerator is at most the full
    mixture over a wide window of cells."""
    rng = np.random.default_rng(0)
    for _ in range(30):
        y = rng.normal(0, 1.5, 2)
        guide = M + rng.normal(0, 1.0, 2)
        _, H = _mode(y)
        got = L.lattice_logq(_f, M, C, G0, y, SCALE, guide, H)
        full = L.lattice_logq(_f, M, C, G0, y, SCALE, M, np.linalg.inv(C) / 400.0, r_eval=60.0, max_points=10 ** 6)
        assert got <= full + 1e-9, (got, full)


def test_a_subset_chosen_adversarially_after_seeing_y_still_integrates_to_at_most_one():
    """independent review T-a: for each y, pick the guide (hence the cells summed) that gives the LARGEST q among 8 candidates."""
    rng = np.random.default_rng(1)
    guides = [M + rng.normal(0, 0.8, 2) for _ in range(7)]
    step = 0.08
    grid = np.arange(-3.2, 3.2 + 1e-9, step)
    z = 0.0
    for y0 in grid:
        for y1 in grid:
            y = np.array([y0, y1])
            th, H = _mode(y)
            z += math.exp(max(L.lattice_logq(_f, M, C, G0, y, SCALE, g, H) for g in [th] + guides)) * step ** 2
    print(f'adversarial subset: integral {z:.5f}')
    assert z <= 1.0 + 5e-3, z


def test_the_linearized_forecast_integrates_to_one_on_a_nonlinear_toy():
    """independent review T-b: N-2b is a Gaussian in y whatever the paths do, so its integral is 1 (quadrature error only)."""
    step = 0.04
    grid = np.arange(-4.0, 4.0 + 1e-9, step)
    f0, G = _f(M)[0], _jac(M)
    z = sum(math.exp(L.linearized_logq(f0, G, C, np.array([a, b]), SCALE)) for a in grid for b in grid) * step ** 2
    assert abs(z - 1.0) < 2e-3, z


def test_one_exploding_cell_leaves_the_numerator_finite():
    """independent review N2-a: a path that explodes (inf or nan readings) drops only its own cell."""
    y = np.array([0.3, -0.2])
    th, H = _mode(y)
    good = L.lattice_logq(_f, M, C, G0, y, SCALE, th, H)
    calls = []

    def bad(theta):
        out = _f(theta)
        calls.append(len(out))
        out[0] = np.nan if len(calls) == 1 else out[0]
        return out
    got = L.lattice_logq(bad, M, C, G0, y, SCALE, th, H)
    assert np.isfinite(got) and got <= good + 1e-12


def test_a_near_singular_prior_drops_the_component_without_raising():
    """independent review N2-b: tight posteriors and collinear columns give a near-singular C; the Woodbury form must not raise."""
    Cs = np.array([[1.0, 1.0], [1.0, 1.0]]) * 1e-3              # singular
    got = L.linearized_logq(_f(M)[0], _jac(M), Cs, np.array([0.1, 0.1]), SCALE)
    assert got == -math.inf or np.isfinite(got)
