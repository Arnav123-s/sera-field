"""Finite procedure curriculum followed by frozen controls and exact replay."""
import os
import subprocess
import sys

if not os.environ.get('SERA_FIELD_SUPERVISED'):
    raise SystemExit('Use scripts/supervise.py')

commands = [['train'], ['register']]
commands += [['evaluate', '--arm', arm] for arm in
             ('learned', 'initialized', 'no_history', 'reciprocal', 'equal_rates')]
commands += [['evaluate', '--arm', 'learned', '--replay']]
for args in commands:
    print('HISTORY-016 ' + ' '.join(args), flush=True)
    process = subprocess.run([sys.executable, '-X', 'utf8', '-u', '-m', 'sera_field.history_training', *args])
    if process.returncode:
        raise SystemExit(process.returncode)
