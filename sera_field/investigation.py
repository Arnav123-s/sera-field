"""Evidence-qualified investigation and non-repeatable progress credit."""

from dataclasses import dataclass
import hashlib
import json
import math

import torch

from .model import weight_hash


@dataclass(frozen=True)
class Evidence:
    identity: str
    goal: str
    decision: str
    predictor_before: str
    predictor_after: str
    source: str
    observed: bool
    before_error: float
    after_error: float
    intended_force: tuple
    actual_force: tuple


class CreditBook:
    def __init__(self):
        self.records = {}

    def award(self, evidence, *, current_predictor, original_goal):
        if evidence.identity in self.records:
            return {"awarded": False, "reason": "evidence already credited"}
        if not evidence.observed or not evidence.source or evidence.source.startswith("imagination"):
            return {"awarded": False, "reason": "independent observed outcome required"}
        if evidence.predictor_after != current_predictor or evidence.goal != original_goal:
            return {"awarded": False, "reason": "stale predictor or wrong original goal"}
        if evidence.predictor_before == evidence.predictor_after:
            return {"awarded": False, "reason": "no predictor revision"}
        if not all(math.isfinite(x) and x >= 0 for x in (evidence.before_error, evidence.after_error)):
            return {"awarded": False, "reason": "invalid independent errors"}
        if evidence.intended_force != evidence.actual_force:
            return {"awarded": False, "reason": "intervention did not execute as assumed"}
        progress = max(0., evidence.before_error - evidence.after_error)
        record = {"awarded": progress > 0, "credit": progress, "evidence": evidence.__dict__}
        self.records[evidence.identity] = record
        return record


def choose_probe(models, velocity, mass, controls, contexts=None):
    """A supplied policy maximizes disagreement of learned consequences, not names."""
    contexts = contexts or [None] * len(models)
    with torch.no_grad():
        predictions = []
        for model, context in zip(models, contexts):
            v = velocity.expand(len(controls), 3)
            m = mass.expand(len(controls), 1)
            pred = model(v, controls, m) if context is None else model(v, controls, m, context)
            predictions.append(pred)
        predictions = torch.stack(predictions)
        disagreement = predictions.var(0, unbiased=False).sum(-1)
        score = disagreement / (1 + .01 * controls.square().sum(-1))
        choice = int(score.argmax())
        # Aliases of numerically indistinguishable predictions count as one outcome family.
        distinct = []
        for pred in predictions[:, choice]:
            if not any(torch.allclose(pred, old, atol=1e-4, rtol=1e-3) for old in distinct):
                distinct.append(pred)
        return {"index": choice, "force": controls[choice].tolist(),
                "disagreement": float(disagreement[choice]), "distinct_predictions": len(distinct),
                "predictions": predictions[:, choice].tolist(),
                "predictors": [weight_hash(m) for m in models], "policy": "fixed disagreement per cost"}


def evidence_identity(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
