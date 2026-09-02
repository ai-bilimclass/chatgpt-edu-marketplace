import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GuidanceRoutingTests(unittest.TestCase):
    def test_shared_guidance_exists_and_is_routed_from_entrypoint(self):
        guidance = ROOT / "references" / "teacher-methodological-guidance.md"
        self.assertTrue(guidance.is_file())
        entrypoint = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/teacher-methodological-guidance.md", entrypoint)

    def test_both_grade_modes_route_to_shared_guidance(self):
        for relative in (Path("primary/MODE.md"), Path("secondary/MODE.md")):
            content = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("teacher-methodological-guidance.md", content, str(relative))

    def test_primary_mode_routes_to_series_memory_protocol(self):
        protocol = ROOT / "primary" / "references" / "pedagogical-memory.md"
        self.assertTrue(protocol.is_file())
        primary_mode = (ROOT / "primary" / "MODE.md").read_text(encoding="utf-8")
        self.assertIn("references/pedagogical-memory.md", primary_mode)
        self.assertIn("ровно три", primary_mode)
        self.assertIn("текущем диалоге", primary_mode)

    def test_both_grade_modes_require_three_concepts_before_docx(self):
        primary_mode = (ROOT / "primary" / "MODE.md").read_text(encoding="utf-8")
        secondary_mode = (ROOT / "secondary" / "MODE.md").read_text(encoding="utf-8")
        self.assertIn("три действительно разные концепции", primary_mode)
        self.assertIn("ровно три действительно разные концепции урока", secondary_mode)
        self.assertIn("До выбора учителя или явной передачи выбора навыку запрещено", secondary_mode)

    def test_local_markdown_links_in_entrypoint_resolve(self):
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", content)
        self.assertTrue(links)
        missing = [link for link in links if not (ROOT / link).is_file()]
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
