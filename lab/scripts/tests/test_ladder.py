import json
import tempfile
import unittest
from pathlib import Path

from scripts.ladder import build_ladder


def check(passed, detail=None):
    return {"pass": passed, "detail": detail or {}, "seconds": 0.1}


def seed_data(c11=True):
    return {
        "C1": check(True, {"coverage": 0.5, "noise_worlds_alarms": 1}),
        "C6": check(True, {"sure_and_wrong": 2}),
        "C8": check(True, {"alarm_rate": 0.25, "eligible_worlds": 4}),
        "C10": check(True),
        "C11": check(c11, {"forgeries_accepted": 3 if not c11 else 0}),
    }


class LadderTests(unittest.TestCase):
    def test_statuses_sums_and_latest_seed_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "nested").mkdir()
            (root / "ladder").mkdir()
            old = root / "core_check_seed1.json"
            old.write_text(json.dumps(seed_data()), encoding="utf-8")
            import os
            os.utime(old, (100, 100))
            latest = root / "nested" / "core_check_seed1.json"
            latest.write_text(json.dumps(seed_data(c11=False)), encoding="utf-8")
            os.utime(latest, (200, 200))
            seed2 = root / "core_check_seed2.json"
            seed2.write_text(json.dumps(seed_data()), encoding="utf-8")
            evidence = [
                {"rung": "L3", "metric": "growth", "value": 1, "bar": ">=1", "pass": True, "source": "a", "seeds": "1"},
                {"rung": "L3", "metric": "growth", "value": 0, "bar": ">=1", "pass": False, "source": "b", "seeds": "2"},
            ]
            (root / "ladder" / "results.json").write_text(json.dumps(evidence), encoding="utf-8")

            rows, _, count, evidence_count = build_ladder(root, generated="2026-01-01T00:00:00Z")

            self.assertEqual(rows["L0"]["status"], "partial")
            self.assertEqual(rows["L2"]["status"], "partial")
            self.assertIn("eligible_worlds 8", rows["L2"]["metrics"])
            self.assertIn("noise_worlds_alarms 2", rows["L2"]["metrics"])
            self.assertEqual(rows["L3"]["status"], "partial")
            self.assertEqual(rows["L5"]["status"], "not measured")
            self.assertEqual(count, 2)
            self.assertEqual(evidence_count, 2)
            self.assertIn("forgeries_accepted 3", rows["L0"]["metrics"])


if __name__ == "__main__":
    unittest.main()
