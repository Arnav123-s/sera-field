"""Evidence compaction (B2, low compute): a world's throws squeezed into a small table the imagination reads.

Your research's Tier-4 idea (store a long trajectory as a few coefficients over a basis) applied to discovery: instead
of feeding raw readings to a big network, SERA measures, for every candidate law piece ("term"), how much of the
motion it explains and whether its strength agrees across objects. One pass of small least-squares fits, a few
milliseconds per world on one CPU thread.

Motion law per reading interval n of a throw (velocity-change form: the hand term is exact for piecewise-constant
pushes; the law term is evaluated at endpoint-averaged measured states, a midpoint approximation, O(DT^2)):
    y_n = (v_{n+1} - v_n) / DT  =  mu_k * ( fbar_n + sum_j c_j * phi_j(xbar_n, vbar_n, tbar_n) )
fbar_n is the hand's mean force over the interval; xbar, vbar, tbar the interval midpoints; mu_k the unknown inverse
mass of object k. Per object and term: least squares y ~ alpha*fbar + beta*phi_j (alpha = mu, beta/alpha = c_j).

Features per term (TERM_FEATURES, one row per term in TERMS):
  0 mean over objects of the variance explained by adding the term (0..1)
  1 min over objects of the same (a real term helps every object)
  2 log(1 + total evidence), evidence = (SSE without - SSE with) / sigma_y^2 summed over objects (a feature, not a
    calibrated likelihood: consecutive velocity changes share a reading, correlation -0.5)
  3 sign agreement of the implied coefficient across objects (|mean sign|)
  4 median log10 |implied coefficient|
  5 spread (std) of log10 |implied coefficient| across objects (a real term has one strength for all objects)
  6 log(1 + evidence of adding the term after the world's best single term) (0 for the best term itself)
  7 1 for the world's best single term
World features (WORLD_FEATURES): objects, throws, share of variance left after the best single term and after the
best pair found greedily, log max |x|, log max |v|, log mean inverse mass estimate.
"""
import numpy as np

from ccops5.core import grammar, paths

TERMS = tuple(grammar.IDEAS) + tuple(grammar.OPEN_TERMS)          # 11 base ideas + 259 invented terms = 270
TERM_INDEX = {t: i for i, t in enumerate(TERMS)}
TERM_FEATURES = 8
WORLD_FEATURES = 7
DT = paths.DT_OBS
SIGMA_Y = np.sqrt(2) * 0.001 / DT                                   # noise of a velocity-change reading


def _shapes(s):
    return np.stack([s, s * np.abs(s), np.tanh(s / 0.05), s ** 3, np.sin(s)], axis=-1)   # grammar.SHAPES order


_P = np.array([t[2] for t in grammar.OPEN_TERMS if t[0] == 'power'])
_POW_INPUT = np.array([0 if t[1] == 'position' else 1 for t in grammar.OPEN_TERMS if t[0] == 'power'])
_W = np.array([t[2] for t in grammar.OPEN_TERMS if t[0] == 'drive'])
_DRV_SIN = np.array([t[1] == 'sin' for t in grammar.OPEN_TERMS if t[0] == 'drive'])
_PROD = [(grammar.SHAPES.index(t[1]), grammar.SHAPES.index(t[2])) for t in grammar.OPEN_TERMS if t[0] == 'product']


def columns(x, v, t):
    """phi_j at each point for every term in TERMS: (n, 270)."""
    sx, sv = _shapes(x), _shapes(v)
    base = []
    for inp, shp in grammar.IDEAS:
        if inp == 'nothing':
            base.append(np.ones_like(x))
        else:
            base.append((sx if inp == 'position' else sv)[:, grammar.SHAPES.index(shp)])
    prods = [sx[:, i] * sv[:, j] for i, j in _PROD]
    s_in = np.where(_POW_INPUT[None, :] == 0, x[:, None], v[:, None])
    pows = np.sign(s_in) * np.abs(s_in) ** _P[None, :]
    wt = _W[None, :] * t[:, None]
    drives = np.where(_DRV_SIN[None, :], np.sin(wt), np.cos(wt))
    return np.concatenate([np.stack(base, 1), np.stack(prods, 1), pows, drives], axis=1)


def mean_force(action):
    """The hand's mean force over each reading interval (N_OBS - 1 values)."""
    t0s, t1s, forces = action.arrays()
    lo = np.arange(paths.N_OBS - 1) * DT
    hi = lo + DT
    out = np.zeros(paths.N_OBS - 1)
    for s0, s1, f in zip(t0s, t1s, forces):
        out += f * np.clip(np.minimum(hi, s1) - np.maximum(lo, s0), 0, None) / DT
    return out


def intervals(throws):
    """Stack every throw's intervals: (object id, y, fbar, xbar, vbar, tbar). Throws need .situation, .action, .x, .v."""
    obj, y, fb, xb, vb, tb = [], [], [], [], [], []
    tt = np.arange(paths.N_OBS) * DT
    for th in throws:
        obj.append(np.full(paths.N_OBS - 1, th.situation))
        y.append(np.diff(th.v) / DT)
        fb.append(mean_force(th.action))
        xb.append(0.5 * (th.x[:-1] + th.x[1:]))
        vb.append(0.5 * (th.v[:-1] + th.v[1:]))
        tb.append(0.5 * (tt[:-1] + tt[1:]))
    return tuple(np.concatenate(a) for a in (obj, y, fb, xb, vb, tb))


def _fit2(ff, fp, pp, fy, py):
    """Least squares y ~ a f + b p for many p at once (closed form); returns a, b and the SSE reduction terms."""
    det = ff * pp - fp * fp
    ok = det > 1e-12 * np.maximum(ff * pp, 1e-300)
    a = np.where(ok, (pp * fy - fp * py) / np.where(ok, det, 1), fy / ff)
    b = np.where(ok, (ff * py - fp * fy) / np.where(ok, det, 1), 0.0)
    explained = a * fy + b * py                                      # = yy - SSE
    return a, b, explained


def compact(throws):
    """(term features (270, 8) float32, world features (7,) float32, extras dict) for the throws seen so far."""
    obj, y, fb, xb, vb, tb = intervals(throws)
    Phi = columns(xb, vb, tb)
    objs = np.unique(obj)
    nT = len(TERMS)
    gain = np.zeros((len(objs), nT))
    ev = np.zeros((len(objs), nT))
    coef = np.zeros((len(objs), nT))
    mu0 = np.zeros(len(objs))
    grams = []
    for k, o in enumerate(objs):
        m = obj == o
        f, yy, P = fb[m], y[m], Phi[m]
        ff, fy, y2 = f @ f, f @ yy, yy @ yy
        if ff <= 0:                                                  # no push on this object: nothing to scale by
            ff = 1e-12
        fp, pp, py = f @ P, np.einsum('ij,ij->j', P, P), yy @ P
        sse0 = y2 - fy * fy / ff if ff > 0 else y2
        a, b, expl = _fit2(ff, fp, pp, fy, py)
        sse = np.maximum(y2 - expl, 0.0)
        gain[k] = np.clip(1 - sse / max(sse0, 1e-300), 0, 1)
        ev[k] = np.maximum(sse0 - sse, 0) / SIGMA_Y ** 2
        coef[k] = np.where(np.abs(a) > 1e-9, b / np.where(np.abs(a) > 1e-9, a, 1), 0.0)
        mu0[k] = fy / ff if ff > 0 else 0.0
        grams.append((f, yy, P, ff, fy, y2, fp, pp, py, sse0))
    total = ev.sum(0)
    best = int(np.argmax(total))
    # second stage: evidence of each term added to (push, best term), and the greedy best pair
    ev2 = np.zeros(nT)
    left1 = left2 = 0.0
    tot0 = 0.0
    for f, yy, P, ff, fy, y2, fp, pp, py, sse0 in grams:
        q = P[:, best]
        A = np.array([[ff, fp[best]], [fp[best], pp[best]]])
        rhs = np.array([fy, py[best]])
        try:
            sol = np.linalg.solve(A, rhs)
        except np.linalg.LinAlgError:
            sol = np.linalg.lstsq(A, rhs, rcond=None)[0]
        sse1 = max(y2 - sol @ rhs, 0.0)
        # add term j: 3x3 normal equations for all j, by projecting on the (f, q) fit's residual space
        r = yy - np.column_stack([f, q]) @ sol
        Bf = np.column_stack([f, q])
        G = Bf.T @ Bf
        Ginv = np.linalg.pinv(G)
        proj = Bf @ (Ginv @ (Bf.T @ P))                               # P projected on span(f, q)
        Pr = P - proj
        num = (r @ Pr) ** 2
        den = np.einsum('ij,ij->j', Pr, Pr)
        drop = np.where(den > 1e-12, num / np.where(den > 1e-12, den, 1), 0.0)
        drop[best] = 0.0
        ev2 += drop / SIGMA_Y ** 2
        left1 += sse1
        left2 += sse1 - drop.max()
        tot0 += max(sse0, 1e-300)
    signs = np.sign(coef)
    logc = np.log10(np.abs(coef) + 1e-6)
    feats = np.stack([gain.mean(0), gain.min(0), np.log1p(total), np.abs(signs.mean(0)), np.median(logc, 0),
                      logc.std(0), np.log1p(ev2), (np.arange(nT) == best).astype(float)], axis=1)
    xs = np.concatenate([t.x for t in throws])
    vs = np.concatenate([t.v for t in throws])
    world = np.array([len(objs) / 8, len(throws) / 40, left1 / tot0, max(left2, 0.0) / tot0,
                      np.log10(np.abs(xs).max() + 1e-3), np.log10(np.abs(vs).max() + 1e-3),
                      np.log(np.clip(np.mean(mu0), 1e-3, None))])
    extras = dict(best=best, coef_median=np.median(coef, 0), mu0=dict(zip(objs.tolist(), mu0.tolist())))
    return feats.astype(np.float32), world.astype(np.float32), extras
