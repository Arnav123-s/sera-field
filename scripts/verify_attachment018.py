"""Verify finite attachment identities after the active curriculum completes.

No parameters are trained and no behavioral final is opened. This report cannot
be used as a learned-growth qualification.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.model import weight_hash
from sera_field.records import sha256, utc, write_json
from sera_field.semantic_training import load_semantic
from sera_field.variable_sheaf import CellAttachment, from_clifford_field


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    if not (ROOT / 'reports/GENRE-017/REPORT.md').exists():
        raise SystemExit('Finish the owned GENRE-017 sequence before taking its numerical slot')
    torch.set_num_threads(1)
    report = ROOT / 'reports/ATTACH-018'
    if (report / 'ENGINEERING.json').exists():
        raise SystemExit('Preserve the completed check; inspect before repeating')
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests/test_variable_sheaf.py'], cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)
    torch.manual_seed(18118)
    owner, selected = load_semantic(ROOT / 'checkpoints/SEMANTIC-015')
    original = weight_hash(owner)
    graph = from_clifford_field(owner.field, dtype=torch.double)
    b = .25 * torch.eye(8, dtype=torch.double)
    a = torch.randn(8, 3, dtype=torch.double) * .1
    chart = CellAttachment(graph, 0, b, a)
    state = torch.randn(4, graph.size, dtype=torch.double)
    enlarged = chart.encode(state)
    old_d, new_d = graph.matrix(), chart.enlarged.matrix()
    t = chart.matrix(); inv = torch.linalg.inv(t); g = inv.T @ inv
    expected = torch.cat((graph.coboundary(state), torch.zeros(4, chart.r, dtype=torch.double)), -1)
    errors = {
        'enlarged_coboundary_max_abs': float((chart.enlarged.coboundary(enlarged) - expected).abs().max().detach()),
        'round_trip_max_abs': float((chart.decode(enlarged)[0] - state).abs().max().detach()),
        'metric_gradient_max_abs': float((chart.metric_gradient(enlarged)
            - torch.linalg.solve(g, (enlarged @ (new_d.T @ new_d)).T).T).abs().max().detach()),
    }
    old_rank = int(torch.linalg.matrix_rank(old_d)); new_rank = int(torch.linalg.matrix_rank(new_d))
    record = {
        'status': 'mathematical_transition_verified', 'utc': utc(),
        'numerical_attempt': os.environ['SERA_FIELD_SUPERVISED'],
        'test_count': 8, 'parent_selection': selected, 'parent_weights': original,
        'owner_weights_unchanged': original == weight_hash(owner),
        'old_dimensions': list(graph.dimensions), 'new_dimensions': list(chart.enlarged.dimensions),
        'old_edges': len(graph.edges), 'new_edges': len(chart.enlarged.edges),
        'old_nullity': graph.size - old_rank, 'new_nullity': chart.size - new_rank,
        'new_free_dimensions': chart.k, 'transform_condition': float(torch.linalg.cond(t).detach()),
        'minimum_metric_eigenvalue': float(torch.linalg.eigvalsh(g).min().detach()),
        'maximum_metric_eigenvalue': float(torch.linalg.eigvalsh(g).max().detach()),
        'errors': errors, 'storage': chart.storage(), 'learned_updates': 0,
        'data_used': 'deterministic mathematical inputs and the retained owner restriction maps',
        'behavioral_qualification': 'not assessed by this engineering suite',
        'scope': 'actual additional stalk with exact initial projection and stated metric consistency flow',
        'sources': {name: sha256(ROOT / name) for name in (
            'protocols/ATTACH-018-ENGINEERING.md', 'sera_field/variable_sheaf.py',
            'tests/test_variable_sheaf.py', 'scripts/verify_attachment018.py')},
    }
    if (record['new_nullity'] - record['old_nullity'] != chart.k
            or not record['owner_weights_unchanged'] or max(errors.values()) > 1e-10):
        raise ValueError('The independent actual-owner attachment identity failed')
    write_json(report / 'ENGINEERING.json', record)
    (report / 'ENGINEERING.md').write_text(f'''# ATTACH-018: verified finite representation attachment

The operator adds an actual stalk to the retained learned field: {len(graph.dimensions)}
vertices and {graph.size} state coordinates become {len(chart.enlarged.dimensions)}
vertices and {chart.size} coordinates. The independent compatible-section space
gains {chart.k} dimensions. The original owner weights and readouts are preserved.

All eight prospective checks passed, including an independent dense metric-flow
calculation, finite-difference gradients, frame changes, explicit non-ring
topology, fixed-operator dependency cones and exact restart. The largest measured
identity discrepancy on the actual owner is {max(errors.values()):.3g}.

This is a mathematical transition and owner adapter. Useful autonomous growth
still requires training a new source/readout coupling, an adequacy-based growth
decision, explicit memory/covariance addressing, and an independently assessed
return to the original task. No new learned capability or final-task score is
inferred from these operator checks. No teaching/final cohort was opened.

The [frozen engineering protocol](../../protocols/ATTACH-018-ENGINEERING.md),
[derivation](../../docs/CELL_ATTACHMENT_CONTRACT.md) and
[machine-readable identities](ENGINEERING.json) record the exact scope.
Supervised attempt `{os.environ['SERA_FIELD_SUPERVISED']}` retains the test output,
source identities, process memory, CPU and wall costs. The original ring and
earlier owners remain available; the enlarged graph uses explicit restrictions.
''', encoding='utf-8')
    print(json.dumps({'status': record['status'], 'errors': errors, 'learned_updates': 0}))


if __name__ == '__main__':
    main()
