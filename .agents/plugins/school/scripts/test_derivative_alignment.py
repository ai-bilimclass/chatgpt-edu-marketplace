#!/usr/bin/env python3
"""Integration and negative tests for KSP derivative alignment."""

from __future__ import annotations

import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path


SCHOOL = Path(__file__).resolve().parents[1]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ALIGN = load(Path(__file__).with_name("validate_derivative_alignment.py"), "validate_derivative_alignment")
KSP = load(
    SCHOOL / "skills" / "school-lesson-planner" / "secondary" / "scripts" / "build_ksp.py",
    "build_ksp_for_integration",
)


class DerivativeAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.ksp = KSP.validate_input(KSP.example(test_fixture=True))
        self.handoff = ALIGN.handoff_from_ksp(self.ksp, "lesson-linear-function-v1")

    def derivative(self, artifact_type: str):
        id_field = ALIGN.ARTIFACT_ID_FIELD[artifact_type]
        return {
            "artifact_type": artifact_type,
            "source_lesson_content_version": self.handoff["lesson_content_version"],
            "items": [
                {
                    "canonical_task_id": task["canonical_task_id"],
                    id_field: f"{artifact_type}-item-{index:02d}",
                    "descriptor": task["descriptor"],
                }
                for index, task in enumerate(self.handoff["canonical_tasks"], start=1)
            ],
        }

    def test_ksp_handoff_worksheet_presentation_chain(self):
        worksheet = ALIGN.validate_alignment(self.handoff, self.derivative("worksheet"))
        presentation = ALIGN.validate_alignment(self.handoff, self.derivative("presentation"))
        self.assertEqual("PASS", worksheet["status"])
        self.assertEqual("PASS", presentation["status"])
        self.assertEqual(3, worksheet["mapped_canonical_tasks"])
        self.assertEqual(3, presentation["mapped_canonical_tasks"])

    def test_descriptor_drift_is_rejected(self):
        derivative = self.derivative("worksheet")
        derivative["items"][0]["descriptor"] += " Изменено."
        with self.assertRaisesRegex(ALIGN.AlignmentError, "Descriptor drift"):
            ALIGN.validate_alignment(self.handoff, derivative)

    def test_missing_canonical_task_is_rejected(self):
        derivative = self.derivative("presentation")
        derivative["items"].pop()
        with self.assertRaisesRegex(ALIGN.AlignmentError, "missing canonical tasks"):
            ALIGN.validate_alignment(self.handoff, derivative)

    def test_unknown_canonical_task_is_rejected(self):
        derivative = self.derivative("worksheet")
        derivative["items"][0]["canonical_task_id"] = "task-unknown"
        with self.assertRaisesRegex(ALIGN.AlignmentError, "Unknown canonical_task_id"):
            ALIGN.validate_alignment(self.handoff, derivative)

    def test_stale_content_version_is_rejected(self):
        derivative = self.derivative("presentation")
        derivative["source_lesson_content_version"] = "lesson-linear-function-v0"
        with self.assertRaisesRegex(ALIGN.AlignmentError, "stale or different"):
            ALIGN.validate_alignment(self.handoff, derivative)

    def test_legacy_handoff_cannot_claim_strict_alignment(self):
        handoff = deepcopy(self.handoff)
        handoff["schema_version"] = "2.0"
        handoff["validation_status"] = "legacy_unverified"
        with self.assertRaisesRegex(ALIGN.AlignmentError, "strict handoff schema 3.0"):
            ALIGN.validate_alignment(handoff, self.derivative("worksheet"))


if __name__ == "__main__":
    unittest.main()
