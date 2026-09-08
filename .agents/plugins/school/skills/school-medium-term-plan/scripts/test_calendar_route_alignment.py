#!/usr/bin/env python3
"""Integration checks for the shared primary/secondary KTP calendar route."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CALENDAR_REFERENCE = "references/calendar/official-holidays-2026-2027.json"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from calendar_contract import apply_calendar_contract


def load_route_test(mode: str):
    script_dir = SCRIPTS / mode
    test_path = script_dir / "test_generate_ktp_docx.py"
    previous = sys.modules.pop("generate_ktp_docx", None)
    sys.path.insert(0, str(script_dir))
    try:
        spec = importlib.util.spec_from_file_location(f"{mode}_ktp_test_support", test_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load {test_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(script_dir))
        sys.modules.pop("generate_ktp_docx", None)
        if previous is not None:
            sys.modules["generate_ktp_docx"] = previous


PRIMARY = load_route_test("primary")
SECONDARY = load_route_test("secondary")


class CalendarRouteAlignmentTest(unittest.TestCase):
    def test_both_modes_explicitly_route_to_shared_calendar(self):
        for mode_name in ("primary-mode.md", "secondary-mode.md"):
            mode_text = (ROOT / "references" / mode_name).read_text(encoding="utf-8")
            self.assertIn(CALENDAR_REFERENCE, mode_text)

    def test_primary_and_secondary_validators_load_identical_base_calendar(self):
        primary_data = PRIMARY.make_data(1)
        secondary_data = SECONDARY.make_data(1)
        PRIMARY.validate(primary_data)
        SECONDARY.validate(secondary_data)
        self.assertEqual(primary_data["public_holidays"], secondary_data["public_holidays"])
        self.assertEqual(primary_data["non_instruction_dates"], secondary_data["non_instruction_dates"])
        self.assertTrue(primary_data["calendar_source_complete"])
        self.assertTrue(secondary_data["calendar_source_complete"])

    def test_grade_one_extra_break_is_added_only_by_primary_contract(self):
        data = PRIMARY.make_data(1)
        data["grade"] = 1
        apply_calendar_contract(data)
        extra_break = {f"2027-02-{day:02d}" for day in range(8, 15)}
        self.assertTrue(extra_break.issubset(set(data["non_instruction_dates"])))
        secondary_data = SECONDARY.make_data(1)
        apply_calendar_contract(secondary_data)
        self.assertTrue(extra_break.isdisjoint(set(secondary_data["non_instruction_dates"])))

    def test_teacher_calendar_cannot_replace_builtin_dates(self):
        data = SECONDARY.make_data(1)
        data["teacher_calendar_additions"].append({
            "date": "2026-12-16",
            "name": "Попытка замены встроенной даты",
        })
        with self.assertRaisesRegex(ValueError, "must not replace a built-in date"):
            SECONDARY.validate(data)

    def test_calendar_conflict_stops_both_routes(self):
        for support in (PRIMARY, SECONDARY):
            data = support.make_data(1)
            data["calendar_conflicts"] = [{
                "date": "2026-12-16",
                "builtin_value": "неучебный день",
                "teacher_value": "учебный день",
            }]
            with self.assertRaisesRegex(ValueError, "requires teacher clarification"):
                support.validate(data)


if __name__ == "__main__":
    unittest.main()
