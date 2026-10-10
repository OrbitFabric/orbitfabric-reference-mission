#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from orbitfabric.conformance.evidence_set import verify_bundle as verify_evidence_manifest

from runtime_evidence import (
    ACCOUNTING_SHA256,
    EXPERIMENT_SCHEMA,
    FROZEN_STIMULUS_SHA256,
    INTEGRATION_RESULT_SHA256,
    MAPPING_SHA256,
    OBSERVATION_SCHEMA,
    SCENARIO_SHA256,
    authorized_invocation_id,
    canonical_json_bytes,
    derive_assessment,
    experiment_identity,
    load_json,
    sha256_file,
    validate_schema,
)
from runtime_transport import sha256_bytes

MAPPING_ID = "mapping.r2.pwnsat.health-check.status"


class RuntimeBundleError(ValueError):
    pass


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _copy_exact(source: Path, target: Path, expected_sha256: str) -> None:
    actual = sha256_file(source)
    if actual != expected_sha256:
        raise RuntimeBundleError(
            f"source identity mismatch for {source}: expected {expected_sha256}, got {actual}"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    copied = sha256_file(target)
    if copied != expected_sha256:
        raise RuntimeBundleError(f"copy identity mismatch for {target}")


def _subjects() -> list[dict[str, Any]]:
    return [
        {
            "type": "scenario_source",
            "scenario_id": "r2_g0_health_check",
            "scenario_sha256": SCENARIO_SHA256,
        },
        {
            "type": "scenario_atom",
            "scenario_sha256": SCENARIO_SHA256,
            "atom_id": "atom-0003",
        },
        {
            "type": "integration_result",
            "result_sha256": INTEGRATION_RESULT_SHA256,
        },
        {
            "type": "integration_mapping",
            "result_sha256": INTEGRATION_RESULT_SHA256,
            "mapping_id": MAPPING_ID,
        },
    ]


def _record(
    record_id: str,
    *,
    kind: str,
    producer_id: str,
    path: str,
    sha256: str,
    media_type: str,
    format_version: str | None = None,
) -> dict[str, Any]:
    content = {
        "kind": kind,
        "producer": {"id": producer_id},
        "reference": {
            "path": path,
            "media_type": media_type,
            "sha256": sha256,
        },
    }
    if format_version is not None:
        content["format_version"] = format_version
    return {
        "id": record_id,
        "content": content,
        "subjects": _subjects(),
    }


def _write_sha256s(root: Path) -> Path:
    lines = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.name == "SHA256SUMS":
            continue
        relative = path.relative_to(root).as_posix()
        lines.append(f"{sha256_file(path)}  {relative}")
    target = root / "SHA256SUMS"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return target


def seal_runtime_bundle(
    *,
    project_root: Path,
    bundle_root: Path,
    definition: dict[str, Any],
    report: dict[str, Any],
    trace: dict[str, Any],
) -> dict[str, str]:
    bundle_root.mkdir(parents=True, exist_ok=True)

    definition_path = bundle_root / "experiment-definition.json"
    report_path = bundle_root / "execution-observation.json"
    trace_path = bundle_root / "runtime-trace.json"
    _write_json(definition_path, definition)
    _write_json(report_path, report)
    _write_json(trace_path, trace)

    g1_dir = project_root / "artifacts" / "g1"
    copied = {
        "g1/integration_result.json": (
            g1_dir / "integration_result.json",
            INTEGRATION_RESULT_SHA256,
        ),
        "g1/scenario_projection_accounting.json": (
            g1_dir / "scenario_projection_accounting.json",
            ACCOUNTING_SHA256,
        ),
        "g1/pwnsat-health-check.tc.bin": (
            g1_dir / "pwnsat-health-check.tc.bin",
            FROZEN_STIMULUS_SHA256,
        ),
        "g1/pwnsat-health-check.mapping.json": (
            g1_dir / "pwnsat-health-check.mapping.json",
            MAPPING_SHA256,
        ),
    }
    for relative, (source, digest) in copied.items():
        _copy_exact(source, bundle_root / relative, digest)

    records = [
        _record(
            "experiment-definition",
            kind="orbitfabric.reference_mission.pwnsat_experiment_definition",
            producer_id="orbitfabric-reference-mission.r2-runtime-proof",
            path="experiment-definition.json",
            sha256=sha256_file(definition_path),
            media_type="application/json",
            format_version="0.2-story",
        ),
        _record(
            "execution-observation",
            kind="orbitfabric.reference_mission.pwnsat_execution_observation",
            producer_id="orbitfabric-reference-mission.r2-runtime-proof",
            path="execution-observation.json",
            sha256=sha256_file(report_path),
            media_type="application/json",
            format_version="0.2-story",
        ),
        _record(
            "runtime-trace",
            kind="orbitfabric.reference_mission.pwnsat_runtime_trace",
            producer_id="orbitfabric-reference-mission.r2-runtime-proof",
            path="runtime-trace.json",
            sha256=sha256_file(trace_path),
            media_type="application/json",
            format_version="0.1-story",
        ),
        _record(
            "accepted-g1-integration-result",
            kind="orbitfabric.integration_result",
            producer_id="r2-pwnsat-story-integration-package",
            path="g1/integration_result.json",
            sha256=INTEGRATION_RESULT_SHA256,
            media_type="application/json",
            format_version="0.2-candidate",
        ),
        _record(
            "accepted-g1-scenario-accounting",
            kind="orbitfabric.scenario_projection_accounting",
            producer_id="r2-pwnsat-story-integration-package",
            path="g1/scenario_projection_accounting.json",
            sha256=ACCOUNTING_SHA256,
            media_type="application/json",
            format_version="0.1-candidate",
        ),
        _record(
            "accepted-g1-frozen-stimulus",
            kind="orbitfabric.reference_mission.pwnsat_target_stimulus",
            producer_id="r2-pwnsat-story-integration-package",
            path="g1/pwnsat-health-check.tc.bin",
            sha256=FROZEN_STIMULUS_SHA256,
            media_type="application/octet-stream",
        ),
        _record(
            "accepted-g1-mapping",
            kind="orbitfabric.reference_mission.pwnsat_projection_mapping",
            producer_id="r2-pwnsat-story-integration-package",
            path="g1/pwnsat-health-check.mapping.json",
            sha256=MAPPING_SHA256,
            media_type="application/json",
            format_version="0.1-story",
        ),
    ]

    captures_root = bundle_root / "captures"
    if captures_root.exists():
        for presentation_dir in sorted(p for p in captures_root.iterdir() if p.is_dir()):
            pid = presentation_dir.name
            for file in sorted(presentation_dir.iterdir()):
                if not file.is_file():
                    continue
                relative = file.relative_to(bundle_root).as_posix()
                suffix = file.suffix.lower()
                media = "application/json" if suffix == ".json" else "application/octet-stream"
                kind = (
                    "orbitfabric.reference_mission.pwnsat_presentation_record"
                    if file.name == "presentation.json"
                    else "orbitfabric.reference_mission.pwnsat_raw_runtime_evidence"
                )
                records.append(
                    _record(
                        f"{pid.lower()}-{file.stem}",
                        kind=kind,
                        producer_id="orbitfabric-reference-mission.r2-runtime-proof",
                        path=relative,
                        sha256=sha256_file(file),
                        media_type=media,
                        format_version="0.1-story" if suffix == ".json" else None,
                    )
                )

    manifest = {
        "kind": "orbitfabric.evidence_set_manifest",
        "manifest_version": "0.1-candidate",
        "evidence_set": {
            "id": f"r2-runtime-{report['execution_attempt_id']}"
        },
        "curator": {
            "id": "orbitfabric-reference-mission",
            "version": "r2-runtime-0.2-story",
        },
        "records": records,
    }
    manifest_path = bundle_root / "evidence-set.json"
    _write_json(manifest_path, manifest)
    verify_evidence_manifest(manifest, bundle_root)

    sums_path = _write_sha256s(bundle_root)
    return {
        "experiment_definition_sha256": sha256_file(definition_path),
        "execution_observation_sha256": sha256_file(report_path),
        "runtime_trace_sha256": sha256_file(trace_path),
        "evidence_set_sha256": sha256_file(manifest_path),
        "sha256s_sha256": sha256_file(sums_path),
    }


def _verify_presentation_identity(value: dict[str, Any]) -> None:
    supplied = value["presentation_record_sha256"]
    core = dict(value)
    del core["presentation_record_sha256"]
    actual = hashlib.sha256(canonical_json_bytes(core)).hexdigest()
    if supplied != actual:
        raise RuntimeBundleError(
            f"presentation {value['id']} identity mismatch: {supplied} != {actual}"
        )


def verify_runtime_bundle(bundle_root: Path) -> dict[str, str]:
    definition = load_json(bundle_root / "experiment-definition.json")
    report = load_json(bundle_root / "execution-observation.json")
    trace = load_json(bundle_root / "runtime-trace.json")

    validate_schema(definition, EXPERIMENT_SCHEMA)
    validate_schema(report, OBSERVATION_SCHEMA)

    definition_sha = sha256_file(bundle_root / "experiment-definition.json")
    if definition_sha != experiment_identity(definition):
        raise RuntimeBundleError("Experiment Definition exact-byte identity mismatch")
    if report["experiment_definition_sha256"] != definition_sha:
        raise RuntimeBundleError("Observation Report references different Experiment Definition")

    expected_a = authorized_invocation_id(
        definition, report["execution_attempt_id"]
    )
    if report["authorized_instance"]["authorized_invocation_id"] != expected_a:
        raise RuntimeBundleError("Observation Report authorized invocation A mismatch")

    if derive_assessment(report) != report["assessment"]:
        raise RuntimeBundleError("Observation Report semantic assessment is not deterministic")

    accepted = [x for x in report["execution_occurrences"] if x["accepted"]]
    if report["evidence_status"] == "complete":
        if report["observed_execution_count"] != len(accepted):
            raise RuntimeBundleError("Observed count differs from accepted occurrences")
    elif report["observed_execution_count"] is not None:
        raise RuntimeBundleError("Non-complete evidence asserts an observed count")

    if trace.get("execution_attempt_id") != report["execution_attempt_id"]:
        raise RuntimeBundleError("Runtime trace attempt identity mismatch")
    if trace.get("authorized_invocation_id") != expected_a:
        raise RuntimeBundleError("Runtime trace authorized invocation mismatch")

    exact_g1 = {
        "g1/integration_result.json": INTEGRATION_RESULT_SHA256,
        "g1/scenario_projection_accounting.json": ACCOUNTING_SHA256,
        "g1/pwnsat-health-check.tc.bin": FROZEN_STIMULUS_SHA256,
        "g1/pwnsat-health-check.mapping.json": MAPPING_SHA256,
    }
    for relative, expected in exact_g1.items():
        if sha256_file(bundle_root / relative) != expected:
            raise RuntimeBundleError(f"retained G1 identity mismatch: {relative}")

    packet_hashes_by_pid: dict[str, set[str]] = {}
    for presentation in report["presentations"]:
        pid = presentation["id"]
        pdir = bundle_root / "captures" / pid
        record_path = pdir / "presentation.json"
        if not record_path.exists():
            raise RuntimeBundleError(f"missing retained presentation record for {pid}")
        retained = load_json(record_path)
        if retained != presentation:
            raise RuntimeBundleError(f"retained presentation record differs for {pid}")
        _verify_presentation_identity(retained)

        raw_stream_path = pdir / "raw-usb-stream.bin"
        if presentation["raw_stream_sha256"] is not None:
            if sha256_file(raw_stream_path) != presentation["raw_stream_sha256"]:
                raise RuntimeBundleError(f"raw USB stream identity mismatch for {pid}")

        packet_hashes = set()
        for packet_path in pdir.glob("packet-*.spp.bin"):
            packet_hashes.add(sha256_file(packet_path))
        packet_hashes_by_pid[pid] = packet_hashes

    for occurrence in accepted:
        if occurrence["raw_spp_sha256"] not in packet_hashes_by_pid.get(
            occurrence["presentation_id"], set()
        ):
            raise RuntimeBundleError(
                f"occurrence {occurrence['id']} has no retained raw SPP packet"
            )

    manifest = load_json(bundle_root / "evidence-set.json")
    verify_evidence_manifest(manifest, bundle_root)

    return {
        "experiment_definition_sha256": definition_sha,
        "execution_observation_sha256": sha256_file(
            bundle_root / "execution-observation.json"
        ),
        "runtime_trace_sha256": sha256_file(bundle_root / "runtime-trace.json"),
        "evidence_set_sha256": sha256_file(bundle_root / "evidence-set.json"),
        "sha256s_sha256": sha256_file(bundle_root / "SHA256SUMS"),
    }
