import json
from pathlib import Path
import subprocess
import sys

import torch

from sera_field.concept_language import lexical_features, extend
from sera_field.concept_language_study import LexicalRepair, phrases
from sera_field.concept_study import Engine
from sera_field.model import weight_hash
from sera_field.records import write_json


def test_lexical_initial_identity_and_phrase_partition():
    e = Engine('full'); model = extend(e.owner)
    texts = ['Imagine increasing the input.', 'Imagine increasing the velocity.']
    with torch.no_grad():
        assert torch.equal(model.route_logits(texts), e.owner.route_logits(texts))
    assert torch.equal(lexical_features(texts), lexical_features(texts))
    assert not torch.equal(lexical_features(texts)[0], lexical_features(texts)[1])
    assert phrases()['unique_counts'][1:] == [32, 80]


def test_lexical_resume_and_parent_retention(tmp_path):
    base = Engine('full'); selected = base.save(tmp_path/'base/revisions')
    write_json(tmp_path/'base/SELECTION.json', selected)
    e = LexicalRepair(tmp_path/'base', phrases()); e.update(); e.save(tmp_path/'repair')
    expected = e.update(); digest = weight_hash(e.owner)
    assert all(torch.equal(v, e.owner.state_dict()[k]) for k,v in e.protected.items())
    out = tmp_path/'next.json'
    code = ('from pathlib import Path;from sera_field.concept_language_study import LexicalRepair,phrases;'
            'from sera_field.model import weight_hash;from sera_field.records import write_json;'
            'e=LexicalRepair(Path('+repr(str(tmp_path/'base'))+'),phrases());'
            'e.resume(Path('+repr(str(tmp_path/'repair'))+'));r=e.update();'
            'write_json(Path('+repr(str(out))+'),{"update":r,"weights":weight_hash(e.owner)})')
    subprocess.run([sys.executable,'-c',code],check=True,cwd=Path(__file__).resolve().parents[1])
    assert json.loads(out.read_text()) == {'update':expected,'weights':digest}
