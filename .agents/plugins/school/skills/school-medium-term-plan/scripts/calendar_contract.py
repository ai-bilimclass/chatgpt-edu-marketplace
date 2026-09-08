#!/usr/bin/env python3
"""Deterministic calendar loading for both KTP generators."""

from __future__ import annotations

import copy
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
BUILTIN_CALENDAR_PATH = (
    SKILL_ROOT / "references" / "calendar" / "official-holidays-2026-2027.json"
)
EXTERNAL_URL = re.compile(r"(?:https?://|www\.)", re.IGNORECASE)
ALLOWED_CALENDAR_SOURCE_TYPES = {
    "builtin_approved_calendar_2026_2027",
    "builtin_with_teacher_additions",
}


def _reject_external_urls(value: Any, path: str = "builtin_calendar") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold() in {"url", "source_url", "external_url"}:
                raise ValueError(f"External URL fields are forbidden in the built-in KTP calendar: {path}.{key}")
            _reject_external_urls(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_external_urls(child, f"{path}[{index}]")
    elif isinstance(value, str) and EXTERNAL_URL.search(value):
        raise ValueError(f"External URLs are forbidden in the built-in KTP calendar: {path}")


def load_builtin_calendar() -> dict[str, Any]:
    if not BUILTIN_CALENDAR_PATH.is_file():
        raise ValueError("Built-in approved calendar is missing; request a source from the teacher and stop generation")
    payload = json.loads(BUILTIN_CALENDAR_PATH.read_text(encoding="utf-8"))
    _reject_external_urls(payload)
    if str(payload.get("academic_year", "")).replace("-", "–") != "2026–2027":
        raise ValueError("Built-in calendar must cover the 2026–2027 academic year")
    holidays = payload.get("public_holidays")
    exclusions = payload.get("non_instruction_dates")
    if not isinstance(holidays, list) or not isinstance(exclusions, list):
        raise ValueError("Built-in calendar requires public_holidays and non_instruction_dates")
    holiday_dates = [str(item.get("date", "")) for item in holidays if isinstance(item, dict)]
    if len(holiday_dates) != len(holidays) or len(holiday_dates) != len(set(holiday_dates)):
        raise ValueError("Built-in calendar contains invalid or duplicate public holiday dates")
    if any(date.fromisoformat(value).isoformat() != value for value in holiday_dates + list(exclusions)):
        raise ValueError("Built-in calendar dates must use YYYY-MM-DD")
    if not set(holiday_dates).issubset(set(exclusions)):
        raise ValueError("Every built-in public holiday must be a non-instruction date")
    return payload


def apply_calendar_contract(data: dict[str, Any]) -> None:
    """Load the approved base calendar and merge verified teacher additions."""
    source_type = data.get("calendar_source_type")
    if source_type not in ALLOWED_CALENDAR_SOURCE_TYPES:
        raise ValueError(
            "calendar_source_type must use the built-in approved calendar, "
            "optionally with verified teacher additions"
        )

    builtin = load_builtin_calendar()
    holidays = copy.deepcopy(builtin["public_holidays"])
    exclusions = list(builtin["non_instruction_dates"])
    pending = {
        str(item.get("name", "")).strip()
        for item in builtin.get("pending_variable_holidays", [])
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    }

    additions = data.get("teacher_calendar_additions", [])
    teacher_exclusions = data.get("teacher_non_instruction_dates", [])
    conflicts = data.get("calendar_conflicts", [])
    if not isinstance(additions, list) or not isinstance(teacher_exclusions, list):
        raise ValueError("Teacher calendar additions must be lists")
    if not isinstance(conflicts, list):
        raise ValueError("calendar_conflicts must be a list")
    if conflicts:
        raise ValueError("Calendar source conflict requires teacher clarification before KTP generation")

    if source_type == "builtin_with_teacher_additions":
        if not str(data.get("teacher_calendar_file", "")).strip():
            raise ValueError("teacher_calendar_file must identify the calendar file uploaded by the teacher")
        resolved_pending: set[str] = set()
        known_dates = {str(item["date"]) for item in holidays}
        for item in additions:
            if not isinstance(item, dict) or not str(item.get("name", "")).strip():
                raise ValueError("Every teacher calendar addition requires date and name")
            item_date = date.fromisoformat(str(item.get("date", ""))).isoformat()
            if item_date in known_dates:
                raise ValueError("Teacher calendar additions must not replace a built-in date")
            resolves_pending = str(item.get("resolves_pending", "")).strip()
            if resolves_pending:
                if resolves_pending not in pending:
                    raise ValueError("Teacher calendar addition resolves an unknown pending item")
                resolved_pending.add(resolves_pending)
            holidays.append(copy.deepcopy(item))
            known_dates.add(item_date)
            exclusions.append(item_date)
        pending -= resolved_pending
        for value in teacher_exclusions:
            normalized = date.fromisoformat(str(value)).isoformat()
            if normalized not in exclusions:
                exclusions.append(normalized)
    elif additions or teacher_exclusions or str(data.get("teacher_calendar_file", "")).strip():
        raise ValueError("Teacher calendar data requires calendar_source_type builtin_with_teacher_additions")

    if pending:
        names = ", ".join(sorted(pending))
        raise ValueError(
            f"Missing mandatory calendar data for {names}; request a source from the teacher and stop generation"
        )

    if int(data.get("grade", 0)) == 1:
        for day in range(8, 15):
            extra_break_date = f"2027-02-{day:02d}"
            if extra_break_date not in exclusions:
                exclusions.append(extra_break_date)

    data["calendar_verified"] = True
    data["calendar_source_complete"] = True
    data["calendar_source"] = "builtin_approved_calendar_2026_2027"
    if source_type == "builtin_with_teacher_additions":
        data["calendar_source"] += f" + {str(data['teacher_calendar_file']).strip()}"
    data["public_holidays"] = holidays
    data["non_instruction_dates"] = exclusions
