#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_evidence import (
    build_experiment_definition,
    build_not_run_report,
    canonical_json_bytes,
    criterion_identity,
    experiment_identity,
    verify_frozen_g1_inputs,
    verify_transport_source_baseline,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="R2 bounded-runtime offline preflight; never opens hardware"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execution-attempt-id", required=True)
    parser.add_argument("--window-seconds", type=float, default=1.0)
    parser.add_argument("--pre-quiet-seconds", type=float, default=0.1)
    parser.add_argument(
        "--not-run-reason",
        default="controlled FlatSat runtime is not available to this execution environment",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    g1 = verify_frozen_g1_inputs()
    transport_sha = verify_transport_source_baseline()
    criterion_sha = criterion_identity()
    definition = build_experiment_definition(
        window_seconds=args.window_seconds,
        pre_quiet_seconds=args.pre_quiet_seconds,
    )
    definition_path = args.output_dir / "experiment-definition.runtime.json"
    definition_path.write_bytes(canonical_json_bytes(definition))

    report = build_not_run_report(
        definition,
        execution_attempt_id=args.execution_attempt_id,
        reason=args.not_run_reason,
    )
    report_path = args.output_dir / "execution-observation.not-run.json"
    report_path.write_bytes(canonical_json_bytes(report))

    result = {
        "runtime_status": "NOT_RUN",
        "experiment_definition_sha256": experiment_identity(definition),
        "occurrence_criterion_sha256": criterion_sha,
        "runtime_transport_source_baseline_sha256": transport_sha,
        "frozen_g1": g1,
        "definition_path": str(definition_path),
        "not_run_report_path": str(report_path),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[r2-runtime] offline preflight PASS / runtime NOT RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
