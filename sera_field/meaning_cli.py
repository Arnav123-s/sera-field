"""Interpret conditional statements or continue a measured task with one owner."""
import argparse
import json
import os
from pathlib import Path

import torch

from .interactive_inquiry import InquirySession
from .model import weight_hash
from .semantic_training import load_semantic

LABELS = ('follows_from_premise', 'conflicts_with_premise', 'additional_information_needed')


@torch.no_grad()
def interpret(owner, premise, hypotheses):
    if not isinstance(premise, str) or not premise.strip() or not hypotheses:
        raise ValueError('A premise and at least one proposed statement are required')
    if any(not isinstance(h, str) or not h.strip() for h in hypotheses):
        raise ValueError('Every proposed statement must contain text')
    before = weight_hash(owner)
    logits = owner.semantic([premise] * len(hypotheses), hypotheses)
    probability = logits.softmax(-1).mean(1)
    results = []
    for hypothesis, distribution, branches in zip(hypotheses, probability, logits):
        results.append({'statement': hypothesis, 'relation': LABELS[int(distribution.argmax())],
            'probabilities': dict(zip(LABELS, distribution.tolist())),
            'conditional_branches': [LABELS[int(i)] for i in branches.argmax(-1)],
            'branch_agreement': len(set(branches.argmax(-1).tolist())) == 1})
    if weight_hash(owner) != before:
        raise ValueError('Interpretation unexpectedly changed retained state')
    return {'premise': premise, 'status': 'conditional_on_the_supplied_premise',
            'interpretations': results, 'predictor': before}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('interpret', 'start', 'propose', 'observe', 'answer'))
    parser.add_argument('--owner', type=Path, default=Path('checkpoints/SEMANTIC-015'))
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--session', type=Path)
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    request = json.loads(args.input.read_text(encoding='utf-8'))
    owner, _ = load_semantic(args.owner); owner.eval()
    session = None
    if args.session is not None:
        session = InquirySession(args.session, owner, source=request['source'], assumptions=request['assumptions'])
        if args.action != 'start':
            session.resume()
    if args.action == 'interpret':
        result = interpret(owner, request['premise'], request['hypotheses'])
        if session is not None:
            result['retained_original_goal'] = session.progress['original_goal']
    elif session is None:
        raise ValueError('A persistent --session is required for a measured investigation')
    elif args.action == 'start':
        result = session.start(request)
    else:
        result = session.observe(request) if args.action == 'observe' else getattr(session, args.action)()
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
