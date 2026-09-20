"""Mathematical contracts for the new research, including counterexamples."""
import torch

from sera_field.clifford_sheaf import (geometric_product, reverse, clifford_rotor, lift_rotation,
                                     coboundary, sheaf_laplacian, sheaf_action, sheaf_gradient, typed_source)
from sera_field.gauge import adjoint_rotations
from sera_field.model import weight_hash
from sera_field.scfe_owner import ScfeOwner

torch.set_num_threads(1)


def test_clifford_basis_metric_anticommutation_and_associativity():
    basis = torch.eye(8, dtype=torch.float64)
    for i in (1, 2, 4):
        torch.testing.assert_close(geometric_product(basis[i], basis[i]), basis[0])
        for j in (1, 2, 4):
            if i != j:
                torch.testing.assert_close(geometric_product(basis[i], basis[j]), -geometric_product(basis[j], basis[i]))
    torch.manual_seed(9004)
    a, b, c = torch.randn(3, 8, dtype=torch.float64)
    torch.testing.assert_close(geometric_product(geometric_product(a,b),c), geometric_product(a,geometric_product(b,c)))


def test_rotor_sandwich_matches_induced_grade_preserving_transport():
    torch.manual_seed(9005)
    coordinates = torch.randn(5, 3, dtype=torch.float64)
    rotor = clifford_rotor(coordinates)
    a, b = torch.randn(2, 5, 8, dtype=torch.float64)
    matrix = lift_rotation(adjoint_rotations(coordinates))
    transformed = geometric_product(geometric_product(rotor, a), reverse(rotor))
    torch.testing.assert_close(transformed, torch.einsum('nij,nj->ni', matrix, a), rtol=1e-10, atol=1e-10)
    mapped_product = torch.einsum('nij,nj->ni', matrix, geometric_product(a,b))
    torch.testing.assert_close(mapped_product, geometric_product(torch.einsum('nij,nj->ni',matrix,a),
                                                                  torch.einsum('nij,nj->ni',matrix,b)))
    grades = [i.bit_count() for i in range(8)]
    for i in range(8):
        for j in range(8):
            if grades[i] != grades[j]:
                assert not matrix[:, i, j].any()


def test_action_gradient_is_actual_coboundary_adjoint_and_phase_derivative():
    torch.manual_seed(9006)
    state = torch.randn(2, 5, 8, dtype=torch.float64, requires_grad=True)*.2
    source = torch.randn_like(state)
    restrictions = lift_rotation(adjoint_rotations(torch.randn(5,3,dtype=torch.float64)))
    prior = torch.zeros(5,8,dtype=torch.float64)
    energy = sheaf_action(state,source,restrictions,prior,.5,.15)
    gradient, = torch.autograd.grad(energy.sum(), state)
    torch.testing.assert_close(gradient, sheaf_gradient(state,source,restrictions,prior,.5,.15), rtol=1e-10,atol=1e-10)
    assert (sheaf_action(state-.1*gradient,source,restrictions,prior,.5,.15) < energy).all()
    laplacian = sheaf_laplacian(state,restrictions)
    torch.testing.assert_close((state*laplacian).sum((-1,-2)), coboundary(state,restrictions).square().sum((-1,-2)))


def test_local_frame_covariance_of_sheaf_laplacian_and_typed_lift():
    torch.manual_seed(9007)
    r = lift_rotation(adjoint_rotations(torch.randn(5,3,dtype=torch.float64)))
    frames = lift_rotation(adjoint_rotations(torch.randn(5,3,dtype=torch.float64)))
    state = torch.randn(2,5,8,dtype=torch.float64)
    transformed_r = frames.roll(-1,0) @ r @ frames.transpose(-1,-2)
    transform = lambda x: torch.einsum('nij,bnj->bni',frames,x)
    torch.testing.assert_close(sheaf_laplacian(transform(state),transformed_r), transform(sheaf_laplacian(state,r)))
    vectors = state[..., [1,2,4]]
    mapped_vectors = transform(state)[..., [1,2,4]]
    torch.testing.assert_close(typed_source(mapped_vectors,transformed_r), transform(typed_source(vectors,r)))


def test_paper_arbitrary_so8_is_not_a_clifford_rotor_action():
    torch.manual_seed(9008)
    raw = torch.randn(8,8,dtype=torch.float64)
    matrix = torch.matrix_exp(.1*(raw-raw.T))
    scalar = torch.eye(8,dtype=torch.float64)[0]
    assert (matrix@scalar)[1:].abs().sum() > .01
    # A geometric algebra automorphism preserves the multiplicative scalar unit.
    assert not torch.allclose(matrix@scalar, scalar)


def test_real_owner_learns_through_new_field_and_imagination_preserves_weights():
    torch.manual_seed(1103)
    owner = ScfeOwner(width=12)
    before = weight_hash(owner)
    scores = owner.rank(['Where is a flower?'], [['The flower is by the wall.', 'A bird flies.']])
    assert weight_hash(owner) == before
    scores[0,0].backward()
    assert owner.field.links.grad.abs().sum() > 0
    assert owner.field.raw_condensation.grad.abs().sum() > 0
    assert owner.words.weight.grad.abs().sum() > 0
