"""Summarize validated SERA worlds by level."""
import argparse
import json
import multiprocessing
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sera import lawspace, worlds


def _one_world(args):
    """Build one world and return compact measurements."""
    seed, index, level, split = args
    started = time.perf_counter()
    try:
        w = worlds.make(seed, index, level, split)
        throws = w.throws + w.held_out
        return {
            'level': level, 'index': index, 'ok': True,
            'family': lawspace.name(w.spec.family), 'coefs': list(w.spec.coefs),
            'rejected': list(w.rejected),
            'max_abs_x': max(float(np.max(np.abs(t.x))) for t in throws),
            'max_abs_v': max(float(np.max(np.abs(t.v))) for t in throws),
            'seconds': time.perf_counter() - started,
        }
    except RuntimeError as exc:
        return {'level': level, 'index': index, 'ok': False, 'error': str(exc),
                'rejected': [], 'seconds': time.perf_counter() - started}


def _median(values):
    return statistics.median(values) if values else None


def _aggregate(level, rows):
    """Compute summary statistics for one level."""
    good = [r for r in rows if r['ok']]
    reasons = Counter(reason[:50] for r in rows for reason in r.get('rejected', []))
    laws = Counter(r['family'] for r in good)
    positions = []
    for row in good:
        for i, coef in enumerate(row['coefs']):
            while len(positions) <= i:
                positions.append([])
            positions[i].append(abs(float(coef)))
    coef_stats = []
    for i, values in enumerate(positions):
        coef_stats.append({'term_position': i, 'min': min(values), 'median': _median(values), 'max': max(values)})
    xs = [r['max_abs_x'] for r in good]
    vs = [r['max_abs_v'] for r in good]
    seconds = [r['seconds'] for r in rows]
    return {
        'level': level, 'requested': len(rows), 'valid': len(good), 'failed': len(rows) - len(good),
        'rejection_reasons': dict(sorted(reasons.items())), 'distinct_laws': len(laws),
        'common_laws': [{'law': name, 'count': count} for name, count in laws.most_common(10)],
        'coefficient_magnitudes': coef_stats,
        'max_abs_x': {'median': _median(xs), 'max': max(xs) if xs else None},
        'max_abs_v': {'median': _median(vs), 'max': max(vs) if vs else None},
        'seconds_total': sum(seconds), 'seconds_mean': statistics.mean(seconds) if seconds else 0.0,
    }


def _write_report(out, seed, split, rows, aggregates):
    """Write JSON data and a concise Markdown report."""
    out.mkdir(parents=True, exist_ok=True)
    stem = f'levels_seed{seed}_{split}'
    payload = {'seed': seed, 'split': split, 'worlds': rows, 'levels': aggregates}
    (out / f'{stem}.json').write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    lines = [
        '| level | valid/requested | distinct laws | top rejection reason (count) | median max abs x | median max abs v | mean seconds/world |',
        '|---:|---:|---:|---|---:|---:|---:|',
    ]
    for item in aggregates:
        top_reason = max(item['rejection_reasons'].items(), key=lambda pair: (pair[1], pair[0])) if item['rejection_reasons'] else ('none', 0)
        lines.append(f"| {item['level']} | {item['valid']}/{item['requested']} | {item['distinct_laws']} | {top_reason[0]} ({top_reason[1]}) | {item['max_abs_x']['median']} | {item['max_abs_v']['median']} | {item['seconds_mean']:.6f} |")
    for item in aggregates:
        lines.extend(['', f"### Level {item['level']} common laws"])
        if item['common_laws']:
            lines.extend(f"- {law['law']}: {law['count']}" for law in item['common_laws'])
        else:
            lines.append('- none')
    (out / f'{stem}.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main(argv=None):
    """Run the level report command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--per-level', type=int, default=1000)
    parser.add_argument('--levels', type=int, nargs='+', default=[0, 1, 2, 3, 4, 5])
    parser.add_argument('--split', choices=('dream', 'held', 'any'), default='dream')
    parser.add_argument('--workers', type=int, default=2)          # laptop budget (SESSIONS.md)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.per_level < 0 or args.workers < 1:
        parser.error('--per-level must be nonnegative and --workers must be positive')
    rows = []
    for level in args.levels:
        tasks = [(args.seed, i, level, args.split) for i in range(args.per_level)]
        started = time.perf_counter()
        valid = 0
        with multiprocessing.Pool(args.workers) as pool:
            for done, row in enumerate(pool.imap(_one_world, tasks), 1):
                rows.append(row)
                valid += bool(row['ok'])
                if done % 100 == 0:
                    print(f'level {level}, done {done}, valid {valid}, elapsed {time.perf_counter() - started:.2f}s', flush=True)
    aggregates = [_aggregate(level, [r for r in rows if r['level'] == level]) for level in args.levels]
    _write_report(args.out, args.seed, args.split, rows, aggregates)


if __name__ == '__main__':
    main()
