"""The observatory (plan revision 5, WP4): SERA's behaviour, generated from its saved worlds, never typed.

  python scripts/sera_observe.py <life dir> [<life dir> ...] [--write docs/SERA_BEHAVIOUR.md]

Reads each life's units (<dir>/units/*.json), its choices (<dir>/events.jsonl) and its checks, and prints markdown
tables answering plan revision 5's questions (B4):
  1. did teaching take?          the Stage 1 check; vocabulary and words by stage
  2. did correction change it?   verdicts by stage; repeated mistakes; worlds with a hint
  3. what does it choose alone?  door shares over time; its goals in its own words
  4. what did it discover?       terms it learned that nobody taught it, with the world and the verdict
  5. does it improve alone?      the yardsticks S0-S3 and fresh; CPU and pushes per proof over time
  6. does it know what it knows? its self-grade against the truth
  7. does it stay honest?        the tripwires, the stricter frozen flag, false sentences
With --write, the generated part of the living report (between its GENERATED markers) is replaced in place.
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

PROVEN = ('proven right', 'proven, surface')
STAGES = ('smoke', 'teach', 'check', 'practice', 'alone', 'yard')


def load(d):
    d = Path(d)
    units = [json.loads(p.read_text()) for p in sorted((d / 'units').glob('*.json'))]
    events = []
    if (d / 'events.jsonl').exists():
        events = [json.loads(l) for l in (d / 'events.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    check = json.loads((d / 'check.json').read_text()) if (d / 'check.json').exists() else None
    halt = json.loads((d / 'HALT.json').read_text()) if (d / 'HALT.json').exists() else None
    return dict(dir=d.name, units=units, events=events, check=check, halt=halt)


def stage_of(u):
    return 'yard' if u['name'].startswith('yard') else u['name'].split('-')[0]


def table(rows, head):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows]
    return '\n'.join(out)


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return xs[len(xs) // 2] if xs else '-'


def verdicts(life):
    rows = []
    by = defaultdict(list)
    for u in life['units']:
        by[stage_of(u) if stage_of(u) != 'yard' else u['name'].rsplit('-', 1)[0]].append(u)
    for st, us in by.items():
        c = Counter(u['verdict'] for u in us)
        stops = Counter((u.get('stop') or {}).get('reason', 'sure' if u['sure'] else '-') for u in us)
        rows.append([st, len(us), c['proven right'], c['proven, surface'], c['right, unsure'], c['unsure, wrong'],
                     c['SURE AND WRONG'] + c['checker refused'], sum(bool(u.get('wrong_frozen')) for u in us),
                     med([u['own'] for u in us]), med([u['cpu'] for u in us]),
                     ', '.join(f'{k} {v}' for k, v in stops.most_common(3))])
    return table(rows, ['stage', 'worlds', 'proven right', 'proven surface', 'right unsure', 'unsure wrong',
                        'WRONG or refused', 'frozen flag', 'median pushes', 'median CPU s', 'how worlds ended'])


def learning(life):
    """Every term SERA learned, how (taught, or discovered: a proof of its own), and what kind of discovery it was: an
    entry of the judge's fixed dictionary found by search, or a free curve SERA shaped itself (growth's cells: the only
    shapes nobody wrote down)."""
    rows = []
    for u in life['units']:
        how = dict((n, h) for n, h in (u.get('credit') or {}).get('vocab', []))
        for names, terms, when in ((u.get('learned') or [], u.get('learned_terms') or [], 'end of world'),
                                   (u.get('learned_after') or [], u.get('learned_terms_after') or [], 'judge')):
            for i, t in enumerate(names):
                raw = terms[i] if i < len(terms) else None
                kind = ('free curve (shaped by SERA)' if raw and raw[0] == 'cell' else
                        'dictionary term (search)' if how.get(t, 'discovered') != 'taught' else 'dictionary term (taught)')
                rows.append([u['name'], t, how.get(t, 'discovered'), kind, when, u['verdict'], u['truth']])
    return table(rows, ['world', 'term learned', 'how', 'what kind', 'written', 'verdict', 'the law there']) \
        if rows else '(none yet)'


def doors(life):
    alone = [u for u in life['units'] if stage_of(u) == 'alone']
    if not alone:
        return '(no Stage 3 worlds yet)'
    rows = []
    for i in range(0, len(alone), 50):
        chunk = alone[i:i + 50]
        c = Counter(u['door'] for u in chunk)
        p = sum(u['verdict'] in PROVEN for u in chunk)
        rows.append([f'{i}-{i + len(chunk) - 1}', ', '.join(f'door {d}: {c[d]}' for d in sorted(c)), p,
                     med([u['cpu'] for u in chunk]), chunk[-1]['vocab_size']])
    goals = Counter(g for e in life['events'] if e.get('kind') == 'choose' for g in e.get('goals', []))
    out = table(rows, ['worlds', 'doors chosen', 'proven', 'median CPU s', 'vocabulary at the end'])
    if goals:
        out += '\n\nIts goals, in its own words (how often it held each):\n' + '\n'.join(
            f'- "{g}" ({n})' for g, n in goals.most_common(8))
    return out


def newdoors(life):
    """Stage 5: which doors it chose once rooms (6) and code (7) opened; in rooms, how well a thing's look predicted
    its mass before it was thrown (its own table of looks, never told), against the hidden truth; in code, verdicts."""
    import math
    us = [u for u in life['units'] if u.get('stage') == 'newdoors' and '-look' not in u['name']]
    if not us:
        return '(no Stage 5 worlds yet)'
    rows = []
    for i in range(0, len(us), 25):
        chunk = us[i:i + 25]
        c = Counter(str(u['door']) for u in chunk)
        rows.append([f'{i}-{i + len(chunk) - 1}', ', '.join(f'door {d}: {c[d]}' for d in sorted(c)),
                     sum(u['verdict'] in PROVEN for u in chunk)])
    out = table(rows, ['worlds', 'doors chosen (6 = rooms, 7 = code)', 'proven'])
    rooms = [u for u in us if u.get('kinds')]
    if rooms:
        rr = []
        for i in range(0, len(rooms), 5):
            chunk = rooms[i:i + 5]
            pred = [abs(math.log(k['predicted'] / k['true'])) for u in chunk for k in u['kinds'] if k.get('predicted')]
            own = [abs(math.log(k['measured'] / k['true'])) for u in chunk for k in u['kinds'] if k.get('measured')]
            rr.append([f'{i}-{i + len(chunk) - 1}', len(pred), round(med(pred), 3) if pred else '-',
                       round(med(own), 3) if own else '-'])
        out += ('\n\nRooms: its mass prediction from a look, made before the room (median |log error| against the '
                'hidden mass), and its own weighing after:\n\n' +
                table(rr, ['rooms', 'predictions', 'predicted from the look', 'weighed by its fit']))
    code = [u for u in us if u.get('level') == 'code']
    if code:
        c = Counter(u['verdict'] for u in code)
        out += ('\n\nCode: ' + ', '.join(f'{k} {v}' for k, v in c.most_common()) +
                f"; programs met before: {sum(bool(u.get('met_before')) for u in code)}")
    return out


def selfgrade(life):
    alone = [u for u in life['units'] if stage_of(u) == 'alone' and u.get('self_p') is not None and not u['sure']]
    if not alone:
        return '(no self-grades yet)'
    right = [u for u in alone if u['verdict'] == 'right, unsure']
    wrong = [u for u in alone if u['verdict'] != 'right, unsure']
    said_right = lambda us: sum(u['self_p'] >= 0.5 for u in us)
    return table([['its guess was the law', len(right), said_right(right)],
                  ['its guess was not the law', len(wrong), said_right(wrong)]],
                 ['unproven worlds', 'n', 'it thought it was right'])


def honesty(life):
    us = life['units']
    return table([[len(us), sum(u['verdict'] == 'SURE AND WRONG' for u in us),
                   sum(u['verdict'] == 'checker refused' for u in us),
                   sum(bool(u.get('wrong_frozen')) for u in us), sum(len(u.get('false_sentences') or []) for u in us),
                   'HALTED: ' + str(life['halt']['why']) if life['halt'] else 'none']],
                 ['worlds', 'sure and wrong', 'checker refused', 'frozen flag', 'false sentences', 'tripwire'])


def narration(life, k=6):
    out = []
    for st in ('teach', 'practice', 'alone'):
        us = [u for u in life['units'] if stage_of(u) == st and u.get('narration')]
        if us:
            u = us[len(us) // 2]
            out.append(f"**{u['name']}** (truth: {u['truth']}; {u['verdict']}):\n" +
                       '\n'.join(f'> {s}' for s in u['narration'][:k]))
    return '\n\n'.join(out) or '(none yet)'


def report(lives):
    parts = []
    for life in lives:
        parts += [f"## Life {life['dir']}", '', '### What happened, stage by stage', '', verdicts(life), '',
                  '### What it learned (vocabulary)', '', learning(life), '', '### What it chose when alone', '',
                  doors(life), '', '### New doors (Stage 5)', '', newdoors(life), '',
                  '### Does it know what it knows?', '', selfgrade(life), '', '### Honesty', '',
                  honesty(life), '', '### It said, while working', '', narration(life), '']
        if life['check']:
            parts += ['### The Stage 1 check (did teaching change its behaviour?)', '',
                      '`' + json.dumps(life['check']['verdict']) + '`', '']
    return '\n'.join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dirs', nargs='+')
    ap.add_argument('--write', default=None)
    a = ap.parse_args()
    text = report([load(d) for d in a.dirs])
    if a.write:
        p = Path(a.write)
        doc = p.read_text(encoding='utf-8') if p.exists() else '<!-- GENERATED -->\n<!-- /GENERATED -->\n'
        head, rest = doc.split('<!-- GENERATED -->', 1)
        tail = rest.split('<!-- /GENERATED -->', 1)[1]
        p.write_text(head + '<!-- GENERATED -->\n' + text + '\n<!-- /GENERATED -->' + tail, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
