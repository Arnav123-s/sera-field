"""Regressions found while packaging the frozen study's task interface."""

import json
import sys

import pytest
import torch

from sera_field import cli
from sera_field.model import Dynamics


def test_requested_planning_horizon_reaches_the_returned_control_schedule(monkeypatch, capsys):
    torch.manual_seed(31)
    predictor = Dynamics()
    monkeypatch.setattr(cli, "supervised", lambda: None)
    monkeypatch.setattr(cli, "load_model", lambda _: (predictor, {"step": 0}))
    monkeypatch.setattr(sys, "argv", ["sera-field", "plan", "--checkpoint", "test-only.pt",
                                     "--steps", "4", "--dt", "0.1"])
    cli.main()
    result = json.loads(capsys.readouterr().out)
    assert len(result["controls"][0]) == 4
    assert result["status"] == "model-conditional control proposal"


def test_odd_planning_horizon_is_explicitly_rejected(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["sera-field", "plan", "--steps", "3"])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2


@pytest.mark.parametrize("vector", ["nan,0,0", "inf,1,2"])
def test_invalid_observation_vector_is_rejected_before_loading_a_model(monkeypatch, vector):
    monkeypatch.setattr(sys, "argv", ["sera-field", "imagine", "--force", vector])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
