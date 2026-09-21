"""One fresh coupled owner across human sources and measured investigation."""
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import random
import time

import torch

from .core_course_data import CoreData, DATA, SCHEDULE, pair
from .core_owner import CoreOwner
from .core_session import CoreSession
from .core_teaching_loss import teaching_loss, assess_program_rows
from .joint_training import cycle, aggregate
from .model import weight_hash
from .native_data import ROOT, identity, physical_episode
from .native_owner import NativeConfig
from .native_training import loss_cases, summarize
from .records import sha256, write_json, utc

TOTAL = 12288
STUDY = ROOT/'runs/CORE-022/foundation'
PROTOCOL = ROOT/'protocols/CORE-022-FOUNDATION.md'


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def identities():
    return {'protocol': sha256(PROTOCOL), 'allocation': sha256(DATA/'MANIFEST.json'),
        'implementation': {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted((ROOT/'sera_field').glob('*.py'))},
        'driver': sha256(ROOT/'scripts/train_core022_foundation.py')}


def new_owner():
    torch.manual_seed(22271); random.seed(22271)
    return CoreOwner(NativeConfig(nodes=4, rounds=2), program_slots=8)


def course_loss(owner, data, kind, rows, *, reward=True, split='train'):
    if kind == 'programs':
        loss, _ = teaching_loss(owner, rows)
        return .1*loss, {'raw_program_loss': float(loss.detach()), 'program_loss_weight': .1}
    if kind == 'mixed':
        loss, cases, terms = cycle(owner, rows, training=split == 'train', reward=reward)
        return loss, {'terms': terms, 'investigations': cases}
    loss, cases = loss_cases(owner, data, kind, rows, split=split)
    return loss, {'cases': cases}


@torch.no_grad()
def assess(owner, data, kind, rows):
    owner.eval(); cases = []
    size = 4 if kind in ('reading','mixed') else 8
    for offset in range(0, len(rows), size):
        batch = rows[offset:offset+size]
        if kind == 'programs': batch_cases = assess_program_rows(owner, batch)
        elif kind == 'mixed': _, batch_cases, _ = cycle(owner, batch)
        else: _, batch_cases = loss_cases(owner, data, kind, batch, split='development')
        cases.extend(batch_cases)
    if kind == 'mixed': return aggregate(cases), cases
    if kind == 'programs': return {'n': len(cases), 'accuracy': sum(c['correct'] for c in cases)/len(cases)}, cases
    result = summarize(cases, kind)
    if kind == 'pairs':
        tracks = defaultdict(list)
        for case in cases: tracks[case['track']].append(case)
        result['subjects'] = {k: summarize(v, 'pairs') for k,v in tracks.items()}
        result['macro_accuracy'] = sum(v['accuracy'] for v in result['subjects'].values())/len(tracks)
    return result, cases


def development(owner, data):
    rows = {**data.development,
        'physics': [physical_episode('CORE-022-foundation-development', i) for i in range(64)],
        'mixed': pair(data.development['semantic'][:32], 'CORE-022-mixed-development')}
    metrics = {}; all_cases = {}
    for kind, items in rows.items(): metrics[kind], all_cases[kind] = assess(owner, data, kind, items)
    score = (metrics['semantic']['accuracy']+metrics['pairs']['macro_accuracy']+
        metrics['reading']['accuracy']+metrics['programs']['accuracy']+
        1/(1+metrics['physics']['mse'])+.5*(metrics['mixed']['accuracy']+1/(1+metrics['mixed']['after_mse'])))/6
    return {'score': score, 'tracks': metrics}, all_cases


def save(root, owner, optimizer, cursor, history, exposures, sources, *, receipts):
    root = Path(root); directory = root/'revisions'; directory.mkdir(parents=True, exist_ok=True)
    temporary = directory/('pending-'+os.environ.get('SERA_FIELD_SUPERVISED','test')+'.pt')
    payload = {'owner': owner.state_dict(), 'specification': owner.specification(), 'optimizer': optimizer.state_dict(),
        'cursor': cursor, 'history': history, 'exposures': dict(exposures), 'sources': sources,
        'torch_rng': torch.get_rng_state(), 'python_rng': random.getstate(), 'receipts': receipts}
    torch.save(payload, temporary)
    digest = sha256(temporary); destination = directory/(digest+'.pt')
    if destination.exists():
        if sha256(destination) != digest: raise ValueError('Existing course revision changed')
        temporary.unlink()
    else: temporary.rename(destination)
    record = {'revision': destination.name, 'sha256': digest, 'weights': weight_hash(owner), 'cursor': cursor}
    write_json(root/'CURRENT.json', record)
    return record


def load(root, pointer='CURRENT.json', *, expected_sources=None):
    root = Path(root); selected = read(root/pointer); path = root/'revisions'/selected['revision']
    if path.resolve().parent != (root/'revisions').resolve() or sha256(path) != selected['sha256']:
        raise ValueError('Changed course checkpoint')
    payload = torch.load(path, map_location='cpu', weights_only=False)
    if expected_sources is not None and payload['sources'] != expected_sources:
        raise ValueError('Course source or protocol identity changed; preserve and diagnose rather than silently resume')
    owner = CoreSession.owner_from_specification(payload['specification']); owner.load_state_dict(payload['owner'])
    if weight_hash(owner) != selected['weights'] or payload['cursor'] != selected['cursor']:
        raise ValueError('Course owner/cursor identity changed')
    optimizer = torch.optim.AdamW(owner.parameters(), lr=.001, weight_decay=.0001)
    optimizer.load_state_dict(payload['optimizer'])
    torch.set_rng_state(payload['torch_rng']); random.setstate(payload['python_rng'])
    return owner, optimizer, payload, selected


def train(arm):
    if arm not in ('credited','withheld'): raise ValueError('Unknown frozen teaching arm')
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise ValueError('Numerical supervision required')
    accepted = read(ROOT/'reports/CORE-022/BUILD_ACCEPTANCE.json')
    sources = identities()
    if not accepted['launch_qualified'] or accepted['course_sources'] != sources:
        raise ValueError('Complete current build acceptance is required before any curriculum update')
    root = STUDY/arm; root.mkdir(parents=True, exist_ok=True)
    if (root/'COMPLETE.json').exists():
        load(root, expected_sources=sources)
        print(json.dumps({'arm': arm, 'already_complete': True})); return
    data = CoreData(); history = []; exposures = Counter(); cursor = 0; prior_receipts = []
    if (root/'CURRENT.json').exists():
        owner, optimizer, payload, _ = load(root, expected_sources=sources)
        cursor = payload['cursor']; history = payload['history']; exposures.update(payload['exposures'])
        prior_receipts = payload['receipts']; best = read(root/'SELECTION.json')
        if history and history[-1]['cursor'] == cursor and history[-1]['score'] > best['score']:
            best = {**read(root/'CURRENT.json'), **{k:v for k,v in history[-1].items() if k != 'cursor'}}
            write_json(root/'SELECTION.json', best)
        for receipt in prior_receipts:
            path = root/receipt['file']
            with path.open('rb') as handle: prefix = handle.read(receipt['bytes'])
            import hashlib
            if hashlib.sha256(prefix).hexdigest() != receipt['sha256']: raise ValueError('Durable teaching receipt prefix changed')
        # Any completed but non-checkpointed tail remains in its old log. Its
        # numerical cost is preserved. The new attempt starts at the durable
        # cursor with exactly restored RNG/optimizer, never rewrites old logs.
        write_json(root/('RESUME-'+os.environ['SERA_FIELD_SUPERVISED']+'.json'),
            {'cursor': cursor, 'prior_receipts': prior_receipts, 'unsaved_tail_preserved': True, 'utc': utc()})
    else:
        owner = new_owner(); optimizer = torch.optim.AdamW(owner.parameters(), lr=.001, weight_decay=.0001)
        metrics, cases = development(owner, data); history.append({'cursor': 0, **metrics})
        write_json(root/'development-00000.json', cases)
        initial = save(root, owner, optimizer, 0, history, exposures, sources, receipts=[])
        best = {**initial, **metrics}; write_json(root/'INITIAL.json', best); write_json(root/'SELECTION.json', best)
    log_path = root/('updates-'+os.environ['SERA_FIELD_SUPERVISED']+'.jsonl')
    with log_path.open('x', encoding='utf-8') as log:
        while cursor < TOTAL:
            started = time.perf_counter(); owner.train(); optimizer.zero_grad(set_to_none=True)
            kind = SCHEDULE[cursor % len(SCHEDULE)]; size = 4 if kind in ('reading','mixed') else 8
            actual_kind, rows = data.lesson(cursor, size)
            if actual_kind != kind: raise ValueError('Frozen course schedule changed')
            loss, details = course_loss(owner, data, kind, rows, reward=arm == 'credited')
            if not torch.isfinite(loss): raise ValueError('Nonfinite course loss; preserve last durable owner')
            loss.backward(); norm = torch.nn.utils.clip_grad_norm_(owner.parameters(), 1., error_if_nonfinite=True)
            optimizer.step()
            if any(not bool(torch.isfinite(p).all()) for p in owner.parameters()):
                raise ValueError('Nonfinite course update; preserve earlier checkpoint and failed attempt')
            cursor += 1; exposures[kind] += len(rows)
            if kind == 'pairs': exposures['pair_subject:'+rows[0]['track']] += len(rows)
            if kind == 'programs':
                for row in rows: exposures['program_subject:'+row['track']] += 1
            log.write(json.dumps({'cursor': cursor, 'kind': kind, 'ids': [r['id'] for r in rows],
                'loss': float(loss.detach()), 'gradient_norm': float(norm),
                'update_wall_seconds': time.perf_counter()-started, 'details': details})+'\n')
            del loss
            metrics = None
            if cursor % 1024 == 0:
                metrics, cases = development(owner, data); history.append({'cursor': cursor, **metrics})
                write_json(root/f'development-{cursor:05}.json', cases)
            if cursor % 64 == 0:
                log.flush(); os.fsync(log.fileno())
                receipts = [*prior_receipts, {'file': log_path.name, 'bytes': log_path.stat().st_size, 'sha256': sha256(log_path)}]
                revision = save(root, owner, optimizer, cursor, history, exposures, sources, receipts=receipts)
                if metrics and metrics['score'] > best['score']:
                    best = {**revision, **metrics}; write_json(root/'SELECTION.json', best)
                progress = {'arm': arm, 'cursor': cursor, 'target': TOTAL, 'exposures': dict(exposures),
                    'selected_cursor': best['cursor'], 'weights': revision['weights'], 'utc': utc(),
                    'next_executable_action': 'resume this arm at the saved cursor; do not initialize again'}
                write_json(root/'PROGRESS.json', progress); print(json.dumps(progress), flush=True)
    write_json(root/'COMPLETE.json', {'arm': arm, 'updates': cursor, 'selected': best,
        'exposures': dict(exposures), 'history': history, 'sources': sources,
        'initial_weights': read(root/'INITIAL.json')['weights'], 'parent_checkpoint_loaded': False,
        'pretrained_weights_loaded': False, 'final_evaluation_opened': False,
        'scope': 'foundation teaching complete; integrated capability assessments remain'})
