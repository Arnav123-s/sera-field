"""S25: contrastive rail teaching and autonomous revisits, with cloned-snapshot timings.

No policy changes. Seeds 1-3 are development only. A retention manifest freezes old lessons:
{"pre_field_sha256": "...", "lessons": [{"seed": 1, "source": "teaching",
 "name": "rail: wind 1", "input_sha256": "original initial-input digest"}, ...]}.
Include every proven task in the pre-Field's log, with its original builder parameters and digest.
The source/name pair uses sera_one's existing builders; custom rail descriptors instead use
{seed, index, family, level, name}. All identity comparisons use complete nested keys.
Without a complete retention manifest the verdict is INCOMPLETE, never PASS.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
KINDS = {'wind': ((('nothing', 'steady'),), 1),
         'spring': ((('position', 'straight'),), 1),
         'ripple': ((('position', 'wave'),), 1),
         'stiff': ((('position', 'cubic'),), 1)}
OUTCOMES = ('helpful_reuse_retained', 'harmful_transfer_reduced',
            'no_negative_uncertainty', 'old_lessons_retained')


def freeze(value):
    return tuple(freeze(v) for v in value) if isinstance(value, (tuple, list)) else value


def identity(item):
    return freeze(item.get('content_identity', item.get('terminal_identity', item.get('identity'))))


def verdict(outcomes):
    """A witnessed violation wins over censoring; absence of evidence never passes."""
    states = [outcomes.get(k, 'INCOMPLETE') for k in OUTCOMES]
    if 'FAIL' in states:
        return 'FAIL'
    return 'PASS' if all(s == 'PASS' for s in states) else 'INCOMPLETE'


def right(row):
    return row.get('status') == 'done' and row.get('unit', {}).get('verdict') == 'proven right'


def selected(row):
    return {identity(i): i for i in row.get('ring', {}).get('selected', [])}


def refuted(row):
    return {identity(e) for e in row.get('ring', {}).get('events', [])
            if e['event'] == 'refuted' and e.get('reason') in ('input', 'misfit', 'teacher')}


def attempts(row, key):
    return sum(e['event'] == 'attempted' and identity(e) == key
               for e in row.get('ring', {}).get('events', []))


def credited(row):
    obj = row.get('ring', {}).get('credited_object') or {}
    if not right(row) or not obj.get('credited'):
        return set()
    # A curve accepted after a refused formula cannot establish helpful formula reuse.
    amounts = {identity(w) for w in obj.get('amounts', []) if w['amount'] > 0}
    return set(selected(row)) & amounts


def evaluate(rows, pairs, retention_pairs, retention_complete):
    """Pure evidence gate, also usable with short stubs. Details retain every lost/opportunity item."""
    outcomes = dict.fromkeys(OUTCOMES, 'INCOMPLETE')
    details = dict(helpful=[], harmful=[], unjustified_negative=[], retention=[], uncertainty=[])
    available = [r for r in rows.values() if r.get('status') in ('done', 'capped') and r.get('ring')]
    for row in available:
        real = refuted(row)
        for write in row['ring'].get('writes', []):
            if write['amount'] < 0 and identity(write) not in real:
                details['unjustified_negative'].append(dict(world=row['id'], write=write))
        for e in row['ring'].get('events', []):
            if (e['event'] == 'judge_result' and not e.get('accepted') and identity(e) not in real
                    and isinstance(e.get('band'), (float, int)) and isinstance(e.get('eps'), (float, int))
                    and e['band'] > e['eps'] and 'something else is here' not in (e.get('reason') or '')):
                details['uncertainty'].append(dict(world=row['id'], identity=e.get('identity'),
                                                   reason=e.get('reason')))
    if details['unjustified_negative']:
        outcomes['no_negative_uncertainty'] = 'FAIL'
    elif details['uncertainty'] and len(available) == len(rows):
        outcomes['no_negative_uncertainty'] = 'PASS'

    for before_id, after_id, teach_ids in pairs:
        before, after = rows[before_id], rows[after_id]
        trained_negative = set().union(*(refuted(rows[t]) for t in teach_ids))
        trained_positive = set().union(*(credited(rows[t]) for t in teach_ids))
        for key in sorted(credited(before) & trained_positive, key=repr):
            details['helpful'].append(dict(before=before_id, after=after_id, identity=key,
                                            retained=key in credited(after), complete=right(after)))
        # It must really have rung, been refuted, and received contrastive teaching evidence.
        for key in sorted(set(selected(before)) & refuted(before) & trained_negative, key=repr):
            old, new = attempts(before, key), attempts(after, key)
            old_led = selected(before)[key].get('led', False)
            new_led = selected(after).get(key, {}).get('led', False)
            details['harmful'].append(dict(before=before_id, after=after_id, identity=key,
                before_attempts=old, after_attempts=new, before_led=old_led, after_led=new_led,
                reduced=new < old or (old_led and not new_led), complete=right(before) and right(after)))
    for label, items, flag in (('helpful_reuse_retained', details['helpful'], 'retained'),
                                ('harmful_transfer_reduced', details['harmful'], 'reduced')):
        if any(i['complete'] and not i[flag] for i in items):
            outcomes[label] = 'FAIL'
        elif items and all(i['complete'] and i[flag] for i in items):
            outcomes[label] = 'PASS'

    for before_id, after_id in retention_pairs:
        before, after = rows[before_id], rows[after_id]
        same = before.get('input_sha256') == after.get('input_sha256') and bool(before.get('input_sha256'))
        details['retention'].append(dict(before=before_id, after=after_id, same_input=same,
                                         baseline_right=right(before), retained=right(after)))
    if any(i['same_input'] and i['baseline_right'] and not i['retained'] and
           rows[i['after']].get('status') in ('done', 'capped') for i in details['retention']):
        outcomes['old_lessons_retained'] = 'FAIL'
    elif retention_complete and details['retention'] and all(
            i['same_input'] and i['baseline_right'] and i['retained'] for i in details['retention']):
        outcomes['old_lessons_retained'] = 'PASS'

    # Any incorrect accepted certificate fails even if it did not concern a selected rung thought.
    wrong = [r['id'] for r in available if r['unit'].get('verdict') == 'SURE AND WRONG']
    details['sure_and_wrong'] = wrong
    if wrong:
        outcomes['helpful_reuse_retained'] = 'FAIL'
    # An unfinished scheduled world cannot hide behind unrelated positive witnesses.
    if len(available) != len(rows) or any(r.get('status') != 'done' for r in rows.values()):
        outcomes = {k: 'INCOMPLETE' if s == 'PASS' else s for k, s in outcomes.items()}
    return dict(verdict=verdict(outcomes), outcomes=outcomes, evidence=details)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=1, allow_nan=False) + '\n', encoding='utf-8')


def validate_spec(spec):
    if spec.get('seed') not in (1, 2, 3):
        raise ValueError('only development seeds 1-3 are allowed')
    if 'source' in spec and spec['source'] not in ('teaching', 'alone'):
        raise ValueError('retention source must be teaching or alone')


def build_world(spec, teaching):
    import numpy as np
    from ccops5.core import grammar
    from sera import tasks as TS, talk as TK
    validate_spec(spec)
    if 'source' in spec:
        from scripts.sera_one import teaching as taught, alone
        builders = dict((taught if spec['source'] == 'teaching' else alone)(spec['seed']))
        if spec['name'] not in builders:
            raise ValueError(f'unknown frozen lesson: {spec["name"]}')
        task = builders[spec['name']]()
        if not teaching:
            task.words = []
            # Exact worlds' teacher-only worked steps are not autonomous observations.
            if hasattr(task, '_worked'):
                task._worked = {}
            if hasattr(task, '_worked_of'):
                task._worked_of = {}
        return task
    family = freeze(spec['family'])
    w, signs = TS.rail_world(spec['seed'], spec['index'], family, spec.get('level', 1))
    words = (TK.teacher_tokens(grammar.canonical(family), signs,
                               np.random.default_rng([spec['seed'], 17, spec['index']])) if teaching else ())
    return TS.Rail(w, spec['name'], words, signs)


def input_digest(task):
    from sera.one import _ring_safe
    if task.form == 'strengths':
        from ccops5.core import truth
        return truth.digest(task.throws)
    # Include the full examples and input/output signatures, not just question text.
    payload = dict(data=task.data, inputs=task.inputs, out=task.out)
    return hashlib.sha256(json.dumps(_ring_safe(payload), sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def worker(job_path):
    # Imports/environment live only in a fresh child, before any world/vocabulary is made.
    os.environ.setdefault('CCOPS5_SHAPES', 'library')
    os.environ.setdefault('CCOPS5_CLAIM', 'functional')
    os.environ.setdefault('CCOPS5_BAND', 'claim')
    sys.path.insert(0, str(ROOT))
    from sera import dictionary as DICT, one as ONE, phi as PH, talk as TK
    from scripts.sera_one import unit_of
    job = json.loads(Path(job_path).read_text(encoding='utf-8'))
    if not ONE.ONE_FIELD or not PH.FIELD_ECHO:
        raise ValueError('diagnostic requires ONE_FIELD=1 and FIELD_ECHO enabled')
    if ONE.RING_MOST != 3:
        raise ValueError('diagnostic requires unchanged RING_MOST=3')
    TK.BOOK = DICT.load(job.get('book'))
    field = PH.Field.load(job['snapshot'])
    task = build_world(job['spec'], job['teaching'])
    digest = input_digest(task)
    if job['spec'].get('input_sha256') and job['spec']['input_sha256'] != digest:
        raise ValueError('frozen old lesson does not match its original input digest')
    ONE.MAX_WALL = job['seconds']
    mind = ONE.Sera(job['mind_seed'], field)
    t0 = time.monotonic()
    rec = mind.live(task, teaching=job['teaching'], ring_log=job['ring_path'])
    # Save/reload is exercised by every subsequent job. The observer never enters this pickle.
    mind.field.save(job['saved_field'])
    result = dict(id=job['id'], status='done' if rec['proven'] else 'capped', spec=job['spec'], teaching=job['teaching'],
                  snapshot_sha256=sha256(job['snapshot']), saved_field_sha256=sha256(job['saved_field']),
                  input_sha256=digest, process_seconds=time.monotonic() - t0,
                  unit=unit_of(rec), ring=rec['ring_observer'])
    write_json(job['result'], result)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--worker', help=argparse.SUPPRESS)
    ap.add_argument('--field', help='trusted saved pre-world Field pickle')
    ap.add_argument('--out')
    ap.add_argument('--retention-manifest')
    ap.add_argument('--seeds', default='1,2,3')
    ap.add_argument('--mind-seed', type=int, choices=(1, 2, 3), default=1)
    ap.add_argument('--world-seconds', type=float, default=120)
    ap.add_argument('--wall-seconds', type=float, default=9000)
    ap.add_argument('--book')
    args = ap.parse_args()
    if args.worker:
        worker(args.worker)
        return 0
    if not args.field or not args.out:
        ap.error('--field and --out are required')
    seeds = [int(s) for s in args.seeds.split(',')]
    if not seeds or len(set(seeds)) != len(seeds) or any(s not in (1, 2, 3) for s in seeds):
        ap.error('use distinct dev seeds 1-3 only')
    if not (0 < args.world_seconds <= 1800 and 0 < args.wall_seconds <= 9600):
        ap.error('world budget must be 0..1800 seconds, total budget 0..9600 seconds')
    out = Path(args.out).resolve()
    if out.exists():
        ap.error('output already exists; diagnostic never resumes or overwrites a run')
    field_path = Path(args.field).resolve()
    if not field_path.is_file():
        ap.error('pre-world Field does not exist')
    retention = (json.loads(Path(args.retention_manifest).read_text(encoding='utf-8'))
                 if args.retention_manifest else {})
    lessons = retention.get('lessons', [])
    for spec in lessons:
        validate_spec(spec)
    original_hash = sha256(field_path)
    if retention and retention.get('pre_field_sha256') != original_hash:
        ap.error('retention manifest must be bound to this exact pre-Field sha256')
    out.mkdir()
    for directory in ('units', 'jobs', 'snapshots', 'logs'):
        (out / directory).mkdir()
    pre = out / 'snapshots' / 'pre.pkl'
    shutil.copyfile(field_path, pre)
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', NUMBA_NUM_THREADS='1',
               CCOPS5_SHAPES='library', CCOPS5_CLAIM='functional', CCOPS5_BAND='claim')
    # Replace only the ONE_FIELD override; leave all other effective knobs captured in each unit.
    knobs = [k for k in env.get('SERA_KNOBS', '').split(',') if k and not k.startswith('ONE_FIELD=')]
    env['SERA_KNOBS'] = ','.join(knobs + ['ONE_FIELD=1'])
    start = time.monotonic()
    deadline = start + args.wall_seconds
    rows, pairs, retention_pairs, jobs = {}, [], [], []

    def run(tag, snapshot, spec, teaching):
        # Never shorten one member of a matched pair to fit the remaining life budget.
        enough = deadline - time.monotonic() >= args.world_seconds + 30
        job = dict(id=tag, snapshot=str(snapshot), spec=spec, teaching=teaching,
                   mind_seed=args.mind_seed, book=args.book,
                   seconds=args.world_seconds if enough else 0,
                   ring_path=str(out / 'units' / f'{tag}.ring.jsonl'),
                   saved_field=str(out / 'snapshots' / f'{tag}.pkl'), result=str(out / 'units' / f'{tag}.json'))
        jobs.append(job)
        row = dict(id=tag, status='not_reached', spec=spec, teaching=teaching)
        if job['seconds'] > 0:
            write_json(out / 'jobs' / f'{tag}.json', job)
            print(f'{tag}: teach={teaching}, cap={job["seconds"]:.1f}s', flush=True)
            with open(out / 'logs' / f'{tag}.log', 'w', encoding='utf-8') as log:
                try:
                    child = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker',
                                            str(out / 'jobs' / f'{tag}.json')], env=env, cwd=ROOT,
                                           stdout=log, stderr=subprocess.STDOUT,
                                           timeout=min(job['seconds'] + 30, max(0.01, deadline - time.monotonic())))
                    if child.returncode == 0 and Path(job['result']).exists():
                        row = json.loads(Path(job['result']).read_text(encoding='utf-8'))
                    else:
                        row.update(status='error', returncode=child.returncode)
                except subprocess.TimeoutExpired:
                    row['status'] = 'censored'
        rows[tag] = row
        if not row.get('ring'):
            write_json(job['result'], row)
        else:
            with open(out / 'ring.jsonl', 'a', encoding='utf-8') as stream:
                stream.write(json.dumps(dict(row['ring'], run_id=tag), allow_nan=False) + '\n')
        return Path(job['saved_field']) if row.get('ring') else None

    # Read the trusted snapshot in a fresh process too; don't import lab globals in the coordinator.
    # The audit job stores the prior successful names and proves that the pickle is loadable.
    audit_code = ("import json,sys; from sera import phi as P; f=P.Field.load(sys.argv[1]); "
                  "json.dump(sorted({r['task'] for r in f.log if r.get('proven')}),"
                  "open(sys.argv[2],'w',encoding='utf-8'))")
    audit_ok = False
    try:
        subprocess.run([sys.executable, '-c', audit_code, str(pre), str(out / 'old-lessons.json')],
                       cwd=ROOT, env=env, check=True, timeout=min(30, args.wall_seconds))
        audit_ok = True
    except (subprocess.SubprocessError, OSError):
        pass
    old_names = json.loads((out / 'old-lessons.json').read_text(encoding='utf-8')) if audit_ok else []
    retention_complete = (bool(retention and audit_ok and old_names) and
                          set(old_names) <= {s['name'] for s in lessons} and
                          all(isinstance(s.get('input_sha256'), str) and s['input_sha256'] for s in lessons))
    for seed in seeds:
        snapshot, teach_ids = pre, []
        teaching_ok = audit_ok
        # Wind first reproduces the direction of S16's wind -> spring interference opportunity.
        for i, (kind, (family, level)) in enumerate(KINDS.items()):
            tag = f's{seed}-teach-{kind}'
            spec = dict(seed=seed, index=810000 + 100 * i, family=family, level=level,
                        name=f'rail: diagnostic {kind} teach seed {seed}')
            if teaching_ok:
                saved = run(tag, snapshot, spec, True)
                teaching_ok = saved is not None
                if saved is not None:
                    snapshot = saved
            else:
                rows[tag] = dict(id=tag, status='not_reached', spec=spec, teaching=True)
            teach_ids.append(tag)
        post = snapshot if teaching_ok else None
        for i, (kind, (family, level)) in enumerate(KINDS.items()):
            spec = dict(seed=seed, index=820000 + 100 * i, family=family, level=level,
                        name=f'rail: diagnostic {kind} revisit seed {seed}')
            a, b = f's{seed}-before-{kind}', f's{seed}-after-{kind}'
            run(a, pre, spec, False)
            if post is not None:
                run(b, post, spec, False)
            else:
                rows[b] = dict(id=b, status='not_reached', spec=spec, teaching=False)
            pairs.append((a, b, [f's{seed}-teach-{kind}']))
        for i, spec in enumerate(lessons):
            a, b = f's{seed}-old-before-{i}', f's{seed}-old-after-{i}'
            run(a, pre, spec, False)
            if post is not None:
                run(b, post, spec, False)
            else:
                rows[b] = dict(id=b, status='not_reached', spec=spec, teaching=False)
            retention_pairs.append((a, b))
    result = evaluate(rows, pairs, retention_pairs, retention_complete)
    # Verify identity of each generated matched situation, even when neither arm found a rung opportunity.
    mismatched = [(a, b) for a, b, _ in pairs if rows[a].get('status') == rows[b].get('status') == 'done'
                  and rows[a]['input_sha256'] != rows[b]['input_sha256']]
    result['input_mismatches'] = mismatched
    if mismatched or sha256(pre) != original_hash or sha256(field_path) != original_hash:
        result['outcomes']['old_lessons_retained'] = 'FAIL'
        result['verdict'] = verdict(result['outcomes'])
    result.update(pre_field_sha256=original_hash, dev_seeds=seeds, retention_complete=retention_complete,
                  old_lesson_names=old_names, wall_seconds=time.monotonic() - start,
                  uncovered_old_lessons=sorted(set(old_names) - {s['name'] for s in lessons}),
                  scope='dev contrastive rails and frozen logged old lessons; not a deployment gate',
                  timing=[dict(world=tag, status=row['status'], snapshot_sha256=row.get('snapshot_sha256'),
                               input_sha256=row.get('input_sha256'), costs=row.get('ring', {}).get('costs'),
                               process_seconds=row.get('process_seconds')) for tag, row in rows.items()])
    write_json(out / 'manifest.json', dict(jobs=jobs, pairs=pairs, retention_pairs=retention_pairs,
                                         retention=retention, environment={k: env.get(k) for k in (
                                             'SERA_KNOBS', 'SERA_CRUTCH_OFF', 'PYTHONHASHSEED',
                                             'CCOPS5_SHAPES', 'CCOPS5_CLAIM', 'CCOPS5_BAND')}))
    write_json(out / 'diagnostic.json', result)
    summary = '\n'.join([result['verdict']] + [f'{k}: {result["outcomes"][k]}' for k in OUTCOMES] +
                        [f'{r["id"]}: {r["status"]}, wall={r.get("ring", {}).get("costs", {}).get("wall")}, '
                         f'cpu={r.get("ring", {}).get("costs", {}).get("cpu")}, '
                         f'phases={r.get("ring", {}).get("costs", {}).get("phases", {})}'
                         for r in rows.values()]) + '\n'
    (out / 'summary.txt').write_text(summary, encoding='utf-8')
    print(summary, flush=True)
    return {'PASS': 0, 'FAIL': 1, 'INCOMPLETE': 2}[result['verdict']]


if __name__ == '__main__':
    raise SystemExit(main())
