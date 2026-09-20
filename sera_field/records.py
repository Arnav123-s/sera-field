"""Atomic records and content identities; no external project imports."""

import hashlib
import json
from pathlib import Path
import time


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def source_manifest(root):
    root = Path(root)
    paths = [*root.glob("sera_field/*.py"), *root.glob("scripts/*.py"),
             *root.glob("tests/*.py"), *root.glob("protocols/*"), root / "pyproject.toml"]
    return {path.relative_to(root).as_posix(): sha256(path) for path in sorted(paths)}
