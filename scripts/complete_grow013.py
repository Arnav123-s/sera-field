"""Sequential training and untouched final cohorts under the shared supervisor."""
import os
import subprocess
import sys

if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
commands=[['train'],['register']]
commands += [['evaluate','--arm',a] for a in ('learned','fixed','no_extension')]
commands += [['evaluate','--arm','learned','--replay']]
for args in commands:
    print('GROW-013 '+' '.join(args),flush=True)
    result=subprocess.run([sys.executable,'-X','utf8','-u','-m','sera_field.extension_study',*args])
    if result.returncode:raise SystemExit(result.returncode)
