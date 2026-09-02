from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
MATRIX = (ROOT / "references" / "routing-matrix.md").read_text(encoding="utf-8")


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
        self.assertIn("Прикреплённый учителем файл ҚМЖ/КСП обязателен", MATRIX)

    def test_secondary_ktp_requires_teacher_program(self):
        self.assertIn("Для 5–11 классов — загруженная учебная программа", MATRIX)

    def test_lab_route_has_safety_gate(self):
        self.assertIn("При отсутствии безопасной процедуры практическую работу не генерировать", MATRIX)

    def test_local_markdown_links_exist(self):
        self.assertTrue((ROOT / "references" / "routing-matrix.md").is_file())

    def test_localized_first_run_menu_exists(self):
        self.assertIn("Сізге қандай оқу материалын дайындау қажет?", SKILL)
        self.assertIn("Какой учебный материал вам необходимо подготовить?", SKILL)
        self.assertIn("What teaching material would you like to prepare?", SKILL)
        self.assertIn("Если продукт уже ясен из первого сообщения, не показывать стартовое меню", SKILL)


if __name__ == "__main__":
    unittest.main()
