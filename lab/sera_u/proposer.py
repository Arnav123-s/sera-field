"""Typed recognition from the same CoreOwner, before enumeration combinations."""
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import math
import time

import torch
from torch import nn

from sera import lang as LG, crutches as CR
from .field.core_owner import CoreOwner
from .field.native_owner import NativeOwner
from .field.unified_energy import UnifiedEnergy
from .ports import PortBudget, TaskView, digest


class _ReadGeometryEnergy(UnifiedEnergy):
    """The pinned geometry, memoized only inside an outer no-grad read."""
    _read_geometry_cache = None

    def geometry(self):
        cache = self._read_geometry_cache
        if cache is None:
            return super().geometry()
        # Echo's functional_call substitutes float64 parameter clones even
        # during inference. Key the ACTUAL inputs, never reuse float32 geometry
        # for those clones, and never retain a parameter graph.
        key = FieldOwner.content_key((('links', self.links), ('anchors', self.anchors)))
        if key not in cache:
            with torch.no_grad():
                cache[key] = super().geometry()
        return cache[key]


class FieldOwner(CoreOwner):
    """New senses/production keys; the geometric Field and its credit are preserved."""
    def __init__(self, config=None, *, keys=1024):
        super().__init__(config)
        self.raw_port = nn.Linear(8, self.config.width, bias=False)
        self.production_query = nn.Linear(64, 48, bias=False)
        self.production_keys = nn.Embedding(keys, 48)
        self.reading_decoder = nn.Linear(self.config.width, 256)
        self.token_ids = {}                 # append-only; byte fallback IDs 1..256
        self.production_ids = {}            # append-only; (kind, payload, signature)
        self.port_enabled = True
        # Private initialization preserves every U1 parameter and random draw
        # when U2 is off. All these fresh parameters share the owner's optimizer.
        with torch.random.fork_rng(devices=list(range(torch.cuda.device_count()))):
            torch.manual_seed(2202)
            self.memory_projection = nn.Linear(2048, self.config.nodes*3, bias=False)
            self.memory_gate = nn.Parameter(torch.tensor(-2.))
            self.understanding_query = nn.Linear(64, 16)
            self.understanding_keys = nn.Embedding(keys, 16)
            self.understanding_mix = nn.Parameter(torch.tensor(0.))
        self.understanding_ids = {}
        self.readout_reuse_enabled = True  # exact engineering path; profile reference disables it
        self._readout_cache = {}
        self._prefix_cache = {}
        self._geometry_cache = {}
        self._geometry_version = None
        # Adopt without initialization: preserve all tensors and random draws.
        self.core.__class__ = _ReadGeometryEnergy

    @staticmethod
    def content_key(items):
        """Small retained states and owner tensors: content, never allocator identity.

        Byte views also cover complex buffers without converting their dtype.
        In-place edits, replacement tensors and optimizer steps all invalidate.
        """
        out = []
        for name, value in sorted(items, key=lambda item: item[0]):
            t = value.detach().cpu().contiguous()
            raw = t.reshape(-1).view(torch.uint8).numpy().tobytes()
            out.append((name, str(value.device), str(t.dtype), tuple(t.shape),
                        hashlib.blake2b(raw, digest_size=32).digest()))
        return tuple(out)

    def readout_version(self):
        return (tuple(sorted(vars(self.config).items())), self.port_enabled,
                tuple((name, module.training) for name, module in self.named_modules()),
                self.content_key(self.named_parameters()), self.content_key(self.named_buffers()))

    def record_vocabulary(self, records, *, grow=True):
        # Appending hypothetical tokens cannot change an already encoded public
        # prefix. Key the actual encoding of relevant tokens, including fallback.
        tokens = sorted({token for row in records for token, _, _, _ in row})
        return tuple((token, tuple(self.token_indices(token, grow=False)),
                      grow and token not in self.token_ids and len(self.token_ids)+257 < self.words.num_embeddings)
                     for token in tokens)

    def clear_readouts(self):
        self._readout_cache.clear()
        self._prefix_cache.clear()
        self._geometry_cache.clear()
        self._geometry_version = None

    @contextmanager
    def geometry_reads(self, version):
        """Scope constants across the coordinate-only autograd inside a read."""
        if torch.is_grad_enabled() or not self.readout_reuse_enabled:
            yield
            return
        if self._geometry_version != version:
            self._geometry_cache.clear()
            self._geometry_version = version
        previous = self.core._read_geometry_cache
        self.core._read_geometry_cache = self._geometry_cache
        try:
            yield
        finally:
            self.core._read_geometry_cache = previous

    def read_features_many(self, views, *, grow=True, states=None, rings=None,
                           memory_read=True, context=()):
        """Exact public-prefix reuse for independent inference views.

        Keep every source for the original stack/mean reduction; summing a
        cached prefix separately would change float32 reduction order. A ring
        is applied to EVERY row, so differing rings cannot share a prefix.
        Autograd always uses the original fresh complete graphs.
        """
        views = tuple(views)
        if not views:
            return []
        if any(type(view) is not TaskView for view in views):
            raise TypeError('The neural input boundary accepts TaskView only')
        if torch.is_grad_enabled() or not self.readout_reuse_enabled:
            return self.task_features_many(views, grow=grow, states=states,
                                           rings=rings, memory_read=memory_read)
        if states is not None and len(states) != len(views):
            raise ValueError('One initial state per view required')
        if rings is not None and len(rings) != len(views):
            raise ValueError('One optional ringing per view required')
        initial = [self.empty(1) for _ in views] if states is None else states
        rings = [None]*len(views) if rings is None else rings
        records = ([(view.records(max_examples=max(4, len(view.examples)), max_records=None)
                     if memory_read else view.records()) for view in views]
                   if self.port_enabled else [() for _ in views])
        moments = [(self.content_key(state.items()),
                    () if ring is None else self.content_key((('ring', ring),)), context)
                   for state, ring in zip(initial, rings)]
        version = self.readout_version()
        with self.geometry_reads(version):
            return self._cached_features_many(views, grow, initial, rings, memory_read,
                                              records, moments, version)

    def _cached_features_many(self, views, grow, initial, rings, memory_read, records, moments, version):
        keys = [(view, grow, version, moment, self.record_vocabulary(rows, grow=grow))
                for view, moment, rows in zip(views, moments, records)]
        ready, pending, duplicates = {}, [], {}
        for j, key in enumerate(keys):
            if key in self._readout_cache:
                ready[j] = self._readout_cache[key]
            elif key in duplicates:
                duplicates[key].append(j)
            else:
                duplicates[key] = [j]
                pending.append(j)
        if pending:
            # Allocate in exactly the old first-view/record order before taking
            # each record's vocabulary key. Grow=False uses full byte fallback.
            sources = [self.task_sources(views[j], grow=grow, ring=rings[j], memory_read=memory_read)
                       for j in pending]
            # Encoding allocates IDs only: these modules have no running-buffer
            # writes. The parameter/buffer content version is still unchanged.
            prefixes, missing, prefix_keys = {}, {}, []
            suffixes, suffix_slots = [], []
            for slot, (j, rows) in enumerate(zip(pending, sources)):
                count = len(records[j])-len(views[j].hypotheses) if self.port_enabled else len(rows)
                # Hashed text encodes the entire view as one source: it has no
                # separable public prefix, but identical views can still hit.
                public = records[j][:count] if self.port_enabled else ('hashed-view', views[j])
                vocabulary = self.record_vocabulary(records[j][:count], grow=grow) if self.port_enabled else ()
                key = (public, grow, version, moments[j], vocabulary)
                prefix_keys.append(key)
                if key not in prefixes:
                    if key in self._prefix_cache:
                        prefixes[key] = self._prefix_cache[key]
                    elif key not in missing:
                        missing[key] = (rows[:count], initial[j])
                if count < len(rows):
                    suffix_slots.append(slot)
                    suffixes.append(rows[count:])
            if missing:
                # One batch across ALL distinct retained-state/ring/context
                # groups. First occurrence fixes the deterministic row order.
                prefix_state = self.observe_sources_many(
                    [row for row, _ in missing.values()],
                    states=[state for _, state in missing.values()])
                for row, key in enumerate(missing):
                    prefix = {k: v[row:row+1].clone() for k, v in prefix_state.items()}
                    prefixes[key] = prefix
                    if len(self._prefix_cache) >= 64:
                        self._prefix_cache.clear()
                    self._prefix_cache[key] = prefix
            # Per-call prefixes survive bounded persistent-cache eviction.
            # Every branch owns all coordinates, including an empty suffix.
            settled = [{k: v.clone() for k, v in prefixes[key].items()} for key in prefix_keys]
            if suffixes:
                state = self.observe_sources_many(suffixes, states=[settled[s] for s in suffix_slots])
                for row, slot in enumerate(suffix_slots):
                    settled[slot] = {k: v[row:row+1] for k, v in state.items()}
            combined = {k: torch.cat([s[k] for s in settled], 0) for k in settled[0]}
            mean = torch.cat([torch.stack(row).mean(0) for row in sources], 0)
            features, diagnostics = self.conditional(combined, mean)
            for slot, j in enumerate(pending):
                read = (features[slot], diagnostics['path_probabilities'][slot], settled[slot])
                if len(self._readout_cache) >= 128:
                    self._readout_cache.pop(next(iter(self._readout_cache)))
                self._readout_cache[(views[j], grow, version, moments[j],
                                     self.record_vocabulary(records[j], grow=grow))] = read
                for duplicate in duplicates[keys[j]]:
                    ready[duplicate] = read
        return [ready[j] for j in range(len(views))]

    def token_indices(self, token, *, grow=True):
        if token not in self.token_ids and grow and len(self.token_ids)+257 < self.words.num_embeddings:
            self.token_ids[token] = len(self.token_ids)+257
        if token in self.token_ids:
            return [self.token_ids[token]]
        return [b+1 for b in token.encode('utf-8')] or [1]

    def encode_record(self, row, *, grow=True):
        indices, ports = [], []
        for j, (token, sign, magnitude, present) in enumerate(row):
            ids = self.token_indices(token, grow=grow)
            for b, index in enumerate(ids):
                indices.append(index)
                ports.append((sign, magnitude, present, j/max(len(row), 1),
                              b/max(len(ids), 1), float(token.startswith('open:')),
                              float(token.startswith('close:')), 1.))
        if len(indices) > 256:
            from .ports import PortBudget
            raise PortBudget('Byte fallback exceeds the complete 256-token record budget')
        ids = torch.tensor(indices, device=self.words.weight.device, dtype=torch.long)[None]
        raw = self.words.weight.new_tensor(ports)[None]
        values = self.words(ids)+self.raw_port(raw)
        local = self.local(values.transpose(1, 2)).transpose(1, 2).tanh()
        pooled = self.text_pool(torch.cat((local.mean(1), local.amax(1)), -1))
        return self.text_source(pooled).reshape(1, self.config.nodes, 3).tanh()

    def encode_texts(self, texts):
        if not self.port_enabled:
            return NativeOwner.encode_texts(self, texts)
        if not texts:
            raise ValueError('Nonempty heard-text batch required')
        return torch.cat([self.encode_record((('role:heard', 0., 0., 1.),)+
                         tuple((word, 0., 0., 1.) for word in text.split())) for text in texts], 0)

    def encode_records(self, rows, *, grow=True):
        """Allocate tokens in record order; batch equal lengths without padding.

        A padded position can feed the biased convolution at a real edge. Exact
        length groups avoid that and retain each single record's mean/max order.
        Only encoding is grouped: observed state transitions remain sequential.
        """
        groups, count = {}, 0
        for index, row in enumerate(rows):
            indices, ports = [], []
            for j, (token, sign, magnitude, present) in enumerate(row):
                ids = self.token_indices(token, grow=grow)
                for b, identity in enumerate(ids):
                    indices.append(identity)
                    ports.append((sign, magnitude, present, j/max(len(row), 1),
                                  b/max(len(ids), 1), float(token.startswith('open:')),
                                  float(token.startswith('close:')), 1.))
            if len(indices) > 256:
                raise PortBudget('Byte fallback exceeds the complete 256-token record budget')
            if not indices:
                raise ValueError('Nonempty record required')
            groups.setdefault(len(indices), []).append((index, indices, ports))
            count += 1
        if not count:
            return self.words.weight.new_empty((0, self.config.nodes, 3))
        result = [None]*count
        for group in groups.values():
            for start in range(0, len(group), 256):
                batch = group[start:start+256]
                ids = torch.tensor([r[1] for r in batch], device=self.words.weight.device, dtype=torch.long)
                raw = self.words.weight.new_tensor([r[2] for r in batch])
                values = self.words(ids)+self.raw_port(raw)
                local = self.local(values.transpose(1, 2)).transpose(1, 2).tanh()
                pooled = self.text_pool(torch.cat((local.mean(1), local.amax(1)), -1))
                source = self.text_source(pooled).reshape(-1, self.config.nodes, 3).tanh()
                for slot, (index, _, _) in enumerate(batch):
                    result[index] = source[slot:slot+1]
        return torch.cat(result, 0)

    def task_sources(self, view, *, grow=True, ring=None, memory_read=False):
        """Allocate in row order; memory batches group encoding by exact length."""
        if type(view) is not TaskView:
            raise TypeError('The neural input boundary accepts TaskView only')
        if self.port_enabled:
            records = (view.records(max_examples=max(4, len(view.examples)), max_records=None)
                       if memory_read else view.records())
            sources = list(self.encode_records(records, grow=grow).split(1)) if memory_read else [
                self.encode_record(row, grow=grow) for row in records]
        else:
            sources = [NativeOwner.encode_texts(self, [json.dumps(view.__dict__, sort_keys=True)])]
        if ring is not None:
            if ring.shape != (2048,) or not bool(torch.isfinite(ring).all()):
                raise ValueError('Finite 2048-dimensional ringing required')
            retained = self.memory_gate.sigmoid()*self.memory_projection(ring).reshape(1, self.config.nodes, 3).tanh()
            sources = [source+retained for source in sources]
        return sources

    def observe_sources_many(self, sources, *, states=None):
        """Independent observed histories, with absent rows frozen in every coordinate."""
        if not sources or any(not row for row in sources):
            raise ValueError('Nonempty source sequence per batch row required')
        if states is None:
            state = self.empty(len(sources))
        else:
            if len(states) != len(sources):
                raise ValueError('One initial state per batch row required')
            state = {k: torch.cat([row[k] for row in states], 0) for k in states[0]}
        for j in range(max(map(len, sources))):
            source = torch.cat([row[j] if j < len(row) else torch.zeros_like(row[0])
                                for row in sources], 0)
            updated, _ = self.observe(state, source)
            present = torch.tensor([j < len(row) for row in sources], device=source.device)
            # CoreOwner.observe has no absent-row argument. Mask *all* state,
            # including reservoir, flow context and integer observation events.
            state = {k: torch.where(present.reshape(-1, *([1]*(v.ndim-1))), v, state[k])
                     for k, v in updated.items()}
        return state

    def features_from_sources_many(self, sources, *, states=None):
        state = self.observe_sources_many(sources, states=states)
        # Keep each row's original reduction order; padding never enters the mean.
        mean = torch.cat([torch.stack(row).mean(0) for row in sources], 0)
        features, diagnostics = self.conditional(state, mean)
        weights = diagnostics['path_probabilities']
        return [(features[j], weights[j], {k: v[j:j+1] for k, v in state.items()})
                for j in range(len(sources))]

    def task_features_many(self, views, *, grow=True, states=None, rings=None, memory_read=False):
        """Read independent views together; a retained wake history is never advanced here."""
        views = tuple(views)
        if not views:
            return []
        if rings is not None and len(rings) != len(views):
            raise ValueError('One optional ringing per batch row required')
        sources = [self.task_sources(view, grow=grow, ring=None if rings is None else rings[j],
                                     memory_read=memory_read) for j, view in enumerate(views)]
        return self.features_from_sources_many(sources, states=states)

    def task_features(self, view, *, grow=True, state=None, ring=None, memory_read=False, context=()):
        if type(view) is not TaskView:
            raise TypeError('The neural input boundary accepts TaskView only')
        if not torch.is_grad_enabled() and self.readout_reuse_enabled:
            return self.read_features_many(
                [view], grow=grow, states=None if state is None else [state],
                rings=[ring], memory_read=memory_read, context=context)[0]
        if self.port_enabled:
            records = (view.records(max_examples=max(4, len(view.examples)), max_records=None)
                       if memory_read else view.records())
            sources = [self.encode_record(row, grow=grow) for row in records]
        else:
            # The control retains the identical safe view through the pinned
            # native hashed text sense, with no ordered raw/position port.
            sources = [NativeOwner.encode_texts(self, [json.dumps(view.__dict__, sort_keys=True)])]
        state = self.empty(1) if state is None else {k: v.clone() for k, v in state.items()}
        if ring is not None:
            if ring.shape != (2048,) or not bool(torch.isfinite(ring).all()):
                raise ValueError('Finite 2048-dimensional ringing required')
            retained_source = self.memory_gate.sigmoid()*self.memory_projection(ring).reshape(1, self.config.nodes, 3).tanh()
            sources = [source+retained_source for source in sources]
        for source in sources:
            state, _ = self.observe(state, source)
        features, diagnostics = self.conditional(state, torch.stack(sources).mean(0))
        return features[0], diagnostics['path_probabilities'][0], state

    def familiarity_readout(self, features, weights, keys, *, grow=True):
        values = []
        settled = (features*weights[:, None]).sum(0)
        query = self.understanding_query(settled)
        for key in keys:
            if key not in self.understanding_ids and grow:
                if len(self.understanding_ids) < self.understanding_keys.num_embeddings:
                    self.understanding_ids[key] = len(self.understanding_ids)
            index = self.understanding_ids.get(key)
            if index is None:
                values.append(query.sum()*0.)
            else:
                value = query @ self.understanding_keys.weight[index]/math.sqrt(16)
                values.append(torch.nn.functional.softplus(value))
        return torch.stack(values) if values else query.new_empty((0,))

    def key(self, identity, *, grow=True):
        if identity not in self.production_ids:
            if not grow or len(self.production_ids) == self.production_keys.num_embeddings:
                return None             # a bounded neural vocabulary; fallback remains reachable
            self.production_ids[identity] = len(self.production_ids)
        return self.production_ids[identity]


@dataclass(frozen=True)
class Production:
    sym: str
    pay: object
    args: tuple
    ret: str

    @property
    def identity(self):
        return (self.sym, self.pay, self.args, self.ret)


def library_identity(concepts):
    return digest([(repr(cid), body, arg, concepts.get('_sig', {}).get(cid))
                   for cid, (body, arg) in sorted(((k, v) for k, v in concepts.items() if k != '_sig'),
                                                key=lambda item: repr(item[0]))])


def legal(typ, env, concepts, constants, types):
    rows = [Production('var', name, (), t) for name, t in sorted(env.items()) if t == typ]
    rows += [Production('lit', value, (), 'num') for value in sorted(set(constants)) if typ == 'num']
    for name, (args, ret) in sorted(LG.INNATE.items()):
        for a, r, sub in LG.instances(args, ret, types):
            if r != typ:
                continue
            pay = sub.get('T') if name == 'head' and sub.get('T', 'num') != 'num' else None
            rows.append(Production(name, pay, tuple(a), r))
    for cid, sig in sorted(concepts.get('_sig', {}).items(), key=lambda item: repr(item[0])):
        if cid not in concepts:
            raise ValueError('Unknown concept signature')
        for args, ret, _ in LG.instances((sig[0],), sig[1], types):
            if ret == typ:
                rows.append(Production('c', cid, tuple(args), ret))
    if typ.startswith('lam:'):
        rows.append(Production('lam', typ[4:].split('>')[0], (typ[4:].split('>')[1],), typ))
    return tuple(dict.fromkeys(rows))


def bound_types(kind, types):
    # Lambda element type is supplied by its enclosing production, not assumed numeric.
    return {'e': types[0], **({'i': 'num'} if kind == 'ie' else {}),
            **({'a': types[1]} if kind == 'ae' else {})}


def _hole(typ, env):
    return ('@hole', typ, tuple(sorted(env.items())))


def _first_hole(p, path=()):
    if p[0] == '@hole':
        return path, p
    for j, child in enumerate(p[2:], 2):
        got = _first_hole(child, path+(j,))
        if got is not None:
            return got
    return None


def _replace(p, path, value):
    if not path:
        return value
    j = path[0]
    return p[:j]+(_replace(p[j], path[1:], value),)+p[j+1:]


class Proposer:
    def __init__(self, owner, field, *, enabled=True):
        self.owner, self.field, self.enabled = owner, field, enabled
        self.revision = 0
        self.cursors = {}             # declarative requests; runtime generators never enter a checkpoint
        self._scores = {}
        self._beamed = set()
        self.stats = dict(inference=0., search=0., proposal=0., chunks=0, candidates=0)
        self.fragments = []
        self.imagined = []
        self._restore_pending = False
        self.retained = None
        self.memory = None
        self.memory_a_enabled = True
        self._feature_cache = {}          # transient, assessment only; never checkpointed

    def concepts(self, supplied):
        verified = self.field.proven_ideas()
        for cid in supplied.get('_sig', {}):
            if cid not in supplied or cid not in verified:
                raise ValueError(f'Unproven or unknown concept ID {cid}')
        return supplied

    def distribution(self, features, weights, choices, *, grow=True):
        indexed = [(p, self.owner.key(p.identity, grow=grow)) for p in choices]
        indexed = [(p, i) for p, i in indexed if i is not None]
        if not indexed:
            return (), features.new_empty((3, 0)), weights
        ids = torch.tensor([i for _, i in indexed], dtype=torch.long, device=features.device)
        logits = self.owner.production_query(features) @ self.owner.production_keys(ids).T/math.sqrt(48)
        return tuple(p for p, _ in indexed), logits.log_softmax(-1), weights

    def features(self, view, concepts, *, grow=True):
        from .clock import charge
        charge('field_read')
        self.concepts(concepts)
        start = time.perf_counter()
        cached = (self._feature_cache.get((view, grow)) if self.memory is None and not torch.is_grad_enabled() else None)
        if cached is not None:
            return cached[:2]
        if self.memory is None:
            retained = self.retained if self.memory_a_enabled else None
            features, weights, _ = self.owner.task_features(
                view, grow=grow, state=retained, context=('proposer', self.memory_a_enabled))
        elif not torch.is_grad_enabled() and self.owner.readout_reuse_enabled:
            # mind.live's own read uses the same layer context and both caches
            # as candidate reads, while retaining Memory's touch/cost accounting.
            features, weights, _ = self.memory.features_many([view], grow=grow)[0]
        else:
            features, weights, _ = self.memory.features(view, grow=grow)
        self.stats['inference'] += time.perf_counter()-start
        return features, weights

    def features_many(self, views, libraries, *, grow=True, memory_read=False):
        from .clock import charge
        charge('field_read', len(views))
        """One read per distinct view within this call; no cache survives an update."""
        views, libraries = tuple(views), tuple(libraries)
        if len(views) != len(libraries):
            raise ValueError('One checked concept table per view required')
        for concepts in libraries:
            self.concepts(concepts)
        if not views:
            return []
        start = time.perf_counter()
        unique = list(dict.fromkeys(views))
        if self.memory is None:
            retained = self.retained if self.memory_a_enabled else None
            states = None if retained is None else [retained]*len(unique)
            reads = self.owner.read_features_many(unique, grow=grow, states=states, memory_read=memory_read,
                                                  context=('proposer', self.memory_a_enabled))
        else:
            reads = self.memory.features_many(unique, grow=grow)
        cache = dict(zip(unique, reads))
        self.stats['inference'] += time.perf_counter()-start
        return [cache[view][:2] for view in views]

    def prior(self, view, concepts, constants=()):
        key = (view.identity, library_identity(concepts), self.revision, tuple(sorted(set(constants))))
        if self.memory is not None and self.memory.choice_on:
            key += (self.memory.a, self.memory.b)
        if key not in self._scores:
            with torch.no_grad():
                features, weights = self.features(view, concepts)
                types = sorted(LG.universe([t for _, t in view.inputs]+[view.out]), key=lambda t: (LG.depth(t), t))
                choices = tuple(dict.fromkeys(p for typ in types for p in
                                             legal(typ, dict(view.inputs), concepts, constants, types)))
                choices, logp, weights = self.distribution(features, weights, choices)
                scores = torch.logsumexp(weights.clamp_min(1e-12).log()[:, None]+logp, 0).tolist()
                order = {}
                for p, score in zip(choices, scores):
                    token = (p.sym, p.pay)
                    order[token] = max(order.get(token, -math.inf), score)
                self._scores[key] = order
        return self._scores[key]

    def admitted(self, concepts):
        verified = self.field.proven_ideas()
        table = {**{k: v for k, v in concepts.items() if k != '_sig' and k in verified},
                 '_sig': {k: v for k, v in concepts.get('_sig', {}).items() if k in verified}}
        roadmap = getattr(self.field, 'roadmap_readout', None)
        return roadmap.basis(table) if roadmap is not None else table

    def beam(self, view, concepts, constants=(), *, width=32, nodes=9, deadline=math.inf, read=None, branch=None):
        """Task-conditioned typed holes; 32 complete programs and 32 partial fragments."""
        start = time.perf_counter()
        if CR.on('gap_syndromes'):
            self._gap_surest = None
            gap_confidence = -math.inf
        with torch.no_grad():
            features, weights = self.features(view, concepts) if read is None else read
            if branch is not None:
                weights = weights.new_zeros(3)
                weights[branch] = 1.
            types = sorted(LG.universe([t for _, t in view.inputs]+[view.out]), key=lambda t: (LG.depth(t), t))
            beam = [(_hole(view.out, dict(view.inputs)), features.new_zeros(3))]
            complete = []
            for _ in range(nodes):
                if time.time() >= deadline:
                    break
                expanded = []
                for ast, branch_score in beam:
                    got = _first_hole(ast)
                    if got is None:
                        complete.append((ast, branch_score))
                        continue
                    path, (_, typ, bindings) = got
                    env = dict(bindings)
                    choices = legal(typ, env, concepts, constants, types)
                    choices, logp, _ = self.distribution(features, weights, choices)
                    if CR.on('gap_syndromes') and choices:
                        mixture = torch.logsumexp(weights.clamp_min(1e-12).log()[:, None]+logp, 0)
                        j = int(mixture.argmax())
                        confidence = float(mixture[j])
                        if confidence > gap_confidence:
                            gap_confidence = confidence
                            best = choices[j]
                            self._gap_surest = ('concept', best.pay) if best.sym == 'c' else ('production', best.sym)
                    for i, prod in enumerate(choices):
                        if LG.WORK_CHARGE is not None:
                            if LG.DEADLINE_CHECK(deadline):
                                break
                            LG.WORK_CHARGE()
                        args = []
                        for a in prod.args:
                            if a.startswith('lam:'):
                                kind, ret = a[4:].split('>')
                                # The enclosing map/fold arguments determine element and accumulator.
                                list_type = prod.args[-1]
                                elem = LG.elem(list_type)
                                acc = prod.args[1] if kind == 'ae' else 'num'
                                local = {**env, **bound_types(kind, (elem, acc))}
                                args.append(LG.node('lam', _hole(ret, local), payload=kind))
                            else:
                                args.append(_hole(a, env))
                        candidate = _replace(ast, path, LG.node(prod.sym, *args, payload=prod.pay))
                        if LG.size(candidate) <= nodes:
                            expanded.append((candidate, branch_score+logp[:, i]))
                expanded.sort(key=lambda item: (-float(torch.logsumexp(weights.log()+item[1], 0)), repr(item[0])))
                beam = expanded[:width]
                if len(complete) >= width or not beam:
                    break
            complete += [item for item in beam if _first_hole(item[0]) is None]
            self.fragments = [dict(ast=p, free=tuple(sorted(dict(view.inputs).items())))
                              for p, _ in beam if _first_hole(p) is not None][:width]
            complete.sort(key=lambda item: (-float(torch.logsumexp(weights.log()+item[1], 0)), repr(item[0])))
            result = []
            for p, _ in complete:
                if len(view.inputs) == 1:
                    var, tin = view.inputs[0]
                    sig = LG.infer(p, concepts, arg=var)
                    if sig is None or not LG.fits(sig, tin, view.out):
                        continue
                probes = [dict(bindings) for bindings in view.queries]
                if any(LG.safe(p, probe, concepts) is None for probe in probes):
                    continue
                if p not in result:
                    result.append(p)
            # Executable subexpressions are temporary step candidates. Their
            # bodies stay expanded until a complete solution earns judge credit.
            fragments = []
            if len(view.inputs) == 1:
                var, tin = view.inputs[0]
                stack = list(reversed(result))
                seen = set()
                while stack and len(fragments) < width:
                    q = stack.pop()
                    stack.extend(reversed(q[2:]))
                    if q in seen or q[0] in ('lam', 'var', 'zero', 'one', 'nil', 'lit'):
                        continue
                    seen.add(q)
                    sig = LG.infer(q, concepts, arg=var)
                    if sig is None:
                        continue
                    for args, ret, _ in LG.instances((sig[0],), sig[1], types):
                        if args == (tin,):
                            fragments.append(dict(ast=q, free=((var, tin),), out=ret, partial=False))
                            break
            self.fragments = fragments+self.fragments[:max(0, width-len(fragments))]
        self.stats['proposal'] += time.perf_counter()-start
        if self.memory is not None:
            result = self.memory.rank(view, result, concepts)
            full = [f for f in self.fragments if not f.get('partial', True)]
            partial = [f for f in self.fragments if f.get('partial', True)]
            for group, is_partial in ((full, False), (partial, True)):
                order = self.memory.rank(view, [f['ast'] for f in group], concepts, partial=is_partial)
                positions = {p: j for j, p in enumerate(order)}
                group.sort(key=lambda f: positions[f['ast']])
            self.fragments = full+partial
        return result[:width]

    def chunks(self, view, inputs, out_type, probes, max_size, concepts, *, deadline,
               chunk=256, **kwargs):
        """20% fallback then 80% preferred; callers can judge after every yielded chunk.

        The fallback never uses work=None. Both schedules increase cumulative
        work, keep namespaces separate, and freeze scores until revision changes.
        """
        concepts = self.concepts(concepts)
        constants = kwargs.get('constants', ())
        order = self.prior(view, concepts, constants)
        identity = digest([view.identity, sorted(inputs.items()), out_type, probes,
                           library_identity(concepts), self.revision, kwargs])
        if self.memory is not None and self.memory.choice_on:
            identity = digest([identity, self.memory.a, self.memory.b])
        cursor = self.cursors.setdefault(identity, dict(fallback=0, preferred=0, yielded=set(), done={},
                                                       seconds={'fallback': 0., 'preferred': 0.}, history=[],
                                                       request=(view, inputs, out_type, probes, max_size, concepts, kwargs)))
        if max_size > cursor['request'][4]:
            cursor['done'].clear()
            cursor['request'] = (view, inputs, out_type, probes, max_size, concepts, kwargs)
        if self._restore_pending:
            self.restore_searches()
        saved = LG.DEADLINE[0]
        try:
            while time.time() < deadline:
                seconds = cursor['seconds']
                # Debt scheduler persists across early judge returns. Roundoff is
                # bounded by one work chunk, rather than restarting the 20% slice.
                lane = 'fallback' if seconds['fallback'] <= .2*sum(seconds.values()) else 'preferred'
                if cursor['done'].get(lane, False):
                    lane = 'preferred' if lane == 'fallback' else 'fallback'
                if cursor['done'].get(lane, False):
                    break
                cursor[lane] += chunk
                LG.DEADLINE[0] = deadline
                before = time.perf_counter()
                found = LG.search(inputs, out_type, probes, max_size, concepts, values=True,
                                  work=cursor[lane], chunk=chunk, namespace=(identity, lane),
                                  order=None if lane == 'fallback' else order, **kwargs)
                elapsed = time.perf_counter()-before
                seconds[lane] += elapsed
                self.stats['search'] += elapsed
                self.stats['chunks'] += 1
                cursor['history'].append((lane, cursor[lane], chunk, max_size))
                cursor['done'][lane] = LG.COMPLETE[0]
                fresh = [q for q in found if q[0] not in cursor['yielded']]
                cursor['yielded'].update(q[0] for q in fresh)
                self.stats['candidates'] += len(fresh)
                yield fresh
                if LG._over_memory():
                    break
        finally:
            LG.DEADLINE[0] = saved

    def search(self, task, inputs, out_type, probes, max_size, concepts=None, **kwargs):
        if not self.enabled or task.form != 'exact':
            return LG.search(inputs, out_type, probes, max_size, concepts, **kwargs)
        view = TaskView.from_task(task)
        if not self.within_budget(view):
            return LG.search(inputs, out_type, probes, max_size, concepts, **kwargs)
        concepts = self.admitted(concepts or {})
        values = kwargs.pop('values', False)
        kwargs.pop('work', None)
        # Return a small new frontier so Sera.live invokes its unchanged judge early.
        accumulated = []
        root = inputs == task.inputs and out_type == task.out
        if root and self.imagined:
            rows = [(p, LG.size(p), [LG.safe(p, probe, concepts) for probe in probes])
                    for p in self.imagined if LG.size(p) <= max_size and task.consistent(p, concepts)]
            if rows:
                return rows if values else [(p, size) for p, size, _ in rows]
        for fresh in self.chunks(view, inputs, out_type, probes, max_size, concepts,
                                 deadline=LG.DEADLINE[0], **kwargs):
            accumulated.extend(fresh)
            fitting = [row for row in fresh if task.consistent(row[0], concepts)] if root else []
            if fitting:
                return fitting if values else [(p, s) for p, s, _ in fitting]
            if fresh and not root:
                return fresh if values else [(p, s) for p, s, _ in fresh]
        return accumulated if values else [(p, s) for p, s, _ in accumulated]

    def order_steps(self, task, rows, concepts):
        view = TaskView.from_task(task) if self.enabled else None
        if not self.enabled or not self.within_budget(view):
            return rows
        order = self.prior(view, self.admitted(concepts))
        def score(p):
            sym, pay = p[:2]
            return order.get((sym, pay), order.get((sym, None), -20.))+sum(score(k) for k in p[2:])
        return sorted(rows, key=lambda row: (-score(row[0]), repr(row[0])))

    def step_fragments(self, inputs, probes, concepts, *, max_size=9):
        out = []
        for fragment in self.fragments:
            if fragment.get('partial', True) or LG.size(fragment['ast']) > max_size:
                continue
            if any(inputs.get(name) != typ for name, typ in fragment['free']):
                continue
            values = []
            for env in probes:
                value = LG.safe(fragment['ast'], env, concepts)
                if value is None:
                    break
                values.append(value)
            if len(values) == len(probes):
                out.append((fragment['ast'], fragment['out'], values))
        return out

    def within_budget(self, view):
        """Whether the Field's ports can read the whole view. A view grown past the pilot port budget (a taught task
        whose teacher or world added examples) is a recorded miss: the proposer steps aside for it and the unchanged
        search runs, never a truncated or summarized view (S28 §2)."""
        try:
            view.records()
            return True
        except PortBudget:
            self.stats['budget_misses'] = self.stats.get('budget_misses', 0)+1
            return False

    def preferred(self, task, concepts, constants):
        concepts = self.admitted(concepts)
        imagined = [p for p in self.imagined if task.consistent(p, concepts)]
        if imagined:
            return imagined
        view = TaskView.from_task(task)
        if not self.within_budget(view):
            return []
        key = (view.identity, library_identity(concepts), self.revision)
        if self.memory is not None and self.memory.choice_on:
            key += (self.memory.a, self.memory.b)
        if key in self._beamed:
            return []
        self._beamed.add(key)
        now = time.time()
        budget = .1*max(0., LG.DEADLINE[0]-now)
        if not math.isfinite(budget):
            budget = 1.
        candidates = self.beam(view, concepts, constants, deadline=now+budget)
        LG.COMPLETE[0] = False
        return [p for p in candidates if task.consistent(p, concepts)]

    def changed(self):
        self.owner.clear_readouts()
        self._feature_cache.clear()
        if self.memory is not None:
            self.memory._feature_cache.clear()
            self.memory._feature_rings.clear()
            self.memory._feature_versions.clear()
        self.revision += 1
        self._scores.clear()
        self._beamed.clear()
        self.cursors.clear()
        self.fragments.clear()
        LG.forget_searches()

    def restore_searches(self):
        """Rebuild only the recorded deterministic frontier, without executing a judge."""
        saved_deadline, saved_stats = LG.DEADLINE[0], self.stats.copy()
        saved_charge, saved_check = LG.WORK_CHARGE, LG.DEADLINE_CHECK
        try:
            LG.WORK_CHARGE = None
            LG.DEADLINE_CHECK = lambda deadline: False
            LG.forget_searches()
            LG.DEADLINE[0] = math.inf
            for identity, cursor in sorted(self.cursors.items()):
                view, inputs, out_type, probes, max_size, concepts, kwargs = cursor['request']
                policy = self.prior(view, concepts, kwargs.get('constants', ()))
                for lane, work, chunk, searched_size in cursor['history']:
                    LG.search(inputs, out_type, probes, searched_size, concepts, values=True, work=work, chunk=chunk,
                              namespace=(identity, lane), order=policy if lane == 'preferred' else None, **kwargs)
            self._restore_pending = False
        finally:
            LG.DEADLINE[0], self.stats = saved_deadline, saved_stats
            LG.WORK_CHARGE, LG.DEADLINE_CHECK = saved_charge, saved_check
