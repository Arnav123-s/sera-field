import json
import pytest
from sera_field.concept_owner import append_session
from sera_field.concept_study import Engine
from sera_field.model import weight_hash
from sera_field.session_cli import solve,retain_receipt,owner_identity


def test_new_task_keeps_original_goal_and_full_evidence(tmp_path):
    owner=Engine('full').owner
    receipt={'source':'independent fixture','kind':'independent_simulation','measured':[0,1,1.]}
    evidence=retain_receipt(tmp_path,receipt)
    assert json.loads((tmp_path/'evidence'/(evidence+'.json')).read_text())==receipt
    goal={'predict':[[0,1]],'name':'original'}
    state=append_session(tmp_path,owner,owner_identity(owner),goal,[receipt['measured']],[evidence])
    question={'predict':[[1,2]],'name':'follow up'}
    result=solve(owner,state,question)
    assert result['original_goal']==goal and result['requested_task']==question
    assert state['original_goal']==goal
    assert result['concept_id']==state['concept']['concept_id']
    with pytest.raises(ValueError):retain_receipt(tmp_path,{'source':'guess','kind':'imagination','measured':[0,1,1]})
    with pytest.raises(ValueError):retain_receipt(tmp_path,{**receipt,'measured':[0,1,float('nan')]})


def test_owner_configuration_is_part_of_session_identity():
    from sera_field.concept_language import extend
    owner=extend(Engine('full').owner)
    tensor_hash=weight_hash(owner);before=owner_identity(owner)
    owner.base_route_scale=0.
    assert weight_hash(owner)==tensor_hash and owner_identity(owner)!=before
