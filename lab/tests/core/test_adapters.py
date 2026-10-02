"""Checks for the legacy adapters without running the core mind."""

import unittest

import numpy as np

from ccops5 import inventor, puzzles, world
from ccops5.core import adapters, gaps, grammar
from c2_check import t4_summary


class LegacySchoolWorldTests(unittest.TestCase):
    def test_teacher_readings_match_legacy(self):
        seed, i, k = 1, 0, 0
        source = puzzles.school_plan(seed)[i]
        sit = source['situations'][k]
        rng = np.random.default_rng([seed, i, k])
        expected = [puzzles.simulate(source, sit['m'], u, rng, sit['trick'])
                    for u in sit['pushes']]
        check = puzzles.simulate(source, sit['m'], sit['check_u'], rng, sit['trick'])
        adapted = adapters.legacy_school_world(seed, i)
        for throw, (x, v) in zip(adapted.situations()[k], expected):
            self.assertTrue(np.array_equal(throw.x, x))
            self.assertTrue(np.array_equal(throw.v, v))
            self.assertEqual(throw.tag, 'teacher')
        self.assertTrue(np.array_equal(adapted.held_out[k].x, check[0]))
        self.assertTrue(np.array_equal(adapted.held_out[k].v, check[1]))
        self.assertEqual(adapted.held_out[k].tag, 'check')
        self.assertEqual(adapted.sigma, (world.SIGMA_X, world.SIGMA_V))

    def test_truth_in_grammar(self):
        for i in range(len(puzzles.school_plan(1))):
            with self.subTest(i=i):
                self.assertIn(adapters.legacy_school_world(1, i).truth, grammar.space())

    def test_true_force(self):
        source = puzzles.school_plan(1)[0]
        adapted = adapters.legacy_school_world(1, 0)
        x = np.array([-0.7, 0.0, 0.8])
        v = np.array([0.5, -0.3, 1.2])
        expected = (-source['sign'] * source['strength']
                    * puzzles.idea_value(puzzles.FORCES[source['force']][0], x, v))
        np.testing.assert_allclose(adapted.true_force(x, v), expected, rtol=1e-12, atol=1e-12)


class LegacyInventorWorldTests(unittest.TestCase):
    def test_teacher_readings_match_legacy(self):
        seed, i, k = 1, 0, 0
        source = inventor.school_plan(seed)[i]
        sit = source['situations'][k]
        rng = np.random.default_rng([seed, i, k])
        expected = [inventor.simulate(source, sit['m'], u, rng, sit['trick'])
                    for u in sit['pushes']]
        check = inventor.simulate(source, sit['m'], sit['check_u'], rng, sit['trick'])
        adapted = adapters.legacy_inventor_world(seed, i)
        for throw, (x, v) in zip(adapted.situations()[k], expected):
            self.assertTrue(np.array_equal(throw.x, x))
            self.assertTrue(np.array_equal(throw.v, v))
            self.assertEqual(throw.tag, 'teacher')
        self.assertTrue(np.array_equal(adapted.held_out[k].x, check[0]))
        self.assertTrue(np.array_equal(adapted.held_out[k].v, check[1]))
        self.assertEqual(adapted.held_out[k].tag, 'check')

    def test_truth_in_open_grammar(self):
        space = grammar.space(inventions=gaps.open_terms())
        outside = []
        for i in range(len(inventor.school_plan(1))):
            adapted = adapters.legacy_inventor_world(1, i)
            if adapted.representable:
                self.assertIn(adapted.truth, space)
            else:
                self.assertIsNone(adapted.truth)
                outside.append(adapted.force)
        self.assertEqual(len(outside), 19)

    def test_true_force(self):
        plan = inventor.school_plan(1)
        x = np.array([-0.7, 0.0, 0.8])
        v = np.array([0.5, -0.3, 1.2])
        for force in ('slope', 'growing drag', 'weakening spring', 'rubbing valley',
                      'wave drag', 'cubic drag'):
            i = next(i for i, source in enumerate(plan) if source['force'] == force)
            source = plan[i]
            adapted = adapters.legacy_inventor_world(1, i)
            expected = (-source['sign'] * source['strength']
                        * inventor.idea_value(inventor.FORCES[force][0], x, v))
            np.testing.assert_allclose(adapted.true_force(x, v), expected, rtol=1e-12, atol=1e-12)

    def test_t4_summary(self):
        rows = [
            {'legacy_sure': True, 'legacy_found': True, 'core_sure': True, 'core_found': True, 'core_wrong': False},
            {'legacy_sure': True, 'legacy_found': True, 'core_sure': False, 'core_found': False, 'core_wrong': False},
            {'legacy_sure': True, 'legacy_found': True, 'core_sure': True, 'core_found': True, 'core_wrong': False},
            {'legacy_sure': True, 'legacy_found': False, 'core_sure': True, 'core_found': False, 'core_wrong': True},
        ]
        self.assertEqual(t4_summary(rows), {
            'legacy_settled_right': 3, 'core_settles_of_those': 2 / 3,
            'core_sure_and_wrong': 1, 'legacy_sure_and_wrong': 1, 'pass_t4': False})


if __name__ == '__main__':
    unittest.main()
