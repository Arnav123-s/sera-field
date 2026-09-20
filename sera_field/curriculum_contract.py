"""Source-attributed, group-separated teaching views. Raw originals stay unchanged."""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .records import sha256, write_json


@dataclass(frozen=True)
class Lesson:
    identity: str
    source_sha256: str
    source_record: str
    origin: str
    subject: str
    group: str
    prompt: str
    teacher: dict
    qualification: str

    def validate(self):
        if len(self.source_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.source_sha256):
            raise ValueError("Exact source SHA-256 required")
        if self.origin not in {"human", "simulation", "engineered_practice"}:
            raise ValueError("Keep human source and constructed experience distinct")
        if not all((self.identity, self.source_record, self.subject, self.group, self.prompt, self.qualification)):
            raise ValueError("Lesson provenance and scope required")


def assigned_split(group, salt="CONNECTED-002-human-groups-v1"):
    fraction = int(hashlib.sha256((salt + "\n" + group).encode()).hexdigest()[:8], 16) % 10000
    return "train" if fraction < 8000 else "development" if fraction < 9000 else "sealed"


def freeze_lessons(lessons, output):
    output = Path(output)
    # A repeat must choose a new study identity, never silently replace an evaluation.
    output.mkdir(parents=True, exist_ok=False)
    handles = {split: (output / (split + ".jsonl")).open("x", encoding="utf-8")
               for split in ("train", "development", "sealed")}
    counts, groups, seen, rejected = {}, {}, {}, []
    try:
        for lesson in lessons:
            lesson.validate()
            content = hashlib.sha256(" ".join(lesson.prompt.split()).casefold().encode()).hexdigest()
            split = assigned_split(lesson.group)
            if lesson.identity in seen:
                raise ValueError("Duplicate lesson identity")
            if content in seen:
                # Keep the exclusion receipt, never move an alias across a partition.
                rejected.append({"identity": lesson.identity, "reason": "duplicate normalized prompt",
                                 "first": seen[content]})
                continue
            seen[lesson.identity] = seen[content] = lesson.identity
            groups[lesson.group] = split
            counts.setdefault(lesson.subject, {s: 0 for s in handles})[split] += 1
            handles[split].write(json.dumps({**asdict(lesson), "split": split}, ensure_ascii=False) + "\n")
    finally:
        for handle in handles.values():
            handle.close()
    manifest = {"schema": "sera-field.curriculum.1", "counts": counts, "group_counts": {
        split: sum(s == split for s in groups.values()) for split in handles},
        "files": {split: {"path": split + ".jsonl", "sha256": sha256(output / (split + ".jsonl"))}
                  for split in handles}, "excluded_duplicates": rejected,
        "final_labels_opened_for_training": False, "new_model_training_performed": False,
        "qualification": "Human teaching references; source-specific independent task checks still required."}
    write_json(output / "MANIFEST.json", manifest)
    return manifest


def teaching_records(root):
    root = Path(root)
    manifest = json.loads((root / "MANIFEST.json").read_text())
    path = root / "train.jsonl"
    if sha256(path) != manifest["files"]["train"]["sha256"]:
        raise ValueError("Teaching source changed after freeze")
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record["split"] != "train":
                raise ValueError("Evaluation record in teaching file")
            yield record
