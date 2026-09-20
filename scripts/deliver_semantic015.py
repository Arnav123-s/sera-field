"""Use human interpretation and measured investigation in one persistent owner."""
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
from sera_field.semantic_training import HumanBank, DATA


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    qualification = json.loads((ROOT / 'reports/SEMANTIC-015/QUALIFICATION.json').read_text())
    if not qualification['all_gates']:
        raise ValueError('Qualify the semantic owner before delivery')
    report = ROOT / 'reports/SEMANTIC-015/DELIVERY.json'
    if report.exists():
        print('Preserved completed semantic delivery'); return
    root = ROOT / 'local/SEMANTIC-015-delivery'; root.mkdir(parents=True, exist_ok=True)
    source = {'kind': 'independent_simulation', 'id': 'SEMANTIC-015-delivery-v1'}
    assumptions = {'scope': 'bounded response, velocity and control in [-2,2]'}
    scope = {'source': source, 'assumptions': assumptions}
    world, adaptation, calibration, queries = episode(15888, 'SEMANTIC-015-delivery-v1')
    queries = queries[:4]
    def run(action, request):
        path = root / (action + '.json'); write_json(path, {**scope, **request})
        process = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'sera_field.meaning_cli', action,
            '--owner', 'checkpoints/SEMANTIC-015', '--session', str(root / 'session'), '--input', str(path)],
            cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        if process.returncode:
            raise RuntimeError(process.stderr)
        return json.loads(process.stdout)
    pointer = root / 'session/revisions/CURRENT.json'
    if not pointer.exists():
        initial = run('start', {'adaptation': adaptation[:8].tolist(), 'calibration': calibration.tolist(),
            'original_goal': {'queries': queries.tolist()}})
        write_json(root / 'initial-result.json', initial)
    initial = json.loads((root / 'initial-result.json').read_text())
    # The first prospectively ordered development example is an interface check,
    # with its original human text. It is not a new generalization estimate.
    bank = HumanBank(DATA / 'development.jsonl'); row = bank.get([0])[0]
    before_revision = sha256(pointer)
    interpreted = run('interpret', {'premise': row['premise'], 'hypotheses': [row['hypothesis']]})
    immutable = sha256(pointer) == before_revision
    if not immutable or interpreted['retained_original_goal'] != initial['original_goal']:
        raise ValueError('Interpreting a conditional statement changed the original measured task')
    current = json.loads(pointer.read_text())
    revision = root / 'session/revisions' / current['revision']
    if sha256(revision) != current['sha256']:
        raise ValueError('Semantic delivery revision changed')
    progress = torch.load(revision, map_location='cpu', weights_only=False)['progress']
    if not progress['rounds']:
        proposal = progress['pending'] or run('propose', {})
        measurement = world.intervene(proposal['requested'])
        truth = world.observe(queries[:, 0], queries[:, 1])
        result = run('observe', {'decision': proposal['decision'], 'measurement_id': 'semantic-delivery-0',
            'assessment_id': 'independent-goal-assessment-semantic-0', 'performed': measurement['performed'],
            'response': measurement['observation'][2], 'goal_measurements': np.column_stack((queries, truth)).tolist()})
        write_json(root / 'observed-result.json', result)
    one, two = run('answer', {}), run('answer', {})
    if one != two or one['original_goal'] != initial['original_goal']:
        raise ValueError('Fresh-process answer changed the task or its exact state')
    truth = world.observe(queries[:, 0], queries[:, 1])
    mse = lambda r: float(np.mean((np.asarray(r['conditional_predictions']).mean(0) - truth) ** 2))
    write_json(report, {'fresh_process_restart_exact': True, 'original_goal_preserved': True,
        'conditional_text_read_did_not_write_observation': immutable, 'human_pair_id': row['id'],
        'human_annotation': row['target'], 'interpretation': interpreted,
        'initial_original_goal_mse': mse(initial), 'returned_original_goal_mse': mse(one),
        'returned_answer': one, 'independent_outcomes': truth.tolist(),
        'source': source, 'teacher_sha256': sha256(ROOT / 'sera_field/extension_world.py'),
        'interface_sha256': sha256(ROOT / 'sera_field/meaning_cli.py'),
        'scope': 'same-owner interface and persistence checks; separate text and measurement inputs, no cross-domain-transfer claim'})
    print(json.dumps({'restart': 'exact', 'initial_mse': mse(initial), 'returned_mse': mse(one)}))


if __name__ == '__main__':
    main()
