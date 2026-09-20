"""Engineering contracts only. Passing is not a trained capability result."""

import copy
from dataclasses import replace

import pytest
import torch

from sera_field.credit_bridge import CheckedOutcome, CreditBridge
from sera_field.gauge import decode, encode, conjugate, random_su2, group_from_coordinates, adjoint_rotations
from sera_field.model import weight_hash
from sera_field.situation_core import (Situation, SituationOwner, token_bytes, boundary_energy,
                                       boundary_step, loop_feature)

torch.set_num_threads(1)


def inputs():
    return (token_bytes(["A flower moves in the breeze."], 64), torch.arange(8.).reshape(1, 8) / 8,
            torch.ones(1, 8), torch.eye(8)[:3][None])


def owner():
    torch.manual_seed(8001)
    return SituationOwner()


def bridge(model=None):
    return CreditBridge(model or owner(), learning_rate=.1, verifier_hashes=["v" * 64], source_hashes=["s" * 64])


def decide(book, name="d1"):
    result = book.owner(*inputs())
    book.record_decision(decision=name, goal="g1", logits=result["logits"][0], choice=1,
                         predictor="predictor-committed-before-evidence", assumptions_id="scope1")
    return CheckedOutcome("g1", name, weight_hash(book.owner), "predictor-committed-before-evidence",
                          "e1", "s" * 64, "v" * 64, "a1", "independent_simulation", "force2", "force2",
                          2., .5, True, "distinct-method-1", "scope1")


def test_boundary_step_is_action_derivative_and_reduces_energy():
    torch.manual_seed(100)
    state = torch.randn(2, 8, 3, dtype=torch.float64, requires_grad=True)
    source = torch.randn_like(state)
    rotation = adjoint_rotations(torch.randn(8, 3, dtype=torch.float64))
    energy = boundary_energy(state, source, rotation, .6)
    gradient, = torch.autograd.grad(energy.sum(), state)
    stepped = boundary_step(state.detach(), source, rotation, .6)
    torch.testing.assert_close(stepped, state.detach() - .1 * gradient, rtol=1e-10, atol=1e-10)
    assert (boundary_energy(stepped, source, rotation, .6) < energy).all()


def test_actual_closed_loop_is_local_frame_invariant():
    generator = torch.Generator().manual_seed(101)
    links = random_su2(8, generator)
    frames = random_su2(8, generator)
    source = torch.randn(2, 8, 3, generator=generator, dtype=torch.float64)
    transformed_links = frames @ links @ frames.roll(-1, 0).mH
    transformed_source = decode(conjugate(frames, encode(source)))
    torch.testing.assert_close(loop_feature(links, source), loop_feature(transformed_links, transformed_source),
                               rtol=1e-9, atol=1e-9)


def test_joint_owner_has_live_loop_and_word_gradients():
    model = owner()
    output = model(*inputs())
    loss = output["prediction"].square().sum() + output["logits"].log_softmax(-1)[0, 1]
    loss.backward()
    assert model.links.grad.abs().sum() > 0
    assert model.bytes.weight.grad.abs().sum() > 0
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())


def test_branch_and_forward_do_not_mutate_fact_or_weights():
    model = owner()
    fact = Situation("original", ("observed-1",), torch.randn(1, 8, 3))
    expected, before = fact.field.clone(), weight_hash(model)
    branch = fact.branch()
    branch.field.add_(2)
    model(*inputs(), previous=branch.field)
    torch.testing.assert_close(fact.field, expected)
    assert fact.goal == branch.goal and branch.hypothetical
    assert before == weight_hash(model)


def test_reward_updates_actual_owner_and_increases_selected_probability():
    book = bridge()
    before = book.owner(*inputs())["logits"].softmax(-1)[0, 1].item()
    evidence = decide(book)
    link_before = book.owner.links.detach().clone()
    event = book.apply(evidence)
    after = book.owner(*inputs())["logits"].softmax(-1)[0, 1].item()
    assert event["accepted"] and event["weights_changed"] and event["reward"] > 0
    assert after > before
    assert not torch.equal(link_before, book.owner.links)


@pytest.mark.parametrize("changes", [
    {"evidence_kind": "imagination"}, {"goal": "different"}, {"predictor": "new"},
    {"verifier_sha256": "unknown"}, {"source_sha256": "unknown"}, {"verified": False},
    {"observed_intervention": "not performed"}, {"after_loss": float("nan")},
    {"assumptions_id": "different"}, {"assessment_id": ""},
])
def test_invalid_credit_does_not_change_weights(changes):
    book = bridge()
    evidence = decide(book)
    before = weight_hash(book.owner)
    assert not book.apply(replace(evidence, **changes))["accepted"]
    assert before == weight_hash(book.owner) and book.updates == 0


def test_renaming_evidence_cannot_credit_same_assessment_again():
    book = bridge()
    evidence = decide(book)
    book.apply(evidence)
    second = decide(book, "d2")
    assert not book.apply(replace(second, evidence_id="renamed"))["accepted"]
    assert book.updates == 1


def test_stale_trace_is_not_applied_after_supervised_learning():
    book = bridge()
    evidence = decide(book)
    with torch.no_grad():
        book.owner.prior.add_(.01)
    assert book.apply(evidence)["reason"] == "stale policy"


def test_resume_preserves_trace_credit_rng_and_exact_next_update(tmp_path):
    book = bridge()
    evidence = decide(book)
    manifest = book.commit(tmp_path, expected_parent=None, progress={"next_record": 27})
    expected_random = torch.rand(4)
    event = book.apply(evidence)
    expected = weight_hash(book.owner)
    restored = bridge()
    state = restored.load_current(tmp_path)
    torch.testing.assert_close(torch.rand(4), expected_random, rtol=0, atol=0)
    assert state["progress"]["next_record"] == 27
    assert restored.apply(evidence) == event
    assert weight_hash(restored.owner) == expected
    restored.commit(tmp_path, expected_parent=manifest["sha256"], progress={"next_record": 28})
    third = bridge()
    third.load_current(tmp_path)
    assert not third.apply(evidence)["accepted"]
    with pytest.raises(ValueError, match="Owner advanced"):
        book.commit(tmp_path, expected_parent=manifest["sha256"], progress={})


def test_eligibility_is_log_probability_derivative():
    book = bridge()
    decide(book)
    parameter = book.owner.policy[-1].weight
    index = (0, 0)
    original = parameter[index].item()
    eps = 1e-3
    results = []
    for offset in [eps, -eps]:
        with torch.no_grad():
            parameter[index] = original + offset
        results.append(book.owner(*inputs())["logits"].log_softmax(-1)[0, 1].item())
    with torch.no_grad():
        parameter[index] = original
    finite_difference = (results[0] - results[1]) / (2 * eps)
    derivative = book.pending["d1"]["eligibility"]["policy.2.weight"][index].item()
    assert finite_difference == pytest.approx(derivative, abs=1e-4)


def test_missing_numeric_values_do_not_leak_into_situation():
    model = owner()
    tokens, numbers, mask, candidates = inputs()
    mask[:, 3] = 0
    first = model(tokens, numbers, mask, candidates)["logits"]
    numbers[:, 3] = 9999
    torch.testing.assert_close(first, model(tokens, numbers, mask, candidates)["logits"])


def test_same_method_on_new_evidence_gets_progress_but_no_novelty_bonus():
    book = bridge()
    first = book.apply(decide(book))
    evidence = decide(book, "d2")
    second = book.apply(replace(evidence, evidence_id="e2", assessment_id="a2"))
    assert first["bonus"] > 0 and second["bonus"] == 0
    assert second["reward"] > 0


def test_stale_decision_can_be_retired_without_reward_or_reused_identity():
    book = bridge()
    evidence = decide(book)
    book.retire("d1", "Prediction changed after a verified supervised lesson")
    assert book.updates == 0 and not book.pending
    assert not book.apply(evidence)["accepted"]
    with pytest.raises(ValueError, match="reused"):
        decide(book)


def test_changing_goal_cannot_renew_novelty_credit():
    book = bridge()
    book.apply(decide(book))
    result = book.owner(*inputs())
    book.record_decision(decision="new-goal-decision", goal="new-goal-name", logits=result["logits"][0],
                         choice=1, predictor="predictor-committed-before-evidence", assumptions_id="scope1")
    evidence = CheckedOutcome("new-goal-name", "new-goal-decision", weight_hash(book.owner),
                              "predictor-committed-before-evidence", "new-evidence", "s" * 64, "v" * 64,
                              "new-assessment", "independent_simulation", "force2", "force2", 2., .5, True,
                              "distinct-method-1", "scope1")
    event = book.apply(evidence)
    assert event["accepted"] and event["reward"] > 0 and event["bonus"] == 0
