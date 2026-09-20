"""Preserve the official human MultiNLI archive; no model work or extraction."""
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
URL = 'https://cims.nyu.edu/~sbowman/multinli/multinli_1.0.zip'


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1048576), b''):
            result.update(chunk)
    return result.hexdigest()


def main():
    started = time.perf_counter(); cpu = time.process_time()
    raw = ROOT / 'data/raw/multinli_1.0.zip'; raw.parent.mkdir(parents=True, exist_ok=True)
    report = ROOT / 'reports/SOURCE_INTAKE/MULTINLI-1.0.json'; report.parent.mkdir(parents=True, exist_ok=True)
    if report.exists():
        recorded = json.loads(report.read_text())
        if digest(raw) != recorded['sha256']:
            raise ValueError('Preserve the existing archive: its source identity changed')
        print(json.dumps({'status': 'previous intake verified', 'sha256': recorded['sha256']})); return
    attempt = report.parent / ('MULTINLI-1.0-attempt-' + str(time.time_ns()) + '.json')
    outcome = {'url': URL, 'original_source_page': 'https://cims.nyu.edu/~sbowman/multinli/',
        'paper': 'https://aclanthology.org/N18-1101/', 'status': 'RUNNING',
        'work_kind': 'stdlib source intake; no model inference or training', 'started_unix': time.time()}
    try:
        if not raw.exists():
            pending = raw.with_suffix('.download-' + str(time.time_ns()))
            request = urllib.request.Request(URL, headers={'User-Agent': 'SERA-Research/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response, pending.open('xb') as target:
                total = 0
                while chunk := response.read(1048576):
                    total += len(chunk)
                    if total > 512 * 1024 ** 2:
                        raise ValueError('The source exceeds the declared archive size guard')
                    target.write(chunk)
                target.flush(); os.fsync(target.fileno())
            pending.rename(raw)
        with zipfile.ZipFile(raw) as archive:
            entries = [{'name': row.filename, 'bytes': row.file_size, 'compressed_bytes': row.compress_size}
                       for row in archive.infolist()]
            expected = {'multinli_1.0/multinli_1.0_train.jsonl',
                        'multinli_1.0/multinli_1.0_dev_matched.jsonl',
                        'multinli_1.0/multinli_1.0_dev_mismatched.jsonl'}
            if not expected <= {row['name'] for row in entries}:
                raise ValueError('The official corpus archive structure changed')
        outcome.update(status='PASS', sha256=digest(raw), bytes=raw.stat().st_size, entries=entries,
            attribution='Adina Williams, Nikita Nangia and Samuel R. Bowman, NAACL 2018',
            human_provenance='Human source premises and crowdworker-authored hypotheses; manual relation annotations',
            license_scope='OANC terms and source-specific fiction permissions/CC/public-domain terms; see the original paper',
            corpus_text_redistributed=False, learned_capability_claim=False)
    except BaseException as error:
        outcome.update(status='FAILED', error=repr(error)); raise
    finally:
        outcome.update(wall_seconds=time.perf_counter()-started, cpu_seconds=time.process_time()-cpu)
        attempt.write_text(json.dumps(outcome, indent=2), encoding='utf-8')
        if outcome['status'] == 'PASS':
            report.write_text(json.dumps(outcome, indent=2), encoding='utf-8')
        print(json.dumps({k: outcome.get(k) for k in ('status', 'sha256', 'bytes', 'wall_seconds', 'cpu_seconds')}), flush=True)


if __name__ == '__main__':
    main()
