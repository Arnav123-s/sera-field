"""Stream original human SNLI records into immutable, source-grouped local views.

No test outcomes are printed or used for model selection. Raw source bytes remain
unchanged. Dataset views are CC BY-SA 4.0, attributed separately from project code.
"""
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import shutil
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/snli_1.0.zip'
OUT = ROOT / 'local/SEMANTIC-015-data-v1'
URL = 'https://nlp.stanford.edu/projects/snli/snli_1.0.zip'
LABELS = {'entailment': 0, 'contradiction': 1, 'neutral': 2}


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(2**20), b''):
            result.update(block)
    return result.hexdigest()


def rows(archive, split):
    with archive.open('snli_1.0/snli_1.0_' + split + '.jsonl') as raw:
        for line in io.TextIOWrapper(raw, encoding='utf-8'):
            yield json.loads(line)


def group(row):
    return row['captionID'].split('#')[0]


def main():
    if (OUT / 'MANIFEST.json').exists():
        print('Preserved completed intake: ' + str(OUT))
        return
    start = time.monotonic(); cpu = time.process_time()
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if not RAW.exists():
        temporary = RAW.with_suffix('.download')
        if temporary.exists():
            raise ValueError('Preserve and reconcile the partial download before retrying')
        request = urllib.request.Request(URL, headers={'User-Agent': 'SERA-Field-research-source-intake'})
        with urllib.request.urlopen(request, timeout=90) as response, temporary.open('xb') as handle:
            shutil.copyfileobj(response, handle, length=2**20)
        temporary.rename(RAW)
    if OUT.exists():
        raise ValueError('Preserve incomplete intake; use its exact resume/reconciliation')
    OUT.mkdir(parents=True)
    counts, excluded = Counter(), Counter()
    groups = {split: set() for split in ('train', 'development', 'sealed')}
    ids = set()
    with zipfile.ZipFile(RAW) as archive:
        # Identifier-only reservation, so an image/caption family cannot enter
        # training because a different hypothesis appeared in an official split.
        held = {split: {group(r) for r in rows(archive, split)} for split in ('dev', 'test')}
        for official, split in (('train', 'train'), ('dev', 'development'), ('test', 'sealed')):
            with (OUT / (split + '.jsonl')).open('x', encoding='utf-8') as dest:
                for row in rows(archive, official):
                    label = row['gold_label']; key = group(row)
                    if label not in LABELS:
                        excluded[split + ':no_consensus'] += 1; continue
                    if official == 'train' and key in held['dev'] | held['test']:
                        excluded[split + ':reserved_source_group'] += 1; continue
                    if official == 'dev' and key in held['test']:
                        excluded[split + ':reserved_source_group'] += 1; continue
                    identifier = hashlib.sha256(('SNLI-1.0:' + row['pairID']).encode()).hexdigest()
                    if identifier in ids:
                        excluded[split + ':duplicate_pair_id'] += 1; continue
                    ids.add(identifier); groups[split].add(key); counts[split] += 1
                    record = {'id': identifier, 'source_pair_id': row['pairID'], 'source_group': key,
                        'premise': row['sentence1'], 'hypothesis': row['sentence2'], 'target': LABELS[label],
                        'human_annotation_votes': row['annotator_labels'], 'official_split': official,
                        'source': 'SNLI-1.0', 'license': 'CC-BY-SA-4.0'}
                    dest.write(json.dumps(record, ensure_ascii=False) + '\n')
    assert not groups['train'] & groups['development']
    assert not groups['train'] & groups['sealed']
    assert not groups['development'] & groups['sealed']
    manifest = {'source_url': URL, 'source_page': 'https://nlp.stanford.edu/projects/snli/',
        'source_sha256': digest(RAW), 'source_bytes': RAW.stat().st_size,
        'authors': 'Samuel R. Bowman, Gabor Angeli, Christopher Potts, Christopher D. Manning (2015)',
        'license': 'CC-BY-SA-4.0', 'license_url': 'https://creativecommons.org/licenses/by-sa/4.0/',
        'human_provenance': 'Human-written sentence pairs and manual annotations per original authors',
        'transformation': 'Keep original sentences; numeric labels; exclude no consensus and cross-partition image groups',
        'labels': LABELS, 'counts': dict(counts), 'excluded': dict(excluded),
        'source_group_counts': {k: len(v) for k, v in groups.items()}, 'group_overlap': 0,
        'views': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in sorted(OUT.glob('*.jsonl'))},
        'transform_sha256': digest(Path(__file__)), 'wall_seconds': time.monotonic() - start,
        'cpu_seconds': time.process_time() - cpu,
        'test_use': 'Source reservation only; no model has seen sealed outcomes or selected using this split'}
    (OUT / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ('source_sha256', 'source_bytes', 'counts', 'group_overlap', 'wall_seconds')}))


if __name__ == '__main__':
    main()
