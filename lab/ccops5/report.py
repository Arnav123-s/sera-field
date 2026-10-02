"""ccops5 lab | turn saved lives into tables.

Built as an isolated experiment. Not part of sera-field.
"""
import json
import statistics
from pathlib import Path

from . import world as W
from .mind import RULES

ORDER = ('full', 'forget_kinds', 'reset_all', 'ungated', 'passive', 'frozen_laws', 'no_reuse', 'baseline',
         'baseline_parts', 'baseline_sets', 'baseline_words')
MEANING = {
    'full': 'everything connected',
    'forget_kinds': 'keeps laws, forgets objects, words and places after each situation (like CORE-022)',
    'reset_all': 'whole library wiped after every situation',
    'ungated': 'keeps everything without checking it first',
    'passive': 'same push every time (never throws again differently)',
    'frozen_laws': 'learns its hand, then may not grow new laws',
    'no_reuse': 'a law may only be used where it was found',
    'baseline': 'ordinary neural network: knowledge only in its weights',
    'baseline_parts': 'ordinary neural network, also shown the parts of glued things (added up)',
    'baseline_sets': 'ordinary neural network that reads each part of a glued thing, then adds (deep sets)',
    'baseline_words': 'ordinary neural network, not shown the look of brand-new toys (words only)',
}
HAND, ICE, CARPET, WATER, SPRINGS, SWINGS, WORDS, STUCK, FINAL = range(9)


def _median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def _mean(values):
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


def _stage(records, i):
    return [r for r in records if r['stage'] == W.STAGES[i]]


def _count(events, what, stage=None):
    return sum(1 for e in events if e['what'] == what and (stage is None or e['stage'] == W.STAGES[stage]))


def per_life(life):
    rec, ev, gated = life['records'], life['events'], not life['mode'].startswith('baseline')
    out = {}
    for i in range(len(W.STAGES)):
        rs = _stage(rec, i)
        out[f'before_{i}'] = _median(r['miss_before'] for r in rs)
        out[f'after_{i}'] = _median(r['miss_after'] for r in rs)
        out[f'pushes_{i}'] = _mean(len(r['pushes']) for r in rs)
        out[f'checked_{i}'] = _mean(1.0 if r.get('checked') else 0.0 for r in rs) if gated else None
    learning = [r for r in rec if r['stage'] in W.STAGES[ICE:SWINGS + 1]]
    out['learning_before'] = _median(r['miss_before'] for r in learning)
    out['learning_after'] = _median(r['miss_after'] for r in learning)
    out['final_before'] = out[f'before_{FINAL}']
    out['final_after'] = out[f'after_{FINAL}']
    words = _stage(rec, WORDS)
    out['words_guess'] = _median(r.get('miss_word_guess') for r in words)
    out['place_guess'] = _median(r.get('miss_place_guess') for r in words)
    stuck = _stage(rec, STUCK)
    out['stuck_pairs_before'] = _median(r['miss_before'] for r in stuck if r.get('parts') == 2)
    out['stuck_triples_before'] = _median(r['miss_before'] for r in stuck if r.get('parts') == 3)
    out['stuck_place'] = _median(r.get('miss_place_guess') for r in stuck)
    out['stuck_worked_out'] = _median(r['miss_before'] for r in stuck if r.get('rule_used'))
    out['rule'] = life.get('math_rule')
    kept = [e for e in ev if e['what'] == 'math rule kept']
    out['rule_after'] = kept[0]['episode'] - stuck[0]['episode'] + 1 if kept and stuck else None
    out['rule_dropped'] = _count(ev, 'math rule dropped')
    out['rule_misses'] = {name: _median(r['rule_misses'][name] for r in stuck if 'rule_misses' in r)
                          for name in RULES}
    out['swing_proposals'] = _count(ev, 'new law proposed', SWINGS)
    out['swing_after'] = out[f'after_{SWINGS}']
    out['laws_kept'] = len(life['laws'])
    out['proposals'] = _count(ev, 'new law proposed')
    out['rejected'] = _count(ev, 'proposed law rejected')
    out['corrections'] = _count(ev, 'memory corrected')
    out['pushes'] = _mean(len(r['pushes']) for r in rec if r['stage'] != W.STAGES[HAND])
    tricked = {(r['kind'], r['scene']) for r in rec if r['trick']}
    out['tricks'] = sum(1 for r in rec if r['trick'])
    out['tricks_stored'] = sum(1 for r in rec if r['trick'] and (r.get('checked') or life['mode'] == 'ungated'))
    out['final_before_tricked'] = _median(r['miss_before'] for r in _stage(rec, FINAL)
                                          if (r['kind'], r['scene']) in tricked)
    spring_use = []
    for r in _stage(rec, SWINGS):
        origins = r.get('law_origins', [])
        if 'spring' in origins and r.get('theta_sd'):
            j = origins.index('spring')
            spring_use.append(abs(r['theta'][j]) / max(r['theta_sd'][j], 1e-9))
    out['spring_law_strength_in_swings'] = _median(spring_use)
    return out


def discoveries(life):
    first = {}
    for r in life['records']:
        first.setdefault(r['stage'], r['episode'])
    looks = {law['name']: law['looks_like'] for law in life['laws']}
    found = []
    for e in life['events']:
        if e['what'] != 'law kept for life':
            continue
        name = e['detail'].split(',')[0]
        found.append({'law': name, 'stage': e['stage'], 'after_situations': e['episode'] - first[e['stage']] + 1,
                      **looks.get(name, {})})
    return found


def _fmt(values, digits=3):
    values = [v for v in values if v is not None]
    if not values:
        return '-'
    mean = statistics.fmean(values)
    if len(values) == 1:
        return f'{mean:.{digits}f}'
    return f'{mean:.{digits}f} ({min(values):.{digits}f} to {max(values):.{digits}f})'


def write_report(root, folder='results'):
    out = Path(root) / folder
    lives = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(out.glob('life-*.json'))]
    stats = {}
    for life in lives:
        stats.setdefault(life['mode'], []).append(per_life(life))
    modes = [m for m in ORDER if m in stats]
    seeds = sorted({life['seed'] for life in lives})

    def col(mode, key, digits=3):
        return _fmt([s[key] for s in stats.get(mode, [])], digits)

    lines = ['# ccops5 lab results', '',
             f'Lives: seeds {seeds}. Each number is the average over seeds of that life\'s median, '
             'with the lowest and highest seed in brackets.',
             'A miss of 0 is a perfect guess of where the thing goes; 1 is as bad as guessing it never moves.', '']
    if 'full' in stats:
        lines += ['## The connected learner, stage by stage', '',
                  '| Stage | Guess before touching | Guess after its own pushes | Pushes used | Situations that checked out |',
                  '|---|---|---|---|---|']
        for i, name in enumerate(W.STAGES):
            lines.append(f"| {name} | {col('full', f'before_{i}')} | {col('full', f'after_{i}')} | "
                         f"{col('full', f'pushes_{i}', 2)} | {col('full', f'checked_{i}', 2)} |")
        lines += ['', '## What it discovered by itself', '',
                  'Depends on: the inputs the learner chose for the law. Most like: which hidden shape the new '
                  'part of the law resembles (correlation), judged only for this report.', '',
                  '| Seed | Law | Kept during | Situations of that stage before keeping it | Depends on | Most like |',
                  '|---|---|---|---|---|---|']
        for life in lives:
            if life['mode'] != 'full':
                continue
            for d in discoveries(life):
                lines.append(f"| {life['seed']} | {d['law']} | {d['stage']} | {d['after_situations']} | "
                             f"{', '.join(d.get('depends_on', []))} | {d.get('best', '-')} ({d.get('score', 0):.3f}) |")
        lines += ['', f"Law proposals in all: {col('full', 'proposals', 1)}; rejected by the check: "
                      f"{col('full', 'rejected', 1)}.", '']
    lines += ['## Switching one connection off at a time', '',
              '| Learner | What changed | Stages 1-5, guess before touching | Stages 1-5, after pushes | '
              'Final check, before touching | New toys from words | Stuck triples, before touching | Laws kept |',
              '|---|---|---|---|---|---|---|---|']
    for m in modes:
        lines.append(f"| {m} | {MEANING[m]} | {col(m, 'learning_before')} | {col(m, 'learning_after')} | "
                     f"{col(m, 'final_before')} | {col(m, 'words_guess')} | {col(m, 'stuck_triples_before')} | "
                     f"{col(m, 'laws_kept', 1)} |")
    if 'full' in stats:
        lines += ['', '## Words it was never told the meaning of', '',
                  '| New toy, never touched before | Miss |', '|---|---|',
                  f"| Guess from the place alone | {col('full', 'place_guess')} |",
                  f"| Guess from the caretaker's words | {col('full', 'words_guess')} |"]
        if 'baseline' in stats:
            lines.append(f"| Ordinary network, given the same words | {col('baseline', 'words_guess')} |")
        lines += ['', '## Math and proof: toys stuck together', '',
                  'Every rule it imagined, judged against what really happened to stuck toys:', '',
                  '| Rule it imagined | Miss when used to guess stuck toys |', '|---|---|']
        for name in RULES:
            lines.append(f"| {name} | {_fmt([s['rule_misses'][name] for s in stats['full']])} |")
        lines += ['', '| Learner | Rule it kept | Stuck situations it needed | Pairs, before touching | '
                      'Triples (never seen), before touching |', '|---|---|---|---|---|']
        for m in modes:
            rules = sorted({str(s['rule']) for s in stats[m]})
            lines.append(f"| {m} | {', '.join(rules)} | {col(m, 'rule_after', 1)} | "
                         f"{col(m, 'stuck_pairs_before')} | {col(m, 'stuck_triples_before')} |")
        lines += ['', f"Full learner, stuck toys: guess from the place average {col('full', 'stuck_place')}, "
                      f"worked out from its parts {col('full', 'stuck_worked_out')}.", '',
                  '## Springs and swings: one law, two looks', '',
                  '| Learner | New laws proposed during swings | Swings, after pushes | '
                  'Spring law strength inside swings (coefficient / uncertainty) |', '|---|---|---|---|']
        for m in ('full', 'no_reuse'):
            if m in stats:
                lines.append(f"| {m} | {col(m, 'swing_proposals', 1)} | {col(m, 'swing_after')} | "
                             f"{col(m, 'spring_law_strength_in_swings', 1)} |")
        lines += ['', '## Contradictions: someone secretly bumps the toy', '',
                  '| Learner | Bumped situations | Bumped situations stored as knowledge | Memories corrected | '
                  'Final check on bumped toys, before touching |', '|---|---|---|---|---|']
        for m in ('full', 'ungated'):
            if m in stats:
                lines.append(f"| {m} | {col(m, 'tricks', 1)} | {col(m, 'tricks_stored', 1)} | "
                             f"{col(m, 'corrections', 1)} | {col(m, 'final_before_tricked')} |")
    (out / 'TABLES.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    summary = {m: stats[m] for m in modes}
    (out / 'summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    return out / 'TABLES.md'
