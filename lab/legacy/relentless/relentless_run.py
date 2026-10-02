"""ccops5 lab | run the relentless robot through the school, and compare it
with the robots that went before, on the same seeds.

Built as an isolated experiment. Not part of sera-field.

    python legacy/relentless/relentless_run.py                                        # seeds 1-10
    python legacy/relentless/relentless_run.py --seeds 11 12 ... 30 --results relentless-fresh --others ../school/school-fresh ../school/school-fresh2
    python legacy/relentless/relentless_run.py --gentle --results relentless-gentle --others     # soft pushes
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

from ccops5 import puzzles as P  # noqa: E402
from ccops5.relentless import LEARNERS, live_relentless  # noqa: E402
from ccops5.school import LEARNERS as BEFORE  # noqa: E402

NEVER = 12   # "right idea was number" when it never imagined it
ORDER = LEARNERS + BEFORE


def one(job):
    seed, learner, folder, soft = job
    path = ROOT / folder / f'school-seed{seed}-{learner}.json'
    try:
        result = live_relentless(seed, learner, soft)
    except Exception:
        return path.name, 'FAILED ' + traceback.format_exc()
    path.write_text(json.dumps(result), encoding='utf-8')
    return path.name, f"{result['seconds']:.0f} s"


def mean_se(values):
    values = [v for v in values if v is not None]
    if not values:
        return '-'
    m = statistics.fmean(values)
    s = statistics.stdev(values) / len(values) ** 0.5 if len(values) > 1 else 0.0
    return f'{m:.2f} ± {s:.2f}'


def pct(values):
    values = list(values)
    return f'{100 * statistics.fmean(values):.0f}% ({len(values)})' if values else '-'


def exam(life, pick=lambda w: True):
    return [w for w in life['worlds'] if w['part'] == 'exam' and pick(w)]


def is_sure(learner, kept):
    # The relentless robots are sure when every rival is beaten; the others
    # when their hunch felt strong (as in the school's doubt table).
    return kept['sure'] if learner in LEARNERS else kept['confidence'] >= 0.6


def write_report(folder, others):
    out = ROOT / folder
    mine = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(out.glob('school-seed*.json'))]
    seeds = sorted({life['seed'] for life in mine})
    lives = list(mine)
    for other in others:
        for p in sorted((ROOT / other).glob('school-seed*.json')):
            life = json.loads(p.read_text(encoding='utf-8'))
            if life['seed'] in seeds and life['learner'] in BEFORE:
                lives.append(life)
    by = {name: [life for life in lives if life['learner'] == name] for name in ORDER}
    by = {k: v for k, v in by.items() if v}
    familiar = lambda w: w['force'] in P.PRACTICE  # noqa: E731
    new = lambda w: w['force'] in P.NEVER_SHOWN  # noqa: E731
    soft = any(life.get('gentle') for life in mine)
    lines = ['# The relentless robot in school' + (': gentle worlds' if soft else ''), '',
             *(['In these worlds every robot pushes softly (0.3 each way); only the relentless robot may '
                'push harder where its idea and a rival would part.', ''] if soft else []),
             f'Seeds {seeds}. Every robot lived the same 40 practice worlds and the same 12-world exam. '
             'Numbers are averages over lives, ± one standard error.', '',
             '- **Tries:** explanations it imagined before and including the right one (1 is best; '
             f'{NEVER} means never).',
             '- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch '
             'felt strong (0.6 or more), as in the school.', '',
             '## Exam', '',
             '| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |',
             '|---|---|---|---|---|---|']
    for name, group in by.items():
        cells = []
        for pick in (familiar, new):
            cells.append(mean_se([statistics.fmean(1.0 if w['found'] else 0.0 for w in exam(life, pick))
                                  for life in group]))
            cells.append(mean_se([statistics.fmean(w['right_idea_was_number'] or NEVER for w in exam(life, pick))
                                  for life in group]))
        cells.append(mean_se([statistics.fmean(w['ideas_imagined'] for w in exam(life)) for life in group]))
        lines.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    lines += ['', '## Honesty: the ideas it kept in the exam', '',
              '| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |', '|---|---|---|---|']
    for name, group in by.items():
        kept = [k for life in group for w in exam(life) for k in w['kept_ideas'] if not k['shown']]
        sure = [k['right'] for k in kept if is_sure(name, k)]
        unsure = [k['right'] for k in kept if not is_sure(name, k)]
        wrong_sure = [1.0 if (is_sure(name, k) and not k['right']) else 0.0 for k in kept]
        lines.append(f'| {name} | {pct(sure)} | {pct(unsure)} | {pct(wrong_sure)} |')
    lines += ['', '## Per force in the exam: found the force', '',
              '| Robot | ' + ' | '.join(P.PRACTICE + P.NEVER_SHOWN) + ' |',
              '|---|' + '---|' * (len(P.PRACTICE) + len(P.NEVER_SHOWN))]
    for name, group in by.items():
        cells = [pct(1.0 if w['found'] else 0.0 for life in group for w in exam(life, lambda w, f=f: w['force'] == f))
                 for f in P.PRACTICE + P.NEVER_SHOWN]
        lines.append(f'| {name} | ' + ' | '.join(c.split(' ')[0] for c in cells) + ' |')
    lines += ['', '## What the relentless robots did (exam, per world)', '',
              '| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |',
              '|---|---|---|---|---|---|---|---|']
    for name in LEARNERS:
        group = by.get(name)
        if not group:
            continue
        ws = [w for life in group for w in exam(life)]
        changed = sum(w['changed_mind'] for life in group for w in life['worlds'])
        lines.append(f"| {name} | {mean_se([w['tests'] for w in ws])} | {mean_se([w['rivals_beaten'] for w in ws])} | "
                     f"{changed} | {pct(1.0 if w['sure'] else 0.0 for w in ws)} | "
                     f"{pct(1.0 if w['found'] else 0.0 for w in ws if w['sure'])} | "
                     f"{pct(1.0 if not w['sure'] else 0.0 for w in ws)} | "
                     f"{pct(1.0 if w['found'] else 0.0 for w in ws if not w['sure'])} |")
    example = next((life for life in mine if life['learner'] == 'relentless'), None)
    if example:
        lines += ['', f"## What it says: the relentless robot's exam, seed {example['seed']}", '']
        for w in exam(example):
            lines.append(f"- **{w['force']}** (truth: {w['truth']}). " + ' '.join(w['says']) + f" `{w['formula']}`")
    (out / 'RELENTLESS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out / 'RELENTLESS.md'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(1, 11)))
    parser.add_argument('--learners', nargs='+', default=list(LEARNERS))
    parser.add_argument('--workers', type=int, default=5)
    parser.add_argument('--results', default='relentless-results')
    parser.add_argument('--others', nargs='*', default=['../school/school-results'])
    parser.add_argument('--gentle', action='store_true')
    args = parser.parse_args()
    (ROOT / args.results).mkdir(exist_ok=True)
    jobs = [(seed, learner, args.results, args.gentle) for seed in args.seeds for learner in args.learners
            if not (ROOT / args.results / f'school-seed{seed}-{learner}.json').exists()]
    if jobs:
        with Pool(min(args.workers, len(jobs))) as pool:
            for name, outcome in pool.imap_unordered(one, jobs):
                print(f'{name}: {outcome}', flush=True)
    print(write_report(args.results, args.others))
