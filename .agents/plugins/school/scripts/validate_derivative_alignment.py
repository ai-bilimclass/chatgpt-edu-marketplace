#!/usr/bin/env python3
"""Validate KSP 3.0 handoff alignment with worksheet or presentation manifests."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


class AlignmentError(ValueError):
    pass


ARTIFACT_ID_FIELD = {"worksheet": "worksheet_task_id", "presentation": "slide_id"}


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AlignmentError(f"{field} must be non-empty text.")
    return value.strip()


def handoff_from_ksp(ksp: dict[str, Any], lesson_content_version: str) -> dict[str, Any]:
    """Create the strict handoff subset used by derivative builders."""
    if str(ksp.get("schema_version", "")) != "3.0":
        raise AlignmentError("Only a validated KSP schema 3.0 can create a strict handoff.")
    if ksp.get("validation_status") != "strict":
        raise AlignmentError("KSP validation_status must be strict.")
    canonical_tasks = []
    for stage in ksp.get("stages", []):
        for task in stage.get("tasks", []):
            canonical_tasks.append({
                "canonical_task_id": _text(task.get("canonical_task_id"), "canonical_task_id"),
                "objective_refs": deepcopy(task.get("objective_refs", [])),
                "instruction": _text(task.get("instruction"), "instruction"),
                "expected_product": _text(task.get("expected_product"), "expected_product"),
                "descriptor": _text(task.get("descriptor"), "descriptor"),
                "feedback": _text(task.get("feedback"), "feedback"),
            })
    if not canonical_tasks:
        raise AlignmentError("Strict handoff requires at least one canonical task.")
    ids = [task["canonical_task_id"] for task in canonical_tasks]
    if len(ids) != len(set(ids)):
        raise AlignmentError("Strict handoff contains duplicate canonical_task_id values.")
    return {
        "schema_version": "3.0",
        "lesson_content_version": _text(lesson_content_version, "lesson_content_version"),
        "ready_for_derivatives": True,
        "validation_status": "strict",
        "canonical_tasks": canonical_tasks,
    }


def validate_alignment(handoff: dict[str, Any], derivative: dict[str, Any]) -> dict[str, Any]:
    if handoff.get("schema_version") != "3.0" or handoff.get("validation_status") != "strict":
        raise AlignmentError("Derivative validation requires a strict handoff schema 3.0.")
    if handoff.get("ready_for_derivatives") is not True:
        raise AlignmentError("Handoff is not ready for derivative materials.")
    artifact_type = derivative.get("artifact_type")
    if artifact_type not in ARTIFACT_ID_FIELD:
        raise AlignmentError("artifact_type must be worksheet or presentation.")
    source_version = _text(derivative.get("source_lesson_content_version"), "source_lesson_content_version")
    if source_version != handoff.get("lesson_content_version"):
        raise AlignmentError("Derivative uses a stale or different lesson_content_version.")
    source_tasks = handoff.get("canonical_tasks")
    items = derivative.get("items")
    if not isinstance(source_tasks, list) or not isinstance(items, list) or not items:
        raise AlignmentError("canonical_tasks and derivative items must be non-empty lists.")
    canonical = {task.get("canonical_task_id"): task for task in source_tasks}
    if None in canonical or len(canonical) != len(source_tasks):
        raise AlignmentError("Handoff canonical task IDs must be present and unique.")
    seen: set[str] = set()
    id_field = ARTIFACT_ID_FIELD[artifact_type]
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise AlignmentError(f"Derivative item {index} must be an object.")
        task_id = _text(item.get("canonical_task_id"), f"items[{index}].canonical_task_id")
        _text(item.get(id_field), f"items[{index}].{id_field}")
        if task_id in seen:
            raise AlignmentError(f"Duplicate derivative mapping for {task_id}.")
        seen.add(task_id)
        if task_id not in canonical:
            raise AlignmentError(f"Unknown canonical_task_id in derivative: {task_id}")
        descriptor = _text(item.get("descriptor"), f"items[{index}].descriptor")
        if descriptor != canonical[task_id].get("descriptor"):
            raise AlignmentError(f"Descriptor drift detected for {task_id}.")
    missing = sorted(set(canonical) - seen)
    if missing:
        raise AlignmentError("Derivative is missing canonical tasks: " + ", ".join(missing))
    return {
        "status": "PASS",
        "artifact_type": artifact_type,
        "source_lesson_content_version": source_version,
        "mapped_canonical_tasks": len(seen),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON with lesson_plan_handoff and derivative")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(validate_alignment(payload["lesson_plan_handoff"], payload["derivative"]), ensure_ascii=False, indent=2))
        return 0
    except (AlignmentError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
