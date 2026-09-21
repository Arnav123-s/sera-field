"""Finish verified delivery, independent assessment, packaging and regressions."""
from pathlib import Path
import json
import argparse

from finish_native019 import phase, command

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit-attempt', default='joint020-audit-001')
    args = parser.parse_args()
    if not args.audit_attempt.startswith('joint020-audit-'):
        raise SystemExit('Use a scoped joint audit attempt name')
    replay = ROOT / 'reports/JOINT-020/REPLAY.json'
    if not replay.exists() or not json.loads(replay.read_text())['exact']:
        raise SystemExit('Finish the existing teaching/final/replay director first')
    phase('joint020-session-tests-001', ['-m', 'pytest', '-q', 'tests/test_joint_session.py'])
    phase('joint020-delivery-001', ['scripts/deliver_joint020.py'])
    phase('joint020-delivery-replay-001', ['scripts/deliver_joint020.py', '--replay'])
    phase('joint020-order-diagnosis-001', ['scripts/diagnose_joint020.py'])
    phase(args.audit_attempt, ['scripts/audit_joint020.py'])
    phase('joint020-package-001', ['scripts/package_joint020.py'])
    phase('native019-release-001', ['scripts/verify_native019_release.py'])
    phase('joint020-release-001', ['scripts/verify_joint020_release.py'])
    command(['scripts/report_native019.py'])
    command(['scripts/report_joint020.py'])
    command(['scripts/index_research_state.py'])


if __name__ == '__main__':
    main()
