"""One full human semantic curriculum with shared-field rehearsal and capture."""
import argparse
from array import array
from collections import Counter
import hashlib
import heapq
import json
import math
import os
from pathlib import Path
import random
import time

import numpy as np
import torch
from torch.nn import functional as F

from .credit_bridge import CreditBridge, CheckedOutcome, identity
from .inquiry_study import load_inquiry
from .model import weight_hash
from .records import sha256, write_json, utc
from .semantic_owner import SemanticOwner, extend_semantic
from .study_data import ROOT
from .study_training import reading_batch, math_batch, pair_batch, physical_batch

STUDY = ROOT / 'runs/SEMANTIC-015'
DATA = ROOT / 'local/SEMANTIC-015-data-v1'
PARENT = ROOT / 'checkpoints/INQUIRY-014'
ENCODER = ('words.', 'local.', 'word_norm.')
NEW = ('semantic_', 'field.raw_curvature', 'capture_policy.')


def read(path):
    return json.loads(Path(path).read_text())


class HumanBank:
    """Random-access UTF-8 source views; large text stays on disk."""
    def __init__(self, path, reserve=0):
        self.path = Path(path); self.offsets = array('Q'); smallest = []
        with self.path.open('rb') as handle:
            while True:
                offset = handle.tell(); line = handle.readline()
                if not line:
                    break
                index = len(self.offsets); self.offsets.append(offset)
                if reserve:
                    row = json.loads(line); key = int(hashlib.sha256(('capture-015' + row['id']).encode()).hexdigest(), 16)
                    heapq.heappush(smallest, (-key, index))
                    if len(smallest) > reserve:
                        heapq.heappop(smallest)
        self.reserved = sorted(i for _, i in smallest)

    def get(self, indices):
        with self.path.open('rb') as handle:
            result = []
            for index in indices:
                handle.seek(self.offsets[index]); result.append(json.loads(handle.readline()))
        return result


def fixed_rows(path, count, prefix):
    smallest = []
    with Path(path).open(encoding='utf-8') as handle:
        for ordinal, line in enumerate(handle):
            row = json.loads(line)
            key = int(hashlib.sha256((prefix + row['id']).encode()).hexdigest(), 16)
            # Earlier corpora can contain different views with the same source
            # ID. Break ties by immutable row position, never by comparing dicts.
            heapq.heappush(smallest, (-key, row['id'], ordinal, row))
            if len(smallest) > count:
                heapq.heappop(smallest)
    return [row for _, _, _, row in sorted(smallest, reverse=True)]


def semantic_loss(owner, rows):
    logits = owner.semantic([r['premise'] for r in rows], [r['hypothesis'] for r in rows])
    labels = torch.tensor([r['target'] for r in rows])
    losses = -logits.log_softmax(-1).gather(2, labels[:, None, None].expand(-1, 3, 1)).squeeze(-1)
    mask = torch.tensor([[float((int(row['id'][:8], 16) + h) % 4 != 0) for h in range(3)] for row in rows])
    loss = (losses * mask).sum() / mask.sum()
    correct = int((logits.softmax(-1).mean(1).argmax(-1) == labels).sum())
    return loss, correct


@torch.no_grad()
def assessment(owner, rows, ablation=None):
    predictions = []; total_loss = 0.; correct = 0
    for start in range(0, len(rows), 16):
        part = rows[start:start + 16]
        logits = owner.semantic([r['premise'] for r in part], [r['hypothesis'] for r in part], ablation=ablation)
        probability = logits.softmax(-1).mean(1)
        labels = torch.tensor([r['target'] for r in part])
        total_loss += float(-probability[torch.arange(len(part)), labels].clamp_min(1e-12).log().sum())
        correct += int((probability.argmax(-1) == labels).sum())
        predictions.extend({'id': r['id'], 'source_group': r['source_group'], 'target': r['target'],
            'probability': p.tolist(), 'branch_predictions': branches.argmax(-1).tolist()}
            for r, p, branches in zip(part, probability, logits))
    return {'n': len(rows), 'accuracy': correct / len(rows), 'loss': total_loss / len(rows)}, predictions


class SemanticEngine:
    def __init__(self, owner, bank, legacy, development, source_id):
        self.owner = owner; self.bank = bank; self.legacy = legacy; self.development_rows = development
        self.source_id = source_id; self.verifier = sha256(__file__)
        self.optimizer = torch.optim.AdamW([
            {'params': [p for n, p in owner.named_parameters() if n.startswith(NEW)], 'lr': .001},
            {'params': [p for n, p in owner.named_parameters() if n.startswith(ENCODER)], 'lr': .0001}],
            weight_decay=.0001)
        self.book = CreditBridge(owner, learning_rate=.01,
            source_hashes=[source_id], verifier_hashes=[self.verifier])
        self.rng = random.Random(15115)
        reserved = set(bank.reserved)
        self.order = [i for i in range(len(bank.offsets)) if i not in reserved]; self.rng.shuffle(self.order)
        self.cursor = self.step = self.semantic_step = self.rehearsal_cursor = 0
        self.parent = None; self.best = None; self.history = []; self.exposures = Counter()
        self.last_lesson = None
        self.configure_gradients()

    def configure_gradients(self):
        for name, parameter in self.owner.named_parameters():
            parameter.requires_grad_(name.startswith(NEW) or (self.semantic_step >= 1024 and name.startswith(ENCODER)))

    def update(self):
        self.configure_gradients(); self.optimizer.zero_grad(set_to_none=True)
        rehearsal = (self.step + 1) % 5 == 0
        if not rehearsal:
            indices = self.order[self.cursor:self.cursor + 32]
            rows = self.bank.get(indices)
            if not rows:
                raise ValueError('Primary curriculum is complete')
            loss, _ = semantic_loss(self.owner, rows)
            self.cursor += len(rows); self.semantic_step += 1
            self.exposures['human_semantic'] += len(rows); self.last_lesson = rows[-1]
        else:
            schedule = ['reading', 'math', *sorted(self.legacy['pairs']), 'physics']
            kind = schedule[self.rehearsal_cursor % len(schedule)]
            self.rehearsal_cursor += 1
            if kind == 'physics':
                loss, _ = physical_batch(self.owner, 15115,
                    list(range(self.rehearsal_cursor * 16, (self.rehearsal_cursor + 1) * 16)), 'SEMANTIC-015-rehearsal')
            else:
                bank = self.legacy[kind] if kind in ('reading', 'math') else self.legacy['pairs'][kind]
                rows = [bank[self.rng.randrange(len(bank))] for _ in range(16)]
                if kind == 'reading':
                    loss, _ = reading_batch(self.owner, rows)
                elif kind == 'math':
                    loss, _ = math_batch(self.owner, rows)
                else:
                    loss, _ = pair_batch(self.owner, rows, bank, self.rng)
            self.exposures['rehearsal:' + kind] += 16
        if not torch.isfinite(loss):
            raise ValueError('Nonfinite semantic update; retain last durable revision')
        loss.backward(); torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1., error_if_nonfinite=True)
        self.optimizer.step(); self.step += 1
        return float(loss.detach())

    def capture_practice(self):
        if self.last_lesson is None or len(self.bank.reserved) < 12:
            return None
        indices = self.rng.sample(self.bank.reserved, 12); rows = self.bank.get(indices)
        with torch.no_grad():
            self.owner.semantic([self.last_lesson['premise']], [self.last_lesson['hypothesis']])
            tag = self.owner.field.last_curvature[self.step % 3].clone()
            proposal = self.owner.field.curvature_memory.propose(tag)
            before, predictions = assessment(self.owner, rows)
            probability = torch.tensor([r['probability'] for r in predictions])
            entropy = -(probability * probability.clamp_min(1e-12).log()).sum(-1).mean()
            features = torch.tensor([float(entropy), float(tag.square().mean()),
                float(self.owner.field.curvature_memory.active.float().mean()),
                float(probability.max(-1).values.mean())])
        logits = self.owner.capture_policy(features)
        choice = int(torch.multinomial(logits.detach().softmax(-1), 1))
        predictor = weight_hash(self.owner)
        goal = identity(['SEMANTIC-015-annotation-progress', [r['id'] for r in rows]])
        decision = identity([goal, self.step, predictor, self.last_lesson['id']])
        scope = 'human-annotation-relative-semantic-loss-with-accuracy-guard'
        self.book.record_decision(decision=decision, goal=goal, logits=logits, choice=choice,
            predictor=predictor, assumptions_id=scope)
        after = before
        if choice:
            self.owner.field.curvature_preview = proposal
            try:
                with torch.no_grad():
                    after, _ = assessment(self.owner, rows)
            finally:
                self.owner.field.curvature_preview = None
        graded_loss = after['loss'] if after['accuracy'] >= before['accuracy'] else max(before['loss'], after['loss'])
        intervention = identity(['conditional_curvature_capture', choice, identity(tag.tolist())])
        outcome = CheckedOutcome(goal, decision, predictor, predictor,
            identity([self.source_id, self.step, [r['id'] for r in rows]]), self.source_id, self.verifier,
            identity([goal, self.step, before, after]), 'human_assessment', intervention, intervention,
            before['loss'], graded_loss, True, 'curvature-semantic-capture-v1', scope)
        event = self.book.apply(outcome)
        captured = None
        if event['accepted'] and choice and after['accuracy'] >= before['accuracy'] and after['loss'] < before['loss']:
            captured = self.owner.field.curvature_memory.capture(tag, event,
                predictor=predictor, decision_policy=predictor)
        return {'step': self.step, 'lesson_id': self.last_lesson['id'], 'assessed_ids': [r['id'] for r in rows],
                'choice': choice, 'before': before, 'after': after, 'credit': event, 'capture': captured}

    def snapshot(self, root):
        progress = {'step': self.step, 'semantic_step': self.semantic_step, 'cursor': self.cursor,
            'order': self.order, 'rehearsal_cursor': self.rehearsal_cursor,
            'sampling_rng': self.rng.getstate(), 'optimizer': self.optimizer.state_dict(),
            'exposures': dict(self.exposures), 'history': self.history, 'last_lesson': self.last_lesson,
            'source_id': self.source_id, 'best': self.best}
        saved = self.book.commit(root / 'revisions', expected_parent=self.parent, progress=progress)
        self.parent = saved['sha256']
        return saved

    def resume(self, root):
        saved = self.book.load_current(root / 'revisions'); self.parent = saved['sha256']; p = saved['progress']
        if p['source_id'] != self.source_id:
            raise ValueError('Human source manifest changed')
        for key in ('step', 'semantic_step', 'cursor', 'order', 'rehearsal_cursor', 'history', 'last_lesson', 'best'):
            setattr(self, key, p[key])
        self.rng.setstate(p['sampling_rng']); self.optimizer.load_state_dict(p['optimizer'])
        self.exposures = Counter(p['exposures']); self.configure_gradients()
        # A successful development selection is written after its content-addressed
        # revision exists; the durable selection pointer is authoritative on resume.
        self.best = read(root / 'SELECTION.json')


def legacy_data(root=None):
    root = Path(root) if root is not None else ROOT / 'local/CONNECTED-003-data-v1'
    result = {kind: fixed_rows(root / ('train-' + kind + '.jsonl'), count, 'SEMANTIC-015-rehearsal')
              for kind, count in (('reading', 2048), ('math', 1024))}
    tracks = {}
    with (root / 'train-pairs.jsonl').open(encoding='utf-8') as handle:
        for ordinal, line in enumerate(handle):
            row = json.loads(line); key = int(hashlib.sha256(('SEMANTIC-015-rehearsal' + row['id']).encode()).hexdigest(), 16)
            bank = tracks.setdefault(row['track'], [])
            heapq.heappush(bank, (-key, row['id'], ordinal, row))
            if len(bank) > 256:
                heapq.heappop(bank)
    result['pairs'] = {name: [r for _, _, _, r in bank] for name, bank in tracks.items()}
    return result


def load_semantic(root):
    root = Path(root); selected = read(root / 'SELECTION.json')
    path = root / 'revisions' / selected['revision']
    if path.resolve().parent != (root / 'revisions').resolve() or sha256(path) != selected['sha256']:
        raise ValueError('Semantic revision identity changed')
    payload = torch.load(path, map_location='cpu', weights_only=False)
    spec = dict(payload['bridge']['specification'])
    if spec.pop('type') != 'curvature-semantic-015':
        raise ValueError('Wrong semantic owner')
    owner = SemanticOwner(**spec); owner.load_state_dict(payload['bridge']['owner'])
    if weight_hash(owner) != selected['weights']:
        raise ValueError('Semantic owner weights changed')
    return owner, selected


def train():
    root = STUDY / 'coupled'; root.mkdir(parents=True, exist_ok=True)
    if (root / 'COMPLETE.json').exists():
        load_semantic(root); return
    parent, parent_selection = load_inquiry(PARENT)
    if (root / 'PARENT.json').exists() and read(root / 'PARENT.json') != parent_selection:
        raise ValueError('Preserve the registered semantic parent while resuming')
    owner = extend_semantic(parent)
    bank = HumanBank(DATA / 'train.jsonl', reserve=2048)
    development = fixed_rows(DATA / 'development.jsonl', 512, 'SEMANTIC-015-development')
    source_id = identity([sha256(DATA / 'MANIFEST.json'), sha256(ROOT / 'local/CONNECTED-003-data-v1/MANIFEST.json')])
    engine = SemanticEngine(owner, bank, legacy_data(), development, source_id)
    torch.manual_seed(15115)
    if (root / 'revisions/CURRENT.json').exists():
        engine.resume(root)
    else:
        initial, _ = assessment(owner, development)
        engine.history.append({'semantic_step': 0, **initial})
        saved = engine.snapshot(root)
        engine.best = {**saved, 'semantic_step': 0, 'accuracy': initial['accuracy'], 'loss': initial['loss']}
        write_json(root / 'SELECTION.json', engine.best)
        write_json(root / 'PARENT.json', parent_selection)
        write_json(root / 'INITIAL.json', engine.best)
    logpath = root / ('updates-' + os.environ['SERA_FIELD_SUPERVISED'] + '.jsonl')
    with logpath.open('x', encoding='utf-8') as log:
        last_development = engine.history[-1]['semantic_step']
        while engine.cursor < len(engine.order):
            loss = engine.update()
            row = {'step': engine.step, 'semantic_step': engine.semantic_step, 'loss': loss}
            if engine.step % 128 == 0:
                row['capture'] = engine.capture_practice()
            if engine.step % 256 == 0:
                row['consolidation'] = owner.field.consolidate()
            completed = engine.cursor == len(engine.order)
            due = engine.semantic_step != last_development and (engine.semantic_step % 1024 == 0 or completed)
            score = None
            if due:
                score, _ = assessment(owner, development); last_development = engine.semantic_step
                engine.history.append({'semantic_step': engine.semantic_step, **score})
                row['development'] = score
            if engine.step % 256 == 0 or due or completed:
                saved = engine.snapshot(root)
                if score and (score['accuracy'], -score['loss']) > (engine.best['accuracy'], -engine.best['loss']):
                    engine.best = {**saved, 'semantic_step': engine.semantic_step, **score}
                    write_json(root / 'SELECTION.json', engine.best)
                write_json(root / 'PROGRESS.json', {'step': engine.step, 'semantic_step': engine.semantic_step,
                    'human_pairs_seen': engine.cursor, 'human_pairs_target': len(engine.order),
                    'curvature_captures': int(owner.field.curvature_memory.cursor), 'updated_utc': utc()})
                print(json.dumps({'semantic_step': engine.semantic_step, 'pairs': engine.cursor, 'loss': loss}), flush=True)
                log.flush()
            log.write(json.dumps(row) + '\n')
            if (STUDY / 'PAUSE_REQUEST.json').exists():
                engine.snapshot(root); write_json(root / 'PAUSED.json', {'step': engine.step}); return
    write_json(root / 'COMPLETE.json', {'exposures': dict(engine.exposures), 'updates': engine.step,
        'semantic_updates': engine.semantic_step, 'selected': read(root / 'SELECTION.json'),
        'development': engine.history, 'parent': parent_selection, 'source_id': source_id,
        'curvature_captures': int(owner.field.curvature_memory.cursor), 'source_manifest': read(DATA / 'MANIFEST.json')})


def register():
    if (STUDY / 'FINAL_REGISTRATION.json').exists():
        return
    if not (STUDY / 'coupled/COMPLETE.json').exists():
        raise ValueError('Complete teaching before final registration')
    cohort = fixed_rows(DATA / 'sealed.jsonl', 4096, 'SEMANTIC-015-final')
    write_json(STUDY / 'FINAL_REGISTRATION.json', {'selected_sha256': sha256(STUDY / 'coupled/SELECTION.json'),
        'source_manifest_sha256': sha256(DATA / 'MANIFEST.json'), 'ids': [r['id'] for r in cohort],
        'source_groups': sorted({r['source_group'] for r in cohort}),
        'protocol_sha256': sha256(ROOT / 'protocols/SEMANTIC-015.md'), 'created_utc': utc()})


def evaluate(arm, replay=False):
    registration = read(STUDY / 'FINAL_REGISTRATION.json')
    if sha256(STUDY / 'coupled/SELECTION.json') != registration['selected_sha256']:
        raise ValueError('Selected owner changed after registration')
    if arm == 'initialized':
        parent, _ = load_inquiry(PARENT); owner = extend_semantic(parent); selected = read(STUDY / 'coupled/INITIAL.json')
        if weight_hash(owner) != selected['weights']:
            raise ValueError('Initialized owner identity changed')
    else:
        owner, selected = load_semantic(STUDY / 'coupled')
    owner.eval(); before = weight_hash(owner)
    owner.field.curvature_disconnected = arm == 'no_curvature'
    rows = fixed_rows(DATA / 'sealed.jsonl', 4096, 'SEMANTIC-015-final')
    if [r['id'] for r in rows] != registration['ids']:
        raise ValueError('Final cohort changed')
    destination = STUDY / ('replay' if replay else 'final') / arm
    destination.mkdir(parents=True, exist_ok=True)
    if (destination / 'RESULTS.json').exists():
        return
    metrics, predictions = assessment(owner, rows, ablation=arm)
    path = destination / 'cases.jsonl'
    path.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in predictions), encoding='utf-8')
    confusion = np.zeros((3, 3), dtype='int64')
    for record in predictions:
        confusion[record['target'], int(np.argmax(record['probability']))] += 1
    metrics.update({'arm': arm, 'selection': selected, 'weights_before': before, 'weights_after': weight_hash(owner),
                    'cases_sha256': sha256(path), 'confusion': confusion.tolist(),
                    'branch_disagreement': sum(len(set(r['branch_predictions'])) > 1 for r in predictions) / len(predictions)})
    assert metrics['weights_before'] == metrics['weights_after']
    write_json(destination / 'RESULTS.json', metrics); print(json.dumps(metrics), flush=True)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=('train', 'register', 'evaluate'))
    parser.add_argument('--arm', default='coupled', choices=('coupled', 'initialized', 'no_imagination', 'no_curvature', 'hypothesis_only'))
    parser.add_argument('--replay', action='store_true'); args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1); STUDY.mkdir(parents=True, exist_ok=True)
    if args.action == 'train': train()
    elif args.action == 'register': register()
    else: evaluate(args.arm, args.replay)


if __name__ == '__main__':
    main()
