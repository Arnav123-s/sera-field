"""Exact forward-mode derivatives of the RK4 path (compute batch K, 2026-09-24).

The finite-difference Jacobian re-simulates the path once per coefficient (45% of ledger time, profile of
088cd52). jacobian_exact carries d(x, v)/d(theta) through the same RK4 stages in one pass. Its readings must be
bit-identical to simulate_program, and its derivatives must agree with finite differences to their accuracy.
"""

import unittest

import numpy as np

from ccops5.core import grammar, paths

T0, T1, F = np.array([0.0, 0.9]), np.array([0.4, 1.1]), np.array([0.8, -0.5])
SX, SV = 0.7, 0.9
FAMILIES = [
    [(0, 1, 0)],                               # speed straight
    [(0, 0, 0), (0, 1, 1)],                    # position straight + speed growing
    [(0, 0, 2), (0, 1, 3)],                    # steps, cubic
    [(0, 1, 4), (0, 2, 0)],                    # wave, constant
    [(1, 0, 0), (1, 1, 0), (1, 0, 1), (1, 1, 1), (1, 2, 0), (1, 0, 2), (1, 2, 1), (1, 1, 2), (1, 2, 2)],
    [(2, 0, 0), (3, 0, 0)],                    # v^1.5 drag, x*v
    [(4, 0, 0), (4, 1, 4), (4, 3, 1)],         # invented products
    [(5, 1, 15), (5, 0, 25), (5, 1, 3)],       # powers, including p < 1
    [(6, 0, 20), (6, 1, 35)],                  # drives
]


def arrays(fam):
    return tuple(np.array([t[i] for t in fam], np.int64) for i in range(3))


def coefs(n, seed):
    return np.random.default_rng(seed).uniform(-0.6, 0.6, n)


class ExactJacobianTests(unittest.TestCase):
    def test_readings_are_bit_identical(self):
        for k, fam in enumerate(FAMILIES):
            kind, a, b = arrays(fam)
            c = coefs(len(fam), k)
            xs, vs = paths.simulate_program(T0, T1, F, 1.3, kind, a, b, c, SX, SV, 0.5, 0.2)
            y, _ = paths.jacobian_exact(T0, T1, F, 1.3, kind, a, b, c, SX, SV, 0.5, 0.2)
            self.assertTrue(np.array_equal(y, np.concatenate([xs, vs])), fam)

    def test_derivatives_match_central_differences(self):
        for k, fam in enumerate(FAMILIES):
            kind, a, b = arrays(fam)
            c = coefs(len(fam), 100 + k)
            mu = 1.3
            _, J = paths.jacobian_exact(T0, T1, F, mu, kind, a, b, c, SX, SV, 0.5, 0.2)
            self.assertEqual(J.shape, (2 * paths.N_OBS, len(fam) + 1))
            for j in range(len(fam) + 1):
                h = 1e-6
                cp, cm, mp, mm = c.copy(), c.copy(), mu, mu
                if j < len(fam):
                    cp[j] += h
                    cm[j] -= h
                else:
                    mp, mm = mu + h, mu - h
                yp = np.concatenate(paths.simulate_program(T0, T1, F, mp, kind, a, b, cp, SX, SV, 0.5, 0.2))
                ym = np.concatenate(paths.simulate_program(T0, T1, F, mm, kind, a, b, cm, SX, SV, 0.5, 0.2))
                fd = (yp - ym) / (2 * h)
                err = np.max(np.abs(J[:, j] - fd)) / max(1.0, np.max(np.abs(fd)))
                self.assertLess(err, 1e-5, (fam, j, err))

    def test_clipped_runaway_has_zero_force_derivatives_after_the_clip(self):
        kind, a, b = arrays([(0, 0, 3)])
        y, J = paths.jacobian_exact(T0, T1, F, 1.0, kind, a, b, np.array([500.0]), SX, SV, 0.0, 0.0)
        self.assertTrue(np.all(np.isfinite(J)))
        self.assertTrue(np.all(np.isfinite(y)))

    def test_runaway_law_gets_a_finite_jacobian_from_the_likelihood(self):
        """The band basis P2(x)P2(v) at a small scale with a large trial coefficient runs away; exact
        sensitivities reach 1e18+ before the clip (overflow seen on the x*v world, 2026-09-24).
        likelihood._jac must fall back to finite differences there."""
        from types import SimpleNamespace
        from ccops5.core import likelihood as L
        from ccops5.core.worlds import Action
        kind, a, b = arrays([(1, 2, 2)])
        model = L.Model(kind, a, b, 0.2, 0.2)
        throw = SimpleNamespace(action=Action(((0.0, 0.4, 1.0),)), situation=0)
        coef = np.array([-40.0])
        y_exact, J_exact = paths.jacobian_exact(*L._arrays(throw.action), 1.0, kind, a, b, coef, 0.2, 0.2, 0.0, 0.0)
        self.assertFalse(np.all(np.isfinite(J_exact)) and np.max(np.abs(J_exact)) < 1e12)   # the premise
        y, J = L._jac(model, coef, 1.0, throw)
        self.assertTrue(np.all(np.isfinite(J)) and np.max(np.abs(J)) < 1e12)
        self.assertTrue(np.array_equal(y, y_exact))

    def test_grammar_codes_are_covered(self):
        kinds = {grammar.code(t)[0] for t in grammar.TERMS}
        self.assertLessEqual(kinds, {0, 4, 5, 6})


if __name__ == '__main__':
    unittest.main()
