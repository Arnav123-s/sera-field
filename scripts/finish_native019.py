"""Finite continuation after the already owned genre course, with exclusive leases.

This immediate process is not a scheduled task. It never interrupts another job,
repeats a completed phase or opens a final before all matched teaching finishes.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
LEASE = Path('D:/ai/projects/sera/runs/v3-batch-001/active.lock')


def read(path): return json.loads(Path(path).read_text())


def command(args):
    result = subprocess.run([sys.executable, '-X', 'utf8', '-u', *args], cwd=ROOT)
    if result.returncode: raise SystemExit(result.returncode)


def phase(attempt, args):
    path = ROOT / 'runs' / attempt / 'state.json'
    if path.exists():
        state = read(path)
        if (state['status'] != 'PASS' or not state.get('lease_released') or state['command'] != ['--', *args]):
            raise SystemExit('Inspect the preserved existing attempt before resuming: ' + attempt)
        print('Preserved completed phase: ' + attempt, flush=True); return
    while LEASE.exists(): time.sleep(15)
    command(['scripts/supervise.py', '--attempt', attempt, '--', *args])


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--test-attempt', default='native019-tests-001')
    args = parser.parse_args()
    if not args.test_attempt.startswith('native019-tests-'): raise SystemExit('Use a registered native test attempt')
    print('Waiting for the preserved GENRE-017 director; no numerical lease held.', flush=True)
    required = ('genre017-campaign-001', 'genre017-delivery-001', 'genre017-audit-001', 'genre017-storage-001')
    while True:
        states = [read(ROOT / 'runs' / name / 'state.json') for name in required
                  if (ROOT / 'runs' / name / 'state.json').exists()]
        if any(state['status'] not in ('RUNNING', 'STARTING', 'PASS') for state in states):
            raise SystemExit('Earlier owned phase needs inspection; no new numerical work started')
        if (len(states) == len(required) and all(s['status'] == 'PASS' and s.get('lease_released') for s in states)
                and (ROOT / 'reports/GENRE-017/REPORT.md').exists() and not LEASE.exists()): break
        time.sleep(15)
    phase('attach018-checks-001', ['scripts/verify_attachment018.py'])
    phase('genre017-uncertainty-tests-001', ['-m', 'pytest', '-q', 'tests/test_genre_uncertainty.py'])
    phase('genre017-uncertainty-001', ['scripts/uncertainty_genre017.py'])
    command(['scripts/report_genre017.py'])
    phase(args.test_attempt, ['-m', 'pytest', '-q', 'tests/test_native_owner.py', 'tests/test_native_session.py'])
    phase('native019-campaign-001', ['scripts/complete_native019.py'])
    phase('native019-delivery-001', ['scripts/deliver_native019.py'])
    phase('native019-audit-001', ['scripts/audit_native019.py'])
    phase('native019-package-001', ['scripts/package_native019.py'])
    command(['scripts/report_native019.py'])
    print(json.dumps({'native_course': 'completed', 'report': 'reports/NATIVE-019/REPORT.md'}), flush=True)


if __name__ == '__main__': main()
