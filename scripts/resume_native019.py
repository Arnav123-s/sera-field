"""Resume only unfinished verification after the preserved replay memory limit.

The original training/final worker had retained allocations when it launched a
fresh interpreter. Run that interpreter under its own exclusive, capped lease.
No training, selection or original final prediction is repeated or modified.
"""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from finish_native019 import phase, command


def read(path):
    return json.loads(Path(path).read_text())


def main():
    original = ROOT / 'runs/native019-campaign-001'
    status = read(original / 'state.json')
    log = (original / 'process.log').read_text(encoding='utf-8')
    if (status['status'] != 'FAILED' or not status.get('lease_released')
            or 'MemoryError' not in log or "'--replay'" not in log):
        raise SystemExit('This recovery is scoped to the preserved replay memory failure')
    study = ROOT / 'runs/NATIVE-019'
    if not all((study / arm / 'COMPLETE.json').exists() for arm in ('native', 'delayed', 'trace')):
        raise SystemExit('Training has not completed; do not skip it')
    routes = ('native', 'delayed', 'trace', 'initial', 'erase_history', 'no_bulk',
              'equal_rates', 'no_imagination')
    for route in routes:
        for cohort in ('matched', 'mismatched', 'physics', 'physics_shifted'):
            if not (study / 'final' / route / cohort / 'RESULTS.json').exists():
                raise SystemExit('Original final assessment is incomplete')
    phase('native019-replay-001', ['scripts/complete_native019.py', '--replay'])
    phase('native019-delivery-001', ['scripts/deliver_native019.py'])
    phase('native019-audit-001', ['scripts/audit_native019.py'])
    phase('native019-package-001', ['scripts/package_native019.py'])
    command(['scripts/report_native019.py'])
    print('Preserved training and final predictions; completed remaining verification.', flush=True)


if __name__ == '__main__':
    main()
