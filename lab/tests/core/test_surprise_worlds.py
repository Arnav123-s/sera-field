import unittest

import numpy as np

from ccops5.core import curriculum, grammar


class SurpriseWorldTests(unittest.TestCase):
    def test_builds_validate_and_are_deterministic(self):
        for kind in curriculum.SURPRISES:
            for seed in (1, 2, 3):
                with self.subTest(kind=kind, seed=seed):
                    world = curriculum.make_world(seed, kind, 0)
                    self.assertIsNone(world.truth)
                    self.assertEqual(len(world.hidden_terms), 1)
                    self.assertIn(grammar.code(world.hidden_terms[0])[0], (4, 5, 6))
                    self.assertTrue(curriculum.validate(seed, kind)['ok'])
                    again = curriculum.make_world(seed, kind, 0)
                    for a, b in zip(world.throws + world.held_out, again.throws + again.held_out):
                        np.testing.assert_array_equal(a.x, b.x)
                        np.testing.assert_array_equal(a.v, b.v)

    def test_effect_size(self):
        for kind in curriculum.SURPRISES:
            values = [curriculum.make_world(seed, kind, 0).effect_size() for seed in (1, 2, 3)]
            print(f'{kind} effect_size seeds 1,2,3: {values}')
            self.assertGreaterEqual(sum(value > 0.1 for value in values), 2)


if __name__ == '__main__':
    unittest.main()
