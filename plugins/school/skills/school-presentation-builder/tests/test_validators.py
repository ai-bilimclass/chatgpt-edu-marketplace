import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


coverage = load("check_lesson_coverage")
fonts = load("check_pptx_fonts")
structure = load("check_pptx_structure")


class CoverageValidatorTests(unittest.TestCase):
    def setUp(self):
        self.plan = {
            "topic": "Механическое движение",
            "objectives": ["9.2.1.1 объяснять относительность движения"],
            "success_criteria": ["объясняет выбор системы отсчёта"],
            "required_tasks": ["Сравните движение пассажира"],
            "assessment": ["взаимооценивание по критерию"],
            "homework": ["Домашнее задание: задача 3"],
            "duration_minutes": 40,
        }

    def test_exact_plan_content_passes(self):
        text = " ".join([
            "Механическое движение",
            "9.2.1.1 объяснять относительность движения",
            "объясняет выбор системы отсчёта",
            "Сравните движение пассажира",
            "взаимооценивание по критерию",
            "Домашнее задание: задача 3",
            "Время: 40 мин",
        ])
        errors, warnings = coverage.check_plan(text, self.plan)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_paraphrased_objective_is_rejected(self):
        text = "Механическое движение. Ученик рассказывает о движении."
        errors, _ = coverage.check_plan(text, self.plan)
        self.assertTrue(any("objective" in item for item in errors))

    def test_duration_mismatch_warns(self):
        text = " ".join([
            self.plan["topic"], *self.plan["objectives"], *self.plan["success_criteria"],
            *self.plan["required_tasks"], *self.plan["assessment"], *self.plan["homework"],
            "Время: 35 мин",
        ])
        errors, warnings = coverage.check_plan(text, self.plan)
        self.assertEqual([], errors)
        self.assertTrue(warnings)


class FontValidatorTests(unittest.TestCase):
    def make_pptx(self, typeface):
        handle = tempfile.NamedTemporaryFile(suffix=".pptx", delete=False)
        handle.close()
        path = Path(handle.name)
        xml = f'''<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:rPr typeface="{typeface}"/><a:t>Text</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'''
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("ppt/slides/slide1.xml", xml)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_arial_visible_text_passes(self):
        visible, _, _, _ = fonts.inspect_fonts(self.make_pptx("Arial"))
        self.assertEqual({"Arial"}, set(visible))

    def test_non_arial_visible_text_is_detectable(self):
        visible, _, _, _ = fonts.inspect_fonts(self.make_pptx("Calibri"))
        self.assertIn("Calibri", visible)
        self.assertNotEqual({"Arial"}, set(visible))


class StructureFontClassificationTests(unittest.TestCase):
    def shape(self, name, text, size_pt, top):
        size = int(size_pt * 100)
        top_emu = int(top * structure.EMU_PER_INCH / 96)
        xml = f'''<p:sld xmlns:p="{structure.PML}" xmlns:a="{structure.DML}">
        <p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="1" name="{name}"/>
        <p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="{top_emu}"/>
        <a:ext cx="1000000" cy="500000"/></a:xfrm></p:spPr><p:txBody><a:bodyPr/>
        <a:lstStyle/><a:p><a:r><a:rPr sz="{size}"/><a:t>{text}</a:t></a:r></a:p>
        </p:txBody></p:sp></p:spTree></p:cSld></p:sld>'''
        return structure.ET.fromstring(xml)

    def test_card_heading_is_body_not_slide_title(self):
        root = self.shape("methodtitle-1", "Картографиялық", 24, 220)
        self.assertEqual([], structure.font_warnings(
            root, 1, structure.DEFAULT_SLIDE_HEIGHT, 20
        ))

    def test_service_label_can_use_compact_font(self):
        root = self.shape("num-2", "2", 16, 46)
        self.assertEqual([], structure.font_warnings(
            root, 2, structure.DEFAULT_SLIDE_HEIGHT, 20
        ))

    def test_real_named_slide_title_below_minimum_warns(self):
        root = self.shape("title-2", "Сабақ тақырыбы", 26, 38)
        warnings = structure.font_warnings(
            root, 2, structure.DEFAULT_SLIDE_HEIGHT, 20
        )
        self.assertTrue(any("title 26 pt" in item for item in warnings))


if __name__ == "__main__":
    unittest.main()
