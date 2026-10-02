"""Suggest force terms that explain acceleration left over by the leading family."""

import math

import numpy as np

from . import grammar, gut, paths


P_GRID = tuple(round(0.1 * k, 1) for k in range(1, 41))
W_GRID = tuple(round(0.1 * k, 1) for k in range(1, 81))


def open_terms():
    products = tuple(('product', a, b) for a in grammar.SHAPES for b in grammar.SHAPES)
    powers = tuple(('power', inp, p) for inp in ('position', 'speed') for p in P_GRID
                   if p not in (1.0, 2.0, 3.0))
    drives = tuple(('drive', f, w) for f in ('sin', 'cos') for w in W_GRID)
    return products + powers + drives


def term_value(term, x, v, t):
    """Evaluate one grammar term at matching arrays of readings."""
    kind, a, b = grammar.code(term)
    return np.array([paths.term_t(kind, a, b, xi, vi, ti, 1.0, 1.0)
                     for xi, vi, ti in zip(x, v, t)], dtype=float)


def _readings(throws):
    """Acceleration readings, their times, and their situation identifiers."""
    x, v, f, a = gut.accelerations(throws)
    times = np.concatenate([np.arange(1, throw.x.size - 1) * paths.DT_OBS for throw in throws])
    situations = np.concatenate([np.full(throw.x.size - 2, throw.situation) for throw in throws])
    return x, v, times, f, a, situations


def _ranked(throws, leader):
    x, v, t, f, a, situations = _readings(throws)
    columns = [f * (situations == situation) for situation in sorted(set(situations))]
    columns.extend(term_value(idea, x, v, t) for idea in leader)
    base = np.column_stack(columns)
    coef, *_ = np.linalg.lstsq(base, a, rcond=None)
    residual = a - base @ coef
    rss = float(residual @ residual)
    ranked = []
    for order, term in enumerate(open_terms()):
        value = term_value(term, x, v, t)
        if not np.all(np.isfinite(value)) or not np.any(value):
            continue
        # Removing the base columns first is equivalent to adding this column
        # to the original least-squares regression.
        projection, *_ = np.linalg.lstsq(base, value, rcond=None)
        independent = value - base @ projection
        norm = float(independent @ independent)
        if norm <= 1e-24 or rss <= 0.0:
            gain = 0.0
        else:
            explained = float(residual @ independent) ** 2 / norm
            remaining = max(rss - explained, 1e-12)
            gain = max(0.0, math.log(rss / remaining))
        ranked.append((gain, order, term))
    return sorted(ranked, key=lambda item: (-item[0], item[1]))


def _group(term):
    """Near-duplicates share a group: one exponent per input, one frequency per sin/cos; each product is its own."""
    return term if term[0] == 'product' else (term[0], term[1])


def propose(throws, leader, top=8):
    """The open terms with the largest gain over the leader's residual, at most one per group (development note, 2026-09-24:
    without this the list filled with neighbouring grid points, e.g. |v|^0.5, 0.6, 0.7, and pushed out x*v)."""
    out, seen = [], set()
    for gain, _, term in _ranked(throws, leader):
        if _group(term) in seen:
            continue
        seen.add(_group(term))
        out.append({'term': term, 'gain': float(gain), 'name': grammar.term_name(term)})
        if len(out) == top:
            break
    return out


def shape_summary(throws, leader):
    """Describe the input and periodicity suggested by the remaining acceleration."""
    ranked = _ranked(throws, leader)
    best = {'position': float('-inf'), 'speed': float('-inf'), 'time': float('-inf')}
    best_drive = None
    best_non_drive = float('-inf')
    for gain, _, term in ranked:
        if term[0] == 'drive':
            best['time'] = max(best['time'], gain)
            if best_drive is None:
                best_drive = (gain, term[2])
        else:
            best_non_drive = max(best_non_drive, gain)
            # A product uses both inputs, so it contributes to both summaries.
            inputs = ('position', 'speed') if term[0] == 'product' else (term[1],)
            for inp in inputs:
                best[inp] = max(best[inp], gain)
    along = max(('position', 'speed', 'time'), key=lambda inp: best[inp])
    return {'along': along,
            'periodic': best_drive is not None and best_drive[0] > best_non_drive + 1.0,
            'best_frequency': None if best_drive is None else float(best_drive[1])}
