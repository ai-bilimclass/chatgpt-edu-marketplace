#!/usr/bin/env python3
"""Structural audit for Kazakhstan primary-school lesson-plan DOCX files."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from lesson_table_policy import contains_framework


@dataclass
class Finding:
    level: str
    code: str
    message: str


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def element_text(element: ET.Element) -> str:
    return normalize(" ".join(node.text or "" for node in element.findall(".//w:t", NS)))


def read_docx(path: Path) -> tuple[str, list[list[str]], list[str]]:
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        raise ValueError(f"не удалось прочитать DOCX: {exc}") from exc
    root = ET.fromstring(xml)
    paragraphs = [element_text(p) for p in root.findall(".//w:p", NS)]
    tables: list[list[str]] = []
    for table in root.findall(".//w:tbl", NS):
        for row in table.findall("./w:tr", NS):
            tables.append([element_text(cell) for cell in row.findall("./w:tc", NS)])
    return normalize("\n".join(filter(None, paragraphs))), tables, paragraphs


def audit_typography(path: Path) -> list[Finding]:
    """Require explicit Times New Roman 12 pt mappings in Word content/styles."""
    findings: list[Finding] = []
    font_values: list[str] = []
    size_values: list[str] = []
    font_attrs = {f"{{{NS['w']}}}{name}" for name in ("ascii", "hAnsi", "eastAsia", "cs")}
    value_attr = f"{{{NS['w']}}}val"
    try:
        with zipfile.ZipFile(path) as archive:
            # Audit rendered lesson content and inherited styles. Numbering/font-table
            # parts may legitimately use Symbol/Courier for marker glyph metadata and
            # do not control the plan or methodological-appendix text.
            members = [name for name in ("word/document.xml", "word/styles.xml") if name in archive.namelist()]
            for name in members:
                root = ET.fromstring(archive.read(name))
                for node in root.findall(".//w:rFonts", NS):
                    font_values.extend(value for key, value in node.attrib.items() if key in font_attrs)
                for tag in ("sz", "szCs"):
                    size_values.extend(
                        node.attrib[value_attr]
                        for node in root.findall(f".//w:{tag}", NS)
                        if value_attr in node.attrib
                    )
    except (zipfile.BadZipFile, ET.ParseError, OSError) as exc:
        return [Finding("ERROR", "TYPOGRAPHY_READ", f"Не удалось проверить типографику DOCX: {exc}")]

    bad_fonts = sorted({value for value in font_values if value.casefold() != "times new roman"})
    bad_sizes = sorted({value for value in size_values if value != "24"})
    if not font_values:
        findings.append(Finding("ERROR", "TYPOGRAPHY_FONT_MISSING", "В DOCX не закреплён шрифт Times New Roman на уровне стилей или фрагментов."))
    elif bad_fonts:
        findings.append(Finding("ERROR", "TYPOGRAPHY_FONT", f"Найдены шрифты, отличные от Times New Roman: {', '.join(bad_fonts)}."))
    if not size_values:
        findings.append(Finding("ERROR", "TYPOGRAPHY_SIZE_MISSING", "В DOCX не закреплён размер 12 pt на уровне стилей или фрагментов."))
    elif bad_sizes:
        findings.append(Finding("ERROR", "TYPOGRAPHY_SIZE", f"Найдены размеры, отличные от 12 pt: {', '.join(bad_sizes)} полупунктов."))
    return findings


def contains(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def extract_stage_minutes(rows: list[list[str]]) -> list[int]:
    values: list[int] = []
    minute_pattern = re.compile(r"(?<!\d)(\d{1,3})\s*(?:мин(?:ут[аы]?)?|мин\.?|minutes?|min\.?)(?!\w)", re.I)
    header_pattern = re.compile(r"время|уақыт|time|этап|кезең|stage", re.I)
    for cells in rows:
        joined = " | ".join(cells)
        if header_pattern.search(joined) and not minute_pattern.search(joined):
            continue
        candidates: list[int] = []
        for cell in cells[:2]:
            candidates.extend(int(match) for match in minute_pattern.findall(cell))
        if candidates:
            values.append(candidates[0])
    return values


def audit(path: Path, expected_minutes: int, combined: bool) -> list[Finding]:
    findings: list[Finding] = []
    text, rows, paragraphs = read_docx(path)
    for cells in rows:
        if len(cells) == 5 and extract_stage_minutes([cells]) and contains_framework(" ".join(cells)):
            findings.append(Finding("ERROR", "METHODOLOGY_IN_TEACHER_ACTIONS", "Перенесите название и объяснение методики в методическое приложение; в действиях учителя оставьте конкретный приём и вид работы."))
    findings.extend(audit_typography(path))
    lower = text.lower()

    required = {
        "LEARNING_OBJECTIVE": (
            [r"цели? обучения", r"оқу мақсат", r"learning objectives?"],
            "Не найден раздел с целью обучения.",
        ),
        "LESSON_OBJECTIVE": (
            [r"цели? урока", r"сабақ(?:тың)? мақсат", r"lesson objectives?"],
            "Не найден раздел с целями урока.",
        ),
        "LESSON_FLOW": (
            [r"ход урока", r"сабақ(?:тың)? барысы", r"lesson (?:procedure|progress|flow)"],
            "Не найден раздел с ходом урока.",
        ),
    }
    for code, (patterns, message) in required.items():
        if not contains(lower, patterns):
            findings.append(Finding("ERROR", code, message))

    if not re.search(r"\b\d+(?:\.\d+){2,4}[a-zа-яәіңғүұқөһ]?\b", lower, re.I):
        findings.append(Finding("ERROR", "OBJECTIVE_CODE", "Не найден код цели обучения."))

    if not contains(lower, [r"критери[ий].*оцен", r"бағалау критер", r"assessment criteria"]):
        findings.append(Finding("WARNING", "CRITERIA", "Не найдены явно обозначенные критерии оценивания."))
    if not contains(lower, [r"дескриптор", r"descriptor"]):
        findings.append(Finding("WARNING", "DESCRIPTORS", "Не найдены дескрипторы или эталон проверки."))
    if not contains(lower, [r"обратн.*связ", r"кері байланыс", r"feedback"]):
        findings.append(Finding("WARNING", "FEEDBACK", "Не обозначена формативная обратная связь."))

    stage_minutes = extract_stage_minutes(rows)
    if not stage_minutes:
        findings.append(Finding("ERROR", "TIME_NOT_FOUND", "Не удалось извлечь время этапов из первых двух колонок таблицы."))
    elif sum(stage_minutes) != expected_minutes:
        findings.append(Finding("ERROR", "TIME_TOTAL", f"Сумма времени этапов {sum(stage_minutes)} мин., ожидалось {expected_minutes} мин. Значения: {stage_minutes}."))

    if not any(len(row) == 5 for row in rows):
        findings.append(Finding("ERROR", "COMMON_KSP_TEMPLATE", "Не найдена общая пятиколоночная таблица хода урока: этап/время, педагог, ученик, оценивание, ресурсы."))

    empty_cells = sum(1 for row in rows for cell in row if not cell)
    if empty_cells:
        findings.append(Finding("WARNING", "EMPTY_CELLS", f"Обнаружены пустые ячейки таблиц: {empty_cells}. Проверить вручную."))

    if not contains(lower, [r"итог", r"рефлекси", r"қорытынды", r"рефлексия", r"reflection", r"plenary"]):
        findings.append(Finding("ERROR", "CLOSURE", "Не найден итоговый этап или рефлексия."))
    if not contains(lower, [r"достижен.*цел", r"достижени.*цел", r"мақсатқа жет", r"objective.*achiev"]):
        findings.append(Finding("WARNING", "GOAL_CHECK", "Не найден явный способ итоговой проверки достижения цели; одной эмоциональной рефлексии недостаточно."))
    if contains(lower, [r"шығу билеті", r"выходн(?:ой|ого) билет"]):
        findings.append(Finding("ERROR", "OLD_ENDING_TERM", "Заключительный этап должен называться «Рефлексия» / «Reflection»; прежние названия заключительного этапа не использовать."))

    is_kazakh_plan = contains(lower, [r"оқу мақсат", r"сабақ барысы"])
    if is_kazakh_plan:
        normalized_headings = {normalize(item).casefold() for item in paragraphs if item}
        if "сабақ материалдары" in normalized_headings:
            findings.append(Finding("ERROR", "KK_APPENDIX_OLD_TITLE", "После КСП не использовать заголовок «САБАҚ МАТЕРИАЛДАРЫ»; заменить его на «Әдістемелік қосымша»."))
        if "әдістемелік қосымша" not in normalized_headings:
            findings.append(Finding("ERROR", "KK_APPENDIX_TITLE", "Не найден обязательный заголовок приложения «Әдістемелік қосымша»."))
        if "оқу мақсаты мен сабақ тақырыбы арқылы дамитын білім мен дағдылар" not in normalized_headings:
            findings.append(Finding("ERROR", "KK_KNOWLEDGE_SKILLS_BLOCK", "Не найден отдельный блок знаний и навыков, реализуемых через цель обучения и тему урока."))
        if contains(lower, [r"ескерту:\s*«?бағалау критерийлері»?[^\n]{0,160}әдістемелік қосымша"]):
            findings.append(Finding("ERROR", "KK_CRITERIA_NOTE", "После поля «Бағалау критерийлері» не выводить пояснение о его методическом статусе."))

    if combined:
        class_mentions = set(re.findall(r"\b([1-4])\s*[-–]?\s*(?:класс|сынып|grade)\b", lower, re.I))
        if len(class_mentions) < 2:
            findings.append(Finding("ERROR", "COMBINED_CLASSES", "Для совмещённого урока не найдены две разные параллели."))
        if not contains(lower, [r"самостоятельн", r"өздік жұмыс", r"independent work"]):
            findings.append(Finding("ERROR", "COMBINED_ROTATION", "Не обозначена самостоятельная работа одного класса во время прямой работы учителя с другим."))

    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--minutes", type=int, required=True)
    parser.add_argument("--combined", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.minutes < 1:
        print("ERROR ARGUMENT: длительность должна быть положительной.")
        return 2
    if not args.docx.is_file():
        print(f"ERROR FILE: файл не найден: {args.docx}")
        return 2
    try:
        findings = audit(args.docx, args.minutes, args.combined)
    except ValueError as exc:
        print(f"ERROR DOCX: {exc}")
        return 2
    for item in findings:
        print(f"{item.level} {item.code}: {item.message}")
    errors = sum(item.level == "ERROR" for item in findings)
    warnings = sum(item.level == "WARNING" for item in findings)
    print(f"SUMMARY errors={errors} warnings={warnings}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
