"""Assess the actual selected owner in restarted interpretation/inquiry processes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.extension_world import episode
from sera_field.genre_training import DATA
from sera_field.records import write_json, sha256
from sera_field.semantic_training import HumanBank


def read(path): return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--owner', default='runs/GENRE-017/exact_noisy')
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    report = ROOT / 'reports/GENRE-017/DELIVERY.json'
    if report.exists(): print('Preserved completed genre delivery'); return
    root = ROOT / 'local/GENRE-017-delivery'; root.mkdir(parents=True, exist_ok=True)
    source = {'kind': 'independent_simulation', 'id': 'GENRE-017-persistent-delivery'}
    assumptions = {'scope': 'bounded response with velocity and control in [-2,2]'}
    scope = {'source': source, 'assumptions': assumptions}
    world, adaptation, calibration, queries = episode(17888, 'GENRE-017-persistent-delivery')
    queries = queries[:4]
    def run(action, request, suffix=''):
        path = root / (action + suffix + '.json'); write_json(path, {**scope, **request})
        process = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'sera_field.genre_cli', action,
            '--owner', args.owner, '--session', str(root / 'session'), '--input', str(path)],
            cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        if process.returncode: raise RuntimeError(process.stderr)
        return json.loads(process.stdout)
    pointer = root / 'session/revisions/CURRENT.json'
    if not pointer.exists():
        initial = run('start', {'adaptation': adaptation[:8].tolist(), 'calibration': calibration.tolist(),
            'original_goal': {'queries': queries.tolist()}})
        write_json(root / 'initial-result.json', initial)
    initial = read(root / 'initial-result.json')
    human = HumanBank(DATA / 'development.jsonl').get([0, 1, 2]); interpretations = []
    for index, row in enumerate(human):
        before = sha256(pointer)
        result = run('interpret', {'premise': row['premise'], 'hypotheses': [row['hypothesis']]}, str(index))
        interpretations.append({'id': row['id'], 'genre': row['genre'], 'human_annotation': row['target'],
            'returned': result, 'read_only': sha256(pointer) == before,
            'original_goal_retained': result['retained_original_goal'] == initial['original_goal']})
    current = read(pointer); revision = pointer.parent / current['revision']
    if sha256(revision) != current['sha256']: raise ValueError('Persistent revision changed')
    progress = torch.load(revision, map_location='cpu', weights_only=False)['progress']
    if not progress['rounds']:
        proposal = progress['pending'] or run('propose', {})
        observed = world.intervene(proposal['requested']); truth = world.observe(queries[:, 0], queries[:, 1])
        result = run('observe', {'decision': proposal['decision'], 'measurement_id': 'genre-delivery-0',
            'assessment_id': 'independent-genre-goal-0', 'performed': observed['performed'],
            'response': observed['observation'][2], 'goal_measurements': np.column_stack((queries, truth)).tolist()})
        write_json(root / 'observed-result.json', result)
    one, two = run('answer', {}), run('answer', {})
    current = read(pointer); payload = torch.load(pointer.parent / current['revision'], map_location='cpu', weights_only=False)
    progress = payload['progress']
    truth = world.observe(queries[:, 0], queries[:, 1])
    mse = lambda result: float(np.mean((np.asarray(result['conditional_predictions']).mean(0) - truth) ** 2))
    checks = {'fresh_process_restart_exact': one == two,
        'original_goal_preserved': one['original_goal'] == initial['original_goal'],
        'conditional_text_read_only': all(r['read_only'] for r in interpretations),
        'text_preserves_original_goal': all(r['original_goal_retained'] for r in interpretations),
        'one_actual_round': progress['rounds'] == 1}
    write_json(report, {'checks': checks, 'human_interpretations': interpretations,
        'initial_original_goal_mse': mse(initial), 'returned_original_goal_mse': mse(one),
        'returned_answer': one, 'independent_outcomes': truth.tolist(), 'credit_history': progress['history'],
        'source': source, 'teacher_sha256': sha256(ROOT / 'sera_field/extension_world.py'),
        'interface_sha256': sha256(ROOT / 'sera_field/genre_cli.py'),
        'scope': 'same-owner source-grounded interface and persistence; not a separate generalization estimate'})
    print(json.dumps({'checks': checks, 'initial_mse': mse(initial), 'returned_mse': mse(one)}))


if __name__ == '__main__': main()
