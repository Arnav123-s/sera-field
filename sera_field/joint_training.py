"""One owner, mixed histories, checked outcome credit and matched teaching."""
from collections import Counter
import json
import os
import random

import torch
from torch.nn import functional as F

from .joint_cycle import (replay, answers, investigation_logits, checked_progress,
                          with_credit, policy_objective)
from .joint_data import action_number
from .native_data import ROOT, identity, independent_outcome
from .native_owner import select_state
from .native_training import (load_native, loss_cases, save_revision, read,
                              summarize, assess)
from .model import weight_hash
from .records import write_json, sha256, utc

STUDY = ROOT / 'runs/JOINT-020'
TOTAL = 1024
GRID = [[float(f), float(v)] for f in (-1, 0, 1) for v in (-1, 0, 1)]


def mixed_state(owner, rows):
    """Replay explicit observed order, never the annotations or teacher family."""
    states = []
    # Different chronology is grouped to avoid interpreting batch padding as
    # observations. Restore original order before any question or decision.
    for first in (False, True):
        indices = [i for i, r in enumerate(rows) if r['text_first'] == first]
        if not indices:
            continue
        chosen = [rows[i] for i in indices]
        if len({r['supports'] for r in chosen}) != 1:
            raise ValueError('A batch must have one explicit support horizon')
        texts = {'kind': 'text', 'texts': [r['human']['premise'] for r in chosen]}
        observed = torch.tensor([r['physics']['support'][:r['supports']] for r in chosen],
                                dtype=owner.words.weight.dtype)
        measurements = [{'kind': 'measurement', 'actual': value} for value in observed.unbind(1)]
        events = [texts, *measurements] if first else [*measurements, texts]
        states.append((indices, replay(owner, events, len(indices))))
    order = [i for indices, _ in states for i in indices]
    inverse = torch.tensor([order.index(i) for i in range(len(rows))])
    return {k: torch.cat([state[k] for _, state in states])[inverse]
            if isinstance(states[0][1][k], torch.Tensor) else states[0][1][k]
            for k in states[0][1]}


def observe_actions(owner, state, rows, actions):
    candidates = state['fast'].new_tensor(GRID)
    performed = actions != len(GRID)
    controls = candidates[actions.clamp_max(len(GRID)-1)]
    receipts = []
    for row, (force, velocity), yes in zip(rows, controls.detach().tolist(), performed.tolist()):
        response = independent_outcome(row['physics']['teacher_only'], force, velocity) if yes else 0.
        receipts.append([force, velocity, response])
    actual = state['fast'].new_tensor(receipts)
    source = owner.encode_numbers(actual[:, 0], actual[:, 1], actual[:, 2])
    updated, _ = owner.observe(state, source)
    after = {key: torch.where(performed.reshape(-1, *([1]*(value.ndim-1))), value, state[key])
             if isinstance(value, torch.Tensor) else value for key, value in updated.items()}
    return after, performed, actual


def cycle(owner, rows, *, route='learned', reward=True, training=False, ablation=None):
    state = mixed_state(owner, rows)
    hypotheses = [r['human']['hypothesis'] for r in rows]
    goals = state['fast'].new_tensor([r['physics']['queries'][0] for r in rows])
    future = state['fast'].new_tensor([r['physics']['queries'][1] for r in rows])
    targets = state['fast'].new_tensor([independent_outcome(r['physics']['teacher_only'], *r['physics']['queries'][0]) for r in rows])
    next_targets = state['fast'].new_tensor([independent_outcome(r['physics']['teacher_only'], *r['physics']['queries'][1]) for r in rows])
    labels = torch.tensor([r['human']['target'] for r in rows])
    if ablation == 'erase_history':
        state = owner.empty(len(rows))
    candidates = state['fast'].new_tensor(GRID)
    logits = investigation_logits(owner, state, goals, candidates, ablation=ablation)
    before = answers(owner, state, hypotheses, goals, ablation=ablation)
    if training or route == 'uniform':
        actions = torch.tensor([action_number(r) for r in rows])
    elif route == 'stop':
        actions = torch.full((len(rows),), len(GRID), dtype=torch.long)
    elif route == 'disagreement':
        with torch.no_grad():
            branches = owner.physical_query(state, candidates[None].expand(len(rows), -1, -1), ablation=ablation)
            actions = (branches.amax(-1)-branches.amin(-1)).argmax(-1)
    elif route == 'learned':
        actions = logits.argmax(-1)
    else:
        raise ValueError('Unregistered investigation route')
    after_state, measured, actual = observe_actions(owner, state, rows, actions)
    if ablation == 'erase_history':
        after_state = owner.empty(len(rows))
    after = answers(owner, after_state, hypotheses, goals, ablation=ablation)
    b = before['physical'].mean(-1); a = after['physical'].mean(-1)
    checked = checked_progress(b, a, targets, requested=actual[:, :2], actual=actual[:, :2])
    credit = torch.where(measured, checked['policy_credit'], torch.zeros_like(a))
    marks = torch.where(measured, checked['signed_progress'], torch.zeros_like(a))
    credited = with_credit(after_state, marks)
    next_answer = owner.physical_query(credited, future[:, None], ablation=ablation)[:, 0].mean(-1)
    semantic = .5*(F.cross_entropy(before['semantic'].mean(1), labels) +
                   F.cross_entropy(after['semantic'].mean(1), labels))
    physical = .5*((before['physical']-targets[:, None]).square().mean() +
                   (after['physical']-targets[:, None]).square().mean())
    transfer = (next_answer-next_targets).square().mean()
    bounded = 4*credit.clamp(-.25, .25) if reward else credit*0
    policy = policy_objective(logits, actions, bounded, behavior_probability=torch.full_like(credit, .1))
    loss = semantic + physical + transfer + policy
    probability = after['semantic'].softmax(-1).mean(1)
    records = []
    for i, row in enumerate(rows):
        records.append({'id': row['id'], 'source_id': row['human']['id'], 'group': row['human']['source_group'],
            'physical_id': row['physics']['id'], 'chronology': 'text_first' if row['text_first'] else 'measurements_first',
            'target': int(labels[i]), 'correct': int(probability[i].argmax()) == int(labels[i]),
            'probabilities': probability[i].detach().tolist(), 'action': int(actions[i]),
            'performed': bool(measured[i]), 'actual': actual[i].detach().tolist() if measured[i] else None,
            'before': float(b[i].detach()), 'after': float(a[i].detach()), 'truth': float(targets[i]),
            'before_mse': float((b[i]-targets[i]).square().detach()),
            'after_mse': float((a[i]-targets[i]).square().detach()),
            'next_query_mse': float((next_answer[i]-next_targets[i]).square().detach()),
            'credit': float(credit[i]), 'signed_progress': float(marks[i]),
            'behavior_probability': .1 if training or route == 'uniform' else None,
            'score_probabilities': logits[i].softmax(-1).detach().tolist()})
    diagnostics = {'semantic': float(semantic.detach()), 'physical': float(physical.detach()),
                   'next_query': float(transfer.detach()), 'policy': float(policy.detach())}
    return loss, records, diagnostics


def aggregate(cases):
    n = len(cases)
    result = {key: sum(r[key] for r in cases)/n for key in
              ('before_mse', 'after_mse', 'next_query_mse', 'credit', 'signed_progress')}
    result.update(n=n, accuracy=sum(r['correct'] for r in cases)/n,
                  measurement_rate=sum(r['performed'] for r in cases)/n)
    return result


@torch.no_grad()
def evaluate(owner, rows, *, route='learned', ablation=None):
    owner.eval(); cases = []
    for start in range(0, len(rows), 8):
        _, batch, _ = cycle(owner, rows[start:start+8], route=route, ablation=ablation)
        cases.extend(batch)
    return aggregate(cases), cases


def selection_score(metrics):
    return .5*(metrics['accuracy'] + 1/(1+metrics['after_mse']))


def train(arm, data, sources):
    root = STUDY / arm; root.mkdir(parents=True, exist_ok=True)
    if (root / 'COMPLETE.json').exists():
        _, _, payload = load_native(root)
        if payload['sources'] != sources:
            raise ValueError('Existing joint sources differ')
        return
    if (root / 'revisions/CURRENT.json').exists():
        owner, saved, payload = load_native(root, pointer='revisions/CURRENT.json')
        if payload['sources'] != sources:
            raise ValueError('Resumed joint sources differ')
        optimizer = torch.optim.AdamW(owner.parameters(), lr=.0001, weight_decay=.0001)
        optimizer.load_state_dict(payload['optimizer'])
        torch.set_rng_state(payload['rng']); random.setstate(payload['python_rng'])
        completed = payload['step']; history = payload['development']; exposures = Counter(payload['exposures'])
        best = read(root / 'SELECTION.json')
        durable = root / 'training.jsonl'
        lines = durable.read_text().splitlines() if durable.exists() else []
        if len(lines) < completed:
            raise ValueError('Checkpoint advanced past teaching receipts')
        if len(lines) > completed:
            archive = root / ('interrupted-' + os.environ.get('SERA_FIELD_SUPERVISED', 'test') + '.jsonl')
            archive.write_text('\n'.join(lines[completed:])+'\n')
            durable.write_text('\n'.join(lines[:completed])+'\n')
    else:
        torch.manual_seed(202020); random.seed(202020)
        owner, original, _ = load_native(ROOT / 'runs/NATIVE-019/native')
        if original != sources['initial_selection']:
            raise ValueError('Initial native selection changed')
        optimizer = torch.optim.AdamW(owner.parameters(), lr=.0001, weight_decay=.0001)
        metrics, _ = evaluate(owner, data.development)
        history = [{'cycle': 0, 'metrics': metrics}]; exposures = Counter(); completed = 0
        saved = save_revision(root, owner, optimizer, 0, history, exposures, sources)
        best = {**saved, 'score': selection_score(metrics), 'metrics': metrics}
        write_json(root / 'INITIAL.json', best); write_json(root / 'SELECTION.json', best)
    with (root / 'training.jsonl').open('a', encoding='utf-8') as log:
        for index in range(completed, TOTAL):
            owner.train(); optimizer.zero_grad(set_to_none=True)
            rows = data.lesson(index)
            loss, cases, diagnostics = cycle(owner, rows, reward=arm == 'credited', training=True)
            if not bool(torch.isfinite(loss)):
                raise ValueError('Nonfinite joint objective')
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(owner.parameters(), 1., error_if_nonfinite=True)
            optimizer.step()
            kind, rehearsal = data.rehearsal.lesson(index, batch=16)
            optimizer.zero_grad(set_to_none=True)
            rehearsal_loss, _ = loss_cases(owner, data.rehearsal, kind, rehearsal)
            rehearsal_loss.backward()
            rehearsal_norm = torch.nn.utils.clip_grad_norm_(owner.parameters(), 1., error_if_nonfinite=True)
            optimizer.step()
            exposures['joint'] += len(rows); exposures[kind] += len(rehearsal)
            step = index+1; score = None
            if step % 128 == 0:
                metrics, _ = evaluate(owner, data.development)
                score = selection_score(metrics); history.append({'cycle': step, 'metrics': metrics})
            record = {'cycle': step, 'cases': cases, 'loss': float(loss.detach()), 'components': diagnostics,
                      'gradient_norm': float(norm), 'rehearsal': {'kind': kind, 'ids': [r['id'] for r in rehearsal],
                      'loss': float(rehearsal_loss.detach()), 'gradient_norm': float(rehearsal_norm)},
                      'development_score': score}
            log.write(json.dumps(record, allow_nan=False)+'\n')
            if step % 128 == 0:
                log.flush(); os.fsync(log.fileno())
                saved = save_revision(root, owner, optimizer, step, history, exposures, sources)
                if score > best['score']:
                    best = {**saved, 'score': score, 'metrics': metrics}; write_json(root / 'SELECTION.json', best)
                write_json(root / 'PROGRESS.json', {'arm': arm, 'cycle': step, 'target': TOTAL,
                           'selected': best['step'], 'utc': utc()})
                print(json.dumps({'joint_arm': arm, 'cycle': step, 'metrics': metrics,
                                  'selected': best['step']}), flush=True)
    write_json(root / 'COMPLETE.json', {'arm': arm, 'cycles': TOTAL, 'optimizer_updates': 2*TOTAL,
                'exposures': dict(exposures), 'selected': best, 'sources': sources,
                'reward_objective': arm == 'credited', 'initial_weights': read(root / 'INITIAL.json')['weights']})
