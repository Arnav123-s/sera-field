"""A fresh owner whose observed memory and imagined boundary learn together.

No inherited owner or pretrained tensor is loaded. The primitives specify the
geometry; the input maps, connections, memory dynamics and output maps are jointly
learned. Observed updates and hypothetical reads are pure, explicit operations.
"""
from dataclasses import dataclass
import re

import torch
from torch import nn

from .clifford_sheaf import CliffordSheafField
from .continuum_core import MemoryContinuum
from .gauge import adjoint_rotations
from .study_data import tokens, VOCAB


def split_text(text):
    """Two consecutive, exhaustive source slices; no labels or summary supplied."""
    words = list(re.finditer(r'\S+', text))
    boundary = words[len(words) // 2].start() if len(words) > 1 else len(text)
    return text[:boundary], text[boundary:]


def select_state(state, indices):
    return {key: value[indices] if isinstance(value, torch.Tensor) else value
            for key, value in state.items()}


def detached_state(state):
    return {key: value.detach().clone() if isinstance(value, torch.Tensor) else value
            for key, value in state.items()}


@dataclass(frozen=True)
class NativeConfig:
    width: int = 48
    nodes: int = 8
    rounds: int = 4
    bulk_steps: int = 2
    branches: int = 3


class NativeOwner(nn.Module):
    def __init__(self, config=None):
        super().__init__()
        self.config = config or NativeConfig()
        c = self.config
        self.words = nn.Embedding(VOCAB, c.width, padding_idx=0)
        nn.init.normal_(self.words.weight, std=.08)
        with torch.no_grad(): self.words.weight[0].zero_()
        self.local = nn.Conv1d(c.width, c.width, 3, padding=1)
        self.text_pool = nn.Sequential(nn.Linear(c.width * 2, c.width), nn.LayerNorm(c.width), nn.Tanh())
        self.text_source = nn.Linear(c.width, c.nodes * 3)
        self.number_source = nn.Sequential(nn.Linear(6, c.width), nn.Tanh(), nn.Linear(c.width, c.nodes * 3))
        self.field = CliffordSheafField(c.nodes, c.rounds)
        self.memory = MemoryContinuum(c.nodes)
        self.observation_write = nn.Linear(c.nodes * 8, c.nodes * 3)
        self.raw_memory_gain = nn.Parameter(torch.tensor(0.))
        self.branches = nn.Parameter(.03 * torch.randn(c.branches, c.nodes, 3))
        features = c.nodes * (3 * 4 + 8) + c.nodes + 1
        self.joint_readout = nn.Sequential(nn.Linear(features, 64), nn.Tanh())
        self.meaning = nn.Linear(64, 3)
        self.choice = nn.Linear(64, 1)
        self.response = nn.Linear(64, 1)

    def specification(self):
        return {'type': 'native-memory-field-019', **vars(self.config)}

    def empty(self, batch):
        state = self.memory.empty(batch)
        # Each episode owns its observation count. A padded/absent text in one
        # batch row must not acquire events from another row's real input.
        state['events'] = torch.zeros(batch, dtype=torch.int64, device=state['fast'].device)
        return state

    def transport(self):
        return adjoint_rotations(self.field.links).transpose(-1, -2)

    def encode_texts(self, texts):
        if not texts: raise ValueError('Nonempty batch required')
        encoded = [tokens(text) for text in texts]
        indices = torch.zeros(len(texts), max(map(len, encoded)), dtype=torch.long)
        for i, row in enumerate(encoded): indices[i, :len(row)] = torch.tensor(row)
        valid = indices != 0
        values = self.local(self.words(indices).transpose(1, 2)).transpose(1, 2).tanh()
        mean = (values * valid[..., None]).sum(1) / valid.sum(1)[:, None]
        maximum = values.masked_fill(~valid[..., None], -torch.inf).amax(1)
        pooled = self.text_pool(torch.cat((mean, maximum), -1))
        return self.text_source(pooled).reshape(-1, self.config.nodes, 3).tanh()

    def encode_numbers(self, force, velocity, response=None):
        if force.shape != velocity.shape or force.ndim != 1:
            raise ValueError('One force and velocity per episode required')
        observed = response is not None
        value = torch.zeros_like(force) if response is None else response
        if value.shape != force.shape: raise ValueError('Response shape changed')
        inputs = torch.stack((force, velocity, value, force * velocity,
                              velocity.square(), torch.full_like(force, float(observed))), -1)
        if not bool(torch.isfinite(inputs).all()):
            raise ValueError('Finite numerical coordinates and derived features required')
        return self.number_source(inputs).reshape(-1, self.config.nodes, 3).tanh()

    def observe(self, state, source, *, equal_rates=False, checked_progress=None, simple_trace=False):
        transport = self.transport()
        recalled = self.memory.recall(state, transport)
        gain = .1 + self.raw_memory_gain.sigmoid()
        boundary, _ = self.field.imagine(source + gain * recalled)
        # The supplied observation is mapped through the same boundary used for
        # questions. No target gradient or teacher coefficient is an input here.
        stimulus = .5 * source + .5 * self.observation_write(boundary.flatten(1)).reshape_as(source).tanh()
        progress = source.new_zeros(source.shape[0]) if checked_progress is None else checked_progress
        if simple_trace:
            context = self.memory.context(state, stimulus)
            encoded, _ = self.memory.flow(stimulus, context, transport)
            updated = {'fast': .5 * state['fast'] + .5 * encoded,
                       'slow': state['slow'] * 0, 'bulk': state['bulk'] * 0,
                       'marks': state['marks'], 'flow_context': context, 'events': state['events']+1}
            return updated, {'control': 'single observed trace; fixed half write and retention'}
        updated, diagnostics = self.memory.advance(state, stimulus, progress, transport,
            relaxation_steps=self.config.bulk_steps, equal_rates=equal_rates)
        return updated, diagnostics

    def remember_texts(self, texts, state=None, *, equal_rates=False, simple_trace=False):
        state = self.empty(len(texts)) if state is None else state
        parts = [split_text(text) for text in texts]
        diagnostics = None
        for index in (0, 1):
            texts_now = [part[index] for part in parts]
            present = torch.tensor([bool(text.strip()) for text in texts_now])
            if not bool(present.any()): continue
            source = self.encode_texts(texts_now)
            updated, diagnostics = self.observe(state, source, equal_rates=equal_rates, simple_trace=simple_trace)
            state = {key: torch.where(present.reshape(-1, *([1] * (value.ndim-1))), value, state[key])
                     if isinstance(value, torch.Tensor) else value for key, value in updated.items()}
        return state, diagnostics

    def imagine(self, state, source, *, ablation=None):
        """Conditional reads return results without modifying observed history."""
        if ablation == 'erase_history': state = self.empty(len(source))
        if ablation == 'no_bulk':
            state = {**state, 'bulk': state['bulk'] * 0}
        remembered = self.memory.recall(state, self.transport())
        gain = .1 + self.raw_memory_gain.sigmoid()
        batch, n = source.shape[:2]; b = self.config.branches
        proposals = source[:, None] + gain * remembered[:, None] + .2 * self.branches.tanh()[None]
        field, geometry = self.field.imagine(proposals.reshape(batch * b, n, 3),
                                             use_imagination=ablation != 'no_imagination')
        relation = torch.cat((remembered, source, remembered * source, (remembered-source).abs()), -1)
        relation = relation.flatten(1)[:, None].expand(-1, b, -1).reshape(batch * b, -1)
        joined = self.joint_readout(torch.cat((relation, field.flatten(1), geometry), -1))
        return joined.reshape(batch, b, -1)

    def semantic(self, premises, hypotheses, *, memory=True, ablation=None):
        if len(premises) != len(hypotheses): raise ValueError('Paired inputs required')
        state, _ = self.remember_texts(premises, equal_rates=ablation == 'equal_rates', simple_trace=ablation == 'simple_trace')
        if not memory: state = self.empty(len(premises))
        return self.meaning(self.imagine(state, self.encode_texts(hypotheses), ablation=ablation))

    def option_logits(self, contexts, options, *, memory=True, ablation=None):
        if len(contexts) != len(options) or any(not row for row in options):
            raise ValueError('A nonempty option list per context is required')
        state, _ = self.remember_texts(contexts, equal_rates=ablation == 'equal_rates', simple_trace=ablation == 'simple_trace')
        if not memory: state = self.empty(len(contexts))
        indices = torch.tensor([i for i, row in enumerate(options) for _ in row])
        source = self.encode_texts([text for row in options for text in row])
        conditional = self.imagine(select_state(state, indices), source, ablation=ablation)
        scores = self.choice(conditional).squeeze(-1).mean(1)
        result = scores.new_full((len(options), max(map(len, options))), -torch.inf)
        offset = 0
        for i, row in enumerate(options):
            result[i, :len(row)] = scores[offset:offset+len(row)]; offset += len(row)
        return result

    def physical_state(self, support, *, equal_rates=False, simple_trace=False):
        if support.ndim != 3 or support.shape[-1] != 3:
            raise ValueError('Support must contain observed force, velocity, acceleration')
        state = self.empty(len(support))
        for item in support.unbind(1):
            source = self.encode_numbers(item[:, 0], item[:, 1], item[:, 2])
            state, _ = self.observe(state, source, equal_rates=equal_rates, simple_trace=simple_trace)
        return state

    def physical_query(self, state, queries, *, ablation=None):
        if queries.ndim != 3 or queries.shape[-1] != 2:
            raise ValueError('Queries supply force and velocity; no answer is allowed')
        batch, count = queries.shape[:2]
        indices = torch.arange(batch).repeat_interleave(count)
        flat = queries.reshape(-1, 2)
        source = self.encode_numbers(flat[:, 0], flat[:, 1])
        imagined = self.imagine(select_state(state, indices), source, ablation=ablation)
        return self.response(imagined).squeeze(-1).reshape(batch, count, self.config.branches)

    def physical(self, support, queries, *, memory=True, ablation=None):
        state = self.physical_state(support, equal_rates=ablation == 'equal_rates', simple_trace=ablation == 'simple_trace')
        if not memory: state = self.empty(len(support))
        return self.physical_query(state, queries, ablation=ablation)
