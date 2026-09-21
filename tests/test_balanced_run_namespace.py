from pathlib import Path
import sys


def test_corrected_worker_targets_new_records_and_retention_worlds(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / 'scripts'))
    import complete_joint020 as original
    import complete_balanced021 as repaired
    from sera_field import joint_training as engine
    # Register prior values with the fixture so this configuration cannot leak
    # to unrelated tests. No data files or old experiment records are opened.
    for name in ('STUDY', 'REPORT', 'JointData', 'registered_sources', 'sources', 'physical_episode'):
        monkeypatch.setattr(original, name, getattr(original, name))
    monkeypatch.setattr(engine, 'STUDY', engine.STUDY)
    repaired.configure()
    assert original.STUDY == engine.STUDY == root / 'runs/JOINT-021'
    assert original.REPORT == root / 'reports/JOINT-021'
    episode = original.physical_episode('JOINT-020-retention-final', 3)
    assert episode['namespace'] == 'JOINT-021-retention-final'
    ordinary = original.physical_episode('some-other-declared-source', 3)
    assert ordinary['namespace'] == 'some-other-declared-source'
