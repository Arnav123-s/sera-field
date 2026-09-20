"""Exact finite conditional neural ensemble, correlators and action forces.

The context is held fixed for density/score derivatives. The operational density
is a normalized finite mixture. Its Edgeworth action is a named approximation.
"""
import itertools
import math

import torch
from torch import nn


def signs(width, *, dtype, device):
    if not 1 <= width <= 8:
        raise ValueError('Finite exact enumeration is restricted to 1..8 signs')
    return torch.tensor(list(itertools.product((-1., 1.), repeat=width)), dtype=dtype, device=device)


def mixture_means(features):
    """features: batch x ensemble-width x field-dimension, including 1/sqrt(N)."""
    return torch.einsum('sk,bkd->bsd', signs(features.shape[-2], dtype=features.dtype,
                                            device=features.device), features)


def cumulant_generator(current, features, sigma):
    projection = torch.einsum('bd,bkd->bk', current, features)
    log_cosh = torch.logaddexp(projection, -projection) - math.log(2.)
    return .5 * sigma.square() * current.square().sum(-1) + log_cosh.sum(-1)


def covariance(features, sigma):
    eye = torch.eye(features.shape[-1], dtype=features.dtype, device=features.device)
    return features.transpose(-1, -2) @ features + sigma.square() * eye


def fourth_connected(features):
    """Explicit small-field diagnostic; use directional contractions for large D."""
    if features.shape[-1] > 32:
        raise ValueError('Use a directional cumulant for a larger field')
    return -2 * torch.einsum('...ia,...ib,...ic,...id->...abcd', features, features, features, features)


def directional_fourth(direction, features):
    return -2 * torch.einsum('bd,bkd->bk', direction, features).pow(4).sum(-1)


def gaussian_inverse_product(vector, features, sigma):
    # Woodbury reduces a D-dimensional solve to N dimensions. Sigma has a
    # strictly positive contract, rather than an adjustable numerical jitter.
    n = features.shape[-2]
    eye = torch.eye(n, dtype=features.dtype, device=features.device)
    gram = features @ features.transpose(-1, -2)
    rhs = torch.einsum('bkd,bd->bk', features, vector)
    solved = torch.linalg.solve(eye + gram / sigma.square(), rhs[..., None]).squeeze(-1)
    correction = torch.einsum('bkd,bk->bd', features, solved)
    return vector / sigma.square() - correction / sigma.pow(4)


def gaussian_action(value, features, sigma):
    dimension = value.shape[-1]; n = features.shape[-2]
    eye = torch.eye(n, dtype=value.dtype, device=value.device)
    sign, logdet_small = torch.linalg.slogdet(eye + features @ features.transpose(-1, -2) / sigma.square())
    if not bool((sign > 0).all()):
        raise ValueError('Positive conditional covariance required')
    logdet = 2 * dimension * sigma.log() + logdet_small
    return .5 * (value * gaussian_inverse_product(value, features, sigma)).sum(-1) + \
        .5 * (logdet + dimension * math.log(2 * math.pi))


def exact_action_and_score(value, features, sigma):
    means = mixture_means(features)
    distance = (value[:, None] - means).square().sum(-1)
    component = -.5 * distance / sigma.square()
    action = .5 * value.shape[-1] * math.log(2 * math.pi) + value.shape[-1] * sigma.log() + \
        math.log(means.shape[1]) - component.logsumexp(-1)
    average = (component.softmax(-1)[..., None] * means).sum(1)
    return action, (average - value) / sigma.square()


def edgeworth_action(value, features, sigma):
    inverse_value = gaussian_inverse_product(value, features, sigma)
    u = torch.einsum('bkd,bd->bk', features, inverse_value)
    inverse_features = torch.stack([gaussian_inverse_product(features[:, i], features, sigma)
                                   for i in range(features.shape[1])], 1)
    v = (features * inverse_features).sum(-1)
    delta = -(u.pow(4) - 6 * u.square() * v + 3 * v.square()).sum(-1) / 12
    return gaussian_action(value, features, sigma) - delta, delta


class FiniteNeuralAction(nn.Module):
    def __init__(self, nodes, width=4):
        super().__init__()
        self.nodes = nodes; self.width = width
        self.coefficients = nn.Parameter(torch.randn(width, 3) * .5)
        self.context = nn.Sequential(nn.Linear(3, 16), nn.Tanh(), nn.Linear(16, width * 3))
        nn.init.zeros_(self.context[-1].weight); nn.init.zeros_(self.context[-1].bias)
        self.raw_sigma = nn.Parameter(torch.tensor(0.))
        self.raw_gain = nn.Parameter(torch.tensor(0.))

    def features(self, source, transport):
        incoming = (transport.roll(1, 0)[None] @ source.roll(1, 1)[..., None]).squeeze(-1)
        outgoing = (transport.transpose(-1, -2)[None] @ source.roll(-1, 1)[..., None]).squeeze(-1)
        invariant = torch.stack((source.square().sum(-1).mean(-1),
            (source * incoming).sum(-1).mean(-1), (incoming * outgoing).sum(-1).mean(-1)), -1)
        coefficients = .75 * (self.coefficients[None] +
            .25 * self.context(invariant).reshape(-1, self.width, 3)).tanh()
        basis = torch.stack((source, incoming, outgoing), 1)
        features = torch.einsum('bkj,bjnd->bknd', coefficients, basis) / math.sqrt(self.width)
        return features.flatten(2)

    def forward(self, source, transport, *, mode='exact', noise=0.):
        if mode not in {'exact', 'gaussian', 'disabled'} or not 0 <= noise <= .1:
            raise ValueError('Use a registered conditional action and bounded teaching noise')
        if mode == 'disabled':
            return source
        features = self.features(source, transport)
        sigma = .2 + .6 * self.raw_sigma.sigmoid()
        value = source + noise * torch.randn_like(source) if noise else source
        flat = value.flatten(1)
        if mode == 'exact':
            _, score = exact_action_and_score(flat, features, sigma)
        else:
            score = -gaussian_inverse_product(flat, features, sigma)
        vectors = score.reshape_as(source)
        bounded = vectors / (1 + torch.linalg.vector_norm(vectors, dim=-1, keepdim=True))
        return value + .15 * self.raw_gain.tanh() * bounded

    @torch.no_grad()
    def diagnostics(self, source, transport):
        features = self.features(source, transport); value = source.flatten(1)
        sigma = .2 + .6 * self.raw_sigma.sigmoid()
        exact, score = exact_action_and_score(value, features, sigma)
        gauss = gaussian_action(value, features, sigma)
        expansion, delta = edgeworth_action(value, features, sigma)
        direction = value / value.norm(dim=-1, keepdim=True).clamp_min(1e-12)
        return {'exact_action': exact.tolist(), 'gaussian_action': gauss.tolist(),
            'fourth_order_action': expansion.tolist(), 'density_correction': delta.tolist(),
            'negative_truncated_density': (1 + delta <= 0).tolist(),
            'directional_connected_fourth': directional_fourth(direction, features).tolist(),
            'score_norm': score.norm(dim=-1).tolist(), 'sigma': float(sigma),
            'signed_gain': float(.15 * self.raw_gain.tanh()), 'enumerated_states': 2 ** self.width,
            'contract': 'conditional context fixed; exact finite mixture is the operational action'}
