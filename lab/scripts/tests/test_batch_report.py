import json
import tempfile
import unittest
from pathlib import Path

from scripts.batch_report import build_report


class BatchReportTests(unittest.TestCase):
    def write(self, path, value):
        path.write_text(json.dumps(value), encoding='utf-8')

    def test_m1a_school_aggregation_and_falling_slope(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            m1a = root / 'm1a'
            school = root / 'school'
            m1a.mkdir()
            school.mkdir()
            self.write(m1a / 'core_check_seed1.json', {
                'checks': {'C1': {'pass': True, 'detail': {'coverage': 0.75}},
                           'C6': {'pass': True, 'detail': {'not_vacuous': True, 'sure_share': {'strong': 0.5}, 'sure_and_wrong': 0}},
                           'C11': {'pass': True, 'detail': {'forgeries_accepted': []}}}})
            self.write(m1a / 'core_check_seed2.json', {
                'checks': {'C1': {'pass': True, 'detail': {'coverage': 0.8}},
                           'C6': {'pass': True, 'detail': {'not_vacuous': True, 'sure_share': {'strong': 0.25}, 'sure_and_wrong': 1}},
                           'C11': {'pass': False, 'detail': {'forgeries_accepted': ['fake']}}}})
            for arm in ('self', 'answer'):
                for seed in (1, 2):
                    worlds = []
                    for n in range(6):
                        phase = 'taught' if n == 0 else 'alone' if n < 5 else 'exam'
                        worlds.append({'n': n, 'phase': phase, 'kind': 'rubbing', 'rank': 6 - n,
                                       'rank_no_words': 5 - n, 'never_shown': False,
                                       'word_only': phase == 'exam', 'correct': n == 5,
                                       'sure_and_wrong': False})
                    self.write(school / f'life-seed{seed}-{arm}.json', {
                        'seed': seed, 'arm_name': arm, 'worlds': worlds,
                        'lexicon': {'grounded': ['a', 'b']}, 'minutes': 3.5})
            report = build_report([m1a], school)
            self.assertIn('C11', report)
            self.assertIn('FAIL', report)
            self.assertIn('forgeries_accepted=1', report)
            self.assertIn('Total sure-and-wrong (C6, C8, T5): 1', report)
            self.assertIn('| self | 2 | 12 | 2/0.167 |', report)
            self.assertIn('| answer | 2 | 12 | 2/0.167 |', report)
            slopes = [line for line in report.splitlines() if line.startswith('| self |') and len(line.split('|')) == 5]
            self.assertEqual(len(slopes), 1)
            self.assertLess(float(slopes[0].split('|')[2].strip()), 0)


if __name__ == '__main__':
    unittest.main()
