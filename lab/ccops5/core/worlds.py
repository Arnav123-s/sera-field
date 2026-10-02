"""Worlds for the core's checks: school-like 1-D worlds with one hidden force (or none, or one outside the
grammar), laid out like `puzzles.school_plan`: objects of three hidden masses, two pushes per situation
(one each way), a check push held out, and an occasional bump by someone else.

The mind sees only the throws it is given or makes (`World.push`); everything else here is the hidden truth
used to judge it.
"""
import dataclasses
import math

import numpy as np

from .. import puzzles as P
from . import grammar, paths

OUTSIDE = {'v^1.5 drag': (2, (1.0, 3.0)), 'x*v force': (3, (1.0, 4.0)),   # kind code, strength range
           'motor': (6, (0.5, 1.5))}         # a hidden motor: a force swinging in time, sin(omega t)
MOTOR_OMEGAS = (2.5, 3.5, 4.5, 5.5)          # none of them is on the mind's invention menu (1, 2, 3, 4, 6, 8)


def hand(u):
    """The hand law the mind learned in the nursery (the world's `hand_force`)."""
    return 3.0 * math.tanh(1.6 * u)


@dataclasses.dataclass(frozen=True)
class Action:
    """A push program: segments (start, end, command), each pushing with the hand's force for the command."""
    segments: tuple

    def arrays(self):
        seg = self.segments
        return (np.array([s[0] for s in seg], float), np.array([s[1] for s in seg], float),
                np.array([hand(s[2]) for s in seg], float))

    @property
    def u(self):
        return self.segments[0][2]


def push_of(u):
    """The teacher's push: command u for the first T_PUSH seconds."""
    return Action(((0.0, paths.T_PUSH, float(u)),))


@dataclasses.dataclass
class Throw:
    situation: int
    index: int
    action: Action
    x: np.ndarray
    v: np.ndarray
    tag: str = 'teacher'

    @property
    def u(self):
        return self.action.u


@dataclasses.dataclass
class World:
    seed: int
    index: int
    force: str
    truth: tuple                 # the true family; None when the force is outside the grammar
    coef: float                  # the true coefficient in the model's form (force per unit inverse mass)
    kind: int                    # 0 grammar idea, 2 v^1.5, 3 x*v (hidden)
    idea: tuple                  # the true idea when in the grammar
    masses: list                 # per situation (hidden)
    bumps: list                  # per situation: None or (start, amplitude) (hidden)
    sigma: tuple                 # the sensor noise the mind knows (x, v)
    throws: list                 # the teacher's pushes, made in advance, in order
    held_out: list
    omega: float = 0.0           # the motor's frequency (hidden; motor worlds only)
    teacher_pushes: list = dataclasses.field(default_factory=list)   # per situation: the teacher's commands
    made: dict = dataclasses.field(default_factory=dict)             # pushes made so far per situation
    log: list = dataclasses.field(default_factory=list)              # every throw made through push()

    @property
    def n_situations(self):
        return len(self.masses)

    def situations(self):
        out = {}
        for t in self.throws:
            out.setdefault(t.situation, []).append(t)
        return [out[k] for k in sorted(out)]

    def teacher_actions(self, k):
        return [push_of(u) for u in self.teacher_pushes[k]]

    def _codes(self):
        if self.force == 'none':
            return np.zeros(0, np.int64), np.zeros(0, np.int64), np.zeros(0, np.int64), np.zeros(0)
        if self.kind == 0:
            return (np.array([0], np.int64), np.array([grammar.INPUT_CODE[self.idea[0]]], np.int64),
                    np.array([grammar.SHAPE_CODE[self.idea[1]]], np.int64), np.array([self.coef]))
        if self.kind == 6:
            return (np.array([6], np.int64), np.zeros(1, np.int64), np.array([int(round(self.omega * 10))], np.int64),
                    np.array([self.coef]))
        return np.array([self.kind], np.int64), np.zeros(1, np.int64), np.zeros(1, np.int64), np.array([self.coef])

    def push(self, k, action, tag='own'):
        """Make a push in situation k (the same object, the same bump if there is one); fresh sensor noise."""
        j = self.made.get(k, 0)
        self.made[k] = j + 1
        kinds, a, b, coefs = self._codes()
        t0, amp = self.bumps[k] if self.bumps[k] else (0.0, 0.0)
        xs, vs = paths.simulate_program(*action.arrays(), 1.0 / self.masses[k], kinds, a, b, coefs, 1.0, 1.0,
                                        t0, amp)
        rng = np.random.default_rng([self.seed, 7, self.index, k, 100 + j])
        throw = Throw(k, len(self.log), action, xs + rng.normal(0, self.sigma[0], xs.size),
                      vs + rng.normal(0, self.sigma[1], vs.size), tag)
        self.log.append(throw)
        return throw

    def true_force(self, x, v, t=None):
        """The hidden force (per unit inverse mass), without the hand."""
        x = np.ravel(np.asarray(x, float))
        v = np.ravel(np.asarray(v, float))
        t = np.zeros_like(x) if t is None else np.ravel(np.asarray(t, float))
        if self.force == 'none':
            return np.zeros_like(x)
        kinds, a, b, _ = self._codes()
        return self.coef * np.array([paths.term_t(kinds[0], a[0], b[0], xi, vi, ti, 1.0, 1.0)
                                     for xi, vi, ti in zip(x, v, t)])

    def _visited(self, n_throws=None):
        seen = (self.throws + self.log)[:n_throws] if n_throws is not None else self.throws + self.log
        times = np.arange(paths.N_OBS) * paths.DT_OBS
        return (np.concatenate([t.x for t in seen]), np.concatenate([t.v for t in seen]),
                np.concatenate([times for _ in seen]))

    def _best_fit_gap(self, family, xs, vs, ts, minimax=False):
        """Largest gap between the true force and family's best least-squares version, over these states; with
        minimax (reviewer VD14 fix 4, for a claim "some strength within eps"), its best version in the largest gap itself
        (a linear program; least squares if it fails)."""
        target = self.true_force(xs, vs, ts)
        if not family:
            return float(np.max(np.abs(target)))
        kind, a, b = grammar.codes(family)
        X = np.column_stack([[paths.term_t(kind[i], a[i], b[i], xi, vi, ti, 1.0, 1.0) for xi, vi, ti in zip(xs, vs, ts)]
                             for i in range(len(kind))])      # every coefficient's column (a K-knot cell has K)
        T = grammar.tie(family)
        if T is not None:                                     # Decision 12: an invented shape's one column
            X = X @ T
        c, *_ = np.linalg.lstsq(X, target, rcond=None)
        gap = float(np.max(np.abs(target - X @ c)))
        if minimax:
            from scipy.optimize import linprog
            n, k = X.shape
            res = linprog(np.r_[np.zeros(k), 1.0], A_ub=np.block([[X, -np.ones((n, 1))], [-X, -np.ones((n, 1))]]),
                          b_ub=np.r_[target, -target], bounds=[(None, None)] * k + [(0, None)], method='highs')
            if res.success:
                gap = min(gap, float(np.max(np.abs(target - X @ res.x[:k]))))
        return gap

    def effect_size(self):
        """For a force outside the grammar: how much of it no family can express, over the visited states."""
        xs, vs, ts = self._visited()
        return min(self._best_fit_gap(f, xs, vs, ts) for f in grammar.space())

    def residual_outside(self, cert, n_throws=None, minimax=False):
        """The part of the true force that the certified family cannot express, over the certificate's scope; reviewer VD14
        fix 4: at the readings of the certificate's own throws (the first n_throws) and, for a functional claim, at the
        strength that makes the largest gap smallest."""
        if self.truth is not None and grammar.contains(cert.family, self.truth):
            return 0.0
        xs, vs, ts = self._visited(n_throws)
        if cert.scope:
            (x0, x1), (v0, v1) = cert.scope['x'], cert.scope['v']
            keep = (xs >= x0) & (xs <= x1) & (vs >= v0) & (vs <= v1)
            if 'cells' in cert.scope:                   # D10: only the cells the claim speaks for
                from .truth import cell_of
                cells = set(cert.scope['cells'])
                keep &= np.array([cell_of(cert.scope, float(x), float(v)) in cells for x, v in zip(xs, vs)])
            xs, vs, ts = xs[keep], vs[keep], ts[keep]
        if xs.size == 0:
            return 0.0
        return self._best_fit_gap(tuple(cert.family), xs, vs, ts, minimax=minimax)


def make(seed, force, *, index=0, situations=10, noise=1.0, tricks=0.05):
    """One world. `force` is a school force name, 'none', or a force outside the grammar."""
    rng = np.random.default_rng([seed, 7, index])
    masses3 = [float(m) for m in rng.uniform(0.6, 2.5, size=3)]
    if force == 'none':
        truth, idea, kind, coef = (), None, 0, 0.0
    elif force in OUTSIDE:
        kind, (lo, hi) = OUTSIDE[force]
        truth, idea, coef = None, None, -float(rng.uniform(lo, hi))
        if kind == 6:
            coef = -coef * float(rng.choice([-1.0, 1.0]))
    else:
        idea, (lo, hi) = P.FORCES[force]
        sign = float(rng.choice([-1.0, 1.0])) if idea[0] == 'nothing' else 1.0
        truth, kind, coef = (idea,), 0, -sign * float(rng.uniform(lo, hi))
    sigma = (0.001 * noise, 0.001 * noise)
    omega = float(rng.choice(MOTOR_OMEGAS)) if force == 'motor' else 0.0
    w = World(seed, index, force, truth, coef, kind, idea, [], [], sigma, [], [], omega=omega)
    for k in range(situations):
        m = float(rng.choice(masses3))
        bump = None
        if rng.random() < tricks:
            bump = (float(rng.choice([0.6, 0.8, 1.0, 1.2])), float(rng.choice([-1.5, 1.5])))
        pushes = (float(rng.choice([0.6, 1.0])), -float(rng.choice([0.6, 1.0])))
        check_u = float(rng.choice((-0.9, -0.5, 0.5, 0.9)))
        w.masses.append(m)
        w.bumps.append(bump)
        w.teacher_pushes.append(pushes)
        kinds, a, b, coefs = w._codes()
        for j, u in enumerate(pushes + (check_u,)):
            t0, amp = bump if bump else (0.0, 0.0)
            xs, vs = paths.simulate(hand(u), 1.0 / m, kinds, a, b, coefs, 1.0, 1.0, t0, amp)
            noise_rng = np.random.default_rng([seed, 7, index, k, j])
            throw = Throw(k, len(w.throws) if j < 2 else -1, push_of(u),
                          xs + noise_rng.normal(0, sigma[0], xs.size), vs + noise_rng.normal(0, sigma[1], vs.size),
                          'teacher' if j < 2 else 'check')
            (w.throws if j < 2 else w.held_out).append(throw)
    return w
