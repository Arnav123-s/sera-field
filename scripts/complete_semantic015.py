"""Sustained human curriculum, registered controls and exact final replay."""
import os
import subprocess
import sys

if not os.environ.get('SERA_FIELD_SUPERVISED'):
    raise SystemExit('Use scripts/supervise.py')
commands = [['train'], ['register']]
commands += [['evaluate', '--arm', arm] for arm in
             ('coupled', 'initialized', 'no_imagination', 'no_curvature', 'hypothesis_only')]
commands += [['evaluate', '--arm', 'coupled', '--replay']]
for args in commands:
    print('SEMANTIC-015 ' + ' '.join(args), flush=True)
    result = subprocess.run([sys.executable, '-X', 'utf8', '-u', '-m', 'sera_field.semantic_training', *args])
    if result.returncode:
        raise SystemExit(result.returncode)
