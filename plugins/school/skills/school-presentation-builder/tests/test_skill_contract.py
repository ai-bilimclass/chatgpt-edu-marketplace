import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class PresentationSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = read("SKILL.md")
        cls.design = read("references/design-core.md")
        cls.cases = read("references/evaluation-cases.md")

    def test_new_deck_requires_teacher_uploaded_lesson_plan(self):
        self.assertIn("абсолютный шлюз КСП/ҚМЖ", self.skill)
        self.assertIn("не создавать черновик, код или PPTX", self.skill)
        self.assertIn("вставленным моделью текстом", self.skill)

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
