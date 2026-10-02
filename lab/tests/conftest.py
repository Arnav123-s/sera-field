"""Shared audit fixtures and the runner's explicit slow integration markers."""
import pytest


SMALL_AUDIT_TERMS = (
    ('power', 'position', 0.5), ('power', 'position', 1.5),
    ('drive', 'cos', 1.0), ('drive', 'cos', 2.0),
    ('piece', 'speed', 'abs', 0.0), ('piece', 'speed', 'tanh', 0.3),
    ('product', 'straight', 'straight'), ('pprod', 'straight', 'abs'),
)


def pytest_configure(config):
    config.addinivalue_line('markers', 'slow: separately budgeted slow tests')
    config.addinivalue_line('markers', 'integration: full-universe or end-to-end judge checks')


@pytest.fixture
def audit_policy(monkeypatch):
    from ccops5.core import grammar, truth
    monkeypatch.setattr(grammar, 'SHAPES_POLICY', 'off')
    monkeypatch.setattr(truth, 'AUDIT_FAST', True)
    monkeypatch.setattr(truth, 'AUDIT_WORKERS', 0)


@pytest.fixture
def small_audit_universe(audit_policy, monkeypatch):
    from ccops5.core import grammar, truth
    monkeypatch.setattr(truth, 'UNIVERSE_TERMS', SMALL_AUDIT_TERMS)
    # E1 needs a good in-space member inside a node that lacks the claim.
    # On forward throws, |v| + a zero constant fits drag. Keep |v| alone
    # OUT of the space so the audit must still record/refuse that rival.
    base_space = grammar.space
    witness = grammar.canonical((('piece', 'speed', 'abs', 0.0), ('nothing', 'steady')))

    def small_space(*args, **kwargs):
        families = base_space(*args, **kwargs)
        return families if witness in families else families + [witness]

    monkeypatch.setattr(grammar, 'space', small_space)


@pytest.fixture
def full_audit_universe(audit_policy):
    from ccops5.core import truth
    assert len(truth.universe_terms()) == 867
