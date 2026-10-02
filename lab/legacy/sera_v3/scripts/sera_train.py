"""Train the imagination on dream shards and test it on real, held-out worlds (B2). CPU, one thread, heat-guarded.

  python legacy/sera_v3/scripts/sera_train.py --dreams dreams-v1 --name imagine-v1 --epochs 8
Reads D:/ai/labs/ccops5-sera-lab/sera-runs/<dreams>/shard-*.npz (the last --val-shards are held for validation).
Writes sera-runs/<name>/: model.pt, progress.jsonl (per epoch), eval.json (final, per suite and level), and
suites-v2.pkl (shared: the fixed real worlds, compacted once).

Real-world suites (made once, teacher throws only, i.e. what the mind sees before its own experiments):
  L1..L5          laws of dreamed kinds, fresh worlds (seed 1, indices 5000+)
  L2..L4-held     held-out structures never dreamed (seed 1, indices 7000+)
Metrics: top-1 and top-16 hit rate of the true law, mean probability on it, and the same for the no-learning
baseline (greedy reading of the evidence table: best single term, then best term added to it).
"""
import argparse
import glob
import json
import pickle
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2]))  # the repo root
sys.path.insert(0, str(ROOT.parents[2] / 'scripts'))  # governor, heat_guard
sys.path.insert(0, str(ROOT))
RUNS = Path('D:/ai/labs/ccops5-sera-lab/sera-runs')


def load(dreams, val_shards):
    files = sorted(glob.glob(str(RUNS / dreams / 'shard-*.npz')))
    if len(files) <= val_shards:
        raise SystemExit(f'only {len(files)} shards in {dreams}')
    parts = [np.load(f) for f in files]
    cat = lambda key, sl: np.concatenate([p[key] for p in parts[sl]])
    tr, va = slice(0, len(files) - val_shards), slice(len(files) - val_shards, None)
    return ({k: cat(k, tr) for k in ('features', 'world', 'label', 'level')},
            {k: cat(k, va) for k in ('features', 'world', 'label', 'level')}, len(files))


def suites():
    """Real worlds, compacted once: {suite: dict(features, world, label, level, names)}."""
    path = RUNS / 'suites-v3.pkl'          # v3: worlds validated with the identifiability rule (review F3)
    if path.exists():
        return pickle.loads(path.read_bytes())
    from legacy.sera_v3 import compact as C, dreams as D, worlds as SW
    plan = [(f'L{lv}', lv, 'dream', 5000) for lv in range(1, 6)] + [(f'L{lv}-held', lv, 'held', 7000) for lv in (2, 3, 4)]
    out = {}
    for name, level, split, base in plan:
        F, Wf, lab, ex = [], [], [], []
        for i in range(30):
            w = SW.make(1, base + i, level, split)
            f, wv, extras = C.compact(w.throws)
            F.append(f)
            Wf.append(wv)
            lab.append(D.FAMILY_INDEX[tuple(w.spec.family)])
            ex.append(extras)
        out[name] = dict(features=np.stack(F), world=np.stack(Wf), label=np.array(lab), extras=ex)
        print(f'suite {name}: 30 worlds', flush=True)
    path.write_bytes(pickle.dumps(out))
    return out


def greedy_baseline(features, extras):
    """No learning: the best single term, then the best term added to it (both as laws), from the evidence table."""
    from legacy.sera_v3 import compact as C, dreams as D
    from ccops5.core import grammar
    out = []
    for f, ex in zip(features, extras):
        best = C.TERMS[ex['best']]
        order = np.argsort(-f[:, 6].astype(float))
        props = [(best,)] + [grammar.canonical((best, C.TERMS[j])) for j in order[:15]]
        out.append([p for p in props if p in D.FAMILY_INDEX][:16])
    return out


def score(props, labels):
    from legacy.sera_v3 import dreams as D
    fams = [D.FAMILIES[i] for i in labels]
    top1 = np.mean([bool(p) and p[0] == t for p, t in zip(props, fams)])
    topk = np.mean([t in p for p, t in zip(props, fams)])
    return round(float(top1), 3), round(float(topk), 3)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--dreams', default='dreams-v1')
    ap.add_argument('--name', default='imagine-v1')
    ap.add_argument('--epochs', type=int, default=8)
    ap.add_argument('--batch', type=int, default=256)
    ap.add_argument('--lr', type=float, default=2e-3)
    ap.add_argument('--val-shards', type=int, default=5)
    ap.add_argument('--threads', type=int, default=1)
    a = ap.parse_args(argv)
    import torch
    import heat_guard
    from legacy.sera_v3 import imagine as I
    torch.set_num_threads(a.threads)
    torch.manual_seed(1)
    out = RUNS / a.name
    out.mkdir(parents=True, exist_ok=True)
    tr, va, n_files = load(a.dreams, a.val_shards)
    print(f'train {len(tr["label"])} dreams, validation {len(va["label"])} ({n_files} shards)', flush=True)
    real = suites()
    model = I.Imagination()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    n = len(tr['label'])
    steps = a.epochs * ((n + a.batch - 1) // a.batch)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=steps, pct_start=0.1)
    Ft = torch.tensor(tr['features'])
    Wt, Yt = torch.tensor(tr['world']), torch.tensor(tr['label'], dtype=torch.long)
    Fv, Wv, Yv = (torch.tensor(va['features'], dtype=torch.float32), torch.tensor(va['world']),
                  torch.tensor(va['label'], dtype=torch.long))
    prog = (out / 'progress.jsonl').open('a', encoding='utf-8')
    for epoch in range(a.epochs):
        t0 = time.perf_counter()
        perm = torch.randperm(n)
        model.train()
        tot = 0.0
        for s in range(0, n, a.batch):
            idx = perm[s:s + a.batch]
            L = I.loss(model, Ft[idx].float(), Wt[idx], Yt[idx])
            opt.zero_grad(set_to_none=True)
            L.backward()
            opt.step()
            sched.step()
            tot += float(L) * len(idx)
        model.eval()
        with torch.no_grad():
            vl = float(sum(I.loss(model, Fv[i:i + 1024], Wv[i:i + 1024], Yv[i:i + 1024]) * len(Yv[i:i + 1024])
                           for i in range(0, len(Yv), 1024)) / len(Yv))
            vp = [[f for f, _ in pr] for i in range(0, len(Yv), 1024)
                  for pr in I.propose(model, Fv[i:i + 1024], Wv[i:i + 1024], K=16)]
        v1, v16 = score(vp, va['label'])
        row = dict(epoch=epoch + 1, train_loss=round(tot / n, 4), val_loss=round(vl, 4), val_top1=v1, val_top16=v16,
                   seconds=round(time.perf_counter() - t0, 1))
        prog.write(json.dumps(row) + '\n')
        prog.flush()
        print(f"epoch {epoch + 1}: train {row['train_loss']:.3f} val {row['val_loss']:.3f} "
              f"dream top-1 {v1} top-16 {v16} ({row['seconds']}s)", flush=True)
        heat_guard.cool_down(log=lambda s: print(s, flush=True))
    torch.save(model.state_dict(), out / 'model.pt')
    ev = {}
    for name, s in real.items():
        props = [[f for f, _ in pr] for pr in I.propose(model, s['features'].astype(np.float32), s['world'], K=16)]
        base = greedy_baseline(s['features'], s['extras'])
        p_true = [dict(pr).get(I.D.FAMILIES[y], 0.0) for pr, y in
                  zip(I.propose(model, s['features'].astype(np.float32), s['world'], K=16), s['label'])]
        ev[name] = dict(imagination=score(props, s['label']), greedy=score(base, s['label']),
                        p_true=round(float(np.mean(p_true)), 3))
        print(f"{name:9s} imagination top-1/top-16 {ev[name]['imagination']}   greedy {ev[name]['greedy']}   "
              f"mean p(true) {ev[name]['p_true']}", flush=True)
    (out / 'eval.json').write_text(json.dumps(dict(args=vars(a), suites=ev), indent=1))


if __name__ == '__main__':
    main()
