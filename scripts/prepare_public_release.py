"""Prepare a reviewed current-file snapshot; never copy private history or corpora."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
DEST=Path('D:/ai/publications/sera-field-20260920')
EXCLUDE={'reports/FIELD-001/raw-evidence.zip'}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if DEST.exists():raise SystemExit('Preserve the existing publication snapshot')
    files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    patterns=[rb'gh[pousr]_[A-Za-z0-9]{24,}',rb'github_pat_[A-Za-z0-9_]{24,}',
              rb'sk-[A-Za-z0-9]{24,}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    reviewed=[]
    for name in files:
        if not name or name in EXCLUDE:continue
        path=ROOT/name
        if path.is_symlink():raise ValueError('Review symlink separately: '+name)
        if name.split('/')[0] in {'intake','local','runs','data','.git','.venv'}:
            raise ValueError('Private tree entered tracked release: '+name)
        raw=path.read_bytes()
        if any(re.search(p,raw) for p in patterns):raise ValueError('Credential-like content needs review: '+name)
        reviewed.append((name,path))
    DEST.mkdir(parents=True)
    for name,path in reviewed:
        target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
    note=DEST/'reports/FIELD-001/LOCAL_RAW_ARCHIVE.md'
    note.write_text('# Preserved raw archive\n\nThe complete FIELD-001 raw archive and exact optimizer/RNG history remain in the local research lab at `reports/FIELD-001/raw-evidence.zip`. Its public identities are recorded in [artifacts.json](artifacts.json). This current-file release publishes assessed weights and results; it does not upload private Git history or raw training archives.\n',encoding='utf-8')
    index=DEST/'reports/INDEX.md'
    index.write_text(index.read_text(encoding='utf-8').replace('(FIELD-001/raw-evidence.zip)','(FIELD-001/LOCAL_RAW_ARCHIVE.md)'),encoding='utf-8')
    scope=DEST/'PUBLICATION_SCOPE.md'
    scope.write_text(f'''# Reviewed publication scope

This is a single current-file release snapshot of the independent SERA Field
laboratory, source revision `{head}`. The local repository and all of its
historical commits remain intact. The original SERA repository is unchanged.

Included: project source, tests, prospective protocols, engineering/usage guides,
research reports, compact numerical logs, source/checkpoint identity manifests,
the assessed CONCEPT-011 inference weights and the earlier packaged checkpoints.
The file-by-file byte counts and SHA-256 identities are in
[PUBLICATION_MANIFEST.json](PUBLICATION_MANIFEST.json).

Excluded: the original local Git history, private research attachments, original
source packets, raw human corpora, complete training/run directories, optimizer
history archives, local sessions, credentials and environment files. The one
historical raw archive link now leads to a local-preservation note. Every earlier
failed study and checkpoint remains in the local lab; its compact reported
results, identity and costs are retained here.

The scanned patterns cover common GitHub/API token and private-key encodings.
This is a scoped content review, not a claim of a universal secret detector.
''',encoding='utf-8')
    manifest={'source_local_revision':head,'repository':'https://github.com/Arnav123-s/sera-field',
        'scope':'Reviewed current-file snapshot, no private Git history or raw corpus/attachment/run trees',
        'excluded_tracked_files':sorted(EXCLUDE),'credential_pattern_matches':0,
        'snapshot_adaptations':['raw archive replaced with local-preservation note and link','publication scope and manifest added'],
        'files':[{'path':p.relative_to(DEST).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)}
                 for p in sorted(DEST.rglob('*')) if p.is_file()]}
    manifest['file_count']=len(manifest['files']);manifest['total_bytes']=sum(x['bytes'] for x in manifest['files'])
    (DEST/'PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'destination':str(DEST),'files':manifest['file_count'],'bytes':manifest['total_bytes'],
        'manifest_sha256':digest(DEST/'PUBLICATION_MANIFEST.json'),'source':head},indent=2))


if __name__=='__main__':main()
