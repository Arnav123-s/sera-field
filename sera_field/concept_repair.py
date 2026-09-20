"""Paired language teaching of the existing owner's question-routing weights."""
import json
import os
from pathlib import Path

import torch
from torch.nn import functional as F

from .credit_bridge import CreditBridge
from .model import weight_hash
from .records import sha256, write_json
from .study_data import ROOT
from .study_inquiry import load_selected

ROOT9=ROOT/'runs/CONCEPT-009'


def phrases():
    templates=(
        'What happens when {} increases?', 'Describe the effect of more {}.',
        'How does increasing {} change acceleration?', 'Imagine a rise in {}. What follows?',
        'If {} becomes larger, explain the effect.', 'Consider a larger {} and explain the response.',
        'What would more {} do to acceleration?', 'Explain how the response changes with higher {}.',
        'How does the acceleration respond to increasing {}?', 'Tell me the consequence of greater {}.',
        'Picture increased {}. Does the response rise or fall?', 'Suppose {} is raised. Describe what changes.')
    variables=(('control input','speed'),('drive','velocity'),('applied input','rate of motion'),
               ('input','motion speed'),('control','the speed of motion'))
    train=[t.format(v) for t in templates for pair in variables for v in pair]
    dev=[
        ['Consider the result of increasing the drive.',
         'Can you explain the acceleration change caused by more input?',
         'Think about a higher control setting and its effect.',
         'The applied input is larger. Which way does the response change?'],
        ['Consider the result of increasing the speed.',
         'Can you explain the acceleration change caused by more velocity?',
         'Think about a higher rate of motion and its effect.',
         'The speed of motion is larger. Which way does the response change?']]
    final=[
        ['If the drive is raised, which direction does acceleration go?',
         'Picture a larger control input and describe the acceleration.',
         'When I turn up the input, should the response rise or fall?',
         'Under more applied drive, what changes in acceleration?',
         'The control is stronger now; explain the acceleration effect.'],
        ['If the speed is raised, which direction does acceleration go?',
         'Picture a larger velocity and describe the acceleration.',
         'When I move faster, should the response rise or fall?',
         'Under a higher rate of motion, what changes in acceleration?',
         'The motion is faster now; explain the acceleration effect.']]
    groups=[set(s.lower().strip() for s in train),set(s.lower().strip() for g in dev for s in g),
            set(s.lower().strip() for g in final for s in g)]
    assert all(not a&b for i,a in enumerate(groups) for b in groups[i+1:])
    return {'train':train,'development':dev,'final':final,
            'provenance':'Supplied paired annotations for the two-variable simulation interface; no human-corpus claim.'}


class Repair:
    def __init__(self,training,bank):
        self.owner,self.parent_selection=load_selected(training)
        for name,p in self.owner.named_parameters():p.requires_grad_(name.startswith('question_route.'))
        self.protected={k:v.clone() for k,v in self.owner.state_dict().items() if not k.startswith('question_route.')}
        self.optimizer=torch.optim.AdamW(self.owner.question_route.parameters(),lr=.001,weight_decay=.0001)
        self.book=CreditBridge(self.owner,source_hashes=[sha256(__file__)],verifier_hashes=[sha256(__file__)])
        with torch.no_grad():
            self.features=self.owner.encode_texts(bank['train'])
            # A second, separately batched live encoding validates the cache.
            check=torch.cat([self.owner.encode_texts(bank['train'][i:i+16]) for i in range(0,len(bank['train']),16)])
            if not torch.allclose(self.features,check,atol=1e-6,rtol=1e-6):raise ValueError('Encoding cache differs')
            text=[s for group in bank['development'] for s in group]
            self.dev_features=self.owner.encode_texts(text)
            self.dev_labels=torch.tensor([r for r,g in enumerate(bank['development']) for _ in g])
        self.rng=torch.Generator().manual_seed(9109);self.step=0;self.parent=None;self.best=None;self.dev=[]

    def update(self):
        pairs=torch.randint(len(self.features)//2,(16,),generator=self.rng)
        indices=torch.stack((pairs*2,pairs*2+1),-1).flatten()
        x=self.features[indices]+.03*torch.randn(32,self.features.shape[-1],generator=self.rng)
        y=torch.arange(32)%2;logits=self.owner.question_route(x)
        differences=logits[:,0]-logits[:,1]
        margin=F.relu(1-(differences[::2]-differences[1::2])).mean()
        loss=F.cross_entropy(logits,y)+.1*margin
        self.optimizer.zero_grad(set_to_none=True);loss.backward()
        torch.nn.utils.clip_grad_norm_(self.owner.question_route.parameters(),3.,error_if_nonfinite=True)
        self.optimizer.step();self.step+=1
        return {'step':self.step,'loss':float(loss.detach())}

    def assess(self):
        with torch.no_grad():
            logits=self.owner.question_route(self.dev_features)
            return {'accuracy':float((logits.argmax(-1)==self.dev_labels).float().mean()),
                    'loss':float(F.cross_entropy(logits,self.dev_labels))}

    def save(self,root):
        result=self.book.commit(root,expected_parent=self.parent,progress={'step':self.step,'rng':self.rng.get_state(),
            'optimizer':self.optimizer.state_dict(),'best':self.best,'development':self.dev,'parent_selection':self.parent_selection})
        self.parent=result['sha256'];return result

    def resume(self,root):
        result=self.book.load_current(root);p=result['progress']
        if p['parent_selection']!=self.parent_selection:raise ValueError('Repair parent changed')
        self.step=p['step'];self.rng.set_state(p['rng']);self.optimizer.load_state_dict(p['optimizer'])
        self.best=p['best'];self.dev=p['development'];self.parent=result['sha256']


def main():
    import argparse
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    torch.set_num_threads(1)
    p=argparse.ArgumentParser();p.add_argument('--training',type=Path,required=True);args=p.parse_args()
    if (ROOT9/'COMPLETE.json').exists():return
    bank=json.loads((ROOT9/'PHRASE_BANKS.json').read_text());e=Repair(args.training,bank)
    if (ROOT9/'revisions/CURRENT.json').exists():e.resume(ROOT9/'revisions')
    def assess():
        metrics=e.assess();r=e.save(ROOT9/'revisions')
        e.dev.append({'step':e.step,**metrics,'weights':weight_hash(e.owner)})
        key=(-metrics['accuracy'],metrics['loss'],e.step)
        old=(-e.best['accuracy'],e.best['loss'],e.best['step']) if e.best else (float('inf'),)*3
        if key<old:
            e.best={**r,'step':e.step,**metrics}
            write_json(ROOT9/'SELECTION.json',e.best)
        print(json.dumps({'repair_development':e.dev[-1]}),flush=True)
    if not e.dev:assess()
    with (ROOT9/('training-'+os.environ['SERA_FIELD_SUPERVISED']+'.jsonl')).open('a') as f:
        while e.step<1536:
            f.write(json.dumps(e.update())+'\n')
            if e.step%128==0:
                f.flush();assess();e.save(ROOT9/'revisions')
    unchanged=all(torch.equal(v,e.owner.state_dict()[k]) for k,v in e.protected.items())
    if not unchanged:raise ValueError('Repair changed protected skills')
    write_json(ROOT9/'COMPLETE.json',{'steps':e.step,'presentations':e.step*32,'distinct_taught_phrases':len(bank['train']),
        'selected':e.best,'development':e.dev,'all_non_routing_parameters_exact':unchanged,'new_physics_training':0,'new_reward_updates':0})


if __name__=='__main__':main()
