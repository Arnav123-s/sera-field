"""Check the full repository and the documented packaged-owner examples once.

This release check is separate from research selection. It does not train,
alter a checkpoint or open another scientific evaluation cohort.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, write_json


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    report = ROOT / 'reports/NATIVE-019/verification'
    report.mkdir(parents=True, exist_ok=True)
    package = ROOT / 'checkpoints/NATIVE-019'
    selected = json.loads((package / 'SELECTION.json').read_text())
    revision = package / 'revisions' / selected['revision']
    if sha256(revision) != selected['sha256']:
        raise ValueError('Package identity changed before release verification')
    subprocess.run([sys.executable, '-m', 'pytest', '--junitxml',
                    str(report / 'repository-tests.xml')], cwd=ROOT, check=True)

    def capture(*args):
        result = subprocess.run([sys.executable, '-X', 'utf8', *args], cwd=ROOT,
                                text=True, encoding='utf-8', capture_output=True)
        if result.returncode:
            print(result.stdout, flush=True)
            print(result.stderr, file=sys.stderr, flush=True)
            raise SystemExit(result.returncode)
        return json.loads(result.stdout)

    packages = capture('scripts/verify_packaged.py')
    meaning = capture('-m', 'sera_field.native_cli', 'interpret',
                      '--input', 'examples/native-meaning.json')
    session = ROOT / 'local/NATIVE-019-release' / os.environ['SERA_FIELD_SUPERVISED']
    start = capture('-m', 'sera_field.native_cli', 'start', '--session', str(session),
                    '--input', 'examples/native-observations.json')
    restored = capture('-m', 'sera_field.native_cli', 'answer', '--session', str(session))
    checks = {
        'packaged_integrity': packages['status'] == 'PASS',
        'documented_meaning_example': len(meaning['relations']) == 3,
        'fresh_process_example_restart': start == restored,
        'four_supplied_observations': start['observed_count'] == 4,
        'same_selected_weights': start['owner_weights'] == selected['weights']
                                == meaning['checkpoint']['weights'],
        'checkpoint_bytes_unchanged': sha256(revision) == selected['sha256'],
    }
    result = {'checks': checks, 'all_checks': all(checks.values()),
              'scope': 'Documented illustrative inputs; operational verification, not a new scientific cohort.',
              'package': selected, 'packaged_owners': packages['packaged_owners'],
              'input_sha256': {name: sha256(ROOT / 'examples' / name) for name in
                               ('native-meaning.json', 'native-observations.json')},
              'meaning': meaning, 'measured_task': start,
              'repository_tests': 'verification/repository-tests.xml'}
    write_json(ROOT / 'reports/NATIVE-019/RELEASE_CHECK.json', result)
    if not result['all_checks']:
        raise ValueError('Release example verification failed')
    print(json.dumps({'release_checks': checks,
                      'documented_goal_prediction': start['predictions']}), flush=True)


if __name__ == '__main__':
    main()
