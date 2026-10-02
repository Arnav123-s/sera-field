"""ccops5 lab | school: teaching the loop how to discover.

The inner system stays as in the nursery. When surprised it imagines
explanations and checks each against the world. It holds a new idea in doubt
until it passes, and keeps only what passed. What is taught is how to use
that system: which explanations to imagine first (its hunch) and how far to
trust them (its doubt).

Teaching follows the baby's way:
  watch   the teacher shows the right idea at the first surprise
  hints   the teacher sometimes says what to look at, less and less often
  alone   no help
After every practice world the teacher reveals the answer and gives credit.
The hunch then changes by a local rule: credit x (what it felt - what it
expected to feel). A final exam follows, with no help and no learning,
including forces it was never shown.

Learners:
  humble        taught the same way, with humility (the SERA author's second plan):
                being sure and wrong costs points, being unsure and wrong costs
                none, effort is free, a daring idea that proves right earns extra.
                When a surprise looks unlike any it has met, it doubts its gut,
                imagines more widely (including ideas it has rarely tried) and
                checks twice. It may change its mind about an idea it kept.
  taught        watch, fading hints, credit (the SERA author's plan)
  credit_only   alone from the start, with the teacher's credit
  self_taught   no teacher: it credits the ideas it kept itself
  untaught      its hunch never changes: every idea equally likely

Built as an isolated experiment. Not part of sera-field.
"""
import collections
import statistics
import time

import numpy as np
import torch

from . import puzzles as P
from . import world as W
from .mind import DT_MODEL, PRIOR_VAR, SIGMA_A, SURPRISE, miss, samples_from

LEARNERS = ('humble', 'taught', 'credit_only', 'self_taught', 'untaught')
WATCH_WORLDS = 8          # the teacher shows the answer
HINT_WORLDS = 16          # then hints, fading from 80% to 10% of surprises
IMAGINE = 2               # explanations it can imagine at once
SURE = 0.6                # a hunch this strong needs one check; weaker ones need two
FAMILIAR = 0.98           # a surprise this similar to one met before is familiar
WIDE = 3                  # explanations it imagines when a surprise is unfamiliar
RATE = 0.3                # how fast the hunch changes
BANDS = 5

# The hunch's numbers: relevance of an input (2), a template per shape over
# the bands (shared by position and speed), a lean per shape, and three
# numbers plus a lean for the steady push.
N_SHAPES = len(P.SHAPES)
REL, TPL = 0, 2
LEAN = TPL + N_SHAPES * BANDS
STEADY = LEAN + N_SHAPES
STEADY_LEAN = STEADY + 3
N_PARAMS = STEADY_LEAN + 1


def picture(z, leftover):
    """What the unexplained part looks like: its average in five bands of
    position and five bands of speed, flipped so that it rises."""
    q = leftover / (np.sqrt(np.mean(leftover ** 2)) + 1e-12)
    along = {}
    for name, col in (('position', 0), ('speed', 1)):
        s = z[:, col]
        bands = np.array_split(np.argsort(s, kind='stable'), BANDS)
        means = np.array([q[b].mean() for b in bands])
        c = float(np.corrcoef(s, q)[0, 1]) if np.std(s) > 1e-9 else 0.0
        c = c if np.isfinite(c) else 0.0
        along[name] = (means * (1.0 if c >= 0 else -1.0), float(np.std(means)), abs(c))
    return along, float(abs(q.mean()))


def looks(along, offset):
    """The picture as one direction, to compare with pictures met before."""
    v = np.concatenate([along['position'][0], along['speed'][0],
                        [along['position'][1], along['speed'][1], along['position'][2], along['speed'][2], offset]])
    return v / (np.linalg.norm(v) + 1e-12)


def feelings(along, offset):
    """One row per idea: the numbers its pull is made of."""
    F = np.zeros((len(P.IDEAS), N_PARAMS))
    for j, (source, shape) in enumerate(P.IDEAS):
        if source == 'nothing':
            F[j, STEADY:STEADY + 3] = (offset, max(a[1] for a in along.values()),
                                       max(a[2] for a in along.values()))
            F[j, STEADY_LEAN] = 1.0
        else:
            bands, spread, corr = along[source]
            h = P.SHAPES.index(shape)
            F[j, REL:REL + 2] = (spread, corr)
            F[j, TPL + h * BANDS:TPL + (h + 1) * BANDS] = bands
            F[j, LEAN + h] = 1.0
    return F


class Hunch:
    """Its gut feeling about which explanation to imagine first. The same
    shape templates are used along position and along speed, so a shape
    learned on one can be recognised on the other."""

    def __init__(self):
        self.theta = np.zeros(N_PARAMS)

    def odds(self, F, allowed):
        z = np.where(allowed, F @ self.theta, -np.inf)
        p = np.exp(z - z[allowed].max())
        return p / p.sum()

    def nudge(self, F, p, j, amount):
        # A local rule: amount x (this idea's features - the features it expected).
        self.theta += amount * (F[j] - p @ F)


def columns(ideas, z):
    """Its own hand (known since the nursery), then one column per idea."""
    return np.column_stack([np.tanh(1.6 * z[:, 2])] + [P.idea_value(i, z[:, 0], z[:, 1]) for i in ideas])


def fit(ideas, z, a):
    """Free numbers for this situation, what is left over, and how surprising
    that is (1 = only sensor noise is left)."""
    x = columns(ideas, z)
    precision = x.T @ x / SIGMA_A ** 2 + np.eye(x.shape[1]) / PRIOR_VAR
    theta = np.linalg.solve(precision, x.T @ a / SIGMA_A ** 2)
    left = a - x @ theta
    return theta, left, float(np.sqrt(np.mean(left ** 2)) / SIGMA_A)


def predict(ideas, theta, u):
    """Imagine the test push with these ideas and numbers."""
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


def partly(idea, truth):
    return idea != truth and (idea[0] == truth[0] or idea[1] == truth[1])


class Student:
    def __init__(self, learner, seed):
        if learner not in LEARNERS:
            raise ValueError(learner)
        self.learner = learner
        self.hunch = Hunch()
        self.rng = np.random.default_rng([seed, 31])
        self.expected_credit = 0.0
        self.tried_ever = set()
        self.tried_count = collections.Counter()
        self.met = []             # what surprises it has met looked like

    def stage(self, index, world):
        if world['part'] == 'exam' or self.learner not in ('taught', 'humble'):
            return 'alone', 0.0
        if index < WATCH_WORLDS:
            return 'watch', 0.0
        if index < WATCH_WORLDS + HINT_WORLDS:
            return 'hints', 0.8 - 0.7 * (index - WATCH_WORLDS) / max(HINT_WORLDS - 1, 1)
        return 'alone', 0.0

    def learn(self, entry, credit):
        self.hunch.nudge(entry['F'], entry['p'], entry['j'], RATE * (credit - self.expected_credit))
        self.expected_credit += 0.05 * (credit - self.expected_credit)

    def live_world(self, world, index, seed):
        truth = P.FORCES[world['force']][0]
        stage, hint_chance = self.stage(index, world)
        kept, ruled_out, tries, misses = [], set(), [], []
        held, shown, found_at, right_at, imagined, hints = None, False, None, None, 0, 0
        humble, kept_entry, first_look, unfamiliar, changed_mind = self.learner == 'humble', {}, None, 0, 0
        for k, sit in enumerate(world['situations']):
            rng = np.random.default_rng([seed, index, k])
            data = [samples_from(*P.simulate(world, sit['m'], u, rng, sit['trick']), u) for u in sit['pushes']]
            z = np.vstack([d[0].numpy() for d in data])
            a = np.concatenate([d[1].numpy() for d in data])
            xs, _ = P.simulate(world, sit['m'], sit['check_u'], rng, sit['trick'])
            theta, left, surprise = fit(kept, z, a)
            misses.append(miss(predict(kept, theta, sit['check_u']), xs))
            if surprise <= SURPRISE:
                continue
            if held is not None:
                # Check the idea it is holding on this new situation.
                ideas = [i for i in kept if i != held['replaces']] + [held['idea']]
                t2, _, s2 = fit(ideas, z, a)
                if s2 < SURPRISE and miss(predict(ideas, t2, sit['check_u']), xs) < misses[-1]:
                    held['active'] += 1
                else:
                    held['repressive'] += 1
                if held['active'] >= held['need'] and held['active'] > held['repressive']:
                    if held['replaces'] is not None:
                        # It changed its mind: the new idea explains more than the old one did.
                        kept.remove(held['replaces'])
                        kept_entry.pop(held['replaces'])['kept'] = False
                        changed_mind += 1
                    kept.append(held['idea'])
                    held['entry']['kept'] = True
                    kept_entry[held['idea']] = held['entry']
                    if held['idea'] == truth:
                        found_at = k + 1
                    held = None
                elif held['repressive'] >= 2:
                    ruled_out.add(held['idea'])
                    held = None
                continue
            # Surprised and holding nothing: imagine explanations.
            along, offset = picture(z, left)
            F = feelings(along, offset)
            look = looks(along, offset)
            first_look = look if first_look is None else first_look
            familiar = bool(self.met) and max(float(look @ m) for m in self.met) >= FAMILIAR
            allowed = np.array([i not in kept and i not in ruled_out for i in P.IDEAS])
            if stage == 'hints' and self.rng.random() < hint_chance:
                hints += 1
                allowed &= np.array([i[0] == truth[0] for i in P.IDEAS])
            if not allowed.any():
                continue
            p = self.hunch.odds(F, allowed)
            watching = stage == 'watch' and not shown
            if watching:
                picks = [P.IDEAS.index(truth)]
                shown = True
                self.hunch.nudge(F, p, picks[0], RATE)   # copy what it watched
            else:
                n = min(IMAGINE, int(allowed.sum()))
                picks = [int(j) for j in self.rng.choice(len(P.IDEAS), size=n, replace=False, p=p)]
                if humble and not familiar:
                    # Doubt its gut: also imagine the idea it has tried least.
                    unfamiliar += 1
                    rest = [j for j in range(len(P.IDEAS)) if allowed[j] and j not in picks]
                    if rest and len(picks) < WIDE:
                        fewest = min(self.tried_count[P.IDEAS[j]] for j in rest)
                        picks.append(int(self.rng.choice([j for j in rest if self.tried_count[P.IDEAS[j]] == fewest])))
            best = None
            for j in picks:
                idea = P.IDEAS[j]
                imagined += 1
                if idea == truth and right_at is None:
                    right_at = imagined
                _, _, s_with = fit(kept + [idea], z, a)
                replaces = None
                if humble and kept:
                    # Could the newest idea it kept be wrong? Try this one in its place.
                    _, _, s_instead = fit(kept[:-1] + [idea], z, a)
                    if s_instead < SURPRISE and s_instead <= s_with:
                        s_with, replaces = s_instead, kept[-1]
                entry = {'F': F, 'p': p, 'j': j, 'confidence': float(p[j]), 'sense': s_with < SURPRISE,
                         'novel': idea not in self.tried_ever, 'kept': False, 'shown': watching}
                tries.append(entry)
                self.tried_ever.add(idea)
                self.tried_count[idea] += 1
                if not entry['sense']:
                    ruled_out.add(idea)
                elif best is None or s_with < best[0]:
                    best = (s_with, idea, entry, replaces)
            if best is not None:
                _, idea, entry, replaces = best
                need = 1 if (entry['shown'] or entry['confidence'] >= SURE) else 2
                if humble and not familiar:
                    need = 2
                held = {'idea': idea, 'need': need, 'active': 0, 'repressive': 0, 'entry': entry,
                        'replaces': replaces}
        world_miss = float(np.mean(misses))
        if world['part'] == 'practice':
            self.receive_credit(tries, truth, world_miss)
            if first_look is not None:
                self.met.append(first_look)
        return {'index': index, 'part': world['part'], 'force': world['force'], 'stage': stage,
                'hints': hints, 'truth': P.explain(truth), 'kept': [P.explain(i) for i in kept],
                'found': truth in kept, 'found_at': found_at, 'right_idea_was_number': right_at,
                'ideas_imagined': imagined, 'miss': world_miss, 'unfamiliar': unfamiliar,
                'changed_mind': changed_mind,
                'wrong_kept': sum(1 for i in kept if i != truth and not partly(i, truth)),
                'partly_kept': sum(1 for i in kept if partly(i, truth)),
                'calibration': statistics.fmean((e['confidence'] - (P.IDEAS[e['j']] == truth)) ** 2
                                                for e in tries if not e['shown']) if any(
                    not e['shown'] for e in tries) else None,
                'kept_ideas': [{'confidence': e['confidence'], 'right': P.IDEAS[e['j']] == truth,
                                'shown': e['shown']} for e in tries if e['kept']]}

    def receive_credit(self, tries, truth, world_miss):
        if self.learner == 'humble':
            # The teacher reveals the answer. Being wrong is fine; being sure and
            # wrong is not. Effort costs nothing. A daring idea that proves right
            # earns extra.
            for e in tries:
                idea, sure = P.IDEAS[e['j']], e['confidence']
                if idea == truth:
                    credit = 1.0 + (0.5 if sure < 0.2 else 0.0)
                elif partly(idea, truth):
                    credit = 0.5 * (1.0 - sure)
                else:
                    credit = -sure
                if e['sense'] and e['novel']:
                    credit += 0.25                         # a new idea that made sense
                if e['kept']:
                    if idea != truth:
                        credit -= sure                     # trusted something wrong, worse the surer it was
                    credit += 0.5 * (1.0 - min(world_miss, 1.0))
                self.learn(e, credit)
        elif self.learner in ('taught', 'credit_only'):
            # The teacher reveals the answer and gives credit.
            for e in tries:
                idea = P.IDEAS[e['j']]
                credit = 1.0 if idea == truth else (0.5 if partly(idea, truth) else 0.0)
                if e['sense'] and e['novel']:
                    credit += 0.25                         # a new idea that made sense
                if not e['sense']:
                    credit -= 0.25                         # an idea that did not fit at all
                if e['kept']:
                    if idea != truth:
                        credit -= 0.5                      # trusted something wrong
                    credit += 0.5 * (1.0 - min(world_miss, 1.0))   # guessed well with it
                self.learn(e, credit)
        elif self.learner == 'self_taught':
            # No teacher: it believes the ideas it kept were right.
            for e in tries:
                credit = (1.0 if e['kept'] else 0.0) + (0.25 if e['sense'] and e['novel'] else 0.0)
                credit -= 0.0 if e['sense'] else 0.25
                self.learn(e, credit)


def live_school(seed, learner):
    torch.set_num_threads(1)
    started = time.perf_counter()
    student = Student(learner, seed)
    records = [student.live_world(world, i, seed) for i, world in enumerate(P.school_plan(seed))]
    return {'seed': seed, 'learner': learner, 'worlds': records, 'hunch': student.hunch.theta.tolist(),
            'seconds': time.perf_counter() - started}
