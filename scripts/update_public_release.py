"""Copy a committed, reviewed current snapshot into the clean publication checkout.

No history, private source attachments, raw corpora or run trees are transferred.
This does not commit or push. Inspect the resulting diff before publication.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('D:/ai/publications/sera-field-20260920')
EXCLUDE = {'reports/FIELD-001/raw-evidence.zip'}
PRIVATE = {'intake', 'local', 'runs', 'data', '.git', '.venv'}
PATTERNS = [rb'gh[pousr]_[A-Za-z0-9]{24,}', rb'github_pat_[A-Za-z0-9_]{24,}',
            rb'sk-[A-Za-z0-9]{24,}', rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def main():
    if not DEST.is_dir() or not (DEST / '.git').exists():
        raise ValueError('Expected the existing reviewed publication checkout')
    if git(ROOT, 'status', '--porcelain') or git(DEST, 'status', '--porcelain'):
        raise ValueError('Commit reviewed source and preserve any dirty publication work first')
    source = git(ROOT, 'rev-parse', 'HEAD').decode().strip()
    contents = {}
    for record in git(ROOT, 'ls-tree', '-rz', '--full-tree', 'HEAD').split(b'\0'):
        if not record:
            continue
        meta, name_bytes = record.split(b'\t', 1)
        mode, kind, blob = meta.decode().split()
        name = name_bytes.decode()
        if name in EXCLUDE:
            continue
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or path.parts[0] in PRIVATE:
            raise ValueError('Private/invalid tracked publication path: ' + name)
        if kind != 'blob' or mode not in {'100644', '100755'}:
            raise ValueError('Review nonregular file independently: ' + name)
        data = git(ROOT, 'cat-file', 'blob', blob)
        if any(re.search(pattern, data) for pattern in PATTERNS):
            raise ValueError('Credential-like content needs review: ' + name)
        contents[name] = data
    note = 'reports/FIELD-001/LOCAL_RAW_ARCHIVE.md'
    contents[note] = (DEST / note).read_bytes().replace(b'\r\n', b'\n')
    contents['reports/INDEX.md'] = contents['reports/INDEX.md'].replace(
        b'(FIELD-001/raw-evidence.zip)', b'(FIELD-001/LOCAL_RAW_ARCHIVE.md)')
    contents['PUBLICATION_SCOPE.md'] = f'''# Reviewed publication scope

This release is a reviewed current-file snapshot of the independent SERA Field
laboratory at source revision `{source}`. The complete local history and original
SERA remain preserved. This checkout has its own public publication history.

Included: source, tests, frozen prospective protocols, engineering and usage
guides, compact research results, costs and identity manifests, and packaged
inference weights with their individually recorded assessment and research roles.
The fresh NATIVE-019 lineage and earlier usable checkpoints remain separately
addressable. The documentation guide separates current interfaces from history.
Work marked active in the research state has not been represented as completed.
File identities below describe the Git blob bytes, before platform line endings.

Excluded: private Git history, source attachments and packets, raw human corpora,
complete run trees, local sessions, credentials and environment files. The
historical FIELD-001 raw archive stays local; its public link points to a
preservation note. Failed studies, full optimizer/RNG histories and old checkpoints
remain in the lab with compact outcomes and costs published.

The historical FIELD-001 base checkpoint includes its selected optimizer and RNG
state from the supplied physical simulation study. Later packaged owners contain
inference weights and lineage. Common token/private-key patterns were scanned;
this scoped review is not a universal secret detector.

See [PUBLICATION_MANIFEST.json](PUBLICATION_MANIFEST.json) for exact file identities.
'''.encode()
    existing = set(filter(None, git(DEST, 'ls-files', '-z').decode().split('\0')))
    missing = existing - set(contents) - {'PUBLICATION_MANIFEST.json'}
    if missing:
        raise ValueError('Review preserved publication-only files explicitly: ' + str(sorted(missing)))
    manifest = {'source_local_revision': source,
        'repository': 'https://github.com/Arnav123-s/sera-field',
        'scope': 'Reviewed current Git blobs; private history, raw attachments/corpora/runs excluded',
        'excluded_tracked_files': sorted(EXCLUDE), 'credential_pattern_matches': 0,
        'snapshot_adaptations': ['raw archive replaced by preservation note and link',
                                 'publication scope and manifest added'],
        'files': [{'path': n, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                  for n, raw in sorted(contents.items())]}
    manifest['file_count'] = len(contents)
    manifest['total_bytes'] = sum(row['bytes'] for row in manifest['files'])
    contents['PUBLICATION_MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    # All validations precede writes; this update never deletes any file.
    for name, raw in contents.items():
        path = DEST / name
        if path.is_symlink():
            raise ValueError('Publication destination symlink: ' + name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    print(json.dumps({'source': source, 'destination': str(DEST),
                      'file_count': manifest['file_count'], 'bytes': manifest['total_bytes']}))


if __name__ == '__main__':
    main()
