from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import g0_contracts as g0  # noqa: E402

SCENARIO = PROJECT_ROOT / "scenario" / "r2_g0_health_check.yaml"
DEFINITION = PROJECT_ROOT / "fixtures" / "experiment-definition.synthetic.json"
OBSERVATIONS = PROJECT_ROOT / "fixtures" / "observations"
EXPECTED_DEFINITION_SHA256 = "489e538c1a88525b2ce06ed2681cfc5e5110685e177cdaf2a59660144489d8f1"


class G0ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.definition_bytes = DEFINITION.read_bytes()
        cls.definition = json.loads(cls.definition_bytes)
        g0.validate_definition(cls.definition)

    def _load_report(self, name: str) -> dict:
        return json.loads((OBSERVATIONS / name).read_text(encoding="utf-8"))

    def _export_core_declaration(self, output: Path) -> dict:
        result = subprocess.run(
            [
                "orbitfabric",
                "export",
                "scenario-declaration",
                str(SCENARIO),
                "--json",
                str(output),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(output.read_text(encoding="utf-8"))

    def test_story_local_scenario_is_exported_by_current_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            declaration = self._export_core_declaration(Path(tmp) / "scenario-declaration.json")
        self.assertEqual(declaration["result"], "loaded")
        self.assertEqual(declaration["scenario"]["id"], "r2_g0_health_check")
        self.assertEqual(
            declaration["source"]["scenario_sha256"],
            self.definition["scenario"]["sha256"],
        )

    def test_command_atom_is_resolved_from_core_declaration_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            declaration = self._export_core_declaration(Path(tmp) / "scenario-declaration.json")
        atom = g0.resolve_command_atom(declaration, g0.COMMAND_ID)
        self.assertEqual(
            atom["references"],
            [
                {
                    "role": "command",
                    "entity": {"domain": "commands", "id": "obc.request_health_check"},
                }
            ],
        )
        self.assertEqual(atom["id"], self.definition["scenario"]["atom_id"])

    def test_retained_definition_is_byte_identical_to_core_derived_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            declaration_path = tmp_path / "scenario-declaration.json"
            declaration = self._export_core_declaration(declaration_path)
            materialized = g0.definition_from_scenario_declaration(declaration)
            output = tmp_path / "experiment-definition.json"
            g0.write_json_deterministic(output, materialized)
            self.assertEqual(output.read_bytes(), self.definition_bytes)

    def test_definition_identity_is_stable_exact_bytes(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.definition_bytes).hexdigest(),
            EXPECTED_DEFINITION_SHA256,
        )
        self.assertNotIn("sha256", self.definition)

    def test_authorized_invocation_a_is_deterministic_and_attempt_scoped(self) -> None:
        digest = hashlib.sha256(self.definition_bytes).hexdigest()
        local_id = self.definition["authorized_instance"]["local_id"]
        first = g0.derive_authorized_invocation(digest, "attempt-one", local_id)
        repeated = g0.derive_authorized_invocation(digest, "attempt-one", local_id)
        changed = g0.derive_authorized_invocation(digest, "attempt-two", local_id)
        self.assertEqual(first, repeated)
        self.assertNotEqual(first, changed)

    def test_authorized_invocation_a_changes_with_definition_digest(self) -> None:
        digest = hashlib.sha256(self.definition_bytes).hexdigest()
        changed_digest = hashlib.sha256(self.definition_bytes + b"\n").hexdigest()
        local_id = self.definition["authorized_instance"]["local_id"]
        self.assertNotEqual(
            g0.derive_authorized_invocation(digest, "attempt-one", local_id),
            g0.derive_authorized_invocation(changed_digest, "attempt-one", local_id),
        )

    def test_scenario_atom_is_not_authorized_invocation_a(self) -> None:
        digest = hashlib.sha256(self.definition_bytes).hexdigest()
        value = g0.derive_authorized_invocation(
            digest,
            "attempt-one",
            self.definition["authorized_instance"]["local_id"],
        )
        self.assertNotEqual(self.definition["scenario"]["atom_id"], value)

    def test_conformant_fixture_recomputes_conformant(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        self.assertEqual(g0.validate_report(self.definition_bytes, report), "CONFORMANT")

    def test_diverged_fixture_recomputes_diverged(self) -> None:
        report = self._load_report("diverged.synthetic.json")
        self.assertEqual(g0.validate_report(self.definition_bytes, report), "DIVERGED")

    def test_inconclusive_fixture_recomputes_inconclusive(self) -> None:
        report = self._load_report("inconclusive.synthetic.json")
        self.assertEqual(g0.validate_report(self.definition_bytes, report), "INCONCLUSIVE")
        self.assertIsNone(report["observed_execution_count"])
        self.assertTrue(report["diagnostics"])

    def test_invalid_run_fixture_is_semantic_not_malformed(self) -> None:
        report = self._load_report("invalid-run.synthetic.json")
        self.assertEqual(g0.validate_report(self.definition_bytes, report), "INVALID_RUN")
        self.assertFalse(report["preconditions"]["identity_binding_valid"])
        self.assertTrue(report["diagnostics"])

    def test_wrong_definition_digest_fails_closed(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        report["experiment_definition_sha256"] = "0" * 64
        with self.assertRaisesRegex(g0.ContractError, "exact Experiment Definition"):
            g0.validate_report(self.definition_bytes, report)

    def test_expected_count_mismatch_fails_closed(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        report["expected_execution_count"] = 2
        with self.assertRaisesRegex(g0.ContractError, "expected_execution_count"):
            g0.validate_report(self.definition_bytes, report)

    def test_observed_count_mismatch_fails_closed(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        report["observed_execution_count"] = 2
        with self.assertRaisesRegex(g0.ContractError, "accepted occurrence"):
            g0.validate_report(self.definition_bytes, report)

    def test_missing_required_identity_fails_schema(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        del report["execution_attempt_id"]
        with self.assertRaisesRegex(g0.ContractError, "schema validation failed"):
            g0.validate_report(self.definition_bytes, report)

    def test_unsupported_kind_fails_schema(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        report["kind"] = "orbitfabric.future_generic_runtime_contract"
        with self.assertRaisesRegex(g0.ContractError, "schema validation failed"):
            g0.validate_report(self.definition_bytes, report)

    def test_unsupported_version_fails_schema(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        report["format_version"] = "9.9"
        with self.assertRaisesRegex(g0.ContractError, "schema validation failed"):
            g0.validate_report(self.definition_bytes, report)

    def test_unknown_property_fails_closed_schema(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        report["future_runtime_semantics"] = {}
        with self.assertRaisesRegex(g0.ContractError, "schema validation failed"):
            g0.validate_report(self.definition_bytes, report)

    def test_wrong_authorized_invocation_fails_closed(self) -> None:
        report = self._load_report("conformant.synthetic.json")
        report["authorized_instance"]["authorized_invocation_id"] = "r2a:" + "0" * 64
        with self.assertRaisesRegex(g0.ContractError, "authorized invocation A"):
            g0.validate_report(self.definition_bytes, report)

    def test_incomplete_evidence_cannot_fabricate_observed_count(self) -> None:
        report = self._load_report("inconclusive.synthetic.json")
        report["observed_execution_count"] = 0
        with self.assertRaisesRegex(g0.ContractError, "must not fabricate"):
            g0.validate_report(self.definition_bytes, report)


if __name__ == "__main__":
    unittest.main()
