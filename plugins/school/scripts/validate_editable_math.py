#!/usr/bin/env python3
"""Validate that DOCX/PPTX equations use native Office Math markup."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A14_NS = "http://schemas.microsoft.com/office/drawing/2010/main"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


class MathValidationError(ValueError):
    pass


def _xml_parts(package: zipfile.ZipFile, prefix: str):
    for name in package.namelist():
        if name.startswith(prefix) and name.endswith(".xml"):
            try:
                yield name, ET.fromstring(package.read(name))
            except ET.ParseError as exc:
                raise MathValidationError(f"invalid XML in {name}: {exc}") from exc


def _count_docx_math(package: zipfile.ZipFile) -> tuple[int, list[str]]:
    count = 0
    parts: list[str] = []
    tag = f"{{{MATH_NS}}}oMath"
    for name, root in _xml_parts(package, "word/"):
        found = len(root.findall(f".//{tag}"))
        if found:
            count += found
            parts.append(name)
    return count, parts


def _count_pptx_math(package: zipfile.ZipFile) -> tuple[int, list[str]]:
    count = 0
    parts: list[str] = []
    alternate_tag = f"{{{MC_NS}}}AlternateContent"
    choice_tag = f"{{{MC_NS}}}Choice"
    text_math_tag = f"{{{A14_NS}}}m"
    office_math_tag = f"{{{MATH_NS}}}oMath"
    for name, root in _xml_parts(package, "ppt/slides/"):
        found = 0
        for alternate in root.findall(f".//{alternate_tag}"):
            for choice in alternate.findall(choice_tag):
                requires = set(choice.attrib.get("Requires", "").split())
                if "a14" not in requires:
                    continue
                for text_math in choice.findall(f".//{text_math_tag}"):
                    if text_math.find(f".//{office_math_tag}") is not None:
                        found += 1
        if found:
            count += found
            parts.append(name)
    return count, parts


def validate(path: Path, expected_min: int = 1, expected_count: int | None = None) -> dict:
    suffix = path.suffix.lower()
    if suffix not in {".docx", ".pptx"}:
        raise MathValidationError("supported formats: .docx and .pptx")
    if expected_min < 0 or (expected_count is not None and expected_count < 0):
        raise MathValidationError("expected counts must be non-negative")
    if not path.is_file():
        raise MathValidationError(f"file not found: {path}")
    try:
        with zipfile.ZipFile(path) as package:
            count, parts = (
                _count_docx_math(package) if suffix == ".docx" else _count_pptx_math(package)
            )
    except zipfile.BadZipFile as exc:
        raise MathValidationError("file is not a valid OOXML ZIP package") from exc
    if expected_count is not None and count != expected_count:
        raise MathValidationError(f"native equation count {count}, expected exactly {expected_count}")
    if count < expected_min:
        raise MathValidationError(f"native equation count {count}, expected at least {expected_min}")
    return {"format": suffix[1:], "native_equations": count, "parts": parts}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--expected-min", type=int, default=1)
    parser.add_argument("--expected-count", type=int)
    args = parser.parse_args(argv)
    try:
        result = validate(args.file, args.expected_min, args.expected_count)
    except MathValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        f"PASS: {result['native_equations']} native equation(s) in "
        f"{', '.join(result['parts'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
