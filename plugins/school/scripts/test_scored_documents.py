"""End-to-end DOCX checks for both age routes and all output languages."""

import importlib.util
import json
import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from build_linked_worksheet import KSP, build as worksheet, audit as audit_worksheet
from validate_derivative_alignment import handoff_from_ksp

PRIMARY_PATH = Path(__file__).resolve().parents[1] / "skills/school-lesson-planner/primary/scripts/build_ksp.py"
SPEC = importlib.util.spec_from_file_location("primary_test_builder", PRIMARY_PATH)
PRIMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRIMARY)

TEXT = {
    "ru": ("Технический пример", "Математика", "Сравнение чисел", "Найди и объясни ошибку", "Показывает неверное сравнение 8 < 3 и просит исправить его.", "Сравните 8 и 3. Исправьте знак и объясните ответ.", "Выбирает большее число", "Исправляет знак сравнения", "Объясняет ответ", "Карточка с числовой прямой.", "8 > 3: восемь больше трёх.", "Проверьте положение чисел на числовой прямой.", "Rosenshine: учитель показывает образец, затем проверяет самостоятельную попытку. UDL: доступна числовая прямая и устный ответ."),
    "kk": ("Техникалық мысал", "Математика", "Сандарды салыстыру", "Қатені тап және түсіндір", "8 < 3 қате салыстыруын көрсетіп, түзетуді сұрайды.", "8 және 3 сандарын салыстыр. Таңбаны түзетіп, жауабыңды түсіндір.", "Үлкен санды таңдайды", "Салыстыру таңбасын түзетеді", "Жауабын түсіндіреді", "Сан сәулесі бар карточка.", "8 > 3: сегіз үштен үлкен.", "Сандардың сан сәулесіндегі орнын тексер.", "Rosenshine: мұғалім үлгі көрсетіп, жеке әрекетті тексереді. UDL: сан сәулесі және ауызша жауап қолжетімді."),
    "en": ("Technical fixture", "Mathematics", "Comparing numbers", "Find and explain the error", "Shows the incorrect comparison 8 < 3 and asks learners to correct it.", "Compare 8 and 3. Correct the sign and explain your answer.", "Selects the larger number", "Corrects the comparison sign", "Explains the answer", "A number-line card.", "8 > 3: eight is greater than three.", "Check the positions on the number line.", "Rosenshine: the teacher models a solution and checks independent practice. UDL: a number line and an oral response are available."),
}


def fixture(grade, language):
    t = TEXT[language]
    data = KSP.example(test_fixture=True)
    data.update(language=language, instruction_language=language, grade=str(grade), subject=t[1], section=t[2], topic=t[2], organization=t[0], teacher=t[0], teacher_experience=t[0], qualification_category=t[0], class_characteristics=t[0])
    data["learning_objectives"] = [f"{grade}.1.1.1 {t[2]} ({t[0]})"]
    data["lesson_objectives"] = [t[2]]
    data["assessment_criteria"] = [t[10]]
    stage = data["stages"][0]
    stage.update(name=t[2], minutes=40, work_forms=["individual", "pair", "group"], teacher_actions=[t[4], t[11], t[4]], action_work_forms=[["individual"], ["pair"], ["group"]], resources=t[9])
    stage["methods"] = [{"method_id": "tech-1", "type": "primary", "name": t[3]}]
    task = stage["tasks"][0]
    task.update(objective_refs=[f"{grade}.1.1.1"], instruction=t[5], learner_action=t[8], expected_product=t[10], descriptor=t[6], descriptor_scores=[{"text": x, "points": 1} for x in t[6:9]], support=t[9], feedback=t[11])
    data["stages"] = [stage]
    appendix = data["methodological_appendix"]
    for key in appendix:
        appendix[key] = t[11]
    appendix["knowledge_skills_analysis"] = [prefix + " " + t[2] for prefix in KSP.KNOWLEDGE_SKILL_PREFIXES[language]]
    appendix["methodology_application"] = t[12]
    appendix["term_explanations"] = t[12] + " " + KSP.TERM_STATUS_MARKERS[language]
    return data


class ScoredDocumentTests(unittest.TestCase):
    def test_six_lesson_worksheet_pairs_and_docx_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(os.environ.get("SCHOOL_QA_OUTPUT", temp))
            directory.mkdir(parents=True, exist_ok=True)
            for grade in (2, 7):
                for language in TEXT:
                    route = PRIMARY if grade == 2 else KSP
                    data = route.validate_input(fixture(grade, language))
                    stem = f"grade-{grade}-{language}"
                    lesson_path = directory / f"{stem}-ksp.docx"
                    route.build(data, lesson_path)
                    handoff = handoff_from_ksp(data, stem)
                    manifest = {"artifact_type": "worksheet", "source_lesson_content_version": stem, "items": [{**deepcopy(task), "worksheet_task_id": f"ws-{i}"} for i, task in enumerate(handoff["canonical_tasks"])]}
                    worksheet_path = directory / f"{stem}-worksheet.docx"
                    worksheet(handoff, manifest, language, worksheet_path)
                    (directory / f"{stem}.json").write_text(json.dumps({"ksp": data, "lesson_plan_handoff": handoff, "derivative": manifest, "language": language}, ensure_ascii=False, indent=2), encoding="utf-8")
                    doc = KSP.Document(lesson_path)
                    self.assertFalse(KSP.contains_framework(" ".join(cell.text for row in doc.tables[1].rows for cell in row.cells)))
                    self.assertIn("Rosenshine", " ".join(p.text for p in doc.paragraphs))
                    self.assertIn("UDL", " ".join(p.text for p in doc.paragraphs))
                    score_heading = next(p for p in doc.tables[1].rows[1].cells[3].paragraphs if "— 3" in p.text)
                    score_heading.runs[0].bold = False
                    damaged = Path(temp) / "damaged.docx"
                    doc.save(damaged)
                    with self.assertRaises(KSP.KSPError):
                        KSP.structural_audit(damaged, expected_stage_contract=data["stages"], expected_language=language)
                    doc = KSP.Document(worksheet_path)
                    next(p for p in doc.paragraphs if "— 3" in p.text).runs[0].bold = False
                    doc.save(damaged)
                    with self.assertRaises(ValueError):
                        audit_worksheet(damaged, handoff, manifest, language)

    def test_ambiguous_forms_and_missing_techniques_fail(self):
        data = fixture(2, "ru")
        del data["stages"][0]["action_work_forms"]
        with self.assertRaises(KSP.KSPError):
            KSP.validate_input(data)
        data = fixture(2, "ru")
        data["stages"][0]["methods"] = []
        with self.assertRaises(KSP.KSPError):
            KSP.validate_input(data)


if __name__ == "__main__":
    unittest.main()
