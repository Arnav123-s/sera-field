"""CPU-only saved-file contracts; no learner, torch, subprocess or live runs."""
import copy
import hashlib
import json
from pathlib import Path
import statistics
from datetime import datetime, timezone

import pytest

from scripts import sera_u_report as report


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding='utf-8')


@pytest.fixture
def saved_batch(tmp_path):
    batch = tmp_path / 'saved-fixture'
    protocol = {'source': 'fixture-package', 'code': 'fixture-code', 'device': 'fixture-cpu',
                'seed': 37, 'generations': 1, 'eval_tasks': 13, 'wake_tasks': 7,
                'task_wall': 19.5, 'hours': 2.75, 'budgets': {'train': 913},
                'arms': ['full', 'no-dreams'], 'frozen_suite_sha256': 'fixture-suite',
                'crutches': {'full': {'memory': False}, 'no-dreams': {'memory': False}}}
    counts = {'no-memory': (5, 6), 'discovery-off': (9, 8), 'ablated': (10, 9)}
    for case, generation_counts in counts.items():
        p = copy.deepcopy(protocol)
        if case == 'ablated':
            p['crutches']['full']['memory'] = True
        if case == 'discovery-off':
            # The task specifically calls these replicates despite code changes.
            p['code'] = 'fixture-new-code'
        rows, curves, retention = [], {}, {}
        for arm in p['arms']:
            curves[arm], retention[arm] = [], []
            for generation, count in enumerate(generation_counts):
                for index in range(p['eval_tasks']):
                    rows.append({'arm': arm, 'generation': generation, 'suite': 'assessment',
                                 'task': f'held-{index}', 'solved': index < count,
                                 'wall': 23.25 + index + generation,
                                 'grade': {'verdict': 'proven right' if index < count else 'not proven'}})
                kept = 3
                for index in range(kept):
                    rows.append({'arm': arm, 'generation': generation, 'suite': 'retention',
                                 'task': f'kept-{index}', 'solved': index < generation + 1,
                                 'wall': 17.125 + index, 'grade': {'verdict': 'not proven'}})
                curves[arm].append({'generation': generation, 'solved': count,
                                    'N': p['eval_tasks'], 'g': count / p['eval_tasks'],
                                    'rows': p['eval_tasks'], 'complete': True})
                retention[arm].append((generation + 1) / kept)
        state = {'protocol': p, 'suite_sha256': p['frozen_suite_sha256'], 'rows': rows,
                 'retention_count': kept, 'stage': 'complete', 'started': 181.25,
                 'finished': 271.75, 'deadline': 999.625,
                 'preflight': {'runtime': {'machine': 'fixture-machine', 'processor': 'fixture-chip'}}}
        root = batch / ('u-' + case)
        write_json(root / 'state.json', state)
        write_json(root / 'protocol.json', p)
        write_json(root / 'g_curve.json', {'complete': True, 'curves': curves, 'retention': retention})
    return batch


def read(path):
    return json.loads(path.read_bytes())


def rewrite(path, edit):
    value = read(path)
    edit(value)
    write_json(path, value)


def generate(tmp_path, batch, raw=None):
    target, index = tmp_path / 'SERA_U_REPORT.md', tmp_path / 'sera-runs' / 'report-index.json'
    if raw is not None:
        target.write_bytes(raw)
    report.generate([batch], target, index)
    return target, index


def detail_text(target):
    return target.with_name('SERA_U_REPORT_TABLES.md').read_text(encoding='utf-8')


def test_only_marker_interiors_change_and_repeat_is_identical(tmp_path, saved_batch):
    raw = (b'\xef\xbb\xbfOutcome written by a human.\r\n'
           b'<!-- generated:begin assessment -->\r\nold\r\n<!-- generated:end assessment -->\r\n'
           b'Technical prose: keep exactly.\n'
           b'<!-- generated:begin habits -->\r\nold\r\n<!-- generated:end habits -->\r\n'
           b'Plain words: keep these, too.\r\n')
    target, index = generate(tmp_path, saved_batch, raw)
    first, first_index = target.read_bytes(), index.read_bytes()
    def outside(data):
        text = data.decode('utf-8')
        matches = list(report.MARKER.finditer(text))
        pieces, cursor = [], 0
        for pos in range(0, len(matches), 2):
            begin, end = matches[pos:pos + 2]
            pieces.append(text[cursor:begin.end()])
            cursor = end.start()
        pieces.append(text[cursor:])
        return ''.join(pieces).encode('utf-8')
    assert outside(first) == outside(raw)
    report.generate([saved_batch, saved_batch], target, index)
    assert target.read_bytes() == first
    assert index.read_bytes() == first_index
    records = read(index)['states']
    assert len(records) == len(list(saved_batch.glob('u-*/state.json')))
    for record in records:
        assert record['sha256'] == hashlib.sha256(Path(record['path']).read_bytes()).hexdigest()


@pytest.mark.parametrize('kind', ['assessment', 'discovery'])
def test_different_frozen_suites_refused_before_any_write(tmp_path, saved_batch, kind):
    for root in saved_batch.glob('u-*'):
        if kind == 'discovery':
            rewrite(root / 'state.json', lambda value: value.update(discovery_suite_sha256='discovery-suite'))
    path = saved_batch / 'u-ablated' / 'state.json'
    def change(value):
        if kind == 'assessment':
            value['suite_sha256'] = 'different-suite'
            value['protocol']['frozen_suite_sha256'] = 'different-suite'
        else:
            value['discovery_suite_sha256'] = 'different-discovery-suite'
    rewrite(path, change)
    if kind == 'assessment':
        write_json(path.parent / 'protocol.json', read(path)['protocol'])
    target, index = tmp_path / 'report.md', tmp_path / 'index.json'
    target.write_bytes(b'Human prose remains untouched.')
    with pytest.raises(ValueError, match='Different frozen suites'):
        report.generate([saved_batch], target, index)
    assert target.read_bytes() == b'Human prose remains untouched.'
    assert not index.exists()


def add_discovery(batch):
    for root in batch.glob('u-*'):
        p = read(root / 'protocol.json')
        p['discovery'] = {'switches': {'open_worlds': True}, 'share': .1375,
                          'einstein': {'symmetry': True}, 'scientists': {'chases': True},
                          'darwin': {'trees': True}, 'roadmap': {'pruning': True}}
        write_json(root / 'protocol.json', p)
        rewrite(root / 'state.json', lambda value: value.update(protocol=p, discovery_suite_sha256='habit-suite'))
        habits = {'laws': 17, 'seconds': 83.375, 'experiments': 29, 'seconds_per_law': 83.375 / 17,
                  'einstein': {'paradoxes': 7, 'paradoxes_confirmed': 4, 'principles': 6,
                               'dual_world_revisions': 3, 'predictions': 11,
                               'predictions_confirmed': 8, 'predictions_failed': 2},
                  'scientists': {'conjectures_audited': 19, 'conjectures_refuted': 5,
                                 'conserved_quantities': 4, 'chases_started': 9,
                                 'chase_endings': {'released': 3, 'explained': 2}},
                  'darwin': {'regions': [{'trials': 23, 'correct': 19, 'loss': .3125,
                                         'brier': .1875, 'bins': [[2, 3]]}],
                             'trees': {'fixture-tree': {'leaves': 5}},
                             'mechanisms': {'fixture-mechanism': {'audits': 7}}},
                  'roadmap': {'operations': {'op': {'admitted': True}, 'rejected-op': {'admitted': False}},
                              'rebuilds': {'concept': {'kept': True}},
                              'calibration': {'coverage': .8125, 'mean_squared_order_error': .15625},
                              'pruning': {'mistakes': [{'recovered': True}]}}}
        rewrite(root / 'g_curve.json', lambda value: value.update(discovery={
            'false_credit': 0, 'generations': [{'arm': 'full', 'generation': 1, **habits}]}))


def test_missing_comparison_is_missing_and_habit_numbers_are_saved(tmp_path, saved_batch):
    add_discovery(saved_batch)
    target, index = generate(tmp_path, saved_batch)
    text = detail_text(target)
    assert 'comparison JSON MISSING (not zero' in text
    data = read(saved_batch / 'u-no-memory' / 'g_curve.json')['discovery']['generations'][0]
    for name, value in report.leaves({key: value for key, value in data.items() if key not in ('arm', 'generation')}):
        assert f'| {report.cell(name)} | {report.cell(value, 1 if report.seconds_metric(name) else 2)} |' in text
    assert '| roadmap.operations.built | 1 |' in text  # derived from admitted fixture entries
    assert '| roadmap.rebuilds.kept | 1 |' in text
    assert any(Path(record['path']).name == 'g_curve.json' for record in read(index)['files'])


def test_all_tables_print_false_credit_and_nonzero_exits_after_flagging(tmp_path, saved_batch):
    add_discovery(saved_batch)
    path = saved_batch / 'u-ablated' / 'g_curve.json'
    rewrite(path, lambda value: value['discovery'].update(false_credit=3))
    target, index = tmp_path / 'report.md', tmp_path / 'index.json'
    with pytest.raises(SystemExit) as exc:
        report.main(['--runs', str(saved_batch), '--write', str(target), '--index', str(index)])
    assert exc.value.code == 2
    text = target.read_text(encoding='utf-8') + detail_text(target)
    assert '3 FLAG: must be zero' in text
    lines = text.splitlines()
    headers = [lines[index - 1] for index, line in enumerate(lines) if line.startswith('|---')]
    assert len(headers) >= len(report.SECTIONS)
    assert all('false credit' in line for line in headers)


def test_comparison_metrics_are_read_and_batch_credit_is_not_case_credit(tmp_path, saved_batch):
    add_discovery(saved_batch)
    entries = {}
    for root in saved_batch.glob('u-*'):
        entries[root.name] = {'false_credit': 0, 'completed': True,
                              'arms': {'full': {'prediction_counts': {'made': 31, 'confirmed': 23, 'failed': 4},
                                                'hidden_lineage_agreement': {'matches': 17, 'tested': 29}}},
                              'roadmap': {'full': {'pruning': {'recovered': 7}}}}
    comparison = {'matched_scope': ['fixture-suite', 'habit-suite', 'fixture-cpu', 37],
                  'false_credit': 2, 'cases': entries}
    write_json(saved_batch / 'u13-comparison.json', comparison)
    target, _ = generate(tmp_path, saved_batch)
    text = detail_text(target)
    assert '| prediction_counts.confirmed | 23 |' in text
    assert '| roadmap.pruning.recovered | 7 |' in text
    assert '0; batch comparison 2 FLAG: must be zero' in text
    assert 'comparison JSON MISSING' not in text


def test_noise_is_the_largest_replicate_difference_over_generations_and_marks_small_differences(saved_batch):
    cases, _ = report.load_batches([saved_batch])
    spreads, differences = report.differences(cases)
    key = ('assessment', 'full', 0, 'solved')
    replicate = next(row for row in spreads if tuple(row[2:6]) == key)
    # Values and spread come from the fixture rows, not case names or constants. One replicate pair gives one
    # difference per generation, so a metric's spread is the largest over its generations (development review, 2026-10-03).
    indexed = {case.label: case for case in cases}
    left, right = indexed[replicate[0]], indexed[replicate[1]]
    same = [k for k in set(left.metrics) & set(right.metrics) if k[:2] == key[:2] and k[3] == key[3]]
    expected = max(abs(right.metrics[k] - left.metrics[k]) for k in same)
    small = next(row for row in differences if row[0].endswith('/ablated') and
                 row[1].endswith('/discovery-off') and tuple(row[2:6]) == key)
    assert small[9] == expected
    assert abs(small[8]) < expected
    assert small[10] == 'within noise'
    later_key = ('assessment', 'full', 1, 'solved')
    later = next(row for row in differences if row[0] == small[0] and row[1] == small[1] and tuple(row[2:6]) == later_key)
    assert later[9] == small[9]
    assert later[10] == ('within noise' if abs(later[8]) < expected else 'at or above measured spread')


def test_no_replicates_does_not_invent_noise(saved_batch):
    cases, _ = report.load_batches([saved_batch])
    distinct = [case for case in cases if not case.label.endswith('/no-memory')]
    spreads, differences = report.differences(distinct)
    assert spreads == []
    assert differences
    assert all(row[9] is None and row[10] == 'noise MISSING' for row in differences)


def test_assessment_values_and_medians_are_derived_only_from_fixture_files(tmp_path, saved_batch):
    target, _ = generate(tmp_path, saved_batch)
    text = detail_text(target)
    cases, _ = report.load_batches([saved_batch])
    for case in cases:
        state = read(case.root / 'state.json')
        for generation in range(state['protocol']['generations'] + 1):
            selected = [row for row in state['rows'] if row['arm'] == 'full' and
                        row['generation'] == generation and row['suite'] == 'assessment']
            solved = sum(row['solved'] for row in selected)
            n = state['protocol']['eval_tasks']
            median = statistics.median(row['wall'] for row in selected)
            expected = (f'| {case.label} | full | {generation} | {solved} | {n} | '
                        f'{len(selected)} | {report.cell(median, 1)} | {report.cell(solved / n)} |')
            assert expected in text
        assert datetime.fromtimestamp(state['started'], timezone.utc).strftime('%Y-%m-%d %H:%M') in text
        assert datetime.fromtimestamp(state['finished'], timezone.utc).strftime('%Y-%m-%d %H:%M') in text
        assert state['preflight']['runtime']['machine'] in text
    # Changing saved measurements changes the rendered values, not prose.
    root = saved_batch / 'u-no-memory'
    rewrite(root / 'state.json', lambda value: [row.update(wall=52.875) for row in value['rows']])
    report.generate([saved_batch], target, tmp_path / 'index.json')
    assert '| 52.9 |' in detail_text(target)


@pytest.mark.parametrize('failure, expected', [
    ('Declared training allowance exhausted', 'declared allowance: Declared training allowance exhausted'),
    ('Tripwire: observer failed fixture audit', 'stop: Tripwire: observer failed fixture audit')])
def test_endings_preserve_failure_strings(tmp_path, saved_batch, failure, expected):
    rewrite(saved_batch / 'u-no-memory' / 'state.json', lambda value: value.update(failure=failure, stage='arms'))
    target, _ = generate(tmp_path, saved_batch)
    assert expected in target.read_text(encoding='utf-8')


def test_missing_grades_does_not_claim_zero(saved_batch):
    root = saved_batch / 'u-no-memory'
    rewrite(root / 'state.json', lambda value: [row.pop('grade') for row in value['rows']])
    cases, _ = report.load_batches([saved_batch])
    case = next(case for case in cases if case.root == root)
    assert case.false_credit == report.MISSING
    assert not case.false_values


@pytest.mark.parametrize('raw', [
    b'no markers',
    b'<!-- generated:begin assessment -->',
    b'<!-- generated:begin assessment --><!-- generated:end habits -->',
    b'<!-- generated:begin unknown --><!-- generated:end unknown -->',
    b'<!-- generated:begin assessment --><!-- generated:end assessment -->'
    b'<!-- generated:begin assessment --><!-- generated:end assessment -->'])
def test_invalid_markers_leave_report_and_index_unchanged(tmp_path, saved_batch, raw):
    target, index = tmp_path / 'report.md', tmp_path / 'index.json'
    target.write_bytes(raw)
    with pytest.raises(ValueError):
        report.generate([saved_batch], target, index)
    assert target.read_bytes() == raw
    assert not index.exists()


def test_template_leads_with_outcome_then_technical_then_plain_words(tmp_path, saved_batch):
    target, _ = generate(tmp_path, saved_batch)
    text = target.read_text(encoding='utf-8')
    assert text.index('generated:begin outcome') < text.index('## Technical') < text.index('## Plain words')


def test_changed_seed_prevents_noise_and_case_comparisons(saved_batch):
    cases, _ = report.load_batches([saved_batch])
    for index, case in enumerate(cases):
        case.protocol['seed'] += index
    assert report.differences(cases) == ([], [])


def test_missing_assessment_rows_are_not_presented_as_complete(tmp_path, saved_batch):
    root = saved_batch / 'u-no-memory'
    rewrite(root / 'state.json', lambda value: value['rows'].pop(0))
    target, _ = generate(tmp_path, saved_batch)
    state = read(root / 'state.json')
    selected = [row for row in state['rows'] if row['arm'] == 'full' and row['generation'] == 0 and row['suite'] == 'assessment']
    assert len(selected) < state['protocol']['eval_tasks']
    assert f'| {state["protocol"]["eval_tasks"]} | {len(selected)} |' in detail_text(target)


def test_missing_discovery_credit_is_not_replaced_with_assessment_zero(saved_batch):
    add_discovery(saved_batch)
    root = saved_batch / 'u-no-memory'
    rewrite(root / 'g_curve.json', lambda value: value['discovery'].pop('false_credit'))
    cases, _ = report.load_batches([saved_batch])
    case = next(case for case in cases if case.root == root)
    assert case.false_credit == report.MISSING
    assert 'Discovery false credit evidence MISSING' in case.notices


def test_missing_curve_is_indexed_and_reported_without_losing_state_metrics(tmp_path, saved_batch):
    root = saved_batch / 'u-no-memory'
    # Read a separate one-case fixture batch with the optional file never supplied.
    batch = tmp_path / 'missing-curve-fixture'
    for name in ('state.json', 'protocol.json'):
        write_json(batch / root.name / name, read(root / name))
    target, index = generate(tmp_path, batch)
    text = detail_text(target)
    assert 'saved curve incomplete or missing' in text
    assert 'g_curve.json' in text
    assert any(record['status'] == 'missing' and Path(record['path']).name == 'g_curve.json' for record in read(index)['files'])
    assert '| full |' in text
    assert 'missing-curve-fixture/no-memory: 0' in text  # empty curve/noise tables retain the observed tripwire


def test_comparison_on_another_frozen_suite_is_refused(tmp_path, saved_batch):
    write_json(saved_batch / 'u10-comparison.json', {'matched_scope': ['other-suite', None], 'cases': {}})
    with pytest.raises(ValueError, match='Comparison frozen suites disagree'):
        generate(tmp_path, saved_batch)


def test_assessment_false_credit_is_counted_from_observer_grades(tmp_path, saved_batch):
    root = saved_batch / 'u-no-memory'
    def wrong(value):
        value['rows'][0]['grade']['verdict'] = 'SURE AND WRONG'
        value['rows'][1]['grade']['verdict'] = 'SURE AND WRONG'
    rewrite(root / 'state.json', wrong)
    target, _ = generate(tmp_path, saved_batch)
    expected = sum(row['grade']['verdict'] == 'SURE AND WRONG' for row in read(root / 'state.json')['rows'])
    assert f'{expected} FLAG: must be zero' in target.read_text(encoding='utf-8')


def test_other_suites_in_separate_batches_have_separate_metric_tables(tmp_path, saved_batch):
    other = tmp_path / 'other-suite-fixture'
    for source in saved_batch.glob('u-*'):
        for name in ('state.json', 'protocol.json', 'g_curve.json'):
            value = read(source / name)
            if name == 'state.json':
                value['suite_sha256'] = 'other-frozen-suite'
                value['protocol']['frozen_suite_sha256'] = 'other-frozen-suite'
            elif name == 'protocol.json':
                value['frozen_suite_sha256'] = 'other-frozen-suite'
            write_json(other / source.name / name, value)
    cases, files = report.load_batches([other, saved_batch])
    sections = report.render_sections(cases, files)
    blocks = sections['assessment'].split('Frozen suites: ')[1:]
    assert len(blocks) == len({case.suite for case in cases})
    for block in blocks:
        assert ('other-suite-fixture/' in block) != ('saved-fixture/' in block)
    _, differences = report.differences(cases)
    assert all(row[0].split('/')[0] == row[1].split('/')[0] for row in differences)
    summary = report.render_summary_sections(cases)
    for name in ('outcome', 'noise'):
        blocks = summary[name].split('Frozen suites: ')[1:]
        assert len(blocks) == len({case.suite for case in cases})
        for block in blocks:
            assert ('other-suite-fixture/' in block) != ('saved-fixture/' in block)
    assert summary['habits'].count('| case |') == len({case.batch for case in cases})


def test_earlier_habit_comparison_does_not_fill_a_missing_later_comparison(tmp_path, saved_batch):
    add_discovery(saved_batch)
    write_json(saved_batch / 'u10-comparison.json', {'matched_scope': ['fixture-suite', 'habit-suite'],
        'false_credit': 0, 'cases': {root.name: {'false_credit': 0} for root in saved_batch.glob('u-*')}})
    target, _ = generate(tmp_path, saved_batch)
    assert 'u13-comparison.json MISSING (not zero)' in target.read_text(encoding='utf-8')


def test_comparison_seed_must_match_saved_state(tmp_path, saved_batch):
    p = read(saved_batch / 'u-no-memory' / 'protocol.json')
    write_json(saved_batch / 'u10-comparison.json', {
        'matched_scope': [p['frozen_suite_sha256'], None, p['device'], p['seed'] + 1], 'cases': {}})
    with pytest.raises(ValueError, match='Comparison seed/device/allowance disagrees'):
        generate(tmp_path, saved_batch)


def outside_markers(raw):
    text = raw.decode('utf-8')
    matches = list(report.MARKER.finditer(text))
    pieces, cursor = [], 0
    for index in range(0, len(matches), 2):
        begin, end = matches[index:index + 2]
        pieces.append(text[cursor:begin.end()])
        cursor = end.start()
    pieces.append(text[cursor:])
    return ''.join(pieces).encode('utf-8')


def test_both_files_preserve_outside_bytes_and_repeat_identically(tmp_path, saved_batch):
    target, detail, index = tmp_path / 'main.md', tmp_path / 'detail.md', tmp_path / 'index.json'
    main_raw = (b'\xef\xbb\xbfHuman outcome.\r\n<!-- generated:begin outcome -->\r\nold\r\n'
                b'<!-- generated:end outcome -->\r\nHuman technical and plain words.\n')
    detail_raw = (b'\xef\xbb\xbfHuman detail introduction.\r\n<!-- generated:begin assessment -->\r\n'
                  b'old\r\n<!-- generated:end assessment -->\r\nHuman explanation.\n'
                  b'<!-- generated:begin habits -->\r\nold\r\n<!-- generated:end habits -->\r\n')
    target.write_bytes(main_raw)
    detail.write_bytes(detail_raw)
    report.generate([saved_batch], target, index, detail)
    assert outside_markers(target.read_bytes()) == outside_markers(main_raw)
    assert outside_markers(detail.read_bytes()) == outside_markers(detail_raw)
    first = [path.read_bytes() for path in (target, detail, index)]
    report.generate([saved_batch, saved_batch], target, index, detail)
    assert [path.read_bytes() for path in (target, detail, index)] == first
    assert read(index)['detail'] == detail.resolve().as_posix()


def test_old_markers_migrate_detail_out_of_main_without_changing_prose(tmp_path, saved_batch):
    raw = report.template(detail=True)
    raw = raw.replace(b'<!-- generated:end assessment -->',
                      b'<!-- generated:end assessment -->\nA human assessment explanation.')
    target, _ = generate(tmp_path, saved_batch, raw)
    text = target.read_text(encoding='utf-8')
    assert outside_markers(target.read_bytes()) == outside_markers(raw)
    assert '| arm | generation |' not in text
    assert '| assessment suite sha256 |' not in text
    assert '| saved path |' not in text
    assert 'A human assessment explanation.' in text
    assert '| arm | generation |' in detail_text(target)
    assert '| assessment suite sha256 |' in detail_text(target)
    assert '| saved path |' in detail_text(target)
    assert text.count('| case | outcome |') == 1


def test_main_is_short_even_when_saved_habit_records_are_large(tmp_path, saved_batch):
    add_discovery(saved_batch)
    for root in sorted(saved_batch.glob('u-*')):
        def records(value):
            row = value['discovery']['generations'][0]
            row['roadmap']['operations'] = {
                f'operation-{index}': {'admitted': index % 2 == 0, 'cost_seconds': index + .123456}
                for index in range(251)}
        rewrite(root / 'g_curve.json', records)
    target, _ = generate(tmp_path, saved_batch)
    text, detail = target.read_text(encoding='utf-8'), detail_text(target)
    assert len(text.splitlines()) < 100
    assert len(detail.splitlines()) > 200
    assert 'operation-250' not in text
    assert 'operation-250' in detail
    assert '| no-dreams |' not in text
    assert '| no-dreams |' in detail
    assert text.count('| case | certified laws / experiments / seconds |') == 1
    assert 'comparison JSON MISSING (not zero' in text
    cases, _ = report.load_batches([saved_batch])
    for case in cases:
        expected = sum(entry['admitted'] for entry in read(case.root / 'g_curve.json')[
            'discovery']['generations'][0]['roadmap']['operations'].values())
        assert f'| {case.label} | laws/experiments=' in text
        row = next(line for line in text.splitlines()
                   if line.startswith(f'| {case.label} | laws/experiments='))
        assert f'| {expected} |' in row


def test_compact_outcome_uses_saved_full_counts_and_rounded_medians(tmp_path, saved_batch):
    target, _ = generate(tmp_path, saved_batch)
    text = target.read_text(encoding='utf-8')
    for root in sorted(saved_batch.glob('u-*')):
        state = read(root / 'state.json')
        groups = [[row for row in state['rows'] if row['suite'] == 'assessment'
                   and row['arm'] == 'full' and row['generation'] == generation]
                  for generation in range(state['protocol']['generations'] + 1)]
        counts = ' '.join(str(sum(row['solved'] for row in rows)) for rows in groups)
        seconds = ' '.join(f'{statistics.median(row["wall"] for row in rows):.1f}' for rows in groups)
        assert f'| {counts} /{state["protocol"]["eval_tasks"]} | {seconds} |' in text
    assert '| arm | generation |' not in text


def test_partial_and_missing_generations_remain_visible_in_outcome(tmp_path, saved_batch):
    root = saved_batch / 'u-no-memory'
    def remove(value):
        value['rows'] = [row for row in value['rows']
                         if not (row['arm'] == 'full' and row['generation'] == 1)]
        value['rows'].pop(0)
    rewrite(root / 'state.json', remove)
    target, _ = generate(tmp_path, saved_batch)
    text = target.read_text(encoding='utf-8')
    row = next(line for line in text.splitlines()
               if line.startswith('| saved-fixture/no-memory | finished'))
    assert '(partial) MISSING /' in row
    assert ' MISSING |' in row


@pytest.mark.parametrize('profile, header, paths', [
    ('discovery', 'certified laws / experiments / seconds', ('laws', 'experiments', 'seconds')),
    ('einstein', 'paradoxes', ('einstein.paradoxes', 'einstein.principles')),
    ('scientists', 'conjectures', ('scientists.conjectures_audited', 'scientists.conserved_quantities')),
    ('darwin', 'hologram fidelity / calibration', ('darwin.trees.count', 'darwin.mechanisms.count')),
    ('roadmap', 'operations built', ('roadmap.operations.built', 'roadmap.rebuilds.kept')),
])
def test_each_habit_summary_selects_saved_metrics(saved_batch, profile, header, paths):
    add_discovery(saved_batch)
    cases, _ = report.load_batches([saved_batch])
    for case in cases:
        original = case.protocol['discovery']
        case.protocol['discovery'] = {key: original[key] for key in ('switches', 'share')}
        if profile != 'discovery':
            case.protocol['discovery'][profile] = original[profile]
    text = report.render_summary_sections(cases)['habits']
    assert header in text
    assert text.count('| case |') == 1
    for case in cases:
        snapshots = report.habit_snapshots(case)
        for path in paths:
            value, _ = report.habit_metric(snapshots, path)
            assert report.cell(value, 1 if report.seconds_metric(path) else 2) in text
    if profile == 'darwin':
        row = read(cases[0].root / 'g_curve.json')['discovery']['generations'][0]['darwin']['regions'][0]
        assert f'correct/trials={row["correct"] / row["trials"]:.2f}' in text
        assert f'Brier/trial={row["brier"] / row["trials"]:.2f}' in text


def test_comparison_totals_take_precedence_over_latest_curve(tmp_path, saved_batch):
    add_discovery(saved_batch)
    comparison = {'matched_scope': ['fixture-suite', 'habit-suite'], 'false_credit': 0,
                  'cases': {root.name: {'false_credit': 0, 'arms': {'full': {
                      'laws': 43, 'experiments': 97, 'seconds': 121.234567}}}
                      for root in sorted(saved_batch.glob('u-*'))}}
    write_json(saved_batch / 'u13-comparison.json', comparison)
    target, _ = generate(tmp_path, saved_batch)
    text = target.read_text(encoding='utf-8')
    saved = read(saved_batch / 'u13-comparison.json')['cases']['u-no-memory']['arms']['full']
    assert f'laws/experiments={saved["laws"]}/{saved["experiments"]}; seconds={saved["seconds"]:.1f}' in text
    assert 'u13-comparison.json:glatest' in text
    assert 'discovery:g1' in text  # other metrics still use a named saved snapshot


def test_summary_noise_packs_generations_and_uses_unrounded_verdicts(tmp_path, saved_batch):
    walls = {'u-no-memory': 10.044, 'u-discovery-off': 10., 'u-ablated': 10.034}
    for root in sorted(saved_batch.glob('u-*')):
        rewrite(root / 'state.json', lambda value, wall=walls[root.name]:
                [row.update(wall=wall) for row in value['rows']])
    cases, _ = report.load_batches([saved_batch])
    text = report.render_summary_sections(cases)['noise']
    _, diffs = report.differences(cases)
    row = next(row for row in diffs if row[0].endswith('/ablated') and
               row[1].endswith('/discovery-off') and row[2:6] ==
               ('assessment', 'full', 0, 'median item wall seconds'))
    assert abs(row[8]) < row[9]
    assert row[10] == 'within noise'
    assert f'g0: {row[8]:.1f} / {row[9]:.1f} within noise' in text
    assert 'g1:' in text
    assert '| replicate |' in text
    assert '| A/B |' in text
    assert sum(line.startswith('| saved-fixture/') for line in text.splitlines()) == len(cases) * (len(cases) - 1) // 2


def test_detail_formats_seconds_fractions_utc_codes_and_switch_deltas(tmp_path, saved_batch):
    for root in sorted(saved_batch.glob('u-*')):
        code = hashlib.sha256(root.name.encode('utf-8')).hexdigest()
        rewrite(root / 'protocol.json', lambda value: value.update(code=code))
        rewrite(root / 'state.json', lambda value: value.update(protocol=read(root / 'protocol.json')))
    target, _ = generate(tmp_path, saved_batch)
    text = detail_text(target)
    cases, _ = report.load_batches([saved_batch])
    first = cases[0]
    for case in cases:
        assert case.protocol['code'][:12] in text
        assert case.protocol['code'] not in text
        assert datetime.fromtimestamp(case.state['started'], timezone.utc).strftime('%Y-%m-%d %H:%M') in text
        assert str(case.state['started']) not in text
        assert report.switch_delta(case, first) in text
    assert 'crutches.full.memory=false' in text
    assert 'same as first case' in text
    assert '{"' not in text
    assert '0.333333' not in text
    assert report.utc_minute('2026-10-03T04:12:59-07:00') == '2026-10-03 11:12'


def test_bad_detail_markers_leave_all_outputs_unchanged(tmp_path, saved_batch):
    target, detail, index = tmp_path / 'main.md', tmp_path / 'detail.md', tmp_path / 'index.json'
    target.write_bytes(report.template())
    detail.write_bytes(b'Human detail with broken markers: <!-- generated:begin assessment -->')
    index.write_bytes(b'Existing index.')
    before = [path.read_bytes() for path in (target, detail, index)]
    with pytest.raises(ValueError, match='unpaired generated markers'):
        report.generate([saved_batch], target, index, detail)
    assert [path.read_bytes() for path in (target, detail, index)] == before


@pytest.mark.parametrize('collision', ['main-detail', 'detail-index', 'detail-input', 'main-input', 'index-input'])
def test_output_collisions_cannot_overwrite_saved_files(tmp_path, saved_batch, collision):
    target, detail, index = tmp_path / 'main.md', tmp_path / 'detail.md', tmp_path / 'index.json'
    saved = saved_batch / 'u-no-memory' / 'state.json'
    if collision == 'main-detail':
        detail = target
    elif collision == 'detail-index':
        detail = index
    elif collision == 'detail-input':
        detail = saved
    elif collision == 'main-input':
        target = saved
    else:
        index = saved
    before = saved.read_bytes()
    with pytest.raises(ValueError, match='Outputs must not overwrite'):
        report.generate([saved_batch], target, index, detail)
    assert saved.read_bytes() == before
    assert not (tmp_path / 'detail.md').exists()
    assert not (tmp_path / 'main.md').exists()
    assert not (tmp_path / 'index.json').exists()


def test_cli_writes_the_requested_detail_file(tmp_path, saved_batch):
    target, detail, index = tmp_path / 'main.md', tmp_path / 'requested-tables.md', tmp_path / 'index.json'
    assert report.main(['--runs', str(saved_batch), '--write', str(target),
                        '--detail', str(detail), '--index', str(index)]) == 0
    assert target.exists() and detail.exists() and index.exists()
    assert not (tmp_path / 'SERA_U_REPORT_TABLES.md').exists()
    assert read(index)['detail'] == detail.resolve().as_posix()

def test_missing_latest_habit_metric_does_not_silently_use_older_generation(saved_batch):
    add_discovery(saved_batch)
    for root in sorted(saved_batch.glob('u-*')):
        def newer(value):
            row = copy.deepcopy(value['discovery']['generations'][0])
            row['generation'] += 1
            row.pop('roadmap')
            value['discovery']['generations'].append(row)
        rewrite(root / 'g_curve.json', newer)
    cases, _ = report.load_batches([saved_batch])
    for case in cases:
        value, source = report.habit_metric(report.habit_snapshots(case), 'roadmap.operations.built')
        assert value is None and source == report.MISSING
    text = report.render_summary_sections(cases)['habits']
    assert '| MISSING | MISSING |' in text
    assert 'discovery:g2' in text

def test_a_discovery_off_control_shares_the_assessment_scope_with_discovery_cases(tmp_path, saved_batch):
    # U9's A/B (development review, 2026-10-03): discovery-off has no discovery suite; it is the control on the same assessment suite.
    for name in ('u-ablated',):
        root = saved_batch / name
        p = read(root / 'protocol.json')
        p['discovery'] = {'switches': {'open_worlds': True}, 'share': .15}
        write_json(root / 'protocol.json', p)
        rewrite(root / 'state.json', lambda value: value.update(protocol=p, discovery_suite_sha256='habit-suite'))
    cases, _ = report.load_batches([saved_batch])
    by = {case.label.split('/')[-1]: case for case in cases}
    assert by['ablated'].scope == by['discovery-off'].scope
    assert by['ablated'].switches != by['discovery-off'].switches
    spreads, differences = report.differences(cases)
    assert any(row[0].endswith('/ablated') and row[1].endswith('/discovery-off') for row in differences)
    root = saved_batch / 'u-no-memory'
    rewrite(root / 'state.json', lambda value: value.update(discovery_suite_sha256='other-habit-suite'))
    p = read(root / 'protocol.json')
    p['discovery'] = {'switches': {'open_worlds': True}, 'share': .15}
    write_json(root / 'protocol.json', p)
    rewrite(root / 'state.json', lambda value: value.update(protocol=p))
    with pytest.raises(ValueError, match='Different frozen suites'):
        report.load_batches([saved_batch])
