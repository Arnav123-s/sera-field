"""Run the finite GENRE-017 curriculum through delivery, audit and reporting.

Each numerical phase obtains its own ordinary exclusive lease and OS limits.
This is an immediate finite command, not a scheduled or recurring task. A failed
phase stops here with its exact revision and costs preserved.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(path): return json.loads(Path(path).read_text())


def command(arguments):
    result = subprocess.run([sys.executable, '-X', 'utf8', '-u', *arguments], cwd=ROOT)
    if result.returncode: raise SystemExit(result.returncode)


def phase(attempt, arguments):
    root = ROOT / 'runs' / attempt
    if root.exists():
        state = read(root / 'state.json')
        if state['status'] != 'PASS' or not state.get('lease_released'):
            raise SystemExit('Preserve and inspect existing attempt before resuming: ' + attempt)
        if state['command'] != ['--', *arguments]:
            raise SystemExit('An existing attempt belongs to another command: ' + attempt)
        print('Preserved completed phase: ' + attempt, flush=True)
        return
    command(['scripts/supervise.py', '--attempt', attempt, '--', *arguments])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-attempt', default='genre017-tests-001')
    parser.add_argument('--suffix', default='001')
    args = parser.parse_args()
    if not args.suffix.isdigit() or not args.test_attempt.startswith('genre017-tests-'):
        raise SystemExit('Use an explicit numeric attempt suffix and registered test attempt')
    test = read(ROOT / 'runs' / args.test_attempt / 'state.json')
    if test['status'] != 'PASS' or not test.get('lease_released'):
        raise SystemExit('Complete the registered tests first')
    history = ROOT / 'reports/HISTORY-016'
    if not all((history / name).exists() for name in ('QUALIFICATION.json', 'DELIVERY.json', 'REPORT.md', 'COSTS.json')):
        raise SystemExit('Complete the current history study before this continuation')
    campaign = 'genre017-campaign-' + args.suffix
    phase(campaign, ['scripts/complete_genre017.py'])
    phase('genre017-delivery-' + args.suffix,
          ['scripts/deliver_genre017.py', '--owner', 'runs/GENRE-017/exact_noisy'])
    phase('genre017-audit-' + args.suffix,
          ['scripts/audit_genre017.py', '--test-attempt', args.test_attempt,
           '--campaign-attempt', campaign])
    decision = read(ROOT / 'reports/GENRE-017/QUALIFICATION.json')
    selected = 'checkpoints/GENRE-017' if decision['all_gates'] else 'runs/GENRE-017/exact_noisy'
    phase('genre017-storage-' + args.suffix,
          ['scripts/inspect_owner_storage.py', '--kind', 'genre', '--owner', selected,
           '--training', 'runs/GENRE-017/exact_noisy', '--output', 'reports/GENRE-017/OWNER_STORAGE.json'])
    command(['scripts/report_genre017.py'])
    print(json.dumps({'status': 'finite_curriculum_delivery_audit_report_complete',
                      'qualified': decision['all_gates'], 'report': 'reports/GENRE-017/REPORT.md'}), flush=True)


if __name__ == '__main__': main()
