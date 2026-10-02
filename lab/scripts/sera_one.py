"""One SERA, end to end (plan revision 6): taught, then alone; every subject one mind (sera.one).

  python scripts/sera_one.py --out RUN [--seed 1] [--hours 20] [--stage all|teach|alone|twin]

1. Teach: worlds of every subject, interleaved - rails with a teacher who says words about the law (a spring, a drag,
   a steady wind, a stiff spring, a rub, a ripple, a spring with a drag), list tasks named by the teacher (count, sum,
   reverse, double each, one more each, keep the positive ones, the last one), number tasks (twice, square, odd,
   triangle, powers of two). The teacher also shows its way of working (sera.phi.LoopField.teach), which fades.
   Nothing is listed in SERA: every law, program, rule and word it ends with, it made or learned here.
2. Alone: new tasks, no teacher, no words: laws in no list (sera.novel, each twice: the second tests what it
   invented), compositions of what it was taught (a spring with a rub; sum of the doubled; count the positive; a
   triangle of the double ...). It chooses their order itself (the least familiar first: curiosity).
3. Twin: the same alone-tasks lived by a copy of SERA whose inventions are hidden (the control): what invention buys.

Every task writes units/<task>.json; the Field is saved after every task (field.pkl); the tripwire (an answer the
judge accepted that the observer finds wrong) halts the run.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from ccops5.core import grammar  # noqa: E402
from sera import dictionary as DICT, one as ONE, phi as PH, tasks as TS, talk as TK  # noqa: E402

LAWS = {'spring': ((('position', 'straight'),), 1), 'drag': ((('speed', 'straight'),), 1),
        'wind': ((('nothing', 'steady'),), 1), 'stiff': ((('position', 'cubic'),), 1),
        'rub': ((('speed', 'steps'),), 1), 'ripple': ((('position', 'wave'),), 1),
        'spring and drag': ((('position', 'straight'), ('speed', 'straight')), 2)}
LISTS = {'count': (len, 'num'), 'sum': (sum, 'num'), 'reverse': (lambda l: l[::-1], 'list'),
         'double': (lambda l: [2 * x for x in l], 'list'), 'one more': (lambda l: [x + 1 for x in l], 'list'),
         'keep positive': (lambda l: [x for x in l if x > 0], 'list'), 'last': (lambda l: l[-1] if l else 0, 'num')}
NUMBERS = {'twice': lambda n: 2 * n, 'square': lambda n: n * n, 'odd': lambda n: 2 * n + 1,
           'triangle': lambda n: n * (n + 1) // 2, 'powers of two': lambda n: 2 ** n}
ALONE_LAWS = {'spring and rub': ((('position', 'straight'), ('speed', 'steps')), 2),
              'stiff and drag': ((('position', 'cubic'), ('speed', 'straight')), 2)}
ALONE_LISTS = {'sum of the doubled': (lambda l: sum(2 * x for x in l), 'num', ('sum', 'double')),
               'count the positive': (lambda l: len([x for x in l if x > 0]), 'num', ('count', 'keep positive')),
               'reverse the doubled': (lambda l: [2 * x for x in l][::-1], 'list', ('reverse', 'double')),
               'sum of one more': (lambda l: sum(x + 1 for x in l), 'num', ('sum', 'one more'))}
ALONE_NUMBERS = {'square of twice': (lambda n: 4 * n * n, ('square', 'twice')),
                 'triangle of twice': (lambda n: n * (2 * n + 1), ('triangle', 'twice')),
                 'twice the square': (lambda n: 2 * n * n, ('twice', 'square'))}
NOVEL = ('fading drag', 'dead zone', 'soft wall', 'ripple')


def teaching(seed):
    """(name, builder) of every teaching task, interleaved across subjects in a fixed shuffled order."""
    out = []
    for i, (name, (fam, level)) in enumerate(LAWS.items()):
        for rep in range(2):
            def build(fam=fam, level=level, i=i, rep=rep, name=name):
                w, signs = TS.rail_world(seed, 80_000 + 100 * i + rep, fam, level)
                rng = np.random.default_rng([seed, 17, i, rep])
                return TS.Rail(w, f'rail: {name} {rep + 1}', TK.teacher_tokens(grammar.canonical(fam), signs, rng),
                               signs)
            out.append((f'rail: {name} {rep + 1}', build))
    for i, (name, (f, typ)) in enumerate(LISTS.items()):
        out.append((f'list: {name}', lambda name=name, f=f, typ=typ, i=i:
                    TS.list_task(f'list: {name}', f, typ, seed, i, words=name.split())))
    for i, (name, f) in enumerate(NUMBERS.items()):
        out.append((f'number: {name}', lambda name=name, f=f, i=i:
                    TS.number_task(f'number: {name}', f, seed, i, words=name.split())))
    order = np.random.default_rng([seed, 47]).permutation(len(out))
    out = [out[i] for i in order]
    return [t for t in out if 'rub' not in t[0]] + [t for t in out if 'rub' in t[0]]   # the teacher: hardest last


def alone(seed):
    out = []
    for rep in range(2):
        for j, shape in enumerate(NOVEL):
            def build(shape=shape, rep=rep):
                w, signs = TS.rail_world(seed, 0, None, novel_shape=shape, rep=rep)
                return TS.Rail(w, f'rail: new {shape} {rep + 1}', (), signs)
            out.append((f'rail: new {shape} {rep + 1}', build))
    for i, (name, (fam, level)) in enumerate(ALONE_LAWS.items()):
        def build(fam=fam, level=level, i=i, name=name):
            w, signs = TS.rail_world(seed, 90_000 + 100 * i, fam, level)
            return TS.Rail(w, f'rail: {name}', (), signs)
        out.append((f'rail: {name}', build))
    for rep in range(2):                                   # worlds with depth: things made of equal units of mass
        def build(rep=rep):
            w, signs = TS.rail_world(seed, 95_000 + rep, (('position', 'straight'),), 1, units=True)
            return TS.Rail(w, f'rail: things {rep + 1}', (), signs)
        out.append((f'rail: things {rep + 1}', build))
    for i, (name, (f, typ, tw)) in enumerate(ALONE_LISTS.items()):
        out.append((f'list: {name}', lambda name=name, f=f, typ=typ, i=i, tw=tw:
                    TS.list_task(f'list: {name}', f, typ, seed, 100 + i, words=(), truth_words=tw)))
    for i, (name, (f, tw)) in enumerate(ALONE_NUMBERS.items()):
        out.append((f'number: {name}', lambda name=name, f=f, i=i, tw=tw:
                    TS.number_task(f'number: {name}', f, seed, 100 + i, words=(), truth_words=tw)))
    return out


def unit_of(rec):
    keep = {k: v for k, v in rec.items() if k not in ('say', 'choices', 'ring_observer')}
    keep['configs'] = rec.get('configs')
    keep['say'] = [s['text'] for s in rec.get('say', [])]
    return keep


def physics_summary(units):
    """World counts are physics units, even empty laws; representation counts are certified parts."""
    groups = {stage: dict(worlds=0, curves_proven=0, drawings_proven=0, formulas_proven=0)
              for stage in ('teach', 'alone', 'twin')}
    rows = []
    for u in units:
        form = u.get('form') or str(u.get('kind', '')).split(':')[0]
        if u.get('subject') != 'physics' or form != 'strengths':
            continue
        stage = u.get('stage')
        if stage not in groups:
            raise ValueError(f'physics unit has no valid stage: {u.get("task")}')
        rows.append(dict(task=u['task'], stage=stage, subject='physics', form=form,
                         proven=bool(u.get('proven')), verdict=u.get('verdict')))
        if u.get('proven'):
            groups[stage]['worlds'] += 1
            for c in u.get('certified') or ():
                groups[stage][c['as'] + 's_proven'] += 1
    return dict(groups=groups, units=rows)


def save_physics(out, units, settings):
    result = dict(physics_summary(units), settings=settings)
    (Path(out) / 'PHYSICS.json').write_text(json.dumps(result, indent=1), encoding='utf-8')
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--hours', type=float, default=20.0)
    ap.add_argument('--stage', default='all', choices=('all', 'teach', 'alone', 'twin'))
    ap.add_argument('--only', default=None, help='comma-separated task names (a smoke run)')
    ap.add_argument('--book', default=None, help='a dictionary it may read (WordNet 3.0 data files; or $SERA_BOOK)')
    args = ap.parse_args()
    from sera import crutches as CR
    print('SETTINGS', json.dumps(dict(CR.settings(), one_field=ONE.ONE_FIELD)), flush=True)
    TK.BOOK = DICT.load(args.book)                             # 2026-09-28: a book to learn our words from
    if TK.BOOK is not None:
        print(f'SERA has a dictionary: {len(TK.BOOK.senses)} words, {TK.BOOK.n} senses', flush=True)
    out = Path(args.out)
    (out / 'units').mkdir(parents=True, exist_ok=True)
    ck = out / 'field.pkl'
    field = PH.Field.load(ck) if ck.exists() else PH.Field(args.seed)
    sera = ONE.Sera(args.seed, field)
    deadline = time.time() + 3600 * args.hours
    events = open(out / 'events.jsonl', 'a', encoding='utf-8')

    def log(**e):
        events.write(json.dumps(dict(e, t=round(time.time(), 1)), default=str) + '\n')
        events.flush()

    def say(s):
        print(f"    [{s['step']}] {s['text']}", flush=True)

    def read_answers():
        """Our answers to its questions, if any (RUN/answers.jsonl: one JSON per line, {"id": "q3", "verdict":
        "right" | "wrong" | "hint", "words": [...]}); each is given once."""
        p = out / 'answers.jsonl'
        if not p.exists():
            return
        for line in p.read_text(encoding='utf-8').splitlines():
            if line.strip():
                a = json.loads(line)
                if sera.field.answer(a['id'], a['verdict'], a.get('words', ())):
                    print(f"  (an answer from us: {a['id']} {a['verdict']} {' '.join(a.get('words', []))})", flush=True)
                    for w, u in sera.field.answers[a['id']].get('understood', {}).items():
                        print(f"    it takes '{w}' ({u['how']}, sure {u['sure']:.2f}"
                              + (f", through {', '.join(u['through'])}" if u['through'] else '') + f"): "
                              + (', '.join(f'{m} {p:.2f}' for m, p in sorted(u['meaning'].items(), key=lambda kv: -kv[1])[:2])
                                 or 'nothing yet'), flush=True)
                    log(kind='answer', **a)

    proofs = []                                     # what each world's proof certified (curve, drawing, formula)

    def live(name, build, stage, teaching, masked=(), tag=''):
        path = out / 'units' / f"{tag}{name.replace(':', '').replace(' ', '_')}.json"
        if not tag:
            read_answers()
        if path.exists():
            saved = json.loads(path.read_text(encoding='utf-8'))
            saved.setdefault('stage', stage)
            proofs.append(saved)
            return proofs[-1]
        task = build()
        ONE.MAX_WALL = max(60.0, deadline - time.time())    # SERA works on a world until it proves it or the run ends
        print(f'\n=== {tag}{name} ({stage}) | words heard: {" ".join(task.words) or "-"}', flush=True)
        rec = sera.live(task, teaching=teaching, masked=masked, on_say=say,
                        ring_log=out / 'ring.jsonl')
        u = unit_of(rec)
        u.update(stage=stage, tag=tag)
        path.write_text(json.dumps(u, indent=1, default=str), encoding='utf-8')
        if not tag:
            sera.field.save(ck)
        proofs.append(u)
        print(f"  -> {u['verdict']} | {u.get('claim')} | steps {u['steps']} | {u['wall']} s | invented "
              f"{[i.get('body') for i in u['invented']]} | reused {u['reused']} | says {u['said']}"
              + (f" | CERTIFIED {' + '.join(c['as'] + ' on ' + c['on'] for c in u['certified'])}"
                 if u.get('certified') else '')
              + (f" | FALSE WORDS {u['false_words']}" if u['false_words'] else '')
              + (f" | SERENDIPITY {u['serendipity']}" if u['serendipity'] else '')
              + (f" | DUALITY {u['duality']}" if u['duality'] else '')
              + (f" | NEW SENSES {u['senses']}" if u.get('senses') else '')
              + (f" | FOUND BY {u['imagined_by']['moves']}" if u.get('imagined_by') else '')
              + (f" | ITS OWN METHOD {u['method_named']}" if u.get('method_named') else '')
              + (f" | IT ASKS: {u['question']['text']}" if u.get('question') else '')
              + f" | time {top_time(u.get('timing') or {})}", flush=True)
        log(kind='task', name=name, stage=stage, tag=tag, verdict=u['verdict'], steps=u['steps'], wall=u['wall'])
        if u['verdict'] == 'SURE AND WRONG':
            print('TRIPWIRE: an accepted answer is wrong. Halting.', flush=True)
            log(kind='tripwire', name=name)
            sys.exit(3)
        return u

    if args.stage in ('all', 'teach'):
        for name, build in teaching(args.seed):
            if args.only and name not in args.only.split(','):
                continue
            if time.time() > deadline:
                break
            live(name, build, 'teach', True)
        sera.field.save(out / 'field-teach.pkl')              # the twin starts from here
        print('TEACH DONE', json.dumps(sera.field.account()), flush=True)
    if args.stage in ('all', 'alone'):
        todo = alone(args.seed)
        while todo and time.time() < deadline:
            probes = []
            for i, (name, build) in enumerate(todo):          # its own choice: the least familiar first (curiosity)
                if args.only and name not in args.only.split(','):
                    continue
                probes.append((i, name))
            if not probes:
                break
            i, name = probes[int(np.random.default_rng([args.seed, len(todo)]).integers(len(probes)))] \
                if not sera.field.understood else min(probes, key=lambda p: familiarity(sera, todo[p[0]][1]))
            name, build = todo.pop(i)
            live(name, build, 'alone', False)
        print('ALONE DONE', json.dumps(sera.field.account()), flush=True)
    if args.stage in ('all', 'twin'):
        start = out / 'field-teach.pkl'
        twin = ONE.Sera(args.seed, PH.Field.load(start) if start.exists() else PH.Field(args.seed))
        masked = tuple(c['id'] for c in twin.field.concepts)          # its taught inventions hidden: the control
        sera_saved = sera
        sera = twin
        for name, build in alone(args.seed):
            if args.only and name not in args.only.split(','):
                continue
            if time.time() > deadline:
                break
            live(name, build, 'twin', False, masked=masked, tag='twin-')
        sera = sera_saved
        print('TWIN DONE', flush=True)
    result = save_physics(out, proofs, CR.settings())
    print('PHYSICS PROVEN', json.dumps(result['groups']), flush=True)
    print('ONE SERA DONE', json.dumps(sera.field.account()), flush=True)
    events.close()


def top_time(timing, n=3):
    """Where a world's time went: its n largest phases, in seconds."""
    return ', '.join(f'{k} {v:.0f}' for k, v in sorted(timing.items(), key=lambda kv: -kv[1])[:n]) or '-'


_FAM_CACHE = {}


def familiarity(sera, build):
    """How familiar a task looks before it is lived: the best similarity of its context to what it understood."""
    key = id(build)
    if key not in _FAM_CACHE:
        task = build()
        kind = ONE.kind_of(task)
        ctx = np.asarray(task.context(), float)
        best = 0.0
        for e in sera.field.understood:
            if e['kind'] == kind and len(e['context']) == len(ctx):
                best = max(best, float(np.exp(-np.sum((ctx - np.asarray(e['context'])) ** 2) / 2)))
        _FAM_CACHE[key] = best
    return _FAM_CACHE[key]


if __name__ == '__main__':
    main()
