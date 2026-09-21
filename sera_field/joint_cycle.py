"""Mixed observed history and investigation through the existing native owner.

No second answer model, memory bank, pretrained tensor or policy head is added.
The existing shared choice map scores goal-conditioned observation candidates.
Annotations and simulated outcomes belong to the independent teaching process.
"""
import math

import torch

from .native_owner import select_state


def replay(owner, events, batch):
    """Reconstruct one chronological state under the current predictor.

    Re-encoding old observations is not a new measurement and earns no credit.
    Events contain observed input only; goal answers and annotations are excluded.
    """
    state = owner.empty(batch)
    for event in events:
        if event['kind'] == 'text':
            texts = event['texts']
            if len(texts) != batch:
                raise ValueError('One observed text per situation required')
            state, _ = owner.remember_texts(texts, state)
        elif event['kind'] == 'measurement':
            actual = event['actual']
            if actual.shape != (batch, 3):
                raise ValueError('Observed force, velocity and response required')
            encoded = owner.encode_numbers(actual[:, 0], actual[:, 1], actual[:, 2])
            updated, _ = owner.observe(state, encoded)
            present = event.get('present')
            if present is not None:
                if present.shape != (batch,) or present.dtype != torch.bool:
                    raise ValueError('A per-situation performed-measurement mask is required')
                updated = {key: torch.where(present.reshape(-1, *([1]*(value.ndim-1))), value, state[key])
                           if isinstance(value, torch.Tensor) else value for key, value in updated.items()}
            state = updated
        elif event['kind'] == 'credit':
            progress = event['progress']
            if progress.shape != (batch,) or not bool(torch.isfinite(progress).all()):
                raise ValueError('Finite independently checked per-situation progress required')
            state = with_credit(state, progress)
        else:
            raise ValueError('Unsupported observed event type')
    return state


def with_credit(state, progress):
    """Record checked progress without creating an observation or a new fact."""
    if progress.shape != state['marks'].shape[:1] or not bool(torch.isfinite(progress).all()):
        raise ValueError('Finite independently checked progress required')
    marks = .95 * state['marks'] + .05 * torch.stack((progress.clamp_min(0), (-progress).clamp_min(0)), -1)
    if not bool(torch.isfinite(marks).all()):
        raise ValueError('Representable evidence marks required')
    return {**state, 'marks': marks}


def answers(owner, state, hypotheses, goals, *, ablation=None):
    """Both original questions read the same retained situation."""
    if goals.ndim != 2 or goals.shape[1] != 2 or len(hypotheses) != goals.shape[0]:
        raise ValueError('Aligned human questions and physical goals required')
    human = owner.meaning(owner.imagine(state, owner.encode_texts(hypotheses), ablation=ablation))
    physical = owner.physical_query(state, goals[:, None], ablation=ablation)[:, 0]
    return {'semantic': human, 'physical': physical}


def investigation_logits(owner, state, goals, candidates, *, used=None, ablation=None):
    """Reuse the shared learned choice map; append an explicit STOP choice.

    The multiplicative goal/action relation is an engineered input construction.
    Learned scores require reward teaching; calling this function alone is not
    evidence of a qualified investigation policy.
    """
    if candidates.ndim != 2 or candidates.shape[1] != 2 or not len(candidates):
        raise ValueError('A finite force/velocity action grid is required')
    if goals.ndim != 2 or goals.shape[1] != 2 or len(goals) != len(state['fast']):
        raise ValueError('One physical goal per retained situation required')
    batch, count = len(goals), len(candidates)
    source = owner.encode_numbers(goals[:, 0], goals[:, 1])
    goal_features = owner.imagine(state, source, ablation=ablation).mean(1)
    indices = torch.arange(batch).repeat_interleave(count)
    action = candidates.repeat(batch, 1)
    source = owner.encode_numbers(action[:, 0], action[:, 1])
    action_features = owner.imagine(select_state(state, indices), source, ablation=ablation).mean(1).reshape(batch, count, -1)
    joint = .5 * (action_features * goal_features[:, None]
                  + action_features - goal_features[:, None])
    scores = owner.choice(joint).squeeze(-1)
    if used is not None:
        if used.shape != scores.shape or used.dtype != torch.bool:
            raise ValueError('Explicit per-situation used-action mask required')
        scores = scores.masked_fill(used, -torch.inf)
    stop = owner.choice(goal_features)
    return torch.cat((scores, stop), -1)


def checked_progress(before, after, truth, *, requested, actual, measurement_cost=.001):
    """Independent measured loss reduction and scoped action credit.

    An unexpectedly performed control can still provide useful evidence. It
    receives no policy credit for executing a different requested intervention.
    The caller supplies independently obtained outcomes, not self-predictions.
    """
    if not math.isfinite(measurement_cost) or measurement_cost < 0:
        raise ValueError('Finite nonnegative measurement cost required')
    if before.shape != after.shape or before.shape != truth.shape or before.ndim != 1:
        raise ValueError('Aligned scalar original-goal outcomes required')
    if requested.shape != actual.shape or requested.shape != (len(before), 2):
        raise ValueError('Both intended and performed controls required')
    if not all(bool(torch.isfinite(value).all()) for value in (before, after, truth, requested, actual)):
        raise ValueError('Finite predictions, outcomes and controls required')
    # Stable difference of squares; evaluation truth stays outside the learner.
    progress = (before-after) * (before+after-2*truth)
    if not bool(torch.isfinite(progress).all()):
        raise ValueError('Representable checked progress required')
    performed = (requested == actual).all(-1)
    policy_credit = torch.where(performed, progress-measurement_cost, torch.zeros_like(progress))
    return {'signed_progress': progress.detach(), 'performed_as_requested': performed,
            'policy_credit': policy_credit.detach()}


def policy_objective(logits, actions, credit, *, entropy_weight=.002, behavior_probability=None):
    """A score-function update from independent credit, not confidence."""
    if not math.isfinite(entropy_weight) or entropy_weight < 0:
        raise ValueError('Finite nonnegative entropy weight required')
    if actions.shape != logits.shape[:1] or credit.shape != actions.shape:
        raise ValueError('One decision and independent credit per situation required')
    if not bool(torch.isfinite(credit).all()):
        raise ValueError('Finite checked credit required')
    logp = logits.log_softmax(-1)
    selected = logp.gather(1, actions[:, None]).squeeze(1)
    if not bool(torch.isfinite(selected).all()):
        raise ValueError('A permitted action with finite probability is required')
    p = logp.exp()
    safe_logp = torch.where(torch.isfinite(logp), logp, torch.zeros_like(logp))
    entropy = -(p * safe_logp).sum(-1)
    ratio = torch.ones_like(credit)
    if behavior_probability is not None:
        if (behavior_probability.shape != credit.shape or
                not bool(torch.isfinite(behavior_probability).all()) or
                not bool(((behavior_probability > 0) & (behavior_probability <= 1)).all())):
            raise ValueError('Positive recorded behavior probabilities required')
        # Uniform exploration supplies identical measurements to matched arms.
        # Stop the importance ratio gradient: the score-function estimator then
        # estimates the policy gradient, not its doubled derivative.
        ratio = (selected.exp() / behavior_probability).detach()
    return -(ratio * credit.detach() * selected + entropy_weight * entropy).mean()
