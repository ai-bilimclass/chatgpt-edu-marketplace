from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT.parents[1]
RUNTIME = (ROOT / "runtime-workflow.md").read_text(encoding="utf-8")
PRIMARY = (ROOT / "primary" / "MODE.md").read_text(encoding="utf-8")
SECONDARY = (ROOT / "secondary" / "MODE.md").read_text(encoding="utf-8")
INTAKE_GATE = (ROOT / "secondary" / "references" / "intake-gate.md").read_text(encoding="utf-8")
CLASS_CONTEXT = (PLUGIN / "references" / "class-characteristics-intake.md").read_text(encoding="utf-8")


class LessonPlanIntakePolicyTests(unittest.TestCase):
    def test_class_characteristics_are_required_in_both_modes(self):
        self.assertIn("особенности класса", PRIMARY.casefold())
        self.assertIn("особенности класса", SECONDARY.casefold())
        self.assertIn("Сыныптың оқу үдерісіне әсер ететін қандай ерекшеліктері бар?", CLASS_CONTEXT)
        for dimension in ("классу", "предмету", "возрасту", "языку обучения", "характеру урока"):
            self.assertIn(dimension, CLASS_CONTEXT)
        self.assertIn("своими словами", CLASS_CONTEXT)

    def test_class_characteristics_are_not_reasked_for_same_context(self):
        self.assertIn("повторно их не спрашивать", CLASS_CONTEXT)
        self.assertIn("тому же классу и предмету", CLASS_CONTEXT)

    def test_instruction_language_drives_document_language(self):
        self.assertIn("Язык обучения спрашивать обязательно", RUNTIME)
        self.assertIn("Не задавать отдельный вопрос о языке документа", RUNTIME)
        self.assertIn("другом языке", RUNTIME)

    def test_duration_is_not_asked_and_defaults_to_40(self):
        for text in (PRIMARY, SECONDARY, INTAKE_GATE):
            self.assertIn("40", text)
        self.assertIn("Продолжительность одного урока по умолчанию равна 40 минутам", PRIMARY)
        self.assertIn("Не спрашивать учителя о минутах урока", SECONDARY)
        self.assertIn("explicitly supplies it", INTAKE_GATE)


if __name__ == "__main__":
    unittest.main()
