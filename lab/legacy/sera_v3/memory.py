"""SERA memory v3 (plan revision 4, R4-3b; the author's design, 2026-09-26; research dive RM, (review notes, not published)),
format 2 (plan revision 5, WP2-WP3: taught and graded lessons, the vocabulary, the words).

SERA is frozen in time during each experience and grown by it afterwards. Memory is state, not a log, and it is
selective the way imagination is: an experience leaves many cheap tags, and only a few are captured.

The five kinds of memory:
- working    the live episode (the judge's ledger: throws, fits, belief). Not stored here.
- tags       one per judged event of the episode (a certificate refused or accepted), with a strength in nats.
             Episode-local; dropped at the end unless captured.
- lessons    "in this situation I believed this, and it was wrong (or right), and why": a context key, a node of the
             hypothesis lattice (a law, or a coarser node such as "depends on speed"), a reason, who said it (the
             judge, the caretaker, or SERA itself), a gap in nats and a fading weight. A lesson fades by half every
             LESSON_HALF episodes and is resolved (cleared) when a proof lands in its context. A lesson against a law
             ('something else is here', 'extra terms needed', the caretaker's 'graded wrong', its own 'doubted') lowers
             the proposal weight of every law under its node in that context; a lesson for one ('taught', 'part
             right', its own 'believed') raises it; a refusal for want of evidence (a rival not ruled out, a band too
             wide) says nothing about the law, so it only waits for the experiment that settles it.
- skills     push programs that settled something (a proof, the best question, the biggest band cut, or the caretaker's
             demonstration), offered again as candidate experiments where the context recurs. A skill becomes active
             once it has helped in 2 distinct episodes (a demonstration is active at once). Programs are matched on a
             0.1 grid, so the same push made twice is recognised.
- knowledge  proven laws only (accepted, checker-verified certificates), as counts on the hypothesis lattice, held at
             fixed anchors. Changed only by more proofs. Also here: the vocabulary (every term SERA knows; a term is
             learned only when a proof holding it is verified, or when the caretaker names it) and the words (the
             posterior over what each word names, sera.words).

Frozen, then grown: begin() returns a Snapshot (the serialized bytes and their digest). Every read during the episode
goes through the snapshot; consolidate() writes the next version, once per episode. The judge never reads memory:
memory changes only proposals, candidate experiments and the Field's prior, which is fixed at the start of each world,
so every proof stays valid (each choice depends on the past only).

Fixed size: the serialized state is exactly MEMORY_BYTES, always (a header, P anchors, L lessons, S skills, the
vocabulary bits and the lexicon; fixed-width records), about 13.6 KB (the author's side goal: at most 35,840 bytes).
Anchors never move (RM section 6.3): a context farther than RADIUS from every anchor gets a new anchor while fewer than
P exist; otherwise the nearest anchor within RADIUS takes the write, and beyond RADIUS with all P used the knowledge
write is skipped. So anchors stay more than RADIUS apart forever: memories never merge into one blob.
"""
import hashlib
import math

import numpy as np

from ccops5.core import grammar
from . import field as F, words as W

P_ANCHORS, N_LESSONS, N_SKILLS, SLOTS = 32, 32, 32, 32
K_CAPTURE = 8                    # lessons captured per episode at most (proofs are always kept)
LESSON_HALF = 8.0                # episodes (RM section 6.2)
W_MIN = 0.05                     # a lesson fainter than this is forgotten
B_MAX = 2.0                      # the largest bias a lesson puts on a law's log weight (RM: B = 2)
ELL, RADIUS = 1.0, 0.5           # context kernel length and the anchors' separation (sera.field's ell and merge)
ACTIVE_USES = 2                  # a skill is active after helping in this many distinct episodes
MAX_SEGMENTS = 4
DOMAINS = {'physics': 1, 'code': 2, 'words': 3}
REASONS = {'rival': 1, 'something else': 2, 'extra terms': 3, 'band': 4, 'fit failed': 5, 'other': 6,
           'taught': 7, 'graded wrong': 8, 'part right': 9, 'believed': 10, 'doubted': 11}
AGAINST_LAW = {2, 3, 8, 11}      # reasons that say the law (or node) is wrong or incomplete
FOR_LAW = {7, 9, 10}             # reasons that say it is right (or partly)
SOURCES = {'judge': 0, 'caretaker': 1, 'self': 2}
D = F.CONTEXT_DIM

NODES = sorted({p[:lv] for p in F.UNIVERSE_PATHS.values() for lv in range(1, 5)}, key=repr)
NODE_ID = {n: i + 1 for i, n in enumerate(NODES)}          # 0 = none; uint16
assert len(NODES) < 65535
TERM_BIT = {t: i for i, t in enumerate(F.UNIVERSE_TERMS)}   # the vocabulary's bit per claimable non-cell term
NB = (len(F.UNIVERSE_TERMS) + 7) // 8

HEADER = np.dtype([('magic', 'S4'), ('version', '<u4'), ('episode', '<u4'), ('pad', 'u1', 52)])
ANCHOR = np.dtype([('key', '<f4', D), ('domain', 'u1'), ('used', 'u1'), ('pad', 'u1', 2), ('visits', '<f4'),
                   ('node', '<u2', SLOTS), ('count', '<f4', SLOTS)])
LESSON = np.dtype([('key', '<f4', D), ('domain', 'u1'), ('status', 'u1'), ('reason', 'u1'), ('source', 'u1'),
                   ('law', '<u2'), ('rival', '<u2'), ('gap', '<f4'), ('weight', '<f4'), ('born', '<u4')])
SKILL = np.dtype([('key', '<f4', D), ('domain', 'u1'), ('state', 'u1'), ('nseg', 'u1'), ('source', 'u1'),
                  ('law', '<u2'), ('uses', '<u2'), ('gain', '<f4'), ('last', '<u4'), ('seg', '<f4', (MAX_SEGMENTS, 3))])
VOCAB = np.dtype([('known', 'u1', NB), ('taught', 'u1', NB), ('pad', 'u1', (-2 * NB) % 8)])
LEXICON = np.dtype([('logp', '<f4', (len(W.SLOTS), W.N_PERMS)), ('heard', '<u4', len(W.SLOTS)), ('pad', 'u1', 4)])
MEMORY_BYTES = (HEADER.itemsize + P_ANCHORS * ANCHOR.itemsize + N_LESSONS * LESSON.itemsize + N_SKILLS * SKILL.itemsize
                + VOCAB.itemsize + LEXICON.itemsize)
OPEN, RESOLVED = 1, 2
CANDIDATE, ACTIVE = 1, 2


def reason_code(text):
    """The judge's refusal reason (truth.certify's words) as a code."""
    for key, code in (('rival fit failed', 5), ('rival family is not ruled out', 1), ('something else is here', 2),
                      ('extra terms needed', 3), ('something else could be as large', 4)):
        if key in text:
            return code
    return REASONS['other']


def law_node(family):
    """The lattice leaf of a law (0 if it is not a claimable non-cell law)."""
    p = F.UNIVERSE_PATHS.get(grammar.canonical(family))
    return NODE_ID[p] if p is not None else 0


def _dist(a, b):
    return float(np.sqrt(np.sum((np.asarray(a, float) - np.asarray(b, float)) ** 2)))


def _kappa(a, b):
    return math.exp(-_dist(a, b) ** 2 / (2 * ELL ** 2))


def _seg_key(segs):
    return tuple((round(float(a), 1), round(float(b), 1), round(float(u), 1)) for a, b, u in segs)


def _laws_under(vocab, node):
    """The vocabulary's laws whose lattice path starts with `node` (cached on the vocabulary)."""
    idx = vocab.__dict__.get('_under')
    if idx is None:
        idx = {}
        for h, p in vocab.paths.items():
            for lv in range(1, 5):
                idx.setdefault(p[:lv], []).append(h)
        vocab.__dict__['_under'] = idx
    return idx.get(tuple(node), ())


class Snapshot:
    """The memory as it was when an episode began: read-only bytes, their digest, and the recall functions."""

    def __init__(self, raw):
        self.raw = bytes(raw)
        self.digest = hashlib.sha256(self.raw).hexdigest()
        self._m = Memory.from_bytes(self.raw)

    def log_prior(self, context, domain='physics', vocab=None):
        return self._m.log_prior(context, domain, vocab)

    def lessons(self, context, domain='physics'):
        return self._m.lessons_near(context, domain)

    def skill_programs(self, context, domain='physics'):
        return self._m.skill_programs(context, domain)

    def vocab(self):
        return self._m.vocab()

    def lexicon(self):
        return self._m.lexicon()


class Tags:
    """The episode's tags (working memory's event log; dropped at the episode's end unless captured)."""

    def __init__(self):
        self.items = []

    def certificate(self, cert, program=None):
        """Tag one certify call: a proof (strength = its smallest margin over the rival threshold) or a refusal
        (strength = how far it was from passing, in nats, by its first reason)."""
        fam = tuple(cert.family)
        law = law_node(fam)                                                # the law's leaf in the lattice
        if cert.accepted:
            margin = min(cert.rivals.values()) - _threshold(cert) if cert.rivals else 0.0
            self.items.append(dict(kind='proof', law=law, family=fam, strength=float(max(margin, 0.0)),
                                   program=program))
            return
        code = reason_code(cert.reasons[0]) if cert.reasons else REASONS['other']
        rival = 0
        if code == 1 and cert.rivals:
            b, e = min(cert.rivals.items(), key=lambda kv: kv[1])
            rival = law_node(tuple(b))
            gap = max(0.0, _threshold(cert) - e)
        elif code == 2 and _adequacy(cert) is not None and np.isfinite(_adequacy(cert)):
            gap = float(max(_adequacy(cert), 0.0))
        elif code == 4 and cert.band is not None and cert.eps:
            gap = float(max(math.log(max(cert.band, 1e-300) / cert.eps), 0.0)) if np.isfinite(cert.band) else 10.0
        else:
            gap = 1.0
        self.items.append(dict(kind='refusal', law=law, family=fam, reason=code, rival=rival,
                               strength=float(min(gap, 1e6)), program=program))


def _adequacy(cert):
    """The certificate's adequacy e-value (truth.Certificate names it `adequacy`; revision 5's first assembled run
    found that memory v3 read a field `adequate` that only its test doubles had)."""
    return getattr(cert, 'adequacy', getattr(cert, 'adequate', None))


def _threshold(cert):
    return grammar.log_threshold(tuple(cert.family), cert.alpha)


class Memory:
    """The long-term state (anchors with knowledge, lessons, skills, vocabulary, words), in fixed-width records."""

    def __init__(self):
        self.header = np.zeros(1, HEADER)
        self.header['magic'] = b'SMV3'
        self.header['version'] = 2
        self.anchors = np.zeros(P_ANCHORS, ANCHOR)
        self.lessons = np.zeros(N_LESSONS, LESSON)
        self.skills = np.zeros(N_SKILLS, SKILL)
        self.vocab_bits = np.zeros(1, VOCAB)
        self.lex = np.zeros(1, LEXICON)
        self.lex['logp'][0] = W.flat()

    # --- the fixed-size form ---
    def to_bytes(self):
        out = (self.header.tobytes() + self.anchors.tobytes() + self.lessons.tobytes() + self.skills.tobytes()
               + self.vocab_bits.tobytes() + self.lex.tobytes())
        assert len(out) == MEMORY_BYTES
        return out

    @classmethod
    def from_bytes(cls, raw):
        assert len(raw) == MEMORY_BYTES
        m = cls()
        o = 0
        for name, dt, n in (('header', HEADER, 1), ('anchors', ANCHOR, P_ANCHORS), ('lessons', LESSON, N_LESSONS),
                            ('skills', SKILL, N_SKILLS), ('vocab_bits', VOCAB, 1), ('lex', LEXICON, 1)):
            setattr(m, name, np.frombuffer(raw, dt, n, o).copy())
            o += dt.itemsize * n
        return m

    def begin(self, context=None):
        """Freeze: the episode reads only this snapshot."""
        return Snapshot(self.to_bytes())

    @property
    def episode(self):
        return int(self.header['episode'][0])

    # --- the vocabulary and the words ---
    def vocab_terms(self, which='known'):
        bits = np.unpackbits(self.vocab_bits[which][0])[:len(F.UNIVERSE_TERMS)]
        return tuple(t for t, b in zip(F.UNIVERSE_TERMS, bits) if b)

    def vocab(self):
        """The Field's vocabulary: the base ideas (innate) and every term SERA has learned."""
        return F.Vocab(self.vocab_terms())

    def _set_bit(self, which, term):
        i = TERM_BIT.get(term)
        if i is None:
            return False
        arr = self.vocab_bits[which][0]
        byte, bit = divmod(i, 8)
        mask = np.uint8(1 << (7 - bit))                    # np.unpackbits is big-endian within a byte
        new = not (arr[byte] & mask)
        arr[byte] |= mask
        return bool(new)

    def lexicon(self):
        """The posterior over what each word names: (3 slots, 120 bijections) log probabilities (sera.words)."""
        return self.lex['logp'][0].astype(float)

    # --- recall ---
    def _near_anchors(self, context, domain):
        dom = DOMAINS[domain]
        out = []
        for a in self.anchors:
            if a['used'] and a['domain'] == dom:
                k = _kappa(context, a['key'])
                if k > 1e-12:
                    out.append((k, a))
        return out

    def log_prior(self, context, domain='physics', vocab=None):
        """log P_mem(h | context) over the vocabulary's laws (sera.field.FULL by default): the Polya tree of proven
        laws at the anchors near this context (kernel-weighted counts), plus each open lesson's signed bias here. Use
        through sera.field.with_floor, which keeps every law proposable."""
        vocab = vocab or F.FULL
        cnt = {}
        for k, a in self._near_anchors(context, domain):
            for node, c in zip(a['node'], a['count']):
                if node:
                    n = NODES[node - 1]
                    cnt[n] = cnt.get(n, 0.0) + k * float(c)
        root = sum(v for n, v in cnt.items() if len(n) == 1)
        bias = self._law_bias(context, domain, vocab)
        out = {}
        for h, p in vocab.paths.items():
            lp, parent_c, parent_m = 0.0, root, 1.0
            for lv in range(1, 5):
                node = p[:lv]
                c = cnt.get(node, 0.0)
                lp += math.log((1.0 * vocab.mass[node] / parent_m + c) / (1.0 + parent_c))
                parent_c, parent_m = c, vocab.mass[node]
            out[h] = lp + bias.get(h, 0.0)
        return F.normalize(out)

    def _law_bias(self, context, domain, vocab):
        dom = DOMAINS[domain]
        bias = {}
        for l in self.lessons:
            if l['status'] != OPEN or l['domain'] != dom or not l['law']:
                continue
            r = int(l['reason'])
            sign = -1.0 if r in AGAINST_LAW else 1.0 if r in FOR_LAW else 0.0
            if not sign:
                continue
            amount = sign * min(B_MAX, float(l['weight'])) * _kappa(context, l['key'])
            for h in _laws_under(vocab, NODES[l['law'] - 1]):
                bias[h] = bias.get(h, 0.0) + amount
        return bias

    def lessons_near(self, context, domain='physics', min_sim=0.5):
        """The open lessons whose context is near this one, strongest first: (law or lattice node, reason code, gap,
        weight, similarity, source)."""
        dom = DOMAINS[domain]
        names = {v: k for k, v in SOURCES.items()}
        out = []
        for l in self.lessons:
            if l['status'] == OPEN and l['domain'] == dom:
                s = _kappa(context, l['key'])
                if s >= min_sim:
                    node = NODES[l['law'] - 1] if l['law'] else None
                    law = node[3] if node is not None and len(node) == 4 else node
                    out.append((law, int(l['reason']), float(l['gap']), float(l['weight']), s,
                                names.get(int(l['source']), 'judge')))
        return sorted(out, key=lambda x: -x[3] * x[4])

    def skill_programs(self, context, domain='physics', min_sim=0.5):
        """Active skills' push programs for this context (candidates for the design step; the analytic score
        still decides)."""
        from ccops5.core.worlds import Action
        dom = DOMAINS[domain]
        out = []
        for s in self.skills:
            if s['state'] == ACTIVE and s['domain'] == dom and _kappa(context, s['key']) >= min_sim:
                segs = tuple((round(float(a), 6), round(float(b), 6), round(float(u), 6))   # float32 back to the
                             for a, b, u in s['seg'][:s['nseg']])                         # program grid
                out.append(Action(segs))
        return out

    # --- growth: the one place memory changes ---
    def consolidate(self, snapshot, tags, context, domain='physics', verified=False, credit=None):
        """End of an episode. `snapshot` must be this memory's own begin() of the episode (nothing changed it since);
        `tags` the episode's Tags; `verified`: the final certificate was accepted and the checker re-derived it (only
        then does a proof become knowledge and resolve lessons). `credit` (revision 5, sera.credit): the grade's
        writes - lessons, skills, vocabulary, and the words heard with the law they were about. Returns the number of
        lessons captured from refusals."""
        assert snapshot.digest == hashlib.sha256(self.to_bytes()).hexdigest(), 'memory changed during the episode'
        dom = DOMAINS[domain]
        c = np.asarray(context, np.float32)
        self.header['episode'] += 1
        ep = self.episode
        live = self.lessons['status'] == OPEN                             # 1. lessons fade
        self.lessons['weight'][live] *= np.float32(2.0 ** (-1.0 / LESSON_HALF))
        self.lessons[live & (self.lessons['weight'] < W_MIN)] = np.zeros(1, LESSON)
        a = self._anchor_for(c, dom)                                      # 2. the anchor (fixed once placed)
        if a is not None:
            self.anchors['visits'][a] += 1.0
        proofs = [t for t in tags.items if t['kind'] == 'proof']
        if verified and proofs:                                           # 3. a proof: knowledge, resolved lessons, skills
            p = proofs[-1]
            path = F.UNIVERSE_PATHS.get(grammar.canonical(p['family']))
            if a is not None and path is not None:
                for lv in range(1, 5):
                    self._add_count(a, NODE_ID[path[:lv]], 1.0)
            for i, l in enumerate(self.lessons):
                if l['status'] == OPEN and l['domain'] == dom and _dist(c, l['key']) <= RADIUS:
                    self.lessons['status'][i] = RESOLVED
            if p.get('program') is not None:
                self._skill(c, dom, p['law'], p['program'], p['strength'], ep)
        # 4. capture, like imagination: many tags, few kept. The plan's value of memory, surprise x P(recur) / bytes,
        # ranks the tags of one episode by surprise alone (they share the context and every lesson has the same
        # size); across episodes, recurrence acts through refresh (a lesson met again is renewed) and fading.
        refusals = [t for t in tags.items if t['kind'] == 'refusal' and t['law']]
        ranked = sorted(refusals, key=lambda t: -t['strength'])
        seen, n = set(), 0
        for t in ranked:
            if n >= K_CAPTURE:
                break
            if (t['law'], t['reason']) in seen:
                continue
            seen.add((t['law'], t['reason']))
            self._lesson(c, dom, t['law'], t['reason'], SOURCES['judge'], 1.0, t['strength'], ep, t['rival'])
            n += 1
        if credit:                                                        # 5. revision 5: the grade's writes
            self._credit(c, dom, credit, ep)
        return n

    def judged(self, context, cert, verified, program=None, domain='physics', vocab=()):
        """Revision 5.1 (the judge's office, sera.proofs): the full verdict on a claim submitted in an earlier episode,
        written between episodes. A proof (accepted, and re-derived by the checker) becomes knowledge exactly as step 3
        of consolidate makes it - the anchor's counts along the law's path, the open lessons near it resolved, the push
        before it as a skill - and `vocab` (its discovered terms) joins the vocabulary; a refusal is captured as one
        lesson from the judge, as step 4 captures a refusal in the world. Returns True when a proof was written."""
        dom = DOMAINS[domain]
        c = np.asarray(context, np.float32)
        tags = Tags()
        tags.certificate(cert, program)
        t, ep = tags.items[0], self.episode
        if cert.accepted and verified:
            a = self._anchor_for(c, dom)
            path = F.UNIVERSE_PATHS.get(grammar.canonical(t['family']))
            if a is not None and path is not None:
                for lv in range(1, 5):
                    self._add_count(a, NODE_ID[path[:lv]], 1.0)
            for i, l in enumerate(self.lessons):
                if l['status'] == OPEN and l['domain'] == dom and _dist(c, l['key']) <= RADIUS:
                    self.lessons['status'][i] = RESOLVED
            if t.get('program') is not None:
                self._skill(c, dom, t['law'], t['program'], t['strength'], ep)
            for term in vocab:
                self._set_bit('known', term)
            return True
        if not cert.accepted and t['law']:
            self._lesson(c, dom, t['law'], t['reason'], SOURCES['judge'], 1.0, t['strength'], ep, t['rival'])
        return False

    def _credit(self, c, dom, credit, ep):
        for l in credit.get('lessons', ()):
            node = NODE_ID.get(tuple(l['node'])) if 'node' in l else law_node(l['law'])
            if node:
                self._lesson(c, dom, node, REASONS[l['reason']], SOURCES[l.get('source', 'judge')],
                             float(l.get('weight', 1.0)), float(l.get('gap', 0.0)), ep)
        for s in credit.get('skills', ()):
            law = law_node(s['law']) if s.get('law') is not None else 0
            self._skill(c, dom, law, s['program'], float(s.get('gain', 0.0)), ep, active=bool(s.get('active')),
                        source=SOURCES[s.get('source', 'judge')])
        for term, how in credit.get('vocab', ()):
            self._set_bit('known', term)
            if how == 'taught':
                self._set_bit('taught', term)
        heard = credit.get('sentences') or ()
        if heard and credit.get('named_law') is not None:
            self.lex['logp'][0] = W.learn(self.lexicon(), heard, credit['named_law']).astype(np.float32)
            for k, slot in enumerate(W.SLOTS):
                self.lex['heard'][0][k] += sum(1 for s, _ in heard if s == slot)

    def _anchor_for(self, c, dom):
        used = np.flatnonzero((self.anchors['used'] == 1) & (self.anchors['domain'] == dom))
        if used.size:
            d = [_dist(c, self.anchors['key'][i]) for i in used]
            j = int(np.argmin(d))
            if d[j] <= RADIUS:
                return int(used[j])
        # farther than RADIUS from every same-domain anchor: a new anchor, if one is free; an anchor of another
        # domain never takes the write
        others = np.flatnonzero(self.anchors['used'] == 1)
        if any(_dist(c, self.anchors['key'][i]) <= RADIUS and self.anchors['domain'][i] == dom for i in others):
            return None
        free = np.flatnonzero(self.anchors['used'] == 0)
        if not free.size:
            return None
        i = int(free[0])
        self.anchors['key'][i] = c
        self.anchors['domain'][i] = dom
        self.anchors['used'][i] = 1
        return i

    def _add_count(self, a, node, v):
        nodes, counts = self.anchors['node'][a], self.anchors['count'][a]
        hit = np.flatnonzero(nodes == node)
        if hit.size:
            counts[hit[0]] += np.float32(v)
            return
        free = np.flatnonzero(nodes == 0)
        j = int(free[0]) if free.size else int(np.argmin(counts))         # full: the weakest count gives way
        if not free.size and counts[j] >= v:
            return
        nodes[j], counts[j] = node, np.float32(v)

    def _lesson(self, c, dom, node, reason, source, weight, gap, ep, rival=0):
        for i, l in enumerate(self.lessons):                              # the same lesson here again: refreshed
            if (l['status'] == OPEN and l['domain'] == dom and l['law'] == node and l['reason'] == reason
                    and _dist(c, l['key']) <= RADIUS):
                self.lessons['weight'][i] = max(float(l['weight']), weight)
                self.lessons['gap'][i] = gap
                return
        free = np.flatnonzero(self.lessons['status'] != OPEN)             # an empty slot, then a resolved one,
        if free.size:                                                     # then the faintest open lesson gives way
            i = int(min(free, key=lambda j: (self.lessons['status'][j] == RESOLVED, j)))
        else:
            i = int(np.argmin(self.lessons['weight']))
        rec = np.zeros(1, LESSON)[0]
        rec['key'], rec['domain'], rec['status'], rec['reason'], rec['source'] = c, dom, OPEN, reason, source
        rec['law'], rec['rival'], rec['gap'], rec['weight'], rec['born'] = node, rival, gap, weight, ep
        self.lessons[i] = rec

    def _skill(self, c, dom, law, program, gain, ep, active=False, source=0):
        segs = list(program.segments)[:MAX_SEGMENTS]
        key = _seg_key(segs)
        arr = np.zeros((MAX_SEGMENTS, 3), np.float32)
        arr[:len(segs)] = segs
        for i, s in enumerate(self.skills):
            if (s['state'] and s['domain'] == dom and s['law'] == law and s['nseg'] == len(segs)
                    and _seg_key(s['seg'][:s['nseg']]) == key and _dist(c, s['key']) <= RADIUS):
                if s['last'] != ep:
                    self.skills['uses'][i] += 1
                    self.skills['last'][i] = ep
                    self.skills['gain'][i] = max(float(s['gain']), gain)
                if self.skills['uses'][i] >= ACTIVE_USES or active:
                    self.skills['state'][i] = ACTIVE
                return
        free = np.flatnonzero(self.skills['state'] == 0)
        i = int(free[0]) if free.size else int(np.argmin(np.where(self.skills['state'] == ACTIVE, np.inf,
                                                                  self.skills['gain'])))
        rec = np.zeros(1, SKILL)[0]
        rec['key'], rec['domain'], rec['state'], rec['nseg'] = c, dom, ACTIVE if active else CANDIDATE, len(segs)
        rec['law'], rec['uses'], rec['gain'], rec['last'], rec['seg'] = law, 1, gain, ep, arr
        rec['source'] = source
        self.skills[i] = rec

    # --- what it holds, for reports ---
    def summary(self):
        """Counts of what the memory holds now (for the observatory)."""
        open_ = self.lessons['status'] == OPEN
        by_reason = {}
        for l in self.lessons[open_]:
            name = next(k for k, v in REASONS.items() if v == int(l['reason']))
            by_reason[name] = by_reason.get(name, 0) + 1
        return dict(episode=self.episode, anchors=int(np.sum(self.anchors['used'])),
                    knowledge_counts=float(np.sum(self.anchors['count'])),
                    lessons_open=int(np.sum(open_)), lessons_by_reason=by_reason,
                    skills_active=int(np.sum(self.skills['state'] == ACTIVE)),
                    skills_candidate=int(np.sum(self.skills['state'] == CANDIDATE)),
                    vocab=len(self.vocab_terms()), vocab_taught=len(self.vocab_terms('taught')),
                    words_grounded=len(W.grounded(self.lexicon())))
