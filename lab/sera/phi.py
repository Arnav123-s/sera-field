"""Phi, SERA's one Field (plan revision 6; docs/SERA_FIELD_THEORY.md v1.1, built as one object).

The author, 2026-09-27:
- "one SERA, the whole Field - all the parts become or dissolve into the Field"; "one mind that's adaptive, not modules
  of each separate field or task";
- "not belief, understanding"; "understanding, laws and beliefs intertwined in superposition, understanding the
  heaviest, then equal weight on laws and beliefs, and they all influence each other";
- "do not give it a predefined set of words, sentences, formulas - teach it, let it learn and use them on its own";
- "the loop must be adaptive - SERA chooses how the loop functions - a superposition of its current loop, part of the
  entire Field, not a separate entity";
- "it should learn and discover from its imagination: when something it did not expect works for something else, or a
  rival makes sense in a different scenario, pursue it, understand it, learn it" (light as wave and particle).

What the Field holds (one object, saved whole after every task; every part bounded):
- concepts      its inventions, in every subject, in order (append-only, hash-chained): a function of its language
                (sera.lang) - an expression, or a table of values it shaped from measurements - with where it came
                from, its words and how often reuse paid.
- understood    the explanations of past tasks: the kind of task, context, the hypothesis, its parts, proven or only
                believed, where it held.
- standing      proofs and refutations of each hypothesis.
- lexicon       what its words mean to it (sera.talk; learned, never given).
- loop          how it acts: a superposition of ways to run its own loop (LoopField below), part of the Field and
                weighed like everything else.
- possibilities what it imagined or set aside (rivals it did not choose, compositions it dreamed), kept to be
                recognized when they fit somewhere else (serendipity).
- links         the times something from one task explained another; questions it holds (dualities: two different
                explanations that both work); the inbox (what it asks us).

The three layers over the hypotheses h of any task (laws, programs, rules, and ways to act):
  U(h | c)   understanding: how well h fits what it understood in contexts like c - each part's familiarity (how often
             the part explained a task like this) and each pair's (parts that explained tasks together); its own
             concepts count as parts, so a law made of understood parts is understood before it is ever met.
  L(h)       laws: h's own standing, context-free - its description length in its own language (sera.lang.bits),
             times (1 + proofs) / (1 + refutations).
  B(h | D)   beliefs: what this task's evidence says (and the words it heard, through its lexicon).
  log Phi(h) = W_U log U + W_L log L + W_B log B, normalized: a logarithmic opinion pool (Genest and Zidek 1986),
  weights 0.5, 0.25, 0.25 (the author's order; the numbers are to measure).
They move each other: Phi chooses what it weighs and what it asks or does; a proof becomes understanding and standing;
evidence against understanding lowers it; an invention changes the language itself (L) and becomes a part (U).
Curiosity is where the layers disagree: the tension KL(B || U).

The judge of each world (its certificate, audit or check) reads only that world's evidence: nothing here enters a proof.
"""
import hashlib
import json
import math
import pickle
import time
import uuid
from collections import deque

import numpy as np

from . import talk as TK

W_U, W_L, W_B = 0.5, 0.25, 0.25
ETA = 0.1                        # the floor: never unthinkable
N_UNDERSTOOD = 1024
N_POSSIBLE = 96
PAIR_POWER = 0.5
V_DONE = 20.0                    # nats: what finishing a task (a proof) is worth


def normalize(logp):
    if not logp:
        return {}
    vals = np.array(list(logp.values()), float)
    top = np.logaddexp.reduce(vals)
    if not np.isfinite(top):
        n = len(logp)
        return {h: -math.log(n) for h in logp}
    return {h: v - top for h, v in logp.items()}


def pool(logU, logL, logB):
    """log Phi = W_U log U + W_L log L + W_B log B over the hypotheses B speaks for, normalized."""
    return normalize({h: W_U * logU.get(h, -700.0) + W_L * logL.get(h, -700.0) + W_B * b for h, b in logB.items()})


def kl(logp, logq):
    out = 0.0
    for h, lp in logp.items():
        if lp == -math.inf:
            continue
        out += math.exp(lp) * (lp - max(logq.get(h, -700.0), -700.0))
    return max(out, 0.0)


def _chain(prev, body):
    return hashlib.sha256((prev + json.dumps(body, sort_keys=True, default=str)).encode()).hexdigest()[:16]


# --- the loop, as part of the Field ---
FACULTIES = ('ask', 'explore', 'convince', 'grow', 'imagine', 'prove', 'leave')    # convince: revision 7
LEGACY_MOMENT = ('bias', 'doubt', 'tension', 'level', 'proven', 'misfit', 'steps', 'stuck', 'tie', 'teaching')
LEGACY_FEATURES = LEGACY_MOMENT + tuple('est_' + f for f in FACULTIES)
MOMENT = LEGACY_MOMENT + ('shown',)  # log1p of pushes since an actual judge report
FEATURES = MOMENT + tuple('est_' + f for f in FACULTIES)        # every faculty sees every faculty's estimate
MAX_AT_ONCE = 3
TAUGHT_Y = 1.0                  # the return a taught way of working is credited with (and -TAUGHT_Y the others)
TAUGHT_FADE = 0.85              # per task: what it was taught about working fades as its own evidence grows


class LoopField:
    """How SERA works, held as a superposition inside the Field (the author: "the loop itself must be a superposed part
    of the entire Field, not a separate entity"; "it is not a loop but a superposed behaviour: each part can interact
    with or jump across the entire loop; SERA can do several parts at once, make one step include another, or design
    the whole configuration for what it is doing - learning or answering; we teach it at first, then it does it on its
    own").

    Its faculties - ask (a push or a question that tells its ideas apart), explore (go where nothing is known), grow
    (think bigger thoughts), imagine (recall what it set aside elsewhere and compose what it knows), prove (ask the
    judge), leave - are not steps in an order. For each faculty f a Gaussian over weights w_f says how much every
    feature of the moment predicts what f returns per second, and the features include every other faculty's own
    estimate: so each faculty's worth depends on all the others (grow is worth more when asking has nothing left to
    tell; exploring after a proof; proving while asking). At each moment it draws one way of working from the pooled
    superposition (Thompson sampling, Thompson 1933) and does, together, every faculty that way values above nothing
    (at most MAX_AT_ONCE, the most valued first, each seeing what the others just did); one push serves every
    faculty in the configuration that wants a push, by their values. The outcome is evidence for every way at once
    (Bayesian linear regression), per faculty. The layers are the Field's own:
      U  its understanding of its own working in tasks of this kind (what it was taught about working, fading, and what
         its own working returned),
      L  the loop's law: the simplest way (trust each faculty's own estimate, nothing else),
      B  this task's evidence;
    pooled like any hypotheses. No order of steps is written anywhere; the teacher's way enters only as evidence."""

    def __init__(self, noise=1.0, prior=1.0):
        self.feature_names = self.active_features()
        self.feature_schema = 2
        self.d = len(self.feature_names)
        self.noise, self.prior = noise, prior
        self.kinds = {}                  # kind of task -> faculty -> [A, b]: its own working (understanding)
        self.taught = {}                 # kind of task -> faculty -> [A, b]: the teacher's way (fading)
        self.task = {}                   # this task: faculty -> [A, b]
        self.configs = {}                # kind -> {configuration: times}: how it has chosen to work

    @staticmethod
    def active_features():
        from . import crutches as CR
        return FEATURES if CR.on('teach_rechecking') else LEGACY_FEATURES

    def saved_features(self):
        names = getattr(self, 'feature_names', None)
        if names is None:
            if self.d != len(LEGACY_FEATURES):
                raise ValueError('unnamed LoopField schema has an unknown dimension')
            names = LEGACY_FEATURES
        if (len(names) != self.d or len(set(names)) != len(names)
                or not set(LEGACY_FEATURES) <= set(names)):
            raise ValueError('invalid LoopField feature schema')
        return tuple(names)

    @staticmethod
    def remap_vector(vector, old, new):
        if np.shape(vector) != (len(old),):
            raise ValueError('LoopField vector/schema mismatch')
        out = np.zeros(len(new))
        for j, name in enumerate(new):
            if name in old:
                out[j] = vector[old.index(name)]
        return out

    def migrate_features(self, names=None):
        """Map sufficient statistics by name, including all precision cross-terms.
        New coordinates have zero evidence; _prior supplies the existing finite variance.
        Defaults keep the legacy dimension, preserving its RNG draws and choices."""
        old = self.saved_features()
        # Turning the switch off must not erase evidence from a previously expanded
        # saved Field. Fresh/default and pre-S24 Fields still use the legacy dimension.
        active = self.active_features()
        new = tuple((FEATURES if active == FEATURES else old) if names is None else names)
        if len(set(new)) != len(new) or not set(LEGACY_FEATURES) <= set(new):
            raise ValueError('invalid target LoopField schema')
        pending = []
        for rows in list(self.kinds.values()) + list(self.taught.values()) + [self.task]:
            for faculty, (A, b) in rows.items():
                if np.shape(A) != (len(old), len(old)):
                    raise ValueError('LoopField matrix/schema mismatch')
                mapped = np.zeros((len(new), len(new)))
                pairs = [(j, old.index(name)) for j, name in enumerate(new) if name in old]
                for j, i in pairs:
                    for k, h in pairs:
                        mapped[j, k] = A[i, h]
                pending.append((rows, faculty, [mapped, self.remap_vector(b, old, new)]))
        for rows, faculty, stats in pending:
            rows[faculty] = stats
        self.feature_names, self.feature_schema, self.d = new, 2, len(new)
        return old, new

    def features(self, moment, estimates, faculty):
        return np.asarray([1.0 if k == 'bias' else float(estimates.get(k[4:], 0.0))
                           if k.startswith('est_') else float(moment.get(k, 0.0))
                           for k in self.feature_names], float)

    def _prior(self, faculty):
        A = np.eye(self.d) / self.prior ** 2
        m = np.zeros(self.d)
        m[self.feature_names.index('est_' + faculty)] = 1.0       # trust your own estimate
        return A, A @ m

    def posterior(self, kind, faculty):
        z = (np.zeros((self.d, self.d)), np.zeros(self.d))
        A0, b0 = self._prior(faculty)
        Au, bu = self.kinds.get(kind, {}).get(faculty, z)
        At, bt = self.taught.get(kind, {}).get(faculty, z)
        Ab, bb = self.task.get(faculty, z)
        A = W_L * A0 + W_U * (Au + At) + W_B * Ab + 1e-9 * np.eye(self.d)
        b = W_L * b0 + W_U * (bu + bt) + W_B * bb
        cov = np.linalg.inv(A)
        return cov @ b, cov

    def choose(self, kind, moment, estimates, available, rng):
        """The configuration it works in now: [faculty ...] (most valued first) and {faculty: (drawn, mean) value}."""
        vals = {}
        for f in FACULTIES:
            if f not in available:
                continue
            x = self.features(moment, estimates, f)
            m, cov = self.posterior(kind, f)
            w = rng.multivariate_normal(m, (cov + cov.T) / 2)
            vals[f] = (float(w @ x), float(m @ x))
        order = sorted(vals, key=lambda f: (-vals[f][0], f))
        config = [f for f in order if vals[f][0] > 0][:MAX_AT_ONCE] or order[:1]
        if 'leave' in config and config[0] != 'leave':
            config.remove('leave')                                  # leaving ends the task: only if it leads
        if config and config[0] == 'leave':
            config = ['leave']
        key = '+'.join(sorted(config))
        self.configs.setdefault(kind, {})[key] = self.configs.setdefault(kind, {}).get(key, 0) + 1
        return config, vals

    def learn(self, faculty, x, y, weight=1.0):
        """One return y at features x; `weight` (0-1) how much this evidence counts (a faint trace counts faintly -
        S05 F6, reviewer: a faint echo taken at full weight shrank what it had learned)."""
        A, b = self.task.setdefault(faculty, [np.zeros((self.d, self.d)), np.zeros(self.d)])
        A += weight * np.outer(x, x) / self.noise ** 2
        b += weight * x * float(y) / self.noise ** 2

    def teach(self, kind, moment, estimates, available, shown):
        """The teacher shows how it would work here (the faculties `shown`): evidence, in its understanding of this
        kind of task, that those return TAUGHT_Y and the others -TAUGHT_Y. It fades task by task."""
        mine = self.taught.setdefault(kind, {})
        for f in available:
            x = self.features(moment, estimates, f)
            A, b = mine.setdefault(f, [np.zeros((self.d, self.d)), np.zeros(self.d)])
            A += np.outer(x, x) / self.noise ** 2
            b += x * (TAUGHT_Y if f in shown else -TAUGHT_Y) / self.noise ** 2

    def end_task(self, kind, fade=0.98):
        mine = self.kinds.setdefault(kind, {})
        for f in mine:
            mine[f][0] *= fade
            mine[f][1] *= fade
        for f in self.taught.get(kind, {}):
            self.taught[kind][f][0] *= TAUGHT_FADE
            self.taught[kind][f][1] *= TAUGHT_FADE
        for f, (A, b) in self.task.items():
            if f not in mine:
                mine[f] = [np.zeros((self.d, self.d)), np.zeros(self.d)]
            mine[f][0] += A
            mine[f][1] += b
        self.task = {}

    def habits(self, kind):
        """How it believes it should work in tasks of this kind: each faculty's mean weights on the moment's features."""
        return {f: {k: v for k, v in zip(self.feature_names, np.round(self.posterior(kind, f)[0], 3).tolist()) if abs(v) >= 0.05}
                for f in FACULTIES}


MOVES = ('recall', 'compose', 'keep', 'closer', 'dimension', 'question',       # innate moves of imagination: the
         'drop', 'swap', 'refine', 'blend', 'wish', 'step')                       # big ones, small edits of an idea,
                                                                                 # wishing for an ability it lacks (it builds
                                                                                 # it and uses it: 2026-09-28), and taking
                                                                                 # one small step, then the rest (2026-09-29)
METHOD_MAX = 3                  # moves in a method it draws (a named method counts as one: methods of methods)
METHOD_PRIOR = 2.0              # nats a method nobody has tried is expected to return
METHOD_AT_ONCE = 2              # methods it may run together at one moment
TRIGGERS = ('bias', 'doubt', 'misfit', 'short', 'level', 'tension', 'stuck', 'curve', 'proven')


class MethodField:
    """How SERA imagines, held in the Field as a superposition (plan revision 7; the author: "teach it the methods of
    imagination and let it develop its own; keep the imagination unbounded"; "let it make its own moves, as a
    superposition that can be triggered or influenced however SERA wants").

    A method is a chain of moves - each move's new thoughts are the next move's focus - or of methods it named; a
    method it names is a move of its own from then on (usable and chainable like the innate ones). Every method it can
    form now is held at once - every move, every pair of moves, every method it named and each of those followed by a
    move - and what each is worth is a function of the moment (its triggers: doubt, misfit, the judge finding it short,
    how far it has grown, tension, being stuck, holding a drawn curve, being proven): for each kind of task and method a
    Gaussian over those weights, from what the method returned (nats of doubt removed) and what the teacher showed
    (taught evidence, fading), like the loop's. It draws from the superposition (Thompson sampling) and runs, together,
    the methods it values above nothing (at most METHOD_AT_ONCE). A method whose thoughts end in a proof is named."""

    def __init__(self, noise=4.0, prior=2.0):
        self.d = len(TRIGGERS)
        self.noise, self.prior = noise, prior
        self.stats = {}                  # (kind, method) -> [A, b]: its own evidence
        self.taught = {}                 # (kind, method) -> [A, b]: the teacher's, fading
        self.named = []                  # its own methods (its own moves): {'id', 'method', 'moves', 'born', 'uses'}

    @staticmethod
    def features(moment):
        return np.asarray([1.0] + [float(moment.get(k, 0.0)) for k in TRIGGERS[1:]], float)

    def candidates(self):
        own = ['#' + str(n['id']) for n in self.named]
        out = [(m,) for m in MOVES + tuple(own)] + [(a, b) for a in MOVES for b in MOVES if a != b]
        out += [(o, m) for o in own for m in MOVES] + [(m, o) for o in own for m in MOVES]
        return list(dict.fromkeys(out))

    def expand(self, method):
        """A method as the moves it runs (named methods unfolded), at most 2 * METHOD_MAX moves."""
        out = []
        for step in method:
            if step.startswith('#'):
                n = next((x for x in self.named if x['id'] == int(step[1:])), None)
                out += list(n['moves']) if n else []
            else:
                out.append(step)
        return tuple(out[:2 * METHOD_MAX])

    def _post(self, kind, method):
        z = (np.zeros((self.d, self.d)), np.zeros(self.d))
        A0 = np.eye(self.d) / self.prior ** 2
        m0 = np.zeros(self.d)
        m0[0] = METHOD_PRIOR
        As, bs = self.stats.get((kind, method), z)
        At, bt = self.taught.get((kind, method), z)
        A = A0 + As + At
        cov = np.linalg.inv(A)
        return cov @ (A0 @ m0 + bs + bt), cov

    def _usable(self, m, moves):
        ex = self.expand(m)
        return bool(ex) and set(ex) <= moves

    def value(self, kind, moves, moment):
        """The best expected return, now, over the methods it can run (the loop's estimate of 'imagine')."""
        x = self.features(moment)
        return max((float(self._post(kind, m)[0] @ x) for m in self.candidates() if self._usable(m, moves)),
                   default=0.0)

    def choose(self, kind, moves, moment, rng):
        """The methods it runs now: a draw from the superposition, the ones valued above nothing (the best if none)."""
        x = self.features(moment)
        draws = []
        for m in self.candidates():
            if not self._usable(m, moves):
                continue
            mean, cov = self._post(kind, m)
            w = rng.multivariate_normal(mean, (cov + cov.T) / 2)
            draws.append((float(w @ x), m))
        draws.sort(key=lambda t: (-t[0], t[1]))
        pick = [m for v, m in draws if v > 0][:METHOD_AT_ONCE] or [m for _, m in draws[:1]]
        return pick

    def learn(self, kind, method, moment, y, weight=1.0):
        x = self.features(moment)
        A, b = self.stats.setdefault((kind, method), [np.zeros((self.d, self.d)), np.zeros(self.d)])
        A += weight * np.outer(x, x) / self.noise ** 2
        b += weight * x * float(y) / self.noise ** 2

    def teach(self, kind, method, moment, y=6.0):
        x = self.features(moment)
        A, b = self.taught.setdefault((kind, method), [np.zeros((self.d, self.d)), np.zeros(self.d)])
        A += np.outer(x, x) / self.noise ** 2
        b += x * float(y) / self.noise ** 2

    def end_task(self):
        for v in self.taught.values():
            v[0] *= TAUGHT_FADE
            v[1] *= TAUGHT_FADE

    def name(self, method, task):
        """A method whose thoughts ended in a proof becomes a move of its own (once); returns its id or None."""
        moves = self.expand(method)
        if len(moves) < 2:
            return None
        for n in self.named:
            if n['moves'] == moves:
                n['uses'] += 1
                return None
        nid = len(self.named) + 1
        self.named.append(dict(id=nid, method=tuple(method), moves=moves, born=task, uses=1))
        return nid

    def triggers(self, kind, method):
        """What triggers a method, as it has learned it: its mean weight on each feature of the moment."""
        return {k: round(float(v), 2) for k, v in zip(TRIGGERS, self._post(kind, method)[0]) if abs(v) >= 0.05}


IDEA_DIM = 2048                  # the Field's dimensions: every thing's identity and state (2026-09-29 night, the author:
#                                  "memory, understanding and belief are not separate ... the whole field is the memory,
#                                  like an automatic trigger"): what it read is laid into the states of the things in
#                                  it, superposed; nothing is kept as a record, and what comes to mind is what the
#                                  Field rings back (holographic memory: Plate's HRR, BEAGLE, Kanerva's SDM)
IDEA_KEEP = 0.75                 # a thing's state the next time it is met: what it held stays this much (the newest
#                                  counts most; a thing met again and again keeps a gist: interference, not time; at 0.9
#                                  the newest led by less than the noise of 2,048 dimensions). A knob to learn.
FIELD_ECHO = True                # the echo and the automatic trigger (False: the Field as before, for comparison)
TRACE_KEEP = 0.8                 # an eligibility trace, one moment of thinking later (e-prop): what took part fades
TRACE_FLOOR = 0.01               # a trace this faint is gone
IDEA_END = '<the end>'           # the end of a sentence, laid in after its last thing (its own identity)
IDEA_PLACES = 64                 # places in a sentence the Field holds (its language's lists hold as many: lang.MAX_LEN)
IDEA_RECORDS = False             # the old way, for comparison only: each thing's last IDEA_MEMORY sentences as records,
#                                  looked up by comes_to_mind (a separate store: what the author asked to end)
IDEA_MEMORY = 64                 # situations an idea remembers (the oldest let go first)
IDEA_DECAY = 0.5                 # what it read long ago fades a little: a reading n sentences ago counts (1 + n)^-0.5
#                                  (the power law of forgetting, ACT-R's base-level decay; 2026-09-29: 0.999^n erased a
#                                  whole book read 13,000 sentences earlier - 2e-6 - which was not "a little"). A knob
#                                  to learn.
IDEA_MIND = 0.5                  # a memory comes to mind if at least this share of the most one thing can tell
#                                  (log(1 + sentences read)): a thing alone brings memories only if it is in fewer than
#                                  1/sqrt(N) of the N sentences read ('is' is not; a name is). A knob to learn.


def _add(d, k, w=1.0):
    d[k] = d.get(k, 0.0) + w


def _cos(a, b):
    num = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return num / (na * nb) if na > 0 and nb > 0 else 0.0


class Ideas:
    """Ideas of things (2026-09-29, the author: "today SERA understands procedures, not things ... I want the field to
    UNDERSTAND what it really is too ... show sera a few examples in sentences of a kitchen or activities going on in a
    kitchen and see if sera has an idea of a kitchen; it can dream and know what a kitchen is; it doesn't have to be
    accurate"). One idea for every thing it meets - a word in what it reads (and, later, an object on a rail or a
    colour in a puzzle): where the thing has been (the situations it read it in), what came just before and after it,
    where in a sentence it stood, what kept it company (the whole sentence), and what its own abilities said of it (a
    role: 'where' answered kitchen - so a kitchen is a thing 'where' gives). Nothing about any thing is given: every
    idea is what it read and what its own abilities saw.
    - Likeness: two things are alike when they stand alike - the same roles, the same neighbours before and after, the
      same places in a sentence - so a word read once ('pantry') already has a rough idea, from what it is like.
    - Company counts by how rare it is in what it has read (the dictionary's way): 'the' and 'in' keep company with
      everything and so tell nothing; no list of little words.
    - What goes on with a thing is its company, grouped by likeness (the doings, the stuff, the people).
    - A dream is a sentence it never read: a situation of a thing like this one, with this one in its place - a guess
      from likeness, as sure as the likeness, that reading may later confirm or correct."""

    def __init__(self):
        self.of = {}                     # thing -> its idea
        self.read_n = 0                  # sentences read
        self.gen = uuid.uuid4().hex      # its own name, unique across runs (a perception cache's key)
        self.rev = 0                     # how many times its memory has changed (reading, an idea laid in, the echo)
        self._field_state()

    def __getstate__(self):
        d = dict(self.__dict__)
        d.pop('_memo', None)
        d.pop('_memo_at', None)
        d.pop('_came', None)             # what came to mind in a world is not kept (S05 F8, reviewer)
        if '_E' in d:                    # the Field's rows in use, not the room kept for growth
            d['_E'], d['_M'] = d['_E'][:d['_n']].copy(), d['_M'][:d['_n']].copy()
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self._field_state()              # a SERA saved before the Field held its memory: laid in now

    # --- the Field state: every thing's identity and what it holds (2026-09-29 night) ---
    def _field_state(self):
        """The identities and states, made once (and, for a SERA saved before, from what it had read: each of its
        remembered sentences laid in, in the order it read them, so nothing it read is lost)."""
        if getattr(self, '_E', None) is not None:
            return
        self._row, self._n = {}, 0
        self._E = np.zeros((0, IDEA_DIM), np.int8)
        self._M = np.zeros((0, IDEA_DIM), np.float32)
        old = sorted({(at, sent) for d in self.of.values() for sent, _, _, at in d.get('situations', ())},
                     key=lambda t: (t[0], repr(t[1])))
        for _, sent in old:
            self._lay_in(sent)
        if not IDEA_RECORDS:
            for d in self.of.values():
                d.pop('situations', None)

    def _at(self, s):
        """The thing's row in the Field (its identity made on first meeting: random, from its name, the same in every
        run)."""
        s = getattr(self, '_aliases', {}).get(s, s)
        r = self._row.get(s)
        if r is None:
            r = self._row[s] = self._n
            if r >= len(self._E):
                cap = max(1024, 2 * len(self._E))
                E = np.zeros((cap, IDEA_DIM), np.int8)
                M = np.zeros((cap, IDEA_DIM), np.float32)
                E[:self._n], M[:self._n] = self._E[:self._n], self._M[:self._n]
                self._E, self._M = E, M
            g = np.random.default_rng(int.from_bytes(hashlib.blake2b(repr(s).encode('utf-8'), digest_size=8).digest(),
                                                     'little'))    # 64 bits: two things never share an identity
            self._E[r] = (g.integers(0, 2, IDEA_DIM) * 2 - 1).astype(np.int8)
            self._n += 1
        return r

    def _hologram(self, sentence):
        """A sentence as one pattern: each thing's identity in its place (a place is a rotation), superposed; unit
        size per thing, so a long sentence weighs no more than a short one. Its end is laid in too, after its last
        thing (a memory knows where it ends: 'zork swam home' ran on into an older sentence's 'blue fish')."""
        sentence = tuple(sentence)[:IDEA_PLACES - 1] + (IDEA_END,)
        h = np.zeros(IDEA_DIM, np.float32)
        for i, s in enumerate(sentence):
            r = self._at(s)                              # first: meeting a thing may enlarge the Field
            h += np.roll(self._E[r], i + 1)
        return h / np.float32(math.sqrt(IDEA_DIM) * math.sqrt(len(sentence)))

    def _lay_in(self, sentence):
        """What it reads changes what each thing in it holds: the sentence laid in on top (what was there stays
        IDEA_KEEP as much)."""
        if not sentence:
            return
        h = self._hologram(sentence)
        for s in dict.fromkeys(sentence):
            r = self._at(s)
            self._M[r] *= np.float32(IDEA_KEEP)
            self._M[r] += h

    def _ring(self, weights, most=8):
        """What the Field rings back when some things are pressed on it (each as hard as its weight): the states
        superposed, read place by place against the identities of what they have been with; the loudest sentence
        first, then what rings when it is taken away, and so on. Sentences reconstructed, never looked up."""
        r = np.zeros(IDEA_DIM, np.float32)
        near = set()
        for s, w in weights:
            r += np.float32(w) * self._M[self._row[s]]
            near.add(s)
            near.update(self.of[s]['company'])
        cand = sorted(near, key=repr) + [IDEA_END]
        if not np.any(r):
            return []
        end = len(cand) - 1
        E = self._E[[self._at(o) for o in cand]].astype(np.float32) / np.float32(math.sqrt(IDEA_DIM))
        sure = math.sqrt(2.0 * math.log(len(cand) + 1.0)) + 1.5      # above the loudest noise among the candidates
        out, first = [], None
        for _ in range(most):
            V = np.stack([np.roll(r, -(i + 1)) for i in range(IDEA_PLACES)])
            S = V @ E.T
            best = S.argmax(1)
            top = S[np.arange(IDEA_PLACES), best]
            noise = float(np.linalg.norm(r)) / math.sqrt(IDEA_DIM)
            n = 0                                               # up to its end (or where nothing rings any more)
            while n < IDEA_PLACES and top[n] > sure * noise and int(best[n]) != end:
                n += 1
            if n == 0:
                break
            sent = tuple(cand[int(best[i])] for i in range(n))
            h = self._hologram(sent)
            beta = float(top[:n].min()) * math.sqrt(n + 1)          # how loudly it rang: the amount every one of
            #   its places supports (its softest place). Not a least-squares projection (S05 F2, reviewer, suggested one):
            #   a projection gives this memory the places it shares with others ("mira went to the ...") and took
            #   the older memory away with it (2026-09-29); shared places always ring louder, so the softest place
            #   is this memory's own amount - a bound, not a fit.
            if first is None:
                first = beta
            if beta < 0.1 * first:
                break
            if sent not in out:
                out.append(sent)
            r = r - np.float32(beta) * h
        return out

    # --- the echo's side in memory (2026-09-29 night; the author's HEB + e-prop, adapted) ---
    def bind(self, thing, key, amount):
        """Lay something (an idea it proved: ('concept', id)) into what a thing holds, in its own place (unrotated:
        sentences sit in rotated places), as strongly as `amount`: next time the thing is pressed, it rings back."""
        if not amount:
            return
        self._idea(thing)                                # a word met only in a question is a thing of the Field too
        self._at(thing)
        k = self._at(key)                                # first: meeting a thing may enlarge the Field
        self._M[self._row[thing]] += np.float32(amount / math.sqrt(IDEA_DIM)) * self._E[k].astype(np.float32)
        self.rev = getattr(self, 'rev', 0) + 1           # its memory changed: perception sees it anew (S05 F1, reviewer)

    def bound(self, thing, key):
        """How strongly a key is laid into a thing now (what bind put there, read back; what else the thing holds
        adds a little noise)."""
        key = getattr(self, '_aliases', {}).get(key, key)
        if thing not in self._row or key not in self._row:
            return 0.0
        e = self._E[self._row[key]].astype(np.float32)
        return float(e @ self._M[self._row[thing]].astype(np.float32)) / math.sqrt(IDEA_DIM)

    def signed(self, thing, key):
        """(how strongly a key is laid into a thing, signed; the noise of reading that thing's state: its size over
        the square root of the dimensions) - a signed record kept in the Field (review 12 F3)."""
        key = getattr(self, '_aliases', {}).get(key, key)
        if thing not in self._row or key not in self._row:
            return 0.0, 0.0
        m = self._M[self._row[thing]].astype(np.float64)
        return self.bound(thing, key), float(np.linalg.norm(m)) / math.sqrt(IDEA_DIM)

    def identities(self, kinds):
        """The Field's own identities whose name is (kind, ...) for a kind in `kinds`, in the order they were met: what
        ringing is read against (the clean-up memory; review 12 F6: nothing about a situation is kept with them)."""
        return list(self.iter_identities(kinds))

    def iter_identities(self, kinds, deadline=None):
        aliases = getattr(self, '_aliases', {})
        for k in self._row:                              # insertion order, without a full-memory list allocation
            if deadline is not None and time.time() >= deadline:
                return
            if isinstance(k, tuple) and len(k) == 2 and k[0] in kinds and k not in aliases:
                yield k

    def redirect(self, mapping, deadline=None):
        """Rename executable identities, keeping the oldest vector; merge already-written alias components.

        Old checkpoints have no bind ledger. Transfer the projection onto the aliases' joint vector subspace,
        leaving its orthogonal residual intact. A single renamed identity keeps its vector exactly. Row chunks
        bound the temporary matrix. Redirects and the retained vectors survive pickling.
        """
        aliases = self.__dict__.setdefault('_aliases', {})
        groups = {}
        for old, new in mapping.items():
            groups.setdefault(new, []).append(old)
        for new, old_keys in groups.items():
            if deadline is not None and time.time() >= deadline:
                return False
            keys = list(dict.fromkeys(old_keys + ([new] if new in self._row else [])))
            rows = sorted({self._row[k] for k in keys if k in self._row})
            if not rows:
                for old in keys:
                    if old != new:
                        aliases[old] = new                # future binds to an unseen duplicate also use its representative
                continue
            keep = rows[0]
            if len(rows) > 1:
                E = self._E[rows].astype(np.float64) / math.sqrt(IDEA_DIM)
                inverse = np.linalg.pinv(E @ E.T)
                staged = []
                for start in range(0, self._n, 256):
                    if deadline is not None and time.time() >= deadline:
                        return False                     # timed migrations commit only complete alias groups
                    stop = min(start + 256, self._n)
                    M = self._M[start:stop].astype(np.float64)
                    amounts = (M @ E.T) @ inverse
                    M += amounts.sum(axis=1)[:, None] * E[0] - amounts @ E
                    if deadline is None:
                        self._M[start:stop] = M.astype(np.float32)
                    else:
                        staged.append((start, stop, M.astype(np.float32)))
                if deadline is not None:
                    if time.time() >= deadline:
                        return False
                    for start, stop, M in staged:
                        self._M[start:stop] = M
            self._row[new] = keep
            for old in keys:
                self._row[old] = keep
                if old != new:
                    aliases[old] = new
            # Flatten older redirects as representatives acquire a concept name.
            for old, target in list(aliases.items()):
                if target in keys:
                    aliases[old] = new
                    self._row[old] = keep
            self.rev = getattr(self, 'rev', 0) + 1
        return True

    def evoked(self, things, keys, deadline=None, chunk_size=256, observe=None):
        """What a situation evokes (the automatic trigger): its things pressed on the Field, each as hard as it is rare,
        and how loudly each key rings back in the ideas' place - [(key, loudness)], loudest first, only above the
        noise of that many keys."""
        if deadline is not None and time.time() >= deadline:
            return []
        press = [(s, self._rare(s)) for s in sorted(set(things), key=repr) if s in self.of and s in self._row]
        press = [(s, t) for s, t in press if t > 0]
        aliases = getattr(self, '_aliases', {})
        if deadline is None:
            keys = [k for k in keys if aliases.get(k, k) in self._row]
        if not press or not keys:
            return []
        r = np.zeros(IDEA_DIM, np.float32)
        for s, t in press:
            r += np.float32(t) * self._M[self._row[s]]
        if deadline is None:                             # unchanged legacy trigger and conversation arithmetic
            E = self._E[[self._row[aliases.get(k, k)] for k in keys]].astype(np.float32) / np.float32(math.sqrt(IDEA_DIM))
            loud = E @ r
        else:
            if chunk_size <= 0:
                raise ValueError('projection chunk_size must be positive')
            scores = []
            for start in range(0, len(keys), chunk_size):
                if time.time() >= deadline:
                    return []                            # cutoff policy: discard the entire unfinished trigger
                end = min(start + chunk_size, len(keys))
                chunk = [k for k in keys[start:end] if aliases.get(k, k) in self._row]
                if chunk:
                    E = self._E[[self._row[aliases.get(k, k)] for k in chunk]].astype(np.float32)
                    values = (E / np.float32(math.sqrt(IDEA_DIM))) @ r
                    scores.extend(zip(chunk, values))
            if time.time() >= deadline:
                return []
            keys = [k for k, _ in scores]
            loud = [v for _, v in scores]
        noise = float(np.linalg.norm(r)) / math.sqrt(IDEA_DIM)
        sure = (math.sqrt(2.0 * math.log(len(keys) + 1.0)) + 1.5) * noise
        if observe is not None:
            # Observer receives the very projections used below; no second read or changed decoder.
            observe([(k, float(v)) for k, v in zip(keys, loud)], noise, sure)
        out = [(k, float(v)) for k, v in zip(keys, loud) if v > sure]
        return sorted(out, key=lambda kv: (-kv[1], repr(kv[0])))

    def came(self, pressed, sentences):
        """What came to mind in this world, and through which of its things - each thing's own trace (e-prop), so a
        memory brought by two things credits both (S05 F5, reviewer: the last cue took all of it)."""
        came = self.__dict__.setdefault('_came', {})
        for sent in sentences:
            cues = came.setdefault(sent, {})
            for s in pressed:
                cues[s] = cues.get(s, 0.0) + 1.0

    def fade(self, keep):
        for sent in list(getattr(self, '_came', {})):
            cues = {s: w * keep for s, w in self._came[sent].items() if w * keep >= 0.01}
            if cues:
                self._came[sent] = cues
            else:
                del self._came[sent]

    def forget_traces(self):
        self._came = {}

    def consolidate(self, signal, holds):
        """The echo in memory: a memory that came to mind and supports what was confirmed (holds(sentence, cues): the
        memory about an example's question, holding its answer in order) is laid in again into the things that
        brought it, each as strongly as signal x its own trace - what verified knowledge rests on is not worn away
        by what it reads next (the author's research: tag and capture, a verification signal). Spent once used."""
        n = 0
        for sent, cues in sorted(getattr(self, '_came', {}).items(), key=lambda kv: repr(kv[0])):
            if not holds(sent, cues):
                continue
            h = self._hologram(sent)
            for s, w in sorted(cues.items(), key=lambda kv: repr(kv[0])):
                if s in self._row and w > 0:
                    self._M[self._row[s]] += np.float32(signal * w) * h
            n += 1
        if n:
            self.rev = getattr(self, 'rev', 0) + 1       # what it perceives from now on is the changed Field
        self._came = {}
        return n

    def _known(self):
        """What it worked out from its ideas (how rare a thing is, how it stands, what goes on with it), kept until
        it reads or learns again (S03 F9, reviewer: thousands of things made every likeness recompute them all)."""
        at = (self.read_n, getattr(self, '_roles_n', 0), getattr(self, 'worlds_n', 0))
        if getattr(self, '_memo_at', None) != at:
            self._memo, self._memo_at = {}, at
        return self._memo

    def _idea(self, s):
        d = self.of.get(s)
        if d is None:
            d = self.of[s] = dict(seen=0.0, sentences=0.0, company={}, before={}, after={}, place={}, roles={})
            if IDEA_RECORDS:
                d['situations'] = deque(maxlen=IDEA_MEMORY)
        return d

    def read(self, sentence, source=''):
        """A sentence it reads (a tuple of things): laid into the Field - each thing in it holds it, superposed on what
        it held (no record is kept; the old way keeps one only when IDEA_RECORDS is set, for comparison)."""
        sentence = tuple(sentence)
        n = len(sentence)
        self.read_n += 1
        self.rev = getattr(self, 'rev', 0) + 1           # its memory changed: perception sees it anew
        for s in set(sentence):                           # in how many sentences it has been (not how many times)
            self._idea(s)['sentences'] = self._idea(s).get('sentences', 0.0) + 1
        self._lay_in(sentence)
        for i, s in enumerate(sentence):
            d = self._idea(s)
            d['seen'] += 1
            if 'situations' in d:
                d['situations'].append((sentence, i, source, self.read_n))
            _add(d['before'], sentence[i - 1] if i else '<start>')
            _add(d['after'], sentence[i + 1] if i + 1 < n else '<end>')
            _add(d['place'], 'first' if i == 0 else 'last' if i == n - 1 else 'inside')
            for j, o in enumerate(sentence):              # what goes on in the sentence is its company (the whole
                if j != i:                                # sentence: 2026-09-29, 'in' and 'the' beside 'kitchen'
                    _add(d['company'], o)                 # crowded out what was done there)

    def role(self, s, ability):
        """One of its abilities gave s here (its name for the ability: a word it learned, or one it coined)."""
        _add(self._idea(s)['roles'], ability)
        self._roles_n = getattr(self, '_roles_n', 0) + 1

    def _rare(self, o):
        """How much a thing tells by keeping company: rarer in what it has read tells more, and a thing in nearly
        every sentence ('the') tells nothing (2026-09-29: log(1 + N/seen) left 'the' and 'in' counting; the sentences
        it was in, not how many times: S03, reviewer)."""
        memo = self._known()
        r = memo.get(('rare', o))
        if r is None:
            d = self.of.get(o)
            if d is not None and 'worlds' in d:          # a perceived cue of a world (One Field, review 12 F1): how rare
                W = getattr(self, 'worlds_n', 0)         # among the worlds perceived so far, smoothed, so a newborn's
                r = memo[('rare', o)] = math.log((2.0 + W) / (1.0 + d['worlds']))   # second world still hears it
                return r
            df = (d.get('sentences', d['seen']) if d else 0.0)
            r = memo[('rare', o)] = max(0.0, math.log((1.0 + self.read_n) / (1.0 + df))) if self.read_n else 0.0
        return r

    def perceive_world(self, cues):
        """A world perceived through its cues (One Field, review 12 F1): each distinct cue counted once, so how rare it
        is among worlds is known (sentence rarity is untouched)."""
        self.worlds_n = getattr(self, 'worlds_n', 0) + 1
        for s in sorted(set(cues), key=repr):
            d = self._idea(s)
            d['worlds'] = d.get('worlds', 0) + 1
            self._at(s)

    def stance(self, s):
        """How a thing stands (not what it is with): its roles, neighbours before and after, and places, each part
        weighed by how rare the neighbour is."""
        memo = self._known()
        if ('stance', s) in memo:
            return memo[('stance', s)]
        d = self.of.get(s)
        out = {}
        if d is not None:
            tot = max(d['seen'], 1.0)
            for k, v in d['roles'].items():
                out[('role', k)] = 2.0 * v / tot
            for part in ('before', 'after'):
                for k, v in d[part].items():
                    out[(part, k)] = v / tot * (self._rare(k) if k in self.of else 1.0)
            for k, v in d['place'].items():
                out[('place', k)] = 0.5 * v / tot
        memo[('stance', s)] = out
        return out

    def _with(self, s):
        """What goes on with a thing (its company, each by how much it tells)."""
        memo = self._known()
        if ('with', s) not in memo:
            d = self.of.get(s)
            memo[('with', s)] = {o: v * self._rare(o) for o, v in d['company'].items()} if d else {}
        return memo[('with', s)]

    def _norm(self, part, s):
        memo = self._known()
        if (part, 'norm', s) not in memo:
            v = self.stance(s) if part == 'stance' else self._with(s)
            memo[(part, 'norm', s)] = math.sqrt(sum(x * x for x in v.values()))
        return memo[(part, 'norm', s)]

    def _like(self, part, a, b):
        va, vb = (self.stance(a), self.stance(b)) if part == 'stance' else (self._with(a), self._with(b))
        if len(vb) < len(va):
            va, vb = vb, va
        na, nb = self._norm(part, a), self._norm(part, b)
        return sum(v * vb.get(k, 0.0) for k, v in va.items()) / (na * nb) if na > 0 and nb > 0 else 0.0

    def alike(self, a, b):
        """Two things are alike when they stand alike and the same things go on with them (a kitchen and a pantry
        both keep bread; a throne keeps monarchs - 2026-09-29, where a word stood alone made kitchen like a throne).
        A score, not a certainty (S03, reviewer)."""
        return 0.5 * self._like('stance', a, b) + 0.5 * self._like('with', a, b)

    def kind(self, s, n=5):
        """The things most like s, with how alike (its idea of what kind of thing s is); every thing's vectors made
        once until it reads again, ties broken the same way every time (S03, reviewer)."""
        out = sorted(((self.alike(s, o), o) for o in self.of if o != s), key=lambda t: (-t[0], repr(t[1])))
        return [(o, round(v, 2)) for v, o in out[:n] if v > 0]

    def company(self, s, n=12):
        """What keeps it company, by how much it tells (rare company tells more)."""
        d = self.of.get(s)
        if d is None:
            return []
        out = sorted(((v * self._rare(o), o) for o, v in d['company'].items()), key=lambda t: (-t[0], repr(t[1])))
        return [(o, round(v, 2)) for v, o in out[:n] if v > 0]

    def goes_on(self, s, n=12, groups=3):
        """What goes on with a thing: its company, grouped by likeness (things that stand alike together)."""
        comp = [o for o, _ in self.company(s, n)]
        out = []
        for o in comp:
            for g in out:
                if self._like('stance', o, g[0]) >= 0.5:                # the doings with the doings, by how they stand
                    g.append(o)
                    break
            else:
                out.append([o])
        out.sort(key=len, reverse=True)
        return out[:groups]

    def comes_to_mind(self, things, most=8):
        """What comes to mind with some things: what the Field rings back when they are pressed on it (2026-09-29
        night, the author: "it doesn't need to know or learn or recall at all if the whole field is the memory; it's
        like an automatic trigger"). Each thing presses as hard as it is rare, and only a thing that tells at least
        IDEA_MIND of the most a single thing can tell (log(1 + sentences read)) presses at all - so a common word
        alone ('is') brings nothing to mind and a rare name does, however long ago it was read (the other things it
        read do not wear it away; only its own later sentences dilute it). The sentences come back reconstructed, the
        loudest first: a thing met once rings back its sentence exactly; a thing met in hundreds rings back a gist.
        The old way (IDEA_RECORDS, for comparison) looks through each thing's last sentences instead."""
        if not IDEA_RECORDS:
            floor = IDEA_MIND * math.log(1.0 + self.read_n)
            press = [(s, self._rare(s)) for s in sorted(set(things), key=repr)     # only what it has read in a
                     if s in self._row and self.of[s].get('sentences', self.of[s].get('seen', 0)) > 0]   # a word
            press = [(s, t) for s, t in press if t >= floor]                      # met only in questions holds ideas
            #                                                                        (the trigger's), not memories
            if not press:
                return []
            out = self._ring(press, most)
            self.came([s for s, _ in press], out)       # its trace, for the echo when something is confirmed
            return out
        return self._recalled(things, most)

    def _recalled(self, things, most=8):
        """The old way (records; IDEA_RECORDS): what comes to mind with some things (2026-09-29, the author: its memory is part of the Field, in the
        superposition, not a separate recall): every sentence it remembers with any of them, each as strongly as the
        things it shares tell (a rare thing more than a common one: every one of them the sentence holds) and as
        recently and as often as it read it (the old fades a little, by the power law of forgetting); the strongest
        few, in the order it read them (the latest last).
        Only what comes strongly: the things a memory shares must tell at least IDEA_MIND of the most a single thing
        can tell (log(1 + sentences read)) - so a common word alone ('is': S03, reviewer) brings nothing to mind, and a rare
        name does, however long ago it was read; the same things bring the same memories every time (sorted, ties by
        reading order).
        2026-09-29 (ideas-4, three books read whole): a shared thing counted only if the memory was among that thing's
        own last situations, and the fade took a psychology definition to 2e-6 after Plato and Locke, under the
        floor - so no definition from the first book could come to mind (22 of 67 recalled, only the ones re-read)."""
        cues = {}
        for s in sorted(set(things), key=repr):
            if s in self.of:
                tell = self._rare(s)
                if tell > 0:
                    cues[s] = tell
        readings = {}                                   # each memory a cue keeps, and when it was read
        for s in cues:
            for sent, _, _, at in self.of[s]['situations']:
                readings.setdefault(sent, set()).add(at)
        floor = IDEA_MIND * math.log(1.0 + self.read_n)
        strong = []
        for sent, ats in readings.items():
            held = set(sent)
            tells = sum(v for t, v in cues.items() if t in held)          # in a fixed order (cues are sorted)
            if tells >= floor:
                fade = sum((1.0 + self.read_n - at) ** -IDEA_DECAY for at in sorted(ats))
                strong.append((sent, tells * fade, max(ats)))
        strongest = sorted(strong, key=lambda t: (-t[1], -t[2]))[:most]
        return [s for s, _, _ in sorted(strongest, key=lambda t: t[2])]

    def _held(self, s, most=4):
        """What s alone rings back (its sentences as the Field holds them), with the place s stands in each."""
        if IDEA_RECORDS:
            return [sit[:2] for sit in self.of[s]['situations']] if s in self.of else []
        if s not in self.of or s not in self._row:
            return []
        return [(sent, sent.index(s)) for sent in self._ring([(s, 1.0)], most) if s in sent]

    def dream(self, s, rng, n=3):
        """Sentences it never read about s: what a thing like s rings back, with s in its place (from the Field's own
        state: no record is looked up)."""
        mine = {sent for sent, _ in self._held(s, 8)}
        out = []
        for o, like in self.kind(s, 6):
            sits = self._held(o)
            for k in rng.permutation(len(sits)):
                sent, i = sits[int(k)][:2]
                new = sent[:i] + (s,) + sent[i + 1:]
                if new not in mine and s not in sent and new not in [d for d, _ in out]:
                    out.append((new, like))
                    break
            if len(out) >= n:
                break
        return out

    def sure(self, s):
        """How sure its idea of s is: how often it has met s (a thing met once is a rough idea)."""
        seen = self.of[s]['seen'] if s in self.of else 0.0
        return seen / (seen + 3.0)


STEP_FEATURES = ('inside', 'smaller', 'toward', 'varies', 'simple')
STEP_FADE = 0.97                 # a task later, what it learned of steps counts this much (the old fades, the new leads)


class StepField:
    """What makes a good first step, as SERA learns it (2026-09-29; the author: "teach sera how to break down ideas or
    problems into pieces ... it finds the smallest and best step to solve a problem, does it correctly, then goes to
    the next smallest step"). A step is a small program of its own language over the problem's input; it is good if
    the rest of the answer then comes easily. Each step is seen by five features of what it makes (sera.one
    Sera._step_features): the answer is inside it, it is smaller than the input, its type is nearer the answer's, it
    differs between examples, it is simple. How much each counts is a Gaussian over weights, from its own steps (the
    rest found or not) and the teacher's word on its candidate steps in teaching (evidence, fading), both fading a
    little each task - neutral at birth: nothing about good steps is given."""

    def __init__(self, noise=1.0, prior=1.0):
        self.d = len(STEP_FEATURES)
        self.noise, self.prior = noise, prior
        self.A = np.zeros((self.d, self.d))       # its own evidence
        self.b = np.zeros(self.d)
        self.At = np.zeros((self.d, self.d))      # the teacher's, fading faster
        self.bt = np.zeros(self.d)
        self.tried = self.found = 0

    def _post(self):
        A = np.eye(self.d) / self.prior ** 2 + self.A + self.At
        cov = np.linalg.inv(A)
        return cov @ (self.b + self.bt), cov

    def weights(self):
        return {k: round(float(v), 2) for k, v in zip(STEP_FEATURES, self._post()[0])}

    def score(self, f, rng=None):
        """How good a step looks: its mean weights (or a draw from them, to try steps it is unsure of) on its features."""
        mean, cov = self._post()
        w = rng.multivariate_normal(mean, (cov + cov.T) / 2) if rng is not None else mean
        return float(w @ np.asarray(f, float))

    def learn(self, f, y):
        """y: +1 the rest came and the answer fit, -1 it did not."""
        x = np.asarray(f, float)
        self.A += np.outer(x, x) / self.noise ** 2
        self.b += x * float(y) / self.noise ** 2
        self.tried += 1
        self.found += y > 0

    def teach(self, f, y):
        x = np.asarray(f, float)
        self.At += np.outer(x, x) / self.noise ** 2
        self.bt += x * float(y) / self.noise ** 2

    def end_task(self):
        self.A *= STEP_FADE
        self.b *= STEP_FADE
        self.At *= TAUGHT_FADE
        self.bt *= TAUGHT_FADE


class Field:
    """SERA's one state."""

    def __init__(self, seed=0):
        self.seed = seed
        self.concepts = []
        self.understood = deque(maxlen=N_UNDERSTOOD)
        self.standing = {}                          # hypothesis key -> [proofs, refutations]
        self.lexicon = TK.Lexicon(seed)
        self.loop = LoopField()
        self.methods = MethodField()                # how it imagines (revision 7)
        self.steps = StepField()                    # what makes a good first step (2026-09-29)
        self.ideas = Ideas()                        # ideas of things, from what it reads (2026-09-29)
        self.possibilities = deque(maxlen=N_POSSIBLE)
        self.links = []                             # serendipity: something from one task explained another
        self.questions = []                         # open questions (dualities, surprises), the last 64
        self.inbox = []                             # what it asks us
        self.answers = {}
        self.skills = deque(maxlen=64)              # actions that paid (a push program, a question), with context
        self.tasks = 0
        self.log = []                               # a compact record per task (for the observatory)
        self.traces = []                            # what took part in thinking, fading (the echo reads them)

    # --- the echo: how the whole Field changes when something is confirmed (2026-09-29 night; the author's research,
    #     Hamiltonian Echo Backpropagation + Eligibility Propagation, adapted: the author chose it) ---
    def trace(self, part):
        """e-prop's forward eligibility trace: a part of the Field that took part in thinking now - ('loop', faculty,
        features) or ('method', kind, method, triggers) - starts at 1 and fades each moment."""
        self.__dict__.setdefault('traces', []).append([part, 1.0])

    def fade_traces(self):
        for t in getattr(self, 'traces', []):
            t[1] *= TRACE_KEEP
        self.traces = [t for t in getattr(self, 'traces', []) if t[1] >= TRACE_FLOOR]
        self.ideas.fade(TRACE_KEEP)

    def forget_traces(self):
        """A new world: nothing of it has taken part yet."""
        self.traces = []
        self.ideas.forget_traces()

    def echo(self, signal):
        """The echo (HEB, adapted): a result confirmed (signal > 0) or refuted (< 0) sent back through everything that
        took part, each part changed by the signal times its trace (e-prop's three-factor rule) - the ways of working
        and the methods of imagining that led here are credited with the proof, however long ago in this world they
        ran (their own immediate returns are credited as they happen). Memory's side is Ideas.consolidate, and the
        confirmed idea is laid into the situation's things (sera.one). Returns how many parts it reached."""
        if not FIELD_ECHO or not signal:
            return 0                                     # no result: nothing is credited (S06 F3, reviewer)
        n = 0
        sure = min(1.0, abs(signal))                     # a softer echo is also less sure evidence, not only a smaller
        for part, w in getattr(self, 'traces', []):      # target (S06 F3); the trace weighs it (S05 F6)
            if part[0] == 'loop':                        # a proof's worth per second of that way of working, as its
                cost = part[3] if len(part) > 3 else 1.0   # returns are counted as they happen
                y = float(np.clip(signal * V_DONE / cost, -5.0, 20.0))
                self.loop.learn(part[1], part[2], y, weight=w * sure)
            elif part[0] == 'method':                    # a method's return is the doubt it removed, in nats
                y = float(np.clip(signal * V_DONE, -20.0, 40.0))
                self.methods.learn(part[1], part[2], part[3], y, weight=w * sure)
            n += 1
        self.traces = []                                 # an echo is spent: the same traces are not credited twice
        return n

    def __getstate__(self):
        d = dict(self.__dict__)
        d['traces'] = []                                 # what took part in a world is not kept with the Field
        return d

    # --- the language it has made ---
    def concept_table(self):
        """{id: (body, argument name)} and '_sig': {id: (argument type, result type)} for sera.lang."""
        out = {c['id']: (c['body'], '_') for c in self.concepts}
        out['_sig'] = {c['id']: tuple(c['sig']) for c in self.concepts}
        return out

    def names(self):
        """Its own name for each concept: the word it learned or coined for it."""
        out = {}
        for c in self.concepts:
            w = self.lexicon.word_for(('concept', c['id']))
            out[c['id']] = w or c['name']
        return out

    def shapes(self):
        """Its concepts drawn on the grid of each measured input they can be drawn on, in the order it made them (the
        physics judge's library: a concept is a function of any input, so it is registered on every one)."""
        out = []
        for c in self.concepts:
            out += list(c.get('shapes') or ([c['shape']] if c.get('shape') is not None else []))
        return tuple(out)

    def audited_by(self, cid, task):
        """An ability it wished (built on a few matching examples) is proven once a proof of a whole world uses it."""
        self.__dict__.setdefault('audited', {}).setdefault(cid, task)

    def proven_ideas(self):
        """Its ideas with a proof behind them: each concept a proof made (and the parts of that proof it kept), and each
        wished ability a proof has used since - a wished ability alone is tentative (S06 F5, reviewer)."""
        audited = getattr(self, 'audited', {})
        out = {c['id'] for c in self.concepts if not str(c.get('born', '')).endswith('(wished)') or c['id'] in audited}
        by = {c['id']: c for c in self.concepts}
        todo = sorted(out, key=repr)
        while todo:                                      # what a proven idea is made of was in its proof (a Field
            c = by.get(todo.pop())                       # saved before audited_by kept it only there)
            for p in (c or {}).get('parts') or ():
                if isinstance(p, (tuple, list)) and len(p) == 2 and p[0] == 'concept' and p[1] in by \
                        and p[1] not in out:
                    out.add(p[1])
                    todo.append(p[1])
        return out

    def invent(self, body, sig, subject, task, parts, shape=None, extra=None):
        """A proven solution becomes a concept of its language. Returns the concept."""
        prev = self.concepts[-1]['hash'] if self.concepts else '0' * 16
        cid = max(getattr(self, 'next_id', 0), len(self.concepts) + 1)    # never an id it used before (2026-09-28: an
        self.next_id = cid + 1                                            # ability it let go of keeps its number)
        c = dict(id=cid, name=f'c{cid}', body=body, sig=list(sig), subject=subject, born=task, parts=list(parts),
                 shape=shape, uses=0, gains=[], prev=prev, **(extra or {}))
        c['hash'] = _chain(prev, {k: v for k, v in c.items() if k not in ('uses', 'gains', 'shape')})
        self.concepts.append(c)
        return c

    # --- the three layers ---
    def _near(self, kind, context):
        out = []
        c = np.asarray(context, float)
        for e in self.understood:
            if e['kind'] != kind:
                continue
            d = float(np.sum((c - np.asarray(e['context'], float)) ** 2)) if len(c) == len(e['context']) else 4.0
            k = math.exp(-d / 2.0)
            if k > 1e-6:
                out.append((k * e['weight'], e))
        return out

    def familiarity(self, kind, context):
        parts, pairs = {}, {}
        for w, e in self._near(kind, context):
            ps = tuple(e['parts'])
            for p in ps:
                parts[p] = parts.get(p, 0.0) + w
            for i in range(len(ps)):
                for j in range(i + 1, len(ps)):
                    key = tuple(sorted((repr(ps[i]), repr(ps[j]))))
                    pairs[key] = pairs.get(key, 0.0) + w
        return parts, pairs

    def layers(self, kind, context, hyps, log_evidence, bits):
        """(log U, log L, log B, log Phi, tension) over hypotheses: hyps {key: parts}, log_evidence {key: log B
        (unnormalized)}, bits {key: description length}."""
        parts, pairs = self.familiarity(kind, context)
        rawU, logL = {}, {}
        for h, ps in hyps.items():
            u = sum(math.log1p(parts.get(p, 0.0)) for p in ps)
            ps = list(ps)
            for i in range(len(ps)):
                for j in range(i + 1, len(ps)):
                    u += PAIR_POWER * math.log1p(pairs.get(tuple(sorted((repr(ps[i]), repr(ps[j])))), 0.0)) / max(len(ps) - 1, 1)
            rawU[h] = u
            pr, rf = self.standing.get(h, (0, 0))
            logL[h] = -bits[h] * math.log(2) + math.log1p(pr) - math.log1p(rf)
        logL = normalize(logL)
        rawU = normalize({h: rawU[h] + logL[h] for h in hyps})       # understanding of parts, over the language
        logU = normalize({h: float(np.logaddexp(math.log(1 - ETA) + rawU[h], math.log(ETA) + logL[h])) for h in hyps})
        logB = normalize(log_evidence)
        phi = pool(logU, logL, logB)
        return logU, logL, logB, phi, kl(logB, logU)

    # --- what happened: the layers move each other ---
    def understand(self, kind, context, key, parts, proven, weight, task, where=None):
        self.understood.append(dict(kind=kind, context=list(map(float, context)), key=key, parts=tuple(parts),
                                    proven=bool(proven), weight=float(weight), task=task, where=where))
        if proven:
            self.standing.setdefault(key, [0, 0])[0] += 1

    def refute(self, key):
        self.standing.setdefault(key, [0, 0])[1] += 1

    def keep_possibility(self, kind, sig, key, hyp, context, task, why, phi):
        self.possibilities.append(dict(kind=kind, sig=sig, key=key, hyp=hyp, context=list(map(float, context)),
                                       task=task, why=why, phi=float(phi)))

    def wonder(self, task, what, text, **numbers):
        self.questions.append(dict(task=task, what=what, text=text, numbers=numbers, at=self.tasks))
        del self.questions[:-64]

    def ask(self, task, what, text, key=None, kind=None, meanings=(), **numbers):
        qid = f'q{len(self.inbox) + 1}'
        self.inbox.append(dict(id=qid, task=task, what=what, text=text, numbers=numbers, at=self.tasks, key=key,
                               kind=kind, meanings=list(meanings)))
        return qid

    def answer(self, qid, verdict, words=()):
        """Our answer to one of its questions (the author's "verify with us"): 'right' - its idea becomes understood and
        gains standing, and any words we add are heard against it; 'wrong' - its idea is refuted there; 'hint' - the
        words are kept and heard in its next task of that kind. Returns False for an unknown or already answered id."""
        q = next((q for q in self.inbox if q['id'] == qid), None)
        if q is None or qid in self.answers:
            return False
        words = [str(w) for w in words]
        self.answers[qid] = dict(verdict=verdict, words=list(words), at=self.tasks,
                                 understood={w: self.lexicon.understand(w) for w in words})    # how it took our words
        if verdict == 'right' and q.get('key') is not None:
            self.standing.setdefault(q['key'], [0, 0])[0] += 1
            if words and q.get('meanings'):
                self.lexicon.hear(words, q['meanings'])
        elif verdict == 'wrong' and q.get('key') is not None:
            self.refute(q['key'])
        if words and verdict == 'hint':
            self.__dict__.setdefault('hints', {}).setdefault(q.get('kind'), []).extend(words)
        return True

    def take_hints(self, kind):
        """Words we gave it for tasks of this kind (heard once, in the next one)."""
        return self.__dict__.setdefault('hints', {}).pop(kind, [])

    def migrate_loop(self):
        old, new = self.loop.migrate_features()
        migrated = []
        for part, weight in getattr(self, 'traces', []):
            if part[0] == 'loop':
                part = tuple(part[:2]) + (self.loop.remap_vector(part[2], old, new),) + tuple(part[3:])
            migrated.append([part, weight])
        self.traces = migrated

    # --- the whole state ---
    def save(self, path):
        import os
        from . import tasks as TS
        self.vocab = dict(TS.VOCAB)                      # the words as it read them (its ideas name them)
        tmp = str(path) + '.tmp'
        with open(tmp, 'wb') as f:
            pickle.dump(self, f)
        os.replace(tmp, path)

    @staticmethod
    def load(path):
        from . import tasks as TS
        with open(path, 'rb') as f:
            field = pickle.load(f)
        field.migrate_loop()
        TS.adopt(getattr(field, 'vocab', None) or {})    # a Field saved before its words were kept has none
        return field

    def digest(self):
        return hashlib.sha256(repr((len(self.concepts), [c['hash'] for c in self.concepts], len(self.understood),
                                    sorted(self.standing.items(), key=repr)[:50])).encode()).hexdigest()[:16]

    def account(self):
        """What it holds, in numbers (the observer's reading of the Field)."""
        by = {}
        for c in self.concepts:
            by[c['subject']] = by.get(c['subject'], 0) + 1
        return dict(tasks=self.tasks, concepts=len(self.concepts), concepts_by_subject=by,
                    words=len(self.lexicon.heard), grounded=len(self.lexicon.grounded()), coined=len(self.lexicon.coined),
                    understood=len(self.understood), possibilities=len(self.possibilities), links=len(self.links),
                    questions=len(self.questions), inbox=len(self.inbox))
