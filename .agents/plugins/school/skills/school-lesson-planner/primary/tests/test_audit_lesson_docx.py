#!/usr/bin/env python3
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_lesson_docx", SKILL_ROOT / "scripts" / "audit_lesson_docx.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""


def make_docx(path: Path, body: str) -> None:
    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}</w:body></w:document>'''
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", RELS)
        archive.writestr("word/document.xml", document)


def p(text: str) -> str:
    return f'<w:p><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr><w:t>{text}</w:t></w:r></w:p>'


def row(*cells: str) -> str:
    padded = list(cells) + [""] * (5 - len(cells))
    return "<w:tr>" + "".join(f"<w:tc>{p(cell)}</w:tc>" for cell in padded) + "</w:tr>"


class AuditTests(unittest.TestCase):
    def test_valid_plan_has_no_errors(self):
        body = "".join([
            p("Цели обучения: 2.1.2.3 использовать данные"),
            p("Цели урока: ученик классифицирует данные"),
            p("Критерии оценивания"), p("Дескриптор"), p("Обратная связь"),
            p("Ход урока"),
            "<w:tbl>" + row("Начало 5 мин", "Действия") + row("Основная часть 30 мин", "Задание") + row("Рефлексия 5 мин", "Доказательство достижения цели") + "</w:tbl>",
        ])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "valid.docx"
            make_docx(path, body)
            findings = MODULE.audit(path, 40, False)
        self.assertFalse([item for item in findings if item.level == "ERROR"])

    def test_invalid_plan_reports_core_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.docx"
            make_docx(path, p("Тема урока"))
            findings = MODULE.audit(path, 40, False)
        codes = {item.code for item in findings if item.level == "ERROR"}
        self.assertTrue({"LEARNING_OBJECTIVE", "LESSON_OBJECTIVE", "LESSON_FLOW", "OBJECTIVE_CODE", "TIME_NOT_FOUND", "CLOSURE"}.issubset(codes))

    def test_wrong_font_and_size_are_errors(self):
        body = '<w:p><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr><w:t>Тема урока</w:t></w:r></w:p>'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "wrong-typography.docx"
            make_docx(path, body)
            findings = MODULE.audit(path, 40, False)
        codes = {item.code for item in findings if item.level == "ERROR"}
        self.assertTrue({"TYPOGRAPHY_FONT", "TYPOGRAPHY_SIZE"}.issubset(codes))

    def test_combined_plan_requires_rotation(self):
        body = "".join([
            p("1 класс 2 класс"), p("Цели обучения 1.1.1.1"), p("Цели урока"), p("Ход урока"), p("Итог: достижение цели"),
            "<w:tbl>" + row("40 мин", "Работа") + "</w:tbl>",
        ])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "combined.docx"
            make_docx(path, body)
            findings = MODULE.audit(path, 40, True)
        self.assertIn("COMBINED_ROTATION", {item.code for item in findings if item.level == "ERROR"})

    def test_time_mismatch_is_error(self):
        body = "".join([
            p("Цели обучения: 3.1.1.1"), p("Цели урока"), p("Ход урока"), p("Итог: достижение цели"),
            "<w:tbl>" + row("Начало 5 мин", "Работа") + row("Основная часть 20 мин", "Работа") + row("Итог 5 мин", "Проверка") + "</w:tbl>",
        ])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "wrong-time.docx"
            make_docx(path, body)
            findings = MODULE.audit(path, 40, False)
        self.assertIn("TIME_TOTAL", {item.code for item in findings if item.level == "ERROR"})

    def test_kazakh_headings_are_recognized(self):
        body = "".join([
            p("Оқу мақсаты: 2.1.2.3"), p("Сабақ мақсаты"), p("Бағалау критерийлері"),
            p("Дескриптор"), p("Кері байланыс"), p("Сабақ барысы"),
            "<w:tbl>" + row("Басы 5 минут", "Әрекет") + row("Ортасы 30 минут", "Тапсырма") + row("Қорытынды 5 минут", "Мақсатқа жетуді тексеру") + "</w:tbl>",
            p("Әдістемелік қосымша"),
            p("Оқу мақсаты мен сабақ тақырыбы арқылы дамитын білім мен дағдылар"),
        ])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "kazakh.docx"
            make_docx(path, body)
            findings = MODULE.audit(path, 40, False)
        self.assertFalse([item for item in findings if item.level == "ERROR"])

    def test_kazakh_old_appendix_labels_are_errors(self):
        body = "".join([
            p("Оқу мақсаты: 2.1.2.3"), p("Сабақ мақсаты"), p("Бағалау критерийлері"),
            p("Дескриптор"), p("Кері байланыс"), p("Сабақ барысы"),
            "<w:tbl>" + row("Басы 5 минут", "Әрекет") + row("Ортасы 30 минут", "Тапсырма") + row("Қорытынды 5 минут", "Мақсатқа жетуді тексеру") + "</w:tbl>",
            p("Ескерту: «Бағалау критерийлері» — әдістемелік қосымша өріс."),
            p("САБАҚ МАТЕРИАЛДАРЫ"),
        ])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "kazakh-old-labels.docx"
            make_docx(path, body)
            findings = MODULE.audit(path, 40, False)
        codes = {item.code for item in findings if item.level == "ERROR"}
        self.assertTrue({"KK_APPENDIX_OLD_TITLE", "KK_APPENDIX_TITLE", "KK_KNOWLEDGE_SKILLS_BLOCK", "KK_CRITERIA_NOTE"}.issubset(codes))


if __name__ == "__main__":
    unittest.main()
