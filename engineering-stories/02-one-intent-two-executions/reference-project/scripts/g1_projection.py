#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import tempfile
from pathlib import Path
from typing import Any

import yaml
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from g0_contracts import COMMAND_ID, resolve_command_atom
from orbitfabric.conformance.scenario_projection_accounting import verify_bundle

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
PROFILE_PATH = PROJECT_ROOT / "profile" / "pwnsat-flat-sat-health-check.yaml"
TARGET_BASELINE_PATH = PROJECT_ROOT / "target" / "pwnsat-source-baseline.json"
RETAINED_DIR = PROJECT_ROOT / "artifacts" / "g1"

MAPPING_ID = "mapping.r2.pwnsat.health-check.status"
INTEGRATION_ID = "orbitfabric-r2-pwnsat-story"
INTEGRATION_SCHEMA_VERSION = "0.1-story"
PACKAGE_ID = "r2-pwnsat-story-integration-package"
PACKAGE_VERSION = "0.1.0"
PROFILE_ID = "r2-pwnsat-flatsat-health-check"
PROFILE_INSTANCE_VERSION = "0.1.0"

TARGET_REPOSITORY = "Pwnsat/FlatSat"
TARGET_COMMIT = "b5ac0f2ba5e7bd60fbb6994f681c28053777628e"
TARGET_APID = 0x0C
TARGET_COMMAND = "STATUS"
TARGET_SYMBOL = "SPP_APID_TC_GET_STATUS"

SUPPORTED_SEQUENCE_FLAGS = {"unsegmented": 3}
SUPPORTED_SECURE_LINK_INTENT = "firmware_default_enabled"

STIMULUS_FILENAME = "pwnsat-health-check.tc.bin"
MAPPING_FILENAME = "pwnsat-health-check.mapping.json"
ACCOUNTING_FILENAME = "scenario_projection_accounting.json"
RESULT_FILENAME = "integration_result.json"


class G1Error(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise G1Error(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_profile() -> tuple[dict[str, Any], bytes]:
    raw = PROFILE_PATH.read_bytes()
    value = yaml.safe_load(raw)
    if not isinstance(value, dict):
        raise G1Error("Projection Profile must be a mapping")
    if value.get("kind") != "orbitfabric.projection_profile":
        raise G1Error("unexpected Projection Profile kind")
    if value.get("profile_version") != "0.1-candidate":
        raise G1Error("unsupported Projection Profile version")
    if (value.get("profile") or {}).get("id") != PROFILE_ID:
        raise G1Error("unexpected Profile id")
    if (value.get("profile") or {}).get("version") != PROFILE_INSTANCE_VERSION:
        raise G1Error("unexpected Profile instance version")
    integration = value.get("integration") or {}
    if (
        integration.get("id") != INTEGRATION_ID
        or integration.get("schema_version") != INTEGRATION_SCHEMA_VERSION
    ):
        raise G1Error("unexpected integration identity")
    bindings = value.get("bindings") or []
    matches = [
        item
        for item in bindings
        if item.get("id") == MAPPING_ID
        and item.get("intent") == "project"
        and {"domain": "commands", "id": COMMAND_ID}
        in (item.get("sources") or [])
    ]
    if len(matches) != 1:
        raise G1Error(
            "Profile must contain exactly one canonical health-check projection binding"
        )
    config = matches[0].get("config") or {}
    if (
        config.get("target_command") != TARGET_COMMAND
        or config.get("target_symbol") != TARGET_SYMBOL
        or config.get("apid") != TARGET_APID
    ):
        raise G1Error("Profile target mapping differs from pinned source facts")
    settings = value.get("settings")
    if not isinstance(settings, dict):
        raise G1Error("Projection Profile settings must be a mapping")
    required_settings = {
        "target_repository",
        "target_commit",
        "sequence_count",
        "sequence_flags",
        "secondary_header",
        "secure_link",
    }
    missing = sorted(required_settings - set(settings))
    if missing:
        raise G1Error(
            "Projection Profile is missing required settings: " + ", ".join(missing)
        )
    if (
        settings["target_repository"] != TARGET_REPOSITORY
        or settings["target_commit"] != TARGET_COMMIT
    ):
        raise G1Error("Profile target baseline differs from pinned source baseline")
    return value, raw


def validate_target_baseline(value: dict[str, Any]) -> None:
    if value.get("kind") != "orbitfabric.reference_mission.pwnsat_source_baseline":
        raise G1Error("unexpected PWNSAT source-baseline kind")
    if value.get("format_version") != "0.1-story":
        raise G1Error("unsupported source-baseline version")
    if (
        value.get("repository") != TARGET_REPOSITORY
        or value.get("commit_sha") != TARGET_COMMIT
    ):
        raise G1Error("unexpected PWNSAT repository/commit")
    cmd = value.get("target_command") or {}
    if cmd != {
        "name": TARGET_COMMAND,
        "symbol": TARGET_SYMBOL,
        "apid": TARGET_APID,
        "logical_payload_hex": "",
        "response_builder": "telemetrySPPTransmitMissionStatus",
    }:
        raise G1Error("target command facts differ from reviewed PWNSAT source")
    correspondence = value.get("semantic_correspondence") or {}
    if (
        correspondence.get("orbitfabric_operation") != COMMAND_ID
        or correspondence.get("pwnsat_operation")
        != "STATUS / SPP_APID_TC_GET_STATUS"
        or not correspondence.get("justification")
        or not correspondence.get("limit")
        or not correspondence.get("ambiguity")
    ):
        raise G1Error("target semantic correspondence is missing or incomplete")
    if not value.get("projection_scope"):
        raise G1Error("target projection scope is not explicit")
    packet = value.get("packet_projection") or {}
    secure = packet.get("secure_link") or {}
    expected = {
        "ccsds_version": 0,
        "packet_type": "TC",
        "secondary_header": False,
        "sequence_flags": 3,
    }
    for key, expected_value in expected.items():
        if packet.get(key) != expected_value:
            raise G1Error(f"unexpected packet projection field {key}")
    if (
        secure.get("enabled") is not True
        or secure.get("algorithm") != "AES-128-ECB"
        or secure.get("key_ascii") != "PWNsatLabKey1234"
        or secure.get("length_prefix_bytes") != 2
        or secure.get("padding") != "zero-to-16-byte-block"
    ):
        raise G1Error("unexpected secure-link projection facts")
    required_sources = {
        ("Firmware/mission.h", "13dd456f26f83ac3b186065c3f7d12e60234afa0"),
        ("Firmware/worker.cpp", "1c3b7e9db506732f77c3214a38b297c0d8625323"),
        ("Firmware/spp.h", "ebd15fc88edcd9c77d2d421eeb890a700c291dc9"),
        ("Firmware/spp.cpp", "a5ec274e7f3b2fd72da432ff4211d30c809e6131"),
        ("Firmware/secure_link.cpp", "a02de14460d41961f0acaf40178bfd68fae686be"),
    }
    actual_sources = {
        (item.get("path"), item.get("blob_sha"))
        for item in value.get("source_files") or []
    }
    if actual_sources != required_sources:
        raise G1Error(
            "pinned PWNSAT source-file identities differ from reviewed baseline"
        )


def resolve_iiss_command(
    iiss_dir: Path, manifest: dict[str, Any]
) -> dict[str, Any]:
    if (
        manifest.get("kind") != "orbitfabric.integration_input_set"
        or manifest.get("input_set_version") != "0.1-candidate"
    ):
        raise G1Error("unsupported Core Integration Input Set")
    if manifest.get("load_result") != "loaded":
        raise G1Error("IISS mission did not load")
    entity_record = next(
        (
            item
            for item in manifest.get("surfaces") or []
            if item.get("role") == "entity_index"
        ),
        None,
    )
    if not entity_record or entity_record.get("status") != "available":
        raise G1Error("IISS entity_index is unavailable")
    entity_index = load_json(iiss_dir / entity_record["path"])
    matches = [
        item
        for item in entity_index.get("entities") or []
        if item.get("domain") == "commands"
        and item.get("id") == COMMAND_ID
    ]
    if len(matches) != 1:
        raise G1Error(
            f"expected one IISS command {COMMAND_ID}, found {len(matches)}"
        )
    return matches[0]


def resolve_profile_projection(
    profile: dict[str, Any], target_baseline: dict[str, Any]
) -> dict[str, Any]:
    settings = profile.get("settings")
    if not isinstance(settings, dict):
        raise G1Error("Projection Profile settings must be a mapping")

    sequence_count = settings.get("sequence_count")
    if (
        isinstance(sequence_count, bool)
        or not isinstance(sequence_count, int)
        or not 0 <= sequence_count <= 0x3FFF
    ):
        raise G1Error("Profile sequence_count must be an integer in [0, 16383]")

    sequence_flags_name = settings.get("sequence_flags")
    if sequence_flags_name not in SUPPORTED_SEQUENCE_FLAGS:
        raise G1Error(
            f"unsupported Profile sequence_flags: {sequence_flags_name!r}"
        )
    sequence_flags = SUPPORTED_SEQUENCE_FLAGS[sequence_flags_name]

    secondary_header = settings.get("secondary_header")
    if not isinstance(secondary_header, bool):
        raise G1Error("Profile secondary_header must be boolean")
    if secondary_header is not False:
        raise G1Error(
            "G1 does not support secondary_header=true for this projection"
        )

    secure_link_intent = settings.get("secure_link")
    if secure_link_intent != SUPPORTED_SECURE_LINK_INTENT:
        raise G1Error(
            f"unsupported Profile secure_link intent: {secure_link_intent!r}"
        )

    packet = target_baseline.get("packet_projection") or {}
    secure = packet.get("secure_link") or {}
    if packet.get("sequence_flags") != sequence_flags:
        raise G1Error(
            "Profile sequence_flags are inconsistent with pinned PWNSAT source facts"
        )
    if packet.get("secondary_header") is not secondary_header:
        raise G1Error(
            "Profile secondary_header is inconsistent with pinned PWNSAT source facts"
        )
    if secure.get("enabled") is not True:
        raise G1Error(
            "Profile secure_link intent disagrees with pinned firmware default"
        )

    return {
        "sequence_count": sequence_count,
        "sequence_flags_name": sequence_flags_name,
        "sequence_flags": sequence_flags,
        "secondary_header": secondary_header,
        "secure_link_intent": secure_link_intent,
        "secure_link_enabled": True,
        "secure_link_label": "AES-128-ECB/default-enabled",
    }


def build_stimulus(
    target_baseline: dict[str, Any],
    projection: dict[str, Any],
) -> bytes:
    secure = target_baseline["packet_projection"]["secure_link"]
    logical_payload = bytes.fromhex(
        target_baseline["target_command"]["logical_payload_hex"]
    )
    if projection["secure_link_enabled"] is not True:
        raise G1Error("resolved secure-link projection is unsupported")
    prefix = len(logical_payload).to_bytes(
        secure["length_prefix_bytes"], "big"
    )
    plain = prefix + logical_payload
    if len(plain) % 16:
        plain += b"\x00" * (16 - (len(plain) % 16))
    key = secure["key_ascii"].encode("ascii")
    encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    wire_payload = encryptor.update(plain) + encryptor.finalize()

    packet_id = (
        (1 << 12)
        | ((1 if projection["secondary_header"] else 0) << 11)
        | TARGET_APID
    )
    sequence = (
        (projection["sequence_flags"] << 14)
        | projection["sequence_count"]
    )
    length_field = len(wire_payload) - 1
    return struct.pack(">HHH", packet_id, sequence, length_field) + wire_payload


def mapping_payload(
    declaration: dict[str, Any],
    atom: dict[str, Any],
    profile_sha: str,
    target_baseline: dict[str, Any],
    target_baseline_sha: str,
    stimulus_sha: str,
    projection: dict[str, Any],
) -> dict[str, Any]:
    return {
        "format_version": "0.1-story",
        "kind": "orbitfabric.reference_mission.pwnsat_projection_mapping",
        "mapping_id": MAPPING_ID,
        "projection_state": "PROJECTED",
        "source": {
            "command": {"domain": "commands", "id": COMMAND_ID},
            "scenario": {
                "id": declaration["scenario"]["id"],
                "sha256": declaration["source"]["scenario_sha256"],
                "atom_id": atom["id"],
            },
        },
        "profile": {"id": PROFILE_ID, "sha256": profile_sha},
        "target_baseline": {
            "repository": target_baseline["repository"],
            "commit_sha": target_baseline["commit_sha"],
            "source_baseline_sha256": target_baseline_sha,
        },
        "target": {
            "command": TARGET_COMMAND,
            "symbol": TARGET_SYMBOL,
            "apid": TARGET_APID,
            "packet_type": "TC",
            "secondary_header": projection["secondary_header"],
            "sequence_flags": projection["sequence_flags"],
            "sequence_count": projection["sequence_count"],
            "secure_link": projection["secure_link_label"],
        },
        "stimulus": {
            "path": STIMULUS_FILENAME,
            "sha256": stimulus_sha,
            "media_type": "application/octet-stream",
        },
        "runtime_claim": False,
        "boundary": "PROJECTED != TRANSMITTED != EXECUTED != OBSERVED",
    }


def accounting_payload(
    declaration: dict[str, Any], command_atom_id: str
) -> dict[str, Any]:
    records = []
    for atom in declaration.get("atoms") or []:
        atom_id = atom.get("id")
        if not atom_id:
            raise G1Error("Scenario Declaration contains atom without id")
        if atom_id == command_atom_id:
            records.append(
                {
                    "atom_id": atom_id,
                    "disposition": "projected",
                    "mapping_ids": [MAPPING_ID],
                    "reason": None,
                }
            )
        else:
            records.append(
                {
                    "atom_id": atom_id,
                    "disposition": "not_projected",
                    "mapping_ids": [],
                    "reason": (
                        "G1 projects only the selected command atom; "
                        f"{atom.get('kind', 'this atom')} remains outside "
                        "the target command projection."
                    ),
                }
            )
    return {
        "accounting_version": "0.1-candidate",
        "completeness": "complete",
        "kind": "orbitfabric.scenario_projection_accounting",
        "records": records,
        "scenario": {
            "id": declaration["scenario"]["id"],
            "sha256": declaration["source"]["scenario_sha256"],
        },
    }


def integration_result_payload(
    manifest: dict[str, Any],
    declaration: dict[str, Any],
    profile_sha: str,
    target_baseline: dict[str, Any],
    target_baseline_sha: str,
    mapping_sha: str,
    stimulus_sha: str,
    accounting_sha: str,
) -> dict[str, Any]:
    mission = manifest.get("mission") or {}
    return {
        "adapter": {"id": PACKAGE_ID, "version": PACKAGE_VERSION},
        "artifacts": [
            {
                "id": "pwnsat-health-check-mapping",
                "kind": "orbitfabric.reference_mission.pwnsat_projection_mapping",
                "status": "generated",
                "requirement": "required",
                "media_type": "application/json",
                "path": MAPPING_FILENAME,
                "sha256": mapping_sha,
                "reason": None,
                "retained_partial": False,
                "derived_from_mappings": [MAPPING_ID],
            },
            {
                "id": "pwnsat-health-check-stimulus",
                "kind": "orbitfabric.reference_mission.pwnsat_target_stimulus",
                "status": "generated",
                "requirement": "required",
                "media_type": "application/octet-stream",
                "path": STIMULUS_FILENAME,
                "sha256": stimulus_sha,
                "reason": None,
                "retained_partial": False,
                "derived_from_mappings": [MAPPING_ID],
            },
            {
                "id": "scenario-accounting",
                "kind": "orbitfabric.scenario_projection_accounting",
                "status": "generated",
                "requirement": "required",
                "media_type": "application/json",
                "path": ACCOUNTING_FILENAME,
                "sha256": accounting_sha,
                "reason": None,
                "retained_partial": False,
                "derived_from_mappings": [MAPPING_ID],
            },
        ],
        "capabilities": [
            "profile_validation",
            "projection",
            "artifact_generation",
            "traceability",
        ],
        "coverage": {
            "status": "complete",
            "scope": {
                "domains": ["commands"],
                "scenario": declaration["scenario"]["id"],
            },
            "reason": None,
            "summary": {
                "projected_scenario_atoms": 1,
                "target_mappings": 1,
            },
            "records": [],
        },
        "diagnostics": [],
        "evidence": [
            {
                "kind": "source_provenance",
                "repository": target_baseline["repository"],
                "commit_sha": target_baseline["commit_sha"],
                "source_baseline_sha256": target_baseline_sha,
            }
        ],
        "external_tools": [],
        "inputs": {
            "core_input_set": {
                "status": "available",
                "kind": manifest["kind"],
                "version": manifest["input_set_version"],
                "sha256": manifest["input_set_sha256"],
                "reason": None,
            },
            "operation_inputs": [
                {
                    "role": "scenario",
                    "status": "available",
                    "id": declaration["scenario"]["id"],
                    "sha256": declaration["source"]["scenario_sha256"],
                    "reason": None,
                }
            ],
            "profile": {
                "status": "available",
                "kind": "orbitfabric.projection_profile",
                "profile_version": "0.1-candidate",
                "id": PROFILE_ID,
                "version": PROFILE_INSTANCE_VERSION,
                "sha256": profile_sha,
                "reason": None,
            },
        },
        "integration": {
            "id": INTEGRATION_ID,
            "schema_version": INTEGRATION_SCHEMA_VERSION,
        },
        "kind": "orbitfabric.integration_result",
        "mappings": [
            {
                "id": MAPPING_ID,
                "profile_bindings": [MAPPING_ID],
                "sources": [{"domain": "commands", "id": COMMAND_ID}],
                "targets": [
                    {
                        "id": f"SPP_APID_TC_GET_STATUS/0x{TARGET_APID:02X}",
                        "kind": "command",
                        "namespace": "pwnsat.flatsat",
                    }
                ],
                "mapping_artifact_sha256": mapping_sha,
                "stimulus_artifact_sha256": stimulus_sha,
            }
        ],
        "mission": {
            "status": "available",
            "id": mission.get("id"),
            "model_version": mission.get("model_version"),
            "reason": None,
        },
        "operation": {"id": "project"},
        "resolutions": [
            {
                "id": "pwnsat-source-baseline",
                "repository": target_baseline["repository"],
                "commit_sha": target_baseline["commit_sha"],
                "source_baseline_sha256": target_baseline_sha,
            }
        ],
        "result": "succeeded",
        "result_version": "0.2-candidate",
    }


def generate(
    iiss_dir: Path, declaration_path: Path, output_dir: Path
) -> dict[str, str]:
    manifest = load_json(iiss_dir / "integration_input_manifest.json")
    resolve_iiss_command(iiss_dir, manifest)

    declaration = load_json(declaration_path)
    atom = resolve_command_atom(declaration, COMMAND_ID)
    scenario = declaration.get("scenario") or {}
    source = declaration.get("source") or {}
    if not scenario.get("id") or not source.get("scenario_sha256"):
        raise G1Error("Scenario Declaration lacks exact identity")

    profile, profile_raw = load_profile()
    profile_sha = sha256_bytes(profile_raw)
    target_baseline = load_json(TARGET_BASELINE_PATH)
    validate_target_baseline(target_baseline)
    target_baseline_sha = sha256_file(TARGET_BASELINE_PATH)
    projection = resolve_profile_projection(profile, target_baseline)

    stimulus = build_stimulus(target_baseline, projection)
    output_dir.mkdir(parents=True, exist_ok=True)
    stimulus_path = output_dir / STIMULUS_FILENAME
    stimulus_path.write_bytes(stimulus)
    stimulus_sha = sha256_bytes(stimulus)

    mapping = mapping_payload(
        declaration,
        atom,
        profile_sha,
        target_baseline,
        target_baseline_sha,
        stimulus_sha,
        projection,
    )
    mapping_path = output_dir / MAPPING_FILENAME
    write_json(mapping_path, mapping)
    mapping_sha = sha256_file(mapping_path)

    accounting = accounting_payload(declaration, atom["id"])
    accounting_path = output_dir / ACCOUNTING_FILENAME
    write_json(accounting_path, accounting)
    accounting_sha = sha256_file(accounting_path)

    result = integration_result_payload(
        manifest,
        declaration,
        profile_sha,
        target_baseline,
        target_baseline_sha,
        mapping_sha,
        stimulus_sha,
        accounting_sha,
    )
    result_path = output_dir / RESULT_FILENAME
    write_json(result_path, result)
    result_sha = sha256_file(result_path)

    outcome = verify_bundle(
        result_path,
        "scenario-accounting",
        declaration_path,
        expected_result_sha256=result_sha,
    )
    if outcome["identity"]["artifact_sha256"] != accounting_sha:
        raise G1Error(
            "Core accounting checker returned a different artifact identity"
        )

    return {
        "scenario_atom_id": atom["id"],
        "profile_sha256": profile_sha,
        "target_baseline_sha256": target_baseline_sha,
        "mapping_sha256": mapping_sha,
        "stimulus_sha256": stimulus_sha,
        "accounting_sha256": accounting_sha,
        "integration_result_sha256": result_sha,
        "iiss_sha256": manifest["input_set_sha256"],
    }


def compare_dirs(left: Path, right: Path) -> None:
    names = [
        STIMULUS_FILENAME,
        MAPPING_FILENAME,
        ACCOUNTING_FILENAME,
        RESULT_FILENAME,
    ]
    for name in names:
        a = (left / name).read_bytes()
        b = (right / name).read_bytes()
        if a != b:
            raise G1Error(f"deterministic regeneration mismatch: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="R2 G1 offline PWNSAT projection-lineage proof"
    )
    parser.add_argument("--iiss-dir", type=Path, required=True)
    parser.add_argument(
        "--scenario-declaration", type=Path, required=True
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--verify-retained", action="store_true")
    parser.add_argument("--print-artifacts-base64", action="store_true")
    args = parser.parse_args()

    identities = generate(
        args.iiss_dir, args.scenario_declaration, args.output_dir
    )
    print(json.dumps(identities, indent=2, sort_keys=True))

    if args.verify_retained:
        compare_dirs(args.output_dir, RETAINED_DIR)
        with tempfile.TemporaryDirectory(prefix="r2-g1-regen-") as tmp:
            second = Path(tmp)
            identities2 = generate(
                args.iiss_dir, args.scenario_declaration, second
            )
            compare_dirs(args.output_dir, second)
            if identities2 != identities:
                raise G1Error(
                    "identity set changed across clean regeneration"
                )
        print("[r2-g1] retained bytes + clean regeneration PASS")

    if args.print_artifacts_base64:
        import base64

        for name in [
            STIMULUS_FILENAME,
            MAPPING_FILENAME,
            ACCOUNTING_FILENAME,
            RESULT_FILENAME,
        ]:
            raw = (args.output_dir / name).read_bytes()
            encoded = base64.b64encode(raw).decode("ascii")
            print(f"G1_ARTIFACT::{name}::{encoded}")

    print("[r2-g1] offline projection lineage PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
