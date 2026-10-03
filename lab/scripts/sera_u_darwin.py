"""U12 observer: freeze branching laws and all specimens before learner time."""
import copy
import math
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from sera import lang as LG
from sera_u.discovery import WorldView
from sera_u.darwin import CRUTCHES
from sera_u.ports import digest, observed
from sera_u.sleep import family
from scripts.sera_u_discovery import Machine, validate
from scripts.sera_u_scientists import MotionBody, ScientistsPool, freeze_scientists

SCHEMA = 'u12-lineage-1'
CLAIM = ('A test of whether Darwin habits help SERA find the process behind varied worlds '
         "in its own picture of them, not a claim of Darwin's insight.")


def freeze_lineage(mind, suite, seed):
    manifest = freeze_scientists(mind, suite, seed)
    rng = np.random.default_rng([seed, 12012])
    excluded = {row['family'] for label in ('retention', 'wake', 'assessment') for row in suite[label]}
    excluded.update(row['family'] for row in manifest['worlds'] if row['form'] == 'exact')
    variable = LG.node('var', payload='x')
    serial = 0
    variants = []
    for typ in ('num', 'list'):
        base = (LG.node('mul', variable, variable) if typ == 'num' else
                LG.node('mul', LG.node('head', variable), LG.node('head', LG.node('tail', variable))))
        for _ in range(5):
            planted = [LG.node('add', base, LG.node('lit', payload=parameter)) for parameter in range(2, 6)]
            if not {family(program, {}) for program in planted} & excluded:
                break
            base = LG.node('add', base, LG.node('zero'))
        else:
            raise ValueError('No disjoint lineage root within bounded structure')
        parents = []
        for generation in range(4):
            next_parents = []
            for index in range(8):
                if parents:
                    parent = parents[int(rng.integers(len(parents)))]
                    before = parent['observer_parameter']
                    step = int(rng.choice((-1, 1)))
                    parameter = before+step
                    variants.append(dict(population=typ, generation=generation, parent=parent['id'],
                        parameter=parameter, persists=2 <= parameter <= 5))
                    if not 2 <= parameter <= 5:
                        parameter = before-step
                        step = -step
                        variants.append(dict(population=typ, generation=generation, parent=parent['id'],
                            parameter=parameter, persists=True))
                else:
                    parent, step, parameter = None, 0, 2+index % 4
                program = LG.node('add', base, LG.node('lit', payload=parameter))
                probes = (-3, -1, 0, 2) if typ == 'num' else ((-3, 1), (-1, 2), (0, 3), (2, 1))
                machine = Machine(program)
                samples = tuple((probe, observed(machine(probe))) for probe in probes)
                wid = digest(('lineage', seed, serial))[:20]
                serial += 1
                row = dict(id=wid, form='exact', tin=typ, tout='num', program=program,
                    family=family(program, {}), seed=seed+12000, index=120000+serial,
                    observer_birth=generation, observer_parent=parent['id'] if parent else None,
                    observer_parameter=parameter, observer_edit=step,
                    observer_sorting=('bounded-coordinate', 2, 5), observer_population=typ,
                    frozen_samples=samples)
                manifest['worlds'].append(row)
                next_parents.append(row)
            parents = next_parents
    parents = []
    for generation in range(4):
        next_parents = []
        for index in range(4):
            parent = parents[int(rng.integers(len(parents)))] if parents else None
            before = parent['observer_parameter'] if parent else .3+.02*index
            step = float(rng.choice((-.01, .01))) if parent else 0.
            parameter = before+step
            variants.append(dict(population='rail', generation=generation, parent=parent['id'] if parent else None,
                parameter=parameter, persists=.25 <= parameter <= .4))
            if not .25 <= parameter <= .4:
                parameter = before-step
                step = -step
            row = dict(id=digest(('lineage-rail', seed, serial))[:20], form='strengths',
                motion_sensor=True, has_conserved=True, seed=seed+12000, index=120000+serial,
                observer_birth=generation, observer_parent=parent['id'] if parent else None,
                observer_parameter=parameter, observer_edit=step,
                observer_sorting=('bounded-coordinate', .25, .4), observer_population='rail')
            serial += 1
            body = LineageMotion(row)
            from ccops5.core.worlds import Action
            samples = []
            for force in (-.5, .5):
                throw = body.make(0, Action(((0., .5, force),)), 0)
                samples.append((0, tuple(throw.action.segments), tuple(map(float, throw.x)), tuple(map(float, throw.v))))
            row['frozen_samples'] = tuple(samples)
            manifest['worlds'].append(row)
            next_parents.append(row)
        parents = next_parents
    manifest.update(lineage_suite=SCHEMA, lineage_variants=variants, claim=CLAIM)
    manifest['split'] += '; frozen untaught branching populations, later generations held back'
    return validate_lineage(validate(manifest, suite, mind))


def validate_lineage(manifest):
    if manifest.get('lineage_suite') != SCHEMA:
        raise ValueError('Frozen lineage schema changed')
    rows = {row['id']: row for row in manifest['worlds'] if 'observer_birth' in row}
    if not rows:
        raise ValueError('No frozen lineage specimens')
    for wid, row in sorted(rows.items()):
        if type(row['observer_birth']) is not int or row['observer_birth'] not in range(4):
            raise ValueError('Invalid lineage release generation')
        parent = row['observer_parent']
        if parent is not None:
            if parent not in rows or rows[parent]['observer_birth'] != row['observer_birth']-1:
                raise ValueError('Invalid hidden branching parent')
            if rows[parent]['observer_population'] != row['observer_population']:
                raise ValueError('Cross-population parent')
            delta = row['observer_parameter']-rows[parent]['observer_parameter']
            if row['form'] == 'exact':
                program, ancestor = LG.freeze(row['program']), LG.freeze(rows[parent]['program'])
                expected = ancestor[:3]+(LG.node('lit', payload=row['observer_parameter']),)
                if program != expected:
                    raise ValueError('Program did not descend by its frozen edit')
            if not math.isclose(delta, row['observer_edit'], abs_tol=1e-12):
                raise ValueError('Frozen lineage edit changed')
        samples = observed(row['frozen_samples'])
        if len(samples) not in (2, 4):
            raise ValueError('Incomplete frozen specimen')
        if row['form'] == 'exact':
            machine = Machine(row['program'])
            if any(machine(probe) != value for probe, value in samples):
                raise ValueError('Specimen is not its frozen law')
    return manifest


class LineageMotion(MotionBody):
    def make(self, k, action, counter, noisy=True):
        throw = super().make(k, action, counter, noisy=noisy)
        shift = self.specification['observer_parameter']-.3
        from ccops5.core import paths
        times = np.arange(paths.N_OBS)*paths.DT_OBS
        throw.x[:] += shift*np.exp(times)
        throw.v[:] += shift*np.exp(times)
        return throw


class LineagePool(ScientistsPool):
    def __init__(self, manifest, *, generation=0):
        validate_lineage(manifest)
        super().__init__(manifest)
        self.generation = generation
        self.delivered = set()
        for wid, spec in sorted(self.specs.items()):
            if 'observer_birth' in spec:
                self.body(wid)

    def body(self, wid):
        if self.specs[wid].get('observer_population') == 'rail':
            if wid not in self.bodies:
                self.bodies[wid] = LineageMotion(self.specs[wid])
            return self.bodies[wid]
        return super().body(wid)

    def public(self):
        return tuple(world for world in super().public()
                     if self.specs[world.id].get('observer_birth', 0) <= self.generation)

    def sync(self, discovery):
        super().sync(discovery)
        self.delivered = {wid for wid, spec in self.specs.items() if 'frozen_samples' in spec
                          and all(observed(sample) in discovery.observations.get(wid, ())
                                  for sample in spec['frozen_samples'])}

    def next_specimen(self, discovery):
        available = {world.id for world in self.public()}
        pending = [wid for wid, spec in sorted(self.specs.items()) if wid in available
                   and 'frozen_samples' in spec and wid not in self.delivered]
        if not pending:
            return None
        wid = pending[0]
        self.delivered.add(wid)
        return wid, observed(self.specs[wid]['frozen_samples'])

    def act(self, wid, action):
        if self.specs[wid].get('observer_birth', 0) > self.generation:
            raise ValueError('Future specimen is still held back')
        return super().act(wid, action)

    def certify(self, wid, hypothesis, concepts, observations, *, library=()):
        if self.specs[wid].get('observer_birth', 0) > self.generation:
            raise ValueError('Future law is still held back')
        return super().certify(wid, hypothesis, concepts, observations, library=library)


def teach_darwin_once(mind):
    discovery = mind.discovery
    if discovery is None or not hasattr(discovery, 'darwin') or discovery.darwin.teacher_shown:
        return False
    if getattr(mind, 'progress', {}).get('assessment'):
        raise ValueError('No method teaching during assessment')
    receipt = next((receipt for receipt, _ in mind.sleep.replay if receipt.origin == 'taught'), None)
    if receipt is None:
        return False
    started = time.perf_counter()
    shown = discovery.darwin.demonstrate(mind, receipt.view, phase='lesson', origin='taught')
    discovery.darwin.phase('rsi')
    discovery.events.append(dict(world='taught-darwin-context', origin='taught', phase='lesson',
        darwin_demo=True, seconds=time.perf_counter()-started, experiment=None,
        certified=None, discovered=False, shown=shown))
    return True


def tree_agreement(trees, manifest):
    parents = {row['id']: row.get('observer_parent') for row in manifest['worlds']}
    hits = total = 0
    for tree in trees.values():
        for left, right, _ in tree['edges']:
            if left in parents and right in parents and (parents[left] or parents[right]):
                total += 1
                hits += int(parents.get(left) == right or parents.get(right) == left)
    return dict(edges=total, direct_parent_edges=hits, agreement=hits/total if total else None,
                fed_to_learner=False, claim='undirected direct-parent overlap, not a history proof')


def compare_runs(paths):
    from scripts.sera_u_rsi import read
    cases, false, scopes = {}, 0, []
    for path in paths:
        root = Path(path)
        state = read(root/'state.json')
        scopes.append((state.get('suite_sha256'), state.get('discovery_suite_sha256'),
                       state['protocol']['device'], state['protocol']['seed'],
                       state['protocol']['discovery']['share']))
        manifest = validate_lineage(read(root/'observer-discovery.json'))
        judges = state.get('discovery_judges', [])
        false += sum(bool(row['false_credit']) for row in judges)
        generations = state.get('discovery_generations', [])
        latest = {}
        for row in sorted(generations, key=lambda item: (item['arm'], item['generation'])):
            if 'darwin' in row:
                latest[row['arm']] = copy.deepcopy(row['darwin'])
        for arm, record in latest.items():
            record['hidden_lineage_agreement'] = tree_agreement(record['trees'], manifest)
            sorting = []
            for key, mechanism in sorted(record['mechanisms'].items()):
                if mechanism.get('parameter_rule'):
                    sorting.append(dict(mechanism=key, held_trajectory_audits=mechanism['audits'],
                        fed_to_learner=False, scope='fitted response coordinate; hidden physical parameter is not the same coordinate'))
                    continue
                typ = mechanism['region'][1]
                proposals = [row for row in manifest['lineage_variants']
                             if row['population'] == typ and row['generation'] > 0]
                answers = [LG.safe(LG.freeze(mechanism['predicate']), {'x': row['parameter']}, {})
                           for row in proposals]
                sorting.append(dict(mechanism=key, tested=len(proposals),
                    matches=sum(answer is row['persists'] for answer, row in zip(answers, proposals)),
                    missing=sum(answer is None for answer in answers), fed_to_learner=False,
                    scope='observer-only audit of later hidden proposals, including vanished variants'))
            record['hidden_sorting_audits'] = sorting
            predictions = record['predictions']
            record['prediction_counts'] = dict(made=len(predictions),
                confirmed=sum(row['confirmed'] is True for row in predictions),
                failed=sum(row['confirmed'] is False for row in predictions),
                pending=sum(row['confirmed'] is None for row in predictions))
        cases[root.name] = dict(arms=latest, completed=state.get('stage') == 'complete',
            discovery_generations=len(generations),
            control=not any(state['protocol']['discovery'].get('darwin', {}).values()),
            baseline_scientists=[dict(arm=row['arm'], generation=row['generation'], laws=row['laws'],
                seconds=row['seconds'], experiments=row['experiments']) for row in generations],
            false_credit=sum(bool(row['false_credit']) for row in judges))
    if not scopes or any(not scope[0] or not scope[1] for scope in scopes) or len(set(scopes)) != 1:
        raise ValueError('Darwin comparison requires identical frozen suites, seed, device and discovery share')
    return dict(claim=CLAIM, cases=cases, matched_scope=scopes[0], false_credit=false, zero_false_credit=not false,
        limits='Sampled supported mechanisms are not certificates; missing or censored runs remain unresolved.')


def main():
    import argparse
    from scripts.sera_u_rsi import read, write, validate_frozen_suite
    from sera_u import SeraU
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite')
    parser.add_argument('--compare', nargs='+')
    parser.add_argument('--out', required=True)
    parser.add_argument('--bootstrap')
    parser.add_argument('--seed', type=int, default=3)
    args = parser.parse_args()
    if args.compare:
        result = compare_runs(args.compare)
        write(args.out, result)
        if not result['zero_false_credit']:
            raise SystemExit('Darwin false credit must be zero')
    else:
        if not args.suite:
            parser.error('--suite is required to freeze')
        if Path(args.out).exists():
            raise SystemExit('Freeze once; refusing to overwrite an existing lineage manifest')
        mind = SeraU.load(args.bootstrap, exact=False) if args.bootstrap else None
        write(args.out, freeze_lineage(mind, validate_frozen_suite(read(args.suite)), args.seed))


if __name__ == '__main__':
    main()
