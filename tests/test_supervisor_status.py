import pytest

from scripts import supervise


def access_error(code):
    result = PermissionError('simulated file-sharing conflict')
    result.winerror = code
    return result


def fake_clock(monkeypatch):
    now = [0.]
    monkeypatch.setattr(supervise.time, 'monotonic', lambda: now[0])
    monkeypatch.setattr(supervise.time, 'sleep', lambda delay: now.__setitem__(0, now[0] + delay))
    return now


def test_transient_status_replacement_does_not_abort_a_worker(monkeypatch, tmp_path):
    calls = []; fake_clock(monkeypatch)
    real_write = supervise.write_json
    def transient(path, state):
        calls.append(str(path))
        if len(calls) <= 2: raise access_error(5)
        real_write(path, state)
    monkeypatch.setattr(supervise, 'write_json', transient)
    state = {'status': 'RUNNING', 'memory_limit_bytes': 2147483648, 'numerical_threads': 1}
    destination = tmp_path / 'state.json'
    supervise.write_status(destination, state)
    assert len(calls) == 3 and state['status_write_retry_count'] == 2
    assert destination.exists() and state['status'] == 'RUNNING'
    assert state['memory_limit_bytes'] == 2147483648 and state['numerical_threads'] == 1


def test_persistent_sharing_error_has_a_bounded_retry(monkeypatch, tmp_path):
    now = fake_clock(monkeypatch)
    def unavailable(path, state): raise access_error(32)
    monkeypatch.setattr(supervise, 'write_json', unavailable)
    state = {}
    with pytest.raises(PermissionError): supervise.write_status(tmp_path / 'state.json', state, timeout=.2)
    assert .2 <= now[0] < .3 and state['status_write_retry_count'] <= 5


def test_unrelated_permission_errors_are_not_retried(monkeypatch, tmp_path):
    now = fake_clock(monkeypatch)
    def unavailable(path, state): raise access_error(123)
    monkeypatch.setattr(supervise, 'write_json', unavailable)
    with pytest.raises(PermissionError): supervise.write_status(tmp_path / 'state.json', {})
    assert now[0] == 0
