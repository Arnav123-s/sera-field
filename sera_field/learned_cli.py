"""Use the trained CONNECTED-003 owner on source reading, arithmetic and worlds."""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch

from .model import weight_hash
from .study_data import ROOT, number_pool, sentences
from .study_evaluation import expression_proposals
from .study_inquiry import load_selected, observation_tensors
from .learned_motion import rollout
from .records import sha256
from .study_world import probes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--training', type=Path, default=ROOT/'checkpoints/SCFE-004')
    sub = parser.add_subparsers(dest='task', required=True)
    reader = sub.add_parser('read')
    reader.add_argument('--question', required=True)
    reader.add_argument('--source', type=Path, required=True)
    math = sub.add_parser('math')
    math.add_argument('--question', required=True)
    world = sub.add_parser('imagine')
    world.add_argument('--observations', required=True, help='JSON rows [velocity, force/mass, measured acceleration]')
    world.add_argument('--queries', required=True, help='JSON rows [velocity, force/mass]')
    inquiry = sub.add_parser('investigate', help='Choose a useful next observation for the original goal')
    inquiry.add_argument('--observations', required=True, help='JSON measured rows [velocity, force/mass, acceleration]')
    inquiry.add_argument('--queries', required=True, help='JSON requested settings [velocity, force/mass]')
    motion = sub.add_parser('motion')
    motion.add_argument('--observations', required=True)
    motion.add_argument('--velocity', type=float, required=True)
    motion.add_argument('--force-per-mass', type=float, required=True)
    motion.add_argument('--duration', type=float, default=1.)
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py to reserve the numerical worker')
    torch.set_num_threads(1)
    owner, selected = load_selected(args.training)
    owner.eval()
    before = weight_hash(owner)
    with torch.no_grad():
        if args.task == 'read':
            text = args.source.read_text(encoding='utf-8-sig')
            slices = sentences(text)
            options = [text[s:e].strip() for s, e in slices]
            if not options or not text.strip():
                raise ValueError('The source must contain readable text')
            scores = torch.cat([owner.rank([args.question], [options[start:start+32]])[0]
                                for start in range(0, len(options), 32)])
            order = scores.argsort(descending=True)[:5].tolist()
            probability = scores.softmax(-1)
            result = {'question': args.question, 'source': str(args.source.resolve()),
                      'source_sha256': sha256(args.source),
                      'learned_evidence_ranking': [{'text': options[i], 'offset': slices[i],
                                                    'ranking_softmax': float(probability[i])} for i in order],
                      'qualification': 'Ranked source passages; preserve the source conditions and context.'}
        elif args.task == 'math':
            values = number_pool(args.question)
            result = {'question': args.question, 'observed_numbers_and_supplied_constants': values,
                      'learned_executable_proposals': expression_proposals(owner, args.question, values),
                      'qualification': 'Each arithmetic execution is exact; applicability to the question requires checking.'}
        elif args.task in ('imagine','investigate'):
            support, query = np.asarray(json.loads(args.observations), dtype='float32'), torch.tensor(json.loads(args.queries), dtype=torch.float32)[None]
            if support.ndim != 2 or not len(support) or support.shape[1] != 3 or query.ndim != 3 or not query.shape[1] or query.shape[-1] != 2 or not np.isfinite(support).all() or not torch.isfinite(query).all():
                raise ValueError('Finite observations and queries with documented shapes required')
            if args.task == 'investigate':
                options = probes()
                logits, situation = owner.probe_logits(*observation_tensors(support), torch.from_numpy(options)[None], query)
                index = int(logits[0].argmax())
            else:
                situation = owner.world(*observation_tensors(support))
            predictions = owner.consequences(situation['coefficients'], query)[0]
            result = {'conditional_acceleration_mean': predictions.mean(0).tolist(),
                      'imagined_alternatives': predictions.tolist(),
                      'qualification': 'Conditional on the supplied observations and learned finite physical basis.'}
            if args.task == 'investigate':
                result.update({'original_goal_queries': query[0].tolist(),
                               'proposed_next_measurement': {'velocity': float(options[index,0]),
                                                            'force_per_mass': float(options[index,1])},
                               'learned_probe_scores': logits[0].softmax(-1).tolist(),
                               'next_step': 'Measure the actual response, append its [velocity, force/mass, acceleration] row and re-imagine the original queries.',
                               'evidence_status': 'Proposed observation; no measurement has been performed.'})
        else:
            support = np.asarray(json.loads(args.observations), dtype='float32')
            if support.ndim != 2 or not len(support) or support.shape[1] != 3 or not np.isfinite(support).all():
                raise ValueError('Finite observation rows [velocity, force/mass, acceleration] required')
            coefficients = owner.world(*observation_tensors(support))['coefficients'][0].numpy()
            result = rollout(coefficients, args.velocity, args.force_per_mass, args.duration)
    assert weight_hash(owner) == before
    print(json.dumps({'checkpoint': selected, 'result': result}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
