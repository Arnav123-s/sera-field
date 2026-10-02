"""Decision D9 (approved 2026-09-24): the claim threshold is log(1 / (alpha * pi(claim))).

pi puts 0.9 uniformly on the 67 base families and 0.1 on the open grammar: one invented term (products of shapes,
powers of an input on a 0.1 grid, drives in time on a 0.1 grid), alone or with one base idea, weighted by its
description length. Written before the code.
"""
import math
import unittest

from ccops5.core import grammar

ALPHA = 1e-3


class D9Tests(unittest.TestCase):
    def test_base_families_share_point_nine(self):
        base = grammar.space()
        self.assertEqual(len(base), 67)
        total = sum(math.exp(grammar.log_prior(f)) for f in base)
        self.assertAlmostEqual(total, 0.9, places=12)
        for f in base:
            self.assertAlmostEqual(grammar.log_prior(f), math.log(0.9 / 67), places=12)

    def test_base_threshold(self):
        self.assertAlmostEqual(grammar.log_threshold((('speed', 'straight'),), ALPHA),
                               math.log(67 / (0.9 * ALPHA)), places=12)

    def test_open_grammar_shares_point_one(self):
        opens = grammar.OPEN_TERMS
        self.assertEqual(len(opens), 25 + 2 * 37 + 2 * 80)
        self.assertEqual(len(set(opens)), len(opens))
        total = 0.0
        for t in opens:
            total += math.exp(grammar.log_prior((t,)))
            for i in grammar.IDEAS:
                total += math.exp(grammar.log_prior((t, i)))
        # truth-v2 (pre-registered, docs/B4_GROWTH.md revision 1, B4-4): truth-v1's open terms now share 0.05 and the
        # grown terms (cells, pieces, piece products) the other 0.05, so the whole open grammar still shares 0.1
        # (tests/core/test_grammar_v2.py checks the total is 1). On truth-v1 this value is 0.1. independent review reviews.
        self.assertAlmostEqual(total, 0.05, places=12)

    def test_not_formable_has_no_prior(self):
        two_open = (('drive', 'sin', 3.5), ('product', 'straight', 'straight'))
        self.assertEqual(grammar.log_prior(two_open), -math.inf)
        self.assertEqual(grammar.log_threshold(two_open, ALPHA), math.inf)
        self.assertEqual(grammar.log_prior((('power', 'speed', 2.0),)), -math.inf)   # equals a base idea

    def test_invented_claims_pay_their_length(self):
        prod = grammar.log_threshold((('product', 'straight', 'straight'),), ALPHA)
        power = grammar.log_threshold((('power', 'speed', 1.5),), ALPHA)
        drive = grammar.log_threshold((('drive', 'sin', 3.5),), ALPHA)
        paired = grammar.log_threshold(grammar.canonical((('drive', 'sin', 3.5), ('speed', 'straight'))), ALPHA)
        base = grammar.log_threshold((('speed', 'straight'),), ALPHA)
        self.assertLess(base, prod)
        self.assertLess(prod, power)
        self.assertLess(power, drive)
        self.assertAlmostEqual(paired - drive, math.log(11), places=12)

    def test_space_accepts_open_terms_in_a_fixed_order(self):
        extra = (('drive', 'sin', 3.5), ('power', 'speed', 1.3))
        s1 = grammar.space(inventions=extra)
        s2 = grammar.space(inventions=tuple(reversed(extra)))
        self.assertEqual(s1, s2)
        self.assertIn(grammar.canonical((('drive', 'sin', 3.5),)), s1)
        self.assertEqual(len(s1), 1 + 13 + 13 * 12 // 2)


if __name__ == '__main__':
    unittest.main()
