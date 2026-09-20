import json
from pathlib import Path
import subprocess
import sys

import torch

from sera_field.concept_repair import Repair, phrases
from sera_field.concept_study import Engine
from sera_field.model import weight_hash
from sera_field.records import write_json


def test_phrase_partitions_and_balanced_pairing():
    b=phrases()
    assert len(b['train'])%2==0 and len(b['train'])==len(set(b['train']))
    assert not set(b['train']) & set(s for group in b['final'] for s in group)


def test_route_repair_resume_and_protected_state(tmp_path):
    base=Engine('full');selected=base.save(tmp_path/'base/revisions')
    write_json(tmp_path/'base/SELECTION.json',selected)
    e=Repair(tmp_path/'base',phrases());e.update();e.save(tmp_path/'repair')
    expected=e.update();expected_hash=weight_hash(e.owner)
    assert all(torch.equal(v,e.owner.state_dict()[k]) for k,v in e.protected.items())
    out=tmp_path/'next.json'
    code=('from pathlib import Path;from sera_field.concept_repair import Repair,phrases;'
          'from sera_field.records import write_json;from sera_field.model import weight_hash;'
          'e=Repair(Path('+repr(str(tmp_path/'base'))+'),phrases());'
          'e.resume(Path('+repr(str(tmp_path/'repair'))+'));r=e.update();'
          'write_json(Path('+repr(str(out))+'),{"update":r,"weights":weight_hash(e.owner)})')
    subprocess.run([sys.executable,'-c',code],check=True,cwd=Path(__file__).resolve().parents[1])
    assert json.loads(out.read_text())=={'update':expected,'weights':expected_hash}
