"""Likelihoods and fits for families of force terms (pure functions of the stored throws).

Parameters of a family: one coefficient per term (shared by the whole world), then one inverse mass mu per
situation. Readings have independent Gaussian noise with the known sensor sigmas, so a throw's likelihood is
exact given the parameters.

- `step` is the prequential part: from a Gaussian posterior over the parameters (information form) it returns
  log q(new throw | earlier throws) by Laplace's method, and the posterior updated with the throw. Laplace's
  method re-optimizes the throw's own numbers (its coefficients and its object's inverse mass, starting from a
  coarse scan when the object is new), so it stays accurate when the path depends on them nonlinearly (a
  spring's phase depends on the mass). q is the Laplace approximation to a proper predictive density.
- `fit` is the maximum-likelihood fit over all throws (the sup in an e-process denominator).

Bumps (someone else knocks the object) are handled by one outlier density b(y), the same for every family.
- Numerator per throw: (1 - RHO) q_clean + RHO b, which is a proper density.
- Denominator per throw: N(y | theta) + RHO b. This is at least the clean density, so the e-process stays
  valid when throws are clean.
- A bumped throw is explained by no smooth law, so every family scores about RHO b on it, and it cancels out
  of every comparison. Such a throw does not update the posterior.
"""
import dataclasses
import math
import os

import numpy as np

from . import paths
from .worlds import hand

COEF_PRIOR_SD = 10.0          # strengths before any data: roughly -20..20 in force units
MU_PRIOR = (1.0, 0.6)         # inverse mass before any data: masses 0.6-2.5 met in the nursery
MU_SCAN = np.geomspace(0.15, 3.0, 40)
RHO = 0.05                    # share of throws someone else bumps (from the nursery: about 1 situation in 20)
OUTLIER_SD = 1.0              # the outlier density: every reading N(0, 1) (metres, metres per second)


@dataclasses.dataclass
class Model:
    """A family's terms as simulator codes, plus the scaling of any smooth-basis terms. Decision 12: `tie` (codes x
    coefficients) when some coefficient moves several codes at once (an invented shape: a cell's hats tied by its
    knots); None, as for every family before it, when each code has its own coefficient."""
    kind: np.ndarray
    a: np.ndarray
    b: np.ndarray
    sx: float = 1.0
    sv: float = 1.0
    tie: np.ndarray = None

    @property
    def n_coef(self):
        return int(self.kind.shape[0]) if self.tie is None else int(self.tie.shape[1])

    def codes_coef(self, coef):
        """The simulator codes' coefficients for the model's coefficients."""
        return coef if self.tie is None else self.tie @ np.asarray(coef, float)

    def extended(self, kind, a, b, sx=None, sv=None):
        """This model with more codes, each with its own coefficient (a flexible fit's extra basis or cells)."""
        tie = None
        if self.tie is not None:
            n = len(kind)
            tie = np.zeros((self.tie.shape[0] + n, self.tie.shape[1] + n))
            tie[:self.tie.shape[0], :self.tie.shape[1]] = self.tie
            tie[self.tie.shape[0]:, self.tie.shape[1]:] = np.eye(n)
        return Model(np.concatenate([self.kind, np.asarray(kind, np.int64)]),
                     np.concatenate([self.a, np.asarray(a, np.int64)]), np.concatenate([self.b, np.asarray(b, np.int64)]),
                     self.sx if sx is None else sx, self.sv if sv is None else sv, tie)


@dataclasses.dataclass
class Post:
    """Gaussian posterior in information form over [coef..., mu(situation)...]."""
    mean: np.ndarray
    prec: np.ndarray
    order: list
    knock: dict = dataclasses.field(default_factory=dict)   # M-1: situation -> log P(knock j | its past throws)

    def cov(self):
        return np.linalg.inv(self.prec)


@dataclasses.dataclass
class Fit:
    coef: np.ndarray
    mu: dict
    cov: np.ndarray
    order: list
    loglik: float
    ok: bool = True
    converged: bool = True       # truth-v2 (independent review T2-B): False when the search stopped before its tolerance
    knocks: dict = None          # M-1: situation -> the knock j the fit assigns (only knocked objects are listed)


def _log_norm(sigma):
    return -paths.N_OBS * (math.log(2 * math.pi) + math.log(sigma[0]) + math.log(sigma[1]))


def _scale(sigma):
    return np.concatenate([np.full(paths.N_OBS, 1 / sigma[0]), np.full(paths.N_OBS, 1 / sigma[1])])


def _obs(throw):
    return np.concatenate([throw.x, throw.v])


def log_outlier(throw):
    y = _obs(throw)
    return math.log(RHO) - 0.5 * float(y @ y) / OUTLIER_SD ** 2 - y.size * math.log(math.sqrt(2 * math.pi) * OUTLIER_SD)


# Compute batch K (2026-09-24): exact one-pass derivatives instead of finite differences, approved by the author
# on 2026-09-24 (golden: evidence within 4e-5 relative, no certificate decision changed, bands tighter because
# finite-difference error had inflated them). CCOPS5_EXACT_JAC=0 restores finite differences for comparison.
EXACT_JACOBIAN = os.environ.get('CCOPS5_EXACT_JAC', '1') != '0'
JAC_LIMIT = 1e12             # beyond this an exact slope is meaningless at float resolution; finite steps are used

_ARRAYS = {}                   # action -> its (t0s, t1s, forces) arrays (built once; actions are frozen)

# truth-v3 T2, M-1 (Decision 10; S4 §C5): knocks per object, as the worlds make them. 'throw' (truth-v2): one outlier
# density per throw only. 'object': a knock latent per object - none, or one of the worlds' own knocks (a push of
# +-1.5 for paths.BUMP_LEN s at 0.6, 0.8, 1.0 or 1.2 s, the same on every throw of the object) - in the numerator
# (a mixture over the object's knock given its past throws) and the denominator (the best knock per object). The
# per-throw outlier density stays in both, for knocks outside this family.
KNOCK = os.environ.get('CCOPS5_KNOCK', 'throw')
RHO_OBJ = 0.05                 # the worlds knock about 1 object in 20 (their `tricks`)
KNOCKS = tuple((t0, amp) for t0 in (0.6, 0.8, 1.0, 1.2) for amp in (-1.5, 1.5))
KNOCK_LOGP = (math.log(1 - RHO_OBJ),) + (math.log(RHO_OBJ / len(KNOCKS)),) * len(KNOCKS)
KNOCK_KEEP = math.log(1e-9)    # a branch whose posterior falls below this is dropped (a sub-density: always valid)
KNOCK_SEARCH_RMS = 3.0         # the denominator searches knocks for objects misfit by this many sigmas (RMS)
KNOCK_ROUNDS = 3


@dataclasses.dataclass(frozen=True)
class Knocked:
    """A throw's program with one knock added: one more segment of force `amp` for BUMP_LEN s from t0 (the simulator
    adds overlapping segments, exactly as it adds a world's bump)."""
    base: object
    t0: float
    amp: float

    def arrays(self):
        a, b, f = self.base.arrays()
        return np.append(a, self.t0), np.append(b, self.t0 + paths.BUMP_LEN), np.append(f, self.amp)

    @property
    def segments(self):
        return self.base.segments

    @property
    def u(self):
        return self.base.u


def knocked(throw, j):
    """The throw as the judge sees it under knock j (0 = none, 1..8 = KNOCKS[j - 1]); the readings are the same."""
    if not j:
        return throw
    t0, amp = KNOCKS[j - 1]
    return dataclasses.replace(throw, action=Knocked(throw.action, t0, amp))


def _arrays(action):
    arr = _ARRAYS.get(action)
    if arr is None:
        if len(_ARRAYS) > 100_000:
            _ARRAYS.clear()
        arr = _ARRAYS[action] = action.arrays()
    return arr


def _sim(model, coef, mu, throw):
    xs, vs = paths.simulate_program(*_arrays(throw.action), mu, model.kind, model.a, model.b, model.codes_coef(coef),
                                    model.sx, model.sv, 0.0, 0.0)
    return np.concatenate([xs, vs])


def _jac(model, coef, mu, throw, base=None):
    """(readings, Jacobian). `base`: the readings already simulated at exactly these numbers, reused as the
    forward-difference base path (the same numbers as simulating it again). Decision 12: a tied model's Jacobian is the
    codes' Jacobian times the tie (the chain rule; exact)."""
    if model.tie is not None:
        codes = Model(model.kind, model.a, model.b, model.sx, model.sv)
        y, J = _jac(codes, model.codes_coef(coef), mu, throw, base)
        nk = model.kind.shape[0]
        return y, np.concatenate([J[:, :nk] @ model.tie, J[:, nk:]], axis=1)
    if EXACT_JACOBIAN:
        y, J = paths.jacobian_exact(*_arrays(throw.action), mu, model.kind, model.a, model.b, coef, model.sx,
                                    model.sv, 0.0, 0.0)
        if np.all(np.isfinite(J)) and np.max(np.abs(J)) < JAC_LIMIT:
            return y, J
        base = y       # a stiff path whose linearization holds only below float resolution (torch autograd agrees
                       # with the kernel there): use the finite-step slope, on the same readings
    free = np.arange(model.n_coef, dtype=np.int64)
    if base is None:
        return paths.jacobian_program(*_arrays(throw.action), mu, model.kind, model.a, model.b, coef, model.sx,
                                      model.sv, 0.0, 0.0, free)
    n = base.size // 2
    return paths.jacobian_from_base(*_arrays(throw.action), mu, model.kind, model.a, model.b, coef, model.sx,
                                    model.sv, 0.0, 0.0, free, base[:n], base[n:])


def throw_loglik(model, coef, mu, throw, sigma):
    r = (_obs(throw) - _sim(model, coef, mu, throw)) * _scale(sigma)
    return -0.5 * float(r @ r) + _log_norm(sigma)


def linear_guess(model, throw):
    """A quick start for the numbers from this throw alone: regress the measured accelerations (velocity
    differences) on the hand and the family's terms. Only a starting point; the likelihood decides."""
    xs, vs = throw.x, throw.v
    xm, vm = .5 * (xs[:-1] + xs[1:]), .5 * (vs[:-1] + vs[1:])
    acc = (vs[1:] - vs[:-1]) / paths.DT_OBS
    t0s, t1s, forces = throw.action.arrays()
    mid = (np.arange(xm.size) + 0.5) * paths.DT_OBS
    push = np.zeros(xm.size)
    for s0, s1, f in zip(t0s, t1s, forces):
        push += np.where((mid >= s0) & (mid < s1), f, 0.0)
    cols = [np.array([paths.term(model.kind[i], model.a[i], model.b[i], x, v, model.sx, model.sv)
                      for x, v in zip(xm, vm)]) for i in range(model.kind.shape[0])]
    if model.tie is not None:                                   # Decision 12: the tied coefficients' columns
        cols = list((np.column_stack(cols) @ model.tie).T) if cols else []
    X = np.column_stack([push] + cols)
    beta, *_ = np.linalg.lstsq(X, acc, rcond=None)
    mu = float(np.clip(beta[0], 0.05, 5.0))
    return np.concatenate([beta[1:] / mu, [mu]])


def empty_post(model):
    nc = model.n_coef
    return Post(np.zeros(nc), np.eye(nc) * COEF_PRIOR_SD ** -2, [])


def familiar_masses(model, post):
    """Inverse masses of the objects already met in this world, merged when they are the same object
    (within 0.5%), with how many situations each was met in."""
    nc = model.n_coef
    found = []
    for i in range(len(post.order)):
        mu = float(post.mean[nc + i])
        for c in found:
            if abs(c[0] - mu) <= 5e-3 * max(c[0], mu):
                c[1] += 1
                break
        else:
            found.append([mu, 1])
    return [(m, n) for m, n in found]


def step(model, post, throw, sigma, iters=30):
    """Laplace predictive log-density of `throw` given `post`, and the updated posterior.

    A throw in a situation met before uses that object's inverse mass. A throw of a new object uses a mixture
    over its inverse mass: the same as an object already met (a Chinese-restaurant weight, each met object in
    proportion to how often it was met) or a new one (the broad nursery prior). The mixture is a proper prior,
    so q stays a (Laplace-approximated) proper predictive density."""
    if KNOCK == 'object':
        return _step_knock(model, post, throw, sigma, iters)
    clean, updated = _clean_step(model, post, throw, sigma, iters)
    a, b = math.log(1 - RHO) + clean, log_outlier(throw)
    log_q = _lse2(a, b)
    return log_q, (updated if a >= b and a > -math.inf else post)     # a bumped throw teaches nothing about the law


def _lse2(a, b):
    """log(e^a + e^b); -inf when both parts are zero (reviewer V395b: a reading so far off that y @ y overflows makes the
    outlier part -inf too, and -inf - -inf is nan)."""
    top = max(a, b)
    if top == -math.inf:
        return -math.inf
    return top + math.log1p(math.exp(-abs(a - b)))


def _step_knock(model, post, throw, sigma, iters):
    """M-1: the predictive mixes over the object's knock j with weights P(j | its past throws), each branch the
    clean Laplace predictive of the knocked program plus the per-throw outlier density. Branches whose weight fell
    below KNOCK_KEEP are dropped, which only lowers q (still a sub-density). The law posterior follows the most
    probable branch; the knock posterior is kept per object."""
    k = throw.situation
    lp = post.knock.get(k, KNOCK_LOGP)
    b = log_outlier(throw)
    branches = []
    for j, w in enumerate(lp):
        if w < KNOCK_KEEP:
            continue
        clean, updated = _clean_step(model, post, knocked(throw, j), sigma, iters)
        a = math.log(1 - RHO) + clean
        branches.append((j, w + _lse2(a, b), a >= b and a > -math.inf, updated))
    tops = np.array([x[1] for x in branches])
    if not np.isfinite(tops.max()):         # V395b: every branch is zero: q = 0, the posterior and knocks unchanged
        return -math.inf, post
    log_q = float(tops.max() + np.log(np.exp(tops - tops.max()).sum()))
    new = [-math.inf] * len(lp)
    for j, v, _, _ in branches:
        new[j] = v - log_q
    j, _, clean_wins, updated = max(branches, key=lambda x: x[1])
    out = updated if clean_wins else post
    knock = dict(post.knock)
    knock[k] = tuple(new)
    return log_q, Post(out.mean, out.prec, out.order, knock)


def _clean_step(model, post, throw, sigma, iters):
    """The clean part of `step`: (log q_clean, updated posterior)."""
    if throw.situation in post.order:
        clean, updated = _laplace(model, post, throw, sigma, None, iters)
    else:
        options = [(None, 1.0)] + [((mu, 2e-3 * mu), n) for mu, n in familiar_masses(model, post)]
        total = sum(w for _, w in options)
        results = [(math.log(w / total) + q, q, pst) for (prior, w), (q, pst) in
                   ((o, _laplace(model, post, throw, sigma, o[0], iters)) for o in options)]
        tops = np.array([r[0] for r in results])
        if not np.isfinite(tops.max()):             # V395: every option failed: no clean density, nothing learned
            return -math.inf, post
        clean = float(tops.max() + np.log(np.exp(tops - tops.max()).sum()))
        updated = max(results, key=lambda r: r[0])[2]
    return clean, updated


def _laplace(model, post, throw, sigma, mu_prior, iters):
    """One Laplace step. mu_prior: None for a situation already met; else None-or-(mean, sd) for a new one,
    where None means the broad nursery prior."""
    nc = model.n_coef
    new = throw.situation not in post.order
    if new:
        mean_mu, sd_mu = mu_prior if mu_prior is not None else MU_PRIOR
        order = post.order + [throw.situation]
        mean = np.concatenate([post.mean, [mean_mu]])
        prec = np.zeros((nc + len(order), nc + len(order)))
        prec[:-1, :-1] = post.prec
        prec[-1, -1] = sd_mu ** -2
    else:
        order, mean, prec = list(post.order), post.mean.copy(), post.prec.copy()
    k = nc + order.index(throw.situation)
    loc = list(range(nc)) + [k]
    try:
        cov = np.linalg.inv(prec)
        m = mean[loc]
        C = cov[np.ix_(loc, loc)]
        Cinv = np.linalg.inv(C)
    except np.linalg.LinAlgError:     # T-S on Colab 2026-09-26: a posterior that cannot be inverted is a ZERO clean
        return -math.inf, post        # component and stays as it was (reviewer V395: a constant floor such as -1e12 is a
                                      # positive density over unbounded readings, not a sub-density)
    scale = _scale(sigma)
    y = _obs(throw)

    def objective_f(th):
        f = _sim(model, th[:nc], th[nc], throw)
        r = (y - f) * scale
        d = th - m
        return 0.5 * float(r @ r) + 0.5 * float(d @ Cinv @ d), f

    def objective(th):
        return objective_f(th)[0]

    starts = [m.copy()]
    broad_mu = new and mu_prior is None
    if broad_mu:                                        # where in mass is this object? scan, then refine
        starts[0][nc] = min(MU_SCAN, key=lambda mu: objective(np.concatenate([m[:nc], [mu]])))
    if broad_mu or np.any(np.diag(C)[:nc] > 1.0):       # little known yet: also start from a quick regression
        guess = linear_guess(model, throw)
        if np.all(np.isfinite(guess)):
            if not broad_mu:
                guess[nc] = m[nc]
            starts.append(guess)

    def refine(th):
        lam, (obj, f_th) = 1e-3, objective_f(th)
        jac_at = None                     # the point whose derivatives are in (f, G); a rejected step keeps it
        for _ in range(iters):
            if jac_at is not th:
                f, G = _jac(model, th[:nc], th[nc], throw, base=f_th)
                jac_at = th
            r = (y - f) * scale
            Gs = G * scale[:, None]
            H = Gs.T @ Gs + Cinv
            g = Gs.T @ r - Cinv @ (th - m)
            try:
                delta = np.linalg.solve(H + lam * np.diag(np.diag(H)), g)
            except np.linalg.LinAlgError:
                break
            cand = th + delta
            cand[nc] = max(cand[nc], 1e-3)
            o2, f2 = objective_f(cand)
            if np.isfinite(o2) and o2 <= obj:
                small = obj - o2 < 1e-9 * max(1.0, obj)
                th, obj, f_th, lam = cand, o2, f2, max(lam / 10, 1e-9)
                if small:
                    break
            else:
                lam *= 10
                if lam > 1e8:
                    break
        return th, obj, f_th

    th, _, f_best = min((refine(s) for s in starts), key=lambda p: p[1])
    f, G = _jac(model, th[:nc], th[nc], throw, base=f_best)
    Gs = G * scale[:, None]
    I_new = Gs.T @ Gs
    H = I_new + Cinv
    r = (y - f) * scale
    d = th - m
    sC, ldC = np.linalg.slogdet(C)
    sH, ldH = np.linalg.slogdet(H)
    log_q = -0.5 * float(r @ r) + _log_norm(sigma) - 0.5 * float(d @ Cinv @ d) - 0.5 * ldC - 0.5 * ldH
    if not np.isfinite(log_q):
        log_q = -math.inf             # V395: no forecast formed is no clean density (was -1e12: see above)
    # Posterior update: add the throw's information, linearized at the local optimum.
    E = np.zeros((len(loc), len(mean)))
    for i, j in enumerate(loc):
        E[i, j] = 1.0
    prec2 = prec + E.T @ I_new @ E
    h2 = prec @ mean + E.T @ (Gs.T @ (r + Gs @ th))
    try:
        mean2 = np.linalg.solve(prec2, h2)
    except np.linalg.LinAlgError:     # an update that cannot be solved teaches nothing: keep the whole posterior (the
        mean2, prec2 = mean, prec     # old code kept the mean but stored the singular prec2, which crashed the next
                                      # throw of the object: T-S, Colab, world s1-i9107-L3, 2026-09-26)
    mean2[nc:] = np.maximum(mean2[nc:], 1e-3)
    return float(log_q), Post(mean2, prec2, order)


def fit(model, throws, sigma, start=None, iters=30, tol=1e-9, robust=True, penalty=None, knocks=None):
    """The judge's best fit (the e-process denominator). With M-1 (KNOCK = 'object') the best knock per object too.
    `penalty` (Decision 11, scoped claims; docs/SCOPED_CLAIMS.md §3): (a, b, lam) - the objective also pays
    lam * max(0, b - a . coef)^2, a one-sided push of one linear function of the coefficients up to b. The returned
    loglik is the likelihood alone at the penalized optimum: never below the best likelihood with a . coef >= b (that
    point pays no penalty, and the likelihood is never below the penalized objective)."""
    if KNOCK == 'object' and robust:
        return _fit_knocks(model, throws, sigma, start, iters, tol, penalty, knocks)
    return _fit(model, throws, sigma, start, iters, tol, robust, penalty)


def _object_score(model, coef, mu, ts, sigma, j):
    total = 0.0
    for t in ts:
        ln, lb = throw_loglik(model, coef, mu, knocked(t, j), sigma), log_outlier(t)
        total += _lse2(ln, lb)                  # V395c: two zero parts are -inf, never nan
    return total


def _fit_knocks(model, throws, sigma, start, iters, tol, penalty=None, knocks=None):
    """M-1 denominator: sup over the numbers and one knock per object of the robust likelihood, by alternating a fit
    with the knocks held and, for each object misfit by more than KNOCK_SEARCH_RMS sigmas, the best of its 9 knocks
    at the fitted numbers (a local search: premise U). A last pass takes the best of all 9 knocks for EVERY object at
    the final numbers (independent review, M-1 item 2), so at those numbers it dominates the per-object model's likelihood
    exactly: max_j L_j >= sum_j p_j L_j per object, and log(N + RHO b) >= log((1 - RHO) N + RHO b) per throw - the
    same convention as truth-v1's per-throw outliers. It uses no knock prior, so it needs only that the world's knocks
    are among the 9 states, not that they come at the prior's rate. `knocks` (reviewer VD14 fix 1): the assignment to start
    from (a claim's own, when its fit is embedded in a bigger model)."""
    assign = {s: j for s, j in (knocks or {}).items() if j}
    f = _fit(model, [knocked(t, assign.get(t.situation, 0)) for t in throws] if assign else throws, sigma, start,
             iters, tol, True, penalty)
    scale = _scale(sigma)
    for _ in range(KNOCK_ROUNDS):
        if not f.ok:
            break
        changed = False
        for s in f.order:
            ts = [t for t in throws if t.situation == s]
            j0 = assign.get(s, 0)
            rms = max(float(np.sqrt(np.mean(((_obs(t) - _sim(model, f.coef, f.mu[s], knocked(t, j0))) * scale) ** 2)))
                      for t in ts)
            if rms <= KNOCK_SEARCH_RMS:
                continue
            scores = [_object_score(model, f.coef, f.mu[s], ts, sigma, j) for j in range(len(KNOCKS) + 1)]
            j = int(np.argmax(scores))
            if j != j0 and scores[j] > scores[j0]:
                assign[s], changed = j, True
        if not changed:
            break
        post = Post(np.concatenate([f.coef, [f.mu[s] for s in f.order]]), np.eye(len(f.coef) + len(f.order)),
                    list(f.order))
        f2 = _fit(model, [knocked(t, assign.get(t.situation, 0)) for t in throws], sigma, post, iters, tol, True,
                  penalty)
        if not (f2.ok and f2.loglik >= f.loglik - 1e-9):
            break
        f = f2
    if f.ok:                                # the exact last pass: every object, every knock, at the final numbers
        total = 0.0
        for s in f.order:
            ts = [t for t in throws if t.situation == s]
            scores = [_object_score(model, f.coef, f.mu[s], ts, sigma, j) for j in range(len(KNOCKS) + 1)]
            j0 = assign.get(s, 0)
            j = int(np.argmax(scores))
            if scores[j] > scores[j0]:
                assign[s] = j
            total += scores[assign.get(s, 0)]
        f.loglik = max(f.loglik, total)     # equal up to rounding unless the pass found a better knock
    f.knocks = {s: j for s, j in assign.items() if j}
    return f


def _fit(model, throws, sigma, start=None, iters=30, tol=1e-9, robust=True, penalty=None):
    """Maximum-likelihood fit of [coef, mu...] over all throws (Levenberg-Marquardt), warm-started from a
    posterior when given. robust=False (truth-v2, T2: only a starting point for `sup_fit`) fits plain Gaussian
    readings, with no bump density: every throw pulls, however far off it starts. Its loglik is not the judge's."""
    order = []
    for t in throws:
        if t.situation not in order:
            order.append(t.situation)
    nc, K = model.n_coef, len(order)
    theta = np.concatenate([np.zeros(nc), np.full(K, MU_PRIOR[0])])
    if start is not None:
        theta[:nc] = start.mean[:nc]
        for i, s in enumerate(order):
            if s in start.order:
                theta[nc + i] = start.mean[nc + start.order.index(s)]
    col = {s: nc + i for i, s in enumerate(order)}
    scale = _scale(sigma)

    outl = [log_outlier(t) for t in throws]
    norm = _log_norm(sigma)
    if penalty is not None:                             # Decision 11: (a, b, lam) over the coefficients
        pa, pb, plam = np.asarray(penalty[0], float), float(penalty[1]), float(penalty[2])

    def pen(theta):
        """(the penalty part of the objective, the violation b - a . coef); both 0 when there is none."""
        if penalty is None:
            return 0.0, 0.0
        viol = pb - float(pa @ theta[:nc])
        return (plam * viol * viol, viol) if viol > 0 else (0.0, 0.0)

    def objective(theta):
        # Objective: -sum log(N_j(theta) + RHO b_j). Also returns each throw's simulated readings, so the
        # derivatives below reuse them (2026-09-24: before, a rejected step also paid for its derivatives).
        coef = theta[:nc]
        obj, fs = 0.0, []
        for t, lb in zip(throws, outl):
            f = _sim(model, coef, theta[col[t.situation]], t)
            r = (_obs(t) - f) * scale
            ln = -0.5 * float(r @ r) + norm
            if not robust:
                obj -= ln
                fs.append((f, ln))
                continue
            obj -= _lse2(ln, lb)                # V395c: a throw with both parts zero is +inf here, never nan
            fs.append((f, ln))
        return obj + pen(theta)[0], fs

    def derivatives(theta, fs):
        # Each throw weighted by how much the clean part explains it.
        coef = theta[:nc]
        H, g = np.zeros((nc + K, nc + K)), np.zeros(nc + K)
        for t, lb, (f0, ln) in zip(throws, outl, fs):
            w = 1.0 / (1.0 + math.exp(min(lb - ln, 700.0))) if robust else 1.0
            if w < 1e-12:
                continue
            f, J = _jac(model, coef, theta[col[t.situation]], t, base=f0)
            r = (_obs(t) - f) * scale
            Js = J * scale[:, None]
            idx = list(range(nc)) + [col[t.situation]]
            H[np.ix_(idx, idx)] += w * (Js.T @ Js)
            g[idx] += w * (Js.T @ r)
        p, viol = pen(theta)
        if p > 0:                                        # Gauss-Newton on lam * viol^2 (viol = b - a . coef)
            H[:nc, :nc] += 2.0 * plam * np.outer(pa, pa)
            g[:nc] += 2.0 * plam * viol * pa
        return H, g

    def assemble(theta):
        obj, fs = objective(theta)
        return derivatives(theta, fs) + (obj,)

    lam = 1e-3
    H, g, obj = assemble(theta)
    ok = bool(np.isfinite(obj))
    converged = False
    for _ in range(iters):
        if not ok:
            break
        try:
            step_ = np.linalg.solve(H + lam * np.diag(np.diag(H) + 1e-12), g)
        except np.linalg.LinAlgError:
            break
        cand = theta + step_
        cand[nc:] = np.maximum(cand[nc:], 1e-3)
        o2, fs2 = objective(cand)
        if np.isfinite(o2) and o2 <= obj:
            H2, g2 = derivatives(cand, fs2)
            small = obj - o2 < tol * max(1.0, abs(obj))
            theta, H, g, obj, lam = cand, H2, g2, o2, max(lam / 10, 1e-9)
            if small:
                converged = True
                break
        else:
            lam *= 10
            if lam > 1e8:                               # independent review R-3: no step helps. At an optimum only float
                try:                                    # noise is left: stationary if the Gauss-Newton step's
                    pred = 0.5 * float(g @ np.linalg.lstsq(H, g, rcond=None)[0])    # predicted gain is within
                    converged = bool(np.isfinite(pred) and pred <= tol * max(1.0, abs(obj)))   # the tolerance
                except np.linalg.LinAlgError:
                    pass
                break
    try:
        cov = np.linalg.inv(H + 1e-12 * np.eye(nc + K))
    except np.linalg.LinAlgError:
        cov, ok = np.full((nc + K, nc + K), np.nan), False
    loglik = -(obj - pen(theta)[0]) if ok else -np.inf        # Decision 11: the likelihood alone, never the penalty
    return Fit(theta[:nc].copy(), {s: float(theta[col[s]]) for s in order}, cov, order, float(loglik),
               bool(ok and np.isfinite(loglik)), bool(converged and ok))


def pooled_start(model, throws, mu):
    """truth-v2 (T2): a start for a family with no prequential posterior. Given inverse masses (situation -> mu), one
    linear regression of every measured acceleration per unit of push (acc / mu - hand) on the family's columns at
    the reading-interval midpoints (as in linear_guess, pooled over the throws)."""
    nc, order, rows, ys = model.n_coef, [], [], []
    for t in throws:
        if t.situation not in order:
            order.append(t.situation)
        xm, vm = .5 * (t.x[:-1] + t.x[1:]), .5 * (t.v[:-1] + t.v[1:])
        mid = (np.arange(xm.size) + 0.5) * paths.DT_OBS
        push = np.zeros(xm.size)
        for s0, s1, f in zip(*_arrays(t.action)):
            push += np.where((mid >= s0) & (mid < s1), f, 0.0)
        nk = model.kind.shape[0]
        row = np.array([[paths.term_t(model.kind[j], model.a[j], model.b[j], x, v, s, model.sx, model.sv)
                         for j in range(nk)] for x, v, s in zip(xm, vm, mid)]).reshape(xm.size, nk)
        rows.append(row if model.tie is None else row @ model.tie)       # Decision 12: tied coefficients' columns
        ys.append((t.v[1:] - t.v[:-1]) / paths.DT_OBS / mu[t.situation] - push)
    coef = np.linalg.lstsq(np.vstack(rows), np.concatenate(ys), rcond=None)[0] if nc else np.zeros(0)
    return Post(np.concatenate([coef, [mu[s] for s in order]]), np.eye(nc + len(order)), order)


def sup_fit(model, throws, sigma, mu, starts=(), stop_above=None, penalty=None):
    """truth-v2 (T2): the maximum-likelihood fit of a family the ledger never weighed (a wide rival). The robust
    likelihood is flat where every throw is a bump, so a start far off never moves. It is started twice - from the
    pooled regression, and from a plain Gaussian fit that every throw pulls - and the higher loglik is kept. A local
    optimum would under-state the rival's best fit and so over-state the claim's evidence: the two starts are the guard,
    and tests/core/test_wide_rivals.py checks it on near-duplicates. independent review (T2-A..C): `starts` adds
    embedded starts (a sub-family's own best fit with the new term at 0), so the result is never below that
    sub-family's best fit; a fit that is not ok, or not converged after one longer search, must never count as a
    rival ruled out (truth.wide_rivals). T3-b2: a start already fitted is not fitted again (E3: the same start gives
    the same fit), and with `stop_above` the search stops at the first ok fit above it (E2: for a caller that only
    needs to know whether the sup exceeds that level). Decision 11: `penalty` (see fit) is passed to every fit; the
    best returned is the highest likelihood among the penalized optima found (each is never below the constrained
    best fit, given it is the penalized objective's maximum: premise U, as for every fit)."""
    start = pooled_start(model, throws, mu)
    fits, seen = [], set()

    def robust_fit(s):
        key = (s.mean.tobytes(), tuple(s.order))
        if key in seen:
            return None
        seen.add(key)
        f = fit(model, throws, sigma, start=s, iters=40, penalty=penalty)
        fits.append(f)
        return f if stop_above is not None and f.ok and f.loglik > stop_above else None

    for s in (start,) + tuple(starts):
        hit = robust_fit(s)
        if hit is not None:
            return hit
    plain = fit(model, throws, sigma, start=start, iters=40, robust=False, penalty=penalty)
    if np.all(np.isfinite(plain.coef)):
        post = Post(np.concatenate([plain.coef, [plain.mu[s] for s in plain.order]]), start.prec, plain.order)
        hit = robust_fit(post)
        if hit is not None:
            return hit
    ok = [f for f in fits if f.ok]
    if not ok:
        return fits[0]                                      # not ok: the caller never counts it as ruled out (T2-A)
    best = max(ok, key=lambda f: f.loglik)
    if not best.converged:                                  # one longer search from the best point (T2-B)
        again = fit(model, throws, sigma, start=Post(np.concatenate([best.coef, [best.mu[s] for s in best.order]]),
                                                     start.prec, best.order), iters=200, penalty=penalty)
        if again.ok and again.loglik >= best.loglik:
            best = again
    return best


def whitened_jacobian(model, fit, throws, sigma):
    throws = [knocked(t, (fit.knocks or {}).get(t.situation, 0)) for t in throws]      # M-1: as the fit saw them
    return _whitened_jacobian(model, fit, throws, sigma)


def _whitened_jacobian(model, fit, throws, sigma):
    """truth-v2 (T1): the stacked Jacobian of every reading over [coef..., mu(situation)...] at a fit, each reading
    divided by its sigma and each throw weighted as in `fit` (by how much the clean part explains it). Its SVD gives
    a band's variances without inverting a near-singular information matrix."""
    nc, K = model.n_coef, len(fit.order)
    col = {s: nc + i for i, s in enumerate(fit.order)}
    scale, norm = _scale(sigma), _log_norm(sigma)
    rows = []
    for t in throws:
        f, J = _jac(model, fit.coef, fit.mu[t.situation], t)
        r = (_obs(t) - f) * scale
        w = 1.0 / (1.0 + math.exp(min(log_outlier(t) - (-0.5 * float(r @ r) + norm), 700.0)))
        full = np.zeros((J.shape[0], nc + K))
        full[:, :nc] = J[:, :nc]
        full[:, col[t.situation]] = J[:, nc]
        rows.append(math.sqrt(w) * scale[:, None] * full)
    return np.vstack(rows)


def interval(model, post, throw, sigma, level=0.95):
    """Central predictive interval for each reading of a throw (readings stacked x then v)."""
    from statistics import NormalDist
    z = NormalDist().inv_cdf(0.5 + level / 2)
    nc = model.n_coef
    cov = post.cov()
    if throw.situation in post.order:
        k = nc + post.order.index(throw.situation)
        mu = post.mean[k]
        idx = list(range(nc)) + [k]
        C = cov[np.ix_(idx, idx)]
    else:
        mu = MU_PRIOR[0]
        C = np.zeros((nc + 1, nc + 1))
        C[:nc, :nc] = cov[:nc, :nc]
        C[nc, nc] = MU_PRIOR[1] ** 2
    f, G = _jac(model, post.mean[:nc], mu, throw)
    d = np.concatenate([np.full(paths.N_OBS, sigma[0] ** 2), np.full(paths.N_OBS, sigma[1] ** 2)])
    sd = np.sqrt(d + np.einsum('ij,jk,ik->i', G, C, G))
    return f - z * sd, f + z * sd


# N-2 (docs/N2_EXACT_NUMERATOR.md; design, not yet the rule): an exactly normalized numerator.
NRES = ((1.0, 0.9), (0.1, 0.08), (0.01, 0.02))      # spacing factor, weight (independent review P-1: skewed, past-only)
LATTICE_SPACING, LATTICE_R, LATTICE_MAX = 0.7, 3.5, 1024       # R 2.5 -> 3.5 on the toy (test_exact_numerator), before any world
_LATTICE_CANDIDATES = 20000


def _log_cell_mass(k, s):
    """log of the standard normal mass of [(k - 1/2) s, (k + 1/2) s), stable in both tails (k: array)."""
    from scipy.special import log_ndtr
    a, b = (k - 0.5) * s, (k + 0.5) * s
    flip = a > 0                                          # measure the tail on the side away from the mean
    lo, hi = np.where(flip, -b, a), np.where(flip, -a, b)
    lhi, llo = log_ndtr(hi), log_ndtr(lo)
    with np.errstate(divide='ignore', invalid='ignore'):
        out = lhi + np.log1p(-np.exp(np.minimum(llo - lhi, 0.0)))
    return np.where(np.isfinite(lhi), out, -np.inf)


def lattice_logq(predict, m, C, G0, y, scale, guide, H, spacing=LATTICE_SPACING, r_eval=LATTICE_R,
                 max_points=LATTICE_MAX):
    """log q(y) for the lattice prior (N-2): the past-only Gaussian N(m, C) over the numbers, cut into cells.

    The frame and the spacing come from the past alone:
    - z = R^T L^-1 (theta - m), with C = L L^T and R the eigenvectors of the predicted information
      (L^T G0^T G0 L, with G0 the whitened Jacobian at m);
    - spacing s_j = spacing / sqrt(1 + lam_j) on each axis;
    - cell k is prod_j [(k_j - 1/2) s_j, (k_j + 1/2) s_j), with prior mass w_k = prod_j of standard normal masses.
      The cells partition the space, so the masses sum to exactly 1.

    q(y) sums w_k N(y; predict(theta_k), diag(scale^-2)) over the cells near `guide`, within r_eval in the metric H.
    At most max_points cells, nearest first. Any subset of this normalized mixture is sub-normalized, so `guide` and
    H may depend on y (e.g. the Laplace mode): the choice costs power, never validity."""
    m, y, scale = np.asarray(m, float), np.asarray(y, float), np.asarray(scale, float)
    d = m.size
    Lc = np.linalg.cholesky(C)
    GL = G0 @ Lc
    lam, R = np.linalg.eigh(GL.T @ GL)
    s = spacing / np.sqrt(1.0 + np.maximum(lam, 0.0))
    T = Lc @ R
    zhat = np.linalg.solve(T, np.asarray(guide, float) - m)
    Hz = T.T @ H @ T
    Hz = 0.5 * (Hz + Hz.T)
    cov = np.linalg.pinv(Hz)
    hw = r_eval * np.sqrt(np.maximum(np.diag(cov), 0.0))
    lo = np.minimum(np.ceil((zhat - hw) / s), np.floor(zhat / s))
    hi = np.maximum(np.floor((zhat + hw) / s), np.ceil(zhat / s))
    counts = hi - lo + 1
    if np.prod(counts) > _LATTICE_CANDIDATES:           # too many: a smaller box around the guide (a subset: valid)
        near = np.round(zhat / s)
        half = np.floor((counts - 1) / 2 * (_LATTICE_CANDIDATES / np.prod(counts)) ** (1.0 / d))
        lo, hi = near - half, near + half
    K = np.stack(np.meshgrid(*[np.arange(a, b + 1) for a, b in zip(lo, hi)], indexing='ij'), -1).reshape(-1, d)
    Z = K * s
    dz = Z - zhat
    d2 = np.einsum('pi,ij,pj->p', dz, Hz, dz)
    order = np.argsort(d2, kind='stable')
    keep = order[d2[order] <= r_eval ** 2][:max_points]
    if keep.size == 0:
        keep = order[:1]
    K, Z = K[keep], Z[keep]
    theta = m + Z @ T.T
    F = np.asarray(predict(theta), float)
    r = (y[None, :] - F) * scale[None, :]
    ll = -0.5 * np.sum(r * r, axis=1) + float(np.log(scale).sum()) - 0.5 * y.size * math.log(2 * math.pi)
    logw = np.sum(_log_cell_mass(K, s[None, :]), axis=1)
    tot = np.where(np.isfinite(logw + ll), logw + ll, -np.inf)     # B N2-a: an exploding path drops its cell only
    top = np.max(tot)
    if not np.isfinite(top):
        return -math.inf
    return float(top + math.log(np.sum(np.exp(tot - top))))


def linearized_logq(f0, G, C, y, scale):
    """N-2b: log N(y; f0, Sigma + G C G^T), the readings' forecast with the numbers' past-only Gaussian N(m, C) pushed
    through the paths linearized at m (f0 = f(m), G = the unwhitened Jacobian at m). An exact Gaussian in y, so
    normalized in any dimension; its power depends on how straight the paths are across the prior."""
    y, f0, scale = np.asarray(y, float), np.asarray(f0, float), np.asarray(scale, float)
    Gs = G * scale[:, None]
    r = (y - f0) * scale
    if not (np.all(np.isfinite(Gs)) and np.all(np.isfinite(r))):
        return -math.inf                                  # B N2-a: this component is dropped (valid)
    try:                                                  # B N2-b: Cholesky; a near-singular C drops the component
        Lc = np.linalg.cholesky(C)
        GL = Gs @ Lc
        Lh = np.linalg.cholesky(np.eye(C.shape[0]) + GL.T @ GL)     # det(C) det(C^-1 + Gs'Gs) = det(I + L'Gs'GsL)
    except np.linalg.LinAlgError:
        return -math.inf
    b = np.linalg.solve(Lh, GL.T @ r)
    quad = float(r @ r) - float(b @ b)                                      # Woodbury, whitened by L
    logdet = -2.0 * float(np.log(scale).sum()) + 2.0 * float(np.log(np.diag(Lh)).sum())
    return -0.5 * quad - 0.5 * logdet - 0.5 * y.size * math.log(2 * math.pi)


def _local_prior(model, post, throw, mu_prior):
    """The past-only Gaussian N(m, C) over (coef, mu of this throw's object): the marginal block for an object met
    before; the coefficients' block and the option's mass prior for a new one."""
    nc = model.n_coef
    cov = np.linalg.inv(post.prec) if post.mean.size else np.zeros((0, 0))
    if throw.situation in post.order:
        loc = list(range(nc)) + [nc + post.order.index(throw.situation)]
        return post.mean[loc].copy(), cov[np.ix_(loc, loc)].copy()
    mean_mu, sd_mu = mu_prior if mu_prior is not None else MU_PRIOR
    C = np.zeros((nc + 1, nc + 1))
    C[:nc, :nc] = cov[:nc, :nc]
    C[nc, nc] = sd_mu ** 2
    return np.concatenate([post.mean[:nc], [mean_mu]]), C


def _mu_lattice_logq(model, m, C, y, scale, throw, guide, H, spacing=LATTICE_SPACING, r_eval=LATTICE_R,
                     max_points=LATTICE_MAX):
    """independent review's P-2: a 1-D lattice over the object's inverse mass (normal-CDF cell masses of its past-only
    marginal), times, in each cell, the coefficients' conditional Gaussian pushed through the paths linearized at
    that mass (linearized_logq). Every component is normalized, in any number of coefficients."""
    nc = m.size - 1
    sd = math.sqrt(C[nc, nc])
    Ccm = C[:nc, nc]
    Ccc = C[:nc, :nc] - np.outer(Ccm, Ccm) / C[nc, nc]
    f0, G = _jac(model, m[:nc], m[nc], throw)                       # past-only: the spacing along mu
    g = G[:, nc] * scale * sd
    s = spacing / math.sqrt(1.0 + float(g @ g))
    Hi = np.linalg.pinv(H)
    zc, zw = (guide[nc] - m[nc]) / sd, r_eval * math.sqrt(max(Hi[nc, nc], 0.0)) / sd
    ks = np.arange(min(math.ceil((zc - zw) / s), math.floor(zc / s)), max(math.floor((zc + zw) / s), math.ceil(zc / s)) + 1)
    ks = ks[np.argsort(np.abs(ks * s - zc), kind='stable')][:max_points].astype(float)
    logw = _log_cell_mass(ks, s)
    out = []
    for k, lw in zip(ks, logw):
        mu = m[nc] + k * s * sd
        mc = m[:nc] + Ccm / C[nc, nc] * (mu - m[nc])
        if nc:
            fk, Gk = _jac(model, mc, mu, throw)
            out.append(lw + linearized_logq(fk, Gk[:, :nc], Ccc, y, scale))
        else:
            r = (y - _sim(model, mc, mu, throw)) * scale
            out.append(lw - 0.5 * float(r @ r) + float(np.log(scale).sum()) - 0.5 * y.size * math.log(2 * math.pi))
    out = np.array(out)
    out = np.where(np.isfinite(out), out, -np.inf)       # B N2-a
    top = out.max()
    return float(top + math.log(np.exp(out - top).sum())) if np.isfinite(top) else -math.inf


def step_exact(model, post, throw, sigma, how='lattice'):
    if KNOCK == 'object':
        raise NotImplementedError('the exact numerator (N-2) is not built for per-object knocks (M-1)')
    """(log q, updated posterior) with an exactly normalized numerator (N-2). The mixture over a new object's mass
    options and the update are as in `step` (the update may use this throw: it is the NEXT throw's prior). The
    Laplace mode only guides which cells are summed (deterministic).
    how: 'lattice' (the full lattice over coefficients and mass) or 'mu' (independent review's P-2)."""
    nc, scale, y = model.n_coef, _scale(sigma), _obs(throw)
    if throw.situation in post.order:
        options = [(None, 1.0)]
    else:
        options = [(None, 1.0)] + [((mu, 2e-3 * mu), n) for mu, n in familiar_masses(model, post)]
    total = sum(w for _, w in options)
    comps = []
    for prior, w in options:
        try:
            m, C = _local_prior(model, post, throw, prior)
        except np.linalg.LinAlgError:               # V395: a past that cannot be inverted: the component is dropped
            comps.append(-math.inf)
            continue
        _, pst = _laplace(model, post, throw, sigma, prior, 30)
        if throw.situation not in pst.order:       # V395: _laplace could not invert a new object's past: no guide
            comps.append(-math.inf)                # and the component is dropped (valid). Any other guide only
            continue                               # picks which cells are summed, so any guide is valid (B, N-2)
        loc = list(range(nc)) + [nc + pst.order.index(throw.situation)]
        guide, H = pst.mean[loc], pst.prec[np.ix_(loc, loc)]
        if how == 'mu':
            lq = _mu_lattice_logq(model, m, C, y, scale, throw, guide, H)
        else:
            _, G = _jac(model, m[:nc], m[nc], throw)
            pred = lambda th: np.stack([_sim(model, t[:nc], t[nc], throw) for t in th])
            # the spacing comes from the forecast at the past mean; where the past is weak (a new object, or the
            # world's first throw) that forecast can be far too coarse (B3 L4-0: 30 posterior widths), so a
            # past-only mixture over finer spacings guards it (design note: NRES)
            weak = throw.situation not in post.order or not post.order
            res = NRES if weak else ((1.0, 1.0),)
            parts = [math.log(wr) + lattice_logq(pred, m, C, G * scale[:, None], y, scale, guide, H,
                                                  spacing=LATTICE_SPACING * fr) for fr, wr in res]
            parts = np.array([p_ if np.isfinite(p_) else -np.inf for p_ in parts])
            top_ = parts.max()
            lq = float(top_ + math.log(np.exp(parts - top_).sum())) if np.isfinite(top_) else -math.inf
        comps.append(math.log(w / total) + lq)
    comps = np.array(comps)
    top = comps.max()
    clean = float(top + math.log(np.exp(comps - top).sum())) if np.isfinite(top) else -math.inf
    a, b = math.log(1 - RHO) + clean, log_outlier(throw)
    log_q = max(a, b) + math.log1p(math.exp(-abs(a - b))) if np.isfinite(max(a, b)) else -math.inf
    _, updated = step(model, post, throw, sigma)
    return log_q, updated
