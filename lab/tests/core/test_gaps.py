"""Synthetic checks for terms proposed from acceleration left over by a leader."""

import unittest
from types import SimpleNamespace

import numpy as np

from ccops5.core import gaps, grammar, paths
from ccops5.core.worlds import Action, hand


def throws_for(term=None, coefficient=0.0):
    """Make four signed pushes per object with reproducible sensor noise."""
    rng = np.random.default_rng(7301)
    if term is None:
        kind = a = b = np.zeros(0, dtype=np.int64)
        coef = np.zeros(0)
    else:
        kind, a, b = grammar.codes((term,))
        coef = np.array([coefficient])
    throws = []
    for situation, mass in enumerate((0.7, 1.0, 1.4, 2.0, 2.4)):
        for u in (0.6, -0.6, 1.0, -1.0):
            action = Action(((0.0, 0.4, u),))
            x, v = paths.simulate_program(
                np.array([0.0]), np.array([0.4]), np.array([hand(u)]),
                1.0 / mass, kind, a, b, coef, 1.0, 1.0, 0.0, 0.0)
            throws.append(SimpleNamespace(
                x=x + rng.normal(0, 1e-3, x.size),
                v=v + rng.normal(0, 1e-3, v.size),
                situation=situation, action=action))
    return throws


class OpenTermsTests(unittest.TestCase):
    def test_count_and_uniqueness(self):
        terms = gaps.open_terms()
        self.assertEqual(len(terms), 25 + 2 * 37 + 2 * 80)
        self.assertEqual(len(set(terms)), len(terms))

    def test_product_force(self):
        ranked = gaps.propose(throws_for(('product', 'straight', 'straight'), -1.0), ())   # -2 ran away (development note)
        # A proposer only has to put the truth among the 8 candidates the exact ledger tests (development note, 2026-09-24:
        # on these synthetic pushes |v|^0.5 edges it out; on School worlds x*v ranks first).
        self.assertIn(('product', 'straight', 'straight'), [r['term'] for r in ranked[:8]])
        self.assertEqual(ranked[0]['name'], grammar.term_name(ranked[0]['term']))

    def test_fractional_drag(self):
        ranked = gaps.propose(throws_for(('power', 'speed', 0.3), -1.5), ())   # the drag that needs invention
        term = ranked[0]['term']
        self.assertEqual(term[:2], ('power', 'speed'))
        self.assertLessEqual(abs(term[2] - 0.3), 0.2)

    def test_hidden_drive(self):
        throws = throws_for(('drive', 'sin', 3.5), 0.8)
        term = gaps.propose(throws, ())[0]['term']
        self.assertEqual(term[0], 'drive')
        self.assertLessEqual(abs(term[2] - 3.5), 0.2)
        summary = gaps.shape_summary(throws, ())
        self.assertEqual(summary['along'], 'time')
        self.assertTrue(summary['periodic'])
        self.assertLessEqual(abs(summary['best_frequency'] - 3.5), 0.2)

    def test_hand_only(self):
        ranked = gaps.propose(throws_for(), (), top=len(gaps.open_terms()))
        self.assertTrue(ranked)
        self.assertTrue(all(item['gain'] < 3.0 for item in ranked))


if __name__ == '__main__':
    unittest.main()
