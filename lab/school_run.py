"""Runs School lives (ccops5/core/school.py) in parallel and saves one JSON per life.

    python school_run.py --seeds 1 2 3 --arms untaught self answer why full --results core-results/school-dev
    python school_run.py --quick                     # a smoke test: 2 arms, tiny lives, into core-results/school-smoke
Lives that already have a file are skipped (fresh seeds are run once). Needs PYTHONHASHSEED=0.
"""
import argparse
import dataclasses
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ccops5.core import evidence as EV, school as S


def _job(spec):
    seed, arm, settings, out, cache_dir = spec
    path = Path(out) / f'life-seed{seed}-{arm}.json'
    trail = Path(out) / f'life-seed{seed}-{arm}.progress.jsonl'
    trail.write_text('', encoding='utf-8')
    cache = EV.Cache(cache_dir)

    def progress(row):
        with trail.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(row, default=str) + '\n')
        print(f"  seed {seed} {arm:10s} #{row['n']:>3} {row['phase']:6s} {row['kind']:13s} rank {row['rank']:>2} "
              f"help {row['help']} {'RIGHT' if row['correct'] else 'wrong' if row['sure_and_wrong'] else '-':5s} "
              f"heard {','.join(row['heard']) or '-'} {row['seconds']}s (cache {cache.hits}/{cache.hits + cache.misses})",
              flush=True)

    started = time.perf_counter()
    life = S.live_life(seed, arm, S.Settings(**settings), progress=progress, cache=cache)
    life['commit'] = spec_commit
    life['minutes'] = round((time.perf_counter() - started) / 60, 1)
    path.write_text(json.dumps(life, indent=1, default=str), encoding='utf-8')
    w = life['worlds']
    ns = [x for x in w if x['phase'] == 'exam' and x['never_shown']]
    return (f"seed {seed} {arm}: {life['minutes']} min; certified right {sum(x['correct'] for x in w)}/{len(w)}; "
            f"sure-and-wrong {sum(x['sure_and_wrong'] for x in w)}; never-shown right-first "
            f"{sum(x['rank'] == 1 for x in ns)}/{len(ns)}; grounded {life['lexicon']['grounded']}")


spec_commit = 'unknown'


def _init(commit):
    global spec_commit
    spec_commit = commit


def _lab_root():
    """The main checkout, shared by every worktree and snapshot (so the evidence cache is shared too; its folder
    name is a fingerprint of the code, so a snapshot of other code never reads it)."""
    try:
        common = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                                capture_output=True, text=True, cwd=ROOT).stdout.strip()
        return Path(common).parent if common else ROOT
    except OSError:
        return ROOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, nargs='+', default=[1])
    ap.add_argument('--arms', nargs='+', default=list(S.ARMS))
    ap.add_argument('--results', default='core-results/school-dev')
    ap.add_argument('--workers', type=int, default=int(os.environ.get('CORE_WORKERS', '12')))
    ap.add_argument('--taught', type=int, default=S.Settings.n_taught)
    ap.add_argument('--alone', type=int, default=S.Settings.n_alone)
    ap.add_argument('--situations', type=int, default=S.Settings.situations)
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--cache', default=str(_lab_root() / 'scratch' / 'evidence-cache'),
                    help="evidence cache folder shared by the workers ('none' = off; the numbers are the same)")
    a = ap.parse_args()
    if os.environ.get('PYTHONHASHSEED') != '0':
        sys.exit('set PYTHONHASHSEED=0 first (decision D5)')
    settings = dataclasses.asdict(S.Settings(n_taught=a.taught, n_alone=a.alone, situations=a.situations))
    if a.quick:
        a.seeds, a.arms = [1], ['untaught', 'full']
        if a.results == ap.get_default('results'):
            a.results = 'core-results/school-smoke'
        settings.update(n_taught=4, n_alone=2, situations=3, n_exam=2)
    out = Path(a.results)
    out.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True,
                                cwd=ROOT).stdout.strip() or 'unknown'
    except OSError:
        commit = 'unknown'
    cache_dir = None if a.cache == 'none' else a.cache
    EV.Cache(cache_dir).clear_stale()
    jobs =[(s, arm, settings, str(out), cache_dir) for s in a.seeds for arm in a.arms
            if not (out / f'life-seed{s}-{arm}.json').exists()]
    print(f'{len(jobs)} lives to run ({commit}), settings {settings}', flush=True)
    with Pool(min(a.workers, max(len(jobs), 1)), initializer=_init, initargs=(commit,)) as pool:
        for line in pool.imap_unordered(_job, jobs):
            print(line, flush=True)
    print('done')


if __name__ == '__main__':
    main()
