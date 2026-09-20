import itertools
import torch
from sera_field.fusion_inquiry import majoranas,projectors,measurement_candidates,LocalInvestigationPolicy


def test_majorana_algebra_complete_measurements_and_braid_branch():
    gamma,charge=projectors();eye=torch.eye(8,dtype=torch.complex128)
    for i,j in itertools.product(range(6),repeat=2):
        assert torch.allclose(gamma[i]@gamma[j]+gamma[j]@gamma[i],2*eye if i==j else eye*0)
    prepared=charge(2,3,1)
    operator=prepared@charge(1,2,1)@charge(0,2,1)@prepared
    expected=(eye-gamma[0]@gamma[1])@prepared/4
    assert torch.allclose(operator,expected,atol=1e-12)
    rows=measurement_candidates(torch.tensor([.4,-.7]))
    assert len(rows)==24 and abs(sum(r['probability'] for r in rows)-1)<1e-12
    probes={tuple(round(x,7) for x in r['probe']) for r in rows if r['probe'] is not None}
    assert len(probes)>2
    # All branches, including non-vacuum ancilla outcomes, remain visible.
    assert {r['outcomes'][2] for r in rows}=={-1,1}


def test_forward_local_score_eligibility_matches_full_autograd():
    torch.manual_seed(1401)
    actor=LocalInvestigationPolicy().double()
    inputs=torch.randn(9,4,dtype=torch.float64)*.2
    sample=torch.tensor([.7,-.4],dtype=torch.float64)
    mean=actor.reference(inputs)
    score=-.5*((sample-mean)/.7).square().sum()
    exact=torch.autograd.grad(score,tuple(actor.parameters()))
    actual_mean,trace=actor.eligibility(inputs,sample)
    assert torch.allclose(actual_mean,mean)
    for (name,_),expected in zip(actor.named_parameters(),exact):
        assert torch.allclose(trace[name],expected,atol=1e-11,rtol=1e-9)


def test_generated_investigation_has_checked_outcomes_and_retains_goal():
    from sera_field.inquiry_owner import InquiryOwner
    from sera_field.inquiry_study import Investigator
    torch.manual_seed(1414)
    owner=InquiryOwner(width=8,nodes=4)
    investigator=Investigator(owner)
    row=investigator.attempt(40,'unit-inquiry-v1')
    assert row['original_goal_returned'] and len(row['events'])==3
    assert row['events'][1]['event']['reason']=='intervention was not performed as assumed'
    assert not row['events'][1]['receipt']['actuation_matched']
    assert all(len(e['branches'])==24 and e['distinct_probes']>2 for e in row['events'])
    assert not investigator.book.pending
