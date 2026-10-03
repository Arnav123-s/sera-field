"""U11 mechanisms over own acquired material. No scientific content is given.

Finite search, sampled audits and learned persistence are fallible. Only a
syntactically identical expanded rewrite can earn the exact-rewrite label.
Observer pools are transient arguments and never enter retained state.
"""
import copy
from dataclasses import asdict, is_dataclass
import math
import time

import numpy as np

from sera import lang as LG, phi as PH
from .discovery import Certification, Readout, add_proof, split_score, compression_credit
from .einstein import EinsteinMethods, PHASE_WEIGHTS, nodes, prediction_record
from .ports import digest, observed
from .sleep import expand, independent, sample_input, substitute

CRUTCHES = ('one_change_experiments', 'gap_predictions', 'number_conjectures',
            'conserved_quantities', 'anomaly_pursuit')


class ScientistMethods(EinsteinMethods):
    def candidates(self):
        return [('observe',)] + [(k,) for k in CRUTCHES if self.switches[k]]

    def demonstrate(self, shown, moment, *, phase, origin):
        if origin != 'taught' or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No demonstrations on rediscovery or assessment worlds')
        if not self.switches.get(shown, False):
            return False
        x = self.features(moment)
        a, b = self.taught.setdefault(('scientists', (shown,)),
            [np.zeros((self.d, self.d)), np.zeros(self.d)])
        weight = PHASE_WEIGHTS[phase]
        a += weight*np.outer(x, x)/self.noise**2
        b += weight*x/self.noise**2
        return True


def replace_at(p, path, replacement):
    if not path:
        return replacement
    j, *rest = path
    return p[:j] + (replace_at(p[j], tuple(rest), replacement),) + p[j+1:]


def literal_sites(p, path=()):
    if p[0] == 'lit' and type(p[1]) is int:
        yield path, p[1]
    for j in range(2, len(p)):
        yield from literal_sites(p[j], path+(j,))


def one_change_actions(world, rows, menu):
    """Mutate one coordinate of a previously performed action, never its size.

    A scalar input is one coordinate; a list keeps every other element and
    length. A push keeps object, segment boundaries and all other commands.
    """
    if not rows:
        return ()
    actions = []
    if world.form == 'exact':
        previous = rows[-1][0]
        if world.tin == 'num' and type(previous) is int:
            actions = [('ask', previous+d) for d in (-1, 1)
                       if abs(previous+d) <= LG.MAX_INT]
        elif isinstance(previous, tuple):
            for j, value in enumerate(previous):
                if type(value) is int:
                    actions.extend(('ask', previous[:j]+(value+d,)+previous[j+1:])
                        for d in (-1, 1) if abs(value+d) <= LG.MAX_INT)
    else:
        k, segments = rows[-1][:2]
        for j, (a, b, force) in enumerate(segments):
            for f in sorted(set((max(-1., force-.25), min(1., force+.25)))):
                if f != force:
                    actions.append(('push', k, segments[:j]+((a, b, f),)+segments[j+1:]))
    scores = {r['action']: r for r in menu}
    seen = {('ask', r[0]) if world.form == 'exact' else ('push', r[0], r[1]) for r in rows}
    return tuple(dict(scores.get(a, dict(action=a, info=0., surprise=0., predicted=None)),
                      one_change=True, anchor=('ask', rows[-1][0]) if world.form == 'exact'
                      else ('push', rows[-1][0], rows[-1][1]))
                 for a in sorted(set(actions)-seen, key=repr))


def motion_probes(rows, quantities=None):
    """State inputs from public throws; the time coordinate is observed time.

    q is a fitted U9 number, never the world's mass/force. Search excludes
    expressions depending only on q or t, which are uninformative invariants.
    """
    from ccops5.core import paths
    out = []
    for k, segments, xs, vs in rows:
        probes = [dict(x=float(x), v=float(v), t=j*paths.DT_OBS,
                       q=float((quantities or {}).get(k, 1.)))
                  for j, (x, v) in enumerate(zip(xs, vs))]
        out.append(tuple(probes))
    return tuple(out)


def state_body(program):
    """Pack the four observed state coordinates as one typed callable input."""
    body = program
    for j, name in enumerate(('x', 'v', 't', 'q')):
        sequence = LG.node('var', payload='_')
        for _ in range(j):
            sequence = LG.node('tail', sequence, payload='real')
        # The payload types the element: a bare head is a number's (list -> num), and rsub of two would not type.
        body = substitute(body, name, LG.node('head', sequence, payload='real'))
    return body


def conserved_fit(program, trajectories, concepts, sigma):
    """Local noise-propagation tolerance, with a nontriviality gate.

    This is sampled constancy within each trajectory, not necessarily equal
    initial values across throws. Gradients charge the expression's sensor
    sensitivity; global scaling cannot make a varying quantity constant.
    """
    if len(trajectories) < 2 or any(len(t) < 4 for t in trajectories):
        return False
    if not {'x', 'v'} & {n[1] for n in nodes(program) if n[0] == 'var'}:
        return False
    means, errors = [], []
    for trajectory in trajectories:
        values, allowances = [], []
        for env in trajectory:
            y = LG.safe(program, env, concepts)
            if type(y) not in (int, float) or not math.isfinite(y):
                return False
            variance = 0.
            for name, noise in zip(('x', 'v'), sigma):
                lo = LG.safe(program, {**env, name: env[name]-noise}, concepts)
                hi = LG.safe(program, {**env, name: env[name]+noise}, concepts)
                if lo is None or hi is None:
                    return False
                variance += ((hi-lo)/2)**2
            values.append(float(y))
            allowances.append(6*math.sqrt(variance)+1e-8)
        center = float(np.median(values))
        if any(abs(y-center) > e for y, e in zip(values, allowances)):
            return False
        means.append(center)
        errors.append(max(allowances))
    # Reject literal constants, x-x, v/v and functions numerically flat over
    # the entire observed support. Several distinct conserved initial values
    # must be resolved above the sensor allowance.
    return max(means)-min(means) > 2*max(errors)


class Scientists:
    def __init__(self, switches):
        if set(switches) != set(CRUTCHES) or any(type(v) is not bool for v in switches.values()):
            raise ValueError('Declare all five boolean U11 switches')
        self.switches = dict(switches)
        self.methods, self.persistence = ScientistMethods(switches), Readout()
        self.families, self.relations, self.conserved, self.chases = {}, {}, {}, {}
        self.predictions, self.events = [], []
        self.attempted, self.experiment_origins = set(), {}
        self.teacher_shown = self.conservation_shown = False
        self.phase_weight = 1.
        self.serial = 0
        self.metrics = {k: dict(seconds=0., experiments=0, audit_inputs=0, audit_throws=0, found=[]) for k in CRUTCHES}

    def demonstrate(self, mind, view, *, phase, origin):
        if origin != 'taught' or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No teaching on rediscovery or assessment worlds')
        self.methods.bind(mind.engine._u_reads([view])[0][0].detach().cpu().numpy())
        moment = dict(doubt=1., misfit=0., proven=len(mind.field.concepts))
        shown = []
        for name in CRUTCHES:
            if not self.switches[name]:
                continue
            # Noether is demonstrated exactly once during the lesson phase.
            if name == 'conserved_quantities':
                if phase != 'lesson' or self.conservation_shown or not self.demonstration_quantity(view, mind.field.concept_table()):
                    continue
            if self.methods.demonstrate(name, moment, phase=phase, origin=origin):
                shown.append(name)
                if name == 'conserved_quantities':
                    self.conservation_shown = True
        self.teacher_shown = True
        x = PH.InnerJudge.features(self.methods.bound)
        if self.switches['one_change_experiments']:
            self.teach_choice(mind.discovery.policy, 'one-change', x, phase)
        if self.switches['anomaly_pursuit']:
            self.teach_choice(self.persistence, 'keep', x, phase)
        return tuple(shown)

    @staticmethod
    def teach_choice(policy, name, x, phase):
        old_a, old_b = policy.taught.get(name, (np.zeros((65, 65)), np.zeros(65)))
        old_a, old_b = old_a.copy(), old_b.copy()
        policy.demonstrate(name, x, phase)
        a, b = policy.taught[name]
        weight = PHASE_WEIGHTS[phase]
        a[...] = old_a+weight*(a-old_a)
        b[...] = old_b+weight*(b-old_b)

    @staticmethod
    def demonstration_quantity(view, concepts):
        """The teacher runs the same search on raw taught motion, not a law."""
        trajectories = {}
        for row in view.measurements:
            if row[0] == 'motion':
                _, k, throw, t, x, v = row
                trajectories.setdefault(throw, []).append(dict(x=x, v=v, t=t, q=1.))
        trajectories = tuple(tuple(rows) for _, rows in sorted(trajectories.items()))
        if len(trajectories) < 2:
            return False
        probes = [env for trajectory in trajectories for env in trajectory]
        saved = LG.DEADLINE[0]
        LG.DEADLINE[0] = min(saved, time.time()+.5)
        try:
            found = LG.search(dict(x='real', v='real', t='real', q='real'), 'real', probes,
                              5, concepts, work=256)
        finally:
            LG.DEADLINE[0] = saved
        return any(conserved_fit(p, trajectories, concepts, (.001, .001)) for p, _ in found)

    def phase(self, name, discovery=None):
        weight = PHASE_WEIGHTS[name]
        ratio = weight/self.phase_weight if self.phase_weight else 0.
        for a, b in self.methods.taught.values():
            a *= ratio
            b *= ratio
        for a, b in self.persistence.taught.values():
            a *= ratio
            b *= ratio
        if discovery is not None and 'one-change' in discovery.policy.taught:
            a, b = discovery.policy.taught['one-change']
            a *= ratio
            b *= ratio
        self.phase_weight = weight

    def learning_state(self):
        # Cost annotations, timestamps and diagnostic copies are not learning.
        def clean(v):
            if isinstance(v, dict):
                return {k: clean(a) for k, a in v.items()
                        if k not in ('seconds', 'recorded_at', 'performed_at')}
            if isinstance(v, list):
                return [clean(a) for a in v]
            return v
        return {k: clean(v) for k, v in self.__dict__.items() if k not in ('events', 'metrics')}

    def choose_experiment(self, discovery, menu, wid, x, rng, concepts=None):
        if not self.switches['one_change_experiments']:
            return discovery.choose_experiment(menu, x, rng)
        extras = one_change_actions(discovery.worlds[wid], discovery.observations[wid], menu)
        if discovery.worlds[wid].form == 'exact' and concepts is not None:
            rivals = discovery.rivals[wid]
            for row in extras:
                ys = [LG.safe(p, {'x': row['action'][1]}, concepts) for p in rivals]
                row.update(info=split_score(ys, tuple(LG.bits(p, concepts) for p in rivals)),
                           predicted=ys[0] if ys else None, surprise=discovery.surprises[wid])
        choices = ['split', 'surprise', 'random'] if discovery.switches['designed_experiments'] else ['random']
        if extras and self.switches['one_change_experiments']:
            choices.append('one-change')
        route = discovery.policy.pick(choices, x, rng)
        if route == 'one-change':
            return min(extras, key=lambda r: (-r['info'], repr(r['action']))), route
        if not menu:
            return None, route
        if route == 'random':
            return menu[int(rng.integers(len(menu)))], route
        return min(menu, key=lambda r: (-r['info' if route == 'split' else 'surprise'], repr(r['action']))), route

    def gap(self, mind, discovery, *, deadline=math.inf):
        if not self.switches['gap_predictions']:
            return 0
        concepts = mind.field.concept_table()
        groups = {}
        for key, law in sorted(discovery.laws.items()):
            if law['form'] != 'exact' or not law['coverage']:
                continue
            p = expand(law['hypothesis'], concepts)
            for path, param in literal_sites(p):
                structure = replace_at(p, path, LG.node('var', payload='parameter'))
                token = digest((law['signature'], structure, path))
                groups.setdefault(token, []).append((param, key, p, path, law['signature']))
        made = 0
        for token, members in sorted(groups.items()):
            if time.time() >= deadline:
                break
            started = time.perf_counter()
            by_param = {r[0]: r for r in members}
            values = sorted(by_param)
            if len(values) < 3:
                continue
            differences = [b-a for a, b in zip(values, values[1:])]
            step = min(differences)
            # A conservative regular lattice: one missing interior member,
            # every other interval equal. Irregular data makes no prediction.
            if step <= 0 or differences.count(2*step) != 1 or any(d not in (step, 2*step) for d in differences):
                continue
            coordinates = [(v-values[0])//step for v in values]
            missing = next(i for i in range(coordinates[-1]+1) if i not in coordinates)
            data = tuple(zip(coordinates, values))
            probes = [{'x': i} for i in coordinates+[missing]]
            saved = LG.DEADLINE[0]
            LG.DEADLINE[0] = min(deadline, time.time()+.25)
            try:
                found = LG.search({'x': 'num'}, 'num', probes, 5, concepts,
                                  constants=tuple(values), work=256)
            finally:
                LG.DEADLINE[0] = saved
            candidates = [p for p, _ in found if all(LG.safe(p, {'x': i}, concepts) == v for i, v in data)]
            if not candidates:
                continue
            shortest = min(LG.size(p) for p in candidates)
            candidates = [p for p in candidates if LG.size(p) == shortest]
            predicted = {LG.safe(p, {'x': missing}, concepts) for p in candidates}
            if len(predicted) != 1:
                continue
            parameter = next(iter(predicted))  # singleton, never order-dependent
            if type(parameter) is not int or parameter in values or abs(parameter) > LG.MAX_INT:
                continue
            _, _, body, path, signature = by_param[values[0]]
            hypothesis = replace_at(body, path, LG.node('lit', payload=parameter))
            pid = digest((token, hypothesis))
            if any(p['id'] == pid for p in self.predictions):
                continue
            pattern = min(candidates, key=repr)
            self.families[token] = dict(key=('law-family', token), members=sorted(r[1] for r in members),
                signature=signature, structure=replace_at(body, path, LG.node('var', payload='parameter')),
                parameters=values, coordinates=coordinates, pattern=pattern, standing=len(values))
            mind.field.ideas.bind(('law-family', token), ('gap-prediction', pid), 1.)
            self.predictions.append(dict(prediction_record(pid, None, ('unseen-member', missing), token, hypothesis),
                prediction_kind='member-law', family=token, signature=signature, hypothesis=hypothesis,
                parameter=parameter, coordinate=missing, pattern=pattern, serial=self.serial,
                seen_worlds=tuple(sorted(w for w, r in discovery.observations.items() if r)),
                eligibility=self.methods.features(dict(proven=len(discovery.laws))).copy(),
                seconds=time.perf_counter()-started,
                checks=[]))
            made += 1
        return made

    def predicted_laws(self, discovery, wid):
        if not self.switches['gap_predictions'] or discovery.worlds[wid].form != 'exact':
            return ()
        w = discovery.worlds[wid]
        return tuple(p['hypothesis'] for p in self.predictions if wid not in p['seen_worlds']
                     and p['signature'] == (w.tin, w.tout) and p['confirmed'] is not True)

    def meet(self, discovery, wid, action, observation):
        if not self.switches['gap_predictions'] or action[0] != 'ask':
            return
        for p in self.predictions:
            if wid in p['seen_worlds'] or p['confirmed'] is True or wid in {r['world'] for r in p['checks']}:
                continue
            if p['signature'] != (discovery.worlds[wid].tin, discovery.worlds[wid].tout):
                continue
            expected = LG.safe(p['hypothesis'], {'x': action[1]}, {})
            p['checks'].append(dict(world=wid, expected=expected, result=observation[1],
                                    matches=expected == observation[1], met_serial=self.serial))
            # A matching first observation is a prospective hit, not credit.
            # Confirmation requires a later unchanged outer audit of the law.
            p['performed_at'] = time.time()

    def conjecture(self, mind, discovery, pool, wid, *, deadline=math.inf):
        if not self.switches['number_conjectures'] or not hasattr(pool, 'audit_relation'):
            return 0
        concepts = copy.deepcopy(mind.field.concept_table())
        ids = sorted(k for k in concepts.get('_sig', {}) if k in concepts)
        for cid in ids[:32]:
            if time.time() >= deadline:
                break
            tin, tout = concepts['_sig'][cid]
            if tin not in ('num', 'list') or tout not in ('num', 'list'):
                continue
            lhs = LG.node('c', LG.node('var', payload='x'), payload=cid)
            xs = tuple(sample_input(tin, mind.random) for _ in range(8))
            ys = tuple(LG.safe(lhs, {'x': a}, concepts) for a in xs)
            if any(y is None for y in ys) or len(set(map(repr, ys))) < 2:
                continue
            # Every target is computed from an acquired concept on own inputs.
            own = tuple(zip(xs, ys))
            alternatives = [LG.node('c', LG.node('var', payload='x'), payload=k) for k in ids[:32]
                if k != cid and concepts['_sig'][k] == (tin, tout)]
            saved = LG.DEADLINE[0]
            LG.DEADLINE[0] = min(deadline, time.time()+.25)
            try:
                alternatives += [p for p, _ in LG.search({'x': tin}, tout,
                    [{'x': a} for a in xs], 5, concepts, work=256)]
            finally:
                LG.DEADLINE[0] = saved
            for rhs in sorted(set(alternatives), key=lambda p: (LG.bits(p, concepts), repr(p))):
                if rhs == lhs or LG.size(rhs) >= LG.size(expand(lhs, concepts)) and rhs[0] != 'c':
                    continue
                token = digest((lhs, rhs, sorted(concepts.items(), key=lambda r: repr(r[0]))))
                if token in self.attempted or not all(LG.safe(rhs, {'x': a}, concepts) == y for a, y in own):
                    continue
                self.attempted.add(token)
                verdict = pool.audit_relation(lhs, rhs, tin, tout, concepts, own)
                if type(verdict) is not Certification:
                    raise TypeError('Unsafe conjecture audit')
                discovery.checks += 1
                self.metrics['number_conjectures']['audit_inputs'] += dict(verdict.bound).get('audit_n', 0)
                exact = expand(lhs, concepts) == expand(rhs, concepts)
                if exact:
                    # The checked-substitution conditions used by Sleep.abstract:
                    # both executors must reproduce the expanded original.
                    exact = all(LG.evaluate(rhs, {'x': a}, concepts) == LG.evaluate(expand(lhs, concepts), {'x': a}, {})
                        and independent(rhs, {'x': a}, concepts) == independent(expand(lhs, concepts), {'x': a}, {})
                        for a in xs)
                self.relations[token] = dict(key=('concept-relation', token), lhs=lhs, rhs=rhs,
                    concept=cid, own_values=own, status='audited' if verdict.accepted else 'refuted',
                    standing=int(verdict.accepted), evidence='exact checked rewrite' if verdict.accepted and exact
                    else 'strong sampled evidence, not proof', certificate=verdict)
                if verdict.accepted:
                    mind.field.ideas.bind(('concept', cid), ('concept-relation', token), 1.)
                    add_proof(mind.field, ('concept-relation', token))
                    self.metrics['number_conjectures']['found'].append(token)
                    for _, chase in sorted(self.chases.items()):
                        source = chase['anomaly']
                        if (chase['world'] == wid and chase['status'] in ('pending', 'active')
                                and isinstance(source, tuple) and source[0] == 'concept-relation'
                                and self.relations[source[1]]['concept'] == cid):
                            self.finish_chase(chase, ('concept-relation', token), 1.)
                            discovery.pending = [r for r in discovery.pending if r['law'] != source or r['world'] != wid]
                            if not any(r['world'] == wid for r in discovery.pending):
                                mind.field.revisit_queue = [r for r in mind.field.revisit_queue if r.get('discovery_world') != wid]
                elif verdict.refuted:
                    discovery.anomaly(mind, wid, ('concept-relation', token), verdict)
                return 1. if verdict.accepted else -1.
        return 0.

    def conservation(self, mind, discovery, pool, wid, *, deadline=math.inf):
        if (not self.switches['conserved_quantities'] or discovery.worlds[wid].form != 'strengths'
                or not hasattr(pool, 'audit_conserved')):
            return 0.
        concepts = mind.field.concept_table()
        quantities = discovery.quantity_values(wid)
        trajectories = motion_probes(discovery.observations[wid], quantities)
        if len(trajectories) < 2:
            return 0.
        probes = [env for trajectory in trajectories[-4:] for env in trajectory[::max(1, len(trajectory)//12)]]
        saved = LG.DEADLINE[0]
        LG.DEADLINE[0] = min(deadline, time.time()+.5)
        try:
            found = LG.search(dict(x='real', v='real', t='real', q='real'), 'real', probes, 7,
                              concepts, work=256)
        finally:
            LG.DEADLINE[0] = saved
        for p, _ in found:
            if time.time() >= deadline:
                break
            token = digest((wid, p, quantities))
            if token in self.attempted or not conserved_fit(p, trajectories, concepts, discovery.worlds[wid].sigma):
                continue
            self.attempted.add(token)
            verdict = pool.audit_conserved(wid, p, concepts, quantities)
            if type(verdict) is not Certification:
                raise TypeError('Unsafe conservation audit')
            discovery.checks += 1
            self.metrics['conserved_quantities']['audit_throws'] += dict(verdict.bound).get('held_throws', 0)
            if not verdict.accepted:
                if verdict.refuted:
                    discovery.anomaly(mind, wid, ('conserved', token), verdict)
                return -1.
            key = digest((p, quantities))
            entry = self.conserved.setdefault(key, dict(key=('conserved', key), program=p,
                worlds=[], certificates={}, quantity_keys=[], standing=0,
                evidence='sampled trajectory constancy, not a universal proof'))
            if wid not in entry['worlds']:
                entry['worlds'].append(wid)
                entry['worlds'].sort()
                entry['standing'] += 1
                entry['certificates'][wid] = verdict
                if ('var', 'q') in LG.parts(p):
                    links = sorted(k for k in discovery.quantities if k[1] == wid)
                    entry['quantity_keys'].extend(links)
                    for quantity in links:
                        mind.field.ideas.bind(quantity, entry['key'], 1.)
                mind.field.ideas.bind(('observed-world', wid), entry['key'], 1.)
                add_proof(mind.field, entry['key'])
                if mind.crutches['sleep_library'] and 'concept_id' not in entry:
                    body = state_body(p)
                    sig = LG.infer(body, concepts)
                    if sig is not None and LG.fits(sig, 'list(real)', 'real'):
                        concept = mind.field.invent(body, ('list(real)', 'real'), 'physics', wid,
                            LG.parts(body), extra=dict(origin='explore', quantity_key=entry['key'],
                            audit_scope='sampled conservation, not a universal proof',
                            proof=dict(record=verdict.record, bound=verdict.bound)))
                        entry['concept_id'] = concept['id']
                        mind.proposer.changed()
                # A packed state concept never registers as a univariate force
                # shape: its scope is the independently audited trajectories.
                principle = dict(key=('principle', key), quantity=entry['key'],
                    laws=[], worlds=list(entry['worlds']), standing=entry['standing'],
                    credit=0., status='fallible-conservation')
                if hasattr(discovery, 'einstein'):
                    # Separate typed space; U10 inverse-transform ranking expects
                    # a different shape and must not consume these as transforms.
                    if not hasattr(discovery.einstein, 'conservation_principles'):
                        discovery.einstein.conservation_principles = {}
                    discovery.einstein.conservation_principles[key] = principle
                mind.field.ideas.bind(entry['key'], principle['key'], 1.)
                self.metrics['conserved_quantities']['found'].append(key)
            return 1.
        return 0.

    def anomaly(self, discovery, wid, law, verdict):
        if not self.switches['anomaly_pursuit'] or not verdict.refuted:
            return None
        token = digest((wid, law))
        if token not in self.chases:
            self.chases[token] = dict(id=token, world=wid, anomaly=law, source=verdict.record,
                status='pending', started=self.serial, ended=None, attempts=[], seconds=0.,
                eligibility=[], explained_by=None, gains=[])
        return token

    def pursue(self, mind, discovery):
        if not self.switches['anomaly_pursuit']:
            return None
        open_chases = [(k, c) for k, c in sorted(self.chases.items()) if c['status'] in ('pending', 'active')]
        if not open_chases:
            return None
        x = discovery.features(mind, discovery.view(discovery.active or open_chases[0][1]['world']))
        route = self.persistence.pick(('keep', 'release'), x, mind.numpy)
        key = self.persistence.pick([k for k, _ in open_chases], x, mind.numpy)
        choice = route
        chase = self.chases[key]
        if route == 'release':
            chase.update(status='released', ended=self.serial)
            self.persistence.learn(choice, x, 0., 1.)
            return None
        chase['status'] = 'active'
        chase['eligibility'].append((choice, x.copy()))
        # Bounded features, full observable attempt history kept for reporting.
        del chase['eligibility'][:-32]
        discovery.active = chase['world']
        return key

    def admitted(self, mind, discovery, wid, key, fresh, seconds=1.):
        if fresh and self.switches['one_change_experiments']:
            discovery.laws[key].setdefault('experiment_options', {})[wid] = tuple(
                self.experiment_origins.get(wid, ()))
            previous = self.experiment_origins.get(wid, ())
            discovery.laws[key].setdefault('certification_option', {})[wid] = previous[-1][1] if previous else None
            if previous:
                discovery.policy.learn(previous[-1][1], discovery.laws[key]['features'], 1., seconds)
                if previous[-1][1] == 'one-change':
                    self.metrics['one_change_experiments']['found'].append(key)
        if self.switches['gap_predictions']:
            for p in self.predictions:
                if (wid not in p['seen_worlds'] and discovery.laws[key]['form'] == 'exact'
                        and p['confirmed'] is not True
                        and discovery.laws[key]['hypothesis'] == p['hypothesis']
                        and any(r['world'] == wid and r['matches'] for r in p['checks'])):
                    p.update(world=wid, result=key, confirmed=True, performed_at=time.time())
                    x = p['eligibility']
                    a, b = self.methods.stats.setdefault(('scientists', ('gap_predictions',)),
                        [np.zeros((self.methods.d, self.methods.d)), np.zeros(self.methods.d)])
                    a += np.outer(x, x)/self.methods.noise**2
                    b += x*min(20., 1./max(p['seconds'], 1e-6))/self.methods.noise**2
                    if p['id'] not in self.metrics['gap_predictions']['found']:
                        self.metrics['gap_predictions']['found'].append(p['id'])
        if not fresh or not self.switches['anomaly_pursuit']:
            return
        credit = max(0., compression_credit(discovery.laws[key]['bits'], discovery.laws[key]['coverage']))
        for token, chase in sorted(self.chases.items()):
            if chase['status'] == 'explained' and chase['explained_by'] == key:
                delta = max(0., credit-chase.get('compression_credit', 0.))
                if delta:
                    for choice, x in chase['eligibility']:
                        self.persistence.learn(choice, x, delta, max(chase['seconds'], 1e-6))
                    chase['gains'].append(delta)
                chase['compression_credit'] = credit
                chase.setdefault('also_explained', []).append(wid)
                continue
            if chase['world'] != wid or chase['status'] not in ('pending', 'active'):
                continue
            if chase['anomaly'] not in discovery.laws:
                continue  # a world law cannot explain a refuted concept relation
            self.finish_chase(chase, key, 1.+credit)
            chase['compression_credit'] = credit

    def finish_chase(self, chase, explanation, gain):
        chase.update(status='explained', ended=self.serial, explained_by=explanation)
        for choice, x in chase['eligibility']:
            self.persistence.learn(choice, x, gain, max(chase['seconds'], 1e-6))
        chase['gains'].append(gain)
        self.metrics['anomaly_pursuit']['found'].append(chase['id'])

    def run(self, mind, discovery, pool, wid, *, deadline):
        self.serial += 1
        self.methods.bind(mind.engine._u_reads([discovery.search_view(wid)])[0][0].detach().cpu().numpy())
        moment = dict(doubt=discovery.rival_entropy(mind, wid), misfit=discovery.surprises[wid], proven=len(discovery.laws))
        chosen = self.methods.choose('scientists', {'observe'} | {k for k in CRUTCHES if self.switches[k]}, moment, mind.numpy)
        results, chase = [], None
        for name in sorted({m[0] for m in chosen}):
            if time.time() >= deadline:
                break
            start, gain = time.perf_counter(), 0.
            if name == 'gap_predictions':
                self.gap(mind, discovery, deadline=deadline)
            elif name == 'number_conjectures':
                gain = self.conjecture(mind, discovery, pool, wid, deadline=deadline)
            elif name == 'conserved_quantities':
                gain = self.conservation(mind, discovery, pool, wid, deadline=deadline)
            elif name == 'anomaly_pursuit':
                chase = self.pursue(mind, discovery)
            seconds = time.perf_counter()-start
            if name in self.metrics:
                self.metrics[name]['seconds'] += seconds
            results.append(dict(method=name, gain=gain, seconds=seconds))
        return chosen, moment, results, chase

    def feedback(self, discovery, chosen, moment, results, row, chase):
        if row.get('experiment') is not None:
            for name in sorted({m[0] for m in chosen} & {'gap_predictions', 'number_conjectures', 'conserved_quantities'}):
                self.metrics[name]['experiments'] += 1
        for method in chosen:
            name = method[0]
            gain = next((r['gain'] for r in results if r['method'] == name), 0.)
            if name in ('one_change_experiments', 'gap_predictions', 'anomaly_pursuit'):
                gain += float(row.get('discovered', False))+row.get('progress', 0.)
            self.methods.learn('scientists', method, moment, float(np.clip(gain/max(row['seconds'], 1e-6), -20., 20.)))
        self.methods.end_task()
        if self.switches['one_change_experiments'] and row.get('experiment') is not None:
            route = row.get('experiment_option', 'random')
            self.experiment_origins.setdefault(row['world'], []).append((self.serial, route))
            if route == 'one-change':
                self.metrics['one_change_experiments']['experiments'] += 1
                self.metrics['one_change_experiments']['seconds'] += row['seconds']
        if chase is not None:
            c = self.chases[chase]
            c['seconds'] += row['seconds']
            c['attempts'].append(dict(item=self.serial, world=row['world'], experiment=row.get('experiment'),
                certified=row.get('certified'), methods=[r['method'] for r in results], law=row.get('law')))
            self.metrics['anomaly_pursuit']['seconds'] += row['seconds']
            self.metrics['anomaly_pursuit']['experiments'] += int(row.get('experiment') is not None)
            # Waiting costs time. Delayed certification supplies positive return;
            # unresolved work supplies negative return, so persistence learns both.
            if c['status'] == 'active' and c['eligibility']:
                name, x = c['eligibility'][-1]
                self.persistence.learn(name, x, -.01, max(row['seconds'], 1e-6))
                c['gains'].append(-.01)

    def report(self):
        return dict(habits=copy.deepcopy(self.metrics), predictions=len(self.predictions),
            predictions_confirmed=sum(p['confirmed'] is True for p in self.predictions),
            predictions_rejected=sum(sum(not c['matches'] for c in p['checks']) for p in self.predictions),
            conjectures_audited=len(self.relations), conjectures_refuted=sum(r['status'] == 'refuted' for r in self.relations.values()),
            conserved_quantities=len(self.conserved), chases_started=len(self.chases),
            chase_endings={s: sum(c['status'] == s for c in self.chases.values())
                           for s in ('pending', 'active', 'released', 'explained')})

    def records(self):
        def public(v):
            if is_dataclass(v):
                return public(asdict(v))
            if isinstance(v, dict):
                return {str(k): public(a) for k, a in v.items() if k != 'eligibility'}
            if isinstance(v, (tuple, list)):
                return [public(a) for a in v]
            if isinstance(v, np.ndarray):
                return v.tolist()
            return v
        return public(dict(families=self.families, predictions=self.predictions,
            relations=self.relations, conserved=self.conserved, chases=self.chases,
            experiment_origins=self.experiment_origins))

    def records_delta(self, previous):
        current = self.records()
        result = {}
        for group in ('families', 'relations', 'conserved', 'chases', 'experiment_origins'):
            result[group] = {}
            for key, value in current[group].items():
                old = previous[group].get(key)
                if value == old:
                    continue
                if group == 'chases' and old is not None:
                    value = {**value, 'attempts': value['attempts'][len(old['attempts']):],
                             'gains': value['gains'][len(old['gains']):]}
                if group == 'experiment_origins' and old is not None:
                    value = value[len(old):]
                result[group][key] = value
        old_predictions = {p['id']: p for p in previous['predictions']}
        result['predictions'] = {p['id']: p for p in current['predictions'] if p != old_predictions.get(p['id'])}
        return result
