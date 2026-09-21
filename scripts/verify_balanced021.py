"""Complete corrected-owner interface and repository verification before release."""
from pathlib import Path

from finish_native019 import phase, command

ROOT = Path(__file__).resolve().parents[1]


def main():
    if not (ROOT / 'reports/JOINT-021/PACKAGE.json').exists():
        raise SystemExit('Finish the owned corrected-course director first')
    phase('joint021-regression-001', ['-m', 'pytest', '-q', '--junitxml',
                                    'reports/JOINT-021/verification/repository-tests.xml'])
    phase('joint021-release-001', ['scripts/check_balanced021.py', 'release'])
    phase('joint021-packaged-integrity-001', ['scripts/verify_packaged.py'])
    command(['scripts/report_balanced021.py'])
    command(['scripts/index_research_state.py'])


if __name__ == '__main__':
    main()
