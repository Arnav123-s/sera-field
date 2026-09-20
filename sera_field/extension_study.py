"""Frozen learned-extension teaching and independent five-use evaluation."""
import argparse
import copy
import json
import os
from pathlib import Path
import time

import numpy as np
import torch

from .credit_bridge import CreditBridge,identity
from .learned_extension import ExtensionOwner,extend_representation
from .extension_world import episode
from . import extension_tasks as tasks
from .model import weight_hash
from .records import sha256,write_json,utc
from .study_data import ROOT
from .study_inquiry import load_selected

STUDY=ROOT/'runs/GROW-013'
PARENT=ROOT/'runs/UNIFIED-012/coupled'


def batch(indices,split):
    episodes=[episode(i,split) for i in indices]
    observations=torch.from_numpy(np.stack([e[1] for e in episodes]))
    queries=torch.from_numpy(np.stack([e[3] for e in episodes]))
    truth=torch.from_numpy(np.stack([e[0].observe(e[3][:,0],e[3][:,1]) for e in episodes])).float()
    return observations,queries,truth


def load_extension(root):
    root=Path(root);selection=json.loads((root/'SELECTION.json').read_text())
    path=root/'revisions'/selection['revision']
    if path.resolve().parent!=(root/'revisions').resolve() or sha256(path)!=selection['sha256']:
        raise ValueError('Extension checkpoint identity mismatch')
    payload=torch.load(path,map_location='cpu',weights_only=False)
    spec=dict(payload['bridge']['specification']);kind=spec.pop('type')
    if kind!='learned-extension-013':raise ValueError('Wrong extension type')
    owner=ExtensionOwner(**spec);owner.load_state_dict(payload['bridge']['owner'])
    if weight_hash(owner)!=selection['weights']:raise ValueError('Extension weights mismatch')
    return owner,selection


@torch.no_grad()
def development(owner):
    errors=[];ranks=[]
    for i in range(96):
        world,a,c,q=episode(i,'GROW-013-development-v1')
        model,diagnosis=owner.acquire_extension(torch.from_numpy(a)[None],torch.from_numpy(c)[None])
        p=owner.predict_model(model,torch.from_numpy(q)[None]).mean(1)[0].numpy()
        errors.append(float(np.mean((p-world.observe(q[:,0],q[:,1]))**2)));ranks.append(model['rank'])
    return {'mse':float(np.mean(errors)),'selected_ranks':ranks,'n':96,'weights':weight_hash(owner)}


def train():
    root=STUDY/'learned';root.mkdir(parents=True,exist_ok=True)
    if (root/'COMPLETE.json').exists():load_extension(root);return
    parent,parent_selection=load_selected(PARENT)
    owner=extend_representation(parent)
    source=sha256(ROOT/'sera_field/extension_world.py');verifier=sha256(__file__)
    book=CreditBridge(owner,verifier_hashes=[verifier],source_hashes=[source])
    optimizer=torch.optim.AdamW([p for p in owner.parameters() if p.requires_grad],lr=.0005,weight_decay=.0001)
    step=0;prior=None;best=None;dev=[]
    if (root/'revisions/CURRENT.json').exists():
        saved=book.load_current(root/'revisions');p=saved['progress'];prior=saved['sha256']
        if p['parent_selection']!=parent_selection:raise ValueError('Parent changed while resuming')
        step=p['step'];optimizer.load_state_dict(p['optimizer']);best=p['best'];dev=p['development']
        if (root/'SELECTION.json').exists():best=json.loads((root/'SELECTION.json').read_text())
    def save():
        nonlocal prior
        record=book.commit(root/'revisions',expected_parent=prior,progress={'step':step,'best':best,
            'development':dev,'optimizer':optimizer.state_dict(),'parent_selection':parent_selection,
            'protocol_sha256':sha256(ROOT/'protocols/GROW-013.md')})
        prior=record['sha256'];return record
    if step==0 and not best:
        assessed=development(owner);dev.append({'step':step,**assessed});revision=save()
        best={**revision,'score':assessed['mse'],'step':0};write_json(root/'SELECTION.json',best)
        write_json(root/'INITIAL.json',{'parent':parent_selection,'development':assessed,'revision':revision})
        # The fixed-feature control starts from exactly these fresh features.
        fixed=STUDY/'fixed';(fixed/'revisions').mkdir(parents=True,exist_ok=True)
        import shutil
        if not (fixed/'SELECTION.json').exists():
            shutil.copyfile(root/'revisions'/revision['revision'],fixed/'revisions'/revision['revision'])
            write_json(fixed/'SELECTION.json',best)
    invocation=os.environ['SERA_FIELD_SUPERVISED'];started=time.monotonic()
    with (root/('updates-'+invocation+'.jsonl')).open('x',encoding='utf-8') as log:
        while step<2048:
            owner.train();optimizer.zero_grad(set_to_none=True)
            observations,queries,truth=batch(range(step*16,(step+1)*16),'GROW-013-teaching-v1')
            rank=(4,8,16)[step%3]
            model=owner.extend_model(observations,torch.ones(observations.shape[:2]),rank)
            prediction=owner.predict_model(model,queries)
            loss=(prediction-truth[:,None]).square().mean()
            if not torch.isfinite(loss):raise ValueError('Nonfinite extension loss')
            loss.backward();torch.nn.utils.clip_grad_norm_(owner.parameters(),3.,error_if_nonfinite=True)
            optimizer.step();step+=1
            row={'step':step,'rank':rank,'loss':float(loss.detach()),'systems':16,'query_targets':256}
            log.write(json.dumps(row)+'\n')
            if step%128==0:
                log.flush();print(json.dumps(row),flush=True)
                write_json(root/'PROGRESS.json',{**row,'target':2048,'updated_utc':utc(),
                                                'seconds_this_invocation':time.monotonic()-started})
            assessment=development(owner) if step%256==0 else None
            if assessment:dev.append({'step':step,**assessment})
            if step%128==0:
                revision=save()
                if assessment and assessment['mse']<best['score']:
                    best={**revision,'step':step,'score':assessment['mse']};write_json(root/'SELECTION.json',best)
            if (STUDY/'PAUSE_REQUEST.json').exists():write_json(root/'PAUSED.json',save());return
    write_json(root/'COMPLETE.json',{'steps':step,'systems':step*16,'adaptation_rows':step*16*24,
        'teaching_query_targets':step*16*16,'selected':best,'development':dev,'parent':parent_selection})


def register():
    if (STUDY/'FINAL_REGISTRATION.json').exists():return
    if not (STUDY/'learned/COMPLETE.json').exists():raise ValueError('Teaching is unfinished')
    write_json(STUDY/'FINAL_REGISTRATION.json',{'selected':{arm:sha256(STUDY/arm/'SELECTION.json')
        for arm in ('learned','fixed')},'source':sha256(ROOT/'sera_field/extension_world.py'),
        'protocol':sha256(ROOT/'protocols/GROW-013.md'),'created_utc':utc()})


@torch.no_grad()
def evaluate(arm,replay=False):
    from scipy.integrate import solve_ivp
    registered=json.loads((STUDY/'FINAL_REGISTRATION.json').read_text())
    selected='learned' if arm=='no_extension' else arm
    assert sha256(STUDY/selected/'SELECTION.json')==registered['selected'][selected]
    owner,selection=load_extension(STUDY/selected);owner.eval();before=weight_hash(owner)
    output=STUDY/('replay' if replay else 'final')/arm;output.mkdir(parents=True,exist_ok=True)
    if (output/'RESULTS.json').exists():return
    results=[]
    for omitted,count in ((False,256),(True,128)):
        for index in range(count):
            world,a,c,q=episode(index,'GROW-013-final-v1',omitted=omitted)
            if arm=='no_extension':
                model=owner.extend_model(torch.from_numpy(a)[None],torch.ones(1,len(a)),0)
                assessment={'selected_rank':0,'qualification':'protected four-feature control'}
            else:model,assessment=owner.acquire_extension(torch.from_numpy(a)[None],torch.from_numpy(c)[None])
            goal={'index':index,'queries':q.tolist(),'name':'acquire-mechanism-return-to-original-goal'}
            assessment={**assessment,'calibration_observations':c.tolist(),
                         'calibration_evidence_id':identity(['calibration',index,omitted,c.tolist()])}
            concept=tasks.serialize_model(owner,model,assessment,
                evidence_ids=[identity(['adaptation',index,omitted,i,row.tolist()]) for i,row in enumerate(a)],
                original_goal=goal)
            prediction=tasks.predict(concept,q).mean(0);truth=world.observe(q[:,0],q[:,1])
            v=float(q[0,0]);target=float(world.observe(v,q[0,1]))
            solution=tasks.inverse(concept,v,target)
            cf=q.copy();cf[:,1]+=.4
            imagined_difference=tasks.predict(concept,cf).mean(0)-prediction
            actual_difference=world.observe(cf[:,0],cf[:,1])-truth
            # Independent DOP853 goals and outcomes never enter fitted weights.
            solve=lambda u:solve_ivp(lambda t,y:[y[1],world.observe(y[1],u)],(0,.4),[0.,0.],
                    method='DOP853',rtol=1e-10,atol=1e-12).y[:,-1]
            target_endpoint=solve(float(q[1,1]));plan=tasks.plan(concept,target_endpoint)
            receipt=world.intervene([v,solution['input']],scale=.7 if index%41==40 else 1.)
            point=q[2].copy();point[1]=min(float(point[1]),1.5)
            explanation=tasks.explain(owner,concept,'What happens when the control input increases?',point)
            changed=point.copy();changed[1]+=.5
            delta=float(world.observe(*changed)-world.observe(*point))
            direction=2 if delta>.08 else 0 if delta<-.08 else 1
            result={'index':index,'omitted':omitted,'rank':model['rank'],'concept_id':concept['concept_id'],
                'forward_mse':float(np.mean((prediction-truth)**2)),
                'inverse_outcome_error':float((world.observe(v,solution['input'])-target)**2),
                'counterfactual_mse':float(np.mean((imagined_difference-actual_difference)**2)),
                'planning_mse':float(np.mean((solve(plan['input'])-target_endpoint)**2)),
                'direction_correct':explanation['direction']==direction,'inverse':solution,'plan':plan,
                'explanation':explanation,'intervention':receipt,'assessment':assessment,
                'original_goal_returned':True,'forward_predictions':prediction.tolist(),'forward_outcomes':truth.tolist()}
            results.append(result)
            if index<4:
                write_json(output/f'concept-{omitted}-{index}.json',concept)
    summary={'arm':arm,'selection':selection,'weights_before':before}
    for omitted in (False,True):
        rows=[r for r in results if r['omitted']==omitted]
        summary['omitted' if omitted else 'supported']={'n':len(rows),
            **{key:float(np.mean([r[key] for r in rows])) for key in
                ('forward_mse','inverse_outcome_error','counterfactual_mse','planning_mse','direction_correct')},
            'ranks':{str(k):sum(r['rank']==k for r in rows) for k in (0,4,8,16)},
            'unmatched_actuation':sum(not r['intervention']['actuation_matched'] for r in rows)}
    raw=''.join(json.dumps(r,sort_keys=True)+'\n' for r in results)
    (output/'cases.jsonl').write_text(raw,encoding='utf-8');summary['cases_sha256']=sha256(output/'cases.jsonl')
    assert weight_hash(owner)==before;summary['weights_after']=before
    write_json(output/'RESULTS.json',summary);print(json.dumps(summary),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('train','register','evaluate'))
    parser.add_argument('--arm',choices=('learned','fixed','no_extension'),default='learned')
    parser.add_argument('--replay',action='store_true');args=parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1);STUDY.mkdir(parents=True,exist_ok=True)
    if args.action=='train':train()
    elif args.action=='register':register()
    else:evaluate(args.arm,args.replay)


if __name__=='__main__':main()
