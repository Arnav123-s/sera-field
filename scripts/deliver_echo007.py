"""Verify the assessed package through real task interfaces sequentially."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import write_json,sha256


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    subprocess.run([sys.executable,str(ROOT/'scripts/package_echo007.py')],check=True)
    output=ROOT/'reports/ECHO-007/USAGE_EXAMPLES.json'
    if output.exists():raise ValueError('Preserve previous demonstrations')
    observations='[[0,0,0],[0,1,1],[1,0,-0.3],[-1,0,0.3]]'
    queries='[[0,2],[1,2],[-1,2]]'
    tasks={'reading':['read','--question','What did Alice see?','--source',str(ROOT/'examples/reading-practice.txt')],
           'arithmetic':['math','--question','I have 5 apples and buy 3 more. How many apples do I have?'],
           'imagination':['imagine','--observations',observations,'--queries',queries],
           'investigation':['investigate','--observations',observations,'--queries',queries],
           'trajectory':['motion','--observations',observations,'--velocity','0','--force-per-mass','1','--duration','1']}
    results={}
    for name,args in tasks.items():
        result=subprocess.run([sys.executable,'-m','sera_field.learned_cli','--training',str(ROOT/'checkpoints/ECHO-007'),*args],
                              check=True,capture_output=True,text=True,encoding='utf-8')
        results[name]=json.loads(result.stdout)
    identities={r['checkpoint']['weights'] for r in results.values()}
    expected=json.loads((ROOT/'checkpoints/ECHO-007/SELECTION.json').read_text())['weights']
    if identities!={expected}:raise ValueError('Different owners were used across task interfaces')
    write_json(output,{'scope':'Unchanged usage fixtures, not capability evaluation or training',
        'source_sha256':sha256(ROOT/'examples/reading-practice.txt'),'same_owner_all_five_interfaces':True,'tasks':results})
    print('Five actual task interfaces verified from the same assessed echo owner')


if __name__=='__main__':main()
