"""Finite continuing-owner training and untouched-cohort ECHO-007 evaluation."""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import time

import numpy as np
import torch

from .credit_bridge import CreditBridge, identity
from .model import weight_hash
from .records import sha256, write_json, utc
from .reversible_field import EchoOwner
from .study_data import ROOT, load_records
from .study_inquiry import load_selected, observation_tensors, Investigator
from .study_training import (Engine, Curriculum, SCHEDULE, reading_batch, math_batch,
                             pair_batch, physical_batch, pair_inputs)
from .study_evaluation import (cohort, completed_stage, reading_evaluation,
                               math_evaluation, summarize_inquiry)
from .study_world import draw, stable_seed, trajectory
from .learned_motion import rollout

STUDY=ROOT/'runs/ECHO-007'
DATA=ROOT/'local/CONNECTED-003-data-v1'
PARENT=ROOT/'checkpoints/SCFE-004'
ARMS=('echo','autograd','no_core_credit')


class EchoEngine(Engine):
    def __init__(self,data,arm):
        super().__init__(data,seed=7107,owner_kind='scfe')
        parent,self.parent_selection=load_selected(PARENT)
        self.owner=EchoOwner(**parent.config,backend=arm)
        self.owner.load_state_dict(parent.state_dict())
        for name,p in self.owner.named_parameters():
            p.requires_grad_(not name.startswith('investigation.'))
        self.initial_hash=weight_hash(self.owner)
        self.optimizer=torch.optim.AdamW(self.owner.parameters(),lr=.0003,weight_decay=.0001)
        self.book=CreditBridge(self.owner,verifier_hashes=[sha256(ROOT/'sera_field/study_world.py')],
                               source_hashes=[data.manifest_sha,sha256(ROOT/'sera_field/study_world.py')])
        random.seed(self.seed);np.random.seed(self.seed);torch.manual_seed(self.seed)
        self.initial_field={k:v.clone() for k,v in self.owner.field.state_dict().items()}

    def update(self,batch=24):
        if SCHEDULE[self.step%len(SCHEDULE)]!='physics':
            return super().update(batch)
        self.owner.train();self.optimizer.zero_grad(set_to_none=True)
        indices=list(range(self.physics_cursor,self.physics_cursor+batch))
        self.physics_cursor+=batch;self.exposures['physical_simulation']+=batch
        loss,mse=physical_batch(self.owner,self.seed,indices,'ECHO-007-teaching-v1')
        if not torch.isfinite(loss): raise ValueError('Nonfinite teaching loss')
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.owner.parameters(),3.,error_if_nonfinite=True)
        self.optimizer.step();self.step+=1
        return {'step':self.step,'kind':'physics','loss':float(loss.detach()),
                'correct_or_physics_mse':mse,'attempts':batch}

    @torch.no_grad()
    def evaluate(self):
        self.owner.eval();results={}
        for kind,fn in (('reading',reading_batch),('math',math_batch)):
            rows=cohort(self.data.dev[kind],128,'ECHO-007-development-v1:'+kind)
            total,correct=0.,0
            for start in range(0,len(rows),16):
                part=rows[start:start+16];loss,count=fn(self.owner,part)
                total+=float(loss)*len(part);correct+=count
            results[kind]={'loss':total/len(rows),'accuracy':correct/len(rows),'n':len(rows)}
        for track,bank in sorted(self.data.dev_pairs.items()):
            rows=cohort(bank,32,'ECHO-007-development-v1:'+track)
            rng=random.Random(stable_seed('ECHO-007-development',track))
            total,correct=0.,0
            for start in range(0,len(rows),16):
                part=rows[start:start+16];loss,count=pair_batch(self.owner,part,bank,rng)
                total+=float(loss)*len(part);correct+=count
            results['pair:'+track]={'loss':total/len(rows),'accuracy':correct/len(rows),'n':len(rows)}
        errors=[physical_batch(self.owner,self.seed,list(range(i,i+32)),
                               'ECHO-007-development-v1')[1] for i in range(0,128,32)]
        results['physics']={'loss':float(np.mean(errors)),'n':128}
        if self.initial_dev is None:self.initial_dev=copy.deepcopy(results)
        ratios={k:v['loss']/max(1e-8,self.initial_dev[k]['loss']) for k,v in results.items()}
        score=(ratios['reading']+ratios['math']+ratios['physics']+
               np.mean([v for k,v in ratios.items() if k.startswith('pair:')]))/4
        record={'step':self.step,'score':float(score),'metrics':results,'weights':weight_hash(self.owner)}
        self.development.append(record);return record


def train(arm):
    root=STUDY/arm;root.mkdir(parents=True,exist_ok=True)
    if (root/'COMPLETE.json').exists():
        load_selected(root);print(arm+' already complete; validated without restarting',flush=True);return
    engine=EchoEngine(Curriculum(DATA),arm)
    if (root/'revisions/CURRENT.json').exists():engine.resume(root/'revisions')
    else:
        initial=engine.evaluate();manifest=engine.save(root/'revisions')
        engine.best={**manifest,'score':initial['score'],'step':0}
        write_json(root/'INITIAL.json',{'weights':engine.initial_hash,'parent':engine.parent_selection,'development':initial})
        write_json(root/'SELECTION.json',engine.best)
    invocation=os.environ['SERA_FIELD_SUPERVISED'];start=time.monotonic()
    with (root/('attempts-'+invocation+'.jsonl')).open('x',encoding='utf-8') as log:
        while engine.step<2048:
            result=engine.update();log.write(json.dumps(result)+'\n')
            if engine.step%128==0:
                log.flush();write_json(root/'PROGRESS.json',{'step':engine.step,'target':2048,
                    'exposures':dict(engine.exposures),'unique_human_records':len(engine.seen),
                    'seconds_this_invocation':time.monotonic()-start,'updated_utc':utc()})
                print(json.dumps({'arm':arm,**result}),flush=True)
            assessment=engine.evaluate() if engine.step%512==0 else None
            if engine.step%128==0:
                manifest=engine.save(root/'revisions')
                if assessment and assessment['score']<engine.best['score']:
                    engine.best={**manifest,'score':assessment['score'],'step':engine.step}
                    write_json(root/'SELECTION.json',engine.best)
            if (STUDY/'PAUSE_REQUEST.json').exists():
                manifest=engine.save(root/'revisions');write_json(root/'PAUSED.json',manifest);return
    chosen,_=load_selected(root)
    parent,_=load_selected(PARENT)
    write_json(root/'COMPLETE.json',{'arm':arm,'steps':engine.step,'exposures':dict(engine.exposures),
        'unique_human_records':len(engine.seen),'physical_systems':engine.physics_cursor,
        'selected':engine.best,'initial_weights':engine.initial_hash,'final_weights':weight_hash(engine.owner),
        'selected_field_change_l2':{k:float((v-parent.field.state_dict()[k]).norm()) for k,v in chosen.field.state_dict().items()},
        'investigation_parameters_exactly_retained':all(torch.equal(v,parent.state_dict()[k]) for k,v in chosen.state_dict().items() if k.startswith('investigation.')),
        'development':engine.development})


def final_cohorts(output):
    opened=set(json.loads((ROOT/'reports/CONNECTED-003/evaluations/scfe/OPENED_GROUPS.json').read_text()))
    banks={k:[r for r in load_records(DATA,'sealed',k) if r['group'] not in opened]
           for k in ('reading','math','pairs')}
    reading=cohort(banks['reading'],512,'ECHO-007-final-reading-v1')
    maths=cohort(banks['math'],256,'ECHO-007-final-math-v1')
    tracks=defaultdict(list)
    for r in banks['pairs']:tracks[r['track']].append(r)
    pairs={k:cohort(v,64,'ECHO-007-final-pair:'+k) for k,v in sorted(tracks.items())}
    groups={r['group'] for r in reading+maths+sum(pairs.values(),[])}
    assert not groups&opened
    write_json(output/'OPENED_GROUPS.json',sorted(groups))
    write_json(output/'COHORTS.json',{'reading':[r['id'] for r in reading],
        'math':[r['id'] for r in maths],'pairs':{k:[r['id'] for r in v] for k,v in pairs.items()},
        'prior_opened_groups_excluded':len(opened),'old_final_group_overlap':0})
    return reading,maths,pairs


@torch.no_grad()
def evaluate(arm,replay=False):
    registered=json.loads((STUDY/'FINAL_REGISTRATION.json').read_text())
    root=PARENT if arm=='parent' else STUDY/arm
    assert sha256(root/'SELECTION.json')==registered['selections'][arm]['selection_sha256']
    owner,selection=load_selected(root);owner.eval();before_hash=weight_hash(owner)
    output=STUDY/('replay' if replay else 'final')/arm;output.mkdir(parents=True,exist_ok=True)
    reading,maths,pairs=final_cohorts(output)
    summary={'selection':selection,'weights_before':before_hash}
    def read_cases():
        metrics,rows=reading_evaluation(owner,reading)
        total=sum(float(reading_batch(owner,reading[i:i+16])[0])*len(reading[i:i+16]) for i in range(0,len(reading),16))
        metrics['loss']=total/len(reading);return metrics,rows
    summary['reading']=completed_stage(output,'reading',read_cases)
    def math_cases():
        metrics,rows=math_evaluation(owner,maths)
        total=sum(float(math_batch(owner,maths[i:i+16])[0])*len(maths[i:i+16]) for i in range(0,len(maths),16))
        metrics['loss']=total/len(maths);return metrics,rows
    summary['math']=completed_stage(output,'mathematics',math_cases)
    def pair_cases():
        metrics,records={},[]
        for track,bank in pairs.items():
            if len(bank)<4:
                metrics[track]={'n':len(bank),'status':'Insufficient untouched candidates'};continue
            rng=random.Random(stable_seed('ECHO-007-final-pair',track));loss_sum,correct=0.,0
            for start in range(0,len(bank),16):
                part=bank[start:start+16];questions,options,labels=pair_inputs(part,bank,rng)
                logits=owner.rank(questions,options)
                targets=torch.tensor([t[0] for t in labels])
                loss_sum+=float(torch.nn.functional.cross_entropy(logits,targets,reduction='sum'))
                for r,options_,choice,label in zip(part,options,logits.argmax(-1).tolist(),targets.tolist()):
                    correct+=choice==label
                    records.append({'id':r['id'],'track':track,'candidate_hashes':[identity(t) for t in options_],
                                    'choice':choice,'target':label,'source_sha256':r['source']})
            metrics[track]={'n':len(bank),'accuracy':correct/len(bank),'loss':loss_sum/len(bank)}
        return metrics,records
    summary['pairs']=completed_stage(output,'human-pairs',pair_cases)
    def forward_cases():
        rows=[]
        for i in range(512):
            _,support,queries,truth=draw(7107,i,'ECHO-007-final-v1')
            coefficients=owner.world(*observation_tensors(support))['coefficients']
            predictions=owner.consequences(coefficients,torch.from_numpy(queries)[None])[0]
            rows.append({'index':i,'support':support.tolist(),'queries':queries.tolist(),
                         'hypotheses':predictions.tolist(),'truth':truth.tolist(),
                         'mse':float((predictions.mean(0)-torch.from_numpy(truth)).square().mean())})
        return {'n':len(rows),'mse':float(np.mean([r['mse'] for r in rows]))},rows
    summary['physics']=completed_stage(output,'physics',forward_cases)
    def motion_cases():
        rows=[]
        for i in range(128):
            world,support,queries,_=draw(7107,i,'ECHO-007-final-motion-v1',with_targets=False)
            coefficients=owner.world(*observation_tensors(support))['coefficients'][0].numpy()
            v,f=map(float,queries[0]);prediction=rollout(coefficients,v,f,1.)
            truth=trajectory(world,velocity=v,force_per_mass=f,duration=1.)
            mse=float(np.mean((np.asarray(prediction['position_velocity_mean'])-truth)**2)) if prediction['status']=='completed' else None
            rows.append({'index':i,'prediction':prediction,'independent_DOP853_outcome':truth,'mse':mse})
        valid=[r['mse'] for r in rows if r['mse'] is not None]
        return {'n':len(rows),'completed':len(valid),'mse':float(np.mean(valid)) if valid else None},rows
    summary['motion']=completed_stage(output,'motion',motion_cases)
    agent=Investigator(owner,seed=7107)
    summary['inquiry']=completed_stage(output,'inquiry',lambda:summarize_with_rows([
        agent.attempt(i,split='ECHO-007-final-inquiry-v1',train=False) for i in range(256)]))
    if weight_hash(owner)!=before_hash:raise ValueError('Assessment changed learned weights')
    summary['weights_after']=weight_hash(owner)
    write_json(output/'RESULTS.json',summary)
    evidence={p.name:sha256(p) for p in sorted(output.glob('*.jsonl'))}
    write_json(output/'EVIDENCE.json',evidence)
    if replay:
        old=STUDY/'final'/arm
        assert summary==json.loads((old/'RESULTS.json').read_text())
        assert evidence==json.loads((old/'EVIDENCE.json').read_text())
        write_json(output/'REPLAY.json',{'all_metrics_and_raw_records_exact':True})
    print(json.dumps({'arm':arm,'replay':replay,'reading':summary['reading']['accuracy'],
                      'physics':summary['physics'],'inquiry':summary['inquiry']},indent=2),flush=True)


def summarize_with_rows(rows):return summarize_inquiry(rows),rows


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('train','evaluate'))
    p.add_argument('--arm',choices=(*ARMS,'parent'),required=True);p.add_argument('--replay',action='store_true')
    args=p.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use the supervisor')
    torch.set_num_threads(1)
    if args.mode=='train':train(args.arm)
    else:evaluate(args.arm,args.replay)


if __name__=='__main__':main()
