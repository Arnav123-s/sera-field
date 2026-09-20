"""Prepare human episode views by identities/text only, without model evaluation."""
from collections import defaultdict
import hashlib
import heapq
import json
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, write_json

DATA = ROOT / 'local/SEMANTIC-015-data-v1'
OUT = ROOT / 'local/HISTORY-016-data-v1'


def priority(prefix, identity):
    return hashlib.sha256((prefix + identity).encode()).hexdigest()


def stream(split):
    with (DATA / (split + '.jsonl')).open(encoding='utf-8') as handle:
        for line in handle:
            yield json.loads(line)


def terms(row):
    return set(re.findall(r'[a-z]+', (row['premise'] + ' ' + row['hypothesis']).lower()))


def build(split, count, *, excluded_groups=()):
    best = {}; excluded = set(excluded_groups)
    for row in stream(split):
        group = row['source_group']
        if group in excluded:
            continue
        key = priority('HISTORY-016-query-row', row['id'])
        if group not in best or key < best[group][0]:
            best[group] = (key, row['id'])
    groups = sorted(best, key=lambda group: priority('HISTORY-016-query-group', group))[:count]
    query_ids = {best[group][1] for group in groups}; query_groups = set(groups)
    queries = {}; heap = []
    for row in stream(split):
        if row['id'] in query_ids:
            queries[row['source_group']] = row
        elif row['source_group'] not in excluded | query_groups:
            key = int(priority('HISTORY-016-support-pool', row['id']), 16)
            heapq.heappush(heap, (-key, row['id'], row))
            if len(heap) > 8192:
                heapq.heappop(heap)
    pool = [row for _, _, row in sorted(heap, reverse=True)]
    pool_terms = [terms(row) for row in pool]
    if len(pool) < 64:
        raise ValueError('Preserve source separation; insufficient support pool')
    episodes = []
    for group in groups:
        query = queries[group]; query_terms = terms(query)
        rng = random.Random(int(priority('HISTORY-016-neighbors', query['id']), 16))
        candidates = rng.sample(range(len(pool)), 64)
        candidates.sort(key=lambda i: (-len(query_terms & pool_terms[i]) / max(1, len(query_terms | pool_terms[i])), pool[i]['id']))
        chosen = []; used = set()
        for i in candidates:
            row = pool[i]
            if row['source_group'] in used or (row['premise'], row['hypothesis']) == (query['premise'], query['hypothesis']):
                continue
            chosen.append(row); used.add(row['source_group'])
            if len(chosen) == 4:
                break
        if len(chosen) != 4:
            raise ValueError('Not enough independent source groups in the fixed candidate pool')
        episodes.append({'id': priority('HISTORY-016-episode', query['id']), 'query': query,
                         'supports': chosen, 'selection': 'label-free lexical overlap among 64 fixed candidate rows'})
    return episodes


def main():
    if OUT.exists():
        raise ValueError('Preserve the existing episode preparation; do not overwrite')
    # This exactly mirrors the prior prospective ID selection. Labels are never
    # consulted in the query or support selection operations above or here.
    reserved = heapq.nsmallest(4096, ((priority('SEMANTIC-015-final', r['id']), r['id'], r['source_group']) for r in stream('sealed')))
    excluded = {r[2] for r in reserved}
    prepared = {'train': build('train', 2048), 'development': build('development', 128),
                'sealed': build('sealed', 256, excluded_groups=excluded)}
    OUT.mkdir(parents=True)
    manifest = {'source_manifest_sha256': sha256(DATA / 'MANIFEST.json'),
        'script_sha256': sha256(__file__), 'previous_final_ids': [r[1] for r in reserved],
        'previous_final_source_groups': sorted(excluded), 'partitions': {},
        'label_use_for_selection': False, 'license': 'CC BY-SA 4.0; Bowman et al., SNLI 1.0'}
    all_groups = {}
    for split, episodes in prepared.items():
        path = OUT / (split + '.jsonl')
        path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in episodes), encoding='utf-8')
        query_groups = {r['query']['source_group'] for r in episodes}
        support_groups = {s['source_group'] for r in episodes for s in r['supports']}
        if query_groups & support_groups:
            raise ValueError('Support and query source groups overlap')
        all_groups[split] = query_groups | support_groups
        manifest['partitions'][split] = {'episodes': len(episodes), 'sha256': sha256(path),
            'query_groups': sorted(query_groups), 'support_groups': sorted(support_groups),
            'query_ids': [r['query']['id'] for r in episodes],
            'support_unique_ids': sorted({s['id'] for r in episodes for s in r['supports']}),
            'support_presentations': len(episodes) * 4}
    for one, two in (('train', 'development'), ('train', 'sealed'), ('development', 'sealed')):
        if all_groups[one] & all_groups[two]:
            raise ValueError('Partition source groups overlap')
    if all_groups['sealed'] & excluded:
        raise ValueError('Do not reuse a prior opened final group')
    write_json(OUT / 'MANIFEST.json', manifest)
    print(json.dumps({key: {'episodes': value['episodes'], 'supports': len(value['support_unique_ids'])}
                      for key, value in manifest['partitions'].items()}))


if __name__ == '__main__':
    main()
