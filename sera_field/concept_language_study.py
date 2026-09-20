"""Prospective lexical repair: fixed owner, fresh weights and phrase partitions."""
import json
import os
from pathlib import Path

import torch
from torch.nn import functional as F

from .concept_language import extend, lexical_features
from .concept_repair import Repair, phrases as earlier_phrases
from .credit_bridge import CreditBridge
from .model import weight_hash
from .records import sha256, write_json
from .study_data import ROOT
from .study_inquiry import load_selected

ROOT10 = ROOT/'runs/CONCEPT-010'


def phrases():
    variables = [('drive', 'speed'), ('input', 'velocity'),
                 ('control input', 'motion speed'), ('applied input', 'rate of motion'),
                 ('control setting', 'speed of motion'), ('applied drive', 'moving speed'),
                 ('actuator input', 'forward velocity'), ('input setting', 'movement speed')]
    templates = [
        'Describe what increasing {} does.', 'What is caused by a rise in {}?',
        'I increased {}. Predict the change in acceleration.',
        'Imagine greater {}. Which way does the acceleration change?',
        'Tell me how acceleration changes after raising {}.',
        'Explain the acceleration effect of higher {}.',
        'What follows if {} becomes larger?', 'Describe the response to more {}.',
        'Is the acceleration higher or lower with increased {}?',
        'I am exploring {}. Imagine increasing it.',
        'How would greater {} affect this system?',
        'Think about a rise in {} and explain its consequence.',
        'Consider increasing {} at this operating point.',
        'The experiment increases {}. Explain what follows.',
        'Predict the result of turning up {}.',
        'Which acceleration change follows an increase in {}?']
    train = earlier_phrases()['train'] + [t.format(v) for t in templates
                                         for pair in variables for v in pair]
    train += [s for pair in [
        ('I apply more drive. Explain the response.', 'I move faster. Explain the response.'),
        ('Imagine stronger input and its effect.', 'Imagine moving faster and its effect.'),
        ('The drive is stronger. What changes?', 'The movement is faster. What changes?'),
        ('If I turn up the control, what follows?', 'If I travel faster, what follows?'),
        ('Think about a stronger control.', 'Think about faster motion.'),
        ('Suppose the actuator supplies more input.', 'Suppose the object is moving faster.')]
        for s in pair]
    def partition(templates):
        return [[t.format(pair[r]) for t in templates for pair in variables] for r in (0, 1)]
    dev = partition([
        'At this point, what consequence follows from a larger {}?',
        'For this acquired system, describe the acceleration after {} increases.'])
    final = partition([
        'Use the observed relationship to explain the effect of increasing {}.',
        'Holding the other variable fixed, {} is raised. What happens to acceleration?',
        'Could you describe the acceleration response under greater {}?',
        'From these observations, which acceleration change would a rise in {} cause?',
        'Make a conditional prediction for a larger {} at the given operating point.'])
    groups = [set(train), set(s for g in dev for s in g), set(s for g in final for s in g)]
    if any(a & b for i, a in enumerate(groups) for b in groups[i+1:]):
        raise ValueError('Phrase split overlap')
    return {'train': train, 'development': dev, 'final': final,
            'provenance': 'Supplied finite two-variable simulation annotations, not a new human corpus.',
            'unique_counts': [len(g) for g in groups]}


class LexicalRepair(Repair):
    def __init__(self, training, bank):
        parent, self.parent_selection = load_selected(training)
        self.owner = extend(parent)
        self.protected = {k: v.clone() for k, v in parent.state_dict().items()}
        self.optimizer = torch.optim.AdamW(self.owner.lexical_route.parameters(), lr=.01, weight_decay=.001)
        self.book = CreditBridge(self.owner, source_hashes=[sha256(__file__)], verifier_hashes=[sha256(__file__)])
        self.features = lexical_features(bank['train'])
        with torch.no_grad():
            self.base = parent.route_logits(bank['train'])
            dev = [s for g in bank['development'] for s in g]
            self.dev_base = parent.route_logits(dev)
        self.dev_features = lexical_features(dev)
        self.dev_labels = torch.tensor([r for r, g in enumerate(bank['development']) for _ in g])
        self.rng = torch.Generator().manual_seed(10110)
        self.step = 0; self.parent = None; self.best = None; self.dev = []

    def update(self):
        pairs = torch.randint(len(self.features)//2, (16,), generator=self.rng)
        indices = torch.stack((pairs*2, pairs*2+1), -1).flatten()
        x = self.features[indices] + .01*torch.randn(32, self.features.shape[-1], generator=self.rng)
        logits = self.base[indices] + self.owner.lexical_route(x)
        labels = torch.arange(32) % 2
        difference = logits[:, 0]-logits[:, 1]
        loss = F.cross_entropy(logits, labels) + .1*F.relu(1-(difference[::2]-difference[1::2])).mean()
        self.optimizer.zero_grad(set_to_none=True); loss.backward()
        torch.nn.utils.clip_grad_norm_(self.owner.lexical_route.parameters(), 3., error_if_nonfinite=True)
        self.optimizer.step(); self.step += 1
        return {'step': self.step, 'loss': float(loss.detach())}

    def assess(self):
        with torch.no_grad():
            logits = self.dev_base+self.owner.lexical_route(self.dev_features)
            return {'accuracy': float((logits.argmax(-1) == self.dev_labels).float().mean()),
                    'loss': float(F.cross_entropy(logits, self.dev_labels))}


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use supervisor')
    torch.set_num_threads(1)
    bank = json.loads((ROOT10/'PHRASE_BANKS.json').read_text())
    if (ROOT10/'COMPLETE.json').exists(): return
    e = LexicalRepair(ROOT/'runs/CONCEPT-009', bank)
    if (ROOT10/'revisions/CURRENT.json').exists(): e.resume(ROOT10/'revisions')
    def assess():
        metrics = e.assess(); r = e.save(ROOT10/'revisions')
        e.dev.append({'step': e.step, **metrics, 'weights': weight_hash(e.owner)})
        key = (-metrics['accuracy'], metrics['loss'], e.step)
        old = (-e.best['accuracy'], e.best['loss'], e.best['step']) if e.best else (float('inf'),)*3
        if key < old:
            e.best = {**r, 'step': e.step, **metrics}; write_json(ROOT10/'SELECTION.json', e.best)
        print(json.dumps({'lexical_development': e.dev[-1]}), flush=True)
    if not e.dev: assess()
    with (ROOT10/('training-'+os.environ['SERA_FIELD_SUPERVISED']+'.jsonl')).open('a') as log:
        while e.step < 2048:
            log.write(json.dumps(e.update())+'\n')
            if e.step % 128 == 0:
                log.flush(); assess(); e.save(ROOT10/'revisions')
    retained = all(torch.equal(v, e.owner.state_dict()[k]) for k, v in e.protected.items())
    if not retained: raise ValueError('Protected owner changed')
    write_json(ROOT10/'COMPLETE.json', {'steps': e.step, 'presentations': e.step*32,
        'distinct_taught_phrases': len(set(bank['train'])), 'selected': e.best, 'development': e.dev,
        'all_parent_parameters_exact': retained, 'new_reward_updates': 0, 'new_physics_training': 0})


if __name__ == '__main__': main()
