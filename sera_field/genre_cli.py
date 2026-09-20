"""Use the finite-action owner for human interpretation and measured inquiry."""
import argparse
import json
import os
from pathlib import Path

import torch

from .genre_training import load_genre
from .interactive_inquiry import InquirySession
from .meaning_cli import interpret


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('interpret', 'start', 'propose', 'observe', 'answer'))
    parser.add_argument('--owner', type=Path, default=Path('checkpoints/GENRE-017'))
    parser.add_argument('--input', type=Path, required=True); parser.add_argument('--session', type=Path)
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1); request = json.loads(args.input.read_text(encoding='utf-8'))
    owner, _ = load_genre(args.owner); owner.eval(); session = None
    if args.session is not None:
        session = InquirySession(args.session, owner, source=request['source'], assumptions=request['assumptions'])
        if args.action != 'start': session.resume()
    if args.action == 'interpret':
        result = interpret(owner, request['premise'], request['hypotheses'])
        if session is not None: result['retained_original_goal'] = session.progress['original_goal']
    elif session is None:
        raise ValueError('Use a persistent --session for measured investigation')
    elif args.action == 'start': result = session.start(request)
    else: result = session.observe(request) if args.action == 'observe' else getattr(session, args.action)()
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__': main()
