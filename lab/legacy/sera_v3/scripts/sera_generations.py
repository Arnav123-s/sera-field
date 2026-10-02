"""B5: the compounding test - lives of generations (sera.generations), full vs no-slots vs frozen, under the governor.

  python legacy/sera_v3/scripts/sera_generations.py --name b5-dev --model imagine-v1 --seeds 1 --generations 4 --max-workers 3
One unit = one life (seed, arm) -> sera-runs/<name>/gen-seed<s>-<arm>.json, with a .progress.jsonl line per world.
Summary (sera-runs/<name>/summary.md): per arm and generation - the imagination on the frozen suite (top-1, top-16,
mean p(true)), the full-mind evaluation subset (right, sure-and-wrong, checker refusals, mean throws, split by
met / slot-dreamed / neither), library size, CPU seconds C_k, and g_k = (J_{k+1} - J_k) / C_k with J = eval right share.
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
    folder, model, seed, arm, generations = unit
    path = Path(folder) / f'gen-seed{seed}-{arm}.json'
    if path.exists():
        return
    from legacy.sera_v3 import generations as GN
    trail = Path(folder) / f'gen-seed{seed}-{arm}.progress.jsonl'
    ckpt = Path(folder) / f'gen-seed{seed}-{arm}.ckpt'
    if not ckpt.exists():
        trail.write_text('', encoding='utf-8')                   # a resumed life keeps its trail

    def progress(row):
        with trail.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, default=str) + '\n')
        if row.get('summary'):
            print(f"  seed {seed} {arm:8s} generation {row['generation']}: imagination {row['imagination']} "
                  f"eval {row['eval']} library {row['library']}", flush=True)
        else:
            print(f"  seed {seed} {arm:8s} g{row['generation']} #{row['n']:2d} L{row['level']} "
                  f"{'RIGHT' if row['right'] else 'wrong' if row['wrong'] else '-':5s} never-met {row['never_met']} "
                  f"throws {row['throws']} cpu {row['cpu']}s", flush=True)

    life = GN.live(seed, arm, str(RUNS / model / 'model.pt'), generations=generations, progress=progress,
                   checkpoint=str(ckpt))
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(life, indent=1, default=str), encoding='utf-8')
    os.replace(tmp, path)


def summarize(folder):
    lives = [json.loads(Path(f).read_text(encoding='utf-8')) for f in glob.glob(str(Path(folder) / 'gen-*.json'))]
    lines = ['| seed | arm | generation | imagination top-1 / top-16 / p(true) | eval right | sure and wrong | '
             'checker refused | mean throws | met / slot-dreamed / neither (right) | library | C_k (CPU s) | g_k |',
             '|' + '---|' * 12]
    for L in sorted(lives, key=lambda l: (l['seed'], l['arm'])):
        gens = L['generations']
        for i, g in enumerate(gens):
            im, ev = g['imagination'], g.get('eval') or {}
            cost = g.get('wake_cpu', 0) + g.get('sleep_cpu', 0)
            gk = ''
            if i + 1 < len(gens) and ev and gens[i + 1].get('eval'):
                nxt = gens[i + 1]
                c_next = nxt.get('wake_cpu', 0) + nxt.get('sleep_cpu', 0)
                if c_next:
                    gk = f"{(nxt['eval']['right'] - ev['right']) / max(ev['n'], 1) / c_next:.2e}"
            bs = ev.get('by_status', {})
            status = ' / '.join(f"{bs.get(s, {}).get('n', 0)} ({bs.get(s, {}).get('right', 0)})"
                                for s in ('met', 'slot-dreamed', 'neither'))
            lines.append(f"| {L['seed']} | {L['arm']} | {g['generation']} | {im['top1']:.2f} / {im['top16']:.2f} / "
                         f"{im['p_true']:.2f} | {ev.get('right', '-')}/{ev.get('n', '-')} | {ev.get('wrong', '-')} | "
                         f"{ev.get('sure_unverified', '-')} | {ev.get('throws', 0):.1f} | {status} | {g.get('library', 0)} | "
                         f"{cost:.0f} | {gk} |")
    text = '\n'.join(lines) + '\n'
    (Path(folder) / 'summary.md').write_text(text, encoding='utf-8')
    return text


def main(argv=None):
    import governor
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default='b5-dev')
    ap.add_argument('--model', default='imagine-v1')
    ap.add_argument('--seeds', type=int, nargs='+', default=[1])
    ap.add_argument('--arms', nargs='+', default=['full', 'no-slots', 'frozen'])
    ap.add_argument('--generations', type=int, default=4)
    ap.add_argument('--max-workers', type=int, default=3)
    a = ap.parse_args(argv)
    folder = RUNS / a.name
    folder.mkdir(parents=True, exist_ok=True)
    units = [(str(folder), a.model, s, arm, a.generations) for s in a.seeds for arm in a.arms
             if not (folder / f'gen-seed{s}-{arm}.json').exists()]
    print(f'{len(units)} lives to run in {folder}', flush=True)
    if units:
        governor.run_units(run_life, units, a.max_workers, log=lambda s: print(s, flush=True))
    print(summarize(folder), flush=True)


if __name__ == '__main__':
    main()
