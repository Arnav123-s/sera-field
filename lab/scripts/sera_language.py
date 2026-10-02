"""SERA learns language worlds, then reads psychology and philosophy books.

Run with scripts/sera_language.py --out RUN [--seed 1] [--hours 20]
"""
import argparse
import ast
import math
import hashlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from sera import dictionary as DICT, lang as LG, one as ONE, phi as PH, tasks as TS, talk as TK


def unit_of(rec):
    keep = {k: v for k, v in rec.items() if k not in ('say', 'choices')}
    keep['say'] = [s['text'] for s in rec.get('say', [])]
    return keep


def live(sera, task, out, deadline, stage, teaching, box=None, visit=1):
    """SERA lives one world until its judge accepts an answer, the world's time box (box seconds; None: the run's
    end) or the run's end. A world revisited later is a new unit (_visitN)."""
    (out / 'units').mkdir(parents=True, exist_ok=True)
    unit = out / 'units' / (task.name.replace(' ', '_').replace(':', '') + (f'_visit{visit}' if visit > 1 else '')
                            + '.json')
    if unit.exists():                                   # a finished world (a resumed run): its answer as an expression
        u = json.loads(unit.read_text(encoding='utf-8'))
        u['answer'] = ast.literal_eval(u['answer_repr']) if u.get('answer_repr') not in (None, 'None') else None
        return u
    ONE.MAX_WALL = max(5.0, min(deadline - time.time(), box or math.inf))
    print(f"=== {task.name} ({stage}{', visit ' + str(visit) if visit > 1 else ''}, box "
          f"{ONE.MAX_WALL:.0f} s) | words heard: {' '.join(task.words) or '-'}", flush=True)
    rec = sera.live(task, teaching=teaching)
    u = unit_of(rec)
    u['answer_repr'] = repr(rec.get('answer'))
    u.update(stage=stage, english=[task.show(x) + ' -> ' + TS.text(y) for x, y in task.data[:3]])
    unit.write_text(json.dumps(u, indent=1, default=str), encoding='utf-8')
    sera.field.save(out / 'field.pkl')
    if u.get('verdict') == 'SURE AND WRONG':
        raise RuntimeError(f"TRIPWIRE: {task.name} accepted but wrong")
    print(f"{task.name}: {u.get('verdict')} | {u.get('claim')} | steps {u.get('steps')} | {u.get('wall')} s | built "
          f"{[b.get('words') for b in u.get('built') or []]} | peak {u.get('peak_mb') or 0:.0f} MB"
          + (f", {u['memory_stops']} memory stops" if u.get('memory_stops') else ''), flush=True)
    for line in u['say'][-6:]:
        print('    ' + line, flush=True)
    u['answer'] = rec.get('answer')
    return u


def proven(u):
    return bool(u.get('proven')) or u.get('verdict') == 'proven right'


def practise(sera, todo, out, deadline, stage, teaching, box):
    """Each world in the teacher's order with a time box; the ones not proven come back after the others with
    twice the box (as the ARC practice), until the stage's time ends. Returns {name: unit} of the last visits."""
    last, visit = {}, 1
    while todo and time.time() < deadline:
        left = []
        for name, build in todo:
            if time.time() >= deadline:
                left.append((name, build))
                continue
            task = build()
            task.name = name
            last[name] = u = live(sera, task, out, deadline, stage, teaching, box=box, visit=visit)
            if not proven(u):
                left.append((name, build))
        todo, box, visit = left, box * 2, visit + 1
    return last


def teaching(seed):
    """The teacher's order, simple to complex; 'what is' right after 'where is', which it builds on."""
    builders = (TS.lesson_first, TS.lesson_last, TS.lesson_who, TS.lesson_where, TS.lesson_what_is,
                TS.lesson_who_in, TS.lesson_where_now, TS.lesson_is_in)
    return [(f'{fn.__name__[7:]} {rep + 1}', lambda fn=fn, i=i, rep=rep: fn(seed + i * 100 + rep))
            for i, fn in enumerate(builders) for rep in range(2)]


def alone(seed):
    return [(n, lambda fn=fn, i=i: fn(seed + 1000 + i)) for i, (n, fn) in enumerate((
        ('where first', TS.lesson_where_first), ('who went', TS.lesson_who_went),
        ('what is alone', TS.lesson_what_is_alone)))]


def _local(tag):
    return tag.rsplit('}', 1)[-1].lower()


def psych_sentences(root):
    out = []
    for path in sorted(Path(root).rglob('*.cnxml')):
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            continue
        base = tree.getroot()
        for parent in base.iter():
            for child in list(parent):
                if _local(child.tag) in ('exercise', 'glossary'):
                    parent.remove(child)
        for p in base.iter():
            if _local(p.tag) != 'para':
                continue
            value = ' '.join(''.join(p.itertext()).split())
            out.extend((s, 'psychology') for s in re.split(r'(?<=[.!?])\s+', value) if s)
    return out


def gutenberg_sentences(root):
    out = []
    for filename in ('gutenberg-1497.txt', 'gutenberg-10615.txt'):
        path = Path(root) / filename
        if not path.exists():
            continue
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        keep, started = [], False
        for line in lines:
            upper = line.upper()
            if '*** START OF' in upper or '*** START OF THE PROJECT GUTENBERG' in upper:
                started = True
                continue
            if '*** END OF' in upper or '*** END OF THE PROJECT GUTENBERG' in upper:
                break
            if started:
                keep.append(line)
        if not started:
            keep = lines
        text = ' '.join(keep)
        out.extend((s, filename) for s in re.split(r'(?<=[.!?])\s+', text) if s)
    return out


NOT_TERMS = set('this that these those it its there here what which who whom whose why how when where he she they '
                'we you i one such and but or nor so yet if then than p e s'.split())


def read_sentences(rows, book=None):
    """The observer's test material from a book (not SERA's ability): its sentences '<term> is|are <3-25 words>',
    a leading the/a/an dropped, the term one word the dictionary knows mostly as a thing (a noun), not a pronoun or a
    little word. A sentence becomes [term, 'is', its words...]."""
    pattern = re.compile(r'^(?:(?:the|a|an) )?([a-z]+) (?:is|are) ((?:[a-z]+ ){2,24}[a-z]+)$')
    terms, counts = {}, {}
    for sentence, source in rows:
        words = re.findall(r'[a-z]+', sentence.lower())
        match = pattern.match(' '.join(words))
        if not match:
            continue
        word = match.group(1)
        if word in NOT_TERMS or len(word) < 3:
            continue
        if book is not None:
            kinds = [k for k, _ in book.senses.get(book.root(word), [])]
            if not kinds or kinds.count('n') * 2 < len(kinds):
                continue
        terms.setdefault(source, {}).setdefault(word, []).append([word, 'is'] + match.group(2).split())
        counts.setdefault(source, Counter())[word] += 1
    return terms, counts


def answer(task, rec, field):
    expr = rec.get('answer')
    if expr is None:
        return None
    concepts = field.concept_table()
    return LG.safe(expr, {'g': task.data[0][0]}, concepts)


def test_story(term, terms, seed):
    """The observer's story for a term: one of its sentences among two sentences about other terms, shuffled (a
    fixed draw per term), and the answer the book gives."""
    rng = np.random.default_rng([seed, 877, sum(map(ord, term))])
    own = terms[term][int(rng.integers(len(terms[term])))]
    others = [t for t in sorted(terms) if t != term]
    picks = [terms[others[int(i)]][0] for i in rng.choice(len(others), size=min(2, len(others)), replace=False)]
    story = [own] + picks
    story = [story[int(i)] for i in rng.permutation(len(story))]
    return story, own[2:]


def evaluate_term(rec, field, term, sentences):
    """SERA's own proven answer to 'what is <term>' over the given sentences (None if it proved nothing)."""
    expr = rec.get('answer')
    if expr is None or not rec.get('proven'):
        return None
    concepts = field.concept_table()
    q = (TS.sym('what'), TS.sym('is'), TS.sym(term))
    story = tuple(tuple(TS.sym(w) for w in s) for s in sentences)
    return LG.safe(expr, {'g': (q,) + story}, concepts)


def reading_source(sera, newborn, source, terms, frequencies, seed, out, deadline, box=None):
    names = sorted(terms)
    rng = np.random.default_rng([seed, len(source), 761])
    order = list(rng.permutation(len(names)))
    ntest = max(1, int(round(len(names) * .30))) if names else 0
    test = [names[i] for i in order[:ntest]]
    practice = [names[i] for i in order[ntest:]]
    train_sentences = [sentence for term in practice for sentence in terms[term]]
    task = TS.book_what_is(train_sentences, seed + 21)
    source_id = hashlib.sha1(source.encode('utf-8')).hexdigest()[:8]
    task.name = 'book what is ' + Path(source).stem + '_' + source_id
    rec = live(sera, task, out, deadline, 'read', False, box=box)
    control_task = TS.book_what_is(train_sentences, seed + 21)
    control_task.name = task.name
    nrec = live(newborn, control_task, out / 'newborn', deadline, 'read-control', False, box=box)
    result = {'sera_answers': {}, 'newborn_answers': {}, 'terms': len(names),
              'practice_terms': len(practice), 'frozen_terms': len(test)}
    for label, runner, field in (('sera', rec, sera.field), ('newborn', nrec, newborn.field)):
        right = 0
        decoded = result['sera_answers'] if label == 'sera' else result['newborn_answers']
        for term in names:
            story, book_says = test_story(term, terms, seed)
            got = evaluate_term(runner, field, term, story)
            decoded[term] = got
            if term in test and got == tuple(TS.sym(w) for w in book_says):
                right += 1
        result[label] = dict(right=right, total=len(test), accuracy=right / len(test) if test else 0.0)
    lines = []
    frequent = sorted(names, key=lambda t: (-frequencies.get(t, 0), t))[:20]
    names_of = sera.field.names()
    for term in frequent:
        got = evaluate_term(rec, sera.field, term, test_story(term, terms, seed)[0])
        lines.append(f"SERA: {term} is {TS.text(got) if got is not None else 'unknown'}")
        u = sera.field.lexicon.understand(term)             # what the word means to it, in its own ideas
        if u['meaning']:
            (kind, ref), p = max(u['meaning'].items(), key=lambda kv: kv[1])
            mine = names_of.get(ref, ref) if kind == 'concept' else f'{kind} {ref}'
            lines.append(f"      (to me '{term}' is near my {mine}, {u['how']}"
                         + (f" through {', '.join(u['through'])}" if u['through'] else '') + f", sure {u['sure']:.2f})")
        else:
            lines.append(f"      (I have no idea of my own for '{term}' yet)")
    result['lines'] = lines
    return result


STOP = set('a an and are as at be by for from in is it of on or that the this to was were what which who with'.split())


def mcq_score(items, answers):
    right = answered = total = 0
    for item in items:
        total += 1
        qwords = [w for w in re.findall(r'[a-z]+', item.get('question', '').lower()) if w not in STOP]
        terms = [w for w in qwords if w in answers]
        if not terms:
            continue
        dictionary = {w: set(re.findall(r'[a-z]+', TS.text(answers[w]).lower())) for w in terms
                      if answers.get(w) is not None}
        terms = [w for w in terms if w in dictionary]
        scores = []
        for option in item.get('options', []):
            ow = set(re.findall(r'[a-z]+', str(option).lower()))
            scores.append(sum(len(ow & dictionary[w]) for w in terms))
        best = max(scores, default=0)
        if best == 0 or scores.count(best) != 1:
            continue
        answered += 1
        if scores.index(best) == item.get('answer'):
            right += 1
    return dict(right=right, answered=answered, total=total)


def mcq_files(root):
    found = []
    for filename in ('questions.json', 'exams.json'):
        for p in sorted(Path(root).rglob(filename)):
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, dict) and 'mit' in data and 'openstax' in data:
                found.append((str(p), data))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--hours', type=float, default=20.0)
    ap.add_argument('--book', default=None, help='WordNet data directory')
    ap.add_argument('--stage', choices=('all', 'teach', 'alone', 'read'), default='all')
    ap.add_argument('--field', default=None, help='starting Field pickle')
    ap.add_argument('--box', type=float, default=30.0, help='minutes a world gets on its first visit (doubles)')
    ap.add_argument('--teach-share', type=float, default=0.6, help='share of the hours for teaching (stage all)')
    ap.add_argument('--alone-share', type=float, default=0.15, help='share of the hours for the alone worlds')
    ap.add_argument('--psych', default='D:/ai/PI&E/private/psychology-sources-20260907')
    ap.add_argument('--phil', default='D:/ai/PI&E/private/sources')
    args = ap.parse_args()
    TK.BOOK = DICT.load(args.book)
    out = Path(args.out)
    (out / 'units').mkdir(parents=True, exist_ok=True)
    field_path = Path(args.field) if args.field else out / 'field.pkl'
    field = PH.Field.load(field_path) if field_path.exists() else PH.Field(args.seed)
    sera = ONE.Sera(args.seed, field)
    newborn = ONE.Sera(args.seed, PH.Field(args.seed))
    deadline = time.time() + 3600 * args.hours
    start = time.time()
    total = deadline - start
    teach_end = start + total * (args.teach_share if args.stage == 'all' else 1.0)
    alone_end = teach_end + total * (args.alone_share if args.stage == 'all' else 0.0)
    if args.stage == 'alone':
        alone_end = deadline
    if args.stage in ('all', 'teach'):
        practise(sera, teaching(args.seed), out, teach_end, 'teach', True, args.box * 60)
        sera.field.save(out / 'field-teach.pkl')
        print('TEACH DONE', json.dumps(sera.field.account()), flush=True)
    if args.stage in ('all', 'alone'):
        alone_worlds = []
        for name, build in alone(args.seed):
            alone_worlds.append((name, lambda build=build: build()))
        practise(sera, alone_worlds, out, alone_end, 'alone', False, args.box * 60)
        print('ALONE DONE', json.dumps(sera.field.account()), flush=True)
    report = ['# SERA language report', '', f'Seed: {args.seed}', f'Stage: {args.stage}', '']
    read_results, sera_answers, newborn_answers = {}, {}, {}
    if args.stage in ('all', 'read'):
        sources = {'psychology': psych_sentences(args.psych), 'gutenberg-1497': [], 'gutenberg-10615': []}
        philrows = gutenberg_sentences(args.phil)
        for row in philrows:
            if row[1] == 'gutenberg-1497.txt': sources['gutenberg-1497'].append(row)
            else: sources['gutenberg-10615'].append(row)
        for bookname, rows in sources.items():
            book_terms, frequencies = read_sentences(rows, TK.BOOK)
            for source, terms in book_terms.items():
                if len(terms) < 3:
                    report.extend([f'## {bookname}: {source}', '',
                                   f"Skipped: {len(terms)} matching terms; at least 3 are needed for a 2-term practice story and a frozen test.", ''])
                    continue
                rr = reading_source(sera, newborn, source, terms, frequencies[source], args.seed, out, deadline,
                                    box=max(60.0, (deadline - time.time()) / 6))
                sera_answers.update(rr['sera_answers'])
                newborn_answers.update(rr['newborn_answers'])
                read_results[bookname + ':' + source] = {k: v for k, v in rr.items()
                                                          if k not in ('lines', 'sera_answers', 'newborn_answers')}
                report.extend([f'## {bookname}: {source}', '',
                               f"Terms: {rr['terms']} total, {rr['practice_terms']} practice, {rr['frozen_terms']} frozen test",
                               f"Frozen test: {rr['sera']['right']} / {rr['sera']['total']} = {rr['sera']['accuracy']:.4f}",
                               f"Newborn control: {rr['newborn']['right']} / {rr['newborn']['total']} = {rr['newborn']['accuracy']:.4f}", ''])
                report.extend(rr['lines'] + [''])
        concepts = sera.field.concept_table()
        report += ['## SERA lexicon', '']
        for c in sera.field.concepts:
            sayings = sera.field.lexicon.say([('concept', c['id'])], coin=False)
            if sayings: report.append(f"{c['id']}: {' '.join(sayings)}")
        report += ['', '## Inbox questions', '']
        report.extend(q.get('text', str(q)) for q in sera.field.inbox)
        report += ['', '## MCQ', '', 'Choice rule: the observer\'s matching rule, not SERA\'s.', '']
        for path, data in mcq_files(args.psych):
            for corpus in ('mit', 'openstax'):
                score = mcq_score(data.get(corpus, []), sera_answers)
                control = mcq_score(data.get(corpus, []), newborn_answers)
                report.append(f'{path} {corpus}: SERA {score["right"]} / {score["answered"]} / {score["total"]}; newborn {control["right"]} / {control["answered"]} / {control["total"]}')
    (out / 'REPORT.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print('\n'.join(report), flush=True)


if __name__ == '__main__':
    main()
