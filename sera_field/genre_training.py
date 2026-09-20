"""Matched full human-genre teaching of the continuing conditional field."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import random

import torch

from .credit_bridge import CreditBridge, identity
from .genre_owner import GenreOwner, extend_genre
from .history_training import load_history
from .model import weight_hash
from .records import sha256, write_json, utc
from .semantic_training import (HumanBank, SemanticEngine, assessment, fixed_rows,
    legacy_data, load_semantic, semantic_loss)
from .study_data import ROOT
from .study_training import reading_batch, math_batch, pair_batch, physical_batch
from .gauge import adjoint_rotations

STUDY = ROOT / 'runs/GENRE-017'
DATA = ROOT / 'local/HUMAN-GENRE-data-v1'
ARMS = {'exact_noisy': ('exact', .03), 'exact_clean': ('exact', 0.), 'gaussian_noisy': ('gaussian', .03)}
NEW = ('semantic_', 'field.ensemble_action.')
ENCODER = ('words.', 'local.', 'word_norm.')


def read(path):
    return json.loads(Path(path).read_text())


def parent_owner():
    decision = ROOT / 'reports/HISTORY-016/QUALIFICATION.json'
    if not decision.exists():
        raise ValueError('Finish the current history audit before choosing the next parent')
    if read(decision)['all_gates']:
        owner, selection = load_history(ROOT / 'checkpoints/HISTORY-016')
        kind = 'qualified-history-016'
    else:
        owner, selection = load_semantic(ROOT / 'checkpoints/SEMANTIC-015')
        kind = 'qualified-semantic-015; unqualified history candidate preserved'
    return owner, {'selection': selection, 'parent_rule': kind, 'history_decision_sha256': sha256(decision)}


def assess(owner, bank, *, ablation=None):
    training = owner.training; action = owner.field.action_mode
    owner.eval()
    if ablation == 'no_action': owner.field.action_mode = 'disabled'
    try:
        metrics, cases = assessment(owner, bank, ablation=ablation)
        by_id = {row['id']: row for row in bank}
        for case in cases: case['genre'] = by_id[case['id']].get('genre', 'preserved-SNLI')
        return metrics, cases
    finally:
        owner.train(training); owner.field.action_mode = action


class GenreEngine(SemanticEngine):
    """Reuse durable cursor/RNG storage, with a separately frozen curriculum."""
    def __init__(self, owner, bank, legacy, snli, development, source_id):
        self.owner = owner; self.bank = bank; self.legacy = legacy; self.snli = snli
        self.development_rows = development; self.source_id = source_id
        self.verifier = sha256(__file__)
        self.optimizer = torch.optim.AdamW([
            {'params': [p for n, p in owner.named_parameters() if n.startswith(NEW)], 'lr': .001},
            {'params': [p for n, p in owner.named_parameters() if n.startswith(ENCODER)], 'lr': .0001}],
            weight_decay=.0001)
        self.book = CreditBridge(owner, source_hashes=[source_id], verifier_hashes=[self.verifier])
        self.rng = random.Random(17117)
        self.order = list(range(len(bank.offsets))); self.rng.shuffle(self.order)
        self.cursor = self.step = self.semantic_step = self.rehearsal_cursor = 0
        self.parent = None; self.best = None; self.history = []; self.exposures = Counter()
        self.last_lesson = None; self.configure_gradients()

    def configure_gradients(self):
        for name, parameter in self.owner.named_parameters():
            parameter.requires_grad_(name.startswith(NEW) or
                (self.semantic_step >= 1024 and name.startswith(ENCODER)))

    def update(self):
        self.owner.train(); self.configure_gradients(); self.optimizer.zero_grad(set_to_none=True)
        rehearsal = (self.step + 1) % 5 == 0
        identifiers = []
        if not rehearsal:
            indices = self.order[self.cursor:self.cursor + 32]
            rows = self.bank.get(indices)
            if not rows: raise ValueError('Primary curriculum already completed')
            loss, _ = semantic_loss(self.owner, rows)
            self.cursor += len(rows); self.semantic_step += 1
            kind = 'human_genre'; self.exposures[kind] += len(rows)
            self.last_lesson = rows[-1]; identifiers = [r['id'] for r in rows]
        else:
            schedule = ['reading', 'math', *sorted(self.legacy['pairs']), 'semantic', 'physics']
            kind = schedule[self.rehearsal_cursor % len(schedule)]
            self.rehearsal_cursor += 1
            if kind == 'physics':
                numbers = list(range(self.rehearsal_cursor * 16, (self.rehearsal_cursor + 1) * 16))
                loss, _ = physical_batch(self.owner, 17117, numbers, 'GENRE-017-rehearsal')
                identifiers = [f'GENRE-017-rehearsal:{i}' for i in numbers]
            elif kind == 'semantic':
                rows = self.snli.get([self.rng.randrange(len(self.snli.offsets)) for _ in range(16)])
                loss, _ = semantic_loss(self.owner, rows); identifiers = [r['id'] for r in rows]
            else:
                bank = self.legacy[kind] if kind in ('reading', 'math') else self.legacy['pairs'][kind]
                rows = [bank[self.rng.randrange(len(bank))] for _ in range(16)]
                if kind == 'reading': loss, _ = reading_batch(self.owner, rows)
                elif kind == 'math': loss, _ = math_batch(self.owner, rows)
                else: loss, _ = pair_batch(self.owner, rows, bank, self.rng)
                identifiers = [r['id'] for r in rows]
            self.exposures['rehearsal:' + kind] += 16
        if not torch.isfinite(loss):
            raise ValueError('Nonfinite genre loss; preserve the last exact revision')
        loss.backward(); torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1., error_if_nonfinite=True)
        self.optimizer.step(); self.step += 1
        return {'loss': float(loss.detach()), 'kind': kind, 'ids': identifiers,
                'step': self.step, 'semantic_step': self.semantic_step}

    def resume(self, root):
        super().resume(root)
        # A durable completed assessment can precede its pointer by one file
        # write. Recover only that exact saved development decision.
        last = self.history[-1]
        if last['semantic_step'] == self.semantic_step and (last['accuracy'], -last['loss']) > \
                (self.best['accuracy'], -self.best['loss']):
            self.best = {**read(root / 'revisions/CURRENT.json'), **last}
            write_json(root / 'SELECTION.json', self.best)


def load_genre(root):
    root = Path(root); selected = read(root / 'SELECTION.json')
    path = root / 'revisions' / selected['revision']
    if path.resolve().parent != (root / 'revisions').resolve() or sha256(path) != selected['sha256']:
        raise ValueError('Genre revision identity changed')
    payload = torch.load(path, map_location='cpu', weights_only=False)
    spec = dict(payload['bridge']['specification'])
    if spec.pop('type') != 'finite-neural-action-017': raise ValueError('Wrong genre owner')
    owner = GenreOwner(**spec); owner.load_state_dict(payload['bridge']['owner'])
    if weight_hash(owner) != selected['weights']: raise ValueError('Genre tensor identity changed')
    return owner, selected


def sources():
    expected = '40e3b405de1a964045ad9af9c2d36b75dc8924bfb54b097334881d989057e9e3'
    if sha256(DATA / 'MANIFEST.json') != expected: raise ValueError('Frozen human manifest changed')
    manifest = read(DATA / 'MANIFEST.json')
    for name, info in manifest['partitions'].items():
        if sha256(DATA / (name + '.jsonl')) != info['sha256']: raise ValueError('A human source view changed')
    return {'genre_manifest': expected,
        'legacy_manifest': sha256(ROOT / 'local/CONNECTED-003-data-v1/MANIFEST.json'),
        'semantic_manifest': sha256(ROOT / 'local/SEMANTIC-015-data-v1/MANIFEST.json'),
        'protocol': sha256(ROOT / 'protocols/GENRE-017.md')}


def train(arm):
    root = STUDY / arm; root.mkdir(parents=True, exist_ok=True)
    if (root / 'COMPLETE.json').exists(): load_genre(root); return
    parent, parent_selection = parent_owner(); source = sources()
    if (root / 'PARENT.json').exists() and read(root / 'PARENT.json') != parent_selection:
        raise ValueError('Registered parent changed; preserve the existing study')
    owner = extend_genre(parent, action_kind=ARMS[arm][0], teaching_noise=ARMS[arm][1])
    bank = HumanBank(DATA / 'train.jsonl')
    if len(bank.offsets) != 371929: raise ValueError('Frozen primary teaching count changed')
    development = fixed_rows(DATA / 'development.jsonl', 512, 'GENRE-017-development')
    snli = HumanBank(ROOT / 'local/SEMANTIC-015-data-v1/train.jsonl')
    source_id = identity([source, parent_selection])
    engine = GenreEngine(owner, bank, legacy_data(), snli, development, source_id)
    torch.manual_seed(17117)
    if (root / 'revisions/CURRENT.json').exists():
        engine.resume(root)
    else:
        initial, _ = assess(owner, development)
        engine.history.append({'semantic_step': 0, **initial})
        saved = engine.snapshot(root)
        engine.best = {**saved, 'semantic_step': 0, **initial}
        write_json(root / 'SELECTION.json', engine.best); write_json(root / 'INITIAL.json', engine.best)
        write_json(root / 'PARENT.json', parent_selection); write_json(root / 'SOURCES.json', source)
    with (root / ('updates-' + os.environ['SERA_FIELD_SUPERVISED'] + '.jsonl')).open('x', encoding='utf-8') as log:
        last_development = engine.history[-1]['semantic_step']
        while engine.cursor < len(engine.order):
            record = engine.update(); complete = engine.cursor == len(engine.order)
            due = engine.semantic_step != last_development and (engine.semantic_step % 1024 == 0 or complete)
            score = None
            if due:
                score, _ = assess(owner, development); last_development = engine.semantic_step
                engine.history.append({'semantic_step': engine.semantic_step, **score}); record['development'] = score
            if engine.step % 256 == 0 or due or complete:
                saved = engine.snapshot(root)
                if score and (score['accuracy'], -score['loss']) > (engine.best['accuracy'], -engine.best['loss']):
                    engine.best = {**saved, 'semantic_step': engine.semantic_step, **score}
                    write_json(root / 'SELECTION.json', engine.best)
                write_json(root / 'PROGRESS.json', {'arm': arm, 'step': engine.step,
                    'semantic_step': engine.semantic_step, 'primary_seen': engine.cursor,
                    'primary_target': len(engine.order), 'utc': utc()})
                print(json.dumps({'arm': arm, 'primary_seen': engine.cursor, 'loss': record['loss']}), flush=True)
            log.write(json.dumps(record) + '\n')
            if engine.step % 256 == 0 or due or complete: log.flush()
            if (STUDY / 'PAUSE_REQUEST.json').exists():
                engine.snapshot(root); write_json(root / 'PAUSED.json', {'step': engine.step}); return
    write_json(root / 'COMPLETE.json', {'arm': arm, 'exposures': dict(engine.exposures),
        'updates': engine.step, 'primary_updates': engine.semantic_step, 'selected': read(root / 'SELECTION.json'),
        'development': engine.history, 'parent': parent_selection, 'source_id': source_id,
        'factual_captures': 0, 'new_procedure': 'conditional field and semantic gradients from human supervision'})


def final_rows():
    return {split: fixed_rows(DATA / ('sealed_' + split + '.jsonl'), 4096, 'GENRE-017-final-' + split)
            for split in ('matched', 'mismatched')}


def register():
    destination = STUDY / 'FINAL_REGISTRATION.json'
    if destination.exists(): return
    if any(not (STUDY / arm / 'COMPLETE.json').exists() for arm in ARMS):
        raise ValueError('All matched training arms must finish before any final opens')
    _, parent = parent_owner()
    write_json(destination, {'selections': {arm: sha256(STUDY / arm / 'SELECTION.json') for arm in ARMS},
        'sources': sources(), 'parent': parent,
        'ids': {split: [r['id'] for r in rows] for split, rows in final_rows().items()}, 'utc': utc()})


def evaluate(arm, replay=False):
    registration = read(STUDY / 'FINAL_REGISTRATION.json')
    if sources() != registration['sources']: raise ValueError('Registered source identities changed')
    if any(sha256(STUDY / name / 'SELECTION.json') != value for name, value in registration['selections'].items()):
        raise ValueError('A registered selection changed')
    if arm == 'parent':
        original, selection = parent_owner()
        if selection != registration['parent']: raise ValueError('Registered parent changed')
        owner = extend_genre(original)
    else:
        owner, selection = load_genre(STUDY / (arm if arm in ARMS else 'exact_noisy'))
    owner.eval(); before = weight_hash(owner)
    for split, bank in final_rows().items():
        if [r['id'] for r in bank] != registration['ids'][split]: raise ValueError('Final cases changed')
        root = STUDY / ('replay' if replay else 'final') / arm / split
        if (root / 'RESULTS.json').exists(): continue
        metrics, cases = assess(owner, bank, ablation=arm)
        root.mkdir(parents=True, exist_ok=True); path = root / 'cases.jsonl'
        path.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in cases), encoding='utf-8')
        field = owner.field; transport = adjoint_rotations(field.links).transpose(-1, -2)
        diagnostics = field.ensemble_action.diagnostics(field.last_action_source, transport)
        if weight_hash(owner) != before: raise ValueError('Final assessment mutated its owner')
        metrics.update(arm=arm, split=split, selection=selection, cases_sha256=sha256(path),
            weights_before=before, weights_after=weight_hash(owner), action_diagnostics=diagnostics,
            final_parameter_updates=0, factual_captures=0)
        write_json(root / 'RESULTS.json', metrics)
        print(json.dumps({k: metrics[k] for k in ('arm', 'split', 'accuracy', 'loss')}), flush=True)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=('train', 'register', 'evaluate'))
    parser.add_argument('--arm', choices=(*ARMS, 'parent', 'no_imagination', 'no_action'), default='exact_noisy')
    parser.add_argument('--replay', action='store_true'); args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1); STUDY.mkdir(parents=True, exist_ok=True)
    if args.action == 'train':
        if args.arm not in ARMS: raise ValueError('Only registered arms may be trained')
        train(args.arm)
    elif args.action == 'register': register()
    else: evaluate(args.arm, args.replay)


if __name__ == '__main__': main()
