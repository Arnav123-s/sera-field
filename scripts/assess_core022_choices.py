"""Source-choice assessment through the actual unchanged coupled owner.

The caller explicitly opens the allowed partition and supplies its registered
views. This adapter reads no corpus, initializes no model and takes no learning
step. Numerical use requires the normal exclusive supervisor.
"""
import os

from scripts.core022_assessment_views import identity, score_choices


def assess_owner(owner, views, *, batch_size=4):
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise ValueError('Use the exclusive numerical supervisor')
    if type(batch_size) is not int or not 1 <= batch_size <= 4:
        raise ValueError('The assessment workload permits one to four cases per batch')
    # Import only when an actual supervised owner is assessed. The data-view
    # construction and bookkeeping checks stay independent of the model stack.
    import torch
    from sera_field.model import weight_hash

    if owner.specification()['type'] != 'complete-core-candidate-022':
        raise ValueError('This assessment requires the actual coupled owner')
    for view in views:
        if identity({k: v for k, v in view.items() if k != 'identity'}) != view['identity']:
            raise ValueError('Changed registered assessment view')
    before = weight_hash(owner)
    original_training_mode = owner.training
    predictions = [None] * len(views)
    scores = [None] * len(views)
    indices = [i for i, view in enumerate(views) if view['scored']]
    owner.eval()
    try:
        with torch.no_grad():
            for offset in range(0, len(indices), batch_size):
                chosen = indices[offset:offset + batch_size]
                # Only public question/context and candidate answer strings
                # reach the owner. Target indices and provenance stay here.
                contexts = [views[i]['context'] for i in chosen]
                options = [views[i]['options'] for i in chosen]
                logits = owner.option_logits(contexts, options)
                if logits.ndim != 2 or logits.shape != (len(chosen), max(map(len, options))):
                    raise ValueError('The owner returned a different candidate layout')
                for local, index in enumerate(chosen):
                    active = logits[local, :len(options[local])]
                    if not bool(torch.isfinite(active).all()):
                        raise ValueError('Nonfinite owned prediction; preserve this failed assessment')
                    predictions[index] = int(active.argmax())
                    scores[index] = active.softmax(-1).tolist()
        if weight_hash(owner) != before:
            raise ValueError('Read-only held-out assessment changed learner weights')
        cases = score_choices(views, predictions)
        for case, probabilities in zip(cases, scores):
            case['probabilities'] = probabilities
        return {'weights': before, 'views_identity': identity(views), 'cases': cases,
                'scored_cases': len(indices), 'unscored_cases': len(views) - len(indices),
                'accuracy': sum(cases[i]['correct'] for i in indices) / len(indices) if indices else None,
                'mean_chance': sum(cases[i]['chance'] for i in indices) / len(indices) if indices else None,
                'optimizer_updates': 0, 'model_initializations': 0,
                'scope': 'same-owner attributed source-answer selection; richer interpretation has separate obligations'}
    finally:
        owner.train(original_training_mode)
