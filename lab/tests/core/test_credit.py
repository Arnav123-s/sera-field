"""T2 (credit), written before the code: what the gut may learn from, and the T2 bars (Architecture §12).

Credit modes: 'checked' (an accepted certificate, else the teacher's correction: the current School),
'outside' (only the teacher's correction), 'self' (the mind's own leading idea, unchecked), 'none'.
T2 passes when: 0 sure-and-wrong; checked credit needs no more tries than outside credit (mean rank of the truth on
teacher-free worlds); checked credit is better calibrated than self credit (paired Brier difference, 95% interval
below 0).
"""
import unittest
from types import SimpleNamespace

import numpy as np

import school_check as SC
from ccops5.core import gut as G, school as S

SPRING, RUB = (G.FAMILIES[3],), (G.FAMILIES[5],)


def fam(f):
    return f[0]


class CreditOutcomeTest(unittest.TestCase):
    claim = SimpleNamespace(family=fam(SPRING))
    correction = {'family': fam(RUB)}
    report = SimpleNamespace(claim=fam(RUB))

    def test_checked_prefers_certificate_then_teacher(self):
        self.assertEqual(S.credit_outcome('checked', self.claim, self.correction, self.report)[1], 'certificate')
        self.assertEqual(S.credit_outcome('checked', None, self.correction, self.report)[1], 'teacher')
        self.assertEqual(S.credit_outcome('checked', None, None, self.report), (None, None))

    def test_outside_ignores_certificates(self):
        self.assertEqual(S.credit_outcome('outside', self.claim, None, self.report), (None, None))
        self.assertEqual(S.credit_outcome('outside', self.claim, self.correction, self.report)[1], 'teacher')

    def test_self_takes_its_own_leading_idea_unchecked(self):
        out, source = S.credit_outcome('self', None, self.correction, self.report)
        self.assertEqual(source, 'self')
        self.assertEqual(out, fam(RUB))

    def test_none_learns_nothing(self):
        self.assertEqual(S.credit_outcome('none', self.claim, self.correction, self.report), (None, None))

    def test_credit_arms_differ_from_why_only_in_credit(self):
        for arm in ('credit-outside', 'credit-self', 'credit-none'):
            self.assertEqual(S.ARMS[arm][:2], S.ARMS['why'][:2])
            self.assertEqual(S.ARMS[arm][3:], S.ARMS['why'][3:])
        self.assertEqual(S.CREDIT.get('why', 'checked'), 'checked')


class GutProbabilityTest(unittest.TestCase):
    def test_probabilities_and_brier(self):
        g = G.Gut()
        F = np.zeros((len(G.FAMILIES), G.N_FEAT))
        p = g.probabilities(F)
        self.assertAlmostEqual(float(p.sum()), 1.0)
        n = len(G.FAMILIES)
        truth = G.FAMILIES[0]
        # uniform: (1 - 1/n)^2 + (n - 1) / n^2 = 1 - 1/n
        self.assertAlmostEqual(G.brier(p, truth), 1 - 1 / n)


def life(seed, arm, ranks, briers, wrong=0):
    worlds = [{'n': i, 'phase': 'alone', 'rank': r, 'brier': b, 'sure_and_wrong': i < wrong}
              for i, (r, b) in enumerate(zip(ranks, briers))]
    return {'seed': seed, 'arm_name': arm, 'worlds': worlds}


def lives(checked_ranks=(1, 2, 1, 1), outside_ranks=(2, 3, 2, 2), checked_brier=0.2, self_brier=0.6, wrong=0):
    out = {}
    for s in (1, 2, 3):
        jitter = [0.01 * s * k for k in range(4)]
        out[(s, 'why')] = life(s, 'why', checked_ranks, [checked_brier + j for j in jitter], wrong)
        out[(s, 'credit-outside')] = life(s, 'credit-outside', outside_ranks, [0.4 + j for j in jitter])
        out[(s, 'credit-self')] = life(s, 'credit-self', (3, 3, 3, 3), [self_brier + j for j in jitter])
        out[(s, 'credit-none')] = life(s, 'credit-none', (5, 5, 5, 5), [0.9] * 4)
    return out


class T2CheckTest(unittest.TestCase):
    def test_passes_when_bars_hold(self):
        ok, detail = SC.check_t2(lives())
        self.assertTrue(ok, detail)
        self.assertEqual(detail['sure_and_wrong'], 0)

    def test_fails_on_any_sure_and_wrong(self):
        self.assertFalse(SC.check_t2(lives(wrong=1))[0])

    def test_fails_when_checked_needs_more_tries_than_outside(self):
        self.assertFalse(SC.check_t2(lives(checked_ranks=(3, 3, 3, 3)))[0])

    def test_fails_when_not_better_calibrated_than_self(self):
        self.assertFalse(SC.check_t2(lives(checked_brier=0.6, self_brier=0.6))[0])

    def test_missing_arms_fail(self):
        partial = {k: v for k, v in lives().items() if k[1] != 'credit-self'}
        self.assertFalse(SC.check_t2(partial)[0])


if __name__ == '__main__':
    unittest.main()
