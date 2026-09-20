"""Persist an evidence-qualified history correction on its original text task.

Human source annotations are external supervision. The assessor recomputes losses
from saved distributions rather than accepting the learner's self-reported grade.
Source identities describe the dataset; they do not authenticate an arbitrary
external caller. Each independent query is assessed once, including failed credit.
"""
import argparse
import copy
from dataclasses import asdict
import json
import math
import os
from pathlib import Path

import torch

from .credit_bridge import CheckedOutcome, CreditBridge, identity
from .history_owner import history_identity
from .history_training import episode, load_history, probability
from .model import weight_hash
from .records import sha256


def checked_loss(distribution, target):
    if target not in (0, 1, 2) or len(distribution) != 3 or not all(
            math.isfinite(p) and 0 <= p <= 1 for p in distribution) or abs(sum(distribution) - 1) > 1e-5:
        raise ValueError('An independent three-way annotation and a normalized distribution are required')
    return -math.log(max(distribution[target], 1e-12))


class HistorySession:
    def __init__(self, root, owner, *, source, assumptions):
        if source.get('kind') != 'human_assessment' or not source.get('id') or not source.get('sha256') or not assumptions:
            raise ValueError('An identified human-annotation source and explicit assumptions are required')
        self.root = Path(root); self.owner = owner; self.source = source; self.assumptions = assumptions
        self.book = CreditBridge(owner, learning_rate=0,
            source_hashes=[identity(source)], verifier_hashes=[sha256(__file__)])
        self.parent = None; self.progress = None

    def commit(self):
        pointer = self.book.commit(self.root / 'revisions', expected_parent=self.parent, progress=self.progress)
        self.parent = pointer['sha256']; return pointer

    def resume(self):
        current = self.book.load_current(self.root / 'revisions')
        self.parent = current['sha256']; self.progress = current['progress']
        if self.progress['source'] != self.source or self.progress['assumptions'] != self.assumptions:
            raise ValueError('Preserve the original source and assumptions')
        self.owner.field.active_history_goal = identity(self.progress['original_goal'])

    def start(self, goal):
        if (self.root / 'revisions/CURRENT.json').exists():
            raise ValueError('Resume the existing session instead of overwriting it')
        if set(goal) != {'id', 'source_group', 'premise', 'hypothesis'} or not all(isinstance(v, str) and v for v in goal.values()):
            raise ValueError('The original query must contain its identity and text, with its answer withheld')
        if bool(self.owner.field.history_code_ready):
            raise ValueError('Begin with an uncommitted owner or resume its existing scoped session')
        self.progress = {'source': self.source, 'assumptions': self.assumptions,
            'original_goal': copy.deepcopy(goal), 'pending': None, 'assessed': False, 'events': []}
        self.owner.field.active_history_goal = identity(goal)
        answer = self.answer(); self.commit(); return answer

    def propose(self, supports):
        if self.progress['pending'] is not None or self.progress['assessed']:
            raise ValueError('Preserve the existing proposal/assessment; do not retry against the revealed query label')
        goal = self.progress['original_goal']
        if len(supports) != 4 or len({s['id'] for s in supports}) != 4 or any(
                s['source_group'] == goal['source_group'] or s['target'] not in (0, 1, 2) for s in supports):
            raise ValueError('Four distinct annotated supports must be separate from the query source')
        predictor = weight_hash(self.owner)
        # The placeholder is used only in discarded grade diagnostics. The
        # proposed state depends on support labels and query text, never its label.
        record = {'id': identity([goal, supports]), 'query': {**goal, 'target': 0}, 'supports': supports}
        _, result, proposed = episode(self.owner, record)
        proposed = {k: v.detach().clone() if isinstance(v, torch.Tensor) else v for k, v in proposed.items()}
        if weight_hash(self.owner) != predictor:
            raise ValueError('Conditional practice changed factual owner state')
        self.progress['pending'] = {'decision': identity([predictor, record['id']]),
            'predictor': predictor, 'proposal': history_identity(proposed), 'state': proposed,
            'before_probability': result['before_probability'], 'after_probability': result['after_probability'],
            'support_ids': [s['id'] for s in supports], 'support_record_sha256': identity(supports)}
        self.commit()
        return {k: v for k, v in self.progress['pending'].items() if k != 'state'}

    def assess(self, receipt):
        pending = self.progress['pending']
        if pending is None or self.progress['assessed']:
            raise ValueError('No unassessed query remains; preserve every previous attempt')
        if pending['predictor'] != weight_hash(self.owner):
            raise ValueError('The predictor changed before independent assessment')
        if receipt['query_id'] != self.progress['original_goal']['id'] or receipt['source'] != self.source:
            raise ValueError('The assessment must address the original query and registered human source')
        if not all(isinstance(receipt[k], str) and receipt[k] for k in ('evidence_id', 'assessment_id', 'performed_proposal')):
            raise ValueError('Preserve complete independent evidence and assessment identities')
        # Verify that the saved proposal actually produces the recorded answer
        # before using an external annotation to judge that answer.
        with torch.no_grad():
            prior_preview = self.owner.field.history_preview
            try:
                self.owner.field.history_preview = pending['state']
                replayed = probability(self.owner, self.progress['original_goal']).tolist()
            finally:
                self.owner.field.history_preview = prior_preview
        if max(abs(a - b) for a, b in zip(replayed, pending['after_probability'])) > 1e-7:
            raise ValueError('The proposed state no longer produces its assessed answer')
        before = checked_loss(pending['before_probability'], receipt['target'])
        after = checked_loss(pending['after_probability'], receipt['target'])
        performed = receipt['performed_proposal']
        verified = performed == pending['proposal'] == history_identity(pending['state'])
        outcome = CheckedOutcome(goal=identity(self.progress['original_goal']), decision=pending['decision'],
            policy_before=pending['predictor'], predictor=pending['predictor'], evidence_id=receipt['evidence_id'],
            source_sha256=identity(self.source), verifier_sha256=sha256(__file__), assessment_id=receipt['assessment_id'],
            evidence_kind='human_assessment', intended_intervention=pending['proposal'], observed_intervention=performed,
            before_loss=before, after_loss=after, verified=verified,
            canonical_contribution=identity([pending['support_record_sha256'], pending['proposal']]),
            assumptions_id=identity(self.assumptions))
        accepted = verified and after < before
        event = {'accepted': accepted, 'outcome': asdict(outcome), 'independent_progress': before - after,
            'reward': (before - after) / (1 + before) if verified else 0.,
            'reason': ('independently checked query improvement' if accepted else
                       'no positive independent query improvement' if verified else 'proposal was not performed as assessed')}
        if accepted:
            self.owner.retain_history(pending['state'], event, proposal_id=pending['proposal'])
        self.progress['events'].append(event); self.progress['assessed'] = True; self.progress['pending'] = None
        returned = self.answer(); self.commit()
        return {'credit': event, 'returned_answer': returned}

    @torch.no_grad()
    def answer(self):
        goal = self.progress['original_goal']; self.owner.field.active_history_goal = identity(goal)
        distribution = probability(self.owner, goal).tolist()
        return {'original_goal': goal, 'probability': distribution, 'predictor': weight_hash(self.owner),
            'retained_history': bool(self.owner.field.history_code_ready),
            'evidence': copy.deepcopy(self.owner.field.history_evidence),
            'status': 'conditional_on_the_stated_premise', 'pending': self.progress['pending'] is not None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('start', 'propose', 'assess', 'answer'))
    parser.add_argument('--owner', type=Path, default=Path('checkpoints/HISTORY-016'))
    parser.add_argument('--session', type=Path, required=True); parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    request = json.loads(args.input.read_text(encoding='utf-8')); owner, _ = load_history(args.owner)
    session = HistorySession(args.session, owner, source=request['source'], assumptions=request['assumptions'])
    if args.action == 'start':
        result = session.start(request['original_goal'])
    else:
        session.resume()
        result = (session.propose(request['supports']) if args.action == 'propose' else
                  session.assess(request['receipt']) if args.action == 'assess' else session.answer())
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
