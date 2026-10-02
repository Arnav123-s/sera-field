"""ccops5 lab | laws: learned axes, and how a new one is grown.

A law is a learned function of some of (position, speed, push). Nobody tells
the learner what shape it has or which of those it depends on. A situation
mixes the laws it needs, each with its own coefficient: the laws are what is
true everywhere, the coefficients are what is true of this object here.

Built as an isolated experiment. Not part of sera-field.
"""
import statistics

import torch
from torch import nn

torch.set_default_dtype(torch.float64)

INPUT_NAMES = ('position', 'speed', 'push')
# Every way a new law could depend on what the learner senses: the several
# explanations it imagines for one surprise.
SUBSETS = ((0,), (1,), (2,), (0, 1), (0, 2), (1, 2), (0, 1, 2))
FOLDS = 3


class Law(nn.Module):
    """A straight-line part plus a bendy part, over the inputs it depends on."""

    def __init__(self, name, origin, inputs=(0, 1, 2), hidden=32):
        super().__init__()
        self.name, self.origin, self.inputs = name, origin, tuple(inputs)
        self.line = nn.Linear(3, 1, bias=False)
        self.net = nn.Sequential(nn.Linear(3, hidden), nn.Tanh(), nn.Linear(hidden, hidden),
                                 nn.Tanh(), nn.Linear(hidden, 1))
        gate = torch.zeros(3)
        gate[list(self.inputs)] = 1.0
        self.register_buffer('gate', gate)
        self.register_buffer('mu', torch.zeros(3))
        self.register_buffer('sd', torch.ones(3))
        self.register_buffer('scale', torch.ones(()))

    def forward(self, z):
        u = self.gate * (z - self.mu) / self.sd
        return self.scale * (self.line(u) + self.net(u)).squeeze(-1)


def design(laws, z, mask=None):
    """One column per law, evaluated at situations z of shape (..., 3)."""
    if not laws:
        return z.new_zeros(z.shape[:-1] + (0,))
    columns = torch.stack([law(z) for law in laws], -1)
    if mask is not None:
        columns = columns * torch.as_tensor(mask, dtype=columns.dtype)
    return columns


def _stack(datasets):
    n, e = max(len(a) for _, a in datasets), len(datasets)
    z, a, m = torch.zeros(e, n, 3), torch.zeros(e, n), torch.zeros(e, n)
    for i, (zi, ai) in enumerate(datasets):
        z[i, :len(ai)], a[i, :len(ai)], m[i, :len(ai)] = zi, ai, 1.0
    return z, a, m


def _fixed(laws, z, m, mask):
    with torch.no_grad():
        return design(laws, z, mask) * m[..., None]


def _errors(law, z, a, m, fixed):
    """Mean squared error left in each situation after it picks its own best
    coefficients for the old laws plus this one (variable projection)."""
    x = torch.cat((fixed, (law(z) * m)[..., None]), -1)
    gram = x.transpose(1, 2) @ x + 1e-6 * torch.eye(x.shape[-1])
    theta = torch.linalg.solve(gram, x.transpose(1, 2) @ a[..., None])
    return (a - (x @ theta).squeeze(-1)).square().sum(-1) / m.sum(-1)


def _train(datasets, laws, inputs, name, origin, seed, mask, steps, lr=3e-3):
    torch.manual_seed(seed)
    law = Law(name, origin, inputs)
    z_all = torch.cat([z for z, _ in datasets])
    law.mu.copy_(z_all.mean(0))
    law.sd.copy_(z_all.std(0).clamp_min(1e-3))
    z, a, m = _stack(datasets)
    fixed = _fixed(laws, z, m, mask)
    optimizer = torch.optim.Adam(law.parameters(), lr=lr)
    for _ in range(steps):
        # Average of each situation's typical error: one odd situation pulls
        # less than it would on squared errors.
        loss = (_errors(law, z, a, m, fixed) + 1e-12).sqrt().mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        law.scale /= law(z_all).square().mean().sqrt().clamp_min(1e-9)
    return law


def grow(datasets, laws, name, origin, *, seed, mask=None, steps=400, final_steps=1200):
    """Grow one new law shared by the surprising situations.

    It imagines one candidate law per way of depending on what it senses.
    Each candidate is judged on situations it was not trained on (every
    situation is held back once), by the typical leftover error, so one odd
    situation cannot decide. The simplest candidate that is nearly as good as
    the best one wins, and is refitted on everything. Old laws stay fixed.
    """
    n = len(datasets)
    folds = [[j for j in range(n) if j % FOLDS == f] for f in range(min(FOLDS, n))]
    tried = []
    for i, inputs in enumerate(SUBSETS):
        held_back = []
        for f, held in enumerate(folds):
            train = [datasets[j] for j in range(n) if j not in held] or [datasets[j] for j in held]
            test = [datasets[j] for j in held]
            candidate = _train(train, laws, inputs, name, origin, seed + 10 * i + f, mask, steps)
            zh, ah, mh = _stack(test)
            with torch.no_grad():
                held_back += _errors(candidate, zh, ah, mh, _fixed(laws, zh, mh, mask)).tolist()
        tried.append((statistics.median(held_back), inputs))
    best = min(score for score, _ in tried)
    near = [t for t in tried if t[0] <= best * 1.05]
    _, inputs = min(near, key=lambda t: (len(t[1]), t[0]))
    law = _train(datasets, laws, inputs, name, origin, seed + 100, mask, final_steps)
    return law, {'explanations_tried': [{'depends_on': [INPUT_NAMES[j] for j in inp],
                                         'error_on_unseen_situations': score} for score, inp in tried],
                 'chosen': [INPUT_NAMES[j] for j in inputs]}
