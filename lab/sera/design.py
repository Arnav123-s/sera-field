"""Designed experiments (SERA v3.1): imagine the futures of many push programs under the leading law and under what
blocks it, and make the push where they part the most.

Why: in B3 dev (b3-dev2 units, 2026-09-24), 7 of the 8 L1/L2 worlds SERA was not sure of had the truth as its best
guess, blocked by a look-alike (sin x against x + x^3; straight + cubic against cubic + wave). Both minds chose from the
same 16 single pushes (M1.menu), and such look-alikes part only far from rest: after a large swing, or a long run.
The world accepts any push program; the hand is the same for every mind: forces |u| <= HAND, inside the 2 s of a throw.

Candidates per object (all within the hand):
  - M1's menu (single pushes of 0.2-1.2 s, one swing);
  - pumping: push with the motion the leader predicts (+-HAND in the direction of its predicted speed, re-planned on
    the predicted path), and braking (against it), starting either way;
  - holds: a constant force for the whole throw, either way, at HAND and HAND / 2;
  - random programs of 1-3 non-overlapping segments (forces +-HAND / 2, +-HAND; times on a 0.1 s grid).
The mind scores each with the expected evidence M1 uses (M1.separation), or, when the band blocks, with the readings
it would put in the widest-band cells. Imagining ~50 futures per object costs ~2 ms each (the judge's compiled path).
"""
import numpy as np

from ccops5.core import paths
from ccops5.core.worlds import Action

HAND = 1.0                      # the strongest command any mind has (M1.COMMANDS, the teacher's push)
GRID = 0.1                      # program times, seconds
RANDOM = 24
ROUNDS = 3                      # re-planning rounds of a pumping program


def _segments(u, dt):
    """Merge a piecewise-constant force (one value per interval of length dt) into (t0, t1, u) segments."""
    segs, start = [], 0
    for i in range(1, len(u) + 1):
        if i == len(u) or u[i] != u[start]:
            if u[start] != 0.0:
                segs.append((round(start * dt, 10), round(min(i * dt, paths.T_END), 10), float(u[start])))
            start = i
    return tuple(segs)


def _pump(model, coef, mu, sign, brake):
    """Push with (or against) the motion the leader predicts, starting with `sign`; re-planned ROUNDS times."""
    n = paths.N_OBS - 1
    u = np.full(n, sign * HAND)
    for _ in range(ROUNDS):
        action = Action(_segments(u, paths.DT_OBS))
        _, vs = paths.simulate_program(*action.arrays(), mu, model.kind, model.a, model.b, model.codes_coef(coef),
                                       model.sx, model.sv, 0.0, 0.0)
        new = np.array([sign * HAND] + [(-1.0 if brake else 1.0) * HAND * (1.0 if vs[i] >= 0 else -1.0)
                                        for i in range(1, n)])
        if np.array_equal(new, u):
            break
        u = new
    return Action(_segments(u, paths.DT_OBS))


def _random_program(rng):
    k = int(rng.integers(1, 4))
    cuts = np.sort(rng.choice(np.arange(1, int(round(paths.T_END / GRID))), size=2 * k, replace=False)) * GRID
    forces = rng.choice([-HAND, -HAND / 2, HAND / 2, HAND], size=k)
    return Action(tuple((round(float(cuts[2 * i]), 10), round(float(cuts[2 * i + 1]), 10), float(forces[i]))
                        for i in range(k)))


SWITCH = tuple(round(0.25 * k, 2) for k in range(1, 8))     # one-switch times 0.25 .. 1.75 s


def switching():
    """Research R2 (reviewer, 2026-09-25): full-strength programs with one or two switches spanning the throw. For
    control-affine laws Pontryagin's condition makes a nonsingular optimum bang-bang; one or two switches is a search
    restriction for a 2 s throw, not a theorem."""
    out = []
    for s in (HAND, -HAND):
        for a in SWITCH:
            out.append(Action(((0.0, a, s), (a, paths.T_END, -s))))
        for a, b in ((0.25, 0.75), (0.25, 1.25), (0.5, 1.0), (0.5, 1.5), (0.75, 1.25), (1.0, 1.5)):
            out.append(Action(((0.0, a, s), (a, b, -s), (b, paths.T_END, s))))
    return out


def refine(action, step=0.05):
    """Programs whose switch times differ from `action`'s by one grid step (local search around the best)."""
    segs = action.segments
    out = []
    for i in range(len(segs) - 1):
        for d in (-step, step):
            t = round(segs[i][1] + d, 10)
            if segs[i][0] < t < segs[i + 1][1]:
                new = list(segs)
                new[i] = (segs[i][0], t, segs[i][2])
                new[i + 1] = (t, segs[i + 1][1], segs[i + 1][2])
                out.append(Action(tuple(new)))
    return out


def programs(model, coef, mu, rng, durations=None, commands=None):
    """Candidate push programs for one object, all within the hand."""
    from ccops5.core import mind as M1
    acts = list(M1.menu(model, coef, mu, durations or M1.DURATIONS, commands or M1.COMMANDS))
    for sign in (1.0, -1.0):
        for brake in (False, True):
            acts.append(_pump(model, coef, mu, sign, brake))
        for level in (HAND, HAND / 2):
            acts.append(Action(((0.0, paths.T_END, sign * level),)))
    acts += switching()
    acts += [_random_program(rng) for _ in range(RANDOM)]
    seen, out = set(), []
    for a in acts:
        if a.segments not in seen:
            seen.add(a.segments)
            out.append(a)
    return out


def separation(model_a, coef_a, model_b, coef_b, mu, action, sigma):
    """Expected log-evidence one push adds between two laws at given numbers: 0.5 |(f_A - f_B) / sigma|^2 (as
    M1.separation, without a ledger)."""
    fa = np.concatenate(paths.simulate_program(*action.arrays(), mu, model_a.kind, model_a.a, model_a.b,
                                               model_a.codes_coef(coef_a), model_a.sx, model_a.sv, 0.0, 0.0))
    fb = np.concatenate(paths.simulate_program(*action.arrays(), mu, model_b.kind, model_b.a, model_b.b,
                                               model_b.codes_coef(coef_b), model_b.sx, model_b.sv, 0.0, 0.0))
    scale = np.concatenate([np.full(paths.N_OBS, 1 / sigma[0]), np.full(paths.N_OBS, 1 / sigma[1])])
    d = (fa - fb) * scale
    return 0.5 * float(d @ d) if np.all(np.isfinite(d)) else 0.0


def surviving_gap(fa, fb, ja, jb, pa, pb, sigma):
    """Research R2 (reviewer, 2026-09-25; T-optimal design, Atkinson & Fedorov 1975): the expected evidence a push adds
    between two laws AFTER each re-fits its own numbers. The raw gap at today's estimates overstates it whenever a law
    can shift its coefficients or the object's mass to absorb the difference.

    fa, fb: predicted readings; ja, jb: their Jacobians over each law's own numbers (coefficients, this object's
    inverse mass); pa, pb: the precision the earlier throws already give those numbers (moving them costs
    0.5 d' P d in evidence). Returns 0.5 min_d |W (fa - fb) - W (ja da - jb db)|^2 + 0.5 da' pa da + 0.5 db' pb db,
    with W the sensor whitening."""
    scale = np.concatenate([np.full(paths.N_OBS, 1 / sigma[0]), np.full(paths.N_OBS, 1 / sigma[1])])
    d = (fa - fb) * scale
    if not np.all(np.isfinite(d)):
        return 0.0
    J = np.concatenate([ja, -jb], axis=1) * scale[:, None]
    na = ja.shape[1]
    P = np.zeros((J.shape[1], J.shape[1]))
    P[:na, :na], P[na:, na:] = pa, pb
    A = J.T @ J + P
    try:
        g = J.T @ d
        return 0.5 * max(float(d @ d - g @ np.linalg.solve(A, g)), 0.0)
    except np.linalg.LinAlgError:
        return 0.0


def _own_numbers(ledger, family, situation, action):
    """(readings, Jacobian over [coefficients, this object's inverse mass], the earlier throws' marginal precision on
    those numbers) for one law at its current estimates."""
    from ccops5.core import likelihood as L
    from ccops5.core.worlds import Throw
    model, post = ledger._models[family], ledger.post[family]
    nc = model.n_coef
    cov = np.linalg.inv(post.prec)
    if situation in post.order:
        k = nc + post.order.index(situation)
        idx = list(range(nc)) + [k]
        mu = post.mean[k]
        C = cov[np.ix_(idx, idx)]
    else:
        mu = L.MU_PRIOR[0]
        C = np.zeros((nc + 1, nc + 1))
        C[:nc, :nc] = cov[:nc, :nc]
        C[nc, nc] = L.MU_PRIOR[1] ** 2
    f, J = L._jac(model, post.mean[:nc], mu, Throw(situation, -1, action, np.zeros(paths.N_OBS), np.zeros(paths.N_OBS)))
    return f, J, np.linalg.pinv(C)


def surviving_separation(ledger, fam_a, fam_b, situation, action):
    """M1.separation, but counting only the gap that survives both laws re-fitting (surviving_gap)."""
    fa, ja, pa = _own_numbers(ledger, fam_a, situation, action)
    fb, jb, pb = _own_numbers(ledger, fam_b, situation, action)
    return surviving_gap(fa, fb, ja, jb, pa, pb, ledger.sigma)
