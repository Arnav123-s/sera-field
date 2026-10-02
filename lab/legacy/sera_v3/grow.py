"""Growth (B4, truth-v2): when no law SERA can say fits, find where the gap lives, attach a new piece there, and let
the judge decide (docs/B4_GROWTH.md).

1. Notice: the judge's alarm on the best law, or no certificate after the experiments.
2. Localize: the leftover force per reading interval, r = y / mu_hat - fbar - F_leader(x, v, t), is fitted by
   piecewise-linear curves (the fixed 9-knot grids) in x, in v and in t, and by x * g(v) and g(x) * v. The address
   whose fit explains the most of r is where the gap lives ("it depends on the speed").
3. Attach and name:
   - a cell (a free curve) at that address, at the resolutions 9 and 17 (fixed grids, priced by the prior);
   - the grown pieces and piece products whose shape best matches r (least squares on r; cheap), the top NAMES of
     them. The prior on every grown term is fixed before data (Kraft), so choosing candidates by matching is
     covered by the union bound (B4-3).
4. Two-stage judgement: the judge weighs the base laws plus the grown formula candidates (no cells) over every stored
   throw; if no formula can be certified, it weighs the base laws plus the cells (a free curve as a rival would block
   every formula forever). A certified formula is a new named piece; a certified cell is a new concept that is not
   yet a formula. Both stages are sound by the same argument as truth-v1's invented terms in play: the claim beats
   every family in its space by a valid e-value, and anything else is bounded by the band and the adequacy test.
"""
import math

import numpy as np

from ccops5.core import grammar, paths, truth
from . import compact as C

NAMES = 6


def leftover(ledger, leader):
    """(r, x, v, t) per reading interval: the force the leader's best fit leaves unexplained, per unit of push."""
    fit = ledger.mle(leader)
    model = ledger._models[leader]
    obj, y, fb, xb, vb, tb = C.intervals(ledger.throws)
    mu = np.array([fit.mu.get(int(o), 1.0) for o in obj])
    F = np.zeros_like(y)
    for c, (k, a, b) in zip(model.codes_coef(fit.coef), zip(model.kind, model.a, model.b)):
        F += c * np.array([paths.term_t(k, a, b, x, v, t, 1.0, 1.0) for x, v, t in zip(xb, vb, tb)])
    return y / np.maximum(mu, 1e-6) - fb - F, xb, vb, tb


def _hat_columns(s, inp):
    lo, hi = paths.CELL_LO[inp], paths.CELL_HI[inp]
    return np.stack([[paths._hat(inp, k, si) for si in s] for k in range(9)], axis=1)


def localize(r, x, v, t):
    """Explained share of the leftover per address: 'position', 'speed', 'time', 'x*g(v)', 'g(x)*v'."""
    total = float(r @ r) + 1e-300
    out = {}
    for name, cols in (('position', _hat_columns(x, 0)), ('speed', _hat_columns(v, 1)), ('time', _hat_columns(t, 2)),
                       ('x*g(v)', x[:, None] * _hat_columns(v, 1)), ('g(x)*v', _hat_columns(x, 0) * v[:, None])):
        c, *_ = np.linalg.lstsq(cols, r, rcond=None)
        out[name] = 1.0 - float(np.sum((r - cols @ c) ** 2)) / total
    return out


def candidates(r, x, v, t, address):
    """Grown terms to try: the cells at the address (9, 17 knots) and the NAMES grown pieces or products whose single
    column explains most of r."""
    terms = []
    if address in ('position', 'speed', 'time'):
        terms += [('cell', address, 9), ('cell', address, 17)]
    scored = []
    for term in grammar.GROWN_TERMS:
        if term[0] == 'cell':
            continue
        k, a, b = grammar.code(term)
        col = np.array([paths.term_t(k, a, b, xi, vi, ti, 1.0, 1.0) for xi, vi, ti in zip(x, v, t)])
        d = float(col @ col)
        if d <= 1e-12:
            continue
        scored.append((float(col @ r) ** 2 / d, term))
    scored.sort(key=lambda s: -s[0])
    return terms + [term for _, term in scored[:NAMES]]


def _replay(terms, throws, sigma):
    led = truth.Ledger(grammar.space(inventions=terms), sigma)
    for th in throws:
        led.add(th)
    return led


def rival_formulas(address):
    """independent review condition 1: every grown formula on the implicated input(s), not only the matched ones (matched
    candidates alone are data-selected local rivals: the inventor's failure, (review notes, not published))."""
    pieces = lambda inp: [g for g in grammar.GROWN_TERMS if g[0] == 'piece' and g[1] == inp]
    if address in ('position', 'speed', 'time'):
        return pieces(address)
    non_shape = [n for n in grammar.PART_NAMES if n not in grammar.SHAPES]
    if address == 'x*g(v)':
        prods = [('pprod', 'straight', n) for n in non_shape]
    else:
        prods = [('pprod', n, 'straight') for n in non_shape]
    return pieces('position') + pieces('speed') + prods


def plan(ledger, leader, extra_terms=()):
    """Where the gap lives and what to weigh, for SERA's mind: (formula terms, cell terms, report).

    The formula terms are the invented terms already in play plus the matched grown candidates. Revision 4's condition
    1 (every grown formula on the implicated inputs as a rival) is now enforced by the judge itself: truth.wide_rivals
    (T2) makes a grown claim rule out every law of one grown or open term sharing a part with it, so the ledger need
    not carry them all. When one of them is not ruled out, the mind adds it to its ledger and separates the two by
    experiment (sera.mind)."""
    r, x, v, t = leftover(ledger, leader)
    where = localize(r, x, v, t)
    address = max(where, key=where.get)
    grown = candidates(r, x, v, t, address)
    formulas = tuple(sorted(set(extra_terms) | {g for g in grown if g[0] != 'cell'}, key=grammar._key))
    cells = tuple(g for g in grown if g[0] == 'cell')
    return formulas, cells, dict(address=address, explained={k: round(v_, 3) for k, v_ in where.items()},
                                 candidates=[grammar.term_name(g) for g in grown])


def grow(ledger, leader, sigma, extra_terms=()):
    """Two ledgers, each replayed over every stored throw (the two-stage judgement):
      formulas: the base laws, the invented terms already in play and the grown formula candidates (no cells: a free
                curve as a rival would block every formula forever);
      curves:   the base laws and the cells at the gap's address (the weaker claim "a free curve in s").
    Returns (formula ledger, curve ledger or None, report)."""
    r, x, v, t = leftover(ledger, leader)
    where = localize(r, x, v, t)
    address = max(where, key=where.get)
    grown = candidates(r, x, v, t, address)
    formulas = tuple(sorted(set(extra_terms) | {g for g in grown if g[0] != 'cell'} | set(rival_formulas(address)),
                            key=grammar._key))
    cells = tuple(g for g in grown if g[0] == 'cell')
    return (_replay(formulas, ledger.throws, sigma), _replay(cells, ledger.throws, sigma) if cells else None,
            dict(address=address, explained={k: round(v_, 3) for k, v_ in where.items()},
                 candidates=[grammar.term_name(g) for g in grown]))
