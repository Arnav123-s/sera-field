"""One perfect-tensor quantum code cell, simulated with finite complex arrays.

The bulk logical qubit is encoded into five boundary qubits. Recovery corrects
one unknown single-qubit error or up to two declared erasures. It protects
represented amplitudes, not the scientific validity of the represented claim.
"""
from functools import lru_cache
import itertools

import torch


def pauli_word(word):
    matrices = {'I': torch.eye(2, dtype=torch.complex128),
        'X': torch.tensor([[0, 1], [1, 0]], dtype=torch.complex128),
        'Y': torch.tensor([[0, -1j], [1j, 0]], dtype=torch.complex128),
        'Z': torch.tensor([[1, 0], [0, -1]], dtype=torch.complex128)}
    result = torch.ones(1, 1, dtype=torch.complex128)
    for letter in word:
        result = torch.kron(result, matrices[letter])
    return result


@lru_cache(maxsize=1)
def code_isometry():
    state = torch.zeros(32, dtype=torch.complex128); state[0] = 1
    for word in ('XZZXI', 'IXZZX', 'XIXZZ', 'ZXIXZ'):
        state = (state + pauli_word(word) @ state) / 2
    state = state / torch.linalg.vector_norm(state)
    partner = pauli_word('XXXXX') @ state
    return torch.stack((state, partner), -1)


@lru_cache(maxsize=12)
def recovery_basis(erasures=()):
    if len(set(erasures)) != len(erasures) or any(i not in range(5) for i in erasures) or len(erasures) > 2:
        raise ValueError('The declared erasure contract covers at most two distinct boundary sites')
    if erasures:
        words = []
        for errors in itertools.product('IXYZ', repeat=len(erasures)):
            word = ['I'] * 5
            for index, letter in zip(erasures, errors):
                word[index] = letter
            words.append(''.join(word))
    else:
        words = ['IIIII']
        for index in range(5):
            for letter in 'XYZ':
                word = ['I'] * 5; word[index] = letter; words.append(''.join(word))
    isometry = code_isometry()
    return torch.stack([pauli_word(word) @ isometry for word in words])


def encode(logical):
    if logical.shape[-1] != 2 or not torch.isfinite(logical).all():
        raise ValueError('Finite logical amplitudes required')
    if not torch.allclose(logical.abs().square().sum(-1), torch.ones_like(logical[..., 0].real), atol=1e-6):
        raise ValueError('Normalize the logical input explicitly before encoding')
    return logical.to(torch.complex128) @ code_isometry().T


def recover(encoded, *, erasures=()):
    if encoded.shape[-1] != 32 or not torch.isfinite(encoded).all():
        raise ValueError('Finite encoded boundary amplitudes required')
    erasures = tuple(sorted(erasures))
    basis = recovery_basis(erasures)
    logical_branches = torch.einsum('sjl,...j->...sl', basis.conj(), encoded.to(torch.complex128))
    density = torch.einsum('...si,...sj->...ij', logical_branches, logical_branches.conj())
    probabilities = logical_branches.abs().square().sum(-1)
    return density, probabilities


def encode_density(density):
    if not torch.isfinite(density).all() or bool(((density < 0) | (density > 1)).any()):
        raise ValueError('A represented density in [0,1] is required')
    logical = torch.stack(((1 - density).sqrt(), density.sqrt()), -1)
    return encode(logical)


def decode_density(encoded, *, erasures=()):
    logical, syndrome = recover(encoded, erasures=erasures)
    norm = logical.diagonal(dim1=-2, dim2=-1).real.sum(-1)
    if not torch.allclose(norm, torch.ones_like(norm), atol=1e-6):
        raise ValueError('Recovery left norm outside the stated code/noise contract')
    return logical[..., 1, 1].real, syndrome
