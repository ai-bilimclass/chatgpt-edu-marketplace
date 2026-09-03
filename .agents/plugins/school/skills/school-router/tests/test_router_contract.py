from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = "\n".join(
    (ROOT / filename).read_text(encoding="utf-8")
    for filename in ("SKILL.md", "runtime-workflow.md")
)
MATRIX = (ROOT / "references" / "routing-matrix.md").read_text(encoding="utf-8")
FOLLOW_UP = (ROOT / ".." / ".." / "references" / "next-material-follow-up.md").read_text(encoding="utf-8")
SURVEY = (ROOT / ".." / ".." / "references" / "teacher-survey-follow-up.md").read_text(encoding="utf-8")


class RouterContractTests(unittest.TestCase):
    def test_routes_to_all_five_generators(self):
        expected = {
            "school-medium-term-plan",
            "school-lesson-planner",
            "school-worksheet-builder",
            "school-assessment-builder",
            "school-presentation-builder",
        }
        combined = SKILL + "\n" + MATRIX
        for generator in expected:
            with self.subTest(generator=generator):
                self.assertIn(f"`{generator}`", combined)

    def test_router_does_not_create_documents(self):
        self.assertIn("Самостоятельно не проектировать содержание", SKILL)
        self.assertIn("не создавать DOCX/PDF/PPTX", SKILL)

    def test_objectives_cannot_be_invented(self):
        self.assertIn("Не восстанавливать отсутствующую цель", SKILL)
        self.assertIn("Не заполнять пропуски предположениями", SKILL)

    def test_presentation_requires_lesson_plan(self):
        self.assertIn("Прикреплённый ҚМЖ/КСП либо полный подтверждённый", MATRIX)

    def test_follow_up_is_localized_and_excludes_completed_product(self):
        for question in (
            "Келесі ретте қандай оқу материалын дайындау қажет?",
            "Какой учебный материал необходимо подготовить следующим?",
            "What learning material should be prepared next?",
        ):
            self.assertIn(question, FOLLOW_UP)
        self.assertIn("убрать только что завершённый вид материала", FOLLOW_UP)
        self.assertIn("В этом примере КТП исключён", FOLLOW_UP)

    def test_router_passes_methodology_without_selecting_it(self):
        self.assertIn("methodology: {}", SKILL)
        self.assertIn("не предлагает учителю выбрать методику", SKILL)
        self.assertIn("не формирует этот блок самостоятельно", SKILL)

    def test_survey_is_shown_once_after_four_completed_materials(self):
        self.assertIn("completed_materials_count >= 4", SURVEY)
        self.assertIn("survey_shown: true", SURVEY)
        self.assertIn("3 октября 2026 года", SURVEY)
        self.assertIn("Сауалнаманы толтыру", SURVEY)
        self.assertIn("Пройти опрос", SURVEY)
        self.assertIn("Complete the survey", SURVEY)
        self.assertIn("teacher-survey-follow-up.md", SKILL)

    def test_secondary_ktp_requires_teacher_program(self):
        self.assertIn("Для 5–11 классов — загруженная учебная программа", MATRIX)

    def test_lab_route_has_safety_gate(self):
        self.assertIn("При отсутствии безопасной процедуры практическую работу не генерировать", MATRIX)

    def test_local_markdown_links_exist(self):
        self.assertTrue((ROOT / "references" / "routing-matrix.md").is_file())
        self.assertTrue((ROOT / ".." / ".." / "references" / "teacher-survey-follow-up.md").is_file())

    def test_localized_first_run_menu_exists(self):
        self.assertIn("Сізге қандай оқу материалын дайындау қажет?", SKILL)
        self.assertIn("Какой учебный материал вам необходимо подготовить?", SKILL)
        self.assertIn("What teaching material would you like to prepare?", SKILL)
        self.assertIn("Если продукт уже ясен из первого сообщения, не показывать стартовое меню", SKILL)


if __name__ == "__main__":
    unittest.main()
