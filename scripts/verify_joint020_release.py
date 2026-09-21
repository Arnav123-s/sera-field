"""Verify the documented CLI against its packaged owner in fresh processes."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import write_json, sha256


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    local = ROOT / 'local/JOINT-020-release' / os.environ['SERA_FIELD_SUPERVISED']
    session = local / 'task'
    local.mkdir(parents=True, exist_ok=False)
    def run(action, input_path=None):
        command = [sys.executable, '-X', 'utf8', '-m', 'sera_field.joint_cli', action, '--session', str(session)]
        if input_path is not None:
            command += ['--input', str(input_path)]
        result = subprocess.run(command, cwd=ROOT, text=True, encoding='utf-8', capture_output=True)
        if result.returncode:
            print(result.stdout); print(result.stderr, file=sys.stderr)
            raise SystemExit(result.returncode)
        return json.loads(result.stdout)
    def content(value):
        return {k: v for k, v in value.items() if k != 'saved_revision'}
    start = run('start', ROOT / 'examples/joint-situation.json')
    restart = run('answer')
    proposed = run('propose'); receipt = {'decision_id': proposed['id']}
    if proposed['requested'] is not None:
        f, v = proposed['requested']
        receipt['evidence'] = {'kind': 'measurement', 'id': 'performed-cli-probe', 'source': 'illustrative-simulator',
                               'performed': True, 'force': f, 'velocity': v, 'response': .8*f-.3*v+.1}
    write_json(local / 'receipt.json', receipt)
    transition = run('observe', local / 'receipt.json')
    assessment = {'decision_id': proposed['id'], 'independent_response': .48,
                  'source': 'separate illustrative goal computation', 'verifier': 'scalar formula',
                  'evidence_id': 'illustrative-goal-receipt'}
    write_json(local / 'assessment.json', assessment)
    graded = run('grade', local / 'assessment.json'); after = run('answer')
    checks = {'initial_fresh_process_restore': content(start) == content(restart),
              'graded_fresh_process_restore': content(after) == graded['returned_answer'],
              'original_goal_retained': start['original_goal'] == after['original_goal'],
              'credit_bound_to_decision': graded['decision'] == proposed['id'],
              'same_initial_packaged_tensors': start['weights'] == json.loads((ROOT / 'checkpoints/JOINT-020/SELECTION.json').read_text())['weights']}
    write_json(ROOT / 'reports/JOINT-020/RELEASE_CHECK.json', {'checks': checks, 'all_checks': all(checks.values()),
        'input_sha256': sha256(ROOT / 'examples/joint-situation.json'), 'start': start,
        'transition': transition, 'credit': graded, 'restored': after,
        'scope': 'Illustrative CLI operation checks, separate from final scientific evidence.'})
    if not all(checks.values()):
        raise ValueError('Joint documented interface verification failed')
    print(json.dumps({'joint_release_checks': checks}), flush=True)


if __name__ == '__main__':
    main()
