"""Persistent mixed-goal investigation with evidence-bound learner updates."""
import copy
import json
import math
from pathlib import Path
import random

import torch

from .joint_cycle import replay, answers, investigation_logits, policy_objective
from .joint_training import GRID
from .native_data import identity
from .native_owner import NativeOwner, NativeConfig, detached_state
from .native_session import pack, finite
from .native_training import save_revision
from .model import weight_hash
from .records import write_json, sha256


class JointSession:
    def checkpoint_extra(self, path):
        return {}

    def restore_extra(self, path, extra):
        if extra:
            raise ValueError('Unexpected session extension')

    @property
    def owner_dtype(self):
        """Input precision belongs to the owner, not to a particular memory."""
        return next(self.owner.parameters()).dtype

    @classmethod
    def owner_from_specification(cls, specification):
        configuration = dict(specification)
        if configuration.pop('type') != 'native-memory-field-019':
            raise ValueError('Unexpected owner type')
        return NativeOwner(NativeConfig(**configuration))

    def __init__(self, owner, goal, *, source):
        if not source or not isinstance(goal.get('hypothesis'), str) or not goal['hypothesis'].strip():
            raise ValueError('Original human question and source identity required')
        self.owner = owner.eval()
        self.goal = {'hypothesis': goal['hypothesis'], 'force': finite(goal['force']),
                     'velocity': finite(goal['velocity'])}
        self.source = str(source); self.weights = weight_hash(owner)
        self.optimizer = torch.optim.AdamW(owner.parameters(), lr=.0001, weight_decay=.0001)
        self.events = []; self.credits = []; self.pending = None; self.transition = None
        self.state = owner.empty(1)

    def checked_owner(self):
        if weight_hash(self.owner) != self.weights:
            raise ValueError('Stale session predictor')

    def state_id(self):
        return identity(pack(self.state))

    def tensors(self, events):
        converted = []; dtype = self.owner_dtype
        for event in events:
            if event['kind'] == 'text':
                converted.append({'kind': 'text', 'texts': [event['text']]})
            elif event['kind'] == 'measurement':
                converted.append({'kind': 'measurement', 'actual': torch.tensor([[event[k] for k in
                                   ('force', 'velocity', 'response')]], dtype=dtype)})
            elif event['kind'] == 'credit':
                converted.append({'kind': 'credit', 'progress': torch.tensor([event['signed_progress']], dtype=dtype)})
            else:
                raise ValueError('Unknown retained event')
        return converted

    def rebuild(self, events=None):
        return replay(self.owner, self.tensors(self.events if events is None else events), 1)

    def used_mask(self, events=None):
        measured = {(e['force'], e['velocity']) for e in (self.events if events is None else events)
                    if e['kind'] == 'measurement'}
        return torch.tensor([[(f, v) in measured for f, v in GRID]])

    def scores(self, state, events=None):
        dtype = self.owner_dtype
        return investigation_logits(self.owner, state, torch.tensor([[self.goal['force'], self.goal['velocity']]], dtype=dtype),
                                     torch.tensor(GRID, dtype=dtype), used=self.used_mask(events))

    @torch.no_grad()
    def answer(self, *, force=None, velocity=None):
        self.checked_owner()
        f = self.goal['force'] if force is None else finite(force)
        v = self.goal['velocity'] if velocity is None else finite(velocity)
        goals = torch.tensor([[f, v]], dtype=self.owner_dtype)
        result = answers(self.owner, self.state, [self.goal['hypothesis']], goals)
        return {'original_goal': copy.deepcopy(self.goal), 'source': self.source, 'weights': self.weights,
                'state': self.state_id(), 'query': [f, v],
                'physical': float(result['physical'].mean()),
                'physical_branches': result['physical'][0].tolist(),
                'human_probabilities': result['semantic'].softmax(-1).mean(1)[0].tolist(),
                'observed_events': int(self.state['events'][0])}

    def validate_id(self, record):
        if not record.get('id') or not record.get('source'):
            raise ValueError('Observed evidence identity and source required')
        if any(e['id'] == record['id'] for e in self.events):
            raise ValueError('Repeated observed evidence')

    @torch.no_grad()
    def remember(self, evidence):
        self.checked_owner(); self.validate_id(evidence)
        if self.pending is not None:
            raise ValueError('Use the pending decision receipt before changing history')
        if evidence.get('kind') == 'text':
            if not isinstance(evidence.get('text'), str) or not evidence['text'].strip():
                raise ValueError('Observed source text required')
            event = {k: evidence[k] for k in ('id', 'source', 'kind', 'text')}
        elif evidence.get('kind') == 'measurement':
            if evidence.get('performed') is not True or evidence.get('response') is None:
                raise ValueError('Unread or unperformed outcome is not an observation')
            event = {**{k: evidence[k] for k in ('id', 'source', 'kind')}, 'performed': True,
                     **{k: finite(evidence[k]) for k in ('force', 'velocity', 'response')}}
        else:
            raise ValueError('Text or performed measurement required')
        state = self.rebuild([*self.events, event])
        if not all(torch.isfinite(v).all() for v in state.values() if isinstance(v, torch.Tensor)):
            raise ValueError('Nonfinite observed state')
        self.events.append(event); self.state = detached_state(state)

    @torch.no_grad()
    def propose(self):
        self.checked_owner()
        if self.pending is not None:
            return copy.deepcopy(self.pending)
        scores = self.scores(self.state); index = int(scores.argmax(-1))
        content = {'goal': copy.deepcopy(self.goal), 'source': self.source,
                   'weights': self.weights, 'state': self.state_id(),
                   'observed_prefix': len(self.events), 'events_sha256': identity(self.events),
                   'action': index, 'requested': None if index == len(GRID) else GRID[index],
                   'probabilities': scores.softmax(-1)[0].tolist(),
                   'policy': 'learned shared choice; deterministic highest-score delivery'}
        self.pending = {'id': identity(content), **content}
        return copy.deepcopy(self.pending)

    @torch.no_grad()
    def observe(self, decision, evidence=None):
        self.checked_owner()
        if self.pending is None or self.pending['id'] != decision:
            raise ValueError('No matching pending decision')
        pending = self.pending
        if pending['state'] != self.state_id() or pending['events_sha256'] != identity(self.events):
            raise ValueError('Stale decision state')
        before = self.answer(); stopped = pending['action'] == len(GRID)
        if stopped and evidence is not None:
            raise ValueError('STOP cannot receive an invented measurement')
        if not stopped:
            if not isinstance(evidence, dict) or evidence.get('kind') != 'measurement':
                raise ValueError('Performed intervention receipt required')
            # Temporarily permit exactly the selected observation; restore the
            # pending decision if validation fails before any state write.
            self.pending = None
            try:
                self.remember(evidence)
            except Exception:
                self.pending = pending
                raise
        after = self.answer()
        performed = not stopped and all(evidence[k] == value for k, value in
                                         zip(('force', 'velocity'), pending['requested']))
        self.transition = {'decision': decision, 'pending': pending,
                           'before': before, 'after': after,
                           'evidence': None if stopped else identity(evidence),
                           'evidence_id': None if stopped else evidence['id'],
                           'performed_as_requested': performed, 'stopped': stopped}
        self.pending = None
        return copy.deepcopy(self.transition)

    def grade(self, decision, *, independent_response, source, verifier, evidence_id):
        self.checked_owner()
        if any(c['decision'] == decision for c in self.credits):
            raise ValueError('Repeated credit')
        if not source or not verifier or not evidence_id:
            raise ValueError('Independent source, verifier and evidence identity required')
        if any(c['independent_evidence_id'] == evidence_id for c in self.credits):
            raise ValueError('Repeated independent outcome receipt')
        t = self.transition
        if (t is None or t['decision'] != decision or t['after']['state'] != self.state_id()
                or t['pending']['weights'] != self.weights):
            raise ValueError('Stale transition or predictor for credit')
        truth = finite(independent_response)
        b, a = t['before']['physical'], t['after']['physical']
        progress = (b-a)*(b+a-2*truth)
        if not math.isfinite(progress) or abs(progress) > torch.finfo(self.state['marks'].dtype).max:
            raise ValueError('Representable independent progress required')
        policy_credit = progress-.001 if t['performed_as_requested'] else 0.
        prefix = self.events[:t['pending']['observed_prefix']]
        if identity(prefix) != t['pending']['events_sha256']:
            raise ValueError('Decision history changed')
        before_weights = self.weights
        old_owner = {k: v.detach().clone() for k, v in self.owner.state_dict().items()}
        old_optimizer = copy.deepcopy(self.optimizer.state_dict())
        credited_event = {'kind': 'credit', 'id': identity(['credit', decision, evidence_id]),
                          'source': source, 'signed_progress': progress}
        updated = False; gradient_norm = 0.
        try:
            if policy_credit != 0:
                self.optimizer.zero_grad(set_to_none=True)
                state = self.rebuild(prefix)
                scores = self.scores(state, prefix)
                if scores.softmax(-1)[0].detach().tolist() != t['pending']['probabilities']:
                    raise ValueError('Reconstructed decision differs')
                value = scores.new_tensor([4*min(.25, max(-.25, policy_credit))])
                objective = policy_objective(scores, torch.tensor([t['pending']['action']]), value, entropy_weight=0)
                objective.backward()
                gradient_norm = float(torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1., error_if_nonfinite=True))
                self.optimizer.step()
                if not all(torch.isfinite(p).all() for p in self.owner.parameters()):
                    raise ValueError('Nonfinite reward update')
                updated = True
            with torch.no_grad():
                rebuilt = detached_state(self.rebuild([*self.events, credited_event]))
            if not all(torch.isfinite(v).all() for v in rebuilt.values() if isinstance(v, torch.Tensor)):
                raise ValueError('Nonfinite re-encoded history')
        except Exception:
            self.owner.load_state_dict(old_owner); self.optimizer.load_state_dict(old_optimizer)
            self.optimizer.zero_grad(set_to_none=True)
            raise
        self.weights = weight_hash(self.owner); self.state = rebuilt; self.events.append(credited_event)
        record = {'decision': decision, 'original_goal': self.goal, 'source': self.source,
                  'before_weights': before_weights, 'after_weights': self.weights,
                  'transition': t, 'independent_response': truth, 'independent_source': source,
                  'verifier': verifier, 'independent_evidence_id': evidence_id,
                  'signed_progress': progress, 'policy_credit': policy_credit,
                  'updated': updated, 'gradient_norm': gradient_norm,
                  'update_rule': 'checked on-decision weighted log likelihood; no entropy-only update',
                  'history_reencoded_under_updated_owner': True, 'returned_answer': self.answer()}
        record['id'] = identity(record); self.credits.append(record)
        return copy.deepcopy(record)

    def save(self, path):
        self.checked_owner(); path = Path(path)
        revision = save_revision(path, self.owner, self.optimizer, len(self.credits), [], {},
                                 {'role': 'persistent verified mixed investigation', 'source': self.source})
        payload = {'owner': revision, 'goal': self.goal, 'source': self.source,
                   'events': self.events, 'credits': self.credits, 'pending': self.pending,
                   'transition': self.transition, 'state': pack(self.state)}
        extra = self.checkpoint_extra(path)
        if extra:
            payload['extensions'] = extra
        record = {'identity': identity(payload), 'payload': payload}
        destination = path / 'revisions' / ('session-' + record['identity'] + '.json')
        if destination.exists() and json.loads(destination.read_text()) != record:
            raise ValueError('Existing session revision changed')
        if not destination.exists():
            write_json(destination, record)
        write_json(path / 'CURRENT.json', {'revision': destination.name, 'identity': record['identity']})
        return record['identity']

    @classmethod
    def load(cls, path):
        path = Path(path); current = json.loads((path / 'CURRENT.json').read_text())
        record_path = path / 'revisions' / current['revision']
        if record_path.resolve().parent != (path / 'revisions').resolve():
            raise ValueError('Invalid session path')
        record = json.loads(record_path.read_text()); data = record['payload']
        if identity(data) != record['identity'] or record['identity'] != current['identity']:
            raise ValueError('Changed session identity')
        selected = data['owner']; revision = path / 'revisions' / selected['revision']
        if revision.resolve().parent != (path / 'revisions').resolve() or sha256(revision) != selected['sha256']:
            raise ValueError('Changed session owner revision')
        payload = torch.load(revision, map_location='cpu', weights_only=False)
        owner = cls.owner_from_specification(payload['specification'])
        # A fresh constructor defaults to float32; preserve an explicitly saved
        # real precision before loading, rather than silently rounding tensors.
        precision = next(v.dtype for v in payload['owner'].values() if v.is_floating_point())
        if precision == torch.float64:
            owner.double()
        elif precision == torch.float32:
            owner.float()
        else:
            raise ValueError('Unsupported saved real precision')
        # Module.to(real_dtype) also converts complex buffers to real and
        # destroys braid phases. float()/double() touch real tensors only.
        owner.load_state_dict(payload['owner'])
        if weight_hash(owner) != selected['weights']:
            raise ValueError('Changed owner tensors')
        task = cls(owner, data['goal'], source=data['source'])
        task.optimizer.load_state_dict(payload['optimizer'])
        task.events = data['events']; task.credits = data['credits']
        task.pending = data['pending']; task.transition = data['transition']
        with torch.no_grad(): task.state = detached_state(task.rebuild())
        if pack(task.state) != data['state']:
            raise ValueError('Stored state does not reproduce under its owner and history')
        task.restore_extra(path, data.get('extensions', {}))
        torch.set_rng_state(payload['rng']); random.setstate(payload['python_rng'])
        return task
