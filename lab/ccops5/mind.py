"""ccops5 lab | the connected loop.

A whiteboard for the current situation and a library kept for life, joined
the way the SERA papers join them:

  perceive with the library -> imagine -> re-try with variation -> check the
  guess against the world -> keep only what passed -> grow a new law when a
  surprise will not go away -> use the library next time.

The same propose-check-keep loop runs at three levels: memories of objects,
laws of motion, and arithmetic rules for how parts make a whole.

`mode` switches one connection off, so each connection can be tested:

  full          everything connected
  forget_kinds  laws are kept, but objects, words and places are forgotten
                after every situation (how CORE-022 treats its state)
  reset_all     the whole library is wiped after every situation
  ungated       everything is stored without being checked first
  passive       no re-trying with variation: the same push every time
  frozen_laws   may learn its own hand, but no new laws after that
  no_reuse      a law may only be used in the kind of place it was found

Built as an isolated experiment. Not part of sera-field.
"""
import math

import numpy as np
import torch

from . import world as W
from .laws import design, grow

SIGMA_A = math.sqrt(2) * W.SIGMA_V / W.DT_OBS   # noise in one measured acceleration
PRIOR_VAR = 2.0 ** 2       # what "no idea yet" means for one coefficient
MAX_TRIALS = 3             # pushes allowed before the test push
MIN_TRIALS = 2             # always throw at least twice
HYPOTHESES = 12            # imagined versions of the situation
DT_MODEL = 0.025           # imagination time step
SURPRISE = 1.8             # leftover error / sensor noise that counts as surprising
WINDOW = 8                 # recent situations the surprise monitor watches
PERSISTENT = 5             # surprising situations in that window that start growth
SAME_LOOK = 0.5            # two sightings of one object differ by about 0.2
WORD_RIDGE = 1.0           # pull on word meanings toward "this word changes nothing"
RULE_PASS = 0.15           # a worked-out guess this close to what happened counts as right
MODES = ('full', 'forget_kinds', 'reset_all', 'ungated', 'passive', 'frozen_laws', 'no_reuse')


def samples_from(xs, vs, u):
    """One trial -> (situation, measured acceleration) samples.

    The learner works out accelerations itself from its own velocity readings;
    nothing hands it forces or accelerations."""
    n = W.N_OBS - 1
    z = np.zeros((n, 3))
    z[:, 0] = .5 * (xs[:-1] + xs[1:])
    z[:, 1] = .5 * (vs[:-1] + vs[1:])
    z[:W.PUSH_INTERVALS, 2] = u
    a = (vs[1:] - vs[:-1]) / W.DT_OBS
    return torch.from_numpy(z), torch.from_numpy(a)


def fit(laws, mask, samples, mean0, var0):
    """Best coefficients for this situation, starting from what it expected.

    Returns the mean, its uncertainty, and how surprising the leftover error is
    (1 = only sensor noise is left)."""
    z = torch.cat([s[0] for s in samples])
    a = torch.cat([s[1] for s in samples]).numpy()
    with torch.no_grad():
        x = design(laws, z, mask).numpy()
    if x.shape[1] == 0:
        return np.zeros(0), np.zeros((0, 0)), float(np.sqrt(np.mean(a ** 2)) / SIGMA_A)
    precision = x.T @ x / SIGMA_A ** 2 + np.diag(1.0 / var0)
    cov = np.linalg.inv(precision)
    cov = .5 * (cov + cov.T)
    mean = cov @ (x.T @ a / SIGMA_A ** 2 + mean0 / var0)
    ratio = float(np.sqrt(np.mean((a - x @ mean) ** 2)) / SIGMA_A)
    return mean, cov, ratio


def settle(laws, mask, samples, mean0, var0):
    """What it now believes about this situation's numbers, and how surprised it is.

    It starts from its expectation. If the readings flatly disagree with that
    expectation but its laws explain them with other numbers, the expectation
    was wrong, not the laws, and it lets go of the expectation. Surprise is
    always measured with free numbers: how much of what it saw no numbers for
    its current laws can explain."""
    k = len(mean0)
    mean, cov, held = fit(laws, mask, samples, mean0, var0)
    free_mean, free_cov, surprise = fit(laws, mask, samples, np.zeros(k), np.full(k, PRIOR_VAR))
    if held > SURPRISE and surprise < SURPRISE:
        return free_mean, free_cov, surprise, True
    return mean, cov, surprise, False


def imagine(laws, mask, thetas, commands):
    """Play situations forward in the mind. Positions at reading times, (S, N_OBS)."""
    thetas = torch.as_tensor(np.atleast_2d(np.asarray(thetas, dtype=float)))
    push = torch.as_tensor(np.asarray(commands, dtype=float))
    x = torch.zeros(len(push))
    v = torch.zeros_like(x)
    rest = torch.zeros_like(x)

    def acc(x, v, c):
        if not laws:
            return torch.zeros_like(x)
        columns = design(laws, torch.stack((x, v, c), -1), mask)
        return (columns * thetas).sum(-1).clamp(-50, 50)

    out = [x]
    per, h, step = int(round(W.DT_OBS / DT_MODEL)), DT_MODEL, 0
    with torch.no_grad():
        for _ in range(W.N_OBS - 1):
            for _ in range(per):
                c = push if step * h < W.T_PUSH - 1e-9 else rest
                k1x, k1v = v, acc(x, v, c)
                k2x, k2v = v + .5 * h * k1v, acc(x + .5 * h * k1x, v + .5 * h * k1v, c)
                k3x, k3v = v + .5 * h * k2v, acc(x + .5 * h * k2x, v + .5 * h * k2v, c)
                k4x, k4v = v + h * k3v, acc(x + h * k3x, v + h * k3v, c)
                x = x + h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
                v = v + h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
                step += 1
            out.append(x)
    return torch.stack(out, -1).numpy()


def miss(pred, xs):
    """How wrong a guessed path was: 0 = perfect, 1 = as bad as 'nothing moves'."""
    return float(np.sqrt(np.mean((pred - xs) ** 2)) / max(np.sqrt(np.mean(xs ** 2)), 1e-3))


def summarize(notes, k, single_spread=0.15):
    """Expectation (mean, variance) for each coefficient from stored notes.
    A coefficient a note predates stays at 'no idea yet'."""
    mean, var = np.zeros(k), np.full(k, PRIOR_VAR)
    for d in range(k):
        values = [m[d] for m, _ in notes if len(m) > d]
        if not values:
            continue
        inner = [v[d] for m, v in notes if len(m) > d]
        spread = float(np.var(values)) if len(values) > 1 else single_spread ** 2
        mean[d] = float(np.mean(values))
        var[d] = spread + float(np.mean(inner)) + 1e-4
    return mean, var


def appearance_key(app, scene):
    place = np.zeros(len(W.SCENES))
    place[W.SCENES.index(scene)] = 3.0
    return np.concatenate((app, place))


def _one_overs(parts):
    out = np.zeros(parts.shape[1])
    for d in range(parts.shape[1]):
        column = parts[:, d]
        if np.all(column > 1e-9) or np.all(column < -1e-9):
            out[d] = 1.0 / np.sum(1.0 / column)
    return out


def _extreme(parts, pick):
    return parts[pick(np.abs(parts), 0), np.arange(parts.shape[1])]


# The small arithmetic it starts with: ways the numbers it keeps for the parts
# might combine into the numbers of the whole. Which one the world obeys is
# not given; it has to find out.
RULES = {
    'same as one part': lambda p: p[0],
    'average of the parts': lambda p: p.mean(0),
    'parts added up': lambda p: p.sum(0),
    'parts multiplied': lambda p: p.prod(0),
    'one-overs added up': _one_overs,
    'largest part': lambda p: _extreme(p, np.argmax),
    'smallest part': lambda p: _extreme(p, np.argmin),
}


class Mind:
    """The connected learner."""

    def __init__(self, mode='full', seed=0):
        if mode not in MODES:
            raise ValueError(f'unknown mode {mode}')
        self.mode, self.seed = mode, seed
        self.rng = np.random.default_rng([seed, 99])
        self.events = []
        self.proposals = 0
        self.reset_library()

    # ----- the library (kept for life unless a mode wipes it) -----
    def reset_library(self):
        self.laws = []            # laws kept for life
        self.candidate = None     # a proposed law, held but not trusted until checked
        self.kinds = []           # remembered objects, each in one kind of place
        self.word_notes = []      # (words said, place, coefficients)
        self.scene_notes = {}     # place -> notes from every checked situation there
        self.rules = {name: {'active': 0, 'repressive': 0, 'misses': 0} for name in RULES}
        self.rule = None          # the arithmetic rule it trusts for stuck-together things
        self.window = []          # was each recent situation surprising?
        self.surprises = []       # data from recent surprising situations
        self.cooldown = 0

    def log(self, index, ep, what, detail=''):
        self.events.append({'episode': index, 'stage': ep['stage'], 'scene': ep['scene'],
                            'what': what, 'detail': detail})

    def usable(self, scene, laws):
        if self.mode != 'no_reuse':
            return None
        return np.array([1.0 if law.origin in ('body', scene) else 0.0 for law in laws])

    # ----- perception: the library shapes what it expects -----
    def match(self, key):
        best, distance = None, SAME_LOOK
        for kind in self.kinds:
            d = float(np.linalg.norm(kind['key'] - key))
            if d < distance:
                best, distance = kind, d
        return best

    def up_to_date(self, notes, scene):
        """A law found in a place means the memories of that place made before
        it were written without it: once newer memories exist, use those."""
        need = max([i + 1 for i, law in enumerate(self.laws) if law.origin == scene], default=0)
        return [n for n in notes if len(n[0]) >= need] or notes

    def expect(self, notes, scene, k):
        return summarize(self.up_to_date(notes, scene), k)

    def scene_prior(self, scene, k):
        return self.expect(self.scene_notes.get(scene, []), scene, k)

    def word_prior(self, words, scene, k):
        """Each word nudges what it expects by how much things called that word
        differed from the rest in this place (a small linear fit over every
        remembered situation where words were said). None if too few."""
        notes = self.up_to_date([(m, said) for said, s, m in self.word_notes if s == scene], scene)
        if not words or len(notes) < 2 * len(W.WORDS):
            return None
        size = min(len(m) for m, _ in notes)

        def features(said):
            return np.array([1.0] + [1.0 if w in said else 0.0 for w in W.WORDS])

        f = np.array([features(said) for _, said in notes])
        y = np.array([m[:size] for m, _ in notes])
        gram = f.T @ f + WORD_RIDGE * np.diag([0.0] + [1.0] * len(W.WORDS))
        meaning = np.linalg.solve(gram, f.T @ y)
        # Spread left over, counting only the notes beyond what the fit used up.
        leftover = ((y - f @ meaning) ** 2).sum(0) / max(len(notes) - np.linalg.matrix_rank(f), 1)
        x = features(words)
        mean, var = np.zeros(k), np.full(k, PRIOR_VAR)
        d = min(size, k)
        mean[:d] = (x @ meaning)[:d]
        var[:d] = leftover[:d] * (1.0 + x @ np.linalg.solve(gram, x)) + 1e-3
        return mean, var

    def recall_parts(self, ep, k):
        """Numbers for each recognised part of a stuck-together thing, or None."""
        parts = []
        for app in ep['parts']:
            kind = self.match(appearance_key(app, ep['scene']))
            if kind is None or not kind['committed']:
                return None
            parts.append(self.expect(kind['notes'], ep['scene'], k)[0])
        return np.array(parts)

    def perceive(self, ep):
        k, scene = len(self.laws), ep['scene']
        if ep.get('parts'):
            parts = self.recall_parts(ep, k)
            if parts is not None and self.rule is not None:
                mean = RULES[self.rule](parts)
                return mean, 0.05 ** 2 + (0.1 * mean) ** 2, 'worked out', None
        else:
            kind = self.match(appearance_key(ep['app'], scene))
            if kind is not None:
                mean, var = self.expect(kind['notes'], scene, k)
                if not kind['committed']:
                    var = var * 4
                return mean, var, 'remembered' if kind['committed'] else 'half-remembered', kind
            said = self.word_prior(ep['words'], scene, k)
            if said is not None:
                return said[0], said[1], 'words', None
        mean, var = self.scene_prior(scene, k)
        return mean, var, 'place average' if scene in self.scene_notes else 'nothing', None

    # ----- imagination chooses the next push (throw again, differently) -----
    def choose(self, laws, mask, mean, cov):
        k = len(mean)
        if k == 0:
            return float(self.rng.choice(W.COMMANDS)), False   # babbling
        draws = self.rng.multivariate_normal(mean, cov + 1e-12 * np.eye(k), size=HYPOTHESES - 1)
        thetas = np.vstack((mean[None], draws))
        commands = np.array(W.COMMANDS)
        paths = imagine(laws, mask, np.repeat(thetas, len(commands), 0), np.tile(commands, HYPOTHESES))
        paths = paths.reshape(HYPOTHESES, len(commands), -1)
        spread = np.sqrt(paths.var(0).mean(-1))
        size = np.sqrt((paths.mean(0) ** 2).mean(-1))
        doubt = spread / np.maximum(size, 1e-3)
        confident = bool(doubt.max() < 0.02)
        if self.mode == 'passive':
            return 0.6, confident
        best = np.flatnonzero(doubt >= doubt.max() - 1e-12)
        return float(commands[int(self.rng.choice(best))]), confident

    # ----- one situation, start to finish -----
    def live(self, ep, rng_world, index):
        if self.mode == 'reset_all':
            self.reset_library()
        elif self.mode == 'forget_kinds':
            self.kinds, self.word_notes, self.scene_notes = [], [], {}
        scene, u_check = ep['scene'], ep['check_u']
        laws = list(self.laws)
        k = len(laws)
        mask = self.usable(scene, laws)
        mean0, var0, source, kind = self.perceive(ep)
        guess = imagine(laws, mask, mean0, [u_check])[0]

        # Guesses it could have made another way, kept only to compare.
        place, _ = self.scene_prior(scene, k)
        others = {}
        if ep['stage'] == W.STAGES[6]:
            said = self.word_prior(ep['words'], scene, k)
            others['words'] = place if said is None else said[0]
        if ep.get('parts'):
            parts = self.recall_parts(ep, k)
            if parts is not None:
                others.update({name: rule(parts) for name, rule in RULES.items()})
        if others:
            others['place'] = place
            names = list(others)
            paths = imagine(laws, mask, np.vstack([others[n] for n in names]), [u_check] * len(names))
            others = dict(zip(names, paths))

        samples, pushes = [], []
        mean, cov = mean0.copy(), np.diag(var0)
        for trial in range(MAX_TRIALS):
            u, confident = self.choose(laws, mask, mean, cov)
            if trial >= MIN_TRIALS and (confident or not laws):
                break
            xs, vs = W.simulate(ep['params'], u, rng_world)
            samples.append(samples_from(xs, vs, u))
            pushes.append(u)
            mean, cov, _, _ = settle(laws, mask, samples, mean0, var0)
        answer = imagine(laws, mask, mean, [u_check])[0]

        tentative = None
        if self.candidate is not None:
            with_law = laws + [self.candidate['law']]
            with_mask = self.usable(scene, with_law)
            with_prior = (np.append(mean0, 0.0), np.append(var0, PRIOR_VAR))
            tmean, _, _, _ = settle(with_law, with_mask, samples, *with_prior)
            tentative = imagine(with_law, with_mask, tmean, [u_check])[0]

        # The world answers the test push. Nothing above has seen this outcome.
        xs, vs = W.simulate(ep['params'], u_check, rng_world)
        miss_before, miss_after = miss(guess, xs), miss(answer, xs)
        everything = samples + [samples_from(xs, vs, u_check)]
        fmean, fcov, ratio, let_go = settle(laws, mask, everything, mean0, var0)
        checked = miss_after < 0.3 and ratio < SURPRISE
        record = {'episode': index, 'stage': ep['stage'], 'scene': scene, 'kind': ep['kind'],
                  'trick': ep['trick'], 'words': list(ep['words']), 'source': source, 'pushes': pushes,
                  'miss_before': miss_before, 'miss_after': miss_after, 'surprise': ratio,
                  'checked': bool(checked), 'expectation_dropped': let_go, 'laws': k, 'law_origins': [law.origin for law in laws],
                  'theta': [float(t) for t in fmean],
                  'theta_sd': [float(s) for s in np.sqrt(np.diag(fcov))] if k else []}
        if 'words' in others:
            record['miss_place_guess'] = miss(others['place'], xs)
            record['miss_word_guess'] = miss(others['words'], xs)
        if ep.get('parts'):
            record['parts'] = len(ep['parts'])
            record['rule_used'] = self.rule if source == 'worked out' else None
            if others:
                record['miss_place_guess'] = miss(others['place'], xs)
                record['rule_misses'] = {name: miss(others[name], xs) for name in RULES}
                self.judge_rules(record['rule_misses'], index, ep)
        if tentative is not None:
            _, _, surprise_with, _ = settle(with_law, with_mask, everything, *with_prior)
            record['miss_with_proposed_law'] = miss(tentative, xs)
            record['surprise_with_proposed_law'] = surprise_with
            self.judge_candidate(record['miss_with_proposed_law'], miss_after, surprise_with, ratio, index, ep)
        if checked or self.mode == 'ungated':
            self.remember(ep, kind, fmean, np.diag(fcov), miss_before, checked, index)
        self.watch(ratio, everything, ep, index)
        return record

    # ----- keep only what passed its check -----
    def remember(self, ep, kind, mean, var, miss_before, checked, index):
        note = (np.array(mean), np.array(var))
        self.scene_notes.setdefault(ep['scene'], []).append(note)
        if ep['words']:
            self.word_notes.append((tuple(ep['words']), ep['scene'], note[0]))
        if ep.get('parts'):
            return    # a one-off stuck-together thing: nothing to recognise later
        if kind is None:
            kind = {'key': appearance_key(ep['app'], ep['scene']), 'scene': ep['scene'], 'name': ep['kind'],
                    'notes': [], 'active': 0, 'repressive': 0, 'misses': 0,
                    'committed': self.mode == 'ungated'}
            self.kinds.append(kind)
        elif checked:
            # Two marks on every memory: times it predicted well, times it did not.
            if miss_before < 0.25:
                kind['active'] += 1
                kind['misses'] = 0
            else:
                kind['repressive'] += 1
                kind['misses'] += 1
            if not kind['committed'] and kind['active'] >= 2:
                kind['committed'] = True
                self.log(index, ep, 'object remembered for good', kind['name'])
            elif kind['committed'] and kind['misses'] >= 2 and self.mode != 'ungated':
                kind['committed'], kind['active'], kind['misses'] = False, 0, 0
                kind['notes'] = kind['notes'][-1:]
                self.log(index, ep, 'memory corrected', kind['name'])
        kind['notes'].append(note)

    # ----- arithmetic is kept the same way: only after the world agrees -----
    def judge_rules(self, rule_misses, index, ep):
        for name, m in rule_misses.items():
            marks = self.rules[name]
            if m < RULE_PASS:
                marks['active'] += 1
                marks['misses'] = 0
            else:
                marks['repressive'] += 1
                marks['misses'] += 1
        if self.rule is not None and self.mode != 'ungated' and self.rules[self.rule]['misses'] >= 2:
            self.log(index, ep, 'math rule dropped', self.rule)
            self.rules[self.rule]['active'] = 0
            self.rule = None
        if self.rule is None:
            if self.mode == 'ungated':
                self.rule = min(rule_misses, key=rule_misses.get)
                self.log(index, ep, 'math rule kept', f'{self.rule}, without checking')
                return
            good = [n for n, mk in self.rules.items() if mk['active'] >= 3 and mk['repressive'] <= 1]
            if good:
                self.rule = min(good, key=lambda n: (self.rules[n]['repressive'], -self.rules[n]['active'],
                                                     rule_misses[n]))
                self.log(index, ep, 'math rule kept',
                         f"{self.rule}, after {self.rules[self.rule]['active']} right guesses")

    # ----- surprise that will not go away grows a new law -----
    def watch(self, ratio, samples, ep, index):
        surprising = ratio > SURPRISE
        self.window = (self.window + [surprising])[-WINDOW:]
        if surprising:
            z = torch.cat([s[0] for s in samples])
            a = torch.cat([s[1] for s in samples])
            self.surprises.append((index, z, a))
        # Only the surprises behind the current alarm, not old one-offs.
        self.surprises = [s for s in self.surprises if s[0] > index - WINDOW]
        if self.cooldown:
            self.cooldown -= 1
            return
        if self.candidate is not None or sum(self.window) < PERSISTENT:
            return
        if self.mode == 'frozen_laws' and ep['scene'] != 'body':
            return
        self.proposals += 1
        law, how = grow([(z, a) for _, z, a in self.surprises], self.laws, f'proposal {self.proposals}',
                        ep['scene'], seed=self.seed * 1000 + index, mask=self.usable(ep['scene'], self.laws))
        self.log(index, ep, 'new law proposed',
                 {'proposal': self.proposals, 'surprising_situations': len(self.surprises), **how})
        self.window, self.surprises = [], []
        if self.mode == 'ungated':
            law.name = f'law {len(self.laws) + 1}'
            self.laws.append(law)
            self.log(index, ep, 'law kept for life', f'{law.name}, without checking')
        else:
            self.candidate = {'law': law, 'active': 0, 'repressive': 0, 'tested': 0}

    def judge_candidate(self, miss_with, miss_without, surprise_with, surprise_without, index, ep):
        """A proposed law passes a check when, with it, the surprise goes away
        and the unseen push is guessed better. Where nothing was surprising, it
        only must not make the guess worse."""
        c = self.candidate
        c['tested'] += 1
        if surprise_without < SURPRISE:
            if miss_with > 1.05 * miss_without + 0.005:
                c['repressive'] += 1
        elif surprise_with < SURPRISE and miss_with < miss_without:
            c['active'] += 1
        else:
            c['repressive'] += 1
        if c['active'] >= 3 and c['repressive'] <= 1:
            law = c['law']
            law.name = f'law {len(self.laws) + 1}'
            self.laws.append(law)
            self.candidate = None
            # Old surprises were measured without this law; start watching afresh.
            self.window, self.surprises = [], []
            self.log(index, ep, 'law kept for life', f"{law.name}, after {c['active']} passed checks")
        elif c['repressive'] >= 3 or c['tested'] >= 12:
            self.candidate = None
            self.cooldown = 4
            self.log(index, ep, 'proposed law rejected',
                     f"{c['active']} checks passed, {c['repressive']} failed")


SHAPES = {
    'push command (the hand)': lambda z: np.tanh(1.6 * z[:, 2]),
    'speed (rubbing)': lambda z: z[:, 1],
    'speed squared (water drag)': lambda z: z[:, 1] * np.abs(z[:, 1]),
    'position (spring)': lambda z: z[:, 0],
}


def describe_law(law, older, rng):
    """For the report only: which known shape the new part of a learned law
    most resembles, after taking away what the older laws it can use already
    cover. If they already cover every known shape, the whole law is compared
    instead. The learner never sees these shapes."""
    z = law.mu.numpy() + law.sd.numpy() * rng.uniform(-1.5, 1.5, size=(4000, 3))
    zt = torch.from_numpy(z)
    with torch.no_grad():
        y = law(zt).numpy()
        old = design(older, zt).numpy()

    def correlations(basis):
        def left(values):
            return values - basis @ np.linalg.lstsq(basis, values, rcond=None)[0]
        fresh, scores = left(y), []
        for name, shape in SHAPES.items():
            values = shape(z)
            rest = left(values)
            if np.linalg.norm(rest) < 0.05 * np.linalg.norm(values - values.mean()):
                continue    # the older laws already cover this shape
            scores.append((abs(float(np.corrcoef(fresh, rest)[0, 1])), name))
        return sorted(scores, reverse=True)

    judged = 'new part'
    scores = correlations(np.column_stack((np.ones(len(z)), old)))
    if not scores:
        judged = 'whole law (older laws already cover every known shape)'
        scores = correlations(np.ones((len(z), 1)))
    second = scores[1] if len(scores) > 1 else (None, None)
    return {'depends_on': [('position', 'speed', 'push')[i] for i in law.inputs], 'judged': judged,
            'best': scores[0][1], 'score': scores[0][0], 'second': second[1], 'second_score': second[0]}
