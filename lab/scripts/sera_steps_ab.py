"""With and without the move 'step' (2026-09-29, the author: "teach sera how to break down ideas or problems into pieces,
that way it can search faster ... if search is a problem this can be a fix without losing ability? if I am right?").

The same SERA (a saved Field, or a newborn), the same lessons in the teacher's order (a saved Field: from 'where is'
on; a newborn: from the first lesson), the same machine, seed and time boxes; in the arm 'whole' the move 'step' is
never available (nothing else differs - the move is taken away here, in the experiment, not in SERA).

  python scripts/sera_steps_ab.py [--field F] --out RUN --arm step|whole [--from LESSON] [--box 30] [--hours 4]

2026-09-29: a SERA taught before the move existed (lang-full-0118e00) keeps its own habit of wishing first, and in
both arms did the same thing (the step was never drawn), so the fair test is a newborn taught from the start.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sera import crutches as CR, dictionary as DICT, one as ONE, phi as PH, talk as TK  # noqa: E402
import sera_language as SL  # noqa: E402


def apply_switches(args):
    """Only explicit command-line ablations override the imported configuration."""
    if args.no_echo:
        PH.FIELD_ECHO = False
    if args.no_back:
        ONE.BACK_ON = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--field', default=None, help='a saved Field (none: a newborn SERA)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--arm', choices=('step', 'whole'), required=True)
    ap.add_argument('--from', dest='start', default=None,
                    help="the first lesson (default: 'where' for a saved Field - it has first, last and who - else 'first')")
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--box', type=float, default=30.0, help='minutes a world gets on its first visit (doubles)')
    ap.add_argument('--hours', type=float, default=4.0)
    ap.add_argument('--book', default=None)
    ap.add_argument('--no-echo', action='store_true', help='the Field as before the echo (no traces, no echo, no trigger)')
    ap.add_argument('--no-back', action='store_true', help='no imagining the way back from the goal when stuck')
    a = ap.parse_args()
    TK.BOOK = DICT.load(a.book)
    if a.book and TK.BOOK is None:              # a named dictionary that is not there is refused (ideas-4, 2026-09-29)
        sys.exit(f'--book {a.book}: no WordNet dictionary there (data.noun missing)')
    apply_switches(a)
    print('SETTINGS', json.dumps(dict(CR.settings(), one_field=ONE.ONE_FIELD)), flush=True)
    if a.arm == 'whole':
        base = ONE.Sera._moves_available

        def whole(self, *args, **kw):
            out = base(self, *args, **kw)
            out.discard('step')
            return out
        ONE.Sera._moves_available = whole
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sera = ONE.Sera(a.seed, PH.Field.load(a.field) if a.field else PH.Field(a.seed))
    start = a.start or ('where' if a.field else 'first')
    todo = SL.teaching(a.seed)
    todo = todo[next(i for i, (n, _) in enumerate(todo) if n.startswith(start + ' ')):]
    t0 = time.time()
    last = SL.practise(sera, todo, out, t0 + 3600 * a.hours, 'teach', True, a.box * 60)
    rows = {}
    for n, u in last.items():                            # every visit's time counts (a world not proven comes back)
        visits = [json.loads(p.read_text(encoding='utf-8'))
                  for p in sorted((out / 'units').glob(n.replace(' ', '_') + '*.json'))]
        rows[n] = dict(verdict=u.get('verdict'), claim=u.get('claim'), visits=len(visits),
                       wall_all_visits=round(sum(float(v.get('wall') or 0) for v in visits), 1),
                       steps=u.get('steps'), stepped=any('I break it into' in s for s in u.get('say') or []),
                       back=any('imagined the last step' in s for s in u.get('say') or []),
                       rang=any('rings in me' in s for s in u.get('say') or []))
    (out / 'AB.json').write_text(json.dumps(dict(arm=a.arm, echo=PH.FIELD_ECHO, back=ONE.BACK_ON, field=a.field,
                                                 box=a.box, hours=a.hours, seed=a.seed, one_field=ONE.ONE_FIELD,
                                                 settings=CR.settings(),
                                                 total_s=round(time.time() - t0, 1), lessons=rows), indent=1),
                                 encoding='utf-8')
    print('AB DONE', a.arm, json.dumps(rows), flush=True)


if __name__ == '__main__':
    main()
