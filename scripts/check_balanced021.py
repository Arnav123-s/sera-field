"""Reuse the established independent checks with explicit JOINT-021 paths."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.balanced_joint_data import BalancedJointData


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('delivery', 'delivery-replay', 'order', 'audit', 'package', 'release'))
    args = parser.parse_args()
    name = 'JOINT-021'; study = ROOT / 'runs' / name; report = ROOT / 'reports' / name
    if args.phase in ('delivery', 'delivery-replay'):
        import deliver_joint020 as operation
        operation.STUDY = study; operation.REPORT = report
        operation.SESSIONS = ROOT / 'local/JOINT-021-delivery'; operation.JointData = BalancedJointData
        sys.argv = [sys.argv[0], *(['--replay'] if args.phase == 'delivery-replay' else [])]
    elif args.phase == 'order':
        import diagnose_joint020 as operation
        operation.STUDY = study; operation.REPORT = report; operation.JointData = BalancedJointData
    elif args.phase == 'audit':
        import audit_joint020 as operation
        operation.STUDY = study; operation.REPORT = report; operation.JointData = BalancedJointData
        operation.PROTOCOL = ROOT / 'protocols/JOINT-021.md'
        operation.EXTRA_PRIOR_GROUPS = [ROOT / 'reports/JOINT-020/REGISTRATION.json']
        operation.ENGINEERING_ATTEMPT = ROOT / 'runs/joint021-tests-001/state.json'
    elif args.phase == 'package':
        import package_joint020 as operation
        operation.NAME = name; operation.STUDY = study
    else:
        import verify_joint020_release as operation
        operation.NAME = name
    operation.main()


if __name__ == '__main__':
    main()
