import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class PresentationSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = "\n".join((read("SKILL.md"), read("runtime-workflow.md")))
        cls.design = read("references/design-core.md")
        cls.cases = read("references/evaluation-cases.md")
        cls.schema = read("references/lesson-plan-schema.md")
        cls.handoff = read("../../references/lesson-plan-handoff.md")
        cls.layouts = read("assets/artifact-tool-school-deck/layouts.mjs")

    def test_new_deck_requires_attached_or_automatic_same_chat_plan(self):
        self.assertIn("общий шлюз ҚМЖ/КСП", self.skill)
        self.assertIn("последнего успешно созданного и проверенного плана в текущем чате", self.skill)
        self.assertIn("lesson_plan_handoff", self.skill)
        self.assertIn("ready_for_derivatives", self.handoff)
        self.assertNotIn("approved_by_teacher", self.handoff)

    def test_assessment_criteria_are_localized(self):
        self.assertIn("Бағалау критерийлері", self.skill)
        self.assertIn("Критерии оценивания", self.skill)
        self.assertIn("Assessment criteria", self.skill)
        deprecated = "Нәтиже " + "өлшемдері"
        self.assertNotIn(deprecated, self.layouts)
        self.assertIn('criteriaLabel = "Критерии оценивания"', self.layouts)

    def test_presentation_applies_methodology_from_handoff_without_reselection(self):
        self.assertIn("Если `lesson_plan_handoff` содержит блок `methodology`", self.skill)
        self.assertIn("Не выбирать другую основную методику", self.skill)
        self.assertIn("не являются активным методом обучения", self.skill)

    def test_version_two_handoff_is_synchronized_to_slides(self):
        for field in ("schema_version", "content_boundaries", "episodes", "canonical_tasks", "canonical_answers"):
            self.assertIn(field, self.skill)
        self.assertIn("episode_id → canonical_task_id → slide_id", self.skill)
        self.assertIn("source_lesson_content_version", self.skill)
        self.assertIn('status: "requires_regeneration"', self.skill)
        self.assertIn("без заявления об эпизодной синхронизации", self.skill)

    def test_math_objects_use_native_powerpoint_math(self):
        for token in ("math_objects", "math_id", "a14:m", "m:oMath", "mc:AlternateContent", "validate_editable_math.py"):
            self.assertIn(token, self.skill)
        self.assertIn("fallback служит только совместимости", self.skill)
        self.assertIn("Не использовать PNG/SVG", self.skill)

    def test_every_slide_task_has_its_own_visible_descriptor(self):
        self.assertIn("Для каждого задания на слайдах без исключения", self.skill)
        self.assertIn("непосредственно следующем слайде проверки", self.skill)
        self.assertIn("не заменять его общим критерием", self.skill)

    def test_only_one_combined_clarification_round(self):
        self.assertIn("не более одного объединённого уточняющего вопроса", self.skill)
        self.assertIn("Не задавать эти вопросы", self.skill)
        self.assertIn("последовательно в разных сообщениях", self.skill)

    def test_teacher_controls_design_and_structure(self):
        for phrase in ("предложенную структуру", "выбора учителя", "изменить"):
            self.assertIn(phrase, self.skill)

    def test_ai_illustration_reference_and_limit_are_explicit(self):
        for phrase in ("референс", "0", "1", "2", "трёх"):
            self.assertIn(phrase, self.skill)

    def test_white_base_and_no_ornament_contract(self):
        self.assertRegex(self.design.casefold(), r"бел\w*\s+(?:фон|основ)")
        self.assertRegex(self.design.casefold(), r"(?:без|не использовать)[^\n]{0,80}(?:ою|орнамент)")

    def test_grade_profiles_are_all_linked(self):
        for band in ("1-2", "3-4", "5-7", "8-9", "10-11"):
            self.assertIn(f"design-grades-{band}.md", self.skill)

    def test_visual_and_pedagogical_qa_are_mandatory(self):
        for script in ("slides_test.py", "check_pptx_structure.py", "check_pptx_fonts.py", "check_lesson_coverage.py", "check_pptx_backgrounds.py"):
            self.assertIn(script, self.skill)

    def test_evaluation_matrix_contains_sixteen_cases(self):
        numbered = [line for line in self.cases.splitlines() if line[:1].isdigit() and ". " in line[:4]]
        self.assertEqual(16, len(numbered))


if __name__ == "__main__":
    unittest.main()
