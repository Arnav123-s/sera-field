"""Learn an update procedure through the continuing owner's actual field."""
import argparse
import copy
import json
import os
from pathlib import Path

import torch

from .credit_bridge import CreditBridge
from .gauge import adjoint_rotations
from .history_owner import HistoryOwner, extend_history, history_identity
from .model import weight_hash
from .records import sha256, write_json, utc
from .semantic_training import load_semantic
from .study_data import ROOT

STUDY = ROOT / 'runs/HISTORY-016'
DATA = ROOT / 'local/HISTORY-016-data-v1'
PARENT = ROOT / 'checkpoints/SEMANTIC-015'
ARMS = ('learned', 'initialized', 'no_history', 'reciprocal', 'equal_rates')


def read(path):
    return json.loads(Path(path).read_text())


def rows(split):
    with (DATA / (split + '.jsonl')).open(encoding='utf-8') as handle:
        return [json.loads(line) for line in handle]


def probability(owner, row):
    return owner.semantic([row['premise']], [row['hypothesis']]).softmax(-1).mean(1)[0]


def annotation_loss(distribution, row):
    return -distribution[row['target']].clamp_min(1e-12).log()


def episode(owner, record, *, arm='learned'):
    """Four annotated supports; the query label cannot affect the proposed state.

    Support fitting progress informs the opposing traces. Independent query
    improvement is assessed only after every support has been processed.
    """
    field = owner.field
    saved_preview, saved_disconnected, saved_tracking = field.history_preview, field.history_disconnected, field.track_boundary_credit
    state = field.continuum.empty(1)
    diagnostics = []; supports = []
    try:
        field.history_preview = state
        field.history_disconnected = arm == 'no_history'
        field.track_boundary_credit = True
        baseline = probability(owner, record['query'])
        baseline_loss = annotation_loss(baseline, record['query'])
        transport = adjoint_rotations(field.links).transpose(-1, -2)
        for support in record['supports']:
            field.history_preview = state
            before = probability(owner, support)
            support_loss = annotation_loss(before, support)
            derivative, = torch.autograd.grad(support_loss, field.last_boundary, retain_graph=True)
            stimulus = -derivative.detach().mean(0, keepdim=True)
            stimulus = stimulus / (.1 + stimulus.square().sum((-2, -1), keepdim=True).sqrt())
            proposal, diagnostic = field.continuum.advance(state, stimulus, stimulus.new_zeros(1), transport,
                reciprocal=arm == 'reciprocal', equal_rates=arm == 'equal_rates')
            field.history_preview = proposal
            after = probability(owner, support)
            after_loss = annotation_loss(after, support)
            practice_progress = (support_loss.detach() - after_loss.detach()) / (1 + support_loss.detach())
            # This is same-example supervised fitting evidence, not independent
            # transfer credit. Query evidence is withheld until below.
            proposal['marks'] = .95 * state['marks'] + .05 * torch.stack(
                (practice_progress.clamp_min(0), (-practice_progress).clamp_min(0)))[None]
            state = proposal; diagnostics.append(diagnostic)
            supports.append({'id': support['id'], 'source_group': support['source_group'],
                'before_loss': float(support_loss.detach()), 'after_loss': float(after_loss.detach()),
                'annotation_fitting_progress': float(practice_progress),
                'relaxation_mass_error': float(diagnostic['relaxation_mass_error'].detach().abs().max()),
                'activity': float(diagnostic['activity'].detach()),
                'fast_rate': float(diagnostic['fast_rate'].detach()), 'slow_rate': float(diagnostic['slow_rate'].detach()),
                'passive_energy_before': diagnostic['passive_energy_before'].detach().tolist(),
                'passive_energy_after': diagnostic['passive_energy_after'].detach().tolist(),
                'spectral_length_before': diagnostic['spectral_length_before'].detach().tolist(),
                'spectral_length_after': diagnostic['spectral_length_after'].detach().tolist(),
                'spatial_power_after': diagnostic['spatial_power_after'].detach().tolist(),
                'current_signal_retrieval_mse': diagnostic['current_signal_retrieval_mse'].detach().tolist(),
                'write_mass_change': diagnostic['write_mass_change'].detach().tolist()})
        field.history_preview = state
        returned = probability(owner, record['query'])
        query_loss = annotation_loss(returned, record['query'])
        regularizer = torch.stack([r['reverse_kl'].mean() for r in diagnostics]).mean()
        result = {'id': record['id'], 'query_id': record['query']['id'],
            'query_group': record['query']['source_group'], 'target': record['query']['target'],
            'before_probability': baseline.detach().tolist(), 'after_probability': returned.detach().tolist(),
            'before_loss': float(baseline_loss.detach()), 'after_loss': float(query_loss.detach()),
            'before_correct': int(baseline.argmax()) == record['query']['target'],
            'after_correct': int(returned.argmax()) == record['query']['target'],
            'supports': supports, 'conditional_history_id': history_identity(state),
            'reverse_kl': float(regularizer.detach()), 'original_goal_returned': True,
            'verified_progress_reward': float(baseline_loss.detach() - query_loss.detach()),
            'independent_query_grade': float((baseline_loss.detach() - query_loss.detach()) / (1 + baseline_loss.detach())),
            'support_signal': 'first-order derivative of supplied human annotation loss; detached for procedure learning'}
        # A fixed before-loss baseline makes this negative verified-progress
        # reward. Its gradient equals query cross entropy plus the stated
        # regularizer, rather than rewarding repeated easy success counts.
        return query_loss - baseline_loss.detach() + .0001 * regularizer, result, state
    finally:
        field.history_preview = saved_preview; field.history_disconnected = saved_disconnected
        field.track_boundary_credit = saved_tracking


def assess(owner, bank, *, arm='learned'):
    cases = []
    for row in bank:
        _, result, _ = episode(owner, row, arm=arm)
        cases.append(result)
    return {'n': len(cases),
        'before_loss': sum(r['before_loss'] for r in cases) / len(cases),
        'loss': sum(r['after_loss'] for r in cases) / len(cases),
        'before_accuracy': sum(r['before_correct'] for r in cases) / len(cases),
        'accuracy': sum(r['after_correct'] for r in cases) / len(cases)}, cases


def load_history(root):
    root = Path(root); selected = read(root / 'SELECTION.json')
    path = root / 'revisions' / selected['revision']
    if path.resolve().parent != (root / 'revisions').resolve() or sha256(path) != selected['sha256']:
        raise ValueError('History revision identity changed')
    payload = torch.load(path, map_location='cpu', weights_only=False)
    spec = dict(payload['bridge']['specification'])
    if spec.pop('type') != 'continuous-history-016':
        raise ValueError('Wrong history owner specification')
    owner = HistoryOwner(**spec); owner.load_state_dict(payload['bridge']['owner'])
    if weight_hash(owner) != selected['weights']:
        raise ValueError('History weights changed')
    for name, p in owner.named_parameters():
        p.requires_grad_(name.startswith(('field.continuum.', 'field.raw_history_gain')))
    return owner, selected


def train():
    if not read(ROOT / 'reports/SEMANTIC-015/QUALIFICATION.json')['all_gates']:
        raise ValueError('Preserve and repair the semantic parent before continuing this package')
    root = STUDY / 'learned'; root.mkdir(parents=True, exist_ok=True)
    if (root / 'COMPLETE.json').exists():
        load_history(root); return
    parent, parent_selection = load_semantic(PARENT); owner = extend_history(parent)
    if (root / 'PARENT.json').exists() and read(root / 'PARENT.json') != parent_selection:
        raise ValueError('History parent changed while resuming')
    source = sha256(DATA / 'MANIFEST.json')
    book = CreditBridge(owner, source_hashes=[source], verifier_hashes=[sha256(__file__)])
    optimizer = torch.optim.AdamW([p for p in owner.parameters() if p.requires_grad], lr=.001, weight_decay=.0001)
    training = rows('train'); development = rows('development')
    if len(training) != 2048 or len(development) != 128:
        raise ValueError('The prepared finite curriculum changed')
    step = 0; current = None; best = None; history = []
    if (root / 'revisions/CURRENT.json').exists():
        saved = book.load_current(root / 'revisions'); current = saved['sha256']; p = saved['progress']
        if p['source'] != source or p['parent'] != parent_selection:
            raise ValueError('History source/parent changed')
        step = p['step']; history = p['development']; optimizer.load_state_dict(p['optimizer'])
        best = read(root / 'SELECTION.json')
        # A crash between committing a newly best checkpoint and updating its
        # selection pointer must not discard the completed assessment.
        if history[-1]['step'] == step and (history[-1]['loss'], -history[-1]['accuracy']) < (best['loss'], -best['accuracy']):
            best = {**read(root / 'revisions/CURRENT.json'), **history[-1]}
            write_json(root / 'SELECTION.json', best)
    def save():
        nonlocal current
        pointer = book.commit(root / 'revisions', expected_parent=current, progress={
            'step': step, 'optimizer': optimizer.state_dict(), 'source': source,
            'parent': parent_selection, 'development': history})
        current = pointer['sha256']; return pointer
    if best is None:
        metrics, _ = assess(owner, development); history.append({'step': 0, **metrics})
        best = {**save(), 'step': 0, **metrics}
        write_json(root / 'SELECTION.json', best); write_json(root / 'INITIAL.json', best)
        write_json(root / 'PARENT.json', parent_selection)
    with (root / ('episodes-' + os.environ['SERA_FIELD_SUPERVISED'] + '.jsonl')).open('x', encoding='utf-8') as log:
        while step < len(training):
            optimizer.zero_grad(set_to_none=True)
            loss, result, _ = episode(owner, training[step])
            if not torch.isfinite(loss):
                raise ValueError('Preserve last committed history state; nonfinite objective')
            loss.backward(); torch.nn.utils.clip_grad_norm_(owner.parameters(), 1., error_if_nonfinite=True)
            optimizer.step(); step += 1
            log.write(json.dumps({'step': step, 'objective': float(loss.detach()), **result}) + '\n')
            metrics = None
            if step % 256 == 0:
                metrics, _ = assess(owner, development); history.append({'step': step, **metrics})
            if step % 64 == 0:
                pointer = save()
                if metrics and (metrics['loss'], -metrics['accuracy']) < (best['loss'], -best['accuracy']):
                    best = {**pointer, 'step': step, **metrics}; write_json(root / 'SELECTION.json', best)
                log.flush()
                write_json(root / 'PROGRESS.json', {'step': step, 'target': len(training), 'utc': utc()})
                print(json.dumps({'step': step, 'objective': float(loss.detach())}), flush=True)
            if (STUDY / 'PAUSE_REQUEST.json').exists():
                save(); write_json(root / 'PAUSED.json', {'step': step}); return
    write_json(root / 'COMPLETE.json', {'episodes': step, 'support_presentations': step * 4,
        'query_presentations': step, 'selected': best, 'development': history,
        'source': source, 'parent': parent_selection, 'factual_training_captures': 0})


def register():
    if (STUDY / 'FINAL_REGISTRATION.json').exists():
        return
    if not (STUDY / 'learned/COMPLETE.json').exists():
        raise ValueError('Complete history teaching before registering its final')
    manifest = read(DATA / 'MANIFEST.json')
    actual_old = read(ROOT / 'runs/SEMANTIC-015/FINAL_REGISTRATION.json')
    if set(manifest['previous_final_ids']) != set(actual_old['ids']):
        raise ValueError('The actual preceding final differs from the prospectively excluded cohort')
    write_json(STUDY / 'FINAL_REGISTRATION.json', {'selected': sha256(STUDY / 'learned/SELECTION.json'),
        'source': sha256(DATA / 'MANIFEST.json'), 'protocol': sha256(ROOT / 'protocols/HISTORY-016.md'),
        'query_ids': manifest['partitions']['sealed']['query_ids'],
        'prior_final_groups_excluded': True, 'created_utc': utc()})


def evaluate(arm, replay=False):
    registered = read(STUDY / 'FINAL_REGISTRATION.json')
    if sha256(STUDY / 'learned/SELECTION.json') != registered['selected'] or sha256(DATA / 'MANIFEST.json') != registered['source']:
        raise ValueError('Frozen history assessment identity changed')
    if arm == 'initialized':
        parent, _ = load_semantic(PARENT); owner = extend_history(parent); selection = read(STUDY / 'learned/INITIAL.json')
        if weight_hash(owner) != selection['weights']:
            raise ValueError('Initial history weights changed')
    else:
        owner, selection = load_history(STUDY / 'learned')
    owner.eval(); before = weight_hash(owner)
    destination = STUDY / ('replay' if replay else 'final') / arm
    if (destination / 'RESULTS.json').exists():
        return
    bank = rows('sealed')
    if [r['query']['id'] for r in bank] != registered['query_ids']:
        raise ValueError('History final query identities changed')
    metrics, cases = assess(owner, bank, arm=arm)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / 'cases.jsonl'
    path.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in cases), encoding='utf-8')
    metrics.update(arm=arm, selection=selection, cases_sha256=sha256(path),
                   weights_before=before, weights_after=weight_hash(owner), factual_captures=0, final_parameter_updates=0)
    assert metrics['weights_before'] == metrics['weights_after']
    write_json(destination / 'RESULTS.json', metrics); print(json.dumps(metrics), flush=True)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=('train', 'register', 'evaluate'))
    parser.add_argument('--arm', choices=ARMS, default='learned'); parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1); STUDY.mkdir(parents=True, exist_ok=True)
    if args.action == 'train': train()
    elif args.action == 'register': register()
    else: evaluate(args.arm, args.replay)


if __name__ == '__main__':
    main()
