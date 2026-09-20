import copy
from dataclasses import replace

import numpy as np
import pytest
import torch

from sera_field.gauge import (conjugate, decode, encode, group_from_coordinates,
                              random_su2, reframe, trace_inner, transport, wilson_loop)
from sera_field.investigation import CreditBook, Evidence, choose_probe
from sera_field.model import Dynamics, Refinement, features, parameters, weight_hash
from sera_field.observatory import independent_outcome, observations
from sera_field.tasks import Situation, imagine, infer_mass, rollout


torch.set_num_threads(1)


def test_pauli_trace_is_classical_inner_product():
    g = torch.Generator().manual_seed(2101)
    x, y = torch.randn(2, 64, 3, generator=g, dtype=torch.float64)
    torch.testing.assert_close(trace_inner(encode(x), encode(y)), (x * y).sum(-1))
    torch.testing.assert_close(decode(encode(x)), x)


def test_independent_local_frames_transport_consistently():
    g = torch.Generator().manual_seed(2102)
    x = torch.randn(64, 3, generator=g, dtype=torch.float64)
    root, local = random_su2(64, g), random_su2(64, g)
    link, field = reframe(root, local, x)
    torch.testing.assert_close(transport(link, field), conjugate(root, encode(x)))
    torch.testing.assert_close(root @ root.mH, torch.eye(2, dtype=torch.complex128).expand(64, 2, 2))


def test_covariant_network_rotates_its_predictions():
    torch.manual_seed(2103)
    model = Dynamics().double()
    v, f = torch.randn(2, 32, 3, dtype=torch.float64)
    m = torch.rand(32, 1, dtype=torch.float64) + .8
    rotations = random_su2(32, torch.Generator().manual_seed(2))
    vr, fr = decode(conjugate(rotations, encode(v))), decode(conjugate(rotations, encode(f)))
    torch.testing.assert_close(model(vr, fr, m), decode(conjugate(rotations, encode(model(v, f, m)))),
                               rtol=1e-7, atol=1e-7)


def test_native_and_compiled_features_agree():
    torch.manual_seed(2104)
    v, f = torch.randn(2, 32, 3)
    m = torch.rand(32, 1) + .8
    torch.testing.assert_close(features(v, f, m), features(v, f, m, matrix_backend=False))


def test_matched_base_parameters_and_actual_gradients():
    counts = [parameters(Dynamics(kind))["total"] for kind in ("field", "scrambled", "dense", "invariant")]
    assert len(set(counts)) == 1
    model = Dynamics()
    v, f, m = torch.randn(8, 3), torch.randn(8, 3), torch.ones(8, 1)
    model(v, f, m).square().mean().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())


def test_expansion_preserves_function_even_after_nonzero_residual():
    torch.manual_seed(2105)
    model = Refinement(Dynamics())
    torch.nn.init.normal_(model.residual.readout.weight, std=.05)
    expanded = model.expanded()
    v, f, m, ctx = torch.randn(8, 3), torch.randn(8, 3), torch.ones(8, 1), torch.randn(8, 3)
    torch.testing.assert_close(model(v, f, m, ctx), expanded(v, f, m, ctx), atol=1e-7, rtol=1e-6)
    assert parameters(expanded)["total"] > parameters(model)["total"]


def test_imagination_does_not_write_into_fact_or_weights():
    model = Dynamics()
    fact = Situation((0., 0., 0.), (1., 0., 0.), (2., 0., 0.), 2.)
    identity, before = fact.identity(), weight_hash(model)
    branch = fact.branch(mass=1.)
    result = imagine(model, branch, steps=2)
    assert fact.mass == 2 and fact.identity() == identity
    assert branch.status == "hypothetical" and result["status"] == "model-conditional"
    assert before == weight_hash(model)


@pytest.mark.parametrize("mass", [0., -1., float("nan"), float("inf")])
def test_invalid_mass_is_rejected(mass):
    with pytest.raises(ValueError):
        Situation((0., 0., 0.), (1., 0., 0.), (2., 0., 0.), mass)


def test_unidentified_inverse_keeps_equivalence_class():
    m = Dynamics()
    result = infer_mass(m, torch.ones(1, 3), torch.ones(1, 3), torch.ones(1, 3), force_known=False)
    assert result["status"] == "equivalence-class"


def test_observation_targets_come_from_coordinates():
    data = observations(128, 321)
    torch.testing.assert_close(data["a"], data["f"] / data["m"], atol=2e-6, rtol=2e-6)
    other = observations(128, 322)
    assert data["identity"] != other["identity"]


class Oracle(torch.nn.Module):
    def forward(self, v, f, m):
        return f / m


def test_learned_integrator_against_independent_solver():
    x = torch.tensor([[.2, -.3, 1.]], dtype=torch.float64)
    v = torch.tensor([[.4, .8, -.2]], dtype=torch.float64)
    f = torch.ones(1, 20, 3, dtype=torch.float64)
    m = torch.tensor([[2.]], dtype=torch.float64)
    predicted_x, predicted_v = rollout(Oracle(), x, v, f, m)
    actual = independent_outcome(x[0].numpy(), v[0].numpy(), f[0].numpy(), 2.)
    np.testing.assert_allclose(predicted_x[0].numpy(), actual["states"][:, :3], atol=1e-9)
    np.testing.assert_allclose(predicted_v[0].numpy(), actual["states"][:, 3:], atol=1e-9)


def test_credit_is_independent_scoped_and_nonrepeatable():
    credit = CreditBook()
    evidence = Evidence("observation-1", "goal", "decision-1", "old", "new", "DOP853-observation",
                        True, .5, .1, (1., 0., 0.), (1., 0., 0.))
    for invalid in (replace(evidence, observed=False), replace(evidence, predictor_after="stale"),
                    replace(evidence, goal="other"), replace(evidence, actual_force=(.5, 0., 0.))):
        assert not credit.award(invalid, current_predictor="new", original_goal="goal")["awarded"]
    assert credit.award(evidence, current_predictor="new", original_goal="goal")["credit"] == .4
    assert not credit.award(evidence, current_predictor="new", original_goal="goal")["awarded"]


def test_prediction_aliases_do_not_create_diversity():
    model = Dynamics()
    probe = choose_probe([model, copy.deepcopy(model)], torch.ones(1, 3), torch.ones(1, 1), torch.eye(3))
    assert probe["distinct_predictions"] == 1
    assert probe["disagreement"] == 0


def test_persistent_group_weights_are_su2():
    model = Dynamics()
    for coordinates in (model.net.links_in, model.net.links_out):
        group = group_from_coordinates(coordinates)
        identity = torch.eye(2, dtype=torch.complex128).expand_as(group)
        torch.testing.assert_close(group @ group.mH, identity, rtol=1e-6, atol=1e-6)
        torch.testing.assert_close(torch.linalg.det(group), torch.ones_like(group[..., 0, 0]),
                                   rtol=1e-6, atol=1e-6)


def test_wilson_loop_survives_independent_node_gauges():
    g = torch.Generator().manual_seed(442)
    u1, u2, u3, u4 = [random_su2(16, g) for _ in range(4)]
    a, b, c, d = [random_su2(16, g) for _ in range(4)]
    before = wilson_loop(u1, u2, u3, u4)
    after = wilson_loop(a @ u1 @ b.mH, c @ u2 @ b.mH,
                        c @ u3 @ d.mH, a @ u4 @ d.mH)
    torch.testing.assert_close(before, after)


def test_first_update_changes_newly_initialized_connection_weights():
    torch.manual_seed(908)
    model = Dynamics()
    before = model.net.links_in.detach().clone()
    data = observations(32, 125)
    optimizer = torch.optim.Adam(model.parameters(), lr=.002)
    loss = (model(data["v"], data["f"], data["m"]) - data["a"]).square().mean()
    loss.backward()
    optimizer.step()
    assert not torch.equal(before, model.net.links_in)


def test_checkpoint_reloads_weights_and_optimizer_exactly(tmp_path, monkeypatch):
    from sera_field.training import load_model, save_checkpoint
    torch.manual_seed(909)
    model = Dynamics()
    optimizer = torch.optim.Adam(model.parameters(), lr=.002)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, 10)
    generator = torch.Generator().manual_seed(21)
    import sera_field.training as training
    monkeypatch.setattr(training, 'ROOT', tmp_path)
    output = tmp_path / 'fresh' / 'nested' / 'checkpoint-contract.pt'
    assert not output.parent.exists()
    save_checkpoint(output, model, optimizer, scheduler, generator, 0, {"origin": "random initialization"})
    restored, saved = load_model(output)
    assert weight_hash(model) == weight_hash(restored)
    assert torch.equal(saved["sampler_rng"], generator.get_state())


def test_haar_rotation_sampler_has_no_forced_first_axis_sign():
    from sera_field.observatory import proper_rotations
    rotations = proper_rotations(np.random.default_rng(287), 4096, haar=True)
    np.testing.assert_allclose(rotations @ rotations.transpose(0, 2, 1),
                               np.broadcast_to(np.eye(3), rotations.shape), atol=2e-14)
    np.testing.assert_allclose(np.linalg.det(rotations), 1., atol=2e-14)
    assert abs(rotations[:, 0, 0].mean()) < .035
    assert .46 < (rotations[:, 0, 0] > 0).mean() < .54


def test_original_training_identity_survives_sampling_extension():
    data = observations(8192, 19092026)
    assert data["identity"] == "ed7522821c90bcb8c31a008eebf1f6e2cb410b28699684e5642efe5ddaed5f9b"


def test_compatible_measured_context_returns_exact_retained_field():
    from sera_field.model import QualifiedOwner
    torch.manual_seed(710)
    successor = Refinement(Dynamics())
    torch.nn.init.normal_(successor.residual.readout.weight, std=.2)
    model = QualifiedOwner(successor, .001)
    data = observations(32, 104)
    old = model.base(data["v"], data["f"], data["m"])
    gated = model(data["v"], data["f"], data["m"], torch.zeros(32, 3))
    assert torch.equal(old, gated)


def test_support_conditioning_never_reads_query_outcome():
    from sera_field.observatory import context_episodes
    from sera_field.training import predict
    torch.manual_seed(11)
    model = Refinement(Dynamics())
    torch.nn.init.normal_(model.residual.readout.weight, std=.05)
    data = context_episodes(16, 443)
    first, _ = predict(model, data)
    altered = {k: v.clone() if isinstance(v, torch.Tensor) else v for k, v in data.items()}
    altered["a"][:, -1] = 1000 * torch.randn_like(altered["a"][:, -1])
    second, _ = predict(model, altered)
    assert torch.equal(first, second)


def test_covariance_owner_loads_and_uses_its_calibration():
    from sera_field.model import CalibratedOwner, construct
    model = CalibratedOwner(Refinement(Dynamics()), 2., [0., 0., 0.], torch.eye(3))
    restored = construct(model.specification())
    restored.load_state_dict(model.state_dict())
    assert weight_hash(model) == weight_hash(restored)
    data = observations(32, 405)
    expected = model.base(data["v"], data["f"], data["m"])
    actual = model(data["v"], data["f"], data["m"], torch.zeros(32, 3))
    assert torch.equal(actual, expected)
