"""Smoke test for the SERA level report command."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import sera_levels_report


def test_report_writes_json_and_markdown(tmp_path):
    """Small run creates both files with expected world and level totals."""
    sera_levels_report.main([
        '--per-level', '3', '--levels', '0', '1', '--workers', '1', '--out', str(tmp_path),
    ])
    json_path = tmp_path / 'levels_seed1_dream.json'
    md_path = tmp_path / 'levels_seed1_dream.md'
    assert json_path.exists()
    assert md_path.exists()
    report = json.loads(json_path.read_text(encoding='utf-8'))
    assert len(report['worlds']) == 6
    level_data = {item['level']: item for item in report['levels']}
    assert level_data[0]['requested'] == 3
    assert level_data[1]['requested'] == 3
    assert any(line.startswith('| level') for line in md_path.read_text(encoding='utf-8').splitlines())
