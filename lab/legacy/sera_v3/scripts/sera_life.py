"""One SERA life, stage by stage (plan revision 5): teach -> let it fail and correct it -> alone -> yardsticks.

  python legacy/sera_v3/scripts/sera_life.py --out <dir> --seed 1 --stage smoke            5 traced worlds, fresh SERA (Stage 0)
  python legacy/sera_v3/scripts/sera_life.py --out <dir> --seed 1 --stage yardstick --label S0
  python legacy/sera_v3/scripts/sera_life.py --out <dir> --seed 1 --stage teach            Stage 1: the 34 teaching worlds
  python legacy/sera_v3/scripts/sera_life.py --out <dir> --seed 1 --stage check            the Stage 1 check (taught vs untaught)
  python legacy/sera_v3/scripts/sera_life.py --out <dir> --seed 1 --stage practice --worlds 150 [--mix mix.json]   Stage 2
  python legacy/sera_v3/scripts/sera_life.py --out <dir> --seed 1 --stage alone --hours 24                        Stage 3
  python legacy/sera_v3/scripts/sera_life.py --out <dir> --seed 1 --stage newdoors --hours 4                      Stage 5 (rooms, code)

The whole agent is saved after every world (<dir>/agent.pkl, atomic), so any stage resumes where it stopped.
Every world writes <dir>/units/<stage>-<n>.json; live narration and decisions go to <dir>/events.jsonl; a condensed
summary is printed every 20 worlds (for reading on Colab).

Tripwires (the program's rules, docs/SERA_STATUS.md, plan revision 5 B1), checked after every world; any one halts
the life and writes <dir>/HALT.json:
  - a "sure" claim that is wrong: neither the exact law nor a correct surface (the P2 gate's definition,
    legacy/sera_v3/scripts/sera_check.py; the observer knows the truth of dev worlds). The stricter frozen flag (core_check.wrong,
    any claim but the exact law) is recorded and reported beside it;
  - a certificate the independent checker refuses;
  - a false sentence (the checked self-report or the live narration);
  - memory not exactly MEMORY_BYTES.
The judge's policy is fixed for the whole program (the author, 2026-09-27: Decision 8's band, CCOPS5_BAND=claim), set
here before the judge is imported; --band ui is the revert after a tripwire.

Revision 5.1, --office <dir> (the judge's office, sera.proofs; its workers: legacy/sera_v3/scripts/sera_judge.py): SERA submits each
claim that passed every part of the certificate but the universe audit and lives on; the office's verdicts are
collected after every world (SERA waits only when more than agent.MAX_WAITING of its claims are queued) and written
into the world's unit ("proof": "submitted" -> "judged", with the full verdict); the tripwires run again on it. A
claim the judge refused for a rival SERA never weighed sends SERA back to that world once (a "second look", unit
<name>-look1, with the rival's terms added, from every throw it made there). Every stage ends only when all its claims
are judged and its second looks lived.
"""
import argparse
import json
import os
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2]))  # the repo root
sys.path.insert(0, str(ROOT.parents[2] / 'scripts'))  # governor, heat_guard
sys.path.insert(0, str(ROOT))


def _summary(agent, stage, recent):
    n = len(recent)
    proven = sum(u['verdict'] in ('proven right', 'proven, surface') for u in recent)
    right_unsure = sum(u['verdict'] == 'right, unsure' and u.get('proof') != 'submitted' for u in recent)
    waiting = sum(u.get('proof') == 'submitted' for u in recent)
    cpu = sum(u['cpu'] for u in recent)
    doors = {}
    for u in recent:
        doors[u['door']] = doors.get(u['door'], 0) + 1
    m = agent.memory.summary()
    return (f"SUMMARY {stage} worlds={sum(agent.done.values())} last{n}: proven {proven}, right-unsure {right_unsure}, "
            f"with the judge {waiting}, "
            f"cpu/world {cpu / max(n, 1):.0f}s, vocab {m['vocab']} (taught {m['vocab_taught']}), "
            f"words {m['words_grounded']}, lessons {m['lessons_open']}, skills {m['skills_active']}+{m['skills_candidate']}, "
            f"doors {doors}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--stage', required=True,
                    choices=('smoke', 'teach', 'check', 'practice', 'alone', 'yardstick', 'newdoors', 'novel'))
    ap.add_argument('--worlds', type=int, default=150)
    ap.add_argument('--hours', type=float, default=24.0)
    ap.add_argument('--mix', default=None, help='JSON {door: weight} for Stage 2 (the teacher re-weights it)')
    ap.add_argument('--label', default='S0')
    ap.add_argument('--band', default='claim', choices=('claim', 'ui'))
    ap.add_argument('--yard-seed', type=int, default=None, help='the yardstick seed (default: --seed; fresh: 11-20)')
    ap.add_argument('--shard', default=None, help='k/K: this process takes worlds n with n %% K == k (yardstick and '
                                                  'check stages only: their worlds never change the memory)')
    ap.add_argument('--mind', default='agent', choices=('agent', 'v31'), help='yardstick only: v31 = the hand-built '
                                                                                'SERA v3.1, as the reference')
    ap.add_argument('--office', default=None, help="rev 5.1: the judge's office folder (default: every proof inline)")
    ap.add_argument('--shapes', default=None, help='novel stage: hidden shapes (sera.novel.SHAPES names, comma-separated)')
    ap.add_argument('--reps', type=int, default=1, help='novel stage: worlds per shape')
    ap.add_argument('--start', default=None, help="a life's agent.pkl to start from (copied once, its claims left behind)")
    args = ap.parse_args()
    os.environ['CCOPS5_BAND'] = args.band
    os.environ.setdefault('PYTHONHASHSEED', '0')
    import numpy as np
    import torch
    torch.set_num_threads(1)
    from legacy.sera_v3 import agent as AG, doors as DR, memory as MV, proofs as PR, worlds as SW

    out = Path(args.out)
    (out / 'units').mkdir(parents=True, exist_ok=True)
    halt = out / 'HALT.json'
    if halt.exists():
        print(f'HALTED earlier: {halt.read_text()}')
        return 2
    ck = out / 'agent.pkl'
    if args.start and not ck.exists():                  # the same SERA, taught elsewhere, continues here
        import shutil
        shutil.copy(args.start, ck)
        fresh = AG.Agent.load(ck)
        fresh.pending, fresh.revisits = {}, []
        fresh.save(ck)
    agent = AG.Agent.load(ck) if ck.exists() else AG.Agent(args.seed)
    k_shard, n_shard = (int(x) for x in args.shard.split('/')) if args.shard else (0, 1)
    mine = lambda n: n % n_shard == k_shard
    if args.shard:
        assert args.stage in ('yardstick', 'check'), 'only worlds that never change the memory may be sharded'
        ck = out / f'agent-readonly-{k_shard}.pkl'                       # never written: learn=False below
    events = None
    events = open(out / (f'events-shard{k_shard}.jsonl' if args.shard else 'events.jsonl'), 'a', encoding='utf-8')
    t_start = time.time()
    recent = []
    office = PR.Office(args.office) if args.office else None
    agent.office = office
    if args.stage in ('yardstick', 'check'):            # a snapshot measures; the life's own claims stay the life's
        agent.pending, agent.revisits = {}, []
    agents = {'agent': agent}
    side = out / (f'pending-shard{k_shard}.pkl' if args.shard else 'pending-readonly.pkl')
    if args.stage in ('yardstick', 'check') and side.exists():   # learn=False lives never write agent.pkl
        blob = pickle.loads(side.read_bytes())
        agent.pending.update(blob.get('agent', {}))
        agent.revisits += blob.get('revisits-agent', [])

    def log(kind, **kw):
        events.write(json.dumps(dict(t=round(time.time(), 1), kind=kind, **kw), default=str) + '\n')
        events.flush()

    def tripwire(unit):
        why = []
        if unit['verdict'] == 'SURE AND WRONG':
            why.append('sure and wrong')
        if unit['verdict'] == 'checker refused':
            why.append('checker refused')
        if unit['verdict'] == 'office policy mismatch':
            why.append(f"the office runs another judge policy: {unit.get('office_why')}")
        if unit['false_sentences']:
            why.append(f"false sentences: {unit['false_sentences'][:3]}")
        if len(agent.memory.to_bytes()) != MV.MEMORY_BYTES:
            why.append('memory size changed')
        return why

    def save_side():
        if args.stage in ('yardstick', 'check'):
            tmp = Path(str(side) + '.tmp')
            blob = {k: a.pending for k, a in agents.items()}
            blob.update({f'revisits-{k}': a.revisits for k, a in agents.items()})
            tmp.write_bytes(pickle.dumps(blob))
            os.replace(tmp, side)

    def settle(until):
        """rev 5.1: the office's verdicts - merged into their units, logged, narrated, and tripwired again."""
        if office is None:
            return
        for who in list(agents.values()):
            def hear(s):
                print(f"  [judge] {s['text']}", flush=True)
                log('say', world=s['numbers']['world'], text=s['text'])
            got = who.collect(until=until if (who is agent or until == 0) else None, on_say=hear)
            for name, upd in got:
                p = out / 'units' / f'{name}.json'
                unit = json.loads(p.read_text()) if p.exists() else dict(name=name)
                false = list(unit.get('false_sentences') or []) + list(upd.get('false_sentences') or [])
                unit.update(upd)
                unit['false_sentences'] = false
                if 'judged_sentence' in upd:
                    unit['narration'] = list(unit.get('narration') or []) + [upd['judged_sentence']]
                p.write_text(json.dumps(unit, indent=1, default=str))
                for u in recent:
                    if u.get('name') == name:
                        u.update(upd)
                j = upd.get('judged') or {}
                print(f"{name}: JUDGED {unit['verdict']} | office cpu {j.get('cpu')}s wall {j.get('wall')}s, "
                      f"waited {j.get('waited')}s | learned {upd.get('learned_after')}", flush=True)
                log('judged', world=name, verdict=unit['verdict'], judged=j)
                why = tripwire(unit)
                if why:
                    halt.write_text(json.dumps(dict(world=name, why=why, band=args.band), indent=1))
                    print(f'TRIPWIRE {name}: {why}', flush=True)
                    raise SystemExit(3)
            if got and who is agent and args.stage not in ('yardstick', 'check'):
                agent.save(ck)
        save_side()

    def second_looks():
        """rev 5.1: back to the worlds whose claims the judge refused for a rival SERA never weighed."""
        for key, who in list(agents.items()):
            while who.revisits:
                rv = who.revisits.pop(0)
                one(rv['world'], rv['stage'], f"{rv['base']}-look{rv['k']}", door=rv['door'], learn=rv['learn'],
                    who=who, resume=rv)

    def finish():
        """A stage ends only when every claim is judged and every second look lived."""
        while True:
            settle(0)
            if not any(a.revisits for a in agents.values()):
                return
            second_looks()

    def one(world, stage, name, door=None, learn=True, who=None, resume=None):
        said = []
        who = who or agent
        def hear(s):                                       # live: SERA says each finding as it goes
            said.append(s['text'])
            print(f"  [{name} @{s['own']}] {s['text']}", flush=True)
        r, unit = who.live(world, stage, door=door, learn=learn, on_say=hear, name=name, resume=resume)
        unit['name'] = name
        (out / 'units' / f'{name}.json').write_text(json.dumps(unit, indent=1, default=str))
        for s in said:
            log('say', world=name, text=s)
        why = tripwire(unit)
        if learn:
            agent.save(ck)
        save_side()
        print(f"{name}: L{unit['level']} door {door} | truth {unit['truth']} | answer {unit['claim']} | "
              f"{unit['verdict']} | own {unit['own']} | stop {(unit['stop'] or {}).get('reason')} | "
              f"learned {unit['learned']} | cpu {unit['cpu']:.0f}s", flush=True)
        if why:
            halt.write_text(json.dumps(dict(world=name, why=why, band=args.band), indent=1))
            print(f'TRIPWIRE {name}: {why}', flush=True)
            raise SystemExit(3)
        recent.append(unit)
        settle(AG.MAX_WAITING)
        if len(recent) >= 20:
            print(_summary(agent, stage, recent), flush=True)
            recent.clear()
        return r, unit

    def one_code(world, name, door):
        """Stage 5, the code door: a task, SERA's loop on code, the observer's check, the tripwires."""
        def hear(s):
            print(f"  [{name} @{s['own']}] {s['text']}", flush=True)
            log('say', world=name, text=s['text'])
        _, unit = agent.live_code(world, 'newdoors', door=door, on_say=hear, name=name)
        unit['name'] = name
        (out / 'units' / f'{name}.json').write_text(json.dumps(unit, indent=1, default=str))
        agent.save(ck)
        print(f"{name}: code door {door} | truth {unit['truth']} | answer {unit['claim']} | {unit['verdict']} | "
              f"questions {unit['own']} | cpu {unit['cpu']:.0f}s", flush=True)
        why = tripwire(unit)
        if why:
            halt.write_text(json.dumps(dict(world=name, why=why, band=args.band), indent=1))
            print(f'TRIPWIRE {name}: {why}', flush=True)
            raise SystemExit(3)
        recent.append(unit)
        settle(AG.MAX_WAITING)

    def v31(world, name, door):
        """The hand-built SERA v3.1 (the P2 gate's mind: its imagination network, designed pushes, the whole budget)
        on a yardstick world, graded the same way; the reference the grown SERA is compared with."""
        from ccops5.core import checker
        from legacy.sera_v3 import caretaker as CT, imagine as I, mind as SM
        model = I.Imagination()
        model.load_state_dict(torch.load(Path(os.environ.get('SERA_RUNS', 'D:/ai/labs/ccops5-sera-lab/sera-runs'))
                                         / 'imagine-v1' / 'model.pt', map_location='cpu'))
        model = model.float().eval()
        t0 = time.process_time()
        r = SM.Mind(model, world.sigma, eps=0.2, budget=3 * world.n_situations, design=True).live(world)
        verified = bool(r.sure and checker.check(r.certificate, r.ledger.throws, world.sigma)[0])
        g = CT.grade(r, verified, world)
        unit = dict(name=name, stage='alone', door=door, level=world.spec.level, truth=g['truth'], claim=g['answer'],
                    verdict=g['verdict'], wrong_frozen=g['wrong_frozen'], sure=bool(r.sure), verified=verified,
                    own=r.own_pushes, calls=r.certify_calls, cpu=round(time.process_time() - t0, 1), mind='v3.1',
                    false_sentences=[], learned=[], vocab_size=None, narration=[], stop=None)
        (out / 'units' / f'{name}.json').write_text(json.dumps(unit, indent=1, default=str))
        print(f"{name} (v3.1): L{unit['level']} | truth {unit['truth']} | answer {unit['claim']} | {unit['verdict']} | "
              f"own {unit['own']} | cpu {unit['cpu']:.0f}s", flush=True)
        if unit['verdict'] in ('SURE AND WRONG', 'checker refused'):
            halt.write_text(json.dumps(dict(world=name, why=[unit['verdict']], band=args.band), indent=1))
            raise SystemExit(3)

    if args.stage == 'smoke':
        worlds = [('smoke-L1-01', SW.make(1, 9001, 1, 'dream'))]
        worlds += [(f'smoke-d{d}', DR.door_world(d, args.seed, 0, 'check')) for d in (1, 2, 2, 4)]
        for name, w in worlds:
            if (out / 'units' / f'{name}.json').exists():
                continue
            one(w, 'alone', name, learn=True)
            second_looks()
        finish()
        print('\n'.join(agent.account()))
        print('SMOKE DONE', flush=True)
    elif args.stage == 'yardstick':
        ys = args.yard_seed or args.seed
        for n, door, build in DR.yardstick_worlds(ys):
            name = f'yard-{args.label}-{n:02d}'
            if not mine(n) or (out / 'units' / f'{name}.json').exists():
                continue
            if args.mind == 'v31':
                v31(build(), name, door)
            else:
                one(build(), 'alone', name, door=door, learn=False)
            second_looks()
        finish()
        print(f'YARDSTICK {args.label} DONE', flush=True)
    elif args.stage == 'teach':
        for n, build in DR.teaching_worlds(args.seed):
            if n < agent.done['teach']:
                continue
            try:
                w = build()
            except RuntimeError as e:                      # a law with no identifiable world: skipped, and said so
                print(f'teach-{n:02d}: SKIPPED ({e})', flush=True)
                log('skip', world=f'teach-{n:02d}', why=str(e))
                agent.done['teach'] += 1
                agent.save(ck)
                continue
            one(w, 'teach', f'teach-{n:02d}')
            second_looks()
        finish()
        print('\n'.join(agent.account()))
        print('TEACH DONE', flush=True)
    elif args.stage == 'check':
        untaught = AG.Agent(args.seed)                     # the same SERA with nothing taught (an empty memory)
        untaught.office = office
        agents['untaught'] = untaught
        if side.exists():
            blob = pickle.loads(side.read_bytes())
            untaught.pending.update(blob.get('untaught', {}))
            untaught.revisits += blob.get('revisits-untaught', [])
        fams = [((t,), 3 if t[0] != 'piece' else 6) for t in DR.TEACH_TERMS]
        for n in range(8):
            if not mine(n) or (out / 'units' / f'check-untaught-{n}.json').exists():
                continue
            if n < 4:
                fam, level = fams[n]
                make = lambda: DR.make_with(args.seed, DR.STAGE_BASE['check'] + n, fam, level)
            else:
                make = lambda: DR.door_world(1, args.seed, n, 'check')
            one(make(), 'alone', f'check-taught-{n}', learn=False)
            one(make(), 'alone', f'check-untaught-{n}', learn=False, who=untaught)
            second_looks()
        finish()
        names = [(f'check-taught-{n}', f'check-untaught-{n}') for n in range(8)]
        if all((out / 'units' / f'{b}.json').exists() for _, b in names):
            ld = lambda nm: json.loads((out / 'units' / f'{nm}.json').read_text())
            res = [dict(n=n, taught=ld(a), untaught=ld(b)) for n, (a, b) in enumerate(names)]
            proved = lambda side: sum(r[side]['verdict'] in ('proven right', 'proven, surface') for r in res)
            pushes = lambda side: sum(r[side]['own'] for r in res)
            differ = sum(r['taught']['events'] != r['untaught']['events'] or r['taught']['own'] != r['untaught']['own']
                         for r in res)
            verdict = dict(proved_taught=proved('taught'), proved_untaught=proved('untaught'),
                           pushes_taught=pushes('taught'), pushes_untaught=pushes('untaught'), differ=differ,
                           passed=bool(proved('taught') >= proved('untaught') and pushes('taught') < pushes('untaught')
                                       and differ >= 6))
            (out / 'check.json').write_text(json.dumps(dict(verdict=verdict, worlds=[
                dict(n=r['n'], taught=r['taught']['verdict'], untaught=r['untaught']['verdict'],
                     own=(r['taught']['own'], r['untaught']['own'])) for r in res]), indent=1, default=str))
            print(f'CHECK {verdict}', flush=True)
        else:
            print('CHECK SHARD DONE (the verdict comes when every world is in)', flush=True)
    elif args.stage == 'practice':
        mix = json.loads(Path(args.mix).read_text()) if args.mix else {'1': 0.2, '2': 0.35, '3': 0.15, '4': 0.2,
                                                                      '5': 0.1}
        doors = sorted(int(d) for d in mix)
        p = np.array([float(mix[str(d)]) for d in doors])
        while agent.done['practice'] < args.worlds:
            n = int(agent.done['practice'])
            door = doors[int(np.random.default_rng([args.seed, 61, n]).choice(len(doors), p=p / p.sum()))]
            one(DR.door_world(door, args.seed, n, 'practice'), 'practice', f'practice-{n:03d}', door=door)
            second_looks()
        finish()
        m = agent.train_selfgrader()
        agent.save(ck)
        print(f'SELFGRADER {m}; trusted {agent.selfgrader.trusted}', flush=True)
        print('\n'.join(agent.account()))
        print('PRACTICE DONE', flush=True)
    elif args.stage == 'alone':
        plateau = 0
        while time.time() - t_start < args.hours * 3600:
            n = int(agent.done['alone'])
            door, why = agent.choose_door()
            log('choose', world=f'alone-{n:04d}', door=door, **why)
            vocab0 = len(agent.memory.vocab_terms())
            one(DR.door_world(door, args.seed, n, 'alone'), 'alone', f'alone-{n:04d}', door=door)
            second_looks()
            agent.save(ck)
            grew = len(agent.memory.vocab_terms()) > vocab0
            lps = [agent.curriculum.lp(d) for d in agent.curriculum.doors]
            plateau = 0 if (grew or max(lps) >= 0.02) else plateau + 1
            if plateau >= 64:
                print('PLATEAU: every door LP < 0.02 and no new vocabulary for 64 worlds', flush=True)
                break
        finish()
        agent.save(ck)
        print('\n'.join(agent.account()))
        print('ALONE DONE', flush=True)
    elif args.stage == 'newdoors':
        agent.curriculum.add_doors(DR.NEW_DOORS)          # Stage 5: two new doors, nobody says what is behind them
        while time.time() - t_start < args.hours * 3600:
            n = int(agent.done['newdoors'])
            name = f'new-{n:04d}'
            door, why = agent.choose_door()
            log('choose', world=name, door=door, **why)
            if door == 7:
                one_code(DR.new_door_world(7, args.seed, n), name, door)
            else:
                w = DR.new_door_world(6, args.seed, n) if door == 6 else DR.door_world(door, args.seed, n, 'newdoors')
                one(w, 'newdoors', name, door=door)
            second_looks()
            agent.save(ck)
        finish()
        agent.save(ck)
        for line in agent.account():
            print(line)
        print('NEWDOORS DONE', flush=True)
    elif args.stage == 'novel':                          # revision 6: laws in no list, and nobody to help
        from legacy.sera_v3 import novel as NV
        shapes = args.shapes.split(',') if args.shapes else list(NV.SHAPES)
        for rep_ in range(args.reps):
            for shape in shapes:
                name = f"novel-{shape.replace(' ', '_')}-{rep_}"
                if (out / 'units' / f'{name}.json').exists():
                    continue
                w = NV.novel_world(shape, args.seed, rep_)
                log('novel', world=name, shape=shape, **w.novelty)
                print(f"{name}: a law in no list (the nearest list law, {w.novelty['nearest']}, misses by "
                      f"{w.novelty['gap']:.2f})", flush=True)
                one(w, 'alone', name, learn=True)
                second_looks()
        finish()
        agent.save(ck)
        for line in agent.account():
            print(line)
        print('NOVEL DONE', flush=True)
    events.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
