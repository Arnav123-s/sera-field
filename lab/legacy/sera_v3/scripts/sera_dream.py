"""Make dream shards for training the imagination, under the thermal governor (resumable; nothing is redone).

  python legacy/sera_v3/scripts/sera_dream.py --set dreams-v1 --shards 100 --per-shard 500 --max-workers 3
Each shard is D:/ai/labs/ccops5-sera-lab/sera-runs/<set>/shard-<i>.npz: features (n, 270, 8) float16, world (n, 7),
label (n,) = index into sera.dreams.FAMILIES, level (n,). Shard i uses its own random stream [seed, i], so the set is
the same however many workers made it and in whatever order.
"""
import argparse
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2]))  # the repo root
sys.path.insert(0, str(ROOT.parents[2] / 'scripts'))  # governor, heat_guard
sys.path.insert(0, str(ROOT))
RUNS = Path('D:/ai/labs/ccops5-sera-lab/sera-runs')


def make_shard(unit):
    folder, seed, i, n = unit
    path = Path(folder) / f'shard-{i:05d}.npz'
    if path.exists():
        return
    from legacy.sera_v3 import dreams as D
    rng = np.random.default_rng([seed, 9001, i])
    feats, world, label, level = D.dream_tables(rng, n)
    tmp = path.with_suffix('.tmp.npz')
    np.savez(tmp, features=feats, world=world, label=label, level=level)
    os.replace(tmp, path)


def main(argv=None):
    import governor
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='dreams-v1')
    ap.add_argument('--shards', type=int, default=100)
    ap.add_argument('--per-shard', type=int, default=500)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--max-workers', type=int, default=3)
    a = ap.parse_args(argv)
    folder = RUNS / a.set
    folder.mkdir(parents=True, exist_ok=True)
    units = [(str(folder), a.seed, i, a.per_shard) for i in range(a.shards)
             if not (folder / f'shard-{i:05d}.npz').exists()]
    print(f'{len(units)} shards to make in {folder} (of {a.shards})', flush=True)
    if units:
        governor.run_units(make_shard, units, a.max_workers, log=lambda s: print(s, flush=True))
    print('done', flush=True)


if __name__ == '__main__':
    main()
