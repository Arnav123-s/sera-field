import pytest
import torch

from sera_field.history_owner import extend_history
from sera_field.history_session import HistorySession, checked_loss
from sera_field.semantic_owner import SemanticOwner


def fixture(tmp_path):
    torch.manual_seed(16120)
    owner = extend_history(SemanticOwner(width=8, nodes=4))
    source = {'kind': 'human_assessment', 'id': 'unit-fixture', 'sha256': 'unit-only'}
    session = HistorySession(tmp_path, owner, source=source, assumptions={'scope': 'unit fixture, not research evidence'})
    goal = {'id': 'query', 'source_group': 'query-group', 'premise': 'A reader holds a book.',
            'hypothesis': 'Someone holds an object.'}
    supports = [{'id': str(i), 'source_group': str(i), 'target': i % 3,
        'premise': 'A person carries a book.', 'hypothesis': 'Someone carries something.'} for i in range(4)]
    return session, source, goal, supports


def test_query_answer_withheld_mismatched_proposal_preserved_and_no_repeat_credit(tmp_path):
    session, source, goal, supports = fixture(tmp_path)
    with pytest.raises(ValueError, match='answer withheld'):
        session.start({**goal, 'target': 0})
    initial = session.start(goal); proposal = session.propose(supports)
    resumed, _, _, _ = fixture(tmp_path); resumed.resume()
    assert resumed.progress['pending']['proposal'] == proposal['proposal']
    result = resumed.assess({'query_id': goal['id'], 'source': source, 'target': 0,
        'evidence_id': 'unit-evidence', 'assessment_id': 'unit-assessment', 'performed_proposal': 'different'})
    assert not result['credit']['accepted'] and result['credit']['reward'] == 0
    assert result['returned_answer']['original_goal'] == initial['original_goal']
    assert not result['returned_answer']['retained_history']
    final, _, _, _ = fixture(tmp_path); final.resume()
    assert final.answer() == result['returned_answer']
    assert len(final.progress['events']) == 1
    with pytest.raises(ValueError, match='previous attempt'):
        final.assess({})
    with pytest.raises(ValueError, match='revealed query'):
        final.propose(supports)


def test_assessor_requires_finite_external_labels_and_distribution():
    assert checked_loss([.5, .25, .25], 0) == pytest.approx(.6931471805599453)
    with pytest.raises(ValueError): checked_loss([1., -1., 1.], 0)
    with pytest.raises(ValueError): checked_loss([.5, .25, .25], 3)
