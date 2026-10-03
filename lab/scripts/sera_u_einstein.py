"""U10 observer-only frozen Einstein suite and taught-method seam.

Hidden programs, domain samplers and categories stay in this script/manifest.
The learner receives only U9 WorldViews and its own executed observations.
"""
import copy
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sera import lang as LG
from sera_u.ports import digest
from sera_u.sleep import family
from sera_u.discovery import einstein_records
from scripts.sera_u_discovery import freeze, validate

CLAIM = ("A test of whether Einstein's habits of thought help on hidden-law worlds, "
         "not a claim of Einstein's insight.")


def freeze_einstein(mind, suite, seed):
    manifest = freeze(mind, suite, seed)
    excluded = {r['family'] for label in ('retention', 'wake', 'assessment') for r in suite[label]}
    excluded.update(r['family'] for r in manifest['worlds'] if r['form'] == 'exact')
    if mind is not None:
        excluded.update(family(p, concepts) for receipt, concepts in mind.sleep.replay
                        if receipt.origin != 'explore' for p in receipt.targets)
    x = LG.node('var', payload='x')
    square = LG.node('mul', x, x)
    first = LG.node('head', x)
    second = LG.node('head', LG.node('tail', x))
    difference = LG.node('sub', first, second)
    # Observer-designed worlds, NEVER teacher demonstrations or learner labels.
    # Family identities deliberately erase literal magnitudes. Vary acquired-
    # language STRUCTURE rather than pretending a changed offset is disjoint.
    # Neutral nesting preserves the intended world behavior and stays <=40 nodes.
    for depth in range(7):
        offset = 2+seed
        literal = LG.node('lit', payload=offset)
        base = square
        dsq = LG.node('mul', difference, difference)
        for _ in range(depth):
            base = LG.node('add', base, LG.node('zero'))
            dsq = LG.node('add', dsq, LG.node('zero'))
        common = LG.node('add', base, literal)
        extreme = LG.node('if', LG.node('lt', x, LG.node('lit', payload=12)),
                          common, LG.node('add', common, LG.node('one')))
        repaired = LG.node('add', common, LG.node('mul', x, LG.node('lit', payload=offset)))
        frame_a = LG.node('add', dsq, literal)
        frame_b = LG.node('add', LG.node('mul', dsq, literal), LG.node('one'))
        candidates = [(common, 'num', (-6, 7), 'conflict'),
                      (extreme, 'num', (-6, 7), 'conflict'),
                      (repaired, 'num', (12, 25), 'shared-assumption-fails'),
                      (frame_a, 'list', (-8, 9), 'differences'),
                      (frame_b, 'list', (-8, 9), 'differences'),
                      (common, 'num', (-6, 7), 'imagined-extreme'),
                      (extreme, 'num', (-6, 7), 'imagined-extreme')]
        families = {family(p, {}) for p, _, _, _ in candidates}
        if families & excluded:
            continue
        for j, (p, tin, interval, category) in enumerate(candidates):
            manifest['worlds'].append(dict(id='e'+str(j), form='exact', program=p,
                tin=tin, tout='num', family=family(p, {}), seed=seed+10000,
                index=100000+j, audit_range=interval, audit_length=2 if tin == 'list' else None,
                observer_category=category))
        break
    else:
        raise ValueError('No disjoint Einstein suite within frozen structural budget')
    manifest['einstein_suite'] = 'u10-einstein-1'
    manifest['claim'] = CLAIM
    manifest['split'] += '; observer-only conflict scopes, transformed frames and extreme paradoxes; never taught'
    return validate(manifest, suite, mind)


def teach_einstein_once(mind):
    """Demonstrate the four METHOD choices on acquired taught public material.

    No answer program, world label, law, invariant or symmetry is handed in.
    Sufficient statistics then fade. This models a teacher showing a way of
    working; whether SERA uses it productively is the frozen untaught A/B.
    """
    d = mind.discovery
    if d is None or not hasattr(d, 'einstein') or d.einstein.teacher_shown:
        return False
    if getattr(mind, 'progress', {}).get('assessment'):
        raise ValueError('No method teaching during assessment')
    receipt = next((r for r, _ in mind.sleep.replay if r.origin == 'taught'), None)
    if receipt is None:
        return False
    started = time.perf_counter()
    shown = d.einstein.demonstrate(mind, receipt.view, phase='lesson', origin='taught')
    d.einstein.phase('rsi')
    d.events.append(dict(world='taught-method-context', origin='taught', mechanism_demo=True,
        phase='lesson', seconds=time.perf_counter()-started, experiment=None, certified=None,
        discovered=False, shown=shown, einstein_demo=True))
    return True


def report_einstein(generations, judges):
    # Counts are cumulative per arm, not summed again across generations.
    latest = {}
    ordered = sorted(generations, key=lambda r: (r['arm'], r['generation']))
    for row in ordered:
        if 'einstein' in row:
            latest[row['arm']] = copy.deepcopy(row)
    for arm, row in latest.items():
        row['einstein_records'] = einstein_records([r for r in ordered if r['arm'] == arm])
    false = sum(bool(r['false_credit']) for r in judges)
    return dict(claim=CLAIM, arms=latest, false_credit=false, zero_false_credit=not false,
        limit='Finite acquired-language search and probabilistic audits; rank proxies do not establish speed. '
              'Compare seconds/experiments per certified law against discovery and each ablation on the same frozen bytes.')


def compare_runs(paths):
    from scripts.sera_u_rsi import read
    scopes, cases = [], {}
    for path in paths:
        path = Path(path)
        state, report = read(path/'state.json'), read(path/'g_curve.json')
        scopes.append((state.get('suite_sha256'), state.get('discovery_suite_sha256'),
                       state['protocol']['device'], state['protocol']['seed']))
        arms = {}
        generations = report.get('discovery', {}).get('generations', [])
        for arm in sorted({r['arm'] for r in generations}):
            rows = [r for r in generations if r['arm'] == arm]
            latest = max(rows, key=lambda r: r['generation'])
            laws = sum(r['laws'] for r in rows)
            seconds, experiments = sum(r['seconds'] for r in rows), sum(r['experiments'] for r in rows)
            later = [r for r in rows if r['generation'] > 0]
            later_laws = sum(r['laws'] for r in later)
            arms[arm] = dict(laws=laws, seconds=seconds, experiments=experiments,
                seconds_per_law=seconds/laws if laws else None,
                experiments_per_law=experiments/laws if laws else None,
                later_seconds_per_law=sum(r['seconds'] for r in later)/later_laws if later_laws else None,
                later_experiments_per_law=sum(r['experiments'] for r in later)/later_laws if later_laws else None,
                einstein=latest.get('einstein'), principles_sped_later_search=None)
        cases[path.name.removeprefix('u-')] = dict(complete=report['complete'], arms=arms,
            false_credit=report.get('discovery', {}).get('false_credit', 0))
    if not scopes or any(not s[0] or not s[1] for s in scopes) or len(set(scopes)) != 1:
        raise ValueError('Einstein comparison requires identical frozen suites, seed and device')
    full, ablated = cases.get('einstein'), cases.get('einstein-no-symmetry-principles')
    if full and ablated and full['complete'] and ablated['complete']:
        for arm, row in full['arms'].items():
            control = ablated['arms'].get(arm, {})
            a, b = row['later_seconds_per_law'], control.get('later_seconds_per_law')
            if a is not None and b is not None:
                row['principles_sped_later_search'] = a < b
    false = sum(row['false_credit'] for row in cases.values())
    return dict(claim=CLAIM, cases=cases, false_credit=false, zero_false_credit=not false,
        matched_scope=scopes[0],
        speed_scope='Observed later-generation seconds per certified law versus the symmetry ablation; '
                    'not a causal guarantee or a claim about identical discovered laws.')


def main():
    import argparse
    from scripts.sera_u_rsi import read, write, validate_frozen_suite
    from sera_u import SeraU
    ap = argparse.ArgumentParser()
    ap.add_argument('--suite', default=None)
    ap.add_argument('--compare', nargs='+', default=None, help='Completed case folders with state.json and g_curve.json')
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--bootstrap', default=None)
    args = ap.parse_args()
    if args.compare:
        result = compare_runs(args.compare)
        write(args.out, result)
        if not result['zero_false_credit']:
            raise SystemExit('Einstein comparison failed: false credit must be zero')
        return
    if not args.suite:
        ap.error('--suite is required when freezing an observer suite')
    mind = SeraU.load(args.bootstrap, exact=False) if args.bootstrap else None
    suite = validate_frozen_suite(read(args.suite))
    manifest = freeze_einstein(mind, suite, args.seed)
    write(args.out, manifest)
    print(digest(manifest))


if __name__ == '__main__':
    main()
