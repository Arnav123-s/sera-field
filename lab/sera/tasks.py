"""The worlds SERA lives in (plan revision 6). These are environments, not parts of SERA: each says what can be seen,
what can be done, how an answer is checked (its judge), and what its teacher says. SERA itself (sera.one) is one mind
that lives every one of them the same way.

Every world offers the same few things to the one mind:
- inputs, out, form      what an answer is: an expression of SERA's language over these inputs (sera.lang); 'strengths'
                         when the answer is a sum of parts with strengths the world's evidence fits (a force law), 'exact'
                         when the expression must give the output exactly (a program, a number rule)
- probes()               inputs to tell expressions apart by (observational equivalence in search)
- evidence(laws)         log evidence of each hypothesis from what has been seen (the world's way of seeing: a rail's
                         readings through its dynamics; a list's outputs)
- actions(rng, laws, w)  what SERA can do next (a push; an input to ask about), each with its expected information
                         about the laws and its novelty (where nothing has been seen yet)
- act(a)                 do it; the world answers
- verify(law)            the world's judge: the physics certificate (Decision 13, a functional claim) and the
                         independent checker; the audit of a program or rule on fresh inputs
- words                  what the teacher says (tokens), in teaching only; the observer's truth of a word
- grade(law, accepted)   the observer's verdict (the hidden truth is known in these worlds; SERA never reads it)

The rail's physics of seeing (a push moves a thing by the force of the hand and the hidden force, over its mass) is how
SERA's body senses motion: the hand law it learned in the nursery (ccops5.core.worlds.hand). The hidden force is what
it must find.
"""
import copy
import math

import numpy as np

from ccops5.core import checker, grammar, likelihood as L, mind as M1, paths, truth, worlds as W
from . import compact as C, crutches as CR, design as DS, field as F, lang as LG, synth as S, talk as TK, worlds as SW

# U4 budgets are caller limits, never parameters of the core's acceptance rule.
SCRUTINY_PROBES = 32
SCRUTINY_THROWS = 4
SCRUTINY_CANDIDATES = 32
SCRUTINY_HISTORY = 32
SCRUTINY_KINDS = 64


class JudgeScrutiny:
    """Bounded history of received counterexamples, shared across tasks by the saved Field.

    No observer grades/targets enter the policy. Exact regions are coarse input sizes
    and magnitudes; only fresh draws from the current world's distribution are tested.
    """
    def __init__(self):
        self.history = {}

    @staticmethod
    def kind(task):
        return f"{task.form}:{','.join(sorted(task.inputs.values()))}->{task.out}"

    @staticmethod
    def region(x, depth=0):
        if isinstance(x, (list, tuple)):
            # Bounded inspection, including story/grid inputs.
            children = [JudgeScrutiny.region(v, depth+1) for v in x[:16]] if depth < 3 else []
            return (math.log1p(len(x)), sum(v[0] for v in children) / max(1, len(children)),
                    sum(v[2] for v in children) / max(1, len(children)))
        if isinstance(x, (int, float, np.number)) and math.isfinite(float(x)):
            return (0., math.copysign(math.log1p(abs(float(x))), float(x)), float(x < 0))
        return (0., 0., 0.)

    def remember(self, kind, region):
        if kind not in self.history and len(self.history) >= SCRUTINY_KINDS:
            del self.history[sorted(self.history)[0]]
        rows = self.history.setdefault(kind, [])
        region = tuple(float(v) for v in region)
        if region in rows:
            rows.remove(region)
        rows.append(region)
        del rows[:-SCRUTINY_HISTORY]

    def begin(self, task, probability=None, calibration=()):
        kind = self.kind(task)
        rows = self.history.get(kind, ())
        p = float(probability) if probability is not None else None
        if p is not None and not (math.isfinite(p) and 0 <= p <= 1):
            raise ValueError('Finite inner probability in [0,1] required')
        # U3 bins are [received verdict count, sum of pre-verdict predictions, right count].
        n, observed = 0, None
        if p is not None and len(calibration) == 10:
            n, _, right = calibration[min(9, int(p * 10))]
            observed = float(right / n) if n else None
        excess = max(0., p - observed) if p is not None and p >= .7 and observed is not None else 0.
        risk = min(1., len(rows) / 8. + excess)
        limit = SCRUTINY_THROWS if task.form == 'strengths' else SCRUTINY_PROBES
        budget = min(limit, (1 if task.form == 'strengths' else 4) + int(risk * (limit - 1)))
        task._scrutiny_policy = self
        task._scrutiny_last = dict(kind=kind, budget=budget, used=0, candidates=0,
                                   max_budget=limit, history=len(rows), inner_probability=p,
                                   calibration_n=int(n), calibration_observed=observed,
                                   overconfidence=excess, baseline_accepted=None, accepted=None,
                                   counterexample=None)
        return task._scrutiny_last

    def distance(self, kind, region):
        rows = self.history.get(kind, ())
        return min((sum((a-b)**2 for a, b in zip(region, row)) for row in rows), default=0.)


def scrutiny(task):
    """Standalone tasks get a local policy; Sera._prove binds the Field's shared policy."""
    policy = getattr(task, '_scrutiny_policy', None)
    if policy is None:
        policy = JudgeScrutiny()
    # A prepared prediction is consumed once, so direct repeated verifies get fresh budgets.
    if not getattr(task, '_scrutiny_prepared', False):
        policy.begin(task)
    task._scrutiny_prepared = False
    return policy, task._scrutiny_last


EPS = 0.2
MISS_NATS = 30.0                              # an example a program gets wrong costs this much (2026-09-28)
GRAM_MAX = 1500                               # above this many columns, a rail's evidence builds G's blocks per law
EVIDENCE_COLS = 4000                          # columns a rail's evidence holds at once (its peak memory: readings x this)
CHANNELS = ('position', 'speed', 'time')
CH_INDEX = {c: i for i, c in enumerate(CHANNELS)}
K_PART = 33                                   # every drawn part lives on the 33-knot grid of its input
DISTURBED = 20.0                              # sigmas: a push its law misses by this much is a surprise


def grid(ch, K=K_PART):
    """The K knots of an input's grid, or of a lens's window (Decision 14: a channel SERA made to look closer)."""
    lo, hi = grammar.input_range(ch)
    return np.linspace(lo, hi, K)


def base(ch):
    """The measured input a channel looks at (a lens looks at its input; a dimension SERA made is its own)."""
    return grammar.base_input(ch)


def values(s, ch):
    """A channel's values at measured points s = {'position': x, 'speed': v, 'time': t}: an input's (or its lens's)
    own, or a dimension's program evaluated there (Decision 15)."""
    if grammar.is_dim(ch):
        return grammar.dim_eval(ch, s['position'], s['speed'], s['time'])
    return s[base(ch)]


def hats(ch, s, K):
    """The K hats of the channel's grid at the points s (points x K): a free curve's columns."""
    g = grid(ch, K)
    h = g[1] - g[0]
    H = np.maximum(0.0, 1.0 - np.abs(s[:, None] - g[None, :]) / h)
    H[:, 0] = np.where(s <= g[0], 1.0, H[:, 0])
    H[:, -1] = np.where(s >= g[-1], 1.0, H[:, -1])
    return H


DIM_K = 9                                     # knots of a curve on a dimension SERA's expression is said as
RAMP = True                                   # Decision 16: its expression is said first as one strength times it
#                                               (False: only as a curve on it, as before, for comparison)
DIM_TOKEN = {'position': 'x', 'speed': 'v', 'time': 't'}
DIM_OPS = {'add': 'add', 'sub': 'sub', 'mul': 'mul', 'radd': 'add', 'rsub': 'sub', 'rmul': 'mul'}


def _dim_program(e, env, concepts, depth=0):
    """SERA's expression as a dimension program (postfix tokens), concepts written out; None if its language says
    something the judge's dimensions cannot (a literal, a division, a choice, a table)."""
    if depth > 12:
        return None
    sym = e[0]
    if sym == 'var':
        return env.get(e[1])
    if sym == 'zero':
        return ('0',)
    if sym in ('one', 'rone'):
        return ('1',)
    if sym in DIM_OPS:
        a = _dim_program(e[2], env, concepts, depth + 1)
        b = _dim_program(e[3], env, concepts, depth + 1)
        return None if a is None or b is None else a + b + (DIM_OPS[sym],)
    if sym == 'c':
        entry = concepts.get(e[1])
        inner = _dim_program(e[2], env, concepts, depth + 1)
        if entry is None or inner is None:
            return None
        body, arg = entry
        return _dim_program(body, {arg: inner}, concepts, depth + 1)
    return None


def draw_knots(part, concepts):
    """(knots on the 33-grid, normalized to at most 1) of an expression or concept part; None if undefined."""
    ch, kind, ref = part
    if kind == 'curve':
        return None
    e = LG.node('var', payload='s') if kind == 'concept' else ref
    if kind == 'concept':
        e = LG.node('c', e, payload=ref)
    vals = [LG.safe(e, {'s': float(s)}, concepts) for s in grid(ch)]
    if any(v is None or isinstance(v, (bool, tuple)) for v in vals):
        return None
    k = np.asarray(vals, float)
    m = float(np.max(np.abs(k)))
    if not m > 1e-9:
        return None
    return tuple(float(x) for x in k / m)


# ============================================================ the rail (physics)
class Rail:
    """A rail with things on it: SERA pushes them and watches where they go. The hidden force is a law of the judge's
    grammar (a spring, drag ...) or a shape in no list (sera.novel); SERA's answer is a sum of at most two parts, each
    a function of one input (position, speed or time): one of its concepts, an expression of its language, or a free
    curve."""
    subject = 'physics'
    form = 'strengths'
    inputs = {'s': 'num'}
    out = 'num'

    def __init__(self, world, name, words=(), signs=None):
        self.world, self.name = world, name
        self.sigma = world.sigma
        self.throws = [t for sit in world.situations() for t in sit]
        self.words = list(words)
        self.hidden = grammar.canonical(world.spec.family)
        self.signs = signs
        self._ledger = None
        self._cache = {}
        self._knots = {}
        self.pushes = 0

    # --- how a part is drawn, and what the judge may be asked ---
    def part_knots(self, part, concepts):
        """draw_knots, once per part in this world (2026-09-28: at level 2 the same thousands of parts were drawn again
        at every weighing, most of a step). The concept table is fixed within a world; another table is drawn anew."""
        hit = self._knots.get(part)
        if hit is not None and hit[0] is concepts:
            return None if hit[1] is None else tuple(float(x) for x in np.frombuffer(hit[1]))
        k = draw_knots(part, concepts)
        self._knots[part] = (concepts, None if k is None else np.asarray(k, float).tobytes())   # the same floats, as
        return k                                        # 264 bytes, not 33 Python floats (~1.1 KB): at level 7 the
                                                        # rub drew millions of parts (the Colab RAM plateau, 2026-09-29)

    def term(self, part, concepts, library):
        """The judge's term for a part: a free curve's cell; a drawn part's tied shape (the library's own entry when the
        part is one of SERA's registered shapes, else an unregistered one, n = 0, for SERA's own ledger only)."""
        ch, kind, ref = part
        if kind == 'curve':
            return ('cell', ch, int(ref))
        knots = self.part_knots(part, concepts)
        if knots is None:
            return None
        for sh in library:
            if sh[1] == ch and np.allclose(sh[4], knots, atol=1e-9):
                return sh
        return ('shape', ch, K_PART, 0, knots)

    def family(self, law, concepts, library):
        terms = [self.term(p, concepts, library) for p in law]
        if any(t is None for t in terms):
            return None
        return grammar.canonical(tuple(terms))

    def claim_family(self, law, concepts, library):
        """What SERA can ask the judge to prove for a law: its registered shapes as they are; a free curve as it is;
        an expression it has not made a concept yet said as exactly as the judge's own language allows (2026-10-01;
        the author: "there might be a problem in communication between the field and the judge"; review 9):
        - as a dimension (Decision 15: u = its expression of the input, a program the judge's simulator runs exactly)
          with a 9-knot curve on it - a force that is some strength times its expression is exactly such a curve;
        - else as the 33-knot curve of its input, never coarser. It was coarsened to the fewest knots that drew the
          normalized drawing within eps / 4 - blind to the force's strength: stiff 2's cubic (strength ~214 in those
          units) was sent as a 9-knot curve that missed by 600-900 sensor sigmas, "something else is here", and SERA
          hunted a force that was not there for hours; the 33-knot curve and the cubic dimension were both accepted
          on the first 16 throws (sera-runs/judge-channel-1001)."""
        terms = self.claim_terms(law, concepts, library)
        return None if terms is None else terms[0]

    def claim_terms(self, law, concepts, library, ramp=False):
        """claim_family's family, and for each part of the law, in order, (the term it is sent as, what a proof of it
        certifies): 'drawing' - a registered shape, some strength times SERA's drawing of one of its concepts; 'curve'
        - a free cell, on an input or on the dimension SERA's expression is said as: some curve of that coordinate,
        never SERA's formula (1 + x^3 is accepted where x^3 is: sera-runs/judge-channel-1001/s10_false_credit.out;
        review 11, the honesty fix of 2026-10-01). With `ramp` (Decision 16), an expression the judge's dimensions can
        say goes as a ramp, 'formula': one strength times exactly that expression, clipped at its range - the only
        claim that certifies SERA's formula. None when the law cannot be said."""
        out = []
        for part in law:
            ch, kind, ref = part
            t = self.term(part, concepts, library)
            if t is None:
                return None
            if t[0] == 'shape' and t[3] == 0:
                d = self._as_dimension(part, concepts)
                if d is not None and ramp and grammar.is_ramp(('ramp', d, grammar.RAMP_K)):
                    out.append((('ramp', d, grammar.RAMP_K), 'formula'))
                    continue
                t = ('cell', d, DIM_K) if d is not None else ('cell', ch, K_PART)
            out.append((t, 'curve' if t[0] == 'cell' else 'drawing'))
        return grammar.canonical(tuple(t for t, _ in out)), tuple(out)

    def _as_dimension(self, part, concepts):
        """An expression of one whole measured input as the judge's dimension (Decision 15) - a program of x, v, t, 0,
        1, add, sub, mul, concepts written out - with the narrowest of the judge's fixed ranges that holds twice the
        largest value it takes at any reading (the pushes to come and the simulator's steps between readings go a
        little beyond what was read). None if it cannot be said there."""
        ch, kind, ref = part
        tok = DIM_TOKEN.get(ch)                          # a whole input (a lens is clamped beyond its window)
        if tok is None or kind not in ('expr', 'concept'):
            return None
        e = ref if kind == 'expr' else LG.node('c', LG.node('var', payload='s'), payload=ref)
        toks = _dim_program(e, {'s': (tok,), '_': (tok,)}, concepts)
        if toks is None or not 1 <= len(toks) <= grammar.DIM_MAX:
            return None
        name = grammar.dim_name(tuple(toks), grammar.DIM_R[0])
        if not grammar.is_dim(name) or not self.throws:
            return None
        x = np.concatenate([np.asarray(t.x, float) for t in self.throws])   # the expanded program on the unrounded
        v = np.concatenate([np.asarray(t.v, float) for t in self.throws])   # readings (review 11: exact range
        tt = np.concatenate([np.arange(len(t.x)) * paths.DT_OBS for t in self.throws])   # selection)
        with np.errstate(all='ignore'):
            u = grammar.dim_eval(name, x, v, tt)
        if not np.all(np.isfinite(u)):
            return None
        need = 2.0 * float(np.max(np.abs(u)))
        for r in grammar.DIM_R:
            if 2.0 ** (r - 4) >= need:
                return grammar.dim_name(tuple(toks), r)
        return None

    def _range(self, ch, scope):
        if grammar.is_dim(ch):                       # Decision 15: where it looked, along the new dimension
            u = values({'position': np.concatenate([t.x for t in self.throws]),
                         'speed': np.concatenate([t.v for t in self.throws]),
                         'time': np.concatenate([np.arange(paths.N_OBS) * paths.DT_OBS for _ in self.throws])}, ch)
            wlo, whi = grammar.input_range(ch)
            lo, hi = max(float(u.min()), wlo), min(float(u.max()), whi)
            return (lo, hi) if lo < hi else (wlo, whi)
        b = base(ch)
        lo, hi = scope['x'] if b == 'position' else scope['v'] if b == 'speed' else (0.0, paths.T_END)
        if grammar.is_lens(ch):                      # Decision 14: where it looked, inside the lens's window
            wlo, whi = grammar.input_range(ch)
            lo, hi = max(lo, wlo), min(hi, whi)
            if not lo < hi:
                return wlo, whi
        return lo, hi

    # --- evidence: every law at once (the reading intervals, each object's inverse mass from the leading fit) ---
    def _points(self, mu):
        obj, y, fb, xb, vb, tb = C.intervals(self.throws)
        keep = np.array([o in mu for o in obj], bool)
        m = np.array([mu[o] for o in obj[keep]], float)
        return dict(z=y[keep] / m - fb[keep], d=(C.SIGMA_Y / m) ** 2,
                    s={'position': xb[keep], 'speed': vb[keep], 'time': tb[keep]})

    def evidence(self, laws, concepts, library, mu):
        """{law: log marginal likelihood} (the Field's exact Gaussian evidence on the reading intervals, sera.field),
        with each object's inverse mass `mu` plugged in.
        Weighed a chunk of laws at a time, each chunk with only the columns its laws use (2026-09-29, the Colab RAM
        spike: the long run at level 7 of the rub built one matrix of every candidate part at every reading - readings
        x parts x 8 bytes - and one process peaked at 40.9 GB). A law's evidence depends only on its own columns and on
        totals of the readings (sera.field.log_marginal), so the numbers are the same as one matrix."""
        pts = self._points(mu)
        seen, hat = {}, {}                             # each input's readings and hats, once per weighing
        drawn = {}                                     # part -> its column block (None: undefined), per chunk

        def block_of(part):
            ch, kind, ref = part
            if ch not in seen:
                seen[ch] = values(pts['s'], ch)
            s = seen[ch]
            if kind == 'curve':
                return hats(ch, s, int(ref))
            knots = self.part_knots(part, concepts)
            if knots is None:
                return None
            if ch not in hat:
                hat[ch] = hats(ch, s, K_PART)
            return (hat[ch] @ np.asarray(knots))[:, None]

        out = {}

        def weigh(chunk):
            cols, index, width = [], {}, 0
            for law in chunk:
                for part in law:
                    if part in index:
                        continue
                    block = drawn[part]
                    if block is None:
                        index[part] = None
                        continue
                    index[part] = list(range(width, width + block.shape[1]))
                    width += block.shape[1]
                    cols.append(block)
            Phi = np.concatenate(cols, axis=1) if cols else np.zeros((len(pts['z']), 0))
            st = (F.LazyStats(Phi, pts['d'], pts['z']) if Phi.shape[1] > GRAM_MAX
                  else F.Stats.from_arrays(Phi, pts['d'], pts['z']))
            for law in chunk:
                idx = []
                ok = True
                for part in law:
                    if index.get(part) is None:
                        ok = False
                        break
                    idx += index[part]
                if not ok:
                    continue
                try:
                    out[law] = F.log_marginal(st, idx)
                except np.linalg.LinAlgError:
                    continue

        chunk, width = [], 0
        for law in laws:
            for part in law:
                if part not in drawn:
                    drawn[part] = block_of(part)
                    if drawn[part] is not None:
                        width += drawn[part].shape[1]
            chunk.append(law)
            if width >= EVIDENCE_COLS:
                weigh(chunk)
                chunk, width = [], 0
                drawn.clear()                          # the next chunk draws what it needs again
        if chunk or not out:
            weigh(chunk)
        return out

    def fitted_curve(self, law, part, concepts, mu):
        """A free curve's fitted knots within a law (weighted least squares on the reading intervals, a small ridge),
        scaled to at most 1 - the shape the snowball keeps; None if the law cannot be drawn."""
        pts = self._points(mu)
        cols, at = [], None
        for p in law:
            ch, kind, ref = p
            s = values(pts['s'], ch)
            if kind == 'curve':
                block = hats(ch, s, int(ref))
            else:
                knots = self.part_knots(p, concepts)
                if knots is None:
                    return None
                block = (hats(ch, s, K_PART) @ np.asarray(knots))[:, None]
            if p == part:
                at = (sum(c.shape[1] for c in cols), block.shape[1])
            cols.append(block)
        if at is None or not cols:
            return None
        Phi = np.concatenate(cols, axis=1)
        w = 1.0 / np.sqrt(pts['d'])
        A = Phi * w[:, None]
        beta = np.linalg.solve(A.T @ A + 1e-6 * np.eye(A.shape[1]), A.T @ (pts['z'] * w))
        k = beta[at[0]:at[0] + at[1]]
        m = float(np.max(np.abs(k)))
        return tuple(float(v) for v in k / m) if m > 1e-9 else None

    def seen(self):
        """The range of every input it has seen (reading intervals of all its throws): {input: (lo, hi)}."""
        obj, y, fb, xb, vb, tb = C.intervals(self.throws)
        return {'position': (float(xb.min()), float(xb.max())), 'speed': (float(vb.min()), float(vb.max())),
                'time': (float(tb.min()), float(tb.max()))}

    # --- the judge's ledger over the leading laws (predictions, masses, proofs) ---
    def ledger(self, families):
        """The judge's ledger over these families on every throw so far; each family's state is kept across rebuilds
        (exactly what Ledger.add computes: a family's update depends on it and the throws alone)."""
        fams = list(dict.fromkeys(f for f in families if f is not None))
        led = truth.Ledger(fams, self.sigma)
        for f in fams:
            k, q, post = 0, 0.0, led.post[f]
            hit = self._cache.get(f)
            if hit is not None and hit[0] <= len(self.throws):
                k, q, post = hit
            for t in self.throws[k:]:
                dq, post = L.step(led._models[f], post, t, self.sigma)
                q += dq
            led.Q[f], led.post[f] = q, post
            self._cache[f] = (len(self.throws), q, post)
        led.throws = list(self.throws)
        self._ledger = led
        return led

    def first_masses(self):
        """How hard a push moves each thing, sensed without any law: per object, the acceleration regressed on the
        hand's force together with a plain local drift in position, speed and time (a + b x + c v + d t); the
        coefficient of the hand is its inverse mass. The hand switches on and off, so this is identifiable whatever the
        hidden force is (a first guess; the leading law's own fit refines it)."""
        obj, y, fb, xb, vb, tb = C.intervals(self.throws)
        out = {}
        for o in np.unique(obj):
            m = obj == o
            X = np.column_stack([fb[m], np.ones(m.sum()), xb[m], vb[m], tb[m]])
            if np.ptp(fb[m]) <= 1e-9:
                continue
            beta = np.linalg.lstsq(X, y[m], rcond=None)[0]
            out[int(o)] = float(np.clip(beta[0], 0.05, 5.0))
        return out

    @staticmethod
    def masses(led, family):
        post, nc = led.post[family], led._models[family].n_coef
        return {s: float(post.mean[nc + i]) for i, s in enumerate(post.order)
                if int(np.argmax(post.knock.get(s, (0.0,)))) == 0 and post.mean[nc + i] > 0}

    # --- what SERA can do ---
    def actions(self, rng, led, families, weights, own_programs=4):
        """Candidate pushes, each with (information about the leading laws: Box-Hill over their predictions; novelty:
        the share of its predicted readings in parts of the rail nothing has visited)."""
        leader = families[0]
        model, post = led._models[leader], led.post[leader]
        nc = model.n_coef
        scope = truth.scope_of(self.throws)
        seen = set(scope['cells'])
        out = []
        for k in range(self.world.n_situations):
            mu = post.mean[nc + post.order.index(k)] if k in post.order else L.MU_PRIOR[0]
            progs = list(DS.programs(model, post.mean[:nc], mu, np.random.default_rng([len(self.throws), k]),
                                     M1.DURATIONS, M1.COMMANDS)) + F.sample_programs(rng, own_programs)
            for a in progs:
                preds = []
                for f in families:
                    try:
                        y, J, P = DS._own_numbers(led, f, k, a)
                        cov = np.linalg.pinv(P)
                        preds.append((y, J @ cov @ J.T))
                    except (np.linalg.LinAlgError, ValueError):
                        preds.append(None)
                ok = [i for i, p in enumerate(preds) if p is not None and np.all(np.isfinite(p[0]))]
                if not ok:
                    continue
                w = np.array([weights[i] for i in ok])
                info = F.box_hill([preds[i] for i in ok], w / w.sum(), self.sigma) if len(ok) > 1 else 0.0
                y0 = preds[ok[0]][0]
                n = len(y0) // 2
                cells = [truth.cell_of(scope, float(x), float(v)) for x, v in zip(y0[:n], y0[n:])]
                novel = float(np.mean([c not in seen for c in cells])) if cells else 0.0
                out.append(dict(action=('push', k, a), info=float(info) if np.isfinite(info) else 0.0,
                                novel=novel, predicted=y0))
        return out

    def act(self, action):
        _, k, a = action
        throw = self.world.push(k, a, 'own')
        self.throws.append(throw)
        self.pushes += 1
        return throw

    def surprise(self, throw, predicted):
        """How far the push landed from the leading law's prediction, in sensor sigmas (RMS)."""
        y = np.concatenate([throw.x, throw.v])
        sc = np.concatenate([np.full(len(throw.x), 1 / self.sigma[0]), np.full(len(throw.v), 1 / self.sigma[1])])
        return float(np.sqrt(np.mean(((y - predicted) * sc) ** 2))) if np.all(np.isfinite(predicted)) else math.inf

    # --- the judge ---
    def verify(self, family):
        if not CR.on('judge_scrutiny'):
            return self._verify_plain(family)
        policy, record = scrutiny(self)
        ok, cert, why = self._verify_plain(family)
        where = dict(truth.LAST_WHERE) if cert.band is not None else {}
        record.update(baseline_accepted=bool(ok), baseline_band=cert.band, baseline_throws=len(self.throws),
                      certifications=1, checker_calls=int(cert.accepted))
        # A refusal cannot be rescued by adaptivity. An uncertainty refusal is not a refutation.
        if not ok:
            if why and 'something else is here' in why:
                record['counterexample'] = self._scrutiny_misfit(family, policy, record)
            record.update(accepted=False, reason=why)
            return ok, cert, why
        if record['budget'] == 0:
            record.update(accepted=True, reason=None)
            return True, cert, None
        led = self._ledger
        targets = list(policy.history.get(record['kind'], ()))
        if where:
            targets.append((where['x'], where['v'], where['t']))
        candidates = []
        # Fixed small public action menu, ranked only by predicted measurements.
        for k in range(min(self.world.n_situations, SCRUTINY_CANDIDATES // 4)):
            for u in (-1., -.5, .5, 1.):
                a = W.push_of(u)
                record['candidates'] += 1
                try:
                    y, _, _ = DS._own_numbers(led, family, k, a)
                except (ValueError, np.linalg.LinAlgError):
                    continue
                if not np.isfinite(y).all():
                    continue
                n = len(y) // 2
                d = min((min(((float(x)-tx)**2 + (float(v)-tv)**2 + (j*paths.DT_OBS-tt)**2
                               for j, (x, v) in enumerate(zip(y[:n], y[n:]))), default=math.inf)
                         for tx, tv, tt in targets), default=0.)
                candidates.append((d, k, u, a))
        made = []
        for _, k, _, a in sorted(candidates, key=lambda v: v[:3])[:record['budget']]:
            t = self.act(('push', k, a))
            record['used'] += 1
            made.append(dict(situation=k, action=a.segments, x=t.x.tolist(), v=t.v.tolist()))
        if not made:
            record.update(accepted=True, reason=None)
            return True, cert, None
        final_ok, final_cert, final_why = self._verify_plain(family)
        record['certifications'] += 1
        record['checker_calls'] += int(final_cert.accepted)
        witness = dict(truth.LAST_WHERE) if final_cert.band is not None else {}
        # Widening due to new scope/noise is a caller veto, never a forged tighter certificate.
        narrow = final_cert.band is not None and final_cert.band <= cert.band
        accepted = bool(final_ok and narrow)
        reason = final_why if not final_ok else None if narrow else 'scrutiny: the band widened'
        record.update(accepted=accepted, final_band=final_cert.band, reason=reason)
        if not accepted:
            record['counterexample'] = dict(kind='misfit' if reason and 'something else is here' in reason
                                            else 'uncertainty', throws=made, where=witness,
                                            baseline_band=cert.band, final_band=final_cert.band, reason=reason)
            if reason and 'something else is here' in reason:
                record['counterexample']['residual'] = self._scrutiny_misfit(family, policy, record)
        return accepted, final_cert, reason

    def _scrutiny_misfit(self, family, policy, record):
        """Locate the largest observed residual, respecting the core fit's bump model.

        The core's aggregate adequacy rejection is the refutation; this reading
        locates it for future throws, without inventing a per-reading verdict.
        """
        led = self._ledger
        fit = led.mle(family)
        best = None
        record['residual_probes'] = 0
        if fit.ok:
            model = led._models[family]
            for t in self.throws[-SCRUTINY_CANDIDATES:]:
                record['residual_probes'] += 1
                kt = L.knocked(t, (fit.knocks or {}).get(t.situation, 0))
                r = (L._obs(t) - L._sim(model, fit.coef, fit.mu[t.situation], kt)) * L._scale(self.sigma)
                if not np.isfinite(r).all():
                    continue
                i = int(np.argmax(np.abs(r)))
                j = i % len(t.x)
                if best is None or abs(float(r[i])) > best[0]:
                    best = (abs(float(r[i])), t, j)
        if best is None:
            return dict(kind='misfit', reason='aggregate adequacy rejection; no finite residual fit')
        residual, t, j = best
        region = (float(t.x[j]), float(t.v[j]), j * paths.DT_OBS)
        policy.remember(record['kind'], region)
        return dict(kind='misfit', where=dict(zip(('x', 'v', 't'), region)),
                    situation=t.situation, action=t.action.segments, residual_sigmas=residual)

    def _verify_plain(self, family):
        """The unchanged core certificate and independent checker, on the current throws."""
        led = self.ledger(list((self._ledger.families if self._ledger else [])) + [family])
        cert = truth.certify(led, family, EPS, claim='functional')
        if not cert.accepted:
            return False, cert, cert.reasons[0] if cert.reasons else 'refused'
        ok, why = checker.check(cert, self.throws, self.sigma)
        return bool(ok), cert, None if ok else '; '.join(why)

    # --- the observer ---
    def grade(self, cert, accepted, n_throws=None):
        """The observer: the claim against the hidden truth at the readings the certificate used (its first n_throws),
        at the fairest strength (minimax: the claim says "some strength") - reviewer VD14 fix 4."""
        if not accepted:
            return dict(verdict='not proven')
        gap = self.world.residual_outside(cert, n_throws=n_throws, minimax=True)
        return dict(verdict='proven right' if gap <= EPS else 'SURE AND WRONG', gap=float(gap))

    def context(self):
        """What SERA perceives of a rail before it thinks: how the leftover motion goes with position, speed and time
        (correlations of each reading interval's acceleration per push with each input, after the hand), how big it
        is and how far things went. Its own senses; no law is named."""
        obj, y, fb, xb, vb, tb = C.intervals(self.throws[:2 * self.world.n_situations])
        r = []
        for o in np.unique(obj):
            m = obj == o
            mu = float(fb[m] @ y[m] / max(fb[m] @ fb[m], 1e-12))
            r.append(y[m] / max(mu, 1e-6) - fb[m])
        r = np.concatenate(r)
        corr = lambda a: float(np.corrcoef(a, r)[0, 1]) if np.std(a) > 1e-12 and np.std(r) > 1e-12 else 0.0
        return [corr(xb), corr(vb), corr(tb), corr(np.abs(vb) * np.sign(vb) ** 0), float(np.log10(np.std(r) + 1e-9)),
                float(np.max(np.abs(xb))), float(np.max(np.abs(vb)))]

    def teacher_truth(self, word):
        return TK.teacher_truth(word, self.hidden, self.signs or [0] * len(self.hidden))


def rail_world(seed, index, family, level=1, novel_shape=None, rep=0, units=False):
    """A rail of a law of the judge's grammar (teaching and practice: validated only for sane paths), or of a shape in
    no list (sera.novel). Returns (world, signs of its parts). units (a world with depth, 2026-09-28): its things are
    made of equal units of mass - 1, 2 and 3 of them - a layer below mass that nothing tells SERA about."""
    if novel_shape is not None:
        from . import novel as NV
        w = NV.novel_world(novel_shape, seed, rep)
        return w, [-1]
    family = grammar.canonical(family)
    for attempt in range(60):
        rng = np.random.default_rng([seed, 31, level, index + 100_000 * attempt])
        coefs = SW.sample_coefs(rng, family, level)
        masses3 = [float(m) for m in rng.uniform(0.6, 2.5, size=3)]
        if units:
            u = float(rng.uniform(0.4, 0.8))
            masses3 = [u, 2 * u, 3 * u]
        masses, bumps, pushes, checks = [], [], [], []
        for _ in range(8):
            masses.append(float(rng.choice(masses3)))
            bumps.append(None)
            pushes.append((float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0]))))
            checks.append(float(rng.choice((-0.9, -0.5, 0.5, 0.9))))
        w = SW.build(SW.Spec(seed, index + 100_000 * attempt, level, family, coefs, masses, bumps, pushes, checks, 1.0))
        paths_ok = all(np.all(np.isfinite(t.x)) and np.max(np.abs(t.x)) < 50 and np.max(np.abs(t.v)) < 50
                       for t in w.throws + w.held_out)
        if paths_ok:
            signs = [int(np.sign(c)) if t[0] != 'nothing' else 0 for t, c in zip(family, coefs)]
            return w, [-1 if s < 0 else 1 if s > 0 else 0 for s in signs]
    raise RuntimeError(f'no sane rail of {grammar.name(family)}')


# ============================================================ lists and numbers (code and math)
def numbers_of(pairs, most=6):
    """The numbers it perceives in examples (x, y): values and lengths from 2 to 20, at every depth of a list, the most
    frequent first - a sense, not an answer (0 and 1 are innate)."""
    seen = {}

    def look(v):                                        # a list's length and what it holds, at every depth
        if isinstance(v, (list, tuple)):
            if 2 <= len(v) <= 20:
                seen[len(v)] = seen.get(len(v), 0) + 1
            for u in v:
                look(u)
        elif isinstance(v, int) and not isinstance(v, bool) and 2 <= v <= 20:
            seen[v] = seen.get(v, 0) + 1
    for x, y in pairs:
        look(x)
        look(y)
    return tuple(sorted(sorted(seen), key=lambda v: -seen[v])[:most])


def _random_list(rng, n_max=6):
    return [int(v) for v in rng.integers(-5, 10, size=int(rng.integers(0, n_max + 1)))]


class Exact:
    """A world whose answer is an exact function: a list world (code) or a number world (math). SERA sees a few
    examples, may ask about any input, and its answer is checked by the audit on fresh inputs (the anytime bar of
    sera.synth: accepted only if every one of n inputs agrees, n from the answer's description length; so the chance of
    ever accepting an answer wrong on eps of inputs is at most delta)."""
    form = 'exact'

    def __init__(self, subject, name, target, inputs, out, examples, pool, fresh, words=(), truth_words=(), worked=None):
        self.subject, self.name = subject, name
        self._target = target                   # the hidden function (the world's, never SERA's)
        self.inputs, self.out = inputs, out
        self.var = next(iter(inputs))
        self.data = [(x, self._y(x)) for x in examples]
        self.pool = pool
        self._probe_inputs = list(examples) + list(pool[:16])      # fixed: the search can continue as it grows
        self._fresh = fresh
        self.words = list(words)
        self._truth_words = set(truth_words or words)
        self.asked = 0
        self._worked_values = worked

    def worked(self, x):
        """Optional teacher-side values for this input, never expressions of SERA's language."""
        if getattr(self, 'course_composed', False) and not CR.on('course_worked_steps'):
            return None
        if getattr(self, '_worked_values', None) is None:
            return None
        return tuple(LG.freeze(v) for v in self._worked_values(x))

    def _y(self, x):
        return LG.freeze(self._target(x))

    def probes(self):
        return [{self.var: (list(x) if isinstance(x, (list, tuple)) else x)} for x in self._probe_inputs]

    def numbers(self, most=6):
        """The numbers it perceives in the task (2026-09-28): values and lengths it sees in its examples, from 2 to 20,
        the most frequent first - a sense, not an answer (0 and 1 are innate)."""
        return numbers_of(self.data, most)

    def _value(self, e, x, concepts):
        return LG.safe(e, {self.var: list(x) if isinstance(x, tuple) else x}, concepts)

    def teacher_check(self, e, concepts, n=100, seed=0):
        """The teacher, when it teaches (S07 F4, reviewer: fail and credit at the proof, not after it has been rewarded):
        tries a proof on the teacher's own fresh examples (not the observer's) and shows the first it gets wrong, as a
        new example. Returns it, or None when the teacher agrees."""
        if self._fresh is None:
            return None
        rng = np.random.default_rng([seed, 887, len(self.name), len(self.data)])
        for _ in range(n):
            x = self._fresh(rng)
            y = self._y(x)
            if self._value(e, x, concepts) != y:
                self.data.append((x, y))
                return x, y
        return None

    def consistent(self, e, concepts):
        for x, y in self.data:
            v = LG.safe(e, {self.var: list(x) if isinstance(x, tuple) else x}, concepts)
            if v != y:
                return False
        return True

    def evidence(self, exprs, concepts):
        """Each expression's log likelihood: MISS_NATS per example it gets wrong (an example may be misread); so a
        thought that fits no example perfectly is still weighed, and its best guess is still a guess."""
        out = {}
        for e in exprs:
            miss = 0
            for x, y in self.data:
                if LG.safe(e, {self.var: list(x) if isinstance(x, tuple) else x}, concepts) != y:
                    miss += 1
            out[e] = -MISS_NATS * miss
        return out

    def evidence_values(self, found, concepts):
        """evidence() from what its search already has - each expression's values on the probes, where the examples
        are (2026-09-28: nothing evaluated twice); an example that is not a probe is evaluated. The same numbers."""
        if type(self).evidence is not Exact.evidence:        # a world that weighs its own way
            return self.evidence([e for e, _, _ in found], concepts)
        at = {}
        for j, x in enumerate(self._probe_inputs):
            at.setdefault(LG.freeze(x), j)
        where = [at.get(LG.freeze(x)) for x, _ in self.data]
        out = {}
        for e, _, vals in found:
            miss = 0
            for (x, y), j in zip(self.data, where):
                v = LG.seen_as(vals[j]) if j is not None else LG.safe(
                    e, {self.var: list(x) if isinstance(x, tuple) else x}, concepts)
                if v != y:
                    miss += 1
            out[e] = -MISS_NATS * miss
        return out

    def actions(self, rng, exprs, weights, concepts):
        """Inputs it can ask about, each with the information its answer would give (how evenly the leading
        expressions' answers split, weighted: Box-Hill for exact answers) and its novelty."""
        seen = {repr(x) for x, _ in self.data}
        out = []
        for x in self.pool:
            if repr(x) in seen:
                continue
            ys = [LG.safe(e, {self.var: list(x) if isinstance(x, tuple) else x}, concepts) for e in exprs]
            groups = {}
            for y, w in zip(ys, weights):
                groups[repr(y)] = groups.get(repr(y), 0.0) + w
            tot = sum(groups.values())
            info = -sum(p / tot * math.log(p / tot) for p in groups.values() if p > 0) if tot > 0 else 0.0
            out.append(dict(action=('ask', x), info=float(info), novel=0.0, predicted=ys[0] if ys else None))
        return out

    def act(self, action):
        x = action[1]
        self.data.append((x, self._y(x)))
        self.asked += 1
        return self.data[-1]

    def verify(self, e, concepts, bits, rng):
        """The audit: n fresh inputs from the world's own distribution, n from the answer's bits; a failing input
        becomes an example (SERA learns from it). Returns (accepted, n, the failing (input, output) or None)."""
        n = S.audit_size(bits)
        for _ in range(n):
            x = self._fresh(rng)
            y = self._y(x)
            if LG.safe(e, {self.var: list(x) if isinstance(x, tuple) else x}, concepts) != y:
                self.data.append((x, y))
                if CR.on('judge_scrutiny'):
                    return self._scrutinize(e, concepts, n, (x, y), rng)
                return False, n, (x, y)
        if CR.on('judge_scrutiny'):
            return self._scrutinize(e, concepts, n, None, rng)
        return True, n, None

    def _scrutinize(self, e, concepts, n, fail, rng):
        policy, record = scrutiny(self)
        record['baseline_accepted'] = fail is None
        record['baseline_budget'] = n
        if fail is not None:
            policy.remember(record['kind'], policy.region(fail[0]))
            record.update(accepted=False, counterexample=dict(kind='input', input=LG.freeze(fail[0]),
                                                             expected=LG.freeze(fail[1])))
            return False, n, fail
        # Copy AFTER the untouched baseline audit: no extra consumption of its RNG.
        extra_rng = copy.deepcopy(rng)
        candidates = [self._fresh(extra_rng) for _ in range(4 * record['budget'])]
        record['candidates'] = len(candidates)
        order = sorted(range(len(candidates)),
                       key=lambda j: (policy.distance(record['kind'], policy.region(candidates[j])), j))
        for j in order[:record['budget']]:
            x = candidates[j]
            y = self._y(x)
            actual = self._value(e, x, concepts)
            record['used'] += 1
            if actual != y:
                self.data.append((x, y))
                policy.remember(record['kind'], policy.region(x))
                record.update(accepted=False, counterexample=dict(kind='input', input=LG.freeze(x),
                                                                 expected=LG.freeze(y), actual=LG.freeze(actual)))
                return False, n + record['used'], (x, y)
        record['accepted'] = True
        return True, n + record['used'], None

    def grade(self, e, concepts, accepted, n=200, seed=0):
        rng = np.random.default_rng([seed, 991, len(self.name)])
        agree = all(LG.safe(e, {self.var: list(x) if isinstance(x, tuple) else x}, concepts) == self._y(x)
                    for x in (self._fresh(rng) for _ in range(n)))
        if accepted:
            return dict(verdict='proven right' if agree else 'SURE AND WRONG')
        return dict(verdict='right, unsure' if agree else 'not proven')

    def context(self):
        """What it perceives before thinking: the kinds of input and output, and simple sizes of the examples."""
        xs = [x for x, _ in self.data]
        ys = [y for _, y in self.data]
        ln = lambda v: len(v) if isinstance(v, (list, tuple)) else abs(v)
        return [1.0 if self.subject == 'code' else 0.0, 1.0 if self.out == 'list' else 0.0,
                float(np.mean([ln(y) for y in ys])) / 10, float(np.mean([ln(x) for x in xs])) / 10,
                float(np.mean([1.0 if (isinstance(y, (int, float)) and y < 0) else 0.0 for y in ys])), 0.0, 0.0]

    def teacher_truth(self, word):
        return word in self._truth_words


class Given(Exact):
    """A job someone describes by examples, and in words if they like (2026-09-30; the author: "I want it to be able to
    code"). Some examples are what SERA learns from; the rest are held back as its audit - no one else knows the
    answers, so it cannot ask about other inputs. A program it proves is right on every example given; that is all
    the proof says. The words are the job's name, heard as a teacher's words are: the ability it proves is called by
    them in its Field from then on."""

    def __init__(self, name, pairs, words=(), held=None):
        pairs = [(LG.freeze(x), LG.freeze(y)) for x, y in pairs]
        if len(pairs) < 2:
            raise ValueError('a job needs at least two examples: one to learn from, one to check')
        k = held if held is not None else max(1, len(pairs) // 3)
        learn, audit = pairs[:len(pairs) - k], pairs[len(pairs) - k:]
        self._table = dict(pairs)
        x0, y0 = pairs[0]
        inputs = {'l': 'list'} if isinstance(x0, tuple) else {'n': 'num'}
        out = 'list' if isinstance(y0, tuple) else 'num'
        audit_x = [x for x, _ in audit]
        super().__init__('code', name, None, inputs, out, [x for x, _ in learn], [],
                         lambda r: audit_x[int(r.integers(len(audit_x)))], words)
        self._probe_inputs = [x for x, _ in pairs]      # inputs only: what it may try its ideas on
        self.held = len(audit)
        self.audit_words = f'draws from the {len(audit)} examples held back (all of them)'

    def _y(self, x):
        return self._table[LG.freeze(x)]


def list_task(name, target, out, seed, n, words=(), truth_words=()):
    rng = np.random.default_rng([seed, 311, n])
    examples = [tuple(_random_list(rng)) for _ in range(3)]
    pool = [tuple(_random_list(rng)) for _ in range(40)]
    fresh = lambda r: tuple(_random_list(r))
    return Exact('code', name, lambda x: target(list(x)), {'l': 'list'}, out, examples, pool, fresh, words,
                 truth_words)


def number_task(name, target, seed, n, words=(), truth_words=()):
    rng = np.random.default_rng([seed, 313, n])
    examples = [1, 2, 3, 4]
    pool = list(range(0, 13))
    fresh = lambda r: int(r.integers(0, 16))
    return Exact('math', name, target, {'n': 'num'}, 'num', examples, pool, fresh, words, truth_words)


# ============================================================ puzzles (ARC: lists of lists)
GRID = 'list(list)'


def to_grid(x):
    return tuple(tuple(int(v) for v in row) for row in x)


def is_grid(v):
    """The world's form of an answer: 1 to 30 rows of equal length (1 to 30), each value a colour 0 to 9."""
    if not isinstance(v, tuple) or not 1 <= len(v) <= 30:
        return False
    w = None
    for row in v:
        if not isinstance(row, tuple) or not 1 <= len(row) <= 30 or (w is not None and len(row) != w):
            return False
        w = len(row)
        if any(isinstance(c, bool) or not isinstance(c, int) or not 0 <= c <= 9 for c in row):
            return False
    return True


class Puzzle(Exact):
    """An ARC puzzle as a world: its example pairs and its test inputs are seen (the test outputs are the observer's),
    and nothing can be asked. SERA's answer is a program from a grid to a grid."""
    audit_words = 'examples it was given'

    def __init__(self, pid, puzzle):
        self.subject, self.name, self.pid = 'puzzles', f'arc {pid}', pid
        self._target = None
        self.inputs, self.out = {'g': GRID}, GRID
        self.var = 'g'
        self.data = [(to_grid(p['input']), to_grid(p['output'])) for p in puzzle['train']]
        self.tests = [to_grid(p['input']) for p in puzzle['test']]
        self._answers = [to_grid(p['output']) for p in puzzle['test'] if 'output' in p]
        self.pool = []
        self._probe_inputs = [x for x, _ in self.data] + self.tests
        self._fresh = None
        self.words, self._truth_words, self.asked = [], set(), 0
        self._miss = {}

    def probes(self):
        return [{'g': x} for x in self._probe_inputs]

    def _misses(self, e, concepts):
        m = self._miss.get(e)
        if m is None:
            m = self._miss[e] = sum(LG.safe(e, {'g': x}, concepts) != y for x, y in self.data)
        return m

    def evidence(self, exprs, concepts):
        """MISS_NATS per example a program gets wrong (as every exact world), each program weighed once here."""
        return {e: -MISS_NATS * self._misses(e, concepts) for e in exprs}

    def evidence_values(self, found, concepts):
        out = {}
        for e, _, vals in found:                   # the examples are its first probes
            m = sum(vals[j] != y for j, (_, y) in enumerate(self.data))
            self._miss.setdefault(e, m)
            out[e] = -MISS_NATS * m
        return out

    def consistent(self, e, concepts):
        return self._misses(e, concepts) == 0

    def actions(self, rng, exprs, weights, concepts):
        return []

    def answers(self, e, concepts):
        return [LG.safe(e, {'g': x}, concepts) for x in self.tests]

    def verify(self, e, concepts, bits, rng):
        """The judge: every example's output exactly, and a grid on every test input (the world's form of an
        answer)."""
        ok = self.consistent(e, concepts) and all(is_grid(v) for v in self.answers(e, concepts))
        if CR.on('judge_scrutiny'):
            _, record = scrutiny(self)
            record.update(baseline_accepted=bool(ok), accepted=bool(ok), budget=0,
                          scope='given examples and grid form; no fresh-answer oracle')
        return ok, len(self.data), None

    def right(self, e, concepts):
        return e is not None and bool(self._answers) and self.answers(e, concepts) == self._answers

    def grade(self, e, concepts, accepted, n=200, seed=0):
        """The observer: the test outputs (never shown to SERA)."""
        right = self.right(e, concepts)
        if accepted:
            return dict(verdict='proven right' if right else 'accepted, wrong on the test')
        return dict(verdict='right, unproven' if right else 'not proven')

    def context(self):
        """What it perceives of a puzzle before thinking - its senses of lists of lists, nothing named: how the outputs'
        lengths go with the inputs' (the outer list's, and what it holds), whether an output keeps its input's shape,
        how long the inputs are, and how many different values each side holds."""
        def shape(g):
            return len(g), (len(g[0]) if g else 0)

        def kinds(g):
            return len({v for row in g for v in row})
        pairs = [(shape(x), shape(y), kinds(x), kinds(y)) for x, y in self.data]
        m = lambda f: float(np.mean([f(p) for p in pairs]))
        return [m(lambda p: math.log2((p[1][0] + 1) / (p[0][0] + 1))),
                m(lambda p: math.log2((p[1][1] + 1) / (p[0][1] + 1))),
                m(lambda p: float(p[0] == p[1])), m(lambda p: p[0][0] / 30), m(lambda p: p[0][1] / 30),
                m(lambda p: p[2] / 10), m(lambda p: p[3] / 10)]

    def teacher_truth(self, word):
        return False


# === stories (language): lists of word symbols
VOCAB = {}
WORDS = {}                              # symbol -> token
_NEXT = [100]                           # the next word's symbol


def sym(token):
    token = str(token).lower()
    if token not in VOCAB:
        value = _NEXT[0]
        _NEXT[0] += 1
        VOCAB[token] = value
        WORDS[value] = token
    return VOCAB[token]


def adopt(vocab):
    """The words of a saved SERA, as it read them (S03, reviewer: a new run numbered words afresh, so a loaded Field's
    ideas would name other words). A word, or a symbol, already taken otherwise in this run is a conflict: refused."""
    for token, value in sorted(vocab.items(), key=lambda kv: kv[1]):
        if VOCAB.get(token, value) != value or WORDS.get(value, token) != token:
            raise ValueError(f"the saved Field reads '{token}' as {value}; this run reads it as {VOCAB.get(token)} "
                             f"and {value} as '{WORDS.get(value)}' - load the Field before any world is made")
    for token, value in vocab.items():
        VOCAB[token] = value
        WORDS[value] = token
    _NEXT[0] = max([_NEXT[0]] + [v + 1 for v in vocab.values()])


def _symbols(v):
    """A worked step's value as the world's symbols: a word, a sentence (a list of words) or sentences."""
    if isinstance(v, (list, tuple)):
        return tuple(_symbols(u) for u in v)
    return sym(v)


def text(v):
    if isinstance(v, (int, np.integer)) and int(v) in WORDS:
        return WORDS[int(v)]
    if isinstance(v, (tuple, list)):
        return ' '.join(text(x) for x in v)
    return str(v)


NAMES = ('mary', 'john', 'sandra', 'daniel')
PLACES = ('kitchen', 'garden', 'office', 'hallway', 'bathroom', 'bedroom')
VERBS = ('went', 'moved', 'travelled', 'journeyed')
for _t in NAMES + PLACES + VERBS + ('to', 'the', 'what', 'is', 'first', 'last', 'word', 'who', 'where', 'in', 'yes',
                                    'no', 'or'):
    sym(_t)                              # the world's own words get the same symbols in every run


def _where_story(r, n_min=3, n_max=7):
    """Sentences where one name appears at least twice, anywhere (not always first or last: no shortcut by place)."""
    ss = [_sentence(r) for _ in range(int(r.integers(n_min, n_max)))]
    who = str(r.choice(NAMES))
    for k in r.choice(len(ss), size=2, replace=False):
        ss[int(k)][0] = who
    return ss, who


class Story(Exact):
    """A language world whose sentences and answers are lists of word symbols."""
    form = 'exact'

    def __init__(self, name, make, seed, words=(), truth_words=(), n_examples=4, n_pool=40):
        self.subject, self.name = 'language', name
        self.inputs, self.out, self.var = {'g': 'list(list)'}, None, 'g'
        self.words = list(words)
        self._truth_words = set(truth_words or words)
        self.asked = 0
        self._key = {}
        self._worked = {}
        self._seen = {}
        self._make_fn = make
        self._rng = np.random.default_rng([seed, 331, len(name)])
        examples = [self._make(self._rng)[0] for _ in range(n_examples)]
        pool = [self._make(self._rng)[0] for _ in range(n_pool)]
        self.data = [(x, self._key[LG.freeze(x)]) for x in examples]
        self.pool = pool
        self._probe_inputs = examples + pool[:16]
        self._fresh = lambda r: self._make(r)[0]
        self.out = 'list' if self.data and isinstance(self.data[0][1], tuple) else 'num'

    def _make(self, rng):
        got = self._make_fn(rng)
        sentences, question, answer = got[:3]
        x = tuple(tuple(sym(t) for t in sent) for sent in [question] + sentences)
        y = tuple(sym(t) for t in answer) if isinstance(answer, list) else sym(answer)
        self._key[LG.freeze(x)] = y
        if len(got) > 3 and self.words:                  # the teacher's worked steps (a taught lesson only)
            self._worked[LG.freeze(x)] = tuple(_symbols(v) for v in got[3])
        return x, y

    def _y(self, x):
        return self._key[LG.freeze(x)]

    def sentences(self, x):
        """The story's sentences, as SERA reads them (not the question)."""
        return [tuple(s) for s in x[1:]]

    def numbers(self, most=6):
        """The words it heard in the lesson (the teacher's words), as it has the numbers it sees in a task: words it
        can say, not only words it can point at in what it reads (2026-09-30, the author: "I want to be able to
        converse" - to answer 'is mary in the kitchen?' it must be able to say yes or no). None when alone."""
        if not CR.on('lesson_words'):                  # the crutch off: the numbers it sees, as before 86cf3e5
            return super().numbers(most)
        return [sym(w) for w in self.words][:most]

    def worked(self, x):
        """The teacher's worked steps for an example (2026-09-29, the author: "teach sera how to break down problems
        into pieces"): what each step makes, as the teacher would say it ("who is it about? mary; which sentence?
        mary went to the kitchen"), never a program - SERA finds its own step that makes it. None in a lesson without
        a teacher, or for an example the teacher did not work."""
        return self._worked.get(LG.freeze(x))

    mind = None                                          # SERA's Field of ideas (set by SERA as it lives the world)

    def perceive(self, x):
        """The situation as SERA takes it in (2026-09-29, the author: its memory is part of the Field and influences
        it): the question and the story, and - for what the question names that the story does not tell of - what
        comes to mind from what it has read (sera.phi.Ideas.comes_to_mind), after the story. With no memory, or when
        the story tells of everything the question names, the situation is just what it sees."""
        if self.mind is None:
            return x
        key = (getattr(self.mind, 'gen', None) or id(self.mind), getattr(self.mind, 'rev', self.mind.read_n), x)   # its own name, not an address
        hit = self._seen.get(key)                                                        # reused (S03, reviewer)
        if hit is not None:
            return hit
        told = {w for s in x[1:] for w in s}
        missing = [w for w in x[0] if w not in told]
        extra = tuple(s[:LG.MAX_LEN] for s in self.mind.comes_to_mind(missing) if s not in x[1:]) if missing else ()
        #   a long sentence comes to mind as its first MAX_LEN words, what its language can hold (2026-09-29: one of
        #   Plato's 100-word sentences made every program on the situation fail - 'too long' - even where the
        #   definition had come to mind first)
        out = x + extra
        self._seen[key] = out
        return out

    def probes(self):
        return [{'g': self.perceive(x)} for x in self._probe_inputs]

    def _value(self, e, x, concepts):
        return LG.safe(e, {'g': self.perceive(x)}, concepts)

    def consistent(self, e, concepts):
        return all(LG.safe(e, {'g': self.perceive(x)}, concepts) == y for x, y in self.data)

    def evidence(self, exprs, concepts):
        return {e: -MISS_NATS * sum(LG.safe(e, {'g': self.perceive(x)}, concepts) != y for x, y in self.data)
                for e in exprs}

    def actions(self, rng, exprs, weights, concepts):
        seen = {LG.freeze(x) for x, _ in self.data}
        out = []
        for x in self.pool:
            if LG.freeze(x) in seen:
                continue
            ys = [LG.safe(e, {'g': self.perceive(x)}, concepts) for e in exprs]
            groups = {}
            for y, w in zip(ys, weights):
                groups[repr(y)] = groups.get(repr(y), 0.0) + w
            total = sum(groups.values())
            info = -sum(p / total * math.log(p / total) for p in groups.values() if p > 0) if total else 0.0
            out.append(dict(action=('ask', x), info=info, novel=0.0, predicted=ys[0] if ys else None))
        return out

    def act(self, action):
        x = action[1]
        y = self._y(x)
        self.data.append((x, y))
        self.asked += 1
        return x, y

    def verify(self, e, concepts, bits, rng):
        n = S.audit_size(bits)
        for _ in range(n):
            x = self._fresh(rng)
            y = self._y(x)
            if LG.safe(e, {'g': self.perceive(x)}, concepts) != y:
                self.data.append((x, y))
                if CR.on('judge_scrutiny'):
                    return self._scrutinize(e, concepts, n, (x, y), rng)
                return False, n, (x, y)
        if CR.on('judge_scrutiny'):
            return self._scrutinize(e, concepts, n, None, rng)
        return True, n, None

    def grade(self, e, concepts, accepted, n=200, seed=0):
        rng = np.random.default_rng([seed, 991, len(self.name)])
        agree = all(LG.safe(e, {'g': self.perceive(x)}, concepts) == self._y(x)
                    for x in (self._fresh(rng) for _ in range(n)))
        if accepted:
            return dict(verdict='proven right' if agree else 'SURE AND WRONG')
        return dict(verdict='right, unsure' if agree else 'not proven')

    def context(self):
        """What it perceives before thinking, from the inputs only (S02, reviewer: features computed from the answers
        leaked them): how many sentences, how long, how long the question is, whether an answer is a list, how many
        different words a story holds, and how many of the question's words are in the story."""
        xs = [x for x, _ in self.data]
        is_list = self.out == 'list'
        kinds = [len({w for s in x for w in s}) for x in xs]
        shared = [np.mean([any(w in s for s in x[1:]) for w in x[0]]) if x[0] else 0.0 for x in xs]
        return [float(np.mean([max(0, len(x) - 1) for x in xs])) / 10,
                float(np.mean([np.mean([len(s) for s in x[1:]]) if len(x) > 1 else 0 for x in xs])) / 10,
                float(np.mean([len(x[0]) for x in xs])) / 10, float(is_list),
                float(np.mean(kinds)) / 30, float(np.mean(shared)), 0.0]

    def teacher_truth(self, word):
        return word in self._truth_words

    def show(self, x):
        q = text(x[0])
        story = '; '.join(text(s) for s in x[1:])
        return f'story: {story} | question: {q}'


def is_words(v):
    """A word it knows, or words: what it can say (S06 F6, reviewer: a number, a float or a list of lists is not)."""
    def word(u):
        return isinstance(u, int) and not isinstance(u, bool) and u in WORDS
    return word(v) or (isinstance(v, tuple) and len(v) > 0 and all(word(u) for u in v))


class Talk:
    """A conversation (2026-09-30; the author: "I want to be able to converse with it"; S06 F5, reviewer: which idea answers
    a question belongs in SERA - taught and graded - not in an interface). The questions of its lessons, mixed as they
    come in a talk, each with its story, and some about someone the story does not tell of (the right reply: it does
    not know). Nothing to search for: what it learns here is which of its proven ideas a question calls for - what
    rings in its Field for it - from a teacher who says the answer after it replies (sera.one.Sera.converse); alone,
    it replies and the observer grades (never shown to it)."""
    form = 'talk'
    subject = 'language'
    mind = None
    perceive = Story.perceive                            # it takes a situation in as in its lessons

    def __init__(self, name, kinds, seed, n=40, absent=0.2):
        self.name, self.words = name, []
        self._seen = {}
        rng = np.random.default_rng([seed, 611, n])
        lessons = [k(seed + 7 * i) for i, k in enumerate(kinds)]
        self.items = []                                  # (situation, the answer or None, the kind: the observer's)
        for _ in range(n):
            if rng.random() < absent:                    # someone it was never told of, here or in any story it
                ss = [_sentence(rng) for _ in range(int(rng.integers(1, 4)))]   # read (a name of its lessons may
                who = str(rng.choice(READERS))                                    # come to mind from another story)
                x = tuple(tuple(sym(t) for t in s) for s in [['where', 'is', who]] + ss)
                self.items.append((x, None, 'absent'))
            else:
                k = lessons[int(rng.integers(len(lessons)))]
                x, y = k._make(rng)
                self.items.append((x, y, k.name))

    def sentences(self, x):
        return [tuple(s) for s in x[1:]]


# ---- understanding that does not depend on where a word sits (plan 7.11 step 3; review 8, design D): small abilities
# taught as their own worlds - is a word among others, the story rows about the question, the latest of them - then
# "where" asked in several frames, the name anywhere, and "is X in the P" answered yes or no. The worlds and the
# teacher's words are the teacher's; every program is SERA's own (none is given; a helper must pass its own audit).
FRAMES_WHERE = (('where', 'is', '*'), ('where', 'did', '*', 'go'), ('*', 'is', 'where'))
FRAME_UNSEEN = ('please', 'tell', 'me', 'where', '*', 'is')        # the evaluation's frame, never taught
_UPOOL = tuple(str(w) for w in NAMES + PLACES + VERBS + ('to', 'the'))


def _frame(frame, who):
    return [who if w == '*' else w for w in frame]


def _among(r):
    """A first word and the words after it; half the time the first is among them."""
    n = int(r.integers(2, 6))
    ws = [str(w) for w in r.choice(_UPOOL, size=n + 1, replace=False)]
    if r.random() < 0.5:
        ws[1 + int(r.integers(n))] = ws[0]
    return tuple(sym(w) for w in ws)


def _situation(r, frames=FRAMES_WHERE, names=NAMES, places=PLACES):
    """(question, rows...) in word symbols, and who it asks about: 2-5 rows 'name verb to the place', the asked name in
    1-2 of them at any place (its latest row is where it is now), the question one of the frames."""
    n = int(r.integers(2, 6))
    rows = []
    for _ in range(n):
        rows.append([str(r.choice(names)), str(r.choice(VERBS)), 'to', 'the', str(r.choice(places))])
    who = rows[int(r.integers(n))][0]
    if r.random() < 0.5 and n > 2:                    # sometimes again, later: where it is now
        k = int(r.integers(n))
        rows[k][0] = who
    q = _frame(frames[int(r.integers(len(frames)))], who)
    return tuple(tuple(sym(w) for w in s) for s in [q] + rows), sym(who)


def _rows_about(g):
    return tuple(row for row in g[1:] if row and row[0] in g[0])


def _exact(name, make, target, inputs, out, seed, words, n_examples=4):
    rng = np.random.default_rng([seed, 709, len(name)])
    xs = [make(rng) for _ in range(n_examples + 40)]
    return Exact('language', name, target, inputs, out, xs[:n_examples], xs[n_examples:], make, words=words)


def lesson_among(seed):
    """Is the first word among the words after it? It, if so; else nothing (0)."""
    return _exact('among', _among, lambda x: x[0] if x[0] in x[1:] else 0, {'w': 'list'}, 'num', seed,
                  ('among',))


def lesson_is_among(seed):
    """Is the first word among the words after it? True or false."""
    return _exact('is among', _among, lambda x: x[0] in x[1:], {'w': 'list'}, 'bool', seed, ('is', 'among'))


def lesson_rows_about(seed):
    """The rows of a story about what the question names (whose first word is in the question), the name anywhere."""
    return _exact('rows about', lambda r: _situation(r)[0], _rows_about, {'g': 'list(list)'}, 'list(list)', seed,
                  ('rows', 'about'))


def lesson_latest_row(seed):
    """The latest of those rows."""
    return _exact('latest row', lambda r: _situation(r)[0],
                  lambda g: (_rows_about(g) or ((),))[-1], {'g': 'list(list)'}, 'list', seed, ('latest', 'row'))


def lesson_where_any(seed):
    """Where is the one the question names now - asked in several ways, the name anywhere in the question."""
    def make(r):
        g, who = _situation(r)
        theirs = [list(text(w) for w in row) for row in g[1:] if row[0] == who]
        q = [text(w) for w in g[0]]
        return ([list(text(w) for w in row) for row in g[1:]], q, theirs[-1][-1], [theirs, theirs[-1]])
    return _story('where any', make, seed, ('where',))


def lesson_is_in_any(seed):
    """Is the one it names in the place it names? Yes or no - the name and the place anywhere in the question."""
    frames = (('is', '*', 'in', 'the', '+'), ('is', '*', 'now', 'in', 'the', '+'), ('in', 'the', '+', 'is', '*'))

    def make(r):
        g, who = _situation(r)
        rows = [[text(w) for w in row] for row in g[1:]]
        now = [row for row in rows if row[0] == text(who)][-1][-1]
        yes = bool(r.integers(2))
        place = now if yes else str(r.choice([p for p in PLACES if p != now]))
        f = frames[int(r.integers(len(frames)))]
        q = [text(who) if w == '*' else place if w == '+' else w for w in f]
        return rows, q, 'yes' if yes else 'no'
    return _story('is in any', make, seed, ('is', 'yes', 'no'))


def where_any_eval(seed, n=20, renamed=False):
    """The observer's test of a where ability: n new stories, each asked in the three taught frames and one never
    taught - [(situation, the answer, the frame)]; renamed: names and places are new words (never read, never
    taught)."""
    r = np.random.default_rng([seed, 733, int(renamed)])
    names = tuple(f'nm{i}x' for i in range(6)) if renamed else NAMES
    places = tuple(f'pl{i}x' for i in range(6)) if renamed else PLACES
    out = []
    for _ in range(n):
        g, who = _situation(r, frames=FRAMES_WHERE[:1], names=names, places=places)
        rows = g[1:]
        now = [row for row in rows if row[0] == who][-1][-1]
        for k, frame in enumerate(FRAMES_WHERE + (FRAME_UNSEEN,)):
            q = tuple(sym(w) for w in _frame(frame, text(who)))
            out.append(((q,) + rows, now, 'unseen' if k == len(FRAMES_WHERE) else ' '.join(frame)))
    return out


def talk_world(seed, n=40):
    """The talk of its lessons' questions (those it may have learned): where, who is in, where now, is in, what is -
    and "what is the first / last word", which begin as "what is <a word>" does but call for other ideas (S07 F7, reviewer:
    the kinds were told apart by their first word alone)."""
    return Talk('talk', (lesson_where, lesson_who_in, lesson_where_now, lesson_is_in, lesson_what_is, lesson_first,
                         lesson_last), seed, n=n)


def _sentence(rng):
    name, verb, place = rng.choice(NAMES), rng.choice(VERBS), rng.choice(PLACES)
    return [str(name), str(verb), 'to', 'the', str(place)]


def _story(name, make, seed, words=(), truth_words=()):
    return Story(name, make, seed, words=words, truth_words=truth_words)


def lesson_first(seed):
    def make(r):
        s = _sentence(r)
        return [s], ['what', 'is', 'the', 'first', 'word'], s[0]
    return _story('first', make, seed, ('first', 'word'))


def lesson_last(seed):
    vocab = list(NAMES + PLACES + VERBS + ('to', 'the'))
    def make(r):
        s = [str(x) for x in r.choice(vocab, size=int(r.integers(3, 7)))]
        return [s], ['what', 'is', 'the', 'last', 'word'], s[-1]
    return _story('last', make, seed, ('last', 'word'))


def lesson_who(seed):
    def make(r):                                         # 2-3 sentences, each to its own place (S02, reviewer: with one
        n = int(r.integers(2, 4))                        # sentence, 'the first word' passed without the question)
        places = [str(p) for p in r.choice(PLACES, size=n, replace=False)]
        ss = [_sentence(r) for _ in range(n)]
        for s, p in zip(ss, places):
            s[-1] = p
        k = int(r.integers(n))
        return ss, ['who', 'went', 'to', 'the', places[k]], ss[k][0], [places[k], ss[k]]   # worked: the place, its
    return _story('who', make, seed, ('who',))                                             # sentence


def lesson_where(seed):
    def make(r):
        names = list(r.choice(NAMES, size=int(r.integers(2, 5)), replace=False))
        ss = []
        for n in names:
            s = _sentence(r); s[0] = str(n); ss.append(s)
        s = ss[int(r.integers(len(ss)))]
        return ss, ['where', 'is', s[0]], s[-1], [s[0], s]          # worked: who it is about, their sentence
    return _story('where', make, seed, ('where', 'is'))


def lesson_where_now(seed):
    def make(r):
        ss, who = _where_story(r)
        place = next(s[-1] for s in reversed(ss) if s[0] == who)
        theirs = [s for s in ss if s[0] == who]
        return ss, ['where', 'is', who], place, [who, theirs, theirs[-1]]   # worked: who, their sentences, the last
    return _story('where now', make, seed, ('where', 'is', 'now'))


def lesson_who_in(seed):
    def make(r):
        names = list(r.choice(NAMES, size=int(r.integers(2, 5)), replace=False))
        places = list(r.choice(PLACES, size=len(names), replace=False))
        ss = []
        for n, p in zip(names, places):
            s = _sentence(r); s[0], s[-1] = str(n), str(p); ss.append(s)
        s = ss[int(r.integers(len(ss)))]
        return ss, ['who', 'is', 'in', 'the', s[-1]], s[0], [s[-1], s]   # worked: the place, its sentence
    return _story('who in', make, seed, ('who', 'is', 'in'))


def lesson_is_in(seed):
    def make(r):
        names = list(r.choice(NAMES, size=int(r.integers(2, 5)), replace=False))
        ss = []
        for n in names:
            s = _sentence(r); s[0] = str(n); ss.append(s)
        s = ss[int(r.integers(len(ss)))]
        yes = bool(r.integers(2)); place = s[-1] if yes else str(r.choice([p for p in PLACES if p != s[-1]]))
        return (ss, ['is', s[0], 'in', 'the', place], 'yes' if yes else 'no',   # asked as we ask (2026-09-30: the
                [s[0], s, s[-1]])                          # answer words are the teacher's, heard, not fetched
        #                                                    from the question's sixth and eighth places); worked:
        #                                                    who, their sentence, where they are
    return _story('is in', make, seed, ('is', 'yes', 'no'))


_FALLBACK_WORDS = ('amber', 'birch', 'cabin', 'daisy', 'eagle', 'fable', 'giant', 'harbor', 'island', 'jungle',
                   'kitten', 'ladder', 'marble', 'nectar', 'otter', 'planet', 'quartz', 'rabbit', 'saddle',
                   'temple', 'umbrella', 'velvet', 'window', 'yellow', 'zephyr', 'acorn', 'basket', 'copper',
                   'dragon', 'engine')
_FALLBACK_GLOSS = ('a', 'small', 'large', 'kind', 'of', 'stone', 'tree', 'house', 'flower', 'bird', 'story', 'person',
                   'place', 'water', 'land', 'animal', 'thing', 'made', 'used', 'for', 'with', 'old', 'bright', 'soft')
_FALLBACK = tuple(f'{w} is ' + ' '.join(_FALLBACK_GLOSS[(7 * i + 3 * j) % len(_FALLBACK_GLOSS)]
                                        for j in range(3 + i % 5))
                  for i, w in enumerate(_FALLBACK_WORDS))  # each its own made-up definition (S02, reviewer: one shared
                                                          # definition let 'the first sentence's' pass)


def _what_make(sentences):
    def make(r):
        groups = {}
        for sentence in sentences:
            groups.setdefault(sentence[0], []).append(list(sentence))
        words = sorted(groups)
        size = min(int(r.integers(2, 5)), len(words))
        ids = r.choice(len(words), size=size, replace=False)
        ss = [groups[words[int(i)]][int(r.integers(len(groups[words[int(i)]])))] for i in ids]
        chosen = int(r.integers(len(ss)))
        sent = ss[chosen]
        return ss, ['what', 'is', sent[0]], sent[2:]
    return make


def _gloss_sentences(rng, book=None, fallback=None):
    if book is None:
        src = [s.split() for s in (fallback or _FALLBACK)]
    else:
        terms = sorted(book.senses)
        if len(terms) > 200:
            terms = [terms[i] for i in rng.choice(len(terms), 200, replace=False)]
        src = []
        for word in terms:
            if not word.isascii() or not word.isalpha():
                continue
            glosses = book.says(word)
            if not glosses: continue
            tokens = glosses[0].lower().partition(') ')[2].split()
            tokens = [t for t in tokens if t.isascii() and t.isalpha()]
            if 3 <= len(tokens) <= 8:
                src.append([word] + ['is'] + tokens)
    return [s for s in src if len(s) >= 5]


def lesson_what_is(seed):
    rng = np.random.default_rng([seed, 337])
    ss = _gloss_sentences(rng, TK.BOOK)
    if len(ss) < 4: ss = [s.split() for s in _FALLBACK]
    def make(r):
        ids = r.choice(len(ss), size=int(r.integers(2, 5)), replace=False)
        selected = [ss[int(i)] for i in ids]
        k = int(r.integers(len(selected)))                            # any sentence, not always the first
        return (selected, ['what', 'is', selected[k][0]], selected[k][2:],
                [selected[k][0], selected[k]])                        # worked: the word, its sentence
    return _story('what is', make, seed, ('what', 'is'))


def lesson_where_first(seed):
    def make(r):
        ss, who = _where_story(r)
        place = next(s[-1] for s in ss if s[0] == who)
        return ss, ['where', 'is', who], place
    return _story('where first', make, seed, (), ('where', 'first'))


def lesson_who_went(seed):
    def make(r):
        n = int(r.integers(2, 5))
        places = [str(p) for p in r.choice(PLACES, size=n, replace=False)]      # one sentence per place: one answer
        ss = [_sentence(r) for _ in range(n)]
        for s, p in zip(ss, places):
            s[-1] = p
        k = int(r.integers(n))
        return ss, ['who', 'went', 'to', 'the', places[k]], ss[k][0]
    return _story('who went', make, seed, (), ('who', 'went'))


def lesson_what_is_alone(seed):
    rng = np.random.default_rng([seed, 338])                      # other words of the book than it was taught with
    taught = {s[0] for s in _gloss_sentences(np.random.default_rng([seed, 337]), TK.BOOK)}
    ss = [s for s in _gloss_sentences(rng, TK.BOOK) if s[0] not in taught] or [s.split() for s in _FALLBACK]
    return _story('what is alone', _what_make(ss), seed, (), ('what', 'is'))


# ---- closed book (2026-09-29, the author: "let sera read the books or short stories and answer in a closed book
# scenario; if it can't answer there might be a flaw in teaching or learning"): a passage it reads first, then
# questions with the passage gone - only the question is its input; what it read is in its memory (sera.phi.Ideas),
# which its language reaches with recall. How it answers from memory is its own: taught here, built by it.
READERS = ('adam', 'alice', 'amir', 'anna', 'ben', 'bella', 'carl', 'clara', 'dan', 'dora', 'eli', 'emma', 'finn',
           'fiona', 'gus', 'grace', 'hugo', 'hana', 'ivan', 'iris', 'jack', 'jade', 'karl', 'kate', 'leo', 'lily',
           'max', 'mia', 'ned', 'nora', 'otto', 'olga', 'paul', 'pia', 'quin', 'rosa', 'sam', 'sara', 'tom', 'tara',
           'umar', 'una', 'vic', 'vera', 'walt', 'wren', 'yuri', 'zoe')            # not the lessons' names


class ClosedBook(Story):
    """Read a passage, then answer about it with the passage gone (the question alone is the input)."""

    def __init__(self, name, passage, pool, seed, words=(), truth_words=(), worked=None):
        self._passage = [tuple(sym(t) for t in s) for s in passage]
        self._pool_q = list(pool)                   # (question tokens, answer) the world may ask
        self._worked_of = worked or {}
        def make(r):
            q, a = self._pool_q[int(r.integers(len(self._pool_q)))]
            w = self._worked_of.get(' '.join(q))
            return ([], list(q), a) + ((w,) if w is not None else ())
        super().__init__(name, make, seed, words=words, truth_words=truth_words)

    def reading(self):
        """What it reads before any question."""
        return list(self._passage)

    def sentences(self, x):
        return []                                   # nothing to read in a question


def closed_where(seed, taught=True, names=READERS):
    """A passage of who went where (each name once), then 'where is <name>?' with the passage gone."""
    rng = np.random.default_rng([seed, 541])
    who = [str(n) for n in rng.permutation(names)[:30]]
    passage, pool, worked = [], [], {}
    for n in who:
        s = [n, str(rng.choice(VERBS)), 'to', 'the', str(rng.choice(PLACES))]
        passage.append(s)
        q = ['where', 'is', n]
        pool.append((q, s[-1]))
        worked[' '.join(q)] = [n, [s], s]           # worked: who it is about, what it remembers of them, their sentence
    return ClosedBook('closed where', passage, pool, seed, words=('where', 'is') if taught else (),
                      truth_words=('where', 'is'), worked=worked if taught else None)


def closed_what_is(seed, taught=True, sentences=None):
    """A passage of definitions (from the dictionary, or given), then 'what is <word>?' with the passage gone.
    A given source that is empty is refused, never replaced by the dictionary's (S03 F13, reviewer)."""
    rng = np.random.default_rng([seed, 543])
    ss = [list(s) for s in (sentences if sentences is not None else _gloss_sentences(rng, TK.BOOK))]
    if not ss:
        raise ValueError('closed what is: no sentences to read (the source is empty)')
    seen, uniq = set(), []
    for s in ss:                                    # one definition per word: one answer
        if s[0] not in seen:
            seen.add(s[0])
            uniq.append(s)
    uniq = [uniq[int(i)] for i in rng.permutation(len(uniq))[:40]]
    pool = [(['what', 'is', s[0]], s[2:]) for s in uniq]
    worked = {' '.join(['what', 'is', s[0]]): [s[0], [s], s] for s in uniq}
    return ClosedBook('closed what is', uniq, pool, seed, words=('what', 'is') if taught else (),
                      truth_words=('what', 'is'), worked=worked if taught else None)


def book_what_is(sentences, seed):
    ss = [list(s) for s in sentences]
    return _story('book what is', _what_make(ss), seed, ())
