#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

from g0_contracts import derive_authorized_invocation
from runtime_transport import (
    FROZEN_STIMULUS_SHA256,
    RuntimeTransportError,
    StatusTelemetry,
    decode_status_tm,
    frame_usb_ingress,
    sha256_bytes,
)

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
SCHEMA_DIR = PROJECT_ROOT / "schemas"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
G1_DIR = PROJECT_ROOT / "artifacts" / "g1"

EXPERIMENT_SCHEMA = SCHEMA_DIR / "pwnsat-experiment-definition-0.2-story.schema.json"
OBSERVATION_SCHEMA = SCHEMA_DIR / "pwnsat-execution-observation-0.2-story.schema.json"
CRITERION_PATH = RUNTIME_DIR / "occurrence-criterion-0.1-story.json"
TRANSPORT_BASELINE_PATH = RUNTIME_DIR / "pwnsat-runtime-transport-source-baseline.json"

IISS_SHA256 = "4bbdca769e4b8fdee51719a47acaa49e9a552b4360f96d8664947514b074ef34"
PROFILE_SHA256 = "16730c278a8f97332994c65eba35c8d0ffdbb2d94da007e0f32712dc7bb28531"
SOURCE_BASELINE_SHA256 = "b6e5a6d04a37d1fb29dd2c00f1c81d22cfae65626564160b2fa11dd80cc4ca5e"
MAPPING_SHA256 = "7ba435832dcc5f8d4e18f0333800b9e3dbaff8f19fc515bc50de99e9db555b72"
ACCOUNTING_SHA256 = "4289c96b0cfadf4443e851cd3b30cc5900dc22d845c752ace80649de4bdcb2f2"
INTEGRATION_RESULT_SHA256 = "4cabd9fb153730b6b6e454a5999dd2c1d4c5c843edf0d75232e7a6002dd5f750"
SCENARIO_SHA256 = "62a6e33afca19a29fa7357cd9c773481b77536bc7b6470575f6f4b8c7aedca27"
TARGET_COMMIT = "b5ac0f2ba5e7bd60fbb6994f681c28053777628e"

CRITERION_ID = "r2.pwnsat.status-occurrence"
CRITERION_VERSION = "0.1-story"
AUTHORIZED_LOCAL_ID = "health-check"
EXPECTED_EXECUTION_COUNT = 1


class RuntimeEvidenceError(ValueError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeEvidenceError(f"expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_schema(value: dict[str, Any], schema_path: Path) -> None:
    jsonschema.Draft202012Validator(
        load_json(schema_path)
    ).validate(value)


def verify_frozen_g1_inputs(project_root: Path = PROJECT_ROOT) -> dict[str, str]:
    paths = {
        "profile_sha256": project_root / "profile" / "pwnsat-flat-sat-health-check.yaml",
        "source_baseline_sha256": project_root / "target" / "pwnsat-source-baseline.json",
        "mapping_sha256": project_root / "artifacts" / "g1" / "pwnsat-health-check.mapping.json",
        "stimulus_sha256": project_root / "artifacts" / "g1" / "pwnsat-health-check.tc.bin",
        "scenario_accounting_sha256": project_root / "artifacts" / "g1" / "scenario_projection_accounting.json",
        "integration_result_sha256": project_root / "artifacts" / "g1" / "integration_result.json",
    }
    expected = {
        "profile_sha256": PROFILE_SHA256,
        "source_baseline_sha256": SOURCE_BASELINE_SHA256,
        "mapping_sha256": MAPPING_SHA256,
        "stimulus_sha256": FROZEN_STIMULUS_SHA256,
        "scenario_accounting_sha256": ACCOUNTING_SHA256,
        "integration_result_sha256": INTEGRATION_RESULT_SHA256,
    }
    actual = {key: sha256_file(path) for key, path in paths.items()}
    if actual != expected:
        mismatches = {
            key: {"expected": expected[key], "actual": actual[key]}
            for key in expected
            if expected[key] != actual[key]
        }
        raise RuntimeEvidenceError(
            f"accepted G1 frozen input identity mismatch: {mismatches}"
        )
    return actual


def criterion_identity() -> str:
    criterion = load_json(CRITERION_PATH)
    if (
        criterion.get("id") != CRITERION_ID
        or criterion.get("version") != CRITERION_VERSION
        or criterion.get("frozen_stimulus_sha256") != FROZEN_STIMULUS_SHA256
        or criterion.get("expected_execution_count") != EXPECTED_EXECUTION_COUNT
    ):
        raise RuntimeEvidenceError("occurrence criterion identity/content mismatch")
    return sha256_file(CRITERION_PATH)


def verify_transport_source_baseline() -> str:
    baseline = load_json(TRANSPORT_BASELINE_PATH)
    if (
        baseline.get("repository") != "Pwnsat/FlatSat"
        or baseline.get("commit_sha") != TARGET_COMMIT
        or (baseline.get("transport") or {}).get("kind") != "usb_cdc_serial"
        or (baseline.get("transport") or {}).get("wired_local_only") is not True
        or (baseline.get("transport") or {}).get("rf") is not False
    ):
        raise RuntimeEvidenceError("runtime transport baseline is outside Decision 029")
    return sha256_file(TRANSPORT_BASELINE_PATH)


def build_experiment_definition(
    *,
    window_seconds: float,
    pre_quiet_seconds: float,
) -> dict[str, Any]:
    if window_seconds <= 0 or pre_quiet_seconds <= 0:
        raise RuntimeEvidenceError("runtime timing bounds must be positive")
    verify_frozen_g1_inputs()
    verify_transport_source_baseline()
    criterion_sha = criterion_identity()
    value = {
        "kind": "orbitfabric.reference_mission.pwnsat_experiment_definition",
        "format_version": "0.2-story",
        "experiment": {
            "id": "r2.pwnsat.bounded-runtime-proof",
            "version": "0.2-story",
        },
        "scenario": {
            "id": "r2_g0_health_check",
            "sha256": SCENARIO_SHA256,
            "atom_id": "atom-0003",
            "command_id": "obc.request_health_check",
        },
        "projection": {
            "iiss_sha256": IISS_SHA256,
            "profile_sha256": PROFILE_SHA256,
            "source_baseline_sha256": SOURCE_BASELINE_SHA256,
            "mapping_sha256": MAPPING_SHA256,
            "stimulus_sha256": FROZEN_STIMULUS_SHA256,
            "scenario_accounting_sha256": ACCOUNTING_SHA256,
            "integration_result_sha256": INTEGRATION_RESULT_SHA256,
        },
        "authorized_instance": {
            "local_id": AUTHORIZED_LOCAL_ID,
            "scope": "execution_attempt",
            "expected_execution_count": EXPECTED_EXECUTION_COUNT,
        },
        "runtime_target": {
            "repository": "Pwnsat/FlatSat",
            "source_commit": TARGET_COMMIT,
            "transport": "usb_cdc_serial",
            "path": "wired_local",
            "rf": False,
        },
        "occurrence_criterion": {
            "id": CRITERION_ID,
            "version": CRITERION_VERSION,
            "sha256": criterion_sha,
        },
        "observation": {
            "window_seconds": window_seconds,
            "pre_quiet_seconds": pre_quiet_seconds,
            "exclusive_command_source_control": True,
            "require_cleared_channel": True,
        },
        "presentations": [{"id": "P1"}, {"id": "P2"}],
        "provenance": {
            "story_owned": True,
            "g0_0_1_story_unchanged": True,
            "note": (
                "Runtime form is additive and Story-owned. Accepted G0 0.1-story "
                "synthetic semantics remain frozen and historical."
            ),
        },
    }
    validate_schema(value, EXPERIMENT_SCHEMA)
    return value


def experiment_identity(definition: dict[str, Any]) -> str:
    validate_schema(definition, EXPERIMENT_SCHEMA)
    return hashlib.sha256(canonical_json_bytes(definition)).hexdigest()


def authorized_invocation_id(
    definition: dict[str, Any], execution_attempt_id: str
) -> str:
    definition_sha = experiment_identity(definition)
    return derive_authorized_invocation(
        definition_sha,
        execution_attempt_id,
        definition["authorized_instance"]["local_id"],
    )


def presentation_record(
    *,
    presentation_id: str,
    authorized_invocation: str,
    stimulus_raw: bytes,
    raw_stream: bytes | None,
    status: str,
    window_start_ns: int | None,
    window_end_ns: int | None,
    channel_cleared: bool,
) -> dict[str, Any]:
    if presentation_id not in {"P1", "P2"}:
        raise RuntimeEvidenceError("presentation id must be P1 or P2")
    if sha256_bytes(stimulus_raw) != FROZEN_STIMULUS_SHA256:
        raise RuntimeEvidenceError("presentation stimulus is not accepted G1 stimulus")
    frame = frame_usb_ingress(stimulus_raw)
    core = {
        "id": presentation_id,
        "authorized_invocation_id": authorized_invocation,
        "stimulus_sha256": FROZEN_STIMULUS_SHA256,
        "transport_frame_sha256": sha256_bytes(frame),
        "raw_stream_sha256": None if raw_stream is None else sha256_bytes(raw_stream),
        "status": status,
        "window_start_ns": window_start_ns,
        "window_end_ns": window_end_ns,
        "channel_cleared": channel_cleared,
    }
    core["presentation_record_sha256"] = sha256_json(core)
    return core


def occurrence_from_status(
    *,
    presentation_id: str,
    authorized_invocation: str,
    status: StatusTelemetry,
) -> dict[str, Any]:
    core = {
        "presentation_id": presentation_id,
        "authorized_invocation_id": authorized_invocation,
        "accepted": True,
        "raw_spp_sha256": status.raw_spp_sha256,
        "tm_sequence_count": status.sequence_count,
        "status_uptime_seconds": status.uptime_seconds,
    }
    identity = "r2e:" + sha256_json(core)
    return {"id": identity, **core}


def evaluate_status_window(
    raw_packets: list[bytes] | tuple[bytes, ...],
    *,
    presentation_id: str,
    authorized_invocation: str,
    prior_accepted: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, str, list[dict[str, str]]]:
    candidates: list[StatusTelemetry] = []
    diagnostics: list[dict[str, str]] = []
    for raw in raw_packets:
        try:
            candidates.append(decode_status_tm(raw))
        except RuntimeTransportError:
            continue

    if not candidates:
        return None, "none", diagnostics
    if len(candidates) != 1:
        diagnostics.append(
            {
                "code": "ambiguous_status_candidates",
                "message": (
                    f"{presentation_id} contained {len(candidates)} valid TM_STATUS "
                    "candidates; attribution is not unique."
                ),
            }
        )
        return None, "ambiguous", diagnostics

    status = candidates[0]
    if prior_accepted is not None:
        if status.raw_spp_sha256 == prior_accepted["raw_spp_sha256"]:
            diagnostics.append(
                {
                    "code": "reused_status_evidence",
                    "message": "STATUS raw evidence identity matches prior accepted occurrence.",
                }
            )
            return None, "ambiguous", diagnostics
        if status.sequence_count == prior_accepted["tm_sequence_count"]:
            diagnostics.append(
                {
                    "code": "non_distinct_tm_sequence",
                    "message": "TM_STATUS sequence identity is not distinct from prior occurrence.",
                }
            )
            return None, "ambiguous", diagnostics
        if status.uptime_seconds < prior_accepted["status_uptime_seconds"]:
            diagnostics.append(
                {
                    "code": "uptime_regression",
                    "message": "STATUS uptime regressed relative to prior accepted occurrence.",
                }
            )
            return None, "ambiguous", diagnostics

    return (
        occurrence_from_status(
            presentation_id=presentation_id,
            authorized_invocation=authorized_invocation,
            status=status,
        ),
        "accepted",
        diagnostics,
    )


def derive_assessment(report: dict[str, Any]) -> str | None:
    runtime_status = report["runtime"]["status"]
    if runtime_status == "NOT_RUN":
        return None

    pre = report["preconditions"]
    if not all(
        [
            pre["identity_binding_valid"],
            pre["controlled_runtime_authorized"],
            pre["exclusive_command_source"],
            pre["observation_channel_clearable"],
        ]
    ):
        return "INVALID_RUN"

    if report["evidence_status"] in {"ambiguous", "insufficient", "not_run"}:
        return "INCONCLUSIVE"

    observed = report["observed_execution_count"]
    if observed is None:
        return "INCONCLUSIVE"
    if observed == report["expected_execution_count"]:
        return "CONFORMANT"
    return "DIVERGED"


def build_not_run_report(
    definition: dict[str, Any],
    *,
    execution_attempt_id: str,
    reason: str,
) -> dict[str, Any]:
    if not reason:
        raise RuntimeEvidenceError("NOT_RUN report requires a concrete reason")
    a = authorized_invocation_id(definition, execution_attempt_id)
    report = {
        "kind": "orbitfabric.reference_mission.pwnsat_execution_observation",
        "format_version": "0.2-story",
        "producer": {"id": "r2-pwnsat-runtime-proof", "version": "0.2-story"},
        "experiment_definition_sha256": experiment_identity(definition),
        "execution_attempt_id": execution_attempt_id,
        "authorized_instance": {
            "local_id": definition["authorized_instance"]["local_id"],
            "authorized_invocation_id": a,
        },
        "runtime": {
            "status": "NOT_RUN",
            "repository": "Pwnsat/FlatSat",
            "source_commit": TARGET_COMMIT,
            "transport": "usb_cdc_serial",
            "path": "wired_local",
        },
        "occurrence_criterion": definition["occurrence_criterion"],
        "preconditions": {
            "identity_binding_valid": True,
            "controlled_runtime_authorized": False,
            "exclusive_command_source": False,
            "observation_channel_clearable": False,
            "reason": reason,
        },
        "presentations": [],
        "execution_occurrences": [],
        "evidence_status": "not_run",
        "expected_execution_count": EXPECTED_EXECUTION_COUNT,
        "observed_execution_count": None,
        "assessment": None,
        "diagnostics": [{"code": "runtime_not_run", "message": reason}],
    }
    validate_schema(report, OBSERVATION_SCHEMA)
    return report


def retain_capture(
    output_dir: Path,
    *,
    presentation: dict[str, Any],
    raw_stream: bytes,
    packets: tuple[bytes, ...] | list[bytes],
) -> dict[str, Any]:
    target = output_dir / presentation["id"]
    target.mkdir(parents=True, exist_ok=True)
    raw_path = target / "raw-usb-stream.bin"
    raw_path.write_bytes(raw_stream)
    packet_records = []
    for index, raw in enumerate(packets, 1):
        packet_path = target / f"packet-{index:04d}.spp.bin"
        packet_path.write_bytes(raw)
        packet_records.append(
            {
                "path": packet_path.name,
                "sha256": sha256_bytes(raw),
            }
        )
    presentation_path = target / "presentation.json"
    presentation_path.write_bytes(canonical_json_bytes(presentation))
    return {
        "presentation_path": str(presentation_path.relative_to(output_dir)),
        "presentation_sha256": sha256_file(presentation_path),
        "raw_stream_path": str(raw_path.relative_to(output_dir)),
        "raw_stream_sha256": sha256_file(raw_path),
        "packets": packet_records,
    }
