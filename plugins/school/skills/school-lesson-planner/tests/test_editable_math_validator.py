import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path


SCHOOL = Path(__file__).resolve().parents[3]
SCRIPT = SCHOOL / "scripts" / "validate_editable_math.py"
SPEC = importlib.util.spec_from_file_location("validate_editable_math", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


MATH = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A14 = "http://schemas.microsoft.com/office/drawing/2010/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"


class EditableMathValidatorTests(unittest.TestCase):
    def package(self, suffix, parts):
        handle = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        handle.close()
        path = Path(handle.name)
        with zipfile.ZipFile(path, "w") as package:
            for name, content in parts.items():
                package.writestr(name, content)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_accepts_native_docx_omml(self):
        xml = f'<w:document xmlns:w="urn:w" xmlns:m="{MATH}"><w:body><w:p><m:oMath><m:r><m:t>x+1</m:t></m:r></m:oMath></w:p></w:body></w:document>'
        result = MODULE.validate(self.package(".docx", {"word/document.xml": xml}))
        self.assertEqual(1, result["native_equations"])

    def test_rejects_docx_with_only_formula_image(self):
        xml = '<w:document xmlns:w="urn:w" xmlns:a="urn:a"><w:body><w:p><w:r><w:drawing><a:blip/></w:drawing></w:r></w:p></w:body></w:document>'
        with self.assertRaises(MODULE.MathValidationError):
            MODULE.validate(self.package(".docx", {"word/document.xml": xml}))

    def test_accepts_pptx_a14_math_inside_alternate_content(self):
        xml = f'<p:sld xmlns:p="urn:p" xmlns:mc="{MC}" xmlns:a14="{A14}" xmlns:m="{MATH}"><p:cSld><mc:AlternateContent><mc:Choice Requires="a14"><a14:m><m:oMath><m:r><m:t>x²</m:t></m:r></m:oMath></a14:m></mc:Choice><mc:Fallback><p:sp/></mc:Fallback></mc:AlternateContent></p:cSld></p:sld>'
        result = MODULE.validate(self.package(".pptx", {"ppt/slides/slide1.xml": xml}))
        self.assertEqual(1, result["native_equations"])

    def test_rejects_pptx_math_without_compatibility_container(self):
        xml = f'<p:sld xmlns:p="urn:p" xmlns:a14="{A14}" xmlns:m="{MATH}"><p:cSld><a14:m><m:oMath><m:r><m:t>x</m:t></m:r></m:oMath></a14:m></p:cSld></p:sld>'
        with self.assertRaises(MODULE.MathValidationError):
            MODULE.validate(self.package(".pptx", {"ppt/slides/slide1.xml": xml}))

    def test_exact_count_is_enforced(self):
        xml = f'<w:document xmlns:w="urn:w" xmlns:m="{MATH}"><w:body><m:oMath/><m:oMath/></w:body></w:document>'
        path = self.package(".docx", {"word/document.xml": xml})
        with self.assertRaises(MODULE.MathValidationError):
            MODULE.validate(path, expected_count=1)
        self.assertEqual(2, MODULE.validate(path, expected_count=2)["native_equations"])


if __name__ == "__main__":
    unittest.main()
