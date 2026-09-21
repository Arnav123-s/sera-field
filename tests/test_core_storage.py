import copy

import pytest
import torch

from sera_field.core_owner import CoreOwner
from sera_field.core_storage import protect_state, recover_state
from sera_field.native_owner import NativeConfig
from sera_field.perfect_tensor_memory import pauli_word
from sera_field.topological_memory import qwz_chern


def fixture():
    torch.manual_seed(22023)
    owner = CoreOwner(NativeConfig(nodes=3, rounds=1))
    with torch.no_grad():
        state, _ = owner.remember_texts(['A child carries a book.'])
    scope = {'goal': 'goal-id', 'source': 'observed-fixture', 'weights': 'predictor-id', 'events': 'event-chain'}
    return state, scope, protect_state(state, scope)


def test_actual_retained_coordinates_recover_exactly_after_single_qubit_error():
    state, scope, record = fixture()
    record['code'] = record['code'] @ pauli_word('IIYII').T
    # A stated scalar-mass perturbation stays inside the same QWZ intervals.
    record['topology'] += .2
    recovered, audit = recover_state(record, scope=scope)
    assert all(torch.equal(recovered[k], state[k]) for k in state)
    assert audit['exact_bytes_verified']
    for mass in (-1.2, -.8, .8, 1.2):
        # Occupied lower band and the ordered (kx,ky) plaquette convention.
        assert qwz_chern(mass)['integer'] == (-1 if mass < 0 else 1)
    assert record['storage']['code_bytes'] == 512*record['storage']['raw_bytes']


def test_two_known_erasures_and_unqualified_errors_are_distinguished():
    state, scope, record = fixture()
    damaged = copy.deepcopy(record)
    damaged['code'] = damaged['code'] @ pauli_word('XYIII').T
    recovered, _ = recover_state(damaged, scope=scope, erasures=(0, 1))
    assert all(torch.equal(recovered[k], state[k]) for k in state)
    with pytest.raises(ValueError):
        recover_state(damaged, scope=scope)
    damaged['topology'][0, 0] = 0
    with pytest.raises(ValueError, match='phase intervals'):
        recover_state(damaged, scope=scope, erasures=(0, 1))


def test_stale_predictor_and_changed_metadata_are_rejected_before_decode():
    state, scope, record = fixture()
    with pytest.raises(ValueError, match='stale'):
        recover_state(record, scope={**scope, 'weights': 'next-predictor'})
    record['metadata']['layout'][0]['bytes'] += 1
    with pytest.raises(ValueError, match='Changed storage'):
        recover_state(record, scope=scope)
    state['fast'][0, 0, 0] = float('inf')
    with pytest.raises(ValueError, match='Finite supported'):
        protect_state(state, scope)
