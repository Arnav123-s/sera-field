"""scripts/sera_grades.py: every verdict on a hand-made unit, the part score, and the card counts."""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts' / 'sera_grades.py'
spec = importlib.util.spec_from_file_location('sera_grades', SCRIPT)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

TRUTH = 'straight with speed + bell3 of position times bell2 of speed'


def unit(world, claim, sure, checker_ok=True):
    t, c = G.terms(TRUTH), G.terms(claim)
    return dict(world=world, truth=TRUTH, claim=claim, sure=sure, right=c == t, contradicted=sure and not c <= t,
                checker_ok=checker_ok if sure else None, scope={'x': [-1, 1], 'v': [-2, 2]}, throws=12, cpu=3.0)


def test_every_verdict_and_the_parts():
    cases = {'proven right': unit('a', TRUTH, True),
             'proven, part': unit('b', 'straight with speed', True),
             'right, unsure': unit('c', TRUTH, False),
             'unsure, wrong': unit('d', 'straight with position', False),
             'SURE AND WRONG': unit('e', 'straight with position + straight with speed', True),
             'checker refused': unit('f', TRUTH, True, checker_ok=False)}
    for verdict, u in cases.items():
        assert G.grade_unit(u)['verdict'] == verdict, verdict
    g = G.grade_unit(cases['SURE AND WRONG'])
    assert g['right_terms'] == ['straight with speed']
    assert g['missing_terms'] == ['bell3 of position times bell2 of speed']
    assert g['extra_terms'] == ['straight with position']
    assert g['part_score'] == round(1 / 3, 3)
    assert G.grade_unit(cases['proven right'])['part_score'] == 1.0


def test_the_card_counts_what_the_files_hold(tmp_path):
    arm = tmp_path / 'universe-1'
    arm.mkdir()
    for u in (unit('a', TRUTH, True), unit('c', TRUTH, False), unit('d', 'straight with position', False)):
        (arm / f'{u["world"]}.json').write_text(json.dumps(u))
    (arm / 'a.claim').write_text('')                                    # queue claims are not units
    card = G.grade_folder(tmp_path)
    assert '| proven right | 1 |' in card and '| right, unsure | 1 |' in card and '| unsure, wrong | 1 |' in card
    assert sorted(p.name for p in (tmp_path / 'grades' / 'universe-1').iterdir()) == ['a.json', 'c.json', 'd.json']
    assert (tmp_path / 'grades' / 'CARD.md').exists()
