"""Fresh shared-field learner: source grounding, programs and observed worlds.

All task interfaces enter the finite gauge-field dynamics. Engineering supplies
tokenization, arithmetic primitives and measurement channels, never hidden answers.
The owner has no next-token loss and imports no trained weights.
"""
import math
from fractions import Fraction
import torch
from torch import nn
from torch.nn import functional as F

from .situation_core import SituationOwner
from .study_data import VOCAB, tokens


class GroundedOwner(nn.Module):
    def __init__(self, width=48, nodes=8, rounds=4):
        super().__init__()
        self.config = dict(width=width, nodes=nodes, rounds=rounds)
        self.words = nn.Embedding(VOCAB, width, padding_idx=0)
        self.local = nn.Conv1d(width, width, 5, padding=2)
        self.word_norm = nn.LayerNorm(width)
        self.field = SituationOwner(nodes=nodes, embedding=width, rounds=rounds)
        self.text_boundary = nn.Linear(4 * width + 4, nodes * 3)
        self.read_score = nn.Sequential(nn.Linear(4 * width + nodes + 5, 64), nn.Tanh(), nn.Linear(64, 1))
        self.math_boundary = nn.Linear(width, nodes * 3)
        self.math_query = nn.Sequential(nn.Linear(width + nodes + 1, 64), nn.Tanh())
        self.math_operator = nn.Linear(64, 4)
        self.number_embed = nn.Sequential(nn.Linear(width + 5, 48), nn.Tanh())
        self.math_left = nn.Linear(64, 48)
        self.math_right = nn.Linear(64, 48)
        self.math_pair = nn.Parameter(torch.randn(4, 48, 48) * .02)
        self.observation = nn.Sequential(nn.Linear(5, width), nn.Tanh(), nn.Linear(width, width))
        self.world_boundary = nn.Linear(2 * width + 1, nodes * 3)
        self.world_decode = nn.Sequential(nn.Linear(2 * width + nodes + 2, 96), nn.Tanh(), nn.Linear(96, 12))
        self.investigation = nn.Sequential(nn.Linear(2 * width + nodes + 2 + 7, 64), nn.Tanh(), nn.Linear(64, 1))
        self.mode = 'full'

    def specification(self):
        return {'type': 'grounded-field-003', **self.config}

    def encode_tokens(self, sequences):
        """Local context is chunked with overlap; every token contributes once."""
        chunks, owners, masks = [], [], []
        for owner, seq in enumerate(sequences):
            seq = seq or [1]
            for start in range(0, len(seq), 256):
                end = min(len(seq), start + 256)
                lo, hi = max(0, start - 2), min(len(seq), end + 2)
                chunks.append(seq[lo:hi])
                owners.append(owner)
                masks.append([0.] * (start - lo) + [1.] * (end - start) + [0.] * (hi - end))
        pooled = torch.zeros(len(sequences), self.config['width'])
        totals = torch.zeros(len(sequences), 1)
        for start in range(0, len(chunks), 96):
            part, weight = chunks[start:start+96], masks[start:start+96]
            size = max(map(len, part))
            ids = torch.zeros(len(part), size, dtype=torch.long)
            valid = torch.zeros(len(part), size, 1)
            for i, (seq, mask) in enumerate(zip(part, weight)):
                ids[i, :len(seq)] = torch.tensor(seq)
                valid[i, :len(mask), 0] = torch.tensor(mask)
            embedded = self.words(ids)
            hidden = self.word_norm(embedded + torch.tanh(self.local(embedded.transpose(1, 2)).transpose(1, 2)))
            index = torch.tensor(owners[start:start+96])
            pooled = pooled.index_add(0, index, (hidden * valid).sum(1))
            totals.index_add_(0, index, valid.sum(1))
        return pooled / totals.clamp_min(1)

    def encode_texts(self, texts):
        return self.encode_tokens([tokens(t) for t in texts])

    def settle(self, source):
        state, feature = self.field.imagine(source.reshape(-1, self.config['nodes'], 3),
                                           use_imagination=self.mode != 'no_imagination')
        if self.mode == 'no_loop':
            feature = torch.cat((feature[:, :-1], feature[:, -1:] * 0), -1)
        return state, feature

    def rank(self, questions, options):
        """Candidate features depend only on the visible question and source text."""
        qtokens = [tokens(q) for q in questions]
        flat = [option for candidates in options for option in candidates]
        otokens = [tokens(o) for o in flat]
        q = self.encode_tokens(qtokens)
        o = self.encode_tokens(otokens)
        indices = [i for i, candidates in enumerate(options) for _ in candidates]
        shared = q[indices]
        overlap = []
        for i, seq in zip(indices, otokens):
            a, b = set(qtokens[i]), set(seq)
            overlap.append([len(a & b) / max(1, len(a)), len(a & b) / max(1, len(b)),
                            math.log1p(len(seq)) / 10, math.log1p(len(qtokens[i])) / 10])
        features = torch.cat((shared, o, shared * o, (shared - o).abs(), torch.tensor(overlap)), -1)
        _, field = self.settle(torch.tanh(self.text_boundary(features)))
        scores = self.read_score(torch.cat((features, field), -1)).squeeze(-1)
        output = torch.full((len(questions), max(map(len, options))), -1e9)
        cursor = 0
        for i, candidates in enumerate(options):
            output[i, :len(candidates)] = scores[cursor:cursor+len(candidates)]
            cursor += len(candidates)
        return output

    def math_logits(self, questions, pools):
        q = self.encode_texts(questions)
        _, field = self.settle(torch.tanh(self.math_boundary(q)))
        query = self.math_query(torch.cat((q, field), -1))
        n = max(map(len, pools))
        context = []
        features = torch.zeros(len(pools), n, 5)
        mask = torch.zeros(len(pools), n, dtype=torch.bool)
        for i, (question, pool) in enumerate(zip(questions, pools)):
            for j in range(n):
                if j >= len(pool):
                    context.append('')
                    continue
                raw = pool[j]
                value = float(Fraction(raw))
                # Numeric position/context are observed, never target dependent.
                needle = str(int(value)) if value.is_integer() else str(value)
                at = question.find(needle)
                context.append(question[max(0, at-55):at+len(needle)+55] if at >= 0 else 'supplied constant ' + raw)
                features[i, j] = torch.tensor([math.copysign(math.log1p(abs(value)), value) / 10,
                                              float(at >= 0), j / max(1, len(pool)-1),
                                              float(value == 0), float(value < 0)])
                mask[i, j] = True
        embedded = self.encode_texts(context).reshape(len(pools), n, -1)
        number = self.number_embed(torch.cat((embedded, features), -1))
        left = (number * self.math_left(query)[:, None]).sum(-1) / math.sqrt(48)
        right = (number * self.math_right(query)[:, None]).sum(-1) / math.sqrt(48)
        pair = torch.einsum('bih,ohk,bjk->boij', number, self.math_pair, number) / math.sqrt(48)
        logits = self.math_operator(query)[:, :, None, None] + left[:, None, :, None] + right[:, None, None, :] + pair
        valid = mask[:, None, :, None] & mask[:, None, None, :]
        logits = logits.masked_fill(~valid, -1e9)
        zeros = features[:, :, 3].bool()
        logits[:, 3] = logits[:, 3].masked_fill(zeros[:, None, :], -1e9)
        return logits

    def world(self, observations, present):
        """Observed rows [velocity, force/mass, acceleration]; no hidden parameters."""
        if observations.shape[-1] != 3 or present.shape != observations.shape[:-1]:
            raise ValueError('Explicit observation mask and three measured channels required')
        x = observations * present[..., None]
        raw = torch.stack((x[..., 0]/3, x[..., 1]/3, x[..., 2]/6,
                           x[..., 0] * x[..., 2]/12, x[..., 1] * x[..., 2]/12), -1)
        h = self.observation(raw) * present[..., None]
        count = present.sum(1, keepdim=True).clamp_min(1)
        mean = h.sum(1) / count
        variance = ((h - mean[:, None]).square() * present[..., None]).sum(1) / count
        summary = torch.cat((mean, variance, present.sum(1, keepdim=True) / 8), -1)
        state, field = self.settle(torch.tanh(self.world_boundary(summary)))
        latent = torch.cat((summary, field), -1)
        coefficients = self.world_decode(latent).reshape(-1, 3, 4)
        return {'state': state, 'latent': latent, 'coefficients': coefficients}

    @staticmethod
    def consequences(coefficients, queries):
        # A supplied observable basis. Coefficients themselves are learned.
        v, f = queries[..., 0], queries[..., 1]
        basis = torch.stack((f, v, v * v.abs(), torch.ones_like(v)), -1)
        return torch.einsum('bhc,bqc->bhq', coefficients, basis)

    def probe_logits(self, observations, present, probes, goal_queries):
        world = self.world(observations, present)
        imagined = self.consequences(world['coefficients'], probes)
        goal = goal_queries.mean(1)
        mean, spread = imagined.mean(1), imagined.std(1)
        descriptors = torch.cat((probes / 3, mean[..., None] / 6, spread[..., None] / 6,
                                 goal[:, None, :].expand(-1, probes.shape[1], -1) / 3,
                                 probes[..., :1].square() / 9), -1)
        latent = world['latent'][:, None].expand(-1, probes.shape[1], -1)
        logits = self.investigation(torch.cat((latent, descriptors), -1)).squeeze(-1)
        return logits, world
