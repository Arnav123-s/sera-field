"""U13: removable basis changes, reconstruction and prequential estimates.

Construction certificates say what an executable macro expands to. Fresh relation
checks are sampled evidence. Neither supplies a world certificate or primitive.
"""
import copy
import math
import time

import numpy as np

from sera import lang as LG, phi as PH, tasks as TS
from .discovery import Certification, Readout
from .einstein import EinsteinMethods, PHASE_WEIGHTS, nodes
from .ports import digest, observed
from .proposer import library_identity
from .sleep import checked_substitution, expand, independent, rewrite, sample_input, substitute

CRUTCHES = ('own_operations', 'rederive_concepts', 'rough_estimates')
LIMIT = 32


def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()
                if key not in ('seconds', 'seconds_cut', 'recorded_at', 'performed_at')}
    if isinstance(value, (tuple, list)):
        return type(value)(clean(item) for item in value)
    return value


def signed_order(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('A finite scalar result is required')
    return math.copysign(math.log10(1.+abs(value)), value) if value else 0.


def checked_operation(program, body, signature, inputs, concepts, cid):
    """Sleep.abstract's two-executor checked substitution, before Field mutation."""
    if LG.infer(body, concepts) is None or not LG.fits(LG.infer(body, concepts), *signature):
        raise ValueError('Ill-typed operation')
    if not inputs or cid in concepts:
        raise ValueError('Fresh production and nonempty executed inputs required')
    expanded = expand(program, concepts)  # refuses dangling/recursive concepts
    candidate = dict(id=cid, body=body)
    table = copy.deepcopy(concepts)
    table[cid] = (body, '_')
    table.setdefault('_sig', {})[cid] = tuple(signature)
    rewritten = rewrite(program, candidate)
    if rewritten == program or expand(rewritten, table) != expanded:
        raise ValueError('Not an exact substitution')
    for value in inputs:
        env = {'x': value}
        target = independent(expanded, env, {})
        if observed(LG.evaluate(expanded, env, {})) != target:
            raise ValueError('Independent execution or checked substitution failed')
    checked_substitution(expanded, rewritten, ({'x': value} for value in inputs), table)
    return rewritten


def search_cost(tin, tout, own, concepts, *, label, deadline=math.inf, size=7):
    """Bounded measured search; count generated typed nodes, including lambda tables.

    Namespaces keep the two comparison frontiers separate. Counts are actual
    generator advances in lang._grow, not source AST size or a guessed speedup.
    """
    namespace = ('u13-cost', label, digest((tin, tout, own, library_identity(concepts))))
    def count():
        return sum(sum(state.get('spent', {}).values()) for key, state in LG._TABLES.items()
                   if len(key) >= 2 and key[-2] == namespace)
    before, started = count(), time.perf_counter()
    saved = LG.DEADLINE[0]
    LG.DEADLINE[0] = min(saved, deadline, time.time()+.08)
    try:
        found = LG.search({'x': tin}, tout, [{'x': x} for x, _ in own], size, concepts,
            constants=TS.numbers_of(own), work=256, chunk=256, lambda_size=2, namespace=namespace)
    finally:
        LG.DEADLINE[0] = saved
    fitting = [p for p, _ in found if all(LG.safe(p, {'x': x}, concepts) == y for x, y in own)]
    fitting.sort(key=lambda p: (LG.size(p), repr(p)))
    return fitting, dict(nodes=max(0, count()-before), seconds=time.perf_counter()-started,
                        solved=bool(fitting), size=LG.size(fitting[0]) if fitting else None)


class RoadmapMethods(EinsteinMethods):
    def candidates(self):
        return [('observe',)] + [(key,) for key in CRUTCHES if self.switches[key]]

    def demonstrate(self, shown, moment, *, phase, origin):
        if origin != 'taught' or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No U13 teaching on rediscovery or assessment worlds')
        if not self.switches.get(shown, False):
            return False
        feature = self.features(moment)
        a, b = self.taught.setdefault(('roadmap', (shown,)),
            [np.zeros((self.d, self.d)), np.zeros(self.d)])
        weight = PHASE_WEIGHTS[phase]
        a += weight*np.outer(feature, feature)/self.noise**2
        b += weight*feature/self.noise**2
        return True


class Roadmap:
    def __init__(self, switches):
        if set(switches) != set(CRUTCHES) or any(type(v) is not bool for v in switches.values()):
            raise ValueError('Declare all three boolean U13 switches')
        self.switches = dict(switches)
        self.methods, self.estimate_choice = RoadmapMethods(switches), Readout()
        self.wishes, self.operations, self.rebuilds = {}, {}, {}
        self.attempted = set()
        self.estimates, self.errors, self.searches, self.mistakes = [], [], [], []
        # Neutral Bayesian linear readout in the Field; targets are own signed orders.
        self.precision, self.target = np.eye(65), np.zeros(65)
        self.residuals = []
        self.phase_weight, self.teacher_shown = 1., False
        self.serial = 0
        self.estimate_serial = 0
        self.estimate_counts = dict(made=0, settled=0, covered=0)
        self.pruning_counts = dict(trials=0, audits=0, gains=0, censored_fallbacks=0)
        self.costs = dict.fromkeys(CRUTCHES, 0.)

    def attach(self, field):
        field.roadmap_methods = self.methods
        field.roadmap_readout = self

    def basis(self, concepts):
        """Advertise the better audited version; keep the original executable."""
        if not self.switches['rederive_concepts']:
            return concepts
        signatures = dict(concepts.get('_sig', {}))
        for _, entry in sorted(self.rebuilds.items()):
            if entry.get('kept') and entry['concept'] in signatures:
                signatures.pop(entry['original'], None)
        return {**concepts, '_sig': signatures}

    def learning_state(self):
        return clean({key: value for key, value in self.__dict__.items() if key not in ('searches', 'costs')})

    def demonstrate(self, mind, view, *, phase, origin):
        if origin != 'taught' or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No U13 teaching on rediscovery or assessment worlds')
        self.methods.bind(mind.engine._u_reads([view])[0][0].detach().cpu().numpy())
        moment = dict(doubt=1., misfit=0., proven=len(mind.field.concepts))
        shown = tuple(key for key in CRUTCHES if self.methods.demonstrate(key, moment, phase=phase, origin=origin))
        self.teacher_shown = True
        return shown

    def phase(self, name):
        weight = PHASE_WEIGHTS[name]
        ratio = weight/self.phase_weight if self.phase_weight else 0.
        for policy in (self.methods, self.estimate_choice):
            for a, b in policy.taught.values():
                a *= ratio
                b *= ratio
        self.phase_weight = weight

    def wish(self, signature, source):
        if not self.switches['own_operations']:
            return
        key = tuple(signature)
        item = self.wishes.setdefault(key, dict(count=0, sources=[]))
        item['count'] += 1
        if source not in item['sources']:
            item['sources'].append(source)

    def build(self, mind, *, deadline):
        if not self.switches['own_operations'] or not mind.crutches['sleep_library']:
            return 0.
        concepts = mind.proposer.admitted(mind.field.concept_table())
        candidates = {}
        # Received certificates and own definitions only; no world/template body.
        for receipt, snapshot in mind.sleep.replay[-LIMIT:]:
            if time.time() >= deadline:
                return 0.
            try:
                receipt.check(snapshot, reserved=mind.sleep.reserved, sources=mind.sleep.reserved_sources)
                var, tin = receipt.view.inputs[0]
                for original in receipt.targets:
                    program = substitute(expand(original, snapshot), var, LG.node('var', payload='x'))
                    for part in sorted(set(nodes(program)), key=repr):
                        if LG.size(part) < 3 or LG.size(part) > 12 or ('var', 'x') not in LG.parts(part):
                            continue
                        body = substitute(part, 'x', LG.node('var', payload='_'))
                        sig = LG.infer(body, concepts)
                        if sig is None or not LG.fits(sig, tin, receipt.view.out):
                            continue
                        key = digest((body, sig))
                        entry = candidates.setdefault(key, dict(body=body, sig=(tin, receipt.view.out), part=part, sources={}, xs=[]))
                        entry['sources'][receipt.source] = receipt.id
                        entry['xs'].extend(dict(bindings)[var] for bindings, _ in receipt.view.examples)
            except (ValueError, KeyError, *LG.BAD):
                continue
        for key, entry in sorted(candidates.items()):
            wish = self.wishes.get(entry['sig'], {})
            if (len(entry['sources']) < 2 or wish.get('count', 0) < 2 or key in self.operations or
                    any(c['body'] == entry['body'] for c in mind.field.concepts)):
                continue
            xs = tuple(dict.fromkeys(entry['xs']))[:8]
            if not xs:
                continue
            cid = max(getattr(mind.field, 'next_id', 0), len(mind.field.concepts)+1)
            try:
                checked_operation(entry['part'], entry['body'], entry['sig'], xs, concepts, cid)
            except (ValueError, KeyError, *LG.BAD):
                self.operations[key] = dict(admitted=False, reason='execution/substitution failed')
                return -1.
            certificate = dict(kind='exact checked substitution', sources=tuple(sorted(entry['sources'].values())),
                               body=entry['body'], signature=entry['sig'], inputs=xs)
            c = mind.field.invent(entry['body'], entry['sig'], 'code' if LG.is_list(entry['sig'][0]) else 'math',
                'own operation', LG.parts(entry['body']), extra=dict(u13_operation=certificate))
            self.operations[key] = dict(admitted=True, concept=c['id'], certificate=certificate,
                                        built_serial=self.serial, seen_worlds=tuple(sorted(
                    wid for wid, rows in mind.discovery.observations.items() if rows)), later=[],
                eligibility=self.methods.features(dict(doubt=0., misfit=0., proven=len(mind.field.concepts))).copy())
            mind.proposer.changed()
            return 0.  # construction alone earns no usefulness credit
        return 0.

    def rebuild(self, mind, discovery, pool, *, deadline):
        if not self.switches['rederive_concepts'] or not mind.crutches['sleep_library'] or not hasattr(pool, 'audit_relation'):
            return 0.
        table = mind.proposer.admitted(mind.field.concept_table())
        for cid in sorted(table.get('_sig', {}), key=repr)[:LIMIT]:
            token = digest((cid, table[cid], table['_sig'][cid]))
            if token in self.attempted or time.time() >= deadline:
                continue
            self.attempted.add(token)
            tin, tout = table['_sig'][cid]
            if tin not in ('num', 'list') or tout not in ('num', 'list'):
                continue
            lhs = LG.node('c', LG.node('var', payload='x'), payload=cid)
            try:
                expand(lhs, table)  # reject a dangling acquired definition before execution
                # Only these computed values cross into reconstruction search.
                xs = tuple(sample_input(tin, mind.random) for _ in range(8))
                own = tuple((x, observed(LG.evaluate(lhs, {'x': x}, table))) for x in xs)
                if any(independent(lhs, {'x': x}, table) != y for x, y in own):
                    return -1.
                alternatives, cost = search_cost(tin, tout, own, {}, label=('rebuild', token), deadline=deadline)
            except (ValueError, KeyError, *LG.BAD):
                return -1.
            record = dict(original=cid, own_values=own, body_hidden=True, primitives_only=True,
                          reconstruction=cost, audited=False, kept=False, original_preserved=True, reuse=0, original_reuse=0)
            self.rebuilds[token] = record
            if not alternatives:
                return 0.
            rhs = alternatives[0]
            audit = getattr(pool, 'audit_reconstruction', pool.audit_relation)
            verdict = audit(lhs, rhs, tin, tout, copy.deepcopy(table), own)
            if type(verdict) is not Certification:
                raise TypeError('Unsafe reconstruction audit')
            discovery.checks += 1
            record.update(audited=True, certificate=verdict, accepted=verdict.accepted, rebuilt=rhs)
            if not verdict.accepted:
                return -1.
            exact = expand(lhs, table) == rhs and all(independent(rhs, {'x': x}, {}) == y
                and observed(LG.evaluate(rhs, {'x': x}, {})) == y for x, y in own)
            if exact:
                checked_substitution(expand(lhs, table), rhs, ({'x': x} for x, _ in own), {})
            record['evidence'] = 'exact checked rewrite' if exact else 'sampled equivalence, not proof'
            original_body = expand(lhs, table)
            # A fresh composition, executed from the original. Neither search sees its body.
            composition = (substitute(original_body, 'x', original_body) if tin == tout else
                           LG.node('add', original_body, LG.node('one')) if tout == 'num' else None)
            if composition is None:
                return 0.
            try:
                probes = tuple(sample_input(tin, mind.random) for _ in range(6))
                values = tuple((x, independent(composition, {'x': x}, {})) for x in probes)
                baseline = {cid: table[cid], '_sig': {cid: (tin, tout)}}
                # Expand the original to exclude dependency productions equally in both arms.
                baseline[cid] = (substitute(original_body, 'x', LG.node('var', payload='_')), '_')
                rebuilt = {cid: (substitute(rhs, 'x', LG.node('var', payload='_')), '_'), '_sig': {cid: (tin, tout)}}
                _, before = search_cost(tin, tout, values, baseline, label=('original', token), deadline=deadline)
                _, after = search_cost(tin, tout, values, rebuilt, label=('rederived', token), deadline=deadline)
            except (ValueError, KeyError, *LG.BAD):
                return 0.
            record.update(composition=dict(original=before, rebuilt=after), later_values=values)
            score = lambda cost, body: (int(cost['solved']), -cost['nodes'], -LG.size(body))
            if not after['solved'] or score(after, rhs) <= score(before, original_body):
                return 0.
            body = substitute(rhs, 'x', LG.node('var', payload='_'))
            c = mind.field.invent(body, (tin, tout), 'math' if tin == 'num' else 'code',
                'own reconstruction', LG.parts(body), extra=dict(u13_reconstruction=verdict, u13_original=cid))
            record.update(kept=True, concept=c['id'],
                eligibility=self.methods.features(dict(doubt=0., misfit=0., proven=len(mind.field.concepts))).copy())
            mind.proposer.changed()
            return 0.  # later certified reuse, not sampled agreement, earns method return
        return 0.

    def estimate_features(self, mind, discovery, wid, action):
        view = discovery.view(wid, (action[1],))
        read = mind.engine._u_reads([view])[0][0].detach().cpu().numpy()
        feature = PH.InnerJudge.features(read)
        feature = np.asarray(feature, float).copy()
        feature[-1] = signed_order(action[1]) / 10.
        return feature

    def predict(self, mind, discovery, wid, action):
        if not self.switches['rough_estimates'] or action[0] != 'ask' or discovery.worlds[wid].tout != 'num':
            return None
        if type(action[1]) not in (int, float):
            return None
        started = time.perf_counter()
        feature = self.estimate_features(mind, discovery, wid, action)
        cov = np.linalg.inv(self.precision)
        mean = float(np.clip(feature @ cov @ self.target, -13., 13.))
        residual = float(np.mean(self.residuals[-LIMIT:])) if self.residuals else 1.
        radius = min(6., max(1., 2.*math.sqrt(max(0., residual)+float(feature @ cov @ feature))))
        interval = (max(-13., mean-radius), min(13., mean+radius))
        if interval[0] > interval[1]:
            interval = (-13., 13.)
        pid = self.estimate_serial
        self.estimate_serial += 1
        self.estimate_counts['made'] += 1
        self.estimates.append(dict(id=pid, world=wid, action=observed(action), feature=feature,
            signed_log_interval=interval,
            interval=tuple(math.copysign(10.**abs(v)-1., v) if v else 0. for v in interval), mean=mean, result=None, covered=None, error=None,
            recorded_at=time.time(), performed_at=None, serial=self.serial))
        self.estimates = self.estimates[-128:]
        self.costs['rough_estimates'] += time.perf_counter()-started
        return pid

    def settle(self, pid, observation):
        if pid is None:
            return 0.
        record = next(row for row in self.estimates if row['id'] == pid)
        if record['result'] is not None:
            raise ValueError('Estimate already settled')
        if observation[0] != record['action'][1]:
            raise ValueError('Estimate received a different act')
        target = signed_order(observation[1])
        error = target-record['mean']
        covered = record['signed_log_interval'][0] <= target <= record['signed_log_interval'][1]
        record.update(result=observed(observation[1]), error=error, covered=covered, performed_at=time.time())
        feature = record['feature']
        self.estimate_counts['settled'] += 1
        self.estimate_counts['covered'] += int(covered)
        self.precision += np.outer(feature, feature)
        self.target += feature*target
        self.residuals.append(min(676., error*error))
        self.residuals = self.residuals[-LIMIT:]
        self.errors.append((bool(covered), min(676., error*error)))
        self.errors = self.errors[-LIMIT:]
        return 1. if covered else -1.

    def calibrated(self):
        return (len(self.errors) >= 12 and sum(hit for hit, _ in self.errors)/len(self.errors) >= .8
                and sum(error for _, error in self.errors)/len(self.errors) <= 1.)

    def order(self, mind, discovery, wid, candidates):
        """Learned fallible ordering/pruning of candidate audits; full list survives."""
        if not self.switches['rough_estimates'] or not self.calibrated():
            return tuple(candidates), None
        pending = [row for row in self.estimates if row['world'] == wid and row['result'] is None]
        if not pending:
            return tuple(candidates), None
        record = pending[-1]
        feature = record['feature']
        method = self.estimate_choice.pick(('plain', 'order', 'prune'), feature, mind.numpy)
        if method == 'plain':
            return tuple(candidates), None
        table = mind.field.concept_table()
        def outside(program):
            value = LG.safe(program, {'x': record['action'][1]}, table)
            if type(value) not in (int, float) or not math.isfinite(value):
                return True
            low, high = record['signed_log_interval']
            return not low <= signed_order(value) <= high
        rejected = tuple(p for p in candidates if outside(p))
        preferred = tuple(p for p in candidates if p not in rejected)
        ordered = preferred+rejected if method == 'order' else preferred
        trial = dict(world=wid, method=method, feature=feature, estimate=record['id'],
            original=tuple(candidates), preferred=ordered, rejected=rejected, fallback=True,
            audits=0, solved=False, accepted_baseline_rank=None, seconds=0.)
        self.pruning_counts['trials'] += 1
        self.searches.append(trial)
        self.searches = self.searches[-LIMIT:]
        return ordered, trial

    def checked(self, trial, program, verdict):
        if trial is None:
            return
        trial['audits'] += 1
        self.pruning_counts['audits'] += 1
        if verdict.accepted:
            trial['solved'] = True
            trial['accepted_baseline_rank'] = trial['original'].index(program)
            if trial['method'] == 'prune' and program in trial['rejected']:
                self.mistakes.append(dict(world=trial['world'], program=program,
                    estimate=trial['estimate'], record=verdict.record, recovered_by_fallback=True))
            gain = trial['accepted_baseline_rank']+1-trial['audits']
            self.pruning_counts['gains'] += gain
            mistake = trial['method'] == 'prune' and program in trial['rejected']
            self.estimate_choice.learn(trial['method'], trial['feature'], gain-int(mistake), 1.)

    def credit(self, method, entry, gain):
        # Saved eligibility gives delayed certified reuse back to its builder.
        feature = entry['eligibility']
        a, b = self.methods.stats.setdefault(('roadmap', (method,)),
            [np.zeros((self.methods.d, self.methods.d)), np.zeros(self.methods.d)])
        a += np.outer(feature, feature)/self.methods.noise**2
        b += feature*float(np.clip(gain, -20., 20.))/self.methods.noise**2

    def later_search(self, mind, discovery, wid, *, deadline):
        if not self.switches['own_operations'] or discovery.worlds[wid].form != 'exact':
            return
        own = tuple(discovery.observations[wid][-8:])
        if len(own) < 4:
            return
        table = mind.proposer.admitted(mind.field.concept_table())
        for key, entry in sorted(self.operations.items()):
            if not entry['admitted'] or entry['built_serial'] >= self.serial or time.time() >= deadline:
                continue
            if wid in entry['seen_worlds'] or any(row['world'] == wid for row in entry['later']):
                continue
            cid = entry['concept']
            if cid not in table:
                continue
            # Remove only this operation; preserve all old basis entries.
            baseline = copy.deepcopy(table)
            baseline.pop(cid, None)
            baseline['_sig'].pop(cid, None)
            # Guard any surviving definition that calls the removed production.
            for old in sorted(list(baseline['_sig']), key=repr):
                try:
                    expand(LG.node('c', LG.node('var', payload='x'), payload=old), baseline)
                except ValueError:
                    baseline.pop(old, None)
                    baseline['_sig'].pop(old, None)
            w = discovery.worlds[wid]
            _, before = search_cost(w.tin, w.tout, own, baseline, label=('before', key, wid), deadline=deadline)
            _, after = search_cost(w.tin, w.tout, own, table, label=('after', key, wid), deadline=deadline)
            entry['later'].append(dict(world=wid, new_composition=True, original=before, operation=after,
                nodes_cut=before['nodes']-after['nodes'], seconds_cut=before['seconds']-after['seconds']))
            gain = (float(after['solved'])-float(before['solved']) +
                    (before['nodes']-after['nodes'])/max(1, before['nodes']))
            self.credit('own_operations', entry, gain)
            return  # one bounded paired comparison per unit

    def run(self, mind, discovery, pool, wid, *, deadline):
        self.serial += 1
        self.methods.bind(mind.engine._u_reads([discovery.search_view(wid)])[0][0].detach().cpu().numpy())
        moment = dict(doubt=discovery.rival_entropy(mind, wid), misfit=discovery.surprises[wid], proven=len(discovery.laws))
        chosen = self.methods.choose('roadmap', {'observe'} | {key for key in CRUTCHES if self.switches[key]}, moment, mind.numpy)
        gains = {}
        if ('own_operations',) in chosen:
            started = time.perf_counter()
            gains['own_operations'] = self.build(mind, deadline=deadline)
            self.later_search(mind, discovery, wid, deadline=deadline)
            self.costs['own_operations'] += time.perf_counter()-started
        if ('rederive_concepts',) in chosen and time.time() < deadline:
            started = time.perf_counter()
            gains['rederive_concepts'] = self.rebuild(mind, discovery, pool, deadline=deadline)
            self.costs['rederive_concepts'] += time.perf_counter()-started
        return chosen, moment, gains

    def feedback(self, context, row, estimate_gain):
        chosen, moment, gains = context
        for method in chosen:
            gain = (estimate_gain if method == ('rough_estimates',) else
                    row['progress'] if method == ('observe',) else gains.get(method[0], 0.))
            self.methods.learn('roadmap', method, moment, float(np.clip(
                gain/max(row['seconds'], 1e-6), -20., 20.)))
        self.methods.end_task()

    def reused(self, program, wid):
        ids = {part[1] for part in nodes(program) if part[0] == 'c'}
        gain = 0.
        for entry in self.operations.values():
            if entry.get('admitted') and entry['concept'] in ids and wid not in entry.get('used_worlds', []):
                entry.setdefault('used_worlds', []).append(wid)
                entry['reuse'] = entry.get('reuse', 0)+1
                self.credit('own_operations', entry, 1.)
                gain += 1.
        for entry in self.rebuilds.values():
            if entry['original'] in ids and wid not in entry.get('original_used_worlds', []):
                entry.setdefault('original_used_worlds', []).append(wid)
                entry['original_reuse'] += 1
            if entry.get('kept') and entry['concept'] in ids and wid not in entry.get('used_worlds', []):
                entry.setdefault('used_worlds', []).append(wid)
                entry['reuse'] += 1
                self.credit('rederive_concepts', entry, 1.)
                gain += 1.
        return gain

    def report(self):
        hits = sum(hit for hit, _ in self.errors)
        def public(value):
            if isinstance(value, Certification):
                return copy.deepcopy(value.__dict__)
            if isinstance(value, dict):
                return {k: public(v) for k, v in value.items() if k != 'eligibility'}
            if isinstance(value, (tuple, list)):
                return type(value)(public(v) for v in value)
            return copy.deepcopy(value)
        return dict(operations=public(self.operations), rebuilds=public(self.rebuilds),
            seconds=dict(self.costs), estimate_counts=dict(self.estimate_counts),
            estimates=[{k: copy.deepcopy(v) for k, v in row.items() if k != 'feature'} for row in self.estimates[-4:]],
            calibration=dict(n=len(self.errors), coverage=hits/len(self.errors) if self.errors else None,
                lifetime_coverage=self.estimate_counts['covered']/self.estimate_counts['settled']
                    if self.estimate_counts['settled'] else None,
                mean_squared_order_error=sum(e for _, e in self.errors)/len(self.errors) if self.errors else None,
                earned=self.calibrated()),
            pruning=dict(**self.pruning_counts,
                mistakes=copy.deepcopy(self.mistakes), unpruned_fallback=True),
            claim='Tests of habits, not scientists insight; basis changes, not new primitive semantics or a mathematical theory')
