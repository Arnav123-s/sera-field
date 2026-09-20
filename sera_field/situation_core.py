"""Finite gauge-field situation core for the next curriculum, initialized from scratch.

This is an explicit lattice action and learned controller, not an implementation of
the paper's unspecified holographic projection or Wetterich representation growth.
There is no next-token head and no pretrained text encoder.
"""

from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F

from .gauge import adjoint_rotations, group_from_coordinates


def token_bytes(texts, length=256):
    """UTF-8 input views; zero is padding, byte b has index b+1."""
    if length < 1:
        raise ValueError("Positive input length required")
    result = torch.zeros(len(texts), length, dtype=torch.long)
    for index, text in enumerate(texts):
        values = list(text.encode("utf-8")[:length])
        if values:
            result[index, :len(values)] = torch.tensor(values) + 1
    return result


def ring_transport(rotations, state):
    forward = torch.einsum("nab,...nb->...na", rotations, state.roll(-1, -2))
    backward = torch.einsum("nba,...nb->...na", rotations.roll(1, 0), state.roll(1, -2))
    return forward, backward


def boundary_energy(state, source, rotations, stiffness):
    forward, _ = ring_transport(rotations, state)
    return (.5 * (state - forward).square().sum((-1, -2))
            + .5 * stiffness * state.square().sum((-1, -2))
            - (source * state).sum((-1, -2)))


def boundary_step(state, source, rotations, stiffness, dt=.1):
    """Explicit descent on the documented finite action, with a stable step bound."""
    if not 0 < dt <= .2:
        raise ValueError("The tested step bound is 0 < dt <= 0.2")
    forward, backward = ring_transport(rotations, state)
    gradient = (2 + stiffness) * state - forward - backward - source
    return state - dt * gradient


def loop_feature(links, source):
    """Closed holonomy of input-conditioned links: exp(i J_i.sigma) U_i.

    Both J and U must be transformed for a change of local frame. Changing J to
    describe a different mass or word is an input change, not a gauge transform.
    """
    injected = group_from_coordinates(source) @ links
    loop = injected[..., 0, :, :]
    for index in range(1, links.shape[0]):
        loop = loop @ injected[..., index, :, :]
    return torch.diagonal(loop, dim1=-2, dim2=-1).sum(-1).real / 2


@dataclass(frozen=True)
class Situation:
    goal: str
    evidence_ids: tuple
    field: torch.Tensor
    hypothetical: bool = False

    def branch(self):
        # Tensor storage must be separate even though the record is frozen.
        return Situation(self.goal, self.evidence_ids, self.field.detach().clone(), True)


class SituationOwner(nn.Module):
    """One registered owner for input, situation evolution, prediction and choice.

    Supplied interfaces: UTF-8 views, eight numerical channels with missing masks,
    candidate descriptors and fixed head dimensions. These are engineering, not
    discovered meanings. Training and held-out transfer must establish semantics.
    """
    def __init__(self, nodes=8, embedding=24, numbers=8, candidate_features=8,
                 outcomes=8, rounds=4):
        super().__init__()
        self.config = dict(nodes=nodes, embedding=embedding, numbers=numbers,
                           candidate_features=candidate_features, outcomes=outcomes, rounds=rounds)
        self.bytes = nn.Embedding(257, embedding, padding_idx=0)
        self.phrases = nn.Conv1d(embedding, embedding, 5, padding=2)
        self.input_field = nn.Linear(embedding + 2 * numbers, nodes * 3)
        self.links = nn.Parameter(torch.randn(nodes, 3) * .15)
        self.raw_stiffness = nn.Parameter(torch.tensor(0.))
        self.prior = nn.Parameter(torch.randn(nodes, 3) * .01)
        self.prediction = nn.Linear(nodes + 1, outcomes)
        self.candidate = nn.Linear(candidate_features, nodes + 1)
        self.policy = nn.Sequential(nn.Linear(2 * (nodes + 1), 24), nn.Tanh(), nn.Linear(24, 1))

    def encode(self, tokens, numbers, observed):
        if numbers.shape != observed.shape or numbers.shape[-1] != self.config["numbers"]:
            raise ValueError("Explicit numeric values and observation masks required")
        if not torch.isfinite(numbers).all() or not torch.isfinite(observed).all():
            raise ValueError("Inputs must be finite; use the observation mask for missing values")
        if not ((observed == 0) | (observed == 1)).all():
            raise ValueError("Observation masks must be binary")
        mask = (tokens != 0).to(numbers.dtype).unsqueeze(-1)
        words = self.bytes(tokens)
        phrases = torch.tanh(self.phrases(words.transpose(1, 2)).transpose(1, 2)) * mask
        text = phrases.sum(1) / mask.sum(1).clamp_min(1)
        joint = torch.cat((text, numbers * observed, observed), -1)
        return torch.tanh(self.input_field(joint)).reshape(-1, self.config["nodes"], 3)

    def imagine(self, source, previous=None, *, use_imagination=True):
        state = self.prior.expand(source.shape[0], -1, -1) if previous is None else previous.clone()
        rotations = adjoint_rotations(self.links)
        stiffness = .1 + .9 * self.raw_stiffness.sigmoid()  # [0.1,1], norm Hessian <= 5
        if use_imagination:
            for _ in range(self.config["rounds"]):
                state = boundary_step(state, source, rotations, stiffness)
        else:
            # A matched no-dynamics control still sees the same input and heads.
            state = source
        loop = loop_feature(group_from_coordinates(self.links), source).to(state.dtype)
        features = torch.cat((state.square().sum(-1).add(1e-8).sqrt(), loop[:, None]), -1)
        return state, features

    def forward(self, tokens, numbers, observed, candidates, previous=None, *, use_imagination=True):
        source = self.encode(tokens, numbers, observed)
        state, features = self.imagine(source, previous, use_imagination=use_imagination)
        candidate = torch.tanh(self.candidate(candidates))
        shared = features[:, None, :].expand_as(candidate)
        logits = self.policy(torch.cat((shared, candidate), -1)).squeeze(-1)
        return {"state": state, "features": features, "prediction": self.prediction(features),
                "logits": logits, "source": source}

    def specification(self):
        return {"type": "situation-field-002", **self.config}
