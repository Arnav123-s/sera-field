"""Fresh-process, task-scoped history retention and protected-answer recovery."""
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.credit_bridge import identity
from sera_field.history_session import HistorySession
from sera_field.history_training import DATA, load_history, rows, probability
from sera_field.model import weight_hash
from sera_field.perfect_tensor_memory import pauli_word
from sera_field.records import sha256, write_json


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--owner', default='runs/HISTORY-016/learned')
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    report = ROOT / 'reports/HISTORY-016/DELIVERY.json'
    if report.exists():
        print('Preserved completed history delivery'); return
    root = ROOT / 'local/HISTORY-016-delivery'; root.mkdir(parents=True, exist_ok=True)
    source = {'kind': 'human_assessment', 'id': 'SNLI-1.0-HISTORY-016-development',
              'sha256': sha256(DATA / 'development.jsonl')}
    assumptions = {'scope': 'human relation annotation conditional on the recorded premise; four source-disjoint supports',
                   'selection': 'first eight prospectively ordered development queries; all attempts reported'}
    results = []
    for index, record in enumerate(rows('development')[:8]):
        directory = root / f'{index:02d}'; directory.mkdir(parents=True, exist_ok=True)
        goal = {k: v for k, v in record['query'].items() if k in ('id', 'source_group', 'premise', 'hypothesis')}
        base = {'source': source, 'assumptions': assumptions}
        def run(action, request):
            input_path = directory / (action + '.json'); write_json(input_path, {**base, **request})
            process = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'sera_field.history_session', action,
                '--owner', args.owner, '--session', str(directory / 'session'), '--input', str(input_path)],
                cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
            if process.returncode:
                raise RuntimeError(process.stderr)
            return json.loads(process.stdout)
        if not (directory / 'session/revisions/CURRENT.json').exists():
            initial = run('start', {'original_goal': goal}); write_json(directory / 'initial-result.json', initial)
        owner, _ = load_history(ROOT / args.owner)
        session = HistorySession(directory / 'session', owner, **base); session.resume()
        if not session.progress['assessed']:
            if session.progress['pending'] is None:
                proposal = run('propose', {'supports': record['supports']})
                write_json(directory / 'proposal-result.json', proposal)
            else:
                proposal = {k: v for k, v in session.progress['pending'].items() if k != 'state'}
            result = run('assess', {'receipt': {'query_id': goal['id'], 'source': source,
                'target': record['query']['target'], 'evidence_id': 'human-query-' + goal['id'],
                'assessment_id': f'HISTORY-016-delivery-{index}',
                'performed_proposal': 'deliberate-mismatched-actuation' if index == 0 else proposal['proposal']}})
            write_json(directory / 'assessed-result.json', result)
        elif not (directory / 'assessed-result.json').exists():
            write_json(directory / 'assessed-result.json', {'credit': session.progress['events'][-1],
                'returned_answer': session.answer()})
        result = json.loads((directory / 'assessed-result.json').read_text())
        one, two = run('answer', {}), run('answer', {})
        if one != two or one['original_goal'] != goal:
            raise ValueError('The resumed history session changed its original goal or answer')
        owner, selected = load_history(ROOT / args.owner)
        session = HistorySession(directory / 'session', owner, **base); session.resume()
        attempt = {'query_id': goal['id'], 'target': record['query']['target'],
            'credit': result['credit'], 'probability': one['probability'], 'fresh_process_restart_exact': True,
            'source': source, 'original_goal_id': identity(goal), 'retained': bool(owner.field.history_code_ready)}
        # A different task must receive the unmodified parent computation even
        # after this task's history has been qualified and retained.
        clean_owner, _ = load_history(ROOT / args.owner)
        with torch.no_grad():
            owner.field.active_history_goal = 'a-different-original-goal'
            unrelated = probability(owner, goal)
            expected = probability(clean_owner, goal)
        attempt['other_scope_unchanged'] = bool(torch.equal(unrelated, expected))
        owner.field.active_history_goal = identity(goal)
        if attempt['retained']:
            clean_state = owner.field.factual_state(); pristine = owner.field.history_code.clone()
            with torch.no_grad():
                clean = probability(owner, goal)
                owner.field.history_code.copy_(pristine @ pauli_word('IIYII').T)
                corrected = probability(owner, goal)
                one_error_delta = float((clean - corrected).abs().max())
                owner.field.history_code.copy_(pristine)
                # A known two-site erasure channel is the uniform Pauli twirl on
                # those sites. Linearity lets us assess each channel branch.
                errors = []
                for a in 'IXYZ':
                    for b in 'IXYZ':
                        encoded = pristine @ pauli_word(a + 'II' + b + 'I').T
                        state = owner.field.factual_state(code=encoded, erasures=(0, 3))
                        owner.field.history_preview = state
                        errors.append(float((probability(owner, goal) - clean).abs().max()))
                owner.field.history_preview = None
            attempt.update(single_error_answer_max_delta=one_error_delta,
                declared_two_erasure_answer_max_delta=max(errors),
                evidence_survives_restart=bool(owner.field.history_evidence),
                geometry_identity=owner.field.geometry_identity())
            if one_error_delta > 1e-6 or max(errors) > 1e-6:
                raise ValueError('The declared correction channel changed the retained answer')
        try:
            session.assess({'query_id': goal['id']})
        except ValueError:
            attempt['duplicate_query_credit_rejected'] = True
        else:
            raise ValueError('A revealed query received repeat credit')
        results.append(attempt)
    checks = {'all_original_goals_and_restarts': all(r['fresh_process_restart_exact'] for r in results),
        'mismatched_proposal_rejected': not results[0]['credit']['accepted'],
        'unrelated_scope_unchanged': all(r['other_scope_unchanged'] for r in results),
        'duplicate_query_credit_rejected': all(r['duplicate_query_credit_rejected'] for r in results)}
    write_json(report, {'checks': checks, 'all_checks': all(checks.values()), 'attempts': results,
        'retained_count': sum(r['retained'] for r in results), 'selected': selected,
        'source_sha256': sha256(__file__), 'assessment_scope': assumptions,
        'whole_architecture_completed': False})
    print(json.dumps({'checks': checks, 'retained_count': sum(r['retained'] for r in results)}))


if __name__ == '__main__':
    main()
