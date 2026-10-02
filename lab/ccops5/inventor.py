"""ccops5 lab | invention school: making up ideas that are not on the menu.

Built as an isolated experiment. Not part of sera-field.
(Built in a separate development session.)
"""
import collections
import statistics
import time
import numpy as np
import torch

from . import puzzles as P
from . import school as S
from . import world as W
from .mind import DT_MODEL, SIGMA_A, SURPRISE, miss, samples_from

LEARNERS = ('inventor', 'menu', 'inventor_untaught')

INPUTS = ('position', 'speed')
SHAPES = tuple(list(P.SHAPES) + ['size'])
STEADY_IDEA = ('nothing', 'steady')
THINGS = tuple((i, s) for i in INPUTS for s in SHAPES)
OLD_IDEAS = P.IDEAS
NEW_PIECES = (('position', 'size'), ('speed', 'size'))
ALL_PIECES = OLD_IDEAS + NEW_PIECES
COMBO_IDEAS = tuple((a, b) for a in ALL_PIECES if a[0] == 'position' for b in ALL_PIECES if b[0] == 'speed')
IDEAS = OLD_IDEAS + COMBO_IDEAS

CLIP_HITS = 0

def _scalar(shape, s):
    if shape == 'straight': return s
    if shape == 'growing': return s * np.abs(s)
    if shape == 'steps': return np.tanh(s / 0.05)
    if shape == 'cubic': return s ** 3
    if shape == 'wave': return np.sin(s)
    if shape == 'size': return np.abs(s)
    raise ValueError(shape)

def idea_value(idea, x, v):
    out = np.ones_like(np.asarray(x, dtype=float))
    parts = idea if isinstance(idea[0], tuple) else (idea,)
    for source, shape in parts:
        if source == 'nothing': continue
        out = out * _scalar(shape, x if source == 'position' else v)
    return out

FORCES = dict(P.FORCES)
PRODUCT_FORCES = {
    'growing drag': ((('position', 'size'), ('speed', 'straight')), (2.0, 5.0)),
    'weakening spring': ((('position', 'straight'), ('speed', 'size')), (3.0, 9.0)),
    'rubbing valley': ((('position', 'steps'), ('speed', 'size')), (1.0, 4.0)),
    'wave drag': ((('position', 'size'), ('speed', 'wave')), (5.0, 15.0)),
    'cubic drag': ((('position', 'size'), ('speed', 'cubic')), (2.0, 6.0)),
}
FORCES.update(PRODUCT_FORCES)
PRACTICE = ('rubbing', 'water drag', 'dry friction', 'spring', 'tight spring', 'stiff spring', 'swing', 'slope', 'growing drag', 'weakening spring', 'rubbing valley')
NEVER_SHOWN = ('thick oil', 'valley', 'wave drag', 'cubic drag')
import os
PRACTICE_WORLDS = 12 if os.environ.get('CCOPS5_QUICK') else 44
SITUATIONS = 10
TRICKS = 0.05

def simulate(world, m, u, rng, trick=None):
    global CLIP_HITS
    idea = FORCES[world['force']][0]
    strength, sign = world['strength'], world['sign']
    def accel(x, v, f):
        global CLIP_HITS
        raw = (f - sign * strength * float(idea_value(idea, x, v))) / m
        if raw < -100 or raw > 100: CLIP_HITS += 1
        return float(np.clip(raw, -100, 100))
    x = v = 0.0
    xs, vs = [x], [v]
    per, step = int(round(W.DT_OBS / W.DT_SIM)), 0
    for _ in range(W.N_OBS - 1):
        for _ in range(per):
            t = step * W.DT_SIM
            f = W.hand_force(u) if t < W.T_PUSH - 1e-9 else 0.0
            if trick and trick[0] - 1e-9 <= t < trick[1] - 1e-9:
                f += trick[2]
            h = W.DT_SIM
            k1x, k1v = v, accel(x, v, f)
            k2x, k2v = v + .5 * h * k1v, accel(x + .5 * h * k1x, v + .5 * h * k1v, f)
            k3x, k3v = v + .5 * h * k2v, accel(x + .5 * h * k2x, v + .5 * h * k2v, f)
            k4x, k4v = v + h * k3v, accel(x + h * k3x, v + h * k3v, f)
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            step += 1
        xs.append(x)
        vs.append(v)
    return (np.array(xs) + rng.normal(0, W.SIGMA_X, W.N_OBS),
            np.array(vs) + rng.normal(0, W.SIGMA_V, W.N_OBS))

def school_plan(seed):
    rng = np.random.default_rng([seed, 2026])
    practice = [PRACTICE[i % len(PRACTICE)] for i in range(PRACTICE_WORLDS)]
    rng.shuffle(practice)
    exam = list(PRACTICE) + list(NEVER_SHOWN) * 2
    rng.shuffle(exam)
    worlds = []
    for part, forces in (('practice', practice), ('exam', exam)):
        for force in forces:
            lo, hi = FORCES[force][1]
            world = {'part': part, 'force': force, 'strength': float(rng.uniform(lo, hi)),
                     'sign': float(rng.choice([-1.0, 1.0])) if force == 'slope' else 1.0,
                     'masses': [float(m) for m in rng.uniform(0.6, 2.5, size=3)], 'situations': []}
            for _ in range(SITUATIONS):
                trick = None
                if rng.random() < TRICKS:
                    start = float(rng.choice([0.6, 0.8, 1.0, 1.2]))
                    trick = (start, start + 0.2, float(rng.choice([-1.5, 1.5])))
                world['situations'].append({
                    'm': float(rng.choice(world['masses'])), 'trick': trick,
                    'pushes': (float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0]))),
                    'check_u': float(rng.choice(W.CHECK_COMMANDS))})
            worlds.append(world)
    return worlds

def columns(ideas, z):
    return np.column_stack([np.tanh(1.6 * z[:, 2])] + [idea_value(i, z[:, 0], z[:, 1]) for i in ideas])

def fit(ideas, z, a):
    x = columns(ideas, z)
    precision = x.T @ x / SIGMA_A ** 2 + np.eye(x.shape[1]) / S.PRIOR_VAR
    theta = np.linalg.solve(precision, x.T @ a / SIGMA_A ** 2)
    left = a - x @ theta
    return theta, left, float(np.sqrt(np.mean(left ** 2)) / SIGMA_A)

def predict(ideas, theta, u):
    def acc(x, v, c):
        return float(np.clip(columns(ideas, np.array([[x, v, c]]))[0] @ theta, -50, 50))
    x = v = 0.0
    out, h, step = [x], DT_MODEL, 0
    for _ in range(W.N_OBS - 1):
        for _ in range(int(round(W.DT_OBS / DT_MODEL))):
            c = u if step * h < W.T_PUSH - 1e-9 else 0.0
            k1x, k1v = v, acc(x, v, c)
            k2x, k2v = v + .5 * h * k1v, acc(x + .5 * h * k1x, v + .5 * h * k1v, c)
            k3x, k3v = v + .5 * h * k2v, acc(x + .5 * h * k2x, v + .5 * h * k2v, c)
            k4x, k4v = v + h * k3v, acc(x + h * k3x, v + h * k3v, c)
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            step += 1
        out.append(x)
    return np.array(out)

BANDS = 3
N_SHAPES = len(SHAPES)
REL = 0
TPL = 2
LEAN = TPL + N_SHAPES * BANDS
STEADY = LEAN + N_SHAPES
STEADY_LEAN = STEADY + 3
GRID_P = STEADY_LEAN + 1
GRID_V = GRID_P + N_SHAPES * BANDS * BANDS
COMBO_LEAN = GRID_V + N_SHAPES * BANDS * BANDS
N_PARAMS = COMBO_LEAN + 1

def picture(z, leftover):
    q = leftover / (np.sqrt(np.mean(leftover ** 2)) + 1e-12)
    along = {}
    for name, col in (('position', 0), ('speed', 1)):
        s = z[:, col]
        bands = np.array_split(np.argsort(s, kind='stable'), BANDS)
        means = np.array([q[b].mean() for b in bands])
        c = float(np.corrcoef(s, q)[0, 1]) if np.std(s) > 1e-9 else 0.0
        c = c if np.isfinite(c) else 0.0
        along[name] = (means * (1.0 if c >= 0 else -1.0), float(np.std(means)), abs(c))

    order_x = np.argsort(z[:, 0], kind='stable')
    order_v = np.argsort(z[:, 1], kind='stable')
    ranks_x = np.empty(len(z), int); ranks_x[order_x] = np.arange(len(z))
    ranks_v = np.empty(len(z), int); ranks_v[order_v] = np.arange(len(z))
    bx = ranks_x * BANDS // len(z)
    bv = ranks_v * BANDS // len(z)
    grid = np.zeros(BANDS * BANDS)
    for i in range(BANDS):
        for j in range(BANDS):
            mask = (bx == i) & (bv == j)
            grid[i * BANDS + j] = q[mask].mean() if mask.any() else 0.0
    return along, grid, float(abs(q.mean()))

def looks(along, offset):
    v = np.concatenate([along['position'][0], along['speed'][0], [offset]])
    return v / (np.linalg.norm(v) + 1e-12)

def feelings(along, grid, offset, all_ideas):
    F = np.zeros((len(all_ideas), N_PARAMS))
    for j, idea in enumerate(all_ideas):
        if idea == STEADY_IDEA:
            F[j, STEADY:STEADY + 3] = (offset, max(a[1] for a in along.values()), max(a[2] for a in along.values()))
            F[j, STEADY_LEAN] = 1.0
        elif isinstance(idea[0], str):
            source, shape = idea
            bands, spread, corr = along[source]
            h = SHAPES.index(shape)
            F[j, REL:REL + 2] = (spread, corr)
            F[j, TPL + h * BANDS:TPL + (h + 1) * BANDS] = bands
            F[j, LEAN + h] = 1.0
        else:
            h_p = SHAPES.index(idea[0][1])
            h_v = SHAPES.index(idea[1][1])
            F[j, REL:REL + 2] = (along['position'][1] + along['speed'][1], along['position'][2] + along['speed'][2])
            F[j, TPL + h_p * BANDS:TPL + (h_p + 1) * BANDS] = along['position'][0]
            F[j, TPL + h_v * BANDS:TPL + (h_v + 1) * BANDS] = along['speed'][0]
            F[j, LEAN + h_p] = 1.0
            F[j, LEAN + h_v] = 1.0
            st_p = GRID_P + h_p * BANDS * BANDS
            F[j, st_p:st_p + BANDS * BANDS] = grid
            st_v = GRID_V + h_v * BANDS * BANDS
            F[j, st_v:st_v + BANDS * BANDS] = grid
            F[j, COMBO_LEAN] = 1.0
    return F

def explain(idea):
    if idea == STEADY_IDEA: return 'a steady push'
    if isinstance(idea[0], str): return f"{idea[1]} with {idea[0]}"
    return f"{idea[1][1]} with {idea[1][0]} and {idea[0][1]} with {idea[0][0]}"

def partly(idea, truth):
    if idea == truth: return False
    i_parts = idea if isinstance(idea[0], tuple) else (idea,)
    t_parts = truth if isinstance(truth[0], tuple) else (truth,)
    return any(ip == tp for ip in i_parts for tp in t_parts)

def name(idea):
    return f'"{explain(idea)}"'

SENTENCE_POS = {
    'straight': 'the farther it is from the middle',
    'growing': 'much more the farther it goes',
    'steps': 'equally anywhere it is',
    'cubic': 'very sharply when far away',
    'wave': 'wavy with distance',
    'size': 'depending on distance',
}
SENTENCE_SPEED = {
    'straight': 'it slows down',
    'growing': 'it slows down more and more as it goes faster',
    'steps': 'it is slowed by the same amount whenever it moves',
    'cubic': 'it is slowed very sharply when fast',
    'wave': 'it is slowed wavy with speed',
    'size': 'it feels a push sized by its speed',
}

def say(idea, sure, beaten, rivals, stuck, tested, wide=()):
    if idea == STEADY_IDEA:
        words = 'A steady push always leans it one way, like a slope.'
    elif isinstance(idea[0], str):
        source, shape = idea
        if source == 'position':
            words = f"It is pulled back toward the middle {SENTENCE_POS[shape]}."
        else:
            words = f"{SENTENCE_SPEED[shape].capitalize()}."
    else:
        p_shape = idea[0][1]
        v_shape = idea[1][1]
        words = f"{SENTENCE_SPEED[v_shape].capitalize()} {SENTENCE_POS[p_shape]}."

    close = [r for r in beaten if r not in wide][:4]
    rest = ', and every other idea I can form fits worse' if any(r in wide for r in beaten) else ''
    if sure and close:
        return words + f" I am sure: I tested it against {', '.join(name(r) for r in close)} and it won{rest}."
    if sure:
        return words + ' I am sure: nothing else I can form fits what I saw.'
    if not rivals:
        return words + ' I am not sure yet: part of what I saw is still unexplained.'
    why = ('and none of my pushes could tell them apart' if any(stuck[r] for r in rivals)
           else 'and I ran out of chances to tell them apart' if tested
           else 'and I did not find a way to tell them apart')
    more = f' (and {len(rivals) - 2} more)' if len(rivals) > 2 else ''
    return words + f" I am not sure: {', '.join(name(r) for r in rivals[:2])}{more} explains what I saw as well, {why}."

SYMBOL = {
    ('position', 'straight'): 'x', ('position', 'growing'): 'x|x|',
    ('position', 'steps'): 'tanh(x/0.05)', ('position', 'cubic'): 'x³', ('position', 'wave'): 'sin(x)',
    ('position', 'size'): '|x|',
    ('speed', 'straight'): 'v', ('speed', 'growing'): 'v|v|',
    ('speed', 'steps'): 'tanh(v/0.05)', ('speed', 'cubic'): 'v³', ('speed', 'wave'): 'sin(v)',
    ('speed', 'size'): '|v|',
    ('nothing', 'steady'): '1'
}

def formula(ideas, theta):
    terms = [f'{theta[0]:.2f}·tanh(1.6u)']
    for idea, c in zip(ideas, theta[1:]):
        if idea == STEADY_IDEA:
            sym = '1'
        elif isinstance(idea[0], str):
            sym = SYMBOL[idea]
        else:
            sym = SYMBOL[idea[1]] + '·' + SYMBOL[idea[0]]
        terms.append(f"{'−' if c < 0 else '+'} {abs(c):.2f}·{sym}")
    return 'a = ' + ' '.join(terms)

def evidence(base, leader, rival, z, a):
    _, left_l, _ = fit(base + [leader], z, a)
    _, left_r, _ = fit(base + [rival], z, a)
    return float(left_r @ left_r - left_l @ left_l) / SIGMA_A ** 2

def imagine(ideas, theta, u):
    def acc(x, v, c):
        return float(np.clip(columns(ideas, np.array([[x, v, c]]))[0] @ theta, -50, 50))
    x = v = 0.0
    xs, vs, h, step = [x], [v], DT_MODEL, 0
    for _ in range(W.N_OBS - 1):
        for _ in range(int(round(W.DT_OBS / DT_MODEL))):
            c = u if step * h < W.T_PUSH - 1e-9 else 0.0
            k1x, k1v = v, acc(x, v, c)
            k2x, k2v = v + .5 * h * k1v, acc(x + .5 * h * k1x, v + .5 * h * k1v, c)
            k3x, k3v = v + .5 * h * k2v, acc(x + .5 * h * k2x, v + .5 * h * k2v, c)
            k4x, k4v = v + h * k3v, acc(x + h * k3x, v + h * k3v, c)
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            step += 1
        xs.append(x)
        vs.append(v)
    return np.array(xs), np.array(vs)

def best_test(base, leader, rival, z, a):
    now = evidence(base, leader, rival, z, a)
    theta, _, _ = fit(base + [leader], z, a)
    best_u, best_gain = None, -np.inf
    for u in W.COMMANDS:
        zu = samples_from(*imagine(base + [leader], theta, u), u)[0].numpy()
        au = columns(base + [leader], zu) @ theta
        gain = evidence(base, leader, rival, np.vstack([z, zu]), np.concatenate([a, au])) - now
        if gain > best_gain:
            best_u, best_gain = u, gain
    return best_u, best_gain

class Hunch:
    def __init__(self):
        self.theta = np.zeros(N_PARAMS)
    def odds(self, F, allowed):
        z = np.where(allowed, F @ self.theta, -np.inf)
        p = np.exp(z - z[allowed].max())
        return p / p.sum()
    def nudge(self, F, p, j, amount):
        self.theta += amount * (F[j] - p @ F)

class Student:
    def __init__(self, learner, seed):
        self.learner = learner
        self.hunch = Hunch()
        self.rng = np.random.default_rng([seed, 31])
        self.expected_credit = 0.0
        self.tried_ever = set()
        self.tried_count = collections.Counter()
        self.met = []
        self.allowed_ideas = OLD_IDEAS if learner == 'menu' else IDEAS

    def stage(self, index, world):
        if world['part'] == 'exam': return 'alone', 0.0
        if index < S.WATCH_WORLDS: return 'watch', 0.0
        if index < S.WATCH_WORLDS + S.HINT_WORLDS:
            return 'hints', 0.8 - 0.7 * (index - S.WATCH_WORLDS) / max(S.HINT_WORLDS - 1, 1)
        return 'alone', 0.0

    def doubt(self, leader, base, d, seen, world, sit, rng):
        open_ = [r for r in d['rivals'] if abs(d['rivals'][r]) < 9.0]
        if not open_: return 0
        def weigh():
            return {r: d['rivals'][r] + float(np.clip(evidence(base, leader, r, seen['z'], seen['a']), -6.0, 6.0)) for r in open_}
        now, stuck_here, pushes = weigh(), set(), 0
        while seen['budget'] > 0:
            waiting = [r for r in open_ if abs(now[r]) < 9.0 and r not in stuck_here]
            if not waiting: break
            target = min(waiting, key=now.get)
            u, gain = best_test(base, leader, target, seen['z'], seen['a'])
            if gain < 1.0:
                stuck_here.add(target)
                continue
            z, a = samples_from(*simulate(world, sit['m'], u, rng, sit['trick']), u)
            seen['z'] = np.vstack([seen['z'], z.numpy()])
            seen['a'] = np.concatenate([seen['a'], a.numpy()])
            seen['budget'] -= 1
            pushes += 1
            now = weigh()
        for r in stuck_here: d['stuck'][r] += 1
        for r in open_:
            _, _, s_l = fit(base + [leader], seen['z'], seen['a'])
            _, _, s_r = fit(base + [r], seen['z'], seen['a'])
            if min(s_l, s_r) < SURPRISE:
                d['rivals'][r] = now[r]
        return pushes

    def learn(self, entry, credit):
        if self.learner != 'inventor_untaught':
            self.hunch.nudge(entry['F'], entry['p'], entry['j'], S.RATE * (credit - self.expected_credit))
            self.expected_credit += 0.05 * (credit - self.expected_credit)

    def live_world(self, world, index, seed):
        truth = FORCES[world['force']][0]
        stage, hint_chance = self.stage(index, world)
        kept, tries, misses = [], [], []
        ruled_out, entry_of, doubts = {}, {}, {}
        held = None
        shown, found_at, right_at, imagined, hints = False, None, None, 0, 0
        first_look, unfamiliar, changed_mind, tests, beaten_total = None, 0, 0, 0, 0
        seen, history = None, []

        def base_for(leader):
            if held is not None and held['idea'] == leader:
                return [i for i in kept if i != held['replaces']]
            return [i for i in kept if i != leader]

        def widen(leader, past, extra=()):
            # Every learner is relentless; 'menu' only within the old ideas.
            d = doubts[leader]
            d.setdefault('wide', set())
            base = base_for(leader)
            fits = [fit(base + [leader], h['z'], h['a'])[2] for h in past]

            rival_set = set(OLD_IDEAS)
            if isinstance(leader[0], tuple):
                p, v = leader
                for new_p in [i for i in OLD_IDEAS if i[0] == 'position']:
                    rival_set.add((new_p, v))
                for new_v in [i for i in OLD_IDEAS if i[0] == 'speed']:
                    rival_set.add((p, new_v))

            for e in tries:
                rival_set.add(self.allowed_ideas[e['j']])
            rival_set.update(extra)

            for r in rival_set:
                if r not in self.allowed_ideas: continue
                if r == leader or r in base or r in d['beaten'] or r in d['rivals']:
                    continue
                total = 0.0
                for h, s_l in zip(past, fits):
                    if min(s_l, fit(base + [r], h['z'], h['a'])[2]) < SURPRISE:
                        total += float(np.clip(evidence(base, leader, r, h['z'], h['a']), -6.0, 6.0))
                d['rivals'][r] = total
                d['wide'].add(r)

        def resolve(leader, k):
            nonlocal held, changed_mind, found_at, beaten_total
            d = doubts[leader]
            for r in [r for r, e in d['rivals'].items() if e >= 9.0]:
                d['beaten'].append(r)
                del d['rivals'][r]
                beaten_total += 1
            losers = {r: e for r, e in d['rivals'].items() if e <= -9.0}
            if not losers: return
            winner = min(losers, key=losers.get)
            shift = d['rivals'].pop(winner)
            new = {'rivals': {r: e - shift for r, e in d['rivals'].items()}, 'beaten': [], 'stuck': collections.Counter(), 'wide': set()}
            new['wide'] = {r for r in d['wide'] if r in new['rivals']}
            new['rivals'][leader] = -shift
            del doubts[leader]
            doubts[winner] = new
            ruled_out[leader] = k
            if winner not in entry_of:
                entry_of[winner] = {'j': self.allowed_ideas.index(winner), 'confidence': 0.0, 'sense': True, 'novel': winner not in self.tried_ever, 'kept': False, 'shown': False, 'sure': False}
                self.tried_ever.add(winner)
            if held is not None and held['idea'] == leader:
                held = {'idea': winner, 'active': 0, 'repressive': 0, 'entry': entry_of[winner], 'replaces': held['replaces']}
            else:
                kept[kept.index(leader)] = winner
                entry_of[leader]['kept'] = False
                entry_of[winner]['kept'] = True
                changed_mind += 1
                if winner == truth and found_at is None: found_at = k + 1
            resolve(winner, k)

        for k, sit in enumerate(world['situations']):
            rng = np.random.default_rng([seed, index, k])
            data = [samples_from(*simulate(world, sit['m'], u, rng, sit['trick']), u) for u in sit['pushes']]
            z = np.vstack([d[0].numpy() for d in data])
            a = np.concatenate([d[1].numpy() for d in data])
            xs, _ = simulate(world, sit['m'], sit['check_u'], rng, sit['trick'])
            theta, left, surprise = fit(kept, z, a)
            misses.append(miss(predict(kept, theta, sit['check_u']), xs))
            seen = {'z': z, 'a': a, 'budget': 3}
            history.append(seen)
            holding = held['idea'] if held is not None else None

            for leader in list(doubts):
                if leader in doubts:
                    widen(leader, history[:-1])
                    tests += self.doubt(leader, base_for(leader), doubts[leader], seen, world, sit, rng)
                    resolve(leader, k)

            if holding is not None and held is not None and held['idea'] == holding and surprise > SURPRISE:
                ideas = base_for(holding) + [holding]
                t2, _, s2 = fit(ideas, seen['z'], seen['a'])
                base = base_for(holding)
                if s2 < SURPRISE and miss(predict(ideas, t2, sit['check_u']), xs) < misses[-1]:
                    held['active'] += 1
                elif s2 < SURPRISE or any(fit(base + [i], seen['z'], seen['a'])[2] < SURPRISE
                                          for i in self.allowed_ideas if i != holding and i not in base):
                    held['repressive'] += 1
                # Otherwise nothing it can imagine explains this situation (a hidden
                # bump): it says nothing against the idea it holds. (Added during development.)
                if held['active'] >= 2 and held['active'] > held['repressive']:
                    if held['replaces'] is not None:
                        kept.remove(held['replaces'])
                        entry_of[held['replaces']]['kept'] = False
                        doubts.pop(held['replaces'], None)
                        changed_mind += 1
                    kept.append(holding)
                    held['entry']['kept'] = True
                    if holding == truth and found_at is None: found_at = k + 1
                    held = None
                elif held['repressive'] >= 2:
                    ruled_out[holding] = k
                    doubts.pop(holding, None)
                    held = None
                continue
            if holding is not None or surprise <= SURPRISE:
                continue

            along, grid, offset = picture(z, left)
            F = feelings(along, grid, offset, self.allowed_ideas)
            look = looks(along, offset)
            first_look = look if first_look is None else first_look
            if not (self.met and max(float(look @ m) for m in self.met) >= 0.98):
                unfamiliar += 1

            allowed = np.array([i not in kept and not (i in ruled_out and k - ruled_out[i] < 3) for i in self.allowed_ideas])
            if stage == 'hints' and self.rng.random() < hint_chance:
                hints += 1
                if truth in self.allowed_ideas:
                    allowed &= np.array([partly(i, truth) or i == truth for i in self.allowed_ideas])
            if not allowed.any():
                continue

            p = self.hunch.odds(F, allowed)
            watching = stage == 'watch' and not shown
            n_imagine = min(4, int(allowed.sum()))
            order = [int(j) for j in self.rng.choice(len(self.allowed_ideas), size=n_imagine, replace=False, p=p)]

            if watching and truth in self.allowed_ideas:
                if self.allowed_ideas.index(truth) not in order:
                    order[0] = self.allowed_ideas.index(truth)
                else:
                    order.remove(self.allowed_ideas.index(truth))
                    order.insert(0, self.allowed_ideas.index(truth))
                shown = True
                self.hunch.nudge(F, p, order[0], S.RATE)

            contenders = []
            for n, j in enumerate(order):
                idea = self.allowed_ideas[j]
                imagined += 1
                if idea == truth and right_at is None: right_at = imagined
                _, _, s_with = fit(kept + [idea], z, a)
                replaces = None
                if kept:
                    _, _, s_instead = fit(kept[:-1] + [idea], z, a)
                    if s_instead < SURPRISE and s_instead <= s_with:
                        s_with, replaces = s_instead, kept[-1]
                entry = {'F': F, 'p': p, 'j': j, 'confidence': float(p[j]), 'sense': s_with < SURPRISE,
                         'novel': idea not in self.tried_ever, 'kept': False, 'shown': watching and n == 0, 'sure': False}
                tries.append(entry)
                entry_of[idea] = entry
                self.tried_ever.add(idea)
                self.tried_count[idea] += 1
                if not entry['sense']:
                    ruled_out[idea] = k
                else:
                    contenders.append((s_with, idea, replaces))
            if not contenders:
                continue

            if watching and any(c[1] == truth for c in contenders):
                _, leader, replaces = next(c for c in contenders if c[1] == truth)
            else:
                _, leader, replaces = min(contenders, key=lambda c: c[0])

            held = {'idea': leader, 'active': 0, 'repressive': 0, 'entry': entry_of[leader], 'replaces': replaces}
            rivals = {c[1]: 0.0 for c in contenders if c[1] != leader}
            doubts[leader] = {'rivals': rivals, 'beaten': [], 'stuck': collections.Counter(), 'wide': set()}
            widen(leader, history[:-1])
            tests += self.doubt(leader, base_for(leader), doubts[leader], seen, world, sit, rng)
            resolve(leader, k)

        explained = sum(fit(kept, h['z'], h['a'])[2] <= SURPRISE for h in history[-3:]) * 2 > min(3, len(history))
        sayings, sure_of = [], {}
        audit_better, truth_open = False, False
        for idea in kept:
            # Before it says "sure", it weighs its idea against every idea it can form, over
            # everything it saw (effort is free). This audit never changes what it keeps, so
            # "found" still measures its own limited search; it only decides whether it may
            # say "sure", and names what fits as well. (Added during development.)
            d = doubts.setdefault(idea, {'rivals': {}, 'beaten': [], 'stuck': collections.Counter(), 'wide': set()})
            widen(idea, history, extra=self.allowed_ideas)
            for r in [r for r, e in d['rivals'].items() if e >= 9.0]:
                d['beaten'].append(r)
                del d['rivals'][r]
            audit_better |= any(e <= -9.0 for e in d['rivals'].values())
            truth_open |= truth in d['rivals']
            sure_of[idea] = not d['rivals'] and explained
            entry_of[idea]['sure'] = sure_of[idea]
            closest = sorted(d['rivals'], key=d['rivals'].get)
            sayings.append(say(idea, sure_of[idea], d['beaten'], closest, d['stuck'], True, d['wide']))
        if not explained:
            sayings.append('Something is still pushing it that I cannot explain. I do not know what it is yet.')
        final_theta, _, _ = fit(kept, seen['z'], seen['a'])
        world_miss = float(np.mean(misses))

        if world['part'] == 'practice':
            for e in tries:
                idea, feel = self.allowed_ideas[e['j']], e['confidence']
                if idea == truth: credit = 1.0 + (0.5 if feel < 0.2 else 0.0)
                elif partly(idea, truth): credit = 0.5 * (1.0 - feel)
                else: credit = -feel
                if e['sense'] and e['novel']: credit += 0.25
                if e['kept']:
                    if idea != truth: credit -= feel
                    credit += 0.5 * (1.0 - min(world_miss, 1.0))
                    if e['sure']: credit += 0.5 if idea == truth else -1.0
                self.learn(e, credit)
            if first_look is not None:
                self.met.append(first_look)

        return {'index': index, 'part': world['part'], 'force': world['force'], 'stage': stage,
                'hints': hints, 'truth': explain(truth), 'kept': [explain(i) for i in kept],
                'found': truth in kept, 'found_at': found_at, 'right_idea_was_number': right_at,
                'ideas_imagined': imagined, 'miss': world_miss, 'unfamiliar': unfamiliar,
                'changed_mind': changed_mind, 'tests': tests, 'rivals_beaten': beaten_total,
                'sure': bool(kept) and all(sure_of.values()) and explained,
                'audit_better': audit_better, 'truth_open_rival': truth_open,
                'rivals_left': sorted({explain(r) for i in kept for r in doubts.get(i, {'rivals': {}})['rivals']}),
                'wrong_kept': sum(1 for i in kept if i != truth and not partly(i, truth)),
                'partly_kept': sum(1 for i in kept if partly(i, truth)),
                'kept_ideas': [{'confidence': e['confidence'], 'right': self.allowed_ideas[e['j']] == truth,
                                'shown': e['shown'], 'sure': e['sure']} for e in tries if e['kept']],
                'says': sayings, 'formula': formula(kept, final_theta)}

def live_school(seed, learner):
    torch.set_num_threads(1)
    started = time.perf_counter()
    student = Student(learner, seed)
    records = [student.live_world(world, i, seed) for i, world in enumerate(school_plan(seed))]
    return {'seed': seed, 'learner': learner, 'worlds': records, 'hunch': student.hunch.theta.tolist(),
            'seconds': time.perf_counter() - started}
