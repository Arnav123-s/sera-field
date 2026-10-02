"""ccops5 lab | runs the ball-throw world and writes BALL.md.

    python legacy/ball/ball_run.py                                   # dev seeds 1-10
    python legacy/ball/ball_run.py --seeds 21 ... 30 --results ball-fresh2    # version 2's fresh seeds, run once
    python legacy/ball/ball_run.py --quick                           # seed 1, all learners, into ball-smoke/

(ball-fresh/ holds version 1's fresh seeds 11-20 and ball-results-v1/ its dev seeds, kept as records.)

A life: every ball is pushed along a rail once. Then, in the vacuum room, air, the windy yard and
the water tank, the teacher throws each ball twice, except one place per ball that is kept back
(two balls per place). The loop robots may then throw balls themselves; the network gets as many
random extra throws as they may. Then the tests: balls in the places they were never thrown in,
new throws of balls it has seen, throwing to a target, the moon, and naming heavy and light.

Built as an isolated experiment. Not part of sera-field.
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import statistics
import time
import traceback
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

import numpy as np
import torch

from ccops5 import ballworld as B
from ccops5.ballmind import OWN_THROWS, TRUTH, Mind, Net, describe, kinematics, landing, miss, speed_for

LEARNERS = ('concept', 'per_place', 'baseline')
MOON_BALLS, MOON_CHECK = (0, 1, 2, 3), 5
K_TRUTH = {('air', 'drag2'): 2, ('windy', 'drag2'): 2, ('water', 'drag2'): 2, ('water', 'down'): 3}


def teacher_throw(seed, place, ball, k):
    rng = np.random.default_rng([seed, 31, B.PLACES.index(place), ball, k])
    return float(rng.uniform(1, 4) if place == 'water' else rng.uniform(2, 8)), float(rng.uniform(0.3, 1.3))


def check_throw(seed, place, ball, k):
    rng = np.random.default_rng([seed, 53, B.PLACES.index(place), ball, k])
    return float(rng.uniform(1, 3.5) if place == 'water' else rng.uniform(2, 7)), float(rng.uniform(0.4, 1.2))


def plain(x):
    """JSON-friendly copy."""
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [plain(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        return x.item()
    return x


def live(seed, learner):
    torch.set_num_threads(1)
    started = time.perf_counter()
    life = B.make_life(seed)
    balls, by_id = life['balls'], {b['id']: b for b in life['balls']}
    public = [{k: b[k] for k in ('id', 'seen_size', 'look', 'rail_speed')} for b in balls]
    mind = Net(seed, public) if learner == 'baseline' else Mind(learner, public, seed)
    log = []

    def world(place, ball, speed, angle, tag, k):
        log.append({'place': place, 'ball': ball, 'tag': tag})
        return B.simulate(place, by_id[ball], speed, angle, B.wind_of(life, place),
                          B.throw_rng(seed, place, ball, tag, k))

    for place in B.TRAINING:
        seen = [b['id'] for b in balls if life['held_out'][b['id']] != place]
        for ball in seen:
            for k in range(2):
                mind.see(place, ball, *world(place, ball, *teacher_throw(seed, place, ball, k), 'teacher', k))
        if learner == 'baseline':
            rng = np.random.default_rng([seed, 41, B.PLACES.index(place)])
            for k in range(OWN_THROWS):
                ball = int(rng.choice(seen))
                mind.see(place, ball, *world(place, ball, *teacher_throw(seed, place, ball, 100 + k), 'extra', k))
        else:
            mind.learn_place(place, throw=lambda ball, s, a, k, place=place: world(place, ball, s, a, 'own', k),
                             allowed=seen)
    if learner == 'concept':
        mind.form_concept()

    def guess(place, ball, speed, angle):
        log.append({'place': place, 'ball': ball, 'tag': 'predict'})
        return mind.predict(place, ball, speed, angle)

    out = {'seed': seed, 'learner': learner, 'held_out': life['held_out']}
    never, seen_miss = [], []
    for b in balls:
        place = life['held_out'][b['id']]
        for k in range(2):
            s, a = check_throw(seed, place, b['id'], k)
            never.append({'place': place, 'ball': b['id'],
                          'miss': miss(*guess(place, b['id'], s, a), *world(place, b['id'], s, a, 'check', k))})
    for place in B.TRAINING:
        for ball in [b['id'] for b in balls if life['held_out'][b['id']] != place][:2]:
            s, a = check_throw(seed, place, ball, 0)
            seen_miss.append(miss(*guess(place, ball, s, a), *world(place, ball, s, a, 'check', 0)))
    out['never_seen'] = never
    out['seen_miss'] = seen_miss

    # Throw to a target in air: balls seen there, and balls never thrown there.
    back = []
    for ball in [b['id'] for b in balls if life['held_out'][b['id']] != 'air'][:2] + \
            [b['id'] for b in balls if life['held_out'][b['id']] == 'air']:
        s = float(np.random.default_rng([seed, 61, ball]).uniform(3, 7))
        target = landing(*world('air', ball, s, 0.8, 'throwback', 0))
        chosen = speed_for(lambda sp, an: guess('air', ball, sp, an), target, 0.8)
        land = landing(*world('air', ball, chosen, 0.8, 'throwback', 1))
        back.append({'ball': ball, 'never_seen': life['held_out'][ball] == 'air',
                     'error': abs(land - target) if land is not None and target is not None else None})
    out['throw_back'] = back

    # The moon: never shown until now. Throws come one at a time; it predicts a ball never thrown there.
    moon = []
    for i, ball in enumerate(MOON_BALLS):
        xs, ys = world('moon', ball, *teacher_throw(seed, 'moon', ball, 0), 'moon', 0)
        if i == 0 and learner != 'baseline':
            out['moon_surprise'] = mind.surprise_on('vacuum', kinematics(xs, ys))
        mind.see('moon', ball, xs, ys)
        if learner != 'baseline':
            mind.learn_place('moon')
        s, a = check_throw(seed, 'moon', MOON_CHECK, 0)
        moon.append(miss(*guess('moon', MOON_CHECK, s, a), *world('moon', MOON_CHECK, s, a, 'check', i)))
    out['moon_miss'] = moon

    if learner != 'baseline':
        out['laws'] = {}
        for p, law in mind.laws.items():
            wr, true_wind = law['wind_range'], B.wind_of(life, p)
            # A claim is true when its forces are the true ones and its wind range holds the true wind.
            claim = set(law['idea'][0]) == set(TRUTH[p][0]) and (
                'drag2' not in TRUTH[p][0] or (wr is not None and wr[0] <= true_wind <= wr[1]))
            out['laws'][p] = {'kept': describe(law['idea']), 'terms': list(law['idea'][0]), 'moving': law['idea'][1],
                              'right': law['idea'] == TRUTH[p], 'claim_true': claim, 'sure': law['sure'],
                              'own_throws': law['own_throws'], 'stuck': law['stuck'], 'wind': law['w'],
                              'wind_range': wr, 'lean': law['lean'], 'open': law['open'],
                              'numbers': {b: {'c': c, 'se': se} for b, (c, _, se) in law['numbers'].items()}}
        out['galileo'] = {k: v for k, v in mind.galileo.items() if k != 'pulls'}
        out['galileo']['pulls'] = list(mind.galileo['pulls'].values())
        words = {b: by_id[b]['word'] for b in life['named']}
        named, cut = mind.name(words)
        out['naming'] = {'right': sum(named[b] == by_id[b]['word'] for b in named),
                         'wrong': sum(named[b] not in (by_id[b]['word'], 'not sure') for b in named),
                         'not_sure': sum(named[b] == 'not sure' for b in named), 'of': len(named), 'cut': list(cut)}
        qs = [mind.balls[b['id']]['q'] for b in balls]
        out['push_numbers'] = qs
        out['q_vs_mass_rank'] = float(np.corrcoef(np.argsort(np.argsort(qs)),
                                                  np.argsort(np.argsort([b['mass'] for b in balls])))[0, 1])
        if mind.concept:
            c = mind.concept
            out['concept'] = {k: c[k] for k in ('kept', 'winner', 'R1_over_R0', 'R1_over_Rs', 'R2_over_R1', 'pairs')}
            out['concept']['exponents'] = {
                f'{p}/{t}': {'k': int(r[1]), 'strong': bool(abs(r[2][1]) >= 3 * r[3])}
                for (p, t), r in c['rules'].items() if r[0] == 'R1'}
        out['says'] = mind.sayings()
    out['log'] = log
    out['seconds'] = time.perf_counter() - started
    return plain(out)


def one(job):
    seed, learner, folder = job
    path = ROOT / folder / f'ball-seed{seed}-{learner}.json'
    try:
        result = live(seed, learner)
    except Exception:
        return path.name, 'FAILED ' + traceback.format_exc()
    path.write_text(json.dumps(result), encoding='utf-8')
    return path.name, f"{result['seconds']:.0f} s"


def mean_se(values, scale=1.0, digits=1):
    v = [x * scale for x in values if x is not None]
    if not v:
        return '-'
    se = statistics.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
    return f'{statistics.fmean(v):.{digits}f} ± {se:.{digits}f}'


def pct(flags):
    flags = [f for f in flags if f is not None]
    return f'{100 * sum(flags) / len(flags):.0f}% ({len(flags)})' if flags else '-'


def write_report(folder):
    out = ROOT / folder
    lives = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(out.glob('ball-seed*.json'))]
    by = {n: [x for x in lives if x['learner'] == n] for n in LEARNERS}
    by = {k: v for k, v in by.items() if v}
    seeds = sorted({x['seed'] for x in lives})
    lines = ['# The ball-throw world', '',
             f'Seeds {seeds}. Numbers are averages over lives ± one standard error. Misses are in centimetres: '
             'the typical distance between where it guessed the ball would be and where it was, over a 2-second throw.', '',
             '## Predicting throws', '',
             '| Robot | New throws of balls it has seen in that place | Balls in a place it never saw them in | Throw to a target, seen ball | Throw to a target, ball never thrown in air |',
             '|---|---|---|---|---|']
    for name, group in by.items():
        lines.append(f"| {name} | {mean_se([statistics.fmean(x['seen_miss']) for x in group], 100)} | "
                     f"{mean_se([statistics.fmean(n['miss'] for n in x['never_seen']) for x in group], 100)} | "
                     f"{mean_se([statistics.fmean([t['error'] for t in x['throw_back'] if not t['never_seen'] and t['error'] is not None] or [None]) if any(not t['never_seen'] and t['error'] is not None for t in x['throw_back']) else None for x in group], 100)} | "
                     f"{mean_se([statistics.fmean([t['error'] for t in x['throw_back'] if t['never_seen'] and t['error'] is not None]) if any(t['never_seen'] and t['error'] is not None for t in x['throw_back']) else None for x in group], 100)} |")
    lines += ['', 'Balls in a place it never saw them in, by place:', '',
              '| Robot | ' + ' | '.join(B.TRAINING) + ' |', '|---|' + '---|' * len(B.TRAINING)]
    for name, group in by.items():
        cells = [mean_se([statistics.fmean(n['miss'] for n in x['never_seen'] if n['place'] == p) for x in group], 100)
                 for p in B.TRAINING]
        lines.append(f'| {name} | ' + ' | '.join(cells) + ' |')

    lines += ['', '## The moon (never shown until the exam)', '',
              '| Robot | Surprise on the first moon throw (noise units; 1.8 is surprising) | Miss for a ball never thrown on the moon, after 1 moon throw | after 2 | after 4 |',
              '|---|---|---|---|---|']
    for name, group in by.items():
        lines.append(f"| {name} | {mean_se([x.get('moon_surprise') for x in group], 1, 1)} | "
                     + ' | '.join(mean_se([x['moon_miss'][i] for x in group], 100) for i in (0, 1, 3)) + ' |')

    loop = [x for x in lives if x['learner'] == 'concept']
    if loop:
        lines += ['', '## Laws of each place (the concept robot; the per-place robot finds the same)', '',
                  '| Place | Kept the true law | Sure | Sure, and the claim is true (its wind range included) | '
                  'Throws of its own | Width of the wind range it states (m/s) |', '|---|---|---|---|---|---|']
        for p in B.PLACES:
            laws = [x['laws'][p] for x in loop if p in x['laws']]
            widths = [l['wind_range'][1] - l['wind_range'][0] for l in laws if l.get('wind_range')]
            lines.append(f"| {p} | {pct([l['right'] for l in laws])} | {pct([l['sure'] for l in laws])} | "
                         f"{pct([l['claim_true'] for l in laws if l['sure']])} | {mean_se([l['own_throws'] for l in laws])} | "
                         f"{mean_se(widths, 1, 2)} |")
        both = [x for x in lives if x['learner'] in ('concept', 'per_place')]
        claims = [l for x in both for l in x['laws'].values() if l['sure']]
        unsure = [(x['seed'], p) for x in loop for p, l in x['laws'].items() if not l['sure']]
        lines += ['', f"Sure and wrong, both loop robots, every place: {sum(not l['claim_true'] for l in claims)} of "
                  f"{len(claims)} sure claims. Not sure (concept robot): {len(unsure)} of "
                  f"{sum(len(x['laws']) for x in loop)} place-lives"
                  + (f" ({', '.join(f'seed {s} {p}' for s, p in unsure)})" if unsure else '') + '.']
        g = [x['galileo'] for x in loop]
        lines += ['', '## Galileo in the vacuum room', '',
                  f"- It said every ball falls the same, heavy or light: {pct([x['same'] for x in g])}.",
                  f"- Evidence for one shared pull over a pull per ball: {mean_se([x['for_shared'] for x in g])} (−9 or less would mean mass matters).",
                  f"- Spread of the pull it measured across balls: {mean_se([x['spread'] for x in g], 1, 3)} m/s²; "
                  f"correlation of that pull with the push number: {mean_se([x['corr_with_q'] for x in g], 1, 2)}.",
                  f"- Throws per ball behind the comparison: at least {min(x['throws_per_ball'] for x in g)}; "
                  f"largest difference between the two models' numbers: {mean_se([x['models_differ_by'] for x in g], 1, 3)}."]
        c = [x['concept'] for x in loop]
        lines += ['', '## The concept: one hidden number per ball', '',
                  f"- It kept the concept in {pct([x['kept'] for x in c])} of lives. It predicted new (ball, place) pairs with: "
                  + ', '.join(f"{m} in {sum(x['winner'] == m for x in c)}" for m in ('R0', 'Rs', 'R1', 'R2')) + ' lives '
                  '(R0 no sharing, Rs size only, R1 one hidden number, R2 two).',
                  f"- Evidence (9 is decisive), predicting each ball in each place from all the others: "
                  f"over 'no sharing' {mean_se([x['R1_over_R0'] for x in c])}; over 'size only' {mean_se([x['R1_over_Rs'] for x in c])}; "
                  f"a second hidden number over the concept {mean_se([x['R2_over_R1'] for x in c])}.",
                  f"- The push number ranks the balls' true masses (rank correlation): {mean_se([x['q_vs_mass_rank'] for x in loop], 1, 2)}.",
                  '', '| Place / term | Where the number clearly depends on the ball | Power of size it chose there | True power |',
                  '|---|---|---|---|']
        keys = sorted({k for x in c for k in x['exponents']})
        for key in keys:
            rows = [x['exponents'][key] for x in c if key in x['exponents']]
            strong = [r for r in rows if r['strong']]
            ks = ', '.join(f"{k}: {sum(r['k'] == k for r in strong)}" for k in range(4) if any(r['k'] == k for r in strong))
            p, t = key.split('/')
            lines.append(f"| {key} | {len(strong)} of {len(rows)} lives | {ks or '-'} | {K_TRUTH.get((p, t), 'none (same for every ball)')} |")
        n = [x['naming'] for x in loop]
        lines += ['', '## Naming', '',
                  f"The caretaker said \"heavy\" or \"light\" for half the balls. For the other half, from their push "
                  f"numbers, it named {sum(x['right'] for x in n)} of {sum(x['of'] for x in n)} right and "
                  f"{sum(x['wrong'] for x in n)} wrong, and said \"not sure\" for {sum(x['not_sure'] for x in n)}: "
                  "those balls lay between the heaviest ball called light and the lightest ball called heavy.",
                  '', f"## What it says (concept robot, seed {loop[0]['seed']})", '']
        lines += [f'- {s}' for s in loop[0]['says']]
    (out / 'BALL.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out / 'BALL.md'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(1, 11)))
    parser.add_argument('--learners', nargs='+', default=list(LEARNERS))
    parser.add_argument('--workers', type=int, default=5)
    parser.add_argument('--results', default='ball-results')
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    if args.quick:
        args.seeds, args.results = [1], 'ball-smoke'
    (ROOT / args.results).mkdir(exist_ok=True)
    jobs = [(s, l, args.results) for s in args.seeds for l in args.learners
            if not (ROOT / args.results / f'ball-seed{s}-{l}.json').exists()]
    with Pool(min(args.workers, max(len(jobs), 1))) as pool:
        for name, status in pool.imap_unordered(one, jobs):
            print(f'{name}: {status}', flush=True)
    print(write_report(args.results))
