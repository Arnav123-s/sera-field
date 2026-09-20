"""Audit selected owner lineage and exposure without changing learned state."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch
from sera_field.records import sha256, write_json
from sera_field.study_inquiry import load_selected


def unique_tensor_bytes(value):
    storage = {}
    def inspect(item):
        if torch.is_tensor(item):
            blob = item.untyped_storage()
            storage[blob.data_ptr()] = blob.nbytes()
        elif isinstance(item, dict):
            for child in item.values():
                inspect(child)
        elif isinstance(item, (tuple, list)):
            for child in item:
                inspect(child)
    inspect(value)
    return sum(storage.values())


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1)
    reports = ROOT/'reports/CONNECTED-003'
    result = {}
    for name, directory in [('field','CONNECTED-003-teaching-1103'), ('scfe','SCFE-004-teaching-1103')]:
        root = ROOT/'runs'/directory
        owner, selection = load_selected(root)
        payload = torch.load(root/'revisions'/selection['revision'], map_location='cpu', weights_only=False)
        progress = payload['progress']
        initial = json.loads((root/'INITIAL.json').read_text())
        entire = json.loads((root/'TEACHING_COMPLETE.json').read_text())
        lineage = []
        digest = selection['sha256']
        while digest:
            path = root/'revisions'/(digest+'.pt')
            if sha256(path) != digest:
                raise ValueError('Broken checkpoint ancestry')
            checkpoint = torch.load(path, map_location='cpu', weights_only=False)
            lineage.append({'revision': path.name, 'step': checkpoint['progress']['step'],
                            'parent': checkpoint['parent']})
            digest = checkpoint['parent']
        if lineage[-1]['revision'] != initial['revision']:
            raise ValueError('Selection did not descend from the recorded fresh initialization')
        result[name] = {'specification': owner.specification(), 'initial': initial,
                        'selected': selection, 'selected_example_exposures': progress['exposures'],
                        'selected_unique_human_records': len(progress['seen']),
                        'selected_unique_simulated_systems': progress['physics_cursor'],
                        'selected_development': next(r for r in progress['development'] if r['step'] == selection['step']),
                        'entire_run': entire, 'selected_ancestry': lineage,
                        'parameters': sum(p.numel() for p in owner.parameters()),
                        'parameter_bytes': sum(p.numel()*p.element_size() for p in owner.parameters()),
                        'field_parameter_bytes': sum(p.numel()*p.element_size() for p in owner.field.parameters()),
                        'optimizer_tensor_bytes': unique_tensor_bytes(progress['optimizer']),
                        'core_links_l2_change': float((owner.field.links.detach()-checkpoint['bridge']['owner']['field.links']).norm()),
                        'core_prior_l2_change': float((owner.field.prior.detach()-checkpoint['bridge']['owner']['field.prior']).norm()),
                        'single_field_state_bytes': owner.config['nodes'] * (8 if name=='scfe' else 3) * 4,
                        'state_scope': 'One field state only, excluding inputs, branches, vocabulary, optimizer, tapes and Python storage.'}
    comparison = ROOT/'runs/CONNECTED-SCFE-COMPARISON-001'
    for name in result:
        directory = comparison/(name+'-final')
        evidence = json.loads((directory/'EVIDENCE.json').read_text())
        if any(sha256(directory/file) != digest for file, digest in evidence.items()):
            raise ValueError('Final evidence bytes changed')
        result[name]['final'] = json.loads((directory/'RESULTS.json').read_text())
        result[name]['replay'] = json.loads((comparison/(name+'-replay')/'REPLAY.json').read_text())
        rewards = ROOT/'runs'/('CONNECTED-SCFE-rewards-'+name)
        reward_summary = {}
        for arm in ('verified_reward','reward_disconnected'):
            rows = [json.loads(line) for path in sorted((rewards/arm).glob('episodes-*.jsonl'))
                    for line in path.read_text().splitlines()]
            events = [r['event'] for r in rows if r['event'] and r['event']['accepted']]
            reward_summary[arm] = {'attempts_including_retries': len(rows),
                                   'accepted_assessments': len(events),
                                   'rejected_assessments': len(rows)-len(events),
                                   'positive_reward_events': sum(e['reward']>0 for e in events),
                                   'negative_reward_events': sum(e['reward']<0 for e in events),
                                   'novel_contribution_bonus_events': sum(e['bonus']>0 for e in events),
                                   'actual_weight_changes': sum(e['weights_changed'] for e in events)}
        result[name]['reward_training'] = reward_summary
    write_json(reports/'LEARNED_EVIDENCE.json', result)
    print(json.dumps({name: {'selected': item['selected']['step'], 'parameters': item['parameters'],
                              'selected_exposures': sum(item['selected_example_exposures'].values()),
                              'reward_training': item['reward_training']} for name,item in result.items()}, indent=2))


if __name__ == '__main__':
    main()
