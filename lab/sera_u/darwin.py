"""U12: acquired-world imagination in the existing Field, never a judge."""
import copy
import math
import time

import numpy as np

from sera import lang as LG, phi as PH
from .discovery import Readout, compression_credit
from .einstein import EinsteinMethods, PHASE_WEIGHTS, nodes, prediction_record
from .ports import digest, observed
from .scientists import literal_sites, replace_at
from .sleep import Syndrome, expand, substitute

CRUTCHES = ('world_hologram', 'patient_observation', 'lineage_trees',
            'change_mechanisms', 'deep_time')
LIMIT = 64


def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()
                if key not in ('seconds', 'recorded_at', 'performed_at')}
    if isinstance(value, (tuple, list)):
        return type(value)(clean(item) for item in value)
    return value


def distance(left, right):
    if left == right:
        return 0
    if not isinstance(left, tuple) or not isinstance(right, tuple):
        return 1
    return abs(len(left)-len(right))+sum(distance(before, after)
                                        for before, after in zip(left, right))


def distribution(values):
    counts = {}
    for value in values:
        key = digest(value)
        counts[key] = counts.get(key, 0)+1
    total = max(1, len(values))
    return tuple((key, count/total) for key, count in sorted(counts.items()))


def distribution_loss(left, right):
    before, after = dict(left), dict(right)
    return .5*sum(abs(before.get(key, 0.)-after.get(key, 0.))
                  for key in sorted(set(before) | set(after)))


def tree_code(programs, concepts):
    """Lossless one-subtree dictionary; charge its definition and references."""
    counts = {}
    for program in programs:
        for part in nodes(program):
            counts[part] = counts.get(part, 0)+1
    baseline = sum(LG.bits(program, concepts) for program in programs)
    best, dictionary = baseline, ()
    for part in sorted(counts, key=repr):
        if counts[part] < 2 or LG.size(part) < 2:
            continue
        reference = 1.+math.ceil(math.log2(max(2, len(programs))))
        def coded(program):
            if program == part:
                return reference
            return LG.bits(program, concepts)-sum(LG.bits(child, concepts)
                for child in program[2:])+sum(coded(child) for child in program[2:])
        cost = LG.bits(part, concepts)+reference+sum(coded(program) for program in programs)
        cost += (len(programs)-1)*2*math.ceil(math.log2(max(2, len(programs))))
        if cost < best:
            best, dictionary = cost, (part,)
    return float(baseline), float(best), dictionary


class DarwinMethods(EinsteinMethods):
    def demonstrate(self, shown, moment, *, phase, origin):
        if origin != 'taught' or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No demonstrations on rediscovery or assessment worlds')
        if not self.switches.get(shown, False):
            return False
        feature = self.features(moment)
        precision, target = self.taught.setdefault(('darwin', (shown,)),
            [np.zeros((self.d, self.d)), np.zeros(self.d)])
        weight = PHASE_WEIGHTS[phase]
        precision += weight*np.outer(feature, feature)/self.noise**2
        target += weight*feature/self.noise**2
        return True

    def candidates(self):
        return [('observe',)] + [(key,) for key in CRUTCHES if self.switches[key]]


class Darwin:
    def __init__(self, switches):
        if set(switches) != set(CRUTCHES) or any(type(value) is not bool for value in switches.values()):
            raise ValueError('Declare all five boolean U12 switches')
        self.switches = dict(switches)
        self.methods = DarwinMethods(switches)
        self.watch, self.time_choice = Readout(), Readout()
        self.phase_weight, self.teacher_shown = 1., False
        self.costs = dict(real=0., imagined=0.)

    def attach(self, field):
        if not hasattr(field, 'hologram'):
            field.hologram = dict(regions={}, arrivals={}, notebook=[], trees={},
                mechanisms={}, predictions=[], dreams=[], serial=0, generation=0)
        field.darwin_methods = self.methods

    def superpose(self, field, thing, key, amount):
        if self.switches['world_hologram'] and isinstance(field.ideas, PH.Ideas):
            PH.Ideas.bind(field.ideas, thing, key, amount)
        else:
            field.ideas.bind(thing, key, amount)

    def learning_state(self):
        return {key: clean(value) for key, value in self.__dict__.items() if key != 'costs'}

    def demonstrate(self, mind, view, *, phase, origin):
        if origin != 'taught' or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No U12 teaching on rediscovery or assessment worlds')
        self.methods.bind(mind.engine._u_reads([view])[0][0].detach().cpu().numpy())
        moment = dict(doubt=1., misfit=0., proven=len(mind.field.concepts))
        shown = tuple(key for key in CRUTCHES
                      if self.methods.demonstrate(key, moment, phase=phase, origin=origin))
        self.teacher_shown = True
        return shown

    def phase(self, name):
        weight = PHASE_WEIGHTS[name]
        ratio = weight/self.phase_weight if self.phase_weight else 0.
        for policy in (self.methods, self.watch, self.time_choice):
            for precision, target in policy.taught.values():
                precision *= ratio
                target *= ratio
        self.phase_weight = weight

    @staticmethod
    def region(discovery, wid):
        world = discovery.worlds[wid]
        return (world.form, world.tin, world.tout, world.objects)

    def material(self, discovery, region):
        if region[0] == 'strengths':
            specimens = []
            for wid, rows in sorted(discovery.observations.items()):
                rows = [row for row in rows if row[0] == 0]
                if self.region(discovery, wid) != region or len(rows) < 2:
                    continue
                matrix = np.array([[1., sum((end-start)*force for start, end, force in row[1])]
                                   for row in rows[-LIMIT:]], float)
                if np.linalg.matrix_rank(matrix) < 2:
                    continue
                values = np.array([row[2]+row[3] for row in rows[-LIMIT:]], float)
                parameters = np.linalg.lstsq(matrix, values, rcond=None)[0]
                if np.isfinite(parameters).all():
                    specimens.append(dict(world=wid, parameters=tuple(map(tuple, parameters.tolist())),
                        fitted=True, certified=False, sigma=discovery.worlds[wid].sigma,
                        actions=tuple(('push', row[0], row[1]) for row in rows[-4:])))
            return specimens[-LIMIT:]
        return [dict(world=wid, law=key, program=entry['hypothesis'])
                for key, entry in sorted(discovery.laws.items())
                for wid in sorted(entry['coverage'])
                if entry['form'] == region[0] and entry['signature'] == region[1:3]
                and self.region(discovery, wid) == region][-LIMIT:]

    def picture(self, mind, discovery, region):
        state = mind.field.hologram['regions'].setdefault(region, dict(seen={}, trials=0,
            correct=0, loss=0., baseline_loss=0., brier=0., bins={}))
        state['material'] = self.material(discovery, region)
        state['quantities'] = {key: copy.deepcopy(value) for key, value in discovery.quantities.items()
                               if self.region(discovery, key[1]) == region}
        state['anomalies'] = [copy.deepcopy(row) for row in discovery.pending
                              if self.region(discovery, row['world']) == region]
        state['concepts'] = tuple(sorted(mind.field.concept_table().get('_sig', {}), key=repr))
        self.superpose(mind.field, ('hologram-region', region), ('hologram-material', digest(repr(clean(state)))), 1.)
        return state

    def forecast(self, mind, discovery, wid, action):
        if not self.switches['world_hologram']:
            return None
        region = self.region(discovery, wid)
        state = self.picture(mind, discovery, region)
        answers = []
        for specimen in state['material']:
            if region[0] == 'exact':
                answer = LG.safe(specimen['program'], {'x': action[1]}, mind.field.concept_table())
                if answer is not None:
                    answers.append(observed(answer))
            else:
                drive = sum((end-start)*force for start, end, force in action[2])
                coefficients = np.array(specimen['parameters'])
                if action[1] == 0:
                    values = coefficients[0]+drive*coefficients[1]
                    if np.isfinite(values).all():
                        answers.append(tuple(map(float, values)))
        baseline = [row[1] if region[0] == 'exact' else row[2]+row[3]
                    for rows in state['seen'].values() for row in rows if
                    (row[0] == action[1] if region[0] == 'exact' else row[:2] == action[1:])]
        answers = answers or baseline
        if not answers:
            return None
        support = distribution(answers)
        chosen = min(support, key=lambda row: (-row[1], row[0]))[0]
        strength = len(state['seen'])/(len(state['seen'])+2.)
        calibrated = (state['correct']+1.)/(state['trials']+2.)
        return dict(region=region, predicted=next(value for value in answers if digest(value) == chosen),
            probability=min(strength, calibrated)*dict(support)[chosen], fresh=wid not in state['seen'],
            baseline=(next(value for value in baseline if digest(value) ==
                min(distribution(baseline), key=lambda row: (-row[1], row[0]))[0]) if baseline else None),
            issued=mind.field.hologram['serial'])

    def not_yet(self, mind, discovery, wid, source):
        item = dict(world=wid, law=source, status='not-yet', scope='own-question', origin='explore')
        if item not in discovery.pending:
            discovery.pending.append(item)
        if mind.crutches.get('taught_not_yet'):
            view = discovery.view(wid)
            if not any(row.get('discovery_world') == wid for row in mind.field.revisit_queue):
                mind.field.revisit_queue.append(dict(identity=view.identity, view=view, phase='world',
                    attempts=1, first_at=mind.field.tasks, last_at=mind.field.tasks,
                    current_identity=view.identity, current_view=view, status='not-yet',
                    origin='explore', discovery_world=wid))
        if mind.crutches.get('gap_syndromes'):
            mind.field.curiosity.observe('hologram-misfit', 1.)
            view = discovery.view(wid)
            syndrome = Syndrome('surprise', 1., (('hologram-region', self.region(discovery, wid)),), 0.)
            reads = mind.engine._u_reads([view])[0][0].detach().cpu().numpy()
            mind.field.curiosity.decode(view, (syndrome,), reads)
        if discovery.switches['own_questions']:
            discovery.own_question(wid, 'anomaly')

    def receive(self, mind, discovery, wid, action, observation, forecast=None):
        atlas = mind.field.hologram
        atlas['serial'] += 1
        atlas['arrivals'].setdefault(wid, atlas['serial'])
        region = self.region(discovery, wid)
        gain = 0.
        if self.switches['world_hologram']:
            state = self.picture(mind, discovery, region)
            if forecast is not None:
                if forecast['issued'] >= atlas['serial']:
                    raise ValueError('Retrospective hologram forecast')
                actual = observation[1] if region[0] == 'exact' else observation[2]+observation[3]
                right = actual == forecast['predicted']
                if region[0] == 'strengths':
                    residual = np.array(actual)-np.array(forecast['predicted'])
                    sensor = min(discovery.worlds[wid].sigma)
                    right = bool(np.sqrt(np.mean((residual/sensor)**2)) <= 3.)
                baseline_right = actual == forecast['baseline']
                if region[0] == 'strengths' and forecast['baseline'] is not None:
                    residual = np.array(actual)-np.array(forecast['baseline'])
                    baseline_right = bool(np.sqrt(np.mean((residual/sensor)**2)) <= 3.)
                state['trials'] += 1
                if forecast['fresh']:
                    state['fresh_trials'] = state.get('fresh_trials', 0)+1
                    state['fresh_loss'] = state.get('fresh_loss', 0.)+float(not right)
                    state['fresh_baseline_loss'] = state.get('fresh_baseline_loss', 0.)+float(not baseline_right)
                state['correct'] += int(right)
                state['loss'] += float(not right)
                state['baseline_loss'] += float(not baseline_right)
                probability = forecast['probability']
                state['brier'] += (probability-float(right))**2
                bucket = min(9, int(probability*10))
                count, total, hits = state['bins'].get(bucket, (0, 0., 0))
                state['bins'][bucket] = (count+1, total+probability, hits+int(right))
                gain = float(right)
                if not right:
                    self.not_yet(mind, discovery, wid, 'hologram:'+digest(region))
            state['seen'].setdefault(wid, []).append(observed(observation))
            del state['seen'][wid][:-LIMIT]
            self.superpose(mind.field, ('observed-world', wid), ('hologram-region', region), 1.)
        if self.switches['patient_observation']:
            atlas['notebook'].append(dict(world=wid, region=region, observation=observed(observation),
                generation=atlas['generation'], arrived=atlas['serial'], eligibility=[], settled=[]))
            self.superpose(mind.field, ('notebook', atlas['serial']), ('observed-world', wid), 1.)
        return gain

    def tree(self, mind, discovery, region):
        if not self.switches['lineage_trees']:
            return None
        specimens = self.material(discovery, region)
        if len(specimens) < 3:
            return None
        if region[0] == 'strengths':
            scale = min(specimens[0]['sigma'])
            vectors = [tuple(int(round(max(-1e12, min(1e12, value/scale)))) for row in specimen['parameters'] for value in row)
                       for specimen in specimens]
            root = vectors[0]
            def bits(vector):
                return sum(2+2*max(1, abs(value).bit_length()) for value in vector)
            baseline = float(sum(bits(vector) for vector in vectors))
            reached, edges, deltas = {0}, [], []
            code = float(bits(root))
            while len(reached) < len(vectors):
                cost, parent, child, delta = min((bits(tuple(after-before for before, after in zip(vectors[parent], vectors[child]))),
                    parent, child, tuple(after-before for before, after in zip(vectors[parent], vectors[child])))
                    for parent in sorted(reached) for child in range(len(vectors)) if child not in reached)
                edges.append((specimens[parent]['world'], specimens[child]['world'], cost))
                deltas.append((parent, child, delta))
                code += cost+2*math.ceil(math.log2(len(vectors)))
                reached.add(child)
            key = digest((region, vectors))
            credit = max(0., compression_credit(code, {'population': (baseline, 0.)}))
            entry = dict(id=key, region=region, root=root, scale=scale, coordinate_cap=1e12, deltas=deltas, edges=edges,
                         baseline_bits=baseline, code_bits=code, compression_credit=credit,
                         claim='lossless quantized fitted-parameter tree; descent hypothesis, not history')
            previous = mind.field.hologram['trees'].get(key)
            entry['earned'] = previous.get('earned', False) if previous is not None else False
            mind.field.hologram['trees'][key] = entry
            self.superpose(mind.field, ('lineage-tree', key), ('hologram-region', region), credit)
            # Compression credit is a search prior, never standing (U9's rule; no MemoryField has a standing table).
            return entry
        programs = [row['program'] for row in specimens]
        baseline, code, dictionary = tree_code(programs, mind.field.concept_table())
        edges, reached = [], {0}
        while len(reached) < len(programs):
            cost, parent, child = min((distance(programs[parent], programs[child]), parent, child)
                for parent in sorted(reached) for child in range(len(programs)) if child not in reached)
            edges.append((specimens[parent]['world'], specimens[child]['world'], cost))
            reached.add(child)
        credit = max(0., compression_credit(code, {'population': (baseline, 0.)}))
        key = digest((region, tuple(programs)))
        def encoded(program):
            if dictionary and program == dictionary[0]:
                return ('shared-subtree', 0)
            return program[:2]+tuple(encoded(child) for child in program[2:])
        entry = dict(id=key, region=region, edges=edges, dictionary=dictionary,
            residual_programs=tuple(encoded(program) for program in programs),
            baseline_bits=baseline, code_bits=code, compression_credit=credit,
            claim='compressing likeness tree; descent hypothesis, not true history')
        previous = mind.field.hologram['trees'].get(key)
        if previous is not None:
            entry['earned'] = previous.get('earned', False)
        mind.field.hologram['trees'][key] = entry
        self.superpose(mind.field, ('lineage-tree', key), ('hologram-region', region), credit)
        # Compression credit is a search prior, never standing (U9's rule; no MemoryField has a standing table).
        return entry

    def variations(self, specimens, region, concepts, *, deadline):
        if region[0] != 'exact':
            return (), ()
        programs = tuple(dict.fromkeys(row['program'] for row in specimens))
        edits = set()
        for left in programs[:16]:
            left_sites = dict(literal_sites(left))
            for right in programs[:16]:
                if distance(left, right) != 1:
                    continue
                for path, value in literal_sites(right):
                    if path in left_sites and value != left_sites[path]:
                        edits.add((path, value-left_sites[path]))
        variants = set()
        for program in programs:
            for path, delta in sorted(edits):
                if time.time() >= deadline:
                    return tuple(sorted(variants, key=repr))[:LIMIT], tuple(sorted(edits))
                sites = dict(literal_sites(program))
                if path not in sites or abs(sites[path]+delta) > LG.MAX_INT:
                    continue
                candidate = replace_at(program, path, LG.node('lit', payload=sites[path]+delta))
                signature = LG.infer(candidate, concepts, arg='x')
                if signature is not None and LG.fits(signature, region[1], region[2]):
                    variants.add(candidate)
        for left in programs[:8]:
            for right in programs[:8]:
                if region[1] == region[2]:
                    variants.add(substitute(right, 'x', left))
        return tuple(sorted((program for program in variants if LG.size(program) <= 40), key=repr))[:LIMIT], tuple(sorted(edits))

    @staticmethod
    def signature(program, probes, concepts):
        values = tuple(LG.safe(program, {'x': probe}, concepts) for probe in probes)
        return None if any(value is None for value in values) else observed(values)

    def sorting_predicates(self, programs, path, concepts):
        parameters = sorted({dict(literal_sites(program))[path] for program in programs
                             if path in dict(literal_sites(program))})
        predicates = []
        argument = LG.node('var', payload='x')
        for key, signature in sorted(concepts.get('_sig', {}).items(), key=lambda row: repr(row[0])):
            if key not in concepts:
                continue
            call = LG.node('c', argument, payload=key)
            if LG.fits(tuple(signature), 'num', 'bool'):
                predicates.append(call)
            elif LG.fits(tuple(signature), 'num', 'num'):
                values = sorted({LG.safe(call, {'x': parameter}, concepts) for parameter in parameters}
                                - {None})
                if len(values) < 2:
                    continue
                gaps = [right-left for left, right in zip(values, values[1:]) if right > left]
                gap = min(gaps)
                low, high = LG.node('lit', payload=values[0]-gap), LG.node('lit', payload=values[-1]+gap)
                lower = LG.node('if', LG.node('lt', low, call), LG.node('one'), LG.node('zero'))
                upper = LG.node('if', LG.node('lt', call, high), LG.node('one'), LG.node('zero'))
                predicates.append(LG.node('eq', LG.node('mul', lower, upper), LG.node('one')))
        return tuple(sorted(set(predicates), key=repr))[:8]

    def imagine_parameters(self, mind, discovery, region, specimens, generations, deadline):
        if not self.switches['change_mechanisms'] or len(specimens) < 4:
            return None
        vectors = [np.array(specimen['parameters']).ravel() for specimen in specimens]
        matrix = np.stack(vectors)
        index = int(np.argmax(np.var(matrix, axis=0)))
        sigma = min(specimens[0]['sigma'])
        coordinates = [int(round(max(-1e12, min(1e12, vector[index]/sigma)))) for vector in vectors]
        programs = [LG.node('lit', payload=value) for value in coordinates]
        predicates = self.sorting_predicates(programs, (), mind.field.concept_table())
        gaps = sorted(abs(after-before) for before in coordinates for after in coordinates if after != before)
        if not predicates or not gaps:
            return None
        resolution = max(1, min(gaps))
        steps = []
        for child, vector in enumerate(vectors[:16]):
            neighbors = [(float(np.linalg.norm(vector-parent)), parent_index)
                         for parent_index, parent in enumerate(vectors[:16]) if parent_index != child]
            _, parent = min(neighbors)
            change = vector-vectors[parent]
            if np.isfinite(change).all() and np.any(change):
                steps.append(change)
        if not steps:
            return None
        def coordinate(vector):
            return int(round(max(-1e12, min(1e12, vector[index]/sigma))))
        def binned(vector):
            return (int(round(coordinate(vector)/resolution)),)
        target = distribution([binned(vector) for vector in vectors])
        unsorted = {binned(vector+change) for vector in vectors[:8] for change in steps[:8]
                    if np.isfinite(vector+change).all()}
        null_loss = distribution_loss(distribution(sorted(unsorted)), target)
        candidates = []
        for predicate in predicates:
            population, rejected, completed, vanished = vectors, 0, 0, []
            for _ in range(min(LIMIT, max(1, generations))):
                if time.time() >= deadline:
                    break
                survivors = {}
                for vector in population[:8]:
                    for change in steps[:8]:
                        candidate = vector+change
                        if not np.isfinite(candidate).all():
                            continue
                        answer = LG.safe(predicate, {'x': coordinate(candidate)}, mind.field.concept_table())
                        if answer is True:
                            survivors.setdefault(binned(candidate), candidate)
                        elif answer is False:
                            rejected += 1
                            if len(vanished) < LIMIT:
                                vanished.append(binned(candidate))
                if not survivors:
                    break
                population = [survivors[key] for key in sorted(survivors)][:LIMIT]
                completed += 1
            predicted = distribution([binned(vector) for vector in population])
            loss = distribution_loss(predicted, target)
            if completed and rejected and len(predicted) >= 2 and loss <= .25 and null_loss-loss >= .1:
                candidates.append(dict(region=region, predicate=expand(predicate, mind.field.concept_table()),
                    edits=tuple(tuple(map(float, change)) for change in steps),
                    probes=specimens[0]['actions'][:2], predicted=predicted, observed=target,
                    distribution_loss=loss, unsorted_loss=null_loss, sorting_path=(), parameter_rule=True,
                    parameter_index=index, sigma=sigma, resolution=resolution,
                    population=tuple(tuple(map(float, vector)) for vector in population),
                    vanishing=distribution(vanished), imagined_generations=completed,
                    rejected=rejected, status='conjecture', certified=False, audits=[]))
        if not candidates:
            return None
        best = min(candidates, key=lambda item: (item['distribution_loss'], repr(item['predicate'])))
        key = digest((region, best['predicate'], best['parameter_index'], best['resolution']))
        previous = mind.field.hologram['mechanisms'].get(key)
        if previous is not None:
            best['audits'], best['status'] = previous['audits'], previous['status']
        mind.field.hologram['mechanisms'][key] = best
        self.superpose(mind.field, ('change-mechanism', key), ('hologram-region', region), 1.)
        return key

    def imagine(self, mind, discovery, region, *, generations=1, deadline=math.inf, conjecture=True):
        if not self.switches['world_hologram']:
            return None
        specimens = self.material(discovery, region)
        if not specimens:
            return None
        if region[0] == 'strengths':
            dreams = []
            for specimen in specimens[:8]:
                for other in specimens[:8]:
                    if specimen['world'] == other['world']:
                        continue
                    parameters = 2*np.array(specimen['parameters'])-np.array(other['parameters'])
                    if not np.isfinite(parameters).all():
                        continue
                    for action in specimen['actions'][:2]:
                        drive = sum((end-start)*force for start, end, force in action[2])
                        values = parameters[0]+drive*parameters[1]
                        if not np.isfinite(values).all():
                            continue
                        prediction = tuple(map(float, values))
                        dreams.append(dict(parameters=tuple(map(tuple, parameters.tolist())),
                            specimens=((action, prediction),), imagined=True, certified=False))
                        if len(dreams) >= LIMIT:
                            break
                    if len(dreams) >= LIMIT:
                        break
                if len(dreams) >= LIMIT:
                    break
            mind.field.hologram['dreams'] = dreams
            return self.imagine_parameters(mind, discovery, region, specimens, generations, deadline) if conjecture else None
        probes = tuple(sorted({row[0] for specimen in specimens
            for row in discovery.observations[specimen['world']]}, key=repr))[:4]
        if not probes:
            return None
        concepts = mind.field.concept_table()
        variants, edits = self.variations(specimens, region, concepts, deadline=deadline)
        dreams = []
        for program in variants:
            values = self.signature(program, probes, concepts)
            if values is not None:
                dreams.append(dict(program=program, specimens=tuple(zip(probes, values)),
                                   imagined=True, certified=False))
        mind.field.hologram['dreams'] = dreams
        if not conjecture or not self.switches['change_mechanisms'] or len(specimens) < 4 or not edits:
            return None
        path = edits[0][0]
        predicates = self.sorting_predicates([row['program'] for row in specimens], path, concepts)
        values = [self.signature(row['program'], probes, concepts) for row in specimens]
        target = distribution([value for value in values if value is not None])
        unsorted = [self.signature(program, probes, concepts) for program in variants
                    if any(distance(program, row['program']) <= 1 for row in specimens)]
        null_loss = distribution_loss(distribution([value for value in unsorted if value is not None]), target)
        candidates = []
        for predicate in predicates[:8]:
            if time.time() >= deadline:
                break
            population, rejected, steps, vanished = specimens, 0, 0, []
            for _ in range(min(LIMIT, max(1, generations))):
                if time.time() >= deadline:
                    break
                proposed, _ = self.variations(population, region, concepts, deadline=deadline)
                survivors = {}
                for program in proposed:
                    if not any(distance(program, parent['program']) <= 1 for parent in population):
                        continue
                    values = self.signature(program, probes, concepts)
                    if values is None:
                        continue
                    parameter = dict(literal_sites(program)).get(path)
                    answers = [LG.safe(predicate, {'x': parameter}, concepts)] if parameter is not None else []
                    if answers and all(answer is True for answer in answers):
                        survivors.setdefault(digest(values), dict(program=program))
                    elif any(answer is False for answer in answers):
                        rejected += 1
                        if len(vanished) < LIMIT:
                            vanished.append(values)
                if not survivors:
                    break
                population, steps = [survivors[key] for key in sorted(survivors)][:LIMIT], steps+1
            produced = [self.signature(row['program'], probes, concepts) for row in population]
            predicted = distribution([value for value in produced if value is not None])
            loss = distribution_loss(predicted, target)
            if steps and rejected and loss <= .25 and len(predicted) >= 2 and null_loss-loss >= .1:
                candidates.append(dict(region=region, predicate=predicate, edits=edits, probes=probes,
                    predicted=predicted, observed=target, distribution_loss=loss, unsorted_loss=null_loss,
                    sorting_path=path, population=tuple(row['program'] for row in population),
                    vanishing=distribution(vanished),
                    imagined_generations=steps, rejected=rejected, status='conjecture',
                    certified=False, audits=[]))
        if not candidates:
            return None
        best = min(candidates, key=lambda row: (row['distribution_loss'], repr(row['predicate'])))
        best['predicate'] = expand(best['predicate'], concepts)
        key = digest((region, best['predicate'], best['edits'], probes))
        previous = mind.field.hologram['mechanisms'].get(key)
        if previous is not None:
            best['audits'] = previous['audits']
            best['status'] = previous['status']
        mind.field.hologram['mechanisms'][key] = best
        self.superpose(mind.field, ('change-mechanism', key), ('hologram-region', region), 1.)
        return key

    def predict_population(self, mind, key, feature, time_arm, seconds):
        atlas = mind.field.hologram
        mechanism = atlas['mechanisms'][key]
        if any(row['law'] == key and row['result'] is None for row in atlas['predictions']):
            return None
        prediction = prediction_record('darwin:'+str(len(atlas['predictions'])),
            'future-population', ('population', mechanism['region']), key, mechanism['predicted'])
        prediction.update(probes=mechanism['probes'], issued=atlas['serial'],
            generation=atlas['generation'], samples=[], contributors=[], time_arm=time_arm,
            feature=feature.copy(), seconds=seconds, credited=False,
            population=mechanism['population'], predicate=mechanism['predicate'],
            sorting_path=mechanism['sorting_path'], vanishing=mechanism['vanishing'],
            parameter_rule=mechanism.get('parameter_rule', False))
        if prediction['parameter_rule']:
            for name in ('parameter_index', 'sigma', 'resolution'):
                prediction[name] = mechanism[name]
        atlas['predictions'].append(prediction)
        return prediction['id']

    def settle_populations(self, mind, discovery):
        atlas = mind.field.hologram
        reward = 0.
        for prediction in atlas['predictions']:
            if prediction['result'] is not None:
                continue
            region = prediction['action'][1]
            for wid in sorted(discovery.worlds):
                if self.region(discovery, wid) != region or wid in prediction['contributors']:
                    continue
                if atlas['arrivals'].get(wid, 0) <= prediction['issued']:
                    continue
                if prediction['parameter_rule']:
                    specimen = next((item for item in self.material(discovery, region) if item['world'] == wid), None)
                    if specimen is None:
                        continue
                    vector = np.array(specimen['parameters']).ravel()
                    coordinate = int(round(max(-1e12, min(1e12, vector[prediction['parameter_index']]/prediction['sigma']))))
                    sample = (int(round(coordinate/prediction['resolution'])),)
                    prediction['samples'].append(sample)
                    prediction.setdefault('sorting_checks', []).append(
                        LG.safe(prediction['predicate'], {'x': coordinate}, {}) is True)
                    prediction['contributors'].append(wid)
                    continue
                by_input = dict(discovery.observations[wid]) if region[0] == 'exact' else {}
                if not all(probe in by_input for probe in prediction['probes']):
                    continue
                prediction['samples'].append(observed(tuple(by_input[probe] for probe in prediction['probes'])))
                prediction['contributors'].append(wid)
            if len(prediction['samples']) < 4:
                continue
            prediction['result'] = distribution(prediction['samples'])
            loss = distribution_loss(prediction['predicted'], prediction['result'])
            prediction['confirmed'] = loss <= .25
            prediction['performed_at'], prediction['loss'] = time.time(), loss
            mechanism = atlas['mechanisms'][prediction['law']]
            if prediction['parameter_rule']:
                sorting_matches = sum(prediction.get('sorting_checks', ()))
            else:
                allowed = {digest(self.signature(program, prediction['probes'], mind.field.concept_table()))
                           for program in prediction['population']}
                sorting_matches = sum(digest(sample) in allowed for sample in prediction['samples'])
            prediction['confirmed'] = prediction['confirmed'] and sorting_matches == len(prediction['samples'])
            mechanism['audits'].append(dict(prediction=prediction['id'], loss=loss,
                sorting_matches=sorting_matches, sorting_tested=len(prediction['samples']),
                                           worlds=tuple(prediction['contributors'])))
            mechanism['status'] = 'supported' if prediction['confirmed'] else 'not-yet'
            reward += float(prediction['confirmed'])
            if not prediction['confirmed']:
                for wid in prediction['contributors']:
                    self.not_yet(mind, discovery, wid, prediction['law'])
        return reward

    def run(self, mind, discovery, wid, *, deadline):
        self.attach(mind.field)
        self.methods.bind(mind.engine._u_reads([discovery.search_view(wid)])[0][0].detach().cpu().numpy())
        moment = dict(doubt=discovery.rival_entropy(mind, wid),
                      misfit=discovery.surprises[wid], proven=len(discovery.laws))
        chosen = self.methods.choose('darwin', {'observe'} | {key for key in CRUTCHES if self.switches[key]}, moment, mind.numpy)
        region = self.region(discovery, wid)
        feature = PH.InnerJudge.features(self.methods.bound)
        watching = ('patient_observation',) in chosen and self.watch.pick(('keep', 'release'), feature, mind.numpy) == 'keep'
        if ('world_hologram',) in chosen:
            self.picture(mind, discovery, region)
        if ('lineage_trees',) in chosen:
            self.tree(mind, discovery, region)
        started = time.perf_counter()
        time_arm = (self.time_choice.pick(('1', '8', '64'), feature, mind.numpy)
                    if self.switches['deep_time'] and ('deep_time',) in chosen else None)   # the ledger's switch site
        if any((key,) in chosen for key in ('world_hologram', 'change_mechanisms', 'deep_time')):
            key = self.imagine(mind, discovery, region, generations=int(time_arm or '1'), deadline=deadline,
                conjecture=('change_mechanisms',) in chosen or (time_arm is not None and bool(mind.field.hologram['mechanisms'])))
            if key is not None:
                self.predict_population(mind, key, feature, time_arm, max(1e-6, time.perf_counter()-started))
            elif time_arm is not None:
                self.time_choice.learn(time_arm, feature, -.05, max(1e-6, time.perf_counter()-started))
        self.costs['imagined'] += time.perf_counter()-started
        return chosen, moment, watching, feature

    def feedback(self, mind, discovery, context, row, gain):
        chosen, moment, watching, feature = context
        atlas = mind.field.hologram
        gain += self.settle_populations(mind, discovery)
        certified = row.get('certified') is not None and row['certified']['accepted']
        if self.switches['patient_observation']:
            self.watch.learn('keep' if watching else 'release', feature,
                             float(certified or gain > 0)-.05, row['seconds'])
            for entry in atlas['notebook']:
                if entry['world'] == row['world'] and not entry['eligibility']:
                    entry['eligibility'] = [('keep' if watching else 'release', feature.copy())]
                if entry['world'] == row['world'] and certified and 'certificate' not in entry['settled']:
                    for option, eligible in entry['eligibility']:
                        self.watch.learn(option, eligible, 1., row['seconds'])
                    entry['settled'].append('certificate')
        for prediction in atlas['predictions']:
            if prediction['result'] is None or prediction['credited']:
                continue
            if prediction['time_arm'] is not None:
                self.time_choice.learn(prediction['time_arm'], prediction['feature'],
                    1. if prediction['confirmed'] else -1., prediction['seconds'])
            prediction['credited'] = True
            for entry in atlas['notebook']:
                if entry['world'] in prediction['contributors']:
                    for option, eligible in entry['eligibility']:
                        self.watch.learn(option, eligible, float(prediction['confirmed']), row['seconds'])
                    entry['settled'].append(prediction['id'])
        for method in chosen:
            credit = gain+float(certified)-.05
            if method == ('lineage_trees',):
                for entry in atlas['trees'].values():
                    if not entry.get('earned'):
                        credit += entry['compression_credit']
                        entry['earned'] = True
            self.methods.learn('darwin', method, moment, float(np.clip(credit/max(row['seconds'], 1e-6), -20., 20.)))
        self.methods.end_task()
        self.costs['real'] += row['seconds']

    def report(self, field):
        atlas = field.hologram
        regions = [dict(region=region, seen_worlds=len(state['seen']),
            **{key: value for key, value in state.items() if key in
               ('trials', 'correct', 'loss', 'baseline_loss', 'brier', 'bins', 'fresh_trials', 'fresh_loss', 'fresh_baseline_loss')})
                   for region, state in sorted(atlas['regions'].items())]
        return dict(switches=self.switches, regions=regions, notebook=len(atlas['notebook']),
            trees=copy.deepcopy(atlas['trees']), mechanisms=copy.deepcopy(atlas['mechanisms']),
            predictions=[{key: copy.deepcopy(value) for key, value in prediction.items() if key != 'feature'}
                         for prediction in atlas['predictions']], seconds=dict(self.costs),
            claim='Darwin habits on varied worlds; not Darwin insight')
