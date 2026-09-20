"""Continuation fixtures are engineering tests, never curriculum/evaluation data."""
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import torch
from sera_field.echo_study import EchoEngine
from sera_field.model import weight_hash
from sera_field.records import write_json
from sera_field.study_inquiry import load_selected


def fixture_data():
    reading=[{'id':str(i),'group':str(i),'track':'human_reading','question':'Which color?',
              'options':['The flower is yellow.','The book is blue.'],'targets':[0]} for i in range(24)]
    return SimpleNamespace(manifest_sha='engineering-fixture-only',train={'reading':reading},
                           tracks=[],pairs={})


def test_exact_next_update_after_fresh_interpreter_restart(tmp_path):
    first=EchoEngine(fixture_data(),'echo');first.update();first.save(tmp_path/'revisions')
    expected=first.update();expected_weights=weight_hash(first.owner)
    result=tmp_path/'child-result.json'
    script=('import json,runpy;from pathlib import Path;'
            'n=runpy.run_path("tests/test_echo_study.py");'
            'e=n["EchoEngine"](n["fixture_data"](),"echo");'
            'e.resume(Path('+repr(str(tmp_path/'revisions'))+'));'
            'r=e.update();n["write_json"](Path('+repr(str(result))+'),'
            '{"update":r,"weights":n["weight_hash"](e.owner)})')
    subprocess.run([sys.executable,'-c',script],check=True,cwd=Path(__file__).resolve().parents[1])
    observed=json.loads(result.read_text())
    assert observed=={'update':expected,'weights':expected_weights}


def test_echo_owner_round_trip_and_frozen_policy(tmp_path):
    engine=EchoEngine(fixture_data(),'echo')
    original={k:v.clone() for k,v in engine.owner.state_dict().items() if k.startswith('investigation.')}
    engine.update();manifest=engine.save(tmp_path/'revisions')
    write_json(tmp_path/'SELECTION.json',{**manifest,'score':1.,'step':1})
    restored,selection=load_selected(tmp_path)
    assert restored.specification()==engine.owner.specification()
    assert weight_hash(restored)==selection['weights']==weight_hash(engine.owner)
    assert all(torch.equal(v,restored.state_dict()[k]) for k,v in original.items())
