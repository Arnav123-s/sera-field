"""Prospective source and checkpoint registration without loading model runtimes."""
import json
from pathlib import Path

from .records import sha256

ROOT = Path(__file__).resolve().parents[1]


def freeze_identity(training, rewards, data):
    selected = json.loads((Path(training) / 'SELECTION.json').read_text())
    rewards = Path(rewards)
    identities = {arm: json.loads((rewards / arm / 'revisions/CURRENT.json').read_text())
                  for arm in ('verified_reward', 'reward_disconnected')}
    modules = ['grounded_owner', 'clifford_sheaf', 'scfe_owner', 'study_world', 'study_inquiry',
               'study_evaluation', 'study_registration', 'study_data', 'study_training',
               'learned_motion', 'model', 'gauge', 'situation_core', 'credit_bridge', 'records']
    return {'teaching': selected, 'reward_arms': identities,
            'data_manifest': sha256(Path(data) / 'MANIFEST.json'),
            'split_audit': sha256(Path(data) / 'SPLIT_AUDIT.json'),
            'evaluator': sha256(ROOT / 'sera_field/study_evaluation.py'),
            'runtime_sources': {name: sha256(ROOT / 'sera_field' / (name + '.py')) for name in modules},
            'cohorts': {'reading': 1024, 'mathematics': 512, 'pairs_per_track': 256,
                        'physics_forward': 256, 'inquiry': 256, 'omitted': 64, 'motion_transfer': 64},
            'comparison': 'Reward arms matched at 2048 attempted episodes; field ablations are inference sensitivities.',
            'cohort_construction': 'Stable group hash then row hash; partial touched groups are excluded from future independent comparisons.',
            'reserved': 'Wholly unselected human final groups and physics split future-comparison-004 remain untouched by scoring.'}


def registered_candidate(training, rewards, data, registry):
    freeze = freeze_identity(training, rewards, data)
    registered = json.loads(Path(registry).read_text())
    if freeze not in registered['candidates'].values():
        raise ValueError('Candidate not in the prospective, joint final registration')
    return freeze
