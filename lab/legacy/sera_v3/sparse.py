"""The Field's sparse proposer (the author's direction, 2026-09-25 20:00: compressed sensing - Candes, Romberg & Tao 2006 -
to find the few terms the data wants among many, with no bookkeeping). The lasso (Tibshirani 1996) over the whole term
dictionary - the 11 base ideas and every universe term of the judge's stage-1 audit (truth-v1's invented terms, the
grown pieces and piece products; 878 columns) - followed exactly along its path (the LARS-lasso homotopy) from
the evidence table's sufficient statistics alone (G = Phi' W Phi, b = Phi' W z; sera.field.Stats): one small solve per
proposal, whatever the number of laws.

It PROPOSES; it never proves. The dictionary's look-alike columns (v, |v|, tanh(v/3) on one-sided data; neighbouring
drive frequencies) are nearly collinear, far outside the incoherence the recovery theorems need, so which of a
look-alike group enters first is not evidence, and the judge never reads any of this. What it is for: which grown
terms are worth weighing (growth), and which rivals the universe audit should try first."""
import numpy as np

from ccops5.core import checker, grammar, truth
from . import compact as C, field as F

DICT = C.TERMS + tuple(t for t in truth.UNIVERSE_TERMS if t not in C.TERM_INDEX)
INDEX = {t: i for i, t in enumerate(DICT)}
_GROWN = DICT[len(C.TERMS):]


def columns(x, v, t):
    """phi_j at each point for every term in DICT: the Field's 270 columns, then each grown term from the checker's
    independent formula (checker._grown_np, verified against the judge's simulator)."""
    grown = np.stack([checker._grown_np(term, x, v, t)[0] for term in _GROWN], 1)
    return np.concatenate([C.columns(x, v, t), grown], axis=1)


def stats(throws, mu, skip=()):
    """The evidence table's sufficient statistics over DICT (as sera.field.evidence, with every column)."""
    obj, y, fb, xb, vb, tb = C.intervals(throws)
    keep = np.array([o in mu and o not in skip for o in obj], bool)
    m = np.array([mu[o] for o in obj[keep]], float)
    z = y[keep] / m - fb[keep]
    d = (C.SIGMA_Y / m) ** 2
    return F.Stats.from_arrays(columns(xb[keep], vb[keep], tb[keep]), d, z)


def _homotopy(G, b, w, lam_stop=0.0, k=None, max_steps=5000):
    """The exact lasso path of argmin_c 1/2 c'Gc - b'c + lam sum_j w_j |c_j| (LARS with the lasso modification:
    Efron, Hastie, Johnstone & Tibshirani 2004; Osborne, Presnell & Turlach 2000), followed from lam_max (nothing in)
    down to lam_stop, or until k distinct columns have entered. On the standardized scale (beta_j = w_j c_j) each step
    moves the active coefficients along G_AA^-1 s until a column joins (its correlation reaches the active ones') or
    an active coefficient reaches 0 (it leaves). A column the active set already spans on these data (residual below
    1e-10 of its own variance) cannot be told apart from it and is set aside. Returns (c, entry order, final lam)."""
    n = len(b)
    ok = np.isfinite(w) & (np.diag(G) > 0)
    idx = np.flatnonzero(ok)
    ws = w[idx]
    Gs = G[np.ix_(idx, idx)] / np.outer(ws, ws)
    corr = b[idx] / ws                                                  # b - G c, standardized
    beta = np.zeros(len(idx))
    free = np.ones(len(idx), bool)                                      # neither active nor set aside
    active, signs, entered = [], [], []
    lam = float(np.max(np.abs(corr))) if len(idx) else 0.0
    if len(idx) and lam > lam_stop:
        j = int(np.argmax(np.abs(corr)))
        active, signs, entered = [j], [float(np.sign(corr[j]))], [j]
        free[j] = False
    for _ in range(max_steps):
        if not active or lam <= lam_stop or (k is not None and len(entered) >= k):
            break
        A = np.array(active)
        d = np.linalg.solve(Gs[np.ix_(A, A)], np.array(signs))
        a = Gs[:, A] @ d
        step, event = lam - lam_stop, None
        cand = np.flatnonzero(free)
        if cand.size:
            cj, aj = corr[cand], a[cand]
            with np.errstate(divide='ignore', invalid='ignore'):
                g1 = np.where(1 - aj > 1e-12, (lam - cj) / (1 - aj), np.inf)
                g2 = np.where(1 + aj > 1e-12, (lam + cj) / (1 + aj), np.inf)
            g = np.minimum(np.where(g1 > 1e-12 * lam, g1, np.inf), np.where(g2 > 1e-12 * lam, g2, np.inf))
            i = int(np.argmin(g))
            if g[i] < step:
                step, event = float(g[i]), ('join', int(cand[i]))
        with np.errstate(divide='ignore', invalid='ignore'):
            gd = np.where(d * np.sign(beta[A]) < 0, -beta[A] / d, np.inf)      # heading for 0
        gd = np.where(gd > 1e-12 * lam, gd, np.inf)
        i = int(np.argmin(gd))
        if gd[i] < step:
            step, event = float(gd[i]), ('drop', int(A[i]))
        beta[A] += step * d
        corr -= step * a
        lam -= step
        if event is None:
            break
        kind, j = event
        if kind == 'drop':
            pos = active.index(j)
            active.pop(pos)
            signs.pop(pos)
            beta[j] = 0.0
            free[j] = True
            continue
        A = np.array(active)
        resid = Gs[j, j] - Gs[j, A] @ np.linalg.solve(Gs[np.ix_(A, A)], Gs[A, j])
        free[j] = False
        if resid <= 1e-10 * Gs[j, j]:
            continue                                                    # set aside: spanned by the active set
        active.append(j)
        signs.append(float(np.sign(corr[j])))
        if j not in entered:
            entered.append(j)
    c = np.zeros(n)
    c[idx] = beta / ws
    return c, [int(idx[e]) for e in entered], lam


def lasso(G, b, lam, w):
    """argmin_c 1/2 c'Gc - b'c + lam sum_j w_j |c_j| (w_j > 0; a column with w_j = inf never enters), exactly, by
    following the path down to lam."""
    return _homotopy(G, b, w, lam_stop=lam)[0]


def weights(st):
    """Standardized penalty weights: sqrt(G_jj), so a column's units do not decide whether it enters; a column that
    is zero on the data never enters."""
    d = np.diag(st.G)
    return np.where(d > 0, np.sqrt(np.maximum(d, 0.0)), np.inf)


def path(st, k):
    """The first k columns (indices into DICT) to enter the exact lasso path, in order of entry."""
    return _homotopy(st.G, st.b, weights(st), k=k)[1][:k]
