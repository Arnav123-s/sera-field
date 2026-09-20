"""Portable integrity check for packaged owners; no training or external sources."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    checked=[]
    for pointer in sorted((ROOT/'checkpoints').glob('*/SELECTION.json')):
        selected=json.loads(pointer.read_text())
        folder=(pointer.parent/'revisions').resolve()
        file=(folder/selected['revision']).resolve()
        if file.parent!=folder:raise ValueError('Unsafe checkpoint revision')
        digest=hashlib.sha256(file.read_bytes()).hexdigest()
        if digest!=selected['sha256']:raise ValueError('Checkpoint bytes changed: '+str(file))
        checked.append({'selection':pointer.relative_to(ROOT).as_posix(),'sha256':digest,
                        'bytes':file.stat().st_size,'weights':selected['weights']})
    if not checked:raise ValueError('No packaged learned owner')
    print(json.dumps({'status':'PASS','packaged_owners':checked},indent=2))


if __name__=='__main__':main()
