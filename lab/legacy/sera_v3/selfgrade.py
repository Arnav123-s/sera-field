"""SERA grades itself (plan revision 5, WP3; theory §11's apprentice rule).

When SERA cannot prove its best guess, is it probably right anyway? A small logistic model answers from what SERA
itself can see at the end of a world: how much of its belief the guess holds, how well its last predictions held,
how far the band still is from the tolerance, how short of the threshold its leader was, and whether the alarm rang.
It is fitted on Stage 1-2 worlds, where the caretaker's grade says whether the guess was the law. It is trusted in
Stage 3 only if, on held-out Stage-2 worlds, its agreement with those grades has a Wilson 95% lower bound of at least
TRUST (0.9); otherwise Stage 3 uses the judge's numbers alone. Its grades never enter a proof.
"""
import math

import numpy as np

TRUST = 0.9
RIDGE = 1.0


def features(report, eps=0.2):
    b = report.belief_leader if report.belief_leader is not None else 0.0
    b = min(max(b, 1e-6), 1 - 1e-6)
    fs = [f['leader_rms'] for f in (report.foresight or []) if math.isfinite(f.get('leader_rms', math.inf))][-4:]
    fore = math.log1p(float(np.median(fs))) if fs else 0.0
    bands = [c['band'] for c in (report.calls or []) if c.get('band')]
    band = min(max(math.log(bands[-1] / eps), 0.0), 5.0) if bands else 0.0
    blocks = report.blocks or []
    short = min(max(blocks[-1]['short'], 0.0), 50.0) / 10.0 if blocks else 0.0
    return np.array([1.0, math.log(b / (1 - b)), fore, band, short, float(bool(report.alarm))])


def wilson_lower(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    return (p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d


class SelfGrader:
    def __init__(self, w=None):
        self.w = None if w is None else np.asarray(w, float)
        self.trusted = False
        self.agreement = None

    def fit(self, X, y, iters=50):
        """Ridge-penalized logistic regression by Newton's method (IRLS)."""
        X, y = np.asarray(X, float), np.asarray(y, float)
        w = np.zeros(X.shape[1])
        pen = RIDGE * np.eye(X.shape[1])
        pen[0, 0] = 0.0
        for _ in range(iters):
            p = 1 / (1 + np.exp(-np.clip(X @ w, -30, 30)))
            g = X.T @ (p - y) + pen @ w
            H = X.T @ (X * (p * (1 - p))[:, None]) + pen + 1e-9 * np.eye(X.shape[1])
            step = np.linalg.solve(H, g)
            w -= step
            if np.max(np.abs(step)) < 1e-8:
                break
        self.w = w
        return self

    def p(self, x):
        return float(1 / (1 + math.exp(-float(np.clip(np.asarray(x, float) @ self.w, -30, 30)))))

    def measure(self, X, y):
        """Agreement with the caretaker's grades on held-out worlds; trusted if its Wilson lower bound >= TRUST."""
        k = sum(int((self.p(x) >= 0.5) == bool(t)) for x, t in zip(X, y))
        n = len(y)
        self.agreement = dict(agree=k, n=n, lower=round(wilson_lower(k, n), 4))
        self.trusted = self.agreement['lower'] >= TRUST
        return self.agreement
