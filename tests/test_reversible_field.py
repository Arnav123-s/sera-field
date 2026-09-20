import copy
import pytest
import torch
from sera_field.reversible_field import FullSheafFlow, position, EchoOwner
from sera_field.clifford_sheaf import lift_rotation
from sera_field.gauge import adjoint_rotations


def coordinates():
    g=torch.Generator().manual_seed(7007107)
    rand=lambda *s:torch.randn(*s,generator=g,dtype=torch.float64)
    return [.1*rand(2,4,8),.05*rand(2,4,8),.2*rand(2,4,8),
            lift_rotation(adjoint_rotations(.1*rand(4,3))),.05*rand(4,8),
            torch.tensor(.5,dtype=torch.float64),torch.tensor(.15,dtype=torch.float64)]


def test_complete_canonical_reversal_and_no_mutation():
    x=coordinates(); old=[t.clone() for t in x]
    flow=FullSheafFlow(*x[2:]); initial=flow.initial(*x[:2])
    final=flow.evolve(initial)
    reverse=flow.echo(final,torch.zeros_like(final.q),0.)
    for a,b in zip((initial.q,initial.p,*initial.credit),(reverse.q,reverse.p,*reverse.credit)):
        torch.testing.assert_close(a,b,atol=2e-14,rtol=2e-14)
    for a,b in zip(old,x): torch.testing.assert_close(a,b,atol=0,rtol=0)


def test_all_seven_coordinate_gradients_against_autograd_and_finite_differences():
    x=[t.requires_grad_() for t in coordinates()]
    out=position(*x,backend='autograd')
    expected=torch.autograd.grad(.5*out.square().sum(),x)
    direct=[t.detach().clone().requires_grad_() for t in x]
    output=position(*direct)
    actual=torch.autograd.grad(.5*output.square().sum(),direct)
    for i,(a,b) in enumerate(zip(actual,expected)):
        torch.testing.assert_close(a,b,atol=2e-8,rtol=2e-7)
        direction=torch.linspace(-1,1,x[i].numel(),dtype=torch.float64).reshape_as(x[i])
        if direction.numel()==1: direction=direction+2
        plus=[t.detach().clone() for t in x]; minus=[t.detach().clone() for t in x]
        plus[i]+=1e-5*direction; minus[i]-=1e-5*direction
        finite=(.5*position(*plus,backend='autograd').square().sum()-.5*position(*minus,backend='autograd').square().sum())/2e-5
        torch.testing.assert_close((a*direction).sum(),finite,atol=2e-8,rtol=2e-7)
        assert not a.requires_grad


def test_shared_prior_initial_condition_chain_rule_is_included():
    x=coordinates()
    prior=x[4].requires_grad_(); x[0]=prior.expand_as(x[0])
    a=position(*x).square().sum()
    actual,=torch.autograd.grad(a,prior)
    b=position(*x,backend='autograd').square().sum()
    expected,=torch.autograd.grad(b,prior)
    torch.testing.assert_close(actual,expected,atol=4e-8,rtol=4e-7)


def test_echo_saved_tensor_storage_is_independent_of_step_count():
    def footprint(steps):
        saved=[]
        def pack(t): saved.append(t.numel()*t.element_size()); return t
        x=[t.requires_grad_() for t in coordinates()]
        with torch.autograd.graph.saved_tensors_hooks(pack,lambda t:t):
            position(*x,steps=steps)
        return sum(saved)
    assert footprint(4)==footprint(64)>0


def test_actual_owner_reading_loss_gradients_match_the_exact_control():
    torch.manual_seed(7107)
    echo=EchoOwner(width=8,nodes=4)
    exact=EchoOwner(width=8,nodes=4,backend='autograd')
    exact.load_state_dict(copy.deepcopy(echo.state_dict()))
    for owner in (echo,exact):
        scores=owner.rank(['Which flower?'],[['A yellow flower.','A red book.']])
        torch.nn.functional.cross_entropy(scores,torch.tensor([0])).backward()
    for name in ('field.links','field.prior','field.raw_stiffness','field.raw_condensation','text_boundary.weight','words.weight'):
        a=dict(echo.named_parameters())[name].grad
        b=dict(exact.named_parameters())[name].grad
        assert a is not None and a.norm()>0
        torch.testing.assert_close(a,b,atol=2e-7,rtol=2e-4)


def test_no_core_credit_arm_has_no_field_gradients():
    owner=EchoOwner(width=8,nodes=4,backend='no_core_credit')
    owner.rank(['Which?'],[['a','b']]).sum().backward()
    assert all(p.grad is None for p in owner.field.parameters())
    assert owner.read_score[0].weight.grad is not None


def test_nonfinite_inputs_and_invalid_backends_are_rejected():
    x=coordinates();x[2][0,0,0]=float('nan')
    with pytest.raises(ValueError): position(*x)
    with pytest.raises(ValueError): position(*coordinates(),backend='unknown')
