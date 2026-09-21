"""Five scoped uses of one unchanged acquired situation and predictor."""
import math
import torch

from .model import weight_hash
from .native_data import identity


@torch.no_grad()
def five_uses(owner, state, *, velocity, force, changed_force, target, candidates):
    """Engineered finite search over the same learned conditional response.

    Read-only queries do not fit a new model, create observations, establish a
    unique law or manufacture a causal explanation. Ties remain alternatives.
    """
    scalars = [velocity, force, changed_force, target, *candidates]
    if len(state['events']) != 1 or not candidates or len(candidates) > 128 or any(not math.isfinite(x) for x in scalars):
        raise ValueError('One situation, finite quantities and one to 128 explicit controls required')
    if len(set(candidates)) != len(candidates): raise ValueError('Distinct intervention candidates required')
    before = identity({k: v.tolist() for k,v in state.items()})
    weights = weight_hash(owner)
    queries = next(owner.parameters()).new_tensor([[[f, velocity] for f in [force, changed_force, *candidates]]])
    branches = owner.physical_query(state, queries)[0]
    if not bool(torch.isfinite(branches).all()): raise ValueError('Nonfinite imagined consequences')
    predictions = branches.mean(-1)
    errors = (predictions[2:]-target).abs()
    best = errors.min()
    inverse = [i for i,e in enumerate(errors) if float(e) <= float(best)+1e-6]
    # Planning minimizes goal error first, then absolute effort. The ordering is
    # supplied, not reported as an independently invented objective.
    effort = min(abs(candidates[i]) for i in inverse)
    plans = [i for i in inverse if abs(candidates[i]) <= effort+1e-12]
    delta = float(predictions[1]-predictions[0])
    if identity({k:v.tolist() for k,v in state.items()}) != before or weight_hash(owner) != weights:
        raise ValueError('Conditional use modified the acquired predictor or situation')
    return {'state': before, 'weights': weights, 'observed_events': int(state['events'][0]),
        'forward': {'force': force, 'velocity': velocity, 'response': float(predictions[0]), 'branches': branches[0].tolist()},
        'inverse': {'target_response': target, 'candidate_forces': [candidates[i] for i in inverse],
                    'minimum_model_error': float(best), 'scope': 'best among supplied finite controls'},
        'counterfactual': {'changed_force': changed_force, 'response': float(predictions[1]), 'difference': delta,
                           'scope': 'conditional prediction; no intervention receipt'},
        'planning': {'target_response': target, 'candidate_forces': [candidates[i] for i in plans],
                     'objective': 'minimum model goal error, then minimum absolute force'},
        'explanation': {'change': 'increase' if delta > 1e-6 else 'decrease' if delta < -1e-6 else 'unresolved at tolerance',
            'model_response_difference': delta, 'scope': 'engineered description of a model contrast; causal claim requires checked interventions'},
        'all_candidates': [{'force': f, 'velocity': velocity, 'response': float(predictions[i+2]),
                            'branches': branches[i+2].tolist()} for i,f in enumerate(candidates)],
        'observations_added': 0, 'separate_models_fitted': 0, 'novelty_credit': 0}


def assess_five_uses(record, receipts):
    """Independent performed outcomes, bound to the complete prediction record."""
    required = {record['forward']['force'], record['counterfactual']['changed_force'],
                *[c['force'] for c in record['all_candidates']]}
    velocity = record['forward']['velocity']; observed = {}
    ids = set()
    for receipt in receipts:
        if (set(receipt) != {'id', 'source_sha256', 'performed', 'force', 'velocity', 'response'}
                or not receipt['performed'] or receipt['velocity'] != velocity or receipt['force'] not in required
                or receipt['id'] in ids or receipt['force'] in observed
                or not all(math.isfinite(receipt[k]) for k in ('force','velocity','response'))
                or len(receipt['source_sha256']) != 64
                or any(c not in '0123456789abcdef' for c in receipt['source_sha256'])):
            raise ValueError('Unique independently sourced outcomes under each declared control required')
        ids.add(receipt['id']); observed[receipt['force']] = receipt['response']
    if set(observed) != required: raise ValueError('An imagined outcome cannot replace a missing measurement')
    before = observed[record['forward']['force']]; after = observed[record['counterfactual']['changed_force']]
    target = record['inverse']['target_response']
    errors = {c['force']: abs(observed[c['force']]-target) for c in record['all_candidates']}
    return {'prediction_id': identity(record), 'receipt_identity': identity(receipts),
        'forward_squared_error': (record['forward']['response']-before)**2,
        'counterfactual_squared_error': (record['counterfactual']['response']-after)**2,
        'inverse_errors': {str(f): errors[f] for f in record['inverse']['candidate_forces']},
        'plan_errors': {str(f): errors[f] for f in record['planning']['candidate_forces']},
        'contrast_squared_error': (record['explanation']['model_response_difference']-(after-before))**2,
        'best_observed_grid_error': min(errors.values()), 'performed_controls_checked': True,
        'scope': 'finite intervention-qualified contrast; not uniqueness of an underlying physical law'}
