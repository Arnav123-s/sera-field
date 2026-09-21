"""Wait for the owned course, then check the next core's new equations once."""
import argparse
from pathlib import Path
import time

from finish_native019 import phase

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', default='core022-equations-001')
    args = parser.parse_args()
    if not args.attempt.startswith('core022-equations-'):
        raise SystemExit('Keep an identified complete-core engineering attempt')
    while not (ROOT / 'reports/JOINT-021/PACKAGE.json').exists():
        time.sleep(10)
    phase(args.attempt, ['-m', 'pytest', '-q', 'tests/test_fibonacci_space.py',
                        'tests/test_unified_energy.py', '--junitxml',
                        'reports/CORE-022/verification/'+args.attempt+'.xml'])


if __name__ == '__main__':
    main()
