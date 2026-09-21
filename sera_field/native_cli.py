"""Use the fresh jointly trained owner on retained text or measured observations."""
import argparse
import json
import os
from pathlib import Path

import torch

from .native_session import NativeSession
from .native_owner import select_state
from .native_training import load_native


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py for local numerical work')
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('interpret', 'start', 'answer', 'propose', 'observe', 'grade'))
    parser.add_argument('--owner', default='checkpoints/NATIVE-019')
    parser.add_argument('--session', type=Path); parser.add_argument('--input', type=Path)
    args = parser.parse_args(); torch.set_num_threads(1)
    owner, checkpoint, _ = load_native(args.owner); owner.eval()
    request = json.loads(args.input.read_text(encoding='utf-8')) if args.input else {}
    if args.action == 'interpret':
        hypotheses = request['hypotheses']
        with torch.no_grad():
            state, _ = owner.remember_texts([request['premise']])
            remembered = select_state(state, torch.zeros(len(hypotheses), dtype=torch.long))
            logits = owner.meaning(owner.imagine(remembered, owner.encode_texts(hypotheses)))
        result = {'checkpoint': checkpoint, 'premise_status': 'supplied conditional premise',
            'relations': [{'hypothesis': h, 'entailment_contradiction_unresolved': p.tolist()}
                          for h, p in zip(hypotheses, logits.softmax(-1).mean(1))]}
    else:
        if args.session is None: raise ValueError('Persistent session path required')
        if args.action == 'start':
            if (args.session / 'CURRENT.json').exists(): raise ValueError('Preserve the existing session')
            session = NativeSession(owner, request['goal'], source=request['source'])
            for evidence in request['observations']: session.remember(evidence)
            result = session.answer()
        else:
            session = NativeSession.load(owner, args.session)
            if args.action == 'answer': result = session.answer(request.get('queries'))
            elif args.action == 'propose': result = session.propose()
            elif args.action == 'observe': result = session.observe(request['decision_id'], request['evidence'])
            else: result = session.grade(request['decision_id'], independent_response=request['independent_response'],
                                         source=request['source'], verifier=request['verifier'])
        result['saved_revision'] = session.save(args.session)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__': main()
