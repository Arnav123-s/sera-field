"""The gut (M1_DESIGN.md §4d.5): which idea to try first. It orders the 67 families; it never decides what is true.

Features of a family F, from what the mind has seen so far in a world (the first situation's teacher pushes):
  - fit: log(RSS_0 / RSS_F), where RSS is the least-squares misfit of the measured accelerations (central
    differences of the speed readings) by the hand's force plus F's terms. This is the fast imagination tier:
    every family scored at once, about a thousand times cheaper than the exact ledger.
  - size |F|;
  - the board's trail score for F (stigmergy);
  - the lexicon's prior for F from the words heard (caretaker);
  - one indicator per idea (base rates).
Score = theta . features; softmax over the families. Training happens only after a world, only on a checked
outcome (an accepted certificate or a teacher's correction), by cross-entropy, optionally mixed with the world's
evidence trace (§4c: softmax of the exact prequential scores).
"""
import math

import numpy as np

from . import grammar, paths
from .worlds import hand

FAMILIES = tuple(grammar.space())
IDEAS = grammar.IDEAS
N_FEAT = 4 + len(IDEAS)


def accelerations(throws):
    """(x, v, hand force during the push, acceleration) at interior readings, from central differences."""
    xs, vs, fs, acc = [], [], [], []
    for t in throws:
        x, v = t.x, t.v
        a = (v[2:] - v[:-2]) / (2 * paths.DT_OBS)
        times = np.arange(1, x.size - 1) * paths.DT_OBS
        push = np.zeros(times.size)
        for s0, s1, u in t.action.segments:
            push += np.where((times >= s0) & (times < s1), hand(u), 0.0)
        xs.append(x[1:-1]); vs.append(v[1:-1]); fs.append(push); acc.append(a)
    return np.concatenate(xs), np.concatenate(vs), np.concatenate(fs), np.concatenate(acc)


def fit_gains(throws):
    """log(RSS_0 / RSS_F) for every family (the fast tier). RSS_0 is the hand-only fit."""
    x, v, f, a = accelerations(throws)
    if a.size < 4:
        return np.zeros(len(FAMILIES))
    cols = {}
    for idea in IDEAS:
        kind, ia, ib = grammar.codes((idea,))
        cols[idea] = np.array([paths.term(kind[0], ia[0], ib[0], xi, vi, 1.0, 1.0) for xi, vi in zip(x, v)])
    out = np.zeros(len(FAMILIES))

    def rss(X):
        beta, *_ = np.linalg.lstsq(X, a, rcond=None)
        r = a - X @ beta
        return float(r @ r)

    r0 = max(rss(f[:, None]), 1e-12)
    for j, fam in enumerate(FAMILIES):
        if not fam:
            continue
        X = np.column_stack([f] + [cols[i] for i in fam])
        out[j] = math.log(r0 / max(rss(X), 1e-12))
    return np.maximum(out, 0.0)


class Gut:
    def __init__(self, lr=0.1):
        self.theta = np.zeros(N_FEAT)
        self.lr = lr
        self.updates = 0

    def features(self, gains, board=None, lexicon=None, heard=(), use_words=True):
        F = np.zeros((len(FAMILIES), N_FEAT))
        F[:, 0] = gains
        for j, fam in enumerate(FAMILIES):
            F[j, 1] = len(fam)
            if board is not None:
                F[j, 2] = board.trail_score(fam)
            if lexicon is not None and use_words and heard:
                F[j, 3] = lexicon.log_prior(heard, grammar.name(fam))
            for idea in fam:
                F[j, 4 + IDEAS.index(idea)] = 1.0
        return F

    def scores(self, F):
        return F @ self.theta

    def probabilities(self, F):
        """Softmax of the scores: how much it would bet on each family being the truth (for calibration, T2)."""
        s = self.scores(F)
        p = np.exp(s - s.max())
        return p / p.sum()

    def ranking(self, F):
        """Families in the order it would try them (ties by the grammar's order, deterministic)."""
        s = self.scores(F)
        return [FAMILIES[j] for j in sorted(range(len(FAMILIES)), key=lambda j: (-s[j], j))]

    def train(self, F, target):
        """One step of cross-entropy toward `target` (a family, or a probability vector over FAMILIES)."""
        if isinstance(target, np.ndarray):
            p_star = target
        else:
            p_star = np.zeros(len(FAMILIES))
            p_star[FAMILIES.index(grammar.canonical(target))] = 1.0
        s = self.scores(F)
        p = np.exp(s - s.max())
        p /= p.sum()
        self.theta -= self.lr * (F.T @ (p - p_star))
        self.updates += 1

    def state(self):
        return {'theta': [float(t) for t in self.theta], 'updates': self.updates}


def brier(p, truth):
    """Multi-class Brier score of the probabilities p over FAMILIES against the true family (0 = perfect)."""
    y = np.zeros(len(FAMILIES))
    y[FAMILIES.index(grammar.canonical(truth))] = 1.0
    return float(((p - y) ** 2).sum())


def trace_targets(ledger):
    """§4c: the world's evidence trace, softmax of the exact prequential scores (a thin trace for weak ideas)."""
    q = np.array([ledger.Q[f] for f in FAMILIES])
    q = q - q.max()
    p = np.exp(np.maximum(q, -50.0))
    p = np.maximum(p, 1e-6)
    return p / p.sum()
