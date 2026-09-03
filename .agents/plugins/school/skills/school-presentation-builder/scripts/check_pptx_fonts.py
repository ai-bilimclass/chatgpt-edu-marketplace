#!/usr/bin/env python3
"""Check Arial in visible PPTX text without failing on technical theme fonts."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree

DML = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"a": DML}

VISIBLE_PARTS = (
    re.compile(r"^ppt/slides/slide\d+\.xml$"),
    re.compile(r"^ppt/notesSlides/notesSlide\d+\.xml$"),
    re.compile(r"^ppt/charts/[^/]+\.xml$"),
    re.compile(r"^ppt/diagrams/[^/]+\.xml$"),
)


def is_visible_part(member: str) -> bool:
    """Return whether the XML part can contain user-visible text."""
    return any(pattern.match(member) for pattern in VISIBLE_PARTS)


def is_theme_placeholder(family: str) -> bool:
    """Ignore OOXML theme references such as +mn-lt and +mj-ea."""
    return family.casefold().startswith(("+mn-", "+mj-"))


def inspect_fonts(
    pptx_path: Path,
) -> tuple[
    dict[str, list[str]],
    dict[str, list[str]],
    dict[str, set[str]],
    int,
]:
    visible: dict[str, list[str]] = defaultdict(list)
    technical: dict[str, list[str]] = defaultdict(list)
    theme_latin: dict[str, set[str]] = {"majorLatin": set(), "minorLatin": set()}
    xml_files = 0

    with zipfile.ZipFile(pptx_path) as archive:
        for member in archive.namelist():
            if not member.startswith("ppt/") or not member.endswith(".xml"):
                continue
            xml_files += 1
            try:
                root = ElementTree.fromstring(archive.read(member))
            except ElementTree.ParseError as exc:
                raise RuntimeError(f"Invalid XML in {member}: {exc}") from exc

            destination = visible if is_visible_part(member) else technical
            if member.startswith("ppt/theme/"):
                for role, xpath in (
                    ("majorLatin", ".//a:fontScheme/a:majorFont/a:latin"),
                    ("minorLatin", ".//a:fontScheme/a:minorFont/a:latin"),
                ):
                    for node in root.findall(xpath, NS):
                        family = (node.get("typeface") or "").strip()
                        if family and not is_theme_placeholder(family):
                            theme_latin[role].add(family)
            for element in root.iter():
                for attribute, value in element.attrib.items():
                    if attribute.rsplit("}", 1)[-1] != "typeface":
                        continue
                    family = value.strip()
                    if family and not is_theme_placeholder(family):
                        destination[family].append(member)

    return visible, technical, theme_latin, xml_files


def print_fonts(title: str, fonts: dict[str, list[str]]) -> None:
    print(title)
    for family in sorted(fonts, key=str.casefold):
        locations = sorted(set(fonts[family]))
        preview = ", ".join(locations[:5])
        suffix = "" if len(locations) <= 5 else ", …"
        print(f"- {family}: {preview}{suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify Arial in visible slide, table, chart, diagram, and notes text. "
            "Report technical theme/master fonts as warnings."
        )
    )
    parser.add_argument("pptx", type=Path, help="PowerPoint file to inspect")
    args = parser.parse_args()

    if not args.pptx.is_file():
        print(f"ERROR: file not found: {args.pptx}", file=sys.stderr)
        return 2

    try:
        visible, technical, theme_latin, xml_files = inspect_fonts(args.pptx)
    except (zipfile.BadZipFile, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    visible_non_arial = {
        family: locations
        for family, locations in visible.items()
        if family.casefold() != "arial"
    }
    technical_non_arial = {
        family: locations
        for family, locations in technical.items()
        if family.casefold() != "arial"
    }

    if visible_non_arial:
        print_fonts(
            "FAIL: non-Arial typefaces found in visible text:",
            visible_non_arial,
        )
    elif not visible:
        print(
            "WARNING: no explicit typeface declarations were found in visible "
            "text; formatting may be inherited from the theme or master."
        )

    if technical_non_arial:
        declaration_count = sum(map(len, technical_non_arial.values()))
        primary = "; ".join(
            f"{role}: {', '.join(sorted(families, key=str.casefold))}"
            for role, families in theme_latin.items()
            if any(family.casefold() != "arial" for family in families)
        )
        detail = f" Theme Latin fonts — {primary}." if primary else ""
        print(
            "WARNING: "
            f"{declaration_count} non-Arial technical theme/master font "
            f"declaration(s) found; visible text is unaffected.{detail}"
        )

    if visible_non_arial:
        return 1

    visible_declarations = sum(map(len, visible.values()))
    print(
        f"PASS: no non-Arial typefaces found in visible text "
        f"({visible_declarations} explicit declarations across "
        f"{xml_files} XML files)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
