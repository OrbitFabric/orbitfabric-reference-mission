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

NATIVE = {
    "p2-original-invalid-topic.log": "207643c4820e25e44311f78c29b3922977af0017e4151587e6257ab65d6a1b8c",
    "p2-a-acceptance.txt": "06643909191411f4b6267400f49c785d385d5801f98340f472bb205c72e0bfb1",
    "p3-acceptance.txt": "3e7076d4500065a42352325af430e61e82f7ac5b7fda87396320438fe19fd4e3",
    "p3-unknown-function-code-result.txt": "f8c968f809a0195913c827ac92c1948fad99a5f898709042076b75a8959bd571",
    "p3-edslib-causal-control.txt": "2da25c8b2f8b0123fbba214e3df16d1cf8736fb85238a7b5f32656486e833223",
    "p2-b-valid-range-observation.tsv": "17ec1d45578e9bb554694cbb188ec760d10cd89610504a6ebc7353a38deb4cc7",
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

    for name, expected in NATIVE.items():
        actual = hashlib.sha256((PKG / "evidence" / name).read_bytes()).hexdigest()
        assert actual == expected, f"original native record digest mismatch: {name}: {actual}"

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

    r3_markdown = (
        DOC / "index.md",
        DOC / "technical-deep-dive.md",
        PKG / "README.md",
        PKG / "reference-project" / "README.md",
    )
    for page in r3_markdown:
        markdown = page.read_text(encoding="utf-8")
        assert (chr(92) + chr(96)) not in markdown, f"escaped backtick in {page}"
        r3_repo_root = "https://github.com/OrbitFabric/orbitfabric-reference-mission/"
        for link_kind in ("blob", "tree"):
            unsafe = r3_repo_root + f"{link_kind}/main/engineering-stories/03-standards-backed-path-to-cfs"
            assert unsafe not in markdown, f"R3 evidence link points to unmerged main: {page}"

        code_fences = re.findall(r"(?m)^" + chr(96) * 3, markdown)
        assert len(code_fences) % 2 == 0, f"unbalanced fenced blocks: {page}"

    telemetry_svg = ET.parse(DOC / "images/03-topic-allocation.svg").getroot()
    visible_labels = [node.text for node in telemetry_svg.iter() if node.tag.endswith("text")]
    assert "Corrected selected-mission binding" not in visible_labels, "unwrapped SVG label"
    assert "Corrected selected-mission" in visible_labels, "first wrapped title line missing"
    assert "binding" in visible_labels, "second wrapped title line missing"
    assert (PKG / "reference-project" / "README.md").is_file()
    assert (PKG / "evidence" / "README.md").is_file()
    assert (PKG / "evidence" / "NATIVE-ARTIFACTS.md").is_file()
    assert "r3-eds-cfs/index.md" in (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert (DOC / "technical-deep-dive.md").is_file(), "missing Technical Deep Dive page"
    cover = DOC / "images" / "r3-cover.jpg"
    assert cover.is_file(), "approved social cover missing"
    assert cover.stat().st_size == 194398, "unexpected social cover size"
    assert hashlib.sha256(cover.read_bytes()).hexdigest() == (
        "7fa104c07fc8ef7b226313fbf65dd0c8c2b337d28797506a01a87239d7bb51e3"
    ), "approved social cover has changed"
    index = (DOC / "index.md").read_text(encoding="utf-8")
    assert "acceptance_semantics=CHARACTERIZATION" in index
    assert "prospective_automatic_rejection_property=FALSIFIED" in index
    assert "story_social_image: engineering-stories/r3-eds-cfs/images/r3-cover.jpg" in index
    assert "](images/r3-cover.jpg)" in index, "approved cover not visible in Story"
    assert "[Technical Deep Dive](technical-deep-dive.md)" in index
    assert index.index("[Technical Deep Dive](technical-deep-dive.md)") < index.index("[Native Proof Sources & Evidence]"), "Deep Dive should be first footer link"
    assert "[EdsLib Upstream Question #120](https://github.com/nasa/EdsLib/issues/120)" in index
    assert "So I opened [NASA EdsLib issue #120]" in index
    assert "intended dispatch semantics" in index
    technical = (DOC / "technical-deep-dive.md").read_text(encoding="utf-8")
    assert "## 6. Source-level dispatch trace" in technical
    for required in (
        "CFE_EDSMSG_Dispatch_CheckActualBufferType()",
        "EdsLib_DataTypeDB_IdentifyBufferWithSize()",
        "EDSLIB_NO_MATCHING_VALUE",
        "EdsLib_DataTypeDB_GetDerivedInfo()",
        "NumDerivatives",
        "CFE_STATUS_UNKNOWN_MSG_ID",
        "https://github.com/nasa/EdsLib/issues/120",
    ):
        assert required in technical, f"missing dispatcher source analysis: {required}"
    assert "images/03-topic-allocation.svg" not in technical, "duplicate topic figure in Deep Dive"
    assert "images/05-authority-matrix.svg" not in technical, "duplicate ownership figure in Deep Dive"
    assert "images/04-unknown-fc-dispatch.svg" in technical, "missing P3 context figure"
    print("R3 source evidence, SHA-256, XML figures and narrative guards: PASS")

if __name__ == "__main__":
    try:
        check()
    except (AssertionError, OSError, ET.ParseError, UnicodeError) as error:
        print(f"R3 proof check FAILED: {error}", file=sys.stderr)
        sys.exit(1)
