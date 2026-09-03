#!/usr/bin/env python3
"""Require an explicit white background on every slide of a new school deck."""

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
SLIDE_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")


def slide_backgrounds(path: Path):
    results = []
    with zipfile.ZipFile(path) as archive:
        members = sorted(
            (name for name in archive.namelist() if SLIDE_RE.match(name)),
            key=lambda name: int(SLIDE_RE.match(name).group(1)),
        )
        for member in members:
            root = ET.fromstring(archive.read(member))
            color = root.find("./p:cSld/p:bg/p:bgPr/a:solidFill/a:srgbClr", NS)
            results.append((int(SLIDE_RE.match(member).group(1)), color.get("val", "").upper() if color is not None else None))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()
    if not args.pptx.is_file():
        print(f"ERROR: file not found: {args.pptx}", file=sys.stderr)
        return 2
    try:
        backgrounds = slide_backgrounds(args.pptx)
    except (OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"ERROR: cannot inspect PPTX: {exc}", file=sys.stderr)
        return 2
    errors = [number for number, color in backgrounds if color != "FFFFFF"]
    if errors:
        print("FAIL: slides without explicit #FFFFFF background: " + ", ".join(map(str, errors)))
        return 1
    print(f"PASS: all {len(backgrounds)} slides use explicit #FFFFFF background.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
