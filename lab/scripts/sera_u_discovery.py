"""Observer owner of U9's frozen rediscovery suite; never installed in SERA.

Hidden programs/laws, check throws, audit draws and truth grades live here.
This is rediscovery of laws we hid: the honest first test of discovery.
"""
import copy
import itertools
import math
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from sera import lang as LG, novel as NV, synth as SY, tasks as TS, worlds as SW
from sera_u.discovery import Certification, SCHEMA, WorldView, public_rail
from sera_u.ports import digest
from sera_u.sleep import expand, family, independent, substitute
from sera_u.proposer import library_identity


class Distribution:
    def __init__(self, typ, interval=None, length=None):
        self.typ = typ
        self.interval, self.length = interval, length

    def __call__(self, rng):
        if self.interval is not None:
            lo, hi = self.interval
            if self.typ == 'num':
                return int(rng.integers(lo, hi))
            length = self.length if self.length is not None else int(rng.integers(0, 9))
            return tuple(int(v) for v in rng.integers(lo, hi, size=length))
        if self.typ == 'num':
            return int(rng.integers(-8, 9))
        return tuple(int(v) for v in rng.integers(-8, 9, size=int(rng.integers(0, 9))))


class Machine:
    """The hidden program is a WORLD implementation, never a learner label."""
    def __init__(self, program):
        self.program = LG.freeze(program)

    def __call__(self, x):
        try:
            return independent(self.program, {'x': x}, {})
        except (ValueError, KeyError, *LG.BAD):
            return None


def freeze(mind, old_suite, seed):
    """Mechanical untaught compositions and held structures, observer side.

    Never borrow assessment programs as discovery worlds. Identities and
    seeds are frozen across all four cases, independent of discovery choices.
    """
    seeds = {}
    for receipt, concepts in (mind.sleep.replay if mind is not None else ()):
        if receipt.origin == 'explore':
            continue
        var, tin = receipt.view.inputs[0]
        for p in receipt.targets:
            p = substitute(expand(p, concepts), var, LG.node('var', payload='x'))
            seeds.setdefault(family(p, {}), (p, tin, receipt.view.out))
    if mind is None:
        # A saved U1 suite's retention generators are the bootstrap's checked
        # seeds. They are read by this observer only, never by the learner.
        for row in old_suite['retention']:
            p = LG.freeze(row['program'])
            seeds.setdefault(family(p, {}), (p, row['tin'], row['tout']))
    acquired = [seeds[k] for k in sorted(seeds)]
    excluded = set(seeds)
    excluded.update(r['family'] for label in ('assessment', 'wake', 'retention') for r in old_suite[label])
    machines = {'num': [], 'list': []}
    rng = np.random.default_rng([seed, 909])
    for length in (2, 3, 4, 5):
        for indices in itertools.product(range(len(acquired)), repeat=length):
            if all(len(rows) >= 2 for rows in machines.values()):
                break
            chain = [acquired[j] for j in indices]
            if any(a[2] != b[1] for a, b in zip(chain, chain[1:])):
                continue
            p, tin, _ = chain[0]
            tout = chain[-1][2]
            if tin not in machines or tout not in ('num', 'list') or len(machines[tin]) >= 2:
                continue
            for q, _, _ in chain[1:]:
                p = substitute(q, 'x', p)
            fam = family(p, {})
            if fam in excluded or LG.size(p) > 40:
                continue
            xs = tuple(Distribution(tin)(rng) for _ in range(32))
            ys = tuple(Machine(p)(x) for x in xs)
            if any(y is None or isinstance(y, tuple) and len(y) > 8 for y in ys):
                continue
            if len(set(map(repr, ys))) < 2 or ys == xs:
                continue
            excluded.add(fam)
            machines[tin].append(dict(form='exact', program=p, tin=tin, tout=tout, family=fam))
        if all(len(rows) >= 2 for rows in machines.values()):
            break
    if any(len(rows) != 2 for rows in machines.values()):
        raise ValueError('Insufficient disjoint untaught number/list compositions for U9')
    rows = []
    for typ in ('num', 'list'):
        for spec in machines[typ]:
            # Two independently seeded bodies test transfer of each found law.
            rows.extend([copy.deepcopy(spec), copy.deepcopy(spec)])
    rows += [dict(form='strengths', level=2, units=False),
             dict(form='strengths', level=2, units=True)]
    for shape in sorted(NV.SHAPES):
        rows.extend([dict(form='strengths', novel=shape), dict(form='strengths', novel=shape)])
    for j, row in enumerate(rows):
        row.update(id='d'+str(j), seed=seed+9000, index=90000+j)
    rows, dropped = buildable(rows)
    return dict(schema=SCHEMA, seed=seed, worlds=rows, dropped=dropped,
                split='untaught expanded compositions disjoint from all RSI suites; held physics structures and novel shapes',
                claim='rediscovery of laws we hid, not demonstrated open-ended scientific discovery')


FREEZE_TRIES = 4


def buildable(rows, tries=FREEZE_TRIES):
    """Build every novel world once, here, observer-side and off SERA's clock: a world that no list law misses by
    NOVEL_GAP within `tries` draws is dropped and listed; a kept one records its draw, so a body rebuilds it in one
    step without measuring again (one draw measures every list law: about 30 s; 40 failed draws stopped a run)."""
    kept, dropped = [], []
    for row in rows:
        if 'novel' in row:
            try:
                world = NV.novel_world(row['novel'], row['seed'], row['index'], tries)
            except RuntimeError as exc:
                dropped.append(dict(id=row['id'], novel=row['novel'], index=row['index'], reason=str(exc)[-200:]))
                continue
            row = dict(row, attempt=world.novelty['attempt'], gap=float(world.novelty['gap']),
                       nearest=str(world.novelty['nearest']))
        kept.append(row)
    return kept, dropped


def validate(manifest, old_suite, mind=None):
    if manifest['schema'] != SCHEMA:
        raise ValueError('Rediscovery suite schema changed')
    rows = manifest['worlds']
    if 'scientists_suite' in manifest and manifest['scientists_suite'] != 'u11-scientists-1':
        raise ValueError('Scientists suite schema changed')
    if 'scientists_suite' in manifest:
        groups = sorted({r['observer_group'] for r in rows if 'observer_group' in r})
        for group in groups:
            members = [r for r in rows if r.get('observer_group') == group]
            if (len(members) != 4 or sorted(r.get('observer_coordinate') for r in members) != [0, 1, 2, 3]
                    or any(r.get('withheld') != (r.get('observer_coordinate') == 2) for r in members)):
                raise ValueError('Scientists withholding schedule changed')
    if 'einstein_suite' in manifest and manifest['einstein_suite'] != 'u10-einstein-1':
        raise ValueError('Einstein suite schema changed')
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Rediscovery IDs must be unique')
    excluded = {r['family'] for label in ('assessment', 'wake', 'retention') for r in old_suite[label]}
    if mind is not None:
        excluded.update(family(p, concepts) for receipt, concepts in mind.sleep.replay
                        if receipt.origin != 'explore' for p in receipt.targets)
    for row in rows:
        if type(row['id']) is not str or any(type(row[k]) is not int or row[k] < 0 for k in ('seed', 'index')):
            raise ValueError('Opaque IDs and nonnegative integer world seeds required')
        if row['form'] == 'exact':
            if 'audit_range' in row:
                interval = row['audit_range']
                if (manifest.get('einstein_suite') != 'u10-einstein-1' or len(interval) != 2 or
                        any(type(v) is not int or abs(v) > 100 for v in interval) or interval[0] >= interval[1] or
                        row.get('audit_length') not in (None, 2)):
                    raise ValueError('Invalid observer Einstein audit scope')
            if family(LG.freeze(row['program']), {}) != row['family'] or row['family'] in excluded:
                raise ValueError('Rediscovery law overlaps course/assessment or its manifest changed')
            if row['tin'] not in ('num', 'list') or row['tout'] not in ('num', 'list'):
                raise ValueError('Unsupported rediscovery machine signature')
            p = LG.freeze(row['program'])
            sig = LG.infer(p, {}, arg='x')
            if LG.size(p) > 40 or sig is None or not LG.fits(sig, row['tin'], row['tout']):
                raise ValueError('Rediscovery program exceeds the bounded typed language')
        elif row['form'] != 'strengths':
            raise ValueError('Unknown rediscovery body')
        elif 'novel' in row:
            if row['novel'] not in NV.SHAPES:
                raise ValueError('Unknown observer novel shape')
            if (type(row.get('attempt')) is not int or row['attempt'] < 0 or type(row.get('gap')) is not float
                    or row['gap'] < NV.NOVEL_GAP or type(row.get('nearest')) is not str):
                raise ValueError('A novel world must be built once by the observer when frozen: freeze again')
        elif row.get('motion_sensor'):
            if (manifest.get('scientists_suite') != 'u11-scientists-1'
                    or row.get('motion_sensor') is not True or type(row.get('has_conserved')) is not bool):
                raise ValueError('Invalid observer-only scientists motion sensor')
        elif row.get('level') not in (2, 3, 4) or type(row.get('units')) is not bool:
            raise ValueError('Rails must draw held structural levels with an explicit units switch')
    if 'roadmap_suite' in manifest:
        from scripts.sera_u_roadmap import validate_roadmap
        validate_roadmap(manifest)
    if 'lineage_suite' in manifest:
        from scripts.sera_u_darwin import validate_lineage
        validate_lineage(manifest)
    return manifest


class WorldPool:
    def __init__(self, manifest):
        self.manifest = copy.deepcopy(manifest)
        self.specs = {r['id']: r for r in self.manifest['worlds']}
        self.bodies, self.audit_records = {}, []
        self.discovered = set()

    def body(self, wid):
        if wid not in self.bodies:
            spec = self.specs[wid]
            if spec['form'] == 'exact':
                self.bodies[wid] = TS.Exact('code' if spec['tin'] == 'list' else 'math', wid,
                    Machine(spec['program']), {'x': spec['tin']}, spec['tout'], [], [],
                    Distribution(spec['tin'], spec.get('audit_range'), spec.get('audit_length')))
            else:
                if 'novel' in spec:
                    world = NV.novel_world(spec['novel'], spec['seed'], spec['index'],
                                           known=(spec['attempt'], spec['gap'], spec['nearest']))
                    # NovelWorld supplies no held_out by default. The observer
                    # makes its own independent test pushes and retains them.
                    from ccops5.core.worlds import Action
                    check_body = copy.deepcopy(world)
                    check_body.made = {k: 1000000 for k in range(world.n_situations)}
                    world.held_out = [check_body.push(k, Action(((0., 1.2, u),)), 'check')
                        for k in range(world.n_situations) for u in (-.9, .9)]
                    world.made = {}
                else:
                    # Held-out structural predicate, never a family sent to SERA.
                    world = SW.make(spec['seed'], spec['index'], spec['level'], split='held', tricks=0.)
                    if spec['units']:
                        world, _ = TS.rail_world(spec['seed'], spec['index'], world.spec.family,
                                                level=spec['level'], units=True)
                self.bodies[wid] = world
        return self.bodies[wid]

    def public(self):
        out = []
        for wid in sorted(self.specs):
            spec = self.specs[wid]
            if spec['form'] == 'exact':
                out.append(WorldView(wid, 'exact', spec['tin'], spec['tout']))
            else:
                # The body schema is public and fixed by these generators.
                # Visiting an unrelated world must not build every hidden rail.
                out.append(WorldView(wid, 'strengths', objects=8, sigma=(.001, .001)))
        return tuple(out)

    def sync(self, discovery):
        """Restore simulator's own-noise counters from performed public acts.

        No simulator state or hidden spec enters an entity checkpoint.
        Exact audits are seeded independently by the frozen trial identity.
        """
        from collections import Counter
        for wid in sorted(discovery.observations):
            if self.specs[wid]['form'] == 'strengths' and discovery.observations[wid]:
                self.body(wid).made = dict(Counter(row[0] for row in discovery.observations[wid]))
                self.body(wid).log = []
        self.discovered = {family(e['hypothesis'], {}) for e in discovery.laws.values() if e['form'] == 'exact'}

    def dream_allowed(self, program, concepts):
        """Partition enforcement stays with the observer, even on resume."""
        fam = family(program, concepts)
        held = {r['family'] for r in self.specs.values() if r['form'] == 'exact'}
        return fam not in held or fam in self.discovered

    def act(self, wid, action):
        body = self.body(wid)
        if self.specs[wid]['form'] == 'exact':
            if action[0] != 'ask':
                raise ValueError('Wrong machine hand')
            x = LG.freeze(action[1])
            y = body._y(x)
            if y is None:
                raise ValueError('Machine undefined at chosen input')
            return x, y
        from ccops5.core import paths
        from ccops5.core.worlds import Action
        _, k, segments = action
        if not 0 <= k < body.n_situations or not segments:
            raise ValueError('Wrong rail hand')
        end = 0.
        for a, b, f in segments:
            if not (end <= a < b <= paths.T_END and abs(f) <= 1. and math.isfinite(f)):
                raise ValueError('Push exceeds design.py hand limits')
            end = b
        t = body.push(k, Action(segments), 'own')
        return int(k), tuple(segments), tuple(map(float, t.x)), tuple(map(float, t.v))

    def certify(self, wid, hypothesis, concepts, observations, *, library=()):
        """Unchanged Exact/Rail gates, observer-controlled fresh checks only.

        A failing fresh input is intentionally discarded from the learner's
        view; its next anomaly question must use its own performed experiments.
        """
        spec, body = self.specs[wid], self.body(wid)
        from ccops5.core import grammar
        grammar.use_library(library)
        record_id = digest((SCHEMA, wid, hypothesis, observations, library_identity(concepts)))
        rng = np.random.default_rng([spec['seed'], spec['index'], int(record_id[:8], 16)])
        if spec['form'] == 'exact':
            task = copy.deepcopy(body)
            bits = LG.bits(hypothesis, concepts)
            task.data = [(x, y) for x, y in observations]
            ok, n, fail = task.verify(hypothesis, concepts, bits, rng)
            own_consistent = task.consistent(hypothesis, concepts)
            ok = bool(ok and own_consistent)  # a caller veto cannot relax the audit
            kind = 'formula'
            bound = (('eps', SY.EPS), ('delta', SY.DELTA), ('audit_n', int(n)), ('bits', float(bits)))
            grade = task.grade(hypothesis, concepts, ok, n=1000, seed=spec['seed'])
            planted = family(hypothesis, concepts) == spec['family']
            refuted = fail is not None or not own_consistent
            records = dict(audit_n=n, bits=bits, failed=fail is not None, own_consistent=own_consistent)
        else:
            public = next(w for w in self.public() if w.id == wid)
            task = public_rail(public, observations)
            accepted = None
            attempts = []
            for ramp in (True, False):
                claim = task.claim_terms(hypothesis, concepts, library, ramp=ramp)
                if claim is None:
                    continue
                fam, credit = claim
                # Same Rail judge, on its own check throws in addition to the
                # observed throws. They never enter the public task or views.
                # Judge scrutiny may make extra throws. Its body is a private
                # clone, so audits cannot advance the learner's noise stream.
                judge = TS.Rail(copy.deepcopy(body), wid)
                judge.throws = copy.deepcopy(task.throws) + copy.deepcopy(body.held_out)
                ok, cert, why = judge.verify(fam)
                attempts.append(dict(accepted=bool(ok), family=fam, credit=credit,
                                     band=cert.band, eps=cert.eps, reason=why))
                if ok:
                    accepted = (judge, cert, credit, ramp)
                    break
            refuted = any(a['reason'] and 'something else is here' in a['reason'] for a in attempts)
            ok = accepted is not None
            if accepted:
                judge, cert, credit, ramp = accepted
                kinds = {k for _, k in credit}
                kind = 'curve' if 'curve' in kinds else 'drawing' if 'drawing' in kinds else 'formula'
                bound = (('eps', float(cert.eps)), ('band', float(cert.band)), ('ramp', bool(ramp)))
                # Grade at exactly the certificate's own throws. The world's
                # original teacher trajectories are not its observed scope.
                grading_body = copy.copy(body)
                grading_body.throws = judge.throws
                grading_body.log = []
                saved = judge.world
                judge.world = grading_body
                try:
                    grade = judge.grade(cert, True, n_throws=len(judge.throws))
                finally:
                    judge.world = saved
                planted = tuple(cert.family) == tuple(body.spec.family)
            else:
                kind, bound = 'curve', (('eps', TS.EPS),)
                grade, planted = dict(verdict='not proven'), False
            records = dict(attempts=attempts)
        # Truth scoring and planted-law comparisons are OBSERVER ONLY.
        false = bool(ok and grade['verdict'] == 'SURE AND WRONG')
        self.audit_records.append(dict(record=record_id, world=wid, accepted=bool(ok), kind=kind,
            bound=bound, hypothesis=hypothesis, grade=grade, false_credit=false,
            found=bool(ok and not planted), judge=records))
        return Certification(bool(ok), kind, bound, record_id, bool(refuted))


def teach_quantity_once(mind):
    """One taught-world demonstration of the mechanism, without a supplied law.

    Only measurements from a nursery world enter the teacher seam. The
    teacher shows 'try fitting a number per thing', never its true numbers.
    No rediscovery world is involved and U5 confines this to the lesson phase.
    """
    if mind.discovery is None or mind.discovery.teacher_shown or not mind.discovery.switches['hidden_quantities']:
        return False
    started = time.perf_counter()
    from ccops5.core.worlds import Action
    from sera import compact as C
    world, _ = TS.rail_world(mind.seed, 80001, (('position', 'straight'),), units=True)
    throws = [world.push(k, Action(((0., .5, u),)), 'own')
              for k in range(world.n_situations) for u in (-1., 1.)]
    obj, y, hand, xb, vb, tb = C.intervals(throws)
    # Remove a local observed drift exactly as the learner's fitter does.
    d = np.column_stack((np.ones(len(y)), xb, vb, tb))
    for k in sorted(set(map(int, obj))):
        m = obj == k
        y[m] -= d[m] @ np.linalg.lstsq(d[m], y[m], rcond=None)[0]
        hand[m] -= d[m] @ np.linalg.lstsq(d[m], hand[m], rcond=None)[0]
    shown = mind.discovery.demonstrate_quantity(obj, y, hand,
        math.sqrt(2)*world.sigma[1]/C.DT, phase='lesson')
    mind.discovery.events.append(dict(world='taught-body', origin='taught',
        mechanism_demo=True, phase='lesson', seconds=time.perf_counter()-started,
        experiment=None, certified=None, discovered=False, shown=shown))
    return shown


def report(generations, judge_records):
    ordered = sorted(generations, key=lambda r: (r['arm'], r['generation']))
    previous = {}
    rows = []
    for row in ordered:
        row = copy.deepcopy(row)
        old = previous.get(row['arm'])
        for key in ('seconds_per_law', 'experiments_per_law'):
            row[key+'_improved'] = (row[key] < old[key] if old and old[key] is not None and row[key] is not None else None)
        previous[row['arm']] = row
        rows.append(row)
    false = sum(bool(r['false_credit']) for r in judge_records)
    return dict(generations=rows, false_credit=false, zero_false_credit=not false,
                found=[r for r in judge_records if r['found']], judge_records=judge_records,
                claim='Rediscovery of laws we hid; search plus retention, not a claim of Newton-level discovery.',
                limit='Audit bounds are probabilistic; found means not the planted structural spelling, not new science.')


def main():
    """Freeze once from a shared bootstrap; same-VM cases read the same bytes."""
    import argparse
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from sera_u import SeraU
    from scripts.sera_u_rsi import read, write, validate_frozen_suite
    ap = argparse.ArgumentParser()
    ap.add_argument('--bootstrap', default=None, help='Optional same-code bootstrap checkpoint; else use frozen retention seeds')
    ap.add_argument('--suite', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=3)
    args = ap.parse_args()
    mind = SeraU.load(args.bootstrap, exact=False) if args.bootstrap else None
    suite = validate_frozen_suite(read(args.suite))
    write(args.out, validate(freeze(mind, suite, args.seed), suite, mind))


if __name__ == '__main__':
    main()
