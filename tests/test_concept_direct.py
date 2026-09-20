import torch
from sera_field.concept_language import lexical_features, extend
from sera_field.concept_direct_study import phrases
from sera_field.concept_study import Engine


def test_direct_route_ignores_conflicting_legacy_scores():
    owner=extend(Engine('full').owner)
    owner.base_route_scale=0.
    text=['What follows when input increases?','What follows when speed increases?']
    with torch.no_grad():
        expected=owner.route_logits(text).clone()
        owner.question_route[-1].bias.add_(torch.tensor([1000.,-1000.]))
        assert torch.equal(expected,owner.route_logits(text))
        assert torch.equal(expected,owner.lexical_route(lexical_features(text)))
    assert owner.specification()['base_route_scale']==0.
    assert phrases()['unique_counts']==[388,64,96]
