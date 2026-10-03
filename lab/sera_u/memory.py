"""Two observed-memory paths and S18 state decoding; no episode store for U/L."""
import copy
import hashlib
import math
import time
from collections import Counter

import numpy as np
import torch
from torch.nn import functional as F

from sera import lang as LG, phi as PH, tasks as TS
from .field.native_owner import detached_state
from .ports import TaskView

D = PH.IDEA_DIM
RESERVED = ('u-part', 'u-pair', 'u-context', 'u-total', 'hypothesis', 'standing-role')


def pair(a, b):
    return tuple(sorted((a, b), key=repr))


def context_pattern(kind, context, version='context-v1'):
    c = np.asarray(context, dtype=np.float64)
    if c.ndim != 1 or not np.isfinite(c).all():
        raise ValueError('Finite one-dimensional context required')
    scope = (kind, len(c), version)
    seed = int.from_bytes(hashlib.blake2b(repr((scope, 'context-frequencies')).encode('utf-8'),
                                        digest_size=8).digest(), 'little')
    omega = np.random.default_rng(seed).standard_normal((D//2, len(c)))
    phase = omega @ c
    z = np.empty(D, dtype=np.float64)
    z[::2], z[1::2] = np.cos(phase)/math.sqrt(D//2), np.sin(phase)/math.sqrt(D//2)
    return scope, z


def roles(ideas):
    # Encoder choice only: no evidence is cached outside _M.
    for nonce in range(1024):
        names = (('standing-role', ('support', nonce)), ('standing-role', ('refutation', nonce)))
        rows = [ideas._at(k) for k in names]             # first: meeting a role may enlarge (replace) _E
        a, b = (ideas._E[r].astype(np.float64) for r in rows)
        if abs(float(a @ b)/D) < .5:
            return names, a, b
    raise ValueError('Cannot construct independent standing roles')


def counts(ideas, key):
    row = ideas._row.get(key)
    if row is None:
        return 0, 0
    _, a, b = roles(ideas)
    m = ideas._M[row].astype(np.float64)
    same = a == b
    plus = float(np.mean(a[same]*m[same]))
    minus = float(np.mean(a[~same]*m[~same]))
    p, r = (plus+minus)/2, (plus-minus)/2
    if (not np.isfinite(m).all() or p < 0 or r < 0 or p != round(p) or r != round(r)
            or p+r > 2**24 or not np.array_equal(m, p*a+r*b)):
        raise ValueError('Malformed two-role state or standing capacity exceeded')
    return int(p), int(r)


def add_count(ideas, key, support=0, refutation=0):
    bridge = getattr(ideas, '_bridge', None)
    if bridge is not None and bridge.defer_b(add_count, ideas, key, support, refutation):
        return
    p, r = counts(ideas, key)
    if type(support) is not int or type(refutation) is not int or min(support, refutation) < 0:
        raise ValueError('Nonnegative integer role increments required')
    if p+r+support+refutation > 2**24:
        raise ValueError('Standing capacity exceeded: P+R > 2^24')
    names, _, _ = roles(ideas)
    ideas.bind(key, names[0], support*math.sqrt(D), perceived=False)
    ideas.bind(key, names[1], refutation*math.sqrt(D), perceived=False)


class ObservedIdeas(PH.Ideas):
    """Live callbacks are scoped by SeraU and excluded from saved state."""
    def __getstate__(self):
        d = super().__getstate__()
        d.pop('_bridge', None)
        return d

    def read(self, sentence, source=None):
        bridge = getattr(self, '_bridge', None)
        sentence = tuple(sentence)
        if any(isinstance(s, tuple) and s[0] in RESERVED for s in sentence):
            raise ValueError('Reserved S18 states cannot receive sentence writes')
        if bridge is None:
            return super().read(sentence, source)
        for j in range(0, len(sentence), 60):
            chunk = sentence[j:j+60]
            bridge.heard(chunk)
            if bridge.defer_b(PH.Ideas.read, self, chunk, source):
                continue
            if bridge.b:
                super().read(chunk, source)

    def _disabled(self):
        bridge = getattr(self, '_bridge', None)
        return bridge is not None and not bridge.b

    def evoked(self, *args, **kwargs):
        bridge = getattr(self, '_bridge', None)
        started = time.perf_counter() if bridge is not None and bridge.choosing else None
        result = [] if self._disabled() else super().evoked(*args, **kwargs)
        if started is not None:
            if result:
                things = args[0] if args else kwargs.get('things', ())
                bridge.touch_b(s for s in sorted(set(things), key=repr)
                               if s in self.of and s in self._row and self._rare(s) > 0.)
            bridge._read_cost(started)
        return result

    def comes_to_mind(self, *args, **kwargs):
        bridge = getattr(self, '_bridge', None)
        started = time.perf_counter() if bridge is not None and bridge.choosing else None
        result = [] if self._disabled() else super().comes_to_mind(*args, **kwargs)
        if started is not None:
            if result:
                things = args[0] if args else kwargs.get('things', ())
                bridge.touch_b(s for s in sorted(set(things), key=repr)
                               if s in self.of and s in self._row and self._rare(s) > 0.)
            bridge._read_cost(started)
        return result

    def _ring(self, *args, **kwargs):
        bridge = getattr(self, '_bridge', None)
        if bridge is not None and bridge.choosing and args:
            bridge.touch_b(s for s, weight in args[0] if weight > 0.)
        return [] if self._disabled() else super()._ring(*args, **kwargs)

    def kind(self, *args, **kwargs):
        return [] if self._disabled() else super().kind(*args, **kwargs)

    def bound(self, *args, **kwargs):
        return 0. if self._disabled() else super().bound(*args, **kwargs)

    def signed(self, *args, **kwargs):
        return (0., 0.) if self._disabled() else super().signed(*args, **kwargs)

    def role(self, s, ability):
        bridge = getattr(self, '_bridge', None)
        if bridge is not None:
            bridge.event('checked-role', (s, ability))
            if bridge.defer_b(PH.Ideas.role, self, s, ability):
                return None
        return None if self._disabled() else super().role(s, ability)

    def perceive_world(self, cues):
        cues = tuple(sorted(set(cues), key=repr))
        bridge = getattr(self, '_bridge', None)
        if bridge is not None:
            bridge.event('world-cues', cues)
            if bridge.defer_b(PH.Ideas.perceive_world, self, cues):
                return None
        return None if self._disabled() else super().perceive_world(cues)

    def consolidate(self, *args, **kwargs):
        bridge = getattr(self, '_bridge', None)
        if bridge is not None and bridge.defer_b(PH.Ideas.consolidate, self, *args, **kwargs):
            return 0
        result = 0 if self._disabled() else super().consolidate(*args, **kwargs)
        bridge = getattr(self, '_bridge', None)
        if result and bridge is not None:
            bridge.mind.proposer.changed()
        return result

    def redirect(self, *args, **kwargs):
        bridge = getattr(self, '_bridge', None)
        if bridge is not None and bridge.defer_b(PH.Ideas.redirect, self, *args, **kwargs):
            return True
        return True if self._disabled() else super().redirect(*args, **kwargs)

    def bind(self, thing, key, amount, *, perceived=True):
        bridge = getattr(self, '_bridge', None)
        if perceived and isinstance(thing, tuple) and thing[0] in RESERVED:
            raise ValueError('Reserved S18 states cannot receive association writes')
        if bridge is not None and perceived:
            bridge.event('binding', (thing, key, float(amount)))
            if bridge.defer_b(PH.Ideas.bind, self, thing, key, amount, perceived=perceived):
                return
            if not bridge.b:
                return
        return super().bind(thing, key, amount, perceived=perceived)

    def bind_pattern(self, thing, pattern, amount):
        bridge = getattr(self, '_bridge', None)
        if bridge is not None and bridge.defer_b(PH.Ideas.bind_pattern, self, thing,
                                                np.asarray(pattern).copy(), amount):
            return
        return super().bind_pattern(thing, pattern, amount)


class MemoryField(PH.Field):
    @classmethod
    def adopt(cls, field, enabled):
        previous = getattr(field, 'field_understanding', False)
        if enabled and not previous:
            field = copy.deepcopy(field)                # failure leaves the source usable
        field.__class__ = cls
        field.ideas.__class__ = ObservedIdeas
        if previous and not enabled:
            raise ValueError('Use a fresh history for understanding-off; U/L records were retired')
        field.field_understanding = enabled
        field.u_schema = dict(dim=D, context='context-v1', live_context='u2-public-v1',
                              frequency_seed='blake2b-64(scope,context-frequencies)',
                              roles='standing-role(support/refutation,nonce)', lifetime='cumulative',
                              capacity=2**24, numpy=np.__version__)
        if enabled and not previous:
            # One-time conversion: standing is migrated independently of U;
            # understand(proven=True) must not replay a second support count.
            events, standing = field.understood, field.standing
            for e in events:
                context = list(e['context'])
                version = 'context-v1'
                if e['kind'].startswith('exact:'):
                    version = 'u2-public-v1'
                    if len(context) == 7 and not e['kind'].startswith('exact:list(list)->'):
                        context[0] = 0.                 # retire Exact's private subject feature
                field._write_u(e['kind'], context, e['parts'], e['proven'], e['weight'], version)
            for h, (p, r) in sorted(standing.items(), key=lambda item: repr(item[0])):
                if (not isinstance(p, (int, np.integer)) or not isinstance(r, (int, np.integer))
                        or isinstance(p, bool) or isinstance(r, bool)):
                    raise ValueError('Legacy standing requires exact integer counts')
                add_count(field.ideas, ('hypothesis', h), int(p), int(r))
            del field.understood, field.standing
        return field

    def __getstate__(self):
        d = super().__getstate__()
        d.pop('_bridge', None)
        return d

    def _write_u(self, kind, context, parts, proven, weight, version='context-v1'):
        bridge = getattr(self, '_bridge', None)
        if bridge is not None and bridge.defer_b(self._write_u, kind, tuple(context), tuple(parts),
                                                proven, weight, version):
            return True
        if not math.isfinite(weight) or weight < 0:
            raise ValueError('Finite nonnegative understanding weight required')
        try:
            scope, z = context_pattern(kind, context, version)
        except (ValueError, TypeError):
            self.__dict__.setdefault('u_diagnostics', {}).setdefault('invalid_context', 0)
            self.u_diagnostics['invalid_context'] += 1
            return False
        ps = tuple(parts)
        increments = Counter(ps)
        pairs = Counter(pair(ps[i], ps[j]) for i in range(len(ps)) for j in range(i+1, len(ps)))
        # Validate totals before any mutation. Empty parts still count as an event.
        totals = ('u-total', scope)
        p, r = counts(self.ideas, totals)
        if p+r+1+int(proven) > 2**24:
            raise ValueError('Understanding total capacity exceeded')
        for part, n in sorted(increments.items(), key=lambda item: repr(item[0])):
            self.ideas.bind_pattern(('u-part', (scope, part)), z, weight*n)
        for pp, n in sorted(pairs.items(), key=lambda item: repr(item[0])):
            self.ideas.bind_pattern(('u-pair', (scope, pp)), z, weight*n)
        self.ideas.bind_pattern(('u-context', (scope, 'all')), z, 1.)
        if proven:
            self.ideas.bind_pattern(('u-context', (scope, 'credited')), z, 1.)
        add_count(self.ideas, totals, 1, int(proven))
        return True

    def familiarity(self, kind, context, query_parts=None, query_pairs=None, *, version='context-v1'):
        if not self.field_understanding:
            return super().familiarity(kind, context)
        bridge = getattr(self, '_bridge', None)
        if bridge is not None and not bridge.b:
            return {}, {}
        try:
            scope, z = context_pattern(kind, context, version)
        except (ValueError, TypeError):
            return {}, {}
        if query_parts is None:
            query_parts = [k[1][1] for k in self.ideas._row if isinstance(k, tuple) and k[0] == 'u-part' and k[1][0] == scope]
        if query_pairs is None:
            query_pairs = [k[1][1] for k in self.ideas._row if isinstance(k, tuple) and k[0] == 'u-pair' and k[1][0] == scope]
        parts = {p: max(0., self.ideas.project_pattern(('u-part', (scope, p)), z)) for p in query_parts}
        pairs = {tuple(sorted((repr(a), repr(b)))):
                 max(0., self.ideas.project_pattern(('u-pair', (scope, pair(a, b))), z)) for a, b in query_pairs}
        return parts, pairs

    def context_density(self, kind, context, which='all', *, version='context-v1'):
        """S18's mean kernel density, read from context state and role totals."""
        if which not in ('all', 'credited'):
            raise ValueError('Choose all or credited context density')
        if not self.field_understanding:
            raise ValueError('Context density requires the S18 state schema')
        bridge = getattr(self, '_bridge', None)
        if bridge is not None and not bridge.b:
            return 0.
        try:
            scope, z = context_pattern(kind, context, version)
        except (TypeError, ValueError):
            return 0.
        total = counts(self.ideas, ('u-total', scope))[int(which == 'credited')]
        if not total:
            return 0.
        value = self.ideas.project_pattern(('u-context', (scope, which)), z)/total
        return float(np.clip(value, 0., 1.))

    def standing_counts(self, h):
        bridge = getattr(self, '_bridge', None)
        if bridge is not None and not bridge.b:
            return 0, 0
        return counts(self.ideas, ('hypothesis', h))

    def layers(self, kind, context, hyps, log_evidence, bits):
        if not self.field_understanding:
            return super().layers(kind, context, hyps, log_evidence, bits)
        bridge = getattr(self, '_bridge', None)
        version = 'context-v1'
        if bridge is not None and bridge.current is not None:
            kind, context = bridge.context or public_context(bridge.current)
            version = 'context-v1' if bridge.current.form == 'strengths' else 'u2-public-v1'
        requested = tuple(dict.fromkeys(p for ps in hyps.values() for p in ps))
        requested_pairs = tuple(dict.fromkeys(pair(ps[i], ps[j]) for ps in hyps.values()
                                              for i in range(len(ps)) for j in range(i+1, len(ps))))
        parts, pairs = self.familiarity(kind, context, requested, requested_pairs, version=version)
        neural = bridge.neural(requested, requested_pairs) if bridge is not None and bridge.a else {}
        alpha = bridge.mix() if bridge is not None else 0.
        logL, ub, ua = {}, {}, {}
        for h, ps in hyps.items():
            def familiar(values, paired):
                u = sum(math.log1p(values.get(p, 0.)) for p in ps)
                for i in range(len(ps)):
                    for j in range(i+1, len(ps)):
                        u += PH.PAIR_POWER*math.log1p(paired.get(tuple(sorted((repr(ps[i]), repr(ps[j])))), 0.))/max(len(ps)-1, 1)
                return u
            p, r = self.standing_counts(h)
            logL[h] = -bits[h]*math.log(2)+math.log1p(p)-math.log1p(r)
            ub[h] = familiar(parts, pairs)
            ua[h] = familiar(neural.get('parts', {}), neural.get('pairs', {}))
        logL = PH.normalize(logL)
        def understanding(f):
            raw = PH.normalize({h: f[h]+logL[h] for h in hyps})
            return PH.normalize({h: float(np.logaddexp(math.log(1-PH.ETA)+raw[h], math.log(PH.ETA)+logL[h])) for h in hyps})
        b, a = understanding(ub), understanding(ua)
        if alpha == 0.:
            u = b
        elif alpha == 1.:
            u = a
        else:
            u = PH.normalize({h: float(np.logaddexp(math.log1p(-alpha)+b[h], math.log(alpha)+a[h])) for h in hyps})
        evidence = PH.normalize(log_evidence)
        return u, logL, evidence, PH.pool(u, logL, evidence), PH.kl(evidence, u)

    def understand(self, kind, context, key, parts, proven, weight, task, where=None):
        bridge = getattr(self, '_bridge', None)
        if not self.field_understanding:
            result = super().understand(kind, context, key, parts, proven, weight, task, where)
        else:
            if not math.isfinite(weight) or weight < 0:
                raise ValueError('Finite nonnegative understanding weight required')
            # Validate standing before writing U; authority remains outside this state.
            if proven:
                p, r = self.standing_counts(key)
                if p+r == 2**24:
                    raise ValueError('Standing capacity exceeded')
            version = 'context-v1'
            if bridge is not None and bridge.current is not None:
                kind, context = bridge.context or public_context(bridge.current)
                version = 'context-v1' if bridge.current.form == 'strengths' else 'u2-public-v1'
            if bridge is None or bridge.store_b:
                self._write_u(kind, context, parts, proven, weight, version)
                if proven:
                    add_count(self.ideas, ('hypothesis', key), support=1)
            result = None
        if bridge is not None:
            bridge.event('checked-proof' if proven else 'tentative-association', (key, tuple(parts)),
                         progress=1. if proven else None)
            if proven:
                bridge.checked_parts.extend(parts)
        return result

    def refute(self, key):
        if not self.field_understanding:
            result = super().refute(key)
        else:
            bridge = getattr(self, '_bridge', None)
            if bridge is None or bridge.store_b:
                add_count(self.ideas, ('hypothesis', key), refutation=1)
            result = None
        bridge = getattr(self, '_bridge', None)
        if bridge is not None:
            bridge.event('refutation', key, progress=-1.)
        return result

    def answer(self, qid, verdict, words=()):
        if not self.field_understanding:
            result = super().answer(qid, verdict, words)
        else:
            q = next((q for q in self.inbox if q['id'] == qid), None)
            if q is None or qid in self.answers:
                return False
            words = [str(w) for w in words]
            self.answers[qid] = dict(verdict=verdict, words=words, at=self.tasks,
                                     understood={w: self.lexicon.understand(w) for w in words})
            bridge = getattr(self, '_bridge', None)
            if q.get('key') is not None:
                if verdict == 'right':
                    if bridge is None or bridge.store_b:
                        add_count(self.ideas, ('hypothesis', q['key']), support=1)
                    if words and q.get('meanings'):
                        self.lexicon.hear(words, q['meanings'])
                elif verdict == 'wrong':
                    self.refute(q['key'])
            if words and verdict == 'hint':
                self.__dict__.setdefault('hints', {}).setdefault(q.get('kind'), []).extend(words)
            result = True
        bridge = getattr(self, '_bridge', None)
        if result and bridge is not None:
            bridge.event('teacher-verdict', (verdict, tuple(words)))
        return result

    def digest(self):
        if not self.field_understanding:
            return super().digest()
        sha = hashlib.sha256(repr((self.u_schema, self.concepts,
                                 sorted(getattr(self, 'audited', {}).items(), key=repr))).encode())
        sha.update(repr(tuple(self.ideas._row.items())).encode())
        sha.update(self.ideas._E[:self.ideas._n].tobytes())
        sha.update(self.ideas._M[:self.ideas._n].tobytes())
        return sha.hexdigest()[:16]

    def account(self):
        if not self.field_understanding:
            return super().account()
        by = Counter(c['subject'] for c in self.concepts)
        totals = {repr(k[1]): dict(zip(('all', 'credited'), counts(self.ideas, k)))
                  for k in self.ideas._row if isinstance(k, tuple) and k[0] == 'u-total'}
        return dict(tasks=self.tasks, concepts=len(self.concepts), concepts_by_subject=dict(by),
                    words=len(self.lexicon.heard), grounded=len(self.lexicon.grounded()), coined=len(self.lexicon.coined),
                    understanding_events=totals, state_rows=self.ideas._n,
                    state_bytes=self.ideas._M[:self.ideas._n].nbytes+self.ideas._E[:self.ideas._n].nbytes,
                    understanding_part_rows=sum(isinstance(k, tuple) and k[0] == 'u-part' for k in self.ideas._row),
                    standing_rows=sum(isinstance(k, tuple) and k[0] == 'hypothesis' for k in self.ideas._row),
                    possibilities=len(self.possibilities), links=len(self.links), questions=len(self.questions), inbox=len(self.inbox))


def memory_records(view):
    # U2 streams all observed events; individual values retain U1's size limits.
    return view.records(max_examples=max(4, len(view.examples)), max_records=None)


def public_context(view):
    """Public schema/size senses, versioned because Exact.context includes subject."""
    kind = f"{view.form}:{','.join(sorted(t for _, t in view.inputs))}->{view.out}"
    def size(x):
        if isinstance(x, (list, tuple, str)):
            return len(x)
        return abs(x) if type(x) in (int, float, bool) else 0.
    if view.form == 'strengths':
        motion, pushes = {}, {}
        for row in view.measurements:
            if row[0] == 'motion':
                _, obj, index, t, x, v = row
                motion.setdefault(index, []).append((obj, t, x, v))
            elif row[0] == 'push':
                _, index, start, end, force = row
                pushes.setdefault(index, []).append((start, end, force))
        objects = sorted({r[0] for rows in motion.values() for r in rows})
        observations = []
        # Same first two throws per object count as Rail.context, computed only
        # from the public motions/commands, without reading world.masses/spec.
        for index in sorted(motion)[:2*len(objects)]:
            rows = sorted(motion[index], key=lambda row: row[1])
            for left, right in zip(rows, rows[1:]):
                obj, t0, x0, v0 = left
                _, t1, x1, v1 = right
                from ccops5.core import paths
                dt = paths.DT_OBS
                force = sum(f*max(0., min(t0+dt, b)-max(t0, a))/dt for a, b, f in pushes.get(index, ()))
                observations.append((obj, (v1-v0)/dt, force, .5*(x0+x1), .5*(v0+v1), .5*(t0+t1)))
        if not observations:
            return kind, (0.,)*7
        obj, y, fb, xb, vb, tb = np.asarray(observations, dtype=np.float64).T
        residual = []
        for o in np.unique(obj):
            mask = obj == o
            mu = float(fb[mask] @ y[mask]/max(fb[mask] @ fb[mask], 1e-12))
            residual.append(y[mask]/max(mu, 1e-6)-fb[mask])
        residual = np.concatenate(residual)
        # Match Rail.context's grouping order for all coordinates.
        order = np.concatenate([np.flatnonzero(obj == o) for o in np.unique(obj)])
        xb, vb, tb = xb[order], vb[order], tb[order]
        corr = lambda a: float(np.corrcoef(a, residual)[0, 1]) if np.std(a) > 1e-12 and np.std(residual) > 1e-12 else 0.
        return kind, (corr(xb), corr(vb), corr(tb), corr(np.abs(vb)),
                      float(np.log10(np.std(residual)+1e-9)), float(np.max(np.abs(xb))), float(np.max(np.abs(vb))))
    xs = [v for bindings, _ in view.examples for _, v in bindings]
    ys = [y for _, y in view.examples]
    mean = lambda values: float(np.mean(values)) if values else 0.
    if len(view.inputs) == 1 and view.inputs[0][1] == 'list(list)' and view.out == 'list(list)':
        shape = lambda grid: (len(grid), len(grid[0]) if grid else 0)
        kinds = lambda grid: len({cell for row in grid for cell in row})
        rows = [(shape(x), shape(y), kinds(x), kinds(y)) for x, y in zip(xs, ys)]
        m = lambda f: mean([f(row) for row in rows])
        return kind, (m(lambda p: math.log2((p[1][0]+1)/(p[0][0]+1))),
                      m(lambda p: math.log2((p[1][1]+1)/(p[0][1]+1))),
                      m(lambda p: float(p[0] == p[1])), m(lambda p: p[0][0]/30),
                      m(lambda p: p[0][1]/30), m(lambda p: p[2]/10), m(lambda p: p[3]/10))
    if view.inputs == (('g', 'list(list)'),):
        # Story's existing input-only context. Numeric word IDs are raw senses.
        kinds = [len({w for sentence in x for w in sentence}) for x in xs]
        shared = [mean([float(any(w in sentence for sentence in x[1:])) for w in x[0]]) if x else 0. for x in xs]
        return kind, (mean([max(0, len(x)-1) for x in xs])/10,
                      mean([mean([len(sentence) for sentence in x[1:]]) for x in xs])/10,
                      mean([len(x[0]) if x else 0 for x in xs])/10,
                      float(view.out == 'list'), mean(kinds)/30, mean(shared), 0.)
    return kind, (0., float(view.out == 'list'), mean([size(y) for y in ys])/10,
                  mean([size(x) for x in xs])/10,
                  mean([float(type(y) in (int, float) and y < 0) for y in ys]), 0., 0.)


class Memory:
    """Transient orchestration. All retained learning lives in the owner/Field."""
    def __init__(self, mind):
        self.mind = mind
        self.current = None
        self.context = None
        self.checked_parts = []
        self.seen_records = Counter()
        self._feature_cache = {}          # bounded no-grad reads; never serialized
        self._feature_rings = {}
        self._feature_versions = {}
        self._ring_cache = {}
        self._record_cache = {}
        self._prepared = None
        self.reset_choice()

    def reset_choice(self):
        self.choosing = False
        self.committing = False
        self.selected = (False, False)
        self.pending = []
        self.consults = []
        self.touched = set()
        self.item_started = None
        self.item_wall = float('inf')
        self.item_phase = 'world'
        self.feedback = None
        self.time_to_right = None
        self.read_seconds = 0.
        self.cue_read = False

    @property
    def choice_on(self):
        return self.mind.crutches.get('memory_choice', False)

    @property
    def store_b(self):
        # Writes are buffered independently of the consulted layers.
        return self.mind.crutches['memory_layer_b'] if self.choosing and not self.committing else self.b

    def defer_b(self, function, *args, **kwargs):
        if not self.choosing or self.committing:
            return False
        if self.mind.crutches['memory_layer_b']:
            self.pending.append(('b', function, copy.deepcopy(args[1:]) if args and args[0] is self.mind.field.ideas
                                 else copy.deepcopy(args), copy.deepcopy(kwargs),
                                 bool(args and args[0] is self.mind.field.ideas)))
        return True

    def start_choice(self, view, *, wall, phase, started=None):
        self.reset_choice()
        self.choosing = True
        self.item_started = time.perf_counter() if started is None else started
        self.item_wall, self.item_phase = wall, phase
        self.begin(view)
        self.consult(view, moment='start')

    def _plain_features(self, view):
        # The cue read has an empty retained state and no ring. Layer keys keep
        # it separate from every actual consulted read, including US3 caches.
        selected = self.selected
        self.selected = (False, False)
        self.cue_read = True
        try:
            with torch.no_grad():
                f, _, _ = self.features(view)
                spent = ((time.perf_counter()-self.item_started)/max(self.item_wall, 1e-6)
                         if math.isfinite(self.item_wall) else 0.)
                return PH.MemoryChoice.features(f.detach().cpu().numpy(), spent)
        finally:
            self.selected = selected
            self.cue_read = False

    def consult(self, view, *, moment='ways'):
        if not self.choosing or self.committing:
            return
        started = time.perf_counter()
        f = self._plain_features(view)
        kind = public_context(view)[0]
        head = self.mind.field.memory_choice
        available = head.options(self.mind.crutches['memory_layer_a'], self.mind.crutches['memory_layer_b'])
        option, values = head.pick(kind, 'consult', f, available, self.mind.numpy)
        self.selected = head.LAYERS[option]
        self.consults.append(dict(kind=kind, option=option, f=f, values=values, moment=moment,
                                  seconds=time.perf_counter()-started, read_seconds=0.))

    def _touch(self, view):
        if not self.choosing or self.committing or not any(self.selected):
            return
        # A is an aggregate: every tracked earlier A write is eligible. B's
        # actual nonzero presses are captured in _compute_ring, including A cues.
        for e in self.mind.field.memory_choice.eligible:
            if self.a and PH.MemoryChoice.LAYERS[e['option']][0]:
                self.touched.add(e['id'])

    def touch_b(self, things):
        if self.choosing and not self.committing and self.b:
            pressed = set(things)
            for e in self.mind.field.memory_choice.eligible:
                if PH.MemoryChoice.LAYERS[e['option']][1] and pressed.intersection(e['tokens']):
                    self.touched.add(e['id'])

    def _read_cost(self, started):
        if self.choosing and not self.committing and not self.cue_read:
            seconds = time.perf_counter()-started
            self.read_seconds += seconds
            if self.consults:
                self.consults[-1]['read_seconds'] += seconds

    def finish_choice(self, view, *, right):
        head = self.mind.field.memory_choice
        started = time.perf_counter()
        f = self._plain_features(view)
        kind = public_context(view)[0]
        option, values = head.pick(kind, 'remember', f,
            head.options(self.mind.crutches['memory_layer_a'], self.mind.crutches['memory_layer_b']), self.mind.numpy)
        self.selected = head.LAYERS[option]
        self.committing = True
        tokens = set()
        rows = [entry[1] for entry in self.pending if entry[0] == 'row']
        # US2's exact-length encoder batching, followed by the same sequential
        # observations. B callbacks cannot allocate native owner token IDs.
        sources = iter(self.encode_rows(rows)) if self.a and rows else None
        for entry in self.pending:
            if entry[0] == 'row':
                _, row, progress, write_b = entry
                tokens.update(t[0] for t in row)
                if self.a or self.b:
                    self.write_record(row, progress=progress, write_b=write_b,
                                      source=next(sources) if sources is not None else None)
            elif self.b:
                _, function, args, kwargs, ideas_first = entry
                call_args = (self.mind.field.ideas, *args) if ideas_first else args
                function(*call_args, **kwargs)
        seconds = time.perf_counter()-started
        total = time.perf_counter()-self.item_started
        # A received verdict (including test2's bit) can override proof credit;
        # test3 receives no observer feedback. Assessments train only their clone.
        right = bool(right if self.feedback is None else self.feedback)
        rate = float(np.clip(float(right)/max(total, 1e-6), 0., 20.))
        for row in self.consults:
            cost = row['seconds'] + row['read_seconds']
            head.learn(row['kind'], 'consult', row['option'], row['f'], rate-cost)
        head.learn(kind, 'remember', option, f, -seconds)
        credited = head.later_return(self.touched, right, total)
        head.retain(kind, option, f, tokens, public_context(view)[1])
        head.end_item()
        def learned(k, decision, feature):
            return {o: float(head.posterior(k, decision, o)[0] @ feature)
                    for o in head.options(self.mind.crutches['memory_layer_a'], self.mind.crutches['memory_layer_b'])}
        report = dict(consult=[dict(option=r['option'], moment=r['moment'], seconds=r['seconds'],
                                    read_seconds=r['read_seconds'], values=r['values'],
                                    learned=learned(r['kind'], 'consult', r['f'])) for r in self.consults],
                      remember=dict(option=option, seconds=seconds, values=values,
                                    learned=learned(kind, 'remember', f)),
                      seconds=total, read_seconds=self.read_seconds, right=right,
                      touched=sorted(self.touched), credited=credited, eligibility='not causal proof',
                      taken=copy.deepcopy(head.taken))
        report['learning_seconds'] = time.perf_counter()-self.item_started-total
        report['seconds'] = time.perf_counter()-self.item_started
        self.reset_choice()
        return report

    def clear_reads(self):
        self._feature_cache.clear()
        self._feature_rings.clear()
        self._feature_versions.clear()
        self._ring_cache.clear()
        self._record_cache.clear()

    def records(self, view):
        if view not in self._record_cache:
            if len(self._record_cache) >= 32:
                self._record_cache.clear()
            self._record_cache[view] = memory_records(view)
        return self._record_cache[view]

    @staticmethod
    def _state_fingerprint(items):
        # Retained states are replaced on every observation, and a freed tensor's id/address/version are reused by
        # the next one, so the state is keyed by its content, never its identity (a reused id made a stale ring look
        # current: US2's resume test, 2026-10-03). The state is small; parameters and Ideas keep their counters.
        out = []
        for key, value in items:
            t = value.detach().cpu().contiguous()
            out.append((key, t.dtype, tuple(t.shape),
                        hashlib.blake2b(t.numpy().tobytes(), digest_size=16).hexdigest()))
        return tuple(out)

    @staticmethod
    def _tensor_versions(items):
        from .proposer import FieldOwner
        return FieldOwner.content_key(items)

    def _read_version(self, *, ring_only=False):
        owner, ideas = self.mind.owner, self.mind.field.ideas
        # All supported Ideas state writes advance rev. _at/_idea can introduce
        # rows/membership without a write, so include their structural content.
        # gen is the Ideas ledger's persistent nonce, not an allocator ID. Native
        # writes advance rev; owner/state content also catches tensor replacement.
        vocabulary = () if ring_only else (owner.port_enabled, tuple(sorted(owner.token_ids.items())))
        return (self.a, self.b, vocabulary, tuple(sorted(vars(owner.config).items())),
                tuple((name, module.training) for name, module in owner.named_modules()),
                ideas.gen, ideas.rev, ideas._n, tuple(ideas._row.items()), tuple(sorted(ideas.of, key=repr)),
                self._state_fingerprint(self.mind.state.items()) if self.a else (),
                self._tensor_versions(owner.named_parameters()),
                self._tensor_versions(owner.named_buffers()))

    @property
    def a(self):
        if self.choosing:
            return self.mind.crutches['memory_layer_a'] and self.selected[0]
        return self.mind.crutches['memory_layer_a']

    @property
    def b(self):
        if self.choosing:
            return self.mind.crutches['memory_layer_b'] and self.selected[1]
        return self.mind.crutches['memory_layer_b']

    def event(self, kind, content, *, progress=None, imagined=False):
        if imagined:
            return
        text = repr((kind, content))
        # B's native sentence place budget is 63; retain every chunk.
        tokens = tuple(text[j:j+32] for j in range(0, len(text), 32))
        for j in range(0, len(tokens), 60):
            row = (('role:'+kind, 0., 0., 1.),)+tuple((w, 0., 0., 1.) for w in tokens[j:j+60])
            self.write_record(row, progress=progress)

    def heard(self, sentence):
        # Called by ObservedIdeas.read: its caller supplies genuinely heard text.
        tokens = tuple(TS.text(s) if isinstance(s, int) else str(s) for s in sentence)
        for j in range(0, len(tokens), 60):
            self.write_record((('role:heard', 0., 0., 1.),)+tuple((w, 0., 0., 1.) for w in tokens[j:j+60]),
                              write_b=False)

    def write_record(self, row, *, progress=None, write_b=True, source=None):
        if self.choosing and not self.committing:
            self.pending.append(('row', tuple(row), progress, write_b))
            return
        owner = self.mind.owner
        with torch.no_grad():
            state = self.mind.state
            if self.a:
                if source is None:
                    source = owner.encode_record(row) if owner.port_enabled else owner.encode_texts([' '.join(t[0] for t in row)])
                checked = None if progress is None else source.new_tensor([progress])
                state, diagnostics = owner.observe(state, source, checked_progress=checked)
                if self.mind.crutches.get('gap_syndromes'):
                    # Actual Field measurement before updating its typical value.
                    self.mind.field.curiosity.observe(row[0][0], float(diagnostics['energy_defect'].mean()))
            if self.b and write_b:
                tokens = tuple(t[0] for t in row)
                for j in range(0, len(tokens), 60):
                    PH.Ideas.read(self.mind.field.ideas, tokens[j:j+60])
            if self.a:
                self.mind.state = detached_state(state)
                self.mind.proposer.retained = self.mind.state
        self.mind.proposer.changed()

    def begin(self, view):
        if type(view) is not TaskView:
            raise TypeError('Only public TaskView observations can enter memory')
        if self._prepared == view:
            self._prepared = None
            return
        self.clear_reads()
        self.current, self.seen_records, self.checked_parts = view, Counter(), []
        self.context = public_context(view)
        self.refresh(view)

    def refresh(self, view):
        if type(view) is not TaskView:
            raise TypeError('Only public TaskView observations can enter memory')
        now = Counter(self.records(view))
        # Counter insertion order is the original first-occurrence schedule,
        # including nonadjacent duplicate measurements and newly grown views.
        schedule = [row for row, count in now.items()
                    for _ in range(max(0, count-self.seen_records[row]))]
        with torch.no_grad():
            sources = (self.encode_rows(schedule) if self.a and schedule and
                       not (self.choosing and not self.committing) else [None]*len(schedule))
            for row, source in zip(schedule, sources):
                self.write_record(row, source=source)
                self.seen_records[row] += 1
        self.current = view

    def encode_rows(self, rows):
        owner = self.mind.owner
        sources = (owner.encode_records(rows) if owner.port_enabled else
                   owner.encode_texts([' '.join(t[0] for t in row) for row in rows]))
        return list(sources.split(1))

    def ring(self, view):
        if not self.b:
            return None
        version = self._read_version(ring_only=True)
        key = (view, self.a, self.b) if self.choice_on else view
        cached = self._ring_cache.get(key)
        if cached is not None and cached[0] == version:
            return cached[1]
        result = self._compute_ring(view)
        if len(self._ring_cache) >= 32:
            self._ring_cache.clear()
        self._ring_cache[key] = (version, result)
        return result

    def _compute_ring(self, view):
        """Uncached reference; preserve row chunks and float64 reduction order."""
        owner, ideas = self.mind.owner, self.mind.field.ideas
        if not self.b:
            return None
        weights = Counter(t[0] for row in memory_records(view) for t in row)
        pattern = np.zeros(D, np.float64)
        reverse = None
        if self.a:
            with torch.no_grad():
                settled = owner.remembered(self.mind.state).flatten(1)
                reverse = owner.memory_projection.weight.T @ settled[0]
                reverse = reverse.cpu().numpy().astype(np.float64)
        # Structural row order is deterministic; unlike of's order it is not
        # determined by the legacy reader's set iteration. Bound scratch space.
        def press(batch):
            nonlocal pattern
            rows = [row for thing, row in batch]
            w = np.asarray([weights.get(thing, 0) for thing, row in batch], dtype=np.float64)
            if reverse is not None:
                w += np.maximum(0., ideas._E[rows].astype(np.float64) @ reverse/math.sqrt(D))
            if self.choosing and not self.committing:
                pressed = {thing for (thing, _), weight in zip(batch, w) if weight != 0.}
                for e in self.mind.field.memory_choice.eligible:
                    if PH.MemoryChoice.LAYERS[e['option']][1] and pressed.intersection(e['tokens']):
                        self.touched.add(e['id'])
            if np.any(w):
                pattern += w @ ideas._M[rows].astype(np.float64)
        batch = []
        for thing, row in ideas._row.items():
            if thing not in ideas.of:
                continue                                # excludes synthetic U/L rows
            batch.append((thing, row))
            if len(batch) == 256:
                press(batch)
                batch = []
        if batch:
            press(batch)
        scale = max(1., float(np.linalg.norm(pattern)))
        return owner.words.weight.new_tensor(pattern/scale)

    def features(self, view, *, grow=True):
        started = time.perf_counter()
        self._touch(view)
        key = self.read_key(view, grow)
        version = self._read_version()
        cached = self._feature_cache.get(key) if not torch.is_grad_enabled() else None
        ring = self.ring(view)
        if cached is not None:
            previous = self._feature_rings[key]
            # Legacy alias/association writes can change B without a native event.
            # Reuse only if the actual ringing supplied to this read is unchanged.
            same_ring = (ring is None and previous is None) or (
                ring is not None and previous is not None and torch.equal(ring, previous))
            if same_ring and self._feature_versions.get(key) == version:
                self._read_cost(started)
                return cached
            self._feature_cache.pop(key)
            self._feature_rings.pop(key)
            self._feature_versions.pop(key, None)
        state = self.mind.state if self.a else self.mind.owner.empty(1)
        read = self.mind.owner.task_features(view, grow=grow, state=state, ring=ring, memory_read=True)
        # Cache only versioned rings. An external/ad-hoc ring provider must
        # retain the old equality-check-and-reread behavior on a changed ring.
        ring_key = (view, self.a, self.b) if self.choice_on else view
        versioned_ring = ring is None or self._ring_cache.get(ring_key, (None, None))[1] is ring
        if not torch.is_grad_enabled() and versioned_ring:
            self.cache_read(view, grow, read, ring)
        self._read_cost(started)
        return read

    def read_key(self, view, grow):
        return (view, grow, self.a, self.b) if self.choice_on else (view, grow)

    def cache_read(self, view, grow, read, ring):
        if len(self._feature_cache) >= 32:
            self._feature_cache.clear()
            self._feature_rings.clear()
            self._feature_versions.clear()
        key = self.read_key(view, grow)
        self._feature_cache[key] = read
        self._feature_rings[key] = None if ring is None else ring.detach().clone()
        self._feature_versions[key] = self._read_version()

    def features_many(self, views, *, grow=True):
        started = time.perf_counter()
        views = tuple(views)
        if not views:
            return []
        owner = self.mind.owner
        # Deduplicate in first-occurrence order. Autograd reads never enter a
        # persistent cache: each training call builds a fresh shared graph.
        unique, ready, pending, rings = list(dict.fromkeys(views)), {}, [], []
        version = self._read_version()
        for view in unique:
            self._touch(view)
            key, ring = self.read_key(view, grow), self.ring(view)
            cached = self._feature_cache.get(key) if not torch.is_grad_enabled() else None
            previous = self._feature_rings.get(key)
            same_ring = (ring is None and previous is None) or (
                ring is not None and previous is not None and torch.equal(ring, previous))
            if cached is not None and same_ring and self._feature_versions.get(key) == version:
                ready[view] = cached
            else:
                pending.append(view)
                rings.append(ring)
        if pending:
            states = [self.mind.state if self.a else owner.empty(1) for _ in pending]
            reads = owner.read_features_many(pending, grow=grow, states=states,
                                            rings=rings, memory_read=True,
                                            context=('memory', self.a, self.b))
            for view, ring, read in zip(pending, rings, reads):
                ready[view] = read
                if not torch.is_grad_enabled():
                    self.cache_read(view, grow, read, ring)
        self._read_cost(started)
        return [ready[view] for view in views]

    def neural(self, parts, pairs):
        if self.current is None:
            return {}
        with torch.no_grad():
            features, weights, _ = self.features(self.current)
            keys = tuple(('part', p) for p in parts)+tuple(('pair', pp) for pp in pairs)
            values = self.mind.owner.familiarity_readout(features, weights, keys).cpu().tolist()
        return dict(parts=dict(zip(parts, values[:len(parts)])),
                    pairs={tuple(sorted((repr(a), repr(b)))): v for (a, b), v in zip(pairs, values[len(parts):])})

    def mix(self):
        if not self.a:
            return 0.
        if not self.b:
            return 1.
        return float(self.mind.owner.understanding_mix.detach().clamp(0., 1.))

    def checked_loss(self, view, parts, *, read=None):
        if not self.mind.crutches['field_understanding'] or not self.a or not parts:
            return self.mind.owner.understanding_mix.new_zeros(())
        parts = tuple(dict.fromkeys(parts))
        pp = tuple(pair(parts[i], parts[j]) for i in range(len(parts)) for j in range(i+1, len(parts)))
        keys = tuple(('part', p) for p in parts)+tuple(('pair', p) for p in pp)
        kind, context = public_context(view)
        version = 'context-v1' if view.form == 'strengths' else 'u2-public-v1'
        bparts, bpairs = self.mind.field.familiarity(kind, context, parts, pp, version=version)
        targets = [math.log1p(bparts.get(p, 0.)) for p in parts]
        targets += [math.log1p(bpairs.get(tuple(sorted((repr(a), repr(b)))), 0.)) for a, b in pp]
        features, weights = self.features(view)[:2] if read is None else read
        predicted = self.mind.owner.familiarity_readout(features, weights, keys).log1p()
        # If B is ablated, checked participation itself supplies the unit target.
        target = predicted.new_tensor(targets) if self.b else torch.ones_like(predicted)*math.log(2)
        error = F.mse_loss(predicted, target)
        reliability = torch.exp(-error.detach())
        gate = self.mind.owner.understanding_mix.clamp(0., 1.)
        return error+(gate-reliability).square()

    def rank(self, view, programs, concepts, *, partial=False):
        if not self.mind.crutches['field_understanding'] or not programs:
            return programs
        def parts(p):
            if p[0] == '@hole':
                return ()
            tag = ('concept', p[1]) if p[0] == 'c' else ('var', p[1]) if p[0] == 'var' else ('sym', p[0])
            head = () if p[0] == 'lam' else (tag,)
            return tuple(dict.fromkeys(head+tuple(t for q in reversed(p[2:]) for t in parts(q))))
        def bits(p):
            if p[0] == '@hole':
                return 0.
            if not partial:
                return LG.bits(p, [0]*sum(k != '_sig' for k in concepts))
            def prefix(q, inside=False):
                if q[0] == '@hole':
                    return 0
                extra = int(q[0] == 'var' and inside and q[1] not in ('e', 'i', 'a'))
                return 1+extra+sum(prefix(child, inside or q[0] == 'lam') for child in q[2:])
            return prefix(p)*math.log2(LG.alphabet_size([0]*sum(k != '_sig' for k in concepts)))
        hparts = {p: parts(p) if partial else LG.parts(p) for p in programs}
        evidence = {p: 0. if partial else -TS.MISS_NATS*sum(
            LG.safe(p, dict(bindings), concepts) != y for bindings, y in view.examples) for p in programs}
        before = self.current
        self.current = view
        try:
            kind, c = public_context(view)
            _, _, _, phi, _ = self.mind.field.layers(kind, c, hparts, evidence, {p: bits(p) for p in programs})
        finally:
            self.current = before
        return sorted(programs, key=lambda p: (-phi[p], repr(p)))


class BranchReadGate:
    """Chosen-layer reads in a disposable imagination Field; writes stay local.

    The normal live bridge cannot be attached here: it would record imagined
    events as public facts. This facade forwards only reads and their charges.
    """
    choosing = True

    def __init__(self, source):
        self.source = source
        self.current, self.context = source.current, source.context
        self.checked_parts = []
        # ObservedIdeas.consolidate may invalidate its bridge's proposer. A
        # branch's local changes must not invalidate the real search history.
        self.mind = self.proposer = self

    @property
    def a(self):
        return self.source.a

    @property
    def b(self):
        return self.source.b

    @property
    def store_b(self):
        return self.b

    def defer_b(self, *args, **kwargs):
        return False

    def event(self, *args, **kwargs):
        pass

    heard = changed = event

    def touch_b(self, things):
        self.source.touch_b(things)

    def _read_cost(self, started):
        self.source._read_cost(started)

    def neural(self, parts, pairs):
        return self.source.neural(parts, pairs)

    def mix(self):
        return self.source.mix()
