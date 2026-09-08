#!/usr/bin/env python3
"""Regression tests for the bundled-form KSP builder."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_ksp.py")
SPEC = importlib.util.spec_from_file_location("build_ksp", SCRIPT)
assert SPEC and SPEC.loader
BUILD_KSP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_KSP)


class BuildKSPTests(unittest.TestCase):
    def data(self):
        return deepcopy(BUILD_KSP.example(test_fixture=True))

    def localized_knowledge_items(self, language):
        return [f"{prefix} Тестовое содержание." for prefix in BUILD_KSP.KNOWLEDGE_SKILL_PREFIXES[language]]

    def test_printed_example_is_not_preconfirmed(self):
        data = BUILD_KSP.example()
        self.assertFalse(data["intake_verification"]["confirmed_by_user"])
        with self.assertRaises(BUILD_KSP.KSPError):
            BUILD_KSP.validate_input(data)

    def test_complete_confirmed_intake_is_accepted(self):
        BUILD_KSP.validate_input(self.data())

    def test_kazakh_source_status_is_normalized(self):
        data = self.data()
        data["instruction_language"] = "kk"
        data["language"] = "kk"
        data["methodological_appendix"]["knowledge_skills_analysis"] = self.localized_knowledge_items("kk")
        data["methodological_appendix"]["methodology_application"] = (
            "Explicit Instruction тәсілі үлгілеу және дербес орындау арқылы қолданылады."
        )
        data["methodological_appendix"]["term_explanations"] = (
            "Explicit Instruction — айқын нұсқау арқылы оқыту. Мәртебесі: әдістемелік ұсыныс."
        )
        validated = BUILD_KSP.validate_input(data)
        self.assertEqual(
            validated["methodological_appendix"]["external_resources"],
            [
                BUILD_KSP.KK_SOURCE_STATUS_GOAL,
                BUILD_KSP.KK_SOURCE_STATUS_EXPLICIT,
                BUILD_KSP.KK_SOURCE_STATUS_FORM,
            ],
        )

    def test_unconfirmed_intake_is_rejected(self):
        data = self.data()
        data["intake_verification"]["confirmed_by_user"] = False
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "explicitly confirmed"):
            BUILD_KSP.validate_input(data)

    def test_missing_confirmed_field_is_rejected(self):
        data = self.data()
        data["intake_verification"]["confirmed_fields"].remove("class_size")
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "class_size"):
            BUILD_KSP.validate_input(data)

    def test_legitimate_expected_result_phrase_is_allowed_in_content(self):
        data = self.data()
        data["methodological_appendix"]["goal_analysis"] = (
            "Ожидаемый результат программы сопоставлен с целью урока."
        )
        BUILD_KSP.validate_input(data)

    def test_missing_knowledge_skills_analysis_is_rejected(self):
        data = self.data()
        del data["methodological_appendix"]["knowledge_skills_analysis"]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "knowledge_skills_analysis"):
            BUILD_KSP.validate_input(data)

    def test_knowledge_skills_analysis_requires_exactly_five_items(self):
        data = self.data()
        data["methodological_appendix"]["knowledge_skills_analysis"].pop()
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "exactly four"):
            BUILD_KSP.validate_input(data)

    def test_removed_knowledge_category_is_rejected(self):
        data = self.data()
        data["methodological_appendix"]["knowledge_skills_analysis"][1] = (
            "ФАКТИЧЕСКИЕ ЗНАНИЯ: концептуальное знание как отдельная категория."
        )
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "removed category"):
            BUILD_KSP.validate_input(data)

    def test_knowledge_skills_analysis_order_is_enforced(self):
        data = self.data()
        items = data["methodological_appendix"]["knowledge_skills_analysis"]
        items[0], items[1] = items[1], items[0]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "item 1"):
            BUILD_KSP.validate_input(data)

    def test_missing_methodology_application_is_rejected(self):
        data = self.data()
        del data["methodological_appendix"]["methodology_application"]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "methodology_application"):
            BUILD_KSP.validate_input(data)

    def test_named_method_requires_term_explanation(self):
        data = self.data()
        data["methodological_appendix"]["model_rationale"] = "Для урока выбрана модель UbD."
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "term_explanations is required"):
            BUILD_KSP.validate_input(data)

    def test_named_method_with_localized_explanation_is_accepted(self):
        data = self.data()
        data["methodological_appendix"]["model_rationale"] = "Для урока выбрана модель UbD."
        data["methodological_appendix"]["term_explanations"] = (
            "UbD (Understanding by Design) — модель обратного проектирования: сначала определяется итоговое доказательство, затем задания. В этом уроке она связывает итоговый график с практикой. Статус: методическая рекомендация."
        )
        BUILD_KSP.validate_input(data)

    def test_term_explanation_requires_localized_status(self):
        data = self.data()
        data["methodological_appendix"]["model_rationale"] = "Для урока выбрана модель UbD."
        data["methodological_appendix"]["term_explanations"] = "UbD — модель обратного проектирования."
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "методическая рекомендация"):
            BUILD_KSP.validate_input(data)

    def test_term_explanation_follows_first_term_use(self):
        data = self.data()
        appendix = data["methodological_appendix"]
        appendix["methodology_application"] = "На этапе исследования применяется UbD."
        appendix["model_rationale"] = "Модель поддерживает согласованность цели и задания."
        appendix["term_explanations"] = (
            "UbD — модель обратного проектирования. Статус: методическая рекомендация."
        )
        order = BUILD_KSP.appendix_render_order(appendix)
        self.assertEqual(order.index("term_explanations"), order.index("methodology_application") + 1)

    def test_term_explanation_moves_with_later_first_use(self):
        data = self.data()
        appendix = data["methodological_appendix"]
        appendix["methodology_application"] = "Ученики сравнивают два решения."
        appendix["model_rationale"] = "Для согласования результата выбрана модель UbD."
        appendix["term_explanations"] = (
            "UbD — модель обратного проектирования. Статус: методическая рекомендация."
        )
        order = BUILD_KSP.appendix_render_order(appendix)
        self.assertEqual(order.index("term_explanations"), order.index("model_rationale") + 1)

    def test_expected_results_field_name_is_rejected(self):
        data = self.data()
        data["expected_results"] = ["Не должно быть отдельным полем встроенной формы."]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "Banned field name"):
            BUILD_KSP.validate_input(data)

    def test_lesson_count_must_be_positive(self):
        data = self.data()
        data["lesson_count"] = 0
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "lesson_count"):
            BUILD_KSP.validate_input(data)

    def test_multiple_lesson_request_is_accepted(self):
        data = self.data()
        data["lesson_count"] = 3
        BUILD_KSP.validate_input(data)

    def test_practical_subject_requires_confirmed_resources(self):
        data = self.data()
        data["subject"] = "Химия"
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "practical_resources is required"):
            BUILD_KSP.validate_input(data)

    def test_practical_subject_accepts_teacher_confirmed_resources(self):
        data = self.data()
        data["subject"] = "Көркем еңбек"
        data["practical_resources"] = (
            "Ішінара мүмкіндік бар: қағаз, желім және қайшы бар; электр құралдарын қолдануға болмайды."
        )
        data["intake_verification"]["confirmed_fields"].append("practical_resources")
        BUILD_KSP.validate_input(data)

    def test_explicit_duration_override_is_preserved(self):
        data = self.data()
        data["lesson_duration_minutes"] = 45
        data["stages"][1]["minutes"] += 5
        validated = BUILD_KSP.validate_input(data)
        self.assertEqual(validated["lesson_duration_minutes"], 45)

    def test_duration_defaults_to_40(self):
        validated = BUILD_KSP.validate_input(self.data())
        self.assertEqual(validated["lesson_duration_minutes"], 40)

    def test_instruction_language_is_required(self):
        data = self.data()
        del data["instruction_language"]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "instruction_language"):
            BUILD_KSP.validate_input(data)

    def test_document_language_follows_instruction_language_without_override(self):
        data = self.data()
        data["language"] = "kk"
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "must match instruction_language"):
            BUILD_KSP.validate_input(data)

    def test_explicit_document_language_override_is_accepted(self):
        data = self.data()
        data["language"] = "kk"
        data["document_language_explicit"] = True
        data["methodological_appendix"]["knowledge_skills_analysis"] = self.localized_knowledge_items("kk")
        BUILD_KSP.validate_input(data)

    def test_stage_time_mismatch_is_rejected(self):
        data = self.data()
        data["stages"][0]["minutes"] += 1
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "Stage minutes total"):
            BUILD_KSP.validate_input(data)

    def test_old_exit_ticket_term_is_rejected(self):
        data = self.data()
        data["stages"][-1]["teacher_actions"] = ["Организует выходной билет."]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "Reflection"):
            BUILD_KSP.validate_input(data)

    def test_schema_3_missing_descriptor_is_rejected(self):
        data = self.data()
        del data["stages"][0]["tasks"][0]["descriptor"]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "descriptor"):
            BUILD_KSP.validate_input(data)

    def test_schema_3_duplicate_task_id_is_rejected(self):
        data = self.data()
        data["stages"][1]["tasks"][0]["canonical_task_id"] = "task-01"
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "Duplicate canonical_task_id"):
            BUILD_KSP.validate_input(data)

    def test_schema_3_unknown_objective_reference_is_rejected(self):
        data = self.data()
        data["stages"][0]["tasks"][0]["objective_refs"] = ["7.4.9.9"]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "not supplied by the teacher"):
            BUILD_KSP.validate_input(data)

    def test_schema_3_descriptor_must_not_repeat_instruction(self):
        data = self.data()
        task = data["stages"][0]["tasks"][0]
        task["descriptor"] = task["instruction"]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "repeats the instruction"):
            BUILD_KSP.validate_input(data)

    def test_schema_3_feedback_phrase_is_not_a_descriptor(self):
        data = self.data()
        data["stages"][0]["tasks"][0]["descriptor"] = "Устная обратная связь"
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "instead of a descriptor"):
            BUILD_KSP.validate_input(data)

    def test_schema_3_learning_stage_requires_task(self):
        data = self.data()
        data["stages"][0]["tasks"] = []
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "requires at least one task"):
            BUILD_KSP.validate_input(data)

    def test_schema_3_organization_stage_may_have_no_task(self):
        data = self.data()
        data["stages"][0]["activity_type"] = "organization"
        data["stages"][0]["tasks"] = []
        BUILD_KSP.validate_input(data)

    def test_schema_3_repeated_descriptor_is_warning(self):
        data = self.data()
        data["stages"][1]["tasks"][0]["descriptor"] = data["stages"][0]["tasks"][0]["descriptor"]
        validated = BUILD_KSP.validate_input(data)
        self.assertTrue(validated["validation_warnings"])

    def test_schema_3_rejects_method_markup(self):
        data = self.data()
        data["stages"][0]["methods"][0]["name"] = "***Метод/приём: Вспомни***"
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "without markup or prefix"):
            BUILD_KSP.validate_input(data)

    def test_schema_2_is_accepted_as_legacy_unverified(self):
        data = self.data()
        data["schema_version"] = "2.0"
        for stage in data["stages"]:
            method_lines = [f"***Метод/приём: {item['name']}***" for item in stage.pop("methods")]
            tasks = stage.pop("tasks")
            stage.pop("activity_type")
            stage["teacher_actions"] = method_lines + stage["teacher_actions"]
            stage["learner_actions"] = [item["learner_action"] for item in tasks]
            stage["assessment"] = [item["descriptor"] for item in tasks]
        validated = BUILD_KSP.validate_input(data)
        self.assertEqual(validated["validation_status"], "legacy_unverified")

    def test_typed_bullet_is_rejected(self):
        data = self.data()
        data["lesson_objectives"] = ["• Строить график"]
        with self.assertRaisesRegex(BUILD_KSP.KSPError, "typed bullet"):
            BUILD_KSP.validate_input(data)

    def test_all_bundled_languages_build_and_rows_do_not_split(self):
        with tempfile.TemporaryDirectory() as directory:
            for language in ("ru", "kk", "en"):
                data = self.data()
                data["instruction_language"] = language
                data["language"] = language
                data["methodological_appendix"]["knowledge_skills_analysis"] = self.localized_knowledge_items(language)
                output = Path(directory) / f"sample-{language}.docx"
                BUILD_KSP.build(BUILD_KSP.validate_input(data), output)
                BUILD_KSP.structural_audit(output)
                with zipfile.ZipFile(output) as archive:
                    xml = archive.read("word/document.xml")
                self.assertGreaterEqual(xml.count(b"w:cantSplit"), len(data["stages"]))
                text = BUILD_KSP.all_text(BUILD_KSP.Document(output)).casefold()
                self.assertIn(BUILD_KSP.LABELS[language]["professional_notice_text"].casefold(), text)
                self.assertIn(BUILD_KSP.LABELS[language]["external_resources"].casefold(), text)
                source_bounds = {
                    "kk": (BUILD_KSP.KK_SOURCE_STATUS_GOAL, BUILD_KSP.KK_SOURCE_STATUS_FORM),
                    "ru": (BUILD_KSP.RU_SOURCE_STATUS_GOAL, BUILD_KSP.RU_SOURCE_STATUS_FORM),
                    "en": (BUILD_KSP.EN_SOURCE_STATUS_GOAL, BUILD_KSP.EN_SOURCE_STATUS_FORM),
                }
                goal_source, form_source = source_bounds[language]
                goal_index = text.index(goal_source.casefold())
                form_index = text.index(form_source.casefold())
                self.assertLess(goal_index, form_index)
                self.assertNotIn("дереккөздер және мәртебесі", text)
                self.assertNotIn("источники и статус", text)
                self.assertNotIn("sources and status", text)
                rendered = BUILD_KSP.Document(output)
                teacher_method_runs = [
                    run
                    for row in rendered.tables[1].rows[1:]
                    for paragraph in row.cells[1].paragraphs
                    for run in paragraph.runs
                    if run.text.strip() and run.bold is True and run.italic is True
                ]
                self.assertEqual(len(teacher_method_runs), sum(len(stage["methods"]) for stage in data["stages"]))
                self.assertTrue(all(run.text.startswith(BUILD_KSP.METHOD_PREFIX[language]) for run in teacher_method_runs))
                self.assertTrue(all("***" not in run.text for run in teacher_method_runs))
                notice_values = {
                    BUILD_KSP.LABELS[language]["professional_notice"],
                    BUILD_KSP.LABELS[language]["professional_notice_text"],
                }
                notice_paragraphs = [p for p in rendered.paragraphs if p.text.strip() in notice_values]
                self.assertEqual(len(notice_paragraphs), 2)
                self.assertTrue(all(run.italic is True for p in notice_paragraphs for run in p.runs if run.text.strip()))
                self.assertNotIn("internal-audit summary", text)
                self.assertNotIn("итог внутреннего аудита", text)
                self.assertNotIn("ішкі аудит қорытындысы", text)
                self.assertNotIn("ескерту: «бағалау критерийлері» — әдістемелік қосымша", text)


if __name__ == "__main__":
    unittest.main()
