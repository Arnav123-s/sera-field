"""Package the taught predictor and independently qualified learned policy."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch
from sera_field.model import weight_hash
from sera_field.records import sha256, write_json
from sera_field.study_inquiry import load_selected


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the resource supervisor')
    torch.set_num_threads(1)
    source = ROOT/'runs/SCFE-004-teaching-1103'
    comparison = ROOT/'runs/CONNECTED-SCFE-COMPARISON-001'
    completed = json.loads((comparison/'COMPLETE.json').read_text())
    if not completed['independent_replays']['scfe']['all_metrics_and_raw_records_exact']:
        raise ValueError('Independent replay is required before packaging')
    owner, selected = load_selected(source)
    qualification = ROOT/'runs/SCFE-006-policy-selection'
    assessed = json.loads((qualification/'final/RESULTS.json').read_text())
    replayed = json.loads((qualification/'REPLAY.json').read_text())
    choice_path = qualification/'SELECTION.json'
    choice = json.loads(choice_path.read_text())['candidate']
    if (not assessed['qualified_for_promotion'] or not replayed['all_results_and_records_exact']
            or assessed['selection_sha256'] != sha256(choice_path)
            or replayed['selection_sha256'] != sha256(choice_path)):
        raise ValueError('The policy must qualify and independently replay before integration')
    policy_path = ROOT/choice['path']
    if sha256(policy_path) != choice['sha256']:
        raise ValueError('Qualified checkpoint changed')
    policy = torch.load(policy_path, map_location='cpu', weights_only=False)
    if any(not torch.equal(value, policy['bridge']['owner'][name]) for name,value in owner.state_dict().items()
           if not name.startswith('investigation.')):
        raise ValueError('Qualified policy would change the retained predictor')
    owner.load_state_dict(policy['bridge']['owner'])
    if weight_hash(owner) != choice['weights']:
        raise ValueError('Policy weight identity differs from qualification')
    destination = ROOT/'checkpoints/SCFE-004'
    if (destination/'SELECTION.json').exists():
        existing, _ = load_selected(destination)
        if weight_hash(existing) != choice['weights']:
            raise ValueError('Preserve the different existing release')
        print('The identical packaged owner is already verified')
        return
    revisions = destination/'revisions'
    revisions.mkdir(parents=True, exist_ok=True)
    temporary = revisions/'inference.tmp'
    with temporary.open('xb') as handle:
        torch.save({'bridge': {'owner': owner.state_dict(), 'specification': owner.specification()},
                    'lineage': {'teacher_checkpoint': selected['sha256'],
                                'policy_checkpoint': choice['sha256'],
                                'policy_qualification': sha256(qualification/'final/RESULTS.json'),
                                'initial_weights': json.loads((source/'INITIAL.json').read_text())['weights'],
                                'comparison_registration': completed['registry_sha256']}}, handle)
    digest = sha256(temporary)
    revision = revisions/(digest+'.pt')
    temporary.rename(revision)
    manifest = {**selected, 'teacher_checkpoint_sha256': selected['sha256'],
                'source_checkpoint_sha256': choice['sha256'], 'weights': choice['weights'],
                'updates': policy['bridge']['updates'], 'parent': policy['parent'],
                'reward_training_attempts': choice['attempts'],
                'sha256': digest, 'revision': revision.name,
                'purpose': 'One taught owner with qualified learned investigation weights; full resumable state remains in source runs.'}
    write_json(destination/'SELECTION.json', manifest)
    restored, _ = load_selected(destination)
    if weight_hash(restored) != weight_hash(owner):
        raise ValueError('Export changed model parameters')
    write_json(destination/'MANIFEST.json', {'inference_checkpoint': manifest,
               'parameter_bytes': sum(p.numel()*p.element_size() for p in owner.parameters()),
               'file_bytes': revision.stat().st_size, 'original_training': str(source.relative_to(ROOT)),
               'reward_study': 'runs/CONNECTED-SCFE-rewards-scfe',
               'qualified_selection': 'runs/SCFE-006-policy-selection/SELECTION.json',
               'no_corpus_text_in_export': True,
               'retained_scope': 'Taught predictor is exactly retained; the 768-attempt policy qualified on a fresh 512-system cohort.'})
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
