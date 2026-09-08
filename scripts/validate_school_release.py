#!/usr/bin/env python3
"""Run all school plugin tests and verify its two published copies are identical."""

from __future__ import annotations

import filecmp
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "plugins" / "school"
MIRROR = ROOT / ".agents" / "plugins" / "school"


def compare_trees(left: Path, right: Path) -> list[str]:
    comparison = filecmp.dircmp(left, right)
    failures = [f"only in primary: {name}" for name in comparison.left_only]
    failures += [f"only in mirror: {name}" for name in comparison.right_only]
    failures += [f"type mismatch: {name}" for name in comparison.common_funny]
    failures += [f"content differs: {name}" for name in comparison.common_files if not filecmp.cmp(left / name, right / name, shallow=False)]
    for name in comparison.common_dirs:
        failures += [f"{name}/{item}" for item in compare_trees(left / name, right / name)]
    return failures


def main() -> int:
    failures = compare_trees(PRIMARY, MIRROR)
    if failures:
        print("Plugin mirrors are not identical:\n- " + "\n- ".join(failures), file=sys.stderr)
        return 2
    tests = sorted(PRIMARY.rglob("test_*.py"))
    env = os.environ.copy()
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    for test in tests:
        print(f"RUN {test.relative_to(ROOT)}", flush=True)
        result = subprocess.run([sys.executable, str(test)], cwd=ROOT, env=env)
        if result.returncode:
            return result.returncode
    print(f"PASS: mirrors identical; {len(tests)} test files passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
