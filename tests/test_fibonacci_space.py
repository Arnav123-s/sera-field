import itertools

import pytest
import torch

from sera_field.fibonacci_space import FibonacciSpace, fusion_basis, recouple_right


def test_pentagon_all_four_particle_charges_and_totals():
    source = (((0, 1), 2), 3)
    for charges in itertools.product((0, 1), repeat=4):
        for total in (0, 1):
            dimension = len(fusion_basis(source, charges, total))
            if not dimension:
                continue
            a, first = recouple_right(source, charges, total)
            short_tree, second = recouple_right(a, charges, total)
            b, x = recouple_right(source, charges, total, (0,))
            c, y = recouple_right(b, charges, total)
            long_tree, z = recouple_right(c, charges, total, (1,))
            assert short_tree == long_tree == (0, (1, (2, 3)))
            assert torch.allclose(second @ first, z @ y @ x, atol=2e-14, rtol=0)
            for matrix in (first, second, x, y, z):
                assert torch.allclose(matrix.T @ matrix, torch.eye(dimension, dtype=torch.float64), atol=2e-14, rtol=0)


def test_all_channels_braids_and_far_commutation():
    for count in range(2, 9):
        for total in (0, 1):
            space = FibonacciSpace(count, total)
            eye = torch.eye(space.dimension, dtype=torch.complex128)
            braids = []
            for pair in range(1, count):
                p, q = space.projectors(pair)
                for projector in (p, q):
                    assert torch.allclose(projector @ projector, projector, atol=2e-14, rtol=0)
                    assert torch.equal(projector, projector.mH)
                assert torch.allclose(p+q, eye, atol=2e-14, rtol=0)
                assert torch.allclose(p @ q, torch.zeros_like(eye), atol=2e-14, rtol=0)
                braid = space.braid(pair); braids.append(braid)
                assert torch.allclose(braid.mH @ braid, eye, atol=2e-14, rtol=0)
                assert torch.equal(space.braid(pair, inverse=True), braid.mH)
            for i, a in enumerate(braids):
                for j, b in enumerate(braids):
                    if abs(i-j) == 1:
                        assert torch.allclose(a @ b @ a, b @ a @ b, atol=3e-14, rtol=0)
                    if abs(i-j) > 1:
                        assert torch.allclose(a @ b, b @ a, atol=3e-14, rtol=0)


def test_read_unread_and_absent_measurements_keep_distinct_states():
    space = FibonacciSpace(4, 1)
    vector = torch.tensor([1., 2j, -1.], dtype=torch.complex128)
    vector = vector / vector.norm()
    density = vector[:, None] @ vector.conj()[None]
    original = density.clone(); measured = space.measure(density, 2)
    assert torch.equal(density, original)
    assert torch.equal(measured['no_measurement'], density)
    assert not torch.allclose(measured['unread'], density)
    assert abs(float(sum(b['probability'] for b in measured['outcomes']))-1) < 1e-14
    reconstructed = sum(b['probability'] * b['conditional'] for b in measured['outcomes'])
    assert torch.allclose(reconstructed, measured['unread'], atol=1e-14, rtol=0)
    space.validate_density(measured['unread'])
    for branch in measured['outcomes']:
        space.validate_density(branch['conditional'])


def test_impossible_outcomes_do_not_invent_normalized_states():
    space = FibonacciSpace(2, 0)
    density = torch.ones(1, 1, dtype=torch.complex128)
    branches = space.measure(density, 1)['outcomes']
    assert branches[0]['probability'] == 1
    assert branches[1]['probability'] == 0 and branches[1]['conditional'] is None
    with pytest.raises(ValueError, match='already'):
        space.measure(density*2, 1)
    with pytest.raises(ValueError):
        FibonacciSpace(50)


def test_opposite_handedness_and_recorded_classical_storage():
    right = FibonacciSpace(4, 1); left = FibonacciSpace(4, 1, handedness=-1)
    assert right.dimension == 3
    for pair in (1, 2, 3):
        assert torch.equal(right.braid(pair).conj(), left.braid(pair))
    assert right.specification()['complex128_density_bytes'] == 144
