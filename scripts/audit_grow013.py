"""Independent retention/readback and inference export after registered finals."""
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys

import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sera_field.extension_study import load_extension
from sera_field.extension_world import episode
from sera_field.model import weight_hash,parameters
from sera_field.records import sha256,write_json
from sera_field.study_data import load_records
from sera_field.study_inquiry import load_selected
from sera_field.study_training import reading_batch,math_batch,pair_batch
from sera_field.study_world import stable_seed


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    runs=ROOT/'runs/GROW-013';report=ROOT/'reports/GROW-013';report.mkdir(parents=True,exist_ok=True)
    owner,selection=load_extension(runs/'learned');owner.eval()
    parent,_=load_selected(ROOT/'runs/UNIFIED-012/coupled')
    protected=all(torch.equal(p,dict(owner.named_parameters())[name]) for name,p in parent.named_parameters())
    registration=json.loads((ROOT/'runs/UNIFIED-012/FINAL_REGISTRATION.json').read_text())
    retained={};data=ROOT/'local/CONNECTED-003-data-v1'
    with torch.no_grad():
        for kind,fn in (('reading',reading_batch),('math',math_batch)):
            bank={r['id']:r for r in load_records(data,'sealed',kind)}
            rows=[bank[i] for i in registration['cohorts'][kind]]
            values=[fn(owner,[r]) for r in rows]
            retained[kind]={'n':len(rows),'accuracy':sum(v[1] for v in values)/len(rows),
                            'loss':sum(float(v[0]) for v in values)/len(rows)}
        bank={r['id']:r for r in load_records(data,'sealed','pairs')};retained['pairs']={}
        for track,ids in registration['cohorts']['pairs'].items():
            rows=[bank[i] for i in ids]
            if len(rows)<4:continue
            rng=random.Random(stable_seed('UNIFIED-012-final-v1',track))
            values=[pair_batch(owner,[r],rows,rng) for r in rows]
            retained['pairs'][track]={'n':len(rows),'accuracy':sum(v[1] for v in values)/len(rows)}
    before=json.loads((ROOT/'reports/UNIFIED-012/final/coupled/RESULTS.json').read_text())
    finals={a:json.loads((runs/'final'/a/'RESULTS.json').read_text()) for a in ('learned','fixed','no_extension')}
    replay=json.loads((runs/'replay/learned/RESULTS.json').read_text())
    gates={'protected_parent_parameters_exact':protected,
        'reading_retention':retained['reading']['accuracy']>=before['reading']['accuracy']-.03,
        'mathematics_retention':retained['math']['accuracy']>=before['math']['accuracy']-.03,
        'mean_pair_retention':np.mean([v['accuracy'] for v in retained['pairs'].values()])>=
            np.mean([v['accuracy'] for v in before['pairs'].values()])-.03,
        'exact_replay':finals['learned']['cases_sha256']==replay['cases_sha256'],
        'immutable_final_owner':all(v['weights_before']==v['weights_after'] for v in finals.values())}
    gates={k:bool(v) for k,v in gates.items()}
    write_json(report/'RETENTION.json',{'cohort':'Previously opened UNIFIED-012 cohort used only for prospective regression checks',
        'metrics':retained,'reference':before,'protected_parent_parameters_exact':protected})
    for a,m in finals.items():
        dest=report/'final'/a;dest.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(runs/'final'/a/'RESULTS.json',dest/'RESULTS.json')
    for name in ('FINAL_REGISTRATION.json',):shutil.copyfile(runs/name,report/name)
    shutil.copyfile(runs/'learned/COMPLETE.json',report/'TEACHING.json')
    shutil.copyfile(runs/'replay/learned/RESULTS.json',report/'REPLAY.json')
    write_json(report/'QUALIFICATION.json',{'gates':gates,'all_gates':all(gates.values()),
        'whole_architecture_completed':False,'selected':selection})
    if not all(gates.values()):raise ValueError('Candidate kept for repair; retention/replay gate failed')
    target=ROOT/'checkpoints/GROW-013';(target/'revisions').mkdir(parents=True,exist_ok=True)
    if not (target/'SELECTION.json').exists():
        temporary=target/'revisions/export.tmp'
        torch.save({'bridge':{'owner':owner.state_dict(),'specification':owner.specification()},
                    'source_checkpoint_sha256':selection['sha256']},temporary)
        digest=sha256(temporary);temporary.rename(target/'revisions'/(digest+'.pt'))
        exported={**selection,'sha256':digest,'revision':digest+'.pt','source_checkpoint_sha256':selection['sha256'],
                  'role':'qualified_learned_response_extension'}
        write_json(target/'SELECTION.json',exported)
        write_json(target/'MANIFEST.json',{'selection':exported,'parameters':parameters(owner),
                   'specification':owner.specification(),'report':'reports/GROW-013/REPORT.md',
                   'full_optimizer_and_rng_retained':'runs/GROW-013/learned/revisions'})
    exported,_=load_extension(target);assert weight_hash(exported)==selection['weights']
    delivery=ROOT/'local/GROW-013-delivery';delivery.mkdir(parents=True,exist_ok=True)
    world,a,c,q=episode(1311307,'GROW-013-delivery-v1')
    request={'original_goal':{'queries':q[:2].tolist()},'adaptation':a.tolist(),'calibration':c.tolist(),
        'source':{'kind':'independent_simulation','id':'GROW-013-delivery-v1'},
        'assumptions':{'scope':'independent two-input simulated response'}}
    write_json(delivery/'task.json',request)
    question={'queries':q[2:4].tolist(),'question':'What happens when the control input increases?','point':[0.,0.]}
    write_json(delivery/'question.json',question)
    commands=[('learn','task.json'),('answer','question.json')]
    if not (delivery/'session/CURRENT.json').exists():
        first=subprocess.run([sys.executable,'-m','sera_field.extension_cli','learn','--owner',str(target),
            '--session',str(delivery/'session'),'--input',str(delivery/'task.json')],capture_output=True,text=True,check=True)
        write_json(delivery/'learn.json',json.loads(first.stdout))
    outputs=[]
    for _ in range(2):
        result=subprocess.run([sys.executable,'-m','sera_field.extension_cli','answer','--owner',str(target),
            '--session',str(delivery/'session'),'--input',str(delivery/'question.json')],capture_output=True,text=True,check=True)
        outputs.append(json.loads(result.stdout))
    assert outputs[0]==outputs[1] and outputs[0]['original_goal']==request['original_goal']
    truth=world.observe(q[2:4,0],q[2:4,1]);p=np.array(outputs[0]['predictions']).mean(0)
    write_json(report/'DELIVERY.json',{'fresh_process_restart_exact':True,'original_goal_retained':True,
        'answer':outputs[0],'independent_outcomes':truth.tolist(),'mse':float(np.mean((p-truth)**2)),
        'owner_weights':selection['weights']})
    print(json.dumps({'gates':gates,'delivery_mse':float(np.mean((p-truth)**2))},indent=2))


if __name__=='__main__':main()
