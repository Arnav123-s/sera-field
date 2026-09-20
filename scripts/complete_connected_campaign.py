"""Sequential supervised reward training, frozen dual-owner evaluation and replay."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, write_json
from sera_field.study_registration import freeze_identity


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    data = ROOT/'local/CONNECTED-003-data-v1'
    plan = {'field': ROOT/'runs/CONNECTED-003-teaching-1103', 'scfe': ROOT/'runs/SCFE-004-teaching-1103'}
    output = ROOT/'runs/CONNECTED-SCFE-COMPARISON-001'
    output.mkdir(parents=True, exist_ok=True)
    reward_paths = {}
    for name, training in plan.items():
        completed = json.loads((training/'TEACHING_COMPLETE.json').read_text())
        if completed['attempted_batches'] != 12288:
            raise ValueError('Both owners must receive the frozen teaching budget')
        rewards = ROOT/'runs'/('CONNECTED-SCFE-rewards-'+name)
        reward_paths[name] = rewards
        receipt_path = rewards/'REWARD_COMPLETE.json'
        if not receipt_path.exists():
            subprocess.run([sys.executable, '-u', '-m', 'sera_field.study_inquiry',
                            '--training', str(training), '--output', str(rewards)], check=True)
        receipt = json.loads(receipt_path.read_text())
        selection = json.loads((training/'SELECTION.json').read_text())
        for arm in ('verified_reward', 'reward_disconnected'):
            current = json.loads((rewards/arm/'revisions/CURRENT.json').read_text())
            if receipt[arm]['attempts'] != 2048 or receipt[arm]['base'] != selection or receipt[arm]['revision'] != current:
                raise ValueError('Reward completion receipt disagrees with actual owner')
            if sha256(rewards/arm/'revisions'/current['revision']) != current['sha256']:
                raise ValueError('Reward checkpoint bytes changed')
    registry = output/'REGISTERED_FINAL_CANDIDATES.json'
    registered = {'protocol': sha256(ROOT/'protocols/SCFE-004.md'),
                  'candidates': {name: freeze_identity(training,reward_paths[name],data) for name,training in plan.items()}}
    if registry.exists():
        if json.loads(registry.read_text()) != registered:
            raise ValueError('Preserve the original final registration')
    else:
        write_json(registry, registered)
    for name, training in plan.items():
        final, replay = output/(name+'-final'), output/(name+'-replay')
        if not (final/'RESULTS.json').exists():
            subprocess.run([sys.executable, '-u', '-m', 'sera_field.study_evaluation',
                            '--training', str(training), '--rewards', str(reward_paths[name]),
                            '--data', str(data), '--output', str(final), '--registry', str(registry)], check=True)
        else:
            prior = json.loads((final/'FROZEN_CANDIDATES.json').read_text())
            if prior != registered['candidates'][name]:
                raise ValueError('Existing evaluation has a different frozen candidate')
            evidence = json.loads((final/'EVIDENCE.json').read_text())
            if any(sha256(final/file) != digest for file,digest in evidence.items()):
                raise ValueError('Existing raw evaluation changed')
        if not (replay/'REPLAY.json').exists():
            # A fresh interpreter replays every numerical result from frozen bytes.
            subprocess.run([sys.executable, '-u', '-m', 'sera_field.study_evaluation',
                            '--training', str(training), '--rewards', str(reward_paths[name]),
                            '--data', str(data), '--output', str(replay), '--registry', str(registry),
                            '--replay', str(final)], check=True)
    write_json(output/'COMPLETE.json', {'registry_sha256': sha256(registry),
                                      'independent_replays': {name: json.loads((output/(name+'-replay')/'REPLAY.json').read_text()) for name in plan},
                                      'results': {name: json.loads((output/(name+'-final')/'RESULTS.json').read_text()) for name in plan}})


if __name__ == '__main__':
    main()
