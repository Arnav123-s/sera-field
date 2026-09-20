"""Carry the measured language repair through independent new-cohort replay."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import sha256, source_manifest, write_json, utc


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    root=ROOT/'runs/CONCEPT-009';root.mkdir(parents=True,exist_ok=True)
    from sera_field.concept_repair import phrases
    bank=root/'PHRASE_BANKS.json'
    if not bank.exists():write_json(bank,phrases())
    decision=json.loads((ROOT/'runs/CONCEPT-008/DECISION.json').read_text())
    parent=ROOT/'runs/CONCEPT-008'/('reward' if decision['reward_qualified'] else decision['teaching_choice'])
    frozen=root/'FROZEN.json'
    record={'sources':source_manifest(ROOT),'parent':str(parent.relative_to(ROOT)),
            'parent_selection_sha256':sha256(parent/'SELECTION.json'),'phrase_bank_sha256':sha256(bank)}
    if frozen.exists():
        old=json.loads(frozen.read_text())
        for name,h in old['sources'].items():
            if sha256(ROOT/name)!=h:raise ValueError('Repair frozen executable changed: '+name)
        if {k:v for k,v in old.items() if k!='sources'}!={k:v for k,v in record.items() if k!='sources'}:
            raise ValueError('Repair freeze changed')
    else:write_json(frozen,record)
    subprocess.run([sys.executable,'-m','sera_field.concept_repair','--training',str(parent)],check=True)
    roots={'repair':root,'unchanged':parent,'echo':ROOT/'checkpoints/ECHO-007'}
    registration={'selections':{arm:json.loads((folder/'SELECTION.json').read_text()) for arm,folder in roots.items()},
                  'freeze_sha256':sha256(frozen)}
    register=root/'FINAL_REGISTRATION.json'
    if register.exists():
        if json.loads(register.read_text())!=registration:raise ValueError('Repair final selection changed')
    else:write_json(register,registration)
    for arm,folder in roots.items():
        for phase in ('final','replay'):
            subprocess.run([sys.executable,'-m','sera_field.concept_study','evaluate','--arm',arm,
                '--training',str(folder),'--output',str(root/phase/arm),'--experiment','CONCEPT-009',
                '--phrase-bank',str(bank)],check=True)
        a=json.loads((root/'final'/arm/'RESULTS.json').read_text())
        b=json.loads((root/'replay'/arm/'RESULTS.json').read_text())
        if a!=b:raise ValueError('Repair replay changed')
        write_json(root/'replay'/arm/'REPLAY.json',{'all_metrics_and_raw_records_exact':True})
    metrics={arm:json.loads((root/'final'/arm/'RESULTS.json').read_text())['metrics']['supported'] for arm in roots}
    new,old,echo=(metrics[k] for k in ('repair','unchanged','echo'))
    names=('forward_mse','inverse_mse','counterfactual_mse','plan_mse')
    checks={'routing':new['route_correct']>=.9,'direction':new['direction_correct']>=.8,
            'direction_improved':new['direction_correct']>=old['direction_correct']+.1,
            'numerical_outputs_retained':all(new[k]==old[k] for k in names),
            'old_parameters_retained':json.loads((root/'COMPLETE.json').read_text())['all_non_routing_parameters_exact']}
    checks.update({k:new[k]<=(.9 if k=='plan_mse' else .8)*echo[k] for k in names})
    write_json(root/'DECISION.json',{'checks':checks,'qualified':all(checks.values()),
        'all_three_replays_exact':True,'completed_utc':utc()})
    print(json.dumps({'decision':json.loads((root/'DECISION.json').read_text()),'supported':metrics},indent=2),flush=True)


if __name__=='__main__':main()
