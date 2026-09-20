"""Exercise persistent acquired-model use through separate real CLI processes."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import write_json,sha256
from sera_field.concept_world import World


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    subprocess.run([sys.executable,str(ROOT/'scripts/package_concept011.py')],check=True)
    root=ROOT/'runs/CONCEPT-011/delivery';root.mkdir(parents=True,exist_ok=True)
    if (root/'RESULTS.json').exists():raise ValueError('Preserve the completed delivery')
    session=root/'session'
    prefix=[sys.executable,'-m','sera_field.session_cli','--training',str(ROOT/'checkpoints/CONCEPT-011'),
            '--session',str(session)]
    def call(args):
        result=subprocess.run(prefix+args,check=True,capture_output=True,text=True,encoding='utf-8')
        return json.loads(result.stdout)
    first=call(['new','--input',str(ROOT/'examples/concept-task.json')])
    restart=call(['solve'])
    if first!=restart:raise ValueError('Fresh-process restart differs')
    oldpointer=json.loads((session/'CURRENT.json').read_text())
    task={'question':'Explain the acceleration effect of higher control input.',
          'operating_point':[.5,1.],'predict':[[.5,1.5]],'name':'reuse the acquired relationship'}
    write_json(root/'followup.json',task)
    followup=call(['ask','--task',str(root/'followup.json')])
    if followup['result']['concept_id']!=first['result']['concept_id']:raise ValueError('Task refit concept')
    if followup['result']['original_goal']!=first['result']['original_goal']:raise ValueError('Original goal changed')
    if json.loads((session/'CURRENT.json').read_text())!=oldpointer:raise ValueError('Question changed session')
    choice=first['result']['next_investigation']
    independent=World(1.,-.5,0.,.2)
    actual=independent.intervene([choice['requested_velocity'],choice['requested_control_input']])
    receipt={'kind':'independent_simulation','source':'concept_world.World delivery fixture',
             'source_sha256':sha256(ROOT/'sera_field/concept_world.py'),'measurement_id':'delivery-followup',
             'requested':actual['requested'],'performed':actual['performed'],'measured':actual['observation']}
    write_json(root/'receipt.json',receipt)
    revised=call(['observe','--receipt',str(root/'receipt.json')])
    if revised['result']['original_goal']!=first['result']['original_goal']:raise ValueError('Failed to return original goal')
    if revised['result']['concept_id']==first['result']['concept_id']:raise ValueError('Evidence did not revise concept')
    if not (session/(oldpointer['sha256']+'.json')).exists():raise ValueError('Earlier revision lost')
    current=json.loads((session/'CURRENT.json').read_text())
    repeat=subprocess.run(prefix+['observe','--receipt',str(root/'receipt.json')],capture_output=True,text=True)
    if repeat.returncode==0 or json.loads((session/'CURRENT.json').read_text())!=current:
        raise ValueError('Duplicate evidence changed current revision')
    if call(['solve'])!=revised:raise ValueError('Revised restart differs')
    retained={}
    for name,args in {'read':['read','--question','What did Alice see?','--source',str(ROOT/'examples/reading-practice.txt')],
                      'math':['math','--question','I have 5 apples and buy 3 more. How many apples do I have?']}.items():
        outputs=[]
        for owner in ('ECHO-007','CONCEPT-011'):
            proc=subprocess.run([sys.executable,'-m','sera_field.learned_cli','--training',str(ROOT/'checkpoints'/owner),*args],
                                check=True,capture_output=True,text=True,encoding='utf-8')
            outputs.append(json.loads(proc.stdout)['result'])
        if outputs[0]!=outputs[1]:raise ValueError('Retained interface changed: '+name)
        retained[name]={'exact_previous_output':True,'result':outputs[1]}
    write_json(root/'RESULTS.json',{'scope':'Engineering usage fixtures, separate from sealed capability assessment',
        'first':first,'followup':followup,'independent_receipt':receipt,'revised':revised,
        'checks':{'original_goal_retained':True,'concept_reused_for_new_task':True,'independent_outcome_added':True,
                  'exact_initial_and_revised_restart':True,'duplicate_rejected':True,'older_revision_preserved':True,
                  'earlier_reading_and_math_exact':True},'retained_interfaces':retained})
    print('Persistent creation, five-use answers, task reuse, measured revision, duplicate rejection and exact restarts passed.')


if __name__=='__main__':main()
