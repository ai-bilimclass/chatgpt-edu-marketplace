"""Primary-school entry point using the shared scored lesson DOCX pipeline."""

import importlib.util
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / "secondary/scripts/build_ksp.py"
SPEC = importlib.util.spec_from_file_location("primary_shared_ksp", PATH)
SHARED = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SHARED)


def validate_input(data):
    if str(data.get("grade")) not in {"1", "2", "3", "4"}:
        raise ValueError("Primary route requires grade 1–4")
    return SHARED.validate_input(data)


def build(data, output):
    return SHARED.build(validate_input(data), output)


if __name__ == "__main__":
    import json
    import sys
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(build(data, Path(sys.argv[2])))
