"""ccops5 lab | live every life (seeds x learners), then write the tables.

Built as an isolated experiment. Not part of sera-field.

    python legacy/nursery/run.py                      # 3 seeds x 8 learners
    python legacy/nursery/run.py --seeds 1 --modes full baseline

Lives that already have results are skipped unless --again is given.
    python legacy/nursery/run.py --seeds 4 5 6 --results results-fresh   # seeds never used while building
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import traceback
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from ccops5.life import live_life  # noqa: E402
from ccops5.report import ORDER, write_report  # noqa: E402


def one(job):
    seed, mode, folder = job
    path = ROOT / folder / f'life-seed{seed}-{mode}.json'
    try:
        result = live_life(seed, mode)
    except Exception:
        return path.name, 'FAILED ' + traceback.format_exc()
    path.write_text(json.dumps(result, default=float), encoding='utf-8')
    return path.name, f"{result['seconds']:.0f} s"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=[1, 2, 3])
    parser.add_argument('--modes', nargs='+', default=list(ORDER))
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--again', action='store_true', help='re-live lives that already have results')
    parser.add_argument('--results', default='results', help='folder for this batch of lives')
    args = parser.parse_args()
    (ROOT / args.results).mkdir(exist_ok=True)
    jobs = [(seed, mode, args.results) for seed in args.seeds for mode in args.modes
            if args.again or not (ROOT / args.results / f'life-seed{seed}-{mode}.json').exists()]
    # Learners that grow laws take longest; start them first.
    jobs.sort(key=lambda job: job[1] in ('reset_all', 'baseline', 'baseline_parts', 'baseline_sets', 'baseline_words', 'frozen_laws'))
    if jobs:
        with Pool(min(args.workers, len(jobs))) as pool:
            for name, outcome in pool.imap_unordered(one, jobs):
                print(f'{name}: {outcome}', flush=True)
    print(write_report(ROOT, args.results))
