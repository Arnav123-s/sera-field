"""ccops5 lab | checks for the ball-throw world. Every check prints its numbers, not only PASS.

    python legacy/ball/ball_check.py --seed 1                             # the invariants, live on one dev seed: A, B, C, E
    python legacy/ball/ball_check.py                                      # full audit of the saved dev runs (ball-results)
    python legacy/ball/ball_check.py --results ball-fresh2 --read-only    # saved runs only: B, C, D, E, F, G

A  Kinematics: the true law, imagined with the robot's own code, predicts new throws within 2 mm in all
   five places (the position noise is 1 mm, so a perfect guess misses by about 1.4 mm); the robot's
   imagining and the world agree within 0.1 mm; halving the world's time step moves a throw by less than
   0.1 mm; and the world keeps its energy books: in the vacuum and on the moon a throw is the exact
   parabola, in air and water its energy only ever falls, and in the windy yard its energy, measured
   riding along with the air, only ever falls.
B  Law selection: in every place it keeps the true forces, no more and no fewer, is sure, puts every
   fitted number within 3 standard errors of the true number, and states a range of wind speeds that
   holds the true wind (0 where the air is still). Over saved runs: no spurious force or wind in any life.
C  Concept hierarchy: one hidden number per ball (R1) beats no sharing (R0) and size only (Rs) by at
   least 9, and a second hidden number (R2) does not beat it by 9. Where mass matters it picks the true
   power of size; where it does not, it sees no dependence on the ball; the push number puts every pair
   of balls in the order of their true masses, unless the rail cannot tell them apart (their masses
   differ by less than 3 times the noise blur of the comparison). No answer built in: the robot's code
   imports no physics numbers, never reads a ball's mass,
   true size or word, and is handed only id, seen size, look and rail speed. Controls (full audit): with
   other size powers it finds those powers; with forces that ignore mass it rejects the concept.
D  Held out: no (ball, place) kept back was ever thrown to a robot before it was predicted, and no moon
   throw came before training ended.
E  Humility: seed N's balls in the windy yard, with the wind set by hand from 0 to 1 m/s. It is never
   sure and wrong (a claim includes its stated wind range). With its own throws it finds every wind of
   0.5 m/s or more. With no throws of its own allowed, a faint wind (0.25 m/s, which its teacher throws
   lean towards but cannot settle) must leave it "not sure". It names no ball wrong. Over saved runs:
   no sure-and-wrong claim anywhere, and no ball named wrong.
F  Galileo is not empty: at least 2 vacuum throws per ball, and the two models differ. In a made-up world
   where heavier balls fall faster, it says mass matters.
G  The report is computed: BALL.md regenerated from the saved runs is byte-identical.
H  Determinism: seed 1 run again gives the same result as the saved run, for every learner.

Built as an isolated experiment. Not part of sera-field.
"""
import sys

sys.dont_write_bytecode = True

import argparse
import ast
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

import numpy as np

import ball_run
from ccops5 import ballworld as B
from ccops5.ballmind import OWN_THROWS, Mind, accel_fn, miss, rollout

ORIGINAL_ACCEL = B.get_accel
TRUE_TERMS = {'vacuum': {'down'}, 'moon': {'down'}, 'air': {'down', 'drag2'}, 'windy': {'down', 'drag2'},
              'water': {'down', 'drag2'}}
TRUE_K = {'air/drag2': 2, 'windy/drag2': 2, 'water/drag2': 2, 'water/down': 3}
MASS_FREE = ('vacuum/down', 'air/down', 'windy/down')
LOOP = ('concept', 'per_place')
SWEEP = (0.0, 0.1, -0.1, 0.25, -0.25, 0.5, -0.5, 1.0, -1.0)     # winds set by hand in the windy yard (m/s)
FIND = 0.5                   # with its own throws it must find winds at least this strong
FAINT = (0.25, -0.25)        # with no own throws these must leave it "not sure" (at least one of the two)
lines, failed = [], []


def say(text=''):
    print(text, flush=True)
    lines.append(text)


def verdict(name, ok, detail):
    say(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failed.append(name)


def guarded(name, fn, *args):
    """Run one check; a crash is a failure of that check, not of the whole script."""
    try:
        return fn(*args)
    except Exception as e:                                   # noqa: BLE001 - every crash is reported as FAIL
        verdict(name, False, f'crashed: {type(e).__name__}: {e}')
        return None


def truth(place, ball, life):
    """The true law of a place in the robot's own terms."""
    s, m = ball['size'], ball['mass']
    if place in ('vacuum', 'moon'):
        return (('down',), False), [B.GRAVITY if place == 'vacuum' else B.MOON_GRAVITY], 0.0
    down = B.GRAVITY - (B.WATER_BUOYANCY * s ** 3 / m if place == 'water' else 0.0)
    drag = (B.WATER_DRAG if place == 'water' else B.AIR_DRAG) * s ** 2 / m
    return (('down', 'drag2'), place == 'windy'), [down, drag], B.wind_of(life, place)


def true_number(place, term, ball):
    s, m = ball['size'], ball['mass']
    if term == 'down':
        if place in ('vacuum', 'moon'):
            return B.GRAVITY if place == 'vacuum' else B.MOON_GRAVITY
        return B.GRAVITY - (B.WATER_BUOYANCY * s ** 3 / m if place == 'water' else 0.0)
    if term == 'drag2':
        return (B.WATER_DRAG if place == 'water' else B.AIR_DRAG) * s ** 2 / m
    return 0.0                                              # no sideways push or linear drag in this world


def claim_true(place, terms, wind_range, true_wind):
    """A law claim is true when its forces are the true ones and, where there is air or water to move,
    its stated range of wind speeds holds the true wind."""
    if set(terms) != TRUE_TERMS[place]:
        return False
    if 'drag2' not in TRUE_TERMS[place]:
        return True
    return wind_range is not None and wind_range[0] <= true_wind <= wind_range[1]


class NoNoise:
    def normal(self, loc, scale, n):
        return np.zeros(n)


# ---------- A: kinematics ----------

def check_a(seeds):
    misses, gaps, steps, parabola, rise = [], [], [], 0.0, -np.inf
    t = np.arange(B.N_OBS) * B.DT_OBS
    for seed in seeds:
        life = B.make_life(seed)
        for ball in life['balls']:
            for place in B.PLACES:
                speed, angle = ball_run.teacher_throw(seed, place, ball['id'], 900)
                idea, c, w = truth(place, ball, life)
                guess = rollout(accel_fn(idea, c, w), speed, angle)
                seen = B.simulate(place, ball, speed, angle, w, B.throw_rng(seed, place, ball['id'], 'extra', 900))
                misses.append(miss(*guess, *seen))
                clean = B.simulate(place, ball, speed, angle, w, NoNoise())
                gaps.append(max(np.abs(guess[0] - clean[0]).max(), np.abs(guess[1] - clean[1]).max()))
                B.DT_SIM = 0.0025
                fine = B.simulate(place, ball, speed, angle, w, NoNoise())
                B.DT_SIM = 0.005
                steps.append(max(np.abs(fine[0] - clean[0]).max(), np.abs(fine[1] - clean[1]).max()))
                xs, ys = clean
                if place in ('vacuum', 'moon'):
                    g = B.GRAVITY if place == 'vacuum' else B.MOON_GRAVITY
                    parabola = max(parabola, float(np.abs(xs - speed * math.cos(angle) * t).max()),
                                   float(np.abs(ys - (speed * math.sin(angle) * t - 0.5 * g * t ** 2)).max()))
                else:
                    g = B.GRAVITY - (B.WATER_BUOYANCY * ball['size'] ** 3 / ball['mass'] if place == 'water' else 0.0)
                    vx = (xs[2:] - xs[:-2]) / (2 * B.DT_OBS)
                    vy = (ys[2:] - ys[:-2]) / (2 * B.DT_OBS)
                    energy = 0.5 * ((vx - w) ** 2 + vy ** 2) + g * ys[1:-1]
                    rise = max(rise, float(np.diff(energy).max()))
    mm = 1000 * np.array(misses)
    where = f"seed{'s' if len(seeds) > 1 else ''} {', '.join(map(str, seeds))}, every ball, every place"
    verdict('A oracle', mm.max() < 2 * B.SIGMA_POS * 1000,
            f'{len(mm)} throws ({where}): true law misses by {mm.mean():.2f} mm on average, '
            f'{mm.max():.2f} mm at most (limit 2 mm)')
    verdict('A integration', max(gaps) < B.SIGMA_POS / 10 and max(steps) < B.SIGMA_POS / 10,
            f'imagining vs world at most {1000 * max(gaps):.2e} mm; half time step moves a throw at most '
            f'{1000 * max(steps):.2e} mm (limit 0.1 mm)')
    verdict('A energy', parabola < 1e-9 and rise < 0.0,
            f'vacuum and moon: largest gap from the exact parabola {parabola:.1e} m (limit 1e-9); air, water '
            f'and windy (riding with the air): largest change of energy between readings {rise:+.2e} J/kg '
            f'(must be below 0: it only ever falls)')


# ---------- B: law selection ----------

def law_rows(run, life):
    """(place, exact, sure, claim true, worst |fit - true| / SE, words) for one loop robot's run."""
    by_id = {b['id']: b for b in life['balls']}
    rows = []
    for place in B.PLACES:
        law = run['laws'][place]
        terms, moving, wr = law['terms'], law['moving'], law['wind_range']
        true_wind = B.wind_of(life, place)
        exact = set(terms) == TRUE_TERMS[place] and moving == (place == 'windy')
        z = max((abs(c - true_number(place, t, by_id[int(b)])) / se
                 for b, nums in law['numbers'].items() for t, c, se in zip(terms, nums['c'], nums['se'])),
                default=float('inf'))
        wind = (f", wind {law['wind']:+.2f} in [{wr[0]:+.2f}, {wr[1]:+.2f}] (true {true_wind:+.2f})"
                if wr is not None else '')
        rows.append((place, exact, law['sure'], claim_true(place, terms, wr, true_wind), z,
                     f"{place}: {'+'.join(sorted(terms))}{' moving' if moving else ''}"
                     f"{'' if law['sure'] else ' NOT SURE'}{wind}, own throws {law['own_throws']}, "
                     f"worst fit {z:.2f} SE"))
    return rows


def check_b_live(seed, runs):
    life = B.make_life(seed)
    for learner in LOOP:
        rows = law_rows(runs[learner], life)
        ok = all(exact and sure and true and z <= 3.0 for _, exact, sure, true, z, _ in rows)
        verdict(f'B law selection ({learner})', ok,
                f'seed {seed}: ' + '; '.join(r[-1] for r in rows)
                + ' (each place: the true forces only, sure, numbers within 3 SE, wind range holds the truth)')


def check_b_saved(runs):
    spurious, exact, total, where = 0, 0, 0, []
    for name, r in runs.items():
        if r['learner'] not in LOOP:
            continue
        for place, law in r['laws'].items():
            total += 1
            bad = not set(law['terms']) <= TRUE_TERMS[place] or (law['moving'] and place != 'windy')
            spurious += bad
            if bad:
                where.append(f"seed {r['seed']} {r['learner']} {place}")
            exact += set(law['terms']) == TRUE_TERMS[place] and law['moving'] == (place == 'windy')
    verdict('B no spurious forces', spurious == 0 and total > 0,
            f'{total} place-lives of the loop robots: kept a force or wind that is not there {spurious} times'
            f"{' (' + ', '.join(where) + ')' if where else ''}; kept exactly the true law {exact} of {total}")


# ---------- C: concept hierarchy ----------

def concept_problems(r):
    c, problems = r['concept'], []
    if not (c['kept'] and c['winner'] == 'R1'):
        problems.append(f"kept {c['kept']}, predicted with {c['winner']}")
    if not (c['R1_over_R0'] >= 9 and c['R1_over_Rs'] >= 9 and c['R2_over_R1'] < 9):
        problems.append(f"evidence R1/R0 {c['R1_over_R0']:.1f}, R1/Rs {c['R1_over_Rs']:.1f}, R2/R1 {c['R2_over_R1']:.1f}")
    for key, k in TRUE_K.items():
        e = c['exponents'].get(key)
        if not (e and e['strong'] and e['k'] == k):
            problems.append(f'{key}: {e} (true power {k})')
    for key in MASS_FREE:
        e = c['exponents'].get(key)
        if e and e['strong']:
            problems.append(f'{key}: depends on the ball, but it does not')
    wrong, ties = order_of_masses(r)
    if wrong:
        problems.append('push number puts these balls in the wrong order although the rail can tell them apart: '
                        + ', '.join(wrong))
    return problems


def order_of_masses(r):
    """Pairs the robot's push numbers put in the wrong order: those the rail could tell apart (wrong), and
    near-ties it could not (their masses differ by less than 3 times the noise blur of the comparison).
    Changed after the dev audit, with the SERA author's approval: it first asked for a perfect ranking,
    which failed on seeds 2 and 4 where masses 0.002 and 0.008 apart swapped (the blur there is 0.02)."""
    masses = [b['mass'] for b in B.make_life(r['seed'])['balls']]
    qs, wrong, ties = r['push_numbers'], [], 0
    for i, mi in enumerate(masses):
        for j, mj in enumerate(masses):
            if mi < mj and qs[i] >= qs[j]:
                blur = math.hypot(mi ** 2, mj ** 2) * B.PUSH_NOISE / B.PUSH
                if mj - mi > 3 * blur:
                    wrong.append(f'balls {i} and {j} (masses {mi:.3f}, {mj:.3f})')
                else:
                    ties += 1
    return wrong, ties


def check_c_live(seed, run):
    c = run['concept']
    problems = concept_problems(run)
    verdict('C concept hierarchy', not problems,
            f"seed {seed}: evidence one number over no sharing {c['R1_over_R0']:.1f}, over size only "
            f"{c['R1_over_Rs']:.1f}, second number over one {c['R2_over_R1']:.1f} (9 is decisive); powers chosen "
            + ', '.join(f"{k} {v['k']}{'' if v['strong'] else ' (none)'}" for k, v in sorted(c['exponents'].items()))
            + f"; push number ranks mass {run['q_vs_mass_rank']:.2f} (near-ties the rail cannot tell apart, "
            f"swapped: {order_of_masses(run)[1]})"
            + (f"; PROBLEMS: {'; '.join(problems)}" if problems else ''))


def check_c_saved(runs):
    concept = [r for r in runs.values() if r['learner'] == 'concept']
    bad = {r['seed']: concept_problems(r) for r in concept}
    bad = {s: p for s, p in bad.items() if p}
    verdict('C concept in every life', concept and not bad,
            f"{len(concept)} lives: concept kept with R1 in {sum(r['concept']['kept'] and r['concept']['winner'] == 'R1' for r in concept)}; "
            f"a second hidden number won in {sum(r['concept']['winner'] == 'R2' for r in concept)}; "
            f"near-ties the rail cannot tell apart, swapped: {sum(order_of_masses(r)[1] for r in concept)}; "
            f"lives with any problem {len(bad)}" + (f': {bad}' if bad else ''))


def check_c_source():
    tree = ast.parse((REPO / 'ccops5' / 'ballmind.py').read_text(encoding='utf-8'))
    allowed = {'DT_OBS', 'DT_SIM', 'N_BALLS', 'N_OBS', 'PLACES', 'PUSH', 'SIGMA_POS', 'TRAINING'}
    imported, keys = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and 'ballworld' in node.module:
            imported |= {a.name for a in node.names}
        if isinstance(node, ast.Import) and any('ballworld' in a.name for a in node.names):
            imported.add('*module*')
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                and node.slice.value in ('mass', 'size', 'word'):
            keys.add(node.slice.value)
    verdict('C source', imported <= allowed and not keys,
            f"ballmind.py imports from the world only {sorted(imported)}; reads keys {sorted(keys) or 'none'} "
            "of 'mass', 'size', 'word'")


class Watch:
    """Wraps a learner class to record what it is given about the balls."""
    given = set()

    @staticmethod
    def wrap(cls):
        class Watched(cls):
            def __init__(self, *args):
                balls = args[-1] if cls.__name__ == 'Net' else args[1]
                for b in balls:
                    Watch.given |= set(b)
                super().__init__(*args)
        return Watched


def watched_lives(seed, learners):
    Watch.given = set()
    mind, net = ball_run.Mind, ball_run.Net
    ball_run.Mind, ball_run.Net = Watch.wrap(mind), Watch.wrap(net)
    try:
        return {learner: json.loads(json.dumps(ball_run.live(seed, learner))) for learner in learners}
    finally:
        ball_run.Mind, ball_run.Net = mind, net


def check_c_given():
    verdict('C what learners are given', Watch.given == {'id', 'seen_size', 'look', 'rail_speed'},
            f'keys handed to the learners: {sorted(Watch.given)}')


def cf_world(size_powers=None, mass_free=False, heavy_falls_faster=False):
    """A made-up world, for controls only."""
    def accel(place, ball, vx, vy, wind_vx):
        s, m = ball['size'], (1.75 if mass_free else ball['mass'])
        if place == 'vacuum' and heavy_falls_faster:
            return 0.0, -B.GRAVITY * (1 + 0.02 * (ball['mass'] - 1.75))
        if place in ('vacuum', 'moon'):
            return ORIGINAL_ACCEL(place, ball, vx, vy, wind_vx)
        p = size_powers or {'drag': 2, 'lift': 3, 'water_drag': 2}
        ay = -B.GRAVITY
        if place == 'water':
            ay += B.WATER_BUOYANCY * s ** p['lift'] / m
        rx, ry = vx - (wind_vx if place == 'windy' else 0.0), vy
        power = p['water_drag'] if place == 'water' else p['drag']
        k = (B.WATER_DRAG if place == 'water' else B.AIR_DRAG) * s ** power * math.hypot(rx, ry) / m
        return -k * rx, ay - k * ry
    return accel


def run_in(world, seed, learner):
    B.get_accel = world
    try:
        return ball_run.live(seed, learner)
    finally:
        B.get_accel = ORIGINAL_ACCEL


def check_c_worlds():
    powers = {'drag': 1, 'lift': 2, 'water_drag': 3}
    out = run_in(cf_world(size_powers=powers), 1, 'concept')
    want = {'air/drag2': 1, 'windy/drag2': 1, 'water/down': 2, 'water/drag2': 3}
    got = {k: v['k'] for k, v in out['concept']['exponents'].items() if v['strong']}
    verdict('C other size powers', got == want and out['concept']['kept'],
            f'world with drag ∝ size¹, lift ∝ size², water drag ∝ size³ (seed 1): chose {got}; '
            f"concept kept {out['concept']['kept']}")
    out = run_in(cf_world(mass_free=True), 1, 'concept')
    c = out['concept']
    verdict('C forces ignore mass', not c['kept'] and c['winner'] == 'Rs',
            f"world where no force depends on mass (seed 1): concept kept {c['kept']}, predicted with "
            f"{c['winner']}; one-number-over-size-only evidence {c['R1_over_Rs']:.1f} (9 is decisive)")


# ---------- D: held out ----------

def check_d(runs):
    trained, moon_early = 0, 0
    for r in runs.values():
        held = {(int(b), p) for b, p in r['held_out'].items()}
        first_predict = {}
        for i, e in enumerate(r['log']):
            key = (e['ball'], e['place'])
            if e['tag'] == 'predict':
                first_predict.setdefault(key, i)
            if key in held and e['tag'] in ('teacher', 'own', 'extra'):
                trained += 1
        last_train = max(i for i, e in enumerate(r['log']) if e['tag'] in ('teacher', 'own', 'extra'))
        moon = [i for i, e in enumerate(r['log']) if e['place'] == 'moon']
        moon_early += bool(moon and min(moon) < last_train)
        missing = held - set(first_predict)
        trained += len(missing)
    verdict('D held out', trained == 0 and moon_early == 0,
            f'{len(runs)} runs: kept-back pairs shown to a robot {trained} times; runs with a moon throw '
            f'before training ended: {moon_early}')


# ---------- E: humility ----------

def windy_life(seed, wind, budget):
    """Seed's balls in the windy yard with the wind set by hand: teacher throws, then its own (at most budget)."""
    life = B.make_life(seed)
    by_id = {b['id']: b for b in life['balls']}
    public = [{k: b[k] for k in ('id', 'seen_size', 'look', 'rail_speed')} for b in life['balls']]
    mind = Mind('concept', public, seed)
    seen = [b['id'] for b in life['balls'] if life['held_out'][b['id']] != 'windy']

    def world(ball, speed, angle, tag, k):
        return B.simulate('windy', by_id[ball], speed, angle, wind, B.throw_rng(seed, 'windy', ball, tag, k))
    for ball in seen:
        for k in range(2):
            mind.see('windy', ball, *world(ball, *ball_run.teacher_throw(seed, 'windy', ball, k), 'teacher', k))
    mind.learn_place('windy', throw=lambda ball, s, a, k: world(ball, s, a, 'own', k), allowed=seen, budget=budget)
    return mind.laws['windy']


def describe_claim(wind, law):
    (terms, moving), wr = law['idea'], law['wind_range']
    rng = f'[{wr[0]:+.2f}, {wr[1]:+.2f}]' if wr is not None else 'no range'
    return (f"{wind:+.2f}: {'moving' if moving else 'still'} {rng} "
            f"{'sure' if law['sure'] else 'not sure'}, {law['own_throws']} own")


def check_e_live(seed, concept_run):
    sweep = {w: windy_life(seed, w, OWN_THROWS) for w in SWEEP}
    wrong = [w for w, law in sweep.items() if law['sure'] and not claim_true('windy', law['idea'][0], law['wind_range'], w)]
    verdict('E never sure and wrong', not wrong,
            f"seed {seed}'s balls, windy yard, wind set by hand, up to {OWN_THROWS} own throws: "
            + '; '.join(describe_claim(w, law) for w, law in sweep.items())
            + f' | sure and wrong at {wrong or "none"}')
    missed = [w for w, law in sweep.items() if abs(w) >= FIND
              and not (law['idea'][1] and claim_true('windy', law['idea'][0], law['wind_range'], w))]
    verdict('E finds the wind', not missed,
            f'every wind of {FIND} m/s or more found (moving air, range holds the true wind): '
            f"{'all found' if not missed else 'missed ' + str(missed)}")
    faint = {w: windy_life(seed, w, 0) for w in FAINT}
    wrong = [w for w, law in faint.items() if law['sure'] and not claim_true('windy', law['idea'][0], law['wind_range'], w)]
    unsure = [w for w, law in faint.items() if not law['sure']]
    verdict('E not sure when it cannot throw', not wrong and len(unsure) >= 1,
            'no own throws allowed, faint winds: ' + '; '.join(describe_claim(w, law) for w, law in faint.items())
            + f' | not sure at {unsure or "none"}, sure and wrong at {wrong or "none"}')
    n = concept_run['naming']
    verdict('E naming', n['wrong'] == 0 and n['right'] + n['not_sure'] == n['of'],
            f"seed {seed}: of {n['of']} balls it was not told about, named {n['right']} right, {n['wrong']} wrong, "
            f"{n['not_sure']} not sure")


def check_e_saved(runs):
    sure_wrong, sure, names_wrong, where = 0, 0, 0, []
    for r in runs.values():
        if r['learner'] not in LOOP:
            continue
        life = B.make_life(r['seed'])
        for place, law in r['laws'].items():
            if law['sure']:
                sure += 1
                if not claim_true(place, law['terms'], law['wind_range'], B.wind_of(life, place)):
                    sure_wrong += 1
                    where.append(f"seed {r['seed']} {r['learner']} {place}")
        names_wrong += r['naming']['wrong']
    verdict('E never sure and wrong', sure_wrong == 0 and names_wrong == 0 and sure > 0,
            f"{sure} sure law claims by the loop robots: {sure_wrong} wrong{' (' + ', '.join(where) + ')' if where else ''}; "
            f'balls named wrong: {names_wrong}')


# ---------- F: Galileo ----------

def check_f_control():
    g = run_in(cf_world(heavy_falls_faster=True), 1, 'concept')['galileo']
    verdict('F control', not g['same'],
            f"world where the pull grows 2% per unit of mass (seed 1): said same {g['same']}, evidence for "
            f"one shared pull {g['for_shared']:.1f} (−9 or less means mass matters), correlation of pull "
            f"with push number {g['corr_with_q']:.2f}")


def check_f(runs):
    g = [r['galileo'] for r in runs.values() if r.get('galileo')]
    verdict('F Galileo not empty', all(x['throws_per_ball'] >= 2 and x['models_differ_by'] > 1e-3 for x in g),
            f"{len(g)} runs: fewest vacuum throws per ball {min(x['throws_per_ball'] for x in g)}; smallest "
            f"difference between the two models' pulls {min(x['models_differ_by'] for x in g):.4f} m/s²; "
            f"said same in {sum(x['same'] for x in g)} of {len(g)}")


# ---------- G: computed report ----------

def check_g(folder):
    path = folder / 'BALL.md'
    before = path.read_bytes() if path.exists() else b''
    ball_run.write_report(folder.name)
    verdict('G computed report', before == path.read_bytes() and before != b'',
            f'{path.name} regenerated from {len(list(folder.glob("ball-seed*.json")))} saved runs: '
            f"{'byte-identical' if before == path.read_bytes() else 'CHANGED'}")


# ---------- H: determinism ----------

def check_h(runs):
    seed = min(r['seed'] for r in runs.values())
    again = watched_lives(seed, [l for l in ball_run.LEARNERS if f'ball-seed{seed}-{l}.json' in runs])
    same = []
    for learner, out in again.items():
        saved = dict(runs[f'ball-seed{seed}-{learner}.json'])
        out = dict(out)
        out.pop('seconds'), saved.pop('seconds')
        same.append((learner, json.dumps(out, sort_keys=True) == json.dumps(saved, sort_keys=True)))
    verdict('H determinism', same and all(s for _, s in same),
            f'seed {seed} again vs saved: ' + ', '.join(f"{l} {'same' if s else 'DIFFERENT'}" for l, s in same))


def load(folder):
    return {p.name: json.loads(p.read_text(encoding='utf-8')) for p in sorted(folder.glob('ball-seed*.json'))}


if __name__ == '__main__':
    import torch
    torch.set_num_threads(1)
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, help='check the invariants live on this seed (A, B, C, E)')
    parser.add_argument('--results', default='ball-results')
    parser.add_argument('--read-only', action='store_true')
    args = parser.parse_args()
    if args.seed is not None:
        out_file = ROOT / 'ball-results' / f'ball_check_seed{args.seed}.md'
        say(f'# Ball world invariants, live on seed {args.seed}')
        say()
        guarded('A kinematics', check_a, (args.seed,))
        lives = guarded('B/C/E lives', watched_lives, args.seed, LOOP)
        if lives:
            guarded('B law selection', check_b_live, args.seed, lives)
            guarded('C concept hierarchy', check_c_live, args.seed, lives['concept'])
            guarded('C source', check_c_source)
            guarded('C what learners are given', check_c_given)
            guarded('E humility', check_e_live, args.seed, lives['concept'])
    else:
        folder = ROOT / args.results
        out_file = folder / 'ball_check.md'
        runs = load(folder)
        say(f'# Ball world checks ({args.results})')
        say()
        if not args.read_only:
            guarded('A kinematics', check_a, (1, 2, 3))
            guarded('C source', check_c_source)
            guarded('H determinism', check_h, runs)
            guarded('C what learners are given', check_c_given)
            guarded('C controls', check_c_worlds)
            guarded('F control', check_f_control)
        guarded('B no spurious forces', check_b_saved, runs)
        guarded('C concept in every life', check_c_saved, runs)
        guarded('D held out', check_d, runs)
        guarded('E never sure and wrong', check_e_saved, runs)
        guarded('F Galileo not empty', check_f, runs)
        guarded('G computed report', check_g, folder)
    say()
    say('ALL PASS' if not failed else f"FAILED: {', '.join(failed)}")
    out_file.parent.mkdir(exist_ok=True)
    out_file.write_text('\n'.join(f'- {l}' if l[:4] in ('PASS', 'FAIL') else l for l in lines) + '\n', encoding='utf-8')
    sys.exit(1 if failed else 0)
