"""Freeze u14-holes-1 once; private links are observer scoring only."""
import argparse
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sera import lang as LG
from sera_u.discovery import WorldView
from sera_u.sleep import family
from scripts.sera_u_discovery import WorldPool, validate

SCHEMA = 'u14-holes-1'


def freeze_holes(suite, seed, base=None, mind=None):
    manifest = copy.deepcopy(base) if base else dict(schema='u9-discovery-1', seed=seed, worlds=[], dropped=[])
    excluded = {row['family'] for label in ('assessment', 'wake', 'retention') for row in suite[label]}
    if mind is not None:
        excluded.update(f for receipt, _ in mind.sleep.replay if receipt.origin != 'explore'
                        for f in receipt.families)
    x = LG.node('var', payload='x')
    head = LG.node('head', x)
    second = LG.node('head', LG.node('tail', x))
    # Direct measured impulse and speed change: dv=J/m. The collision body
    # measures the contact impulse too, so throws alone are never used to claim
    # mass. Scalars below are reciprocal masses in fixed observer units.
    candidates = []
    for depth in range(8):
        square = LG.node('mul', head, head)
        measured = head
        for _ in range(depth):
            square = LG.node('add', square, LG.node('zero'))
            measured = LG.node('add', measured, LG.node('zero'))
        for scalar in range(2, 32):
            push = LG.node('mul', measured, LG.node('lit', payload=scalar))
            collision = LG.node('add', push, second)
            term = LG.node('add', square, LG.node('lit', payload=scalar))
            domain = LG.node('if', LG.node('lt', head, LG.node('zero')), term,
                             LG.node('add', term, head))
            uncovered = LG.node('mul', LG.node('add', measured, second), LG.node('lit', payload=scalar+1))
            programs = (push, collision, term, square, domain, uncovered)
            if max(map(LG.size, programs)) <= 40 and not {family(p, {}) for p in programs} & excluded:
                candidates.append((scalar, programs))
        if candidates:
            scalar, programs = candidates[0]
            break
    else:
        raise ValueError('No disjoint linked worlds; refuse to teach the observer suite')
    rows = []
    roles = ('direct-push', 'measured-contact-impulse', 'term', 'term-subject', 'region-change', 'uncovered')
    for j, (program, role) in enumerate(zip(programs, roles)):
        rows.append(dict(id='h14-'+str(j), form='exact', program=program, tin='list', tout='num',
            family=family(program, {}), seed=seed+14000, index=140000+j,
            object_ids=['object-'+str(seed)] if j < 2 else [], observer_role=role))
    manifest['worlds'].extend(rows)
    manifest.update(holes_suite=SCHEMA, observer_links=[
        dict(reason='constant', source=rows[0]['id'], target=rows[1]['id'],
             direct_measurement=True, reciprocal_mass=scalar),
        dict(reason='term', source=rows[2]['id'], target=rows[3]['id']),
        dict(reason='failure', source=rows[2]['id'], target=rows[4]['id']),
        dict(reason='uncovered', source=rows[2]['id'], target=rows[5]['id'])],
        claim='Linked frozen sensor/program worlds; direct impulse measurement pins a per-object mass. Not a claim of new physics.')
    return validate(manifest, suite, mind)


class HolesPool(WorldPool):
    def public(self):
        return tuple(WorldView(w.id, w.form, w.tin, w.tout, w.objects, w.sigma,
            tuple(self.specs[w.id].get('object_ids', ()))) for w in super().public())


def report_holes(generations, manifest):
    """Score only recorded questions and certificates; no learner access."""
    results = {}
    for row in sorted(generations, key=lambda r: (r['arm'], r['generation'])):
        holes = row.get('holes')
        if holes is None:
            continue
        found = [r for r in holes['records'] if r['kind'] == 'hole']
        answered = {r['id']: r for r in holes['records'] if r['kind'] == 'hole-answer'}
        links = manifest.get('observer_links', [])
        # To answer a benchmark link the certified answer must occur in its
        # linked target body; an arbitrary repeated integer earns no suite hit.
        certificates = {(r['law'], r['world']) for prior in generations if prior['arm'] == row['arm'] and
                        prior['generation'] <= row['generation']
                        for r in prior.get('admission_records', [])}
        linked = [q for q in found if q['id'] in answered and any(
            q['reason'] == link['reason'] and q['source_world'] == link['source'] and
            (answered[q['id']]['law'], link['target']) in certificates for link in links)]
        results[row['arm']] = dict(generation=row['generation'], holes_found=holes['found'],
            holes_answered=holes['answered'], linked_answers=len(linked), chain_depth=holes['chain_depth'],
            distinct_laws=holes['distinct_laws'], zero_progress_repeat_visits=holes['zero_progress_repeat_visits'])
    return dict(suite=SCHEMA, arms=results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', required=True, help='Frozen observer.json; never passed into SERA')
    parser.add_argument('--base-suite', help='Optional frozen U13 manifest to include the other habits')
    parser.add_argument('--bootstrap', help='Optional existing learned checkpoint to exclude all taught replay families')
    parser.add_argument('--seed', type=int, default=3)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    output = Path(args.out)
    if output.exists():
        raise ValueError('Freeze once: output already exists')
    suite = json.loads(Path(args.suite).read_text(encoding='utf-8'))
    base = json.loads(Path(args.base_suite).read_text(encoding='utf-8')) if args.base_suite else None
    from sera_u import SeraU
    mind = SeraU.carry(args.bootstrap, device='cpu') if args.bootstrap else None
    manifest = freeze_holes(suite, args.seed, base, mind)
    from scripts.sera_u_rsi import write
    write(output, manifest)


if __name__ == '__main__':
    main()
