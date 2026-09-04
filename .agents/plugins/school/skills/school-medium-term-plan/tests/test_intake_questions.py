from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (ROOT / "runtime-workflow.md").read_text(encoding="utf-8")
PRIMARY = (ROOT / "references" / "primary-mode.md").read_text(encoding="utf-8")
SECONDARY = (ROOT / "references" / "secondary-mode.md").read_text(encoding="utf-8")
PRIMARY_SCHEMA = (ROOT / "references" / "primary" / "input-schema.md").read_text(encoding="utf-8")
SECONDARY_SCHEMA = (ROOT / "references" / "secondary" / "input-schema.md").read_text(encoding="utf-8")
CLASS_OPTIONS = (ROOT / "references" / "class-characteristics-options.md").read_text(encoding="utf-8")


class IntakeQuestionTests(unittest.TestCase):
    def test_academic_year_is_fixed_and_not_requested(self):
        for text in (RUNTIME, PRIMARY, SECONDARY, PRIMARY_SCHEMA, SECONDARY_SCHEMA):
            with self.subTest(source=text[:30]):
                self.assertIn("2026–2027", text)
        self.assertIn("не запрашивать у учителя", RUNTIME)
        self.assertIn("Оқу жылын сұрамау", PRIMARY)

    def test_generic_weekday_question_is_present_in_all_languages(self):
        for question in (
            "Аптаның қай күндерінде/күнінде сабақ өтеді?",
            "В какие дни/какой день недели проходят уроки?",
            "On which day/days of the week are the lessons held?",
        ):
            self.assertIn(question, RUNTIME)

        self.assertNotIn("Аптаның қай үш күнінде сабақ өтеді?", RUNTIME)
        self.assertIn("первых обязательных вопросов", RUNTIME)
        self.assertIn("не зависит от того, известна ли недельная нагрузка", RUNTIME)

    def test_weekdays_must_match_weekly_load(self):
        self.assertIn("сопоставить недельные уроковые слоты с недельной нагрузкой", RUNTIME)
        self.assertIn("расписание и нагрузка не согласованы", RUNTIME)

    def test_class_characteristics_is_question_six_with_three_subject_options(self):
        self.assertIn("### 6. Особенности класса", RUNTIME)
        self.assertIn("ровно три кратких варианта", RUNTIME)
        self.assertIn("6. Сыныптың оқу үдерісіне әсер ететін қандай ерекшеліктері бар?", CLASS_OPTIONS)
        self.assertIn("Музыка, көркем еңбек және технология", CLASS_OPTIONS)
        self.assertIn("Математика және информатика", CLASS_OPTIONS)
        self.assertIn("Тіл және әдебиет", CLASS_OPTIONS)
        self.assertIn("Мұғалімге нөмірді таңдауға немесе өз сипаттамасын жазуға рұқсат беру", CLASS_OPTIONS)


if __name__ == "__main__":
    unittest.main()
