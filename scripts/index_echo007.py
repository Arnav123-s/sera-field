"""Publish compact evidence copies and complete supervised costs without computation."""
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import sha256,write_json


def main():
    study=ROOT/'runs/ECHO-007';report=ROOT/'reports/ECHO-007';checks={}
    def copy(origin,destination):
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(origin,destination)
        checks[origin.relative_to(ROOT).as_posix()]=sha256(origin)
        checks[destination.relative_to(ROOT).as_posix()]=sha256(destination)
    for name in ('FROZEN.json','FINAL_REGISTRATION.json','DECISION.json'):
        copy(study/name,report/name)
    for arm in ('echo','autograd','no_core_credit','parent'):
        for name in ('RESULTS.json','EVIDENCE.json','COHORTS.json','OPENED_GROUPS.json'):
            copy(study/'final'/arm/name,report/'evaluation'/arm/name)
        copy(study/'replay'/arm/'REPLAY.json',report/'evaluation'/arm/'REPLAY.json')
        if arm!='parent':copy(study/arm/'COMPLETE.json',report/'training'/arm/'COMPLETE.json')
    for p in (ROOT/'checkpoints/ECHO-007').rglob('*'):
        if p.is_file():checks[str(p.relative_to(ROOT))]=sha256(p)
    for name in ('LEARNED_STATE.json','FIELD_STORAGE.json','USAGE_EXAMPLES.json'):
        p=report/name;checks[str(p.relative_to(ROOT))]=sha256(p)
    all_costs=[json.loads(line) for line in (ROOT/'runs/costs.jsonl').read_text().splitlines()]
    own=[r for r in all_costs if r['attempt'].startswith('echo-007-')]
    for attempt in own:
        for name in ('state.json','process.log'):
            copy(ROOT/'runs'/attempt['attempt']/name,report/'supervision'/attempt['attempt']/name)
    costs={'scope':'All supervised ECHO-007 numerical work, including contracts, training, development, controls, final replay, delivery and storage/lineage audit.',
        'attempts':own,'wall_seconds':sum(r['wall_seconds'] for r in own),
        'cpu_seconds':sum(r.get('resources',{}).get('cpu_seconds',0) for r in own),
        'peak_committed_bytes':max(r.get('resources',{}).get('peak_committed_bytes',0) for r in own),
        'failed_process_attempts':sum(r['status']!='PASS' for r in own),
        'numerical_threads':1,'memory_cap_bytes':2147483648,'paid_compute':False,
        'previous_work':'reports/CONNECTED-003/COSTS.json and reports/COSTS.json remain preserved.'}
    write_json(report/'COSTS.json',costs)
    checks[(report/'COSTS.json').relative_to(ROOT).as_posix()]=sha256(report/'COSTS.json')
    for name in ('thdft-repost-20260920','thdft-synthesis-20260920'):
        copy(ROOT/'intake'/name/'MANIFEST.json',report/'source-intake'/(name+'.json'))
    write_json(report/'EVIDENCE_INDEX.json',checks)
    print(json.dumps({k:v for k,v in costs.items() if k!='attempts'},indent=2))


if __name__=='__main__':main()
