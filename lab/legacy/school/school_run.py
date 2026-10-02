"""ccops5 lab | run the school: every learner through the same puzzle worlds.

Built as an isolated experiment. Not part of sera-field.

    python legacy/school/school_run.py                                 # seeds 1-10, all learners
    python legacy/school/school_run.py --seeds 11 12 13 --results school-fresh
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
from ccops5.school import LEARNERS, live_school  # noqa: E402

NEVER = 12   # "right idea was number" when it never imagined it
LATE = P.SITUATIONS + 1   # "found at situation" when it never found it
BLOCK = 8


def one(job):
    seed, learner, folder = job
    path = ROOT / folder / f'school-seed{seed}-{learner}.json'
    try:
        result = live_school(seed, learner)
    except Exception:
        return path.name, 'FAILED ' + traceback.format_exc()
    path.write_text(json.dumps(result), encoding='utf-8')
    return path.name, f"{result['seconds']:.0f} s"


def _mean(values):
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


def _fmt(value, digits=2, pct=False):
    if value is None:
        return '-'
    return f'{100 * value:.0f}%' if pct else f'{value:.{digits}f}'


def summarize(worlds):
    return {
        'found': _mean([1.0 if w['found'] else 0.0 for w in worlds]),
        'number': _mean([w['right_idea_was_number'] or NEVER for w in worlds]),
        'at': _mean([w['found_at'] or LATE for w in worlds]),
        'wrong': _mean([w['wrong_kept'] for w in worlds]),
        'partly': _mean([w['partly_kept'] for w in worlds]),
        'miss': statistics.median([w['miss'] for w in worlds]) if worlds else None,
        'calibration': _mean([w['calibration'] for w in worlds]),
    }


def write_report(folder):
    out = ROOT / folder
    lives = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(out.glob('school-seed*.json'))]
    by = {name: [life for life in lives if life['learner'] == name] for name in LEARNERS}
    by = {k: v for k, v in by.items() if v}
    seeds = sorted({life['seed'] for life in lives})
    lines = ['# ccops5 school results', '',
             f'Seeds {seeds}: every learner lived the same {P.PRACTICE_WORLDS} practice worlds and the same '
             '12-world exam. In the exam nobody gets help and nobody learns.', '',
             '- **Right idea was number:** how many explanations it imagined before (and including) the '
             f'right one. 1 is best; {NEVER} means it never imagined it.',
             '- **Found at situation:** when it kept the right idea, out of '
             f'{P.SITUATIONS} situations per world; {LATE} means never.',
             '- **Calibration:** how far its confidence was from the truth (0 is perfect, lower is better).', '']
    lines += ['## Practice: getting better at discovering', '',
              'Right idea was number (average), per block of 8 practice worlds. For `taught`, the teacher '
              'showed the answer in block 1 and gave fading hints in blocks 2 and 3.', '',
              '| Learner | ' + ' | '.join(f'worlds {b * BLOCK + 1}-{(b + 1) * BLOCK}'
                                         for b in range(P.PRACTICE_WORLDS // BLOCK)) + ' |',
              '|---|' + '---|' * (P.PRACTICE_WORLDS // BLOCK)]
    for name, group in by.items():
        cells = []
        for b in range(P.PRACTICE_WORLDS // BLOCK):
            ws = [w for life in group for w in life['worlds'][b * BLOCK:(b + 1) * BLOCK]]
            cells.append(_fmt(summarize(ws)['number']))
        lines.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    for title, pick in (('all 12 exam worlds', lambda w: True),
                        ('the 8 kinds of force it practised', lambda w: w['force'] in P.PRACTICE),
                        ('the 4 worlds with forces it was never shown', lambda w: w['force'] in P.NEVER_SHOWN)):
        lines += ['', f'## Final exam: {title}', '',
                  '| Learner | Found the force | Right idea was number | Found at situation | '
                  'Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |',
                  '|---|---|---|---|---|---|---|---|']
        for name, group in by.items():
            ws = [w for life in group for w in life['worlds'] if w['part'] == 'exam' and pick(w)]
            s = summarize(ws)
            lines.append(f"| {name} | {_fmt(s['found'], pct=True)} | {_fmt(s['number'])} | {_fmt(s['at'])} | "
                         f"{_fmt(s['partly'])} | {_fmt(s['wrong'])} | {_fmt(s['miss'], 3)} | {_fmt(s['calibration'], 3)} |")
    lines += ['', '## Doubt: how sure it was about the ideas it kept (exam)', '',
              '| Learner | Kept after one check (sure) | ...of those, right | Kept after two checks (unsure) | '
              '...of those, right |', '|---|---|---|---|---|']
    for name, group in by.items():
        kept = [k for life in group for w in life['worlds'] if w['part'] == 'exam' for k in w['kept_ideas']]
        sure = [k for k in kept if k['confidence'] >= 0.6]
        unsure = [k for k in kept if k['confidence'] < 0.6]
        lines.append(f"| {name} | {len(sure)} | {_fmt(_mean([1.0 if k['right'] else 0.0 for k in sure]), pct=True)} | "
                     f"{len(unsure)} | {_fmt(_mean([1.0 if k['right'] else 0.0 for k in unsure]), pct=True)} |")
    lines += ['', '## Per force in the exam: found the force', '',
              '| Learner | ' + ' | '.join(P.PRACTICE + P.NEVER_SHOWN) + ' |',
              '|---|' + '---|' * (len(P.PRACTICE) + len(P.NEVER_SHOWN))]
    for name, group in by.items():
        cells = []
        for force in P.PRACTICE + P.NEVER_SHOWN:
            ws = [w for life in group for w in life['worlds'] if w['part'] == 'exam' and w['force'] == force]
            cells.append(_fmt(summarize(ws)['found'], pct=True))
        lines.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    (out / 'SCHOOL.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out / 'SCHOOL.md'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(1, 11)))
    parser.add_argument('--learners', nargs='+', default=list(LEARNERS))
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--results', default='school-results')
    args = parser.parse_args()
    (ROOT / args.results).mkdir(exist_ok=True)
    jobs = [(seed, learner, args.results) for seed in args.seeds for learner in args.learners
            if not (ROOT / args.results / f'school-seed{seed}-{learner}.json').exists()]
    if jobs:
        with Pool(min(args.workers, len(jobs))) as pool:
            for name, outcome in pool.imap_unordered(one, jobs):
                print(f'{name}: {outcome}', flush=True)
    print(write_report(args.results))
