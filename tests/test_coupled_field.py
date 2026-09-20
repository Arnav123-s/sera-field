import copy
import numpy as np
import pytest
import torch

from sera_field.condensate import CondensateMemory,relax
from sera_field.spd_sheaf import (congruence,log_lift,covariance_coboundary,
                                   covariance_adjoint,covariance_sequence)
from sera_field.temporal_echo import TimedSheafFlow,timed_positions
from sera_field.clifford_sheaf import lift_rotation
from sera_field.gauge import adjoint_rotations
from sera_field.topological_memory import qwz_chern,encode_density,decode_density


def test_spd_transport_adjoint_and_coordinate_change():
    torch.manual_seed(12001)
    r=adjoint_rotations(torch.randn(4,3,dtype=torch.float64)*.2)
    v=torch.randn(2,4,3,dtype=torch.float64)
    logs=log_lift(v)
    cov=torch.matrix_exp(logs)
    assert torch.all(torch.linalg.eigvalsh(cov)>0)
    assert torch.allclose(cov,torch.eye(3)+v[...,None]*v[...,None,:],atol=2e-12)
    e=torch.randn_like(logs);e=(e+e.transpose(-1,-2))/2
    delta=covariance_coboundary(logs,r)
    assert torch.allclose((delta*e).sum(),(logs*covariance_adjoint(e,r)).sum(),atol=2e-12)
    g=adjoint_rotations(torch.randn(4,3,dtype=torch.float64))
    rr=g.roll(-1,0)@r@g.transpose(-1,-2)
    changed=covariance_coboundary(congruence(g,logs),rr)
    assert torch.allclose(changed,congruence(g.roll(-1,0),delta),atol=2e-12)
    evolved=covariance_sequence(v,r,torch.tensor(.4),frames=4)
    vv=(g@v[...,None]).squeeze(-1)
    assert torch.allclose(covariance_sequence(vv,rr,torch.tensor(.4)),congruence(g,evolved),atol=2e-12)


def test_timed_echo_all_derivatives_and_reversal():
    torch.manual_seed(12002)
    q=torch.randn(2,3,8,dtype=torch.float64)*.08;p=torch.randn_like(q)*.04
    source=torch.randn(4,2,3,8,dtype=torch.float64)*.12
    r=lift_rotation(adjoint_rotations(torch.randn(3,3,dtype=torch.float64)*.1))
    prior=torch.randn(3,8,dtype=torch.float64)*.02
    operands=(q,p,source,r,prior,torch.tensor(.6,dtype=torch.float64),torch.tensor(.1,dtype=torch.float64))
    derivatives=torch.randn_like(source)
    gradients=[]
    for backend in ('autograd','echo'):
        inputs=[x.clone().requires_grad_() for x in operands]
        ys=timed_positions(*inputs,steps=5,backend=backend)
        gradients.append(torch.autograd.grad((ys*derivatives).sum(),inputs))
    for direct,echo in zip(*gradients):
        assert torch.allclose(direct,echo,rtol=.002,atol=.00002),(direct-echo).abs().max()
    flow=TimedSheafFlow(*operands[2:],steps=5)
    _,final=flow.evolve(q,p)
    recovered,_=flow.reverse_with_losses(final,torch.zeros_like(source),0.)
    assert torch.allclose(recovered.q,q,atol=2e-12)
    assert torch.allclose(recovered.p,p,atol=2e-12)


def test_phase_memory_mass_energy_and_charge_codec():
    torch.manual_seed(12003)
    x=.5+.03*torch.randn(3,4,8,3,dtype=torch.float64)
    result,report=relax(x,torch.full_like(x,.5),steps=32)
    assert 0<result.min()<result.max()<1
    assert report['mass_error']<1e-10
    assert all(a<=b+1e-10 for a,b in zip(report['energy_after'],report['energy_before']))
    assert qwz_chern(-1)['integer']==-qwz_chern(1)['integer']
    assert abs(qwz_chern(-1)['integer'])==1
    for m in (-1.4,-.6):assert qwz_chern(m)['integer']==qwz_chern(-1)['integer']
    with pytest.raises(ValueError):qwz_chern(0)
    values=torch.linspace(.1,.9,257,dtype=torch.float64)
    code=encode_density(values)
    assert (decode_density(code)-values).abs().max()<=.8/510+1e-12
    assert torch.equal(decode_density(code),decode_density(code+.25))
    with pytest.raises(ValueError):decode_density(code*0)


def capture_event():
    return {'accepted':True,'outcome':{'goal':'g','decision':'d','predictor':'p','policy_before':'w',
        'evidence_id':'e','assessment_id':'a','source_sha256':'s','verifier_sha256':'v',
        'assumptions_id':'scope','verified':True,'evidence_kind':'independent_simulation',
        'intended_intervention':'i','observed_intervention':'i','before_loss':2.,'after_loss':1.}}


def test_capture_requires_credit_and_returns_through_same_source():
    m=CondensateMemory();source=torch.linspace(-1,1,24).reshape(8,3)
    event=capture_event()
    before=copy.deepcopy(m.state_dict())
    for key,value in [('verified',False),('observed_intervention','wrong'),('evidence_kind','imagination')]:
        bad=copy.deepcopy(event);bad['outcome'][key]=value
        with pytest.raises(ValueError):m.capture(source,bad,predictor='p',decision_policy='w')
    assert torch.equal(m.density,before['density'])
    record=m.capture(source,event,predictor='p',decision_policy='w')
    assert record['codec_max_error']<=.8/510+1e-7
    assert m.recall(source[None]).norm()>0
    with pytest.raises(ValueError):m.capture(source,event,predictor='p',decision_policy='w')
    other=CondensateMemory();other.load_state_dict(m.state_dict())
    assert torch.equal(m.recall(source[None]),other.recall(source[None]))
    assert m.evidence==other.evidence


def test_current_owner_coupled_path_and_parent_retained():
    from sera_field.study_inquiry import load_selected
    from sera_field.study_data import ROOT
    from sera_field.coupled_owner import extend_coupled
    from sera_field.model import weight_hash
    parent,selection=load_selected(ROOT/'checkpoints/CONCEPT-011')
    before=weight_hash(parent);owner=extend_coupled(parent)
    source=torch.randn(2,8,3)*.3
    _,a=owner.field.imagine(source)
    a.sum().backward()
    for name in ('raw_covariance','raw_anchor'):
        gradient=getattr(owner.field,name).grad
        assert gradient is not None and gradient.abs().sum()>0
    owner.field.ablation='no_covariance'
    _,b=owner.field.imagine(source)
    assert not torch.equal(a,b)
    owner.field.ablation=None
    owner.field.memory.capture(source[0],capture_event(),predictor='p',decision_policy='w')
    owner.zero_grad(set_to_none=True)
    _,c=owner.field.imagine(source);c.sum().backward()
    assert owner.field.raw_memory.grad is not None and owner.field.raw_memory.grad.abs()>0
    frozen=weight_hash(owner)
    owner.field.memory_preview=owner.field.memory.propose(source[1])
    owner.field.imagine(source)
    owner.field.memory_preview=None
    assert weight_hash(owner)==frozen
    assert weight_hash(parent)==before==selection['weights']


def test_training_capture_resume_keeps_actual_state(tmp_path):
    from sera_field.coupled_study import CoupledEngine
    from types import SimpleNamespace
    from sera_field.model import weight_hash
    rows=[{'id':f'unit-{i}','question':'Which item is a flower?',
           'options':['A rose is a flower.','A stone is a rock.'],
           'targets':[0],'track':'unit-fixture'} for i in range(4)]
    data=SimpleNamespace(manifest_sha='unit-fixture-v1',train={'reading':rows},
                         dev={'reading':rows},pairs={},dev_pairs={},tracks=[])
    engine=CoupledEngine(data,'coupled')
    engine.update(batch=2)
    # A distinct teaching clock creates a real capture decision. The comparison
    # does not require a positive reward or force a proposal to pass.
    engine.step=32
    event=engine.capture_attempt()
    assert event['original_goal_returned']
    engine.save(tmp_path/'revisions')
    resumed=CoupledEngine(data,'coupled');resumed.resume(tmp_path/'revisions')
    assert weight_hash(resumed.owner)==weight_hash(engine.owner)
    assert resumed.book.used_evidence==engine.book.used_evidence
    assert resumed.owner.field.memory.evidence==engine.owner.field.memory.evidence
    assert resumed.step==engine.step
    assert torch.equal(resumed.owner.field.memory.density,engine.owner.field.memory.density)
