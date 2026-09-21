"""One finite corrected course followed by independently supervised assessment."""
from finish_native019 import phase


def main():
    phase('joint021-tests-001', ['-m', 'pytest', '-q', 'tests/test_balanced_joint_data.py', 'tests/test_joint_cycle.py', 'tests/test_joint_session.py'])
    phase('joint021-prepare-001', ['scripts/complete_balanced021.py', 'prepare'])
    phase('joint021-train-001', ['scripts/complete_balanced021.py', 'train'])
    phase('joint021-final-001', ['scripts/complete_balanced021.py', 'final'])
    phase('joint021-replay-001', ['scripts/complete_balanced021.py', 'replay'])
    phase('joint021-delivery-001', ['scripts/check_balanced021.py', 'delivery'])
    phase('joint021-delivery-replay-001', ['scripts/check_balanced021.py', 'delivery-replay'])
    phase('joint021-order-001', ['scripts/check_balanced021.py', 'order'])
    phase('joint021-audit-001', ['scripts/check_balanced021.py', 'audit'])
    phase('joint021-package-001', ['scripts/check_balanced021.py', 'package'])
    print('Corrected teaching, independent assessment and package complete.', flush=True)


if __name__ == '__main__':
    main()
