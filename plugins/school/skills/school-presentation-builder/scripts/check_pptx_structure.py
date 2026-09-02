#!/usr/bin/env python3
"""Check technical structure and common quality risks in a PPTX file."""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

PML = "http://schemas.openxmlformats.org/presentationml/2006/main"
DML = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_TYPES = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"p": PML, "a": DML, "r": REL, "pr": PKG_REL, "ct": CONTENT_TYPES}
SLIDE_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
EMU_PER_INCH = 914400
DEFAULT_SLIDE_HEIGHT = int(7.5 * EMU_PER_INCH)
SOURCE_PREFIX_RE = re.compile(
    r"^\s*(?:источник(?:и)?|дереккөз(?:дер)?|source(?:s)?)\s*:",
    re.IGNORECASE,
)
SOURCE_LINK_RE = re.compile(r"(?:https?://|www\.|\bdoi\s*:)", re.IGNORECASE)
CAPTION_RE = re.compile(
    r"^(рис(?:унок)?\.?|сурет|figure|fig\.?|кесте|таблица|table|диаграмма|chart)\b",
    re.IGNORECASE,
)
TITLE_NAME_RE = re.compile(
    r"^(?:deck[-_]?title|slide[-_]?title|title(?:[-_]\d+)?|heading(?:[-_]\d+)?)$",
    re.IGNORECASE,
)
SERVICE_NAME_RE = re.compile(
    r"^(?:num|eyebrow|lab|label|flowlab|anst|mat-title|methodq|choice|"
    r"honesty|signal|footer|page)(?:-|$)",
    re.IGNORECASE,
)
NOTE_FIELDS = {
    "scenario": re.compile(
        r"(сценари|реплик|действи[ея]\s+учител|мұғалім|teacher|say|show)", re.IGNORECASE
    ),
    "time": re.compile(r"(\b\d+\s*(?:мин|minute|min\b)|уақыт|время|time)", re.IGNORECASE),
    "answer": re.compile(
        r"(ожидаем\w*\s+ответ|ответ|ключ|күтілетін\s+жауап|жауап|expected\s+answer|answer\s+key)",
        re.IGNORECASE,
    ),
    "assessment": re.compile(
        r"(оцениван|критери|дескриптор|бағалау|assessment|feedback)", re.IGNORECASE
    ),
}


def qname(namespace: str, name: str) -> str:
    return f"{{{namespace}}}{name}"


def read_xml(archive: zipfile.ZipFile, member: str) -> ET.Element:
    try:
        return ET.fromstring(archive.read(member))
    except KeyError as exc:
        raise RuntimeError(f"missing required part: {member}") from exc
    except ET.ParseError as exc:
        raise RuntimeError(f"invalid XML in {member}: {exc}") from exc


def resolve_target(source: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), target))


def relationships(
    archive: zipfile.ZipFile, source: str
) -> list[tuple[str, str, str]]:
    source_path = PurePosixPath(source)
    rels_path = str(
        source_path.parent / "_rels" / f"{source_path.name}.rels"
    )
    if rels_path not in archive.namelist():
        return []
    root = read_xml(archive, rels_path)
    result = []
    for rel in root.findall("pr:Relationship", NS):
        if rel.get("TargetMode") == "External":
            continue
        result.append(
            (
                rel.get("Id", ""),
                rel.get("Type", ""),
                resolve_target(source, rel.get("Target", "")),
            )
        )
    return result


def source_for_rels(rels_path: str) -> str | None:
    """Return the package part that owns a .rels file."""
    path = PurePosixPath(rels_path)
    if path.name == ".rels" and str(path.parent) == "_rels":
        return ""
    if path.parent.name != "_rels" or not path.name.endswith(".rels"):
        return None
    return str(path.parent.parent / path.name.removesuffix(".rels"))


def package_errors(archive: zipfile.ZipFile, names: set[str]) -> list[str]:
    """Validate content-type declarations and every internal relationship."""
    errors: list[str] = []
    content_types = read_xml(archive, "[Content_Types].xml")
    defaults: dict[str, str] = {}
    overrides: dict[str, str] = {}

    for node in content_types.findall("ct:Default", NS):
        extension = (node.get("Extension") or "").lower()
        content_type = node.get("ContentType") or ""
        if not extension or not content_type:
            errors.append("invalid Default entry in [Content_Types].xml")
            continue
        defaults[extension] = content_type

    for node in content_types.findall("ct:Override", NS):
        raw_part = node.get("PartName") or ""
        content_type = node.get("ContentType") or ""
        part = raw_part.lstrip("/")
        if not part or not content_type:
            errors.append("invalid Override entry in [Content_Types].xml")
            continue
        if part in overrides and overrides[part] != content_type:
            errors.append(f"conflicting content types for part: {part}")
        overrides[part] = content_type
        if part not in names:
            errors.append(
                f"[Content_Types].xml declares missing part: {part}"
            )

    for name in sorted(names):
        if (
            name.endswith("/")
            or name == "[Content_Types].xml"
            or name.endswith(".rels")
        ):
            continue
        extension = PurePosixPath(name).suffix.lstrip(".").lower()
        if name not in overrides and extension not in defaults:
            errors.append(f"package part has no content type: {name}")

    for rels_path in sorted(name for name in names if name.endswith(".rels")):
        source = source_for_rels(rels_path)
        if source is None:
            errors.append(f"relationship part is in an invalid location: {rels_path}")
            continue
        root = read_xml(archive, rels_path)
        for rel in root.findall("pr:Relationship", NS):
            if rel.get("TargetMode") == "External":
                continue
            target = rel.get("Target") or ""
            if not target:
                errors.append(f"{rels_path} contains an empty relationship target")
                continue
            resolved = resolve_target(source, target)
            if resolved not in names:
                owner = source or "package root"
                errors.append(f"{owner} references missing part: {resolved}")

    return errors


def slide_text(root: ET.Element) -> str:
    return " ".join(
        text.strip()
        for node in root.findall(".//a:t", NS)
        if (text := node.text) and text.strip()
    )


def shape_text(shape: ET.Element) -> str:
    return slide_text(shape)


def shape_name(shape: ET.Element) -> str:
    node = shape.find("./p:nvSpPr/p:cNvPr", NS)
    return "" if node is None else str(node.get("name", ""))


def shape_y(shape: ET.Element) -> int | None:
    off = shape.find("./p:spPr/a:xfrm/a:off", NS)
    if off is None:
        off = shape.find("./p:spPr/a:xfrm/a:chOff", NS)
    if off is None:
        return None
    try:
        return int(off.get("y", ""))
    except ValueError:
        return None


def has_title(root: ET.Element, slide_height: int) -> bool:
    for shape in root.findall(".//p:sp", NS):
        placeholder = shape.find("./p:nvSpPr/p:nvPr/p:ph", NS)
        if placeholder is not None and placeholder.get("type", "") in {
            "title",
            "ctrTitle",
        }:
            if slide_text(shape):
                return True
        text = shape_text(shape)
        name = shape_name(shape)
        sizes = declared_font_sizes(shape)
        y = shape_y(shape)
        if (
            text
            and len(text) <= 220
            and sizes
            and (
                TITLE_NAME_RE.search(name)
                or (
                    y is not None
                    and y <= slide_height * 0.18
                    and max(sizes) >= 28
                )
            )
        ):
            return True
    return False


def declared_font_sizes(root: ET.Element) -> list[float]:
    sizes = []
    for element in root.iter():
        value = element.get("sz")
        if value and element.tag in {
            qname(DML, "rPr"),
            qname(DML, "defRPr"),
            qname(DML, "endParaRPr"),
        }:
            try:
                sizes.append(int(value) / 100)
            except ValueError:
                continue
    return sizes


def text_kind(
    text: str, name: str, y: int | None, slide_height: int, is_title: bool
) -> str:
    if is_title:
        return "title"
    compact = " ".join(text.split())
    if SERVICE_NAME_RE.search(name):
        return "service"
    if SOURCE_PREFIX_RE.search(compact) or SOURCE_LINK_RE.search(compact):
        return "source"
    if (
        y is not None
        and y >= slide_height * 0.80
        and len(compact) <= 300
        and re.search(
            r"\b(?:источник|дереккөз|source)\b", compact, re.IGNORECASE
        )
    ):
        return "source"
    if (y is not None and y >= slide_height * 0.88) or re.fullmatch(
        r"\s*(?:©.*|\d{1,3})\s*", text
    ):
        return "service"
    if CAPTION_RE.search(text):
        return "caption"
    return "body"


def font_warnings(
    root: ET.Element, slide_number: int, slide_height: int, min_body_font: float
) -> list[str]:
    thresholds = {
        "title": 28.0,
        "body": min_body_font,
        "caption": 16.0,
        "source": 13.0,
        "service": 13.0,
    }
    issues: dict[str, float] = {}
    for shape in root.findall(".//p:sp", NS):
        text = shape_text(shape)
        sizes = declared_font_sizes(shape)
        if not text or not sizes:
            continue
        placeholder = shape.find("./p:nvSpPr/p:nvPr/p:ph", NS)
        placeholder_title = placeholder is not None and placeholder.get(
            "type", ""
        ) in {"title", "ctrTitle"}
        name = shape_name(shape)
        y = shape_y(shape)
        visual_title = (
            TITLE_NAME_RE.search(name) is not None
            or (
                y is not None
                and y <= slide_height * 0.18
                and max(sizes) >= 28
                and len(text) <= 220
            )
        )
        kind = text_kind(
            text, name, y, slide_height, placeholder_title or visual_title
        )
        threshold = thresholds[kind]
        smallest = min(sizes)
        if smallest < threshold:
            issues[kind] = min(smallest, issues.get(kind, smallest))
    if not issues:
        return []
    details = ", ".join(
        f"{kind} {size:g} pt (target ≥{thresholds[kind]:g})"
        for kind, size in sorted(issues.items())
    )
    return [f"slide {slide_number} has undersized text: {details}"]


def meaningful_notes(root: ET.Element) -> str:
    parts = []
    for shape in root.findall(".//p:sp", NS):
        placeholder = shape.find("./p:nvSpPr/p:nvPr/p:ph", NS)
        placeholder_type = placeholder.get("type", "") if placeholder is not None else ""
        if placeholder_type in {"sldImg", "hdr", "ftr", "dt", "sldNum"}:
            continue
        text = shape_text(shape)
        if text:
            parts.append(text)
    return " ".join(parts).strip()


def inspect(
    path: Path, expected_slides: int, min_body_font: float
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                return [f"corrupt ZIP member: {bad_member}"], warnings

            names = set(archive.namelist())
            for required in ("[Content_Types].xml", "ppt/presentation.xml"):
                if required not in names:
                    errors.append(f"missing required part: {required}")
            if errors:
                return errors, warnings

            errors.extend(package_errors(archive, names))

            presentation = read_xml(archive, "ppt/presentation.xml")
            slide_size = presentation.find("./p:sldSz", NS)
            try:
                slide_height = int(slide_size.get("cy", "")) if slide_size is not None else DEFAULT_SLIDE_HEIGHT
            except ValueError:
                slide_height = DEFAULT_SLIDE_HEIGHT

            slide_members = sorted(
                (name for name in names if SLIDE_RE.match(name)),
                key=lambda name: int(SLIDE_RE.match(name).group(1)),  # type: ignore[union-attr]
            )
            if len(slide_members) != expected_slides:
                errors.append(
                    f"expected {expected_slides} slides, found {len(slide_members)}"
                )

            for index, member in enumerate(slide_members, start=1):
                root = read_xml(archive, member)
                text = slide_text(root)
                graphic_count = len(root.findall(".//p:pic", NS)) + len(
                    root.findall(".//p:graphicFrame", NS)
                )
                if not text and graphic_count == 0:
                    errors.append(f"slide {index} is empty")
                if not has_title(root, slide_height):
                    warnings.append(
                        f"slide {index} has no title placeholder or upper large title"
                    )

                warnings.extend(
                    font_warnings(root, index, slide_height, min_body_font)
                )

                rels = relationships(archive, member)
                note_targets = [
                    target for _, rel_type, target in rels if rel_type.endswith("/notesSlide")
                ]
                if text and not note_targets:
                    errors.append(f"slide {index} has content but no speaker notes")
                for target in note_targets:
                    if target not in names:
                        errors.append(
                            f"slide {index} references missing notes part: {target}"
                        )
                        continue
                    notes_text = meaningful_notes(read_xml(archive, target))
                    if len(notes_text) < 40 or len(notes_text.split()) < 7:
                        errors.append(
                            f"slide {index} speaker notes have no meaningful teaching script"
                        )
                        continue
                    missing_fields = [
                        field
                        for field, pattern in NOTE_FIELDS.items()
                        if not pattern.search(notes_text)
                    ]
                    if missing_fields:
                        warnings.append(
                            f"slide {index} speaker notes may be missing: "
                            + ", ".join(missing_fields)
                        )

                embed_ids = {
                    node.get(qname(REL, "embed"))
                    for node in root.findall(".//*[@r:embed]", NS)
                }
                rel_map = {rel_id: target for rel_id, _, target in rels}
                for rel_id in sorted(value for value in embed_ids if value):
                    target = rel_map.get(rel_id)
                    if not target:
                        errors.append(
                            f"slide {index} has unresolved embedded object {rel_id}"
                        )
                    elif target not in names:
                        errors.append(
                            f"slide {index} references missing embedded file: {target}"
                        )

    except zipfile.BadZipFile:
        errors.append("file is not a valid PPTX/ZIP archive")
    except (OSError, RuntimeError) as exc:
        errors.append(str(exc))

    return list(dict.fromkeys(errors)), list(dict.fromkeys(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check OOXML package integrity, slide count, notes, empty slides, "
            "titles, fonts, and links."
        )
    )
    parser.add_argument("pptx", type=Path, help="PowerPoint file to inspect")
    parser.add_argument("--expected-slides", type=int, default=10)
    parser.add_argument(
        "--min-body-font",
        type=float,
        default=20,
        help="minimum body-text size; captions use 16 pt and sources/service text 13 pt",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat every warning as a failing quality gate",
    )
    args = parser.parse_args()

    if not args.pptx.is_file():
        print(f"ERROR: file not found: {args.pptx}", file=sys.stderr)
        return 2
    if args.expected_slides < 1 or args.min_body_font <= 0:
        print("ERROR: expected slides and minimum font must be positive", file=sys.stderr)
        return 2

    errors, warnings = inspect(
        args.pptx, args.expected_slides, args.min_body_font
    )
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")

    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    if args.strict and warnings:
        print(f"FAIL: strict mode rejects {len(warnings)} warning(s).")
        return 1
    print(f"PASS: structure checks completed with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
