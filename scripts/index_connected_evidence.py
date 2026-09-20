"""Index completed evidence and full supervised costs using only file records."""
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import sha256, write_json


def main():
    report = ROOT/'reports/CONNECTED-003'
    comparison = ROOT/'runs/CONNECTED-SCFE-COMPARISON-001'
    checks = {}
    for name in ('field','scfe'):
        target = report/'evaluations'/name
        target.mkdir(parents=True,exist_ok=True)
        for file in ('RESULTS.json','EVIDENCE.json','FROZEN_CANDIDATES.json','OPENED_GROUPS.json'):
            origin = comparison/(name+'-final')/file
            shutil.copyfile(origin,target/file)
            checks[str(origin.relative_to(ROOT))] = sha256(origin)
        origin = comparison/(name+'-replay')/'REPLAY.json'
        shutil.copyfile(origin,target/'REPLAY.json')
        checks[str(origin.relative_to(ROOT))] = sha256(origin)
    qualification = ROOT/'runs/SCFE-006-policy-selection'
    target = report/'policy-qualification'
    target.mkdir(parents=True,exist_ok=True)
    for relative in ('final/RESULTS.json','REPLAY.json','SELECTION.json','FROZEN.json'):
        origin = qualification/relative
        shutil.copyfile(origin,target/Path(relative).name)
        checks[str(origin.relative_to(ROOT))] = sha256(origin)
    paths = list((ROOT/'checkpoints/SCFE-004').rglob('*'))
    paths += [report/'LEARNED_EVIDENCE.json',report/'usage-examples.json']
    for path in paths:
        if path.is_file():
            checks[str(path.relative_to(ROOT))] = sha256(path)
    write_json(report/'EVIDENCE_INDEX.json',checks)
    prefixes = r'^(connected-003-|connected-scfe-|scfe-004-|echo-005-|scfe-006-|connected-delivery-)'
    attempts = [json.loads(line) for line in (ROOT/'runs/costs.jsonl').read_text().splitlines()]
    own = [r for r in attempts if re.match(prefixes,r['attempt'])]
    costs = {'scope':'All supervised direct CONNECTED-003, SCFE-004, ECHO-005, SCFE-006 and delivery attempts, including failures and replay.',
             'attempts':own, 'wall_seconds':sum(r['wall_seconds'] for r in own),
             'cpu_seconds':sum(r.get('resources',{}).get('cpu_seconds',0) for r in own),
             'peak_committed_bytes':max(r.get('resources',{}).get('peak_committed_bytes',0) for r in own),
             'failed_attempts':sum(r['status']!='PASS' for r in own),
             'numerical_threads':1,'memory_cap_bytes':2147483648,'paid_compute':False,
             'earlier_costs':'reports/COSTS.json and the full append-only runs/costs.jsonl remain preserved.',
             'interrupted_delegated_costs':'local/takeover-003/ag-run-state-at-takeover.json preserves a lower-bound sample, not a fabricated complete cost.'}
    write_json(report/'COSTS.json',costs)
    print(json.dumps({k:v for k,v in costs.items() if k!='attempts'},indent=2))


if __name__ == '__main__':
    main()
