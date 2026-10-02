"""Tests for the world-side caretaker, without running a simulation."""

import ast
import subprocess
import sys
import unittest
from types import SimpleNamespace

from ccops5.core.caretaker import Caretaker, FILLERS, Utterance


def world(force='rubbing', masses=(1.2, 2.3, 0.8)):
    return SimpleNamespace(force=force, kind_name=force, masses=masses)


class CaretakerTests(unittest.TestCase):
    def test_import_isolation(self):
        code = ("import ccops5.core.caretaker, sys; "
                "print(sorted(m for m in sys.modules if m.startswith('ccops5')))")
        result = subprocess.run([sys.executable, '-c', code], check=True,
                                capture_output=True, text=True)
        names = set(ast.literal_eval(result.stdout.strip()))
        allowed = {'ccops5', 'ccops5.core', 'ccops5.core.caretaker',
                   'ccops5.core.grammar', 'ccops5.puzzles'}
        self.assertEqual(names - allowed, set())
        self.assertIn('ccops5.core.caretaker', names)

    def test_timed_first_event_and_mass(self):
        c = Caretaker('timed', 9, filler_rate=0)
        w = world()
        self.assertEqual(c.start_world(0, w), [])
        self.assertEqual(c.on_situation(0, w, 0), [])
        self.assertEqual(c.heard(0), frozenset())
        self.assertEqual(c.on_event(0, w, 0, 'blocked'),
                         [Utterance(0, 0, 'rough', 'blocked')])
        self.assertEqual(c.on_event(0, w, 0, 'alarm'), [])
        self.assertEqual(c.on_event(0, w, 0, 'surprise'), [])
        self.assertEqual(c.on_event(0, w, 1, 'surprise'),
                         [Utterance(0, 1, 'heavy', 'surprise')])
        self.assertEqual(c.on_event(0, w, 1, 'surprise'), [])
        self.assertEqual(c.on_event(0, w, 2, 'surprise'),
                         [Utterance(0, 2, 'light', 'surprise')])
        self.assertEqual(c.heard(0), frozenset({'rough', 'heavy', 'light'}))

    def test_pairs_aliases_and_word_only(self):
        c = Caretaker('timed', 2, filler_rate=0)
        w = world('faint rubbing+swing small')
        self.assertEqual(c.start_world(3, w, word_only=True),
                         [Utterance(3, -1, 'rough', 'word-only'),
                          Utterance(3, -1, 'swingy', 'word-only')])
        self.assertEqual(c.on_event(3, w, 0, 'alarm'), [])
        self.assertEqual(c.definitions()['rough'], 'rubbing')

    def test_none(self):
        c = Caretaker('none', 1, filler_rate=1, p_random=1)
        w = world()
        self.assertEqual(c.start_world(0, w, word_only=True), [])
        self.assertEqual(c.on_event(0, w, 1, 'surprise'), [])
        self.assertEqual(c.on_situation(0, w, 1), [])
        self.assertEqual(c.log, [])

    def test_random_ignores_world(self):
        c = Caretaker('random', 6, filler_rate=0)
        for number in range(200):
            w = world('rubbing', (1.2,))
            c.start_world(number, w)
            c.on_event(number, w, 0, 'surprise')
            c.on_situation(number, w, 0)
        rough = sum('rough' in c.heard(n) for n in range(200))
        wet = sum('wet' in c.heard(n) for n in range(200))
        self.assertLessEqual(abs(rough - wet), 12)

    def test_fillers_and_reproducibility(self):
        w = world()
        first = Caretaker('timed', 77)
        second = Caretaker('timed', 77)
        for situation in range(1000):
            first.on_situation(0, w, situation)
            second.on_situation(0, w, situation)
        self.assertEqual(first.log, second.log)
        count = sum(u.word in FILLERS for u in first.log)
        self.assertGreaterEqual(count, 160)
        self.assertLessEqual(count, 240)


if __name__ == '__main__':
    unittest.main()
