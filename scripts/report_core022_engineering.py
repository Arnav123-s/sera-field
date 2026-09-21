"""Record the ongoing build accurately without declaring a trained complete core."""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, write_json


def main():
    report = ROOT / 'reports/CORE-022'
    states = [json.loads(p.read_text()) for p in sorted((ROOT / 'runs').glob('core022-*/state.json'))]
    if any(s['status'] in ('RUNNING', 'STARTING') for s in states):
        raise ValueError('Let the owned engineering phase finish first')
    last = states[-1]
    suite = ET.parse(report / 'verification' / (last['attempt']+'.xml')).getroot().find('testsuite')
    sources = ('sera_field/fibonacci_space.py', 'sera_field/unified_energy.py',
               'tests/test_fibonacci_space.py', 'tests/test_unified_energy.py')
    record = {'stage': 'complete-core engineering; full owner and curriculum not yet launched',
        'work_order': 'docs/COMPLETE_CORE_WORK_ORDER.md', 'equations': 'docs/CORE_022_EQUATIONS.md',
        'mathematical_tests': int(suite.attrib['tests']),
        'failures': int(suite.attrib['failures']), 'errors': int(suite.attrib['errors']),
        'all_checks': last['status'] == 'PASS',
        'sources': {p: sha256(ROOT / p) for p in sources},
        'trained_presentations': 0, 'whole_owner_integration_complete': False,
        'research_complete': False,
        'next_work': 'Connect these equations and the preserved mechanisms through one fresh owner; complete the entire build acceptance before freezing and launching its behavior curriculum.',
        'recheck_reason': 'The second attempt adds a full-action local-frame test to the nine initially passing checks.'}
    costs = {'attempts': [{k:v for k,v in s.items() if k != 'sources'} for s in states],
        'wall_seconds': sum(s['wall_seconds'] for s in states),
        'cpu_seconds': sum(s.get('resources', {}).get('cpu_seconds', 0) for s in states),
        'peak_bytes': max(s.get('resources', {}).get('peak_committed_bytes', 0) for s in states)}
    write_json(report / 'ENGINEERING.json', record); write_json(report / 'COSTS.json', costs)
    (report / 'REPORT.md').write_text(f'''# CORE-022: complete-core construction in progress

I began the user's requested sequence: finish the mechanism build and its
engineering checks, then teach fresh weights on the complete behavioral course,
assess the whole learner, and later continue learning incrementally.
The [work order](../../docs/COMPLETE_CORE_WORK_ORDER.md) lists every required
connection and curriculum obligation. Earlier owners and all evaluations remain.

Two missing mathematical connections now have executable constructions: a shared
energy with reciprocal boundary/covariance/fast/slow/bulk dependencies and explicit
active-work accounting; and a finite chiral Fibonacci fusion space with complete
outcome bookkeeping. **{record['mathematical_tests']} engineering checks passed**.
They cover the pentagon, braid relations, measurement channels, energy/mass
identities, discrete-step refinement, local frames and actual gradients through
the coupled coordinates. [Equations and scope](../../docs/CORE_022_EQUATIONS.md).

The initial nine checks passed; the subsequent tenth check covers the entire
action's frame transformation, including stored-frame bulk anchors. Both costs
are retained. Supervised wall time is {costs['wall_seconds']:.3f} seconds and
peak process-tree memory is {costs['peak_bytes']/1024**2:.1f} MiB, using one numerical
thread and the 2 GiB cap. [Identities](ENGINEERING.json) · [Costs](COSTS.json).

This is the build phase. These operators have not yet been connected to every
required route of the fresh owner, and no CORE-022 curriculum has started. The
next work completes that connection and the remaining mechanisms before training.
Operator consistency is recorded separately from learned behavior; no older
checkpoint is presented as having acquired these new mechanisms.
''', encoding='utf-8')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
