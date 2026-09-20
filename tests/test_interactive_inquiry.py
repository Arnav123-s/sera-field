import copy
import numpy as np
import pytest
import torch

from sera_field.extension_world import episode
from sera_field.inquiry_owner import InquiryOwner
from sera_field.interactive_inquiry import InquirySession


def setup_session(path):
    torch.manual_seed(1471)
    owner = InquiryOwner(width=8, nodes=4)
    world, a, c, q = episode(8, 'interactive-inquiry-unit-v1')
    source = {'kind': 'independent_simulation', 'id': 'independent-unit-world'}
    scope = {'domain': 'bounded response fixture'}
    session = InquirySession(path, owner, source=source, assumptions=scope)
    session.start({'adaptation': a[:8].tolist(), 'calibration': c.tolist(),
                   'original_goal': {'queries': q[:4].tolist()}})
    return session, world, q[:4]


def reload(session):
    owner = InquiryOwner(width=8, nodes=4)
    result = InquirySession(session.root, owner, source=session.source, assumptions=session.assumptions)
    result.resume()
    return result


def test_pending_local_eligibility_survives_restart_and_mismatch_is_not_rewarded(tmp_path):
    session, world, q = setup_session(tmp_path)
    proposal = session.propose()
    assert len(proposal['branches']) == 24 and session.book.pending
    restored = reload(session)
    assert restored.progress['pending'] == proposal
    for decision in session.book.pending:
        for key, value in session.book.pending[decision]['eligibility'].items():
            assert torch.equal(value, restored.book.pending[decision]['eligibility'][key])
    performed = np.asarray(proposal['requested'], dtype='float32').copy()
    performed[1] *= .7
    measured = world.observe(q[:, 0], q[:, 1])
    request = {'decision': proposal['decision'], 'source': restored.source,
        'measurement_id': 'measurement-1', 'assessment_id': 'assessment-1',
        'performed': performed.tolist(), 'response': float(world.observe(*performed)),
        'goal_measurements': np.column_stack((q, measured)).tolist()}
    result = restored.observe(request)
    assert not result['performed_measurement']['credit']['accepted']
    assert result['performed_measurement']['credit']['reason'] == 'intervention was not performed as assumed'
    assert not restored.book.pending and restored.progress['rounds'] == 1
    again = reload(restored)
    assert again.answer() == restored.answer()
    assert again.progress['original_goal'] == session.progress['original_goal']
    again.propose()
    request['decision'] = again.progress['pending']['decision']
    with pytest.raises(ValueError, match='New independently'):
        again.observe(request)


def test_outcome_rows_must_match_preserved_original_goal_and_failure_does_not_commit(tmp_path):
    session, world, q = setup_session(tmp_path)
    proposal = session.propose(); parent = session.parent
    altered = q.copy(); altered[0, 0] += .01
    request = {'decision': proposal['decision'], 'source': session.source,
        'measurement_id': 'measurement-1', 'assessment_id': 'assessment-1',
        'performed': proposal['requested'], 'response': 0.,
        'goal_measurements': np.column_stack((altered, np.zeros(len(q)))).tolist()}
    with pytest.raises(ValueError, match='correspond exactly'):
        session.observe(request)
    restored = reload(session)
    assert restored.parent == parent and restored.progress['pending'] == proposal
