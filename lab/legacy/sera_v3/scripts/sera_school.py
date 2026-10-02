"""B3 teaching test: lives of never-dreamed law structures, taught vs verified-only vs frozen (sera.school).

  python legacy/sera_v3/scripts/sera_school.py --name school-dev --model imagine-v1 --seeds 1 2 --max-workers 3
One unit = one life (seed, arm) -> sera-runs/<name>/life-seed<s>-<arm>.json, with a .progress.jsonl line per world.
Summary (sera-runs/<name>/summary.md): per arm and phase, worlds, right (exact, verified), sure and wrong, mean
throws, mean own pushes, mean rank and probability of the true law in the imagination at the start of the world.
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2]))  # the repo root
sys.path.insert(0, str(ROOT.parents[2] / 'scripts'))  # governor, heat_guard
sys.path.insert(0, str(ROOT))
RUNS = Path('D:/ai/labs/ccops5-sera-lab/sera-runs')


def run_life(unit):
    folder, model, seed, arm = unit
    path = Path(folder) / f'life-seed{seed}-{arm}.json'
    if path.exists():
        return
    from legacy.sera_v3 import school
    trail = Path(folder) / f'life-seed{seed}-{arm}.progress.jsonl'
    trail.write_text('', encoding='utf-8')

    def progress(row):
        with trail.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row) + '\n')
        print(f"  seed {seed} {arm:8s} #{row['n']:2d} {row['phase']:6s} L{row['level']} {row['split']:5s} "
              f"rank {row['rank']} p {row['p_true']:.3f} {'RIGHT' if row['right'] else 'wrong' if row['wrong'] else '-':5s} "
              f"throws {row['throws']} learned {row['learned'] or '-'} {row['seconds']}s", flush=True)

    life = school.live_life(seed, arm, str(RUNS / model / 'model.pt'), progress=progress)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(life, indent=1), encoding='utf-8')
    os.replace(tmp, path)


def summarize(folder):
    lives = [json.loads(Path(f).read_text(encoding='utf-8')) for f in glob.glob(str(Path(folder) / 'life-*.json'))]
    lines = ['| arm | phase | worlds | right | sure and wrong | mean throws | mean own pushes | truth imagined (top 16) | '
             'mean p(true) at start |', '|' + '---|' * 9]
    for arm in ('taught', 'verified', 'frozen'):
        for phase in ('taught', 'alone'):
            rows = [w for L in lives if L['arm'] == arm for w in L['worlds'] if w['phase'] == phase]
            if not rows:
                continue
            n = len(rows)
            mean = lambda k: sum(r[k] for r in rows) / n
            lines.append(f"| {arm} | {phase} | {n} | {sum(r['right'] for r in rows)}/{n} | {sum(r['wrong'] for r in rows)} | "
                         f"{mean('throws'):.1f} | {mean('own'):.1f} | {sum(r['rank'] is not None for r in rows)}/{n} | "
                         f"{mean('p_true'):.3f} |")
    text = '\n'.join(lines) + '\n'
    (Path(folder) / 'summary.md').write_text(text, encoding='utf-8')
    return text


def main(argv=None):
    import governor
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default='school-dev')
    ap.add_argument('--model', default='imagine-v1')
    ap.add_argument('--seeds', type=int, nargs='+', default=[1])
    ap.add_argument('--arms', nargs='+', default=['taught', 'verified', 'frozen'])
    ap.add_argument('--max-workers', type=int, default=3)
    a = ap.parse_args(argv)
    folder = RUNS / a.name
    folder.mkdir(parents=True, exist_ok=True)
    units = [(str(folder), a.model, s, arm) for s in a.seeds for arm in a.arms
             if not (folder / f'life-seed{s}-{arm}.json').exists()]
    print(f'{len(units)} lives to run in {folder}', flush=True)
    if units:
        governor.run_units(run_life, units, a.max_workers, log=lambda s: print(s, flush=True))
    print(summarize(folder), flush=True)


if __name__ == '__main__':
    main()
