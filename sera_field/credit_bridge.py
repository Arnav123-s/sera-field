"""Durable delayed policy credit, committed with weights and RNG in one revision.

Score-function eligibility is computed when a decision is made. An independently
checked outcome can later update the actual shared owner. This finite estimator is
not e-prop for a recurrent spiking network and is not curvature-as-credit.
"""

import copy
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import random
import uuid

import numpy as np
import torch

from .model import weight_hash
from .records import sha256, write_json


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class CheckedOutcome:
    goal: str
    decision: str
    policy_before: str
    predictor: str
    evidence_id: str
    source_sha256: str
    verifier_sha256: str
    assessment_id: str
    evidence_kind: str
    intended_intervention: str
    observed_intervention: str
    before_loss: float
    after_loss: float
    verified: bool
    canonical_contribution: str
    assumptions_id: str


class CreditBridge:
    """Single-writer state. The campaign's exclusive numerical lease owns writes.

    Verifier/source allowlists are frozen before training. They establish identity,
    not semantic independence by themselves; verifier implementations and exposure
    are audited separately. No guessed or self-scored outcome qualifies as evidence.
    """
    def __init__(self, owner, *, learning_rate=.01, verifier_hashes=(), source_hashes=()):
        self.owner = owner
        self.optimizer = torch.optim.SGD(owner.parameters(), lr=learning_rate)
        self.verifiers = set(verifier_hashes)
        self.sources = set(source_hashes)
        self.pending = {}
        self.used_decisions = set()
        self.used_evidence = set()
        self.used_assessments = set()
        self.contributions = set()
        self.events = []
        self.updates = 0

    def record_decision(self, *, decision, goal, logits, choice, predictor, assumptions_id):
        if not decision or not goal or not predictor or not assumptions_id:
            raise ValueError("Decision, original goal, predictor and assumptions are mandatory")
        if decision in self.pending or decision in self.used_decisions:
            raise ValueError("Decision identifiers cannot be reused")
        if len(self.pending) >= 32:
            raise ValueError("Resolve or explicitly retire pending decisions before opening more")
        if logits.ndim != 1 or not torch.isfinite(logits).all() or len(logits) < 2:
            raise ValueError("One finite choice distribution required")
        if not 0 <= choice < len(logits):
            raise ValueError("Choice outside supplied candidates")
        log_probability = logits.log_softmax(-1)[choice]
        named = [(n, p) for n, p in self.owner.named_parameters() if p.requires_grad]
        derivatives = torch.autograd.grad(log_probability, [p for _, p in named], allow_unused=True)
        trace = {n: (g.detach().clone() if g is not None else torch.zeros_like(p))
                 for (n, p), g in zip(named, derivatives)}
        if not all(torch.isfinite(g).all() for g in trace.values()):
            raise ValueError("Non-finite eligibility")
        self.pending[decision] = {"goal": goal, "predictor": predictor, "assumptions": assumptions_id,
                                  "policy": weight_hash(self.owner), "choice": choice,
                                  "eligibility": trace, "logits": logits.detach().clone()}

    def apply(self, outcome):
        data = asdict(outcome)
        pending = self.pending.get(outcome.decision)
        assessment = identity([outcome.source_sha256, outcome.assessment_id])
        reason = None
        if pending is None:
            reason = "unknown or consumed decision"
        elif outcome.evidence_id in self.used_evidence or assessment in self.used_assessments:
            reason = "evidence already used"
        elif outcome.evidence_kind not in {"independent_simulation", "measurement", "exact_checker", "human_assessment"}:
            reason = "independent evidence required"
        elif outcome.verifier_sha256 not in self.verifiers or outcome.source_sha256 not in self.sources:
            reason = "unregistered source or verifier"
        elif not outcome.evidence_id or not outcome.assessment_id:
            reason = "missing evidence identity"
        elif (pending["goal"] != outcome.goal or pending["predictor"] != outcome.predictor
              or pending["assumptions"] != outcome.assumptions_id):
            reason = "goal, predictor or scope mismatch"
        elif pending["policy"] != outcome.policy_before or weight_hash(self.owner) != pending["policy"]:
            reason = "stale policy"
        elif outcome.intended_intervention != outcome.observed_intervention:
            reason = "intervention was not performed as assumed"
        elif not outcome.verified or not outcome.canonical_contribution:
            reason = "qualification failed"
        elif not all(math.isfinite(x) and x >= 0 for x in (outcome.before_loss, outcome.after_loss)):
            reason = "invalid assessment loss"
        if reason:
            event = {"decision": outcome.decision, "accepted": False, "reason": reason, "outcome": data}
            self.events.append(event)
            return event
        # Qualification remains bound to the original goal, but a new goal name
        # cannot make an already retained method novel to the learner again.
        key = identity([outcome.assumptions_id, outcome.canonical_contribution])
        progress = (outcome.before_loss - outcome.after_loss) / (1 + outcome.before_loss)
        bonus = .1 * max(0., progress) if key not in self.contributions else 0.
        reward = max(-1., min(1., progress + bonus))
        before = weight_hash(self.owner)
        backup, optimizer_backup = copy.deepcopy(self.owner.state_dict()), copy.deepcopy(self.optimizer.state_dict())
        try:
            self.optimizer.zero_grad(set_to_none=True)
            for name, parameter in self.owner.named_parameters():
                if parameter.requires_grad:
                    parameter.grad = -reward * pending["eligibility"][name].clone()
            torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1., error_if_nonfinite=True)
            self.optimizer.step()
            if not all(torch.isfinite(p).all() for p in self.owner.parameters()):
                raise ValueError("Non-finite update")
        except BaseException:
            self.owner.load_state_dict(backup)
            self.optimizer.load_state_dict(optimizer_backup)
            raise
        after = weight_hash(self.owner)
        self.used_evidence.add(outcome.evidence_id)
        self.used_assessments.add(assessment)
        self.used_decisions.add(outcome.decision)
        if progress > 0:
            self.contributions.add(key)
        del self.pending[outcome.decision]
        self.updates += int(before != after)
        event = {"decision": outcome.decision, "accepted": True, "reward": reward, "bonus": bonus,
                 "before": before, "after": after, "weights_changed": before != after, "outcome": data}
        self.events.append(event)
        return event

    def snapshot(self):
        return {"schema": "sera-field.credit-bridge.1", "owner": self.owner.state_dict(),
                "specification": self.owner.specification(), "optimizer": self.optimizer.state_dict(),
                "verifiers": sorted(self.verifiers), "sources": sorted(self.sources),
                "pending": self.pending, "used_evidence": sorted(self.used_evidence),
                "used_assessments": sorted(self.used_assessments), "used_decisions": sorted(self.used_decisions),
                "contributions": sorted(self.contributions), "events": self.events, "updates": self.updates,
                "torch_rng": torch.get_rng_state(), "python_rng": random.getstate(), "numpy_rng": np.random.get_state()}

    def retire(self, decision, reason):
        if decision not in self.pending or not reason:
            raise ValueError("A pending decision and explicit retirement reason are required")
        event = {"decision": decision, "accepted": False, "reason": reason, "retired": True,
                 "original_goal": self.pending[decision]["goal"]}
        self.events.append(event)
        self.used_decisions.add(decision)
        del self.pending[decision]
        return event

    def restore(self, snapshot):
        if snapshot["schema"] != "sera-field.credit-bridge.1" or snapshot["specification"] != self.owner.specification():
            raise ValueError("Wrong schema or model specification")
        if set(snapshot["verifiers"]) != self.verifiers or set(snapshot["sources"]) != self.sources:
            raise ValueError("Frozen verification contracts changed")
        self.owner.load_state_dict(snapshot["owner"])
        self.optimizer.load_state_dict(snapshot["optimizer"])
        self.pending = snapshot["pending"]
        self.used_evidence = set(snapshot["used_evidence"])
        self.used_assessments = set(snapshot["used_assessments"])
        self.used_decisions = set(snapshot["used_decisions"])
        self.contributions = set(snapshot["contributions"])
        # Committed events remain in their immutable revision; new events start here.
        self.events, self.updates = [], snapshot["updates"]
        torch.set_rng_state(snapshot["torch_rng"])
        random.setstate(snapshot["python_rng"])
        np.random.set_state(snapshot["numpy_rng"])

    def commit(self, root, *, expected_parent, progress):
        """Crash-safe weights, credit and resume cursor in one content-addressed file.

        No persistent state is accepted from an untrusted checkpoint. The caller
        loads only its own locally created revision after checking this manifest.
        """
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        lock = root / "COMMIT.lock"
        with lock.open("x", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        try:
            pointer = root / "CURRENT.json"
            parent = json.loads(pointer.read_text())["sha256"] if pointer.exists() else None
            if parent != expected_parent:
                raise ValueError("Owner advanced: reload; never overwrite another revision")
            payload = {"bridge": self.snapshot(), "progress": progress, "parent": parent}
            temporary = root / (uuid.uuid4().hex + ".tmp")
            with temporary.open("xb") as handle:
                torch.save(payload, handle)
                handle.flush()
                os.fsync(handle.fileno())
            digest = sha256(temporary)
            revision = root / (digest + ".pt")
            temporary.rename(revision)
            manifest = {"sha256": digest, "revision": revision.name, "parent": parent,
                        "weights": weight_hash(self.owner), "updates": self.updates}
            write_json(pointer, manifest)
            self.events = []
            return manifest
        finally:
            lock.unlink()

    def load_current(self, root):
        root = Path(root)
        manifest = json.loads((root / "CURRENT.json").read_text())
        revision = (root / manifest["revision"]).resolve()
        if revision.parent != root.resolve() or revision.suffix != ".pt" or sha256(revision) != manifest["sha256"]:
            raise ValueError("Invalid local revision identity")
        payload = torch.load(revision, map_location="cpu", weights_only=False)
        self.restore(payload["bridge"])
        if weight_hash(self.owner) != manifest["weights"]:
            raise ValueError("Owner weights do not match manifest")
        return {"sha256": manifest["sha256"], "progress": payload["progress"]}
