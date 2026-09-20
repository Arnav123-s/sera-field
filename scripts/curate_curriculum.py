"""Preserve human-source identity and inspect training records before teaching.

This performs intake validation, not model training. Official evaluation problem
bodies are not selected for inspection, execution, or teaching.
"""

import ast
from collections import Counter
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calculate(expression):
    """Evaluate only small literal arithmetic from a supplied worked solution."""
    tree = ast.parse(expression.replace(",", ""), mode="eval")
    if len(list(ast.walk(tree))) > 64:
        raise ValueError("Expression exceeds the inspection bound")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            result = Fraction(str(node.value))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            result = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                result = left + right
            elif isinstance(node.op, ast.Sub):
                result = left - right
            elif isinstance(node.op, ast.Mult):
                result = left * right
            elif isinstance(node.op, ast.Div):
                result = left / right
            elif isinstance(node.op, ast.Pow) and right.denominator == 1 and abs(right) <= 6:
                result = left ** int(right)
            else:
                raise ValueError("Unsupported arithmetic operator")
        else:
            raise ValueError("Only literal arithmetic is admitted")
        if abs(result) > 10 ** 12 or result.denominator > 10 ** 12:
            raise ValueError("Arithmetic exceeds the inspection bound")
        return result

    return visit(tree)


def main():
    if not os.environ.get("SERA_FIELD_SUPERVISED"):
        raise RuntimeError("Use scripts/supervise.py for the bounded inspection")
    out = Path(os.environ["SERA_FIELD_ATTEMPT"])
    manifest = json.loads((ROOT / "local/MULTIDOMAIN_REMOTE_INTAKE.json").read_text())
    records = {r["source_path"]: r for r in manifest if "local_path" in r}
    math_record, code_record = records["grade_school_math/data/train.jsonl"], records["mbpp/mbpp.jsonl"]
    for record in (math_record, code_record):
        assert sha(Path(record["local_path"])) == record["sha256"]
    math_counts, code_counts = Counter(), Counter()
    math_issues, code_issues, selected_code_ids = [], [], []
    with (out / "eligible-math.jsonl").open("w", encoding="utf-8") as admitted:
        for index, line in enumerate(Path(math_record["local_path"]).read_text(encoding="utf-8").splitlines()):
            row = json.loads(line)
            math_counts["human_training_records"] += 1
            annotations = re.findall(r"<<([^<>]+)>>", row["answer"])
            problems, checked = [], 0
            for annotation in annotations:
                try:
                    expression, expected = annotation.rsplit("=", 1)
                    actual, expected_value = calculate(expression), calculate(expected)
                    checked += 1
                    if actual != expected_value:
                        problems.append({"annotation": annotation, "computed": str(actual),
                                         "stated": str(expected_value), "reason": "not exact; may be a stated approximation"})
                except (SyntaxError, ValueError, TypeError, ZeroDivisionError) as error:
                    problems.append({"annotation": annotation, "reason": str(error)})
            math_counts["arithmetic_annotations_checked"] += checked
            if "####" not in row["answer"] or not annotations:
                problems.append({"reason": "Missing final answer marker or calculation annotations"})
            if problems:
                math_counts["records_held_for_review"] += 1
                math_issues.append({"training_line": index + 1, "issues": problems})
            else:
                math_counts["records_with_exact_checked_annotations"] += 1
                admitted.write(json.dumps({"source_sha256": math_record["sha256"],
                                           "source_line": index + 1, "record": row,
                                           "qualification": "Literal annotations checked; word-problem interpretation not independently certified"}) + "\n")
    with (out / "candidate-code.jsonl").open("w", encoding="utf-8") as admitted:
        for line in Path(code_record["local_path"]).read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            identity = row["task_id"]
            if not 601 <= identity <= 974:
                code_counts["nontraining_records_skipped"] += 1
                continue
            code_counts["human_training_records"] += 1
            selected_code_ids.append(identity)
            try:
                tree = ast.parse(row["code"])
                tests = [ast.parse(test) for test in row["test_list"]]
                assert tests and all(any(isinstance(n, ast.Assert) for n in ast.walk(t)) for t in tests)
                code_counts["syntax_and_assertion_structure_valid"] += 1
                admitted.write(json.dumps({"source_sha256": code_record["sha256"], "task_id": identity,
                                           "record": row, "qualification": "Parsed only; reference program and tests not executed or independently certified"}) + "\n")
            except (SyntaxError, AssertionError) as error:
                code_counts["records_held_for_review"] += 1
                code_issues.append({"task_id": identity, "reason": str(error)})
    report = {"status": "intake inspected; model training not started", "math": dict(math_counts),
              "coding": dict(code_counts), "source_ids": {"math": math_record["sha256"], "coding": code_record["sha256"]},
              "preserved_issues": {"math": math_issues, "coding": code_issues},
              "selected_coding_training_ids": selected_code_ids,
              "code_executed": False, "model_weights_updated": False,
              "official_math_test_downloaded": False, "coding_evaluation_bodies_selected_for_inspection": False,
              "public_raw_redistribution": False}
    (out / "intake-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "math", "coding", "code_executed", "model_weights_updated")}, indent=2))


if __name__ == "__main__":
    main()
