"""The observatory of one SERA (plan revision 6): every table generated from a run's saved units and Field.

  python scripts/sera_one_observe.py RUN [--md out.md]

Tables: what it did in each task (by stage); proofs by subject; what it invented and reused (and from where); what it
says and whether its words are true; serendipity and dualities; how it chose to work (its configurations, by kind of
task, early against late); the twin (its taught inventions hidden) against itself; what it asked us.
"""
import argparse
import json
import pickle
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def load(run):
    units = []
    for p in sorted((Path(run) / 'units').glob('*.json')):
        u = json.loads(p.read_text(encoding='utf-8'))
        u['_file'] = p.name
        units.append(u)
    field = None
    fp = Path(run) / 'field.pkl'
    if fp.exists():
        with open(fp, 'rb') as f:
            field = pickle.load(f)
    return units, field


def table(rows, head):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    for r in rows:
        out.append('| ' + ' | '.join(str(x) for x in r) + ' |')
    return '\n'.join(out)


def order_of(units):
    events = {}
    return units


def report(run):
    units, field = load(run)
    main = [u for u in units if u.get('tag', '') == '']
    twin = {u['task']: u for u in units if u.get('tag') == 'twin-'}
    out = [f'# One SERA: {run}', '']
    out.append(f'{len(main)} tasks lived ({sum(1 for u in main if u["stage"] == "teach")} taught, '
               f'{sum(1 for u in main if u["stage"] == "alone")} alone); twin: {len(twin)}.')
    out.append('')
    out.append('## Every task')
    rows = []
    for u in main:
        rows.append([u['stage'], u['task'], u['verdict'], (u.get('claim') or '-')[:60], u['steps'], u['wall'],
                     ', '.join(i.get('body', '')[:30] for i in u.get('invented', [])) or '-',
                     ', '.join(map(str, u.get('reused', []))) or '-', ' '.join(u.get('said', [])) or '-',
                     'yes' if u.get('serendipity') else '-', 'yes' if u.get('duality') else '-']
                    )
    out.append(table(rows, ['stage', 'task', 'verdict', 'claim', 'steps', 'wall s', 'invented', 'reused', 'says',
                            'serendipity', 'duality']))
    out.append('')
    out.append('## Proofs by subject and stage')
    agg = defaultdict(Counter)
    for u in main:
        agg[(u['subject'], u['stage'])][u['verdict']] += 1
        agg[(u['subject'], u['stage'])]['tasks'] += 1
    rows = [[s, st, c['tasks'], c['proven right'], c['SURE AND WRONG'], c['not proven'] + c['right, unsure']]
            for (s, st), c in sorted(agg.items())]
    out.append(table(rows, ['subject', 'stage', 'tasks', 'proven right', 'SURE AND WRONG', 'not proven']))
    out.append('')
    if field is not None:
        out.append('## What it invented (its concepts, in order), and how each arose')
        out.append('None of these was given to it: there is no list of laws, programs or rules anywhere in SERA. "Built '
                   'by search" = it found the expression by trying compositions of its innate mechanisms (and its own '
                   'earlier concepts), bigger and bigger, until one fit and was proven; "shaped from measurements" = it '
                   'fitted a free curve to what it saw and the judge proved it. Either way, keeping it as a new named '
                   'part of its language is the invention (compression); "reused" counts later proofs that used it.')
        names = field.names() if hasattr(field, 'names') else {}
        stage_of = {u['task']: u['stage'] for u in main}
        rows = []
        from sera import lang as LG
        for c in field.concepts:
            tab = c['body'][0] == 'tab'
            parts = [p for p in c.get('parts', []) if isinstance(p, (list, tuple)) and p and p[0] == 'concept']
            rows.append([c['id'], names.get(c['id'], c['name']), c['subject'], c['born'], stage_of.get(c['born'], '?'),
                         'shaped from measurements' if tab else 'built by search in its own language',
                         LG.show(c['body'], names)[:70] if not tab else 'a curve it drew',
                         ', '.join(str(p[1]) for p in parts) or '-', len(c.get('shapes') or []), c['uses']])
        out.append(table(rows, ['id', 'its word', 'subject', 'born in', 'taught or alone', 'how', 'body',
                                'made of its concepts', 'judge shapes', 'reused']))
        out.append('')
        out.append('## Its words')
        rows = [[w, repr(m), f'{p:.2f}'] for w, m, p in field.lexicon.grounded(level=0.6, min_heard=1)]
        out.append(table(rows, ['word', 'what it means to SERA', 'P']))
        out.append(f'\nCoined by itself: {dict((repr(k), v) for k, v in field.lexicon.coined.items())}')
        out.append('')
    said = [(u['task'], ' '.join(u.get('said', [])), ', '.join(u.get('false_words', [])) or '-') for u in main
            if u.get('said')]
    out.append('## What it says, and whether it is true (the teacher\'s language; its own coined names count as true)')
    out.append(table(said, ['task', 'says', 'false words']))
    out.append('')
    out.append('## Serendipity and dualities')
    rows = [[u['task'], json.dumps(u['serendipity'])] for u in main if u.get('serendipity')]
    out.append(table(rows, ['task', 'an idea from elsewhere explained it']) if rows else 'None yet.')
    rows = [[u['task'], u['duality']['other'][:80]] for u in main if u.get('duality')]
    out.append('')
    out.append(table(rows, ['task', 'another, different idea that also works']) if rows else 'No dualities.')
    out.append('')
    out.append('## How it chose to work (configurations of its faculties), early and late, by kind of task')
    by = defaultdict(list)
    for u in main:
        by[u['kind']].append(u)
    rows = []
    for kind, us in sorted(by.items()):
        half = max(1, len(us) // 2)
        early = Counter(c for u in us[:half] for c in (u.get('configs') or []))
        late = Counter(c for u in us[half:] for c in (u.get('configs') or []))
        rows.append([kind, len(us), ', '.join(f'{k} {v}' for k, v in early.most_common(4)),
                     ', '.join(f'{k} {v}' for k, v in late.most_common(4))])
    out.append(table(rows, ['kind of task', 'tasks', 'first half', 'second half']))
    out.append('')
    out.append('## Its senses: where it looked closer (lenses) and the new dimensions it made, and whether they helped')
    from ccops5.core import grammar as GR
    rows = [[u['task'], ', '.join(GR.describe_input(s) for s in u.get('senses') or []) or '-',
             ', '.join(GR.describe_input(s) for s in u.get('senses_used') or []) or '-', u['verdict']]
            for u in main if u.get('senses') or u.get('senses_used')]
    out.append(table(rows, ['task', 'made', 'used in its proof', 'verdict']) if rows else 'It made no new sense.')
    if field is not None and getattr(field, 'senses', None):
        out.append('')
        out.append(table([[s['name'], GR.describe_input(s['name']), s['born'], s['uses']] for s in field.senses],
                         ['sense', 'in words', 'made in', 'proofs']))
    out.append('')
    out.append('## Its imagination: which method found each proven idea, and the methods it made its own')
    rows = [[u['task'], u['imagined_by']['moves'], u['imagined_by'].get('origin') or '-',
             (u.get('method_named') or {}).get('moves', '-')] for u in main if u.get('imagined_by')]
    out.append(table(rows, ['task', 'moves that found the proven idea', 'how', 'named as its own']) if rows
               else 'No proven idea came from its imagination yet.')
    if field is not None and getattr(field, 'methods', None) is not None and field.methods.named:
        out.append('')
        kinds = sorted({k for (k, _) in field.methods.stats})
        out.append(table([[n['id'], ' then '.join(n['moves']), n['born'], n['uses'],
                           '; '.join(f"{k}: {field.methods.triggers(k, n['method'])}" for k in kinds)]
                          for n in field.methods.named],
                         ['its method', 'moves', 'made in', 'proofs', 'what triggers it (by kind of task)']))
    out.append('')
    out.append('## Its deeper questions (from what it measured)')
    rows = [[u['task'], u['question'].get('things'), u['question'].get('kinds'), u['question']['text'][:140]]
            for u in main if u.get('question')]
    out.append(table(rows, ['task', 'things', 'kinds of mass', 'what it asks']) if rows else 'None yet.')
    out.append('')
    out.append('## Where its time went (seconds per phase, summed over the tasks of each subject)')
    tim = defaultdict(Counter)
    for u in main:
        for k, v in (u.get('timing') or {}).items():
            tim[u['subject']][k] += v
    phases = sorted({k for c in tim.values() for k in c})
    out.append(table([[s] + [f'{tim[s][k]:.0f}' for k in phases] for s in sorted(tim)], ['subject'] + phases)
               if tim else 'Not recorded.')
    out.append('')
    if twin:
        out.append('## Invention\'s worth: SERA against its twin (the same alone-tasks, its taught inventions hidden)')
        rows = []
        for u in main:
            if u['stage'] != 'alone' or u['task'] not in twin:
                continue
            t = twin[u['task']]
            rows.append([u['task'], u['verdict'], u['steps'], u['wall'], t['verdict'], t['steps'], t['wall']])
        out.append(table(rows, ['task', 'SERA', 'steps', 'wall s', 'twin', 'steps', 'wall s']))
        out.append('')
    if field is not None and field.inbox:
        out.append('## What it asked us')
        out.append(table([[q['id'], q['task'], q['text'][:160]] for q in field.inbox], ['id', 'task', 'question']))
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--md', default=None)
    a = ap.parse_args()
    text = report(a.run)
    if a.md:
        Path(a.md).write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
