import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class AssessmentSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = "\n".join((read("SKILL.md"), read("runtime-workflow.md")))
        cls.guidance = read("references/teacher-guidance.md")
        cls.terminology = read("references/terminology.md")
        cls.moderation = read("references/moderation-guidance-trilingual.md")

    def test_student_writing_uses_blue_ink_in_three_languages(self):
        combined = "\n".join((self.skill, self.guidance, self.moderation))
        for phrase in (
            "көк пасталы қаламмен жазыңыз",
            "пишите ручкой с синей пастой",
            "write with a blue-ink pen",
        ):
            self.assertIn(phrase, combined)
        self.assertIn("Никогда не рекомендовать обучающемуся чёрную пасту", self.skill)

    def test_teacher_guidance_headings_are_localized(self):
        for heading in (
            "Бағалауды ұйымдастыру бойынша мұғалімге арналған ұсыныстар",
            "Рекомендации учителю по организации оценивания",
            "Recommendations for teachers on organizing assessment",
        ):
            self.assertIn(heading, self.guidance)

    def test_moderation_is_defined_in_three_languages(self):
        for heading in (
            "Жиынтық бағалауды модерациялау",
            "Модерация суммативного оценивания",
            "Moderation of summative assessment",
        ):
            self.assertIn(heading, self.moderation)
        self.assertIn("Модерация / Модерация / Moderation", self.terminology)
        self.assertIn("Источники, предоставленные пользователем", self.moderation)

    def test_methodology_does_not_replace_assessment_logic(self):
        self.assertIn("Если готовый `lesson_plan_handoff` содержит блок `methodology`", self.skill)
        self.assertIn("не перестраивать самостоятельную логику", self.skill)

    def test_docx_formulas_are_native_and_validated(self):
        for phrase in ("editable-math-contract.md", "math_id", "m:oMath", "m:oMathPara", "validate_editable_math.py"):
            self.assertIn(phrase, self.skill)
        self.assertIn("Не выдавать изображение, строку LaTeX", self.skill)


if __name__ == "__main__":
    unittest.main()
