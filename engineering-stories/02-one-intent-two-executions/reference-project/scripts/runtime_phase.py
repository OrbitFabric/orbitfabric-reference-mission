#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Any

from runtime_bundle import seal_runtime_bundle, verify_runtime_bundle
from runtime_evidence import (
    PROJECT_ROOT,
    authorized_invocation_id,
    build_experiment_definition,
    build_runtime_report,
    canonical_json_bytes,
    evaluate_status_window,
    presentation_record,
    retain_capture,
    verify_frozen_g1_inputs,
)
from runtime_transport import (
    RuntimeTransportError,
    drain_until_quiet,
    open_serial_link,
    present_frozen_stimulus,
    sha256_bytes,
)

STIMULUS_PATH = PROJECT_ROOT / "artifacts" / "g1" / "pwnsat-health-check.tc.bin"


class RuntimePhaseError(ValueError):
    pass


def _event(name: str, *, clock_ns, **fields: Any) -> dict[str, Any]:
    return {"event": name, "monotonic_ns": clock_ns(), **fields}


def _write_bytes(path: Path, raw: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return sha256_bytes(raw)


def _run_presentation(
    *,
    serial_link,
    bundle_root: Path,
    definition: dict[str, Any],
    presentation_id: str,
    authorized_invocation: str,
    prior_accepted: dict[str, Any] | None,
    trace_events: list[dict[str, Any]],
    clock_ns,
    sleep,
) -> tuple[dict[str, Any], dict[str, Any] | None, str, list[dict[str, str]]]:
    observation = definition["observation"]
    quiet_seconds = observation["pre_quiet_seconds"]
    trace_events.append(
        _event(
            "quiescence_start",
            clock_ns=clock_ns,
            presentation_id=presentation_id,
        )
    )
    drained = drain_until_quiet(
        serial_link,
        quiet_seconds,
        max_seconds=max(2.0, quiet_seconds * 20),
        clock_ns=clock_ns,
        sleep=sleep,
    )
    pre_path = bundle_root / "captures" / presentation_id / "pre-window-drain.bin"
    pre_sha = _write_bytes(pre_path, drained)
    trace_events.append(
        _event(
            "quiescence_established",
            clock_ns=clock_ns,
            presentation_id=presentation_id,
            drained_bytes=len(drained),
            drained_sha256=pre_sha,
        )
    )

    stimulus = STIMULUS_PATH.read_bytes()
    framed, capture = present_frozen_stimulus(
        serial_link,
        stimulus,
        window_seconds=observation["window_seconds"],
        clock_ns=clock_ns,
        sleep=sleep,
    )
    trace_events.append(
        _event(
            "presentation_complete",
            clock_ns=clock_ns,
            presentation_id=presentation_id,
            transport_frame_sha256=sha256_bytes(framed),
            raw_stream_sha256=sha256_bytes(capture.raw_stream),
            parsed_packet_count=len(capture.packets),
            trailing_bytes=len(capture.trailing),
        )
    )

    presentation = presentation_record(
        presentation_id=presentation_id,
        authorized_invocation=authorized_invocation,
        stimulus_raw=stimulus,
        raw_stream=capture.raw_stream,
        status="PRESENTED",
        window_start_ns=capture.window_start_ns,
        window_end_ns=capture.window_end_ns,
        channel_cleared=True,
    )
    retain_capture(
        bundle_root / "captures",
        presentation=presentation,
        raw_stream=capture.raw_stream,
        packets=capture.packets,
    )

    if capture.trailing:
        diagnostics = [
            {
                "code": "incomplete_usb_egress_frame",
                "message": (
                    f"{presentation_id} observation window ended with "
                    f"{len(capture.trailing)} unparsed trailing bytes."
                ),
            }
        ]
        return presentation, None, "ambiguous", diagnostics

    occurrence, state, diagnostics = evaluate_status_window(
        capture.packets,
        presentation_id=presentation_id,
        authorized_invocation=authorized_invocation,
        prior_accepted=prior_accepted,
    )
    trace_events.append(
        _event(
            "occurrence_evaluation",
            clock_ns=clock_ns,
            presentation_id=presentation_id,
            result=state,
            occurrence_id=None if occurrence is None else occurrence["id"],
        )
    )
    return presentation, occurrence, state, diagnostics


def run_attempt(
    *,
    serial_link,
    output_dir: Path,
    execution_attempt_id: str,
    definition: dict[str, Any],
    controlled_runtime_authorized: bool,
    exclusive_command_source: bool,
    clock_ns=time.monotonic_ns,
    sleep=time.sleep,
) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimePhaseError(
            f"runtime output directory must be empty: {output_dir}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    verify_frozen_g1_inputs()
    a = authorized_invocation_id(definition, execution_attempt_id)
    trace_events: list[dict[str, Any]] = [
        _event(
            "attempt_start",
            clock_ns=clock_ns,
            execution_attempt_id=execution_attempt_id,
            authorized_invocation_id=a,
        )
    ]
    presentations: list[dict[str, Any]] = []
    occurrences: list[dict[str, Any]] = []
    diagnostics: list[dict[str, str]] = []

    preconditions = {
        "identity_binding_valid": True,
        "controlled_runtime_authorized": controlled_runtime_authorized,
        "exclusive_command_source": exclusive_command_source,
        "observation_channel_clearable": True,
        "reason": None,
    }

    if not controlled_runtime_authorized or not exclusive_command_source:
        preconditions["reason"] = "Decision 029 runtime control preconditions are not satisfied"
        report = build_runtime_report(
            definition,
            execution_attempt_id=execution_attempt_id,
            runtime_status="ABORTED",
            preconditions=preconditions,
            presentations=presentations,
            execution_occurrences=occurrences,
            evidence_status="insufficient",
            observed_execution_count=None,
            diagnostics=[
                {
                    "code": "runtime_control_precondition_failed",
                    "message": preconditions["reason"],
                }
            ],
        )
        trace_events.append(
            _event("attempt_aborted", clock_ns=clock_ns, reason=preconditions["reason"])
        )
        trace = {
            "kind": "orbitfabric.reference_mission.pwnsat_runtime_trace",
            "format_version": "0.1-story",
            "execution_attempt_id": execution_attempt_id,
            "authorized_invocation_id": a,
            "events": trace_events,
        }
        identities = seal_runtime_bundle(
            project_root=PROJECT_ROOT,
            bundle_root=output_dir,
            definition=definition,
            report=report,
            trace=trace,
        )
        verified = verify_runtime_bundle(output_dir)
        return {"report": report, "identities": identities, "verified": verified}

    try:
        p1, e1, p1_state, p1_diag = _run_presentation(
            serial_link=serial_link,
            bundle_root=output_dir,
            definition=definition,
            presentation_id="P1",
            authorized_invocation=a,
            prior_accepted=None,
            trace_events=trace_events,
            clock_ns=clock_ns,
            sleep=sleep,
        )
        presentations.append(p1)
        diagnostics.extend(p1_diag)

        if p1_state != "accepted" or e1 is None:
            evidence_status = "ambiguous" if p1_state == "ambiguous" else "insufficient"
            report = build_runtime_report(
                definition,
                execution_attempt_id=execution_attempt_id,
                runtime_status="COMPLETE",
                preconditions=preconditions,
                presentations=presentations,
                execution_occurrences=occurrences,
                evidence_status=evidence_status,
                observed_execution_count=None,
                diagnostics=diagnostics
                + [
                    {
                        "code": "g2_nominal_occurrence_not_established",
                        "message": (
                            "P1 did not establish one independently acceptable E1; "
                            "P2 was not presented in this attempt."
                        ),
                    }
                ],
            )
        else:
            occurrences.append(e1)
            p2, e2, p2_state, p2_diag = _run_presentation(
                serial_link=serial_link,
                bundle_root=output_dir,
                definition=definition,
                presentation_id="P2",
                authorized_invocation=a,
                prior_accepted=e1,
                trace_events=trace_events,
                clock_ns=clock_ns,
                sleep=sleep,
            )
            presentations.append(p2)
            diagnostics.extend(p2_diag)

            if p2_state == "ambiguous":
                evidence_status = "ambiguous"
                observed = None
            else:
                if e2 is not None:
                    occurrences.append(e2)
                evidence_status = "complete"
                observed = len(occurrences)

            report = build_runtime_report(
                definition,
                execution_attempt_id=execution_attempt_id,
                runtime_status="COMPLETE",
                preconditions=preconditions,
                presentations=presentations,
                execution_occurrences=occurrences,
                evidence_status=evidence_status,
                observed_execution_count=observed,
                diagnostics=diagnostics,
            )
    except RuntimeTransportError as exc:
        preconditions["observation_channel_clearable"] = False
        preconditions["reason"] = str(exc)
        diagnostics.append(
            {
                "code": "runtime_transport_failure",
                "message": str(exc),
            }
        )
        report = build_runtime_report(
            definition,
            execution_attempt_id=execution_attempt_id,
            runtime_status="ABORTED",
            preconditions=preconditions,
            presentations=presentations,
            execution_occurrences=occurrences,
            evidence_status="insufficient",
            observed_execution_count=None,
            diagnostics=diagnostics,
        )
        trace_events.append(
            _event("attempt_aborted", clock_ns=clock_ns, reason=str(exc))
        )

    trace_events.append(
        _event(
            "attempt_end",
            clock_ns=clock_ns,
            assessment=report["assessment"],
            evidence_status=report["evidence_status"],
            observed_execution_count=report["observed_execution_count"],
        )
    )
    trace = {
        "kind": "orbitfabric.reference_mission.pwnsat_runtime_trace",
        "format_version": "0.1-story",
        "execution_attempt_id": execution_attempt_id,
        "authorized_invocation_id": a,
        "events": trace_events,
    }

    identities = seal_runtime_bundle(
        project_root=PROJECT_ROOT,
        bundle_root=output_dir,
        definition=definition,
        report=report,
        trace=trace,
    )
    verified = verify_runtime_bundle(output_dir)
    return {"report": report, "identities": identities, "verified": verified}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="R2 bounded FlatSat runtime proof; explicit live invocation only"
    )
    parser.add_argument("--port", required=True)
    parser.add_argument("--execution-attempt-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--window-seconds", type=float, default=1.0)
    parser.add_argument("--pre-quiet-seconds", type=float, default=0.1)
    parser.add_argument("--controlled-runtime-authorized", action="store_true")
    parser.add_argument("--exclusive-command-source", action="store_true")
    parser.add_argument("--execute-live", action="store_true")
    args = parser.parse_args()

    if not args.execute_live:
        raise SystemExit(
            "live execution refused: pass --execute-live only at the explicitly "
            "authorized and controlled FlatSat"
        )
    if not args.controlled_runtime_authorized or not args.exclusive_command_source:
        raise SystemExit(
            "live execution refused: Decision 029 control preconditions not asserted"
        )

    definition = build_experiment_definition(
        window_seconds=args.window_seconds,
        pre_quiet_seconds=args.pre_quiet_seconds,
    )
    link = open_serial_link(args.port)
    try:
        result = run_attempt(
            serial_link=link,
            output_dir=args.output_dir,
            execution_attempt_id=args.execution_attempt_id,
            definition=definition,
            controlled_runtime_authorized=True,
            exclusive_command_source=True,
        )
    finally:
        link.close()

    print(json.dumps({
        "assessment": result["report"]["assessment"],
        "evidence_status": result["report"]["evidence_status"],
        "observed_execution_count": result["report"]["observed_execution_count"],
        "identities": result["identities"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
