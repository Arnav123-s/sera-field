"""Joint native teaching, assessment and exact resumable revisions."""
from collections import Counter
import json
import os
from pathlib import Path
import random

import torch
from torch.nn import functional as F

from .model import weight_hash
from .native_data import ROOT, TRACKS, identity, physical_episode, independent_outcome
from .native_owner import NativeOwner, NativeConfig
from .records import sha256, write_json, utc

STUDY = ROOT / 'runs/NATIVE-019'
TOTAL = 8192
ARMS = ('native', 'delayed', 'trace')


def read(path): return json.loads(Path(path).read_text())


def training_ablation(arm, completed_updates):
    return 'simple_trace' if arm == 'trace' or (arm == 'delayed' and completed_updates < TOTAL // 2) else None


def selected_ablation(arm, selected_step):
    # A checkpoint after update 4096 still belongs to its just-completed basic
    # trace course. The first richer update is update 4097.
    return training_ablation(arm, max(0, selected_step-1))


def tensors(rows):
    return (torch.tensor([r['support'] for r in rows], dtype=torch.float32),
            torch.tensor([r['queries'] for r in rows], dtype=torch.float32),
            torch.tensor([r['targets'] for r in rows], dtype=torch.float32))


def loss_cases(owner, data, kind, rows, *, memory=True, ablation=None, split='train'):
    if kind == 'semantic':
        logits = owner.semantic([r['premise'] for r in rows], [r['hypothesis'] for r in rows],
                                memory=memory, ablation=ablation)
        targets = torch.tensor([r['target'] for r in rows])
        branch_loss = -logits.log_softmax(-1).gather(2, targets[:, None, None].expand(-1, 3, 1)).squeeze(-1)
        mask = torch.tensor([[float((int(row['id'][:8], 16)+b) % 4 != 0) for b in range(3)] for row in rows])
        loss = (branch_loss * mask).sum() / mask.sum()
        probabilities = logits.softmax(-1).mean(1)
        cases = [{'id': r['id'], 'group': r['source_group'], 'genre': r['genre'], 'target': int(targets[i]),
            'prediction': int(probabilities[i].argmax()), 'probabilities': probabilities[i].detach().tolist(),
            'correct': int(probabilities[i].argmax()) == int(targets[i]),
            'loss': float(-probabilities[i, targets[i]].clamp_min(1e-12).log().detach())} for i, r in enumerate(rows)]
    elif kind == 'physics':
        support, query, target = tensors(rows)
        predicted = owner.physical(support, query, memory=memory, ablation=ablation)
        mask = torch.tensor([[float((int(row['id'][:8], 16)+b) % 4 != 0) for b in range(3)] for row in rows])
        loss = ((predicted-target[..., None]).square() * mask[:, None]).sum() / (mask.sum() * target.shape[1])
        mean = predicted.mean(-1)
        cases = [{'id': r['id'], 'prediction': mean[i].detach().tolist(), 'target': r['targets'],
            'branches': predicted[i].detach().tolist(), 'mse': float((mean[i]-target[i]).square().mean().detach())}
            for i, r in enumerate(rows)]
    else:
        contexts, options, targets = data.choices(kind, rows, split)
        logits = owner.option_logits(contexts, options, memory=memory, ablation=ablation)
        logp = logits.log_softmax(-1)
        losses = torch.stack([-torch.logsumexp(logp[i, target], 0) for i, target in enumerate(targets)])
        loss = losses.mean()
        cases = [{'id': r['id'], 'track': r.get('track', kind), 'group': r.get('group'),
            'target': targets[i], 'prediction': int(logits[i].argmax()),
            'correct': int(logits[i].argmax()) in targets[i], 'loss': float(losses[i].detach()),
            'options': len(options[i])} for i, r in enumerate(rows)]
    return loss, cases


def summarize(cases, kind):
    if kind == 'physics': return {'n': len(cases), 'mse': sum(c['mse'] for c in cases)/len(cases)}
    return {'n': len(cases), 'accuracy': sum(c['correct'] for c in cases)/len(cases),
            'loss': sum(c['loss'] for c in cases)/len(cases)}


@torch.no_grad()
def assess(owner, data, kind, rows, *, memory=True, ablation=None):
    owner.eval(); cases = []
    for offset in range(0, len(rows), 16):
        _, batch = loss_cases(owner, data, kind, rows[offset:offset+16], memory=memory,
                              ablation=ablation, split='development')
        cases.extend(batch)
    return summarize(cases, kind), cases


def development(owner, data, *, memory=True, ablation=None):
    metrics = {kind: assess(owner, data, kind, rows, memory=memory, ablation=ablation)[0]
               for kind, rows in data.development.items()}
    physics = [physical_episode('NATIVE-019-development', i) for i in range(128)]
    metrics['physics'] = assess(owner, data, 'physics', physics, memory=memory, ablation=ablation)[0]
    score = (sum(metrics[k]['accuracy'] for k in ('semantic', 'pairs', 'reading', 'math')) +
             1/(1+metrics['physics']['mse']))/5
    return {'score': score, 'tracks': metrics}


def new_owner():
    torch.manual_seed(19119); random.seed(19119)
    return NativeOwner()


def save_revision(root, owner, optimizer, step, history, exposures, sources):
    revisions = root / 'revisions'; revisions.mkdir(parents=True, exist_ok=True)
    temp = revisions / ('pending-' + os.environ.get('SERA_FIELD_SUPERVISED', 'test') + '.pt')
    payload = {'specification': owner.specification(), 'owner': owner.state_dict(),
        'optimizer': optimizer.state_dict(), 'rng': torch.get_rng_state(), 'python_rng': random.getstate(),
        'step': step, 'development': history, 'exposures': dict(exposures), 'sources': sources}
    torch.save(payload, temp)
    digest = sha256(temp); destination = revisions / (digest + '.pt')
    if destination.exists():
        if sha256(destination) != digest: raise ValueError('Existing native revision identity changed')
        temp.unlink()
    else: temp.rename(destination)
    record = {'revision': destination.name, 'sha256': digest, 'weights': weight_hash(owner), 'step': step}
    write_json(revisions / 'CURRENT.json', record)
    return record


def load_native(root, *, pointer='SELECTION.json'):
    root = Path(root); selected = read(root / pointer)
    path = root / 'revisions' / selected['revision']
    if path.resolve().parent != (root / 'revisions').resolve() or sha256(path) != selected['sha256']:
        raise ValueError('Native revision identity changed')
    payload = torch.load(path, map_location='cpu', weights_only=False)
    spec = dict(payload['specification'])
    if spec.pop('type') != 'native-memory-field-019': raise ValueError('Wrong native owner')
    owner = NativeOwner(NativeConfig(**spec)); owner.load_state_dict(payload['owner'])
    if weight_hash(owner) != selected['weights']: raise ValueError('Native tensor identity changed')
    return owner, selected, payload


def source_files():
    files = ['native_owner.py', 'native_data.py', 'native_training.py', 'clifford_sheaf.py',
             'continuum_core.py', 'gauge.py', 'study_data.py', 'records.py', 'model.py', 'situation_core.py']
    return {'sera_field/' + name: sha256(ROOT / 'sera_field' / name) for name in files}


def train(arm, data, sources):
    root = STUDY / arm; root.mkdir(parents=True, exist_ok=True)
    if (root / 'COMPLETE.json').exists():
        _, _, old = load_native(root)
        if old['sources'] != sources: raise ValueError('Completed study source changed')
        return
    owner = new_owner()
    optimizer = torch.optim.AdamW(owner.parameters(), lr=.001, weight_decay=.0001)
    step = 0; history = []; exposures = Counter()
    if (root / 'revisions/CURRENT.json').exists():
        owner, _, payload = load_native(root, pointer='revisions/CURRENT.json')
        if payload['sources'] != sources: raise ValueError('Resume source identity changed')
        optimizer = torch.optim.AdamW(owner.parameters(), lr=.001, weight_decay=.0001)
        optimizer.load_state_dict(payload['optimizer']); torch.set_rng_state(payload['rng'])
        random.setstate(payload['python_rng']); step = payload['step']
        history = payload['development']; exposures.update(payload['exposures'])
        best = read(root / 'SELECTION.json')
        if history and history[-1]['step'] == step and history[-1]['score'] > best['score']:
            best = {**read(root / 'revisions/CURRENT.json'), **history[-1]}
            write_json(root / 'SELECTION.json', best)
    else:
        initial = development(owner, data, ablation=selected_ablation(arm, 0))
        history.append({'step': 0, **initial})
        record = save_revision(root, owner, optimizer, 0, history, exposures, sources)
        best = {**record, **initial}; write_json(root / 'SELECTION.json', best)
        write_json(root / 'INITIAL.json', best)
    log_path = root / ('updates-' + os.environ['SERA_FIELD_SUPERVISED'] + '.jsonl')
    with log_path.open('x', encoding='utf-8') as log:
        while step < TOTAL:
            owner.train(); optimizer.zero_grad(set_to_none=True)
            kind, rows = data.lesson(step)
            loss, _ = loss_cases(owner, data, kind, rows, ablation=training_ablation(arm, step))
            if not torch.isfinite(loss): raise ValueError('Nonfinite loss; preserve last native revision')
            loss.backward(); norm = torch.nn.utils.clip_grad_norm_(owner.parameters(), 1., error_if_nonfinite=True)
            optimizer.step(); step += 1; exposures[kind] += len(rows)
            if kind == 'pairs': exposures['pair_track:' + rows[0]['track']] += len(rows)
            score = None
            if step % 1024 == 0:
                score = development(owner, data, ablation=selected_ablation(arm, step))
                history.append({'step': step, **score})
            record = {'step': step, 'kind': kind, 'ids': [r['id'] for r in rows],
                      'loss': float(loss.detach()), 'gradient_norm': float(norm), 'development': score}
            log.write(json.dumps(record) + '\n')
            if step % 256 == 0:
                # A durable cursor must not advance past its teaching receipts.
                log.flush(); os.fsync(log.fileno())
                saved = save_revision(root, owner, optimizer, step, history, exposures, sources)
                if score and score['score'] > best['score']:
                    best = {**saved, **score}; write_json(root / 'SELECTION.json', best)
                write_json(root / 'PROGRESS.json', {'arm': arm, 'step': step, 'target': TOTAL,
                    'exposures': dict(exposures), 'selected_step': best['step'], 'utc': utc()})
                print(json.dumps({'arm': arm, 'step': step, 'loss': record['loss'], 'score': score}), flush=True)
    write_json(root / 'COMPLETE.json', {'arm': arm, 'updates': step, 'selected': best,
        'exposures': dict(exposures), 'development': history, 'sources': sources,
        'initial_weights': read(root / 'INITIAL.json')['weights'],
        'parent_checkpoint_loaded': False, 'pretrained_weights_loaded': False})
