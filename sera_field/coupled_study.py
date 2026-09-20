"""Prospective continuing-owner training with independently graded bulk capture."""
import argparse
import copy
import json
import os
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

from .coupled_owner import extend_coupled
from .credit_bridge import CreditBridge,CheckedOutcome,identity
from .model import weight_hash,parameters
from .records import sha256,utc,write_json
from .study_data import ROOT,load_records
from .study_inquiry import load_selected,observation_tensors
from .study_training import Engine,Curriculum,SCHEDULE,reading_batch,math_batch,pair_batch,physical_batch
from .study_evaluation import cohort
from .study_world import draw,stable_seed

STUDY=ROOT/'runs/UNIFIED-012'
DATA=ROOT/'local/CONNECTED-003-data-v1'
PARENT=ROOT/'checkpoints/CONCEPT-011'
ARMS=('coupled','capture_disconnected')


class CoupledEngine(Engine):
    def __init__(self,data,arm):
        super().__init__(data,seed=12112,owner_kind='scfe')
        parent,self.parent_selection=load_selected(PARENT)
        self.owner=extend_coupled(parent,capture_enabled=arm=='coupled')
        for name,p in self.owner.named_parameters():
            p.requires_grad_(not name.startswith(('investigation.','acquisition.','question_route.',
                                                  'lexical_route.','meaning.')))
        self.initial_hash=weight_hash(self.owner)
        self.optimizer=torch.optim.AdamW(self.owner.parameters(),lr=.00015,weight_decay=.0001)
        self.book=CreditBridge(self.owner,learning_rate=.05,
            verifier_hashes=[sha256(__file__)],source_hashes=[sha256(ROOT/'sera_field/study_world.py')])
        random.seed(self.seed);np.random.seed(self.seed);torch.manual_seed(self.seed)

    def update(self,batch=24):
        if SCHEDULE[self.step%len(SCHEDULE)]!='physics':return super().update(batch)
        self.owner.train();self.optimizer.zero_grad(set_to_none=True)
        indices=list(range(self.physics_cursor,self.physics_cursor+batch));self.physics_cursor+=batch
        self.exposures['physical_simulation']+=batch
        loss,mse=physical_batch(self.owner,self.seed,indices,'UNIFIED-012-teaching-v1')
        if not torch.isfinite(loss):raise ValueError('Nonfinite coupled loss')
        loss.backward();torch.nn.utils.clip_grad_norm_(self.owner.parameters(),3.,error_if_nonfinite=True)
        self.optimizer.step();self.step+=1
        return {'step':self.step,'kind':'physics','loss':float(loss.detach()),
                'correct_or_physics_mse':mse,'attempts':batch}

    def capture_attempt(self):
        index=self.step//32-1
        world,support,queries,_=draw(self.seed,index,'UNIFIED-012-capture-teaching-v1',with_targets=False)
        obs,present=observation_tensors(support);q=torch.from_numpy(queries)[None]
        with torch.no_grad():
            situation=self.owner.world(obs,present)
            before=self.owner.consequences(situation['coefficients'],q).mean(1)[0]
            tag=self.owner.field.last_source[0].clone()
        descriptor=torch.tensor([float(tag.norm())/5,len(support)/8,
                                  float(before.std())/6,float(self.owner.field.memory.active.float().mean())])
        logits=self.owner.capture_policy(descriptor)
        choice=int(torch.multinomial(logits.detach().softmax(-1),1))
        predictor=weight_hash(self.owner);decision=identity(['UNIFIED-012-capture',index])
        goal=identity(['acquire-retain-return',queries.tolist(),index])
        scope='observed-simulator-response-and-retained-boundary-field-v1'
        self.book.record_decision(decision=decision,goal=goal,logits=logits,choice=choice,
                                  predictor=predictor,assumptions_id=scope)
        if choice:
            proposal=self.owner.field.memory.propose(tag)
            try:
                self.owner.field.memory_preview=proposal
                with torch.no_grad():
                    revised=self.owner.world(obs,present)
                    after=self.owner.consequences(revised['coefficients'],q).mean(1)[0]
            finally:self.owner.field.memory_preview=None
        else:after=before
        assert weight_hash(self.owner)==predictor
        # Targets are obtained only after the proposal/decision. They never enter
        # the encoder or the conditional memory representation.
        truth=torch.from_numpy(world.observe(queries[:,0],queries[:,1]).astype('float32'))
        before_loss=float((before-truth).square().mean());after_loss=float((after-truth).square().mean())
        evidence=identity(['simulator-capture-assessment',index,queries.tolist(),truth.tolist()])
        intervention=identity(['retain-proposal',choice])
        result=CheckedOutcome(goal,decision,predictor,predictor,evidence,
            sha256(ROOT/'sera_field/study_world.py'),sha256(__file__),identity([evidence,'outcome']),
            'independent_simulation',intervention,intervention,before_loss,after_loss,True,
            identity(['field-tag',tag.tolist()]),scope)
        event=self.book.apply(result)
        capture=None
        if choice and after_loss<before_loss and event['accepted'] and self.owner.capture_enabled:
            capture=self.owner.field.memory.capture(tag,event,predictor=predictor,decision_policy=predictor)
        self.exposures['capture_goal_outcomes']+=len(queries)
        return {'step':self.step,'index':index,'choice':choice,'event':event,'capture':capture,
                'original_goal':goal,'original_goal_returned':True,'before':before.tolist(),
                'conditional_after':after.tolist(),'independent_outcomes':truth.tolist(),
                'provisional_memory_was_immutable':True}

    @torch.no_grad()
    def evaluate(self):
        self.owner.eval();results={}
        for kind,fn in (('reading',reading_batch),('math',math_batch)):
            rows=cohort(self.data.dev[kind],128,'UNIFIED-012-development-v1:'+kind)
            loss,count=0.,0
            for start in range(0,len(rows),16):
                batch=rows[start:start+16];a,b=fn(self.owner,batch);loss+=float(a)*len(batch);count+=b
            results[kind]={'loss':loss/len(rows),'accuracy':count/len(rows),'n':len(rows)}
        for track,bank in sorted(self.data.dev_pairs.items()):
            rows=cohort(bank,32,'UNIFIED-012-development-v1:'+track)
            rng=random.Random(stable_seed('UNIFIED-012-development-v1',track));loss,count=0.,0
            for start in range(0,len(rows),16):
                batch=rows[start:start+16];a,b=pair_batch(self.owner,batch,bank,rng)
                loss+=float(a)*len(batch);count+=b
            results['pair:'+track]={'loss':loss/len(rows),'accuracy':count/len(rows),'n':len(rows)}
        errors=[physical_batch(self.owner,self.seed,list(range(i,i+32)),
                    'UNIFIED-012-development-v1')[1] for i in range(0,128,32)]
        results['physics']={'loss':float(np.mean(errors)),'n':128}
        if self.initial_dev is None:self.initial_dev=copy.deepcopy(results)
        ratios={k:v['loss']/max(1e-8,self.initial_dev[k]['loss']) for k,v in results.items()}
        score=(ratios['reading']+ratios['math']+ratios['physics']+
               np.mean([v for k,v in ratios.items() if k.startswith('pair:')]))/4
        record={'step':self.step,'score':float(score),'metrics':results,'weights':weight_hash(self.owner),
                'captured_fields':int(self.owner.field.memory.cursor)}
        self.development.append(record);return record


def train(arm):
    root=STUDY/arm;root.mkdir(parents=True,exist_ok=True)
    if (root/'COMPLETE.json').exists():
        load_selected(root);print(arm+' complete; preserved',flush=True);return
    engine=CoupledEngine(Curriculum(DATA),arm)
    if (root/'revisions/CURRENT.json').exists():engine.resume(root/'revisions')
    else:
        initial=engine.evaluate();revision=engine.save(root/'revisions')
        engine.best={**revision,'score':initial['score'],'step':0}
        write_json(root/'INITIAL.json',{'weights':engine.initial_hash,'parent':engine.parent_selection,
                                       'development':initial,'parameters':parameters(engine.owner)})
        write_json(root/'SELECTION.json',engine.best)
    invocation=os.environ['SERA_FIELD_SUPERVISED'];started=time.monotonic()
    with (root/('attempts-'+invocation+'.jsonl')).open('x',encoding='utf-8') as log, \
         (root/('captures-'+invocation+'.jsonl')).open('x',encoding='utf-8') as captures:
        while engine.step<3072:
            row=engine.update();log.write(json.dumps(row)+'\n')
            if engine.step%32==0:
                captures.write(json.dumps(engine.capture_attempt())+'\n');captures.flush()
            if engine.step%128==0:
                log.flush();write_json(root/'PROGRESS.json',{'step':engine.step,'target':3072,
                    'exposures':dict(engine.exposures),'unique_human_records':len(engine.seen),
                    'captures':int(engine.owner.field.memory.cursor),'updated_utc':utc(),
                    'seconds_this_invocation':time.monotonic()-started})
                print(json.dumps({'arm':arm,**row,'captures':int(engine.owner.field.memory.cursor)}),flush=True)
            assessment=engine.evaluate() if engine.step%512==0 else None
            if engine.step%128==0:
                revision=engine.save(root/'revisions')
                if assessment and assessment['score']<engine.best['score']:
                    engine.best={**revision,'score':assessment['score'],'step':engine.step}
                    write_json(root/'SELECTION.json',engine.best)
            if (STUDY/'PAUSE_REQUEST.json').exists():
                revision=engine.save(root/'revisions');write_json(root/'PAUSED.json',revision);return
    chosen,_=load_selected(root)
    write_json(root/'COMPLETE.json',{'arm':arm,'steps':engine.step,'selected':engine.best,
        'exposures':dict(engine.exposures),'unique_human_records':len(engine.seen),
        'initial_weights':engine.initial_hash,'last_weights':weight_hash(engine.owner),
        'selected_captures':int(chosen.field.memory.cursor),'all_captures':int(engine.owner.field.memory.cursor),
        'selected_memory_events':chosen.field.memory.evidence,'development':engine.development})


def register():
    if (STUDY/'FINAL_REGISTRATION.json').exists():return
    selections={arm:{'selection_sha256':sha256(STUDY/arm/'SELECTION.json'),
                     'selection':json.loads((STUDY/arm/'SELECTION.json').read_text())} for arm in ARMS}
    selections['parent']={'selection_sha256':sha256(PARENT/'SELECTION.json')}
    opened=set()
    for p in (ROOT/'reports').rglob('OPENED_GROUPS.json'):
        opened.update(json.loads(p.read_text()))
    banks={k:[r for r in load_records(DATA,'sealed',k) if r['group'] not in opened]
           for k in ('reading','math','pairs')}
    tracks=defaultdict(list)
    for r in banks['pairs']:tracks[r['track']].append(r)
    cohorts={'reading':[r['id'] for r in cohort(banks['reading'],384,'UNIFIED-012-final-v1:reading')],
             'math':[r['id'] for r in cohort(banks['math'],192,'UNIFIED-012-final-v1:math')],
             'pairs':{k:[r['id'] for r in cohort(v,48,'UNIFIED-012-final-v1:'+k)] for k,v in sorted(tracks.items())}}
    ids=set(cohorts['reading']+cohorts['math']+sum(cohorts['pairs'].values(),[]))
    groups={r['group'] for rows in banks.values() for r in rows if r['id'] in ids}
    assert not groups&opened
    write_json(STUDY/'FINAL_REGISTRATION.json',{'selections':selections,'cohorts':cohorts,
        'prior_opened_groups_excluded':len(opened),'selected_groups':sorted(groups),
        'protocol_sha256':sha256(ROOT/'protocols/UNIFIED-012.md'),'registered_utc':utc()})


@torch.no_grad()
def evaluate(arm,ablation=None,replay=False):
    registered=json.loads((STUDY/'FINAL_REGISTRATION.json').read_text())
    root=PARENT if arm=='parent' else STUDY/arm
    assert sha256(root/'SELECTION.json')==registered['selections'][arm]['selection_sha256']
    owner,selection=load_selected(root);owner.eval();before=weight_hash(owner)
    if ablation:owner.field.ablation=ablation
    output=STUDY/('replay' if replay else 'final')/(arm+('-'+ablation if ablation else ''))
    output.mkdir(parents=True,exist_ok=True)
    if (output/'RESULTS.json').exists():return
    write_json(output/'OPENED_GROUPS.json',registered['selected_groups'])
    summary={'arm':arm,'ablation':ablation,'selection':selection,'weights_before':before}
    rows_out=[]
    for kind,fn in (('reading',reading_batch),('math',math_batch)):
        bank={r['id']:r for r in load_records(DATA,'sealed',kind)}
        rows=[bank[i] for i in registered['cohorts'][kind]];loss,count=0.,0
        for row in rows:
            a,b=fn(owner,[row]);loss+=float(a);count+=b
            rows_out.append({'track':kind,'id':row['id'],'loss':float(a),'correct':b})
        summary[kind]={'n':len(rows),'accuracy':count/len(rows),'loss':loss/len(rows)}
    bank={r['id']:r for r in load_records(DATA,'sealed','pairs')}
    summary['pairs']={}
    for track,ids in registered['cohorts']['pairs'].items():
        rows=[bank[i] for i in ids]
        if len(rows)<4:continue
        rng=random.Random(stable_seed('UNIFIED-012-final-v1',track));loss,count=0.,0
        for row in rows:
            a,b=pair_batch(owner,[row],rows,rng);loss+=float(a);count+=b
            rows_out.append({'track':track,'id':row['id'],'loss':float(a),'correct':b})
        summary['pairs'][track]={'n':len(rows),'accuracy':count/len(rows),'loss':loss/len(rows)}
    for omitted,n in ((False,256),(True,128)):
        errors=[]
        for index in range(n):
            world,support,queries,truth=draw(12112,index,'UNIFIED-012-final-v1',omitted=omitted)
            situation=owner.world(*observation_tensors(support))
            pred=owner.consequences(situation['coefficients'],torch.from_numpy(queries)[None]).mean(1)[0].numpy()
            mse=float(np.mean((pred-truth)**2));errors.append(mse)
            rows_out.append({'track':'omitted' if omitted else 'physics','index':index,'mse':mse,
                             'predictions':pred.tolist(),'outcomes':truth.tolist()})
        summary['omitted' if omitted else 'physics']={'n':n,'mse':float(np.mean(errors)),'median':float(np.median(errors))}
    assert weight_hash(owner)==before
    summary['weights_after']=weight_hash(owner)
    raw=''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows_out)
    (output/'cases.jsonl').write_text(raw,encoding='utf-8')
    summary['cases_sha256']=sha256(output/'cases.jsonl')
    write_json(output/'RESULTS.json',summary)
    print(json.dumps(summary),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('train','register','evaluate'))
    parser.add_argument('--arm',choices=(*ARMS,'parent'),default='coupled')
    parser.add_argument('--ablation',choices=('no_memory','no_covariance'))
    parser.add_argument('--replay',action='store_true');args=parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1);STUDY.mkdir(parents=True,exist_ok=True)
    if args.action=='train':train(args.arm)
    elif args.action=='register':register()
    else:evaluate(args.arm,args.ablation,args.replay)


if __name__=='__main__':main()
