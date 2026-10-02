"""The idea space S_K: which families of force terms the mind can form.

A term is either a school idea (input, shape), or a term the mind can invent when its ideas are not enough:
  ('product', shape_of_x, shape_of_v)   e.g. x*v
  ('power', input, p)                   |s|^p sign(s), p in 0.5 / 1.5 / 2.5
  ('drive', 'sin' or 'cos', omega)      a force that depends on time, like a hidden motor
A family is a sorted tuple of terms (at most two), plus the known hand.
S_K = the empty family, every single term, and every pair, over the terms in play. The school's grammar alone
gives 67 families; with every invention term there are 1,486 (the "universe"). The checker enumerates the space
itself, so no certificate can leave a rival out.

Decision D9 (approved 2026-09-24): a claim's threshold is log(1 / (alpha * pi(claim))). pi is fixed before any data:
0.9 spread evenly over the 67 base families, 0.1 over the open grammar (one invented term from OPEN_TERMS, alone or
with one base idea, weighted by its description length). The library and the gut only change the search order,
never pi, so the chance of ever being sure and wrong stays below alpha over the whole open grammar.

Decision 12 (plan revision 6, policy CCOPS5_SHAPES; 'off' by default = everything above, unchanged): SERA's own
invented shapes. When SERA proves a free curve (a K-knot cell), it may compress it into a shape of its own: the curve's
knot values, fixed, times one strength. The term ('shape', input, K, n, knots) is the n-th shape SERA invented; its
columns are the cell's hats combined by the fixed knots (a tied cell: K simulator codes, one coefficient, `tie`).
Under 'library' the cells' share 0.03 becomes 0.02 and the shapes get 0.01, the n-th invention n's part 6/(pi^2 n^2)
of it (the e-LOND sequence: the shares sum to 1 over every invention SERA will ever make), so Kraft still holds. The
shapes a claim may use are the library's (`use_library`), fixed before a world begins: which curve became the n-th
shape depends on earlier worlds only, so its prior is fixed before this world's data (premise P) - the same argument
as a prior fixed before any data, applied world by world.
"""
import hashlib
import itertools
import math
import os

import numpy as np

from .. import puzzles as P

IDEAS = tuple(P.IDEAS)
INPUT_CODE = {'position': 0, 'speed': 1, 'nothing': 2}
SHAPE_CODE = {'straight': 0, 'growing': 1, 'steps': 2, 'cubic': 3, 'wave': 4, 'steady': 0}
SHAPES = ('straight', 'growing', 'steps', 'cubic', 'wave')
PRODUCTS = tuple(('product', a, b) for a in SHAPES for b in SHAPES)
POWERS = tuple(('power', i, p) for i in ('position', 'speed') for p in (0.5, 1.5, 2.5))
DRIVES = tuple(('drive', f, w) for f in ('sin', 'cos') for w in (1.0, 2.0, 3.0, 4.0, 6.0, 8.0))
INVENTIONS = PRODUCTS + POWERS + DRIVES
TERMS = IDEAS + INVENTIONS


def code(term):
    """(kind, a, b) for the path simulator (one coefficient; a cell has K, see term_codes)."""
    if term[0] == 'ramp':                       # Decision 16: kind 10, one direct column (paths.term_t)
        if not is_ramp(term):
            raise ValueError(f'not a ramp: {term!r}')
        return 10, input_code(term[1]), 0
    if term[0] == 'piece':
        op = PIECE_OPS.index(term[2])
        return 8, CELL_INPUTS.index(term[1]), op * 16 + (0 if op == 0 else PIECE_C.index(term[3]))
    if term[0] == 'pprod':
        return 9, PART_NAMES.index(term[1]), PART_NAMES.index(term[2])
    if term[0] == 'product':
        return 4, SHAPE_CODE[term[1]], SHAPE_CODE[term[2]]
    if term[0] == 'power':
        return 5, INPUT_CODE[term[1]], int(round(term[2] * 10))
    if term[0] == 'drive':
        return 6, 0 if term[1] == 'sin' else 1, int(round(term[2] * 10))
    return 0, INPUT_CODE[term[0]], SHAPE_CODE[term[1]]


def _key(term):
    """A total order on terms: the grammar's own order, then open terms by their repr (never set order)."""
    return (TERMS.index(term), '') if term in TERMS else (len(TERMS), repr(term))


def canonical(family):
    return tuple(sorted(set(family), key=_key))


P_GRID = tuple(round(0.1 * k, 1) for k in range(1, 41))          # exponents 0.1 .. 4.0
W_GRID = tuple(round(0.1 * k, 1) for k in range(1, 81))          # frequencies 0.1 .. 8.0
OPEN_TERMS = (PRODUCTS
              + tuple(('power', i, p) for i in ('position', 'speed') for p in P_GRID if p not in (1.0, 2.0, 3.0))
              + tuple(('drive', f, w) for f in ('sin', 'cos') for w in W_GRID))
# truth-v2 (B4, docs/B4_GROWTH.md): grown terms, fixed before any data. They extend what the judge can claim; truth-v1's
# OPEN_TERMS list is unchanged (SERA's imagination reads it), and the prior below covers both lists.
CELL_INPUTS = ('position', 'speed', 'time')
CELL_KS = (9, 17, 33)
CELL_K_WEIGHT = {9: 0.5, 17: 0.25, 33: 0.25}
PIECE_OPS = ('abs', 'tanh', 'bell')
PIECE_C = (0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0)
PART_NAMES = SHAPES + ('abs',) + tuple(f'tanh{c:g}' for c in PIECE_C) + tuple(f'bell{c:g}' for c in PIECE_C)
CELLS = tuple(('cell', i, K) for i in CELL_INPUTS for K in CELL_KS)
PIECES = tuple(('piece', i, 'abs', 0.0) for i in CELL_INPUTS) + tuple(
    ('piece', i, op, c) for i in CELL_INPUTS for op in ('tanh', 'bell') for c in PIECE_C)
PPRODS = tuple(('pprod', a, b) for a in PART_NAMES for b in PART_NAMES if not (a in SHAPES and b in SHAPES))
GROWN_TERMS = CELLS + PIECES + PPRODS
SHAPES_POLICY = os.environ.get('CCOPS5_SHAPES', 'off')              # Decision 12: 'off' | 'library'
assert SHAPES_POLICY in ('off', 'library'), SHAPES_POLICY
SHAPE_WEIGHT = 0.01 if SHAPES_POLICY == 'library' else 0.0
V1_OPEN_WEIGHT, CELL_WEIGHT, PIECE_WEIGHT = 0.05, 0.03 - SHAPE_WEIGHT, 0.02   # with BASE_WEIGHT 0.9: exactly 1
LIBRARY = ()                    # Decision 12: SERA's invented shapes, in the order it invented them (use_library)


def is_shape(term):
    return term[0] == 'shape'


# Decision 14 (plan revision 6.2; the author: "it can improve its own drawing and get more abilities to perceive"): a
# LENS looks at one input 2^j times closer (j = 1 .. 6), at the window of width W / 2^j centred at lo + m W / 2^(j+1)
# (W the input's whole range lo .. hi; m = 0 .. 2^(j+1), so the centres lie on a lattice of half-windows and the
# window never leaves the input's range by more than half its width). Named '<input>@<j>:<m>'. A curve on a lens has
# its K knots across the window and is constant beyond it, like every cell beyond its range.
LENS_J = (1, 2, 3, 4, 5, 6)


def lens(inp):
    """(base input, j, m) of an input or a lens; (inp, 0, 0) for a whole input. Raises ValueError if malformed."""
    if isinstance(inp, str) and inp in CELL_INPUTS:
        return inp, 0, 0
    if not isinstance(inp, str) or inp.count('@') != 1:
        raise ValueError(f'not an input: {inp!r}')
    base, rest = inp.split('@')
    if base not in CELL_INPUTS or rest.count(':') != 1:
        raise ValueError(f'not an input: {inp!r}')
    js, ms = rest.split(':')
    if not (js.isdigit() and ms.isdigit()):
        raise ValueError(f'not an input: {inp!r}')
    j, m = int(js), int(ms)
    if j not in LENS_J or not 0 <= m <= 2 ** (j + 1) or lens_name(base, j, m) != inp:
        raise ValueError(f'not an input: {inp!r}')
    return base, j, m


def lens_name(base, j, m):
    return f'{base}@{j}:{m}'


# Decision 15 (plan revision 6.3; the author: "give SERA more dimensions of perception, let it improve the number of
# dimensions it functions and thinks in"): a DIMENSION is a new input SERA made - a program of its own language over
# what it measures, u = e(position, speed, time), written in postfix with the tokens below - looked at over -R .. R,
# R = 2^(r - 4), r in DIM_R. Named 'dim:<token>.<token>...@<r>' (e.g. 'dim:x.v.mul@6': position times speed, over
# -4 .. 4). A curve on it is a function of that combination; the simulator runs the program with its exact slopes.
DIM_TOKENS = ('x', 'v', 't', '0', '1', 'add', 'sub', 'mul', 'lt', 'if')        # codes 1 .. 10 (0 ends the program)
DIM_ARITY = {'x': 0, 'v': 0, 't': 0, '0': 0, '1': 0, 'add': 2, 'sub': 2, 'mul': 2, 'lt': 2, 'if': 3}
DIM_R = tuple(range(2, 11))                     # ranges 0.25 .. 64
DIM_MAX = 14                                    # tokens (4 bits each, below the range's 4 bits and the flag)


def dim(inp):
    """(tokens, r) of a dimension. Raises ValueError unless it is a well-formed program (every token known, the stack
    one deep at its end, at least one measured input) with a known range, named canonically."""
    if not isinstance(inp, str) or not inp.startswith('dim:') or inp.count('@') != 1:
        raise ValueError(f'not a dimension: {inp!r}')
    body, rs = inp[4:].split('@')
    toks = tuple(body.split('.'))
    if not rs.isdigit() or int(rs) not in DIM_R or not 1 <= len(toks) <= DIM_MAX or \
            any(t not in DIM_TOKENS for t in toks) or not any(t in ('x', 'v', 't') for t in toks):
        raise ValueError(f'not a dimension: {inp!r}')
    depth = 0
    for t in toks:
        depth += 1 - DIM_ARITY[t]
        if depth < 1:
            raise ValueError(f'not a dimension: {inp!r}')
    if depth != 1 or dim_name(toks, int(rs)) != inp:
        raise ValueError(f'not a dimension: {inp!r}')
    return toks, int(rs)


# Decision 16 (the author, 2026-10-01; review 11): a RAMP ('ramp', dimension, 9) is one strength times SERA's own
# expression, clipped at its dimension's range: c * clip(e(x, v, t), -R, R). Functional claims only; its dimension is
# a smooth program (no lt, no if: they have no slope), and K is fixed (it names the equivalent 9-knot drawing, a
# coordinate line, which every grid holds exactly; it adds no accuracy and no prior mass).
RAMP_K = 9
RAMP_TOKENS = frozenset(('x', 'v', 't', '0', '1', 'add', 'sub', 'mul'))


def is_ramp(term):
    """The exact schema of a ramp: ('ramp', a smooth dimension, RAMP_K), K an int, nothing more."""
    return (isinstance(term, tuple) and len(term) == 3 and term[0] == 'ramp' and isinstance(term[1], str)
            and is_dim(term[1]) and set(dim(term[1])[0]) <= RAMP_TOKENS and type(term[2]) is int
            and term[2] == RAMP_K)


def dim_name(tokens, r):
    return f"dim:{'.'.join(tokens)}@{r}"


def is_dim(inp):
    try:
        dim(inp)
        return True
    except ValueError:
        return False


def dim_prior(inp):
    """Decision 15: a dimension's code probability, fixed before any data: its tokens and an end mark, each one of
    11 (11^-(n+1): every end-marked sequence, so it sums to at most 1), then its range, one of the 9 in DIM_R."""
    toks, r = dim(inp)
    return 11.0 ** -(len(toks) + 1) / len(DIM_R)


def dim_eval(inp, x, v, t):
    """A dimension's value at arrays x, v, t (numpy; the same program as paths._dim)."""
    toks, _ = dim(inp)
    st = []
    for tok in toks:
        if tok in ('x', 'v', 't', '0', '1'):
            st.append({'x': x, 'v': v, 't': t, '0': np.zeros_like(x), '1': np.ones_like(x)}[tok] * np.ones_like(x))
        elif tok == 'if':
            b, a, c = st.pop(), st.pop(), st.pop()
            st.append(np.where(c > 0.5, a, b))
        else:
            q, p = st.pop(), st.pop()
            st.append(p + q if tok == 'add' else p - q if tok == 'sub' else p * q if tok == 'mul'
                      else (p < q).astype(float))
    return st[0]


def dim_words(inp):
    """A dimension in words: its program in infix, over position, speed and time."""
    toks, _ = dim(inp)
    st = []
    for tok in toks:
        if DIM_ARITY[tok] == 0:
            st.append({'x': 'position', 'v': 'speed', 't': 'time'}.get(tok, tok))
        elif tok == 'if':
            b, a, c = st.pop(), st.pop(), st.pop()
            st.append(f'({a} if {c} else {b})')
        else:
            q, p = st.pop(), st.pop()
            st.append(f"({p} {dict(add='+', sub='-', mul='x', lt='<')[tok]} {q})")
    return st[0]


def is_input(inp):
    try:
        lens(inp)
        return True
    except ValueError:
        return is_dim(inp)


def is_lens(inp):
    try:
        return lens(inp)[1] > 0
    except ValueError:
        return False


def base_input(inp):
    """The measured input a channel looks at: a lens's input; a dimension is its own."""
    return inp if is_dim(inp) else lens(inp)[0]


def input_code(inp):
    """The simulator's input code (paths._input, paths._lens): the base input's index, plus 3 (j + 8 m) for a lens;
    for a dimension, paths.DIM_FLAG, its range's 4 bits at bit 56 and its tokens 4 bits each from bit 0."""
    if is_dim(inp):
        from . import paths
        toks, r = dim(inp)
        code = paths.DIM_FLAG | (r << 56)
        for i, tok in enumerate(toks):
            code |= (DIM_TOKENS.index(tok) + 1) << (4 * i)
        return int(code)
    base, j, m = lens(inp)
    return CELL_INPUTS.index(base) + (3 * (j + 8 * m) if j else 0)


def input_range(inp):
    """The knot range (lo, hi) of an input, a lens or a dimension (the same numbers as paths._lens)."""
    from . import paths
    if is_dim(inp):
        R = 2.0 ** (dim(inp)[1] - 4)
        return -R, R
    base, j, m = lens(inp)
    i = CELL_INPUTS.index(base)
    lo, hi = float(paths.CELL_LO[i]), float(paths.CELL_HI[i])
    if not j:
        return lo, hi
    half = (hi - lo) / 2.0 ** (j + 1)
    c = lo + m * half
    return c - half, c + half


def lens_origin(base, j):
    """The m whose window is centred on the input's own zero (every input's range holds 0 on the lattice)."""
    from . import paths
    i = CELL_INPUTS.index(base)
    lo, hi = float(paths.CELL_LO[i]), float(paths.CELL_HI[i])
    return int(round(-lo / ((hi - lo) / 2.0 ** (j + 1))))


def lens_prior(inp):
    """Decision 14: a lens's code probability, fixed before any data: 2^-j for its zoom (j = 1 .. 6: 63/64 in all),
    then half for the window centred on the input's own zero and half shared by the other 2^(j+1) centres."""
    base, j, m = lens(inp)
    if not j:
        return 0.0
    return 2.0 ** -j * (0.5 if m == lens_origin(base, j) else 0.5 / 2 ** (j + 1))


def describe_input(inp):
    """An input in words: 'speed', 'speed 16x closer around 0', or a dimension's program '(position x speed)'."""
    if is_dim(inp):
        return dim_words(inp)
    base, j, m = lens(inp)
    if not j:
        return base
    lo, hi = input_range(inp)
    return f'{base} {2 ** j}x closer around {0.5 * (lo + hi):g}'


def shape_term(inp, K, n, knots):
    """The n-th invented shape (n = 1, 2, ...): input (or lens), grid, and its K knot values (floats, fixed)."""
    assert is_input(inp) and K in CELL_KS and len(knots) == K and n >= 1
    return ('shape', inp, int(K), int(n), tuple(float(k) for k in knots))


SHAPE_MIN = 1e-6                # a library shape's largest knot at least this (a zero shape spans nothing)


def use_library(shapes):
    """Fix the library for the next world (never during one): the n-th entry must be shape n."""
    global LIBRARY
    shapes = tuple(shapes)
    for i, s in enumerate(shapes):                  # reviewer VD13 fix 4: the exact schema, validated at the boundary
        if not (is_shape(s) and len(s) == 5 and is_input(s[1]) and type(s[2]) is int and s[2] in CELL_KS
                and type(s[3]) is int and s[3] == i + 1 and isinstance(s[4], tuple) and len(s[4]) == s[2]
                and all(isinstance(k, float) and math.isfinite(k) for k in s[4])
                and max(abs(k) for k in s[4]) >= SHAPE_MIN):          # reviewer VD14 fix 2: no zero shapes; raised,
            raise AssertionError(f'library entry {i + 1} is malformed')   # not asserted (python -O keeps it)
    LIBRARY = shapes


def library_digest(shapes=None):
    """A digest of the library (the certificate records the one it was made under; the checker compares)."""
    shapes = LIBRARY if shapes is None else shapes
    return hashlib.sha256(repr(tuple(shapes)).encode()).hexdigest()[:16] if shapes else ''


def _in_library(term):
    return SHAPES_POLICY == 'library' and 1 <= term[3] <= len(LIBRARY) and LIBRARY[term[3] - 1] == term


def _grown_term_log_prior(term):
    """Log prior of one grown term within the whole grammar (its class share times its choice among the class)."""
    if term[0] == 'shape':                                         # Decision 12: e-LOND shares of the shapes' mass
        return math.log(SHAPE_WEIGHT) + math.log(6 / (math.pi ** 2 * term[3] ** 2))
    if term[0] == 'cell':
        return math.log(CELL_WEIGHT) + math.log(1 / 3) + math.log(CELL_K_WEIGHT[term[2]])
    if term[0] == 'piece':
        return (math.log(PIECE_WEIGHT) + math.log(0.5) + math.log(1 / 3) + math.log(1 / 3)
                + (0.0 if term[2] == 'abs' else math.log(1 / len(PIECE_C))))
    return math.log(PIECE_WEIGHT) + math.log(0.5) + math.log(1 / len(PPRODS))


def n_coef(family):
    """Coefficients a family's model has: K for a K-knot cell, 1 for every other term (an invented shape too, and a
    ramp: Decision 16, one strength); a band's check hats (Decision 13, 'hats') one per hat it keeps."""
    return sum(t[2] if t[0] == 'cell' else len(hat_indices(t)) if t[0] == 'hats' else 1 for t in family)


def hat_indices(term):
    """Decision 13: the hats a band's check ('hats', input, K, excluded) keeps (every hat of the K grid but those
    excluded)."""
    return [k for k in range(term[2]) if k not in set(term[3])]


def tie(family):
    """Decision 12: the matrix taking the family's coefficients to its simulator codes' coefficients (codes x
    coefficients), or None when every code has its own coefficient (no invented shape: the model is unchanged)."""
    if not any(is_shape(t) for t in family):
        return None
    blocks = []
    for t in family:
        if is_shape(t):
            blocks.append(np.asarray(t[4], float).reshape(-1, 1))
        else:
            n = n_coef((t,))
            blocks.append(np.eye(n))
    rows = sum(b.shape[0] for b in blocks)
    T = np.zeros((rows, sum(b.shape[1] for b in blocks)))
    r = c = 0
    for b in blocks:
        T[r:r + b.shape[0], c:c + b.shape[1]] = b
        r, c = r + b.shape[0], c + b.shape[1]
    return T


def coef_slice(family, term):
    """The coefficient positions of `term` in `family`'s model (canonical order)."""
    fam = canonical(family)
    start = n_coef(fam[:fam.index(term)])
    return slice(start, start + n_coef((term,)))


_OPEN_SET = frozenset(OPEN_TERMS + GROWN_TERMS)


def claimable_term(term):
    """An invented term the grammar knows: truth-v1's, a grown one, or (Decision 12) a shape of the library."""
    return term in _OPEN_SET or (is_shape(term) and _in_library(term))


BASE_WEIGHT = 0.9
_N_POWERS = sum(1 for t in OPEN_TERMS if t[0] == 'power') // 2
_N_DRIVES = sum(1 for t in OPEN_TERMS if t[0] == 'drive') // 2


def _open_term_log_prior(term):
    """Description-length weight of one invented term: operator (1 of 3), then its parts."""
    if term[0] == 'product':
        return math.log(1 / 3) + math.log(1 / len(PRODUCTS))
    if term[0] == 'power':
        return math.log(1 / 3) + math.log(1 / 2) + math.log(1 / _N_POWERS)
    return math.log(1 / 3) + math.log(1 / 2) + math.log(1 / _N_DRIVES)


def log_prior(family):
    """log pi(family) under D9 as extended by truth-v2 (base 0.9 unchanged; truth-v1 open terms 0.05, i.e. their
    log prior is truth-v1's minus log 2; cells 0.03; pieces and piece products 0.02); -inf if it cannot be claimed."""
    fam = canonical(family)
    if len(fam) <= 2 and all(t in IDEAS for t in fam):
        return math.log(BASE_WEIGHT / _N_BASE)
    opens = [t for t in fam if t not in IDEAS]
    bases = [t for t in fam if t in IDEAS]
    if len(opens) != 1 or len(bases) > 1 or not claimable_term(opens[0]):
        return -math.inf
    term = opens[0]
    lp = math.log(V1_OPEN_WEIGHT) + _open_term_log_prior(term) if term[0] in ('product', 'power', 'drive') \
        else _grown_term_log_prior(term)
    return math.log(0.5) + (math.log(1 / len(IDEAS)) if bases else 0.0) + lp


def log_threshold(family, alpha):
    """The evidence a claim of `family` needs against every rival (D9)."""
    lp = log_prior(family)
    return math.inf if lp == -math.inf else -math.log(alpha) - lp


def collinear(family):
    """truth-v2 (V3): a cell together with a term its hats already span exactly (a constant, the line of its own
    input, |s| of its own input: 0 is a knot of every grid) makes the family's columns dependent; such families are
    left out of the space (they add nothing and would block each other forever)."""
    cells = [t for t in family if t[0] == 'cell']
    for c in cells:
        for t in family:
            if t == ('nothing', 'steady'):
                return True
            if t == (c[1], 'straight'):
                return True
            if t[0] == 'piece' and t[1] == c[1] and t[2] == 'abs':
                return True
            if t[0] == 'cell' and t != c and t[1] == c[1]:
                return True
            if is_shape(t) and t[1] == c[1] and c[2] >= t[2]:   # Decision 12: a cell whose grid holds the shape's
                return True                                     # spans it (reviewer VD13: not a coarser one)
            if t[0] == 'ramp' and t[1] == c[1]:                 # Decision 16: every grid holds its coordinate's
                return True                                     # line (S11: any K)
    return False

def space(max_terms=2, inventions=()):
    """The families over the school's ideas plus the given invented terms."""
    terms = IDEAS + tuple(sorted({t for t in inventions if claimable_term(t)}, key=_key))
    fams = [()]
    for n in range(1, max_terms + 1):
        fams += [canonical(c) for c in itertools.combinations(terms, n) if not collinear(c)]
    return fams


UNIVERSE = len(space(inventions=INVENTIONS))       # 1,486 families (before D9 the size paid when inventing)
_N_BASE = len(space())                              # 67
ADEQUACY_THRESHOLD_SPACE = _N_BASE                  # the adequacy test keeps its base threshold log(67 / alpha)


def contains(big, small):
    """small's terms are all in big; truth-v2 (V2): a coarser cell on the same input is inside a finer one (the grids
    nest exactly: 9 in 17 in 33 knots)."""
    big = set(big)
    for term in small:
        if term in big:
            continue
        if term[0] == 'cell' and any(b[0] == 'cell' and b[1] == term[1] and b[2] > term[2] for b in big):
            continue
        if is_shape(term) and any(b[0] == 'cell' and b[1] == term[1] and b[2] >= term[2] for b in big):
            continue                                    # Decision 12: a shape is inside a cell whose grid holds its own
        if term[0] == 'ramp' and any(b[0] == 'cell' and b[1] == term[1] for b in big):
            continue                                    # Decision 16: a ramp is inside any cell on its dimension (never
        return False                                    # the reverse)
    return True



def term_name(term):
    if term[0] == 'ramp':
        R = input_range(term[1])[1]
        return f'some strength times {describe_input(term[1])} (clipped at +-{R:g})'
    if term[0] == 'shape':
        return f'my shape {term[3]} of {describe_input(term[1])}'
    if term[0] == 'cell':
        return f'a free curve in {describe_input(term[1])} ({term[2]} knots)'
    if term[0] == 'piece':
        return {'abs': f'|{term[1]}|', 'tanh': f'tanh({term[1]}/{term[3]:g})',
                'bell': f'exp(-{term[1]}^2/{term[3]:g})'}[term[2]]
    if term[0] == 'pprod':
        return f'{term[1]} of position times {term[2]} of speed'
    if term[0] == 'product':
        return f'{term[1]} with position times {term[2]} with speed'
    if term[0] == 'power':
        return f'{term[1]} to the power {term[2]:g}'
    if term[0] == 'drive':
        return f'a push that swings in time ({term[1]} {term[2]:g}t)'
    return P.explain(term)


def name(family):
    return ' + '.join(term_name(i) for i in family) if family else 'nothing but my hand'


def term_codes(term):
    """Every (kind, a, b) of a term: a K-knot cell has K (kind 7, b = G * 100 + k); so has an invented shape (its
    hats, tied by its knots: see tie)."""
    if term[0] in ('cell', 'shape'):
        G = CELL_KS.index(term[2])
        return [(7, input_code(term[1]), G * 100 + k) for k in range(term[2])]      # Decision 14: or a lens's
    if term[0] == 'hats':                       # Decision 13: a band's check, some hats of a grid
        G = CELL_KS.index(term[2])
        return [(7, input_code(term[1]), G * 100 + k) for k in hat_indices(term)]
    return [code(term)]


def codes(family):
    """Arrays for the path simulator."""
    c = [x for t in family for x in term_codes(t)]
    return (np.array([k for k, _, _ in c], np.int64), np.array([a for _, a, _ in c], np.int64),
            np.array([b for _, _, b in c], np.int64))
