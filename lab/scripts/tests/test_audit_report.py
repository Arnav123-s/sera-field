import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_report import audit, main, numbers, units


class AuditReportTests(unittest.TestCase):
    def test_sources_globs_json_rounding_pairs_and_sub_bullets(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'results').mkdir()
            (root / 'results' / 'check.json').write_text(json.dumps({
                'coverage': 0.94951, 'share': 0.25, 'accepted': [],
                'worlds': [False, False, False, False],
            }), encoding='utf-8')
            (root / 'results' / 'run.log').write_text('Passed 12 trials.\n', encoding='utf-8')
            report = ('# Session 2026-09-24\n'
                      '| Claim | Evidence |\n|---|---|\n'
                      '| Coverage 0.950 and 25%; 0 of 4 accepted | `results/check.json` |\n'
                      '- Ran 12 trials.\n'
                      '  - Source: `results/*.log`\n')
            rows = audit(report, root)
            self.assertEqual([row[1] for row in rows], ['0.950', '25%', '0 of 4', '12'])
            self.assertTrue(all(row[2] == 'traced' for row in rows))
            self.assertEqual(rows[-1][0], 5)

    def test_planted_number_no_source_and_exemptions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'log.txt').write_text('8 of 8 worlds passed; value 0.75\n', encoding='utf-8')
            report = ('## 4.2 Results on 2026-09-24 at 13:40\n'
                      '- seed 1 B4-02 L3 C11 §4 commit `3e7a496`: 8/8 worlds `log.txt`.\n'
                      '- Planted value 937. `log.txt`\n'
                      '\nNo source supports 42.\n'
                      'Run `python tool.py --seed 9` and see `missing-seed1.json`.\n')
            rows = audit(report, root)
            self.assertEqual([(row[1], row[2]) for row in rows],
                             [('8/8', 'traced'), ('937', 'untraced'), ('42', 'no-source')])

    def test_exit_codes_and_table(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data.json').write_text('{"result": 2}', encoding='utf-8')
            report = root / 'report.md'
            report.write_text('Result 2. `data.json`\n\nWrong 91. `data.json`\n', encoding='utf-8')
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(report), '--root', str(root)]), 1)
            self.assertIn('| 3 | 91 | untraced |  |', output.getvalue())
            self.assertIn('1 traced; 1 untraced; 0 no-source', output.getvalue())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(report), '--root', str(root), '--warn-only']), 0)

    def test_exempt_numbered_list_and_paragraphs(self):
        self.assertEqual(numbers('1. Step for seed 2 on B0, B4-02, L3, C11, §4, 2026-09-24 at 14:06.'), [])
        self.assertEqual(list(units('One 3.\ncontinued.\n\nTwo 4.\n')),
                         [(1, 'One 3.\ncontinued.'), (4, 'Two 4.')])


if __name__ == '__main__':
    unittest.main()
