"""Decision D10 (approved 2026-09-24, amends D2): a certificate speaks only for the (position, speed) cells its
throws visited (at least 2 readings), on the GRID x GRID lattice over the 2nd-98th percentile box. The band is taken
over those cells only. Written before the code.
"""
import unittest

import numpy as np

from ccops5.core import curriculum, truth


class D10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = curriculum.make_world(1, 'rubbing', 0, situations=4, tricks=0.0)
        cls.scope = truth.scope_of(cls.w.throws)

    def test_scope_lists_visited_cells(self):
        cells = self.scope['cells']
        self.assertTrue(cells)
        self.assertEqual(list(cells), sorted(set(cells)))
        for i, j in cells:
            self.assertTrue(0 <= i < truth.GRID and 0 <= j < truth.GRID)
        counts = {}
        for t in self.w.throws:
            for x, v in zip(t.x, t.v):
                c = truth.cell_of(self.scope, x, v)
                if c is not None:
                    counts[c] = counts.get(c, 0) + 1
        self.assertEqual(set(cells), {c for c, n in counts.items() if n >= 2})

    def test_scope_is_deterministic(self):
        self.assertEqual(truth.scope_of(self.w.throws), self.scope)

    def test_band_over_cells_is_at_most_band_over_box(self):
        fam, sigma = self.w.truth, self.w.sigma
        cells = truth.band_of(self.w.throws, fam, sigma, self.scope, 1e-3 / 67)
        box_scope = {k: v for k, v in self.scope.items() if k != 'cells'}
        box = truth.band_of(self.w.throws, fam, sigma, box_scope, 1e-3 / 67)
        self.assertLessEqual(cells, box + 1e-12)
        self.assertTrue(np.isfinite(cells))


if __name__ == '__main__':
    unittest.main()
