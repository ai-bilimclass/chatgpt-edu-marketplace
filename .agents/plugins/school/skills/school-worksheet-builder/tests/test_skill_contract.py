import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class WorksheetSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = "\n".join((read("SKILL.md"), read("runtime-workflow.md")))
        cls.primary_design = read("primary/design-system.md")
        cls.primary_regular = read("primary/regular-worksheet.md")
        cls.primary_practical = read("primary/practical-investigation.md")
        cls.secondary_regular = read("secondary/regular-worksheet.md")
        cls.secondary_lab = read("secondary/laboratory-practical.md")
        cls.cognitive = read("secondary/cognitive-levels.md")
        cls.safety = read("references/source-and-safety-policy.md")

    def test_requires_attached_or_automatic_same_chat_lesson_plan(self):
        self.assertIn("общий шлюз ҚМЖ/КСП", self.skill)
        self.assertIn("lesson_plan_handoff", self.skill)
        self.assertIn("последнего успешно созданного и проверенного плана в текущем чате", self.skill)
        self.assertIn("Не требовать повторной загрузки или фразы о принятии плана", self.skill)

    def test_every_task_has_a_descriptor(self):
        combined = "\n".join((
            self.skill,
            self.primary_regular,
            self.primary_practical,
            self.secondary_regular,
            self.secondary_lab,
        ))
        self.assertIn("Для каждого задания включать локализованный дескриптор", combined)
        self.assertGreaterEqual(combined.casefold().count("дескриптор"), 5)

    def test_methodology_is_applied_from_handoff_without_reselection(self):
        self.assertIn("Если handoff содержит блок `methodology`", self.skill)
        self.assertIn("Не выбирать заново основной или специализированный метод", self.skill)

    def test_version_two_handoff_is_synchronized_to_tasks(self):
        for field in ("schema_version", "content_boundaries", "episodes", "canonical_tasks", "canonical_answers"):
            self.assertIn(field, self.skill)
        self.assertIn("episode_id → canonical_task_id → worksheet_task_id", self.skill)
        self.assertIn("source_lesson_content_version", self.skill)
        self.assertIn('status: "requires_regeneration"', self.skill)
        self.assertIn("без заявления об эпизодной синхронизации", self.skill)

    def test_all_four_routes_are_declared(self):
        for path in (
            "primary/regular-worksheet.md",
            "primary/practical-investigation.md",
            "secondary/regular-worksheet.md",
            "secondary/laboratory-practical.md",
        ):
            self.assertIn(path, self.skill)

    def test_teacher_guidance_is_localized(self):
        for heading in ("Мұғалімге нұсқаулық", "Руководство для учителя", "Guide for the Teacher"):
            self.assertIn(heading, self.skill)

    def test_student_page_numbers_are_static_and_exclude_teacher_pages(self):
        for token in ("1-бет / 2", "Страница 1 из 2", "Page 1 of 2"):
            self.assertIn(token, self.skill)
        self.assertIn("Не использовать динамические поля Word", self.skill)
        self.assertIn("раздел для учителя не продолжает эту нумерацию", self.skill)

    def test_primary_does_not_use_abc_or_summative_logic(self):
        self.assertIn("Для 1–4 классов не использовать A/B/C", self.skill)
        self.assertIn("Не переносить БЖБ/ТЖБ", self.skill)
        self.assertIn("по умолчанию не использовать баллы", self.skill)

    def test_secondary_requires_abc_bloom_and_counts(self):
        for phrase in ("Уровень сложности", "Навыки Блума", "Количество заданий"):
            self.assertIn(phrase, self.cognitive)
        self.assertIn("Не генерировать лист", self.cognitive)

    def test_practical_routes_require_safety_inputs(self):
        combined = "\n".join((self.skill, self.primary_practical, self.secondary_lab, self.safety))
        for phrase in ("ресурсный и безопасностный шлюз", "подтверждения ресурсов и источника", "не проектировать процедуру"):
            self.assertRegex(combined.casefold(), re.escape(phrase.casefold()))

    def test_grade_band_visual_contracts(self):
        self.assertIn("цветные акценты", self.skill)
        self.assertIn("чёрно-белое оформление", self.skill)
        self.assertIn("12–18 pt", self.primary_design)
        self.assertIn("тонкие сплошные внутренние и внешние линии", self.primary_design)

    def test_student_teacher_information_separation(self):
        self.assertIn("Не показывать ученику", self.skill)
        self.assertIn("ожидаемый ответ или продукт", self.cognitive)
        self.assertIn("типичную ошибку и корректирующую обратную связь", self.cognitive)

    def test_interactive_answers_do_not_require_second_confirmation(self):
        policy = read("../../references/interactive-question-policy.md")
        self.assertIn("общему правилу интерактивных вопросов", self.skill)
        self.assertIn("Ответ учителя на интерактивный раунд считается окончательным выбором", policy)
        for phrase in ("келісемін", "согласен", "подтверждаю", "confirm"):
            self.assertIn(phrase, policy)
        self.assertIn("продолжить без второго подтверждения", self.skill)


if __name__ == "__main__":
    unittest.main()
