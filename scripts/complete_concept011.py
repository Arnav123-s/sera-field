"""Fresh qualification of direct routing, retaining all earlier failures."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import sha256,source_manifest,write_json,utc


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    from sera_field.concept_direct_study import phrases
    root=ROOT/'runs/CONCEPT-011';root.mkdir(parents=True,exist_ok=True)
    bank=root/'PHRASE_BANKS.json'
    if not bank.exists():write_json(bank,phrases())
    frozen=root/'FROZEN.json'
    record={'sources':source_manifest(ROOT),'parent':'runs/CONCEPT-009',
        'parent_selection_sha256':sha256(ROOT/'runs/CONCEPT-009/SELECTION.json'),'phrase_bank_sha256':sha256(bank)}
    if frozen.exists():
        if json.loads(frozen.read_text())!=record:raise ValueError('Frozen protocol changed')
    else:write_json(frozen,record)
    subprocess.run([sys.executable,'-m','sera_field.concept_direct_study'],check=True)
    roots={'repair':root,'residual':ROOT/'runs/CONCEPT-010','unchanged':ROOT/'runs/CONCEPT-009',
           'original':ROOT/'runs/CONCEPT-008/reward','echo':ROOT/'checkpoints/ECHO-007'}
    registration={'selections':{a:json.loads((p/'SELECTION.json').read_text()) for a,p in roots.items()},
                  'freeze_sha256':sha256(frozen)}
    register=root/'FINAL_REGISTRATION.json'
    if register.exists():
        if json.loads(register.read_text())!=registration:raise ValueError('Final registry changed')
    else:write_json(register,registration)
    for arm,folder in roots.items():
        for phase in ('final','replay'):
            subprocess.run([sys.executable,'-m','sera_field.concept_study','evaluate','--arm',arm,
                '--training',str(folder),'--output',str(root/phase/arm),'--experiment','CONCEPT-011',
                '--phrase-bank',str(bank)],check=True)
        if json.loads((root/'final'/arm/'RESULTS.json').read_text())!=json.loads((root/'replay'/arm/'RESULTS.json').read_text()):
            raise ValueError('Replay differs')
        write_json(root/'replay'/arm/'REPLAY.json',{'all_metrics_and_raw_records_exact':True})
    metrics={a:json.loads((root/'final'/a/'RESULTS.json').read_text())['metrics']['supported'] for a in roots}
    new,old,original,echo=(metrics[k] for k in ('repair','unchanged','original','echo'))
    names=('forward_mse','inverse_mse','counterfactual_mse','plan_mse')
    checks={'routing':new['route_correct']>=.9,'direction':new['direction_correct']>=.8,
        'direction_improved':new['direction_correct']>=original['direction_correct']+.1,
        'numerical_outputs_retained':all(new[k]==old[k] for k in names),
        'old_parameters_retained':json.loads((root/'COMPLETE.json').read_text())['all_parent_parameters_exact']}
    checks.update({k:new[k]<=(.9 if k=='plan_mse' else .8)*echo[k] for k in names})
    decision={'checks':checks,'qualified':all(checks.values()),'all_five_replays_exact':True,'completed_utc':utc()}
    write_json(root/'DECISION.json',decision)
    print(json.dumps({'decision':decision,'supported':metrics},indent=2),flush=True)


if __name__=='__main__':main()
