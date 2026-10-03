"""U13 observer: one frozen untaught roadmap plus the U12 lineage worlds."""
import copy
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sera import lang as LG
from sera_u.ports import digest
from sera_u.sleep import family
from scripts.sera_u_darwin import LineagePool, compare_runs as compare_lineage, freeze_lineage
from scripts.sera_u_discovery import validate

SCHEMA = 'u13-roadmap-1'
CLAIM = ('A test of whether own operations, rebuilding and rough estimates help SERA, '
         'not a claim of Newton, Feynman or Fermi insight. Basis changes are not new primitive semantics '
         'or a new mathematical theory; sampled equivalence is not exact proof.')


def freeze_roadmap(mind, suite, seed):
    manifest = freeze_lineage(mind, suite, seed)
    excluded = {row['family'] for label in ('wake', 'retention', 'assessment') for row in suite[label]}
    excluded.update(row['family'] for row in manifest['worlds'] if row['form'] == 'exact')
    variable = LG.node('var', payload='x')
    serial = 0
    for typ in ('num', 'list'):
        argument = variable if typ == 'num' else LG.node('head', variable)
        repeated = LG.node('add', argument, LG.node('one'))
        base = LG.node('mul', repeated, repeated)
        # Observer-only, explicit structural partition from the nursery/U1 suite.
        for _ in range(8):
            templates = [LG.node('add', base, LG.node('lit', payload=k)) for k in (2, 3)]
            later = [LG.node('add', LG.node('mul', base, base), LG.node('lit', payload=k)) for k in (4, 5)]
            reuse = [LG.node('add', LG.node('mul', base, LG.node('lit', payload=k)), base) for k in (2, 3)]
            scales = [LG.node('mul', LG.node('lit', payload=k), base) for k in (-10000, -100, -1, 1, 10, 1000, 10000)]
            if not {family(p, {}) for p in templates+later+reuse+scales} & excluded:
                break
            base = LG.node('add', base, LG.node('zero'))
        else:
            raise ValueError('No disjoint bounded roadmap structure; freeze with another nursery')
        seeds = []
        for habit, programs in (('own_operations', templates+later), ('rederive_concepts', reuse), ('rough_estimates', scales)):
            for index, program in enumerate(programs):
                sig = LG.infer(program, {}, arg='x')
                if LG.size(program) > 40 or sig is None or not LG.fits(sig, typ, 'num'):
                    raise ValueError('Roadmap structure exceeded its finite typed budget')
                wid = digest(('roadmap', seed, serial))[:20]
                row = dict(id=wid, form='exact', tin=typ, tout='num', program=program,
                    family=family(program, {}), seed=seed+13000, index=130000+serial,
                    observer_habit=habit, observer_requires=tuple(seeds) if habit == 'own_operations' and index >= 2 else ())
                serial += 1
                if habit == 'own_operations' and index < 2:
                    seeds.append(wid)
                manifest['worlds'].append(row)
        excluded.update(family(p, {}) for p in templates+later+reuse+scales)
    manifest.update(roadmap_suite=SCHEMA, claim=CLAIM)
    manifest['split'] += '; untaught repeated substructures, rebuilt reuse, magnitude spans'
    return validate_roadmap(validate(manifest, suite, mind))


def validate_roadmap(manifest):
    if manifest.get('roadmap_suite') != SCHEMA:
        raise ValueError('Frozen roadmap schema changed')
    rows = {row['id']: row for row in manifest['worlds']}
    habits = set()
    for wid, row in sorted(rows.items()):
        if 'observer_habit' not in row:
            continue
        habits.add(row['observer_habit'])
        if row['observer_habit'] not in ('own_operations', 'rederive_concepts', 'rough_estimates'):
            raise ValueError('Unknown observer roadmap category')
        requires = row.get('observer_requires', ())
        if any(parent not in rows or parent == wid or rows[parent].get('observer_requires') for parent in requires):
            raise ValueError('Invalid later-composition release')
    if habits != {'own_operations', 'rederive_concepts', 'rough_estimates'}:
        raise ValueError('Incomplete roadmap opportunities')
    return manifest


class RoadmapPool(LineagePool):
    def __init__(self, manifest, *, generation=0):
        validate_roadmap(manifest)
        super().__init__(manifest, generation=generation)
        # All body construction is observer setup, outside Discovery.tick.
        for wid in sorted(self.specs):
            self.body(wid)

    def public(self):
        return tuple(world for world in super().public() if all(
            parent in self.met_certified for parent in self.specs[world.id].get('observer_requires', ())))

    def act(self, wid, action):
        if not all(parent in self.met_certified for parent in self.specs[wid].get('observer_requires', ())):
            raise ValueError('Later composition still held back')
        return super().act(wid, action)

    def certify(self, wid, hypothesis, concepts, observations, *, library=()):
        if not all(parent in self.met_certified for parent in self.specs[wid].get('observer_requires', ())):
            raise ValueError('Later composition still held back')
        return super().certify(wid, hypothesis, concepts, observations, library=library)

    def audit_reconstruction(self, lhs, rhs, tin, tout, concepts, own):
        verdict = super().audit_relation(lhs, rhs, tin, tout, concepts, own)
        self.audit_records[-1]['habit'] = 'rederive_concepts'
        return verdict


def teach_roadmap_once(mind):
    discovery = mind.discovery
    if discovery is None or not hasattr(discovery, 'roadmap') or discovery.roadmap.teacher_shown:
        return False
    receipts = [receipt for receipt, _ in mind.sleep.replay if receipt.origin == 'taught']
    if not receipts:
        return False
    started = time.perf_counter()
    shown = discovery.roadmap.demonstrate(mind, receipts[0].view, phase='lesson', origin='taught')
    discovery.roadmap.phase('rsi')
    discovery.events.append(dict(world='taught-roadmap-context', origin='taught', phase='lesson',
        roadmap_demo=True, methods=shown, seconds=time.perf_counter()-started, experiment=None,
        certified=None, discovered=False, progress=0.))
    return True


def compare_runs(paths):
    from scripts.sera_u_rsi import read
    result = compare_lineage(paths)  # retains U12 metrics and matched scope/tripwire
    result['claim'] = CLAIM
    for path in paths:
        root = Path(path)
        state = read(root/'state.json')
        validate_roadmap(read(root/'observer-discovery.json'))
        latest = {}
        for row in sorted(state.get('discovery_generations', []), key=lambda item: (item['arm'], item['generation'])):
            if 'roadmap' in row:
                latest[row['arm']] = copy.deepcopy(row['roadmap'])
        result['cases'][root.name]['roadmap'] = latest
        result['cases'][root.name]['u13_control'] = not any(state['protocol']['discovery'].get('roadmap', {}).values())
    result['limits'] += (' Cost pairs are bounded own-value searches; solved there is a fit, not world truth. '
        'Pruning gains count audit attempts and recovered mistakes; full A/B measures overall benefit. '
        'Missing/pruned candidates beyond the unchanged bounded fallback are not known truths.')
    return result


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
            raise SystemExit('Roadmap false credit must be zero')
    else:
        if not args.suite:
            parser.error('--suite is required to freeze')
        if Path(args.out).exists():
            raise SystemExit('Freeze once; refusing to overwrite an existing roadmap manifest')
        mind = SeraU.load(args.bootstrap, exact=False) if args.bootstrap else None
        write(args.out, freeze_roadmap(mind, validate_frozen_suite(read(args.suite)), args.seed))


if __name__ == '__main__':
    main()
