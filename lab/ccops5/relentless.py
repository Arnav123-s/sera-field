"""ccops5 lab | school: the relentless robot, humble and sure-footed.

The humble robot doubted itself but never went back: once a half-right idea
made the surprise go away, nothing made it look again. The relentless robot is
humble in the same way (points off for being sure and wrong; being wrong is
fine; effort is free) and it does not stop until it has made sure:

  it imagines every idea it has not ruled out, in the order its hunch feels them;
  it keeps a list of rivals: every other idea that also explains what it saw;
  it weighs the evidence for its idea against each rival, over everything it
    has seen, and never decides from one situation alone (a re-trial);
  it chooses pushes of its own where its idea and the strongest rival would
    disagree most, as the nursery's imagination chooses pushes;
  it changes its mind when a rival wins, even about an idea it kept;
  it keeps checking a kept idea until every rival is beaten;
  it says it is sure only when every rival has been beaten; otherwise it names
    the rival it could not rule out, and whether its pushes could tell them apart.

Learners:
  relentless    all of the above
  no_tests      the same, without pushes of its own: it weighs rivals only on
                the pushes every robot makes
  imagine_all   imagines every idea too, but keeps the best fit without weighing
                rivals, like the humble robot does

Gentle worlds: the same worlds, but the pushes every robot makes are soft (0.3
each way), so curved forces look almost straight. Only the relentless robot can
push harder, where its idea and a rival would part.

Built as an isolated experiment. Not part of sera-field.
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

LEARNERS = ('relentless', 'no_tests', 'imagine_all')
TESTS = 3                 # pushes of its own it may add in one situation
TEST_COMMANDS = W.COMMANDS
DECISIVE = 9.0            # evidence that beats a rival (twice the log-odds: about 90 to 1)
ONE_SITUATION = 6.0       # the most one situation may add, so one odd situation never decides
HOPELESS = 1.0            # a push expected to add less evidence than this cannot tell them apart
RETRY_AFTER = 3           # situations after which an idea that failed one check may be imagined again
NEED = 2                  # checks before keeping, always
GENTLE = (0.3, -0.3)      # the soft pushes of a gentle world
LAST = 3                  # it has explained a world when it explains most of its last situations

SYMBOL = {('position', 'straight'): 'x', ('position', 'growing'): 'x|x|',
          ('position', 'steps'): 'tanh(x/0.05)', ('position', 'cubic'): 'x³', ('position', 'wave'): 'sin(x)',
          ('speed', 'straight'): 'v', ('speed', 'growing'): 'v|v|',
          ('speed', 'steps'): 'tanh(v/0.05)', ('speed', 'cubic'): 'v³', ('speed', 'wave'): 'sin(v)',
          ('nothing', 'steady'): '1'}
SENTENCE = {
    ('position', 'straight'): 'it is pulled back toward the middle, harder the farther away it is, like a spring',
    ('position', 'growing'): 'it is pulled back toward the middle, much harder the farther it goes',
    ('position', 'steps'): 'it is pushed toward the middle by the same amount on either side, like a valley',
    ('position', 'cubic'): 'it is pulled back gently near the middle and very hard far away',
    ('position', 'wave'): 'it is pulled back the way a swing is: by the sine of how far it has gone',
    ('speed', 'straight'): 'it is slowed in step with its speed, like rubbing',
    ('speed', 'growing'): 'it is slowed more and more as it goes faster, by speed times speed, like water',
    ('speed', 'steps'): 'it is slowed by the same amount whenever it moves, like dry friction',
    ('speed', 'cubic'): 'it is slowed a little when slow and very sharply when fast, by speed cubed',
    ('speed', 'wave'): 'it is slowed by the sine of its speed',
    ('nothing', 'steady'): 'a steady push always leans it one way, like a slope',
}


def evidence(base, leader, rival, z, a):
    """How much better the leader explains these samples than the rival does,
    in units of the sensor noise (each gets its own free numbers)."""
    _, left_l, _ = S.fit(base + [leader], z, a)
    _, left_r, _ = S.fit(base + [rival], z, a)
    return float(left_r @ left_r - left_l @ left_l) / SIGMA_A ** 2


def imagine(ideas, theta, u):
    """Imagine push u with these ideas and numbers: positions and speeds."""
    def acc(x, v, c):
        return float(np.clip(S.columns(ideas, np.array([[x, v, c]]))[0] @ theta, -50, 50))

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
    """The push where it expects its idea and the rival to part most. It
    imagines each push as its idea says it would go, adds that to what it has
    seen, and asks how much worse the rival would then explain everything."""
    now = evidence(base, leader, rival, z, a)
    theta, _, _ = S.fit(base + [leader], z, a)
    best_u, best_gain = None, -np.inf
    for u in TEST_COMMANDS:
        zu = samples_from(*imagine(base + [leader], theta, u), u)[0].numpy()
        au = S.columns(base + [leader], zu) @ theta
        gain = evidence(base, leader, rival, np.vstack([z, zu]), np.concatenate([a, au])) - now
        if gain > best_gain:
            best_u, best_gain = u, gain
    return best_u, best_gain


def name(idea):
    return f'"{P.explain(idea)}"'


def say(idea, sure, beaten, rivals, stuck, tested, wide=()):
    """Its idea in a plain sentence, with how sure it is and why."""
    words = SENTENCE[idea][0].upper() + SENTENCE[idea][1:] + '.'
    close = [r for r in beaten if r not in wide]
    rest = ', and every other idea I can imagine fits worse' if any(r in wide for r in beaten) else ''
    if sure and close:
        return words + f" I am sure: I tested it against {', '.join(name(r) for r in close)} and it won{rest}."
    if sure:
        return words + ' I am sure: nothing else I can imagine fits what I saw.'
    if not rivals:
        return words + ' I am not sure yet: part of what I saw is still unexplained.'
    why = ('and none of my pushes could tell them apart' if any(stuck[r] for r in rivals)
           else 'and I ran out of chances to tell them apart' if tested
           else 'and I did not find a way to tell them apart')
    return words + f" I am not sure: {', '.join(name(r) for r in rivals)} explains what I saw as well, {why}."


def formula(ideas, theta):
    """Its ideas as a formula, with the numbers it fitted for the last object."""
    terms = [f'{theta[0]:.2f}·tanh(1.6u)']
    for idea, c in zip(ideas, theta[1:]):
        terms.append(f"{'−' if c < 0 else '+'} {abs(c):.2f}·{SYMBOL[idea]}")
    return 'a = ' + ' '.join(terms)


class Relentless(S.Student):
    def __init__(self, learner, seed):
        if learner not in LEARNERS:
            raise ValueError(learner)
        self.learner = learner
        self.hunch = S.Hunch()
        self.rng = np.random.default_rng([seed, 31])
        self.expected_credit = 0.0
        self.tried_ever = set()
        self.tried_count = collections.Counter()
        self.met = []

    def stage(self, index, world):
        # Taught like the humble robot: watch, then fading hints, then alone.
        if world['part'] == 'exam':
            return 'alone', 0.0
        if index < S.WATCH_WORLDS:
            return 'watch', 0.0
        if index < S.WATCH_WORLDS + S.HINT_WORLDS:
            return 'hints', 0.8 - 0.7 * (index - S.WATCH_WORLDS) / max(S.HINT_WORLDS - 1, 1)
        return 'alone', 0.0

    def doubt(self, leader, base, d, seen, world, sit, rng):
        """Weigh one leader against its open rivals on this situation, pushing
        where they would part if it may. Returns how many pushes it made."""
        open_ = [r for r in d['rivals'] if abs(d['rivals'][r]) < DECISIVE]
        if not open_:
            return 0

        def weigh():
            return {r: d['rivals'][r] + float(np.clip(evidence(base, leader, r, seen['z'], seen['a']),
                                                      -ONE_SITUATION, ONE_SITUATION)) for r in open_}

        now, stuck_here, pushes = weigh(), set(), 0
        while self.learner == 'relentless' and seen['budget'] > 0:
            waiting = [r for r in open_ if abs(now[r]) < DECISIVE and r not in stuck_here]
            if not waiting:
                break
            target = min(waiting, key=now.get)          # the rival closest to beating it
            u, gain = best_test(base, leader, target, seen['z'], seen['a'])
            if gain < HOPELESS:
                stuck_here.add(target)
                continue
            z, a = samples_from(*P.simulate(world, sit['m'], u, rng, sit['trick']), u)
            seen['z'] = np.vstack([seen['z'], z.numpy()])
            seen['a'] = np.concatenate([seen['a'], a.numpy()])
            seen['budget'] -= 1
            pushes += 1
            now = weigh()
        for r in stuck_here:
            d['stuck'][r] += 1
        # Only the better of the two may speak: a situation neither explains
        # (a hidden bump) says nothing about which is right.
        for r in open_:
            _, _, s_l = S.fit(base + [leader], seen['z'], seen['a'])
            _, _, s_r = S.fit(base + [r], seen['z'], seen['a'])
            if min(s_l, s_r) < SURPRISE:
                d['rivals'][r] = now[r]
        return pushes

    def live_world(self, world, index, seed):
        truth = P.FORCES[world['force']][0]
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

        def resolve(leader, k):
            """Beaten rivals leave; a rival that beats the leader takes its place."""
            nonlocal held, changed_mind, found_at, beaten_total
            d = doubts[leader]
            for r in [r for r, e in d['rivals'].items() if e >= DECISIVE]:
                d['beaten'].append(r)
                del d['rivals'][r]
                beaten_total += 1
            losers = {r: e for r, e in d['rivals'].items() if e <= -DECISIVE}
            if not losers:
                return
            winner = min(losers, key=losers.get)
            shift = d['rivals'].pop(winner)
            new = {'rivals': {r: e - shift for r, e in d['rivals'].items()}, 'beaten': [],
                   'stuck': collections.Counter(), 'wide': set()}
            new['wide'] = {r for r in d['wide'] if r in new['rivals']}
            new['rivals'][leader] = -shift
            del doubts[leader]
            doubts[winner] = new
            ruled_out[leader] = k
            if held is not None and held['idea'] == leader:
                held = {'idea': winner, 'active': 0, 'repressive': 0, 'entry': entry_of[winner],
                        'replaces': held['replaces']}
            else:
                # It changed its mind about an idea it had kept.
                kept[kept.index(leader)] = winner
                entry_of[leader]['kept'] = False
                entry_of[winner]['kept'] = True
                changed_mind += 1
                if winner == truth and found_at is None:
                    found_at = k + 1
            resolve(winner, k)

        def widen(leader, past):
            """Every idea it has not beaten is a rival, even one it ruled out on an
            unlucky situation: to be sure, it must beat everything it can imagine.
            A new rival starts with the evidence of everything already seen."""
            if self.learner == 'imagine_all':
                return
            d, base = doubts[leader], base_for(leader)
            fits = [S.fit(base + [leader], h['z'], h['a'])[2] for h in past]
            for r in P.IDEAS:
                if r == leader or r in base or r in d['beaten'] or r in d['rivals']:
                    continue
                total = 0.0
                for h, s_l in zip(past, fits):
                    if min(s_l, S.fit(base + [r], h['z'], h['a'])[2]) < SURPRISE:
                        total += float(np.clip(evidence(base, leader, r, h['z'], h['a']),
                                               -ONE_SITUATION, ONE_SITUATION))
                d['rivals'][r] = total
                d['wide'].add(r)

        for k, sit in enumerate(world['situations']):
            rng = np.random.default_rng([seed, index, k])
            data = [samples_from(*P.simulate(world, sit['m'], u, rng, sit['trick']), u) for u in sit['pushes']]
            z = np.vstack([d[0].numpy() for d in data])
            a = np.concatenate([d[1].numpy() for d in data])
            xs, _ = P.simulate(world, sit['m'], sit['check_u'], rng, sit['trick'])
            theta, left, surprise = S.fit(kept, z, a)
            misses.append(miss(S.predict(kept, theta, sit['check_u']), xs))
            seen = {'z': z, 'a': a, 'budget': TESTS}
            history.append(seen)
            holding = held['idea'] if held is not None else None

            # 1. Doubt everything it believes that still has open rivals.
            for leader in list(doubts):
                if leader in doubts:
                    widen(leader, history[:-1])
                    resolve(leader, k)
                if leader in doubts:
                    tests += self.doubt(leader, base_for(leader), doubts[leader], seen, world, sit, rng)
                    resolve(leader, k)

            # 2. Check the idea it has been holding, on this new situation.
            if holding is not None and held is not None and held['idea'] == holding and surprise > SURPRISE:
                ideas = base_for(holding) + [holding]
                t2, _, s2 = S.fit(ideas, seen['z'], seen['a'])
                base = base_for(holding)
                if s2 < SURPRISE and miss(S.predict(ideas, t2, sit['check_u']), xs) < misses[-1]:
                    held['active'] += 1
                elif s2 < SURPRISE or any(S.fit(base + [i], seen['z'], seen['a'])[2] < SURPRISE
                                          for i in P.IDEAS if i != holding and i not in base):
                    held['repressive'] += 1
                # Otherwise nothing it can imagine explains this situation (a hidden
                # bump): it says nothing against the idea it holds.
                if held['active'] >= NEED and held['active'] > held['repressive']:
                    if held['replaces'] is not None:
                        kept.remove(held['replaces'])
                        entry_of[held['replaces']]['kept'] = False
                        doubts.pop(held['replaces'], None)
                        changed_mind += 1
                    kept.append(holding)
                    held['entry']['kept'] = True
                    if holding == truth and found_at is None:
                        found_at = k + 1
                    held = None
                elif held['repressive'] >= 2:
                    ruled_out[holding] = k
                    doubts.pop(holding, None)
                    held = None
                continue
            if holding is not None or surprise <= SURPRISE:
                continue

            # 3. Surprised and holding nothing: imagine every idea it may, most-felt first.
            along, offset = S.picture(z, left)
            F = S.feelings(along, offset)
            look = S.looks(along, offset)
            first_look = look if first_look is None else first_look
            if not (self.met and max(float(look @ m) for m in self.met) >= S.FAMILIAR):
                unfamiliar += 1
            allowed = np.array([i not in kept and not (i in ruled_out and k - ruled_out[i] < RETRY_AFTER)
                                for i in P.IDEAS])
            if stage == 'hints' and self.rng.random() < hint_chance:
                hints += 1
                allowed &= np.array([i[0] == truth[0] for i in P.IDEAS])
            if not allowed.any():
                continue
            p = self.hunch.odds(F, allowed)
            watching = stage == 'watch' and not shown
            order = [int(j) for j in self.rng.choice(len(P.IDEAS), size=int(allowed.sum()), replace=False, p=p)]
            if watching:
                order = [P.IDEAS.index(truth)] + [j for j in order if P.IDEAS[j] != truth]
                shown = True
                self.hunch.nudge(F, p, order[0], S.RATE)   # copy what it watched
            contenders = []
            for n, j in enumerate(order):
                idea = P.IDEAS[j]
                imagined += 1
                if idea == truth and right_at is None:
                    right_at = imagined
                _, _, s_with = S.fit(kept + [idea], z, a)
                replaces = None
                if kept:
                    # Could the newest idea it kept be wrong? Try this one in its place.
                    _, _, s_instead = S.fit(kept[:-1] + [idea], z, a)
                    if s_instead < SURPRISE and s_instead <= s_with:
                        s_with, replaces = s_instead, kept[-1]
                entry = {'F': F, 'p': p, 'j': j, 'confidence': float(p[j]), 'sense': s_with < SURPRISE,
                         'novel': idea not in self.tried_ever, 'kept': False, 'shown': watching and n == 0,
                         'sure': False}
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
            rivals = {} if self.learner == 'imagine_all' else {c[1]: 0.0 for c in contenders if c[1] != leader}
            doubts[leader] = {'rivals': rivals, 'beaten': [], 'stuck': collections.Counter(), 'wide': set()}
            widen(leader, history[:-1])
            tests += self.doubt(leader, base_for(leader), doubts[leader], seen, world, sit, rng)
            resolve(leader, k)

        # What it says at the end of the world, and how sure it is.
        # One odd last situation (a hidden bump) should not undo a world's worth of evidence.
        explained = sum(S.fit(kept, h['z'], h['a'])[2] <= SURPRISE for h in history[-LAST:]) * 2 > min(LAST, len(history))
        sayings, sure_of = [], {}
        for idea in kept:
            d = doubts.get(idea, {'rivals': {}, 'beaten': [], 'stuck': collections.Counter(), 'wide': set()})
            sure_of[idea] = not d['rivals'] and explained
            entry_of[idea]['sure'] = sure_of[idea]
            sayings.append(say(idea, sure_of[idea], d['beaten'], list(d['rivals']), d['stuck'],
                               self.learner == 'relentless', d['wide']))
        if not explained:
            sayings.append('Something is still pushing it that I cannot explain. I do not know what it is yet.')
        final_theta, _, _ = S.fit(kept, seen['z'], seen['a'])
        world_miss = float(np.mean(misses))
        if world['part'] == 'practice':
            self.receive_credit(tries, truth, world_miss)
            if first_look is not None:
                self.met.append(first_look)
        return {'index': index, 'part': world['part'], 'force': world['force'], 'stage': stage,
                'hints': hints, 'truth': P.explain(truth), 'kept': [P.explain(i) for i in kept],
                'found': truth in kept, 'found_at': found_at, 'right_idea_was_number': right_at,
                'ideas_imagined': imagined, 'miss': world_miss, 'unfamiliar': unfamiliar,
                'changed_mind': changed_mind, 'tests': tests, 'rivals_beaten': beaten_total,
                'sure': bool(kept) and all(sure_of.values()) and explained,
                'rivals_left': sorted({P.explain(r) for i in kept for r in doubts.get(i, {'rivals': {}})['rivals']}),
                'wrong_kept': sum(1 for i in kept if i != truth and not S.partly(i, truth)),
                'partly_kept': sum(1 for i in kept if S.partly(i, truth)),
                'calibration': statistics.fmean((e['confidence'] - (P.IDEAS[e['j']] == truth)) ** 2
                                                for e in tries if not e['shown']) if any(
                    not e['shown'] for e in tries) else None,
                'kept_ideas': [{'confidence': e['confidence'], 'right': P.IDEAS[e['j']] == truth,
                                'shown': e['shown'], 'sure': e['sure']} for e in tries if e['kept']],
                'says': sayings, 'formula': formula(kept, final_theta)}

    def receive_credit(self, tries, truth, world_miss):
        # The humble robot's credit, plus: sure and right earns more, sure and
        # wrong costs the most. Unsure and wrong costs nothing: it said it could be wrong.
        for e in tries:
            idea, feel = P.IDEAS[e['j']], e['confidence']
            if idea == truth:
                credit = 1.0 + (0.5 if feel < 0.2 else 0.0)
            elif S.partly(idea, truth):
                credit = 0.5 * (1.0 - feel)
            else:
                credit = -feel
            if e['sense'] and e['novel']:
                credit += 0.25
            if e['kept']:
                if idea != truth:
                    credit -= feel
                credit += 0.5 * (1.0 - min(world_miss, 1.0))
                if e['sure']:
                    credit += 0.5 if idea == truth else -1.0
            self.learn(e, credit)


def gentle(plan):
    """The same worlds, with soft pushes; everything else is drawn as before."""
    for world in plan:
        for sit in world['situations']:
            sit['pushes'] = GENTLE
    return plan


def live_relentless(seed, learner, soft=False):
    torch.set_num_threads(1)
    started = time.perf_counter()
    student = Relentless(learner, seed)
    plan = gentle(P.school_plan(seed)) if soft else P.school_plan(seed)
    records = [student.live_world(world, i, seed) for i, world in enumerate(plan)]
    return {'seed': seed, 'learner': learner, 'gentle': soft, 'worlds': records,
            'hunch': student.hunch.theta.tolist(), 'seconds': time.perf_counter() - started}
