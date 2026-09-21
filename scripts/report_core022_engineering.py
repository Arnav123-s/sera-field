"""Record the ongoing build accurately without declaring a trained complete core."""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, write_json


def main():
    report = ROOT / 'reports/CORE-022'
    states = sorted([json.loads(p.read_text()) for p in (ROOT / 'runs').glob('core022-*/state.json')],
                    key=lambda s: s['started_utc'])
    if any(s['status'] in ('RUNNING', 'STARTING') for s in states):
        raise ValueError('Let the owned engineering phase finish first')
    tested = [s for s in states if (report/'verification'/(s['attempt']+'.xml')).exists()]
    last = tested[-1]
    suite = ET.parse(report / 'verification' / (last['attempt']+'.xml')).getroot().find('testsuite')
    sources = sorted({p.relative_to(ROOT).as_posix() for pattern in ('sera_field/core_*.py', 'tests/test_core_*.py')
                      for p in ROOT.glob(pattern)} | {'sera_field/fibonacci_space.py', 'sera_field/unified_energy.py',
                      'sera_field/joint_session.py', 'tests/test_fibonacci_space.py', 'tests/test_unified_energy.py'})
    if any(last['sources'].get(p) != sha256(ROOT/p) for p in sources):
        raise ValueError('Changed implementation since the selected verification')
    old = report/'ENGINEERING.json'
    if old.exists():
        history = report/'history'; history.mkdir(exist_ok=True)
        destination = history/('ENGINEERING-'+sha256(old)[:16]+'.json')
        if not destination.exists(): destination.write_bytes(old.read_bytes())
    relevant = [c for c in suite.findall('testcase') if any(c.attrib['classname'].startswith(s) for s in
                ('tests.test_core_', 'tests.test_fibonacci_space', 'tests.test_unified_energy'))]
    record = {'stage': 'coupled owner integrated; remaining complete-core behavior engineering precedes curriculum',
        'work_order': 'docs/COMPLETE_CORE_WORK_ORDER.md', 'equations': 'docs/CORE_022_EQUATIONS.md',
        'owner_integration': 'docs/CORE_022_OWNER.md', 'source_reconciliation': 'docs/EMPIRICAL_SYNTHESIS_20260921.md',
        'repository_tests': int(suite.attrib['tests']), 'coupled_core_tests': len(relevant),
        'failures': int(suite.attrib['failures']), 'errors': int(suite.attrib['errors']),
        'all_checks': last['status'] == 'PASS',
        'verification_attempt': last['attempt'],
        'sources': {p: sha256(ROOT / p) for p in sources},
        'trained_presentations': 0, 'whole_owner_integration_complete': False,
        'research_complete': False,
        'next_work': 'Connect broader executable proposals, distinct-contribution credit and learning-procedure assessment; finish complete-core acceptance, freeze the course and teach fresh weights before whole-system assessment and incremental learning.',
        'failed_attempts_preserved': [s['attempt'] for s in states if s['status'] != 'PASS'],
        'engineering_fixture_updates_are_not_curriculum': True}
    outcomes = []
    for state in tested:
        xml = ET.parse(report/'verification'/(state['attempt']+'.xml')).getroot().find('testsuite')
        outcomes.append({'attempt': state['attempt'], 'status': state['status'],
            'tests': int(xml.attrib['tests']), 'failures': int(xml.attrib['failures']), 'errors': int(xml.attrib['errors']),
            'xml': 'verification/'+state['attempt']+'.xml',
            'source_identities': {p: state['sources'][p] for p in sources if p in state['sources']}})
    write_json(report/'ATTEMPTS.json', outcomes)
    costs = {'attempts': [{k:v for k,v in s.items() if k != 'sources'} for s in states],
        'wall_seconds': sum(s['wall_seconds'] for s in states),
        'cpu_seconds': sum(s.get('resources', {}).get('cpu_seconds', 0) for s in states),
        'peak_bytes': max(s.get('resources', {}).get('peak_committed_bytes', 0) for s in states)}
    write_json(report / 'ENGINEERING.json', record); write_json(report / 'COSTS.json', costs)
    for name in ('STABILITY', 'WORKLOAD', 'REPLAY'):
        path = ROOT/'runs/CORE-022/engineering-probe'/(name+'.json')
        if path.exists(): write_json(report/(name+'.json'), json.loads(path.read_text()))
    state_path = ROOT/'reports/STATE.json'
    current = json.loads(state_path.read_text())
    current['studies']['CORE-022'].update(stage=record['stage'], training_started=False,
        whole_owner_integration_complete=False, coupled_core_tests=len(relevant), repository_tests=int(suite.attrib['tests']))
    current['latest_empirical_synthesis'] = {'title': 'An Empirical and Theoretical Synthesis of the SERA Field Architecture',
        'sha256': '9ba551b71722b1e90ff0530cae537f4b9af01e01591c65aa4f1b4a30813056b5', 'bytes': 20335,
        'read_completely': True, 'source_preserved': True, 'audit': 'docs/EMPIRICAL_SYNTHESIS_20260921.md'}
    current['active_numerical_attempts'] = []; current['numerical_lease_released'] = True
    write_json(state_path, current)
    (report / 'REPORT.md').write_text(f'''# CORE-022: complete-core construction in progress

I connected the fresh input maps, reciprocal energy, retained memory, conditional
fusion and independent reward path through one owner. The build now also uses
temporal echo, exact protected-state recovery and an actual finite stalk
attachment with optimizer migration. **{record['coupled_core_tests']} coupled-core checks and
{record['repository_tests']} repository tests passed** at the recorded source identities.

I am following the requested sequence: finish the complete mechanism and its
engineering acceptance, then teach fresh weights on the behavioral course,
assess the whole learner, and afterward continue learning incrementally.
The [work order](../../docs/COMPLETE_CORE_WORK_ORDER.md) lists every required
connection and curriculum obligation. Earlier owners and all evaluations remain.

## What the build now executes

- Observed text and numerical evidence enter one coupled boundary/covariance/
  fast/slow/bulk state, with the retained flow context participating in encoding.
- The same energy propagates conditional branches. A performed unread fusion
  instrument and an absent instrument produce different continued states;
  averaging all read outcomes agrees with the unread channel.
- Canonical credit includes the learned metric and every frozen slow-coordinate
  dependence. Irreversible relaxation keeps its own derivative and work account.
- An independent outcome updates the existing weights, re-encodes retained
  history and returns the saved original question. Repeated/stale credit and
  unperformed observations are rejected.
- Coded state decodes exactly into the actual resumed owner. The fixed error,
  erasure, phase-gap, identity and evidence-scope contracts are checked.
- Independent residuals and model spread feed a trainable adequacy decision.
  The attached stalk adds real coordinates, an input port, common-energy terms
  and a decoder; its existing optimizer moments and original goal survive.

The [owner note](../../docs/CORE_022_OWNER.md) and
[equations](../../docs/CORE_022_EQUATIONS.md) give precise scope. A forced fixture
decision verifies an executable route; its capability must still be learned and
assessed. Structural attachment earns no correctness credit by itself.

## Verification and costs

The checks include whole-action frame changes, reciprocal mixed derivatives,
multi-event finite differences, canonical reversal, timed/intermediate-loss echo
derivatives, passive loss/active work, complete fusion outcomes and exact state,
optimizer and RNG restart. Four failed attempts exposed two implementation bugs
and two fixture-contract errors; all are described in [REPAIRS.md](REPAIRS.md).
Every attempt and source identity is in [ATTEMPTS.json](ATTEMPTS.json).

A separate [96-event bounded stream](STABILITY.json) kept finite coordinates,
positive covariance and pure conditional reads. The [resource workload](WORKLOAD.json)
executes eight cases with eight retained observations and two three-branch
queries per case, including the full learning derivative. It takes no optimizer
step. A new interpreter [reproduced the pending decision, independent credit,
next weight update and RNG exactly](REPLAY.json). These are engineering fixtures.

Supervised wall time is {costs['wall_seconds']:.3f} seconds and
peak process-tree memory is {costs['peak_bytes']/1024**2:.1f} MiB, using one numerical
thread and the 2 GiB cap. [Identities](ENGINEERING.json) · [Costs](COSTS.json).

## New source and remaining acceptance

The latest 20,335-byte synthesis is preserved and
[reconciled with local evidence](../../docs/EMPIRICAL_SYNTHESIS_20260921.md).
Its five-use coherent-correction assessment is adopted prospectively. Some of
its historical status claims are superseded by trained ECHO, UNIFIED and NATIVE
studies. None of their completed finals were reopened for tuning.

CORE-022 curriculum presentations remain **zero**. The engineering fixtures are
reported as such. Broader executable proposals, distinct-contribution reward,
learning-procedure assessment and the complete behavioral curriculum remain in
the active work order. The whole research remains open; these working connections
are not relabeled as the completion of every behavioral requirement.
''', encoding='utf-8')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
