"""Observer life ledger. No grades, generators, or runner clocks enter SERA."""
import hashlib
import json
import os
from pathlib import Path
import time


def atomic_json(path, value):
    pending = path.with_name(path.name+'.pending')
    with pending.open('w', encoding='utf-8') as fh:
        json.dump(value, fh, sort_keys=True, indent=2, allow_nan=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(pending, path)


class Life:
    def __init__(self, directory):
        self.root = Path(directory)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root/'sera.pt'
        self.ledger_path = self.root/'life.json'
        self.ledger = json.loads(self.ledger_path.read_text(encoding='utf-8')) if self.ledger_path.exists() else dict(
            schema='u14-life-1', born=False, sessions=[], exam_asked=[])
        if self.ledger.get('schema') != 'u14-life-1':
            raise ValueError('Unknown life ledger')

    def open(self, factory, *, carry=False):
        from .mind import SeraU
        if not self.path.exists():
            if self.ledger['born'] or self.ledger['sessions']:
                raise ValueError('Life checkpoint missing; refusing a second birth')
            return factory(), None
        parent = hashlib.sha256(self.path.read_bytes()).hexdigest()
        mind = SeraU.carry(self.path) if carry else SeraU.load(self.path)
        return mind, parent

    def begin(self, mind, work, parent, *, session=None):
        session = session or str(len(self.ledger['sessions'])+1)
        existing = next((s for s in self.ledger['sessions'] if s['id'] == session), None)
        if existing is not None:
            if existing['package'] != mind.code or existing['parent_digest'] != parent:
                raise ValueError('Changed life session parent/package')
            return existing
        row = dict(id=session, start=time.time(), start_work=0 if mind.clock_mode == 'wall' else mind.clock.count,
            work_allowance=work, work_done=0, package=mind.code, parent_digest=parent,
            questions_asked=[], forks={}, status='open', carry=getattr(mind, 'carry_manifest', None))
        self.ledger['sessions'].append(row)
        # A stop before the first teaching unit must still leave the original
        # newborn, rather than a ledger which cannot safely be opened again.
        if not self.path.exists():
            self.ledger['checkpoint_digest'] = mind.save(self.path)
        atomic_json(self.ledger_path, self.ledger)
        return row

    def born(self, mind):
        """Called only after the teaching cursor finishes, once per life."""
        self.ledger['born'] = True
        self.path.parent.mkdir(parents=True, exist_ok=True)
        sha = mind.save(self.path)
        self.ledger['checkpoint_digest'] = sha
        atomic_json(self.ledger_path, self.ledger)

    def save_birth(self, mind, cursor):
        if self.ledger['born']:
            raise ValueError('A living SERA is never bootstrapped again')
        self.ledger.update(birth_index=cursor, checkpoint_digest=mind.save(self.path))
        atomic_json(self.ledger_path, self.ledger)

    def fork_path(self, session, arm):
        if any(not part or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in part)
               for part in (session, arm)):
            raise ValueError('Invalid life fork identity')
        path = self.root/'forks'/(session+'-'+arm)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def finish_arm(self, row, mind, records, *, complete):
        path = self.fork_path(row['id'], mind.arm)
        sha = mind.save(path/'sera.pt')
        atomic_json(path/'records.json', records)
        row['forks'][mind.arm] = dict(parent_digest=row.get('fork_parent_digest', row['parent_digest']), final_digest=sha,
                                     learned_digest=mind.learning_hash(), complete=complete)
        if mind.arm == 'full':
            current = mind.save(self.path)
            self.ledger['checkpoint_digest'] = current
            row['work_done'] = max(0, mind.clock.count-row['start_work']) if mind.clock_mode == 'work' else 0
        atomic_json(self.ledger_path, self.ledger)

    def checkpoint(self, row, mind):
        """The full branch is the current living mind at every safe boundary."""
        if mind.arm != 'full':
            return
        self.ledger['checkpoint_digest'] = mind.save(self.path)
        row['work_done'] = max(0, mind.clock.count-row['start_work']) if mind.clock_mode == 'work' else 0
        atomic_json(self.ledger_path, self.ledger)

    def finish(self, row, status):
        row.update(status=status, end=time.time())
        atomic_json(self.ledger_path, self.ledger)
