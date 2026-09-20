import torch
import numpy as np
from sera_field.stationary_field import stationary,stationary_solution
from sera_field.gauge import adjoint_rotations
from sera_field.learned_extension import gaussian_scale_flow,ExtensionOwner
from sera_field.extension_tasks import serialize_model,predict,inverse


def test_stationary_implicit_gradient_and_steady_state():
    torch.manual_seed(1301)
    x=torch.randn(2,4,3,dtype=torch.float64)*.2
    r=adjoint_rotations(torch.randn(4,3,dtype=torch.float64)*.2)
    c=torch.tensor(1.7,dtype=torch.float64)
    gradients=[]
    for implicit in (False,True):
        a,b,d=[t.clone().requires_grad_() for t in (x,r,c)]
        y=stationary(a,b,d) if implicit else stationary_solution(a,b,d)[0]
        gradients.append(torch.autograd.grad(y.square().sum(),(a,b,d)))
    for a,b in zip(*gradients):assert torch.allclose(a,b,rtol=2e-6,atol=2e-9)


def test_finite_gaussian_flow_integral():
    h=torch.diag(torch.tensor([.3,1.,4.],dtype=torch.float64))
    report=gaussian_scale_flow(h)
    assert np.isclose(report['d_gamma_d_scale'][1],sum(1/(np.array([.3,1,4])+1)))
    assert np.isclose(report['integrated_gaussian_flow'],.5*np.log((np.array([.3,1,4])+4)/(np.array([.3,1,4])+.25)).sum())


def test_acquired_extension_matches_portable_formula_and_separates_calibration():
    torch.manual_seed(1303)
    owner=ExtensionOwner(width=8,nodes=4)
    x=torch.rand(1,24,2)*4-2
    y=x[...,1]-.4*x[...,0]+.6*torch.sin(x[...,0])
    obs=torch.cat((x,y[...,None]),-1)
    model=owner.extend_model(obs,torch.ones(1,24),8)
    q=torch.rand(1,12,2)*4-2
    report={'qualification':'unit fixture'}
    concept=serialize_model(owner,model,report,evidence_ids=[f'e{i}' for i in range(24)],original_goal='fixture')
    assert np.allclose(owner.predict_model(model,q)[0].detach().numpy(),predict(concept,q[0].numpy()),atol=2e-5)
    target=float(predict(concept,[[.2,.4]]).mean())
    solution=inverse(concept,.2,target)
    assert abs(predict(concept,[[.2,solution['input']]]).mean()-target)<1e-6
    # A factual acquisition was not mutated by imagined queries.
    assert concept['original_goal']=='fixture'


def test_source_calibration_does_not_receive_final_targets():
    from sera_field.extension_world import episode
    world,adapt,calib,queries=episode(0,'unit-fixture')
    assert adapt.shape==(24,3) and calib.shape==(8,3) and queries.shape==(16,2)
    assert not set(map(tuple,adapt[:,:2]))&set(map(tuple,calib[:,:2]))


def test_extension_session_keeps_goal_and_exact_function(tmp_path):
    import pytest
    from sera_field.extension_cli import learn,persist,restore,answer
    from sera_field.extension_world import episode
    owner=ExtensionOwner(width=8,nodes=4)
    _,a,c,q=episode(7,'unit-session')
    goal={'queries':q[:2].tolist()}
    request={'original_goal':goal,'adaptation':a.tolist(),'calibration':c.tolist(),
        'source':{'kind':'independent_simulation','id':'unit-fixture'},
        'assumptions':{'scope':'synthetic test fixture'}}
    concept=learn(owner,request);persist(tmp_path,concept)
    restored=restore(tmp_path)
    assert answer(owner,concept,goal)==answer(owner,restored,goal)
    assert answer(owner,restored,{'queries':q[2:3].tolist()})['original_goal']==goal
    with pytest.raises(ValueError):persist(tmp_path,concept)
