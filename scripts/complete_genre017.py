"""Complete matched human curricula before unlocking any final assessment."""
import os
import subprocess
import sys

if not os.environ.get('SERA_FIELD_SUPERVISED'):
    raise SystemExit('Use scripts/supervise.py')
commands = [['train', '--arm', arm] for arm in ('exact_noisy', 'exact_clean', 'gaussian_noisy')]
commands += [['register']]
commands += [['evaluate', '--arm', arm] for arm in
             ('exact_noisy', 'exact_clean', 'gaussian_noisy', 'parent', 'no_imagination', 'no_action')]
commands += [['evaluate', '--arm', 'exact_noisy', '--replay']]
for command in commands:
    print('GENRE-017 ' + ' '.join(command), flush=True)
    result = subprocess.run([sys.executable, '-X', 'utf8', '-u', '-m', 'sera_field.genre_training', *command])
    if result.returncode: raise SystemExit(result.returncode)
