"""The imagination (B2, low compute): from a world's evidence table (sera.compact), imagine many laws at once.

Every candidate law piece (term) gets a vector built from what it is (its pieces: operator, input, shapes, exponent,
frequency, so pieces it never saw together still mean something) and from the evidence about it in this world. A law
of one or two terms is scored from its terms' vectors plus a pair interaction. Softmax over all 3,175 certifiable
laws gives a probability for every law: `propose` returns the K most probable (the cloud the mind tests).

About 25k parameters; one CPU thread trains it (the laptop overheated once; low compute is the design, not a limit).
The judge never trusts it: it decides only what the mind tests first and which experiments it makes.
"""
import math

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ccops5.core import grammar
from . import compact as C, dreams as D

_OPS = ('IDEA', 'PROD', 'POW', 'DRV')


def piece_vector(term):
    """What a term is made of, as numbers (44): operator, input, shapes, sin/cos, Fourier features of p and omega."""
    v = np.zeros(44, np.float32)
    if term[0] == 'product':
        v[1] = 1
        v[7 + grammar.SHAPES.index(term[1])] = 1
        v[13 + grammar.SHAPES.index(term[2])] = 1
    elif term[0] == 'power':
        v[2] = 1
        v[4 + ('position', 'speed').index(term[1])] = 1
        k = np.arange(1, 7)
        v[20:26], v[26:32] = np.sin(k * math.pi * term[2] / 4), np.cos(k * math.pi * term[2] / 4)
    elif term[0] == 'drive':
        v[3] = 1
        v[18 + ('sin', 'cos').index(term[1])] = 1
        k = np.arange(1, 7)
        v[32:38], v[38:44] = np.sin(k * math.pi * term[2] / 8), np.cos(k * math.pi * term[2] / 8)
    else:
        v[0] = 1
        v[4 + ('position', 'speed', 'nothing').index(term[0])] = 1
        v[7 + (grammar.SHAPES + ('steady',)).index(term[1])] = 1
    return v


PIECES = np.stack([piece_vector(t) for t in C.TERMS])                 # (270, 44)
_FI = np.array([C.TERM_INDEX[f[0]] if len(f) >= 1 else -1 for f in D.FAMILIES])
_FJ = np.array([C.TERM_INDEX[f[1]] if len(f) == 2 else -1 for f in D.FAMILIES])


class Imagination(nn.Module):
    def __init__(self, d=64, e=32):
        super().__init__()
        self.register_buffer('pieces', torch.tensor(PIECES))
        self.register_buffer('fi', torch.tensor(_FI))
        self.register_buffer('fj', torch.tensor(_FJ))
        self.embed = nn.Sequential(nn.Linear(PIECES.shape[1], e), nn.GELU(), nn.Linear(e, e))
        self.evidence = nn.Sequential(nn.Linear(C.TERM_FEATURES + C.WORLD_FEATURES + e, d), nn.GELU(),
                                      nn.Linear(d, d), nn.GELU())
        self.att = nn.Linear(d, 1)
        self.context = nn.Sequential(nn.Linear(3 * d, d), nn.GELU(), nn.Linear(d, d))
        self.single = nn.Linear(d, 1)
        self.pair = nn.Parameter(torch.zeros(d, d))
        self.pair_bias = nn.Parameter(torch.zeros(1))
        self.empty = nn.Linear(C.WORLD_FEATURES, 1)

    def forward(self, feats, world):
        """feats (B, 270, 8), world (B, 7) -> logits over the 3,175 laws (B, F)."""
        B = feats.shape[0]
        dt = self.single.weight.dtype       # ccops5.laws sets torch's default dtype at import; follow the weights
        feats, world = feats.to(dt), world.to(dt)
        e = self.embed(self.pieces.to(dt)).unsqueeze(0).expand(B, -1, -1)
        h = self.evidence(torch.cat([feats, world.unsqueeze(1).expand(-1, feats.shape[1], -1), e], -1))
        w = torch.softmax(self.att(h).squeeze(-1), -1)
        ctx = torch.cat([(w.unsqueeze(-1) * h).sum(1), h.amax(1)], -1)
        h = h + self.context(torch.cat([h, ctx.unsqueeze(1).expand(-1, h.shape[1], -1)], -1))
        s = self.single(h).squeeze(-1)                                  # (B, 270)
        fi, fj = self.fi.clamp(min=0), self.fj.clamp(min=0)
        hi, hj = h[:, fi], h[:, fj]                                     # (B, F, d)
        A = 0.5 * (self.pair + self.pair.T)
        pair = torch.einsum('bfd,de,bfe->bf', hi, A, hj) + self.pair_bias
        logit = s[:, fi] + torch.where(self.fj >= 0, s[:, fj] + pair, torch.zeros_like(pair))
        return torch.where(self.fi >= 0, logit, self.empty(world).expand(-1, logit.shape[1]))


def loss(model, feats, world, labels):
    return F.cross_entropy(model(feats, world), labels)


@torch.no_grad()
def propose(model, feats, world, K=16):
    """For each world: the K most probable laws [(family, probability)], probabilities over all 3,175 laws."""
    p = torch.softmax(model(torch.as_tensor(feats, dtype=torch.float32), torch.as_tensor(world)), -1)
    top = torch.topk(p, K, dim=-1)
    return [[(D.FAMILIES[i], float(q)) for q, i in zip(qs.tolist(), ix.tolist())]
            for qs, ix in zip(top.values, top.indices)]


def imagine_world(model, throws, K=16):
    """The K laws the imagination proposes for these throws (compacting them first), with probabilities."""
    f, w, extras = C.compact(throws)
    return propose(model, f[None].astype(np.float32), w[None], K)[0], extras
