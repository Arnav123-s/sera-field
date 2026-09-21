"""Bind reviewed engineering acceptance to one exact fresh teaching program."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.core_course import identities
from sera_field.records import sha256, write_json, utc


def main():
    report = ROOT/'reports/CORE-022'
    result = report/'BUILD_ACCEPTANCE.json'
    if result.exists(): raise ValueError('Preserve accepted source identity; qualify a changed course separately')
    engineering = json.loads((report/'ENGINEERING.json').read_text())
    attempt = json.loads((ROOT/'runs'/engineering['verification_attempt']/'state.json').read_text())
    if not engineering['all_checks'] or attempt['status'] != 'PASS' or engineering['repository_tests'] < 255:
        raise ValueError('Current complete regression required')
    sources = identities()
    for path, digest in sources['implementation'].items():
        if attempt['sources'].get(path) != digest: raise ValueError('Implementation changed after regression: '+path)
    if attempt['sources'].get('scripts/train_core022_foundation.py') != sources['driver']:
        raise ValueError('Training driver changed after regression')
    workload = json.loads((report/'COURSE_WORKLOAD.json').read_text())
    replay = json.loads((report/'COURSE_REPLAY.json').read_text())
    if (not workload['same_weights'] or workload['optimizer_steps'] != 0
            or {r['kind'] for r in workload['workloads']} != {'semantic','pairs','reading','programs','physics','mixed'}
            or not replay['independent_process_replay_exact']):
        raise ValueError('Course workload and exact continuation evidence required')
    required = ['ENGINEERING.json', 'COURSE_WORKLOAD.json', 'COURSE_REPLAY.json', 'COURSE_ALLOCATION.json',
                'TEACHING_VIEWS.json', 'PROGRAM_REPLAY.json', 'LEARNING_REPLAY.json', 'REPLAY.json', 'STABILITY.json']
    record = {'schema': 'sera-field.core022.foundation-build-acceptance.1', 'utc': utc(),
        'launch_qualified': True, 'scope': 'Reviewed finite coupled construction and registered foundation teaching',
        'course_sources': sources, 'engineering_tests': engineering['repository_tests'],
        'evidence': {name: sha256(report/name) for name in required},
        'alignment_review': {'path': 'docs/CORE_022_BUILD_ACCEPTANCE.md', 'sha256': sha256(ROOT/'docs/CORE_022_BUILD_ACCEPTANCE.md')},
        'whole_research_complete': False, 'whole_behavior_qualified': False,
        'curriculum_updates_at_acceptance': 0,
        'next_executable_action': '.venv/Scripts/python.exe scripts/supervise.py --attempt core022-foundation-credited-001 -- scripts/train_core022_foundation.py credited'}
    write_json(result, record); print(json.dumps({'launch_qualified': True, 'course_sources_identity': sha256(result)}))


if __name__ == '__main__': main()
