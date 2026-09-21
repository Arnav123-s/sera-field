from collections import Counter
import copy

from sera_field.balanced_joint_data import counterbalance
from sera_field.joint_data import paired, action_number


def examples():
    return paired([{'id': str(i), 'source_group': str(i), 'premise': 'A person reads.',
                    'hypothesis': 'Someone reads.', 'target': 0} for i in range(16)], 'engineering-balanced-order')


def test_every_family_occurs_in_both_orders_equally():
    rows = counterbalance(examples())
    cells = Counter((r['physics']['teacher_only']['quadratic'], r['text_first']) for r in rows)
    assert cells == Counter({(False, False): 4, (False, True): 4, (True, False): 4, (True, True): 4})


def test_only_chronology_changes_and_original_records_are_preserved():
    original = examples(); saved = copy.deepcopy(original); repaired = counterbalance(original)
    assert original == saved
    for before, after in zip(original, repaired):
        assert {k: v for k, v in before.items() if k != 'text_first'} == {k: v for k, v in after.items() if k != 'text_first'}
        assert action_number(before) == action_number(after)
    assert any(a['text_first'] != b['text_first'] for a, b in zip(original, repaired))
