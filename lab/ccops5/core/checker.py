"""The checker: re-derives a certificate from the stored throws and accepts it only if every number matches
and every rule holds. It imports no learner module and keeps no state between calls.

Rules it applies itself (not trusting the certificate's own verdict):
- the throws' digest matches; alpha and delta are no laxer than policy; the idea space is the full one;
- every rival family (not containing the claimed family) is listed with an e-value that matches the
  recomputed one and passes log(|S_K| / alpha);
- every nested term is listed, its interval matches, and it contains 0;
- the band matches the recomputed one and is <= eps; the scope matches the data.
"""
import copy
import math

import numpy as np

from . import grammar, truth

POLICY_ALPHA = 1e-3
POLICY_DELTA = 1e-3
TOL = 1e-6


def _close(a, b):
    if a is None or b is None:
        return a is None and b is None
    if math.isinf(a) or math.isinf(b):
        return a == b
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))


_C = (0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0)
_RANGE = {'position': (-3.0, 3.0), 'speed': (-6.0, 6.0), 'time': (0.0, 2.0)}


def _part_np(name, s):
    """A grown term's part, written here from its definition (docs/B4_GROWTH.md), not taken from the simulator."""
    shapes = {'straight': s, 'growing': s * np.abs(s), 'steps': np.tanh(s / 0.05), 'cubic': s ** 3, 'wave': np.sin(s)}
    if name in shapes:
        return shapes[name]
    if name == 'abs':
        return np.abs(s)
    if name.startswith('tanh'):
        return np.tanh(s / float(name[4:]))
    return np.exp(-s * s / float(name[4:]))


def _dim_np(body, x, v, t):
    """Decision 15, evaluated here (not grammar.dim_eval, not paths._dim): a dimension's postfix program."""
    st = []
    for tok in body.split('.'):
        if tok in ('x', 'v', 't'):
            st.append(np.asarray({'x': x, 'v': v, 't': t}[tok], float) + 0.0 * x)
        elif tok in ('0', '1'):
            st.append(np.full(np.shape(x), float(tok)))
        elif tok == 'if':
            b, a, c = st.pop(), st.pop(), st.pop()
            st.append(np.where(c > 0.5, a, b))
        else:
            q, p = st.pop(), st.pop()
            st.append({'add': p + q, 'sub': p - q, 'mul': p * q, 'lt': np.where(p < q, 1.0, 0.0)}[tok])
    assert len(st) == 1
    return st[0]


def _window_np(inp):
    """Decision 14, parsed here from the name (not grammar.lens): (the measured input, lo, hi) of an input or of a lens
    '<input>@<j>:<m>' (2^j times closer, the window of width W / 2^j centred at lo + m W / 2^(j+1)); Decision 15: of a
    dimension 'dim:<program>@<r>' (its program, -R .. R with R = 2^(r - 4))."""
    if inp.startswith('dim:'):
        body, r = inp[4:].split('@')
        R = 2.0 ** (int(r) - 4)
        return ('dim', body), -R, R
    if '@' not in inp:
        lo, hi = _RANGE[inp]
        return inp, lo, hi
    base, rest = inp.split('@')
    j, m = (int(p) for p in rest.split(':'))
    lo, hi = _RANGE[base]
    half = (hi - lo) / 2 ** (j + 1)
    c = lo + m * half
    return base, c - half, c + half


def _grown_np(term, x, v, t):
    """Every model column of a grown term, evaluated independently of paths.term_t (independent review review V1)."""
    s = {'position': x, 'speed': v, 'time': t}
    if term[0] == 'hats':                           # Decision 13: a band's check, the grid's hats it keeps
        hats = _grown_np(('cell', term[1], term[2]), x, v, t)
        return [hats[k] for k in range(term[2]) if k not in set(term[3])]
    if term[0] == 'shape':                          # Decision 12: its knots times the cell's hats, one column
        hats = _grown_np(('cell', term[1], term[2]), x, v, t)
        return [sum(w * h for w, h in zip(term[4], hats))]
    if term[0] == 'ramp':                           # Decision 16: its dimension's value, clipped at the range
        inp, lo, hi = _window_np(term[1])
        with np.errstate(all='ignore'):
            z = _dim_np(inp[1], x, v, t)
        return [np.where(np.isfinite(z), np.clip(z, lo, hi), np.nan)]   # infinity is no value (S14 F2)
    if term[0] == 'cell':
        inp, lo, hi = _window_np(term[1])                 # Decision 14: or a lens's window on its input
        K = term[2]
        h = (hi - lo) / (K - 1)
        z = _dim_np(inp[1], x, v, t) if isinstance(inp, tuple) else s[inp]      # Decision 15: or its dimension
        cols = []
        for k in range(K):
            c = lo + k * h
            col = np.maximum(0.0, 1.0 - np.abs(z - c) / h)
            if k == 0:
                col = np.where(z <= c, 1.0, col)
            if k == K - 1:
                col = np.where(z >= c, 1.0, col)
            cols.append(col)
        return cols
    if term[0] == 'piece':
        z = s[term[1]]
        name = 'abs' if term[2] == 'abs' else f'{term[2]}{term[3]:g}'
        return [_part_np(name, z)]
    return [_part_np(term[1], x) * _part_np(term[2], v)]


def _grown_terms_agree(inventions, scope):
    """The judge's simulator and this independent formula give the same values for every grown term in play, on a
    grid over the scope (and beyond it, where cells are constant)."""
    from . import paths
    xs = np.linspace(scope['x'][0] - 1.0, scope['x'][1] + 1.0, 13)
    vs = np.linspace(scope['v'][0] - 1.0, scope['v'][1] + 1.0, 13)
    X, V = np.meshgrid(xs, vs)
    X, V = X.ravel(), V.ravel()
    T = np.linspace(0.0, 2.0, X.size)
    for term in inventions:
        if term[0] not in ('cell', 'piece', 'pprod', 'shape', 'ramp'):
            continue
        mine = _grown_np(term, X, V, T)
        theirs = [np.array([paths.term_t(k, a, b, x, v, tt, 1.0, 1.0) for x, v, tt in zip(X, V, T)])
                  for k, a, b in grammar.term_codes(term)]
        if term[0] == 'ramp' and not all(np.all(np.isfinite(m)) for m in mine + theirs):
            return False                            # Decision 16: a ramp's values are finite on both sides (S14 F2)
        if term[0] == 'shape':                      # Decision 12: the simulator's hats, tied by the knots
            theirs = [sum(w * h for w, h in zip(term[4], theirs))]
        if len(mine) != len(theirs) or any(np.max(np.abs(m - th)) > 1e-12 for m, th in zip(mine, theirs)):
            return False
    return True


def _ramp_outside_np(family, throws):
    """Decision 16, independently of truth.ramp_outside: whether any ramp's expression is not finite or leaves its
    range at any reading of any throw (its program and range parsed here from the name)."""
    from . import paths
    ramps = [t for t in family if t[0] == 'ramp']
    if not ramps:
        return False
    x = np.concatenate([np.asarray(t.x, float) for t in throws])
    v = np.concatenate([np.asarray(t.v, float) for t in throws])
    tt = np.concatenate([np.arange(len(t.x)) * paths.DT_OBS for t in throws])
    for term in ramps:
        inp, lo, hi = _window_np(term[1])
        with np.errstate(all='ignore'):
            z = _dim_np(inp[1], x, v, tt)
        if not (np.all(np.isfinite(z)) and np.all(z >= lo) and np.all(z <= hi)):
            return True
    return False


def _column_np(term, x, v, t):
    """Every column of any term, from its definition (not paths.term_t)."""
    if term[0] in ('cell', 'piece', 'pprod', 'shape', 'hats', 'ramp'):
        return _grown_np(term, x, v, t)
    if term == ('nothing', 'steady'):
        return [np.ones_like(x)]
    if term[0] in ('position', 'speed'):
        return [_part_np(term[1], x if term[0] == 'position' else v)]
    if term[0] == 'product':
        return [_part_np(term[1], x) * _part_np(term[2], v)]
    if term[0] == 'power':
        s = x if term[1] == 'position' else v
        return [np.sign(s) * np.abs(s) ** term[2]]
    return [np.sin(term[2] * t) if term[1] == 'sin' else np.cos(term[2] * t)]


FD_RCOND = 1e-9                # Decision 13: directions below the finite differences' own precision are not seen
FD_AGREE = 1e-5                # the finite differences and the exact Jacobian agree column by column, at one of
FD_STEPS = (1e-6, 1e-7, 1e-8, 1e-5)   # these relative steps (2026-09-28: at step 1e-6 alone, paths that dwell on a
                               # kink - carts stopped by a rub sit at speed 0, a knot - broke 1e-6 by up to 52% on a
                               # whole-input curve; at 1e-8 they agreed to 2.3e-7 .. 3.7e-6, lenses included, but
                               # round-off broke rarely-reached columns with 80 throws: colab-upload/diag_lens3-4.py)
EXACT_NULL = 1e-12             # the exact Jacobian's own zero (machine precision on these sizes)
NULL_EXACT = 1e-12             # the band's share there must be nil (reviewer VD13 fix 5: strict)
FD_NULL = 1e-9                 # and a band with more than this share of its content there is unbounded (fail closed)


def _band_independent(cert, throws, sigma, n_space=None, checks=None, delta_eff=None, fd_svd=False):
    """independent review T1-b: the grown band re-derived by other numerics. The flexible fit is the band's definition, but:
    - sensitivities come from central finite differences of the simulated paths (not the exact one-pass Jacobian);
    - the claim's span is removed by QR (not an SVD);
    - variances are minimum-norm solutions of J' z = a (not the SVD of J);
    - every column is evaluated from its definition here (not paths.term_t).
    Returns the band, or inf where a value lies outside what the data can see."""
    from numpy.polynomial import legendre as LG
    from . import likelihood as L, paths
    fam = grammar.canonical(cert.family)
    scope = truth.scope_of(throws)
    base = truth.model_of(fam, extra_basis=True, scope=scope)
    cells = truth.curve_checks(fam) if checks is None else checks        # Decision 13 passes its own
    extra = [c for cell in cells for c in grammar.term_codes(cell)]
    model = base.extended([c[0] for c in extra], [c[1] for c in extra], [c[2] for c in extra])
    q_f, post_f = truth.prequential_exact(model, throws, sigma, truth._band_numerator())
    fit = truth.flexible_fit(model, throws, sigma, fam, post_f)          # the band's definition: the best of two starts
    n = n_space if n_space is not None else len(grammar.space(inventions=cert.inventions))
    q_ref = q_f                                                           # Decision 8: the claim's own forecast,
    cm = truth.model_of(fam)                                              # re-derived here from the throws
    q_c, post_c = truth.prequential_exact(cm, throws, sigma)
    if truth.BAND == 'claim':
        q_ref = q_c
    fc = L.fit(cm, throws, sigma, start=post_c, iters=40)                 # reviewer VD14 fix 1: the flexible fit never
    if fc.ok and fit.ok and fit.loglik < fc.loglik - 1e-6 * max(1.0, abs(fc.loglik)):   # below the claim it holds
        return math.inf
    radius2 = 2.0 * (fit.loglik - q_ref + (math.log(n / POLICY_DELTA) if delta_eff is None     # B (ebecb4c review):
                                            else math.log(1.0 / delta_eff)))                 # the checker's own policy
    if not fit.ok or radius2 < 0:
        return math.inf
    nc, K = model.n_coef, len(fit.order)
    col = {s: nc + i for i, s in enumerate(fit.order)}
    scale = np.concatenate([np.full(paths.N_OBS, 1 / sigma[0]), np.full(paths.N_OBS, 1 / sigma[1])])

    def fd_jacobian(step, only=None):
        """The whitened Jacobian by central finite differences at this relative step (the columns in `only`, or all)."""
        rows = []
        for th in throws:
            arrays = L.knocked(th, (fit.knocks or {}).get(th.situation, 0)).action.arrays()   # M-1: as the fit saw it
            theta = np.concatenate([fit.coef, [fit.mu[th.situation]]])

            def path(v_):
                xs, vs = paths.simulate_program(*arrays, v_[-1], model.kind, model.a, model.b,
                                                model.codes_coef(v_[:-1]), model.sx, model.sv, 0.0, 0.0)
                return np.concatenate([xs, vs])

            y0 = path(theta)
            r = (np.concatenate([th.x, th.v]) - y0) * scale
            w = 1.0 / (1.0 + math.exp(min(L.log_outlier(th) - (-0.5 * float(r @ r) + L._log_norm(sigma)), 700.0)))
            J = np.zeros((y0.size, nc + K))
            for j in range(nc + 1):
                g = j if j < nc else col[th.situation]
                if only is not None and g not in only:
                    continue
                h = step * max(1.0, abs(theta[j]))
                up, dn = theta.copy(), theta.copy()
                up[j] += h
                dn[j] -= h
                J[:, g] = (path(up) - path(dn)) / (2 * h)
            rows.append(math.sqrt(w) * scale[:, None] * J)
        return np.vstack(rows)

    J = fd_jacobian(FD_STEPS[0])
    cellset = set(scope['cells'])
    pts = np.array([(float(th.x[n]), float(th.v[n]), n * paths.DT_OBS) for th in throws for n in range(paths.N_OBS)
                    if truth.cell_of(scope, float(th.x[n]), float(th.v[n])) in cellset])
    if not len(pts):
        return math.inf
    X, V, T = pts[:, 0], pts[:, 1], pts[:, 2]
    cols_claim = [c for term in fam for c in _column_np(term, X, V, T)]
    claim = np.stack(cols_claim, axis=1) if cols_claim else np.zeros((len(X), 0))     # the empty law: no columns
    basis = truth.basis_for(fam, scope)
    leg = [LG.legval(X / model.sx, [0] * dx + [1]) * LG.legval(V / model.sv, [0] * dv + [1]) for dx, dv in basis]
    hats = [c for cell in cells for c in _column_np(cell, X, V, T)]
    U = np.stack(leg + hats, axis=1)
    from scipy.linalg import qr as pivoted_qr               # Decision 13: pivoted, so a claim column no reading touches
    if claim.shape[1]:
        Q, R, _ = pivoted_qr(claim, mode='economic', pivoting=True)     # (a free curve's knot nothing reached) goes
        d = np.abs(np.diag(R))                              # last and is dropped whole; without pivoting its arbitrary
        Q = Q[:, :int(np.sum(d > 1e-12 * max(d.max(), 1e-300)))]   # direction took part of the claim's span with it
    else:
        Q = np.zeros((len(X), 0))
    G = U - Q @ (Q.T @ U)
    na = claim.shape[1]
    if fd_svd:
        # Decision 13. Which combinations of numbers no throw's path depends on at all (a free curve's knots nothing
        # reached; at the edge of where the throws went, one knot's effect along every path equal to a mix of its
        # neighbours') is read from the exact Jacobian, where they are 0 to machine precision; finite differences turn
        # such exact zeros into noise at their own precision (1e-9 here). The exact Jacobian is first checked against
        # the finite differences column by column (a fault there cannot hide anything), the band's content in those
        # combinations must be nil (else it fails closed), and the rest - the band itself - is re-derived from the
        # finite differences alone, restricted to what the paths depend on, cut at their precision.
        Jx = L.whitened_jacobian(model, fit, throws, sigma)
        if Jx.shape != J.shape:
            return math.inf
        cn = np.maximum(np.linalg.norm(Jx, axis=0), 1e-300)
        tol = FD_AGREE * cn + 1e-9 * cn.max()
        bad = np.flatnonzero(np.linalg.norm(J - Jx, axis=0) > tol)
        for step in FD_STEPS[1:]:               # 2026-09-28: a column may agree at another step (a kink breaks a large
            if not bad.size:                    # step, round-off a small one); a fault in the exact Jacobian breaks
                break                           # them all
            Jh = fd_jacobian(step, set(bad.tolist()))
            good = np.linalg.norm(Jh[:, bad] - Jx[:, bad], axis=0) <= tol[bad]
            J[:, bad[good]] = Jh[:, bad[good]]
            bad = bad[~good]
        if bad.size:
            return math.inf
        _, sx_, Vx = np.linalg.svd(Jx, full_matrices=False)
        B = Vx[sx_ > EXACT_NULL * sx_.max()].T                    # the combinations the paths depend on
        a = np.zeros((nc + K, len(pts)))
        a[na:nc, :] = G.T
        ab = B.T @ a
        size2 = np.sum(a * a, axis=0)
        if np.any(size2 - np.sum(ab * ab, axis=0) > NULL_EXACT * np.maximum(size2, 1e-300)):
            return math.inf
        _, sv, Ut = np.linalg.svd(J @ B, full_matrices=False)
        keep = sv > FD_RCOND * sv.max()
        proj = Ut[keep] @ ab
        if np.any(np.sum(ab * ab, axis=0) - np.sum(proj * proj, axis=0) > FD_NULL * np.maximum(size2, 1e-300)):
            return math.inf
        var = np.sum((proj / sv[keep][:, None]) ** 2, axis=0)
        return float(np.max(np.abs(G @ fit.coef[na:]) + np.sqrt(radius2 * var)))
    A = np.zeros((nc + K, len(pts)))
    A[na:nc, :] = G.T
    z = np.linalg.lstsq(J.T, A, rcond=None)[0]
    miss = np.linalg.norm(J.T @ z - A, axis=0)
    if np.any(miss > 1e-6 * np.maximum(np.linalg.norm(A, axis=0), 1e-12)):
        return math.inf
    var = np.sum(z * z, axis=0)
    return float(np.max(np.abs(G @ fit.coef[na:]) + np.sqrt(radius2 * var)))


BAND_AGREE = 0.05              # the independent band may exceed the certificate's by at most 5% (finite differences)


def band_reason(cert, throws, sigma, n_space=None):
    """independent review T1-b: a reason to refuse when the grown band, re-derived by other numerics, exceeds the certificate's
    (a fault shared by certify and its re-run would pass the plain match), else None."""
    own = _band_independent(cert, throws, sigma, n_space)
    if own <= cert.band * (1 + BAND_AGREE) + 1e-9:
        return None
    return f'the grown band does not re-derive independently ({own:.3g} against {cert.band:.3g})'


def lookalike_reason(cert, throws):
    """Decision 11: a reason to refuse when a rival the certificate records as a look-alike is not one, re-derived
    here by other numerics - its recorded best-fit force and the claim's, each evaluated from its definition
    (_column_np, not paths.term_t) at every reading in the visited cells, must differ by less than eps, and by the
    recorded gap - else None."""
    from . import paths
    looks = getattr(cert, 'lookalikes', None) or {}
    if not looks:
        return None
    scope = truth.scope_of(throws)
    cellset = set(scope['cells'])
    pts = np.array([(float(th.x[n]), float(th.v[n]), n * paths.DT_OBS) for th in throws for n in range(paths.N_OBS)
                    if truth.cell_of(scope, float(th.x[n]), float(th.v[n])) in cellset], float).reshape(-1, 3)
    if not len(pts):
        return 'a look-alike is recorded, but no reading lies in a visited cell'
    X, V, T = pts[:, 0], pts[:, 1], pts[:, 2]
    fam = grammar.canonical(cert.family)
    for b, r in looks.items():
        f_a = np.stack([c for term in fam for c in _column_np(term, X, V, T)], axis=1) @ np.asarray(r['coef_claim'])
        f_b = np.stack([c for term in grammar.canonical(b) for c in _column_np(term, X, V, T)], axis=1) @ \
            np.asarray(r['coef'])
        gap = float(np.max(np.abs(f_b - f_a)))
        if not (gap < cert.eps and abs(gap - r['gap']) <= 1e-6 * max(1.0, gap)):
            return f'the look-alike {grammar.name(b)} does not re-derive (gap {gap:.3g}, recorded {r["gap"]:.3g})'
    return None


def premise_reason(cert):
    """truth-v3 T2: a reason to refuse when the certificate's premise ledger is not the policy's for its audit and
    numerator (for example, a premise claimed proven that the judge only measures), else None."""
    want = truth.premise_ledger(getattr(cert, 'audit', 'wide'), getattr(cert, 'numerator', 'laplace'),
                                getattr(cert, 'knock', 'throw'), getattr(cert, 'band_test', 'ui'),
                                getattr(cert, 'claim_kind', 'exact'))
    if tuple(getattr(cert, 'premises', ())) != want:
        return 'the premise ledger is not the policy one'
    return None


def check_functional(cert, throws, sigma):
    """Decision 13: a functional claim, re-derived - the same premises and policy, the prior pi_F from the claim
    language, the throws, every grown term's values, then certify_functional again from the throws, and its band
    once more by other numerics (finite differences, QR, minimum-norm solves; every column from its definition)."""
    reasons = []
    why = premise_reason(cert)
    if why:
        reasons.append(why)
    throws = copy.deepcopy(list(throws))
    fam = grammar.canonical(cert.family)
    if cert.alpha > POLICY_ALPHA or cert.delta > POLICY_DELTA:
        reasons.append('alpha or delta laxer than policy')
    from . import likelihood as L
    for have, want, what in ((getattr(cert, 'numerator', 'laplace'), truth.NUMERATOR, 'numerator'),
                             (getattr(cert, 'audit', 'wide'), truth.AUDIT, 'audit'),
                             (getattr(cert, 'knock', 'throw'), L.KNOCK, 'knock model'),
                             (getattr(cert, 'band_test', 'ui'), truth.BAND, 'band test'),
                             (getattr(cert, 'claim_kind', 'exact'), truth.CLAIM, 'claim kind'),
                             (getattr(cert, 'library', ''), grammar.library_digest(), "invented shapes' library")):
        if have != want:
            reasons.append(f'the {what} is not the one in force')
    lp = truth.functional_prior(fam)
    if lp == -math.inf:
        return False, reasons + ['this family cannot be claimed in the functional language']
    if cert.log_prior is None or not _close(cert.log_prior, lp):
        reasons.append('the prior does not match the claim language')
    if cert.rivals or cert.nested:
        reasons.append('a functional claim lists no rivals and no nested terms')
    if not throws or truth.digest(throws) != cert.digest:
        return False, reasons + ['the throws are not the ones the certificate was made from']
    if not _grown_terms_agree(tuple(fam), truth.scope_of(throws)):
        return False, reasons + ["a grown term's values differ from its definition"]
    if _ramp_outside_np(fam, throws):                  # Decision 16: coverage re-derived here, from the throws
        return False, reasons + ["a ramp's expression leaves its range (or is not finite) at a reading"]
    if reasons:
        return False, reasons
    ledger = truth.Ledger([fam], sigma)
    for t in throws:
        ledger.add(t)
    redo = truth.certify_functional(ledger, fam, cert.eps, POLICY_ALPHA, POLICY_DELTA, cert.audit)
    if not _close(cert.band, redo.band):
        reasons.append('band does not match')
    elif redo.band is not None:                        # every functional law (reviewer VD13 fix 3 and 5)
        own = _band_independent(cert, throws, sigma, checks=truth.functional_checks(fam),
                                delta_eff=POLICY_DELTA * math.exp(lp), fd_svd=True)
        if not (own <= cert.band * (1 + BAND_AGREE) + 1e-9 and own <= cert.eps):
            reasons.append(f'the band does not re-derive independently below eps ({own:.3g} against {cert.band:.3g})')
    if not _close(cert.adequacy, redo.adequacy):
        reasons.append('adequacy does not match')
    if cert.scope != redo.scope:
        reasons.append('scope does not match the data')
    if not redo.accepted:
        reasons.extend(redo.reasons)
    return (not reasons), reasons


def check(cert, throws, sigma):
    """(accepted, reasons)."""
    if getattr(cert, 'claim_kind', 'exact') == 'functional':             # Decision 13
        return check_functional(cert, throws, sigma)
    reasons = []
    why = premise_reason(cert)
    if why:
        reasons.append(why)
    throws = copy.deepcopy(list(throws))
    fam = grammar.canonical(cert.family)
    space = grammar.space(inventions=cert.inventions)
    if fam not in space:
        return False, ['family is not in the idea space']
    if cert.alpha > POLICY_ALPHA or cert.delta > POLICY_DELTA:
        reasons.append('alpha or delta laxer than policy')
    needed = len(space)                                   # D9: the claim's multiplicity is paid through its prior
    if cert.n_space < needed:
        reasons.append('idea space size is wrong')
    if getattr(cert, 'numerator', 'laplace') != truth.NUMERATOR:          # N-2: the policy numerator only
        reasons.append('the numerator is not the policy one')
    if getattr(cert, 'audit', 'wide') != truth.AUDIT:                     # truth-v3 Decision 9: the policy audit
        reasons.append('the universe audit is not the policy one')
    from . import likelihood as L
    if getattr(cert, 'knock', 'throw') != L.KNOCK:                        # truth-v3 M-1: the policy knock model
        reasons.append('the knock model is not the policy one')
    if getattr(cert, 'band_test', 'ui') != truth.BAND:                    # Decision 8: the policy band test
        reasons.append('the band test is not the policy one')
    if getattr(cert, 'claim_kind', 'exact') != truth.CLAIM:               # Decision 11: the policy claim kind
        reasons.append('the claim kind is not the policy one')
    if getattr(cert, 'library', '') != grammar.library_digest():          # Decision 12: the same invented shapes
        reasons.append("the invented shapes' library is not the one in force")
    lp = grammar.log_prior(fam)
    if lp == -math.inf:
        return False, reasons + ['this family cannot be claimed in the grammar']
    if cert.log_prior is None or not _close(cert.log_prior, lp):
        reasons.append('the prior does not match the grammar')
    if not throws or truth.digest(throws) != cert.digest:
        return False, reasons + ['the throws are not the ones the certificate was made from']
    if not _grown_terms_agree(cert.inventions, truth.scope_of(throws)):
        return False, reasons + ["a grown term's values differ from its definition"]
    if truth.AUDIT == 'universe-1':                       # its own coverage test over the certificate's rival list
        gaps = truth.audit_gaps(fam, cert.rivals, space)
        if gaps:
            reasons.append(f'the universe audit has {len(gaps)} holes, e.g. {grammar.term_name(gaps[0][1])} '
                           f'without {grammar.term_name(gaps[0][0])}')
    if reasons:                     # T3-b1: a cheap reason already refuses; re-deriving (33 min with the audit) could
        return False, reasons       # only add reasons, never accept
    ledger = truth.Ledger(space, sigma, universe=max(needed, cert.n_space))
    for t in throws:
        ledger.add(t)
    redo = truth.certify(ledger, fam, cert.eps, POLICY_ALPHA, POLICY_DELTA)
    if set(cert.rivals) != set(redo.rivals):
        reasons.append('rival list differs from the idea space')
    else:
        for b, e in redo.rivals.items():
            if not _close(cert.rivals[b], e):
                reasons.append(f'e-value against {grammar.name(b)} does not match')
    thr = -math.log(POLICY_ALPHA) - lp                    # D9, computed here from the grammar
    adequacy_thr = math.log(grammar.ADEQUACY_THRESHOLD_SPACE / POLICY_ALPHA)
    if any(e < thr for e in redo.rivals.values()):
        reasons.append('a rival is not ruled out')
    if set(cert.nested) != set(redo.nested):
        reasons.append('nested terms differ')
    else:
        for i, iv in redo.nested.items():
            mine = iv if (iv and isinstance(iv[0], tuple)) else (iv,)          # a cell: one interval per knot
            theirs = cert.nested[i] if (cert.nested[i] and isinstance(cert.nested[i][0], tuple)) else (cert.nested[i],)
            if len(mine) != len(theirs) or not all(_close(a, c) and _close(b, d)
                                                    for (a, b), (c, d) in zip(theirs, mine)):
                reasons.append(f'interval for {i} does not match')
    if any(not truth.zero_inside(iv) for iv in redo.nested.values()):
        reasons.append('an extra term is needed')
    if not _close(cert.band, redo.band):
        reasons.append('band does not match')
    elif cert.band is not None and truth.curve_checks(fam):          # independent review T1-b: re-derived independently
        why = band_reason(cert, throws, sigma, needed)
        if why:
            reasons.append(why)
    if not _close(cert.adequacy, redo.adequacy):
        reasons.append('adequacy does not match')
    if redo.adequacy is None or redo.adequacy >= adequacy_thr:
        reasons.append('the law misfits more objects than bumps explain')
    if redo.band is None or not redo.band <= cert.eps:
        reasons.append('band exceeds eps')
    if cert.scope != redo.scope:
        reasons.append('scope does not match the data')
    mine, theirs = getattr(redo, 'lookalikes', None) or {}, getattr(cert, 'lookalikes', None) or {}
    if set(mine) != set(theirs):                                          # Decision 11: the same look-alikes,
        reasons.append('the look-alikes differ')                          # with the same numbers
    else:
        for b, r in mine.items():
            t = theirs[b]
            if not (_close(r['gap'], t['gap']) and _close(r.get('bound'), t.get('bound')) and
                    tuple(r.get('point') or ()) == tuple(t.get('point') or ())):
                reasons.append(f'the look-alike record of {grammar.name(b)} does not match')
        why = lookalike_reason(cert, throws)                               # and each re-derived by other numerics
        if why:
            reasons.append(why)
    if not redo.accepted:
        reasons.extend(redo.reasons)
    return (not reasons), reasons
