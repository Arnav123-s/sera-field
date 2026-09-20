"""Actual acquired-model -> generated probe -> outcome -> local credit -> answer."""
import argparse
import copy
import json
import os
from pathlib import Path
import time

import numpy as np
import torch

from .concept_owner import basis
from .credit_bridge import CheckedOutcome,identity
from .extension_study import load_extension
from .extension_world import episode
from .fusion_inquiry import measurement_candidates,LocalCreditBridge
from .inquiry_owner import InquiryOwner,extend_inquiry
from .model import weight_hash
from .records import sha256,write_json,utc
from .study_data import ROOT

STUDY=ROOT/'runs/INQUIRY-014'
PARENT=ROOT/'runs/GROW-013/learned'


def load_inquiry(root):
    root=Path(root);selection=json.loads((root/'SELECTION.json').read_text())
    path=root/'revisions'/selection['revision']
    if path.resolve().parent!=(root/'revisions').resolve() or sha256(path)!=selection['sha256']:
        raise ValueError('Inquiry source identity mismatch')
    payload=torch.load(path,map_location='cpu',weights_only=False)
    spec=dict(payload['bridge']['specification']);kind=spec.pop('type')
    if kind!='local-inquiry-014':raise ValueError('Wrong inquiry owner')
    owner=InquiryOwner(**spec);owner.load_state_dict(payload['bridge']['owner'])
    if weight_hash(owner)!=selection['weights']:raise ValueError('Inquiry state identity mismatch')
    return owner,selection


class Investigator:
    def __init__(self,owner,*,learning=True):
        self.owner=owner;self.learning=learning
        for name,p in owner.named_parameters():p.requires_grad_(name.startswith('imagination_policy.'))
        self.source=sha256(ROOT/'sera_field/extension_world.py');self.verifier=sha256(__file__)
        self.book=LocalCreditBridge(owner,learning_rate=.02 if learning else 0.,
                                    source_hashes=[self.source],verifier_hashes=[self.verifier])
        self.cursor=0;self.parent=None

    @torch.no_grad()
    def feature_information(self,model,queries,probes):
        owner=self.owner
        def feature(x):
            phi=basis(x)
            if model['rank']:
                residual=owner.feature(x,model['context'],model['rank'])-phi@model['projection']
                phi=torch.cat((phi,residual),-1)
            return phi[0]
        x=feature(model['observations'][...,:2]);g=feature(queries);p=feature(probes)
        covariance=torch.linalg.inv(x.T@x+.03*torch.eye(x.shape[1]))
        benefit=(g@covariance@p.T).square().sum(0)/(1+(p@covariance*p).sum(-1))
        return int(benefit.argmax())

    def attempt(self,index,split,*,train=True,policy='learned',omitted=False):
        world,adaptation,calibration,queries=episode(index,split,omitted=omitted)
        support=torch.from_numpy(adaptation[:8])[None];calib=torch.from_numpy(calibration)[None]
        query=torch.from_numpy(queries)[None]
        goal=identity([split,index,omitted,queries.tolist()]);events=[]
        model,assessment=self.owner.acquire_extension(support,calib)
        initial=None;final=None
        for t in range(3):
            with torch.no_grad():
                before=self.owner.predict_model(model,query).mean(1)[0]
                inputs=self.owner.investigation_inputs(model,support)
                mean=self.owner.imagination_policy.reference(inputs)
                sampled=mean+.7*torch.randn(2)
            branches=measurement_candidates(sampled)
            # Merge coordinate aliases but retain every branch and its probability.
            unique={}
            for branch in branches:
                if branch['probe'] is None:continue
                key=tuple(round(x,7) for x in branch['probe'])
                entry=unique.setdefault(key,{'probe':branch['probe'],'probability':0.,'methods':[]})
                entry['probability']+=branch['probability'];entry['methods'].append(branch['method'])
            options=list(unique.values());probability=torch.tensor([r['probability'] for r in options])
            choice=int(torch.multinomial(probability,1))
            if policy=='uniform':
                requested=(4*torch.rand(2)-2).tolist();method='uniform-probe'
            elif policy=='information':
                candidates=torch.tensor([r['probe'] for r in options],dtype=torch.float32)[None]
                choice=self.feature_information(model,query,candidates)
                requested=options[choice]['probe'];method='learned-feature-information'
            else:
                requested=options[choice]['probe'];method=identity(sorted(set(options[choice]['methods'])))
            predictor=weight_hash(self.owner);decision=identity([goal,t,policy])
            if train:
                _,trace=self.owner.imagination_policy.eligibility(inputs,sampled)
                self.book.record_local_score(decision=decision,goal=goal,predictor=predictor,
                    assumptions_id='scoped-generated-investigation-v1',sample=sampled,
                    trace={'imagination_policy.'+k:v for k,v in trace.items()})
            with torch.no_grad():
                imagined=self.owner.predict_model(model,torch.tensor([requested],dtype=torch.float32)[None])[0,:,0].tolist()
            # All generated alternatives and the chosen conditional prediction
            # exist before the actual intervention or goal outcomes are obtained.
            receipt=world.intervene(requested,scale=.7 if index%41==40 and t==1 else 1.)
            support=torch.cat((support,torch.tensor([[receipt['observation']]],dtype=torch.float32)),1)
            revised,revision_assessment=self.owner.acquire_extension(support,calib)
            with torch.no_grad():after=self.owner.predict_model(revised,query).mean(1)[0]
            truth=torch.from_numpy(world.observe(queries[:,0],queries[:,1]).astype('float32'))
            old_loss=float((before-truth).square().mean());new_loss=float((after-truth).square().mean())
            if initial is None:initial=old_loss
            final=new_loss
            evidence=identity([self.source,split,index,omitted,t,receipt])
            outcome=CheckedOutcome(goal,decision,predictor,predictor,evidence,self.source,self.verifier,
                identity([evidence,queries.tolist(),truth.tolist()]),'independent_simulation',
                identity(receipt['requested']),identity(receipt['performed']),old_loss,new_loss,True,
                identity([method,model['rank'],revised['rank']]),'scoped-generated-investigation-v1')
            event=None;capture=None
            if train:
                event=self.book.apply(outcome)
                if not event['accepted']:self.book.retire(decision,event['reason'])
                elif self.learning and new_loss<old_loss:
                    tag=self.owner.field.last_source[0].clone()
                    capture=self.owner.field.memory.capture(tag,event,predictor=predictor,decision_policy=predictor)
            events.append({'step':t,'branches':branches,'distinct_probes':len(options),
                'requested':requested,'imagined_responses':imagined,'receipt':receipt,
                'before_mse':old_loss,'after_mse':new_loss,'event':event,'capture':capture,
                'representation':revision_assessment,'cost':{'measurement_branches':24,
                    'charge_projections':72,'performed_probes':1,'goal_outcomes':len(queries)}})
            model,assessment=revised,revision_assessment
        self.cursor=index+1
        return {'index':index,'split':split,'omitted':omitted,'goal':goal,'events':events,
                'initial_mse':initial,'final_mse':final,'returned_answer':after.tolist(),
                'independent_outcomes':truth.tolist(),'original_goal_returned':True}

    def save(self,root,progress):
        saved=self.book.commit(root,expected_parent=self.parent,progress={**progress,'cursor':self.cursor})
        self.parent=saved['sha256'];return saved


@torch.no_grad()
def development(owner):
    # The fork preserves the training RNG and only the temporary controller's
    # cursor changes; no developmental reward or memory write is performed.
    with torch.random.fork_rng():
        torch.manual_seed(1411401);agent=Investigator(owner,learning=False)
        rows=[agent.attempt(i,'INQUIRY-014-development-v1',train=False) for i in range(64)]
    return {'mse':float(np.mean([r['final_mse'] for r in rows])),
            'initial_mse':float(np.mean([r['initial_mse'] for r in rows])),'n':64}


def train(arm):
    root=STUDY/arm;root.mkdir(parents=True,exist_ok=True)
    if (root/'COMPLETE.json').exists():load_inquiry(root);return
    parent,parent_selection=load_extension(PARENT);owner=extend_inquiry(parent)
    agent=Investigator(owner,learning=arm=='learned');torch.manual_seed(14114)
    selected=None;history=[]
    if (root/'revisions/CURRENT.json').exists():
        saved=agent.book.load_current(root/'revisions');agent.parent=saved['sha256'];p=saved['progress']
        if p['parent_selection']!=parent_selection:raise ValueError('Parent changed while resuming')
        agent.cursor=p['cursor'];selected=json.loads((root/'SELECTION.json').read_text());history=p['history']
    else:
        assessment=development(owner);history.append({'cursor':0,**assessment})
        saved=agent.save(root/'revisions',{'history':history,'parent_selection':parent_selection})
        selected={**saved,'score':assessment['mse'],'step':0};write_json(root/'SELECTION.json',selected)
    start=time.monotonic();invocation=os.environ['SERA_FIELD_SUPERVISED']
    with (root/('episodes-'+invocation+'.jsonl')).open('x',encoding='utf-8') as log:
        while agent.cursor<1024:
            row=agent.attempt(agent.cursor,'INQUIRY-014-teaching-v1');log.write(json.dumps(row)+'\n')
            if agent.cursor%64==0:
                log.flush();print(json.dumps({'arm':arm,'episodes':agent.cursor,'last_mse':row['final_mse']}),flush=True)
                write_json(root/'PROGRESS.json',{'episodes':agent.cursor,'target':1024,'updated_utc':utc(),
                    'captures':int(owner.field.memory.cursor),'seconds_this_invocation':time.monotonic()-start})
            assessment=development(owner) if agent.cursor%256==0 else None
            if assessment:history.append({'cursor':agent.cursor,**assessment})
            if agent.cursor%64==0:
                saved=agent.save(root/'revisions',{'history':history,'parent_selection':parent_selection})
                if assessment and assessment['mse']<selected['score']:
                    selected={**saved,'score':assessment['mse'],'step':agent.cursor};write_json(root/'SELECTION.json',selected)
            if (STUDY/'PAUSE_REQUEST.json').exists():
                write_json(root/'PAUSED.json',agent.save(root/'revisions',{'history':history,'parent_selection':parent_selection}));return
    write_json(root/'COMPLETE.json',{'episodes':agent.cursor,'attempted_probes':agent.cursor*3,
        'goal_outcome_evaluations':agent.cursor*48,'all_captures':int(owner.field.memory.cursor),
        'selected':selected,'history':history,'parent':parent_selection})


def register():
    if (STUDY/'FINAL_REGISTRATION.json').exists():return
    for arm in ('learned','disconnected'):
        if not (STUDY/arm/'COMPLETE.json').exists():raise ValueError('Teaching unfinished')
    write_json(STUDY/'FINAL_REGISTRATION.json',{'selections':{arm:sha256(STUDY/arm/'SELECTION.json')
        for arm in ('learned','disconnected')},'parent':sha256(PARENT/'SELECTION.json'),
        'protocol':sha256(ROOT/'protocols/INQUIRY-014.md'),'created_utc':utc()})


def evaluate(arm,replay=False):
    registered=json.loads((STUDY/'FINAL_REGISTRATION.json').read_text())
    if arm in ('learned','disconnected','retained_parent_memory'):
        selected_arm='learned' if arm=='retained_parent_memory' else arm
        assert sha256(STUDY/selected_arm/'SELECTION.json')==registered['selections'][selected_arm]
        owner,selected=load_inquiry(STUDY/selected_arm);policy='learned'
        if arm=='retained_parent_memory':
            parent,_=load_extension(PARENT)
            owner.field.memory.load_state_dict(parent.field.memory.state_dict())
    else:
        parent,_=load_extension(PARENT);owner=extend_inquiry(parent);selected={'role':'identical initialized owner'}
        policy=arm if arm in ('uniform','information') else 'learned'
    before=weight_hash(owner);torch.manual_seed(1411402)
    agent=Investigator(owner,learning=False)
    output=STUDY/('replay' if replay else 'final')/arm;output.mkdir(parents=True,exist_ok=True)
    if (output/'RESULTS.json').exists():return
    rows=[agent.attempt(i,'INQUIRY-014-final-v1',train=False,policy=policy,omitted=omitted)
          for omitted,count in ((False,128),(True,64)) for i in range(count)]
    raw=''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows)
    (output/'cases.jsonl').write_text(raw,encoding='utf-8')
    summary={'arm':arm,'selection':selected,'weights_before':before,'cases_sha256':sha256(output/'cases.jsonl')}
    for omitted in (False,True):
        cases=[r for r in rows if r['omitted']==omitted]
        summary['omitted' if omitted else 'supported']={'n':len(cases),
            'initial_mse':float(np.mean([r['initial_mse'] for r in cases])),
            'final_mse':float(np.mean([r['final_mse'] for r in cases])),
            'all_goals_returned':all(r['original_goal_returned'] for r in cases),
            'performed_probes':len(cases)*3,
            'mean_distinct_proposals':float(np.mean([e['distinct_probes'] for r in cases for e in r['events']])),
            'actuation_mismatches':sum(not e['receipt']['actuation_matched'] for r in cases for e in r['events'])}
    assert weight_hash(owner)==before;summary['weights_after']=before
    write_json(output/'RESULTS.json',summary);print(json.dumps(summary),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('train','register','evaluate'))
    parser.add_argument('--arm',default='learned',choices=('learned','disconnected','initialized','uniform','information','retained_parent_memory'))
    parser.add_argument('--replay',action='store_true');args=parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1);STUDY.mkdir(parents=True,exist_ok=True)
    if args.action=='train':train(args.arm)
    elif args.action=='register':register()
    else:evaluate(args.arm,args.replay)


if __name__=='__main__':main()
