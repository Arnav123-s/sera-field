"""Whole-problem teaching and independent assessment through the common owner."""
import torch

from .core_learning import greedy_graph
from .core_programs import reachable
from .core_program_verifier import independently_execute
from .core_proposals import log_probability
from .core_teaching import public_input


def distribution_for(owner, rows):
    if not rows or any(not row['programs'] for row in rows):
        raise ValueError('Qualified executable teaching targets required')
    views = [public_input(row) for row in rows]
    state, _ = owner.remember_texts([view['context'] for view in views])
    return owner.program_distribution(state, [view['question'] for view in views], [view['arity'] for view in views])


def teaching_loss(owner, rows):
    distribution = distribution_for(owner, rows)
    terms = []
    for i, row in enumerate(rows):
        # Targets are alternative compatible computations for the supplied
        # instance. They never become extra input observations.
        probabilities = [log_probability(distribution, program, branch, row=i)
                         for program in row['programs'] for branch in range(3)]
        terms.append(-torch.logsumexp(torch.stack(probabilities), 0))
    return torch.stack(terms).mean(), distribution


@torch.no_grad()
def assess_program_rows(owner, rows):
    distribution = distribution_for(owner, rows)
    cases = []
    for i, row in enumerate(rows):
        proposed = greedy_graph(distribution, i)
        tests = ([{'inputs': row['inputs'], 'output': row['answer']}]
                 if row['track'] == 'whole_human_mathematics' else row['cases'])
        outcomes = []
        for case in tests:
            try:
                actual = str(independently_execute(proposed, case['inputs']))
                outcomes.append({'correct': actual == case['output'], 'prediction': actual})
            except (ValueError, ZeroDivisionError, OverflowError) as error:
                outcomes.append({'correct': False, 'error': type(error).__name__})
        cases.append({'id': row['id'], 'group': row['group'], 'track': row['track'],
            'proposal': proposed, 'checks': outcomes, 'correct': all(o['correct'] for o in outcomes),
            'active_instructions': len(reachable(proposed)), 'assessment': row['qualification']})
    return cases
