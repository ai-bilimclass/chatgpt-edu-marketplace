from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (ROOT / "runtime-workflow.md").read_text(encoding="utf-8")
PRIMARY = (ROOT / "references" / "primary-mode.md").read_text(encoding="utf-8")
SECONDARY = (ROOT / "references" / "secondary-mode.md").read_text(encoding="utf-8")
PRIMARY_SCHEMA = (ROOT / "references" / "primary" / "input-schema.md").read_text(encoding="utf-8")
SECONDARY_SCHEMA = (ROOT / "references" / "secondary" / "input-schema.md").read_text(encoding="utf-8")


class IntakeQuestionTests(unittest.TestCase):
    def test_academic_year_is_fixed_and_not_requested(self):
        for text in (RUNTIME, PRIMARY, SECONDARY, PRIMARY_SCHEMA, SECONDARY_SCHEMA):
            self.assertIn("2026–2027", text)
        self.assertIn("не запрашивать у учителя", RUNTIME)

    def test_weekday_question_is_required_in_all_languages(self):
        for question in (
            "Аптаның қай күндерінде/күнінде сабақ өтеді?",
            "В какие дни/какой день недели проходят уроки?",
            "On which day/days of the week are the lessons held?",
        ):
            self.assertIn(question, RUNTIME)
        self.assertIn("сопоставить недельные уроковые слоты с недельной нагрузкой", RUNTIME)

    def test_ktp_does_not_request_class_characteristics(self):
        self.assertNotIn("### 6. Особенности класса", RUNTIME)
        self.assertIn("Для КТП не спрашивать особенности класса", SECONDARY)
        self.assertIn("КТП үшін сынып ерекшеліктерін", PRIMARY)
        self.assertFalse((ROOT / "references" / "class-characteristics-options.md").exists())

    def test_ktp_requests_instruction_language_not_document_language(self):
        self.assertIn("язык обучения", RUNTIME)
        self.assertIn("Құжат тілін бөлек сұрамау", PRIMARY)
        self.assertIn("Не задавать отдельный вопрос о языке документа", SECONDARY)

    def test_instruction_language_becomes_output_language(self):
        for schema in (PRIMARY_SCHEMA, SECONDARY_SCHEMA):
            self.assertIn("автоматически равен `instruction_language`", schema)
            self.assertIn("прямом указании учителя", schema)


if __name__ == "__main__":
    unittest.main()
