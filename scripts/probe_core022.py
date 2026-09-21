"""Finite pre-curriculum resource/stability and independent restart qualification.

All inputs are labeled engineering fixtures. No final cohort or human teaching
corpus is opened. Repeated observations and optimizer tests are not curriculum.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import time

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.core_owner import CoreOwner
from sera_field.core_session import CoreSession
from sera_field.model import weight_hash
from sera_field.native_data import identity
from sera_field.native_owner import NativeConfig
from sera_field.records import write_json

OUT = ROOT/'runs/CORE-022/engineering-probe'


def independent_continuation(task):
    decision = task.propose()
    if decision['requested'] is None:
        task.observe(decision['id'])
    else:
        force, velocity = decision['requested']
        task.observe(decision['id'], {'id': 'probe-resumed', 'source': 'independent-engineering-law',
            'kind': 'measurement', 'performed': True, 'force': force, 'velocity': velocity,
            'response': .7*force-.15*velocity})
    record = task.grade(decision['id'], independent_response=.155,
        source='independent-original-goal-fixture', verifier='separate-exact-linear-expression',
        evidence_id='assessment-resumed')
    return {'credit': record, 'answer': task.answer(), 'weights': weight_hash(task.owner),
            'torch_next': torch.rand(4).tolist(), 'python_next': random.random()}


def prepare():
    if OUT.exists(): raise ValueError('Preserve the prior probe; use its explicit replay rather than replace it')
    OUT.mkdir(parents=True)
    torch.manual_seed(22029); random.seed(22029)
    owner = CoreOwner(NativeConfig(nodes=4, rounds=2))
    state = owner.empty(1); maximum = {}; history = []
    started = time.perf_counter()
    with torch.no_grad():
        for index in range(96):
            # Vary all supplied observed coordinates, include contradictory
            # responses and preserve them as separate observed events.
            force = torch.tensor([((index*7)%23-11)/11])
            velocity = torch.tensor([((index*13)%19-9)/9])
            response = .7*force-(.15 if index < 48 else .35)*velocity
            source = owner.encode_numbers(force, velocity, response)
            state, audit = owner.observe(state, source, checked_progress=torch.tensor([.1*(-1)**index]))
            assert all(bool(torch.isfinite(v).all()) for v in state.values())
            assert torch.linalg.eigvalsh(torch.matrix_exp(state['log_covariance'])).min() > 0
            for name, value in state.items():
                if value.is_floating_point(): maximum[name] = max(maximum.get(name, 0), float(value.abs().max()))
            if index in (0, 15, 47, 95):
                history.append({'event': index+1, 'state_hash': identity({k: v.tolist() for k,v in state.items()}),
                    'energy_defect': audit['energy_defect'].tolist(), 'active_work': audit['active_work_integral'].tolist()})
        assert state['events'].item() == 96 and bool((state['marks'] > 0).all())
        before = identity({k:v.tolist() for k,v in state.items()})
        for phrase in ('A child sees a tree.', 'A person reads a book.', 'An object moves.'):
            owner.imagine(state, owner.encode_texts([phrase]))
        assert before == identity({k:v.tolist() for k,v in state.items()})
    stability = {'events': 96, 'maximum_coordinate_magnitude': maximum, 'checkpoints': history,
        'wall_seconds': time.perf_counter()-started, 'conditional_queries_preserve_state': True,
        'positive_covariance_and_finite_state': True,
        'scope': 'random fresh owner; supplied bounded engineering stream, not acquired understanding'}
    write_json(OUT/'STABILITY.json', stability)

    # One finite differentiable workload, with no optimizer step. It estimates
    # a declared joint teaching batch before deciding a curriculum envelope.
    started = time.perf_counter(); owner.zero_grad(set_to_none=True)
    state = owner.empty(8)
    for index in range(8):
        f = torch.linspace(-.8, .8, 8); v = f.roll(index)
        state, _ = owner.observe(state, owner.encode_numbers(f, v, .7*f-.15*v))
    outputs = owner.physical_query(state, torch.tensor([[[.2, -.1], [-.3, .2]]]*8))
    loss = outputs.square().mean(); loss.backward()
    gradients = {name: float(p.grad.norm()) for name,p in owner.named_parameters() if p.grad is not None}
    assert all(bool(torch.isfinite(p.grad).all()) for p in owner.parameters() if p.grad is not None)
    write_json(OUT/'WORKLOAD.json', {'batch': 8, 'observed_events_per_case': 8, 'queries_per_case': 2,
        'branches': 3, 'nodes': 4, 'split_rounds': 2, 'loss': float(loss.detach()),
        'wall_seconds': time.perf_counter()-started, 'gradient_norms': gradients,
        'optimizer_steps': 0, 'curriculum_presentations': 0})
    del state, outputs, loss

    owner = CoreOwner(NativeConfig(nodes=3, rounds=1))
    with torch.no_grad(): owner.choice.weight.zero_(); owner.choice.bias.zero_()
    task = CoreSession(owner, {'hypothesis': 'A person reads.', 'force': .2, 'velocity': -.1}, source='fresh-process-fixture')
    task.remember({'id': 'observed-1', 'source': 'engineering-fixture', 'kind': 'text', 'text': 'A person holds a book.'})
    task.remember({'id': 'observed-2', 'source': 'independent-fixture', 'kind': 'measurement', 'performed': True,
                   'force': .3, 'velocity': -.2, 'response': .24})
    task.propose(); task.save(OUT/'session')
    write_json(OUT/'EXPECTED.json', independent_continuation(task))
    write_json(OUT/'PENDING.json', {'next': 'verify', 'session': str(OUT/'session'),
                                 'completed': False, 'scope': 'engineering fixture only'})
    print(json.dumps({'prepared': True, 'next': 'scripts/probe_core022.py verify'}))


def verify():
    task = CoreSession.load(OUT/'session')
    expected = json.loads((OUT/'EXPECTED.json').read_text())
    actual = independent_continuation(task)
    assert actual == expected, 'Independent process did not reproduce the next decision/credit/update/RNG'
    result = {'fresh_process_exact_next_update': True, 'expected_identity': identity(expected),
              'actual_identity': identity(actual), 'protected_retained_state_used': True,
              'weights_after': actual['weights'], 'updated': actual['credit']['updated'],
              'scope': 'one pending fresh-owner fixture; curriculum has not started'}
    write_json(OUT/'REPLAY.json', result)
    write_json(OUT/'PENDING.json', {'completed': True, 'result': 'REPLAY.json'})
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('mode', choices=['prepare', 'verify'])
    options = parser.parse_args()
    (prepare if options.mode == 'prepare' else verify)()
