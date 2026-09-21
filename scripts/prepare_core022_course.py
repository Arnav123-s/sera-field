"""Allocate new untouched source groups before complete-core teaching."""
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.core_course_data import prepare

if __name__ == '__main__':
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the numerical resource supervisor')
    print(json.dumps(prepare(), indent=2))
