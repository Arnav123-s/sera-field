"""Generations (B5): wake at the frontier -> sleep (learn from verified discoveries, dream the library's empty slots)
-> evaluate on a frozen suite. Measures whether each discovery makes the next one cheaper (docs/B5_COMPOUNDING.md).

Arms (docs/B5_COMPOUNDING.md; the library prior D12 waits for review, so it is not in any arm yet):
  full      learns from verified discoveries (generation 0 also from the caretaker) + empty-slot dreams
  no-slots  the same without empty-slot dreams
  frozen    never learns (the control)
Per generation the record holds: the wake worlds (level, split, never-met?, right, wrong, throws, seconds), library
size and admissions, the empty slots dreamed, sleep seconds, and the evaluation: the imagination's rank / probability
of the true law on the full frozen suite (cheap, every generation) and full-mind results on the evaluation subset.
C_k = wake + sleep CPU seconds.
"""
import os
import time

import numpy as np
import torch

from ccops5.core import checker, grammar
from . import compact as C, dreams as D, imagine as I, library as LB, mind as SM, school as SC, worlds as SW

import core_check

ARMS = {'full': dict(learn=True, slots=True), 'no-slots': dict(learn=True, slots=False),
        'frozen': dict(learn=False, slots=False),
        # plan revision 2 (P4): learn from every graded imagination on the credit ladder (sera.grade)
        'ladder': dict(learn='ladder', slots=True), 'ladder-no-slots': dict(learn='ladder', slots=False)}
ARMS['certified'] = ARMS['full']              # the v3.0 learning: only the law a world proved (or the caretaker's)
LEVELS = (1, 2, 3, 4)


def frontier(history):
    """The lowest level whose recent solve rate is in [0.3, 0.8]; else the lowest above 0.8's; else level 1."""
    rates = {}
    for lv in LEVELS:
        recent = [h['right'] for h in history if h['level'] == lv][-6:]
        rates[lv] = np.mean(recent) if len(recent) >= 3 else None
    for lv in LEVELS:
        if rates[lv] is None or 0.3 <= rates[lv] <= 0.8:
            return lv
    solved = [lv for lv in LEVELS if rates[lv] is not None and rates[lv] > 0.8]
    return min(max(solved) + 1, LEVELS[-1]) if solved else LEVELS[0]


def suite(seed, per=4):
    """The frozen evaluation suite: (name, level, split, index) — fixed for every generation and arm."""
    groups = [('L1', 1, 'dream'), ('L2', 2, 'dream'), ('L3', 3, 'dream'), ('L4', 4, 'dream'),
              ('L2-held', 2, 'held'), ('L3-held', 3, 'held'), ('L4-held', 4, 'held')]
    return [(g, lv, sp, 30_000 + 100 * gi + i) for gi, (g, lv, sp) in enumerate(groups) for i in range(per)]


def slot_dreams(rng, slots, n):
    """Dream tables for laws the library predicts (a slot is dreamed until a valid dream of it is made)."""
    F, Wf, Y = [], [], []
    tries = 0
    while len(Y) < n and slots and tries < 20 * n:
        tries += 1
        fam = slots[rng.integers(len(slots))]
        d = D.dream(rng, family=fam)
        if d is None:
            continue
        f, w, _ = C.compact(d[2])
        F.append(f)
        Wf.append(w)
        Y.append(D.FAMILY_INDEX[fam])
    if not Y:
        return None
    return torch.tensor(np.stack(F), dtype=torch.float32), torch.tensor(np.stack(Wf)), torch.tensor(Y)


def imagination_metrics(model, worlds):
    fams, ranks, ps = [], [], []
    for w in worlds:
        truth = grammar.canonical(w.spec.family)
        props, _ = I.imagine_world(model, w.throws, 16)
        order = [f for f, _ in props]
        ranks.append(order.index(truth) + 1 if truth in order else None)
        ps.append(dict(props).get(truth, 0.0))
    return dict(top1=float(np.mean([r == 1 for r in ranks])), top16=float(np.mean([r is not None for r in ranks])),
                p_true=float(np.mean(ps)))


def run_world(model, w, eps=0.2, design=False):
    t0 = time.process_time()
    r = SM.Mind(model, w.sigma, eps=eps, budget=3 * w.n_situations, design=design).live(w)
    verified = bool(r.sure and checker.check(r.certificate, r.ledger.throws, w.sigma)[0])
    truth = grammar.canonical(w.spec.family)
    return r, dict(level=w.spec.level, truth=grammar.name(truth), claim=grammar.name(r.claim), sure=r.sure,
                   verified=verified, right=bool(verified and grammar.canonical(r.claim) == truth),
                   wrong=bool(r.sure and core_check.wrong(r.certificate, w)), sure_unverified=bool(r.sure and not verified),
                   throws=r.throws, own=r.own_pushes, cpu=round(time.process_time() - t0, 1))


def _save(path, st, model, learner, lib, rng):
    """The life's whole state after a world: counters and records, the imagination, the learner (optimizer, what it
    learned, its sampler, the slot dreams it added), the library and the random streams. Atomic (tmp, then rename)."""
    extra = None
    if learner is not None:
        n0 = learner.n_base
        extra = (learner.dF[n0:].clone(), learner.dW[n0:].clone(), learner.dY[n0:].clone())
    blob = dict(st=st, model=model.state_dict(), lib=lib, rng=rng.bit_generator.state, torch_rng=torch.get_rng_state(),
                learner=None if learner is None else dict(opt=learner.opt.state_dict(), F=learner.F, W=learner.W,
                                                         Y=learner.Y, rng=learner.rng.bit_generator.state, extra=extra,
                                                         grades=getattr(learner, 'grades', None)))
    tmp = str(path) + '.tmp'
    torch.save(blob, tmp)
    os.replace(tmp, path)


def _restore(path, model, learner, rng):
    blob = torch.load(path, map_location='cpu', weights_only=False)
    model.load_state_dict(blob['model'])
    model.eval()
    rng.bit_generator.state = blob['rng']
    torch.set_rng_state(blob['torch_rng'])
    if learner is not None:
        L = blob['learner']
        learner.opt.load_state_dict(L['opt'])
        learner.F, learner.W, learner.Y = L['F'], L['W'], L['Y']
        learner.rng.bit_generator.state = L['rng']
        if L.get('grades') is not None:
            learner.grades = L['grades']
        n0 = learner.n_base
        learner.dF = torch.cat([learner.dF[:n0], L['extra'][0]])
        learner.dW = torch.cat([learner.dW[:n0], L['extra'][1]])
        learner.dY = torch.cat([learner.dY[:n0], L['extra'][2]])
    return blob['st'], blob['lib']


def live(seed, arm, model_path, generations=4, wake=12, eval_every=1, eval_per=2, dreams_set='dreams-v1',
         progress=print, checkpoint=None, design=False):
    """One life. checkpoint: a path; the whole state is saved there after every world (and after each sleep), and a
    life that finds it resumes where it stopped, so a crash costs at most one world (the laptop crashed twice on
    2026-09-24; a life is about three hours). A resumed life equals an uninterrupted one (tests/sera/test_generations.py)."""
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    cfg = ARMS[arm]
    model = I.Imagination()
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    learner = ((SC.LadderLearner if cfg['learn'] == 'ladder' else SC.Learner)(model, dreams_set, seed=seed)
               if cfg['learn'] else None)
    if learner is not None:
        learner.n_base = len(learner.dY)
    lib = LB.Library()
    rng = np.random.default_rng([seed, 777])
    suite_worlds = [SW.make(seed, idx, lv, sp) for _, lv, sp, idx in suite(seed)]
    eval_worlds = [w for i, w in enumerate(suite_worlds) if i % 4 < eval_per]      # the full-mind subset
    st = dict(g=0, phase=None, i=0, rec=None, rows=[], history=[], gens=[], slot_dreamed=set(), wake_cpu=0.0)
    if checkpoint is not None and os.path.exists(checkpoint):
        st, lib = _restore(checkpoint, model, learner, rng)
    save = (lambda: _save(checkpoint, st, model, learner, lib, rng)) if checkpoint is not None else (lambda: None)
    history = st['history']
    while st['g'] <= generations:                           # generation 0 = before any wake (the starting point)
        g = st['g']
        if st['rec'] is None:
            st.update(rec=dict(generation=g, arm=arm), phase='wake' if g > 0 else 'eval', i=0, rows=[], wake_cpu=0.0)
        rec = st['rec']
        if st['phase'] == 'wake':
            while st['i'] < wake:
                i = st['i']
                t_world = time.process_time()
                lv = frontier(history)
                w = SW.make(seed, 50_000 + 1000 * g + i, lv, 'any')
                truth = grammar.canonical(w.spec.family)
                never_met = truth not in lib.met
                feats, wv, _ = C.compact(w.throws)
                r, row = run_world(model, w, design=design)
                row.update(n=i, never_met=never_met, held=SW.held_out(truth))
                lib.new_world()                             # every world is one e-LOND test (review L1)
                if row['verified']:
                    row['admitted'] = lib.offer(r.claim, r.certificate, (g, i))
                    row['admitted_wrong'] = bool(row['admitted'] and row['wrong'])     # reported directly (review L2)
                label = None
                if cfg['learn']:
                    if g == 1:
                        label = truth                       # generation 1: the caretaker says which law was right
                    elif row['verified']:
                        label = grammar.canonical(r.claim)  # afterwards: only its own checked discoveries
                if label is not None:
                    lib.met.add(label)
                    if cfg['learn'] != 'ladder':
                        learner.learn(feats, wv, label)
                if cfg['learn'] == 'ladder':                # every imagination graded, the wrong ones included
                    from . import grade as G
                    gr = G.grade(r.ledger, r.certificate, row['verified'], taught=truth if g == 1 else None,
                                 q_start=getattr(r, 'q_start', None), alarm=bool(r.alarm))
                    row.update(flaw=gr.flaw, questions=len(gr.questions))
                    learner.learn_graded(feats, wv, gr)
                history.append(row)
                st['rows'].append(row)
                st['wake_cpu'] += time.process_time() - t_world
                st['i'] += 1
                save()
                progress(dict(generation=g, arm=arm, **row))
            rec['wake'] = st['rows']
            rec['wake_cpu'] = round(st['wake_cpu'], 1)
            t_sleep = time.process_time()
            slots = lib.empty_slots() if cfg['slots'] else []
            st['slot_dreamed'].update(slots)
            rec['slots'] = [grammar.name(s) for s in slots[:12]]
            if cfg['learn']:
                extra = slot_dreams(rng, slots, 64) if slots else None
                if extra is not None:
                    learner.dF = torch.cat([learner.dF, extra[0]])
                    learner.dW = torch.cat([learner.dW, extra[1]])
                    learner.dY = torch.cat([learner.dY, extra[2]])
                learner.train(200)                                     # the sleep: a longer consolidation
            rec['sleep_cpu'] = round(time.process_time() - t_sleep, 1)
            rec['library'] = len(lib.entries)
            st.update(phase='eval', i=0, rows=[])
            save()
        if 'imagination' not in rec:
            rec['imagination'] = imagination_metrics(model, suite_worlds)
        if g % eval_every == 0:
            while st['i'] < len(eval_worlds):               # status of each eval law: met / slot-dreamed / neither (L3)
                w = eval_worlds[st['i']]
                truth = grammar.canonical(w.spec.family)
                row = run_world(model, w, design=design)[1]
                row['status'] = ('met' if truth in lib.met else 'slot-dreamed' if truth in st['slot_dreamed']
                                 else 'neither')
                st['rows'].append(row)
                st['i'] += 1
                save()
            rows = st['rows']
            rec['eval'] = dict(n=len(rows), right=sum(r['right'] for r in rows), wrong=sum(r['wrong'] for r in rows),
                               sure_unverified=sum(r['sure_unverified'] for r in rows),
                               throws=float(np.mean([r['throws'] for r in rows])),
                               by_status={s: dict(n=sum(r['status'] == s for r in rows),
                                                  right=sum(r['right'] for r in rows if r['status'] == s))
                                          for s in ('met', 'slot-dreamed', 'neither')})
        st['gens'].append(rec)
        st.update(g=g + 1, rec=None)
        save()
        progress(dict(generation=g, arm=arm, summary=True, imagination=rec['imagination'], eval=rec.get('eval'),
                      library=rec.get('library')))
    return dict(seed=seed, arm=arm, generations=st['gens'], library=[e['family'] for e in lib.entries],
                chain_ok=lib.verify_chain())
