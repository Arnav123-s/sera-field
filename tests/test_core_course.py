import copy
import random

import pytest
import torch

from sera_field.core_owner import CoreOwner
from sera_field.native_owner import NativeConfig
from sera_field.core_course_data import pair, partition
from sera_field.core_cross_use import five_uses, assess_five_uses
from sera_field.joint_training import cycle
from sera_field.core_course import save, load
from sera_field.model import weight_hash


def human(i):
    return {'id': str(i), 'source_group': 'fixture-'+str(i), 'premise': 'A person observes a moving object.',
            'hypothesis': 'A person is watching.', 'target': 0}


def test_mixed_course_uses_actual_core_and_counterbalances_family_and_order():
    rows = pair([human(i) for i in range(4)], 'CORE-022-engineering')
    assert {(r['text_first'], r['physics']['teacher_only']['quadratic']) for r in rows} == {(a,b) for a in (False,True) for b in (False,True)}
    torch.manual_seed(22249); owner = CoreOwner(NativeConfig(nodes=3, rounds=1), program_slots=8)
    loss, cases, diagnostics = cycle(owner, rows, training=True)
    assert torch.isfinite(loss) and len(cases) == 4
    loss.backward()
    assert owner.choice.weight.grad is not None and owner.choice.weight.grad.norm() > 0
    assert any(p.grad is not None and p.grad.norm() > 0 for p in owner.core.parameters())
    assert all(c['behavior_probability'] == .1 for c in cases)


def test_five_uses_share_unchanged_state_and_require_performed_receipts():
    torch.manual_seed(22251); owner = CoreOwner(NativeConfig(nodes=3, rounds=1), program_slots=8)
    with torch.no_grad():
        state = owner.physical_state(torch.tensor([[[-1.,0.,-.7],[1.,0.,.7]]]))
    record = five_uses(owner, state, velocity=0., force=.5, changed_force=1., target=.35, candidates=[-1.,0.,.5,1.])
    assert record['observations_added'] == 0 and record['separate_models_fitted'] == 0 and record['novelty_credit'] == 0
    receipts = [{'id': str(i), 'source_sha256': 'a'*64, 'performed': True, 'force': f, 'velocity': 0., 'response': .7*f}
                for i,f in enumerate([-1.,0.,.5,1.])]
    result = assess_five_uses(record, receipts)
    assert result['performed_controls_checked'] and result['best_observed_grid_error'] == 0
    with pytest.raises(ValueError): assess_five_uses(record, receipts[:-1])
    changed = copy.deepcopy(receipts); changed[0]['velocity'] = .1
    with pytest.raises(ValueError): assess_five_uses(record, changed)
    with torch.no_grad():
        revised, _ = owner.observe(state, owner.encode_numbers(torch.tensor([1.]),torch.tensor([0.]),torch.tensor([-.7])))
    updated = five_uses(owner, revised, velocity=0., force=.5, changed_force=1., target=.35, candidates=[-1.,0.,.5,1.])
    assert updated['weights'] == record['weights'] and updated['state'] != record['state']
    assert updated['observed_events'] == record['observed_events']+1
    assert updated['forward']['response'] != record['forward']['response']


def test_course_partition_ignores_labels_and_is_stable_across_views():
    before = random.getstate(); one = [partition('source-group-'+str(i)) for i in range(1000)]
    assert set(one) == {'train','development','final'}
    assert one == [partition('source-group-'+str(i)) for i in range(1000)] and random.getstate() == before


def test_course_checkpoint_preserves_next_actual_update_and_rejects_sources(tmp_path):
    torch.manual_seed(22253); random.seed(22253)
    owner = CoreOwner(NativeConfig(nodes=3, rounds=1), program_slots=8)
    optimizer = torch.optim.AdamW(owner.parameters(), lr=.001)
    def update(model, opt):
        opt.zero_grad(set_to_none=True)
        loss = model.semantic(['A person watches.'], ['Someone sees.']).square().mean()
        loss.backward(); opt.step()
        return weight_hash(model), torch.rand(3).tolist(), random.random()
    update(owner, optimizer)
    save(tmp_path, owner, optimizer, 1, [], {'fixture': 1}, {'fixture': 'checked'}, receipts=[])
    expected = update(owner, optimizer)
    restored, opt, payload, record = load(tmp_path, expected_sources={'fixture': 'checked'})
    assert payload['cursor'] == record['cursor'] == 1
    assert update(restored, opt) == expected
    with pytest.raises(ValueError, match='source or protocol'):
        load(tmp_path, expected_sources={'fixture': 'changed'})
