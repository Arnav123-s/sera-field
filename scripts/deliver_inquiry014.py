"""Fresh-process delivery of the actual persisted investigation and reward loop."""
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.extension_world import episode
from sera_field.records import write_json, sha256


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    report = ROOT / 'reports/INQUIRY-014/DELIVERY.json'
    if report.exists():
        print('Preserved completed delivery: ' + str(report)); return
    root = ROOT / 'local/INQUIRY-014-delivery'; root.mkdir(parents=True, exist_ok=True)
    source = {'kind': 'independent_simulation', 'id': 'INQUIRY-014-delivery-v1'}
    assumptions = {'scope': 'bounded response, velocity and control in [-2,2]'}
    world, adaptation, calibration, queries = episode(14777, 'INQUIRY-014-delivery-v1')
    queries = queries[:4]
    request = {'source': source, 'assumptions': assumptions, 'adaptation': adaptation[:8].tolist(),
        'calibration': calibration.tolist(), 'original_goal': {'queries': queries.tolist()}}
    write_json(root / 'start.json', request)
    write_json(root / 'scope.json', {'source': source, 'assumptions': assumptions})

    def run(action, filename):
        process = subprocess.run([sys.executable, '-m', 'sera_field.interactive_inquiry', action,
            '--owner', 'checkpoints/INQUIRY-014', '--session', str(root / 'session'),
            '--input', str(root / filename)], cwd=ROOT, text=True, capture_output=True)
        if process.returncode:
            raise RuntimeError(process.stderr)
        return json.loads(process.stdout)

    pointer = root / 'session/revisions/CURRENT.json'
    if not pointer.exists():
        write_json(root / 'initial.json', run('start', 'start.json'))
    current = json.loads(pointer.read_text())
    payload_path = root / 'session/revisions' / current['revision']
    if sha256(payload_path) != current['sha256']:
        raise ValueError('Delivery checkpoint changed')
    progress = torch.load(payload_path, map_location='cpu', weights_only=False)['progress']
    for step in range(progress['rounds'], 3):
        proposal = progress['pending'] if progress['pending'] is not None else run('propose', 'scope.json')
        write_json(root / f'proposal-{step}.json', proposal)
        receipt = world.intervene(proposal['requested'], scale=.7 if step == 1 else 1.)
        truth = world.observe(queries[:, 0], queries[:, 1])
        request = {'source': source, 'assumptions': assumptions, 'decision': proposal['decision'],
            'measurement_id': f'delivery-{step}', 'assessment_id': f'independent-goal-assessment-{step}',
            'performed': receipt['performed'], 'response': receipt['observation'][2],
            'goal_measurements': np.column_stack((queries, truth)).tolist()}
        write_json(root / f'observation-{step}.json', request)
        result = run('observe', f'observation-{step}.json')
        write_json(root / f'result-{step}.json', result)
        if step == 1:
            assert not result['performed_measurement']['credit']['accepted']
        progress['pending'] = None
    one, two = run('answer', 'scope.json'), run('answer', 'scope.json')
    assert one == two and one['pending_measurement'] is None
    initial = json.loads((root / 'initial.json').read_text())
    assert one['original_goal'] == initial['original_goal']
    truth = world.observe(queries[:, 0], queries[:, 1])
    mse = lambda response: float(np.mean((np.asarray(response['conditional_predictions']).mean(0) - truth) ** 2))
    receipts = [json.loads((root / f'result-{i}.json').read_text())['performed_measurement'] for i in range(3)]
    write_json(report, {'fresh_process_restart_exact': True, 'original_goal_preserved': True,
        'initial_mse': mse(initial), 'returned_mse': mse(one), 'returned_answer': one,
        'independent_outcomes': truth.tolist(), 'performed_interventions': len(receipts),
        'mismatched_credit_rejected': not receipts[1]['credit']['accepted'],
        'all_branches_preserved': all(len(r['proposal']['branches']) == 24 for r in receipts),
        'credits': [r['credit'] for r in receipts], 'source': source,
        'teacher_source_sha256': sha256(ROOT / 'sera_field/extension_world.py'),
        'session_source_sha256': sha256(ROOT / 'sera_field/interactive_inquiry.py')})
    print(json.dumps({'initial_mse': mse(initial), 'returned_mse': mse(one), 'restart': 'exact'}))


if __name__ == '__main__':
    main()
