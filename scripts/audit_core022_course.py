"""Read-only foundation receipt audit, independent of the training libraries.

This uses only the standard library. It never imports the learner, opens a
checkpoint pickle, parses reserved human rows, or changes a worker file. A live
audit reports an observed prefix, not training completion or replay equivalence.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import time


ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ('semantic', 'physics', 'programs', 'pairs', 'reading', 'semantic',
            'physics', 'programs', 'pairs', 'mixed', 'semantic', 'pairs')
TRACKS = ('calculus', 'dailydialog', 'descartes', 'grammar', 'plato', 'programming', 'webster')
TOTAL = 12288
SPLIT_KEY = 'CORE-022-fresh-course-groups-20260921-v1|'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def rank(prefix, value):
    return hashlib.sha256((prefix + value).encode()).hexdigest()


def safe_child(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Referenced file escapes its evidence directory')
    return path


def validate_indices(pools):
    """Check disjoint row allocations without decoding their source text."""
    for kind, roles in pools.items():
        if set(roles) != {'train', 'development', 'final'}:
            raise ValueError('Incomplete allocation roles')
        seen = set()
        for role, tracks in roles.items():
            for indices in tracks.values():
                if any(type(i) is not int or i < 0 for i in indices):
                    raise ValueError('Invalid source row index')
                current = set(indices)
                if len(current) != len(indices) or seen & current:
                    raise ValueError('Duplicate or cross-partition source index: ' + kind + '/' + role)
                seen.update(current)


def expected_layout(pools, cursor):
    if type(cursor) is not int or not 0 <= cursor <= TOTAL:
        raise ValueError('Invalid durable curriculum cursor')
    orders = {}
    for kind in pools:
        for track, indices in pools[kind]['train'].items():
            values = list(indices)
            random.Random(int(rank('CORE-022-order|', kind + '|' + track), 16)).shuffle(values)
            orders[kind + ':' + track] = values
    pairs = [t for t in TRACKS if pools['pairs']['train'].get(t)]
    occurrences = Counter()
    result = []
    needed = defaultdict(set)
    for step in range(cursor):
        kind = SCHEDULE[step % len(SCHEDULE)]
        occurrence = occurrences[kind]
        occurrences[kind] += 1
        batch = 4 if kind in ('reading', 'mixed') else 8
        record = {'cursor': step + 1, 'kind': kind, 'batch': batch}
        if kind == 'physics':
            record['numbers'] = list(range(occurrence * batch, (occurrence + 1) * batch))
        else:
            bank = 'semantic' if kind == 'mixed' else kind
            track = bank
            if kind == 'pairs':
                if not pairs:
                    raise ValueError('No teaching pair subjects')
                track = pairs[occurrence % len(pairs)]
                occurrence //= len(pairs)
            order = orders[bank + ':' + track]
            if not order:
                raise ValueError('Empty scheduled teaching track')
            indices = [order[(occurrence * batch + i) % len(order)] for i in range(batch)]
            record.update(bank=bank, track=track, indices=indices)
            if kind == 'mixed':
                record['numbers'] = list(range(occurrence * batch, (occurrence + 1) * batch))
            needed[bank].update(indices)
        result.append(record)
    return result, needed


def source_metadata(root, manifest, pools, needed):
    """Hash complete source bytes; decode only actually taught source rows."""
    result = {}
    for kind, entry in manifest['files'].items():
        path = safe_child(root, entry['path'])
        if digest(path) != entry['sha256']:
            raise ValueError('Changed frozen source bytes: ' + kind)
        wanted = needed.get(kind, set())
        train = {i for values in pools[kind]['train'].values() for i in values}
        if not wanted <= train:
            raise ValueError('Requested a reserved source row')
        selected = {}
        with path.open('rb') as handle:
            for index, line in enumerate(handle):
                if index not in wanted:
                    continue
                row = json.loads(line)
                group = row.get('group', row.get('source_group'))
                if not group or int(rank(SPLIT_KEY, group)[:8], 16) % 20 < 2:
                    raise ValueError('Teaching contains a reserved source group')
                selected[index] = {'id': row['id'], 'group': group, 'track': row.get('track', kind)}
        if set(selected) != wanted:
            raise ValueError('Missing allocated teaching source row')
        result[kind] = selected
    return result


def receipt_prefix(path, *, limit=None, cursor=None):
    """Read only complete lines up to the fixed saved cursor/byte boundary."""
    rows = []
    hasher = hashlib.sha256()
    consumed = 0
    with path.open('rb') as handle:
        while True:
            if limit is not None and consumed == limit:
                break
            line = handle.readline(-1 if limit is None else limit - consumed)
            if not line:
                break
            if not line.endswith(b'\n'):
                if limit is not None:
                    raise ValueError('Committed receipt boundary is not a complete record')
                break
            row = json.loads(line)
            if cursor is not None and row['cursor'] > cursor:
                break
            rows.append(row)
            hasher.update(line)
            consumed += len(line)
    if limit is not None and consumed != limit:
        raise ValueError('Durable receipt prefix is truncated')
    return rows, {'file': path.name, 'bytes': consumed, 'sha256': hasher.hexdigest()}


def receipt_chain(root, log_name, cursor):
    current = safe_child(root, log_name)
    if current.parent != root.resolve() or not current.name.startswith('updates-') or current.suffix != '.jsonl':
        raise ValueError('Explicit course update log required')
    token = current.stem[len('updates-'):]
    resume = root / ('RESUME-' + token + '.json')
    entries = read(resume)['prior_receipts'] if resume.exists() else []
    rows = []
    prefixes = []
    seen = set()
    for entry in entries:
        if entry['file'] in seen or entry['file'] == current.name:
            raise ValueError('Repeated receipt chain file')
        seen.add(entry['file'])
        part, record = receipt_prefix(safe_child(root, entry['file']), limit=entry['bytes'])
        if record != entry:
            raise ValueError('Previously committed receipt prefix changed')
        rows.extend(part)
        prefixes.append(record)
    part, record = receipt_prefix(current, cursor=cursor)
    rows.extend(part)
    prefixes.append(record)
    if [r['cursor'] for r in rows] != list(range(1, cursor + 1)):
        raise ValueError('Teaching receipt chain skips, reorders or repeats updates')
    return rows, prefixes


def check_rows(layout, metadata, rows):
    if len(layout) != len(rows):
        raise ValueError('Wrong number of completed update receipts')
    counts = Counter()
    unique = defaultdict(set)
    groups = set()
    for expected, row in zip(layout, rows):
        kind = expected['kind']
        if row['cursor'] != expected['cursor'] or row['kind'] != kind:
            raise ValueError('Update differs from the registered subject schedule')
        if kind == 'physics':
            ids = [identity(['CORE-022-physical-teaching', n]) for n in expected['numbers']]
        else:
            sources = [metadata[expected['bank']][i] for i in expected['indices']]
            ids = [s['id'] for s in sources]
            groups.update(s['group'] for s in sources)
            if kind == 'mixed':
                ids = [identity(['CORE-022-mixed-teaching', source_id, n])
                       for source_id, n in zip(ids, expected['numbers'])]
            if kind == 'pairs':
                if any(s['track'] != expected['track'] for s in sources):
                    raise ValueError('Incorrect pair subject in allocated rows')
                counts['pair_subject:' + expected['track']] += len(ids)
            if kind == 'programs':
                counts.update('program_subject:' + s['track'] for s in sources)
        if row['ids'] != ids:
            raise ValueError('Teaching source/order differs at update ' + str(row['cursor']))
        for name in ('loss', 'gradient_norm', 'update_wall_seconds'):
            if type(row[name]) not in (float, int) or not math.isfinite(row[name]):
                raise ValueError('Nonfinite or invalid numerical receipt')
        if row['gradient_norm'] < 0 or row['update_wall_seconds'] < 0:
            raise ValueError('Negative gradient norm or cost')
        counts[kind] += len(ids)
        unique[kind].update(ids)
    return {'presentations': dict(counts), 'distinct_records': {k: len(v) for k, v in unique.items()},
            'distinct_human_source_groups': len(groups),
            'recorded_update_wall_seconds': sum(r['update_wall_seconds'] for r in rows)}


def run(arm, log_name, *, root=ROOT):
    started = time.perf_counter()
    if arm not in ('credited', 'withheld'):
        raise ValueError('Unknown course arm')
    course = root / 'runs/CORE-022/foundation' / arm
    current = read(course / 'CURRENT.json')
    initial = read(course / 'INITIAL.json')
    checkpoint = safe_child(course / 'revisions', current['revision'])
    if checkpoint.name != current['sha256'] + '.pt' or digest(checkpoint) != current['sha256']:
        raise ValueError('Durable checkpoint byte identity changed')
    acceptance = read(root / 'reports/CORE-022/BUILD_ACCEPTANCE.json')
    pinned = acceptance['course_sources']
    if not acceptance['launch_qualified']:
        raise ValueError('Course build was not accepted')
    expected_files = {**pinned['implementation'], 'protocols/CORE-022-FOUNDATION.md': pinned['protocol'],
                      'scripts/train_core022_foundation.py': pinned['driver'],
                      'local/CORE-022-course-v1/MANIFEST.json': pinned['allocation']}
    for relative, expected in expected_files.items():
        if digest(safe_child(root, relative)) != expected:
            raise ValueError('Frozen teaching implementation changed: ' + relative)
    libraries = {p.relative_to(root).as_posix() for p in (root / 'sera_field').glob('*.py')}
    if libraries != set(pinned['implementation']):
        raise ValueError('Frozen library file set changed')
    data = root / 'local/CORE-022-course-v1'
    manifest = read(data / 'MANIFEST.json')
    if manifest['split_key'] != SPLIT_KEY or digest(data / 'INDICES.json') != manifest['indices_sha256']:
        raise ValueError('Frozen source allocation changed')
    pools = read(data / 'INDICES.json')
    validate_indices(pools)
    layout, needed = expected_layout(pools, current['cursor'])
    metadata = source_metadata(root, manifest, pools, needed)
    rows, prefixes = receipt_chain(course, log_name, current['cursor'])
    evidence = check_rows(layout, metadata, rows)
    progress = read(course / 'PROGRESS.json')
    progress_comparable = progress['cursor'] == current['cursor']
    if progress_comparable and progress['exposures'] != evidence['presentations']:
        raise ValueError('Progress presentation counts disagree with actual teaching receipts')
    complete = read(course / 'COMPLETE.json') if (course / 'COMPLETE.json').exists() else None
    completed_at_snapshot = bool(complete and current['cursor'] == TOTAL)
    if completed_at_snapshot and (complete['updates'] != TOTAL or complete['exposures'] != evidence['presentations']
                                  or complete['sources'] != pinned or complete['initial_weights'] != initial['weights']):
        raise ValueError('Completion summary disagrees with independent prefix audit')
    return {'schema': 'sera-field.core022.receipt-audit.1', 'arm': arm,
            'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'cursor': current['cursor'], 'target': TOTAL, 'checkpoint': current,
            'initial_weights': initial['weights'], 'weights_changed': current['weights'] != initial['weights'],
            'receipt_prefixes': prefixes, **evidence, 'progress_same_cursor': progress_comparable,
            'audit_passed': True, 'course_completed_at_snapshot': completed_at_snapshot,
            'reserved_source_rows_parsed': 0, 'model_imports': 0, 'checkpoint_pickles_opened': 0,
            'worker_files_modified': 0, 'whole_behavior_qualified': False,
            'verifier_sha256': digest(Path(__file__)), 'audit_wall_seconds': time.perf_counter() - started,
            'scope': 'Recorded source order, partitions, finite updates and checkpoint bytes; numerical replay is a separate assessment.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arm', choices=('credited', 'withheld'))
    parser.add_argument('--log', required=True, help='Exact updates-<token>.jsonl in the course directory')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / 'local').resolve()):
        raise ValueError('Follow-up audits belong to a fresh local path, outside worker evidence')
    if output.exists():
        raise ValueError('Preserve the previous audit; choose a fresh output path')
    result = run(args.arm, args.log)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({k: result[k] for k in ('arm', 'cursor', 'audit_passed', 'course_completed_at_snapshot',
                                            'presentations', 'reserved_source_rows_parsed', 'audit_wall_seconds')}))


if __name__ == '__main__':
    main()
