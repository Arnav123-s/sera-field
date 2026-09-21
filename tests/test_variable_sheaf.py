"""Prospective operator identities, not an assessment of learned growth."""
import json
from pathlib import Path

import pytest
import torch

from sera_field.variable_sheaf import CellAttachment, Edge, FiniteSheaf, from_clifford_field


@pytest.fixture
def heterogeneous():
    torch.manual_seed(18118)
    return FiniteSheaf((2, 3, 2), [
        Edge(0, 1, torch.randn(2, 2, dtype=torch.double), torch.randn(2, 3, dtype=torch.double)),
        Edge(1, 2, torch.randn(1, 3, dtype=torch.double), torch.randn(1, 2, dtype=torch.double)),
    ])


def close(a, b):
    torch.testing.assert_close(a, b, atol=1e-10, rtol=1e-9)


def attachment(graph):
    return CellAttachment(graph, 1, torch.tensor([[.4, -.2, .1], [.2, .1, -.3]], dtype=torch.double),
                          torch.tensor([[.1, -.2, .3], [-.3, .2, .1]], dtype=torch.double))


def test_sparse_coboundary_and_adjoint_match_dense(heterogeneous):
    graph = heterogeneous
    state = torch.randn(2, 3, graph.size, dtype=torch.double)
    edge = torch.randn(2, 3, graph.edge_size, dtype=torch.double)
    d = graph.matrix()
    close(graph.coboundary(state), state @ d.T)
    close(graph.adjoint(edge), edge @ d)
    close((graph.coboundary(state) * edge).sum(), (state * graph.adjoint(edge)).sum())
    close(graph.laplacian(state), state @ (d.T @ d))


def test_cell_adds_exact_free_directions_and_preserves_sections(heterogeneous):
    chart = attachment(heterogeneous)
    d, enlarged = heterogeneous.matrix(), chart.enlarged.matrix()
    x = torch.randn(4, heterogeneous.size, dtype=torch.double)
    eta = torch.randn(4, chart.k, dtype=torch.double)
    w = torch.randn(4, chart.r, dtype=torch.double)
    state = chart.encode(x, eta, w)
    old, recovered_eta, recovered_w = chart.decode(state)
    close(old, x); close(recovered_eta, eta); close(recovered_w, w)
    close(chart.enlarged.coboundary(state), torch.cat((heterogeneous.coboundary(x), w), -1))
    assert torch.equal(chart.encode(x)[..., :heterogeneous.size], x)
    old_nullity = heterogeneous.size - int(torch.linalg.matrix_rank(d))
    new_nullity = chart.size - int(torch.linalg.matrix_rank(enlarged))
    assert new_nullity == old_nullity + chart.k
    _, _, vh = torch.linalg.svd(d, full_matrices=True)
    sections = vh[int(torch.linalg.matrix_rank(d)):]
    close(chart.enlarged.coboundary(chart.encode(sections)),
          torch.zeros(len(sections), chart.enlarged.edge_size, dtype=torch.double))
    free_sections = chart.encode(torch.zeros(chart.k, heterogeneous.size, dtype=torch.double), torch.eye(chart.k, dtype=torch.double))
    close(chart.enlarged.coboundary(free_sections),
          torch.zeros(chart.k, chart.enlarged.edge_size, dtype=torch.double))


def test_metric_and_transition_have_independent_dense_check(heterogeneous):
    chart = attachment(heterogeneous)
    t = chart.matrix(); inv = torch.linalg.inv(t); g = inv.T @ inv
    u = torch.randn(5, chart.size, dtype=torch.double)
    close(chart.transform(chart.inverse(u)), u)
    close(chart.transpose(u), u @ t)
    close(chart.inverse_transpose(u), u @ inv)
    close(chart.metric(u), u @ g.T)
    close(chart.inverse_metric(u), u @ torch.linalg.inv(g).T)
    dnew = chart.enlarged.matrix()
    independent_gradient = torch.linalg.solve(g, (u @ (dnew.T @ dnew)).T).T
    close(chart.metric_gradient(u), independent_gradient)
    old, eta, w = chart.decode(u)
    close(chart.metric_gradient(u), chart.transform(torch.cat((heterogeneous.laplacian(old), eta * 0, w), -1)))
    duration = .17
    after = chart.implicit_step(u, duration)
    independent_after = torch.linalg.solve(g + duration * dnew.T @ dnew, (u @ g.T).T).T
    close(after, independent_after)
    assert bool((chart.enlarged.energy(after) <= chart.enlarged.energy(u) + 1e-10).all())
    d = heterogeneous.matrix()
    parent_after = torch.linalg.solve(torch.eye(heterogeneous.size, dtype=torch.double) + duration * d.T @ d, old.T).T
    close(chart.implicit_step(chart.encode(old), duration), chart.encode(parent_after))


def test_state_and_restriction_derivatives_match_finite_differences(heterogeneous):
    chart = attachment(heterogeneous)
    b, a = chart.b.clone().requires_grad_(), chart.a.clone().requires_grad_()
    state = torch.randn(2, chart.size, dtype=torch.double, requires_grad=True)
    assert torch.autograd.gradcheck(
        lambda u, x, y: CellAttachment(heterogeneous, 1, x, y).metric_gradient(u),
        (state, b, a), eps=1e-6, atol=1e-6, rtol=1e-5)


def test_independent_stalk_frames_preserve_residuals_and_energy(heterogeneous):
    graph = heterogeneous
    vertex_frames = [torch.linalg.qr(torch.randn(d, d, dtype=torch.double)).Q for d in graph.dimensions]
    edge_frames = [torch.linalg.qr(torch.randn(d, d, dtype=torch.double)).Q for d in graph.edge_dimensions]
    transformed = FiniteSheaf(graph.dimensions,
        [Edge(e.left, e.right, f @ e.left_map @ vertex_frames[e.left].T,
              f @ e.right_map @ vertex_frames[e.right].T) for e, f in zip(graph.edges, edge_frames)])
    state = torch.randn(6, graph.size, dtype=torch.double)
    changed = torch.cat([piece @ frame.T for piece, frame in zip(state.split(graph.dimensions, -1), vertex_frames)], -1)
    expected = torch.cat([piece @ frame.T for piece, frame in zip(graph.coboundary(state).split(graph.edge_dimensions, -1), edge_frames)], -1)
    close(transformed.coboundary(changed), expected)
    close(transformed.energy(changed), graph.energy(state))


def test_fixed_polynomial_preserves_sections_norm_and_dependency_cone():
    eye = torch.ones(1, 1, dtype=torch.double)
    graph = FiniteSheaf((1,) * 8, [Edge(i, i + 1, eye, eye) for i in range(7)])
    state = torch.randn(8, 8, dtype=torch.double)
    filtered = graph.polynomial(state, [.2, .3, .5])
    assert bool((filtered.norm(dim=-1) <= state.norm(dim=-1) + 1e-10).all())
    close(graph.polynomial(torch.ones(8, dtype=torch.double), [.2, .3, .5]), torch.ones(8, dtype=torch.double))
    operator = graph.polynomial(torch.eye(8, dtype=torch.double), [.2, .3, .5])
    for i in range(8):
        for j in range(8):
            if abs(i - j) > 2:
                assert operator[i, j] == 0
    with pytest.raises(ValueError, match='spectral bound'):
        graph.polynomial(state, [.2, .3, .5], rho=.01)


def test_restart_storage_and_invalid_graphs(heterogeneous):
    chart = attachment(heterogeneous)
    restored = CellAttachment.from_specification(json.loads(json.dumps(chart.specification())))
    assert restored.specification() == chart.specification()
    state = torch.randn(3, chart.size, dtype=torch.double)
    assert torch.equal(restored.implicit_step(state, .11), chart.implicit_step(state, .11))
    assert chart.storage()['new_state_bytes_per_case'] == chart.size * 8
    assert chart.storage()['added_free_scalars'] == 3
    with pytest.raises(ValueError):
        FiniteSheaf((2, 0), heterogeneous.edges)
    with pytest.raises(ValueError):
        FiniteSheaf((2, 2), [Edge(0, 0, torch.eye(2), torch.eye(2))])
    with pytest.raises(ValueError):
        CellAttachment(heterogeneous, 1, chart.b, chart.a[:, :0])
    with pytest.raises(ValueError):
        chart.implicit_step(state, float('nan'))


def test_attachment_uses_actual_owner_maps_without_changing_old_readout():
    from sera_field.clifford_sheaf import coboundary
    from sera_field.model import weight_hash
    from sera_field.semantic_training import load_semantic

    root = Path(__file__).resolve().parents[1]
    owner, _ = load_semantic(root / 'checkpoints/SEMANTIC-015')
    owner.eval(); before = weight_hash(owner)
    with torch.no_grad():
        source = torch.linspace(-.1, .2, 2 * owner.field.nodes * 3).reshape(2, owner.field.nodes, 3)
        state, features = owner.field.imagine(source)
        graph = from_clifford_field(owner.field)
        restrictions = torch.stack([edge.left_map for edge in graph.edges])
        torch.testing.assert_close(graph.coboundary(state.flatten(1)), coboundary(state, restrictions).flatten(1), atol=3e-5, rtol=3e-5)
        chart = CellAttachment(graph, 0, .25 * torch.eye(8), torch.zeros(8, 3))
        enlarged = chart.encode(state.flatten(1))
        recovered, _, _ = chart.decode(enlarged)
        old_logits = owner.semantic_readout(torch.cat((state.flatten(1), features), -1))
        recovered_logits = owner.semantic_readout(torch.cat((recovered, features), -1))
        assert torch.equal(old_logits, recovered_logits)
        assert chart.size == graph.size + 11
        assert chart.storage()['added_free_scalars'] == 3
    assert weight_hash(owner) == before
