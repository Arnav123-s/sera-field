import torch

from sera_field.unified_energy import UnifiedEnergy
from sera_field.clifford_sheaf import lift_rotation
from sera_field.gauge import adjoint_rotations


def fixture():
    torch.manual_seed(22022)
    core = UnifiedEnergy(4, 2).double()
    state = {k: .07*torch.randn_like(v) for k, v in core.empty(2).items()}
    logs = state['log_covariance']
    state['log_covariance'] = .5*(logs+logs.transpose(-1, -2))
    source = .1*torch.randn(2, 4, 3, dtype=torch.float64)
    return core, state, source


def test_passive_and_active_continuous_balances_and_conserved_bulk():
    core, state, source = fixture()
    for active in (False, True):
        derivative, evidence = core.rhs(state, source, active=active, create_graph=False)
        assert evidence['energy_balance_residual'].abs().max() < 2e-13
        assert evidence['bulk_mass_rate'].abs().max() < 2e-13
        assert (evidence['dissipation'] >= 0).all()
        assert torch.allclose(derivative['log_covariance'], derivative['log_covariance'].transpose(-1, -2), atol=1e-14, rtol=0)
        if not active:
            assert torch.equal(evidence['active_work'], torch.zeros(2, dtype=torch.float64))


def test_mixed_derivatives_show_reciprocal_boundary_memory_coupling():
    core, state, source = fixture()
    state = {k: v.requires_grad_() for k, v in state.items()}
    energy, _ = core.energy(state, source)
    q_force, memory_force = torch.autograd.grad(energy.sum(), (state['q'], state['fast']), create_graph=True)
    direction_q = torch.randn_like(state['q']); direction_m = torch.randn_like(state['fast'])
    qm = torch.autograd.grad((q_force*direction_q).sum(), state['fast'], retain_graph=True)[0]
    mq = torch.autograd.grad((memory_force*direction_m).sum(), state['q'])[0]
    left = (qm*direction_m).sum(); right = (mq*direction_q).sum()
    assert abs(float(left)) > 1e-5
    assert torch.allclose(left, right, atol=1e-13, rtol=0)


def test_pure_discrete_step_preserves_mass_and_reports_convergence():
    core, state, source = fixture()
    before = {k: v.clone() for k, v in state.items()}
    with torch.no_grad():
        large, large_diagnostic = core.step(state, source, dt=.02, active=False)
        small, small_diagnostic = core.step(state, source, dt=.01, active=False)
    assert all(torch.equal(state[k], v) for k, v in before.items())
    assert large_diagnostic['bulk_mass_change'].abs().max() < 1e-14
    assert small_diagnostic['discrete_balance_defect'].abs().max() < large_diagnostic['discrete_balance_defect'].abs().max()*.3
    assert (large['reservoir'] >= state['reservoir']).all()


def test_step_trains_energy_rates_memory_and_input_together():
    core, state, source = fixture(); source.requires_grad_()
    result, _ = core.step(state, source)
    objective = result['q'].square().sum()+result['fast'].square().sum()+result['bulk'].square().sum()
    objective.backward()
    for parameter in (core.links, core.anchors, core.raw_rates, core.raw_couplings,
                      core.raw_activity, core.action.coefficients, core.action.raw_sigma):
        assert parameter.grad is not None and torch.isfinite(parameter.grad).all()
        assert parameter.grad.abs().sum() > 0
    assert source.grad is not None and source.grad.abs().sum() > 0


def test_whole_energy_respects_local_frame_changes_with_fixed_bulk_coordinates(monkeypatch):
    core, state, source = fixture()
    with torch.no_grad():
        core.prior.copy_(.05*torch.randn_like(core.prior))
        energy, parts = core.energy(state, source)
        transport, anchors = core.geometry()
        frames = adjoint_rotations(.2*torch.randn(4, 3, dtype=torch.float64))
        lifted = lift_rotation(frames)
        vector = lambda x: (frames[None] @ x[..., None]).squeeze(-1)
        changed = {**state, 'q': (lifted[None] @ state['q'][..., None]).squeeze(-1),
                   'p': (lifted[None] @ state['p'][..., None]).squeeze(-1),
                   'log_covariance': frames[None] @ state['log_covariance'] @ frames.transpose(-1, -2)[None],
                   'fast': vector(state['fast']), 'slow': vector(state['slow'])}
        core.prior.copy_((lifted @ core.prior[..., None]).squeeze(-1))
        transformed_transport = frames.roll(-1, 0) @ transport @ frames.transpose(-1, -2)
        monkeypatch.setattr(core, 'geometry', lambda: (transformed_transport, frames @ anchors))
        transformed_energy, transformed_parts = core.energy(changed, vector(source))
        for key in parts:
            assert torch.allclose(parts[key], transformed_parts[key], atol=2e-13, rtol=0), key
        assert torch.allclose(energy, transformed_energy, atol=2e-13, rtol=0)
