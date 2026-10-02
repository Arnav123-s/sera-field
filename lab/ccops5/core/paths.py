"""Paths of a pushed object, compiled with numba.

The mind simulates a candidate law exactly the way the 1-D worlds move (RK4 at the world's step, the push and
any bump held constant within a step), so a correct law predicts the noise-free readings exactly and the
likelihood carries no error of the model's own making.

Motion: acceleration = mu * (hand * [t < T_PUSH] + bump + sum_i coef_i * term_i(x, v)).
Term kinds: 0 a grammar idea (a = input 0 position / 1 speed / 2 nothing; b = shape 0 straight, 1 growing,
2 steps, 3 cubic, 4 wave); 1 a smooth basis function P_a(x/sx) * P_b(v/sv) (Legendre, degree <= 2);
2 v^1.5 drag (|v|^1.5 sign v); 3 x*v; and the terms the mind can invent:
4 a product shape_a(x) * shape_b(v); 5 a power |s|^p sign(s) of input a with p = b / 10;
6 a time drive, sin (a = 0) or cos (a = 1) of omega * t with omega = b / 10.
"""
import numpy as np
from numba import njit

DT_SIM = 0.005
DT_OBS = 0.05
T_PUSH = 0.4
T_END = 2.0
N_OBS = int(round(T_END / DT_OBS)) + 1
PER = int(round(DT_OBS / DT_SIM))
BUMP_LEN = 0.2
CLIP = 1e4                      # accelerations beyond this mean a runaway law; the path stops growing


@njit(cache=True)
def _shape(b, s):
    if b == 0:
        return s
    if b == 1:
        return s * abs(s)
    if b == 2:
        return np.tanh(s / 0.05)
    if b == 3:
        return s * s * s
    return np.sin(s)


@njit(cache=True)
def _legendre(n, t):
    if n == 0:
        return 1.0
    if n == 1:
        return t
    return 1.5 * t * t - 0.5


# truth-v2 (B4, docs/B4_GROWTH.md): terms the judge can grow into. Fixed before any data.
CELL_LO = np.array([-3.0, -6.0, 0.0])          # knot ranges per input: x, v, t
CELL_HI = np.array([3.0, 6.0, 2.0])
CELL_K = np.array([9, 17, 33])                 # nested resolutions (9 in 17 in 33)
PIECE_C = np.array([0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0])


DIM_FLAG = 1 << 61                             # Decision 15: an input code at or above this is a dimension SERA made
DIM_PROG = (1 << 56) - 1                       # its program: postfix tokens, 4 bits each, the first lowest (14 at most)


@njit(cache=True)
def _dim(a, x, v, t):
    """Decision 15: (u, du/dx, du/dv) of a dimension's program at (x, v, t). Tokens: 1 position, 2 speed, 3 time,
    4 zero, 5 one, 6 add, 7 sub, 8 mul, 9 lt (1 if a < b else 0), 10 if (c > 0.5: a, else b); nan if malformed."""
    c = a & DIM_PROG
    val = np.zeros(16)
    gx = np.zeros(16)
    gv = np.zeros(16)
    sp = 0
    while c > 0:
        tok = c & 15
        c = c >> 4
        if tok >= 1 and tok <= 5:
            if sp >= 16:
                return np.nan, np.nan, np.nan
            val[sp] = x if tok == 1 else v if tok == 2 else t if tok == 3 else 0.0 if tok == 4 else 1.0
            gx[sp] = 1.0 if tok == 1 else 0.0
            gv[sp] = 1.0 if tok == 2 else 0.0
            sp += 1
        elif tok >= 6 and tok <= 9:
            if sp < 2:
                return np.nan, np.nan, np.nan
            p, px, pv = val[sp - 2], gx[sp - 2], gv[sp - 2]
            q, qx, qv = val[sp - 1], gx[sp - 1], gv[sp - 1]
            sp -= 1
            if tok == 6:
                val[sp - 1], gx[sp - 1], gv[sp - 1] = p + q, px + qx, pv + qv
            elif tok == 7:
                val[sp - 1], gx[sp - 1], gv[sp - 1] = p - q, px - qx, pv - qv
            elif tok == 8:
                val[sp - 1], gx[sp - 1], gv[sp - 1] = p * q, p * qx + q * px, p * qv + q * pv
            else:
                val[sp - 1], gx[sp - 1], gv[sp - 1] = (1.0 if p < q else 0.0), 0.0, 0.0
        elif tok == 10:
            if sp < 3:
                return np.nan, np.nan, np.nan
            k = sp - 2 if val[sp - 3] > 0.5 else sp - 1
            val[sp - 3], gx[sp - 3], gv[sp - 3] = val[k], gx[k], gv[k]
            sp -= 2
        else:
            return np.nan, np.nan, np.nan
    if sp != 1:
        return np.nan, np.nan, np.nan
    return val[0], gx[0], gv[0]


@njit(cache=True)
def _input(a, x, v, t):
    """The measured input of input code a: a % 3 (0 position, 1 speed, 2 time; a lens looks at its base input), or
    (Decision 15) a dimension's program evaluated at (x, v, t)."""
    if a >= DIM_FLAG:
        return _dim(a, x, v, t)[0]
    a = a % 3
    if a == 0:
        return x
    if a == 1:
        return v
    return t


@njit(cache=True)
def _lens(a):
    """Decision 14: the knot range (lo, hi) of input code a. a < 3 is a whole input; a >= 3 is a lens on input a % 3:
    L = a // 3 = j + 8 m looks 2^j times closer, at the window of width W / 2^j centred at lo + m W / 2^(j+1) (W the
    whole input's range). Decision 15: a dimension's range is -R .. R, R = 2^(r - 4), r its 4 bits above the program."""
    if a >= DIM_FLAG:
        R = 2.0 ** (((a >> 56) & 15) - 4)
        return -R, R
    base = a % 3
    lo = CELL_LO[base]
    hi = CELL_HI[base]
    L = a // 3
    if L == 0:
        return lo, hi
    j = L % 8
    m = L // 8
    half = (hi - lo) / 2.0 ** (j + 1)
    c = lo + m * half
    return c - half, c + half


@njit(cache=True)
def _hat(a, b, s):
    """Knot k of a K-knot cell on input a (b = G * 100 + k): hat function, the end knots constant beyond the range."""
    G = b // 100
    k = b - 100 * G
    K = CELL_K[G]
    lo, hi = _lens(a)
    h = (hi - lo) / (K - 1)
    c = lo + k * h
    if k == 0 and s <= c:
        return 1.0
    if k == K - 1 and s >= c:
        return 1.0
    return max(0.0, 1.0 - abs(s - c) / h)


@njit(cache=True)
def _dhat(a, b, s):
    G = b // 100
    k = b - 100 * G
    K = CELL_K[G]
    lo, hi = _lens(a)
    h = (hi - lo) / (K - 1)
    c = lo + k * h
    if (k == 0 and s <= c) or (k == K - 1 and s >= c) or abs(s - c) >= h:
        return 0.0
    return -1.0 / h if s > c else 1.0 / h


@njit(cache=True)
def _piece(code, s):
    """A part of a grown term: 0-4 the grammar's shapes, 5 |s|, 6-14 tanh(s / C), 15-23 exp(-s^2 / C)."""
    if code < 5:
        return _shape(code, s)
    if code == 5:
        return abs(s)
    if code < 15:
        return np.tanh(s / PIECE_C[code - 6])
    return np.exp(-s * s / PIECE_C[code - 15])


@njit(cache=True)
def _dpiece(code, s):
    if code < 5:
        return _dshape(code, s)
    if code == 5:
        return 0.0 if s == 0.0 else (1.0 if s > 0 else -1.0)
    if code < 15:
        c = PIECE_C[code - 6]
        th = np.tanh(s / c)
        return (1.0 - th * th) / c
    c = PIECE_C[code - 15]
    return -2.0 * s / c * np.exp(-s * s / c)


@njit(cache=True)
def _ramp(a, x, v, t):
    """Decision 16 (review 11, the direct route): a dimension's value clipped at its range, -R .. R; nan when the input
    code is no dimension or its program gives no finite value (fail closed: a clip must not hide bad arithmetic)."""
    if a < DIM_FLAG:
        return np.nan
    u = _dim(a, x, v, t)[0]
    if not np.isfinite(u):
        return np.nan
    R = _lens(a)[1]
    return min(max(u, -R), R)


@njit(cache=True)
def _dramp(a, x, v, t):
    """(d ramp / dx, d ramp / dv): (du/dx, du/dv) strictly inside -R .. R, 0 at and beyond the ends (a kink there:
    the convention, checked by finite differences); nan where the program is not finite."""
    if a < DIM_FLAG:
        return np.nan, np.nan
    u, ux, uv = _dim(a, x, v, t)
    if not (np.isfinite(u) and np.isfinite(ux) and np.isfinite(uv)):
        return np.nan, np.nan
    R = _lens(a)[1]
    if -R < u < R:
        return ux, uv
    return 0.0, 0.0


@njit(cache=True)
def _unary_code(b):
    """kind 8's b = op * 16 + i  ->  the part code: |s| (5), tanh(s / C[i]) (6 + i), exp(-s^2 / C[i]) (15 + i)."""
    op = b // 16
    i = b - 16 * op
    if op == 0:
        return 5
    if op == 1:
        return 6 + i
    return 15 + i


@njit(cache=True)
def term_t(kind, a, b, x, v, t, sx, sv):
    if kind == 0:
        if a == 2:
            return 1.0
        return _shape(b, x if a == 0 else v)
    if kind == 1:
        return _legendre(a, x / sx) * _legendre(b, v / sv)
    if kind == 2:
        return np.sign(v) * abs(v) ** 1.5
    if kind == 3:
        return x * v
    if kind == 4:
        return _shape(a, x) * _shape(b, v)
    if kind == 5:
        s = x if a == 0 else v
        return np.sign(s) * abs(s) ** (b / 10.0)
    if kind == 7:
        return _hat(a, b, _input(a, x, v, t))
    if kind == 8:
        return _piece(_unary_code(b), _input(a, x, v, t))
    if kind == 9:
        return _piece(a, x) * _piece(b, v)
    if kind == 10:                                     # Decision 16: a ramp, c * clip(u, -R, R) of a dimension's u
        return _ramp(a, x, v, t)
    w = b / 10.0
    return np.sin(w * t) if a == 0 else np.cos(w * t)


@njit(cache=True)
def term(kind, a, b, x, v, sx, sv):
    return term_t(kind, a, b, x, v, 0.0, sx, sv)


@njit(cache=True)
def _acc(x, v, t, f, mu, kind, a, b, coef, sx, sv):
    tot = f
    for i in range(kind.shape[0]):
        tot += coef[i] * term_t(kind[i], a[i], b[i], x, v, t, sx, sv)
    acc = mu * tot
    if acc > CLIP:
        return CLIP
    if acc < -CLIP:
        return -CLIP
    return acc


@njit(cache=True)
def simulate_program(t0s, t1s, forces, mu, kind, a, b, coef, sx, sv, bump_t0, bump_amp):
    """Noise-free readings (x and v at N_OBS times) of one push program: force forces[i] (the hand's force for
    the command) during [t0s[i], t1s[i]), held constant within each integration step as the worlds do."""
    xs = np.zeros(N_OBS)
    vs = np.zeros(N_OBS)
    x = 0.0
    v = 0.0
    h = DT_SIM
    step = 0
    nseg = t0s.shape[0]
    for n in range(1, N_OBS):
        for _ in range(PER):
            t = step * h
            f = 0.0
            for s in range(nseg):
                if t >= t0s[s] - 1e-9 and t < t1s[s] - 1e-9:
                    f += forces[s]
            if bump_amp != 0.0 and t >= bump_t0 - 1e-9 and t < bump_t0 + BUMP_LEN - 1e-9:
                f += bump_amp
            k1x = v
            k1v = _acc(x, v, t, f, mu, kind, a, b, coef, sx, sv)
            k2x = v + .5 * h * k1v
            k2v = _acc(x + .5 * h * k1x, v + .5 * h * k1v, t + .5 * h, f, mu, kind, a, b, coef, sx, sv)
            k3x = v + .5 * h * k2v
            k3v = _acc(x + .5 * h * k2x, v + .5 * h * k2v, t + .5 * h, f, mu, kind, a, b, coef, sx, sv)
            k4x = v + h * k3v
            k4v = _acc(x + h * k3x, v + h * k3v, t + h, f, mu, kind, a, b, coef, sx, sv)
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            step += 1
        xs[n] = x
        vs[n] = v
    return xs, vs


@njit(cache=True)
def simulate(hand, mu, kind, a, b, coef, sx, sv, bump_t0, bump_amp):
    """One push of force `hand` for the first T_PUSH seconds (the teacher's push)."""
    return simulate_program(np.array([0.0]), np.array([T_PUSH]), np.array([hand]), mu, kind, a, b, coef, sx, sv,
                            bump_t0, bump_amp)


@njit(cache=True)
def _dshape(b, s):
    """d shape_b(s) / ds."""
    if b == 0:
        return 1.0
    if b == 1:
        return 2.0 * abs(s)
    if b == 2:
        th = np.tanh(s / 0.05)
        return (1.0 - th * th) / 0.05
    if b == 3:
        return 3.0 * s * s
    return np.cos(s)


@njit(cache=True)
def _dlegendre(n, t):
    if n == 0:
        return 0.0
    if n == 1:
        return 1.0
    return 3.0 * t


@njit(cache=True)
def _dterm(kind, a, b, x, v, sx, sv, t=0.0):
    """(d term / dx, d term / dv). A power |s|^p with p < 1 has an infinite slope at s = 0 exactly; there the
    sensitivities it multiplies are those of a path at rest, and the slope is taken as 0."""
    if kind == 0:
        if a == 2:
            return 0.0, 0.0
        if a == 0:
            return _dshape(b, x), 0.0
        return 0.0, _dshape(b, v)
    if kind == 1:
        return (_dlegendre(a, x / sx) / sx * _legendre(b, v / sv),
                _legendre(a, x / sx) * _dlegendre(b, v / sv) / sv)
    if kind == 2:
        return 0.0, 1.5 * abs(v) ** 0.5
    if kind == 3:
        return v, x
    if kind == 4:
        return _dshape(a, x) * _shape(b, v), _shape(a, x) * _dshape(b, v)
    if kind == 5:
        s = x if a == 0 else v
        p = b / 10.0
        d = 0.0 if s == 0.0 else p * abs(s) ** (p - 1.0)
        return (d, 0.0) if a == 0 else (0.0, d)
    if kind == 7:
        if a >= DIM_FLAG:                              # Decision 15: through its program (the chain rule)
            u, ux, uv = _dim(a, x, v, t)
            d = _dhat(a, b, u)
            return d * ux, d * uv
        base = a % 3                                   # Decision 14: a lens moves with its base input
        if base == 2:
            return 0.0, 0.0
        d = _dhat(a, b, x if base == 0 else v)
        return (d, 0.0) if base == 0 else (0.0, d)
    if kind == 8:
        if a == 2:
            return 0.0, 0.0
        d = _dpiece(_unary_code(b), x if a == 0 else v)
        return (d, 0.0) if a == 0 else (0.0, d)
    if kind == 9:
        return _dpiece(a, x) * _piece(b, v), _piece(a, x) * _dpiece(b, v)
    if kind == 10:                                     # Decision 16: the dimension's own chain rule strictly inside
        return _dramp(a, x, v, t)                      # its range, nothing at or beyond it
    return 0.0, 0.0


@njit(cache=True)
def _acc_sens(x, v, t, f, mu, kind, a, b, coef, sx, sv, sxs, svs, out):
    """The acceleration (the same number as _acc) and, into out[j], its total derivative with respect to
    parameter j (coefficients, then mu) given the stage's state sensitivities sxs, svs."""
    n = kind.shape[0]
    tot = f
    ax = 0.0
    av = 0.0
    for i in range(n):
        ti = term_t(kind[i], a[i], b[i], x, v, t, sx, sv)
        tot += coef[i] * ti
        out[i] = ti
        dx, dv = _dterm(kind[i], a[i], b[i], x, v, sx, sv, t)
        ax += coef[i] * dx
        av += coef[i] * dv
    acc = mu * tot
    if acc > CLIP or acc < -CLIP:
        for j in range(n + 1):
            out[j] = 0.0
        return CLIP if acc > CLIP else -CLIP
    for j in range(n):
        out[j] = mu * out[j] + mu * (ax * sxs[j] + av * svs[j])
    out[n] = tot + mu * (ax * sxs[n] + av * svs[n])
    return acc


@njit(cache=True)
def jacobian_exact(t0s, t1s, forces, mu, kind, a, b, coef, sx, sv, bump_t0, bump_amp):
    """Readings and their exact derivatives in one pass (forward-mode through the same RK4 steps as
    simulate_program): columns = each coefficient, then mu. Returns (y (2N,), J (2N, n + 1)); y is bit-identical
    to simulate_program. Compute batch K, 2026-09-24."""
    n = kind.shape[0]
    m = n + 1
    y = np.zeros(2 * N_OBS)
    J = np.zeros((2 * N_OBS, m))
    x = 0.0
    v = 0.0
    Sx = np.zeros(m)
    Sv = np.zeros(m)
    s2x = np.empty(m)
    s2v = np.empty(m)
    d1 = np.empty(m)
    d2 = np.empty(m)
    d3 = np.empty(m)
    d4 = np.empty(m)
    dk2x = np.empty(m)
    dk3x = np.empty(m)
    h = DT_SIM
    step = 0
    nseg = t0s.shape[0]
    for r in range(1, N_OBS):
        for _ in range(PER):
            t = step * h
            f = 0.0
            for s in range(nseg):
                if t >= t0s[s] - 1e-9 and t < t1s[s] - 1e-9:
                    f += forces[s]
            if bump_amp != 0.0 and t >= bump_t0 - 1e-9 and t < bump_t0 + BUMP_LEN - 1e-9:
                f += bump_amp
            k1x = v
            k1v = _acc_sens(x, v, t, f, mu, kind, a, b, coef, sx, sv, Sx, Sv, d1)
            for j in range(m):
                s2x[j] = Sx[j] + .5 * h * Sv[j]
                s2v[j] = Sv[j] + .5 * h * d1[j]
            k2x = v + .5 * h * k1v
            k2v = _acc_sens(x + .5 * h * k1x, v + .5 * h * k1v, t + .5 * h, f, mu, kind, a, b, coef, sx, sv,
                            s2x, s2v, d2)
            dk2x[:] = s2v
            for j in range(m):
                s2x[j] = Sx[j] + .5 * h * dk2x[j]
                s2v[j] = Sv[j] + .5 * h * d2[j]
            k3x = v + .5 * h * k2v
            k3v = _acc_sens(x + .5 * h * k2x, v + .5 * h * k2v, t + .5 * h, f, mu, kind, a, b, coef, sx, sv,
                            s2x, s2v, d3)
            dk3x[:] = s2v
            for j in range(m):
                s2x[j] = Sx[j] + h * dk3x[j]
                s2v[j] = Sv[j] + h * d3[j]
            k4x = v + h * k3v
            k4v = _acc_sens(x + h * k3x, v + h * k3v, t + h, f, mu, kind, a, b, coef, sx, sv, s2x, s2v, d4)
            dk4x = s2v
            for j in range(m):
                Sx[j] += h / 6 * (Sv[j] + 2 * dk2x[j] + 2 * dk3x[j] + dk4x[j])
                Sv[j] += h / 6 * (d1[j] + 2 * d2[j] + 2 * d3[j] + d4[j])
            x += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            step += 1
        y[r] = x
        y[N_OBS + r] = v
        for j in range(m):
            J[r, j] = Sx[j]
            J[N_OBS + r, j] = Sv[j]
    return y, J


@njit(cache=True)
def jacobian_program(t0s, t1s, forces, mu, kind, a, b, coef, sx, sv, bump_t0, bump_amp, free_coef):
    """Readings and their derivatives by forward differences: columns = each free coefficient, then mu.
    Returns (y (2N,), J (2N, n_free + 1))."""
    xs, vs = simulate_program(t0s, t1s, forces, mu, kind, a, b, coef, sx, sv, bump_t0, bump_amp)
    return jacobian_from_base(t0s, t1s, forces, mu, kind, a, b, coef, sx, sv, bump_t0, bump_amp, free_coef, xs, vs)


@njit(cache=True)
def jacobian_from_base(t0s, t1s, forces, mu, kind, a, b, coef, sx, sv, bump_t0, bump_amp, free_coef, xs, vs):
    """`jacobian_program` given the base path (xs, vs) already simulated at these numbers (2026-09-24: the fits
    had just simulated it, so this saves one simulation per Jacobian; every number is the same)."""
    n = xs.shape[0]
    y = np.empty(2 * n)
    y[:n] = xs
    y[n:] = vs
    nf = free_coef.shape[0]
    J = np.empty((2 * n, nf + 1))
    c2 = coef.copy()
    for j in range(nf):
        i = free_coef[j]
        step = 1e-5 * max(1.0, abs(coef[i]))
        c2[i] = coef[i] + step
        x2, v2 = simulate_program(t0s, t1s, forces, mu, kind, a, b, c2, sx, sv, bump_t0, bump_amp)
        c2[i] = coef[i]
        for r in range(n):
            J[r, j] = (x2[r] - xs[r]) / step
            J[n + r, j] = (v2[r] - vs[r]) / step
    step = 1e-6 * max(1.0, abs(mu))
    x2, v2 = simulate_program(t0s, t1s, forces, mu + step, kind, a, b, coef, sx, sv, bump_t0, bump_amp)
    for r in range(n):
        J[r, nf] = (x2[r] - xs[r]) / step
        J[n + r, nf] = (v2[r] - vs[r]) / step
    return y, J
