"""The band's smooth basis must not repeat a term the family already has (user-approved truth fix, 2026-09-24).

Seed 1 T5 (fca11f5): on x*v worlds the invented ('product', 'straight', 'straight') equals the basis function
P1(x)P1(v). With both in one fit, the coefficient is unidentified and the band blew up to 42,773 against eps 0.2
(band_dup.py: 2.35 without the duplicate).
"""

import unittest

from ccops5.core import grammar, truth
from tests.core.test_gaps import throws_for

XV = ('product', 'straight', 'straight')


class BasisDuplicateTests(unittest.TestCase):
    def test_xv_drops_p1p1(self):
        self.assertNotIn((1, 1), truth.basis_for((XV,)))
        self.assertEqual(len(truth.basis_for((XV,))), len(truth.BASIS) - 1)

    def test_xv_with_base_idea_drops_both(self):
        basis = truth.basis_for((('position', 'straight'), XV))
        self.assertNotIn((1, 1), basis)
        self.assertNotIn((1, 0), basis)

    def test_other_products_keep_the_whole_basis(self):
        for term in grammar.PRODUCTS:
            if term != XV:
                self.assertEqual(truth.basis_for((term,)), truth.BASIS, term)

    def test_base_families_unchanged(self):
        for family in grammar.space():
            expected = tuple(d for d in truth.BASIS
                             if d not in {truth.DUPLICATE[i] for i in family if i in truth.DUPLICATE})
            self.assertEqual(truth.basis_for(family), expected, family)

    def test_band_model_has_no_copy_of_xv(self):
        scope = truth.scope_of(throws_for(XV, 0.8))
        m = truth.model_of((XV,), extra_basis=True, scope=scope)
        terms = list(zip(m.kind.tolist(), m.a.tolist(), m.b.tolist()))
        self.assertIn((4, 0, 0), terms)             # x*v, as the family's own term
        self.assertNotIn((1, 1, 1), terms)          # P1(x)P1(v), the same function again


if __name__ == '__main__':
    unittest.main()
