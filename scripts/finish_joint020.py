"""Immediate sequential owned course, with a new capped process for each phase."""
from finish_native019 import phase


def main():
    phase('joint020-prepare-001', ['scripts/complete_joint020.py', 'prepare'])
    phase('joint020-train-001', ['scripts/complete_joint020.py', 'train'])
    phase('joint020-final-001', ['scripts/complete_joint020.py', 'final'])
    phase('joint020-replay-001', ['scripts/complete_joint020.py', 'replay'])
    print('Joint teaching and once-opened final/replay completed; independent audit remains.', flush=True)


if __name__ == '__main__':
    main()
