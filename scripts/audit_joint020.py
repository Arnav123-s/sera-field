"""Independent arithmetic, teaching, reward contrast, retention and provenance."""
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import numpy as np
import torch
from sera_field.joint_data import JointData
from sera_field.joint_training import cycle, STUDY
from sera_field.native_training import load_native, read, assess
from sera_field.records import sha256, write_json

REPORT = ROOT / 'reports/JOINT-020'


def case_records(route, cohort):
    return [json.loads(line) for line in (STUDY / 'final' / route / cohort / 'cases.jsonl').read_text().splitlines()]


def interval(values, *, seed):
    grouped = defaultdict(list)
    for group, value in values:
        grouped[group].append(value)
    sums = np.array([sum(v) for v in grouped.values()]); counts = np.array([len(v) for v in grouped.values()])
    rng = np.random.default_rng(seed); samples = []
    for _ in range(2000):
        indices = rng.integers(0, len(sums), len(sums))
        samples.append(float(sums[indices].sum()/counts[indices].sum()))
    return {'mean': float(sums.sum()/counts.sum()), '95_percent_interval': np.quantile(samples, [.025, .975]).tolist(),
            'premise_groups': len(sums), 'rows': int(counts.sum()), 'resamples': 2000,
            'scope': 'Fixed learned checkpoints; evaluation group sampling, not training seed variability.'}


def decimal_outcome(teacher, force, velocity):
    with localcontext() as context:
        context.prec = 50
        f, v, mass, drag, offset = map(lambda x: Decimal(str(x)),
            (force, velocity, teacher['mass'], teacher['drag'], teacher['offset']))
        resistance = drag*v*(abs(v) if teacher['quadratic'] else Decimal(1))
        return float(f/mass-resistance+offset)


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1); data = JointData(); sources = read(STUDY / 'SOURCES.json')
    source_checks = {p: sha256(ROOT / p) == digest for p, digest in sources['implementation'].items()}
    source_checks['protocol'] = sha256(ROOT / 'protocols/JOINT-020.md') == sources['protocol_sha256']
    from sera_field.native_data import GENRE, fixed
    native_registration = read(ROOT / 'reports/NATIVE-019/FINAL_REGISTRATION.json')
    for cohort in ('matched', 'mismatched'):
        path = GENRE / ('sealed_' + cohort + '.jsonl')
        old_ids = set(native_registration['cohorts'][cohort]['ids'])
        old_rows = fixed(path, 4096, 'GENRE-017-final-' + cohort)
        prior_groups = {r['source_group'] for r in old_rows}
        with path.open(encoding='utf-8') as handle:
            for line in handle:
                row = json.loads(line)
                if row['id'] in old_ids:
                    prior_groups.add(row['source_group'])
        source_checks['fresh_'+cohort+'_groups'] = not (prior_groups & set(sources['finals'][cohort]['groups']))
    training = {}; orders = {}; exposure_checks = {}; raw_errors = []
    for arm in ('credited', 'withheld'):
        path = STUDY / arm / 'training.jsonl'; logs = [json.loads(line) for line in path.read_text().splitlines()]
        if len(logs) != 1024 or [r['cycle'] for r in logs] != list(range(1, 1025)):
            raise ValueError('Incomplete or repeated teaching receipts')
        counts = Counter(); primary_ids = set(); measures = 0; signed = 0.
        orders[arm] = []
        for row in logs:
            counts['joint'] += len(row['cases']); counts[row['rehearsal']['kind']] += len(row['rehearsal']['ids'])
            for c in row['cases']:
                primary_ids.add(c['source_id']); measures += c['performed']; signed += c['signed_progress']
            orders[arm].append({'joint': [(c['id'], c['action'], c['actual'], c['behavior_probability']) for c in row['cases']],
                                'rehearsal': row['rehearsal']['ids']})
        complete = read(STUDY / arm / 'COMPLETE.json')
        exposure_checks[arm] = dict(counts) == complete['exposures'] and sum(counts.values()) == 32768
        training[arm] = {'cycles': len(logs), 'optimizer_updates': complete['optimizer_updates'],
                         'presentations': dict(counts), 'distinct_joint_human_rows': len(primary_ids),
                         'observed_probes': measures, 'summed_signed_progress': signed,
                         'log_sha256': sha256(path), 'selection': complete['selected']}
    first = read(STUDY / 'credited/INITIAL.json')
    initial, _, _ = load_native(STUDY / 'credited', pointer='INITIAL.json')
    selected, chosen, _ = load_native(STUDY / 'credited')
    base = dict(initial.named_parameters())
    changes = {name: float((p.detach()-base[name].detach()).double().square().sum().sqrt())
               for name, p in selected.named_parameters()}
    initial.zero_grad(set_to_none=True)
    loss, _, parts = cycle(initial, data.lesson(0), training=True, reward=True)
    loss.backward()
    norm = torch.nn.utils.clip_grad_norm_(initial.parameters(), 1., error_if_nonfinite=True)
    first_log = json.loads((STUDY / 'credited/training.jsonl').open().readline())
    first_checks = {'loss': abs(float(loss.detach())-first_log['loss']) < 1e-6,
                    'gradient_norm': abs(float(norm)-first_log['gradient_norm']) < 1e-5,
                    'components': all(abs(parts[k]-first_log['components'][k]) < 1e-6 for k in parts)}
    source_checks['first_teaching_replay'] = all(first_checks.values())
    write_json(REPORT / 'LEARNING.json', {'first_cycle_replay': first_checks, 'changes': changes,
               'all_parameters_in_optimizer': True, 'initial_weights': first['weights'], 'selected': chosen})

    final = read(REPORT / 'RESULTS.json'); tables = {}; paired = []
    for route, cohorts in final.items():
        tables[route] = {}
        for cohort, result in cohorts.items():
            rows = data.shifted() if cohort == 'shifted' else data.finals(cohort)
            cases = case_records(route, cohort)
            if [c['id'] for c in cases] != [r['id'] for r in rows]:
                raise ValueError('Final source order differs')
            for row, c in zip(rows, cases):
                exact = decimal_outcome(row['physics']['teacher_only'], *row['physics']['queries'][0])
                error = abs(c['truth']-exact)
                if error > 2e-6*(1+abs(exact)):
                    raise ValueError('Independent decimal outcome differs')
                expected = (c['before']-exact)**2-(c['after']-exact)**2
                if abs(c['signed_progress']-expected) > 2e-6*(1+abs(expected)):
                    raise ValueError('Credit not bound to independently measured progress')
                if not c['performed'] and (c['before'] != c['after'] or c['credit'] != 0 or c['actual'] is not None):
                    raise ValueError('STOP created a measurement or credit')
                if c['performed']:
                    f, v, observed = c['actual']
                    real = decimal_outcome(row['physics']['teacher_only'], f, v)
                    if abs(real-observed) > 2e-6*(1+abs(real)):
                        raise ValueError('Observed probe differs from independent environment')
                raw_errors.append(error)
            metrics = {'accuracy': sum(c['correct'] for c in cases)/len(cases),
                       'original_goal_mse': sum((c['after']-c['truth'])**2 for c in cases)/len(cases),
                       'utility': sum(-(c['after']-c['truth'])**2-.001*c['performed'] for c in cases)/len(cases)}
            tables[route][cohort] = metrics
    contrasts = {}
    for control in ('withheld', 'initial', 'uniform', 'disagreement', 'stop', 'erase_history', 'no_imagination'):
        values = []
        for cohort in ('matched', 'mismatched'):
            primary = case_records('credited', cohort); other = case_records(control, cohort)
            for a, b in zip(primary, other):
                if a['id'] != b['id']:
                    raise ValueError('Paired comparison source mismatch')
                ua = -(a['after']-a['truth'])**2-.001*a['performed']
                ub = -(b['after']-b['truth'])**2-.001*b['performed']
                values.append((cohort+'|'+a['group'], ua-ub))
        contrasts[control] = interval(values, seed=202020)
    # Utility is returned original-goal accuracy after paying for measurements.
    # It prevents a weak before-prediction from earning advantage merely because
    # it had more error available to reduce.
    write_json(REPORT / 'INDEPENDENT_METRICS.json', {'metrics': tables, 'decimal_max_outcome_discrepancy': max(raw_errors),
        'utility': 'negative squared original-goal error minus .001 per performed probe', 'comparisons': contrasts})
    retention = read(REPORT / 'RETENTION.json')
    broader = {}
    for arm, pointer in (('credited', 'SELECTION.json'), ('withheld', 'SELECTION.json'), ('initial', 'INITIAL.json')):
        owner, _, _ = load_native(STUDY / ('withheld' if arm == 'withheld' else 'credited'), pointer=pointer)
        broader[arm] = {kind: assess(owner, data.rehearsal, kind, rows)[0]
                        for kind, rows in data.rehearsal.development.items()}
    write_json(REPORT / 'BROADER_DEVELOPMENT.json', {'scope': 'Previously available source development checks, not new sealed tests.',
                                                    'tracks': broader})
    human_ok = all(retention['credited'][c]['accuracy'] >= retention['initial'][c]['accuracy']-.03
                   for c in ('matched', 'mismatched'))
    physical_ok = retention['credited']['physics']['mse'] <= 1.1*retention['initial']['physics']['mse']
    delivery = read(REPORT / 'DELIVERY.json')
    tests = read(ROOT / 'runs/joint020-session-tests-001/state.json')
    gates = {'source_identity': all(source_checks.values()), 'complete_matched_teaching': all(exposure_checks.values()),
             'same_order_and_evidence': orders['credited'] == orders['withheld'],
             'selected_updated_state': chosen['step'] > 0,
             'learned_choice_weights_changed': changes['choice.weight'] > 0,
             'mixed_goal_improvement': all(tables['credited'][c]['original_goal_mse'] < tables['initial'][c]['original_goal_mse']
                                           for c in ('matched', 'mismatched')),
             'human_retention': human_ok, 'physical_retention': physical_ok,
             'credit_contrast': contrasts['withheld']['95_percent_interval'][0] > 0,
             'exact_replay': read(REPORT / 'REPLAY.json')['exact'],
             'persistent_weight_update_and_restart': delivery['all_checks'],
             'engineering_tests': tests['status'] == 'PASS'}
    write_json(REPORT / 'TEACHING.json', {'arms': training, 'source_checks': source_checks,
                                        'matched_evidence': gates['same_order_and_evidence']})
    quality = {'all_family_order_cells_taught': read(REPORT / 'ORDER_DIAGNOSIS.json')['all_family_order_cells_taught']}
    write_json(REPORT / 'QUALIFICATION.json', {'gates': gates, 'all_frozen_gates': all(gates.values()),
        'post_training_design_quality': quality, 'all_gates': all(gates.values()) and all(quality.values()), 'selected': chosen,
        'scope': 'Finite supplied mixed histories and investigation grid; reward contrast measures the complete trained candidate.'})
    print(json.dumps({'joint_qualification': gates, 'design_quality': quality,
                      'all_checks': all(gates.values()) and all(quality.values())}), flush=True)


if __name__ == '__main__':
    main()
