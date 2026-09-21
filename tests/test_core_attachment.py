import copy

import torch

from sera_field.core_owner import CoreOwner
from sera_field.native_owner import NativeConfig


def test_actual_attachment_preserves_old_sections_and_answers_before_learning():
    torch.manual_seed(22025)
    owner = CoreOwner(NativeConfig(nodes=3, rounds=1)).double()
    texts, query = ['A person holds a book.'], ['Someone is reading.']
    old_parameters = copy.deepcopy(owner.state_dict())
    with torch.no_grad():
        old_state, _ = owner.remember_texts(texts)
        before = owner.semantic(texts, query)
    owner.install_extension(4)
    with torch.no_grad():
        new_state, _ = owner.remember_texts(texts)
        after = owner.semantic(texts, query)
    for name in old_parameters:
        assert torch.equal(old_parameters[name], owner.state_dict()[name]), name
    for name in old_state:
        if name == 'reservoir':
            # Relaxation of newly written free coordinates has additional
            # accounted loss; preserving old answers must not erase that cost.
            assert bool((new_state[name] >= old_state[name]).all())
            continue
        assert torch.allclose(old_state[name], new_state[name], atol=5e-14, rtol=0), name
    assert torch.allclose(before, after, atol=5e-14, rtol=0)
    chart = owner.core.attachment()
    actual = owner.core.attached_section(new_state)
    assert chart.enlarged.dimensions == (8, 8, 8, 5)
    old, free, disagreement = chart.decode(actual)
    assert torch.allclose(old, new_state['q'].flatten(1), atol=1e-15, rtol=0)
    assert torch.allclose(free, new_state['extension'], atol=1e-15, rtol=0)
    assert torch.allclose(disagreement, new_state['disagreement'], atol=1e-15, rtol=0)
    assert torch.allclose(chart.enlarged.coboundary(actual)[..., -1:], disagreement, atol=1e-15, rtol=0)


def test_new_memory_coordinates_and_decoder_receive_gradients_and_reach_old_field():
    torch.manual_seed(22026)
    owner = CoreOwner(NativeConfig(nodes=3, rounds=1)).double(); owner.install_extension(4)
    state, _ = owner.remember_texts(['A child sees the sky.'])
    query = owner.encode_texts(['A person watches.'])
    features = owner.imagine(state, query)
    features.square().sum().backward()
    assert owner.extension_readout.weight.grad.abs().sum() > 0
    # Once the initially preserving decoder is learned, the new input port and
    # energy coupling can participate. This is a fixture, not trained growth.
    owner.zero_grad(set_to_none=True)
    with torch.no_grad(): owner.extension_readout.weight.fill_(.02)
    state, _ = owner.remember_texts(['A child sees the sky.'])
    owner.imagine(state, owner.encode_texts(['A person watches.'])).square().sum().backward()
    assert owner.extension_port.weight.grad.abs().sum() > 0
    assert owner.core.extension_map.weight.grad.abs().sum() > 0
    state = {k: v.detach() for k, v in state.items()}
    source = query.detach()
    before = owner.core.rhs(state, source)[0]['p']
    with torch.no_grad(): owner.core.extension_map.weight.fill_(.1)
    after = owner.core.rhs(state, source)[0]['p']
    assert (after-before).abs().max() > 1e-8
