"""Resume one learned situation, investigate it and learn from checked credit."""
import argparse
import json
import os
from pathlib import Path

import torch

from .joint_session import JointSession
from .native_training import load_native


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py for local numerical work')
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('start', 'answer', 'propose', 'observe', 'grade'))
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--owner', default='checkpoints/JOINT-020')
    args = parser.parse_args(); torch.set_num_threads(1)
    request = json.loads(args.input.read_text(encoding='utf-8')) if args.input else {}
    if args.action == 'start':
        if (args.session / 'CURRENT.json').exists():
            raise ValueError('Preserve the existing task; use its saved session')
        owner, _, _ = load_native(args.owner)
        task = JointSession(owner, request['goal'], source=request['source'])
        for evidence in request['observations']:
            task.remember(evidence)
        result = task.answer()
    else:
        task = JointSession.load(args.session)
        if args.action == 'answer':
            result = task.answer(**{k: request[k] for k in ('force', 'velocity') if k in request})
        elif args.action == 'propose':
            result = task.propose()
        elif args.action == 'observe':
            result = task.observe(request['decision_id'], request.get('evidence'))
        else:
            result = task.grade(request['decision_id'], independent_response=request['independent_response'],
                source=request['source'], verifier=request['verifier'], evidence_id=request['evidence_id'])
    result['saved_revision'] = task.save(args.session)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
