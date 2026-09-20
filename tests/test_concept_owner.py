"""Engineering contracts for acquisition, persistence, and no hidden-state inputs."""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import torch

from sera_field.concept_owner import (continue_owner, acquire, append_session,
                                      inverse_input, numpy_predict, plan, explain)
from sera_field.concept_study import Engine, PARENT
from sera_field.model import weight_hash
from sera_field.study_inquiry import load_selected
from sera_field.records import write_json


def owner():
    parent,_=load_selected(PARENT)
    return continue_owner(parent,'full')


def test_positive_precision_and_observation_credit():
    m=owner()
    x=torch.tensor([[[0.,0.,.2],[0.,1.,1.2],[1.,0.,-.3],[-1.,0.,.7]]])
    state=m.world(x,torch.ones(1,4))
    assert torch.linalg.eigvalsh(state['precision']).min()>0
    loss=(m.consequences(state['coefficients'],torch.tensor([[[.5,.5]]]))-.45).square().mean()
    loss.backward()
    assert any(p.grad is not None and p.grad.abs().sum()>0 for p in m.acquisition.parameters())
    assert all(p.grad is None for n,p in m.named_parameters() if not n.startswith(('acquisition.','meaning.','question_route.')))
    changed=x.clone();changed[:,:,2]*=-1
    revised=m.world(changed,torch.ones(1,4))
    assert not torch.allclose(state['coefficients'],revised['coefficients'])


def test_five_uses_share_immutable_acquired_state():
    m=owner();before=weight_hash(m)
    c=acquire(m,[[0,0,.2],[0,1,1.2],[1,0,-.3],[-1,0,.7]],before,['a','b','c','d'])
    original=json.dumps(c,sort_keys=True)
    predictions=numpy_predict(c['coefficients'],[[0,1],[.5,.2]])
    inv=inverse_input(c['coefficients'],0,1.2)
    proposal=plan(c['coefficients'],[.2,.3])
    answer=explain(m,c,'What happens when speed increases?',np.array([0.,1.],dtype='float32'))
    assert predictions.shape==(3,2) and inv['mean'] is not None
    assert -2<=proposal['input']<=2
    assert answer['concept_id']==c['concept_id']
    json.dumps(answer)
    assert json.dumps(c,sort_keys=True)==original and weight_hash(m)==before


def test_persistent_revisions_duplicate_and_wrong_goal_rejected(tmp_path):
    m=owner();h=weight_hash(m)
    first=append_session(tmp_path,m,h,'reach the endpoint',[[0,0,.2]],['observed-a'])
    pointer=json.loads((tmp_path/'CURRENT.json').read_text())['sha256']
    second=append_session(tmp_path,m,h,'reach the endpoint',[[0,1,1.2]],['observed-b'],pointer)
    assert first['concept']['concept_id']!=second['concept']['concept_id']
    assert (tmp_path/(pointer+'.json')).exists()
    latest=json.loads((tmp_path/'CURRENT.json').read_text())['sha256']
    with pytest.raises(ValueError):append_session(tmp_path,m,h,'reach the endpoint',[[0,1,1.2]],['observed-b'],latest)
    with pytest.raises(ValueError):append_session(tmp_path,m,h,'other goal',[[0,1,1.2]],['new'],latest)
    with pytest.raises(ValueError):append_session(tmp_path,m,h,'reach the endpoint',[[0,1,1.2]],['new'],pointer)
    restored=json.loads((tmp_path/(latest+'.json')).read_text())
    assert restored==second and not (tmp_path/'WRITE.lock').exists()


def test_no_observation_and_nonfinite_are_not_evidence():
    m=owner()
    with pytest.raises(ValueError):m.world(torch.zeros(1,2,3),torch.zeros(1,2))
    with pytest.raises(ValueError):m.world(torch.full((1,2,3),float('nan')),torch.ones(1,2))
    with pytest.raises(ValueError):acquire(m,[[0,0,1]],'predictor',[])


def test_teaching_retains_old_reading_and_math_exactly():
    e=Engine('diagonal')
    with torch.no_grad():
        read=e.owner.rank(['Which color?'],[['The flower is yellow.','A book is red.']]).clone()
        math=e.owner.math_logits(['There are 2 and 3 objects.'],[['2','3']]).clone()
    before={k:v.clone() for k,v in e.protected.items()}
    e.update(n=4)
    assert all(torch.equal(v,e.owner.state_dict()[k]) for k,v in before.items())
    with torch.no_grad():
        assert torch.equal(read,e.owner.rank(['Which color?'],[['The flower is yellow.','A book is red.']]))
        assert torch.equal(math,e.owner.math_logits(['There are 2 and 3 objects.'],[['2','3']]))


def test_exact_next_update_and_roundtrip_in_fresh_process(tmp_path):
    e=Engine('full');e.update(n=4);revision=e.save(tmp_path/'revisions')
    write_json(tmp_path/'SELECTION.json',{**revision,'step':1,'score':1.})
    loaded,_=load_selected(tmp_path)
    assert weight_hash(loaded)==weight_hash(e.owner)
    expected=e.update(n=4);digest=weight_hash(e.owner)
    result=tmp_path/'next.json'
    script=('from pathlib import Path;from sera_field.concept_study import Engine;'
            'from sera_field.records import write_json;from sera_field.model import weight_hash;'
            'e=Engine("full");e.resume(Path('+repr(str(tmp_path/'revisions'))+'));'
            'r=e.update(n=4);write_json(Path('+repr(str(result))+'),{"step":r,"hash":weight_hash(e.owner)})')
    subprocess.run([sys.executable,'-c',script],check=True,cwd=Path(__file__).resolve().parents[1])
    assert json.loads(result.read_text())=={'step':expected,'hash':digest}
