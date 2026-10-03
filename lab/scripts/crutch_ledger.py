"""The crutch ledger of docs/SERA_STATUS.md §3, read from the code and from saved runs (never typed by hand).

  python scripts/crutch_ledger.py            print the ledger
  python scripts/crutch_ledger.py --write    replace it in docs/SERA_STATUS.md between the crutch-ledger markers
  python scripts/crutch_ledger.py --run RUN  write RUN/LEDGER.md from its saved teaching boundaries

Two tables: the mechanisms we coded into SERA's mind (sera/crutches.py REGISTRY), and the fixed numbers at the top
of sera/one.py (every module-level constant, with its line, the commit that last set it and its comment). A measured
effect is read from a saved run, as the capability table reads its numbers; with none it says so.
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'scripts'))

from capability_table import value  # noqa: E402
from sera.crutches import REGISTRY  # noqa: E402

DOC = REPO / 'docs' / 'SERA_STATUS.md'
ONE = REPO / 'sera' / 'one.py'
START, END = '<!-- crutch-ledger:start -->', '<!-- crutch-ledger:end -->'

# name -> [(what was compared, saved file, how to read it: as in capability_table.ROWS)]
EFFECTS = {
    'lesson_words': [
        ('b2 seed 2 lessons, with every crutch / without it (timing at the 1,800 s box)', 'ab-b2/compare-lang-lesson_words.json',
         ('re', r'"lessons": \{"universe": \d+, "off": (\d+), "on": (\d+)')),
        ('taught talk of 60, with / without', 'ab-b2/compare-lang-lesson_words.json',
         ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ],
    'way_back': [
        ('b2 seed 2 lessons, with every crutch / without it', 'ab-b2/compare-lang-way_back.json',
         ('re', r'"lessons": \{"universe": \d+, "off": (\d+), "on": (\d+)')),
        ('taught talk of 60, with / without', 'ab-b2/compare-lang-way_back.json',
         ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ],
    'leader_override': [
        ('b2 seed 2 lessons, with every crutch / without it', 'ab-b2/compare-lang-leader_override.json',
         ('re', r'"lessons": \{"universe": \d+, "off": (\d+), "on": (\d+)')),
        ('taught talk of 60, with / without', 'ab-b2/compare-lang-leader_override.json',
         ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ],
    'nobody_said': [
        ('b2 seed 2 taught talk of 60, with / without', 'ab-b2/compare-talk-nobody_said.json',
         ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ],
    'talk_tally': [
        ('b2 seed 2 taught talk of 60, with / without', 'ab-b2/compare-talk-talk_tally.json',
         ('re', r'"taught: the fresh talk": \{"n": \d+, "off": (\d+), "on": (\d+)')),
    ],
    'teacher_none_fits': [
        ('lessons proven with it', 'teach-ab-1001/summary.txt',
         ('count', r': proven right', r': (?:proven right|not proven)', '== new', '--- the where 1')),
        ('without it (the old teacher)', 'teach-ab-1001/summary.txt',
         ('count', r': proven right', r': (?:proven right|not proven)', '== old', '== new')),
    ],
}


def blame(line):
    r = subprocess.run(['git', '-C', str(REPO), 'blame', '-L', f'{line},{line}', '--porcelain', 'HEAD', '--',
                        'sera/one.py'], capture_output=True, text=True)
    return r.stdout[:7] if r.returncode == 0 else '?'


def knobs():
    src = ONE.read_text(encoding='utf-8')
    lines = src.splitlines()
    out = []
    for node in ast.parse(src).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
            continue
        text = lines[node.lineno - 1]
        val = ast.get_source_segment(src, node.value)
        note = text.split('#', 1)[1].strip() if '#' in text[len(text.split('=', 1)[0]) + 1:] else ''
        out.append((name, val, node.lineno, note))
    return out


def effect(name):
    rows = EFFECTS.get(name)
    if not rows:
        return 'not measured (a switch-off A/B: plan 3.5)'
    return '; '.join(f'{label}: **{value(src, how)}** (`sera-runs/{src}`)' for label, src, how in rows)


def ledger():
    out = ['**Mechanisms** (`sera/crutches.py`; off: `SERA_CRUTCH_OFF=<name>`, SERA as it was before the commit)', '',
           '| name | what it does | where | commit | fixed / taught / learned | measured effect |',
           '|---|---|---|---|---|---|']
    for name, c in REGISTRY.items():
        out.append(f"| `{name}` | {c['what']} | `{c['where']}` | {c['commit']} | {c['status']} | {effect(name)} |")
    ks = knobs()
    out += ['', f'**Knobs**: the {len(ks)} fixed numbers at the top of `sera/one.py`, none learned yet (set one for an '
                f'A/B: `SERA_KNOBS=<NAME>=<value>`)', '',
            '| knob | value | line | commit | what it is |', '|---|---|---|---|---|']
    for name, val, line, note in ks:
        val = val if len(val) <= 40 else val[:37] + '...'
        out.append(f"| `{name}` | `{val}` | {line} | {blame(line)} | {note.replace('|', '/')} |")
    return '\n'.join(out)


def run_ledger(run):
    """Render saved phase boundaries; no git blame, grading or learner execution.

    Consultation counts are separately named. A measured callable invocation
    does not establish that a whole task depended on that mechanism. Null
    dependence remains 'not measured', including for fixed crutches.
    """
    run = Path(run)
    path = run / 'LEDGER.jsonl'
    if not path.is_file():
        raise ValueError(f'No saved teaching ledger: {path}')
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    lines = ['| phase | boundary | crutch | on | status | teacher weight | consultations | enabled checks | callable uses | outcome dependence / cheap check |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for row in rows:
        for name, entry in sorted(row['crutches'].items()):
            use = entry['use']
            cf = entry.get('counterfactual')
            dependence = entry.get('outcome_dependence')
            if dependence is None:
                effect = 'not measured'
            else:
                effect = str(dependence)
            if cf:
                effect += f"; {cf['changed']}/{cf['n']} channel/decision changes ({cf['scope']})"
            weight = entry.get('teacher_weight')
            calls = use.get('calls')
            lines.append(f"| {row['phase']} | {row['boundary']} | {name} | {entry['on']} | {entry['status']} | "
                         f"{weight if weight is not None else '-'} | {use['consulted']} | {use['enabled']} | "
                         f"{calls if calls is not None else 'not instrumented'} | {effect.replace('|', '/')} |")
    lines += ['', 'Counts are cumulative through each boundary. Callable scopes and teacher evidence totals are in ',
              '`LEDGER.jsonl`. Fixed mechanisms keep their configured switches; only teacher statistics fade. ',
              'Cheap checks compare a public channel or answer decision, not causal task success.']
    table = '\n'.join(lines)+'\n'
    (run/'LEDGER.md').write_text(table, encoding='utf-8')
    return table


if __name__ == '__main__':
    if '--run' in sys.argv:
        i = sys.argv.index('--run')
        if i+1 >= len(sys.argv) or '--write' in sys.argv:
            raise SystemExit('Use --run RUN (without --write)')
        print(run_ledger(sys.argv[i+1]))
        raise SystemExit(0)
    t = ledger()
    if '--write' in sys.argv:
        with open(DOC, encoding='utf-8', newline='') as f:
            s = f.read()
        a, b = s.index(START), s.index(END)
        nl = '\r\n' if '\r\n' in s else '\n'
        s = s[:a + len(START)] + nl + t.replace('\n', nl) + nl + s[b:]
        with open(DOC, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
    print(t)
