import torch

from sera_field.core_echo import canonical
from sera_field.unified_energy import UnifiedEnergy


def fixture():
    torch.manual_seed(22024)
    core = UnifiedEnergy(3, 2).double()
    state = {k: (.05*torch.randn_like(v)).requires_grad_() for k, v in core.empty(2).items()}
    state['log_covariance'] = (.5*(state['log_covariance']+state['log_covariance'].mT)).detach().requires_grad_()
    source = (.1*torch.randn(2, 3, 3, dtype=torch.float64)).requires_grad_()
    return core, state, source


def test_metric_canonical_forward_reverse_preserves_frozen_coordinates():
    core, state, source = fixture()
    with torch.no_grad():
        forward = canonical(core, state, source, dt=.02, steps=3)
        restored = canonical(core, forward, source, dt=-.02, steps=3)
    assert torch.allclose(restored['q'], state['q'], atol=2e-15, rtol=0)
    assert torch.allclose(restored['p'], state['p'], atol=2e-15, rtol=0)
    for name in ('log_covariance', 'fast', 'slow', 'bulk', 'reservoir'):
        assert torch.equal(forward[name], state[name])
    altered = {**state, 'log_covariance': state['log_covariance']+torch.eye(3)*.2}
    changed = canonical(core, altered, source, dt=.02, steps=3)
    assert not torch.allclose(changed['q'], forward['q'], atol=1e-7, rtol=0)


def test_echo_matches_whole_coupled_energy_derivatives_with_intermediate_loss():
    core, state, source = fixture()
    targets = (state['q'], state['p'], state['log_covariance'], state['fast'], state['slow'], state['bulk'],
               source, core.links, core.anchors, core.raw_couplings, core.action.coefficients)
    derivatives = []
    for backend in ('autograd', 'echo'):
        first = canonical(core, state, source, dt=.015, steps=2, backend=backend)
        second = canonical(core, first, source*.8, dt=.01, steps=2, backend=backend)
        loss = first['q'].square().mean()+.3*second['q'].square().sum()+.7*second['p'].square().sum()
        derivatives.append(torch.autograd.grad(loss, targets))
    for exact, echoed in zip(*derivatives):
        assert torch.isfinite(echoed).all()
        assert torch.allclose(exact, echoed, atol=2e-8, rtol=2e-4), (exact-echoed).abs().max()


def test_actual_split_respects_mass_and_reports_its_energy_defect():
    core, state, source = fixture()
    with torch.no_grad():
        single, audit = core.coupled_step(state, source, dt=.02)
        half, _ = core.coupled_step(state, source, dt=.01)
        refined, _ = core.coupled_step(half, source, dt=.01)
        quarter = state
        for _ in range(4): quarter, _ = core.coupled_step(quarter, source, dt=.005)
    for result in (single, refined, quarter):
        assert torch.allclose(result['bulk'].sum((-3, -2)), state['bulk'].sum((-3, -2)), atol=2e-15, rtol=0)
        assert bool((result['reservoir'] >= state['reservoir']).all())
    coarse_error = sum((single[k]-quarter[k]).square().sum() for k in state)
    fine_error = sum((refined[k]-quarter[k]).square().sum() for k in state)
    assert fine_error < coarse_error*.2
    old = core.energy(state, source)[0]+state['reservoir']
    new = core.energy(single, source)[0]+single['reservoir']
    assert torch.allclose(new-old, audit['active_work_integral']+audit['discrete_balance_defect'], atol=1e-15, rtol=0)
