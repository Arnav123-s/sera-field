"""Parallel graph decisions from the existing imagined field, freshly weighted."""
import torch
from torch import nn

from .core_programs import BASE, OPERATIONS, UNARY, reachable, validate


class GraphProposal(nn.Module):
    def __init__(self, slots=4):
        super().__init__()
        if type(slots) is not int or not 1 <= slots <= 8:
            raise ValueError('One to eight explicit instruction slots required')
        self.slots = slots; refs = BASE+slots
        self.operations = nn.Linear(64, slots*len(OPERATIONS))
        self.left = nn.Linear(64, slots*refs)
        self.right = nn.Linear(64, slots*refs)
        self.output = nn.Linear(64, refs)

    def forward(self, features, branch_probabilities, arities):
        batch, branches = features.shape[:2]; slots = self.slots; refs = BASE+slots
        if len(arities) != batch or any(type(a) is not int or not 1 <= a <= 4 for a in arities):
            raise ValueError('Declared input arity per question required')
        valid = torch.tensor([[j >= 4 or j < a for j in range(refs)] for a in arities], device=features.device)
        order = torch.arange(refs, device=features.device)[None] < (BASE+torch.arange(slots, device=features.device))[:, None]
        operand_mask = valid[:, None, None] & order[None, None]
        return {'operations': self.operations(features).reshape(batch, branches, slots, len(OPERATIONS)),
            'left': self.left(features).reshape(batch, branches, slots, refs).masked_fill(~operand_mask, -torch.inf),
            'right': self.right(features).reshape(batch, branches, slots, refs).masked_fill(~operand_mask, -torch.inf),
            'output': self.output(features).masked_fill(~valid[:, None], -torch.inf),
            'branch_probabilities': branch_probabilities, 'arities': tuple(arities)}


def log_probability(distribution, program, branch, *, row=0):
    validate(program)
    slots = distribution['operations'].shape[-2]
    if len(program['nodes']) != slots or program['arity'] != distribution['arities'][row]:
        raise ValueError('Decision graph differs from the declared proposal space')
    if type(branch) is not int or not 0 <= branch < distribution['operations'].shape[1]:
        raise ValueError('Unknown conditional branch')
    result = distribution['branch_probabilities'][row, branch].log()
    result = result+distribution['output'][row, branch].log_softmax(-1)[program['output']]
    # Choices in dead slots are marginalized, not rewarded as creativity.
    for i in reachable(program):
        op, a, b = program['nodes'][i]
        result = result+distribution['operations'][row, branch, i].log_softmax(-1)[OPERATIONS.index(op)]
        result = result+distribution['left'][row, branch, i].log_softmax(-1)[a]
        if op not in UNARY: result = result+distribution['right'][row, branch, i].log_softmax(-1)[b]
    return result


@torch.no_grad()
def sample(distribution, count, *, row=0):
    if type(count) is not int or not 1 <= count <= 64:
        raise ValueError('One to 64 recorded proposal attempts per decision required')
    choose = lambda logits: int(torch.multinomial(logits.softmax(-1), 1))
    proposals = []
    for _ in range(count):
        branch = int(torch.multinomial(distribution['branch_probabilities'][row], 1))
        nodes = []
        for i in range(distribution['operations'].shape[-2]):
            op = OPERATIONS[choose(distribution['operations'][row, branch, i])]
            a = choose(distribution['left'][row, branch, i])
            b = a if op in UNARY else choose(distribution['right'][row, branch, i])
            nodes.append([op, a, b])
        program = {'arity': distribution['arities'][row], 'nodes': nodes,
                   'output': choose(distribution['output'][row, branch])}
        proposals.append({'branch': branch, 'program': program,
                          'log_probability': float(log_probability(distribution, program, branch, row=row))})
    return proposals
