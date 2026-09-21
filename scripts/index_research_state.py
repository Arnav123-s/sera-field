"""Summarize completed evidence without loading or changing learned tensors."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIES = (
    ('UNIFIED-012', 'Coupled covariance, echo and condensate memory'),
    ('GROW-013', 'Acquired physical representation and retained cross-use'),
    ('INQUIRY-014', 'Persistent measured investigation'),
    ('SEMANTIC-015', 'Human sentence interpretation and curvature memory'),
    ('HISTORY-016', 'Added fast/slow history procedure'),
    ('GENRE-017', 'Broader human language and finite neural action'),
    ('NATIVE-019', 'Joint developmental memory, perception and imagination'),
    ('JOINT-020', 'Mixed observed situation, investigation and verified reward learning'),
    ('JOINT-021', 'Counterbalanced chronology repair and fresh reward comparison'),
    ('CORE-022', 'Complete-core engineering before from-scratch behavioral teaching'),
)


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def main():
    state_path = ROOT / 'reports/STATE.json'
    old = read('reports/STATE.json')
    archive = ROOT / 'reports/history/STATE-before-native019.json'
    if not archive.exists():
        if old.get('schema_version') == 2:
            raise ValueError('Preserve the original research state before indexing')
        archive.parent.mkdir(parents=True, exist_ok=True)
        archive.write_bytes(state_path.read_bytes())
    prior = read('reports/history/STATE-before-native019.json')
    studies = {}
    for name, purpose in STUDIES:
        folder = ROOT / 'reports' / name
        entry = {'purpose': purpose, 'report': f'reports/{name}/REPORT.md',
                 'completed_report': (folder / 'REPORT.md').exists()}
        decision = folder / 'QUALIFICATION.json'
        if decision.exists():
            assessment = json.loads(decision.read_text(encoding='utf-8'))
            entry.update(qualification=f'reports/{name}/QUALIFICATION.json',
                         all_frozen_gates=assessment.get('all_frozen_gates', assessment['all_gates']),
                         all_qualification_checks=assessment['all_gates'])
        for label in ('COSTS', 'TEACHING', 'REPLAY', 'DELIVERY'):
            if (folder / (label + '.json')).exists():
                entry[label.lower()] = f'reports/{name}/{label}.json'
        manifest = ROOT / 'checkpoints' / name / 'MANIFEST.json'
        if manifest.exists():
            entry['checkpoint_manifest'] = f'checkpoints/{name}/MANIFEST.json'
        if name == 'CORE-022' and (folder / 'ENGINEERING.json').exists():
            build = json.loads((folder / 'ENGINEERING.json').read_text())
            entry.update(stage=build['stage'], engineering='reports/CORE-022/ENGINEERING.json',
                         training_started=False, whole_owner_integration_complete=False)
        studies[name] = entry
    active = []
    for pattern in ('genre017-*', 'attach018-*', 'native019-*', 'joint020-*', 'joint021-*', 'core022-*'):
        for path in sorted((ROOT / 'runs').glob(pattern + '/state.json')):
            row = json.loads(path.read_text(encoding='utf-8'))
            if row['status'] in ('STARTING', 'RUNNING'):
                active.append({'attempt': path.parent.name, 'state': path.relative_to(ROOT).as_posix(),
                               'status': row['status'], 'command': row['command']})
    state = {
        'schema_version': 2,
        'goal': prior['full_vision'],
        'whole_research_completed': False,
        'research_focus': 'Complete the entire specified core and its engineering checks before fresh behavioral teaching, whole-system assessment and subsequent incremental learning. JOINT-021 is completed and preserved.',
        'next_work_order': 'docs/COMPLETE_CORE_WORK_ORDER.md',
        'readme': 'README.md',
        'documentation': 'docs/INDEX.md',
        'evidence_index': 'reports/INDEX.md',
        'architecture_tracker': 'docs/WHOLE_ARCHITECTURE.md',
        'behavioral_acceptance': 'docs/BEHAVIOR_ACCEPTANCE.md',
        'studies': studies,
        'preserved_usable_interfaces': {
            'persistent_device': {'owner': 'checkpoints/CONCEPT-011', 'guide': 'docs/CONCEPT_USAGE.md'},
            'physical_cross_use': {'owner': 'checkpoints/GROW-013', 'guide': 'docs/EXTENSION_USAGE.md'},
            'measured_investigation': {'owner': 'checkpoints/INQUIRY-014', 'guide': 'docs/INQUIRY_USAGE.md'},
            'human_interpretation': {'owner': 'checkpoints/SEMANTIC-015', 'guide': 'docs/SEMANTIC_USAGE.md'},
        },
        'native_research_interface': {
            'owner': 'checkpoints/NATIVE-019', 'guide': 'docs/NATIVE_USAGE.md',
            'qualification': 'reports/NATIVE-019/QUALIFICATION.json',
            'parent_checkpoint': None, 'pretrained_weights': None,
            'prior_default_replaced': False,
        },
        'preserved_reference': {
            'head': prior['preserved_reference_head'],
            'checkpoint_sha256': prior['preserved_reference_checkpoint_sha256'],
            'historical_state': 'reports/history/STATE-before-native019.json',
            'historical_readme': 'docs/README_HISTORY_20260920.md',
        },
        'latest_supplied_synthesis': prior['latest_supplied_synthesis'],
        'active_numerical_attempts': active,
        'numerical_lease_released': not Path('D:/ai/projects/sera/runs/v3-batch-001/active.lock').exists(),
        'resource_contract': {'numerical_threads': 1, 'process_tree_bytes': 2 * 1024**3, 'paid_compute': False},
        'work_delegated': False,
        'scheduled_followup': False,
        'publication': {
            'repository': 'https://github.com/Arnav123-s/sera-field',
            'previous_verified_record': prior['publication_record'],
            'latest_verified_release': read('reports/PUBLICATION.json') if (ROOT / 'reports/PUBLICATION.json').exists() else None,
            'current_snapshot_identity': 'PUBLICATION_MANIFEST.json',
        },
    }
    temporary = state_path.with_suffix('.json.pending')
    temporary.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    temporary.replace(state_path)
    print(json.dumps({'indexed_studies': len(studies), 'active_numerical_attempts': len(active),
                      'preserved_history': archive.relative_to(ROOT).as_posix()}))


if __name__ == '__main__':
    main()
