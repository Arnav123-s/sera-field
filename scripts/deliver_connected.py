"""Sequential release audit and real CLI exercises inside one resource lease."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import sha256, write_json


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    for script in ('summarize_connected.py','export_connected_owner.py'):
        subprocess.run([sys.executable,'-u',str(ROOT/'scripts'/script)],check=True)
    output = ROOT/'reports/CONNECTED-003/usage-examples.json'
    if output.exists():
        raise ValueError('Preserve the earlier usage demonstration')
    observations = '[[0,0,0],[0,1,1],[1,0,-0.3],[-1,0,0.3]]'
    queries = '[[0,2],[1,2],[-1,2]]'
    tasks = {
        'reading': ['read','--question','What did Alice see?','--source',str(ROOT/'examples/reading-practice.txt')],
        'arithmetic': ['math','--question','I have 5 apples and buy 3 more. How many apples do I have?'],
        'imagination': ['imagine','--observations',observations,'--queries',queries],
        'investigation': ['investigate','--observations',observations,'--queries',queries],
        'trajectory': ['motion','--observations',observations,'--velocity','0','--force-per-mass','1','--duration','1']}
    records = {}
    for name,arguments in tasks.items():
        completed = subprocess.run([sys.executable,'-m','sera_field.learned_cli',*arguments],
                                   check=True,capture_output=True,text=True,encoding='utf-8')
        records[name] = json.loads(completed.stdout)
    if len({r['checkpoint']['weights'] for r in records.values()}) != 1:
        raise ValueError('Usage tasks did not share the identical released owner')
    write_json(output,{'scope':'Usage fixtures, not additional capability scores',
                       'source_sha256':sha256(ROOT/'examples/reading-practice.txt'), 'tasks':records})
    print(json.dumps({'same_owner_in_all_five_tasks':True,'demonstration':str(output)}))


if __name__ == '__main__':
    main()
