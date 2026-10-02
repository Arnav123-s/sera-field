"""Dreams (B2, low compute): imagined worlds, compacted into evidence tables, to train the imagination.

A dream is a world SERA makes up: a hidden law (never a held-out one, sera.worlds.held_out), objects of hidden
masses, the teacher's pushes and some pushes of its own, noisy readings. It is simulated with the judge's own compiled
physics (one CPU thread) and compacted (sera.compact) into the table the imagination reads, with the true law as the
label. Dreams are made once and stored in shards on D: (scripts/sera_dream.py), so training reads them many times.
Cost: ~15 ms per dream on one thread (simulation ~5 ms, compaction ~10 ms).
"""
import numpy as np

from ccops5.core import grammar, paths, worlds as W
from . import lawspace as LS, simulate as S, worlds as SW

MAX_SLOTS = 8
LEVEL_WEIGHTS = np.array([0.03, 0.22, 0.25, 0.20, 0.22, 0.08])       # L0..L5
OWN_DURATIONS = (0.2, 0.4, 0.8, 1.2, 1.6)
OWN_COMMANDS = (-1.5, -1.0, -0.5, 0.5, 1.0, 1.5)
TIMES = np.arange(paths.N_OBS) * paths.DT_OBS
SCALE = {'x': 0.5, 'v': 1.0, 'a': 5.0, 'f': 1.0}                    # asinh(value / scale) normalization


def norm(value, key):
    return np.arcsinh(value / SCALE[key])


def term_np(kind, a, b, x, v, t):
    """paths.term_t, vectorized over numpy arrays (kinds 0, 4, 5, 6: the terms laws are made of)."""
    def shape(code, s):
        return {0: s, 1: s * np.abs(s), 2: np.tanh(s / 0.05), 3: s * s * s, 4: np.sin(s)}[code]
    if kind == 0:
        return np.ones_like(x) if a == 2 else shape(b, x if a == 0 else v)
    if kind == 4:
        return shape(a, x) * shape(b, v)
    if kind == 5:
        s = x if a == 0 else v
        return np.sign(s) * np.abs(s) ** (b / 10.0)
    if kind == 6:
        return np.sin(b / 10.0 * t) if a == 0 else np.cos(b / 10.0 * t)
    raise ValueError(kind)


_IDEA_CODES = [grammar.code(i) for i in grammar.IDEAS]
_BASE_PAIRS = [f for f in grammar.space() if f]                     # the 66 non-empty base families


def identifiable(family, coefs, xs, vs, ts, effect=SW.EFFECT):
    """The dream-time version of worlds.validate's term rules, vectorized: every term visibly matters, and an
    invented term is not mimicked by any base family (best-fit gaps in force units over the given states)."""
    if not family:
        return True
    cols = np.stack([term_np(*grammar.code(t), xs, vs, ts) for t in family], axis=1)
    F = cols @ np.asarray(coefs)
    for j in range(len(family)):
        rest = np.delete(cols, j, axis=1)
        if rest.shape[1] == 0:
            gap = np.max(np.abs(F))
        else:
            c, *_ = np.linalg.lstsq(rest, F, rcond=None)
            gap = np.max(np.abs(F - rest @ c))
        if gap < effect:
            return False
    if any(LS.is_open(t) for t in family):
        ideas = np.stack([term_np(k, a, b, xs, vs, ts) for k, a, b in _IDEA_CODES], axis=1)
        for fam in _BASE_PAIRS:
            idx = [grammar.IDEAS.index(i) for i in fam]
            X = ideas[:, idx]
            c, *_ = np.linalg.lstsq(X, F, rcond=None)
            if np.max(np.abs(F - X @ c)) < effect:
                return False
    return True


def _own_push(rng):
    d = float(rng.choice(OWN_DURATIONS))
    u = float(rng.choice(OWN_COMMANDS))
    if rng.random() < 0.2:                                           # a push that reverses (like pushing a swing)
        t1 = float(rng.uniform(0.4, 1.2))
        return W.Action(((0.0, 0.4, u), (t1, t1 + 0.4, -u)))
    return W.Action(((0.0, d, u),))


def dream_spec(rng, family=None):
    """One dream: (family, coefs, level, masses per slot, bumps, actions per slot). With `family`, that law is dreamed
    (the library's empty-slot predictions); otherwise a law is drawn from the dream prior (never a held-out one)."""
    if family is None:
        level = int(rng.choice(6, p=LEVEL_WEIGHTS))
        fam = SW.sample_law(rng, level, 'dream')
    else:
        fam, level = grammar.canonical(family), LS.level(family)
    coefs = SW.sample_coefs(rng, fam, level)
    n_slots = int(rng.integers(3, MAX_SLOTS + 1))
    masses3 = rng.uniform(0.6, 2.5, size=3)
    masses = [float(rng.choice(masses3)) for _ in range(n_slots)]
    bumps = [((float(rng.choice([0.6, 0.8, 1.0, 1.2])), float(rng.choice([-1.5, 1.5])))
              if rng.random() < 0.05 else None) for _ in range(n_slots)]
    actions = []
    for _ in range(n_slots):
        acts = [W.push_of(float(rng.choice([0.6, 1.0]))), W.push_of(-float(rng.choice([0.6, 1.0])))]
        acts += [_own_push(rng) for _ in range(int(rng.integers(0, 4)))]
        actions.append(acts)
    return fam, coefs, level, masses, bumps, actions


FAMILIES = LS.all_families()                                        # 3,175 laws the judge can certify
FAMILY_INDEX = {f: i for i, f in enumerate(FAMILIES)}


class Throw:
    """A dream throw: the same fields the compaction reads from a real ccops5 Throw."""
    __slots__ = ('situation', 'action', 'x', 'v')

    def __init__(self, situation, action, x, v):
        self.situation, self.action, self.x, self.v = situation, action, x, v


def dream(rng, noise=1.0, family=None):
    """(family, level, throws) of one valid dream, or None when it is not valid (the caller draws again)."""
    fam, coefs, level, masses, bumps, actions = dream_spec(rng, family)
    kinds = [grammar.code(t) for t in fam]
    rows = [(k, masses[k], bumps[k], act) for k in range(len(masses)) for act in actions[k]]
    B, Tn, Sn = len(rows), max(1, len(kinds)), max(len(r[3].segments) for r in rows)
    t0s, t1s, frc = np.zeros((B, Sn)), np.zeros((B, Sn)), np.zeros((B, Sn))
    nseg = np.zeros(B, np.int64)
    kind, a, b = np.zeros((B, Tn), np.int64), np.zeros((B, Tn), np.int64), np.zeros((B, Tn), np.int64)
    coef = np.zeros((B, Tn))
    nterm = np.full(B, len(kinds), np.int64)
    mu, bt, ba = np.zeros(B), np.zeros(B), np.zeros(B)
    for i, (k, m, bump, act) in enumerate(rows):
        s0, s1, f = act.arrays()
        t0s[i, :len(s0)], t1s[i, :len(s1)], frc[i, :len(f)], nseg[i] = s0, s1, f, len(s0)
        for j, (kk, aa, bb) in enumerate(kinds):
            kind[i, j], a[i, j], b[i, j], coef[i, j] = kk, aa, bb, coefs[j]
        mu[i] = 1.0 / m
        if bump:
            bt[i], ba[i] = bump
    xs, vs = S.simulate_many(t0s, t1s, frc, nseg, mu, kind, a, b, coef, nterm, bt, ba)
    if not (np.all(np.isfinite(xs)) and np.all(np.isfinite(vs)) and np.abs(xs).max() < 50 and np.abs(vs).max() < 50):
        return None
    if level != 5:
        pick = rng.choice(xs.size, size=min(400, xs.size), replace=False)
        tt = np.broadcast_to(TIMES, xs.shape).ravel()[pick]
        if not identifiable(fam, coefs, xs.ravel()[pick], vs.ravel()[pick], tt):
            return None
    sig = 0.001 * noise
    throws = [Throw(k, act, xs[i] + rng.normal(0, sig, paths.N_OBS), vs[i] + rng.normal(0, sig, paths.N_OBS))
              for i, (k, m, bump, act) in enumerate(rows)]
    return fam, level, throws


def dream_tables(rng, n):
    """n valid dreams, compacted: features (n, 270, 8), world (n, 7), label (n,) family index, level (n,)."""
    from . import compact as C
    F, Wf, lab, lev = [], [], [], []
    while len(lab) < n:
        d = dream(rng)
        if d is None:
            continue
        fam, level, throws = d
        f, w, _ = C.compact(throws)
        F.append(f)
        Wf.append(w)
        lab.append(FAMILY_INDEX[fam])
        lev.append(level)
    return (np.stack(F).astype(np.float16), np.stack(Wf).astype(np.float32), np.array(lab, np.int32),
            np.array(lev, np.int8))
