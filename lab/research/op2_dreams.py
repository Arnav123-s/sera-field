"""OP2 side experiment: does "dream school" keep the learner improving after the teacher leaves?

The school world (ccops5/school.py, ccops5/puzzles.py) is used unchanged. The taught learner lives its usual
40 practice worlds (watch, fading hints, teacher credit). Then, before the same 12-world exam (no help,
no learning), it gets one of:
  none          nothing more (the school as it was)
  extra_real    120 more real practice worlds of the practised forces, graded by the teacher (a reference)
  dreams_known  120 dream worlds it makes up from the kinds of force it has practised, graded exactly
                against the law it planted itself
  dreams_all    120 dream worlds from its whole grammar of ideas (every shape along position or speed, and the
                steady push), including combinations it has never kept, graded the same way
  dreams_mixed  120 dream worlds, each drawn half the time from the practised kinds and half the time from the
                whole grammar (added after the first dev run showed dreams_all costing skill on familiar forces)
Dreams use the learner's own grammar and its experience of how strong forces were; they never touch the
exam worlds, whose objects, pushes and noise are identical in every arm (same world index and seed).

    python research/op2_dreams.py --seeds 1 2 3 4 5 6 7 8 9 10 --workers 8
"""
import argparse
import json
import statistics
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch

from ccops5 import puzzles as P
from ccops5 import school as S

ARMS = ('none', 'extra_real', 'dreams_known', 'dreams_all', 'dreams_mixed')
N_EXTRA = 120
# Strength ranges it has experienced along each input in practice (the dreamer's own knowledge).
PRACTISED = {'speed': (0.5, 3.0), 'position': (3.0, 20.0), 'nothing': (0.5, 1.5)}


def build_world(force, rng, part='practice'):
    """A world laid out exactly like puzzles.school_plan's (objects, pushes, tricks)."""
    lo, hi = P.FORCES[force][1]
    world = {'part': part, 'force': force, 'strength': float(rng.uniform(lo, hi)),
             'sign': float(rng.choice([-1.0, 1.0])) if P.FORCES[force][0][0] == 'nothing' else 1.0,
             'masses': [float(m) for m in rng.uniform(0.6, 2.5, size=3)], 'situations': []}
    for _ in range(P.SITUATIONS):
        trick = None
        if rng.random() < P.TRICKS:
            start = float(rng.choice([0.6, 0.8, 1.0, 1.2]))
            trick = (start, start + 0.2, float(rng.choice([-1.5, 1.5])))
        world['situations'].append({'m': float(rng.choice(world['masses'])), 'trick': trick,
                                    'pushes': (float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0]))),
                                    'check_u': float(rng.choice(P.W.CHECK_COMMANDS))})
    return world


def register_dream_forces():
    """Dream laws: every idea in the grammar, with the strength range the learner has met along that input.
    Registered under new names so the real forces (and the exam) are untouched."""
    names = {}
    for idea in P.IDEAS:
        name = f'dream: {P.explain(idea)}'
        P.FORCES[name] = (idea, PRACTISED[idea[0]])
        names[idea] = name
    return names


def live(args):
    seed, arm = args
    torch.set_num_threads(1)
    started = time.perf_counter()
    dream_names = register_dream_forces()
    plan = P.school_plan(seed)
    practice = [w for w in plan if w['part'] == 'practice']
    exam = [w for w in plan if w['part'] == 'exam']
    student = S.Student('taught', seed)
    for i, world in enumerate(practice):
        student.live_world(world, i, seed)
    rng = np.random.default_rng([seed, 777, ARMS.index(arm)])
    practised_ideas = sorted({P.FORCES[f][0] for f in P.PRACTICE})
    for d in range(N_EXTRA if arm != 'none' else 0):
        if arm == 'extra_real':
            world = build_world(P.PRACTICE[int(rng.integers(len(P.PRACTICE)))], rng)
        else:
            known = arm == 'dreams_known' or (arm == 'dreams_mixed' and rng.random() < 0.5)
            pool = practised_ideas if known else list(P.IDEAS)
            world = build_world(dream_names[pool[int(rng.integers(len(pool)))]], rng)
        student.live_world(world, 1000 + d, seed)        # part='practice': graded, credit to the hunch
    records = [student.live_world(world, len(practice) + i, seed) for i, world in enumerate(exam)]
    return {'seed': seed, 'arm': arm, 'exam': records, 'seconds': time.perf_counter() - started}


def summarise(results):
    lines = ['| Arm | Familiar: found | Familiar: tries | New: found | New: tries | Right idea first (all exam) | Sure but not right |',
             '|---|---|---|---|---|---|---|']
    for arm in ARMS:
        rows = [r for res in results if res['arm'] == arm for r in res['exam']]
        if not rows:
            continue
        fam =[r for r in rows if r['force'] not in P.NEVER_SHOWN]
        new = [r for r in rows if r['force'] in P.NEVER_SHOWN]

        def tries(rs):
            return statistics.fmean((r['right_idea_was_number'] or 12) for r in rs)

        def se_tries(rs):
            v = [(r['right_idea_was_number'] or 12) for r in rs]
            return statistics.stdev(v) / len(v) ** 0.5

        first = statistics.fmean(1.0 if r['right_idea_was_number'] == 1 else 0.0 for r in rows)
        kept = [k for r in rows for k in r['kept_ideas'] if not k['shown']]
        sure_wrong = [k for k in kept if k['confidence'] >= S.SURE and not k['right']]
        sure = [k for k in kept if k['confidence'] >= S.SURE]
        lines.append(f'| {arm} | {statistics.fmean(r["found"] for r in fam):.0%} | {tries(fam):.2f} ± {se_tries(fam):.2f} | '
                     f'{statistics.fmean(r["found"] for r in new):.0%} | {tries(new):.2f} ± {se_tries(new):.2f} | {first:.0%} | '
                     f'{len(sure_wrong)} of {len(sure)} sure |')
    lines += ['', paired(results)]
    return '\n'.join(lines)


def paired(results):
    """Each arm minus 'none' on the very same exam world (same seed, same index, same noise): tries saved."""
    tries = {(res['arm'], res['seed'], r['index']): ((r['right_idea_was_number'] or 12), r['force'] in P.NEVER_SHOWN)
             for res in results for r in res['exam']}
    lines = ['| Arm minus none (same exam worlds) | Familiar: change in tries | New: change in tries |', '|---|---|---|']
    for arm in ARMS[1:]:
        cells = []
        for new in (False, True):
            d = [tries[(arm, s, i)][0] - t for (a, s, i), (t, n) in tries.items()
                 if a == 'none' and n == new and (arm, s, i) in tries]
            if len(d) < 2:
                cells.append('–')
                continue
            m, se = statistics.fmean(d), statistics.stdev(d) / len(d) ** 0.5
            cells.append(f'{m:+.2f} ± {se:.2f} (n={len(d)})')
        lines.append(f'| {arm} | {cells[0]} | {cells[1]} |')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, nargs='+', default=list(range(1, 11)))
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--out', default='research/op2-results.json')
    ap.add_argument('--summarise', help='only summarise a saved results file')
    a = ap.parse_args()
    if a.summarise:
        print(summarise(json.loads(Path(a.summarise).read_text(encoding='utf-8'))))
        return
    jobs = [(s, arm) for s in a.seeds for arm in ARMS]
    with Pool(a.workers) as pool:
        results = pool.map(live, jobs)
    Path(a.out).write_text(json.dumps(results), encoding='utf-8')
    print(f'seeds {a.seeds}; {N_EXTRA} extra worlds per arm; exam identical across arms')
    print(summarise(results))


if __name__ == '__main__':
    main()
