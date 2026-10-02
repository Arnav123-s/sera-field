"""C2 parity check against saved school or inventor runs."""

import argparse
import json
import multiprocessing
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import core_check
from ccops5.core import adapters, mind, truth
from ccops5 import inventor, puzzles


def _core_world(spec):
    track, seed, i = spec
    w = (adapters.legacy_school_world(seed, i) if track == 'school'
         else adapters.legacy_inventor_world(seed, i))
    report = mind.Mind(w.sigma, eps=0.5, budget=2).live(w)
    accepted = bool(report.sure and truth.Library(w.sigma).record(report.certificate, report.ledger.throws))
    wrong = accepted and core_check.wrong(report.certificate, w)     # the M1 checks' own definition
    return {'index': i, 'force': w.force, 'part': w.part,
            'representable': getattr(w, 'representable', True),
            'core_found': bool(accepted and report.claim == w.truth),
            'core_sure': bool(accepted), 'core_wrong': bool(wrong)}


def t4_summary(rows):
    settled = [row for row in rows if row['legacy_sure'] and row['legacy_found']]
    core_of_those = sum(row['core_sure'] and row['core_found'] and not row['core_wrong']
                        for row in settled)
    core_wrong = sum(row['core_sure'] and row['core_wrong'] for row in rows)
    legacy_wrong = sum(row['legacy_sure'] and not row['legacy_found'] for row in rows)
    share = core_of_those / len(settled) if settled else 0.0
    return {'legacy_settled_right': len(settled), 'core_settles_of_those': share,
            'core_sure_and_wrong': core_wrong, 'legacy_sure_and_wrong': legacy_wrong,
            'pass_t4': share >= 0.70 and core_wrong == 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--track', choices=('school', 'inventor'), default='school')
    parser.add_argument('--seeds', type=int, nargs='+', required=True)
    parser.add_argument('--legacy', type=Path)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get('PYTHONHASHSEED') != '0':
        parser.error('PYTHONHASHSEED=0 is required')
    if args.workers < 1:
        parser.error('--workers must be positive')
    legacy_dir = args.legacy or (Path('legacy/relentless/relentless-results') if args.track == 'school'
                                 else Path('legacy/inventor/inventor-results'))

    sources = {}
    jobs = []
    for seed in args.seeds:
        path = (legacy_dir / f'school-seed{seed}-relentless.json' if args.track == 'school'
                else legacy_dir / f'inventor-seed{seed}-inventor.json')
        with path.open('r', encoding='utf-8') as stream:
            saved = json.load(stream)
        plan = puzzles.school_plan(seed) if args.track == 'school' else inventor.school_plan(seed)
        learner = 'relentless' if args.track == 'school' else 'inventor'
        if saved.get('seed') != seed or saved.get('learner') != learner or saved.get('gentle'):
            raise ValueError(f'wrong legacy run: {path}')
        if len(saved['worlds']) != len(plan):
            raise ValueError(f'world count differs: {path}')
        for i, (old, source) in enumerate(zip(saved['worlds'], plan)):
            if (old['index'], old['force'], old['part']) != (i, source['force'], source['part']):
                raise ValueError(f'world {i} differs: {path}')
            jobs.append((args.track, seed, i))
        sources[seed] = saved['worlds']

    with multiprocessing.Pool(args.workers) as pool:
        core = pool.map(_core_world, jobs)
    grouped = {seed: [] for seed in args.seeds}
    for (_, seed, i), row in zip(jobs, core):
        old = sources[seed][i]
        row['legacy_found'] = bool(old['found'])
        row['legacy_sure'] = bool(old['sure'])
        if args.track == 'inventor':
            row['part'] = ('never_shown' if old['part'] == 'exam' and old['force'] in inventor.NEVER_SHOWN
                           else old['part'])
        grouped[seed].append(row)

    args.out.mkdir(parents=True, exist_ok=True)
    for seed, rows in grouped.items():
        with (args.out / f'c2_seed{seed}.json').open('w', encoding='utf-8') as stream:
            json.dump({'seed': seed, 'worlds': rows, 't4': t4_summary(rows)}, stream, indent=2)
            stream.write('\n')

    all_rows = [row for seed in args.seeds for row in grouped[seed]]
    parts = ('practice', 'exam', 'all') if args.track == 'school' else ('practice', 'exam', 'never_shown', 'all')
    for part in parts:
        rows = all_rows if part == 'all' else [row for row in all_rows if row['part'] == part]
        if args.track == 'inventor':
            rows = [row for row in rows if row['representable']]
        if not rows:
            continue
        core_rate = sum(row['core_found'] for row in rows) / len(rows)
        legacy_rate = sum(row['legacy_found'] for row in rows) / len(rows)
        print(f'{part}: core found {core_rate:.3f}, legacy found {legacy_rate:.3f} ({len(rows)} worlds)')
    if args.track == 'inventor':
        for row in all_rows:
            if row['representable']:
                print(f"world {row['index']} {row['force']} ({row['part']}): "
                      f"core found {row['core_found']}, sure {row['core_sure']}, wrong {row['core_wrong']}; "
                      f"legacy found {row['legacy_found']}, sure {row['legacy_sure']}")
        outside = [row for row in all_rows if not row['representable']]
        print(f'unrepresentable: {len(outside)} worlds')
        for row in outside:
            print(f"  world {row['index']} {row['force']} ({row['part']}): core found {row['core_found']}, "
                  f"sure {row['core_sure']}, wrong {row['core_wrong']}; "
                  f"legacy found {row['legacy_found']}, sure {row['legacy_sure']}")
    wrong = sum(row['core_sure'] and row['core_wrong'] for row in all_rows)
    eligible = [row for row in all_rows if row['representable']]
    core_rate = sum(row['core_found'] for row in eligible) / len(eligible)
    legacy_rate = sum(row['legacy_found'] for row in eligible) / len(eligible)
    passed = core_rate >= legacy_rate - 0.05 and wrong == 0
    t4 = t4_summary(all_rows)
    print(f"T4: legacy settled right {t4['legacy_settled_right']}; core settles of those "
          f"{t4['core_settles_of_those']:.3f}; core sure-and-wrong {t4['core_sure_and_wrong']}; "
          f"legacy sure-and-wrong {t4['legacy_sure_and_wrong']}; "
          f"T4: {'PASS' if t4['pass_t4'] else 'FAIL'}")
    print(f'core sure-and-wrong: {wrong}; C2: {"PASS" if passed else "FAIL"}')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
