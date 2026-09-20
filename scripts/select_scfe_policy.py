"""Prospective selection of saved policies, fresh final qualification and replay."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from sera_field.model import weight_hash
from sera_field.records import sha256, write_json
from sera_field.study_evaluation import completed_stage, summarize_inquiry
from sera_field.study_inquiry import Investigator, load_selected
from sera_field.study_registration import freeze_identity

TRAINING = ROOT/'runs/SCFE-004-teaching-1103'
REWARDS = ROOT/'runs/CONNECTED-SCFE-rewards-scfe'
DATA = ROOT/'local/CONNECTED-003-data-v1'
OUTPUT = ROOT/'runs/SCFE-006-policy-selection'


def load_candidate(candidate):
    owner, teacher = load_selected(TRAINING)
    agent = Investigator(owner)
    path = ROOT/candidate['path']
    allowed = (REWARDS/'verified_reward/revisions').resolve()
    if path.resolve().parent != allowed or sha256(path) != candidate['sha256']:
        raise ValueError('Invalid saved policy identity')
    payload = torch.load(path, map_location='cpu', weights_only=False)
    if payload['progress']['predictor_sha'] != teacher['weights']:
        raise ValueError('Changed predictor ancestry')
    agent.book.restore(payload['bridge'])
    if weight_hash(agent.owner) != candidate['weights']:
        raise ValueError('Changed candidate parameters')
    base, _ = load_selected(TRAINING)
    if any(not torch.equal(value, base.state_dict()[name]) for name,value in agent.owner.state_dict().items()
           if not name.startswith('investigation.')):
        raise ValueError('Only learned decision parameters may differ')
    agent.owner.eval()
    agent.rng.manual_seed(95537)
    return agent


def candidate_bank():
    distinct = {}
    for path in sorted((REWARDS/'verified_reward/revisions').glob('*.pt')):
        if sha256(path) != path.stem:
            raise ValueError('Checkpoint bytes changed')
        payload = torch.load(path, map_location='cpu', weights_only=False)
        owner, _ = load_selected(TRAINING)
        owner.load_state_dict(payload['bridge']['owner'])
        weights = weight_hash(owner)
        row = {'path': path.relative_to(ROOT).as_posix(), 'sha256': path.stem,
               'weights': weights, 'attempts': payload['progress']['cursor']}
        if weights not in distinct or (row['attempts'], row['sha256']) < (distinct[weights]['attempts'], distinct[weights]['sha256']):
            distinct[weights] = row
    bank = sorted(distinct.values(), key=lambda r:(r['attempts'],r['weights']))
    if {r['attempts'] for r in bank} != set(range(0,2049,128)):
        raise ValueError('Expected the complete saved policy trajectory')
    return bank


@torch.no_grad()
def assess(candidate, split, policy='learned'):
    agent = load_candidate(candidate)
    before = weight_hash(agent.owner)
    rows = [agent.attempt(i, split=split, policy=policy, train=False) for i in range(512)]
    if weight_hash(agent.owner) != before:
        raise ValueError('Evaluation altered a frozen policy')
    return summarize_inquiry(rows), rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the shared numerical supervisor')
    torch.set_num_threads(1)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    freeze_path = OUTPUT/'FROZEN.json'
    source = {'script': sha256(__file__), 'protocol': sha256(ROOT/'protocols/SCFE-006-POLICY-SELECTION.md'),
               'runtime': freeze_identity(TRAINING, REWARDS, DATA),
               'development': {'split': 'SCFE-006-development-v1', 'seed':73113, 'cases':512},
               'final': {'split': 'SCFE-006-final-v1', 'seed':73113, 'cases':512}}
    if freeze_path.exists():
        frozen = json.loads(freeze_path.read_text())
        if frozen['sources'] != source:
            raise ValueError('The frozen experiment sources changed')
        bank = frozen['candidates']
    else:
        if args.replay:
            raise ValueError('No completed selection to replay')
        bank = candidate_bank()
        frozen = {'sources':source,'candidates':bank}
        write_json(freeze_path, frozen)
    selection_path = OUTPUT/'SELECTION.json'
    if selection_path.exists():
        selection = json.loads(selection_path.read_text())
        if selection['freeze_sha256'] != sha256(freeze_path) or selection['candidate'] not in bank:
            raise ValueError('Selection identity mismatch')
    else:
        if args.replay:
            raise ValueError('No selection to replay')
        development = OUTPUT/'development'
        development.mkdir(exist_ok=True)
        scored = []
        for candidate in bank:
            metrics = completed_stage(development, 'policy-'+candidate['weights'][:16],
                                      lambda: assess(candidate, source['development']['split']))
            scored.append({'candidate':candidate,'metrics':metrics})
        selected = min(scored,key=lambda r:(r['metrics']['after_mse'],r['candidate']['attempts'],r['candidate']['weights']))
        selection = {'candidate':selected['candidate'], 'development':scored,'freeze_sha256':sha256(freeze_path)}
        write_json(selection_path,selection)
    final = OUTPUT/('replay' if args.replay else 'final')
    final.mkdir(exist_ok=True)
    plan = {'selected':(selection['candidate'],'learned'), 'unchanged':(bank[0],'learned'),
             'last_update':(bank[-1],'learned'), 'analytic':(bank[0],'analytic'), 'random':(bank[0],'random')}
    selection_sha = sha256(selection_path)
    binding = final/'SELECTION_BINDING.json'
    if binding.exists() and json.loads(binding.read_text())['sha256'] != selection_sha:
        raise ValueError('Final selection changed')
    write_json(binding, {'sha256':selection_sha})
    metrics = {}
    for name,(candidate,policy) in plan.items():
        metrics[name] = completed_stage(final, name, lambda: assess(candidate,source['final']['split'],policy))
    def losses(name):
        return np.array([json.loads(line)['after_loss'] for line in (final/(name+'.jsonl')).read_text().splitlines()])
    baseline, selected = losses('unchanged'), losses('selected')
    difference = baseline-selected
    rng = np.random.default_rng(6006)
    means = np.array([rng.choice(difference,len(difference),replace=True).mean() for _ in range(2000)])
    interval = np.quantile(means,[.025,.975]).tolist()
    relative = float(1-selected.mean()/baseline.mean())
    qualified = bool(selection['candidate']['weights'] != bank[0]['weights'] and relative >= .05 and interval[0] > 0)
    result = {'metrics':metrics,'selected_training_attempts':selection['candidate']['attempts'],
               'paired_mean_improvement_95_percent_bootstrap':interval,
               'relative_mse_reduction_vs_unchanged':relative, 'qualified_for_promotion':qualified,
               'selection_sha256':selection_sha,'raw':{p.name:sha256(p) for p in final.glob('*.jsonl')}}
    write_json(final/'RESULTS.json',result)
    if args.replay:
        if result != json.loads((OUTPUT/'final/RESULTS.json').read_text()):
            raise ValueError('Fresh-process final replay differs')
        write_json(OUTPUT/'REPLAY.json',{'all_results_and_records_exact':True, 'selection_sha256':selection_sha})
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
