"""Direct learned question routing after diagnosed frozen-head interference."""
import json
import os
import torch
from .concept_language_study import LexicalRepair, phrases as previous_phrases
from .model import weight_hash
from .records import write_json
from .study_data import ROOT

ROOT11 = ROOT/'runs/CONCEPT-011'


def phrases():
    bank = previous_phrases()
    variables = [('drive','speed'),('input','velocity'),('control input','motion speed'),
                 ('applied input','rate of motion'),('control setting','speed of motion'),
                 ('applied drive','moving speed'),('actuator input','forward velocity'),
                 ('input setting','movement speed')]
    def expand(templates):
        return [[t.format(pair[r]) for t in templates for pair in variables] for r in (0,1)]
    bank['development'] = expand([
        'I want to investigate a larger {}. Describe its effect.',
        'Consider a change that raises {}. Explain the acceleration.',
        'Imagine the {} increases at this point. Describe the result.',
        'After increasing {}, which way does the response go?'])
    bank['final'] = expand([
        'In this situation I increase {}. What acceleration change follows?',
        'Explain the predicted response when the {} is made higher.',
        'Suppose I raise {} from the stated value. Describe the effect on acceleration.',
        'Based on the measured response, how would acceleration react to increased {}?',
        'For the same device, imagine changing {} upwards. Explain what follows.',
        'What acceleration consequence do you predict from having greater {}?'])
    groups = [set(bank['train']),set(s for g in bank['development'] for s in g),
              set(s for g in bank['final'] for s in g)]
    if any(a & b for i,a in enumerate(groups) for b in groups[i+1:]):raise ValueError('Split overlap')
    previous = previous_phrases()
    if groups[2] & set(s for key in ('development','final') for g in previous[key] for s in g):
        raise ValueError('Reused earlier assessment question')
    bank['unique_counts'] = [len(g) for g in groups]
    return bank


class DirectRepair(LexicalRepair):
    def __init__(self,training,bank):
        super().__init__(training,bank)
        self.owner.base_route_scale = 0.
        self.base.zero_(); self.dev_base.zero_()


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    torch.set_num_threads(1)
    if (ROOT11/'COMPLETE.json').exists():return
    bank=json.loads((ROOT11/'PHRASE_BANKS.json').read_text())
    e=DirectRepair(ROOT/'runs/CONCEPT-009',bank)
    if (ROOT11/'revisions/CURRENT.json').exists():e.resume(ROOT11/'revisions')
    def assess():
        metrics=e.assess();r=e.save(ROOT11/'revisions')
        e.dev.append({'step':e.step,**metrics,'weights':weight_hash(e.owner)})
        key=(-metrics['accuracy'],metrics['loss'],e.step)
        old=(-e.best['accuracy'],e.best['loss'],e.best['step']) if e.best else (float('inf'),)*3
        if key<old:
            e.best={**r,'step':e.step,**metrics};write_json(ROOT11/'SELECTION.json',e.best)
        print(json.dumps({'direct_development':e.dev[-1]}),flush=True)
    if not e.dev:assess()
    with (ROOT11/('training-'+os.environ['SERA_FIELD_SUPERVISED']+'.jsonl')).open('a') as log:
        while e.step<2048:
            log.write(json.dumps(e.update())+'\n')
            if e.step%128==0:
                log.flush();assess();e.save(ROOT11/'revisions')
    retained=all(torch.equal(v,e.owner.state_dict()[k]) for k,v in e.protected.items())
    if not retained:raise ValueError('Protected owner changed')
    write_json(ROOT11/'COMPLETE.json',{'steps':e.step,'presentations':e.step*32,
        'distinct_taught_phrases':len(set(bank['train'])),'selected':e.best,'development':e.dev,
        'all_parent_parameters_exact':retained,'new_reward_updates':0,'new_physics_training':0,
        'routing_construction':'direct learned lexical map; old routing parameters preserved but bypassed for this interface'})


if __name__=='__main__':main()
