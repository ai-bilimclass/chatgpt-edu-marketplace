from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT.parents[1]
SKILL = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("SKILL.md", "runtime-workflow.md"))
MATRIX = (ROOT / "references" / "routing-matrix.md").read_text(encoding="utf-8")
FOLLOW_UP = (PLUGIN / "references" / "next-material-follow-up.md").read_text(encoding="utf-8")
SURVEY = (PLUGIN / "references" / "teacher-survey-follow-up.md").read_text(encoding="utf-8")
HANDOFF = (PLUGIN / "references" / "lesson-plan-handoff.md").read_text(encoding="utf-8")
CLASS_CONTEXT = (PLUGIN / "references" / "class-characteristics-intake.md").read_text(encoding="utf-8")
ALL_TEXT = "\n".join(
    path.read_text(encoding="utf-8", errors="ignore")
    for path in PLUGIN.rglob("*")
    if path.is_file() and path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json", ".js", ".mjs", ".svg"}
)


class RouterContractTests(unittest.TestCase):
    def test_routes_to_all_generators_without_creating_documents(self):
        for generator in (
            "school-medium-term-plan", "school-lesson-planner", "school-worksheet-builder",
            "school-assessment-builder", "school-presentation-builder",
        ):
            self.assertIn(f"`{generator}`", SKILL + MATRIX)
        self.assertIn("не создавать DOCX/PDF/PPTX", SKILL)

    def test_ktp_and_lesson_plan_intake_are_separated(self):
        self.assertIn("Особенности класса и отдельный язык документа не спрашивает", MATRIX)
        self.assertIn("методически содержательные особенности класса", MATRIX)
        self.assertIn("Сыныптың оқу үдерісіне әсер ететін қандай ерекшеліктері бар?", CLASS_CONTEXT)
        self.assertIn("собственное описание", CLASS_CONTEXT)
        self.assertIn("Особенностей нет", CLASS_CONTEXT)

    def test_language_of_instruction_is_required_and_drives_output(self):
        self.assertIn("instruction_language", SKILL)
        self.assertIn("автоматически равен `instruction_language`", SKILL)
        self.assertIn("отдельный вопрос о языке документа не задавать", SKILL.casefold())

    def test_lesson_duration_defaults_and_override(self):
        self.assertIn("40 минут по умолчанию", MATRIX)
        self.assertIn("явное значение учителя сохраняется", MATRIX)
        obsolete_duration_prompt = "40 или " + "45 минут"
        self.assertNotIn(obsolete_duration_prompt, ALL_TEXT)

    def test_follow_up_exact_questions_and_menus(self):
        required = (
            "Келесі кезекте қандай оқу материалын құрастыруды қалайсыз?",
            "Какой учебный материал вы хотели бы создать следующим?",
            "Which learning material would you like to create next?",
            "Бағалау материалы: ҚБ/БЖБ/ТЖБ",
            "Оценочный материал: ФО/СОР/СОЧ",
            "Methodological consultation",
        )
        for value in required:
            self.assertIn(value, FOLLOW_UP)
        for obsolete in (
            "Келесі кезекте қандай материал " + "қажет?",
            "Келесі кезекте қандай материал " + "құрастырайын?",
            "Келесі кезекте қандай оқу материалын " + "дайындауды қалайсыз?",
        ):
            self.assertNotIn(obsolete, ALL_TEXT)
        self.assertNotIn("&#" + "x20;", ALL_TEXT)

    def test_follow_up_counts_only_new_learning_materials(self):
        for excluded in ("маршрутизацию", "методическую консультацию", "проверку готового документа", "ошибку", "незавершённую"):
            self.assertIn(excluded, FOLLOW_UP)

    def test_handoff_recommendation_is_exact_bold_italic_and_monolingual(self):
        for text in (
            "***Бір сынып пен бір пәнге арналған сабақ материалдарын бір чатта құрастырып, жалғастырған ыңғайлы. Сондықтан оқу материалдарын осы чатта жалғастыруды ұсынамыз.***",
            "***Материалы уроков для одного класса и одного предмета удобно создавать и продолжать в одном чате. Поэтому рекомендуем продолжить работу над учебными материалами в этом чате.***",
            "***It is convenient to create and continue developing lesson materials for the same class and subject in one chat. Therefore, we recommend continuing the work on these learning materials in this chat.***",
        ):
            self.assertIn(text, HANDOFF)
        self.assertIn("не показывать три языковые версии одновременно", HANDOFF)

    def test_survey_is_exactly_once_after_four_materials(self):
        self.assertIn("completed_materials_count == 4", SURVEY)
        self.assertIn("survey_shown: true", SURVEY)
        self.assertIn("после пятого и следующих материалов", SURVEY)
        self.assertIn("3 октября 2026 года", SURVEY)
        self.assertIn("перед обязательным общим вопросом", SURVEY)
        for label in ("[***Сауалнаманы толтыру***]", "[***Заполнить опрос***]", "[***Complete the survey***]"):
            self.assertIn(label, SURVEY)
        self.assertEqual(3, SURVEY.count("https://docs.google.com/forms/d/e/1FAIpQLSchaV5hHSVebvD_IRWUE5XZDWPLVPCUUDfOCikoLDf3IRtUAQ/viewform?usp=header"))

    def test_survey_excludes_non_material_events(self):
        for excluded in ("маршрутизацию", "методическую консультацию", "проверку готового документа", "ошибку", "отменённую", "незавершённую"):
            self.assertIn(excluded, SURVEY)

    def test_assessment_terminology_is_consistent(self):
        self.assertIn("бағалау критерийлері", ALL_TEXT.casefold())
        deprecated = "нәтиже " + "өлшемдері"
        self.assertNotIn(deprecated, ALL_TEXT.casefold())

    def test_secondary_ktp_requires_teacher_program(self):
        self.assertIn("Для 5–11 классов — загруженная учебная программа", MATRIX)

    def test_academic_year_is_fixed(self):
        self.assertIn('academic_year: "2026–2027"', SKILL)
        self.assertIn("не задавать учителю вопрос об учебном годе", SKILL)

    def test_localized_first_run_menu_exists(self):
        for question in (
            "Сізге қандай оқу материалын дайындау қажет?",
            "Какой учебный материал вам необходимо подготовить?",
            "What teaching material would you like to prepare?",
        ):
            self.assertIn(question, SKILL)


if __name__ == "__main__":
    unittest.main()
