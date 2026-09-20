"""One frozen final opening and independent replay; no optimization code path."""
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import random
import re
import uuid

import numpy as np
import torch

from .credit_bridge import identity
from .model import weight_hash
from .records import sha256, write_json
from .study_data import ROOT, canonical_expression, expression_value, load_records
from .study_inquiry import Investigator, load_selected
from .study_training import pair_inputs, physical_batch
from .study_world import stable_seed
from .study_world import draw, trajectory
from .learned_motion import rollout
from .study_inquiry import observation_tensors
from .study_registration import freeze_identity, registered_candidate


def cohort(rows, count, salt):
    # Groups touched by selection are never described as untouched future groups,
    # including the unused tail when the last selected group crosses the cap.
    return sorted(rows, key=lambda r: (hashlib.sha256((salt + r['group']).encode()).hexdigest(),
                                       hashlib.sha256((salt + r['id']).encode()).hexdigest()))[:count]


def summarize_inquiry(rows):
    before = np.array([r['before_loss'] for r in rows])
    after = np.array([r['after_loss'] for r in rows])
    return {'n': len(rows), 'before_mse': float(before.mean()), 'after_mse': float(after.mean()),
            'mean_absolute_progress': float((before-after).mean()),
            'fraction_improved': float((after < before).mean()),
            'relative_mse_reduction': float(1 - after.mean()/before.mean()) if before.mean() > 0 else None,
            'original_goals_returned': sum(r['original_goal_returned'] for r in rows),
            'failed_actuators': sum(not r['intervention_receipt']['actuation_matched'] for r in rows),
            'probe_count': sum(r['cost']['probes_performed'] for r in rows)}


def expression_proposals(owner, question, values, count=5):
    logits = owner.math_logits([question], [values])[0]
    n = len(values)
    ranked = torch.argsort(logits.flatten(), descending=True)
    results, seen = [], set()
    probability = logits.flatten().softmax(-1)
    for index in ranked.tolist():
        op, rem = divmod(index, n*n)
        a, b = divmod(rem, n)
        try:
            value = expression_value(op, values[a], values[b])
        except ZeroDivisionError:
            continue
        canonical = canonical_expression(op, values[a], values[b])
        if canonical in seen:
            continue
        seen.add(canonical)
        results.append({'program': json.loads(canonical), 'result': str(value),
                        'probability': float(probability[index]), 'indices': [op, a, b],
                        'assumptions': 'binary rational expression over the supplied observed-number inventory'})
        if len(results) == count:
            break
    return results


@torch.no_grad()
def reading_evaluation(owner, rows, mode='full'):
    owner.mode = mode
    outputs = []
    for start in range(0, len(rows), 24):
        part = rows[start:start+24]
        scores = owner.rank([r['question'] for r in part], [r['options'] for r in part])
        for i, row in enumerate(part):
            order = scores[i, :len(row['options'])].argsort(descending=True).tolist()
            q = set(re.findall(r'\w+', row['question'].casefold()))
            lexical = [len(q & set(re.findall(r'\w+', option.casefold()))) / max(1, len(q)) for option in row['options']]
            baseline = int(np.argmax(lexical))
            outputs.append({'id': row['id'], 'source_sha256': row['source'], 'mode': mode,
                            'candidate_count': len(order), 'proposed_order': order, 'correct_targets': row['targets'],
                            'correct': order[0] in row['targets'],
                            'top3_contains_evidence': bool(set(order[:3]) & set(row['targets'])),
                            'lexical_baseline_correct': baseline in row['targets'],
                            'input_sha256': identity([row['question'], row['context']]),
                            'selected_source_span': row['spans'][order[0]],
                            'selected_source_sentence': row['options'][order[0]]})
    owner.mode = 'full'
    multi = [r for r in outputs if r['candidate_count'] > 1]
    summary = {'n': len(outputs), 'accuracy': sum(r['correct'] for r in outputs)/len(outputs),
               'multi_sentence_n': len(multi), 'multi_sentence_accuracy': sum(r['correct'] for r in multi)/max(1,len(multi)),
               'top3_evidence_recall': sum(r['top3_contains_evidence'] for r in outputs)/len(outputs),
               'lexical_baseline_accuracy': sum(r['lexical_baseline_correct'] for r in outputs)/len(outputs)}
    return summary, outputs


@torch.no_grad()
def math_evaluation(owner, rows):
    outputs = []
    for row in rows:
        proposals = expression_proposals(owner, row['question'], row['values'])
        op, a, b = row['target']
        expected = canonical_expression(op, row['values'][a], row['values'][b])
        numeric = [Fraction(x['result']) == Fraction(row['answer']) for x in proposals]
        matched = [json.dumps(x['program'], separators=(',', ':')) == expected for x in proposals]
        outputs.append({'id': row['id'], 'source_sha256': row['source'], 'proposals': proposals,
                        'answer': row['answer'], 'teacher_forced_steps': row['teacher_forced_steps'],
                        'original_one_step': row['original_one_step'], 'numeric_matches': numeric,
                        'human_expression_matches': matched, 'original_question_sha256': identity(row['question'])})
    def metrics(part):
        return {'n': len(part), 'numeric_top1': sum(r['numeric_matches'][0] for r in part)/max(1,len(part)),
                'numeric_top5': sum(any(r['numeric_matches']) for r in part)/max(1,len(part)),
                'human_expression_top1': sum(r['human_expression_matches'][0] for r in part)/max(1,len(part)),
                'human_expression_top5': sum(any(r['human_expression_matches']) for r in part)/max(1,len(part))}
    return {'all_continuations': metrics(outputs),
            'original_one_step': metrics([r for r in outputs if r['original_one_step']]),
            'scope': 'Executable binary arithmetic proposals; teacher-forced continuations reported separately.'}, outputs


@torch.no_grad()
def pair_evaluation(owner, rows):
    tracks = defaultdict(list)
    for row in rows:
        tracks[row['track']].append(row)
    summary, results = {}, []
    for track, bank in sorted(tracks.items()):
        selected = cohort(bank, 256, 'CONNECTED-003-final-pairs-v1')
        if len(bank) < 4:
            summary[track] = {'n': len(bank), 'status': 'Insufficient independent final examples'}
            continue
        rng = random.Random(stable_seed('final-pairs', track))
        correct = 0
        for start in range(0, len(selected), 24):
            part = selected[start:start+24]
            questions, options, labels = pair_inputs(part, selected, rng)
            scores = owner.rank(questions, options)
            choices = scores.argmax(-1).tolist()
            for row, choice, label, candidates in zip(part, choices, labels, options):
                valid = choice == label[0]
                correct += valid
                results.append({'id': row['id'], 'track': track, 'source_sha256': row['source'],
                                'selected': choice, 'target': label[0], 'correct': valid,
                                'candidate_hashes': [identity(x) for x in candidates]})
        summary[track] = {'n': len(selected), 'four_candidate_association_accuracy': correct/len(selected)}
    return summary, results


def load_investigator(training, reward_root, arm):
    owner, _ = load_selected(training)
    agent = Investigator(owner, reward=arm != 'reward_disconnected')
    agent.resume(Path(reward_root) / arm / 'revisions')
    agent.rng.manual_seed(83119)
    return agent


def dump_rows(path, rows):
    with Path(path).open('x', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')


def completed_stage(output, name, produce):
    """Resume committed components exactly; retain incomplete attempts separately."""
    output = Path(output)
    journal = output / 'stages' / (name + '.json')
    raw = output / (name + '.jsonl')
    if journal.exists():
        saved = json.loads(journal.read_text())
        if not raw.exists() or sha256(raw) != saved['raw_sha256']:
            raise ValueError('Committed final records changed: ' + name)
        return saved['metrics']
    if raw.exists():
        abandoned = output / 'incomplete' / uuid.uuid4().hex
        abandoned.mkdir(parents=True, exist_ok=False)
        raw.rename(abandoned / raw.name)
    metrics, rows = produce()
    dump_rows(raw, rows)
    write_json(journal, {'metrics': metrics, 'raw_sha256': sha256(raw)})
    print(json.dumps({'completed_final_component': name, 'records': len(rows)}), flush=True)
    return metrics


def evaluate(training, rewards, data, output, *, registry, replay=None):
    output = Path(output)
    rewards = Path(rewards)
    freeze = registered_candidate(training, rewards, data, registry)
    identities = freeze['reward_arms']
    output.mkdir(parents=True, exist_ok=True)
    frozen_path = output / 'FROZEN_CANDIDATES.json'
    if frozen_path.exists() and json.loads(frozen_path.read_text()) != freeze:
        raise ValueError('Existing final belongs to another frozen candidate')
    if replay is not None:
        old = json.loads((Path(replay) / 'FROZEN_CANDIDATES.json').read_text())
        if freeze != old:
            raise ValueError('Replay must use the same frozen source, evaluator and candidate identities')
    write_json(frozen_path, freeze)
    opening = Path(data) / 'FINAL_OPENING_CONNECTED_003.json'
    registration_sha = sha256(registry)
    if not opening.exists():
        if replay is not None:
            raise ValueError('Nothing was evaluated to replay')
        with opening.open('x', encoding='utf-8') as handle:
            json.dump({'registered_study_sha256': registration_sha, 'first_output': str(output.resolve())}, handle, indent=2)
    else:
        if json.loads(opening.read_text())['registered_study_sha256'] != registration_sha:
            raise ValueError('The final cohort is already bound to another registered study')
    # First access to final rows for capability scoring occurs after the freeze above.
    owner, selected = load_selected(training)
    owner.eval()
    reading = cohort(load_records(data, 'sealed', 'reading'), 1024, 'CONNECTED-003-final-reading-v1')
    mathematics = cohort(load_records(data, 'sealed', 'math'), 512, 'CONNECTED-003-final-math-v1')
    pairs = load_records(data, 'sealed', 'pairs')
    used_groups = {r['group'] for r in reading + mathematics}
    pair_tracks = defaultdict(list)
    for row in pairs:
        pair_tracks[row['track']].append(row)
    for track, bank in pair_tracks.items():
        used_groups.update(r['group'] for r in cohort(bank, 256, 'CONNECTED-003-final-pairs-v1'))
    write_json(output / 'OPENED_GROUPS.json', sorted(used_groups))
    summary = {'reading': {}, 'physics': {}, 'retention': {}}
    for mode in ('full', 'no_imagination', 'no_loop'):
        summary['reading'][mode] = completed_stage(output, 'reading-' + mode,
                                                    lambda: reading_evaluation(owner, reading, mode))
    summary['math'] = completed_stage(output, 'mathematics', lambda: math_evaluation(owner, mathematics))
    summary['human_associations'] = completed_stage(output, 'human-associations', lambda: pair_evaluation(owner, pairs))
    @torch.no_grad()
    def forward_cases():
        rows = []
        for index in range(256):
            environment, support, query, truth = draw(1103, index, 'final-forward-v1')
            situation = owner.world(*observation_tensors(support))
            prediction = owner.consequences(situation['coefficients'], torch.from_numpy(query)[None])[0]
            mse = float((prediction.mean(0) - torch.from_numpy(truth)).square().mean())
            rows.append({'index': index, 'support': support.tolist(), 'queries': query.tolist(),
                         'hypotheses': prediction.tolist(), 'independent_outcomes': truth.tolist(), 'mse': mse})
        return {'n': len(rows), 'mse': float(np.mean([r['mse'] for r in rows]))}, rows
    summary['physics']['forward'] = completed_stage(output, 'physics-forward', forward_cases)
    @torch.no_grad()
    def motion_cases():
        motion_rows = []
        for index in range(64):
            environment, support, queries, _ = draw(1103, index, 'final-motion-transfer-v1', with_targets=False)
            coefficients = owner.world(*observation_tensors(support))['coefficients'][0].numpy()
            velocity, force = map(float, queries[0])
            imagined = rollout(coefficients, velocity, force, 1.)
            measured = trajectory(environment, velocity=velocity, force_per_mass=force, duration=1.)
            error = float(np.mean((np.asarray(imagined['position_velocity_mean'])-measured)**2)) if imagined['status']=='completed' else None
            motion_rows.append({'index': index, 'imagined': imagined, 'independent_DOP853_outcome': measured,
                                'position_velocity_mse': error})
        valid_motion = [r['position_velocity_mse'] for r in motion_rows if r['position_velocity_mse'] is not None]
        return {'n': 64, 'completed_rollouts': len(valid_motion),
                'mean_position_velocity_mse': float(np.mean(valid_motion)) if valid_motion else None,
                'duration': 1., 'taught_target': 'acceleration; trajectories independently evaluated'}, motion_rows
    summary['physics']['motion_transfer'] = completed_stage(output, 'motion-transfer', motion_cases)
    for policy in ('verified_reward', 'reward_disconnected', 'random', 'analytic'):
        arm = policy if policy in identities else 'verified_reward'
        agent = load_investigator(training, rewards, arm)
        control = policy if policy in ('random', 'analytic') else 'learned'
        @torch.no_grad()
        def inquiry_cases():
            before_hash = weight_hash(agent.owner)
            rows = [agent.attempt(i, split='final-inquiry-v1', policy=control, train=False) for i in range(256)]
            if weight_hash(agent.owner) != before_hash:
                raise ValueError('Final evaluation changed model weights')
            return summarize_inquiry(rows), rows
        summary['physics'][policy] = completed_stage(output, 'inquiry-' + policy, inquiry_cases)
        if policy in identities:
            preserved = all(torch.equal(value, owner.state_dict()[name]) for name, value in agent.owner.state_dict().items()
                            if not name.startswith('investigation.'))
            summary['retention'][policy] = {'non_policy_parameters_exactly_retained': preserved,
                                           'method': 'Predictor frozen during this controlled policy study'}
    agent = load_investigator(training, rewards, 'verified_reward')
    @torch.no_grad()
    def omitted_cases():
        rows = [agent.attempt(i, split='final-omitted-v1', train=False, omitted=True) for i in range(64)]
        metrics = summarize_inquiry(rows)
        metrics['mean_model_spread'] = float(np.mean([r['model_spread'] for r in rows]))
        return metrics, rows
    summary['physics']['omitted_mechanism'] = completed_stage(output, 'inquiry-omitted', omitted_cases)
    write_json(output / 'RESULTS.json', summary)
    evidence = {p.name: sha256(p) for p in sorted(output.glob('*.jsonl'))}
    write_json(output / 'EVIDENCE.json', evidence)
    if replay is not None:
        old_summary = json.loads((Path(replay)/'RESULTS.json').read_text())
        old_evidence = json.loads((Path(replay)/'EVIDENCE.json').read_text())
        if old_summary != summary or old_evidence != evidence:
            raise ValueError('Independent replay mismatch; preserve both outputs')
        write_json(output / 'REPLAY.json', {'all_metrics_and_raw_records_exact': True, 'original': str(replay)})
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--training', type=Path, required=True)
    parser.add_argument('--rewards', type=Path, required=True)
    parser.add_argument('--data', type=Path, default=ROOT/'local/CONNECTED-003-data-v1')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replay', type=Path)
    parser.add_argument('--registry', type=Path, required=True)
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the resource supervisor')
    torch.set_num_threads(1)
    evaluate(args.training, args.rewards, args.data, args.output, registry=args.registry, replay=args.replay)
