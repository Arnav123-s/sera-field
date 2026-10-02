"""A talk with a teacher (2026-09-30; the author: "I want to be able to converse with it"; S06 F5, reviewer: which idea
answers belongs in SERA, taught and graded). The same SERA (a saved Field), three arms from copies of that same
Field, all graded alone on the same fresh talk of mixed questions from its lessons, each with its story, some about
someone it was never told of (sera.tasks.Talk; S07, reviewer: matched arms):

- before: nothing more - what its Field chooses now;
- taught: a talk with the teacher (it replies, the teacher says the answer, its Field learns which idea a question
  calls for), then the fresh talk;
- read only: the same talk's stories and questions without the teacher (exposure alone), then the fresh talk.

Nothing is searched: each reply is its proven idea that rings loudest for the question (sera.one.Sera.reply), or it
does not know. Light and quick (seconds): fit for the laptop.

  python scripts/sera_converse.py --field F --out DIR [--seed 1] [--n 40] [--save F2] [--book WORDNET]
"""
import argparse
import copy
import json
import os
import pickle
import sys
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sera import dictionary as DICT, one as ONE, tasks as TS, talk as TK  # noqa: E402


def load(path):
    """A saved Field, or a light copy (a dict: the Field without its ideas' state, as saved before a machine ended)."""
    with open(path, 'rb') as f:
        got = pickle.load(f)
    field = got['field'] if isinstance(got, dict) else got
    TS.adopt(getattr(field, 'vocab', None) or {})
    return field


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--field', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--save', default=None, help='save the taught arm\'s Field')
    ap.add_argument('--book', default=None)
    a = ap.parse_args()
    TK.BOOK = DICT.load(a.book)
    from sera import crutches as CR
    print('SETTINGS', json.dumps(dict(CR.settings(), one_field=ONE.ONE_FIELD)), flush=True)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    base = load(a.field)
    arms = {'before': ONE.Sera(a.seed, copy.deepcopy(base)), 'taught': ONE.Sera(a.seed, base),
            'read only': ONE.Sera(a.seed, copy.deepcopy(base))}
    names = base.names()
    print('its ideas of a situation:', ', '.join(str(names.get(c, c)) for c in arms['taught']._situation_ideas()),
          flush=True)
    recs = {}

    def show(part, rec, teaching):
        recs[part] = rec
        print(f"\n== {part}: {rec['right']}/{rec['n']} right, answered {rec['answered']}  {rec['by_kind']}  "
              f"({rec['wall']} s)", flush=True)
        for r in rec['rows'][:6]:
            print(f"   {r['question']}? -> {r['said'] or 'I do not know'}"
                  + (f" (idea {r['idea']})" if r['idea'] else '')
                  + (f" | teacher: {r['teacher'] or 'nobody said'}" if teaching else '')
                  + ('' if r['right'] else '  [wrong]'), flush=True)
        if rec['learned']:
            print('   set in its Field:', '; '.join(f'{w} -> {i} {v:+.2f}' for i, w, v in rec['learned'][:14]),
                  flush=True)

    show('taught: the lesson', arms['taught'].converse(TS.talk_world(a.seed, a.n), teaching=True), True)
    show('read only: the lesson', arms['read only'].converse(TS.talk_world(a.seed, a.n), teaching=False), False)
    for arm in ('before', 'taught', 'read only'):
        show(f'{arm}: the fresh talk', arms[arm].converse(TS.talk_world(a.seed + 6000, a.n), teaching=False), False)
    (out / 'CONVERSE.json').write_text(json.dumps(recs, indent=1, default=str), encoding='utf-8')
    if a.save:
        arms['taught'].field.save(a.save)
    print('\nCONVERSE DONE', json.dumps({k: [v['right'], v['answered'], v['n']] for k, v in recs.items()}),
          flush=True)


if __name__ == '__main__':
    main()
