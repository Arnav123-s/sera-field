"""Prospective acquisition teaching, five-use assessment and checked rewards."""
import argparse
import json
import os
from pathlib import Path
import random

import numpy as np
import torch
from torch.nn import functional as F

from .concept_owner import (ConceptOwner, continue_owner, TRAIN_PHRASES, TRANSFER_PHRASES,
                            acquire, explain, inverse_input, numpy_predict, plan)
from .concept_world import case, direction
from .credit_bridge import CreditBridge, CheckedOutcome, identity
from .model import weight_hash
from .records import sha256, write_json
from .study_data import ROOT
from .study_inquiry import load_selected, observation_tensors
from .study_world import probes, analytic_probe

STUDY=ROOT/'runs/CONCEPT-008'
PARENT=ROOT/'checkpoints/ECHO-007'
NEW=('acquisition.','question_route.','meaning.')
SEED=8108


def batch(indices,split,transfer=False):
    observed=torch.zeros(len(indices),12,3); mask=torch.zeros(len(indices),12)
    queries=[];truth=[];routes=[];labels=[];phrases=[]
    for j,i in enumerate(indices):
        w,s,q=case(SEED,i,split)
        observed[j,:len(s)]=torch.from_numpy(s);mask[j,:len(s)]=1
        queries.append(q);truth.append(w.observe(q[:,0],q[:,1]))
        route=i%2;routes.append(route);labels.append(direction(w,q[0],route))
        bank=(TRANSFER_PHRASES if transfer else TRAIN_PHRASES)[route]
        phrases.append(bank[(i//2)%len(bank)])
    return observed,mask,torch.tensor(np.stack(queries)),torch.tensor(np.stack(truth),dtype=torch.float32),torch.tensor(routes),torch.tensor(labels),phrases


def objective(owner,indices,split,transfer=False):
    o,m,q,y,r,d,p=batch(indices,split,transfer)
    world=owner.world(o,m)
    prediction=owner.consequences(world['coefficients'],q)
    error=(prediction.mean(1)-y).square().mean()
    language=owner.directional_logits(world['coefficients'],q[:,0],r)
    route=owner.route_logits(p)
    loss=error+.3*F.cross_entropy(language,d)+.1*F.cross_entropy(route,r)
    return loss,{'mse':float(error.detach()),'direction':float((language.argmax(-1)==d).float().mean()),
                 'route':float((route.argmax(-1)==r).float().mean())}


def development(owner):
    owner.eval()
    metrics=[]
    with torch.no_grad():
        for i in range(0,256,32):
            _,m=objective(owner,list(range(i,i+32)),'CONCEPT-008-development',True);metrics.append(m)
    mean={k:float(np.mean([m[k] for m in metrics])) for k in metrics[0]}
    return {**mean,'score':mean['mse']+.05*(1-mean['direction'])+.05*(1-mean['route'])}


class Engine:
    def __init__(self,kind):
        parent,self.parent_selection=load_selected(PARENT)
        self.owner=continue_owner(parent,kind)
        self.optimizer=torch.optim.AdamW([p for p in self.owner.parameters() if p.requires_grad],lr=.002,weight_decay=.0001)
        self.book=CreditBridge(self.owner,source_hashes=[sha256(ROOT/'sera_field/concept_world.py')],
                               verifier_hashes=[sha256(__file__)])
        self.step=0;self.parent=None;self.best=None;self.development=[]
        self.initial=weight_hash(self.owner);self.kind=kind
        self.protected={k:v.clone() for k,v in parent.state_dict().items()}

    def update(self,n=24):
        self.owner.train();self.optimizer.zero_grad(set_to_none=True)
        loss,m=objective(self.owner,list(range(self.step*n,(self.step+1)*n)),'CONCEPT-008-teaching')
        if not torch.isfinite(loss):raise ValueError('Nonfinite teaching loss')
        loss.backward();torch.nn.utils.clip_grad_norm_(self.owner.parameters(),3.,error_if_nonfinite=True)
        self.optimizer.step();self.step+=1
        return {'step':self.step,'loss':float(loss.detach()),**m}

    def save(self,root):
        r=self.book.commit(root,expected_parent=self.parent,progress={'step':self.step,'kind':self.kind,
            'teaching_optimizer':self.optimizer.state_dict(),'best':self.best,'development':self.development,
            'initial_weights':self.initial,'parent_selection':self.parent_selection})
        self.parent=r['sha256'];return r

    def resume(self,root):
        r=self.book.load_current(root);p=r['progress']
        if p['kind']!=self.kind or p['parent_selection']!=self.parent_selection:raise ValueError('Changed teaching identity')
        self.step=p['step'];self.best=p['best'];self.development=p['development'];self.initial=p['initial_weights']
        self.optimizer.load_state_dict(p['teaching_optimizer']);self.parent=r['sha256']


def train(kind):
    root=STUDY/kind;root.mkdir(parents=True,exist_ok=True)
    if (root/'COMPLETE.json').exists():return
    e=Engine(kind)
    if (root/'revisions/CURRENT.json').exists():e.resume(root/'revisions')
    def assess():
        dev=development(e.owner);r=e.save(root/'revisions')
        item={'step':e.step,**dev,'weights':weight_hash(e.owner)}
        e.development.append(item)
        if e.best is None or dev['score']<e.best['score']:
            e.best={**r,'step':e.step,'score':dev['score']}
            write_json(root/'SELECTION.json',e.best)
        print(json.dumps({'arm':kind,'development':item}),flush=True)
    if not e.development:assess()
    with (root/('training-'+os.environ['SERA_FIELD_SUPERVISED']+'.jsonl')).open('a',encoding='utf-8') as log:
        while e.step<4096:
            log.write(json.dumps(e.update())+'\n')
            if e.step%128==0:
                log.flush()
                if e.step%512==0:assess()
                e.save(root/'revisions')
    changed=[k for k,v in e.protected.items() if not torch.equal(v,e.owner.state_dict()[k])]
    if changed:raise ValueError('Protected parent changed: '+repr(changed))
    write_json(root/'COMPLETE.json',{'arm':kind,'steps':e.step,'system_presentations':e.step*24,
        'independent_simulation_labels':True,'new_human_records':0,'selected':e.best,'development':e.development,
        'old_parameters_exact':not changed,'initial_weights':e.initial,'final_weights':weight_hash(e.owner)})


def ridge(s):
    v,u=s[:,0],s[:,1]
    x=np.stack((u,v,v*abs(v),np.ones(len(v))),-1)
    c=np.linalg.solve(x.T@x+np.eye(4)*.01,x.T@s[:,2])
    return np.repeat(c[None],3,axis=0)


def assess_cases(arm,root,*,training=None,experiment='CONCEPT-008',phrase_bank=TRANSFER_PHRASES):
    root.mkdir(parents=True,exist_ok=True)
    if (root/'RESULTS.json').exists():return
    owner,selected=load_selected(training or (PARENT if arm in ('parent','ridge') else STUDY/arm))
    owner.eval();before=weight_hash(owner);records=[];metrics={}
    for omitted,n in ((False,512),(True,128)):
        subset=[]
        for i in range(n):
            w,s,q=case(SEED,i,experiment+'-final-'+('omitted' if omitted else 'supported'),omitted=omitted)
            concept=acquire(owner,s,before,[identity([experiment,omitted,i,j,s[j].tolist()]) for j in range(len(s))])
            if arm=='ridge':
                concept['coefficients']=ridge(s).tolist()
                concept['concept_id']=identity(concept)
            c=np.asarray(concept['coefficients'])
            forward=numpy_predict(c,q).mean(0)
            y=w.observe(q[:,0],q[:,1])
            cf=q.copy();cf[:,0]+=.6;cf[:,1]-=.4
            imagined=numpy_predict(c,cf).mean(0);cf_truth=w.observe(cf[:,0],cf[:,1])
            inverse=inverse_input(c,float(q[0,0]),float(y[0]))
            inverse_error=(inverse['mean']-float(q[0,1]))**2 if inverse['mean'] is not None else 100.
            target_input=float(q[1,1]*.8);target=w.endpoint(target_input)
            proposal=plan(c,target)
            outcome=w.endpoint(proposal['input'])
            route=i%2;phrases=phrase_bank[route];question=phrases[(i//2)%len(phrases)]
            explanation=explain(owner,concept,question,q[0]) if isinstance(owner,ConceptOwner) else None
            direction_ok=(explanation['learned_route']==route and explanation['direction']==direction(w,q[0],route)) if explanation else None
            record={'index':i,'omitted':omitted,'concept':concept,'all_five_views_concept_id':concept['concept_id'],
                'forward':{'queries':q.tolist(),'predicted':forward.tolist(),'independent':y.tolist()},
                'inverse':{'velocity':float(q[0,0]),'desired_acceleration':float(y[0]),'proposal':inverse,'independent_input':float(q[0,1])},
                'counterfactual':{'queries':cf.tolist(),'predicted':imagined.tolist(),'independent':cf_truth.tolist()},
                'plan':{'target':target.tolist(),'proposal':proposal,'independent_outcome':outcome.tolist()},
                'language':explanation,'metrics':{'forward_mse':float(np.mean((forward-y)**2)),
                    'counterfactual_mse':float(np.mean((imagined-cf_truth)**2)),'inverse_mse':float(inverse_error),
                    'plan_mse':float(np.mean((outcome-target)**2)),'direction_correct':direction_ok,
                    'route_correct':explanation['learned_route']==route if explanation else None,
                    'residual_flag':float(np.mean((forward-y)**2))>.05,'cloud_spread':float(np.std(numpy_predict(c,q),axis=0).mean())}}
            records.append(record);subset.append(record['metrics'])
        metrics['omitted' if omitted else 'supported']={k:float(np.mean([m[k] for m in subset])) if subset[0][k] is not None else None for k in subset[0]}
    assert weight_hash(owner)==before
    with (root/'cases.jsonl').open('x',encoding='utf-8') as f:
        for r in records:f.write(json.dumps(r,allow_nan=False)+'\n')
    write_json(root/'RESULTS.json',{'arm':arm,'selection':selected,'metrics':metrics,'weights_immutable':True,
                                  'case_counts':{'supported':512,'omitted':128},'cases_sha256':sha256(root/'cases.jsonl')})


class Inquiry:
    def __init__(self,training,*,reward):
        self.owner,self.selected=load_selected(training);self.predictor=weight_hash(self.owner)
        for name,p in self.owner.named_parameters():p.requires_grad_(name.startswith('investigation.'))
        self.source=sha256(ROOT/'sera_field/concept_world.py');self.verifier=sha256(__file__)
        self.book=CreditBridge(self.owner,learning_rate=.04 if reward else 0.,
            source_hashes=[self.source],verifier_hashes=[self.verifier])
        self.rng=torch.Generator().manual_seed(8119);self.cursor=0;self.parent=None;self.best=None;self.dev=[]

    def attempt(self,i,split,*,policy='learned',train=False):
        w,s,q=case(8119,i,split,inquiry=True)
        options=probes();query=torch.from_numpy(q)[None]
        logits,world=self.owner.probe_logits(*observation_tensors(s),torch.from_numpy(options)[None],query)
        distribution=logits[0].softmax(-1)
        if policy=='random':choice=int(np.random.default_rng(i+8119).integers(len(options)))
        elif policy=='analytic':choice=analytic_probe(s,options,q)
        elif train:choice=int(torch.multinomial(distribution.detach(),1,generator=self.rng))
        else:choice=int(distribution.argmax())
        before=self.owner.consequences(world['coefficients'],query)[0].mean(0).detach().numpy()
        goal=identity([split,i,q.tolist()]);decision=identity([split,i,policy])
        commit={'goal':goal,'decision':decision,'predictor':self.predictor,'policy':weight_hash(self.owner),
                'support':s.tolist(),'queries':q.tolist(),'prediction':before.tolist(),'choice':options[choice].tolist()}
        scope='CONCEPT-008-calibrated-drive-basis'
        if train:self.book.record_decision(decision=decision,goal=goal,logits=logits[0],choice=choice,predictor=self.predictor,assumptions_id=scope)
        receipt=w.intervene(options[choice],scale=.7 if i%41==40 else 1.)
        revised=np.vstack((s,receipt['observation'])).astype('float32')
        with torch.no_grad():
            state=self.owner.world(*observation_tensors(revised))
            after=self.owner.consequences(state['coefficients'],query)[0].mean(0).numpy()
        truth=w.observe(q[:,0],q[:,1])
        old_loss=float(np.mean((before-truth)**2));new_loss=float(np.mean((after-truth)**2))
        outcome=CheckedOutcome(goal,decision,commit['policy'],self.predictor,identity([split,i,receipt]),
            self.source,self.verifier,identity([split,i,truth.tolist()]),'independent_simulation',
            identity(receipt['requested']),identity(receipt['performed']),old_loss,new_loss,True,
            'probe:'+identity(receipt['performed']),scope)
        event=None
        if train:
            event=self.book.apply(outcome)
            if not event['accepted']:self.book.retire(decision,event['reason'])
        self.cursor=i+1
        return {'index':i,'commit':commit,'receipt':receipt,'independent_outcomes':truth.tolist(),
                'before_mse':old_loss,'after_mse':new_loss,'returned_answer':after.tolist(),'event':event}

    def evaluate(self,split,n=128,policy='learned'):
        rows=[self.attempt(i,split,policy=policy) for i in range(n)]
        return rows,{'before_mse':float(np.mean([r['before_mse'] for r in rows])),
                     'after_mse':float(np.mean([r['after_mse'] for r in rows]))}

    def save(self,root):
        r=self.book.commit(root,expected_parent=self.parent,progress={'cursor':self.cursor,'rng':self.rng.get_state(),
            'best':self.best,'dev':self.dev,'predictor':self.predictor})
        self.parent=r['sha256'];return r


def reward(training):
    root=STUDY/'reward';root.mkdir(parents=True,exist_ok=True)
    if (root/'COMPLETE.json').exists():return
    e=Inquiry(training,reward=True)
    if (root/'revisions/CURRENT.json').exists():
        r=e.book.load_current(root/'revisions');p=r['progress']
        e.cursor=p['cursor'];e.rng.set_state(p['rng']);e.best=p['best'];e.dev=p['dev'];e.parent=r['sha256']
        if e.predictor!=p['predictor']:raise ValueError('Changed reward predictor')
    def assess():
        cursor=e.cursor
        with torch.no_grad():_,metric=e.evaluate('CONCEPT-008-reward-development')
        e.cursor=cursor;revision=e.save(root/'revisions')
        e.dev.append({'step':cursor,**metric,'weights':weight_hash(e.owner)})
        if e.best is None or metric['after_mse']<e.best['score']:
            e.best={**revision,'step':cursor,'score':metric['after_mse']}
            write_json(root/'SELECTION.json',e.best)
        print(json.dumps({'reward_development':e.dev[-1],'updates':e.book.updates}),flush=True)
    if not e.dev:assess()
    with (root/('episodes-'+os.environ['SERA_FIELD_SUPERVISED']+'.jsonl')).open('a',encoding='utf-8') as f:
        while e.cursor<2048:
            row=e.attempt(e.cursor,'CONCEPT-008-reward-teaching',train=True);f.write(json.dumps(row)+'\n')
            if e.cursor%128==0:
                f.flush()
                if e.cursor%256==0:assess()
                e.save(root/'revisions')
    write_json(root/'COMPLETE.json',{'episodes':e.cursor,'reward_updates':e.book.updates,'selected':e.best,'development':e.dev})


def inquiry_final(arm,training,root):
    root.mkdir(parents=True,exist_ok=True)
    if (root/'RESULTS.json').exists():return
    e=Inquiry(training,reward=False)
    with torch.no_grad():rows,metrics=e.evaluate('CONCEPT-008-inquiry-final',256,
        policy=arm if arm in ('analytic','random') else 'learned')
    with (root/'cases.jsonl').open('x',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    write_json(root/'RESULTS.json',{'metrics':metrics,'cases_sha256':sha256(root/'cases.jsonl'),
        'all_goals_returned':len(rows)==256,'failed_actuators':sum(not r['receipt']['actuation_matched'] for r in rows)})


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1)
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['train','evaluate','reward','inquiry'])
    p.add_argument('--arm',default='full');p.add_argument('--training',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--experiment',default='CONCEPT-008');p.add_argument('--phrase-bank',type=Path)
    a=p.parse_args()
    if a.mode=='train':train(a.arm)
    elif a.mode=='evaluate':
        phrases=json.loads(a.phrase_bank.read_text())['final'] if a.phrase_bank else TRANSFER_PHRASES
        assess_cases(a.arm,a.output or STUDY/'final'/a.arm,training=a.training,experiment=a.experiment,phrase_bank=phrases)
    elif a.mode=='reward':reward(a.training)
    else:inquiry_final(a.arm,a.training,a.output or STUDY/'inquiry-final'/a.arm)


if __name__=='__main__':main()
