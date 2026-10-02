"""The legacy SERA minds (v3, revisions 3-5), kept for reference and comparison; quarantined 2026-10-01.

Nothing in `sera/one.py` (the one SERA) reaches these modules. They import their siblings as `from . import x`, and
some siblings are live modules that stayed in `sera/`: those names are served from `sera` here, so the old code runs
unchanged and shares the live modules (one copy of each). Scripts: `legacy/sera_v3/scripts/`, run from the repo root.
Tests: `legacy/sera_v3/tests/`, not part of the default suite (`tests/`).
"""
import importlib

LIVE = ('compact', 'design', 'dictionary', 'field', 'general', 'lang', 'lawspace', 'novel', 'one', 'phi', 'pyprint',
        'synth', 'talk', 'tasks', 'worlds')


def __getattr__(name):
    if name in LIVE:
        return importlib.import_module('sera.' + name)
    raise AttributeError(name)
