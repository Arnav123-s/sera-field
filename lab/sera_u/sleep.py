"""Checked replay, exact inner abilities, executable self-made tasks and credit.

Dream execution is a second interpreter, not a call to lang.evaluate/_ev/_prim.
Its deliberately finite scope is recorded. Unsupported syntax is rejected.
"""
from dataclasses import dataclass
import math
import time

import torch
from torch.nn import functional as F

from sera import lang as LG
from .ports import TaskView, digest, observed
from .proposer import legal, bound_types, library_identity


def substitute(p, name, value):
    if p[0] == 'tab' and len(p) == 2 and name == '_':
        return p+(value,)
    if p[0] == 'var' and p[1] == name:
        return value
    if p[0] == 'lam' and name in p[1]:
        return p
    return p[:2]+tuple(substitute(k, name, value) for k in p[2:])


def expand(p, concepts, stack=()):
    if p[0] == 'c':
        cid = p[1]
        if cid not in concepts or cid in stack:
            raise ValueError('Unknown or recursive concept')
        body, arg = concepts[cid]
        return expand(substitute(body, arg, expand(p[2], concepts, stack)), concepts, stack+(cid,))
    if p[0] not in LG.INNATE and p[0] not in ('var', 'lit', 'lam', 'tab'):
        raise ValueError('Unsupported executable production')
    return p[:2]+tuple(expand(k, concepts, stack) for k in p[2:])


def family(p, concepts):
    """Expanded structural template; remove source/variable names and literal magnitudes."""
    def canonical(q, env):
        if q[0] == 'var':
            return ('var', env.get(q[1], 'input'))
        if q[0] == 'lit':
            return ('lit', 'observed')
        if q[0] == 'lam':
            env = {**env, **{name: name for name in q[1]}}
        return (q[0], q[1] if q[0] == 'lam' else None,
                tuple(canonical(k, env) for k in q[2:]))
    return digest(canonical(expand(p, concepts), {}))


def rewrite(p, concept):
    """Exact single-parameter pattern substitution; never infer a domain rule."""
    capture = []
    def matches(pattern, value):
        if pattern == LG.node('var', payload='_'):
            if not capture:
                capture.append(value)
            return capture[0] == value
        return pattern[:2] == value[:2] and len(pattern) == len(value) and all(
            matches(a, b) for a, b in zip(pattern[2:], value[2:]))
    if matches(concept['body'], p) and capture:
        return LG.node('c', capture[0], payload=concept['id'])
    return p[:2]+tuple(rewrite(k, concept) for k in p[2:])


def independent(p, env, concepts, *, limit=LG.MAX_STEPS):
    steps = [0]

    def integer(v):
        if type(v) not in (int, float) or not math.isfinite(v) or abs(v) > LG.MAX_INT:
            raise ValueError('Bounded non-boolean number required')
        return v

    def sequence(v):
        if not isinstance(v, tuple) or len(v) > LG.MAX_LEN:
            raise ValueError('Bounded list required')
        return v

    def real(v):
        if type(v) not in (float, int) or not math.isfinite(v) or abs(v) > 1e12:
            raise ValueError('Finite real required')
        return float(v)

    def held(v):
        return sequence(v) if isinstance(v, tuple) else integer(v)

    def run(q, bindings, stack=()):
        steps[0] += 1
        if steps[0] > limit:
            raise ValueError('Independent executor step budget')
        sym, pay = q[:2]
        if sym == 'var':
            return LG.freeze(bindings[pay])
        if sym == 'lit':
            return integer(pay)
        if sym in ('zero', 'one', 'rone', 'nil'):
            return {'zero': 0, 'one': 1, 'rone': 1., 'nil': ()}[sym]
        if sym == 'c':
            if pay not in concepts or pay in stack:
                raise ValueError('Unknown/recursive concept')
            body, arg = concepts[pay]
            return run(body, {arg: run(q[2], bindings, stack)}, stack+(pay,))
        if sym == 'lam':
            raise ValueError('A lambda must be used by an interpreter mechanism')
        if sym == 'tab':
            # Independent piecewise-linear execution of an accepted drawing.
            grid, knots = pay
            if len(grid) < 2 or len(grid) != len(knots) or any(
                    b <= a for a, b in zip(grid, grid[1:])):
                raise ValueError('Ordered finite drawing knots required')
            for value in (*grid, *knots):
                real(value)
            x = real(run(q[2], bindings, stack) if len(q) > 2 else bindings['_'])
            if x <= grid[0]:
                return real(knots[0])
            for j in range(1, len(grid)):
                if x <= grid[j]:
                    if x == grid[j]:
                        return real(knots[j])
                    slope = (knots[j]-knots[j-1])/(grid[j]-grid[j-1])
                    return real(knots[j-1]+slope*(x-grid[j-1]))
            return real(knots[-1])
        if sym == 'if':
            condition = run(q[2], bindings, stack)
            if type(condition) is not bool:
                raise ValueError('Boolean condition required')
            return run(q[3] if condition else q[4], bindings, stack)
        if sym in ('map', 'filter', 'mapi', 'filteri', 'foldn', 'foldl'):
            lam = q[2]
            if lam[0] != 'lam':
                raise ValueError('Expected a typed lambda')
            xs = sequence(run(q[-1], bindings, stack))
            if sym.startswith('fold'):
                acc = run(q[3], bindings, stack)
                for item in xs:
                    acc = run(lam[2], {**bindings, 'a': acc, 'e': item}, stack)
                    sequence(acc) if sym == 'foldl' else integer(acc)
                return acc
            out = []
            for i, item in enumerate(xs, 1):
                value = run(lam[2], {**bindings, 'e': item, 'i': i}, stack)
                if sym.startswith('filter'):
                    if type(value) is not bool:
                        raise ValueError('Filter predicate must be boolean')
                    if value:
                        out.append(item)
                else:
                    out.append(held(value))
            return tuple(out)
        args = [run(k, bindings, stack) for k in q[2:]]
        if sym in ('add', 'sub', 'mul', 'lt', 'eq'):
            a, b = map(integer, args)
            if sym == 'lt':
                return a < b
            if sym == 'eq':
                return a == b
            return integer({'add': lambda: a+b, 'sub': lambda: a-b, 'mul': lambda: a*b}[sym]())
        if sym == 'cons':
            return sequence((held(args[0]),)+sequence(args[1]))
        if sym == 'head':
            xs = sequence(args[0])
            if xs:
                return xs[0]
            # lang's typed default for an empty head.
            return 0 if pay is None else ()
        if sym == 'tail':
            return sequence(args[0])[1:]
        if sym == 'range':
            n = integer(args[0])
            if not float(n).is_integer() or n > LG.MAX_LEN:
                raise ValueError('Range bound')
            return tuple(range(1, int(n)+1))
        if sym in ('radd', 'rsub', 'rmul', 'rdiv'):
            a, b = map(real, args)
            return real({'radd': lambda: a+b, 'rsub': lambda: a-b,
                         'rmul': lambda: a*b, 'rdiv': lambda: a/b}[sym]())
        if sym in ('sqrt', 'exp', 'log', 'sin', 'cos'):
            return real(getattr(math, sym)(real(args[0])))
        raise ValueError(f'Outside independent executor scope: {sym}')

    return observed(run(p, {k: LG.freeze(v) for k, v in env.items()}))


@dataclass(frozen=True)
class Receipt:
    view: TaskView
    targets: tuple
    scope: str
    origin: str
    source: str
    library: str
    families: tuple
    id: str
    acceptance = ()                    # no extra instance slot on the old path

    @classmethod
    def make(cls, view, targets, concepts, *, scope, origin, source, acceptance=()):
        if type(view) is not TaskView or view.form != 'exact':
            raise ValueError('Only an exact public view can supply program labels')
        view.records()                       # never admit a target whose complete sensing exceeds budget
        if len(view.examples) != 4:
            raise ValueError('Pilot program receipts require four independently executed examples')
        if scope not in ('exact-audit', 'dream-self-task', 'explore-shape') or origin not in ('taught', 'alone', 'book', 'dream', 'explore'):
            raise ValueError('A checked exact program scope and provenance are required')
        if origin == 'explore' and (len(acceptance) != 3 or acceptance[1] not in ('curve', 'drawing', 'formula')
                                    or not acceptance[0] or not acceptance[2]):
            raise ValueError('Discovery needs an outer judge record, honest kind and acceptance bound')
        if (scope == 'explore-shape' and origin != 'explore') or (acceptance and origin != 'explore'):
            raise ValueError('Discovery provenance required for a bound/shape receipt')
        acceptance = observed(acceptance)
        expanded = {repr(expand(p, concepts)): p for p in targets}
        targets = tuple(expanded[k] for k in sorted(expanded))
        if not targets:
            raise ValueError('Empty positive targets')
        data = dict(view=view.identity, targets=targets, scope=scope, origin=origin, source=source,
                    library=library_identity(concepts), families=tuple(sorted({family(p, concepts) for p in targets})))
        if acceptance:
            data['acceptance'] = acceptance
        receipt = cls(view, targets, scope, origin, source, data['library'], data['families'], digest(data))
        if acceptance:
            object.__setattr__(receipt, 'acceptance', acceptance)
        return receipt

    def check(self, concepts, *, reserved=(), sources=()):
        again = Receipt.make(self.view, self.targets, concepts, scope=self.scope, origin=self.origin, source=self.source,
                             acceptance=getattr(self, 'acceptance', ()))
        if self.id != again.id or self.library != library_identity(concepts):
            raise ValueError('Corrupted/stale program receipt')
        if set(self.families) & set(reserved) or self.source in sources:
            raise ValueError('Reserved family/source in training target')
        for p in self.targets:
            if len(self.view.inputs) != 1:
                raise ValueError('Pilot checked training uses unary task signatures')
            var, tin = self.view.inputs[0]
            sig = LG.infer(p, concepts, arg=var)
            if sig is None or not LG.fits(sig, tin, self.view.out):
                raise ValueError('Ill-typed program target')
            for bindings, expected in self.view.examples:
                env = dict(bindings)
                a = independent(p, env, concepts)
                b = observed(LG.evaluate(p, env, concepts))
                if a != b or b != expected:
                    raise ValueError('Independent/lab executor or target disagreement')
        return True


def sample_input(typ, rng, *, max_list=8):
    if LG.is_list(typ):
        return tuple(sample_input(LG.elem(typ), rng, max_list=max_list) for _ in range(rng.randrange(max_list+1)))
    if typ == 'bool':
        return bool(rng.randrange(2))
    if typ == 'real':
        return rng.uniform(-4., 4.)
    if typ == 'num':
        return rng.randrange(-8, 9)
    raise ValueError('Unsupported dream input type')


def program_log_probability(proposer, view, targets, concepts, *, read=None):
    features, weights = proposer.features(view, concepts) if read is None else read
    types = sorted(LG.universe([t for _, t in view.inputs]+[view.out]), key=lambda t: (LG.depth(t), t))
    constants = sorted({q[1] for p in targets for q in walk(p) if q[0] == 'lit'})

    def logp(p, typ, env):
        choices = legal(typ, env, concepts, constants, types)
        choices, logs, _ = proposer.distribution(features, weights, choices)
        derivations = []
        for i, production in enumerate(choices):
            if (production.sym, production.pay) != p[:2] or len(production.args) != len(p[2:]):
                continue
            total = logs[:, i]
            try:
                for child, arg_type in zip(p[2:], production.args):
                    if arg_type.startswith('lam:'):
                        kind, result = arg_type[4:].split('>')
                        if child[0] != 'lam' or child[1] != kind:
                            raise ValueError('Wrong binder')
                        elem = LG.elem(production.args[-1])
                        acc = production.args[1] if kind == 'ae' else 'num'
                        local = {**env, **bound_types(kind, (elem, acc))}
                        total = total+logp(child[2], result, local)
                    else:
                        total = total+logp(child, arg_type, env)
                derivations.append(total)
            except ValueError:
                continue
        if not derivations:
            raise ValueError('Target outside the bounded typed key vocabulary')
        return torch.logsumexp(torch.stack(derivations), 0)

    targets = tuple({repr(expand(p, concepts)): p for p in targets}.values())
    branch = torch.stack([logp(p, view.out, dict(view.inputs)) for p in targets])
    return torch.logsumexp(branch+weights.clamp_min(1e-12).log()[None], (0, 1))


def program_log_probabilities(proposer, rows, *, batched_reads=True):
    """Rows are (view, target programs, concepts); all targets share the view read."""
    rows = tuple(rows)
    if not rows:
        return proposer.owner.words.weight.new_empty((0,))
    reads = (proposer.features_many([view for view, _, _ in rows], [c for _, _, c in rows])
             if batched_reads else [None]*len(rows))
    return torch.stack([program_log_probability(proposer, view, targets, concepts, read=read)
                        for (view, targets, concepts), read in zip(rows, reads)])


def walk(p):
    yield p
    for child in p[2:]:
        yield from walk(child)


class Sleep:
    def __init__(self, mind):
        self.mind = mind
        self.replay = []                  # (frozen receipt, frozen concept table)
        self.dreams = []
        self.consumed = set()             # evidence admission, not supervised replay
        self.reserved = set()
        self.reserved_sources = set()
        self.logs = []

    def admit(self, receipt, concepts):
        receipt.check(concepts, reserved=self.reserved, sources=self.reserved_sources)
        if receipt.id in self.consumed:
            raise ValueError('Duplicate evidence receipt; sample existing replay instead')
        if receipt.origin != 'dream' and receipt.id not in self.mind.checked_wake:
            raise ValueError('No bound independent wake acceptance for this receipt')
        self.consumed.add(receipt.id)
        import copy
        (self.dreams if receipt.origin == 'dream' else self.replay).append((receipt, copy.deepcopy(concepts)))

    def abstract(self):
        if not self.mind.crutches['sleep_library']:
            return []
        from types import SimpleNamespace
        kept = []
        for receipt, snapshot in self.replay:
            receipt.check(snapshot, reserved=self.reserved, sources=self.reserved_sources)
            var, _ = receipt.view.inputs[0]
            data = [(dict(bindings)[var], y) for bindings, y in receipt.view.examples]
            task = SimpleNamespace(data=data, _probe_inputs=[x for x, _ in data],
                                   subject='code' if LG.is_list(receipt.view.inputs[0][1]) else 'math',
                                   name='checked sleep '+receipt.id[:12])
            for p in receipt.targets:
                expanded = expand(p, snapshot)
                concepts = self.mind.field.concept_table()
                kept.extend(self.mind.engine._inner_ability(expanded, var, task, concepts))
                # A library rewrite is checked on every replay input before admission.
                for c in kept:
                    if LG.infer(c['body'], concepts) is None:
                        raise ValueError('Inner ability failed type validation')
                    rewritten = rewrite(expanded, c)
                    for bindings, _ in receipt.view.examples:
                        env = dict(bindings)
                        if (LG.evaluate(rewritten, env, concepts) != LG.evaluate(expanded, env, {}) or
                                independent(rewritten, env, concepts) != independent(expanded, env, {})):
                            raise ValueError('Library rewrite failed checked substitution')
        if kept:
            self.mind.proposer.changed()
        return kept

    def dream(self, count=32, *, attempts=512, deadline=math.inf, filter_program=None):
        if not self.mind.crutches['program_dreams']:
            return []
        started = time.perf_counter()
        concepts = self.mind.field.concept_table()
        acquired = [c for c in self.mind.field.concepts if c['id'] in self.mind.field.proven_ideas()]
        generators = []
        if acquired and self.mind.crutches['sleep_library']:
            for c in acquired:
                tin, tout = c['sig']
                generators.append((LG.node('c', LG.node('var', payload='x'), payload=c['id']), tin, tout))
        else:
            # Empty-library/no-library bootstrap: only independently accepted wake programs.
            for receipt, snapshot in self.replay:
                var, tin = receipt.view.inputs[0]
                generators.extend((substitute(expand(p, snapshot), var, LG.node('var', payload='x')),
                                   tin, receipt.view.out) for p in receipt.targets)
        made, behavior = [], set()
        rng = self.mind.random
        if not generators:
            return made
        curiosity = getattr(self.mind.field, 'curiosity', None) if self.mind.crutches.get('gap_syndromes') else None
        gap = None if curiosity is None else curiosity.gap
        share = curiosity.dream_share if gap is not None and self.mind.crutches.get('aimed_dreams') else 0.
        pools = {}
        for attempt in range(attempts):
            if len(made) >= count or time.time() >= deadline or len(self.dreams) >= 10_000:
                break
            aimed = math.floor((attempt+1)*share) > math.floor(attempt*share)
            route = 'aimed' if aimed else 'random'
            if aimed:
                distribution = gap['distribution']
                part = rng.choices([p for p, _ in distribution], [w for _, w in distribution])[0]
                if part not in pools:
                    try:
                        pools[part] = aimed_compositions(generators, concepts, part, deadline=deadline)
                    except (ValueError, KeyError, *LG.BAD):
                        pools[part] = []
                curiosity.dream_trial(gap, route, False)
                if not pools[part]:
                    continue
                p, tin, tout = rng.choice(pools[part])
                left, right = (p, tin, tout), (p, tin, tout)
            else:
                if curiosity is not None:
                    curiosity.dream_trial(gap, route, False)
                left = rng.choice(generators)
                compatible = [g for g in generators if g[1] == left[2]]
                if not compatible:
                    continue
                right = rng.choice(compatible)
                p = substitute(right[0], 'x', left[0])
            try:                          # an attempt it cannot form, run or sample inputs for is a failed attempt
                if LG.size(expand(p, concepts)) > 40 or family(p, concepts) in self.reserved:
                    continue
                # Transient observer partition gate. No hidden law/template,
                # pool, callback or bound method is retained by Sleep.
                if filter_program is not None and not filter_program(p, concepts):
                    continue
                xs = tuple(sample_input(left[1], rng) for _ in range(4))
                ys = tuple(independent(p, {'x': x}, concepts) for x in xs)
                if any(observed(LG.evaluate(p, {'x': x}, concepts)) != y for x, y in zip(xs, ys)):
                    raise ValueError('Dream executor disagreement')
            except (ValueError, KeyError, *LG.BAD):
                continue
            if len(set(map(repr, ys))) < 2 or ys == xs:
                continue                  # constant floods and identity aliases
            key = digest([left[1], right[2], xs, ys])
            if key in behavior:
                continue
            behavior.add(key)
            try:                          # (a dream's outputs can outgrow the port: PortBudget, a ValueError)
                view = TaskView((('x', left[1]),), right[2],
                                tuple((((('x', x),)), y) for x, y in zip(xs, ys)))
                receipt = Receipt.make(view, (p,), concepts, scope='dream-self-task', origin='dream',
                                       source='dream:'+key)
                self.admit(receipt, concepts)
            except ValueError:
                continue
            made.append(receipt)
            if curiosity is not None and gap is not None:
                curiosity.dream_result(gap, route, receipt, concepts)
                curiosity.dream_log[-1]['part'] = part if aimed else None
        self.logs.append(dict(kind='dream', count=len(made), attempted=attempts,
                              wall=time.perf_counter()-started, factual_observations=0))
        return made

    def training_rows(self, batch):
        """Validate receipt labels without changing the original slot order."""
        rows = []
        for receipt, snapshot in batch:
            if receipt.id not in self.consumed:
                raise ValueError('Unadmitted training receipt')
            receipt.check(snapshot, reserved=self.reserved, sources=self.reserved_sources)
            concepts = self.mind.proposer.admitted(self.mind.engine._concepts())
            targets = []
            for p in receipt.targets:
                try:
                    valid_call = expand(p, concepts) == expand(p, snapshot)
                except ValueError:
                    valid_call = False
                targets.append(p if valid_call else expand(p, snapshot))
            rows.append((receipt.view, tuple(targets), concepts))
        return rows

    def check_dreams(self, dreams=None):
        """Optional diagnostic read of checked self-tasks; no new evidence or decisions."""
        batch = self.dreams if dreams is None else tuple(dreams)
        for receipt, _ in batch:
            if receipt.origin != 'dream':
                raise ValueError('Dream diagnostic requires dream receipts')
        rows = self.training_rows(batch)
        with torch.no_grad():
            return program_log_probabilities(self.mind.proposer, rows, batched_reads=self.mind.batched_reads)

    def train(self, batches=1, batch_size=8, *, deadline=math.inf, reading=()):
        if not self.replay:
            raise ValueError('No independently checked wake replay')
        logs = []
        if self.mind.proposer.memory is not None:
            for text in reading:
                self.mind.field.ideas.read(tuple(text.split()))
        for _ in range(batches):
            if time.time() >= deadline:
                break
            start = time.perf_counter()
            # Eight slots round 40/50/10 to 3/4/1. Reading is authorized text only;
            # if absent that slot becomes checked wake replay and is disclosed.
            n_wake = max(1, round(.4*batch_size))
            n_dream = round(.5*batch_size)
            use_dreams = self.mind.crutches['program_dreams'] and bool(self.dreams)
            batch = [self.mind.random.choice(self.replay) for _ in range(n_wake)]
            batch += [self.mind.random.choice(self.dreams if use_dreams else self.replay) for _ in range(n_dream)]
            reading_slots = max(0, batch_size-len(batch)) if reading else 0
            batch += [self.mind.random.choice(self.replay) for _ in range(max(0, batch_size-len(batch)-reading_slots))]
            self.mind.optimizer.zero_grad(set_to_none=True)
            losses = []
            understanding_losses = []
            rows = self.training_rows(batch) if self.mind.batched_reads else None
            reads = (self.mind.proposer.features_many([v for v, _, _ in rows], [c for _, _, c in rows])
                     if rows is not None else [None]*len(batch))
            for slot, (receipt, snapshot) in enumerate(batch):
                if rows is None:
                    if receipt.id not in self.consumed:
                        raise ValueError('Unadmitted training receipt')
                    receipt.check(snapshot, reserved=self.reserved, sources=self.reserved_sources)
                    # Keep the complete pre-US single-slot path when batching is off.
                    concepts = self.mind.proposer.admitted(self.mind.engine._concepts())
                    targets = []
                    for p in receipt.targets:
                        try:
                            valid_call = expand(p, concepts) == expand(p, snapshot)
                        except ValueError:
                            valid_call = False
                        targets.append(p if valid_call else expand(p, snapshot))
                    targets = tuple(targets)
                else:
                    _, targets, concepts = rows[slot]
                losses.append(-program_log_probability(self.mind.proposer, receipt.view, targets, concepts,
                                                       read=reads[slot]))
                if receipt.origin != 'dream' and self.mind.proposer.memory is not None:
                    ps = tuple(p for target in targets for p in LG.parts(target))
                    understanding_losses.append(self.mind.memory.checked_loss(receipt.view, ps, read=reads[slot]))
            program_loss = torch.stack(losses).mean()
            reading_loss = program_loss.new_zeros(())
            for _ in range(reading_slots):
                text = self.mind.random.choice(tuple(reading))
                raw = list(text.encode('utf-8'))
                if not raw or len(raw) > 256:
                    raise ValueError('Authorized reading chunk must contain 1..256 UTF-8 bytes')
                ids = torch.tensor(raw, device=self.mind.device, dtype=torch.long)
                embeddings = self.mind.owner.words(ids+1)[None]
                ordered = self.mind.owner.local(embeddings.transpose(1, 2)).transpose(1, 2).tanh()[0]
                reading_loss = reading_loss+F.cross_entropy(self.mind.owner.reading_decoder(ordered), ids)/reading_slots
            understanding_loss = (torch.stack(understanding_losses).mean() if understanding_losses
                                  else program_loss.new_zeros(()))
            loss = program_loss+.1*reading_loss+understanding_loss
            before = {k: v.detach().clone() for k, v in self.mind.owner.named_parameters()}
            loss.backward()
            gradient = {}
            for group, prefix in (('input', ('words', 'raw_port', 'local', 'text_')), ('core', ('core.', 'flow.',)),
                                  ('readout', ('joint_readout', 'production_'))):
                gradient[group] = sum(float(p.grad.detach().square().sum()) for n, p in
                                      self.mind.owner.named_parameters() if n.startswith(prefix) and p.grad is not None)**.5
            norm = float(torch.nn.utils.clip_grad_norm_(self.mind.owner.parameters(), 1., error_if_nonfinite=True))
            self.mind.optimizer.step()
            delta = sum(float((p.detach()-before[n]).square().sum()) for n, p in self.mind.owner.named_parameters())**.5
            if not all(bool(torch.isfinite(p).all()) for p in self.mind.owner.parameters()):
                raise ValueError('Nonfinite owner update')
            self.mind.updates += 1
            self.mind.proposer.changed()
            row = dict(kind='train', update=self.mind.updates, program=float(program_loss.detach()),
                       reading=float(reading_loss.detach()), objective=float(loss.detach()),
                       gradient=gradient, clip_input_norm=norm, parameter_change=delta,
                       wake=len(batch)-(n_dream if use_dreams else 0), dreams=n_dream if use_dreams else 0,
                       reading_slots=reading_slots, wall=time.perf_counter()-start, portfolio_credit=0)
            if any(self.mind.crutches.get(k, False) for k in ('memory_layer_a', 'memory_layer_b', 'field_understanding')):
                row['understanding'] = float(understanding_loss.detach())
                row['understanding_mix'] = self.mind.memory.mix()
            logs.append(row)
            self.logs.append(row)
        return logs

# U6 checks are fixed mechanisms; every retained decoder parameter is Field data.
GAP_CHECKS = ('committee', 'memories', 'roadmap', 'calibration', 'surprise',
              'familiar_failure', 'proposer_search', 'concept_body')


def gap_parts(programs, view):
    parts = {('type', typ) for _, typ in view.inputs} | {('type', view.out)}
    parts.add(('kind', gap_kind(view)))
    for p in programs:
        for q in walk(p):
            if q[0] == 'c':
                parts.add(('concept', q[1]))
            else:
                parts.add(('production', q[0]))
    return tuple(sorted(parts, key=repr))


def gap_kind(view):
    # No task name, subject, private target or observer kind.
    return f"{view.form}:{','.join(sorted(t for _, t in view.inputs))}->{view.out}"


@dataclass(frozen=True)
class Syndrome:
    check: str
    value: float
    parts: tuple
    cost: float
    inputs: tuple = ()

    def __post_init__(self):
        if self.check not in GAP_CHECKS or not math.isfinite(self.value) or not math.isfinite(self.cost) or self.cost < 0:
            raise ValueError('Finite registered self-check and nonnegative cost required')


class Curiosity:
    """Online Field readout over check/part paths and settled moment features.

    Inputs are explicit public views, own programs/measurements, and received
    verdicts. No generic task/record/observer dictionary is accepted here.
    Returns update both check reliabilities and their contextual decoder paths.
    """
    def __init__(self):
        self.weights = {k: 1. for k in GAP_CHECKS}
        self.weight_paths = {k: [1.] for k in GAP_CHECKS}
        self.paths = {}                  # (check, location) -> 65-d online readout
        self.typical = {}                # record kind -> count, running mean
        self.calibration = {}            # public kind -> count, signed error sum
        self.surprises = []              # observed native defects in this task
        self.gap = None
        self.last_checks = ()
        self.history = {}                # public cue -> own prior outcome
        self.returns = []
        self.dream_returns = {'aimed': [1., 1.], 'random': [1., 1.]}
        self.share_path = [.5]
        self.dream_trials = {}           # cue -> aimed/random attempted work
        self.dream_log = []
        self.found = {}                  # cue -> gap first observed while unsolved
        self.later_solved = set()
        self.step = 0

    @property
    def dream_share(self):
        means = [a/(a+b) for a, b in (self.dream_returns[k] for k in ('aimed', 'random'))]
        return means[0]/sum(means)

    def observe(self, kind, value):
        value = float(value)
        if not math.isfinite(value):
            raise ValueError('Finite own Field defect required')
        n, mean = self.typical.get(kind, (0, 0.))
        if n:
            self.surprises.append((value-mean)/(1.+abs(mean)))
        self.typical[kind] = (n+1, mean+(value-mean)/(n+1))

    def verdict(self, kind, probability, right, source='proof'):
        if source not in ('proof', 'refutation', 'teacher', 'book', 'talk'):
            raise ValueError('Only actually received outer/teacher/book/talk verdicts')
        if type(right) is not bool or not 0 <= probability <= 1:
            raise ValueError('Own prediction and received boolean verdict required')
        bins = self.calibration.setdefault(kind, [[0, 0., 0.] for _ in range(10)])
        row = bins[min(9, int(probability*10))]
        row[0] += 1
        row[1] += probability
        row[2] += float(right)

    def checks(self, view, candidates, concepts, *, memories=(), roadmap=(),
               log_u=None, log_b=None, surest=None, accepted=None):
        if type(view) is not TaskView:
            raise TypeError('Only the allowlisted public TaskView enters curiosity')
        candidates = tuple(dict.fromkeys(candidates))[:16]
        kind = gap_kind(view)
        parts = gap_parts(candidates, view) if view.form == 'exact' else gap_parts((), view)
        rows = []

        def add(name, run):
            start = time.perf_counter()
            value, located, inputs = run()
            rows.append(Syndrome(name, float(value), tuple(located), time.perf_counter()-start, tuple(inputs)))

        def committee():
            if view.form != 'exact':
                return 0., (), ()
            fitting = [p for p in candidates if all(LG.safe(p, dict(b), concepts) == y for b, y in view.examples)]
            seen = {b for b, _ in view.examples}
            disagree, implicated = [], []
            for b in view.queries:
                if b in seen:
                    continue
                values = [(p, LG.safe(p, dict(b), concepts)) for p in fitting]
                # Missing executions are not answers from a fitting committee.
                values = [(p, y) for p, y in values if y is not None]
                if len({repr(y) for _, y in values}) > 1:
                    disagree.append(b)
                    implicated.extend(p for p, _ in values)
            return float(bool(disagree)), gap_parts(implicated, view) if disagree else (), tuple(dict.fromkeys(disagree))
        add('committee', committee)

        def memory():
            if not memories:
                return 0., (), ()
            # Paired A/B familiarity recalls of exactly the same cue and part.
            differences = [(part, math.log1p(max(0., a))-math.log1p(max(0., b))) for part, a, b in memories]
            part, error = max(differences, key=lambda row: abs(row[1]))
            return error, (part, ('kind', kind)), ()
        add('memories', memory)

        def execution():
            missed = [(p, bindings) for p, bindings, predicted, computed in roadmap if predicted != computed]
            return float(bool(missed)), gap_parts([p for p, _ in missed], view) if missed else (), [b for _, b in missed]
        add('roadmap', execution)
        def calibration():
            bins = self.calibration.get(kind, ())
            n = sum(row[0] for row in bins)
            errors = [(predicted-right)/max(1, n) for count, predicted, right in bins if count]
            return max(errors, key=abs) if errors else 0., parts, ()
        add('calibration', calibration)
        add('surprise', lambda: (max(self.surprises, key=abs) if self.surprises else 0., parts, ()))

        def familiar():
            # U and B are already normalized probabilities in the same pool.
            failures = [(p, math.exp(log_u[p])-math.exp(log_b[p])) for p in candidates
                        if log_u is not None and log_b is not None and p in log_u and p in log_b
                        and math.exp(log_u[p]) > math.exp(log_b[p])]
            if not failures:
                return 0., (), ()
            p, error = max(failures, key=lambda row: row[1])
            return error, gap_parts((p,), view), ()
        add('familiar_failure', familiar)
        present = gap_parts((accepted,), view) if view.form == 'exact' and accepted is not None else ()
        add('proposer_search', lambda: (float(surest is not None and accepted is not None and surest not in present),
                                       (surest, ('kind', kind)) if surest is not None else (), ()))

        def bodies():
            if view.form != 'exact':
                return 0., (), ()
            bad, inputs = [], []
            for p in candidates:
                if not any(q[0] == 'c' for q in walk(p)):
                    continue
                try:
                    body = expand(p, concepts)
                    for b in tuple(dict.fromkeys(tuple(b for b, _ in view.examples)+view.queries)):
                        if LG.safe(p, dict(b), concepts) != LG.safe(body, dict(b), {}):
                            bad.append(p); inputs.append(b)
                except (ValueError, KeyError, *LG.BAD):
                    # Unsupported/missing library calls are a bug flag too.
                    bad.append(p)
            return float(bool(bad)), gap_parts(bad, view) if bad else (), tuple(dict.fromkeys(inputs))
        add('concept_body', bodies)
        return tuple(rows)

    @staticmethod
    def moment(features):
        import numpy as np
        z = np.asarray(features, float)
        if z.shape != (3, 64) or not np.isfinite(z).all():
            raise ValueError('Three finite settled Field branches required')
        z = np.tanh(z.mean(0))
        return np.r_[1., z/max(1., float(np.linalg.norm(z)))]

    def decode(self, view, checks, features):
        import numpy as np
        if type(view) is not TaskView or any(type(row) is not Syndrome for row in checks):
            raise TypeError('Decoder needs a public view and registered syndrome rows')
        x = self.moment(features)
        self.last_checks = tuple(checks)
        scores, links = {}, {}
        self.step += 1
        for row in checks:
            if not row.value:
                self.weights[row.check] = max(.01, .99*self.weights[row.check])
            for part in (row.parts if row.value else ()):
                path = (row.check, part)
                w = self.paths.get(path, np.zeros(65))
                strength = abs(row.value)*self.weights[row.check]*math.exp(float(np.clip(w @ x, -8., 8.)))
                scores[part] = scores.get(part, 0.)+strength/max(1, len(row.parts))
                links.setdefault(part, []).append((row.check, abs(row.value)))
            self.weight_paths[row.check].append(self.weights[row.check])
        total = sum(scores.values())
        if not total:
            self.gap = None
            return None
        distribution = tuple((p, scores[p]/total) for p in sorted(scores, key=repr))
        if not self.history.get(view.identity, {}).get('solved', False):
            self.found.setdefault(view.identity, self.step)
        self.gap = dict(cue=view.identity, view=view, distribution=distribution, links=links, x=x,
                        checks=checks, inputs=tuple(dict.fromkeys(b for row in checks if row.check == 'committee' for b in row.inputs)),
                        words=view.words, step=self.step)
        return self.gap

    def reinforce(self, gap, reward):
        import numpy as np
        reward = min(1., max(0., float(reward)))
        active = {row.check for row in gap['checks'] if row.value}
        # Reward/no-return increases/decreases the actual attributed paths.
        for check in GAP_CHECKS:
            if check in active:
                self.weights[check] = min(100., max(.01, self.weights[check]*math.exp(.2*(reward if reward > 0 else -1.))))
            self.weight_paths[check].append(self.weights[check])
        for part, probability in gap['distribution']:
            for check, strength in gap['links'][part]:
                key = (check, part)
                w = self.paths.setdefault(key, np.zeros(65))
                prediction = 1./(1.+math.exp(-float(np.clip(w @ gap['x'], -30., 30.))))
                label = float(reward > 0)
                amount = reward if reward > 0 else 1.
                w += .35*probability*min(1., strength)*amount*(label-prediction)*gap['x']

    def finish(self, cue, gap, checks, *, solved, search):
        if type(solved) is not bool or not math.isfinite(search) or search < 0:
            raise ValueError('Own completed-run result and charged search time required')
        values = {row.check: abs(row.value) for row in checks}
        before = self.history.get(cue)
        rewards = []
        if before:
            rewards += [float(solved and not before['solved']),
                        max(0., (before['search']-search)/max(before['search'], 1e-9)) if solved and before['solved'] else 0.]
            rewards += [float(before['values'].get(k, 0.) > 0 and values.get(k, 0.) == 0) for k in GAP_CHECKS]
        if gap:
            rewards += [float(abs(row.value) > 0 and values.get(row.check, 0.) == 0) for row in gap['checks']]
            if not solved and cue not in self.found:
                self.found[cue] = self.step
            if before is None:
                rewards.append(float(solved))
        reward = max(rewards, default=0.)
        credited = gap or (before or {}).get('gap')
        if credited:
            self.reinforce(credited, reward)
        trials = self.dream_trials.pop(cue, {})
        for route in sorted(trials):
            # Matched return attribution; no reward for merely admitting a dream.
            a, b = self.dream_returns[route]
            trial = trials[route]
            gain = reward*trial['eligible']/max(1, trial['attempted'])
            self.dream_returns[route] = [a+gain, b+1.-gain]
        if trials:
            self.share_path.append(self.dream_share)
        if solved and cue in self.found:
            self.later_solved.add(cue)
        self.history[cue] = dict(solved=solved, search=search, values=values, gap=credited)
        self.returns.append(dict(cue=cue, reward=reward, solved=solved, search=search,
                                 dream_routes=sorted(trials), later_solved=cue in self.later_solved))

    def dream_trial(self, gap, route, admitted):
        if gap is None:
            return
        rows = self.dream_trials.setdefault(gap['cue'], {})
        trial = rows.setdefault(route, dict(attempted=0, eligible=0.))
        trial['attempted'] += 1
        self.dream_log.append(dict(cue=gap['cue'], route=route, admitted=bool(admitted)))

    def dream_result(self, gap, route, receipt, concepts):
        present = set(gap_parts(receipt.targets, receipt.view))
        structural = [(p, mass) for p, mass in gap['distribution'] if p[0] in ('production', 'concept')]
        located = structural or list(gap['distribution'])
        relevance = sum(mass for p, mass in located if p in present)/sum(mass for _, mass in located)
        self.dream_trials[gap['cue']][route]['eligible'] += relevance
        self.dream_log[-1].update(admitted=True, receipt=receipt.id, relevance=relevance)

    def study_order(self, views):
        if any(type(v) is not TaskView for v in views):
            raise TypeError('Study ordering accepts public book views only')
        if not self.gap:
            return list(range(len(views)))
        words = {w for text in self.gap['words'] for w in text.lower().split()}
        for part, _ in self.gap['distribution']:
            if part[0] in ('production', 'type'):
                words.add(str(part[1]).lower())
        kinds = {p[1]: mass for p, mass in self.gap['distribution'] if p[0] == 'kind'}
        def score(v):
            heard = {w for text in v.words for w in text.lower().split()}
            return len(words & heard)+kinds.get(gap_kind(v), 0.)
        return sorted(range(len(views)), key=lambda j: (-score(views[j]), j))

    def report(self):
        return dict(weights=dict(self.weights), weight_paths={k: list(v) for k, v in self.weight_paths.items()},
                    decoder_paths={repr(path): w.tolist() for path, w in sorted(self.paths.items(), key=lambda row: repr(row[0]))},
                    dream_share=self.dream_share, share_path=list(self.share_path),
                    gaps_found=len(self.found), gaps_later_solved=len(self.later_solved),
                    returns=list(self.returns),
                    locations=[] if self.gap is None else [(repr(p), mass) for p, mass in self.gap['distribution']],
                    checks_registered=list(GAP_CHECKS),
                    checks=[dict(check=r.check, value=r.value, parts=r.parts, cost=r.cost, inputs=r.inputs)
                            for r in self.last_checks])


def aimed_compositions(generators, concepts, part, *, deadline=math.inf):
    """Known generator plus located part, within the existing typed dream scope."""
    candidates = []
    def keep(p, tin, tout):
        view = TaskView((('x', tin),), tout)
        if part in gap_parts((p,), view) and LG.size(expand(p, concepts)) <= 40:
            candidates.append((p, tin, tout))
    for left in generators:
        if time.time() >= deadline:
            break
        for right in generators:
            if time.time() >= deadline:
                break
            if right[1] == left[2]:
                keep(substitute(right[0], 'x', left[0]), left[1], right[2])
            if len(candidates) >= 256:
                return list(dict.fromkeys(candidates))
        # At the edge: insert an innate typed operation not yet in a generator.
        if part[0] == 'production':
            import itertools
            types = sorted(LG.universe([t for _, tin, tout in generators for t in (tin, tout)]),
                           key=lambda t: (LG.depth(t), t))
            for tout in types:
                for prod in legal(tout, {'x': left[1]}, concepts, (), types):
                    if time.time() >= deadline or len(candidates) >= 256:
                        return list(dict.fromkeys(candidates))
                    if prod.sym != part[1] or not prod.args:
                        continue
                    slots = []
                    for typ in prod.args:
                        if typ.startswith('lam:'):
                            kind, result = typ[4:].split('>')
                            elem = LG.elem(prod.args[-1])
                            acc = prod.args[1] if kind == 'ae' else 'num'
                            bindings = bound_types(kind, (elem, acc))
                            bodies = []
                            for name, source_type in sorted(bindings.items()):
                                for body, tin, ret in generators:
                                    if tin == source_type and ret == result:
                                        bodies.append(substitute(body, 'x', LG.node('var', payload=name)))
                            slots.append([LG.node('lam', body, payload=kind) for body in dict.fromkeys(bodies)])
                        else:
                            options = [body for body, tin, ret in generators if tin == left[1] and ret == typ]
                            if left[1] == typ:
                                options.append(LG.node('var', payload='x'))
                            slots.append(list(dict.fromkeys(options)))
                    # Bounded mixed-type/lambda grafts, still containing a known
                    # accepted component rather than a supplied domain program.
                    for j, args in enumerate(itertools.product(*slots)):
                        if j >= 64 or time.time() >= deadline or len(candidates) >= 256:
                            break
                        if any(left[0] == child or left[0] in tuple(walk(child)) for child in args):
                            keep(LG.node(prod.sym, *args, payload=prod.pay), left[1], tout)
    return list(dict.fromkeys(candidates))
