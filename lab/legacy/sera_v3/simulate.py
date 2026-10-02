"""Batched world physics for SERA v3 (torch): many throws at once, the same motion law as `ccops5.core.paths`.

Motion: acceleration = mu * (push(t) + bump(t) + sum_j coef_j * term_j(x, v, t)), clipped at +-CLIP; RK4 at DT_SIM,
readings every DT_OBS, from rest. Term codes are ccops5's (kind, a, b) (see paths.py), so a family simulated here
moves exactly as the judge's own simulator moves it. In float64 on the CPU the readings agree with
`paths.simulate_program` to rounding (tests/sera/test_simulate.py); dreams run in float32 on the GPU.

Batch layout (B throws): kind, a, b, coef (B, T) term slots (padding: coef 0); mu (B,); segments t0, t1, force
(B, S) (padding: t0 = t1 = 0, never active); bump_t0, bump_amp (B,).
"""
import torch

from ccops5.core import paths

DT_SIM, DT_OBS, N_OBS, PER, BUMP_LEN, CLIP = (paths.DT_SIM, paths.DT_OBS, paths.N_OBS, paths.PER, paths.BUMP_LEN,
                                              paths.CLIP)


def _shape(b, s):
    """paths._shape, elementwise over tensors: 0 straight, 1 growing, 2 steps, 3 cubic, 4 wave."""
    out = torch.sin(s)
    out = torch.where(b == 3, s * s * s, out)
    out = torch.where(b == 2, torch.tanh(s / 0.05), out)
    out = torch.where(b == 1, s * torch.abs(s), out)
    return torch.where(b == 0, s, out)


def _legendre(n, u):
    return torch.where(n == 0, torch.ones_like(u), torch.where(n == 1, u, 1.5 * u * u - 0.5))


def term_t(kind, a, b, x, v, t, sx=1.0, sv=1.0):
    """paths.term_t over tensors (all broadcastable)."""
    s_in = torch.where(a == 0, x, v)
    k0 = torch.where(a == 2, torch.ones_like(s_in), _shape(b, s_in))
    k1 = _legendre(a, x / sx) * _legendre(b, v / sv)
    k2 = torch.sign(v) * torch.abs(v) ** 1.5
    k3 = x * v
    k4 = _shape(a, x) * _shape(b, v)
    bf = b.to(x.dtype)                     # exponents and frequencies in the readings' precision (b / 10 exactly)
    k5 = torch.sign(s_in) * torch.abs(s_in) ** (bf / 10.0)
    w = bf / 10.0
    k6 = torch.where(a == 0, torch.sin(w * t), torch.cos(w * t))
    out = k6
    for code, val in ((5, k5), (4, k4), (3, k3), (2, k2), (1, k1), (0, k0)):
        out = torch.where(kind == code, val, out)
    return out


def _acc(x, v, t, f, mu, kind, a, b, coef):
    tot = f
    for j in range(kind.shape[1]):
        tot = tot + coef[:, j] * term_t(kind[:, j], a[:, j], b[:, j], x, v, t)
    return torch.clamp(mu * tot, -CLIP, CLIP)


def _hand(t, t0, t1, force, bump_t0, bump_amp):
    active = (t >= t0 - 1e-9) & (t < t1 - 1e-9)
    f = (force * active).sum(dim=1)
    bump = (bump_amp != 0) & (t >= bump_t0 - 1e-9) & (t < bump_t0 + BUMP_LEN - 1e-9)
    return f + torch.where(bump, bump_amp, torch.zeros_like(bump_amp))


@torch.no_grad()
def simulate(kind, a, b, coef, mu, t0, t1, force, bump_t0, bump_amp):
    """Noise-free readings (x, v), each (B, N_OBS), of B throws from rest."""
    B = mu.shape[0]
    x = torch.zeros(B, dtype=mu.dtype, device=mu.device)
    v = torch.zeros_like(x)
    xs, vs = [x], [v]
    h = DT_SIM
    step = 0
    for _ in range(1, N_OBS):
        for _ in range(PER):
            t = step * h
            f = _hand(t, t0, t1, force, bump_t0, bump_amp)
            k1x = v
            k1v = _acc(x, v, t, f, mu, kind, a, b, coef)
            k2x = v + .5 * h * k1v
            k2v = _acc(x + .5 * h * k1x, v + .5 * h * k1v, t + .5 * h, f, mu, kind, a, b, coef)
            k3x = v + .5 * h * k2v
            k3v = _acc(x + .5 * h * k2x, v + .5 * h * k2v, t + .5 * h, f, mu, kind, a, b, coef)
            k4x = v + h * k3v
            k4v = _acc(x + h * k3x, v + h * k3v, t + h, f, mu, kind, a, b, coef)
            x = x + h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v = v + h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            step += 1
        xs.append(x)
        vs.append(v)
    return torch.stack(xs, dim=1), torch.stack(vs, dim=1)


# CPU path used for dreams: the judge's own compiled simulator (paths.simulate_program), run over many throws in
# parallel. Same function, so the readings are bit-identical to what the judge computes. (Measured 2026-09-24: the
# torch loop above launches ~10^5 small GPU kernels per batch and reaches only ~2,400 throws/s on the GTX 1650 Ti,
# so the GPU is kept for the network.)
import numpy as np
from numba import njit, prange


@njit(parallel=True, cache=True)
def _many(t0s, t1s, forces, nseg, mu, kind, a, b, coef, nterm, bump_t0, bump_amp, out_x, out_v):
    for i in prange(mu.shape[0]):
        xs, vs = paths.simulate_program(t0s[i, :nseg[i]], t1s[i, :nseg[i]], forces[i, :nseg[i]], mu[i],
                                        kind[i, :nterm[i]], a[i, :nterm[i]], b[i, :nterm[i]], coef[i, :nterm[i]],
                                        1.0, 1.0, bump_t0[i], bump_amp[i])
        out_x[i, :] = xs
        out_v[i, :] = vs


def simulate_many(t0s, t1s, forces, nseg, mu, kind, a, b, coef, nterm, bump_t0, bump_amp):
    """Noise-free readings (B, N_OBS) x2 for B throws given as padded numpy arrays (float64 / int64)."""
    B = mu.shape[0]
    out_x = np.zeros((B, N_OBS))
    out_v = np.zeros((B, N_OBS))
    _many(t0s, t1s, forces, nseg, mu, kind, a, b, coef, nterm, bump_t0, bump_amp, out_x, out_v)
    return out_x, out_v
