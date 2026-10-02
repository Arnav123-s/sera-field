import argparse
import json
import math
from pathlib import Path


CHECK_NAMES = ('C1', 'C6', 'C8', 'C10', 'C11', 'T5')


def _read_json(path):
    with path.open(encoding='utf-8') as stream:
        return json.load(stream)


def _fmt(value, digits=2):
    if value is None:
        return 'n/a'
    return f'{value:.{digits}f}'


def _share(numerator, denominator):
    return numerator / denominator if denominator else None


def _files(folder, pattern):
    return sorted(Path(folder).glob(pattern), key=lambda p: p.name)


def _checks(item):
    return item.get('checks', item)


def _check_summary(detail, name):
    if name == 'C1':
        return f"coverage={_fmt(detail.get('coverage'), 3)}"
    if name == 'C6':
        shares = detail.get('sure_share') or {}
        strongest = next(iter(shares.values()), None)
        return f"not_vacuous={detail.get('not_vacuous', 'n/a')}; strongest_share={_fmt(strongest, 3)}"
    if name == 'C8':
        return f"alarm_rate={_fmt(detail.get('alarm_rate'), 3)}; eligible_worlds={detail.get('eligible_worlds', 'n/a')}"
    if name == 'C11':
        accepted = detail.get('forgeries_accepted')
        return f"forgeries_accepted={len(accepted) if isinstance(accepted, list) else 'n/a'}"
    if name == 'T5':
        return (f"rate={_fmt(detail.get('rate'), 3)}; eligible={detail.get('eligible', 'n/a')}; "
                f"grown_right={detail.get('grown_right', 'n/a')}; noise_growth={detail.get('noise_growth', 'n/a')}")
    return ''


def _m1a_section(folders):
    out = ['## M1a checks', '']
    found = False
    for folder in folders:
        # whole-seed files only; core_check also saves one part file per check (core_check_seed1.C1.pass1.json)
        paths = [p for p in _files(folder, 'core_check_seed*.json') if p.stem.removeprefix('core_check_seed').isdigit()]
        if not paths:
            continue
        found = True
        seeds = [(p, _read_json(p)) for p in paths]
        checks = [name for name in CHECK_NAMES if any(name in _checks(item) for _, item in seeds)]
        out.extend([f'### {Path(folder).name}', '', '| Seed | ' + ' | '.join(checks) + ' | Key numbers |',
                    '|---|' + '|'.join('---' for _ in checks) + '|---|'])
        wrong_total = 0
        for path, item in seeds:
            data = _checks(item)
            statuses, summaries = [], []
            for name in checks:
                row = data.get(name)
                statuses.append(('PASS' if row.get('pass') else 'FAIL') if row is not None else 'n/a')
                if row is None:
                    continue
                detail = row.get('detail') or {}
                summary = _check_summary(detail, name)
                if summary:
                    summaries.append(f'{name}: {summary}')
                if name in ('C6', 'C8', 'T5'):
                    wrong_total += detail.get('sure_and_wrong', 0) or 0
            out.append(f"| {path.stem.removeprefix('core_check_seed')} | " + ' | '.join(statuses) +
                       f" | {'; '.join(summaries) or 'n/a'} |")
        out.extend([f'\nTotal sure-and-wrong (C6, C8, T5): {wrong_total}', ''])
        if 'T5' in checks:
            out.extend(['### T5 worlds', '', '| Seed | Kind | Effect | Alarm | Invented | Accepted | Right | Own pushes |',
                        '|---|---|---:|---|---|---|---|---:|'])
            for path, item in seeds:
                rows = ((_checks(item).get('T5', {}).get('detail') or {}).get('worlds') or [])
                for row in rows:
                    out.append(f"| {path.stem.removeprefix('core_check_seed')} | {row.get('kind', 'n/a')} | "
                               f"{_fmt(row.get('effect'), 3)} | {row.get('alarm', 'n/a')} | {row.get('invented') or 'n/a'} | "
                               f"{row.get('accepted', 'n/a')} | {row.get('right', 'n/a')} | {row.get('own_pushes', 'n/a')} |")
            out.append('')
    return out if found else ['## M1a checks', '', 'No M1a check files found; section skipped.', '']


def _school_section(folder):
    paths = _files(folder, 'life-seed*.json')
    if not paths:
        return ['## School by arm', '', 'No School life files found; section skipped.', '',
                '## Alone-phase slope', '', 'No School life files found; section skipped.', '']
    lives = [_read_json(p) for p in paths]
    arms = {}
    for life in lives:
        arms.setdefault(life.get('arm_name', 'unknown'), []).append(life)
    out = ['## School by arm', '', '| Arm | Lives | Worlds | Certified right (count/share) | Sure-and-wrong | Mean rank taught | Mean rank alone | Mean rank exam | Never-shown exam right-first | Word-only exam right-first: words / no words | Grounded words/life | Mean minutes/life |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for arm in sorted(arms):
        group = arms[arm]
        worlds = [w for life in group for w in life.get('worlds', [])]
        right = sum(bool(w.get('correct')) for w in worlds)
        wrong = sum(bool(w.get('sure_and_wrong')) for w in worlds)
        def phase_mean(phase):
            vals = [w['rank'] for w in worlds if w.get('phase') == phase and isinstance(w.get('rank'), (int, float))]
            return _fmt(sum(vals) / len(vals) if vals else None)
        never_exam = [w for w in worlds if w.get('phase') == 'exam' and w.get('never_shown')]
        never_share = _share(sum(w.get('rank') == 1 for w in never_exam), len(never_exam))
        word_exam = [w for w in worlds if w.get('phase') == 'exam' and w.get('word_only') and
                     not w.get('never_shown') and w.get('kind') in {'rubbing', 'spring', 'water drag', 'swing', 'dry friction', 'stiff spring'}]
        word_share = _share(sum(w.get('rank') == 1 for w in word_exam), len(word_exam))
        no_word_share = _share(sum(w.get('rank_no_words') == 1 for w in word_exam), len(word_exam))
        grounded = [len(l.get('lexicon', {}).get('grounded', [])) for l in group]
        minutes = [l['minutes'] for l in group if isinstance(l.get('minutes'), (int, float))]
        out.append(f"| {arm} | {len(group)} | {len(worlds)} | {right}/{_fmt(_share(right, len(worlds)), 3)} | {wrong} | "
                   f"{phase_mean('taught')} | {phase_mean('alone')} | {phase_mean('exam')} | {_fmt(never_share, 3)} | "
                   f"{_fmt(word_share, 3)} / {_fmt(no_word_share, 3)} | "
                   f"{_fmt(sum(grounded) / len(grounded) if grounded else None)} | {_fmt(sum(minutes) / len(minutes) if minutes else None)} |")
    out.extend(['', '## Alone-phase slope', '', '| Arm | Slope | Standard error |', '|---|---:|---:|'])
    for arm in sorted(arms):
        points = []
        for life in arms[arm]:
            selected = [w for w in life.get('worlds', []) if w.get('phase') == 'alone' and
                        isinstance(w.get('n'), (int, float)) and isinstance(w.get('rank'), (int, float))]
            mean = sum(w['rank'] for w in selected) / len(selected) if selected else None
            if mean is not None:
                points.extend((w['n'], w['rank'] - mean) for w in selected)
        if len(points) > 1:
            xs, ys = zip(*points)
            xbar, ybar = sum(xs) / len(xs), sum(ys) / len(ys)
            sxx = sum((x - xbar) ** 2 for x in xs)
            slope = sum((x - xbar) * (y - ybar) for x, y in points) / sxx if sxx else 0.0
            residual = sum((y - slope * (x - xbar) - ybar) ** 2 for x, y in points)
            se = math.sqrt((residual / max(len(points) - 2, 1)) / sxx) if sxx else 0.0
        else:
            slope = se = None
        out.append(f'| {arm} | {_fmt(slope, 3)} | {_fmt(se, 3)} |')
    out.append('')
    return out


def build_report(m1a_folders, school_folder):
    return '\n'.join(_m1a_section(m1a_folders) + _school_section(school_folder)).rstrip() + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--m1a', nargs='+', required=True)
    parser.add_argument('--school', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    report = build_report(args.m1a, args.school)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding='utf-8')
    print(report, end='')


if __name__ == '__main__':
    main()
