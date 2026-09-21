"""Reuse the frozen joint engine with an explicit repaired data/run namespace."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import complete_joint020 as driver
from sera_field import joint_training as engine
from sera_field.balanced_joint_data import BalancedJointData, registered_sources
from sera_field.records import sha256


def configure():
    # Only experiment configuration changes in this fresh interpreter. The
    # original engine files and all JOINT-020 outputs stay byte-for-byte intact.
    study = ROOT / 'runs/JOINT-021'
    engine.STUDY = study; driver.STUDY = study; driver.REPORT = ROOT / 'reports/JOINT-021'
    driver.JointData = BalancedJointData; driver.registered_sources = registered_sources
    original_sources = driver.sources
    def sources():
        value = original_sources()
        for name in ('sera_field/balanced_joint_data.py', 'scripts/complete_balanced021.py'):
            value['implementation'][name] = sha256(ROOT / name)
        value['experiment_namespace'] = 'JOINT-021'
        return value
    driver.sources = sources
    original_episode = driver.physical_episode
    def episode(namespace, number, **kwargs):
        if namespace == 'JOINT-020-retention-final':
            namespace = 'JOINT-021-retention-final'
        return original_episode(namespace, number, **kwargs)
    driver.physical_episode = episode


if __name__ == '__main__':
    configure(); driver.main()
