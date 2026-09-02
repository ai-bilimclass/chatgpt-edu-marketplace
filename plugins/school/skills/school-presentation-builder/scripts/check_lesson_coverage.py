#!/usr/bin/env python3
"""Check lesson-component coverage in visible PPTX text and speaker notes."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

TEXT_TAG = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"

LABELS = {
    "criteria": r"критери|дескриптор|критерий|табыс критерий|success criter|descriptor",
    "task": r"тапсырма|задани|task|instruction|нұсқаулық|инструкц",
    "assessment": r"бағалау|форматив|оцениван|feedback|assessment|өзін.?өзі|взаимооцен",
    "support": r"қолдау|поддержк|scaffold|support|подсказк|үлгі|образец",
    "extension": r"күрделен|усложнен|challenge|extension|дополнительн|тереңдет",
    "time": r"\b\d{1,3}\s*(?:мин|minute|min\b)|уақыт\s*:|время\s*:|time\s*:",
    "homework": r"үй\s+тапсырмасы|домашн\w*\s+задани|homework|home\s+task",
    "sources": r"\[sources\]|дереккөз|источник|source\s*:",
    "answer": r"күтілетін\s+жауап|ожидаем\w*\s+ответ|answer\s+key|ключ\s*:",
}


def normalize(value: str) -> str:
    return re.sub(r"[^\w]+", " ", value.casefold(), flags=re.UNICODE).strip()


def extract_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        members = [
            name
            for name in archive.namelist()
            if re.match(r"ppt/(?:slides/slide\d+|notesSlides/notesSlide\d+)\.xml$", name)
        ]
        parts: list[str] = []
        for member in members:
            try:
                root = ET.fromstring(archive.read(member))
            except ET.ParseError as exc:
                raise RuntimeError(f"invalid XML in {member}: {exc}") from exc
            parts.extend(node.text or "" for node in root.iter(TEXT_TAG))
    return "\n".join(parts)


def load_plan(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read plan JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("plan JSON root must be an object")
    return data


def contains_phrase(haystack: str, phrase: str) -> bool:
    needle = normalize(phrase)
    if not needle:
        return True
    return needle in haystack


def check_plan(text: str, plan: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    normalized = normalize(text)

    topic = plan.get("topic", "")
    if topic and not contains_phrase(normalized, str(topic)):
        errors.append("exact lesson topic is not covered")

    fields = {
        "objectives": "objective",
        "success_criteria": "success criterion",
        "required_tasks": "required task",
        "assessment": "assessment item",
        "homework": "homework item",
    }
    for key, label in fields.items():
        values = plan.get(key, [])
        if values is None:
            continue
        if not isinstance(values, list):
            errors.append(f"plan field {key} must be a list")
            continue
        for index, value in enumerate(values, start=1):
            if value and not contains_phrase(normalized, str(value)):
                errors.append(f"missing {label} {index}: {value}")

    duration = plan.get("duration_minutes")
    if duration is not None:
        try:
            duration_value = int(duration)
        except (TypeError, ValueError):
            errors.append("duration_minutes must be an integer")
        else:
            minute_values = [
                int(x)
                for x in re.findall(
                    r"(?:уақыт|время|time)\s*:\s*(\d{1,3})\s*(?:мин|minute|min\b)",
                    text,
                    re.I,
                )
            ]
            if minute_values and sum(minute_values) != duration_value:
                warnings.append(
                    f"sum of explicit minute values is {sum(minute_values)}, plan duration is {duration_value}"
                )
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check pedagogical coverage in a PPTX")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--plan-json", type=Path, required=True)
    args = parser.parse_args()

    if not args.pptx.is_file() or not args.plan_json.is_file():
        print("ERROR: PPTX or plan JSON file not found", file=sys.stderr)
        return 2
    try:
        text = extract_text(args.pptx)
        plan = load_plan(args.plan_json)
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors, warnings = check_plan(text, plan)
    for field, pattern in LABELS.items():
        if not re.search(pattern, text, re.I):
            errors.append(f"missing lesson component: {field}")

    for error in dict.fromkeys(errors):
        print(f"ERROR: {error}")
    for warning in dict.fromkeys(warnings):
        print(f"WARNING: {warning}")
    if errors:
        return 1
    print("PASS: required lesson components and plan items are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
