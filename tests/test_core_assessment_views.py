"""Reserved-choice integrity without reading a corpus or importing a model."""
import copy
import unittest

from scripts.core022_assessment_views import choice_views, role, score_choices


class AssessmentViewTests(unittest.TestCase):
    def rows(self):
        groups = [str(i) for i in range(500) if role(str(i)) == 'final'][:4]
        return [{'id': 'record-' + str(i), 'group': group, 'track': 'fixture',
                 'question': 'Human question ' + str(i), 'answer': 'Answer ' + str(i)}
                for i, group in enumerate(groups)]

    def test_final_alternatives_use_other_groups_of_same_subject(self):
        rows = self.rows()
        views = choice_views(rows, partition='final')
        self.assertTrue(all(v['scored'] and len(v['options']) == 4 for v in views))
        self.assertEqual(views, choice_views(list(reversed(rows)), partition='final')[::-1])
        for view in views:
            for i, source in enumerate(view['option_sources']):
                if i != view['target']:
                    self.assertNotEqual(source['group'], view['group'])
        scored = score_choices(views, [v['target'] for v in views])
        self.assertTrue(all(case['correct'] and case['chance'] == .25 for case in scored))

    def test_one_choice_is_unscored_not_a_correct_answer(self):
        row = self.rows()[0]
        views = choice_views([row], partition='final')
        self.assertFalse(views[0]['scored'])
        record = score_choices(views, [None])[0]
        self.assertIsNone(record['correct'])
        self.assertIsNone(record['chance'])
        with self.assertRaises(ValueError):
            score_choices(views, [0])

    def test_partition_leak_duplicate_and_changed_view_fail(self):
        rows = self.rows()
        leaked = copy.deepcopy(rows)
        leaked[1]['group'] = next(str(i) for i in range(100) if role(str(i)) == 'train')
        with self.assertRaises(ValueError):
            choice_views(leaked, partition='final')
        with self.assertRaises(ValueError):
            choice_views([*rows, rows[0]], partition='final')
        views = choice_views(rows, partition='final')
        views[0]['options'][0] = 'Changed after prediction'
        with self.assertRaises(ValueError):
            score_choices(views, [v['target'] for v in views])

    def test_normalized_duplicate_or_other_subject_is_not_a_negative(self):
        rows = self.rows()
        rows[1]['answer'] = rows[0]['answer'] + '  '
        rows[2]['track'] = 'different subject'
        rows[3]['group'] = rows[0]['group']
        view = choice_views(rows, partition='final')[0]
        self.assertFalse(view['scored'])


if __name__ == '__main__':
    unittest.main()
