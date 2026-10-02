"""Two arms of a paired A/B, compared lesson by lesson and question by question (review 15 F7: totals alone must not
pass a batch). Lessons: every lesson of the teacher's order for the seed - a lesson the off arm proved right and the
on arm did not is LOST, whatever the totals. Talks: the same fresh talk, row by row (the same question in the same
place, or the comparison is refused) - rows the off arm got right and the on arm got wrong, and answers about people
nobody told of ('absent', any answer is wrong), per arm.

  python scripts/ab_compare.py --seed S --off LANG_DIR --on LANG_DIR [--talk-off DIR --talk-on DIR]
      [--physics-off DIR --physics-on DIR] [--out FILE]
The gate prints PASS/FAIL for the requested scope and exits 0/1. Old b1 aggregate files cannot establish talk
identity: both talks must be recorded again with observer digests. Physics needs PHYSICS.json from sera_one.py.
"""
import argparse
import json
import sys
from pathlib import Path

TALK_ARMS = {'taught: the lesson', 'read only: the lesson', 'before: the fresh talk',
             'taught: the fresh talk', 'read only: the fresh talk'}

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def lessons(seed, off, on):
    import sera_language as SL
    names = [n for n, _ in SL.teaching(seed)]
    a = json.loads((Path(off) / 'AB.json').read_text(encoding='utf-8'))['lessons']
    b = json.loads((Path(on) / 'AB.json').read_text(encoding='utf-8'))['lessons']
    right = lambda rows, n: (rows.get(n) or {}).get('verdict') == 'proven right'   # noqa: E731
    return dict(universe=len(names), off=sum(right(a, n) for n in names), on=sum(right(b, n) for n in names),
                lost=[n for n in names if right(a, n) and not right(b, n)],
                gained=[n for n in names if right(b, n) and not right(a, n)],
                missing_on=[n for n in names if n not in b], missing_off=[n for n in names if n not in a],
                wrong=[n for n in names for rows in (a, b) if (rows.get(n) or {}).get('verdict') == 'SURE AND WRONG'])


def talks(off, on):
    paths = [Path(p) / 'CONVERSE.json' for p in (off, on)]
    if any(not p.exists() for p in paths):
        return dict(refused='missing CONVERSE.json and observer digests: saved b1 aggregates cannot verify '
                            'stories and targets; rerun both talks with this recorder')
    a, b = [json.loads(p.read_text(encoding='utf-8')) for p in paths]
    if set(a) != set(b) or set(a) != TALK_ARMS:
        return dict(refused='missing or mismatched talk arm keys',
                    missing_off=sorted(TALK_ARMS - set(a)), missing_on=sorted(TALK_ARMS - set(b)),
                    unexpected_off=sorted(set(a) - TALK_ARMS), unexpected_on=sorted(set(b) - TALK_ARMS))
    out = {}
    for key in sorted(a):
        ra, rb = a[key].get('rows') or [], b[key].get('rows') or []
        if any(not r.get('observer_digest') for r in ra + rb):
            out[key] = dict(refused='missing observer digests: saved b1 talks cannot verify stories and targets; '
                                   'rerun both talks with this recorder')
            continue
        if (not ra or len(ra) != len(rb)
                or any((x['observer_digest'], x['kind'], x['question']) !=
                       (y['observer_digest'], y['kind'], y['question']) for x, y in zip(ra, rb))):
            out[key] = dict(refused='the two talks have different question/story/target identities or kinds')
            continue
        out[key] = dict(n=len(ra), off=sum(r['right'] for r in ra), on=sum(r['right'] for r in rb),
                        lost=[i for i, (x, y) in enumerate(zip(ra, rb)) if x['right'] and not y['right']],
                        gained=[i for i, (x, y) in enumerate(zip(ra, rb)) if y['right'] and not x['right']],
                        absent_answered_off=sum(r['kind'] == 'absent' and r['said'] is not None for r in ra),
                        absent_answered_on=sum(r['kind'] == 'absent' and r['said'] is not None for r in rb),
                        absent=sum(r['kind'] == 'absent' for r in ra))
    return out


def physics(off, on):
    paths = [Path(p) / 'PHYSICS.json' for p in (off, on)]
    if any(not p.exists() for p in paths):
        return dict(refused='missing PHYSICS.json; rerun physics summaries with this recorder')
    a, b = [json.loads(p.read_text(encoding='utf-8')) for p in paths]
    stages = {'teach', 'alone', 'twin'}
    if set(a.get('groups', {})) != stages or set(b.get('groups', {})) != stages:
        return dict(refused='missing or mismatched physics stages')

    def indexed(result):
        rows = result.get('units')
        if rows is None:
            raise ValueError('missing physics unit identities')
        out = {}
        for row in rows:
            key = (row['stage'], row['task'], row['subject'], row['form'])
            if key in out:
                raise ValueError('duplicate physics unit identity')
            out[key] = row
        return out

    try:
        ra, rb = indexed(a), indexed(b)
    except (KeyError, ValueError) as exc:
        return dict(refused=str(exc))
    if not ra or set(ra) != set(rb):
        return dict(refused='missing or mismatched physics worlds',
                    missing_on=[list(k) for k in sorted(set(ra) - set(rb))],
                    missing_off=[list(k) for k in sorted(set(rb) - set(ra))])
    groups = {}
    for stage in sorted(stages):
        ga, gb = a['groups'][stage], b['groups'][stage]
        if set(ga) != set(gb) or set(ga) != {'worlds', 'curves_proven', 'drawings_proven', 'formulas_proven'}:
            return dict(refused='missing or mismatched PHYSICS PROVEN counters')
        groups[stage] = dict(off=ga, on=gb, delta={k: gb[k] - ga[k] for k in sorted(ga)},
                             lost=[k[1] for k in sorted(ra) if k[0] == stage and ra[k]['proven']
                                   and (not rb[k]['proven'] or rb[k].get('verdict') != 'proven right')],
                             gained=[k[1] for k in sorted(ra) if k[0] == stage and rb[k]['proven']
                                     and not ra[k]['proven']])
    return groups


def gate(result):
    """A refusal or missing observation cannot pass the no-lesson-or-answer-lost gate."""
    reasons = []

    def inspect(value, path):
        if isinstance(value, dict):
            for key, item in value.items():
                if (key == 'refused' and item) or (key in ('lost', 'missing_on', 'missing_off', 'wrong') and item):
                    reasons.append(f'{path}.{key}: {item}')
                elif isinstance(item, dict):
                    inspect(item, f'{path}.{key}')

    for name in ('lessons', 'talks', 'physics'):
        if name in result:
            inspect(result[name], name)
    return dict(name='no lesson or answer lost', verdict='FAIL' if reasons else 'PASS',
                scope=[k for k in ('lessons', 'talks', 'physics') if k in result], reasons=reasons)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--off', required=True)
    ap.add_argument('--on', required=True)
    ap.add_argument('--talk-off')
    ap.add_argument('--talk-on')
    ap.add_argument('--physics-off', help='physics run containing PHYSICS.json')
    ap.add_argument('--physics-on')
    ap.add_argument('--out')
    a = ap.parse_args()
    for name in ('talk', 'physics'):
        if bool(getattr(a, name + '_off')) != bool(getattr(a, name + '_on')):
            ap.error(f'--{name}-off and --{name}-on must be supplied together')
    res = dict(seed=a.seed, lessons=lessons(a.seed, a.off, a.on))
    if a.talk_off and a.talk_on:
        res['talks'] = talks(a.talk_off, a.talk_on)
    elif any((Path(p) / 'CONVERSE.json').exists() for p in (a.off, a.on)):
        res['talks'] = talks(a.off, a.on)
    elif any('ab-b1' in Path(p).parts for p in (a.off, a.on)):
        res['talks'] = dict(refused='saved b1 files lack observer digests; their question-only or aggregate '
                                   'talk comparisons cannot certify matching stories and targets')
    if a.physics_off and a.physics_on:
        res['physics'] = physics(a.physics_off, a.physics_on)
    elif any((Path(p) / 'PHYSICS.json').exists() for p in (a.off, a.on)):
        res['physics'] = physics(a.off, a.on)
    res['gate'] = gate(res)
    text = json.dumps(res)
    if a.out:
        Path(a.out).write_text(text + '\n', encoding='utf-8')
    print('AB COMPARE', text, flush=True)
    print('GATE no lesson or answer lost:', res['gate']['verdict'], flush=True)
    return 0 if res['gate']['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
