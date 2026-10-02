"""Adversarial checks of bookkeeping; no model imports or numerical workload."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_core022_course import (check_rows, identity, rank, receipt_chain,
    receipt_prefix, safe_child, source_metadata, SPLIT_KEY, validate_indices)


class CourseReceiptAuditTests(unittest.TestCase):
    def test_receipt_order_and_source_substitution_are_rejected(self):
        layout = [{'cursor': 1, 'kind': 'semantic', 'batch': 2,
                   'bank': 'semantic', 'indices': [4, 7]}]
        sources = {'semantic': {4: {'id': 'first', 'group': 'a', 'track': 'semantic'},
                                7: {'id': 'second', 'group': 'b', 'track': 'semantic'}}}
        rows = [{'cursor': 1, 'kind': 'semantic', 'ids': ['first', 'second'],
                 'loss': 1., 'gradient_norm': 2., 'update_wall_seconds': 3.}]
        result = check_rows(layout, sources, rows)
        self.assertEqual(result['distinct_human_source_groups'], 2)
        self.assertEqual(result['presentations'], {'semantic': 2})
        for change in ({'ids': ['second', 'first']}, {'ids': ['first', 'reserved']},
                       {'cursor': 2}, {'kind': 'programs'}, {'loss': float('nan')},
                       {'gradient_norm': -1.}):
            tampered = [{**rows[0], **change}]
            with self.subTest(change=change), self.assertRaises(ValueError):
                check_rows(layout, sources, tampered)

    def test_durable_prefix_excludes_failed_tail_and_partial_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / 'updates-a.jsonl'
            line1 = (json.dumps({'cursor': 1}) + '\n').encode()
            first.write_bytes(line1 + (json.dumps({'cursor': 2, 'failed_unsaved_tail': True}) + '\n').encode())
            second = root / 'updates-b.jsonl'
            second.write_bytes((json.dumps({'cursor': 2}) + '\n').encode() + b'{"cursor":3')
            entry = {'file': first.name, 'bytes': len(line1), 'sha256': hashlib.sha256(line1).hexdigest()}
            (root / 'RESUME-b.json').write_text(json.dumps({'prior_receipts': [entry]}))
            rows, prefixes = receipt_chain(root, second.name, 2)
            self.assertEqual(rows, [{'cursor': 1}, {'cursor': 2}])
            self.assertEqual(prefixes[0], entry)
            with self.assertRaises(ValueError):
                receipt_prefix(second, limit=second.stat().st_size)
            first.write_bytes(line1.replace(b'1', b'0') + b'preserved tail\n')
            with self.assertRaises(ValueError):
                receipt_chain(root, second.name, 2)

    def test_cross_partition_index_and_reserved_group_are_rejected(self):
        pools = {'semantic': {'train': {'semantic': [0]},
                              'development': {'semantic': []}, 'final': {'semantic': [1]}}}
        validate_indices(pools)
        crossed = copy.deepcopy(pools)
        crossed['semantic']['final']['semantic'] = [0]
        with self.assertRaises(ValueError):
            validate_indices(crossed)
        train = next(str(i) for i in range(100) if int(rank(SPLIT_KEY, str(i))[:8], 16) % 20 >= 2)
        reserved = next(str(i) for i in range(100) if int(rank(SPLIT_KEY, str(i))[:8], 16) % 20 < 2)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'source.jsonl'
            # The reserved line is deliberately invalid JSON. A teaching audit
            # must hash its bytes but never parse that reserved record.
            path.write_bytes((json.dumps({'id': 'human', 'group': train}) + '\n').encode() + b'reserved not opened\n')
            manifest = {'files': {'semantic': {'path': path.name,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}}}
            actual = source_metadata(root, manifest, pools, {'semantic': {0}})
            self.assertEqual(actual['semantic'][0]['id'], 'human')
            with self.assertRaises(ValueError):
                source_metadata(root, manifest, pools, {'semantic': {1}})
            path.write_text(json.dumps({'id': 'leaked', 'group': reserved}) + '\n')
            manifest['files']['semantic']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                source_metadata(root, manifest, pools, {'semantic': {0}})

    def test_mixed_identity_includes_original_human_and_episode_number(self):
        layout = [{'cursor': 1, 'kind': 'mixed', 'batch': 1, 'bank': 'semantic',
                   'indices': [0], 'numbers': [6]}]
        sources = {'semantic': {0: {'id': 'human', 'group': 'g', 'track': 'semantic'}}}
        rows = [{'cursor': 1, 'kind': 'mixed',
                 'ids': [identity(['CORE-022-mixed-teaching', 'human', 6])],
                 'loss': 0., 'gradient_norm': 0., 'update_wall_seconds': .1}]
        self.assertEqual(check_rows(layout, sources, rows)['presentations'], {'mixed': 1})
        rows[0]['ids'] = [identity(['CORE-022-mixed-teaching', 'human', 7])]
        with self.assertRaises(ValueError):
            check_rows(layout, sources, rows)
        with tempfile.TemporaryDirectory() as temporary, self.assertRaises(ValueError):
            safe_child(Path(temporary), '../escape')


if __name__ == '__main__':
    unittest.main()
