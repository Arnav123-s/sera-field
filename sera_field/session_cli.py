"""Persistent observed-model tasks; immutable goals, receipts and returned answers."""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch

from .concept_owner import append_session, numpy_predict, inverse_input, plan, explain
from .credit_bridge import identity
from .model import weight_hash
from .records import sha256, write_json
from .study_inquiry import load_selected, observation_tensors
from .study_world import probes


def owner_identity(owner):
    return identity({'weights':weight_hash(owner),'specification':owner.specification()})


def load_session(root):
    pointer=json.loads((root/'CURRENT.json').read_text())
    path=root/(pointer['sha256']+'.json')
    if sha256(path)!=pointer['sha256']:raise ValueError('Changed session evidence')
    return json.loads(path.read_text()),pointer['sha256']


def solve(owner,state,task=None):
    concept=state['concept'];c=concept['coefficients']
    task=state['original_goal'] if task is None else task
    if owner_identity(owner)!=state['predictor']:raise ValueError('Session belongs to a different learned owner')
    result={'concept_id':concept['concept_id'],'original_goal':state['original_goal'],'requested_task':task,
            'qualification':'Conditional on the recorded observations and supplied response basis'}
    for name in ('predict','counterfactual'):
        if name in task:
            means=numpy_predict(c,task[name])
            result[name]={'hypotheses':means.tolist(),'mean':means.mean(0).tolist()}
    if 'inverse' in task:
        inv=task['inverse'];result['inverse']=inverse_input(c,inv['velocity'],inv['acceleration'])
    if 'plan' in task:
        item=task['plan'];result['plan']=plan(c,item['target'],item.get('velocity',0.),item.get('duration',.8))
    if 'question' in task:
        result['explanation']=explain(owner,concept,task['question'],task.get('operating_point',[0,0]))
    goal_queries=np.asarray(task.get('predict',[[0,0]]),dtype='float32')
    with torch.no_grad():
        logits,_=owner.probe_logits(*observation_tensors(concept['observations']),
                                    torch.from_numpy(probes())[None],torch.from_numpy(goal_queries)[None])
    choice=probes()[int(logits[0].argmax())].tolist()
    result['next_investigation']={'requested_velocity':choice[0],'requested_control_input':choice[1],
                                  'status':'proposed; obtain an actual outcome before adding evidence'}
    return result


def retain_receipt(root,receipt):
    """Keep source bytes alongside their identity; declarations are not certification."""
    if not receipt.get('source') or receipt.get('kind') not in ('measurement','independent_simulation'):
        raise ValueError('A declared source and measured evidence kind are required')
    rows=np.asarray(receipt['measured'],dtype=float)
    if rows.shape!=(3,) or not np.isfinite(rows).all():raise ValueError('Finite measured row required')
    digest=identity(receipt);path=root/'evidence'/(digest+'.json')
    if path.exists():
        if json.loads(path.read_text())!=receipt:raise ValueError('Evidence identity conflict')
    else:write_json(path,receipt)
    return digest


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    p=argparse.ArgumentParser();p.add_argument('--training',type=Path,default=Path('checkpoints/CONCEPT-011'))
    p.add_argument('--session',type=Path,required=True)
    sub=p.add_subparsers(dest='command',required=True)
    new=sub.add_parser('new');new.add_argument('--input',type=Path,required=True)
    add=sub.add_parser('observe');add.add_argument('--receipt',type=Path,required=True)
    ask=sub.add_parser('ask');ask.add_argument('--task',type=Path,required=True)
    sub.add_parser('solve')
    a=p.parse_args();owner,selected=load_selected(a.training);owner.eval();before=weight_hash(owner);task=None
    predictor=owner_identity(owner)
    if a.command=='new':
        data=json.loads(a.input.read_text(encoding='utf-8'))
        receipts=data['observations']
        if any(not r.get('source') or r.get('kind') not in ('measurement','independent_simulation') for r in receipts):
            raise ValueError('Every row requires a declared source and measured evidence kind')
        rows=[r['measured'] for r in receipts]
        ids=[retain_receipt(a.session,r) for r in receipts]
        state=append_session(a.session,owner,predictor,data['goal'],rows,ids)
    elif a.command=='observe':
        state,current=load_session(a.session)
        receipt=json.loads(a.receipt.read_text(encoding='utf-8'))
        if not receipt.get('source') or receipt.get('kind') not in ('measurement','independent_simulation'):
            raise ValueError('A declared source and measured evidence kind are required')
        evidence=retain_receipt(a.session,receipt)
        state=append_session(a.session,owner,predictor,state['original_goal'],[receipt['measured']],[evidence],current)
    else:
        state,_=load_session(a.session)
        if a.command=='ask':
            task=json.loads(a.task.read_text(encoding='utf-8'))
    result=solve(owner,state,task)
    if weight_hash(owner)!=before:raise ValueError('Task solving altered retained weights')
    output={'checkpoint':selected,'result':result}
    answer=a.session/('answer-'+state['concept']['concept_id']+'-'+identity(result['requested_task'])+'.json')
    if not answer.exists():write_json(answer,output)
    elif json.loads(answer.read_text())!=output:raise ValueError('Repeated answer changed without a new concept')
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
