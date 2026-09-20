"""Complete teaching, reward, frozen finals and fresh-process replay sequentially."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import sha256, source_manifest, write_json, utc


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use the numerical supervisor')
    root=ROOT/'runs/CONCEPT-008';root.mkdir(parents=True,exist_ok=True)
    freeze=root/'FROZEN.json'
    if freeze.exists():
        f=json.loads(freeze.read_text())
        for name,h in f['sources'].items():
            if sha256(ROOT/name)!=h:raise ValueError('Changed frozen source '+name)
        if sha256(ROOT/'checkpoints/ECHO-007/SELECTION.json')!=f['parent_selection_sha256']:raise ValueError('Changed parent')
    else:
        write_json(freeze,{'sources':source_manifest(ROOT),'parent_selection_sha256':sha256(ROOT/'checkpoints/ECHO-007/SELECTION.json'),
            'protocol_sha256':sha256(ROOT/'protocols/CONCEPT-008.md'),'created_utc':utc()})
    def run(*args):
        subprocess.run([sys.executable,'-m','sera_field.concept_study',*map(str,args)],check=True,cwd=ROOT)
    for arm in ('full','diagonal'):run('train','--arm',arm)
    chosen=min(('full','diagonal'),key=lambda arm:json.loads((root/arm/'SELECTION.json').read_text())['score'])
    choice={'arm':chosen,'criterion':'minimum prospectively specified development score'}
    write_json(root/'TEACHING_CHOICE.json',choice)
    run('reward','--training',root/chosen)
    selections={a:json.loads((root/a/'SELECTION.json').read_text()) for a in ('full','diagonal','reward')}
    selections['parent']=json.loads((ROOT/'checkpoints/ECHO-007/SELECTION.json').read_text())
    registration={'protocol_sha256':sha256(ROOT/'protocols/CONCEPT-008.md'),'selections':selections,'teaching_choice':chosen}
    path=root/'FINAL_REGISTRATION.json'
    if path.exists():
        if json.loads(path.read_text())!=registration:raise ValueError('Final registration changed')
    else:write_json(path,registration)
    for arm in ('full','diagonal','parent','ridge'):
        for phase in ('final','replay'):
            run('evaluate','--arm',arm,'--output',root/phase/arm)
        actual=json.loads((root/'final'/arm/'RESULTS.json').read_text())
        replay=json.loads((root/'replay'/arm/'RESULTS.json').read_text())
        if actual!=replay:raise ValueError('Five-use final replay differs: '+arm)
        write_json(root/'replay'/arm/'REPLAY.json',{'all_metrics_and_raw_records_exact':True})
    for arm in ('reward','unchanged','random','analytic'):
        training=root/'reward' if arm=='reward' else root/chosen
        for phase in ('inquiry-final','inquiry-replay'):
            run('inquiry','--arm',arm,'--training',training,'--output',root/phase/arm)
        actual=json.loads((root/'inquiry-final'/arm/'RESULTS.json').read_text())
        replay=json.loads((root/'inquiry-replay'/arm/'RESULTS.json').read_text())
        if actual!=replay:raise ValueError('Inquiry replay differs: '+arm)
        write_json(root/'inquiry-replay'/arm/'REPLAY.json',{'all_metrics_and_raw_records_exact':True})
    results={a:json.loads((root/'final'/a/'RESULTS.json').read_text()) for a in ('full','diagonal','parent','ridge')}
    candidate=results[chosen]['metrics']['supported'];parent=results['parent']['metrics']['supported']
    checks={k:candidate[k]<=factor*parent[k] for k,factor in
            (('forward_mse',.8),('inverse_mse',.8),('counterfactual_mse',.8),('plan_mse',.9))}
    checks.update(direction=candidate['direction_correct']>=.8,language_route=candidate['route_correct']>=.8,
        immutable=all(r['weights_immutable'] for r in results.values()),
        old_parameters_exact=json.loads((root/chosen/'COMPLETE.json').read_text())['old_parameters_exact'])
    reward_mse=json.loads((root/'inquiry-final/reward/RESULTS.json').read_text())['metrics']['after_mse']
    unchanged=json.loads((root/'inquiry-final/unchanged/RESULTS.json').read_text())['metrics']['after_mse']
    decision={'teaching_choice':chosen,'checks':checks,'qualified':all(checks.values()),
        'reward_qualified':reward_mse<=1.05*unchanged,'reward_final_mse':reward_mse,'unchanged_final_mse':unchanged,
        'all_eight_replays_exact':True,'completed_utc':utc()}
    write_json(root/'DECISION.json',decision)
    print(json.dumps(decision,indent=2),flush=True)


if __name__=='__main__':main()
