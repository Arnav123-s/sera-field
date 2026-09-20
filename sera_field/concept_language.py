"""Learned lexical residual for the acquired-model question interface."""
import hashlib
import re

import torch
from torch import nn
from torch.nn import functional as F

from .concept_owner import ConceptOwner


def lexical_features(texts, size=4096):
    """Deterministic signed feature hashing, with no variable-name rules."""
    x = torch.zeros(len(texts), size)
    for row, text in enumerate(texts):
        for word in re.findall(r"[a-z]+", text.lower()):
            padded = '^' + word + '$'
            features = ['w:' + word]
            features += ['c:' + padded[i:i+n] for n in (2, 3, 4, 5)
                         for i in range(max(0, len(padded)-n+1))]
            for feature in features:
                digest = hashlib.blake2b(feature.encode(), digest_size=8).digest()
                slot = int.from_bytes(digest[:4], 'little') % size
                x[row, slot] += 1. if digest[4] & 1 else -1.
    return F.normalize(x, dim=-1)


class LanguageConceptOwner(ConceptOwner):
    def __init__(self, *args, lexical_size=4096, base_route_scale=1., **kwargs):
        super().__init__(*args, **kwargs)
        if base_route_scale not in (0., 1.):
            raise ValueError('Explicit routing construction required')
        self.base_route_scale = base_route_scale
        self.lexical_size = lexical_size
        self.lexical_route = nn.Linear(lexical_size, 2)
        nn.init.zeros_(self.lexical_route.weight)
        nn.init.zeros_(self.lexical_route.bias)

    def specification(self):
        return {**super().specification(), 'type': 'concept-language-010',
                'lexical_size': self.lexical_size, 'base_route_scale': self.base_route_scale}

    def route_logits(self, questions):
        return self.base_route_scale*super().route_logits(questions) + self.lexical_route(
            lexical_features(questions, self.lexical_size))


def extend(parent):
    spec = parent.specification()
    spec.pop('type')
    torch.manual_seed(10110)
    owner = LanguageConceptOwner(**spec)
    result = owner.load_state_dict(parent.state_dict(), strict=False)
    if result.unexpected_keys or set(result.missing_keys) != {
            'lexical_route.weight', 'lexical_route.bias'}:
        raise ValueError('Unexpected language-extension identity')
    for name, parameter in owner.named_parameters():
        parameter.requires_grad_(name.startswith('lexical_route.'))
    return owner
