"""Sequential locally supervised learning, final comparison and replay."""
import os
import subprocess
import sys

if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
commands=[['train','--arm',a] for a in ('learned','disconnected')]+[['register']]
commands += [['evaluate','--arm',a] for a in
             ('learned','disconnected','initialized','uniform','information','retained_parent_memory')]
commands += [['evaluate','--arm','learned','--replay']]
for args in commands:
    print('INQUIRY-014 '+' '.join(args),flush=True)
    result=subprocess.run([sys.executable,'-X','utf8','-u','-m','sera_field.inquiry_study',*args])
    if result.returncode:raise SystemExit(result.returncode)
