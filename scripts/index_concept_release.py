"""Publishable compact evidence; full raw cases and resumable states stay local."""
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import sha256,write_json,utc


def main():
    costs=[json.loads(line) for line in (ROOT/'runs/costs.jsonl').read_text().splitlines() if line.strip()]
    total=[]
    for number in (8,9,10,11):
        name=f'CONCEPT-{number:03d}';root=ROOT/'runs'/name;dest=ROOT/'reports'/name
        dest.mkdir(parents=True,exist_ok=True)
        evidence=[]
        for file in sorted(root.rglob('*')):
            if not file.is_file():continue
            rel=file.relative_to(root)
            evidence.append({'path':file.relative_to(ROOT).as_posix(),'bytes':file.stat().st_size,'sha256':sha256(file)})
            if file.suffix=='.json' and 'revisions' not in rel.parts and 'session' not in rel.parts:
                target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target)
            elif file.name.startswith('training-') and file.suffix=='.jsonl':
                target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target)
        write_json(dest/'EVIDENCE_INDEX.json',{'created_utc':utc(),'local_root':root.as_posix(),
            'raw_evidence_and_exact_resume_preserved':True,'artifacts':evidence})
        attempts=[row for row in costs if row['attempt'].startswith(f'concept-{number:03d}-')]
        total+=attempts
        for row in attempts:
            for file in ('state.json','process.log'):
                source=ROOT/'runs'/row['attempt']/file
                if source.exists():
                    target=dest/'supervision'/row['attempt']/file
                    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        write_json(dest/'COSTS.json',{'attempts':attempts,'wall_seconds':sum(r['wall_seconds'] for r in attempts),
            'cpu_seconds':sum(r.get('resources',{}).get('cpu_seconds',0) for r in attempts)})
    release=[row for row in costs if row['attempt'].startswith('concept-release-')]
    total+=release
    dest=ROOT/'reports/CONCEPT-011'
    for row in release:
        for file in ('state.json','process.log'):
            source=ROOT/'runs'/row['attempt']/file
            if source.exists():
                target=dest/'supervision'/row['attempt']/file
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    write_json(dest/'TOTAL_COSTS.json',{'all_concept_attempts':total,
        'wall_seconds':sum(r['wall_seconds'] for r in total),
        'cpu_seconds':sum(r.get('resources',{}).get('cpu_seconds',0) for r in total),
        'peak_process_tree_bytes':max(r.get('resources',{}).get('peak_committed_bytes',0) for r in total),
        'numerical_cpu_threads':1,'memory_cap_bytes':2147483648,'paid_compute':False,
        'scope':'All CONCEPT-008 through CONCEPT-011 supervision, including tests, failed qualifications, repairs, replays and delivery; earlier campaigns have separate preserved ledgers.'})
    summaries={}
    for n in (8,9,10,11):
        name=f'CONCEPT-{n:03d}';root=ROOT/'runs'/name
        summaries[name]={'decision':json.loads((root/'DECISION.json').read_text()),
            'finals':{p.parent.name:json.loads(p.read_text()) for p in sorted((root/'final').glob('*/RESULTS.json'))}}
    write_json(dest/'CAMPAIGN_SUMMARY.json',summaries)
    print('Indexed all four studies, exact artifact identities and total supervised costs.')


if __name__=='__main__':main()
