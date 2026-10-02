"""Invention's proposal list (written before the fix, 2026-09-24, session 2).

Seed 1 T5: in v^p worlds (true force |v|^0.2 sign(v)) the proposals never held p = 0.2. The mind merged the terms
that fit the leader's leftover with those that fit the hand-only leftover, but capped the total at 8 and filled it
from the first list, so the hand-only list never contributed. The merge must take from both lists.
"""
import unittest

from ccops5.core import gaps, mind

from tests.core.test_gaps import throws_for


def p(term, gain):
    return {'term': term, 'gain': gain, 'name': str(term)}


class MergeTest(unittest.TestCase):
    def test_both_lists_contribute_when_the_first_is_full(self):
        leader = [p(('power', 'position', 0.1 * k), 10.0 - k) for k in range(1, 9)]
        hand = [p(('power', 'speed', 0.2), 50.0)] + [p(('drive', 'sin', 1.0 * k), 1.0) for k in range(1, 8)]
        merged = mind.merge_proposals(leader, hand, top=8)
        terms = [q['term'] for q in merged]
        self.assertIn(('power', 'speed', 0.2), terms)
        self.assertEqual(len(terms), 8)
        self.assertEqual(sum(t in [q['term'] for q in leader] for t in terms), 4)

    def test_duplicates_counted_once_and_space_refilled(self):
        shared = p(('product', 'straight', 'straight'), 5.0)
        leader = [shared] + [p(('power', 'position', 0.1 * k), 1.0) for k in range(1, 8)]
        hand = [shared] + [p(('drive', 'cos', 1.0 * k), 1.0) for k in range(1, 8)]
        terms = [q['term'] for q in mind.merge_proposals(leader, hand, top=8)]
        self.assertEqual(len(terms), len(set(terms)))
        self.assertEqual(len(terms), 8)

    def test_short_lists(self):
        self.assertEqual(len(mind.merge_proposals([p(('power', 'speed', 0.5), 1.0)], [], top=8)), 1)


class BracketTest(unittest.TestCase):
    """The fast tier's exponent is biased toward 0.5 for |v|^p with p in 0.2-0.4 (it fits central-difference
    accelerations, which smear the kink at v = 0; measured 2026-09-24). So the exact tier gets the neighbours of
    each input's leading exponent and chooses p by evidence. D9's prior already pays for any term of the open
    grammar, so adding candidates does not weaken "sure"."""

    def test_neighbours_of_the_leading_exponent_are_added(self):
        props = [p(('power', 'speed', 0.5), 1.2), p(('product', 'straight', 'straight'), 0.3)]
        terms = [q['term'] for q in mind.bracket_exponents(props, span=0.3)]
        for q in (0.2, 0.3, 0.4, 0.6, 0.7, 0.8):
            self.assertIn(('power', 'speed', q), terms)
        self.assertEqual(len(terms), len(set(terms)))

    def test_integer_exponents_and_grid_edges_are_skipped(self):
        terms = [q['term'] for q in mind.bracket_exponents([p(('power', 'position', 0.8), 1.0)], span=0.3)]
        self.assertNotIn(('power', 'position', 1.0), terms)
        self.assertTrue(all(t in gaps.open_terms() for t in terms))
        edge = [q['term'] for q in mind.bracket_exponents([p(('power', 'speed', 0.1), 1.0)], span=0.3)]
        self.assertTrue(all(t[2] >= 0.1 for t in edge))


class PremiseTest(unittest.TestCase):
    """The fix rests on this (the first version of this test, asking the fast tier for p within 0.15 of 0.2,
    failed: it proposes 0.5): from the hand-only leftover of a |v|^p world the fast tier names the right shape,
    a power of speed, and its exponent lies within the bracket's reach (0.3) of the truth."""

    def test_hand_only_leftover_names_the_shape_within_bracket_reach(self):
        for true_p in (0.2, 0.3, 0.4):
            throws = throws_for(('power', 'speed', true_p), -2.0)
            top = [q['term'] for q in gaps.propose(throws, (), top=4)]
            speed_powers = [t for t in top if t[0] == 'power' and t[1] == 'speed']
            self.assertTrue(speed_powers, top)
            self.assertLessEqual(abs(speed_powers[0][2] - true_p), 0.3 + 1e-9, top)


if __name__ == '__main__':
    unittest.main()
