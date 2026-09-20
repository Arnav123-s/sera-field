import torch

from sera_field.meaning_cli import interpret
from sera_field.model import weight_hash
from sera_field.semantic_owner import SemanticOwner


def test_interpretation_preserves_owner_and_returns_all_conditional_branches():
    torch.manual_seed(15150)
    owner = SemanticOwner(width=8, nodes=4)
    before = weight_hash(owner)
    result = interpret(owner, 'A person carries a book.', ['Someone carries something.', 'Nobody carries anything.'])
    assert result['status'] == 'conditional_on_the_supplied_premise'
    assert result['predictor'] == before == weight_hash(owner)
    assert len(result['interpretations']) == 2
    for row in result['interpretations']:
        assert len(row['conditional_branches']) == 3
        assert abs(sum(row['probabilities'].values()) - 1) < 1e-6
