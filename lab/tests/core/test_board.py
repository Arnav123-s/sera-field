"""Checks for the board's deposits, decay, hints, and import boundary."""

import math
import subprocess
import sys
import unittest

import numpy as np

from ccops5.core import grammar
from ccops5.core.board import Board


class Certificate:
    digest = 'checked-digest'


class Claim:
    def __init__(self, family, sure=True):
        self.family = family
        self.sure = sure
        self.certificate = Certificate()


class Library:
    def __init__(self, *claims):
        self.claims = claims


class BoardTests(unittest.TestCase):
    def test_certificate_requires_library_identity_and_sure(self):
        idea = grammar.IDEAS[0]
        board = Board()
        claim = Claim((idea,))
        with self.assertRaisesRegex(ValueError, 'unchecked deposit'):
            board.deposit_certificate(Library(Claim((idea,))), claim)
        claim.sure = False
        with self.assertRaisesRegex(ValueError, 'unchecked deposit'):
            board.deposit_certificate(Library(claim), claim)
        self.assertEqual(board.trails[idea], 1.0)
        self.assertEqual(board.audit, [])
        claim.sure = True
        board.deposit_certificate(Library(claim), claim)
        self.assertEqual(board.trails[idea], 2.0)
        self.assertEqual(board.audit[0]['source_id'], 'checked-digest')
        self.assertEqual(board.trail_score((idea,)), math.log(2.0))
        self.assertEqual(board.trail_score(()), 0.0)

    def test_correction_requires_registered_teacher_id(self):
        idea = grammar.IDEAS[0]
        registry = {'c1'}
        board = Board(corrections_registry=registry)
        correction = {'id': 'other', 'family': (idea,), 'issued_by': 'teacher'}
        with self.assertRaises(ValueError):
            board.deposit_correction(correction)
        correction['id'] = 'c1'
        correction['issued_by'] = 'learner'
        with self.assertRaises(ValueError):
            board.deposit_correction(correction)
        self.assertEqual(board.trails[idea], 1.0)
        correction['issued_by'] = 'teacher'
        board.deposit_correction(correction)
        self.assertEqual(board.trails[idea], 1.5)
        self.assertEqual(board.audit[-1]['source_id'], 'c1')

    def test_alarm_hotspots_and_cell_mapping(self):
        board = Board()
        with self.assertRaises(ValueError):
            board.deposit_alarm(1.9, 2.0, [(0, 0)])
        self.assertEqual(float(board.hotspots.sum()), 0.0)
        board.deposit_alarm(4.0, 2.0, [(0, 0), (0, 7)])
        self.assertEqual(board.hotspots[0, 0], 2.0)
        self.assertEqual(board.placement_hint(), ('fast', None))
        self.assertEqual(board.cell_of(-1, 1), (0, 7))
        self.assertEqual(board.cell_of(-2, 2), (0, 7))
        self.assertEqual(board.cell_of(0, 0), (4, 4))

    def test_evaporation_floor_and_lookalike_hint(self):
        board = Board()
        first, second = grammar.IDEAS[:2]
        board.mark_lookalike((first,), (second,))
        self.assertIsNone(board.placement_hint())
        board.mark_lookalike((second,), (first,))
        self.assertEqual(board.placement_hint(), ('large', None))
        for _ in range(100):
            board.evaporate()
        self.assertTrue(all(tau >= board.tau_min for tau in board.trails.values()))
        self.assertTrue(all(tau == board.tau_min for tau in board.trails.values()))
        self.assertIsNone(board.placement_hint())
        self.assertEqual(board.lookalikes, {})

    def test_json_round_trip(self):
        board = Board(rho=0.2, tau_min=0.08, grid=4, corrections_registry={'c1'})
        first, second = grammar.IDEAS[:2]
        claim = Claim((first, second))
        board.deposit_certificate(Library(claim), claim)
        board.deposit_correction({'id': 'c1', 'family': (first,), 'issued_by': 'teacher'})
        board.deposit_alarm(2.0, 1.0, [(0, 0)])
        board.mark_lookalike((first,), (second,))
        board.evaporate()
        restored = Board.from_json(board.to_json())
        self.assertEqual(restored.rho, board.rho)
        self.assertEqual(restored.tau_min, board.tau_min)
        self.assertEqual(restored.grid, board.grid)
        self.assertEqual(restored.trails, board.trails)
        np.testing.assert_array_equal(restored.hotspots, board.hotspots)
        self.assertEqual(restored.lookalikes, board.lookalikes)
        self.assertEqual(restored.audit, board.audit)
        self.assertEqual(restored.corrections_registry, set())

    def test_import_isolation(self):
        code = ("import sys; import ccops5.core.board; "
                "forbidden = {'ccops5.core.' + name for name in "
                "('truth', 'likelihood', 'worlds', 'checker')}; "
                "assert not forbidden.intersection(sys.modules)")
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
