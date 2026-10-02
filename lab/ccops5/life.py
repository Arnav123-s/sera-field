"""ccops5 lab | one whole life, start to finish.

Built as an isolated experiment. Not part of sera-field.
"""
import time

import numpy as np
import torch

from . import world as W
from .baseline import WeightsOnly
from .mind import Mind, describe_law


def live_life(seed, mode, *, limit=None):
    torch.set_num_threads(1)
    started = time.perf_counter()
    plan = W.life_plan(seed)
    if limit:
        plan = plan[:limit]
    agent = WeightsOnly(seed, parts={'baseline_parts': 'sum', 'baseline_sets': 'sets'}.get(mode, False),
                        blind_new=mode == 'baseline_words') if mode.startswith('baseline') else Mind(mode, seed)
    records = []
    for index, ep in enumerate(plan):
        # Same world noise stream per situation for every learner with this seed.
        records.append(agent.live(ep, np.random.default_rng([seed, index, 7]), index))
    rng = np.random.default_rng([seed, 5])
    laws = []
    for i, law in enumerate(agent.laws):
        # Older laws this learner could use where this law was found.
        older = [o for o in agent.laws[:i] if mode != 'no_reuse' or o.origin in ('body', law.origin)]
        laws.append({'name': law.name, 'origin': law.origin, 'looks_like': describe_law(law, older, rng)})
    remembered = [k['name'] for k in getattr(agent, 'kinds', []) if k['committed']]
    return {'seed': seed, 'mode': mode, 'records': records, 'events': agent.events, 'laws': laws,
            'objects_remembered': remembered, 'math_rule': getattr(agent, 'rule', None),
            'seconds': time.perf_counter() - started}
