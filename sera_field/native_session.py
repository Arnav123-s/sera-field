"""Persistent observed state, conditional questions and independently scoped credit."""
import json
import math
from pathlib import Path

import torch

from .model import weight_hash
from .native_data import identity
from .native_owner import detached_state
from .records import write_json


def pack(state):
    return {key: {'tensor': value.tolist(), 'dtype': str(value.dtype)}
            if isinstance(value, torch.Tensor) else value for key, value in state.items()}


def unpack(state):
    return {key: torch.tensor(value['tensor'], dtype={'torch.float32': torch.float32,
            'torch.float64': torch.float64, 'torch.int64': torch.int64}[value['dtype']])
            if isinstance(value, dict) and 'tensor' in value else value for key, value in state.items()}


def finite(value):
    result = float(value)
    if not math.isfinite(result): raise ValueError('Finite measured values required')
    return result


class NativeSession:
    def __init__(self, owner, goal, *, source):
        if not source: raise ValueError('Observed source identity required')
        self.owner = owner.eval(); self.weights = weight_hash(owner)
        self.goal = {'force': finite(goal['force']), 'velocity': finite(goal['velocity'])}
        self.source = str(source); self.state = owner.empty(1)
        self.observations = []; self.pending = None; self.last_transition = None; self.credits = []

    def checked_owner(self):
        if weight_hash(self.owner) != self.weights: raise ValueError('Stale session predictor; replay under its recorded owner')

    def state_id(self): return identity(pack(self.state))

    @torch.no_grad()
    def answer(self, queries=None):
        self.checked_owner()
        queries = [[self.goal['force'], self.goal['velocity']]] if queries is None else queries
        tensor = torch.tensor([queries], dtype=self.owner.memory.raw_fast.dtype)
        values = self.owner.physical_query(self.state, tensor)[0]
        return {'original_goal': self.goal, 'source': self.source, 'owner_weights': self.weights,
            'state': self.state_id(), 'queries': queries, 'predictions': values.mean(-1).tolist(),
            'conditional_branches': values.tolist(), 'observed_count': len(self.observations)}

    @torch.no_grad()
    def remember(self, evidence):
        self.checked_owner()
        required = ('id', 'source', 'force', 'velocity', 'response', 'performed')
        if any(key not in evidence for key in required): raise ValueError('Complete performed measurement receipt required')
        if evidence['performed'] is not True or evidence['response'] is None:
            raise ValueError('An unread or unperformed measurement does not supply an observed response')
        if not evidence['id'] or not evidence['source']: raise ValueError('Measurement identity required')
        if any(row['id'] == evidence['id'] for row in self.observations): raise ValueError('Repeated evidence')
        force, velocity, response = map(finite, (evidence['force'], evidence['velocity'], evidence['response']))
        dtype = self.owner.memory.raw_fast.dtype
        value = self.owner.encode_numbers(torch.tensor([force], dtype=dtype), torch.tensor([velocity], dtype=dtype),
                                          torch.tensor([response], dtype=dtype))
        updated, _ = self.owner.observe(self.state, value)
        self.state = detached_state(updated)
        self.observations.append({**evidence, 'force': force, 'velocity': velocity, 'response': response})

    def propose(self):
        self.checked_owner()
        if self.pending is not None: return self.pending
        used = {(row['force'], row['velocity']) for row in self.observations}
        candidates = [[f, v] for f in (-1., -.5, 0., .5, 1.) for v in (-1., 0., 1.) if (f, v) not in used]
        if not candidates: raise ValueError('The finite investigation grid is exhausted')
        imagined = self.answer(candidates)
        spreads = [max(b)-min(b) for b in imagined['conditional_branches']]
        index = max(range(len(candidates)), key=lambda i: (spreads[i], -i))
        content = {'goal': self.goal, 'weights': self.weights, 'state': self.state_id(),
            'requested': {'force': candidates[index][0], 'velocity': candidates[index][1]},
            'policy': 'fixed maximum branch disagreement on a supplied finite grid',
            'predicted_response': imagined['predictions'][index]}
        self.pending = {'id': identity(content), **content}
        return self.pending

    def observe(self, decision_id, evidence):
        self.checked_owner()
        if self.pending is None or self.pending['id'] != decision_id: raise ValueError('No matching pending decision')
        if self.pending['state'] != self.state_id(): raise ValueError('Stale investigation state')
        previous = self.answer()['predictions'][0]; pending = self.pending
        self.remember(evidence)
        after = self.answer()['predictions'][0]
        self.last_transition = {'decision': decision_id, 'original_goal': self.goal, 'weights': self.weights,
            'before_state': pending['state'], 'after_state': self.state_id(), 'before': previous, 'after': after,
            'evidence': identity(evidence), 'evidence_id': evidence['id'],
            'performed_as_requested': all(evidence[k] == pending['requested'][k] for k in ('force', 'velocity'))}
        self.pending = None
        return self.last_transition

    def grade(self, decision_id, *, independent_response, source, verifier):
        self.checked_owner()
        if any(c['decision'] == decision_id for c in self.credits): raise ValueError('Repeated credit')
        transition = self.last_transition
        if (transition is None or transition['decision'] != decision_id or
                transition['after_state'] != self.state_id()): raise ValueError('Stale credit or state')
        if not source or not verifier: raise ValueError('Independent outcome and verifier identities required')
        truth = finite(independent_response)
        # Difference of squares without subtracting two almost equal large
        # losses. The stored marks must also represent the result finitely.
        before, after = transition['before'], transition['after']
        change = (before-after) * (before+after-2*truth)
        if not math.isfinite(change) or abs(change) > torch.finfo(self.state['marks'].dtype).max:
            raise ValueError('Finite representable credit required')
        marks = .95 * self.state['marks'] + self.state['marks'].new_tensor(
            [[max(change, 0.), max(-change, 0.)]]) * .05
        if not bool(torch.isfinite(marks).all()): raise ValueError('Finite representable credit required')
        record = {**transition, 'independent_response': truth, 'outcome_source': source, 'verifier': verifier,
                  'signed_progress': change, 'positive_credit': max(change, 0.)}
        record['id'] = identity(record); self.credits.append(record)
        # Marks record assessed progress; they do not turn guesses into measured
        # values or make a reward counter equivalent to learning a policy.
        self.state = {**self.state, 'marks': marks}
        return record

    def save(self, path):
        self.checked_owner(); path = Path(path)
        payload = {'weights': self.weights, 'goal': self.goal, 'source': self.source, 'state': pack(self.state),
            'observations': self.observations, 'pending': self.pending, 'transition': self.last_transition,
            'credits': self.credits}
        record = {'identity': identity(payload), 'payload': payload}
        revision = path / 'revisions' / (record['identity'] + '.json')
        if revision.exists() and json.loads(revision.read_text()) != record: raise ValueError('Session revision changed')
        if not revision.exists(): write_json(revision, record)
        write_json(path / 'CURRENT.json', {'revision': revision.name, 'identity': record['identity']})
        return record['identity']

    @classmethod
    def load(cls, owner, path):
        path = Path(path); current = json.loads((path / 'CURRENT.json').read_text())
        revision = path / 'revisions' / current['revision']
        if revision.resolve().parent != (path / 'revisions').resolve(): raise ValueError('Invalid session revision')
        record = json.loads(revision.read_text()); payload = record['payload']
        if identity(payload) != record['identity'] or record['identity'] != current['identity']:
            raise ValueError('Session identity changed')
        result = cls(owner, payload['goal'], source=payload['source'])
        if result.weights != payload['weights']: raise ValueError('Session predictor changed')
        result.state = unpack(payload['state']); result.observations = payload['observations']
        result.pending = payload['pending']; result.last_transition = payload['transition']; result.credits = payload['credits']
        return result
