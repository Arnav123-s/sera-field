"""World generator for SERA v3 (B1): hidden laws by level, in the ccops5 world format the judge already reads.

Levels (every level is certifiable by the frozen judge, tag truth-v1):
  L0 no force; L1 one base idea; L2 two base ideas; L3 one invented term alone (x*v-like product, |s|^p, sin/cos wt);
  L4 one invented term with one base idea;
  L5 "surface and deeper": a law of two terms whose second term is too weak to see in the teacher's pushes and only
     shows in harder pushes (a correct surface law hides a deeper one).
Laws beyond the frozen judge (three terms, new pieces such as |v| or other saturations, a second hidden number per
object) arrive in B4 with decision D11.

Held-out structures (`held_out`) are never dreamed: they test whether the imagination composes pieces it has seen
into laws it has not. The evaluation suite draws from them and from fresh seeds.

Every world is validated before use ((review notes, not published) rules, strengthened after independent review F3): finite and bounded
paths, no acceleration clip, and the truth is identifiable where a wrong claim could otherwise be certified: for a base
law (always among the laws the judge weighs), every sub-law misses the true force by at least EFFECT (>= 2 eps); for an
invented law (possibly absent from the ledger), every other certifiable law that does not contain it (other ideas,
base pairs, neighbouring exponents and frequencies, other products) misses it by EFFECT, on the teacher's throws.
So the strict (frozen) definition of "sure and wrong" is fair. L5 instead requires its weak term to be invisible on the
teacher's throws (< HIDE) and visible on a hard push (> SHOW).
"""
import dataclasses

import numpy as np

from ccops5 import puzzles as P
from ccops5.core import curriculum, grammar, paths, worlds as W
from . import lawspace as LS

EFFECT = 0.4                     # force units, >= 2 eps (eps 0.2): every law that could be claimed instead of the truth
                                 # misses the true force by at least this much somewhere on the teacher's throws
HIDE, SHOW = 0.1, 0.8            # L5: the deeper term's gap below HIDE on the teacher's throws, above SHOW on a hard push
IDEA_RANGE = {idea: rng for idea, rng in P.FORCES.values()}
IDEA_RANGE[('speed', 'wave')] = (1.0, 3.0)
OPEN_RANGE = {'product': (0.5, 1.5), 'power': {'speed': (1.0, 3.0), 'position': (3.0, 9.0)}, 'drive': (0.5, 1.5)}
L5_LAWS = ((('speed', 'straight'), ('speed', 'growing')), (('position', 'straight'), ('position', 'cubic')),
           (('speed', 'straight'), ('speed', 'cubic')))
HARD_PUSH = W.Action(((0.0, 1.2, 1.5),))           # the depth probe: long and strong

HELD_OUT_PRODUCTS = {('cubic', 'steps'), ('wave', 'growing'), ('steps', 'cubic'), ('growing', 'wave'),
                     ('straight', 'cubic')}
HELD_OUT_PAIRS = {grammar.canonical(p) for p in ((('position', 'wave'), ('speed', 'growing')),
                                                 (('position', 'cubic'), ('speed', 'steps')),
                                                 (('position', 'steps'), ('speed', 'cubic')))}


def held_out(family):
    """True for laws the imagination never dreams (structural generalization tests)."""
    fam = grammar.canonical(family)
    if fam in HELD_OUT_PAIRS:
        return True
    for t in fam:
        if t[0] == 'product' and (t[1], t[2]) in HELD_OUT_PRODUCTS:
            return True
        if t[0] == 'power' and 2.1 <= t[2] <= 2.9:
            return True
        if t[0] == 'drive' and 6.1 <= t[2] <= 7.0:
            return True
    return False


def _open_term(rng, ops=('product', 'power', 'drive')):
    op = rng.choice(list(ops))
    if op == 'product':
        return ('product', str(rng.choice(grammar.SHAPES)), str(rng.choice(grammar.SHAPES)))
    if op == 'power':
        return ('power', str(rng.choice(['position', 'speed'])), float(rng.choice(LS.P_VALUES)))
    return ('drive', str(rng.choice(['sin', 'cos'])), float(rng.choice(LS.W_VALUES)))


def sample_law(rng, level, split='dream', ops=('product', 'power', 'drive')):
    """A family of this level. split 'dream' never returns a held-out law; 'held' returns only held-out laws (may
    need many draws); 'any' returns either."""
    for _ in range(10_000):
        if level == 0:
            fam = ()
        elif level == 1:
            fam = (grammar.IDEAS[rng.integers(len(grammar.IDEAS))],)
        elif level == 2:
            i, j = rng.choice(len(grammar.IDEAS), size=2, replace=False)
            fam = (grammar.IDEAS[i], grammar.IDEAS[j])
        elif level == 3:
            fam = (_open_term(rng, ops),)
        elif level == 4:
            fam = (_open_term(rng, ops), grammar.IDEAS[rng.integers(len(grammar.IDEAS))])
        elif level == 5:
            fam = L5_LAWS[rng.integers(len(L5_LAWS))]
        elif level in (6, 7):                                    # truth-v2 (B4): a law that needs a grown piece
            grown = [g for g in grammar.GROWN_TERMS if g[0] != 'cell' and not (g[0] == 'piece' and g[1] == 'time')]
            term = grown[rng.integers(len(grown))]
            fam = (term,) if level == 6 else (term, grammar.IDEAS[rng.integers(len(grammar.IDEAS))])
        else:
            raise ValueError(level)
        fam = grammar.canonical(fam)
        h = held_out(fam)
        if split == 'any' or (split == 'dream') == (not h):
            return fam
    raise RuntimeError(f'no {split} law found at level {level}')


def sample_coefs(rng, family, level):
    """Coefficients in the model's form (force per unit inverse mass); negative = opposing, as in ccops5."""
    coefs = []
    for i, t in enumerate(family):
        if t[0] == 'product':
            c = -rng.uniform(*OPEN_RANGE['product'])
        elif t[0] == 'power':
            c = -rng.uniform(*OPEN_RANGE['power'][t[1]])
        elif t[0] == 'drive':
            c = rng.uniform(*OPEN_RANGE['drive']) * rng.choice([-1.0, 1.0])
        elif t[0] in ('piece', 'pprod'):                         # truth-v2 grown pieces: opposing, like drag or a spring
            c = -rng.uniform(0.5, 3.0)
        else:
            lo, hi = IDEA_RANGE[t]
            c = rng.uniform(lo, hi) * (rng.choice([-1.0, 1.0]) if t[0] == 'nothing' else -1.0)
        coefs.append(float(c))
    if level == 5:                                  # the deeper term: log-uniform strength; `validate` keeps only
        weak = [i for i, t in enumerate(family) if t[1] != 'straight']       # the window where it hides in the
        for i in weak:                                                       # teacher's pushes but not in a hard one
            coefs[i] = float(-np.exp(rng.uniform(np.log(0.05), np.log(30.0))))
    return coefs


@dataclasses.dataclass
class Spec:
    """Everything hidden about one world, as plain data (the judge's world object is built from it)."""
    seed: int
    index: int
    level: int
    family: tuple
    coefs: list
    masses: list                 # per situation
    bumps: list                  # per situation: None or (start, amplitude)
    pushes: list                 # per situation: the teacher's two commands
    checks: list                 # per situation: the held-out check command
    noise: float = 1.0

    @property
    def sigma(self):
        return (0.001 * self.noise, 0.001 * self.noise)


def sample_spec(seed, index, level, split='dream', situations=8, tricks=0.05, noise=1.0,
                ops=('product', 'power', 'drive')):
    rng = np.random.default_rng([seed, 31, level, index])
    fam = sample_law(rng, level, split, ops)
    coefs = sample_coefs(rng, fam, level)
    masses3 = [float(m) for m in rng.uniform(0.6, 2.5, size=3)]
    masses, bumps, pushes, checks = [], [], [], []
    for _ in range(situations):
        masses.append(float(rng.choice(masses3)))
        bumps.append((float(rng.choice([0.6, 0.8, 1.0, 1.2])), float(rng.choice([-1.5, 1.5])))
                     if rng.random() < tricks else None)
        pushes.append((float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0]))))
        checks.append(float(rng.choice((-0.9, -0.5, 0.5, 0.9))))
    return Spec(seed, index, level, fam, coefs, masses, bumps, pushes, checks, noise)


def build(spec):
    """The ccops5 world (a curriculum.MultiWorld) of a spec: the judge, the M1 mind and the SERA mind all live it."""
    w = curriculum.MultiWorld(spec.seed, spec.index, LS.name(spec.family), spec.family,
                              spec.coefs[0] if spec.coefs else 0.0, 0, None, [], [], spec.sigma, [], [],
                              ideas=(), coefs=(), hidden_terms=tuple(spec.family), hidden_coefs=tuple(spec.coefs))
    kinds, a, b, coefs = w._codes()
    for k in range(len(spec.masses)):
        m, bump = spec.masses[k], spec.bumps[k]
        w.masses.append(m)
        w.bumps.append(bump)
        w.teacher_pushes.append(spec.pushes[k])
        for j, u in enumerate(tuple(spec.pushes[k]) + (spec.checks[k],)):
            t0, amp = bump if bump else (0.0, 0.0)
            xs, vs = paths.simulate(W.hand(u), 1.0 / m, kinds, a, b, coefs, 1.0, 1.0, t0, amp)
            noise_rng = np.random.default_rng([spec.seed, 31, spec.level, spec.index, k, j])
            throw = W.Throw(k, len(w.throws) if j < 2 else -1, W.push_of(u),
                            xs + noise_rng.normal(0, spec.sigma[0], xs.size),
                            vs + noise_rng.normal(0, spec.sigma[1], vs.size), 'teacher' if j < 2 else 'check')
            (w.throws if j < 2 else w.held_out).append(throw)
    w.level = spec.level
    w.spec = spec
    return w


def _states(w, extra=()):
    """(x, v, t) over the teacher's throws (what every mind sees first), plus extra throws. The held-out check throws
    are never used: no mind sees them (independent review review F3b)."""
    seen = list(w.throws) + list(extra)
    times = np.arange(paths.N_OBS) * paths.DT_OBS
    return (np.concatenate([t.x for t in seen]), np.concatenate([t.v for t in seen]),
            np.concatenate([times for _ in seen]))


def _hard_throws(w):
    """Noise-free readings of the depth probe in every situation (for the L5 check only)."""
    kinds, a, b, coefs = w._codes()
    out = []
    for k, m in enumerate(w.masses):
        xs, vs = paths.simulate_program(*HARD_PUSH.arrays(), 1.0 / m, kinds, a, b, coefs, 1.0, 1.0, 0.0, 0.0)
        out.append(W.Throw(k, -1, HARD_PUSH, xs, vs, 'probe'))
    return out


def grid_twin(a, b):
    """True when two laws differ only by one grid step in one invented term's exponent or frequency (p or omega +-0.1)."""
    a, b = grammar.canonical(a), grammar.canonical(b)
    if len(a) != len(b):
        return False
    diff = [(x, y) for x, y in zip(sorted(a, key=repr), sorted(b, key=repr)) if x != y]
    if len(diff) != 1:
        return False
    (x, y), = diff
    return (x[0] == y[0] and x[0] in ('power', 'drive') and x[1] == y[1] and abs(x[2] - y[2]) <= 0.1 + 1e-9)


def grown_twin(a, b):
    """Two grown pieces that differ only by one step of their constant C (same kind, same input or parts)."""
    if a[0] != b[0] or a[0] not in ('piece', 'pprod'):
        return False
    Cs = grammar.PIECE_C
    if a[0] == 'piece':
        return (a[1], a[2]) == (b[1], b[2]) and a[2] != 'abs' and abs(Cs.index(a[3]) - Cs.index(b[3])) == 1

    def split(name):
        for pre in ('tanh', 'bell'):
            if name.startswith(pre):
                return pre, Cs.index(float(name[4:]))
        return name, None
    pa, pb = [split(n) for n in a[1:]], [split(n) for n in b[1:]]
    steps = 0
    for (na, ca), (nb, cb) in zip(pa, pb):
        if na != nb:
            return False
        if ca is not None:
            steps += abs(ca - cb)
    return steps == 1


def rival_gaps(w, xs, vs, ts, grid=False):
    """For every certifiable law that could be claimed instead of the truth (every law not containing it): the largest gap between the true force and that law's best least-squares version on these states.
    Returns {family: gap}. Vectorized: one column per term, 2x2 normal equations per pair."""
    from . import compact as C
    truth = grammar.canonical(w.spec.family)
    F = w.true_force(xs, vs, ts)
    Phi = C.columns(xs, vs, ts)
    G = Phi.T @ Phi
    b = Phi.T @ F
    out = {}
    fams = [f for f in LS.all_families() if f != truth and not grammar.contains(f, truth)
            and not (grid and grid_twin(f, truth))]   # every size (review:
    # a one-term invented truth absent from the ledger can be mimicked by a two-term law, e.g. |v|^2.5 by v|v| + v^3)
    singles = [f for f in fams if len(f) == 1]
    pairs = [f for f in fams if len(f) == 2]
    if () in fams:
        out[()] = float(np.max(np.abs(F)))
    if singles:
        idx = np.array([C.TERM_INDEX[f[0]] for f in singles])
        d = np.diag(G)[idx]
        c = np.where(d > 1e-12, b[idx] / np.where(d > 1e-12, d, 1), 0.0)
        res = np.abs(F[:, None] - Phi[:, idx] * c[None, :]).max(0)
        out.update(zip(singles, res.tolist()))
    if pairs:
        i = np.array([C.TERM_INDEX[f[0]] for f in pairs])
        j = np.array([C.TERM_INDEX[f[1]] for f in pairs])
        a11, a12, a22 = G[i, i], G[i, j], G[j, j]
        det = a11 * a22 - a12 * a12
        ok = det > 1e-10 * np.maximum(a11 * a22, 1e-300)
        ci = np.where(ok, (a22 * b[i] - a12 * b[j]) / np.where(ok, det, 1), np.where(a11 > 0, b[i] / np.maximum(a11, 1e-300), 0))
        cj = np.where(ok, (a11 * b[j] - a12 * b[i]) / np.where(ok, det, 1), 0.0)
        for s in range(0, len(pairs), 512):
            sl = slice(s, s + 512)
            res = np.abs(F[:, None] - Phi[:, i[sl]] * ci[None, sl] - Phi[:, j[sl]] * cj[None, sl]).max(0)
            out.update(zip(pairs[s:s + 512], res.tolist()))
    return out


def validate(w, grid=False):
    """(ok, reason). The rules in the module docstring (revised after independent review F3). grid=True: laws one grid
    step away (p or omega +-0.1) are not counted as rivals (the power/drive suites, scored within one grid step)."""
    for t in w.throws + w.held_out:
        if not (np.all(np.isfinite(t.x)) and np.all(np.isfinite(t.v))):
            return False, 'non-finite path'
        if np.max(np.abs(t.x)) >= 50 or np.max(np.abs(t.v)) >= 50:
            return False, 'runaway path'
    xs, vs, ts = _states(w)
    force = w.true_force(xs, vs, ts)
    if np.max(np.abs(force)) * max(1.0 / m for m in w.masses) >= 0.5 * paths.CLIP:
        return False, 'acceleration near the clip'
    fam = tuple(w.spec.family)
    if w.spec.level == 5:
        weak = [t for t in fam if t[1] != 'straight']
        surface = tuple(t for t in fam if t not in weak)
        if w._best_fit_gap(surface, xs, vs, ts) >= HIDE:
            return False, 'the deeper term already shows in the teacher pushes'
        hx, hv, ht = _states(w, _hard_throws(w))
        if w._best_fit_gap(surface, hx, hv, ht) < SHOW:
            return False, 'the deeper term does not show even on the hard push'
        return True, 'ok'
    if w.spec.level in (6, 7):
        truth_fam = grammar.canonical(fam)
        gaps = rival_gaps(w, xs, vs, ts)                          # every truth-v1 certifiable law
        from . import compact as C
        F = w.true_force(xs, vs, ts)
        for g in grammar.GROWN_TERMS:
            if g[0] == 'cell' or g in fam or grown_twin(g, next(x for x in fam if x[0] in ('piece', 'pprod'))):
                continue
            for other in [(g,)] + [(g, i) for i in grammar.IDEAS]:
                cols = [np.array([paths.term_t(k, a, b, x, v, tt, 1.0, 1.0) for x, v, tt in zip(xs, vs, ts)])
                        for tm in other for k, a, b in grammar.term_codes(tm)]
                X = np.stack(cols, 1)
                c, *_ = np.linalg.lstsq(X, F, rcond=None)
                gaps[grammar.canonical(other)] = float(np.max(np.abs(F - X @ c)))
        worst = min(gaps, key=gaps.get)
        if gaps[worst] < EFFECT:
            return False, f'not identifiable: {LS.name(worst)} mimics the law (gap {gaps[worst]:.2g})'
        return True, 'ok'
    if not any(LS.is_open(x) for x in fam):
        # A base law is always among the laws the judge weighs (every mind tracks the whole base space), and a claim
        # F is certified only if it beats every rival not containing F by the threshold. The truth fits the readings
        # exactly, so F can beat it only when the truth contains F: the sub-laws are the only way to be sure and
        # wrong here, and each must miss the true force by EFFECT.
        gaps = {fam[:i] + fam[i + 1:]: w._best_fit_gap(fam[:i] + fam[i + 1:], xs, vs, ts) for i in range(len(fam))}
    else:
        # An invented law may be absent from the ledger (only terms the imagination believes enter it), so every
        # other certifiable law not containing the truth, of any size, must miss it by EFFECT.
        gaps = rival_gaps(w, xs, vs, ts, grid)
    if not gaps:                                                 # L0: no force, nothing to leave out
        return True, 'ok'
    worst = min(gaps, key=gaps.get)
    if gaps[worst] < EFFECT:
        return False, f'not identifiable: {LS.name(worst)} mimics the law (gap {gaps[worst]:.2g})'
    return True, 'ok'


def make(seed, index, level, split='dream', situations=8, tricks=0.05, noise=1.0, tries=None,
         ops=('product', 'power', 'drive'), grid=False):
    """A validated world: the first valid spec from index, index + 100000, ... (deterministic)."""
    reasons = []
    tries = tries or (150 if grid else {5: 300, 4: 150, 6: 150, 7: 150}.get(level, 50))
    for attempt in range(tries):
        spec = sample_spec(seed, index + 100_000 * attempt, level, split, situations, tricks, noise, ops)
        w = build(spec)
        ok, why = validate(w, grid)
        if ok:
            w.rejected = reasons
            return w
        reasons.append(why)
    raise RuntimeError(f'no valid level-{level} world for seed {seed} index {index}: {reasons[-5:]}')
