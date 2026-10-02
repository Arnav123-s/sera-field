"""SERA v4's Field, the exact part (docs/SERA_FIELD_THEORY.md v1.1 Part I, §3-5): one joint model, one update rule.

- **Belief over laws (§3), exact on one scale.** From the evidence table's reading intervals (sera.compact), dividing
  each measured acceleration by the object's inverse mass makes every law linear in its strengths:
      z_n = y_n / mu_k - fbar_n = sum_j c_j phi_j(n) + e_n,   e_n ~ N(0, (SIGMA_Y / mu_k)^2),   c ~ N(0, S_C^2 I).
  Each law's evidence m(h) is then the closed-form Gaussian marginal (no prior inside it), and the belief
  b(h) ∝ p_F(h) m(h) is a finite sum over all 3,175 laws. The inverse masses are plugged in (the judge's fit): the
  one named approximation, with the surrogate's neighbour noise correlation (-1/2) ignored.
- **The floor (§4), outside the joint:** p_F = (1 - ETA) P_mem + ETA pi0, so no law is ever forgotten
  (Proposition 2: its odds against any rival are at least its evidence margin minus log(1 / (ETA pi0(h)))).
- **Memory (§5): a faded, context-weighted Polya tree over the hypothesis lattice** (inputs -> operator class ->
  subtype -> law). A node's child has probability (a0 pi0(child)/pi0(node) + C_child) / (a0 + C_node), the counts
  being past worlds' final beliefs, faded by 2^(-1/half_life) per world and weighted by context similarity. With no
  counts it is pi0; a refuted law simply gets no count (no trace code); a memory held by C worlds keeps its shape until
  its faded count nears a0, then halves every half-life.
The judge never reads any of this: it steers belief, dreams and pushes only.

Vocabulary (plan revision 5, WP2): the laws the Field weighs are the base laws plus each term SERA knows, alone and
with one idea (`Vocab`). With no vocabulary given, it knows every truth-v1 invented term: the 3,175 laws of v4,
unchanged. A term it does not know can still be found (sera.mind's discover step, over the whole dictionary of
sera.sparse) and proven by the judge; the judge's prior and audit never depend on the vocabulary.
"""
import math

import numpy as np

from ccops5.core import grammar
from . import compact as C

S_C = 10.0                       # prior sd of a strength (the judge's COEF_PRIOR_SD)
ETA = 0.1                        # the floor's share (a decision rule, frozen)
CONTEXT_DIM = C.WORLD_FEATURES


def normalize(logp):
    top = np.logaddexp.reduce(np.array(list(logp.values()), float))
    return {h: v - top for h, v in logp.items()}


def term_columns(terms, x, v, t):
    """phi_j at each point for the given terms, in order: truth-v1 terms from the evidence table's own columns, grown
    terms (pieces, piece products) from the checker's independent formulas, as in sera.sparse.columns."""
    if tuple(terms) == C.TERMS:
        return C.columns(x, v, t)
    base = C.columns(x, v, t)
    out = []
    for term in terms:
        j = C.TERM_INDEX.get(term)
        if j is not None:
            out.append(base[:, j])
        else:
            from ccops5.core import checker
            out.append(np.asarray(checker._grown_np(term, x, v, t)[0], float))
    return np.stack(out, 1) if out else np.zeros((len(x), 0))


class Stats:
    """Sufficient statistics of the fidelity-0 model for every term at once: G = Phi' W Phi, b = Phi' W z, z' W z,
    log det D and n (W = D^-1). `vocab` names the columns (the full truth-v1 table unless given)."""

    def __init__(self, G, b, zz, logdet, n, vocab=None):
        self.G, self.b, self.zz, self.logdet, self.n = G, b, zz, logdet, n
        self.vocab = vocab

    @classmethod
    def from_arrays(cls, Phi, d, z, vocab=None):
        w = 1.0 / d
        return cls(Phi.T @ (Phi * w[:, None]), Phi.T @ (w * z), float(z @ (w * z)), float(np.log(d).sum()), len(z),
                   vocab)

    def gram(self, idx):
        return self.G[np.ix_(idx, idx)]


class LazyStats(Stats):
    """The same statistics with G's blocks computed only for the columns a law uses (2026-09-28: at growth level 2 a
    rail's candidate parts give thousands of columns, and the full G took most of a step). Equal to Stats up to
    rounding."""

    def __init__(self, Phi, d, z, vocab=None):
        w = 1.0 / d
        self.Phi, self.w = Phi, w
        super().__init__(None, Phi.T @ (w * z), float(z @ (w * z)), float(np.log(d).sum()), len(z), vocab)

    def gram(self, idx):
        P = self.Phi[:, idx]
        return P.T @ (P * self.w[:, None])


def _vocab_of(st):
    return st.vocab if getattr(st, 'vocab', None) is not None else FULL


SHAPE_MASS = 0.01                # rev 6: an invented shape's description-length mass (grammar's Decision 12 share)


def law_log_prior(h):
    """A law's description length: the judge's prior (D9, truth-v2), or (rev 6) for a law with one of SERA's invented
    shapes, the shape's library share - the numbers of grammar's Decision 12, whether or not the judge's policy uses
    them (SERA may think with its inventions before the judge may prove with them)."""
    h = grammar.canonical(h)
    shapes = [t for t in h if t[0] == 'shape']
    if not shapes:
        return grammar.log_prior(h)
    bases = [t for t in h if t in grammar.IDEAS]
    if len(shapes) != 1 or len(h) - len(bases) != 1 or len(bases) > 1:
        return -math.inf
    n = shapes[0][3]
    return (math.log(SHAPE_MASS) + math.log(6 / (math.pi ** 2 * n * n)) + math.log(0.5)
            + (math.log(1 / len(grammar.IDEAS)) if bases else 0.0))


def prior_logp(vocab=None):
    """log pi0(h) (D9) over the vocabulary's laws (sub-normalized: over the full vocabulary the sum is 0.95)."""
    return {h: law_log_prior(h) for h in (vocab or FULL).laws}


def with_floor(log_mem, vocab=None):
    """p_F = (1 - ETA) P_mem + ETA pi0, normalized over the vocabulary's laws (§4)."""
    vocab = vocab or FULL
    pi0 = prior_logp(vocab)
    return normalize({h: float(np.logaddexp(math.log(1 - ETA) + log_mem.get(h, -math.inf), math.log(ETA) + pi0[h]))
                      for h in vocab.laws})


def evidence(throws, mu, skip=(), vocab=None):
    """The Stats of the throws, given each object's inverse mass {situation: mu} (objects without one, or in `skip` -
    knocked or disturbed ones - are left out), over the vocabulary's columns."""
    vocab = vocab or FULL
    obj, y, fb, xb, vb, tb = C.intervals(throws)
    keep = np.array([o in mu and o not in skip for o in obj], bool)
    m = np.array([mu[o] for o in obj[keep]], float)
    z = y[keep] / m - fb[keep]
    d = (C.SIGMA_Y / m) ** 2
    return Stats.from_arrays(term_columns(vocab.cols, xb[keep], vb[keep], tb[keep]), d, z, vocab)


def log_marginal(st, idx):
    """log N(z; 0, D + S_C^2 Phi_S Phi_S') by Woodbury: -1/2 [n log 2 pi + log det D + z'Wz - b_S' A^-1 b_S + log det A
    + k log S_C^2], A = G_SS + I / S_C^2."""
    base = st.n * math.log(2 * math.pi) + st.logdet + st.zz
    if not idx:
        return -0.5 * base
    A = st.gram(idx) + np.eye(len(idx)) / S_C ** 2
    L_ = np.linalg.cholesky(A)
    u = np.linalg.solve(L_, st.b[idx])
    return -0.5 * (base - float(u @ u) + 2.0 * float(np.log(np.diag(L_)).sum()) + len(idx) * math.log(S_C ** 2))


def law_log_marginal(st, h):
    return log_marginal(st, _vocab_of(st).idx[grammar.canonical(h)])


def belief(st, log_prior):
    """The exact belief over the vocabulary's laws: log b(h) = log p(h) + log m(h) - log Z (p need not be
    normalized)."""
    vocab = _vocab_of(st)
    return normalize({h: log_prior[h] + log_marginal(st, vocab.idx[h]) for h in vocab.laws})


# --- the hypothesis lattice (§5) and the vocabulary (revision 5) ---

_PIECE_INPUT = {'position': 'x', 'speed': 'v', 'time': 't'}


def _inputs(h):
    ins = set()
    for t in h:
        if t[0] in ('product', 'pprod'):
            ins |= {'x', 'v'}
        elif t[0] == 'power':
            ins.add('x' if t[1] == 'position' else 'v')
        elif t[0] == 'drive':
            ins.add('t')
        elif t[0] in ('piece', 'cell', 'shape'):
            ins.add(_PIECE_INPUT[t[1]])
        elif t[0] == 'position':
            ins.add('x')
        elif t[0] == 'speed':
            ins.add('v')
    return ''.join(sorted(ins)) or 'none'


def path(h):
    """The law's path in the lattice: (inputs, operator class, subtype, law). A piece's subtype is its operation
    (abs, tanh, bell); a piece product's is 'pprod'."""
    opens = [t for t in h if t not in grammar.IDEAS]
    if not opens:
        op, sub = 'base', 'base'
    else:
        t = opens[0]
        op = t[0]
        sub = t[1] if t[0] in ('power', 'drive') else (t[2] if t[0] == 'piece' else op)
    return (_inputs(h), op, sub, h)


def _node_masses(paths, pi0):
    mass = {(): 1.0}
    for h, p in paths.items():
        for lv in range(1, 5):
            mass[p[:lv]] = mass.get(p[:lv], 0.0) + math.exp(pi0[h])
    return mass


class Vocab:
    """The terms SERA knows (plan revision 5, WP2). Its Field weighs the 67 base laws and each known invented or grown
    term alone and with one idea, at the judge's D9 prices. `terms=None` is every truth-v1 invented term (v4's 3,175
    laws). Cells are never vocabulary: a free curve has many strengths, and growth weighs it directly."""

    def __init__(self, terms=None):
        if terms is None:
            opens = tuple(grammar.OPEN_TERMS)
        else:
            opens = tuple(sorted({t for t in terms if t not in grammar.IDEAS and t[0] != 'cell'}, key=grammar._key))
        self.terms = opens
        self.cols = tuple(grammar.IDEAS) + opens
        col = {t: i for i, t in enumerate(self.cols)}
        fams = list(grammar.space())
        for t in opens:
            fams.append((t,))
            fams += [grammar.canonical((t, i)) for i in grammar.IDEAS]
        self.laws = tuple(f for f in dict.fromkeys(grammar.canonical(f) for f in fams)
                          if law_log_prior(f) > -math.inf)
        self.idx = {h: [col[t] for t in h] for h in self.laws}
        self.paths = {h: path(h) for h in self.laws}
        self.mass = _node_masses(self.paths, normalize({h: law_log_prior(h) for h in self.laws}))

    def __contains__(self, term):
        return term in grammar.IDEAS or term in self._known

    @property
    def _known(self):
        k = self.__dict__.get('_known_set')
        if k is None:
            k = self.__dict__['_known_set'] = frozenset(self.terms)
        return k

    def with_terms(self, more):
        """This vocabulary and `more` terms (a new Vocab; this one is unchanged)."""
        more = [t for t in more if t not in grammar.IDEAS and t[0] != 'cell' and t not in self.terms]
        return self if not more else Vocab(self.terms + tuple(more))


FULL = Vocab(None)               # v4's Field: every truth-v1 invented term
LAWS = FULL.laws                 # the truth-v1 claimable laws. independent review T2/T4 review M2: the judge's universe audit
                                 # also weighs the piece and piece-product laws (grammar.PIECES, PPRODS); in revision 5
                                 # a Vocab may hold them too, once SERA knows them
_IDX = FULL.idx
_PATHS = FULL.paths
_MASS = FULL.mass
UNIVERSE_TERMS = tuple(grammar.OPEN_TERMS) + tuple(grammar.PIECES) + tuple(grammar.PPRODS)   # every claimable
UNIVERSE_PATHS = {h: path(h) for h in Vocab(UNIVERSE_TERMS).laws}                             # non-cell term


class Memory:
    """Past worlds' final beliefs as soft counts on the lattice's nodes, held in at most `prototypes` context
    prototypes (a fixed size), faded by 2^(-1/half_life) per world, recalled by context similarity
    exp(-|c - c'|^2 / 2 ell^2)."""

    def __init__(self, alpha0=1.0, half_life=5.0, prototypes=16, ell=1.0, merge=0.5):
        self.alpha0, self.gamma = alpha0, 2.0 ** (-1.0 / half_life)
        self.max_protos, self.ell, self.merge = prototypes, ell, merge
        self.protos = []                                   # [center, weight, {node: count}]

    def _kappa(self, c, center):
        return math.exp(-float(np.sum((np.asarray(c) - center) ** 2)) / (2 * self.ell ** 2))

    def add_world(self, context, log_b):
        """Fold one world's final belief (log probabilities over LAWS) into the nearest prototype, or a new one."""
        c = np.asarray(context, float)
        counts = {}
        for h, lb in log_b.items():
            if lb == -math.inf:
                continue
            w = math.exp(lb)
            p = _PATHS[h]
            for lv in range(1, 5):
                counts[p[:lv]] = counts.get(p[:lv], 0.0) + w
        near = min(self.protos, key=lambda q: float(np.sum((q[0] - c) ** 2)), default=None)
        if near is None or (np.sqrt(np.sum((near[0] - c) ** 2)) > self.merge * self.ell
                            and len(self.protos) < self.max_protos):
            self.protos.append([c.copy(), 1.0, counts])
            return
        near[0] = (near[0] * near[1] + c) / (near[1] + 1.0)
        near[1] += 1.0
        for k, v in counts.items():
            near[2][k] = near[2].get(k, 0.0) + v

    def fade(self):
        """One world passes: every count shrinks by gamma."""
        for q in self.protos:
            q[1] *= self.gamma
            for k in q[2]:
                q[2][k] *= self.gamma

    def count(self, node, context):
        return sum(self._kappa(context, q[0]) * q[2].get(tuple(node), 0.0) for q in self.protos)

    def weight(self, node, context):
        """How far a node's children lean from pi0: C / (a0 + C)."""
        c = self.count(node, context)
        return c / (self.alpha0 + c)

    def log_prior(self, context):
        """log P_mem(h | context) for every law (normalized at every node)."""
        cnt = {}
        for q in self.protos:
            k = self._kappa(context, q[0])
            if k < 1e-300:
                continue
            for node, v in q[2].items():
                cnt[node] = cnt.get(node, 0.0) + k * v
        root = sum(v for n, v in cnt.items() if len(n) == 1)
        out = {}
        for h, p in _PATHS.items():
            lp, parent_c, parent_m = 0.0, root, 1.0
            for lv in range(1, 5):
                node = p[:lv]
                c = cnt.get(node, 0.0)
                lp += math.log((self.alpha0 * _MASS[node] / parent_m + c) / (self.alpha0 + parent_c))
                parent_c, parent_m = c, _MASS[node]
            out[h] = lp
        return out


# --- dreams and curiosity (§6-7) ---

def posterior(st, h):
    """The strengths' exact posterior under the fidelity-0 model: N(A^-1 b_S, A^-1), A = G_SS + I / S_C^2."""
    idx = _vocab_of(st).idx[grammar.canonical(h)]
    if not idx:
        return np.zeros(0), np.zeros((0, 0))
    cov = np.linalg.inv(st.G[np.ix_(idx, idx)] + np.eye(len(idx)) / S_C ** 2)
    return cov @ st.b[idx], cov


def dreams(rng, st, log_b, n, beta=1.0):
    """n imagined worlds (law, strengths): a law from the tempered belief b^beta (beta < 1: a fuzzier dream), its
    strengths from their posterior."""
    laws = list(log_b)
    lp = beta * np.array([log_b[h] for h in laws])
    p = np.exp(lp - lp.max())
    p /= p.sum()
    out = []
    for i in rng.choice(len(laws), size=n, p=p):
        m, c = posterior(st, laws[i])
        out.append((laws[i], rng.multivariate_normal(m, c) if len(m) else m))
    return out


def predictive(st, h, action, mu, var_mu=0.0):
    """A law's predicted readings for `action` on an object of inverse mass mu, as a Gaussian linearized at its
    posterior mean strengths: (mean (82,), covariance J C J' over the strengths' posterior and the mass's variance)."""
    from ccops5.core import paths
    kind, a, b = grammar.codes(h)
    m, cov = posterior(st, h)
    T = grammar.tie(h)                                   # Decision 12: an invented shape moves its hats together
    y, J = paths.jacobian_exact(*action.arrays(), mu, kind, a, b, m if T is None else T @ m, 1.0, 1.0, 0.0, 0.0)
    if T is not None:
        J = np.concatenate([J[:, :len(kind)] @ T, J[:, len(kind):]], axis=1)
    nc = len(m)
    Cf = np.zeros((nc + 1, nc + 1))
    Cf[:nc, :nc] = cov
    Cf[nc, nc] = var_mu
    return y, J @ Cf @ J.T


def box_hill(preds, weights, sigma):
    """Box & Hill (1967): D = sum_{i<j} w_i w_j [KL(N_i || N_j) + KL(N_j || N_i)], N_i = N(y_i, S_i + noise), the
    discrimination criterion for choosing between rival models; it bounds the expected drop in entropy of the belief
    over them. Each law's own strength uncertainty widens its Gaussian, so a push that a rival can match by re-fitting
    earns little (the multi-law form of the surviving gap). [approximation: linearized predictives]"""
    n = len(preds[0][0]) // 2
    noise = np.diag(np.concatenate([np.full(n, sigma[0] ** 2), np.full(n, sigma[1] ** 2)]))
    Ss = [S + noise for _, S in preds]
    inv = [np.linalg.inv(S) for S in Ss]
    d = 2 * n
    total = 0.0
    for i in range(len(preds)):
        for j in range(i + 1, len(preds)):
            dy = preds[i][0] - preds[j][0]
            sym = 0.5 * (np.trace(inv[j] @ Ss[i]) + np.trace(inv[i] @ Ss[j]) - 2 * d
                         + float(dy @ (inv[i] + inv[j]) @ dy))
            total += weights[i] * weights[j] * sym
    return total


# --- the action language (§8): SERA composes its own pushes ---

T_STEP = 0.1                     # program times on a 0.1 s grid over the throw
U_LEVELS = tuple(round(u, 2) for u in np.linspace(-1.0, 1.0, 11) if abs(u) > 1e-9)
MAX_SEGMENTS = 2                 # within the regime where premise N was measured (independent review, N2); longer programs
                                 # wait for a per-class N sentinel


def code_length(program):
    """Bits of a program under the prefix-free code: the number of segments (1 bit each, unary), then per segment
    its start and end on the time grid and its command level (Kraft: sum over programs of 2^-bits <= 1)."""
    n_t = int(round(2.0 / T_STEP)) + 1
    per = math.log2(n_t) + math.log2(n_t) + math.log2(len(U_LEVELS))
    return len(program.segments) + len(program.segments) * per


def sample_programs(rng, n):
    """n programs from the code prior conditioned on disjoint segments (1 segment with probability 1/2, 2 with 1/4,
    renormalized to MAX_SEGMENTS; a subset of the code, so Kraft still holds)."""
    from ccops5.core.worlds import Action
    ks = np.arange(1, MAX_SEGMENTS + 1)
    pk = 2.0 ** -ks
    pk /= pk.sum()
    grid = np.round(np.arange(0.0, 2.0 + 1e-9, T_STEP), 1)
    out = []
    for _ in range(n):
        k = int(rng.choice(ks, p=pk))
        cuts = sorted(rng.choice(len(grid), size=2 * k, replace=False))    # 2k distinct grid points, paired in order:
        segs = [(float(grid[cuts[2 * i]]), float(grid[cuts[2 * i + 1]]), float(rng.choice(U_LEVELS)))   # disjoint
                for i in range(k)]                                         # segments, so |u| <= 1 (independent review review)
        out.append(Action(tuple(segs)))
    return out


def mutate(rng, program):
    """A neighbouring program: one segment's start, end or command moved one step."""
    from ccops5.core.worlds import Action
    segs = [list(s) for s in program.segments]
    s = segs[rng.integers(len(segs))]
    what = rng.integers(3)
    if what < 2:
        s[what] = float(np.clip(round(s[what] + T_STEP * rng.choice([-1, 1]), 1), 0.0, 2.0))
        if s[1] <= s[0]:
            return program
    else:
        i = U_LEVELS.index(s[2]) if s[2] in U_LEVELS else 0
        s[2] = U_LEVELS[int(np.clip(i + rng.choice([-1, 1]), 0, len(U_LEVELS) - 1))]
    segs = sorted(tuple(x) for x in segs)
    if any(segs[i][1] > segs[i + 1][0] for i in range(len(segs) - 1)):   # overlapping segments would add past the hand
        return program
    return Action(tuple(segs))


def context(throws):
    """The world's context for memory recall: the evidence table's world features (sera.compact)."""
    return np.asarray(C.compact(throws)[1], float)


def top_laws(log_b, k):
    return sorted(log_b, key=log_b.get, reverse=True)[:k]


def open_terms(log_b, max_open, mask=()):
    """The invented terms of the most believed laws, in belief order, at most max_open (none masked)."""
    out = []
    for h in sorted(log_b, key=log_b.get, reverse=True):
        for t in h:
            if t not in grammar.IDEAS and t not in mask and t not in out:
                out.append(t)
        if len(out) >= max_open:
            break
    return tuple(sorted(out[:max_open], key=grammar._key))
