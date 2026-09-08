import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHOOL = ROOT.parents[1]
ROUTER = SCHOOL / "skills" / "school-router" / "runtime-workflow.md"
URL = re.compile(r"https?://|www\.", re.IGNORECASE)


class NoExternalSearchTests(unittest.TestCase):
    def test_ktp_instruction_and_reference_files_have_no_external_urls(self):
        checked = []
        for suffix in ("*.md", "*.json", "*.yaml", "*.yml"):
            for path in ROOT.rglob(suffix):
                checked.append(path)
                self.assertIsNone(URL.search(path.read_text(encoding="utf-8")), str(path))
        self.assertTrue(checked)

    def test_entire_ktp_route_states_source_boundaries_and_nonblocking_calendar(self):
        combined = "\n".join((
            (ROOT / "runtime-workflow.md").read_text(encoding="utf-8"),
            (ROOT / "references" / "teacher-source-policy.md").read_text(encoding="utf-8"),
            ROUTER.read_text(encoding="utf-8"),
        ))
        for phrase in (
            "полностью запрещён внешний веб-поиск",
            "внешние URL",
            "файлы учителя",
            "встроенный утверждённый календарь плагина на 2026–2027 учебный год",
            "автоматически продолжать создание без запроса календаря у учителя",
            "pending_variable_holidays",
            "не блокируют КТП",
            "Не задавать вопросы «Укажите дату Құрбан айт»",
        ):
            self.assertIn(phrase.casefold(), combined.casefold())

    def test_old_official_internet_permission_is_removed(self):
        policy = (ROOT / "references" / "teacher-source-policy.md").read_text(encoding="utf-8")
        self.assertNotIn("Официальный интернет-источник разрешён", policy)
        self.assertNotIn("проверить самостоятельно по официальным источникам", policy)

    def test_builtin_holiday_catalog_has_no_url_fields(self):
        payload = json.loads((ROOT / "references" / "calendar" / "official-holidays-2026-2027.json").read_text(encoding="utf-8"))

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key.casefold()
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)

        catalog_keys = set(keys(payload))
        self.assertNotIn("url", catalog_keys)
        self.assertNotIn("source_url", catalog_keys)
        self.assertEqual(payload["source_type"], "builtin_approved_calendar_2026_2027")


if __name__ == "__main__":
    unittest.main()
