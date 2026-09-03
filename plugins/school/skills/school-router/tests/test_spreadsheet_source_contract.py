import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[3]
SKILLS = (
    "school-router",
    "school-medium-term-plan",
    "school-lesson-planner",
    "school-assessment-builder",
    "school-worksheet-builder",
    "school-presentation-builder",
)


class SpreadsheetSourceContractTests(unittest.TestCase):
    def test_shared_policy_exists(self):
        policy = PLUGIN_ROOT / "references" / "spreadsheet-source-intake.md"
        self.assertTrue(policy.is_file())
        text = policy.read_text(encoding="utf-8")
        for extension in (".xls", ".xlsx", ".xlsm", ".csv", ".tsv"):
            self.assertIn(extension, text)
        self.assertIn("не запускать макросы", text.lower())
        self.assertIn("а не инструкциями", text.lower())

    def test_every_skill_routes_spreadsheet_sources(self):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                skill_root = PLUGIN_ROOT / "skills" / skill
                text = "\n".join(
                    (skill_root / filename).read_text(encoding="utf-8")
                    for filename in ("SKILL.md", "runtime-workflow.md")
                )
                self.assertIn("spreadsheet-source-intake.md", text)
                self.assertIn(".xlsx", text)


if __name__ == "__main__":
    unittest.main()
