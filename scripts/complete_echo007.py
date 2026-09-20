"""Sequential supervised campaign; frozen cohorts, resumable arms, exact replay."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import sha256,write_json,source_manifest,utc


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    study=ROOT/'runs/ECHO-007';study.mkdir(parents=True,exist_ok=True)
    identity={'sources':source_manifest(ROOT),'parent_selection_sha256':sha256(ROOT/'checkpoints/SCFE-004/SELECTION.json'),
              'data_manifest_sha256':sha256(ROOT/'local/CONNECTED-003-data-v1/MANIFEST.json'),
              'split_audit_sha256':sha256(ROOT/'local/CONNECTED-003-data-v1/SPLIT_AUDIT.json'),
              'previous_final_groups_sha256':sha256(ROOT/'reports/CONNECTED-003/evaluations/scfe/OPENED_GROUPS.json'),
              'arms':['echo','autograd','no_core_credit'],'seed':7107,'updates_per_arm':2048,'batch':24}
    freeze=study/'FROZEN.json'
    if freeze.exists():
        saved=json.loads(freeze.read_text())
        for name,digest in saved['sources'].items():
            if sha256(ROOT/name)!=digest:raise ValueError('Frozen executable changed: '+name)
        if {k:v for k,v in saved.items() if k!='sources'}!={k:v for k,v in identity.items() if k!='sources'}:
            raise ValueError('Frozen evidence changed')
    else:write_json(freeze,identity)
    def invoke(mode,arm,replay=False):
        command=[sys.executable,'-m','sera_field.echo_study',mode,'--arm',arm]
        if replay:command+=['--replay']
        subprocess.run(command,cwd=ROOT,check=True)
    for arm in identity['arms']:
        invoke('train',arm)
        if (study/'PAUSE_REQUEST.json').exists():return
    registration={'protocol_sha256':sha256(ROOT/'protocols/ECHO-007.md'),'study_freeze_sha256':sha256(freeze),'selections':{}}
    for arm in (*identity['arms'],'parent'):
        root=ROOT/'checkpoints/SCFE-004' if arm=='parent' else study/arm
        selected=json.loads((root/'SELECTION.json').read_text())
        registration['selections'][arm]={'selection_sha256':sha256(root/'SELECTION.json'),**selected}
    path=study/'FINAL_REGISTRATION.json'
    if path.exists():
        if json.loads(path.read_text())!=registration:raise ValueError('Registered final candidate changed')
    else:write_json(path,registration)
    for arm in (*identity['arms'],'parent'):
        invoke('evaluate',arm)
        invoke('evaluate',arm,True)
    results={arm:json.loads((study/'final'/arm/'RESULTS.json').read_text()) for arm in (*identity['arms'],'parent')}
    echo,parent,exact=results['echo'],results['parent'],results['autograd']
    pair_loss=lambda r:sum(v['loss'] for v in r['pairs'].values() if 'loss' in v)/sum('loss' in v for v in r['pairs'].values())
    checks={'reading_retained':echo['reading']['accuracy']>=parent['reading']['accuracy']-.02,
            'math_retained':echo['math']['loss']<=1.05*parent['math']['loss'],
            'pairs_retained':pair_loss(echo)<=1.05*pair_loss(parent),
            'physics_retained':echo['physics']['mse']<=1.05*parent['physics']['mse'],
            'inquiry_retained':echo['inquiry']['after_mse']<=1.10*parent['inquiry']['after_mse'],
            'trajectories_finite':echo['motion']['completed']==128,
            'weights_unchanged_during_evaluation':echo['weights_before']==echo['weights_after']}
    ratios=[echo['reading']['loss']/exact['reading']['loss'],echo['math']['loss']/exact['math']['loss'],
            pair_loss(echo)/pair_loss(exact),echo['physics']['mse']/exact['physics']['mse']]
    checks['exact_gradient_control_agreement']=sum(ratios)/4<=1.05
    write_json(study/'DECISION.json',{'checks':checks,'promote':all(checks.values()),
        'mean_normalized_objective_against_exact':sum(ratios)/4,
        'decision':'qualified_candidate' if all(checks.values()) else 'preserve_experimental_owner_and_qualified_parent',
        'completed_utc':utc(),'all_four_replays_exact':True})
    print(json.dumps(json.loads((study/'DECISION.json').read_text()),indent=2),flush=True)


if __name__=='__main__':main()
