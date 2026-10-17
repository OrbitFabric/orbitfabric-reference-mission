#!/usr/bin/env python3
"""Verify bounded R3 source preservation and local documentation assets."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "engineering-stories/03-standards-backed-path-to-cfs"
DOC = ROOT / "docs/engineering-stories/r3-eds-cfs"

EXPECTED = {
    "b10-original-failure.log": (
        "075a8db5e044bc6dcf733815a58ff438809b97efe3bd2143a265881f13e96f55",
        ("86-write_dds_idl.lua:87: assertion failed!",),
    ),
    "b10-corrected-proof.log": (
        "b571ca9d4ae58d0f1e5423e3a01d90019c5a1ebd74fe4b3c5d888adc49ebdec6",
        ("SEDS tool complete", "attribute 'basetype' could not be resolved"),
    ),
    "p2-native-closed-loop.log": (
        "1fbbbda9d83a478c850b7e29360eab29b4c05a6e2be6ca1f3313dff2766555e2",
        ("EDS decoder observed PayloadEnabled=true",),
    ),
    "p3-unknown-fc-characterization.log": (
        "d23431115321a62e5c72459c058ed78043e019d1cb86fd506591405154f2642c",
        (
            "unknown_function_code=127",
            "valid_handler=payload.enable",
            "P3 characterization acceptance PASS",
        ),
    ),
}

FIGURES = tuple(f"{i:02d}-{name}.svg" for i, name in [
    (1, "standards-backed-path"),
    (2, "one-bit-boolean8"),
    (3, "topic-allocation"),
    (4, "unknown-fc-dispatch"),
    (5, "authority-matrix"),
])

def check() -> None:
    for name, (expected, markers) in EXPECTED.items():
        path = PKG / "evidence" / name
        content = path.read_bytes()
        actual = hashlib.sha256(content).hexdigest()
        assert actual == expected, f"evidence changed or digest incorrect: {name}: {actual}"
        text = content.decode("utf-8")
        for marker in markers:
            assert marker in text, f"source marker missing: {name}: {marker}"

    for name in FIGURES:
        svg = DOC / "images" / name
        root = ET.parse(svg).getroot()
        ns = {"s": "http://www.w3.org/2000/svg"}
        assert root.tag.endswith("svg"), f"not SVG: {name}"
        assert root.find("s:title", ns) is not None, f"missing SVG title: {name}"
        assert root.find("s:desc", ns) is not None, f"missing SVG description: {name}"

    for file in ("index.md", "technical-deep-dive.md"):
        page = DOC / file
        text = page.read_text(encoding="utf-8")
        for filename in re.findall(r"\]\(images/([-\w]+\.svg)\)", text):
            assert filename in FIGURES, f"unregistered figure {filename} in {file}"
            assert (DOC / "images" / filename).is_file()
        assert "\u2014" not in text, f"long dash in R3 narrative: {file}"

    assert (PKG / "reference-project" / "README.md").is_file()
    assert (PKG / "evidence" / "README.md").is_file()
    assert "r3-eds-cfs/index.md" in (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    index = (DOC / "index.md").read_text(encoding="utf-8")
    assert "acceptance_semantics=CHARACTERIZATION" in index
    assert "prospective_automatic_rejection_property=FALSIFIED" in index
    print("R3 source evidence, SHA-256, XML figures and narrative guards: PASS")

if __name__ == "__main__":
    try:
        check()
    except (AssertionError, OSError, ET.ParseError, UnicodeError) as error:
        print(f"R3 proof check FAILED: {error}", file=sys.stderr)
        sys.exit(1)
