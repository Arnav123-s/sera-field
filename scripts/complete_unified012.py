"""Sequential campaign; every child inherits the exclusive numerical job cap."""
import os
import subprocess
import sys


if not os.environ.get('SERA_FIELD_SUPERVISED'):
    raise SystemExit('Use scripts/supervise.py')
commands=[['train','--arm',arm] for arm in ('coupled','capture_disconnected')]
commands += [['register']]
commands += [['evaluate','--arm',arm] for arm in ('coupled','capture_disconnected','parent')]
commands += [['evaluate','--arm','coupled','--ablation',arm] for arm in ('no_memory','no_covariance')]
commands += [['evaluate','--arm','coupled','--replay']]
for args in commands:
    print('UNIFIED-012 '+ ' '.join(args),flush=True)
    result=subprocess.run([sys.executable,'-X','utf8','-u','-m','sera_field.coupled_study',*args])
    if result.returncode:raise SystemExit(result.returncode)
