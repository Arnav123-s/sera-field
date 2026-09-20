"""Persistent proposal -> actual measurement -> independent assessment -> answer.

Source records declare the measurement provider. The numerical verifier checks
against supplied measured outcomes, not against the learner's imagined answer.
Neither this file nor a source label authenticates an external instrument.
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch

from .credit_bridge import CheckedOutcome, identity
from .fusion_inquiry import LocalCreditBridge, measurement_candidates
from .inquiry_study import load_inquiry
from .model import weight_hash
from .records import sha256


def finite_rows(value, columns, minimum=1):
    rows = np.asarray(value, dtype='float32')
    if rows.ndim != 2 or rows.shape[1] != columns or len(rows) < minimum or not np.isfinite(rows).all():
        raise ValueError('Finite rows with the declared shape and minimum count required')
    if (abs(rows[:, :2]) > 2).any():
        raise ValueError('The qualified velocity/control input domain is [-2,2]')
    return rows


class InquirySession:
    def __init__(self, root, owner, *, source, assumptions):
        self.root = Path(root); self.owner = owner
        self.source = source; self.assumptions = assumptions
        if source.get('kind') not in ('measurement', 'independent_simulation', 'human_assessment') or not source.get('id'):
            raise ValueError('An identified measurement provider is required')
        if not assumptions:
            raise ValueError('Record the scope and assumptions')
        for name, p in owner.named_parameters():
            p.requires_grad_(name.startswith('imagination_policy.'))
        self.book = LocalCreditBridge(owner, learning_rate=.02,
            source_hashes=[identity(source)], verifier_hashes=[sha256(__file__)])
        self.parent = None; self.progress = None

    def commit(self):
        pointer = self.book.commit(self.root / 'revisions', expected_parent=self.parent, progress=self.progress)
        self.parent = pointer['sha256']
        return pointer

    def resume(self):
        current = self.book.load_current(self.root / 'revisions')
        self.parent = current['sha256']; self.progress = current['progress']
        if self.progress['source'] != self.source or self.progress['assumptions'] != self.assumptions:
            raise ValueError('Session measurement scope changed')

    @torch.no_grad()
    def acquire(self):
        return self.owner.acquire_extension(
            torch.tensor(self.progress['adaptation'], dtype=torch.float32)[None],
            torch.tensor(self.progress['calibration'], dtype=torch.float32)[None])

    @torch.no_grad()
    def answer(self):
        model, assessment = self.acquire()
        query = torch.tensor(self.progress['original_goal']['queries'], dtype=torch.float32)[None]
        result = self.owner.predict_model(model, query)[0].tolist()
        return {'original_goal': self.progress['original_goal'], 'conditional_predictions': result,
                'predictor': weight_hash(self.owner), 'assessment': assessment,
                'assumptions': self.assumptions, 'source': self.source,
                'pending_measurement': self.progress['pending']}

    def start(self, request):
        if (self.root / 'revisions/CURRENT.json').exists():
            raise ValueError('Preserve the existing session; resume it')
        a = finite_rows(request['adaptation'], 3, 8); c = finite_rows(request['calibration'], 3, 4)
        q = finite_rows(request['original_goal']['queries'], 2)
        adaptation, calibration, queries = set(map(tuple, a[:, :2])), set(map(tuple, c[:, :2])), set(map(tuple, q))
        if adaptation & calibration or queries & (adaptation | calibration):
            raise ValueError('Separate adaptation, calibration and original-goal query inputs')
        self.progress = {'source': self.source, 'assumptions': self.assumptions,
            'original_goal': request['original_goal'], 'adaptation': a.tolist(), 'calibration': c.tolist(),
            'pending': None, 'rounds': 0, 'seen_measurements': [], 'history': []}
        response = self.answer(); self.commit()
        return response

    def propose(self):
        if self.progress['pending'] is not None:
            raise ValueError('Resolve the pending measurement before proposing another')
        with torch.no_grad():
            model, _ = self.acquire()
            inputs = self.owner.investigation_inputs(model, model['observations'])
            mean = self.owner.imagination_policy.reference(inputs)
            sample = mean + .7 * torch.randn(2)
            branches = measurement_candidates(sample)
            options = {}
            for branch in branches:
                if branch['probe'] is None:
                    continue
                key = tuple(round(x, 7) for x in branch['probe'])
                entry = options.setdefault(key, {'probe': branch['probe'], 'probability': 0., 'methods': []})
                entry['probability'] += branch['probability']; entry['methods'].append(branch['method'])
            candidates = list(options.values())
            chosen = candidates[int(torch.multinomial(torch.tensor([r['probability'] for r in candidates]), 1))]
            goal = identity(self.progress['original_goal']); predictor = weight_hash(self.owner)
            decision = identity([self.parent, goal, self.progress['rounds'], sample.tolist()])
            query = torch.tensor(self.progress['original_goal']['queries'], dtype=torch.float32)[None]
            old_prediction = self.owner.predict_model(model, query).mean(1)[0].tolist()
            consequences = self.owner.predict_model(model, torch.tensor([chosen['probe']], dtype=torch.float32)[None])[0, :, 0].tolist()
        _, trace = self.owner.imagination_policy.eligibility(inputs, sample)
        self.book.record_local_score(decision=decision, goal=goal, predictor=predictor,
            assumptions_id=identity(self.assumptions), sample=sample,
            trace={'imagination_policy.' + k: v for k, v in trace.items()})
        pending = {'decision': decision, 'goal': goal, 'predictor': predictor,
            'requested': chosen['probe'], 'method': identity(sorted(set(chosen['methods']))),
            'branches': branches, 'distinct_proposals': len(candidates),
            'conditional_responses': consequences, 'original_goal_predictions': old_prediction,
            'rank_before': model['rank'], 'measurement_branches': 24, 'charge_projections': 72}
        self.progress['pending'] = pending; self.commit()
        return pending

    def observe(self, request):
        pending = self.progress['pending']
        if pending is None:
            raise ValueError('A retained proposal is required')
        if request['decision'] != pending['decision'] or request['source'] != self.source:
            raise ValueError('Measurement decision or source does not match')
        evidence_id = request['measurement_id']
        if not evidence_id or evidence_id in self.progress['seen_measurements']:
            raise ValueError('New independently identified measurement required')
        if not request.get('assessment_id'):
            raise ValueError('An independent assessment identifier is required')
        performed = finite_rows([request['performed']], 2)[0]
        observation = finite_rows([[*performed.tolist(), request['response']]], 3)[0]
        if tuple(performed) in set(map(tuple, np.asarray(self.progress['calibration'])[:, :2])):
            raise ValueError('Keep calibration inputs separate from acquisition')
        goals = np.asarray(self.progress['original_goal']['queries'], dtype='float32')
        measured = finite_rows(request['goal_measurements'], 3)
        if len(measured) != len(goals) or not np.array_equal(goals, measured[:, :2]):
            raise ValueError('Independent outcomes must correspond exactly to the original goal inputs')
        # The actual performed point is incorporated even when actuation differed.
        self.progress['adaptation'].append(observation.tolist())
        with torch.no_grad():
            model, assessment = self.acquire()
            after = self.owner.predict_model(model, torch.from_numpy(goals)[None]).mean(1)[0]
            truth = torch.from_numpy(measured[:, 2])
            before_loss = float((torch.tensor(pending['original_goal_predictions']) - truth).square().mean())
            after_loss = float((after - truth).square().mean())
            tag = self.owner.field.last_source[0].clone()
        intended = np.asarray(pending['requested'], dtype='float32')
        matched = np.array_equal(intended, performed)
        independent_inputs = not (set(map(tuple, goals)) &
            set(map(tuple, np.asarray(self.progress['adaptation'], dtype='float32')[:, :2])))
        assessment_id = identity([identity(self.source), request['assessment_id'], measured.tolist()])
        outcome = CheckedOutcome(pending['goal'], pending['decision'], pending['predictor'], pending['predictor'],
            identity([identity(self.source), evidence_id]), identity(self.source), sha256(__file__), assessment_id,
            self.source['kind'], identity(intended.tolist()), identity(performed.tolist()), before_loss, after_loss,
            independent_inputs, identity([pending['method'], pending['rank_before'], model['rank']]), identity(self.assumptions))
        credit = self.book.apply(outcome)
        capture = None
        if not credit['accepted']:
            self.book.retire(pending['decision'], credit['reason'])
        elif after_loss < before_loss:
            capture = self.owner.field.memory.capture(tag, credit,
                predictor=pending['predictor'], decision_policy=pending['predictor'])
        record = {'proposal': pending, 'receipt': request, 'actuation_matched': matched,
            'independent_goal_inputs': independent_inputs, 'credit': credit, 'capture': capture,
            'assessment': assessment, 'checked_predictions_before_credit': after.tolist()}
        self.progress['history'].append(record)
        self.progress['seen_measurements'].append(evidence_id)
        self.progress['pending'] = None; self.progress['rounds'] += 1
        response = self.answer()
        # Return the current post-credit/post-capture owner, not a stale prediction.
        returned_mean = np.asarray(response['conditional_predictions']).mean(0)
        record['returned_mse'] = float(np.mean((returned_mean - measured[:, 2]) ** 2))
        self.commit()
        return {**response, 'performed_measurement': record}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('start', 'propose', 'observe', 'answer'))
    parser.add_argument('--owner', type=Path, default=Path('checkpoints/INQUIRY-014'))
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    request = json.loads(args.input.read_text(encoding='utf-8'))
    owner, _ = load_inquiry(args.owner)
    session = InquirySession(args.session, owner, source=request['source'], assumptions=request['assumptions'])
    if args.action == 'start':
        result = session.start(request)
    else:
        session.resume()
        result = session.observe(request) if args.action == 'observe' else getattr(session, args.action)()
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
