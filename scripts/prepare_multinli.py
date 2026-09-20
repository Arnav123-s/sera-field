"""Create immutable human source views; no model import, inference or training."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import time
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'entailment': 0, 'contradiction': 1, 'neutral': 2}
PARTS = {'train': 'multinli_1.0/multinli_1.0_train.jsonl',
         'sealed_matched': 'multinli_1.0/multinli_1.0_dev_matched.jsonl',
         'sealed_mismatched': 'multinli_1.0/multinli_1.0_dev_mismatched.jsonl'}


def normalized(text):
    return ' '.join(unicodedata.normalize('NFKC', text).casefold().split())


def identity(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for piece in iter(lambda: handle.read(1048576), b''): result.update(piece)
    return result.hexdigest()


def records(archive, part):
    with archive.open(PARTS[part]) as handle:
        for line_number, line in enumerate(handle, 1):
            row = json.loads(line)
            if not isinstance(row.get('sentence1'), str) or not isinstance(row.get('sentence2'), str):
                raise ValueError('Unexpected original human sentence representation')
            yield line_number, row


def main():
    started, cpu = time.perf_counter(), time.process_time()
    output = ROOT / 'local/HUMAN-GENRE-data-v1'
    if output.exists():
        raise ValueError('Preserve the existing preparation; use its manifest rather than overwriting')
    output.mkdir(parents=True)
    report_root = ROOT / 'reports/SOURCE_INTAKE'; report_root.mkdir(parents=True, exist_ok=True)
    attempt = report_root / ('MULTINLI-VIEWS-attempt-' + str(time.time_ns()) + '.json')
    status = {'status': 'RUNNING', 'work_kind': 'stdlib source views; no model work',
        'started_unix': time.time(), 'output': 'local/HUMAN-GENRE-data-v1'}
    attempt.write_text(json.dumps(status, indent=2), encoding='utf-8')
    try:
        archive_path = ROOT / 'data/raw/multinli_1.0.zip'
        archive_sha = file_hash(archive_path)
        intake = json.loads((report_root / 'MULTINLI-1.0.json').read_text())
        if archive_sha != intake['sha256']:
            raise ValueError('The preserved original corpus identity changed')
        previous = ROOT / 'local/SEMANTIC-015-data-v1'
        previous_manifest = json.loads((previous / 'MANIFEST.json').read_text())
        old_groups = set(); prior_views = {}
        for split in ('train', 'development', 'sealed'):
            path = previous / (split + '.jsonl'); prior_views[split] = file_hash(path)
            if prior_views[split] != previous_manifest['views'][path.name]['sha256']:
                raise ValueError('A previously qualified human source view changed')
            with path.open(encoding='utf-8') as handle:
                for line in handle:
                    row = json.loads(line); old_groups.add(identity(normalized(row['premise'])))
        reserved = {}; labels_by_pair = defaultdict(set); raw_counts = Counter()
        with zipfile.ZipFile(archive_path) as archive:
            # Metadata pass over all labels is solely an annotation-consistency
            # check; no model output or learner selection participates.
            for part in PARTS:
                for _, row in records(archive, part):
                    group = identity(normalized(row['sentence1']))
                    key = identity(group + '|' + normalized(row['sentence2']))
                    raw_counts[part] += 1
                    if part != 'train':
                        reserved[group] = part  # Mismatched is visited last.
                    if row.get('gold_label') in LABELS:
                        labels_by_pair[key].add(row['gold_label'])
            conflicting = {key for key, labels in labels_by_pair.items() if len(labels) > 1}
            counts = Counter(); exclusions = Counter(); genres = defaultdict(Counter)
            labels = defaultdict(Counter); groups = defaultdict(set); seen = defaultdict(set)
            handles = {part: (output / (part + '.jsonl')).open('x', encoding='utf-8')
                       for part in ('train', 'development', 'sealed_matched', 'sealed_mismatched')}
            excluded = (output / 'EXCLUSIONS.jsonl').open('x', encoding='utf-8')
            try:
                for original in PARTS:
                    for line_number, row in records(archive, original):
                        group = identity(normalized(row['sentence1']))
                        pair_key = identity(group + '|' + normalized(row['sentence2']))
                        source_id = identity('|'.join((archive_sha, PARTS[original], str(line_number), str(row['pairID']))))
                        part = original; reason = None; label = row.get('gold_label')
                        if original == 'train':
                            part = 'development' if int(identity('SERA-human-genre-v1|' + group), 16) % 20 == 0 else 'train'
                        if label not in LABELS: reason = 'no_consensus_label'
                        elif group in old_groups: reason = 'previous_SNLI_premise'
                        elif pair_key in conflicting: reason = 'conflicting_human_pair_labels'
                        elif original == 'train' and group in reserved: reason = 'released_evaluation_premise'
                        elif original != 'train' and reserved[group] != original: reason = 'other_released_evaluation_partition'
                        elif pair_key in seen[part]: reason = 'duplicate_text_and_label'
                        if reason:
                            exclusions[reason] += 1
                            excluded.write(json.dumps({'id': source_id, 'pairID': row['pairID'], 'member': PARTS[original],
                                'line': line_number, 'reason': reason, 'source_group': group}) + '\n')
                            continue
                        seen[part].add(pair_key); groups[part].add(group)
                        view = {'id': source_id, 'source_group': group, 'pairID': row['pairID'],
                            'promptID': row.get('promptID'), 'genre': row['genre'],
                            'premise': row['sentence1'], 'hypothesis': row['sentence2'], 'target': LABELS[label],
                            'original_label': label, 'annotator_labels': row.get('annotator_labels', []),
                            'source_member': PARTS[original], 'source_line': line_number, 'source_archive': archive_sha}
                        handles[part].write(json.dumps(view, ensure_ascii=False) + '\n')
                        counts[part] += 1; genres[part][row['genre']] += 1; labels[part][label] += 1
            finally:
                excluded.close()
                for handle in handles.values(): handle.close()
        partitions = {}
        for part in handles:
            group_path = output / (part + '-groups.json')
            group_path.write_text(json.dumps(sorted(groups[part])), encoding='utf-8')
            partitions[part] = {'rows': counts[part], 'groups': len(groups[part]),
                'genres': dict(genres[part]), 'labels': dict(labels[part]),
                'sha256': file_hash(output / (part + '.jsonl')), 'group_sha256': file_hash(group_path)}
        overlaps = {a + ':' + b: len(groups[a] & groups[b]) for i, a in enumerate(handles) for b in list(handles)[i+1:]}
        if any(overlaps.values()): raise ValueError('A normalized premise crossed source partitions')
        manifest = {'archive_sha256': archive_sha, 'producer_sha256': file_hash(Path(__file__)),
            'protocol_sha256': file_hash(ROOT / 'protocols/HUMAN-GENRE-SOURCE.md'),
            'prior_manifest_sha256': file_hash(previous / 'MANIFEST.json'), 'prior_views': prior_views,
            'partitions': partitions, 'raw_counts': dict(raw_counts), 'exclusions': dict(exclusions),
            'exclusions_sha256': file_hash(output / 'EXCLUSIONS.jsonl'), 'group_overlaps': overlaps,
            'labels': LABELS, 'human_source': intake['attribution'], 'source_page': intake['original_source_page'],
            'license_scope': intake['license_scope'], 'model_predictions_opened': False,
            'costs': {'wall_seconds': time.perf_counter()-started, 'cpu_seconds': time.process_time()-cpu}}
        (output / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        (report_root / 'MULTINLI-VIEWS.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        status.update(status='PASS', manifest_sha256=file_hash(output / 'MANIFEST.json'), counts=dict(counts))
    except BaseException as error:
        status.update(status='FAILED', error=repr(error)); raise
    finally:
        status.update(wall_seconds=time.perf_counter()-started, cpu_seconds=time.process_time()-cpu)
        attempt.write_text(json.dumps(status, indent=2), encoding='utf-8')
        print(json.dumps(status), flush=True)


if __name__ == '__main__':
    main()
