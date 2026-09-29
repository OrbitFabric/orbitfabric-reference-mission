#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

EXPERIMENT_KIND = "orbitfabric.reference_mission.pwnsat_experiment_definition"
OBSERVATION_KIND = "orbitfabric.reference_mission.pwnsat_execution_observation"
FORMAT_VERSION = "0.1-story"
COMMAND_ID = "obc.request_health_check"
EXPECTED_EXECUTION_COUNT = 1
A_PREFIX = "r2a:"
A_DOMAIN = "orbitfabric-r2-authorized-invocation-v1"

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
EXPERIMENT_SCHEMA = PROJECT_ROOT / "schemas" / "pwnsat-experiment-definition-0.1-story.schema.json"
OBSERVATION_SCHEMA = PROJECT_ROOT / "schemas" / "pwnsat-execution-observation-0.1-story.schema.json"
DEFAULT_DEFINITION = PROJECT_ROOT / "fixtures" / "experiment-definition.synthetic.json"
OBSERVATIONS = PROJECT_ROOT / "fixtures" / "observations"

_STABLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


class ContractError(ValueError):
    """Raised when a structurally valid R2 artifact violates Story semantics."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_deterministic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _schema_validate(instance: Any, schema_path: Path) -> None:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    if errors:
        rendered = "; ".join(
            f"{'.'.join(str(p) for p in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ContractError(f"schema validation failed: {rendered}")


def validate_definition(definition: dict[str, Any]) -> None:
    _schema_validate(definition, EXPERIMENT_SCHEMA)

    auth = definition["authorized_instance"]
    if auth["scope"] != "execution_attempt":
        raise ContractError("authorized_instance.scope must be execution_attempt")
    if auth["expected_execution_count"] != EXPECTED_EXECUTION_COUNT:
        raise ContractError("first R2 proof freezes expected_execution_count at 1")

    projection = definition["projection"]
    if projection["synthetic"] is not True:
        raise ContractError("G0 projection identities must be explicitly synthetic")
    if definition["provenance"]["synthetic"] is not True:
        raise ContractError("G0 definition provenance must be explicitly synthetic")


def derive_authorized_invocation(
    experiment_definition_sha256: str,
    execution_attempt_id: str,
    authorized_instance_local_id: str,
) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", experiment_definition_sha256):
        raise ContractError("experiment definition digest must be lowercase SHA-256")
    for label, value in (
        ("execution_attempt_id", execution_attempt_id),
        ("authorized_instance.local_id", authorized_instance_local_id),
    ):
        if not _STABLE_ID.fullmatch(value):
            raise ContractError(f"{label} is not a stable identifier")

    # Canonical preimage rule:
    # UTF-8(domain + LF + definition_sha256 + LF + attempt_id + LF + local_id + LF)
    # The schema forbids LF in all variable identifiers, making the encoding unambiguous.
    preimage = (
        f"{A_DOMAIN}\n"
        f"{experiment_definition_sha256}\n"
        f"{execution_attempt_id}\n"
        f"{authorized_instance_local_id}\n"
    ).encode("utf-8")
    return A_PREFIX + sha256_bytes(preimage)


def resolve_command_atom(declaration: dict[str, Any], command_id: str = COMMAND_ID) -> dict[str, Any]:
    if declaration.get("kind") != "orbitfabric.scenario_declaration":
        raise ContractError("unexpected Scenario Declaration kind")
    if declaration.get("declaration_version") != "0.1-candidate":
        raise ContractError("unsupported Scenario Declaration version")
    if declaration.get("result") != "loaded":
        raise ContractError("Scenario Declaration is not loaded")

    matches: list[dict[str, Any]] = []
    for atom in declaration.get("atoms") or []:
        if atom.get("kind") != "command":
            continue
        for ref in atom.get("references") or []:
            entity = ref.get("entity") or {}
            if (
                ref.get("role") == "command"
                and entity.get("domain") == "commands"
                and entity.get("id") == command_id
            ):
                matches.append(atom)
                break

    if len(matches) != 1:
        raise ContractError(
            f"expected exactly one Core command atom for {command_id}, found {len(matches)}"
        )
    return matches[0]


def _synthetic_sha(label: str) -> str:
    return sha256_bytes(label.encode("utf-8"))


def definition_from_scenario_declaration(declaration: dict[str, Any]) -> dict[str, Any]:
    atom = resolve_command_atom(declaration, COMMAND_ID)
    scenario = declaration.get("scenario") or {}
    source = declaration.get("source") or {}
    scenario_id = scenario.get("id")
    scenario_sha = source.get("scenario_sha256")
    if not isinstance(scenario_id, str) or not scenario_id:
        raise ContractError("Scenario Declaration has no scenario id")
    if not isinstance(scenario_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", scenario_sha):
        raise ContractError("Scenario Declaration has no exact source SHA-256")

    definition = {
        "authorized_instance": {
            "expected_execution_count": EXPECTED_EXECUTION_COUNT,
            "local_id": "health-check-once",
            "scope": "execution_attempt",
        },
        "experiment": {
            "id": "r2-g0-health-check",
            "version": "0.1",
        },
        "format_version": FORMAT_VERSION,
        "kind": EXPERIMENT_KIND,
        "projection": {
            "integration_result_sha256": _synthetic_sha(
                "R2-G0 synthetic integration result placeholder; G1 not executed"
            ),
            "mapping_id": "synthetic.r2-g0.mapping-not-produced",
            "scenario_accounting_artifact_id": "synthetic.r2-g0.accounting-not-produced",
            "stimulus_artifact_id": "synthetic.r2-g0.stimulus-not-produced",
            "synthetic": True,
        },
        "provenance": {
            "note": (
                "G0-only fixture. Projection identities are deterministic placeholders; "
                "G1 artifacts and runtime evidence do not exist."
            ),
            "synthetic": True,
        },
        "scenario": {
            "atom_id": atom["id"],
            "id": scenario_id,
            "sha256": scenario_sha,
        },
    }
    validate_definition(definition)
    return definition


def verify_scenario_binding(
    declaration: dict[str, Any],
    definition: dict[str, Any],
) -> str:
    validate_definition(definition)
    atom = resolve_command_atom(declaration, COMMAND_ID)

    scenario = declaration["scenario"]
    source = declaration["source"]
    if definition["scenario"]["id"] != scenario["id"]:
        raise ContractError("Experiment Definition scenario id does not match Core declaration")
    if definition["scenario"]["sha256"] != source["scenario_sha256"]:
        raise ContractError("Experiment Definition scenario SHA-256 does not match Core declaration")
    if definition["scenario"]["atom_id"] != atom["id"]:
        raise ContractError("Experiment Definition atom id does not match Core-emitted command atom")
    return atom["id"]


def _validate_unique_ids(records: list[dict[str, Any]], label: str) -> None:
    ids = [item["id"] for item in records]
    if len(ids) != len(set(ids)):
        raise ContractError(f"{label} ids must be unique")


def derive_assessment(report: dict[str, Any]) -> str:
    if report["preconditions"]["identity_binding_valid"] is not True:
        return "INVALID_RUN"
    if report["evidence_status"] in {"insufficient", "ambiguous"}:
        return "INCONCLUSIVE"
    if report["observed_execution_count"] == report["expected_execution_count"]:
        return "CONFORMANT"
    return "DIVERGED"


def validate_report(
    definition_bytes: bytes,
    report: dict[str, Any],
) -> str:
    definition = json.loads(definition_bytes.decode("utf-8"))
    validate_definition(definition)
    _schema_validate(report, OBSERVATION_SCHEMA)

    definition_sha = sha256_bytes(definition_bytes)
    if report["experiment_definition_sha256"] != definition_sha:
        raise ContractError("report does not reference the exact Experiment Definition bytes")

    expected_local_id = definition["authorized_instance"]["local_id"]
    if report["authorized_instance"]["local_id"] != expected_local_id:
        raise ContractError("report authorized-instance local id does not match definition")

    if report["expected_execution_count"] != definition["authorized_instance"]["expected_execution_count"]:
        raise ContractError("report expected_execution_count differs from frozen definition")

    expected_a = derive_authorized_invocation(
        definition_sha,
        report["execution_attempt_id"],
        expected_local_id,
    )
    if report["authorized_instance"]["authorized_invocation_id"] != expected_a:
        raise ContractError("report authorized invocation A is inconsistent with definition/attempt")

    presentations = report["presentations"]
    occurrences = report["execution_occurrences"]
    _validate_unique_ids(presentations, "presentation")
    _validate_unique_ids(occurrences, "execution occurrence")

    for item in presentations:
        if item["authorized_invocation_id"] != expected_a:
            raise ContractError("presentation references a different authorized invocation A")
    for item in occurrences:
        if item["authorized_invocation_id"] != expected_a:
            raise ContractError("execution occurrence references a different authorized invocation A")

    evidence_status = report["evidence_status"]
    observed = report["observed_execution_count"]
    accepted_count = sum(1 for item in occurrences if item["accepted"] is True)
    if evidence_status == "complete":
        if not isinstance(observed, int):
            raise ContractError("complete occurrence evidence requires an observed execution count")
        if observed != accepted_count:
            raise ContractError(
                "explicit observed_execution_count differs from accepted occurrence records"
            )
    else:
        if observed is not None:
            raise ContractError(
                "insufficient/ambiguous occurrence evidence must not fabricate an observed count"
            )

    preconditions = report["preconditions"]
    if preconditions["identity_binding_valid"] is True and preconditions["reason"] is not None:
        raise ContractError("valid identity precondition must not carry a failure reason")
    if preconditions["identity_binding_valid"] is False and not preconditions["reason"]:
        raise ContractError("invalid identity precondition requires an explicit reason")

    if evidence_status in {"insufficient", "ambiguous"} and not report["diagnostics"]:
        raise ContractError("inconclusive occurrence evidence requires diagnostics")
    if preconditions["identity_binding_valid"] is False and not report["diagnostics"]:
        raise ContractError("invalid-run precondition requires diagnostics")

    derived = derive_assessment(report)
    if report["assessment"] != derived:
        raise ContractError(
            f"reported assessment {report['assessment']} differs from derived assessment {derived}"
        )
    return derived


def verify_all(
    scenario_declaration_path: Path,
    definition_path: Path = DEFAULT_DEFINITION,
) -> dict[str, str]:
    declaration = load_json(scenario_declaration_path)
    definition = load_json(definition_path)
    atom_id = verify_scenario_binding(declaration, definition)

    definition_bytes = definition_path.read_bytes()
    results: dict[str, str] = {}
    for path in sorted(OBSERVATIONS.glob("*.synthetic.json")):
        report = load_json(path)
        results[path.name] = validate_report(definition_bytes, report)

    expected = {"CONFORMANT", "DIVERGED", "INCONCLUSIVE", "INVALID_RUN"}
    if set(results.values()) != expected:
        raise ContractError(
            f"synthetic fixture outcome coverage mismatch: {sorted(set(results.values()))}"
        )

    return {"scenario_atom_id": atom_id, **results}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="R2 G0 Story-owned offline contract tooling")
    sub = parser.add_subparsers(dest="command", required=True)

    materialize = sub.add_parser(
        "materialize-definition",
        help="Create the deterministic synthetic Experiment Definition from a Core declaration",
    )
    materialize.add_argument("--scenario-declaration", type=Path, required=True)
    materialize.add_argument("--output", type=Path, required=True)

    digest = sub.add_parser("experiment-digest", help="Print exact Definition byte SHA-256")
    digest.add_argument("--definition", type=Path, default=DEFAULT_DEFINITION)

    derive = sub.add_parser("derive-a", help="Derive run-scoped authorized invocation A")
    derive.add_argument("--definition", type=Path, default=DEFAULT_DEFINITION)
    derive.add_argument("--attempt-id", required=True)

    report = sub.add_parser("verify-report", help="Validate and assess one Observation Report")
    report.add_argument("--definition", type=Path, default=DEFAULT_DEFINITION)
    report.add_argument("--report", type=Path, required=True)

    verify = sub.add_parser("verify-all", help="Verify Scenario binding and all G0 fixtures")
    verify.add_argument("--scenario-declaration", type=Path, required=True)
    verify.add_argument("--definition", type=Path, default=DEFAULT_DEFINITION)

    return parser


def main() -> int:
    args = _build_parser().parse_args()

    if args.command == "materialize-definition":
        declaration = load_json(args.scenario_declaration)
        definition = definition_from_scenario_declaration(declaration)
        write_json_deterministic(args.output, definition)
        print(f"materialized definition: {args.output}")
        print(f"resolved Core command atom: {definition['scenario']['atom_id']}")
        print(f"definition sha256: {sha256_file(args.output)}")
        return 0

    if args.command == "experiment-digest":
        definition = load_json(args.definition)
        validate_definition(definition)
        print(sha256_file(args.definition))
        return 0

    if args.command == "derive-a":
        definition = load_json(args.definition)
        validate_definition(definition)
        digest = sha256_file(args.definition)
        print(
            derive_authorized_invocation(
                digest,
                args.attempt_id,
                definition["authorized_instance"]["local_id"],
            )
        )
        return 0

    if args.command == "verify-report":
        outcome = validate_report(args.definition.read_bytes(), load_json(args.report))
        print(f"{args.report.name}: {outcome}")
        return 0

    if args.command == "verify-all":
        results = verify_all(args.scenario_declaration, args.definition)
        for key, value in results.items():
            print(f"{key}: {value}")
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
