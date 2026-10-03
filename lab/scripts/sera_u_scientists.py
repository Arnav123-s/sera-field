"""U11 observer: frozen hidden families, independent audits, reports.

All target programs, withheld membership, samplers and clean trajectories
remain here. The learner gets opaque WorldViews and performed observations.
"""
import copy
import math
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from sera import lang as LG, synth as SY, tasks as TS
from sera_u.discovery import Certification, WorldView, scientist_records
from sera_u.ports import TaskView, digest
from sera_u.scientists import CRUTCHES, conserved_fit, motion_probes
from sera_u.sleep import family, independent
from sera_u.proposer import library_identity
from scripts.sera_u_discovery import Distribution, WorldPool, validate
from scripts.sera_u_einstein import freeze_einstein

SCIENTISTS_SCHEMA = 'u11-scientists-1'
CLAIM = ('A test of whether these habits help on worlds with hidden structure, '
         "not a claim of these scientists' insight.")


def freeze_scientists(mind, suite, seed):
    manifest = freeze_einstein(mind, suite, seed)
    excluded = {r['family'] for label in ('retention', 'wake', 'assessment') for r in suite[label]}
    excluded.update(r['family'] for r in manifest['worlds'] if r['form'] == 'exact')
    if mind is not None:
        excluded.update(family(p, concepts) for receipt, concepts in mind.sleep.replay
                        if receipt.origin != 'explore' for p in receipt.targets)
    x = LG.node('var', payload='x')
    head, tail = LG.node('head', x), LG.node('head', LG.node('tail', x))
    # Observer-only content: same structural law with regular literals. The
    # fourth body is unavailable until three seed laws earn outer certificates.
    # Both family identity and the withholding schedule stay private.
    for depth in range(7):
        base = LG.node('mul', LG.node('mul', x, x), x)
        list_base = LG.node('mul', LG.node('add', head, tail), LG.node('sub', head, tail))
        for _ in range(depth):
            base = LG.node('add', base, LG.node('zero'))
            list_base = LG.node('add', list_base, LG.node('zero'))
        candidates = []
        for group, primitive, tin in (('number-gap', base, 'num'), ('list-gap', list_base, 'list')):
            for coordinate in (0, 1, 3, 2):
                parameter = 2+2*coordinate
                p = LG.node('add', primitive, LG.node('lit', payload=parameter))
                candidates.append(dict(program=p, tin=tin, tout='num', observer_category=group,
                    observer_group=group, observer_coordinate=coordinate, withheld=coordinate == 2))
        odd = LG.node('if', LG.node('lt', x, LG.node('lit', payload=4)),
                      base, LG.node('add', base, LG.node('one')))
        candidates += [dict(program=base, tin='num', tout='num', observer_category='long-chase', audit_range=(-6, 4)),
                       dict(program=odd, tin='num', tout='num', observer_category='long-chase', audit_range=(-6, 9))]
        if {family(r['program'], {}) for r in candidates} & excluded:
            continue
        for j, row in enumerate(candidates):
            row.update(id='s'+str(j), form='exact', family=family(row['program'], {}),
                       seed=seed+11000, index=110000+j)
            manifest['worlds'].append(row)
        break
    else:
        raise ValueError('No disjoint scientists number/list suite within structural budget')
    for j, conserved in enumerate((True, True, False)):
        manifest['worlds'].append(dict(id='s-motion'+str(j), form='strengths',
            motion_sensor=True, has_conserved=conserved, seed=seed+11000, index=111000+j,
            observer_category='conserved' if conserved else 'no-conserved'))
    manifest.update(scientists_suite=SCIENTISTS_SCHEMA, claim=CLAIM)
    manifest['split'] += '; untaught parameter families, withheld members, relation search, motion and cross-item anomalies'
    return validate(manifest, suite, mind)


class MotionBody:
    """Synthetic rails with controllable trajectory initial conditions.

    This is a sensor benchmark, not a force-law simulator certified by Rail.
    Conserved-law audits inspect independently kept throws; force certification
    on these sensor bodies always abstains. No core acceptance bar is changed.
    """
    def __init__(self, spec):
        from ccops5.core.worlds import Action
        self.specification = copy.deepcopy(spec)
        self.n_situations = 8
        self.sigma = (.001, .001)
        self.made, self.log = {}, []
        self.held_out = [self.make(k, Action(((0., .5, f),)), 1000000+j, noisy=True)
                         for j, (k, f) in enumerate((k, f) for k in range(8) for f in (-.9, .3, .9))]
        self.clean_held = [self.make(k, Action(((0., .5, f),)), 1000000+j, noisy=False)
                          for j, (k, f) in enumerate((k, f) for k in range(8) for f in (-.9, .3, .9))]

    def make(self, k, action, counter, noisy=True):
        from ccops5.core import paths
        from ccops5.core.worlds import Throw
        spec = self.specification
        times = np.arange(paths.N_OBS)*paths.DT_OBS
        rate = .12+.01*k
        initial = .2+.03*k
        impulse = sum((b-a)*f for a, b, f in action.segments)
        c = .3*impulse+.04*k
        # No invariant formula or parameter enters the learner. In the first
        # class v-x remains constant with throw-specific initial value; the
        # second adds independent drift, so that candidate must fail.
        xs = (initial+c)*np.exp(times)-c
        vs = xs+c
        if not spec['has_conserved']:
            xs = xs+rate*times**2
            vs = vs+2*rate*times
        if noisy:
            rng = np.random.default_rng([spec['seed'], spec['index'], k, counter])
            xs = xs+rng.normal(0, self.sigma[0], len(xs))
            vs = vs+rng.normal(0, self.sigma[1], len(vs))
        return Throw(k, counter, action, xs, vs, 'own' if counter < 1000000 else 'check')

    def push(self, k, action, tag='own'):
        j = self.made.get(k, 0)
        self.made[k] = j+1
        throw = self.make(k, action, j)
        self.log.append(throw)
        return throw


def throw_rows(throws):
    return tuple((int(t.situation), tuple(t.action.segments), tuple(map(float, t.x)), tuple(map(float, t.v)))
                 for t in throws)


class ScientistsPool(WorldPool):
    def __init__(self, manifest):
        super().__init__(manifest)
        self.met_certified = set()

    def body(self, wid):
        if self.specs[wid].get('motion_sensor'):
            if wid not in self.bodies:
                self.bodies[wid] = MotionBody(self.specs[wid])
            return self.bodies[wid]
        return super().body(wid)

    def public(self):
        public = super().public()
        return tuple(w for w in public if not self.specs[w.id].get('withheld') or self.available(w.id))

    def available(self, wid):
        spec = self.specs[wid]
        peers = [r['id'] for r in self.specs.values() if r.get('observer_group') == spec.get('observer_group')
                 and not r.get('withheld')]
        return len(peers) >= 3 and all(p in self.met_certified for p in peers)

    def sync(self, discovery):
        super().sync(discovery)
        self.met_certified = {w for e in discovery.laws.values() for w in e['coverage']}

    def act(self, wid, action):
        if self.specs[wid].get('withheld') and not self.available(wid):
            raise ValueError('Withheld member has not been exposed')
        return super().act(wid, action)

    def certify(self, wid, hypothesis, concepts, observations, *, library=()):
        if self.specs[wid].get('motion_sensor'):
            return Certification(False, 'formula', (('sensor_only', True),),
                                 digest((wid, hypothesis, observations)))
        result = super().certify(wid, hypothesis, concepts, observations, library=library)
        if result.accepted:
            self.met_certified.add(wid)
        return result

    def audit_relation(self, lhs, rhs, tin, tout, concepts, own):
        record = digest(('u11-relation', lhs, rhs, tin, library_identity(concepts), own))
        # Acquired execution is the definition being conjectured; the
        # independent interpreter supplies the target, not a hidden world law.
        snapshot = copy.deepcopy(concepts)
        def target(x):
            try:
                return independent(lhs, {'x': x}, snapshot)
            except (ValueError, KeyError, *LG.BAD):
                return None
        task = TS.Exact('math' if tin == 'num' else 'code', record, target,
                        {'x': tin}, tout, [x for x, _ in own], [], Distribution(tin))
        task.data = list(own)
        rng = np.random.default_rng([11011, int(record[:8], 16)])
        bits = LG.bits(rhs, concepts)+LG.bits(lhs, concepts)
        ok, n, failure = task.verify(rhs, concepts, bits, rng)
        ok = bool(ok and task.consistent(rhs, concepts))
        grade = task.grade(rhs, concepts, ok, n=1000, seed=int(record[8:16], 16))
        false = bool(ok and grade['verdict'] == 'SURE AND WRONG')
        bound = (('eps', SY.EPS), ('delta', SY.DELTA), ('audit_n', int(n)))
        self.audit_records.append(dict(record=record, world='own-concepts', habit='number_conjectures',
            accepted=ok, kind='formula', hypothesis=(lhs, rhs), bound=bound,
            grade=grade, found=ok, false_credit=false, judge=dict(audit_n=n, failed=failure is not None)))
        return Certification(ok, 'formula', bound, record, failure is not None or not task.consistent(rhs, concepts))

    def audit_conserved(self, wid, program, concepts, quantities):
        body = self.body(wid)
        sigma = body.sigma
        rows = throw_rows(body.held_out)
        probes = motion_probes(rows, quantities)
        try:
            checked = all(math.isclose(LG.evaluate(program, env, concepts), independent(program, env, concepts),
                                      rel_tol=1e-9, abs_tol=1e-9) for trajectory in probes for env in trajectory)
        except (ValueError, KeyError, *LG.BAD):
            checked = False
        accepted = checked and conserved_fit(program, probes, concepts, sigma)
        # Observer truth check on clean trajectories with tighter tolerance,
        # only for this artificial sensor class. Actual Rail worlds retain
        # a declared sampled sensor scope, rather than a universal theorem.
        clean = (conserved_fit(program, motion_probes(throw_rows(body.clean_held), quantities), concepts, (1e-7, 1e-7))
                 if hasattr(body, 'clean_held') else accepted)
        record = digest(('u11-conserved', wid, program, library_identity(concepts), quantities))
        bound = (('held_throws', len(rows)), ('noise_sigma', tuple(sigma)))
        false = bool(accepted and not clean)
        self.audit_records.append(dict(record=record, world=wid, habit='conserved_quantities', accepted=bool(accepted),
            kind='formula', bound=bound, hypothesis=program, found=bool(accepted), false_credit=false,
            grade=dict(verdict='SURE AND WRONG' if false else 'sampled constancy' if accepted else 'not proven'),
            judge=dict(held_throws=len(rows), independent_execution=bool(checked))))
        return Certification(bool(accepted), 'formula', bound, record, not accepted)


def teach_scientists_once(mind):
    d = mind.discovery
    if d is None or not hasattr(d, 'scientists') or d.scientists.teacher_shown:
        return False
    if getattr(mind, 'progress', {}).get('assessment'):
        raise ValueError('No method teaching during assessment')
    receipt = next((r for r, _ in mind.sleep.replay if r.origin == 'taught'), None)
    if receipt is None:
        return False
    started = time.perf_counter()
    shown = d.scientists.demonstrate(mind, receipt.view, phase='lesson', origin='taught')
    if d.scientists.switches['conserved_quantities'] and not d.scientists.conservation_shown:
        shown += d.scientists.demonstrate(mind, taught_motion_view(mind.seed), phase='lesson', origin='taught')
    d.scientists.phase('rsi', d)
    d.events.append(dict(world='taught-scientist-context', origin='taught', phase='lesson',
        scientist_demo=True, seconds=time.perf_counter()-started, experiment=None,
        certified=None, discovered=False, shown=shown))
    return True


def taught_motion_view(seed):
    """Nursery sensor, disjoint from every frozen discovery/assessment body."""
    from ccops5.core import paths
    from ccops5.core.worlds import Action
    body = MotionBody(dict(has_conserved=True, seed=seed, index=81111))
    measurements = []
    for j, force in enumerate((-1., 1.)):
        throw = body.push(0, Action(((0., .5, force),)))
        for i in range(0, len(throw.x), 2):
            measurements.append(('motion', 0, j, i*paths.DT_OBS, float(throw.x[i]), float(throw.v[i])))
    return TaskView((('s', 'num'),), 'num', form='strengths', measurements=tuple(measurements))


def report_scientists(generations, judges):
    latest = {}
    for row in sorted(generations, key=lambda r: (r['arm'], r['generation'])):
        if 'scientists' in row:
            latest[row['arm']] = copy.deepcopy(row)
    for arm, row in latest.items():
        row['scientist_records'] = scientist_records([r for r in sorted(generations, key=lambda r: r['generation'])
                                                     if r['arm'] == arm])
    false = sum(bool(r['false_credit']) for r in judges)
    return dict(claim=CLAIM, arms=latest, false_credit=false, zero_false_credit=not false,
        audit_scope='Fresh Exact samples for relations; held sensor throws for quantities. Sampled audits are not proofs.',
        family_scope='Own literal-hole structural families on a conservative one-gap regular lattice; no member labels supplied.')


def compare_runs(paths):
    from scripts.sera_u_rsi import read
    cases, scopes = {}, []
    for path in paths:
        path = Path(path)
        state, report = read(path/'state.json'), read(path/'g_curve.json')
        scopes.append((state.get('suite_sha256'), state.get('discovery_suite_sha256'),
                       state['protocol']['device'], state['protocol']['seed']))
        generations = report.get('discovery', {}).get('generations', [])
        habits = report_scientists(generations, report.get('discovery', {}).get('judge_records', []))
        arms = {}
        for arm in sorted({r['arm'] for r in generations}):
            rows = [r for r in generations if r['arm'] == arm]
            last = max(rows, key=lambda r: r['generation'])
            arms[arm] = dict(laws=sum(r['laws'] for r in rows), seconds=sum(r['seconds'] for r in rows),
                experiments=sum(r['experiments'] for r in rows), scientists=last.get('scientists'),
                records=habits['arms'].get(arm, {}).get('scientist_records'), generations=rows)
        cases[path.name.removeprefix('u-')] = dict(complete=report['complete'], arms=arms,
                                                 false_credit=habits['false_credit'])
    if not scopes or any(not a or not b for a, b, _, _ in scopes) or len(set(scopes)) != 1:
        raise ValueError('Scientists comparison requires identical frozen suites, seed and device')
    false = sum(r['false_credit'] for r in cases.values())
    return dict(claim=CLAIM, matched_scope=scopes[0], cases=cases,
                false_credit=false, zero_false_credit=not false)


def main():
    import argparse
    from scripts.sera_u_rsi import read, write, validate_frozen_suite
    from sera_u import SeraU
    ap = argparse.ArgumentParser()
    ap.add_argument('--suite')
    ap.add_argument('--compare', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--bootstrap')
    ap.add_argument('--seed', type=int, default=3)
    args = ap.parse_args()
    if args.compare:
        result = compare_runs(args.compare)
        write(args.out, result)
        if not result['zero_false_credit']:
            raise SystemExit('Scientists false credit must be zero')
    else:
        if not args.suite:
            ap.error('--suite is required to freeze')
        mind = SeraU.load(args.bootstrap, exact=False) if args.bootstrap else None
        write(args.out, freeze_scientists(mind, validate_frozen_suite(read(args.suite)), args.seed))


if __name__ == '__main__':
    main()
