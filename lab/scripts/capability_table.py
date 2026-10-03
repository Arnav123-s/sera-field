"""The capability table of docs/SERA_STATUS.md, read from saved runs (never typed by hand).

  python scripts/capability_table.py            print the table
  python scripts/capability_table.py --write    replace it in docs/SERA_STATUS.md between the capability markers

Each row names a saved file and how to read its number. A run folder is under sera-runs/ (SERA_RUNS overrides the
place). A source 'git:<rev>:<path>' reads a file as it was at that revision (for numbers whose run files were lost,
kept only in the report of the time). A number that cannot be read prints as 'NOT FOUND', never as a guess.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# The default is only computed when SERA_RUNS is unset: a package unpacked at /content/<name> has no parents[2].
RUNS = Path(os.environ['SERA_RUNS']) if os.environ.get('SERA_RUNS') else REPO.parents[2] / 'sera-runs'
DOC = REPO / 'docs' / 'SERA_STATUS.md'
START, END = '<!-- capability-table:start -->', '<!-- capability-table:end -->'
JOURNAL = 'git:reports-journal-2026-10-01:docs/SERA_STATUS.md'

# subject, measure, source, how: ('re', pattern) -> the groups joined by ', '; ('count', hit, of[, start, end]) ->
# 'hits of total' within [start, end); ('json', key, field, field) -> 'field1/field2'. Screen copies wrap at the
# terminal's width, so text is read with its line breaks removed.
ROWS = [
    ('physics', 'a newborn, 1.5 h, seed 3 (176de5a): worlds proven', 'phys-176de5a-s3/summary.txt',
     ('count', r':: proven right', r':: (?:proven right|not proven|proven wrong)')),
    ('physics', 'stiff 2, proven as a curve over its cubic (steps, seconds)', 'phys-176de5a-s3/summary.txt',
     ('re', r"\(9 knots\) \| steps (\d+) \| ([\d.]+ s) \| invented \['mul\(_, mul\(_, _\)\)'\]")),
    ('physics', 'the newborn again after the honesty fix (ec5d2ec): worlds proven', 'phys-ec5d2ec-s3/summary.txt',
     ('count', r'-> proven right', r'-> (?:proven right|not proven|proven wrong|SURE AND WRONG)')),
    ('physics', 'its proofs by what the judge certified (ec5d2ec): curves, drawings, formulas',
     'phys-ec5d2ec-s3/summary.txt',
     ('re', r'"curves_proven": (\d+), "drawings_proven": (\d+), "formulas_proven": (\d+)')),
    ('physics', 'what the judge proves is a curve, not the formula: the wrong 1 + x³ accepted?',
     'judge-channel-1001/s10_false_credit.out', ('re', r'add\(1, mul\(s, mul\(s, s\)\)\).*?accepted=(\w+)')),
    ('physics', 'the ramp (Decision 16) judge regression: old claims before, after; accepted',
     'ab-b1/judge/summary.txt', ('re', r'JUDGE REGRESSION (\d+) and (\d+) claims; all the same ; accepted: (\d+)')),
    ('physics', 'A/B b1, One Field off (1d1f91f, ramp on): worlds proven', 'ab-b1/physics-f0/summary.txt',
     ('count', r'-> proven right', r'-> (?:proven right|not proven|proven wrong|SURE AND WRONG)')),
    ('physics', 'A/B b1, One Field on, same time: worlds proven', 'ab-b1/physics-f1/summary.txt',
     ('count', r'-> proven right', r'-> (?:proven right|not proven|proven wrong|SURE AND WRONG)')),
    ('physics', 'A/B b1, off: curves, drawings, formulas proven', 'ab-b1/physics-f0/summary.txt',
     ('re', r'"curves_proven": (\d+), "drawings_proven": (\d+), "formulas_proven": (\d+)')),
    ('physics', 'A/B b1, on: curves, drawings, formulas proven', 'ab-b1/physics-f1/summary.txt',
     ('re', r'"curves_proven": (\d+), "drawings_proven": (\d+), "formulas_proven": (\d+)')),
    ('physics', 'stiff 2 with the ramp (b1, off): steps, seconds, credited as', 'ab-b1/physics-f0/summary.txt',
     ('re', r'times \(position x \(position x position\)\) \(clipped at \+-1\) \| steps (\d+) \| ([\d.]+ s)'
            r'.*?CERTIFIED (formula) on dim:x\.x\.x')),
    ('language', 'A/B b1 seed 2: lessons proven, One Field off', 'ab-b1/compare-s2.json',
     ('json', 'lessons', 'off', 'universe')),
    ('language', 'A/B b1 seed 2: lessons proven, One Field on', 'ab-b1/compare-s2.json',
     ('json', 'lessons', 'on', 'universe')),
    ('language', 'A/B b1 seed 3: lessons proven, off; on', 'ab-b1/compare-s3.json',
     ('re', r'"lessons": \{"universe": \d+, "off": (\d+), "on": (\d+)')),
    ('talk', 'A/B b1 seed 2, before its talk lesson: of 60, off, on', 'ab-b1/compare-s2.json',
     ('re', r'"before: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ('talk', 'A/B b1 seed 2, the lesson re-read untaught: of 60, off, on', 'ab-b1/compare-s2.json',
     ('re', r'"read only: the lesson": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ('talk', 'A/B b1 seed 2, after its talk lesson: of 60, off, on', 'ab-b1/compare-s2.json',
     ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ('talk', 'A/B b1 seed 2, a second talk from the saved Field, taught: of 60, off, on',
     'ab-b1/compare-s2-reload.json', ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ('physics', 'A/B b1 general chain (physics and lists 4 h), One Field off: worlds proven',
     'ab-b1/general-f0/summary.txt',
     ('count', r'-> proven right', r'-> (?:proven right|not proven|proven wrong|SURE AND WRONG)')),
    ('physics', 'A/B b1 general chain, One Field on: worlds proven', 'ab-b1/general-f1/summary.txt',
     ('count', r'-> proven right', r'-> (?:proven right|not proven|proven wrong|SURE AND WRONG)')),
    ('lists', 'A/B b1 general chain: "list: reverse" proven in, off', 'ab-b1/general-f0/summary.txt',
     ('re', r'list: reverse \(teach\).*?-> proven right .*?\| steps \d+ \| ([\d.]+ s)')),
    ('lists', 'A/B b1 general chain: "list: reverse" proven in, on', 'ab-b1/general-f1/summary.txt',
     ('re', r'list: reverse \(teach\).*?-> proven right .*?\| steps \d+ \| ([\d.]+ s)')),
    ('language', 'A/B b1 general chain: language lessons proven, off', 'ab-b1/general-f0/summary.txt',
     ('count', r'"verdict": "proven right"', r'"verdict": "', 'AB DONE step', 'CONVERSE DONE')),
    ('language', 'A/B b1 general chain: language lessons proven, on', 'ab-b1/general-f1/summary.txt',
     ('count', r'"verdict": "proven right"', r'"verdict": "', 'AB DONE step', 'CONVERSE DONE')),
    ('talk', 'A/B b1 general chain, second talk taught: right/answered, off', 'ab-b1/general-f0/converse/reload/CONVERSE.json',
     ('json', 'taught: the fresh talk', 'right', 'answered')),
    ('talk', 'A/B b1 general chain, second talk taught: right/answered, on', 'ab-b1/general-f1/converse/reload/CONVERSE.json',
     ('json', 'taught: the fresh talk', 'right', 'answered')),
    ('physics', 'crutch A/B b2: the newborn without convince_halving: worlds proven',
     'ab-b2/physics-s3-off-convince_halving/summary.txt',
     ('count', r'-> proven right', r'-> (?:proven right|not proven|proven wrong|SURE AND WRONG)')),
    ('talk', 'crutch A/B b2: seed 2 taught, without talk_tally: right/answered (b1 with it: 47/42)',
     'ab-b2/talkonly-s2-off-talk_tally/CONVERSE.json', ('json', 'taught: the fresh talk', 'right', 'answered')),
    ('talk', 'crutch A/B b2: seed 2 taught, without nobody_said: right/answered (b1 with it: 47/42)',
     'ab-b2/talkonly-s2-off-nobody_said/CONVERSE.json', ('json', 'taught: the fresh talk', 'right', 'answered')),
    ('language', 'crutch A/B b2 seed 2: lessons proven, b1 with every crutch; without lesson_words (86cf3e5)',
     'ab-b2/compare-lang-lesson_words.json', ('re', r'"lessons": \{"universe": \d+, "off": (\d+), "on": (\d+)')),
    ('talk', 'crutch A/B b2 seed 2: taught talk of 60, b1 with every crutch; without lesson_words',
     'ab-b2/compare-lang-lesson_words.json', ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ('language', 'crutch A/B b2 seed 2: lessons proven, b1; without way_back',
     'ab-b2/compare-lang-way_back.json', ('re', r'"lessons": \{"universe": \d+, "off": (\d+), "on": (\d+)')),
    ('talk', 'crutch A/B b2 seed 2: taught talk of 60, b1; without way_back',
     'ab-b2/compare-lang-way_back.json', ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ('language', 'crutch A/B b2 seed 2: lessons proven, b1; without leader_override',
     'ab-b2/compare-lang-leader_override.json', ('re', r'"lessons": \{"universe": \d+, "off": (\d+), "on": (\d+)')),
    ('talk', 'crutch A/B b2 seed 2: taught talk of 60, b1; without leader_override',
     'ab-b2/compare-lang-leader_override.json',
     ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ('lists', '"list: reverse" proven (steps) on the way', 'phys-176de5a-s3/summary.txt',
     ('re', r'list: reverse \(teach\)[^:]*:: (proven right).*?steps (\d+)')),
    ('language', "the new teacher (e5666b4) on the general SERA's Field: lessons proven", 'teach-ab-1001/summary.txt',
     ('count', r': proven right', r': (?:proven right|not proven)', '== new', '--- the where 1')),
    ('language', 'the old teacher (176de5a), same Field: lessons proven', 'teach-ab-1001/summary.txt',
     ('count', r': proven right', r': (?:proven right|not proven)', '== old', '== new')),
    ('reading', 'closed book: psychology terms never asked about, right', 'ideas-6-colab/REPORT.md',
     ('re', r'terms it was never asked about: (\d+ of \d+) right')),
    ('talk', 'the general SERA: right before its talk lesson', 'converse-gen-fix2/summary.txt',
     ('re', r'== before: the fresh talk: (\d+/\d+) right')),
    ('talk', 'the general SERA: right after its talk lesson', 'converse-gen-fix2/summary.txt',
     ('re', r'== taught: the fresh talk: (\d+/\d+) right')),
    ('talk', 'the general SERA after the lesson: "never told of" right', 'converse-gen-fix2/summary.txt',
     ('re', r"== taught: the fresh talk:.*?'absent': '(\d+/\d+)")),
    ('talk', 'a seed-2 Field: right after its talk lesson', 'converse-s2-light-arms/CONVERSE.json',
     ('json', 'taught: the fresh talk', 'right', 'n')),
    ('talk', 'the same Field, untaught', 'converse-s2-light-arms/CONVERSE.json',
     ('json', 'before: the fresh talk', 'right', 'n')),
    ('code', 'write "reverse the list" from examples (general SERA, 140e36f): not proven within',
     'general-140e36f-s3/code_and_write.txt', ('re', r'reverse the list.*?SERA: I could not prove a program for this in (\d+ s)')),
    ('benchmark', '250 list functions, trials 2-11 (f8bdfb5; run files lost)', JOURNAL,
     ('re', r'\| SERA \| 250 \| ([\d.]+) \|')),
    ('benchmark', 'ARC, 400 evaluation puzzles (634f34c; run files lost)', JOURNAL,
     ('re', r'newborn (0 of 400); practised (3 of 400)')),
]


def read(src):
    if src.startswith('git:'):
        _, rev, path = src.split(':', 2)
        r = subprocess.run(['git', '-C', str(REPO), 'show', f'{rev}:{path}'], capture_output=True, text=True,
                           encoding='utf-8')
        return r.stdout if r.returncode == 0 else None
    p = RUNS / src
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else None


def value(src, how):
    text = read(src)
    if text is None:
        return 'NOT FOUND (no file)'
    if how[0] == 'json':
        d = json.loads(text).get(how[1], {})
        return f'{d[how[2]]}/{d[how[3]]}' if how[2] in d and how[3] in d else 'NOT FOUND'
    flat = text.replace('\r', '').replace('\n', '')
    if how[0] == 're':
        m = re.search(how[1], flat, re.S)
        return ', '.join(m.groups()) if m else 'NOT FOUND'
    if len(how) > 3:
        a = flat.find(how[3])
        b = flat.find(how[4], a + 1) if a >= 0 else -1
        if a < 0 or b < 0:
            return 'NOT FOUND (section)'
        flat = flat[a:b]
    total = len(re.findall(how[2], flat))
    return f'{len(re.findall(how[1], flat))} of {total}' if total else 'NOT FOUND'


def table():
    out = ['| subject | measure | result | saved in |', '|---|---|---|---|']
    for subject, measure, src, how in ROWS:
        where = (f'report at tag `{src.split(":")[1]}`' if src.startswith('git:')
                 else f'`sera-runs/{src}`')
        out.append(f'| {subject} | {measure} | **{value(src, how)}** | {where} |')
    return '\n'.join(out)


if __name__ == '__main__':
    t = table()
    if '--write' in sys.argv:
        with open(DOC, encoding='utf-8', newline='') as f:
            s = f.read()
        a, b = s.index(START), s.index(END)
        nl = '\r\n' if '\r\n' in s else '\n'
        s = s[:a + len(START)] + nl + t.replace('\n', nl) + nl + s[b:]
        with open(DOC, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
    print(t)
