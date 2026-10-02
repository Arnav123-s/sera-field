"""The truth layer: evidence (D1), certificates for "sure" (D2), the "something else" alarm (OP3) and the
library of claims. See M1_DESIGN.md §3.

Everything here is a pure function of the stored throws (in the order they were made), the idea space and
the sensor noise, so the checker can recompute it all. A family A is certified at level alpha only if:
  1. every family in the idea space that does not contain A is ruled out: log E(A:B) >= log(1 / (alpha pi(A)))
     (decision D9, 2026-09-24; for the 67 base families this is log(67 / (0.9 alpha)) = 11.2, before it was 11.1)
     (the prior pi pays for choosing A after seeing the data: over all claims, P(ever sure and wrong) <= alpha);
  2. for every family A + psi, the time-uniform interval for psi's strength contains 0;
  3. a flexible family (A plus a smooth basis over the scope) bounds anything else by a band <= eps;
  3b. adequacy: A's best fit does not misfit more throws than bumps explain. This catches "something else"
     of any form, including forces that are not functions of position and speed (a hidden motor);
  4. the scope is the region the throws visited.

Every throw counts. A new object's mass is predicted from a mixture: the masses of objects already met in this
world, or something new (see likelihood.step), so meeting a familiar object again costs little.
"""
import copy
import dataclasses
import hashlib
import math
import os

import numpy as np

from . import grammar, likelihood as L, paths

BASIS = ((0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1), (1, 2), (2, 2))   # Legendre degrees (x, v)
GRID = 25                      # band checked on a GRID x GRID lattice over the scope
MISFIT_RMS = 1.5               # a throw whose best-fit residual is this many sigmas (RMS) is misfit
RHO0 = 0.15                    # misfit share that bumps can explain (nursery: about 5%; generous)
P1S = (0.3, 0.5, 0.8)          # alternatives mixed in the adequacy e-value


def model_of(family, extra_basis=False, scope=None):
    kind, a, b = grammar.codes(family)
    model = L.Model(kind, a, b, tie=grammar.tie(family))           # Decision 12: tied only with an invented shape
    if not extra_basis:
        return model
    sx = max(abs(scope['x'][0]), abs(scope['x'][1]), 1e-3)
    sv = max(abs(scope['v'][0]), abs(scope['v'][1]), 1e-3)
    basis = basis_for(family, scope)
    return model.extended(np.ones(len(basis), np.int64), [d[0] for d in basis], [d[1] for d in basis], sx, sv)


DUPLICATE = {('nothing', 'steady'): (0, 0), ('position', 'straight'): (1, 0), ('speed', 'straight'): (0, 1),
             ('product', 'straight', 'straight'): (1, 1)}      # x*v = P1(x)P1(v) up to scale (approved 2026-09-24)


def basis_for(family, scope=None):
    """The smooth basis, minus functions the family already has (a constant, x, v or x*v). truth-v2 (B4-1, R1): a
    cell spans exactly the constants and the lines of its input over its knot range, so it removes P0 always (its hats
    sum to 1 everywhere) and P1 of its input only when the scope lies inside the knot range (beyond the end knots the
    cell is constant, so a line there is not in its span). Nothing else is removed."""
    drop = {DUPLICATE[i] for i in family if i in DUPLICATE}
    for term in family:
        if term[0] != 'cell':
            continue
        drop.add((0, 0))
        base = grammar.base_input(term[1])                  # Decision 14: a lens's knot range is its window
        if base == 'time' or scope is None:
            continue
        if base not in ('position', 'speed'):              # Decision 15: a dimension spans no line of an input
            continue
        lo, hi = grammar.input_range(term[1])
        key, line = ('x', (1, 0)) if base == 'position' else ('v', (0, 1))
        if lo <= scope[key][0] and scope[key][1] <= hi:
            drop.add(line)
    return tuple(d for d in BASIS if d not in drop)


def curve_checks(family):
    """truth-v2 (independent review condition 2): a claim with a grown formula (a piece or a piece product) must also show that
    no further curve along the inputs it depends on is needed: the finest cell (33 knots) on each such input is a
    mandatory nested check, per knot at delta / (n K). It is never a rival (a free curve as a rival blocks every
    formula). Below the knot spacing (x 0.19, v 0.375, t 0.0625) only the adequacy test guards, and the certificate
    states that limit (docs/B4_GROWTH.md revision 4)."""
    inputs = []
    for term in family:
        if term[0] in ('piece', 'shape'):              # Decision 12: an invented shape is checked like a piece
            inputs.append(term[1])
        elif term[0] == 'pprod':
            inputs += ['position', 'speed']
    return [('cell', i, 33) for i in dict.fromkeys(inputs)]


def wide_terms(family):
    """truth-v2 (independent review T2): the terms whose laws a grown formula claim must also rule out, beyond the ledger's
    space - every grown piece on an input the claim's pieces use; every piece product sharing a part with the claim
    (the same x-part or the same v-part: additive curve checks cannot see a multiplicative mismatch); truth-v1's
    products sharing a shape part; the powers of those inputs; the drives when time is one. A law two swaps away (both
    parts of a product different) is not among them: only the band and the adequacy test guard against it, and the
    certificate's scope says so (docs/B4_GROWTH.md revision 6)."""
    inputs, xparts, vparts = set(), set(), set()
    for term in family:
        if term[0] == 'shape':                          # Decision 12: its input's pieces, powers (and drives)
            inputs.add(term[1])
        elif term[0] == 'piece':
            inputs.add(term[1])
            name = 'abs' if term[2] == 'abs' else f'{term[2]}{term[3]:g}'
            (xparts if term[1] == 'position' else vparts if term[1] == 'speed' else set()).add(name)
        elif term[0] == 'pprod':
            inputs |= {'position', 'speed'}
            xparts.add(term[1])
            vparts.add(term[2])
    out = [g for g in grammar.PIECES if g[1] in inputs]
    out += [g for g in grammar.LIBRARY if g[1] in inputs and grammar.claimable_term(g)]     # Decision 12
    out += [g for g in grammar.PPRODS if g[1] in xparts or g[2] in vparts]
    out += [g for g in grammar.OPEN_TERMS if (g[0] == 'product' and (g[1] in xparts or g[2] in vparts))
            or (g[0] == 'power' and g[1] in inputs) or (g[0] == 'drive' and 'time' in inputs)]
    return [g for g in dict.fromkeys(out) if g not in family]


def embedded_starts(ledger, family, limit=3):
    """independent review T2-C: starts for a wide rival's fit from laws it contains: each one's best fit, with the rival's extra
    terms at 0, so its best fit is never below theirs. independent review R-1: chosen from the SPACE only - the in-space
    families it contains, ranked by their prequential score Q, the top `limit` - and fitted here, so the starts depend
    on the throws alone (never on which fits earlier calls happened to leave in the ledger's cache): the mind's
    certificate and the checker's fresh re-derivation see the same rivals."""
    family = grammar.canonical(family)
    subs = [f for f in ledger.families if f != family and grammar.contains(family, f) and all(t in family for t in f)]
    subs.sort(key=lambda f: (-ledger.Q[f], repr(f)))
    out = []
    for f in subs[:limit]:
        fit = ledger.mle(f)
        if not fit.ok:
            continue
        coef = np.zeros(grammar.n_coef(family))
        for term in f:
            coef[grammar.coef_slice(family, term)] = fit.coef[grammar.coef_slice(f, term)]
        out.append(L.Post(np.concatenate([coef, [fit.mu[s] for s in fit.order]]),
                          np.eye(len(coef) + len(fit.order)), list(fit.order)))
    return tuple(out)


def _usable(fit):
    """independent review T2-A/B: only a fit that ran and converged may rule a rival out."""
    return bool(fit.ok and getattr(fit, 'converged', True) and math.isfinite(fit.loglik))


def wide_rivals(ledger, family, thr, scoped=None):
    """T2: every law of one wide term alone or with one base idea that is outside the space and does not contain the
    claim must be ruled out like a rival: log E = Q_claim - sup loglik >= thr. One fit of the term with every base idea
    (a superset: its sup is at least each member's) rules out the whole group at once; if it does not, each member is
    fitted. Returns (rivals, the first rival not ruled out or None, why: 'weak' | 'failed' | None); a superset appears
    under its own family. A fit that failed or did not converge is never a rival ruled out (independent review, T2-A/B)."""
    space = set(ledger.families)
    mu = ledger.mle(family).mu
    q_a = ledger.q_claim(family)
    rivals = {}
    for g in wide_terms(family):
        group = [f for f in dict.fromkeys(grammar.canonical(x) for x in [(g,)] + [(g, i) for i in grammar.IDEAS])
                 if f not in space and not grammar.collinear(f) and not grammar.contains(f, family)]
        if not group:
            continue
        top = grammar.canonical((g,) + tuple(grammar.IDEAS))
        s_top = ledger.sup(top, mu, embedded_starts(ledger, top))
        if _usable(s_top) and q_a - s_top.loglik >= thr:   # recorded only when it rules the group out: a superset
            rivals[top] = q_a - s_top.loglik                # the claim beats member by member is no rival itself
            continue
        for f in group:
            s = ledger.sup(f, mu, embedded_starts(ledger, f))
            if not _usable(s):
                rivals[f] = -math.inf
                return rivals, f, 'failed'
            rivals[f] = q_a - s.loglik
            if rivals[f] < thr and scoped is not None:
                e = scoped_evidence(ledger, f, family, q_a, scoped, fit=s)
                if e is not None:
                    rivals[f] = e
            if rivals[f] < thr:
                return rivals, f, 'weak'
    return rivals, None, None


# truth-v3 T2, Decision 9 (premise S; docs/SERA_FIELD_THEORY.md §14.1, independent review's rulings of 2026-09-25): the
# universe audit. 'universe-1' = stage 1, every claimable term except the cells (independent review: their families are left
# out and the certificate says so; semantic containment for cells is stage 2); 'wide' = truth-v2's T2 alone.
AUDIT = os.environ.get('CCOPS5_AUDIT', 'universe-1')
UNIVERSE_TERMS = grammar.OPEN_TERMS + grammar.PIECES + grammar.PPRODS
AUDIT_CHUNK = 8                 # terms of one kind per root node of the audit tree (a fixed, data-free partition)
AUDIT_FAST = True               # T3-b2: exact speed-ups E1-E3 (see universe_audit); False = the old path, for golden runs
NOT_AUDITED = 'cells (stage 1): laws with a free curve are not rivals here'


def universe_terms():
    """Every claimable non-cell term: truth-v1's open terms, the grown pieces and piece products and (Decision 12,
    under the 'library' policy) the library's invented shapes, fixed before the world began."""
    if grammar.SHAPES_POLICY != 'library':
        return UNIVERSE_TERMS
    return UNIVERSE_TERMS + tuple(t for t in grammar.LIBRARY if grammar.claimable_term(t))


def _audit_kind(term):
    return (term[0],) if term[0] in ('product', 'pprod') else (term[0], term[1])


def audit_tree(family, a):
    """The roots of the audit tree for the claim's term a: every universe term but a, grouped by kind (products; the
    powers of one input; sin or cos drives; the pieces of one input; piece products; the invented shapes of one
    input) in grammar order, AUDIT_CHUNK at a time. Fixed before any data; the claim's own invented term is included
    when a is another term (independent review 1b)."""
    kinds = {}
    for t in universe_terms():
        if t != a:
            kinds.setdefault(_audit_kind(t), []).append(t)
    return [tuple(ts[i:i + AUDIT_CHUNK]) for ts in kinds.values() for i in range(0, len(ts), AUDIT_CHUNK)]


def audit_children(node):
    """A node's two halves; a single term is a leaf."""
    if len(node) == 1:
        return []
    h = (len(node) + 1) // 2
    return [tuple(node[:h]), tuple(node[h:])]


def audit_superset(node, a):
    """U(node, -a): the node's terms with every base idea but a. Every claimable law made of one of the node's terms and
    at most one idea, and lacking a, is nested in it; a is never in it, so it never contains the claim."""
    return grammar.canonical(tuple(node) + tuple(i for i in grammar.IDEAS if i != a))


def audit_members(term, a):
    """The claimable laws U(term, -a) stands for: the term alone and with each idea but a."""
    return [grammar.canonical((term,) + extra) for extra in [()] + [(i,) for i in grammar.IDEAS if i != a]]


def _embed(family, sub, fit):
    """sub's best fit as a start for family (sub's terms inside family), family's other terms at 0."""
    coef = np.zeros(grammar.n_coef(family))
    for term in sub:
        coef[grammar.coef_slice(family, term)] = fit.coef[grammar.coef_slice(sub, term)]
    return L.Post(np.concatenate([coef, [fit.mu[s] for s in fit.order]]), np.eye(len(coef) + len(fit.order)),
                  list(fit.order))


def _best_member(ledger, family, claim):
    """The best-fitting law of the space inside `family` that is not the claim and does not contain it: (law, fit) or
    None. Its loglik is a lower bound on `family`'s sup (a nested model fits at least as well)."""
    best = None
    for f in ledger.families:
        if f != claim and not grammar.contains(f, claim) and set(f) <= set(family):
            fit = ledger.mle(f)
            if _usable(fit) and (best is None or fit.loglik > best[1].loglik):
                best = (f, fit)
    return best


def audit_fit(ledger, family, mu, claim, stop_above=None):
    """The best fit of a law or superset outside the space, for the audit. Started as truth-v2's wide rivals (pooled
    regression, plain Gaussian fit, embedded starts) and also (independent review 2) from the best-fitting law of the space that
    it contains and that does not contain the claim, with its extra terms at 0; the result must be at least that law's
    best fit, else it is marked unusable (an internal node then splits, a member refuses). The members come from the
    space and the claim alone, so the mind and the checker start from the same points. T3-b2 (E2): with `stop_above`
    the fit may stop early, at the first start already above that level (the caller then only splits).
    T3-b3: a ledger may carry `audit_shared`, a cache the mind shares across the ledgers it rebuilds within a world
    (never the checker's). The fit is a function of the throws, sigma, the fitting policy, the superset, the claim, its
    inverse masses, the early-exit level and the in-space laws inside the superset (its embedded starts and best
    member) - so under that key (_shared_key) the shared cache returns the same fit a fresh call would compute."""
    family = grammar.canonical(family)
    key = (family, grammar.canonical(claim)) + (() if stop_above is None else (stop_above,))
    if key in ledger._audit:
        return ledger._audit[key]
    shared = getattr(ledger, 'audit_shared', None)
    if shared is not None:
        skey = _shared_key(ledger, key, mu)
        if skey in shared:
            ledger._audit[key] = copy.deepcopy(shared[skey])      # V37E: never hand out the shared object itself
            return ledger._audit[key]
    best = _best_member(ledger, family, claim)
    starts = embedded_starts(ledger, family)
    if best is not None:
        starts = starts + (_embed(family, best[0], best[1]),)
    s = L.sup_fit(model_of(family), ledger.throws, ledger.sigma, mu, starts, stop_above=stop_above)
    if best is not None and _usable(s) and s.loglik < best[1].loglik - 1e-6:
        s = dataclasses.replace(s, converged=False)       # below a member it contains: a local optimum, never used
    ledger._audit[key] = s
    if shared is not None:
        shared[skey] = copy.deepcopy(s)
    return s


def _share(ledger, key, fit, mu):
    """Put a fit made elsewhere (a parallel worker) into the ledger's shared cache under audit_fit's key."""
    if getattr(ledger, 'audit_shared', None) is None:
        return
    ledger.audit_shared.setdefault(_shared_key(ledger, key, mu), copy.deepcopy(fit))


def _shared_key(ledger, key, mu):
    """audit_fit's key in the shared cache. an independent review ((review notes, not published)): the
    throws' digest is recomputed at every call (a throw changed in place, at the same count, is never served a stale
    fit; the digest is a hash of their bytes, cheap beside any fit), and the fitting policy is part of the key
    (the knock mode picks _fit or _fit_knocks and the Jacobian rule changes every fit). When the throws change, the
    older fits are dropped."""
    shared = ledger.audit_shared
    d = digest(ledger.throws)
    if shared.get('__throws__') != d:
        shared.clear()
        shared['__throws__'] = d
    inside = tuple(sorted((f for f in ledger.families if set(f) <= set(key[0])), key=repr))
    return d, tuple(ledger.sigma), (L.KNOCK, L.EXACT_JACOBIAN), key, inside, tuple(sorted(mu.items()))


def _walk_root(ledger, family, a, root, mu, q_a, thr, bar, space, known, scoped=None):
    """One root node's subtree of the universe audit, depth first: returns (the rivals it records, in order; the
    first law not ruled out or None; why: 'weak' | 'failed' | None). `known`: rivals recorded before this root's
    term of the claim began (a member recorded there is skipped). `scoped` (Decision 11): the certificate's scope
    context; a single law (a member) the plain rule cannot rule out is tried again over W (scoped_evidence). A
    superset is only ever split, as before: a flexible superset mimics almost any claim, and a bound over W rarely
    rules it out, so it is not tried (trying less is never less valid)."""
    rivals = {}
    stack = [root]
    while stack:
        node = stack.pop()
        U = audit_superset(node, a)
        if AUDIT_FAST:
            best = _best_member(ledger, U, family)
            s = None if best is not None and best[1].loglik > bar else audit_fit(ledger, U, mu, family, bar)
        else:
            s = audit_fit(ledger, U, mu, family)
        if s is not None and _usable(s) and q_a - s.loglik >= thr:
            rivals[U] = q_a - s.loglik
            continue
        kids = audit_children(node)
        if kids:
            stack += list(reversed(kids))
            continue
        for f in audit_members(node[0], a):
            if f in space or f in known or f in rivals or grammar.log_prior(f) == -math.inf or \
                    grammar.contains(f, family):
                continue
            s = audit_fit(ledger, f, mu, family)
            if not _usable(s):
                rivals[f] = -math.inf
                return rivals, f, 'failed'
            rivals[f] = q_a - s.loglik
            if rivals[f] < thr and scoped is not None:
                e = scoped_evidence(ledger, f, family, q_a, scoped, fit=s)
                if e is not None:
                    rivals[f] = e
            if rivals[f] < thr:
                return rivals, f, 'weak'
    return rivals, None, None


AUDIT_WORKERS = int(os.environ.get('CCOPS5_AUDIT_WORKERS', '0'))   # T3-b4: 0 = the one-process walk
_WORKER = {}


def _worker_init(ledger, args, scoped=None):
    _WORKER['ledger'], _WORKER['args'], _WORKER['scoped'] = ledger, args, scoped


def _worker_walk(job):
    """A worker's root: its walk, the fits it made (so the caller's caches keep them) and, Decision 11, the
    look-alikes it recorded."""
    a, root, known = job
    ledger, sc = _WORKER['ledger'], _WORKER.get('scoped')
    before = set(ledger._audit)
    seen = set(sc['lookalikes']) if sc is not None else set()
    out = _walk_root(ledger, *_WORKER['args'][:1], a, root, *_WORKER['args'][1:], known, scoped=sc)
    looks = {k: v for k, v in sc['lookalikes'].items() if k not in seen} if sc is not None else {}
    return out, {k: v for k, v in ledger._audit.items() if k not in before}, looks


def universe_audit(ledger, family, thr, workers=None, scoped=None):
    """Rule out every claimable law (stage 1: but cells) that does not contain the claim and is not in the ledger's
    space (those were ruled out one by one): for each term a of the claim, walk the audit tree; a node whose superset
    U(node, -a) is ruled out (Q_A - sup >= thr) covers all its laws at once, one that is not is halved, and at a single
    term the laws it stands for are fitted one by one. Returns (rivals, the first law not ruled out or None, why:
    'weak' | 'failed' | None); a superset is recorded under its own family, only when it rules its laws out.
    T3-b2 (AUDIT_FAST): a superset is not fitted when its best in-space member is already within the threshold (E1),
    and its fit stops at the first start above q_A - thr (E2) - in both cases it could not be ruled out and is split,
    exactly as before; nothing recorded changes. T3-b4: with `workers` (default AUDIT_WORKERS) > 1 the roots of each
    term are walked in parallel processes and merged in the tree's order, up to the first law not ruled out - the
    same record as the one-process walk."""
    family = grammar.canonical(family)
    space = set(ledger.families)
    q_a = ledger.q_claim(family)
    mu = ledger.mle(family).mu
    bar = q_a - thr + 1e-6                                  # a superset above this is never ruled out
    workers = AUDIT_WORKERS if workers is None else workers
    if workers <= 1:                                        # the one-process walk, as committed in f14cb0c
        rivals = {}
        for a in family:
            stack = list(reversed(audit_tree(family, a)))
            while stack:
                node = stack.pop()
                U = audit_superset(node, a)
                if AUDIT_FAST:
                    best = _best_member(ledger, U, family)
                    s = None if best is not None and best[1].loglik > bar else audit_fit(ledger, U, mu, family, bar)
                else:
                    s = audit_fit(ledger, U, mu, family)
                if s is not None and _usable(s) and q_a - s.loglik >= thr:
                    rivals[U] = q_a - s.loglik
                    continue
                kids = audit_children(node)
                if kids:
                    stack += list(reversed(kids))
                    continue
                for f in audit_members(node[0], a):
                    if f in space or f in rivals or grammar.log_prior(f) == -math.inf or grammar.contains(f, family):
                        continue
                    s = audit_fit(ledger, f, mu, family)
                    if not _usable(s):
                        rivals[f] = -math.inf
                        return rivals, f, 'failed'
                    rivals[f] = q_a - s.loglik
                    if rivals[f] < thr and scoped is not None:
                        e = scoped_evidence(ledger, f, family, q_a, scoped, fit=s)
                        if e is not None:
                            rivals[f] = e
                    if rivals[f] < thr:
                        return rivals, f, 'weak'
        return rivals, None, None
    rivals = {}
    pool = None
    try:
        for a in family:
            roots = audit_tree(family, a)
            known = frozenset(rivals)
            if True:
                if pool is None:
                    import concurrent.futures as cf
                    import multiprocessing as mp
                    pool = cf.ProcessPoolExecutor(         # workers get a copy of the ledger (and of its shared
                        max_workers=workers, initializer=_worker_init,   # cache: exact, so reading it only saves work)
                        initargs=(ledger, (family, mu, q_a, thr, bar, space), scoped),
                        mp_context=mp.get_context('spawn' if os.name == 'nt' else 'fork'))
                results = pool.map(_worker_walk, [(a, root, known) for root in roots])
            for (part, weak, why), fits, looks in results:
                if fits:
                    for key, fit in fits.items():
                        ledger._audit.setdefault(key, fit)
                        if key[0] != 'scoped':                  # Decision 11's bounds are not fits: never shared
                            _share(ledger, key, fit, mu)
                if scoped is not None:
                    scoped['lookalikes'].update(looks)
                rivals.update(part)
                if weak is not None:
                    return rivals, weak, why
    finally:
        if pool is not None:
            pool.shutdown(cancel_futures=True)
    return rivals, None, None


def audit_gaps(family, rivals, space):
    """The checker's coverage test: every (a, t) - a term of the claim, t a universe term but a - must be covered by a
    recorded superset holding t and every idea but a (and not a), or by all the laws U(t, -a) stands for being in the
    space or recorded. Returns the (a, t) pairs not covered."""
    space = set(space)
    gaps = []
    for a in grammar.canonical(family):
        need = set(grammar.IDEAS) - {a}
        covered = set()
        for U in rivals:
            if a not in U and need <= set(U):
                covered |= set(U) - need
        for t in universe_terms():
            if t == a or t in covered:
                continue
            if all(f in space or f in rivals or grammar.log_prior(f) == -math.inf for f in audit_members(t, a)):
                continue
            gaps.append((a, t))
    return gaps


def zero_inside(interval):
    """True when a nested interval holds 0; a cell's nested interval is one (lo, hi) per knot, all must hold 0."""
    if interval and isinstance(interval[0], tuple):
        return all(lo <= 0.0 <= hi for lo, hi in interval)
    lo, hi = interval
    return lo <= 0.0 <= hi



def digest(throws):
    h = hashlib.sha256()
    for t in throws:
        h.update(np.asarray([t.situation] + [x for s in t.action.segments for x in s], float).tobytes())
        h.update(np.asarray(t.x, float).tobytes())
        h.update(np.asarray(t.v, float).tobytes())
    return h.hexdigest()


MIN_CELL_READINGS = 2           # D10: a cell counts as visited with at least this many readings


def cell_of(scope, x, v):
    """D10: the lattice node (i, j) nearest to (x, v) on the GRID x GRID lattice over the scope's box, or None
    outside the box."""
    (x0, x1), (v0, v1) = scope['x'], scope['v']
    if not (x0 <= x <= x1 and v0 <= v <= v1):
        return None
    i = int(round((x - x0) / (x1 - x0) * (GRID - 1))) if x1 > x0 else 0
    j = int(round((v - v0) / (v1 - v0) * (GRID - 1))) if v1 > v0 else 0
    return (i, j)


def scope_of(throws):
    """Part 4: the 2nd-98th percentile box of the readings and, by decision D10 (2026-09-24), the lattice cells
    the readings visited; a certificate speaks only for those cells."""
    xs = np.concatenate([t.x for t in throws])
    vs = np.concatenate([t.v for t in throws])
    us = [s[2] for t in throws for s in t.action.segments]
    scope = {'x': (float(np.percentile(xs, 2)), float(np.percentile(xs, 98))),
             'v': (float(np.percentile(vs, 2)), float(np.percentile(vs, 98))),
             'u': (float(min(us)), float(max(us)))}
    counts = {}
    for x, v in zip(xs, vs):
        c = cell_of(scope, float(x), float(v))
        if c is not None:
            counts[c] = counts.get(c, 0) + 1
    scope['cells'] = tuple(sorted(c for c, n in counts.items() if n >= MIN_CELL_READINGS))
    return scope


def prequential(model, throws, sigma):
    """Sum of log q(y_j | y_<j) over the throws in order, and the posterior after all of them."""
    total, post = 0.0, L.empty_post(model)
    for t in throws:
        q, post = L.step(model, post, t, sigma)
        total += q
    return total, post


# N-2 (docs/N2_EXACT_NUMERATOR.md, draft Decision 7): the numerator where validity is claimed - the claim's Q in its
# e-values and the band's flexible q_f. 'laplace' (today's rule) | 'lattice' | 'mu' (independent review's P-2). The ledger's
# running Laplace Q still ranks laws and chooses pushes (adaptive choices may use anything), and the nested intervals
# keep Laplace (independent review S-2: an inflated Q there only narrows them, which errs on the side of "not sure").
NUMERATOR = os.environ.get('CCOPS5_NUMERATOR', 'laplace')
# Decision 8 (plan revision 4, R4-2; docs/D8_BAND_TEST.md): the band's confidence radius from the flexible model's own
# forecast Q_f ('ui', truth-v1/v2) or from the claim's forecast Q_A ('claim': the band as a test of "the extra force
# exceeds the bound somewhere", the same formula with radius^2 = 2 (log L_f - Q_A + log(1 / delta))).
BAND = os.environ.get('CCOPS5_BAND', 'ui')
if BAND not in ('ui', 'claim'):                 # reviewer VD8: any other string must not silently compute the 'ui' band
    raise ValueError(f"CCOPS5_BAND must be 'ui' or 'claim', not {BAND!r}")


def prequential_exact(model, throws, sigma, how=None):
    """(Q, posterior) with the policy numerator; the posterior path is Laplace's in every case."""
    how = how or NUMERATOR
    if how == 'laplace':
        return prequential(model, throws, sigma)
    total, post = 0.0, L.empty_post(model)
    for t in throws:
        q, post = L.step_exact(model, post, t, sigma, how)
        total += q
    return total, post


class Ledger:
    """Throws in the order they were made, with each family's running prequential log-score (the e-process
    numerator) and, on demand, its maximum-likelihood fit (the denominator)."""

    def __init__(self, families, sigma, universe=None):
        self.families = [grammar.canonical(f) for f in families]
        self.sigma = sigma
        self.n_space = universe or len(self.families)   # the size paid for in thresholds
        self.throws = []
        self.Q = {f: 0.0 for f in self.families}
        self._models = {f: model_of(f) for f in self.families}
        self.post = {f: L.empty_post(self._models[f]) for f in self.families}
        self._mle = {}
        self._sup = {}
        self._qx = {}
        self._audit = {}
        self.library = grammar.library_digest()        # Decision 12: the library this ledger's world was lived under

    def add(self, throw):
        for f in self.families:
            q, self.post[f] = L.step(self._models[f], self.post[f], throw, self.sigma)
            self.Q[f] += q
        self.throws.append(throw)
        self._mle = {}
        self._sup = {}
        self._qx = {}
        self._audit = {}

    def mle(self, family):
        family = grammar.canonical(family)
        if family not in self._mle:
            if family not in self._models:                    # truth-v2: a family outside the space (a nested check)
                self._extra(family)
            self._mle[family] = L.fit(self._models[family], self.throws, self.sigma, start=self.post[family],
                                      iters=30)
        return self._mle[family]

    def _extra(self, family):
        """Model, prequential score and posterior of a family outside the space, from the stored throws (used only
        by truth-v2's mandatory curve check; it never becomes a rival)."""
        self._models[family] = model_of(family)
        self.Q[family], self.post[family] = prequential(self._models[family], self.throws, self.sigma)

    def sup(self, family, mu, starts=()):
        """truth-v2 (T2): the best fit of a family outside the space (a wide rival), started from the claim's inverse
        masses `mu` and the given embedded starts (L.sup_fit); it never gets a prequential score and never becomes a
        claim."""
        family = grammar.canonical(family)
        if family not in self._sup:
            self._sup[family] = L.sup_fit(model_of(family), self.throws, self.sigma, mu, starts)
        return self._sup[family]

    def q_claim(self, family):
        """The claim's numerator under the policy (N-2); the running Laplace Q when the policy is 'laplace'."""
        f = grammar.canonical(family)
        if NUMERATOR == 'laplace':
            return self.Q[f]
        key = (f, len(self.throws), NUMERATOR)
        if key not in self._qx:
            self._qx[key] = prequential_exact(self._models.get(f) or model_of(f), self.throws, self.sigma)[0]
        return self._qx[key]

    def log_e(self, a, b):
        ll = self.mle(b).loglik
        if not math.isfinite(ll):       # V395c: a rival fit that broke down bounds nothing: never ruled out by it
            return -math.inf
        return self.q_claim(a) - ll

    def best_family(self):
        return max(self.families, key=lambda f: (self.Q[f], -len(f)))

    def interval(self, family, throw, level=0.95):
        f = grammar.canonical(family)
        return L.interval(self._models[f], self.post[f], throw, self.sigma, level)


@dataclasses.dataclass(frozen=True)
class Certificate:
    family: tuple
    alpha: float
    delta: float
    eps: float
    n_space: int
    inventions: tuple             # invented terms in play (their families are rivals too)
    digest: str
    rivals: dict                  # rival family -> log E(A:B)
    nested: dict                  # extra idea -> (lo, hi) for its strength
    band: object                  # float, or None when not computed
    adequacy: object              # log e-value that the family misfits too many throws (None if not computed)
    scope: dict
    accepted: bool
    reasons: tuple
    log_prior: object = None      # D9: log pi(family); the checker recomputes it from the grammar
    numerator: str = 'laplace'    # N-2: which numerator the e-values and the band used (the checker requires policy)
    audit: str = 'wide'           # truth-v3 Decision 9: which rivals outside the space were ruled out (policy AUDIT)
    premises: tuple = ()          # truth-v3 T2: the premise ledger (premise_ledger), recomputed by the checker
    knock: str = 'throw'          # truth-v3 M-1: the knock model (likelihood.KNOCK); the checker requires policy
    band_test: str = 'ui'         # Decision 8: whose forecast sets the band's radius (policy BAND); the checker too
    claim_kind: str = 'exact'     # Decision 11: 'scoped' = "A up to eps at the visited readings" (policy CLAIM)
    lookalikes: object = None     # Decision 11: rival -> its look-alike record (gap, coefficients, bound, evidence)
    library: str = ''             # Decision 12: the digest of the invented shapes' library it was made under


def _nested_interval(ledger, family, idea, delta_eff):
    """The interval for the extra term's coefficient; a cell (truth-v2) gets one interval per knot, each at
    delta_eff / K (B4-5)."""
    fam_b = grammar.canonical(family + (idea,))
    fit_b = ledger.mle(fam_b)
    sl = grammar.coef_slice(fam_b, idea)
    width = sl.stop - sl.start
    radius2 = 2.0 * (fit_b.loglik - ledger.Q[fam_b] + math.log(width / delta_eff))
    out = []
    for k in range(sl.start, sl.stop):
        var = float(fit_b.cov[k, k])
        if not (fit_b.ok and np.isfinite(var) and var >= 0 and radius2 >= 0):
            out.append((-math.inf, math.inf))
            continue
        half = math.sqrt(radius2 * var)
        c = float(fit_b.coef[k])
        out.append((c - half, c + half))
    return out[0] if width == 1 else tuple(out)


def _band_numerator():
    """The flexible fit has many numbers: a full lattice is infeasible there, so any exact policy uses the
    mu-lattice (every component normalized in any dimension; independent review P-2)."""
    return 'laplace' if NUMERATOR == 'laplace' else 'mu'


def band_of(throws, family, sigma, scope, delta_eff, q_ref=None):
    """Part 3: the largest possible size of a smooth unmodelled force over the scope, at confidence 1-delta."""
    model = model_of(family, extra_basis=True, scope=scope)
    q_f, post_f = prequential_exact(model, throws, sigma, _band_numerator())
    fit_f = L.fit(model, throws, sigma, start=post_f, iters=40)
    if not fit_f.ok:
        return math.inf
    basis = basis_for(family, scope)
    nb, na = len(basis), grammar.n_coef(family)
    cb = fit_f.coef[na:na + nb]
    cov = fit_f.cov[na:na + nb, na:na + nb]
    radius2 = 2.0 * (fit_f.loglik - (q_f if q_ref is None else q_ref) + math.log(1.0 / delta_eff))   # D8: q_ref = Q_A
    if not (math.isfinite(radius2) and radius2 >= 0) or not np.all(np.isfinite(cov)):   # reviewer VD8: fail closed on
        return math.inf                                                                 # nan / inf, not only < 0
    xs = np.linspace(scope['x'][0], scope['x'][1], GRID)
    vs = np.linspace(scope['v'][0], scope['v'][1], GRID)
    from . import paths
    worst = 0.0
    cells = set(scope['cells']) if 'cells' in scope else None      # D10: only where the throws went
    for i, x in enumerate(xs):
        for j, v in enumerate(vs):
            if cells is not None and (i, j) not in cells:
                continue
            bvec = np.array([paths.term(1, d[0], d[1], x, v, model.sx, model.sv) for d in basis])
            var = float(bvec @ cov @ bvec)
            if var < -1e-6 * float(np.abs(bvec) @ np.abs(cov) @ np.abs(bvec)):   # reviewer VD8: a materially negative
                return math.inf                                                  # variance is no covariance
            val = abs(float(bvec @ cb)) + math.sqrt(radius2 * max(var, 0.0))
            if not math.isfinite(val):                  # max(worst, nan) would keep worst: fail closed instead
                return math.inf
            worst = max(worst, val)
    return worst


LAST_WHERE = {}                 # revision 7 (the author: SERA may convince the judge, never change it): the reading
                                # where the last band peaked - information only; nothing the judge decides reads it
NULL_SHARE = 1e-9               # truth-v2 T1: a band value with more than this share the data cannot see is unbounded


def flexible_fit(model, throws, sigma, family, post_f):
    """The band's flexible fit: its maximum likelihood (the band's radius and centre are those of the sup; a local
    optimum below it would make the band too narrow, or its radius negative). Started from its own prequential
    posterior, the robust fit can stall where most objects look knocked (2026-09-28: a steady push claimed as a free
    curve in time - the fit called six of eight objects knocked, loglik -618 against the claim's own best 7110, so every
    law on time was refused with an infinite band). So it is also started from the claim's own best fit with every
    extra number at 0 - it can then never end below that fit, as every accepted step raises the likelihood - and the
    best ok fit is kept (as sup_fit keeps the best of its starts). reviewer VD14 fix 1: the embedded start carries the
    claim's own knock assignment, the embedded claim itself is a candidate (no step taken), and the result must not
    fall below the claim's own best likelihood - else the fit is not ok (fail closed). This is a search improvement,
    not a certified supremum (premise Q)."""
    fits = [L.fit(model, throws, sigma, start=post_f, iters=40)]
    cm = model_of(grammar.canonical(family))
    fc = L.fit(cm, throws, sigma, start=prequential_exact(cm, throws, sigma)[1], iters=40)
    floor = None
    if fc.ok and np.all(np.isfinite(fc.coef)):
        mean = np.concatenate([fc.coef, np.zeros(model.n_coef - cm.n_coef), [fc.mu[s] for s in fc.order]])
        emb = L.Post(mean, np.eye(mean.size), list(fc.order))
        fits.append(L.fit(model, throws, sigma, start=emb, iters=40, knocks=fc.knocks))
        fits.append(L.fit(model, throws, sigma, start=emb, iters=0, knocks=fc.knocks))    # the claim, embedded
        floor = float(fc.loglik)
    ok = [f for f in fits if f.ok]
    if not ok:
        return fits[0]
    best = max(ok, key=lambda f: f.loglik)
    if floor is not None and best.loglik < floor - 1e-6 * max(1.0, abs(floor)):
        best.ok = False                                   # below the claim it contains: fail closed
    return best


def grown_band(throws, family, sigma, scope, delta_eff, q_ref=None, checks=None):
    """truth-v2 (independent review T1): part 3 for a claim with a grown formula - a SIZE bound on anything else, including any
    further curve along the inputs the claim's pieces use.

    One flexible fit: the claim, the smooth basis and the finest cell (33 knots) on each such input (curve_checks).
    What the claim leaves out at a point is (I - P) [basis | cells] theta, with P the projection onto the claim's own
    columns over the measured points (what the claim's own coefficients can say is not "something else"). It is
    bounded like band_of: |value| + sqrt(radius2 * var), radius2 = 2 (loglik - Q + log(1 / delta_eff)), its maximum
    over every reading in a visited D10 cell (where the data looked: between readings, below the sampling, only the
    adequacy test guards; a lattice node between readings can sit in a cell's knot the data never touched). The
    variances come from the SVD of the whitened Jacobian (L.whitened_jacobian), never from inverting the
    near-singular information matrix (the cell spans the claim's pieces up to interpolation error); a value the data
    cannot see (a share above NULL_SHARE in the Jacobian's null space) is unbounded. The cells span x in [-3, 3],
    v in [-6, 6], t in [0, 2] at spacings 0.1875, 0.375, 0.0625; finer or farther, the smooth basis and the adequacy
    test guard (docs/B4_GROWTH.md revision 5)."""
    family = grammar.canonical(family)
    base = model_of(family, extra_basis=True, scope=scope)
    checks = curve_checks(family) if checks is None else checks          # Decision 13 passes its own
    extra = [c for cell in checks for c in grammar.term_codes(cell)]
    model = base.extended([c[0] for c in extra], [c[1] for c in extra], [c[2] for c in extra])
    q_f, post_f = prequential_exact(model, throws, sigma, _band_numerator())
    fit_f = flexible_fit(model, throws, sigma, family, post_f)            # 2026-09-28: the best of two starts
    radius2 = 2.0 * (fit_f.loglik - (q_f if q_ref is None else q_ref) + math.log(1.0 / delta_eff))   # D8
    if not fit_f.ok or not (math.isfinite(radius2) and radius2 >= 0):          # reviewer VD8: nan / inf fail closed
        return math.inf
    na, nc = grammar.n_coef(family), model.n_coef
    cells = set(scope['cells'])
    pts = [(float(t.x[n]), float(t.v[n]), n * paths.DT_OBS) for t in throws for n in range(paths.N_OBS)
           if cell_of(scope, float(t.x[n]), float(t.v[n])) in cells]
    if not pts:
        return math.inf
    nk = model.kind.shape[0]
    F = np.array([[paths.term_t(model.kind[j], model.a[j], model.b[j], x, v, t, model.sx, model.sv)
                   for j in range(nk)] for x, v, t in pts])
    if model.tie is not None:                                   # Decision 12: the tied coefficients' columns
        F = F @ model.tie
    Uc, sc, _ = np.linalg.svd(F[:, :na], full_matrices=False)
    Qc = Uc[:, sc > 1e-12 * sc.max()] if sc.size and sc.max() > 0 else Uc[:, :0]
    G = F[:, na:] - Qc @ (Qc.T @ F[:, na:])                   # what the claim leaves out, per unit of each coefficient
    J = L.whitened_jacobian(model, fit_f, throws, sigma)
    if not np.all(np.isfinite(J)):
        return math.inf
    _, s, Vt = np.linalg.svd(J, full_matrices=False)
    keep = s > 1e-12 * s.max()
    Vk = Vt[keep][:, na:nc]                                   # directions the data sees, restricted to the band part
    proj = G @ Vk.T
    size2 = np.sum(G * G, axis=1)
    null = np.maximum(size2 - np.sum(proj * proj, axis=1), 0.0)
    if np.any(null > NULL_SHARE * np.maximum(size2, 1e-300)):
        return math.inf
    var = np.sum((proj / s[keep]) ** 2, axis=1)
    vals = np.abs(G @ fit_f.coef[na:]) + np.sqrt(radius2 * var)
    i = int(np.argmax(vals))
    out = float(vals[i])
    LAST_WHERE.clear()                                          # revision 7: where the judge is least sure, for
    LAST_WHERE.update(x=pts[i][0], v=pts[i][1], t=pts[i][2], band=out)   # SERA to answer with evidence there
    return out if math.isfinite(out) else math.inf                          # reviewer VD8: fail closed


def adequacy(ledger, family):
    """log e-value that `family` misfits more situations than bumps explain: a binomial mixture over P1S against a
    misfit share of RHO0, over situations (Decision 6), a situation being misfit when any of its throws' residuals
    under the family's best fit exceeds MISFIT_RMS."""
    fam = grammar.canonical(family)
    fit = ledger.mle(fam)
    if not fit.ok:
        return math.inf
    model = ledger._models[fam]
    misfit = {}                     # Decision 6 (2026-09-25, B3 L1-07): per SITUATION. A bump is drawn per situation
    for t in ledger.throws:         # and repeats on every push of it, so a per-throw count let a mind that keeps
        kt = L.knocked(t, (fit.knocks or {}).get(t.situation, 0))                  # M-1: its knock, if any
        r = (L._obs(t) - L._sim(model, fit.coef, fit.mu[t.situation], kt)) * L._scale(ledger.sigma)   # pushing one
        bad = float(np.sqrt(np.mean(r * r))) > MISFIT_RMS                                   # bumped object fire the
        misfit[t.situation] = misfit.get(t.situation, False) or bad                         # alarm on the true law
    k, n = sum(misfit.values()), len(misfit)
    terms = [k * math.log(p / RHO0) + (n - k) * math.log((1 - p) / (1 - RHO0)) for p in P1S]
    top = max(terms)
    return top + math.log(sum(math.exp(x - top) for x in terms) / len(P1S))


def challenge(cert, family, coef, mu, throws, sigma):
    """truth-v3 T2, the refutation API (S4 §6.6): premise U made publicly attackable. A witness is a rival law (a
    claimable family that does not contain the claim) with numbers: its coefficients and each object's inverse mass
    {situation: mu}. On the certificate's own throws, its robust log-likelihood (the judge's: log(N + rho b) per
    throw) is a lower bound on that rival's best fit, so if it exceeds Q_A - thr(A) the rival was not ruled out and
    the certificate is refuted. Returns (refuted, margin in nats = Q_A - loglik - thr; negative refutes) or
    (False, why) when the witness is not admissible."""
    fam_a, fam_b = grammar.canonical(cert.family), grammar.canonical(family)
    if not throws or digest(throws) != cert.digest:
        return False, "these are not the certificate's throws"
    if (getattr(cert, 'numerator', 'laplace'), getattr(cert, 'audit', 'wide'), getattr(cert, 'knock', 'throw')) != \
            (NUMERATOR, AUDIT, L.KNOCK):            # independent review T2 review M1: Q_A below is computed under the policy
        return False, 'the certificate was made under another policy than the current one'
    if fam_b == fam_a or grammar.contains(fam_b, fam_a) or grammar.log_prior(fam_b) == -math.inf:
        return False, 'the witness is not a rival of the claim'
    model = model_of(fam_b)
    coef = np.asarray(coef, float)
    if coef.shape != (grammar.n_coef(fam_b),) or any(t.situation not in mu for t in throws):
        return False, 'the witness numbers do not fit the rival law'
    ll = 0.0
    for t in throws:
        ln, lb = L.throw_loglik(model, coef, float(mu[t.situation]), t, sigma), L.log_outlier(t)
        ll += L._lse2(ln, lb)                   # V395c: -inf, never nan
    ledger = Ledger([fam_a], sigma)
    for t in throws:
        ledger.add(t)
    margin = ledger.q_claim(fam_a) - ll - grammar.log_threshold(fam_a, cert.alpha)
    return bool(margin < 0), float(margin)


SCOPED_CLAIM = 'the force is the claim, up to eps, at every reading in the visited cells (Decision 11)'


def premise_ledger(audit, numerator, knock='throw', band='ui', claim='exact'):
    """truth-v3 T2 (docs/SERA_FIELD_THEORY.md v1.1 §12-15): the premises of Theorem A a "sure" rests on, each with its
    standing - proven (by construction), computed (by this certificate), measured (by a probe, not a proof) or
    assumed - and why, in words. It is policy, not data: it changes only with the judge's version, and the checker
    refuses a certificate whose ledger differs (one that overstates a premise). Order: P, M, N, U, S, F, Q (and T for
    a scoped claim, Decision 11, whose S speaks only of laws that differ from the claim by more than eps)."""
    out = _premises(audit, numerator, knock, band)
    if grammar.SHAPES_POLICY == 'library':                  # Decision 12
        out = out + (('L', 'proven', "SERA's invented shapes (the library) are fixed before the world begins; the n-th "
                                     'has prior 0.01 * 6 / (pi^2 n^2) whatever it is, so every prior is fixed before '
                                     "this world's data"),)
    if claim == 'functional':                               # Decision 13
        keep = tuple(p for p in out if p[0] in ('P', 'M', 'N', 'L'))
        return keep + (
            ('S', 'not needed', 'a functional claim names no law against its rivals: any law within eps of it at the '
                                'visited readings is as right as it, and any law farther is bounded out by the band - '
                                'given F, N and Q'),
            ('F', 'assumed', "the true force lies in the span of the band basis (the law, smooth terms up to degree 2 "
                             "in each of position and speed, and a 33-knot free curve on every input the law uses - "
                             "for a law on a lens, on the lens and on its whole input; on a dimension SERA made, on that "
                             "dimension); outside it there is no coverage guarantee - a feature finer than the 33-knot "
                             "grids, one outside a lens's window finer than its whole input's grid, one in an input the "
                             "law does not use, an interaction of inputs no dimension of the law carries - and the "
                             "adequacy test may refuse, without a bound"),
            ('Q', 'assumed', 'the band takes the quadratic approximation of the likelihood set around one local best '
                             'flexible fit (the best of several starts, never below the claim) as one-sided - not a '
                             'certified bound; it holds at the readings in the visited cells, not between them'),
            ('C', 'computed', FUNCTIONAL_CLAIM))
    if claim != 'scoped':
        return out
    s_scoped = ('S', 'computed', 'every claimable law that differs from the claim\'s best fit by at least eps at a '
                                 'reading in the visited cells was ruled out, except the laws with a free curve (cells), '
                                 'given U and T') if audit == 'universe-1' else \
        ('S', 'assumed', 'only the laws in the space (and a grown claim\'s wide rivals) that differ from the claim by at '
                         'least eps at a visited reading were ruled out')
    return tuple(s_scoped if p[0] == 'S' else p for p in out) + (
        ('T', 'assumed', 'a look-alike rival (within eps of the claim at every visited reading) is bounded by penalized '
                         'fits at the 4 (reading, sign) pairs its quadratic approximation ranks first, each never below '
                         'the best fit pushed out to eps there; the ranking is not certified (docs/SCOPED_CLAIMS.md)'),)


def _premises(audit, numerator, knock, band):
    n_why = {'laplace': 'the Laplace forecast integrates to at most 1: measured on teacher throws (N-1 pass); designed '
                        'throws under T-ADAPT',
             'lattice': 'the exact lattice forecast is normalized by construction (N-2); its guard NRES measured',
             'mu': 'the exact mass-lattice forecast is normalized by construction (N-2)'}.get(numerator, 'unknown')
    return (('P', 'proven', 'every push and every claim chosen uses only the past; constants frozen before the world'),
            ('M', 'proven', "the lab's world makers (ccops5.core.worlds, curriculum; sera.worlds builds on the same "
                            'generator, verified by independent review) knock as the judge models it: '
                            'one of the same 8 pushes of +-1.5 for 0.2 s at 0.6-1.2 s, on every throw of that '
                            'object; the best-fit side needs only that, not the rate (other knocks: assumed)')
            if knock == 'object' else
            ('M', 'assumed', 'a knock is drawn per throw, while the worlds knock per object (M-1 pending); no harm '
                             'measured so far'),
            ('N', 'measured' if numerator == 'laplace' else 'computed', n_why),
            ('U', 'measured', 'each rival best fit is a local maximum found from several starts: 0 flips in 956 '
                              'in-space rule-outs; the audit\'s superset fits not yet measured; not a certified '
                              'upper bound (U-1 pending)'),
            ('S', 'computed', 'every claimable law that does not contain the claim was ruled out, except the laws '
                              'with a free curve (cells), given U') if audit == 'universe-1' else
            ('S', 'assumed', 'only the laws in the space (and a grown claim\'s wide rivals) were ruled out'),
            ('F', 'assumed', 'a missing force lies in the span of the band basis'),
            ('Q', 'assumed', 'the band test (Decision 8) takes the quadratic approximation as one-sided: its '
                             'constrained best fit is never below the true one at any tested point and sign (not '
                             'certified); the band holds at the lattice points of the visited cells (L: not between '
                             'them)') if band == 'claim' else
            ('Q', 'assumed', 'the band uses the ellipsoid (quadratic) approximation'))


# Decision 11 (the author, 2026-09-27; docs/SCOPED_CLAIMS.md): a scoped claim says "the force is A, up to eps, at every
# reading in the visited cells". A rival then counts only through its members that differ from the claim's best fit
# by at least eps at some such reading (the set W): for a look-alike (a rival whose own best fit is within eps of the
# claim everywhere there), W's best likelihood is bounded by SCOPE_K penalized fits (likelihood.fit's `penalty`).
CLAIM = os.environ.get('CCOPS5_CLAIM', 'exact')
assert CLAIM in ('exact', 'scoped', 'functional'), CLAIM          # reviewer VD11 fix 6: an allowlist
FUNCTIONAL_CLAIM = ('the force is the claim\'s law with some strength, up to eps at every reading in the visited '
                    'cells, if the force lies in the span of the band basis; nothing is said beyond them (Decision 13)')
FUNCTIONAL_EMPTY = 0.1          # the functional code: the empty law, then n terms (0.1 + 0.45 + 0.3 + 0.1 + 0.05 = 1)
FUNCTIONAL_PARTS = {1: 0.45, 2: 0.3, 3: 0.1, 4: 0.05}      # Decision 15 (two terms were 0.45 before it)
FUNCTIONAL_MAX_PARTS = 4
SHAPE_PIVOT = 0.5               # reviewer VD14 fix 2: a shape replaces its largest hat only when that hat carries half its size
LENS_SHARE = 0.25               # Decision 14: of a free curve's code, the share for curves on a lens
DIM_SHARE = 0.25                # Decision 15: and for curves on a dimension SERA made
RAMP_WEIGHT = 1 / 1024          # Decision 16 (review 11): a ramp's share, fixed before data, on top of the 511/512 the
#                                 other terms can hold at most (no old term's or family's prior changes)


def _functional_term(term):
    """A term of SERA's own claim language and its code probability: a free curve (1/2: 1/3 per input, then the
    grid's weight; of that, 1 - LENS_SHARE on the whole input and LENS_SHARE on a lens, by grammar.lens_prior, which
    sums to 63/64) or one of its invented shapes (1/2: the e-LOND share 6 / (pi^2 n^2) of the library's n-th, on an
    input or a lens); 0 for anything else (the judge's dictionary is never SERA's language)."""
    if term[0] == 'ramp':                              # Decision 16: one strength times SERA's expression, its
        return RAMP_WEIGHT * grammar.dim_prior(term[1]) if grammar.is_ramp(term) else 0.0   # program's own code
    if term[0] in ('cell', 'shape') and (len(term) < 3 or type(term[2]) is not int):     # reviewer VD14: exact grids
        return 0.0
    if term[0] in ('cell', 'shape') and grammar.is_dim(term[1]) and set(grammar.dim(term[1])[0]) & {'lt', 'if'}:
        return 0.0                                     # reviewer VD14 fix 3: a switch in a dimension has no slope there
    if term in grammar.CELLS:                          # reviewer VD13 fix 4: exactly the grammar's cells, no aliases
        return 0.5 / 3 * grammar.CELL_K_WEIGHT[term[2]] * (1.0 - LENS_SHARE - DIM_SHARE)
    if (term[0] == 'cell' and len(term) == 3 and grammar.is_dim(term[1]) and term[2] in grammar.CELL_KS
            and isinstance(term[2], int)):                 # Decision 15: a free curve on a dimension it made
        return 0.5 * grammar.CELL_K_WEIGHT[term[2]] * DIM_SHARE * grammar.dim_prior(term[1])
    if (term[0] == 'cell' and len(term) == 3 and grammar.is_lens(term[1]) and term[2] in grammar.CELL_KS
            and isinstance(term[2], int)):                 # Decision 14: a free curve on a lens
        return 0.5 / 3 * grammar.CELL_K_WEIGHT[term[2]] * LENS_SHARE * grammar.lens_prior(term[1])
    if grammar.is_shape(term) and len(term) == 5 and grammar.claimable_term(term):
        return 0.5 * 6 / (math.pi ** 2 * term[3] ** 2)
    return 0.0


def functional_prior(family):
    """Decision 13: log pi_F(family), the prior of SERA's functional claims (the empty law, or n terms on different
    inputs: Decision 15 lets n grow to FUNCTIONAL_MAX_PARTS, the n-term laws sharing FUNCTIONAL_PARTS[n], times n! for
    the orders of an unordered family), fixed before the world's data (the library is: grammar.use_library). Its band
    is computed at delta * pi_F, so a claim chosen after seeing the data is paid for by a union bound. -inf when not
    claimable."""
    fam = grammar.canonical(family)
    if not fam:
        return math.log(FUNCTIONAL_EMPTY)
    ps = [_functional_term(t) for t in fam]
    if len(fam) > FUNCTIONAL_MAX_PARTS or not all(p > 0 for p in ps):
        return -math.inf
    bases = [grammar.base_input(t[1]) for t in fam]
    if len(set(bases)) < len(bases):                      # two terms on one input (or on a lens of it): one would
        return -math.inf                                   # span part of the other
    return (math.log(FUNCTIONAL_PARTS[len(fam)]) + sum(math.log(p) for p in ps)
            + math.lgamma(len(fam) + 1))


def functional_checks(family):
    """The 33-knot free curve on every input the claim uses, less what the claim already spans there, so the flexible
    fit has no two columns saying the same thing (the checker's other numerics need that): beside a K-knot cell of the
    claim, the 33-grid's hats between the cell's knots (the claim's hats and these span exactly the 33-knot curves: a
    hierarchical basis); beside an invented shape, every hat but the one its knots lean on most (the shape and these
    span them too); beside a 33-knot cell, nothing. As ('hats', input, 33, the excluded hats).
    Decision 14: a claim on a lens is constant beyond its window, so its input's whole 33-knot curve is checked too,
    less the inner hats whose whole support lies inside the window (their knots are lens knots: the lens's 33-knot
    curve spans them exactly)."""
    out = []
    fam = grammar.canonical(family)
    inputs = list(dict.fromkeys(t[1] for t in fam if t[0] in ('cell', 'shape', 'piece', 'ramp')))
    for inp in inputs:
        drop = set()
        for t in fam:
            if t[0] == 'ramp' and t[1] == inp:         # Decision 16 (review 11): the coordinate's line weighs the first
                drop.add(0)                            # hat -R, never 0: the ramp and the other 32 span the 33 hats
            elif t[0] == 'cell' and t[1] == inp:
                step = 32 // (t[2] - 1)
                drop |= {k for k in range(33) if k % step == 0}
            elif t[0] == 'shape' and t[1] == inp:
                w = np.interp(np.linspace(0, 1, 33), np.linspace(0, 1, t[2]), np.asarray(t[4], float))
                if float(np.max(np.abs(w))) >= SHAPE_PIVOT * float(np.max(np.abs(np.asarray(t[4], float)))) > 0:
                    drop.add(int(np.argmax(np.abs(w))))        # reviewer VD14 fix 2: only a shape that can stand in
        if len(drop) < 33:
            out.append(('hats', inp, 33, tuple(sorted(drop))))
    for inp in inputs:
        if not grammar.is_lens(inp):
            continue
        base = grammar.base_input(inp)
        if base in inputs:                                  # (never claimable: functional_prior refuses the pair)
            continue
        lo, hi = grammar.input_range(inp)
        g0, g1 = grammar.input_range(base)
        h = (g1 - g0) / 32
        inside = {k for k in range(1, 32) if g0 + (k - 1) * h >= lo - 1e-12 and g0 + (k + 1) * h <= hi + 1e-12}
        out.append(('hats', base, 33, tuple(sorted(inside))))
    return out
SCOPE_K = 4                     # candidate (reading, sign) pairs fitted exactly, ranked by the quadratic approximation
SCOPE_LAM = 1e3                 # the penalty's strength, in units of 1 / (a' Sigma a)


def scope_points(throws, scope):
    """Decision 11: the readings in the visited cells (where the band and a scoped claim speak), as rows (x, v, t)."""
    cells = set(scope.get('cells', ()))
    pts = [(float(t.x[n]), float(t.v[n]), n * paths.DT_OBS) for t in throws for n in range(paths.N_OBS)
           if cell_of(scope, float(t.x[n]), float(t.v[n])) in cells]
    return np.array(pts, float).reshape(-1, 3)


def force_columns(family, pts):
    """Each coefficient's force column of `family` at the points (the simulator's own terms, paths.term_t)."""
    kind, a, b = grammar.codes(family)
    cols = np.array([[paths.term_t(int(kind[j]), int(a[j]), int(b[j]), x, v, t, 1.0, 1.0) for j in range(len(kind))]
                     for x, v, t in pts], float).reshape(len(pts), len(kind))
    T = grammar.tie(family)
    return cols if T is None else cols @ T                          # Decision 12: tied coefficients' columns


def scope_context(ledger, family, eps):
    """What every scoped bound of one certificate shares: the scope points, the claim's best-fit force there and its
    coefficients, its inverse masses (the fits' pooled start), eps, and the look-alikes recorded so far."""
    fit = ledger.mle(family)
    nc = grammar.n_coef(family)
    pts = scope_points(ledger.throws, scope_of(ledger.throws))
    f_a = force_columns(family, pts) @ np.asarray(fit.coef[:nc], float) if (fit.ok and len(pts)) else None
    return dict(pts=pts, f_a=f_a, coef_a=tuple(float(c) for c in fit.coef[:nc]), mu=fit.mu, eps=float(eps),
                lookalikes={})


def scoped_sup(ledger, fam, fit, sc):
    """Decision 11 (docs/SCOPED_CLAIMS.md §3): an upper bound on `fam`'s likelihood over the coefficients whose force
    differs from the claim's best fit by at least eps at some scope point (the set W). Returns (bound, record).
    record is None when W already holds the fit (its force differs by eps somewhere: the plain rule applies, bound =
    its likelihood). For a look-alike: the largest likelihood of the SCOPE_K penalized fits, each at a (reading, sign)
    ranked by the quadratic approximation (premise T), and each never below the best likelihood with that reading's
    force pushed out to eps (the penalized-optimum lemma); +inf when it cannot be bounded (fail closed)."""
    pts, f_a, eps = sc['pts'], sc['f_a'], sc['eps']
    if f_a is None or not len(pts) or not _usable(fit):
        return fit.loglik, None
    nc = grammar.n_coef(fam)
    phi = force_columns(fam, pts)
    coef = np.asarray(fit.coef[:nc], float)
    diff = phi @ coef - f_a
    gap = float(np.max(np.abs(diff)))
    if not math.isfinite(gap) or gap >= eps:
        return fit.loglik, None
    rec = dict(gap=gap, coef=tuple(float(c) for c in coef))
    sig = np.asarray(fit.cov, float)[:nc, :nc]
    if not np.all(np.isfinite(sig)):
        return math.inf, dict(rec, why='the fit has no covariance')
    var = np.einsum('ij,jk,ik->i', phi, sig, phi)
    cand = sorted(((eps - s * diff[i]) ** 2 / (2.0 * var[i]), i, s) for s in (1.0, -1.0) for i in range(len(pts))
                  if math.isfinite(var[i]) and var[i] > 1e-300)[:SCOPE_K]
    if not cand:
        return math.inf, dict(rec, why='no direction the data sees')
    model, best = model_of(fam), -math.inf
    for _, i, s in cand:
        a_vec = s * phi[i]
        b = s * float(f_a[i]) + eps
        asa = float(a_vec @ sig @ a_vec)
        if not (math.isfinite(asa) and asa > 0):
            return math.inf, dict(rec, why='no direction the data sees')
        c0 = coef + sig @ a_vec * ((b - float(a_vec @ coef)) / asa)       # the quadratic approximation's optimum
        start = L.Post(np.concatenate([c0, [fit.mu[o] for o in fit.order]]), np.eye(nc + len(fit.order)),
                       list(fit.order))
        f = L.sup_fit(model, ledger.throws, ledger.sigma, sc['mu'], (start,), penalty=(a_vec, b, SCOPE_LAM / asa))
        if not _usable(f):
            return math.inf, dict(rec, why='a constrained fit failed')
        best = max(best, float(f.loglik))
    i, s = cand[0][1], cand[0][2]
    return best, dict(rec, point=tuple(float(x) for x in pts[i]), sign=float(s), bound=best)


def scoped_evidence(ledger, fam, claim, q_a, sc, fit=None):
    """log E of the claim against `fam`'s members in W (scoped_sup), recording the look-alike in sc; None when `fam`
    is no look-alike (the plain log E stands). `fit`: fam's best fit when the caller has it (else the audit's)."""
    fam = grammar.canonical(fam)
    key = ('scoped', fam, grammar.canonical(claim))
    if key not in ledger._audit:
        f = fit if fit is not None else audit_fit(ledger, fam, sc['mu'], claim)
        ledger._audit[key] = scoped_sup(ledger, fam, f, sc)
    bound, rec = ledger._audit[key]
    if rec is None:
        return None
    sc['lookalikes'][fam] = dict(rec, evidence=q_a - bound, coef_claim=sc['coef_a'])
    return q_a - bound


def ramp_outside(throws, family):
    """Decision 16 (review 11): the ramps of a family whose expression is not finite, or leaves its range -R .. R, at
    any reading of any throw (scope or not; exact values, grammar.dim_eval on the unrounded readings). A ramp says
    "strength times this expression" only where the expression is what the clip passes through."""
    ramps = [t for t in family if t[0] == 'ramp']
    if not ramps or not throws:
        return [t for t in ramps if not throws]
    x = np.concatenate([np.asarray(t.x, float) for t in throws])
    v = np.concatenate([np.asarray(t.v, float) for t in throws])
    tt = np.concatenate([np.arange(len(t.x)) * paths.DT_OBS for t in throws])
    out = []
    for t in ramps:
        lo, hi = grammar.input_range(t[1])
        with np.errstate(all='ignore'):
            u = grammar.dim_eval(t[1], x, v, tt)
        if not (np.all(np.isfinite(u)) and np.all(u >= lo) and np.all(u <= hi)):
            out.append(t)
    return out


def certify_functional(ledger, family, eps, alpha=1e-3, delta=1e-3, audit=None):
    """Decision 13 (plan revision 6; the author: no predefined set of formulas - SERA claims laws in its own language):
    "the force is this law with some strength, up to eps at every reading in the visited cells" - if the force lies in
    the band basis's span (premise F; outside it there is no coverage guarantee). Accepted when the law does not
    misfit (the adequacy test: a veto only, never an error bound) and the band - the claim's own forecast as the
    reference (Decision 8's claim test; reviewer VD13 fix 2), at delta * pi_F(law), evaluated at every visited reading for
    every law (fix 3) - is at most eps. It names no rivals. The library must be the one the ledger was made under."""
    audit = audit or AUDIT
    family = grammar.canonical(family)
    lp = functional_prior(family)
    reasons = []
    scope = dict(scope_of(ledger.throws), band_at='visited readings', claim=FUNCTIONAL_CLAIM)
    band, adequate = None, None
    if lp == -math.inf:
        reasons.append('this is not a law in the language of the claim')
    elif BAND != 'claim':
        reasons.append("a functional claim needs the claim's own forecast as the band's reference (CCOPS5_BAND=claim)")
    elif getattr(ledger, 'library', '') != grammar.library_digest():
        reasons.append('the library of invented shapes changed during this world')
    elif ramp_outside(ledger.throws, family):
        reasons.append('a strength times this expression is not what was read: the expression leaves its range '
                       '(or is not finite) at a reading')
    else:
        adequate = adequacy(ledger, family)
        if adequate >= math.log(grammar.ADEQUACY_THRESHOLD_SPACE / alpha):
            reasons.append('something else is here: the law misfits more objects than bumps explain')
        else:
            checks = functional_checks(family)
            base = {k: v for k, v in scope.items() if k not in ('band_at', 'claim')}
            delta_eff = delta * math.exp(lp)
            band = grown_band(ledger.throws, family, ledger.sigma, base, delta_eff, q_ref=ledger.q_claim(family),
                              checks=checks)                    # at every visited reading, for every law
            if not band <= eps:
                reasons.append(f'something else could be as large as {band:.3g} > eps {eps:g}')
    inventions = tuple(sorted({x for f in ledger.families for x in f if x not in grammar.IDEAS}, key=grammar._key))
    return Certificate(family, alpha, delta, eps, len(ledger.families), inventions, digest(ledger.throws), {}, {},
                       band, adequate, scope, not reasons, tuple(reasons), lp, NUMERATOR, audit,
                       premise_ledger(audit, NUMERATOR, L.KNOCK, BAND, 'functional'), L.KNOCK, BAND, 'functional',
                       None, grammar.library_digest())


def certify(ledger, family, eps, alpha=1e-3, delta=1e-3, audit=None, claim=None):
    audit = audit or AUDIT
    claim_kind = claim or CLAIM
    if claim_kind == 'functional':                          # Decision 13
        return certify_functional(ledger, family, eps, alpha, delta, audit)
    family = grammar.canonical(family)
    space = ledger.families
    n = ledger.n_space
    thr = grammar.log_threshold(family, alpha)                 # D9 (was log(n / alpha) = 11.1 for the base space)
    adequacy_thr = math.log(grammar.ADEQUACY_THRESHOLD_SPACE / alpha)   # unchanged: misfit is never judged laxer
    reasons = []
    # Rivals in order of how well they predicted. A rival whose own prequential score is within the threshold
    # cannot be ruled out: its best fit scores at least that well (a marginal likelihood never exceeds the
    # maximum), so log E(A:B) <= Q_A - Q_B < threshold. That screen fails a claim without fitting anything.
    candidates = sorted((b for b in space if b != family and not grammar.contains(b, family)),
                        key=lambda b: -ledger.Q[b])
    rivals, weak = {}, []
    sc = scope_context(ledger, family, eps) if claim_kind == 'scoped' else None    # Decision 11
    for b in candidates:
        if sc is None and ledger.Q[b] > ledger.Q[family] - thr:    # the screen holds for exact claims only: a scoped
            rivals[b] = ledger.Q[family] - ledger.Q[b]              # bound over W can be below Q_B
            weak.append(b)
            break
        rivals[b] = ledger.log_e(family, b)
        if rivals[b] < thr and sc is not None:
            e = scoped_evidence(ledger, b, family, ledger.q_claim(family), sc, fit=ledger.mle(b))
            if e is not None:
                rivals[b] = e
        if rivals[b] < thr:
            weak.append(b)
            break
    if weak:
        reasons.append(f'a rival family is not ruled out: {grammar.name(weak[0])}')
    nested, band, adequate = {}, None, None
    scope = scope_of(ledger.throws)
    if not weak:
        adequate = adequacy(ledger, family)
        if adequate >= adequacy_thr:
            reasons.append('something else is here: the law misfits more objects than bumps explain')
    if not reasons:
        for idea in sorted({x for f in space for x in f}, key=grammar._key):
            if idea in family or grammar.canonical(family + (idea,)) not in space:
                continue
            nested[idea] = _nested_interval(ledger, family, idea, delta / n)
        for idea in curve_checks(family):                   # truth-v2, independent review condition 2
            nested[idea] = _nested_interval(ledger, family, idea, delta / n)
        bad = [i for i, iv in nested.items() if not zero_inside(iv)]
        if bad:
            reasons.append(f'{len(bad)} extra terms needed (their bounds exclude 0)')
        else:
            size = grown_band if curve_checks(family) else band_of      # truth-v2 T1: a grown claim's band holds
            band = size(ledger.throws, family, ledger.sigma, scope, delta / n,   # its finest cells too; D8: the
                        q_ref=ledger.q_claim(family) if BAND == 'claim' else None)   # claim's own forecast
            if size is grown_band:                  # independent review T1-a: say where the bound holds - at the readings in
                scope = dict(scope, band_at='visited readings')         # the visited cells, not a lattice or knots
            if not band <= eps:
                reasons.append(f'something else could be as large as {band:.3g} > eps {eps:g}')
    if audit == 'universe-1':                               # truth-v3 Decision 9: every claimable law (but cells);
        scope = dict(scope, not_audited=NOT_AUDITED)        # it holds truth-v2's T2 wide rivals, so replaces them
    if sc is not None:                                      # Decision 11: what a scoped claim says
        scope = dict(scope, claim=SCOPED_CLAIM)
    if not reasons and audit == 'universe-1':
        wide, weak_wide, why = universe_audit(ledger, family, thr, scoped=sc)
        rivals.update(wide)
        if why == 'failed':
            reasons.append(f'a rival fit failed, so it is not ruled out: {grammar.name(weak_wide)}')
        elif weak_wide is not None:
            reasons.append(f'a rival family is not ruled out: {grammar.name(weak_wide)}')
    elif not reasons and curve_checks(family):              # truth-v2 T2, last because it is the costliest part
        wide, weak_wide, why = wide_rivals(ledger, family, thr, scoped=sc)
        rivals.update(wide)
        if why == 'failed':
            reasons.append(f'a rival fit failed, so it is not ruled out: {grammar.name(weak_wide)}')
        elif weak_wide is not None:
            reasons.append(f'a rival family is not ruled out: {grammar.name(weak_wide)}')
    accepted = not reasons
    inventions = tuple(sorted({x for f in space for x in f if x not in grammar.IDEAS}, key=grammar._key))   # any open term in play
    return Certificate(family, alpha, delta, eps, n, inventions, digest(ledger.throws), rivals, nested, band,
                       adequate, scope, accepted, tuple(reasons), grammar.log_prior(family), NUMERATOR, audit,
                       premise_ledger(audit, NUMERATOR, L.KNOCK, BAND, claim_kind), L.KNOCK, BAND, claim_kind,
                       None if sc is None else dict(sc['lookalikes']), grammar.library_digest())


def something_else(ledger, family, alpha=1e-3):
    """The alarm: the flexible family (family + smooth basis) predicts the throws better than the family's
    best fit by more than chance allows. Returns (fired, log E)."""
    family = grammar.canonical(family)
    if not ledger.throws:
        return False, 0.0
    scope = scope_of(ledger.throws)
    model = model_of(family, extra_basis=True, scope=scope)
    q_f, _ = prequential(model, ledger.throws, ledger.sigma)
    log_e = max(q_f - ledger.mle(family).loglik, adequacy(ledger, family))
    return log_e >= math.log(ledger.n_space / alpha), log_e


@dataclasses.dataclass(frozen=True)
class Claim:
    family: tuple
    certificate: Certificate
    sure: bool


class Library:
    """Claims kept for life. A claim is sure only if the checker accepts its certificate."""

    def __init__(self, sigma):
        self.sigma = sigma
        self._claims = []

    @property
    def claims(self):
        return tuple(self._claims)

    def record(self, certificate, throws):
        from . import checker
        ok, _ = checker.check(certificate, throws, self.sigma)
        if ok:
            self._claims.append(Claim(tuple(certificate.family), certificate, True))
        return ok
