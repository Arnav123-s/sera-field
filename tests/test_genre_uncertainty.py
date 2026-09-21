"""Check cluster weighting and pairing without opening research final data."""
import numpy as np
import pytest

from scripts.uncertainty_genre017 import align, case_metrics, grouped_replicates


def test_unequal_premise_groups_move_together_with_row_weighting():
    # A has three correct primary rows; B has one incorrect primary row.
    # The comparator is the opposite. Two sampled premise groups can only
    # produce AA, AB/BA, or BB: paired gains are 1, .5, or -1 respectively.
    groups = ['A', 'A', 'A', 'B']
    values = np.zeros((4, 2, 2))
    values[:3, 0, 0] = 1; values[3, 1, 0] = 1
    sampled, count = grouped_replicates(groups, values, np.random.default_rng(171170))
    differences = sampled[:, 0, 0] - sampled[:, 1, 0]
    assert count == 2
    assert set(differences.tolist()) == {-1., .5, 1.}
    assert .45 < np.mean(differences == .5) < .55
    assert np.all(sampled[:, 0, 0] + sampled[:, 1, 0] == 1)


def test_pairing_reorders_by_identity_and_rejects_duplicates_or_changed_truth():
    rows = [dict(id=str(i), source_group=str(i // 2), genre='human', target=i % 3,
                 probability=[.6, .3, .1]) for i in range(4)]
    assert align(rows, list(reversed(rows))) == rows
    metrics = case_metrics(rows)
    assert metrics[:, 0].tolist() == [1., 0., 0., 1.]
    np.testing.assert_allclose(metrics[:, 1], -np.log([.6, .3, .1, .6]))
    with pytest.raises(ValueError, match='distinct'):
        align(rows, [*rows[:3], rows[0]])
    with pytest.raises(ValueError, match='annotation differs'):
        align(rows, [dict(rows[0], target=2), *rows[1:]])
