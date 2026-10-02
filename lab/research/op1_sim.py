"""OP1 side experiment: how often does each evidence rule end up "sure and wrong"
when the mind checks after every sample and stops as soon as it feels sure?

A toy 1-D drag world, samples (v, a) with a = law(v) + Gaussian noise (sigma known).
Two rival ideas with one free number each:
    A: a = -theta * v        (linear drag)
    B: a = -theta * v**2     (quadratic drag)
Rules compared (all may stop at any sample, up to N_MAX):
  in-sample  : (RSS_B - RSS_A)/sigma^2 >= 9, both fitted on all samples so far
               (the form of ccops5 relentless.evidence; 9 = its DECISIVE)
  leave-1-out: sum over samples of clipped (loo_B - loo_A)/sigma^2 >= 9
               (the form of ccops5 ballmind.retrial, clip +-6 per sample)
  e-process  : log E = sum log q_A(prequential) - max log L_B(all) >= log(1/alpha),
               alpha = 1e-3 (universal inference, sequential form)
Truths: A true, B true, and M = neither (a = -theta * v**1.5, outside both ideas).
Sure-and-wrong = declaring "sure A" when A is not the truth (or "sure B" when B is not).

    python research/op1_sim.py
"""
import sys
import numpy as np

sys.dont_write_bytecode = True
N_LIVES, N_MAX, SIGMA, THETA = 20000, 200, 0.05, 1.0
DECISIVE, CLIP, ALPHA = 9.0, 6.0, 1e-3
V_LO, V_HI = 0.2, 1.0          # slow throws: linear and quadratic drag look alike


def features(v):
    return {'A': v, 'B': v ** 2}


def run(truth, rng):
    v = rng.uniform(V_LO, V_HI, size=(N_LIVES, N_MAX))
    law = {'A': v, 'B': v ** 2, 'M': v ** 1.5}[truth]
    a = -THETA * law + SIGMA * rng.standard_normal(v.shape)
    phi = features(v)
    s2 = SIGMA ** 2
    cyy = np.cumsum(a * a, axis=1)
    out = {}
    fits = {}
    for k, f in phi.items():
        cff = np.cumsum(f * f, axis=1)
        cfy = np.cumsum(f * a, axis=1)
        rss = cyy - cfy ** 2 / cff                     # in-sample RSS after t samples
        theta_prev = np.zeros_like(cfy)                # prequential plug-in (0 before any data)
        theta_prev[:, 1:] = cfy[:, :-1] / cff[:, :-1]
        preq_sq = np.cumsum((a - theta_prev * f) ** 2, axis=1)
        fits[k] = (cff, cfy, rss, preq_sq)
    t = np.arange(1, N_MAX + 1)
    # in-sample evidence for A over B (positive favours A), and for B over A
    ins = (fits['B'][2] - fits['A'][2]) / s2
    # leave-one-out, recomputed on the samples seen so far (closed form for one-number laws)
    loo = np.zeros((N_LIVES, N_MAX))
    for n in range(2, N_MAX + 1):
        r = {}
        for k, f in phi.items():
            cff, cfy = fits[k][0][:, n - 1:n], fits[k][1][:, n - 1:n]
            th = cfy / cff
            h = f[:, :n] ** 2 / cff
            r[k] = ((a[:, :n] - th * f[:, :n]) / (1 - h)) ** 2 / s2
        loo[:, n - 1] = np.clip(r['B'] - r['A'], -CLIP, CLIP).sum(axis=1)
    # e-process for A against the B family, and for B against the A family
    logE_A = (fits['B'][2] - fits['A'][3]) / (2 * s2)   # max-likelihood B over all vs prequential A
    logE_B = (fits['A'][2] - fits['B'][3]) / (2 * s2)
    thr = np.log(1 / ALPHA)
    for name, (sA, sB) in {'in-sample': (ins >= DECISIVE, ins <= -DECISIVE),
                           'leave-1-out': (loo >= DECISIVE, loo <= -DECISIVE),
                           'e-process': (logE_A >= thr, logE_B >= thr)}.items():
        sA[:, 0] = sB[:, 0] = False                    # never sure on one sample
        firstA = np.where(sA.any(axis=1), sA.argmax(axis=1), N_MAX + 1)
        firstB = np.where(sB.any(axis=1), sB.argmax(axis=1), N_MAX + 1)
        sure_A = firstA < firstB
        sure_B = firstB < firstA
        wrong = (sure_A & (truth != 'A')) | (sure_B & (truth != 'B'))
        right = (sure_A & (truth == 'A')) | (sure_B & (truth == 'B'))
        n_sure = np.minimum(firstA, firstB)[sure_A | sure_B] + 1
        out[name] = (wrong.mean(), right.mean(), float(np.median(n_sure)) if n_sure.size else float('nan'))
    return out


def certificate_run(truth, rng, lives=2000, n_max=1000, every=20, eps=0.05, delta=1e-3, lam=1e-4, s_bound=2.0):
    """Full certificate: part 1 (e-process against the rival family) AND part 3 (the truth stays within eps
    of the claimed law over the tested speeds). Part 3 uses a flexible family F = {v, v^2, v^3} with the
    self-normalized, time-uniform confidence set of Abbasi-Yadkori, Pal & Szepesvari (valid if the truth
    lies in F up to a negligible remainder); it is checked every `every` samples."""
    v = rng.uniform(V_LO, V_HI, size=(lives, n_max))
    law = {'A': v, 'B': v ** 2, 'M': v ** 1.5}[truth]
    a = -THETA * law + SIGMA * rng.standard_normal(v.shape)
    s2 = SIGMA ** 2
    phi = np.stack([v, v ** 2, v ** 3], axis=2)                       # (lives, n, 3)
    grid = np.linspace(V_LO, V_HI, 17)
    pg = np.stack([grid, grid ** 2, grid ** 3], axis=1)               # (17, 3)
    single = {'A': v, 'B': v ** 2}
    cyy = np.cumsum(a * a, axis=1)
    fit = {}
    for k, f in single.items():
        cff, cfy = np.cumsum(f * f, axis=1), np.cumsum(f * a, axis=1)
        prev = np.zeros_like(cfy)
        prev[:, 1:] = cfy[:, :-1] / cff[:, :-1]
        fit[k] = (cff, cfy, cyy - cfy ** 2 / cff, np.cumsum((a - prev * f) ** 2, axis=1))
    logE = {'A': (fit['B'][2] - fit['A'][3]) / (2 * s2), 'B': (fit['A'][2] - fit['B'][3]) / (2 * s2)}
    first = {'A': np.full(lives, n_max + 1), 'B': np.full(lives, n_max + 1)}
    V = np.broadcast_to(lam * np.eye(3), (lives, 3, 3)).copy()
    b = np.zeros((lives, 3))
    for t in range(every, n_max + 1, every):
        P, y = phi[:, t - every:t], a[:, t - every:t]              # add this chunk to the running sums
        V += np.einsum('lni,lnj->lij', P, P)
        b += np.einsum('lni,ln->li', P, y)
        th = np.linalg.solve(V, b[..., None])[..., 0]
        _, logdet = np.linalg.slogdet(V)
        beta = SIGMA * np.sqrt(2 * np.log(1 / delta) + logdet - 3 * np.log(lam)) + np.sqrt(lam) * s_bound
        Vinv = np.linalg.inv(V)
        half = beta[:, None] * np.sqrt(np.einsum('gi,lij,gj->lg', pg, Vinv, pg))   # band half-width on the grid
        centre = np.einsum('gi,li->lg', pg, th)
        for k, basis in (('A', grid), ('B', grid ** 2)):
            coef = fit[k][1][:, t - 1] / fit[k][0][:, t - 1]              # best one-number law of this idea
            adequate = (np.abs(centre - coef[:, None] * basis[None, :]) + half <= eps).all(axis=1)
            ok = adequate & (logE[k][:, t - 1] >= np.log(1 / ALPHA))
            newly = ok & (first[k] > n_max)
            first[k][newly] = t
    sure_A, sure_B = first['A'] < first['B'], first['B'] < first['A']
    wrong = (sure_A & (truth != 'A')) | (sure_B & (truth != 'B'))
    right = (sure_A & (truth == 'A')) | (sure_B & (truth == 'B'))
    n_sure = np.minimum(first['A'], first['B'])[sure_A | sure_B]
    return wrong.mean(), right.mean(), (float(np.median(n_sure)) if n_sure.size else float('nan')), lives, n_max


def main():
    rng = np.random.default_rng([2026, 9, 22])
    print(f'{N_LIVES} lives per truth, up to {N_MAX} samples, sigma={SIGMA}, speeds {V_LO}-{V_HI}; '
          f'stop at the first "sure"')
    print(f'{"truth":<8}{"rule":<13}{"sure & WRONG":>14}{"sure & right":>14}{"median samples":>16}')
    for truth in ('A', 'B', 'M'):
        res = run(truth, rng)
        for rule, (w, r, n) in res.items():
            print(f'{truth:<8}{rule:<13}{w:>14.4f}{r:>14.4f}{n:>16.0f}')
    print('M = the true law (v**1.5) is outside both ideas: any "sure" there is wrong.')
    print()
    for eps, n_max in ((0.10, 1000), (0.05, 4000)):
        print(f'Full certificate = e-process (part 1) + "something else" band within eps={eps} (part 3), '
              f'checked every 20 samples, up to {n_max}')
        for truth in ('A', 'B', 'M'):
            w, r, n, lives, _ = certificate_run(truth, rng, n_max=n_max, eps=eps)
            print(f'{truth:<8}{"certificate":<13}{w:>14.4f}{r:>14.4f}{n:>16.0f}   ({lives} lives)')


if __name__ == '__main__':
    main()
