from dataclasses import replace
import json

import pytest

from sera_field.curriculum_contract import Lesson, assigned_split, freeze_lessons, teaching_records


def lesson(identity, group, prompt):
    return Lesson(identity, "a" * 64, identity, "human", "language", group, prompt,
                  {"answer": "a supplied human answer"}, "Human teaching; independently assess capability")


def test_all_views_from_one_source_group_keep_one_partition(tmp_path):
    root = tmp_path / "fresh"
    records = [lesson(str(i), "same-human-article", "Question " + str(i)) for i in range(12)]
    result = freeze_lessons(records, root)
    split = assigned_split("same-human-article")
    assert result["counts"]["language"][split] == 12
    assert result["group_counts"][split] == 1
    with pytest.raises(FileExistsError):
        freeze_lessons(records, root)


def test_alias_cannot_cross_partition_and_raw_teacher_is_not_prompt(tmp_path):
    root = tmp_path / "fresh"
    records = [lesson("1", "group1", "Original question"), lesson("2", "group2", "ORIGINAL  QUESTION")]
    result = freeze_lessons(records, root)
    assert len(result["excluded_duplicates"]) == 1
    rows = [json.loads(line) for file in root.glob("*.jsonl") for line in file.read_text().splitlines()]
    assert len(rows) == 1 and "supplied human answer" not in rows[0]["prompt"]


def test_training_loader_detects_changes_and_rejects_evaluation(tmp_path):
    root = tmp_path / "fresh"
    freeze_lessons([lesson("1", "group1", "Original")], root)
    with (root / "train.jsonl").open("a") as handle:
        handle.write("{}\n")
    with pytest.raises(ValueError, match="changed"):
        list(teaching_records(root))


def test_human_and_simulated_provenance_cannot_be_collapsed():
    with pytest.raises(ValueError, match="distinct"):
        replace(lesson("1", "g", "Question"), origin="human-or-simulation").validate()
