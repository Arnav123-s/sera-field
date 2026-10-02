"""ccops5 lab | run the inventor through the school.

Built as an isolated experiment. Not part of sera-field.
(Built in a separate development session.)

    python legacy/inventor/inventor_run.py                                        # seeds 1-10
    python legacy/inventor/inventor_run.py --seeds 11 12 ... 20 --results inventor-fresh
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import statistics
import traceback
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from ccops5 import puzzles as P
from ccops5.inventor import LEARNERS, live_school, PRACTICE, NEVER_SHOWN, PRODUCT_FORCES

NEVER = 12
ORDER = LEARNERS
OLD_FORCES = P.PRACTICE

def one(job):
    seed, learner, folder = job
    path = ROOT / folder / f'inventor-seed{seed}-{learner}.json'
    try:
        result = live_school(seed, learner)
    except Exception:
        return path.name, 'FAILED ' + traceback.format_exc()
    path.write_text(json.dumps(result), encoding='utf-8')
    return path.name, f"{result['seconds']:.0f} s"

def mean_se(values):
    values = [v for v in values if v is not None]
    if not values: return '-'
    m = statistics.fmean(values)
    s = statistics.stdev(values) / len(values) ** 0.5 if len(values) > 1 else 0.0
    return f'{m:.2f} ± {s:.2f}'

def pct(values):
    values = list(values)
    return f'{100 * statistics.fmean(values):.0f}% ({len(values)})' if values else '-'

def exam(life, pick=lambda w: True):
    return [w for w in life['worlds'] if w['part'] == 'exam' and pick(w)]

def write_report(folder):
    out = ROOT / folder
    mine = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(out.glob('inventor-seed*.json'))]
    seeds = sorted({life['seed'] for life in mine})
    lives = list(mine)
    by = {name: [life for life in lives if life['learner'] == name] for name in ORDER}
    by = {k: v for k, v in by.items() if v}

    old_f = lambda w: w['force'] in OLD_FORCES
    prac_inv = lambda w: w['force'] in PRODUCT_FORCES and w['force'] in PRACTICE
    new_sing = lambda w: w['force'] in NEVER_SHOWN and w['force'] not in PRODUCT_FORCES
    new_prod = lambda w: w['force'] in NEVER_SHOWN and w['force'] in PRODUCT_FORCES

    lines = ['# The inventor robot in school', '',
             f'Seeds {seeds}. Numbers are averages over lives, ± one standard error.', '']

    force_check_path = REPO / '(review notes, not published)'
    force_check_text = force_check_path.read_text(encoding='utf-8').strip() if force_check_path.exists() else "No force_check.md found"

    lines += ['## Exam Force Check', '',
              'Are the worlds a fair test? Computed by `(review notes, not published)`: the true idea must explain the world, '
              'nothing may run away, and every product force must beat every old idea and every sum of two old ideas by decisive evidence over one world.',
              '', force_check_text]

    lines += ['', '## Exam', '',
              '| Robot | Old: found | Old: kept nothing | Old: tries | Practised Inv: found | Practised Inv: kept nothing | Practised Inv: tries | New Sing: found | New Sing: kept nothing | New Sing: tries | New Prod: found | New Prod: kept nothing | New Prod: tries | Ideas imagined per world | Guess miss (median) |',
              '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for name, group in by.items():
        cells = []
        for pick in (old_f, prac_inv, new_sing, new_prod):
            cells.append(mean_se([statistics.fmean(1.0 if w['found'] else 0.0 for w in exam(life, pick)) for life in group]))
            cells.append(mean_se([statistics.fmean(1.0 if not w['kept'] else 0.0 for w in exam(life, pick)) for life in group]))
            cells.append(mean_se([statistics.fmean(w['right_idea_was_number'] or NEVER for w in exam(life, pick)) for life in group]))
        cells.append(mean_se([statistics.fmean(w['ideas_imagined'] for w in exam(life)) for life in group]))
        cells.append(f"{statistics.median([w['miss'] for life in group for w in exam(life)]):.3f}")
        lines.append(f'| {name} | ' + ' | '.join(cells) + ' |')

    lines += ['', '## Honesty: the ideas it kept in the exam', '',
              '| Robot | Old: Sure → right | Old: Unsure → right | Old: Sure but not right | Practised Inv: Sure → right | Practised Inv: Unsure → right | Practised Inv: Sure but not right | New Sing: Sure → right | New Sing: Unsure → right | New Sing: Sure but not right | New Prod: Sure → right | New Prod: Unsure → right | New Prod: Sure but not right |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for name, group in by.items():
        row = [f'| {name} |']
        for pick in (old_f, prac_inv, new_sing, new_prod):
            kept = [k for life in group for w in exam(life, pick) for k in w['kept_ideas'] if not k['shown']]
            sure = [k['right'] for k in kept if k['sure']]
            unsure = [k['right'] for k in kept if not k['sure']]
            wrong_sure = [1.0 if (k['sure'] and not k['right']) else 0.0 for k in kept]
            row.append(f"{pct(sure)} | {pct(unsure)} | {pct(wrong_sure)} |")
        lines.append(' '.join(row))

    lines += ['', '## The final check before "sure"', '',
              'Before saying "sure", every robot weighs its idea against every idea it can form. The check never changes what it keeps.', '',
              '| Robot | Exam worlds where a kept idea was wrong | ...and it named the right idea as a rival it could not rule out | Worlds where an idea it never imagined fitted decisively better |',
              '|---|---|---|---|']
    for name, group in by.items():
        worlds = [w for life in group for w in exam(life)]
        wrong = [w for w in worlds if w['kept'] and not w['found']]
        named = sum(1 for w in wrong if w.get('truth_open_rival'))
        better = sum(1 for w in worlds if w.get('audit_better'))
        lines.append(f'| {name} | {len(wrong)} of {len(worlds)} | {named} of {len(wrong)} | {better} of {len(worlds)} |')

    example = next((life for life in mine if life['learner'] == 'inventor'), None)
    if example:
        lines += ['', f"## What it says: the inventor robot's exam, seed {example['seed']}", '']
        for w in exam(example):
            lines.append(f"- **{w['force']}** (truth: {w['truth']}). " + ' '.join(w['says']) + f" `{w['formula']}`")

    lines += ['', '## Changes made', '',
              '- Widened rivals in inventor.py to include every old idea, single-piece variations, and any idea imagined during the world.',
              '- Fixed "sure" to mean the idea beat all these rivals.',
              '- Split the 3x3 leftover grid feature into position-specific and speed-specific templates in `feelings`, so credit carries over correctly to unseen combos.',
              '- Updated INVENTOR.md generation to include "kept nothing" metrics and the force checks.',
              '- Replaced np.abs default fallback in _scalar with explicit size shape, changed all product forces to use size instead of growing/steps so they do not change sign with position.',
              '- Fine-tuned product force strengths to match typical accelerations of old forces and stay well within the (-100, 100) clip range.',
              '- Added a --quick flag to inventor_run.py for faster iterations.',
              '- Categorized exam results into 4 categories: old forces, practised products, never-shown singles, never-shown products.',
              '- Added sure/unsure/wrong metrics for each of the 4 categories.',
              '- (development note) Round 3: the first product forces changed sign with position and ran away into the acceleration clip, so even the true idea explained only 2–34% of moments; they were replaced by stable ones.',
              '- (development note) Round 3: the fairness check "median surprise of the best old idea >= 3" failed (1.1–3.8), because old ideas pass about half the moments. It was replaced, after seeing that, by the robot’s own rule: the true product must beat every old idea and pair by decisive evidence over a world, and the best old rival must fail at least 30% of moments.',
              '- (development note) The held idea is no longer blamed for a moment that no idea can explain (hidden bump), as in the relentless robot.',
              '- (development note) After dev seeds 1–10: "sure" was wrong for 22–42% of kept inventions, because the right idea was two part-swaps away and never became a rival (for example |x|·v kept for x·|v|). Before saying "sure", it now weighs its idea against every idea it can form, over everything it saw. This final check never changes what it keeps, so "found" still measures its own limited search.']

    (ROOT / 'INVENTOR.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return ROOT / 'INVENTOR.md'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(1, 11)))
    parser.add_argument('--learners', nargs='+', default=list(LEARNERS))
    parser.add_argument('--workers', type=int, default=5)
    parser.add_argument('--results', default='inventor-results')
    parser.add_argument('--quick', action='store_true', help='Run a quick smoke test')
    args = parser.parse_args()

    if args.quick:
        import os
        os.environ['CCOPS5_QUICK'] = '1'
        args.seeds = [1]
        args.results = 'experiment-results/inventor/smoke'

    (ROOT / args.results).mkdir(exist_ok=True, parents=True)
    jobs = [(seed, learner, args.results) for seed in args.seeds for learner in args.learners
            if not (ROOT / args.results / f'inventor-seed{seed}-{learner}.json').exists()]
    if jobs:
        with Pool(min(args.workers, len(jobs))) as pool:
            for name, outcome in pool.imap_unordered(one, jobs):
                print(f'{name}: {outcome}', flush=True)
    print(write_report(args.results))
