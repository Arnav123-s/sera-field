"""Original-goal investigation, independent progress and durable real credit."""
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import torch

from .credit_bridge import CheckedOutcome, CreditBridge, identity
from .grounded_owner import GroundedOwner
from .model import weight_hash
from .records import sha256, write_json
from .study_data import ROOT
from .study_world import draw, probes, analytic_probe


def load_selected(training_root):
    root = Path(training_root)
    selection = json.loads((root / 'SELECTION.json').read_text())
    path = root / 'revisions' / selection['revision']
    if path.resolve().parent != (root / 'revisions').resolve() or sha256(path) != selection['sha256']:
        raise ValueError('Untrusted or changed selected checkpoint')
    payload = torch.load(path, map_location='cpu', weights_only=False)
    spec = dict(payload['bridge']['specification'])
    kind = spec.pop('type')
    if kind == 'grounded-field-003':
        owner = GroundedOwner(**spec)
    elif kind == 'clifford-sheaf-field-004':
        from .scfe_owner import ScfeOwner
        owner = ScfeOwner(**spec)
    elif kind == 'echo-sheaf-field-007':
        from .reversible_field import EchoOwner
        owner = EchoOwner(**spec)
    elif kind == 'concept-owner-008':
        from .concept_owner import ConceptOwner
        owner = ConceptOwner(**spec)
    elif kind == 'concept-language-010':
        from .concept_language import LanguageConceptOwner
        owner = LanguageConceptOwner(**spec)
    else:
        raise ValueError('Wrong owner')
    owner.load_state_dict(payload['bridge']['owner'])
    if weight_hash(owner) != selection['weights']:
        raise ValueError('Selected owner mismatch')
    return owner, selection


def observation_tensors(observations):
    return torch.tensor(np.asarray(observations), dtype=torch.float32)[None], torch.ones(1, len(observations))


def json_array(tensor):
    return tensor.detach().cpu().tolist()


class Investigator:
    def __init__(self, owner, *, seed=73113, reward=True):
        self.owner = owner
        self.seed = seed
        self.rng = torch.Generator().manual_seed(seed)
        self.reward_enabled = reward
        self.predictor_sha = weight_hash(owner)
        self.source_sha = sha256(ROOT / 'sera_field/study_world.py')
        self.verifier_sha = sha256(__file__)
        for name, parameter in owner.named_parameters():
            parameter.requires_grad_(name.startswith('investigation.'))
        self.book = CreditBridge(owner, learning_rate=.04 if reward else 0.,
                                 source_hashes=[self.source_sha], verifier_hashes=[self.verifier_sha])
        self.parent, self.cursor = None, 0

    def attempt(self, index, *, split='reward_teaching', policy='learned', train=True, omitted=False):
        world, support, queries, _ = draw(self.seed, index, split, inquiry=True,
                                          omitted=omitted, with_targets=False)
        observed, present = observation_tensors(support)
        options = probes()
        query = torch.from_numpy(queries)[None]
        logits, situation = self.owner.probe_logits(observed, present, torch.from_numpy(options)[None], query)
        before = self.owner.consequences(situation['coefficients'], query).detach()
        probabilities = logits[0].softmax(-1)
        if policy == 'random':
            choice = int(torch.randint(len(options), (1,), generator=self.rng))
        elif policy == 'analytic':
            choice = analytic_probe(support, options, queries)
        elif train:
            choice = int(torch.multinomial(probabilities.detach(), 1, generator=self.rng))
        else:
            choice = int(probabilities.argmax())
        goal = identity(['original-goal', split, self.seed, index, queries.tolist()])
        decision = identity(['decision', split, self.seed, index, policy])
        scope = 'observed-acceleration-linear-quadratic-drag-offset-v1'
        commit = {'goal': goal, 'decision': decision, 'predictor': self.predictor_sha,
                  'policy': weight_hash(self.owner), 'support': support.tolist(),
                  'goal_queries': queries.tolist(), 'imagined_goal_alternatives': json_array(before[0]),
                  'probe_probabilities': json_array(probabilities), 'chosen_probe': options[choice].tolist(),
                  'kind': 'conditional_predictions_before_independent_outcome'}
        if train:
            # On-policy categorical sampling; score-function matches actual behavior.
            self.book.record_decision(decision=decision, goal=goal, logits=logits[0], choice=choice,
                                      predictor=self.predictor_sha, assumptions_id=scope)
        # No queried answer or goal-outcome checker has been executed above this line.
        actuation_scale = .7 if index % 41 == 40 else 1.
        receipt = world.intervene(options[choice], actuator_scale=actuation_scale)
        actual_truth = torch.from_numpy(world.observe(queries[:, 0], queries[:, 1]).astype('float32'))
        after_support = np.vstack((support, receipt['observation'])).astype('float32')
        with torch.no_grad():
            revised = self.owner.world(*observation_tensors(after_support))
            after = self.owner.consequences(revised['coefficients'], query)[0]
        before_loss = float((before[0].mean(0) - actual_truth).square().mean())
        after_loss = float((after.mean(0) - actual_truth).square().mean())
        evidence = identity([self.source_sha, split, self.seed, index, receipt['performed'], receipt['observation']])
        assessment = identity([evidence, queries.tolist(), actual_truth.tolist()])
        outcome = CheckedOutcome(goal, decision, commit['policy'], self.predictor_sha, evidence,
                                 self.source_sha, self.verifier_sha, assessment, 'independent_simulation',
                                 identity(receipt['requested']), identity(receipt['performed']),
                                 before_loss, after_loss, True, 'probe:' + identity(receipt['performed']), scope)
        event = None
        if train:
            event = self.book.apply(outcome)
            if not event['accepted']:
                self.book.retire(decision, event['reason'])
        self.cursor = index + 1
        return {'index': index, 'split': split, 'decision_commit': commit,
                'decision_commit_sha256': identity(commit), 'intervention_receipt': receipt,
                'independent_goal_outcomes': actual_truth.tolist(),
                'before_loss': before_loss, 'after_loss': after_loss,
                'returned_answer': after.mean(0).tolist(), 'revised_alternatives': json_array(after),
                'original_goal_returned': True, 'event': event,
                'qualification': 'empirical simulated outcome; retained conditional model with supplied basis',
                'model_adequacy_mse': after_loss,
                'model_spread': float(after.std(0).mean()), 'cost': {'probes_requested': 1, 'probes_performed': 1,
                                                                            'goal_audit_outcomes': len(queries)}}

    def save(self, root):
        revision = self.book.commit(root, expected_parent=self.parent,
                                    progress={'cursor': self.cursor, 'seed': self.seed,
                                              'predictor_sha': self.predictor_sha,
                                              'reward_enabled': self.reward_enabled,
                                              'local_rng': self.rng.get_state()})
        self.parent = revision['sha256']
        return revision

    def resume(self, root):
        result = self.book.load_current(root)
        p = result['progress']
        if (p['seed'], p['reward_enabled'], p['predictor_sha']) != (self.seed, self.reward_enabled, self.predictor_sha):
            raise ValueError('Investigation identity changed')
        self.parent, self.cursor = result['sha256'], p['cursor']
        self.rng.set_state(p['local_rng'])


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--training', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--episodes', type=int, default=2048)
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the resource supervisor')
    torch.set_num_threads(1)
    args.output.mkdir(parents=True, exist_ok=True)
    summary = {}
    for reward in (True, False):
        arm = 'verified_reward' if reward else 'reward_disconnected'
        root = args.output / arm
        root.mkdir(parents=True, exist_ok=True)
        owner, selection = load_selected(args.training)
        agent = Investigator(owner, reward=reward)
        if (root / 'revisions/CURRENT.json').exists():
            agent.resume(root / 'revisions')
        else:
            agent.save(root / 'revisions')
        invocation = os.environ['SERA_FIELD_SUPERVISED']
        with (root / ('episodes-' + invocation + '.jsonl')).open('x', encoding='utf-8') as log:
            while agent.cursor < args.episodes:
                episode = agent.attempt(agent.cursor)
                episode['invocation'] = invocation
                log.write(json.dumps(episode) + '\n')
                if agent.cursor % 128 == 0:
                    log.flush()
                    revision = agent.save(root / 'revisions')
                    print(json.dumps({'arm': arm, 'attempts': agent.cursor, 'reward_updates': agent.book.updates,
                                      'last_before': episode['before_loss'], 'last_after': episode['after_loss']}), flush=True)
        revision = agent.save(root / 'revisions')
        summary[arm] = {'attempts': agent.cursor, 'weight_updates': agent.book.updates,
                        'revision': revision, 'base': selection}
    write_json(args.output / 'REWARD_COMPLETE.json', summary)


if __name__ == '__main__':
    main()
