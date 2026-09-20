"""Sustained, exactly resumable human/simulation training of one fresh owner."""
import copy
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import time

import numpy as np
import torch
from torch.nn import functional as F

from .credit_bridge import CreditBridge, identity
from .grounded_owner import GroundedOwner
from .model import weight_hash
from .records import sha256, utc, write_json
from .study_data import ROOT, load_records
from .study_world import draw, stable_seed

SCHEDULE = ('reading', 'reading', 'math', 'pairs', 'physics', 'reading', 'math', 'pairs',
            'physics', 'pairs', 'reading', 'physics')


def multi_target_loss(logits, targets):
    logs = logits.log_softmax(-1)
    return torch.stack([-torch.logsumexp(logs[i, choices], dim=0) for i, choices in enumerate(targets)]).mean()


def reading_batch(owner, rows):
    logits = owner.rank([r['question'] for r in rows], [r['options'] for r in rows])
    loss = multi_target_loss(logits, [r['targets'] for r in rows])
    correct = sum(int(int(logits[i].argmax()) in row['targets']) for i, row in enumerate(rows))
    return loss, correct


def math_batch(owner, rows):
    logits = owner.math_logits([r['question'] for r in rows], [r['values'] for r in rows])
    n = logits.shape[-1]
    targets = []
    for row in rows:
        op, a, b = row['target']
        options = [op * n * n + a * n + b]
        if op in (0, 2) and a != b:
            options.append(op * n * n + b * n + a)
        targets.append(options)
    flat = logits.flatten(1)
    loss = multi_target_loss(flat, targets)
    correct = sum(int(int(flat[i].argmax()) in choices) for i, choices in enumerate(targets))
    return loss, correct


def pair_inputs(rows, bank, rng):
    options, labels = [], []
    for row in rows:
        choices = [row['answer']]
        attempts = 0
        while len(choices) < 4 and attempts < 100:
            other = bank[rng.randrange(len(bank))]['answer']
            if other not in choices:
                choices.append(other)
            attempts += 1
        rng.shuffle(choices)
        labels.append([choices.index(row['answer'])])
        options.append(choices)
    return [r['question'] for r in rows], options, labels


def pair_batch(owner, rows, bank, rng):
    questions, options, labels = pair_inputs(rows, bank, rng)
    logits = owner.rank(questions, options)
    return multi_target_loss(logits, labels), sum(int(int(logits[i].argmax()) == x[0]) for i, x in enumerate(labels))


def physical_batch(owner, seed, indices, split):
    observations, present = torch.zeros(len(indices), 6, 3), torch.zeros(len(indices), 6)
    queries, targets = [], []
    for i, index in enumerate(indices):
        _, support, query, truth = draw(seed, index, split)
        observations[i, :len(support)] = torch.from_numpy(support)
        present[i, :len(support)] = 1
        queries.append(query)
        targets.append(truth)
    query, truth = torch.from_numpy(np.stack(queries)), torch.from_numpy(np.stack(targets))
    world = owner.world(observations, present)
    prediction = owner.consequences(world['coefficients'], query)
    # Deterministic bootstrap inclusion, to preserve a conditional hypothesis cloud.
    inclusion = torch.tensor([[float((index + h) % 4 != 0) for h in range(3)] for index in indices])
    loss = (((prediction - truth[:, None]) ** 2).mean(-1) * inclusion).sum() / inclusion.sum()
    mse = (prediction.mean(1) - truth).square().mean().item()
    return loss, mse


def small_cohort(rows, n):
    return sorted(rows, key=lambda r: hashlib.sha256(('development-v1' + r['id']).encode()).hexdigest())[:n]


class Curriculum:
    def __init__(self, root):
        self.root = Path(root)
        self.manifest_sha = identity([sha256(self.root / 'MANIFEST.json'), sha256(self.root / 'SPLIT_AUDIT.json')])
        self.train = {k: load_records(root, 'train', k) for k in ('reading', 'math', 'pairs')}
        self.dev = {k: load_records(root, 'development', k) for k in ('reading', 'math', 'pairs')}
        self.pairs, self.dev_pairs = {}, {}
        for record in self.train['pairs']:
            self.pairs.setdefault(record['track'], []).append(record)
        for record in self.dev['pairs']:
            self.dev_pairs.setdefault(record['track'], []).append(record)
        self.tracks = sorted(self.pairs)


class Engine:
    def __init__(self, curriculum, *, seed=1103, width=48, owner_kind='field'):
        self.data = curriculum
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.set_num_threads(1)
        if owner_kind == 'field':
            self.owner = GroundedOwner(width=width)
        elif owner_kind == 'scfe':
            from .scfe_owner import ScfeOwner
            self.owner = ScfeOwner(width=width)
        else:
            raise ValueError('Unknown explicit owner type')
        self.initial_hash = weight_hash(self.owner)
        self.optimizer = torch.optim.AdamW(self.owner.parameters(), lr=.0015, weight_decay=.0001)
        self.book = CreditBridge(self.owner, verifier_hashes=[sha256(ROOT / 'sera_field/study_world.py')],
                                 source_hashes=[curriculum.manifest_sha, sha256(ROOT / 'sera_field/study_world.py')])
        self.rng = random.Random(seed)
        self.step = 0
        self.pair_cursor = 0
        self.physics_cursor = 0
        self.samplers = {}
        self.exposures, self.seen = Counter(), set()
        self.development, self.initial_dev = [], None
        self.parent, self.best = None, None

    def sample(self, key, bank, batch):
        if key not in self.samplers:
            order = list(range(len(bank)))
            self.rng.shuffle(order)
            self.samplers[key] = {'order': order, 'cursor': 0, 'epochs': 0}
        state = self.samplers[key]
        result = []
        for _ in range(batch):
            if state['cursor'] == len(state['order']):
                self.rng.shuffle(state['order'])
                state['cursor'] = 0
                state['epochs'] += 1
            row = bank[state['order'][state['cursor']]]
            state['cursor'] += 1
            result.append(row)
            self.seen.add(row['id'])
            self.exposures[row['track']] += 1
        return result

    def update(self, batch=24):
        kind = SCHEDULE[self.step % len(SCHEDULE)]
        self.owner.train()
        self.optimizer.zero_grad(set_to_none=True)
        if kind == 'reading':
            rows = self.sample(kind, self.data.train[kind], batch)
            loss, correct = reading_batch(self.owner, rows)
        elif kind == 'math':
            rows = self.sample(kind, self.data.train[kind], batch)
            loss, correct = math_batch(self.owner, rows)
        elif kind == 'pairs':
            track = self.data.tracks[self.pair_cursor % len(self.data.tracks)]
            self.pair_cursor += 1
            rows = self.sample('pair:' + track, self.data.pairs[track], batch)
            loss, correct = pair_batch(self.owner, rows, self.data.pairs[track], self.rng)
            kind = 'pair:' + track
        else:
            indices = list(range(self.physics_cursor, self.physics_cursor + batch))
            self.physics_cursor += batch
            self.exposures['physical_simulation'] += batch
            loss, correct = physical_batch(self.owner, self.seed, indices, 'teaching')
        if not torch.isfinite(loss):
            raise ValueError('Non-finite loss; preserve prior checkpoint')
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 3., error_if_nonfinite=True)
        self.optimizer.step()
        self.step += 1
        return {'step': self.step, 'kind': kind, 'loss': float(loss.detach()),
                'correct_or_physics_mse': correct, 'attempts': batch}

    @torch.no_grad()
    def evaluate(self):
        self.owner.eval()
        results = {}
        for kind, function, maximum in (('reading', reading_batch, 384), ('math', math_batch, 256)):
            rows = small_cohort(self.data.dev[kind], maximum)
            losses, correct = [], 0
            for start in range(0, len(rows), 16):
                part = rows[start:start+16]
                loss, count = function(self.owner, part)
                losses.append(float(loss) * len(part))
                correct += count
            results[kind] = {'loss': sum(losses)/len(rows), 'accuracy': correct/len(rows), 'n': len(rows)}
        for track, bank in self.data.dev_pairs.items():
            rows = small_cohort(bank, 64)
            rng = random.Random(stable_seed('development', track))
            losses, correct = [], 0
            for start in range(0, len(rows), 16):
                part = rows[start:start+16]
                loss, count = pair_batch(self.owner, part, bank, rng)
                losses.append(float(loss)*len(part))
                correct += count
            results['pair:' + track] = {'loss': sum(losses)/len(rows), 'accuracy': correct/len(rows), 'n': len(rows)}
        losses = []
        for start in range(0, 256, 32):
            _, mse = physical_batch(self.owner, self.seed, list(range(start, start+32)), 'development')
            losses.append(mse)
        results['physics'] = {'loss': float(np.mean(losses)), 'n': 256}
        if self.initial_dev is None:
            self.initial_dev = copy.deepcopy(results)
        # Each objective family has equal weight; book tracks do not overwhelm physics/math.
        ratios = {k: v['loss'] / max(1e-8, self.initial_dev[k]['loss']) for k, v in results.items()}
        pair_mean = float(np.mean([v for k, v in ratios.items() if k.startswith('pair:')]))
        score = (ratios['reading'] + ratios['math'] + ratios['physics'] + pair_mean) / 4
        record = {'step': self.step, 'score': score, 'metrics': results, 'weights': weight_hash(self.owner)}
        self.development.append(record)
        return record

    def save(self, root):
        progress = {'step': self.step, 'seed': self.seed, 'data_manifest_sha256': self.data.manifest_sha,
                    'initial_hash': self.initial_hash, 'optimizer': self.optimizer.state_dict(),
                    'samplers': self.samplers, 'local_rng': self.rng.getstate(),
                    'pair_cursor': self.pair_cursor, 'physics_cursor': self.physics_cursor,
                    'exposures': dict(self.exposures), 'seen': sorted(self.seen),
                    'development': self.development, 'initial_dev': self.initial_dev, 'best': self.best}
        manifest = self.book.commit(root, expected_parent=self.parent, progress=progress)
        self.parent = manifest['sha256']
        return manifest

    def resume(self, root):
        saved = self.book.load_current(root)
        self.parent = saved['sha256']
        p = saved['progress']
        if p['data_manifest_sha256'] != self.data.manifest_sha or p['seed'] != self.seed:
            raise ValueError('Resume source/seed mismatch')
        self.optimizer.load_state_dict(p['optimizer'])
        self.step, self.initial_hash = p['step'], p['initial_hash']
        self.samplers, self.pair_cursor, self.physics_cursor = p['samplers'], p['pair_cursor'], p['physics_cursor']
        self.rng.setstate(p['local_rng'])
        self.exposures, self.seen = Counter(p['exposures']), set(p['seen'])
        self.development, self.initial_dev, self.best = p['development'], p['initial_dev'], p['best']
        selection_path = Path(root).parent / 'SELECTION.json'
        if selection_path.exists():
            selected = json.loads(selection_path.read_text())
            revision = Path(root) / selected['revision']
            if sha256(revision) != selected['sha256']:
                raise ValueError('Selected revision changed')
            if selected['step'] <= self.step and (self.best is None or selected['score'] < self.best['score']):
                self.best = selected


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=ROOT / 'local/CONNECTED-003-data-v1')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--steps', type=int, default=12288)
    parser.add_argument('--seed', type=int, default=1103)
    parser.add_argument('--owner', choices=('field', 'scfe'), default='field')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Run under scripts/supervise.py')
    args.output.mkdir(parents=True, exist_ok=True)
    engine = Engine(Curriculum(args.data), seed=args.seed, owner_kind=args.owner)
    checkpoints = args.output / 'revisions'
    if args.resume:
        engine.resume(checkpoints)
    elif checkpoints.exists():
        raise ValueError('Existing state requires explicit resume')
    else:
        initial = engine.evaluate()
        revision = engine.save(checkpoints)
        write_json(args.output / 'INITIAL.json', {**revision, 'development': initial})
        print(json.dumps({'initial': initial}), flush=True)
    started = time.monotonic()
    invocation = os.environ['SERA_FIELD_SUPERVISED']
    with (args.output / ('attempts-' + invocation + '.jsonl')).open('x', encoding='utf-8') as log:
        while engine.step < args.steps:
            result = engine.update()
            result['invocation'] = invocation
            log.write(json.dumps(result) + '\n')
            if engine.step % 128 == 0:
                log.flush()
                write_json(args.output / 'PROGRESS.json', {'step': engine.step, 'target': args.steps,
                           'last': result, 'exposures': dict(engine.exposures), 'unique_human_records': len(engine.seen),
                           'worker_seconds_this_invocation': time.monotonic()-started, 'updated_utc': utc()})
                print(json.dumps(result), flush=True)
            assessment = None
            if engine.step % 1024 == 0 or engine.step == args.steps:
                assessment = engine.evaluate()
                print(json.dumps({'development': assessment}), flush=True)
            if engine.step % 512 == 0 or engine.step == args.steps:
                revision = engine.save(checkpoints)
                if assessment and (engine.best is None or assessment['score'] < engine.best['score']):
                    engine.best = {'score': assessment['score'], 'step': engine.step, **revision}
                    write_json(args.output / 'SELECTION.json', engine.best)
            if (args.output / 'PAUSE_REQUEST.json').exists():
                revision = engine.save(checkpoints)
                write_json(args.output / 'PAUSED.json', {'step': engine.step, **revision})
                return
    engine.save(checkpoints)
    write_json(args.output / 'TEACHING_COMPLETE.json', {'attempted_batches': engine.step,
               'example_exposures': dict(engine.exposures), 'unique_human_records': len(engine.seen),
               'unique_simulated_systems': engine.physics_cursor, 'selection': engine.best,
               'initial_weights': engine.initial_hash, 'final_weights': weight_hash(engine.owner),
               'final_evaluation_opened': False, 'reward_training_pending': True})


if __name__ == '__main__':
    main()
