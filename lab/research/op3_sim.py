"""OP3 side experiment: does "grow a hidden number per object" ever fire on noise, and how fast does it fire
when the objects really differ? The mind checks after every sample and grows at its first "yes".

A toy 1-D drag world. K objects; each sample is one reading from a randomly chosen object:
    a = -theta_obj * v + Gaussian noise (sigma known), speeds v in [0.2, 1.0]
Current family C: one shared number (theta the same for every object).
Grown family G:   one number per object (a hidden quantity, like mass).
Truths:
    same   all objects share theta = 1           (growing would be growth on noise)
    faint  theta = 0.95, 1.00, 1.05, 1.10        (a small real difference)
    clear  theta = 0.8, 1.0, 1.2, 1.5            (a clear real difference)
Rules (may stop at any sample, up to N_MAX):
    in-sample  (RSS_C - RSS_G) / sigma^2 >= 9, both fitted on all samples so far (the lab's DECISIVE form)
    e-process  log E = log q_G(prequential) - max log L_C(all) >= log(1/alpha), alpha = 1e-3
               q_G predicts each reading from earlier readings only: the object's own estimate, shrunk toward
               the pooled estimate (KAPPA pseudo-readings), so it is a proper predictive distribution.

    python research/op3_sim.py
"""
import sys

import numpy as np

sys.dont_write_bytecode = True
K, N_MAX, SIGMA = 4, 400, 0.05
DECISIVE, ALPHA, KAPPA = 9.0, 1e-3, 1.0
V_LO, V_HI = 0.2, 1.0
TRUTHS = {'same': (1.0, 1.0, 1.0, 1.0), 'faint': (0.95, 1.0, 1.05, 1.10), 'clear': (0.8, 1.0, 1.2, 1.5)}


def run(truth, lives, rng):
    v = rng.uniform(V_LO, V_HI, size=(lives, N_MAX))
    obj = rng.integers(K, size=(lives, N_MAX))
    theta = np.asarray(TRUTHS[truth])[obj]
    a = -theta * v + SIGMA * rng.standard_normal(v.shape)
    f, s2 = -v, SIGMA ** 2                               # a = theta * f + noise, with f = -v

    def cum_prev(x):                                     # sums over samples strictly before each one
        c = np.cumsum(x, axis=1)
        return c, np.concatenate([np.zeros((x.shape[0], 1)), c[:, :-1]], axis=1)

    cyy, _ = cum_prev(a * a)
    cff, cff_p = cum_prev(f * f)
    cfy, cfy_p = cum_prev(f * a)
    rss_c = cyy - cfy ** 2 / cff                         # best shared number, fitted on all samples so far
    pooled_p = np.where(cff_p > 0, cfy_p / np.maximum(cff_p, 1e-12), 0.0)
    rss_g = np.zeros_like(a)
    pred = np.zeros_like(a)
    for k in range(K):
        m = (obj == k)
        ky, _ = cum_prev(np.where(m, a * a, 0.0))
        kff, kff_p = cum_prev(np.where(m, f * f, 0.0))
        kfy, kfy_p = cum_prev(np.where(m, f * a, 0.0))
        rss_g += np.where(kff > 0, ky - kfy ** 2 / np.maximum(kff, 1e-12), 0.0)
        shrunk = (kfy_p + KAPPA * pooled_p) / (kff_p + KAPPA)   # uses only earlier readings
        pred = np.where(m, shrunk * f, pred)
    preq_g = np.cumsum((a - pred) ** 2, axis=1)
    rules = {'in-sample': (rss_c - rss_g) / s2 >= DECISIVE,
             'e-process': (rss_c - preq_g) / (2 * s2) >= np.log(1 / ALPHA)}
    out = {}
    for name, grow in rules.items():
        grow[:, :K] = False                              # not before each object could have been seen
        out[name] = (grow.any(axis=1), grow.argmax(axis=1) + 1)
    return out


def main():
    rng = np.random.default_rng([2026, 9, 22, 3])
    print(f'{K} objects, up to {N_MAX} readings, sigma={SIGMA}, speeds {V_LO}-{V_HI}; grow at the first "yes"')
    print(f'{"truth":<8}{"rule":<12}{"grew":>10}{"median readings":>18}{"lives":>8}')
    for truth, lives in (('same', 20000), ('faint', 5000), ('clear', 5000)):
        parts = [run(truth, 2500, rng) for _ in range(lives // 2500)]   # chunks keep memory small
        for rule in parts[0]:
            grew = np.concatenate([p[rule][0] for p in parts])
            first = np.concatenate([p[rule][1] for p in parts])
            med = float(np.median(first[grew])) if grew.any() else float('nan')
            print(f'{truth:<8}{rule:<12}{grew.mean():>10.4f}{med:>18.0f}{lives:>8}')
    print('"same": the objects do not differ, so every growth is growth on noise.')


if __name__ == '__main__':
    main()
