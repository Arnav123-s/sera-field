"""The continuing semantic/physical owner with one qualified history state.

Conditional history is used by the existing field, never by a second answer
model. New mechanism parameters are taught on episodes; factual writes use the
same independently assessed progress contract as earlier capture.
"""
import copy
import math

import torch
from torch import nn

from .continuum_core import MemoryContinuum
from .credit_bridge import identity
from .gauge import adjoint_rotations
from .model import weight_hash
from .perfect_tensor_memory import encode_density, decode_density
from .semantic_owner import CurvatureField, SemanticOwner


def history_identity(state):
    return identity({name: value.detach().tolist() if isinstance(value, torch.Tensor) else value
                     for name, value in state.items()})


class HistoryField(CurvatureField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.continuum = MemoryContinuum(self.nodes)
        self.raw_history_gain = nn.Parameter(torch.tensor(0.))
        initial = self.continuum.empty(1)
        for name, value in initial.items():
            if isinstance(value, torch.Tensor):
                self.register_buffer('history_' + name, value)
        self.register_buffer('history_events', torch.zeros((), dtype=torch.int64))
        length = sum(value.numel() for value in initial.values() if isinstance(value, torch.Tensor))
        self.register_buffer('history_code', torch.zeros(length, 32, dtype=torch.complex128))
        self.register_buffer('history_code_ready', torch.zeros((), dtype=torch.bool))
        self.history_preview = None
        self.history_disconnected = False
        self.history_evidence = []
        self.history_encoder = None
        self.last_boundary = None
        self.track_boundary_credit = False
        self.active_history_goal = None

    def get_extra_state(self):
        return {'evidence': copy.deepcopy(self.history_evidence), 'encoder': self.history_encoder}

    def set_extra_state(self, state):
        self.history_evidence = copy.deepcopy(state['evidence']); self.history_encoder = state['encoder']

    def geometry_identity(self):
        return identity({'continuum': {name: p.detach().tolist() for name, p in self.continuum.named_parameters()},
                         'connection': self.links.detach().tolist()})

    def factual_state(self, *, code=None, erasures=()):
        result = {name: getattr(self, 'history_' + name).clone()
                  for name in ('fast', 'slow', 'marks', 'bulk', 'flow_context')}
        if bool(self.history_code_ready):
            if self.geometry_identity() != self.history_encoder:
                raise ValueError('The saved history uses a different flow; qualify a recorded re-encoding first')
            represented, _ = decode_density(self.history_code if code is None else code, erasures=erasures)
            flat = torch.tan(torch.pi * (represented - .5))
            cursor = 0
            for name, value in result.items():
                result[name] = flat[cursor:cursor + value.numel()].reshape_as(value).to(value)
                cursor += value.numel()
        result['events'] = int(self.history_events)
        return result

    def imagine(self, source, previous=None, *, use_imagination=True):
        if self.track_boundary_credit and not source.requires_grad:
            source = source.detach().requires_grad_(True)
        self.last_boundary = source
        if self.history_preview is not None:
            state = self.history_preview
        elif self.active_history_goal is not None and self.history_evidence and all(
                row['goal'] == self.active_history_goal for row in self.history_evidence):
            state = self.factual_state()
        else:
            state = self.continuum.empty(1, dtype=source.dtype, device=source.device)
        if state['fast'].shape[0] != len(source):
            if len(source) % len(state['fast']):
                raise ValueError('A conditional history must correspond to the actual source batch')
            count = len(source) // len(state['fast'])
            state = {name: value.repeat_interleave(count, 0) if isinstance(value, torch.Tensor) else value
                     for name, value in state.items()}
        if self.history_disconnected:
            drive = torch.zeros_like(source)
        else:
            transport = adjoint_rotations(self.links).transpose(-1, -2)
            remembered = self.continuum.recall(state, transport)
            affinity = torch.nn.functional.cosine_similarity(source.flatten(1), state['fast'].flatten(1), dim=-1)
            drive = affinity.sigmoid()[:, None, None] * remembered
        return super().imagine(source + .2 * self.raw_history_gain.tanh() * drive,
                               previous, use_imagination=use_imagination)

    @torch.no_grad()
    def commit_history(self, proposed, event, *, predictor, decision_policy, proposal_id):
        outcome = event.get('outcome', {})
        required = ('goal', 'decision', 'predictor', 'policy_before', 'evidence_id',
                    'assessment_id', 'source_sha256', 'verifier_sha256', 'assumptions_id')
        if (not event.get('accepted') or not outcome.get('verified') or
            any(not outcome.get(key) for key in required) or
            outcome.get('evidence_kind') not in {'measurement', 'independent_simulation', 'exact_checker', 'human_assessment'}):
            raise ValueError('Qualified independent evidence and its complete identities are required')
        if outcome['predictor'] != predictor or outcome['policy_before'] != decision_policy:
            raise ValueError('History proposal/predictor mismatch')
        if outcome['goal'] != self.active_history_goal or any(
                row['goal'] != outcome['goal'] for row in self.history_evidence):
            raise ValueError('Retained history belongs to its independently assessed original goal')
        if outcome.get('intended_intervention') != proposal_id or outcome.get('observed_intervention') != proposal_id:
            raise ValueError('Only the independently tested history proposal may be retained')
        if history_identity(proposed) != proposal_id:
            raise ValueError('The proposed state changed after independent assessment')
        before, after = outcome.get('before_loss', math.nan), outcome.get('after_loss', math.nan)
        if not (math.isfinite(before) and math.isfinite(after) and 0 <= after < before):
            raise ValueError('History retention requires independently measured positive progress')
        if any(row['evidence_id'] == outcome['evidence_id'] or row['assessment_id'] == outcome['assessment_id'] or
               row['decision'] == outcome['decision'] for row in self.history_evidence):
            raise ValueError('History credit has already been consumed')
        names = ('fast', 'slow', 'marks', 'bulk', 'flow_context')
        for name in names:
            value = proposed[name]
            if value.shape != getattr(self, 'history_' + name).shape or not torch.isfinite(value).all():
                raise ValueError('A finite one-context history with the registered shape is required')
        flat = torch.cat([proposed[name].flatten() for name in names]).double()
        represented = .5 + torch.atan(flat) / torch.pi
        code = encode_density(represented)
        if not torch.isfinite(code).all():
            raise ValueError('History encoding failed before factual write')
        recovered, _ = decode_density(code)
        round_trip = torch.tan(torch.pi * (recovered - .5))
        if not torch.allclose(round_trip, flat, atol=1e-7, rtol=1e-6):
            raise ValueError('History amplitude map exceeded its recoverable numerical range')
        for name in names:
            getattr(self, 'history_' + name).copy_(proposed[name])
        self.history_events.fill_(proposed['events']); self.history_code.copy_(code)
        self.history_code_ready.fill_(True); self.history_encoder = self.geometry_identity()
        record = {key: outcome[key] for key in required}
        record.update(proposal=proposal_id, encoder=self.history_encoder,
                      code_scope='one unknown qubit error or at most two declared boundary erasures per cell')
        self.history_evidence.append(record)
        return record


class HistoryOwner(SemanticOwner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = HistoryField(self.config['nodes'], self.config['rounds'],
                                  backend=self.field.backend, steps=self.field.steps)

    def specification(self):
        return {**super().specification(), 'type': 'continuous-history-016'}

    def retain_history(self, proposed, event, *, proposal_id):
        """Check the actual current owner before entering the factual write path."""
        predictor = event.get('outcome', {}).get('predictor')
        if weight_hash(self) != predictor:
            raise ValueError('Stale predictor: independently reassess the proposal on the current owner')
        return self.field.commit_history(proposed, event, predictor=predictor,
            decision_policy=predictor, proposal_id=proposal_id)


def extend_history(parent, seed=16116):
    torch.manual_seed(seed)
    spec = dict(parent.specification()); spec.pop('type')
    owner = HistoryOwner(**spec)
    result = owner.load_state_dict(parent.state_dict(), strict=False)
    allowed = ('field.continuum.', 'field.raw_history_gain', 'field.history_', 'field._extra_state')
    if result.unexpected_keys or any(not key.startswith(allowed) for key in result.missing_keys):
        raise ValueError('Unexpected history-parent incompatibility')
    for name, p in owner.named_parameters():
        p.requires_grad_(name.startswith(('field.continuum.', 'field.raw_history_gain')))
    return owner
