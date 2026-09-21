"""Independent-interpreter replay of the course's actual next optimizer update."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.core_course import save, load
from sera_field.core_owner import CoreOwner
from sera_field.native_owner import NativeConfig
from sera_field.model import weight_hash
from sera_field.native_data import identity
from sera_field.records import write_json

OUT = ROOT/'runs/CORE-022/checkpoint-probe'


def tensors(value):
    if isinstance(value, torch.Tensor):
        return {'dtype': str(value.dtype), 'shape': list(value.shape),
                'sha256': hashlib.sha256(value.detach().contiguous().numpy().tobytes()).hexdigest()}
    if isinstance(value, dict): return {str(k): tensors(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [tensors(v) for v in value]
    return value


def update(owner, optimizer):
    optimizer.zero_grad(set_to_none=True)
    loss = owner.semantic(['A person watches a ball.'], ['Someone observes an object.']).square().mean()
    loss.backward(); torch.nn.utils.clip_grad_norm_(owner.parameters(), 1., error_if_nonfinite=True); optimizer.step()
    return {'loss': float(loss.detach()), 'weights': weight_hash(owner),
        'optimizer': tensors(optimizer.state_dict()), 'torch_next': torch.rand(4).tolist(), 'python_next': random.random()}


def main(mode):
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the numerical resource supervisor')
    torch.set_num_threads(1)
    if mode == 'prepare':
        if OUT.exists(): raise ValueError('Preserve the existing checkpoint probe')
        OUT.mkdir(parents=True); torch.manual_seed(22261); random.seed(22261)
        owner = CoreOwner(NativeConfig(nodes=3, rounds=1), program_slots=8)
        optimizer = torch.optim.AdamW(owner.parameters(), lr=.001, weight_decay=.0001)
        update(owner, optimizer)
        save(OUT/'checkpoint', owner, optimizer, 1, [], {'engineering': 1}, {'source': 'explicit engineering fixture'}, receipts=[])
        write_json(OUT/'EXPECTED.json', update(owner, optimizer))
        print(json.dumps({'prepared': True, 'curriculum_steps': 0, 'fixture_updates': 2}))
    else:
        owner, optimizer, _, _ = load(OUT/'checkpoint', expected_sources={'source': 'explicit engineering fixture'})
        actual = update(owner, optimizer); expected = json.loads((OUT/'EXPECTED.json').read_text())
        if actual != expected: raise ValueError('Independent next-update replay differs')
        record = {'independent_process_replay_exact': True, 'expected_identity': identity(expected),
            'actual_identity': identity(actual), 'weights_after': actual['weights'], 'optimizer_and_both_rngs_exact': True,
            'scope': 'two explicit engineering updates; no source curriculum or final evaluation used'}
        write_json(OUT/'REPLAY.json', record); write_json(ROOT/'reports/CORE-022/COURSE_REPLAY.json', record)
        print(json.dumps(record))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('mode', choices=['prepare','verify']); main(p.parse_args().mode)
