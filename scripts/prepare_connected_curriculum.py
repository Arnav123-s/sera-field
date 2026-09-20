"""Build immutable human teaching/development/sealed views without model training."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.curriculum_contract import Lesson, freeze_lessons
from sera_field.records import sha256


def lines(path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            yield json.loads(line)


def normalized_hash(text):
    return hashlib.sha256(" ".join(text.split()).casefold().encode()).hexdigest()


def examples(source_lab, originals):
    math_source = source_lab / "intake/multidomain-sources/openai_grade-school-math_grade_school_math_data_train.jsonl"
    code_source = source_lab / "intake/multidomain-sources/google-research_google-research_mbpp_mbpp.jsonl"
    expected = [(math_source, "17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465"),
                (code_source, "ccf64ceae9c5403bf50a044cb6d505bfd2a2963ee58338ba268fd65beab92a9f")]
    for path, digest in expected:
        if sha256(path) != digest:
            raise ValueError("Original source identity changed: " + str(path))
    original_math = list(lines(math_source))
    original_code = {record["task_id"]: record for record in lines(code_source)}
    for row in lines(source_lab / "runs/curriculum-intake-001/eligible-math.jsonl"):
        raw = row["record"]
        if raw != original_math[row["source_line"] - 1] or row["source_sha256"] != expected[0][1]:
            raise ValueError("Mathematics view no longer matches its original source")
        yield Lesson("gsm8k-train-" + str(row["source_line"]), row["source_sha256"], str(row["source_line"]),
                     "human", "mathematics", "math-" + normalized_hash(raw["question"]), raw["question"],
                     {"worked_solution": raw["answer"]}, row["qualification"])
    for row in lines(source_lab / "runs/curriculum-intake-001/candidate-code.jsonl"):
        raw = row["record"]
        if raw != original_code[row["task_id"]] or row["source_sha256"] != expected[1][1] or not 601 <= row["task_id"] <= 974:
            raise ValueError("Programming view no longer matches the official training source")
        yield Lesson("mbpp-train-" + str(row["task_id"]), row["source_sha256"], str(row["task_id"]),
                     "human", "programming", "code-" + normalized_hash(raw["code"]), raw["text"],
                     {"reference_program": raw["code"], "tests": raw["test_list"],
                      "setup": raw.get("test_setup_code", "")}, row["qualification"])
    squad = originals / "runs/HR-corpus/raw/train-v1.1.json"
    digest = "3527663986b8295af4f7fcdff1ba1ff3f72d07d61a20f487cb238a6ef92fd955"
    if sha256(squad) != digest:
        raise ValueError("Human reading source identity changed")
    for article in json.loads(squad.read_text(encoding="utf-8"))["data"]:
        group = "squad-article-" + normalized_hash(article["title"])
        for paragraph in article["paragraphs"]:
            for qa in paragraph["qas"]:
                yield Lesson("squad-train-" + qa["id"], digest, qa["id"], "human", "language_reading",
                             group, paragraph["context"] + "\n\n" + qa["question"],
                             {"answers": qa["answers"], "question": qa["question"],
                              "context_length": len(paragraph["context"])},
                             "Human extractive annotations; a correct span alone is not a semantic situation assessment.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-lab", type=Path, default=ROOT)
    parser.add_argument("--originals", type=Path, default=Path("D:/ai/projects/sera"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = freeze_lessons(examples(args.source_lab, args.originals), args.output)
    print(json.dumps({"output": str(args.output), "counts": manifest["counts"],
                      "groups": manifest["group_counts"], "excluded": len(manifest["excluded_duplicates"])}, indent=2))


if __name__ == "__main__":
    main()
