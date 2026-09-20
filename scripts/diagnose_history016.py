"""Inspect retained training evidence without rerunning or tuning a final."""
import json
import math
import os
from pathlib import Path
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, write_json


def read(path): return json.loads(Path(path).read_text())


def summarize(values):
    return {'n': len(values), 'mean': sum(values) / len(values), 'min': min(values),
            'max': max(values), 'rms': math.sqrt(sum(v * v for v in values) / len(values))}


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    root = ROOT / 'runs/HISTORY-016/learned'; report = ROOT / 'reports/HISTORY-016/DIAGNOSIS.json'
    if report.exists(): raise SystemExit('Preserve the completed diagnosis')
    if not (ROOT / 'reports/HISTORY-016/QUALIFICATION.json').exists():
        raise SystemExit('Complete the frozen independent assessment first')
    initial = read(root / 'INITIAL.json'); final = read(root / 'revisions/CURRENT.json')
    states = []
    for selection in (initial, final):
        path = root / 'revisions' / selection['revision']
        if path.resolve().parent != (root / 'revisions').resolve() or sha256(path) != selection['sha256']:
            raise ValueError('Diagnosis requires the exact retained training revision')
        states.append(torch.load(path, map_location='cpu', weights_only=False)['bridge']['owner'])
    changes = {}
    for name, value in states[0].items():
        if not isinstance(value, torch.Tensor) or not name.startswith(('field.continuum.', 'field.raw_history_gain')):
            continue
        a, b = value.double(), states[1][name].double()
        changes[name] = {'elements': a.numel(), 'initial_norm': float(a.norm()), 'last_norm': float(b.norm()),
                         'change_norm': float((b-a).norm()), 'maximum_absolute_change': float((b-a).abs().max())}
    rows = []; identities = []; seen = set()
    for path in sorted(root.glob('episodes-*.jsonl')):
        identities.append({'file': path.name, 'sha256': sha256(path)})
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row['step'] in seen: raise ValueError('Reconcile repeated teaching before diagnosis')
            seen.add(row['step']); rows.append(row)
    if seen != set(range(1, 2049)): raise ValueError('Incomplete teaching record')
    rewards = [r['verified_progress_reward'] for r in rows]
    l1 = [sum(abs(a-b) for a,b in zip(r['before_probability'],r['after_probability'])) for r in rows]
    supports = [s for r in rows for s in r['supports']]
    result = {'initial': initial, 'last': final, 'changed_parameter_tensors': changes,
        'initial_history_gain': float(.2 * states[0]['field.raw_history_gain'].tanh()),
        'last_history_gain': float(.2 * states[1]['field.raw_history_gain'].tanh()),
        'training_reward': summarize(rewards), 'training_probability_l1_change': summarize(l1),
        'positive_query_progress': sum(r > 0 for r in rewards),
        'negative_query_progress': sum(r < 0 for r in rewards), 'zero_query_progress': sum(r == 0 for r in rewards),
        'query_choice_changed': sum(a['before_correct'] != a['after_correct'] for a in rows),
        'query_probability_argmax_changed': sum(max(range(3),key=r['before_probability'].__getitem__) !=
            max(range(3),key=r['after_probability'].__getitem__) for r in rows),
        'regularizer_contribution': summarize([.0001*r['reverse_kl'] for r in rows]),
        'same_support_fitting_progress': summarize([s['annotation_fitting_progress'] for s in supports]),
        'signal_retrieval_mse': summarize([s['current_signal_retrieval_mse'][0] for s in supports]),
        'development': read(root / 'COMPLETE.json')['development'], 'logs': identities,
        'scope': 'Post-assessment descriptive inspection of recorded training/development and exact initial/latest parameters; no final opened, no model update, no new selection.',
        'mechanism_observations': [
            'Four normalized annotation-gradient fields are mixed into one shared trace; there is no per-support content-addressed retrieval bank in this procedure.',
            'The fixed lexical selector uses overlap among source-disjoint examples; it does not establish a shared missing rule.',
            'The retained new history gain begins at zero, and development selection is allowed to preserve that baseline.'],
        'unresolved_causal_hypotheses': [
            'Cross-support gradient interference may make the mixed trace unhelpful to the distinct query.',
            'Support relevance and query-conditioned retrieval may need to be learned together with consolidation.',
            'The relative task-gradient and regularizer contributions need a fresh prospective study, not tuning on this final.'],
        'attempt': Path(os.environ['SERA_FIELD_ATTEMPT']).name, 'script_sha256': sha256(__file__)}
    write_json(report, result)
    print(json.dumps({k:result[k] for k in ('initial_history_gain','last_history_gain',
        'training_reward','training_probability_l1_change','positive_query_progress','negative_query_progress')}))


if __name__ == '__main__': main()
