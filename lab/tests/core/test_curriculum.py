import unittest

import numpy as np

from ccops5 import puzzles
from ccops5.core import curriculum, grammar, worlds


class CurriculumTests(unittest.TestCase):
    def test_plain_world_matches_worlds_make(self):
        actual = curriculum.make_world(11, 'spring', 2, situations=4)
        expected = worlds.make(11, 'spring', index=2, situations=4)
        self.assertEqual(actual.masses, expected.masses)
        self.assertEqual(actual.bumps, expected.bumps)
        self.assertEqual(actual.teacher_pushes, expected.teacher_pushes)
        self.assertEqual(actual.truth, expected.truth)
        for left, right in zip(actual.throws + actual.held_out, expected.throws + expected.held_out):
            self.assertTrue(np.array_equal(left.x, right.x))
            self.assertTrue(np.array_equal(left.v, right.v))

    def test_pair_force(self):
        w = curriculum.make_world(3, 'rubbing+spring', 0)
        self.assertIsInstance(w, curriculum.MultiWorld)
        self.assertIn(w.truth, grammar.space())
        x = np.array([-0.4, 0.0, 0.7])
        v = np.array([0.2, -0.5, 0.9])
        expected = sum(c * puzzles.idea_value(idea, x, v) for idea, c in zip(w.ideas, w.coefs))
        np.testing.assert_allclose(w.true_force(x, v), expected)

    def test_validation(self):
        for kind in curriculum.KINDS:
            for seed in (1, 2, 3):
                with self.subTest(kind=kind, seed=seed):
                    result = curriculum.validate(seed, kind)
                    self.assertTrue(result['ok'], result)
                    self.assertEqual(result['truth'], curriculum.KIND_TRUTH[kind])

    def test_ladder_unlocks_in_order(self):
        c = curriculum.Curriculum('ladder', 5)
        self.assertEqual(c.next_kind()[0], 'none')
        c.record('none', 1, True, False)
        self.assertEqual(c.state()['unlocked_stages'], ['S0', 'S1'])
        self.assertEqual([c.next_kind()[0] for _ in range(3)], list(curriculum.STAGES[1][1]))

    def test_random_reaches_all_stages(self):
        c = curriculum.Curriculum('random', 7)
        seen = {c.next_kind()[0] for _ in range(60)}
        for _, kinds in curriculum.STAGES:
            self.assertTrue(seen.intersection(kinds))

    def test_progress_chooses_largest_change(self):
        c = curriculum.Curriculum('progress', 8, stage_cap=100, explore=0.0)
        c.record('none', 1, True, False)
        for kind in ('none', 'spring', 'slope'):
            for _ in range(6):
                c.record(kind, 3, False, False)
        for tries in (8, 8, 8, 2, 2, 2):
            c.record('rubbing', tries, False, False)
        self.assertEqual(c.next_kind()[0], 'rubbing')

    def test_same_seed_and_restored_state(self):
        a = curriculum.Curriculum('random', 13)
        b = curriculum.Curriculum('random', 13)
        self.assertEqual([a.next_kind() for _ in range(20)], [b.next_kind() for _ in range(20)])
        restored = curriculum.Curriculum.from_state(a.state())
        self.assertEqual([a.next_kind() for _ in range(10)], [restored.next_kind() for _ in range(10)])


if __name__ == '__main__':
    unittest.main()
