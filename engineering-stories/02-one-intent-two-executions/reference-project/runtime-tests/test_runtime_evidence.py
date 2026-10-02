from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import runtime_evidence as ev
import runtime_transport as rt


def encrypt_secure_payload(payload: bytes) -> bytes:
    plain = len(payload).to_bytes(2, "big") + payload
    if len(plain) % 16:
        plain += b"\x00" * (16 - (len(plain) % 16))
    enc = Cipher(
        algorithms.AES(rt.SECURE_LINK_KEY), modes.ECB()
    ).encryptor()
    return enc.update(plain) + enc.finalize()


def build_status_tm(sequence_count: int, uptime: int) -> bytes:
    logical = bytearray(26)
    logical[12:16] = uptime.to_bytes(4, "little")
    data = encrypt_secure_payload(bytes(logical))
    packet_id = rt.SPP_APID_STATUS
    sequence = (3 << 14) | sequence_count
    return (
        packet_id.to_bytes(2, "big")
        + sequence.to_bytes(2, "big")
        + (len(data) - 1).to_bytes(2, "big")
        + data
    )


class RuntimeEvidenceTests(unittest.TestCase):
    def test_frozen_g1_chain_is_exact(self):
        identities = ev.verify_frozen_g1_inputs()
        self.assertEqual(
            identities,
            {
                "profile_sha256": ev.PROFILE_SHA256,
                "source_baseline_sha256": ev.SOURCE_BASELINE_SHA256,
                "mapping_sha256": ev.MAPPING_SHA256,
                "stimulus_sha256": rt.FROZEN_STIMULUS_SHA256,
                "scenario_accounting_sha256": ev.ACCOUNTING_SHA256,
                "integration_result_sha256": ev.INTEGRATION_RESULT_SHA256,
            },
        )

    def test_transport_baseline_is_wired_only_and_pinned(self):
        digest = ev.verify_transport_source_baseline()
        self.assertEqual(len(digest), 64)
        baseline = ev.load_json(ev.TRANSPORT_BASELINE_PATH)
        self.assertEqual(baseline["commit_sha"], ev.TARGET_COMMIT)
        self.assertTrue(baseline["transport"]["wired_local_only"])
        self.assertFalse(baseline["transport"]["rf"])

    def test_occurrence_criterion_is_frozen_and_status_alone_insufficient(self):
        digest = ev.criterion_identity()
        self.assertEqual(len(digest), 64)
        criterion = ev.load_json(ev.CRITERION_PATH)
        self.assertFalse(
            criterion["acceptance"]["status_alone_is_sufficient"]
        )
        self.assertEqual(
            criterion["acceptance"]["ambiguous_attribution_result"],
            "INCONCLUSIVE",
        )

    def test_runtime_experiment_definition_is_additive_v0_2_story(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        self.assertEqual(definition["format_version"], "0.2-story")
        self.assertEqual(
            definition["projection"]["stimulus_sha256"],
            rt.FROZEN_STIMULUS_SHA256,
        )
        self.assertEqual(
            definition["authorized_instance"]["expected_execution_count"], 1
        )
        self.assertEqual(
            [x["id"] for x in definition["presentations"]],
            ["P1", "P2"],
        )
        self.assertTrue(definition["provenance"]["g0_0_1_story_unchanged"])

    def test_authorized_invocation_is_run_scoped_and_stable_per_attempt(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        a1 = ev.authorized_invocation_id(definition, "attempt-001")
        a1_again = ev.authorized_invocation_id(definition, "attempt-001")
        a2 = ev.authorized_invocation_id(definition, "attempt-002")
        self.assertEqual(a1, a1_again)
        self.assertNotEqual(a1, a2)
        self.assertTrue(a1.startswith("r2a:"))

    def test_unique_p1_status_can_be_accepted_as_e1(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        a = ev.authorized_invocation_id(definition, "attempt-001")
        raw = build_status_tm(20, 1000)
        occurrence, state, diagnostics = ev.evaluate_status_window(
            [raw],
            presentation_id="P1",
            authorized_invocation=a,
            prior_accepted=None,
        )
        self.assertEqual(state, "accepted")
        self.assertEqual(diagnostics, [])
        self.assertIsNotNone(occurrence)
        self.assertEqual(occurrence["presentation_id"], "P1")
        self.assertEqual(occurrence["tm_sequence_count"], 20)
        self.assertEqual(occurrence["status_uptime_seconds"], 1000)

    def test_status_alone_is_not_enough_when_attribution_is_ambiguous(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        a = ev.authorized_invocation_id(definition, "attempt-001")
        occurrence, state, diagnostics = ev.evaluate_status_window(
            [build_status_tm(20, 1000), build_status_tm(21, 1000)],
            presentation_id="P1",
            authorized_invocation=a,
            prior_accepted=None,
        )
        self.assertIsNone(occurrence)
        self.assertEqual(state, "ambiguous")
        self.assertEqual(diagnostics[0]["code"], "ambiguous_status_candidates")

    def test_second_occurrence_requires_distinct_tm_sequence_and_evidence(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        a = ev.authorized_invocation_id(definition, "attempt-001")
        first, _, _ = ev.evaluate_status_window(
            [build_status_tm(20, 1000)],
            presentation_id="P1",
            authorized_invocation=a,
            prior_accepted=None,
        )
        second, state, diagnostics = ev.evaluate_status_window(
            [build_status_tm(20, 1001)],
            presentation_id="P2",
            authorized_invocation=a,
            prior_accepted=first,
        )
        self.assertIsNone(second)
        self.assertEqual(state, "ambiguous")
        self.assertEqual(diagnostics[0]["code"], "non_distinct_tm_sequence")

    def test_second_occurrence_rejects_uptime_regression(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        a = ev.authorized_invocation_id(definition, "attempt-001")
        first, _, _ = ev.evaluate_status_window(
            [build_status_tm(20, 1000)],
            presentation_id="P1",
            authorized_invocation=a,
            prior_accepted=None,
        )
        second, state, diagnostics = ev.evaluate_status_window(
            [build_status_tm(21, 999)],
            presentation_id="P2",
            authorized_invocation=a,
            prior_accepted=first,
        )
        self.assertIsNone(second)
        self.assertEqual(state, "ambiguous")
        self.assertEqual(diagnostics[0]["code"], "uptime_regression")

    def test_distinct_later_status_can_be_accepted_as_e2(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        a = ev.authorized_invocation_id(definition, "attempt-001")
        first, _, _ = ev.evaluate_status_window(
            [build_status_tm(20, 1000)],
            presentation_id="P1",
            authorized_invocation=a,
            prior_accepted=None,
        )
        second, state, diagnostics = ev.evaluate_status_window(
            [build_status_tm(22, 1001)],
            presentation_id="P2",
            authorized_invocation=a,
            prior_accepted=first,
        )
        self.assertEqual(state, "accepted")
        self.assertEqual(diagnostics, [])
        self.assertIsNotNone(second)
        self.assertNotEqual(first["id"], second["id"])

    def test_no_status_is_not_fabricated_as_occurrence(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        a = ev.authorized_invocation_id(definition, "attempt-001")
        occurrence, state, diagnostics = ev.evaluate_status_window(
            [],
            presentation_id="P2",
            authorized_invocation=a,
            prior_accepted=None,
        )
        self.assertIsNone(occurrence)
        self.assertEqual(state, "none")
        self.assertEqual(diagnostics, [])

    def test_not_run_report_has_no_semantic_assessment_or_fake_evidence(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        report = ev.build_not_run_report(
            definition,
            execution_attempt_id="attempt-not-run",
            reason="controlled FlatSat runtime is not available to this execution environment",
        )
        self.assertEqual(report["runtime"]["status"], "NOT_RUN")
        self.assertEqual(report["evidence_status"], "not_run")
        self.assertIsNone(report["assessment"])
        self.assertIsNone(report["observed_execution_count"])
        self.assertEqual(report["presentations"], [])
        self.assertEqual(report["execution_occurrences"], [])
        self.assertIsNone(ev.derive_assessment(report))

    def test_assessment_is_count_based_when_evidence_is_complete(self):
        base = {
            "runtime": {"status": "COMPLETE"},
            "preconditions": {
                "identity_binding_valid": True,
                "controlled_runtime_authorized": True,
                "exclusive_command_source": True,
                "observation_channel_clearable": True,
            },
            "evidence_status": "complete",
            "expected_execution_count": 1,
        }
        conformant = {**base, "observed_execution_count": 1}
        diverged = {**base, "observed_execution_count": 2}
        self.assertEqual(ev.derive_assessment(conformant), "CONFORMANT")
        self.assertEqual(ev.derive_assessment(diverged), "DIVERGED")

    def test_ambiguous_evidence_assesses_inconclusive(self):
        report = {
            "runtime": {"status": "COMPLETE"},
            "preconditions": {
                "identity_binding_valid": True,
                "controlled_runtime_authorized": True,
                "exclusive_command_source": True,
                "observation_channel_clearable": True,
            },
            "evidence_status": "ambiguous",
            "expected_execution_count": 1,
            "observed_execution_count": None,
        }
        self.assertEqual(ev.derive_assessment(report), "INCONCLUSIVE")

    def test_invalid_precondition_assesses_invalid_run(self):
        report = {
            "runtime": {"status": "COMPLETE"},
            "preconditions": {
                "identity_binding_valid": True,
                "controlled_runtime_authorized": True,
                "exclusive_command_source": False,
                "observation_channel_clearable": True,
            },
            "evidence_status": "complete",
            "expected_execution_count": 1,
            "observed_execution_count": 1,
        }
        self.assertEqual(ev.derive_assessment(report), "INVALID_RUN")

    def test_retained_capture_keeps_exact_raw_stream_and_packets(self):
        definition = ev.build_experiment_definition(
            window_seconds=1.0,
            pre_quiet_seconds=0.1,
        )
        a = ev.authorized_invocation_id(definition, "attempt-001")
        stimulus = (
            ROOT / "artifacts" / "g1" / "pwnsat-health-check.tc.bin"
        ).read_bytes()
        raw = build_status_tm(20, 1000)
        stream = b"\xAA" + raw
        presentation = ev.presentation_record(
            presentation_id="P1",
            authorized_invocation=a,
            stimulus_raw=stimulus,
            raw_stream=stream,
            status="PRESENTED",
            window_start_ns=10,
            window_end_ns=20,
            channel_cleared=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            retained = ev.retain_capture(
                Path(tmp),
                presentation=presentation,
                raw_stream=stream,
                packets=[raw],
            )
            self.assertEqual(
                retained["raw_stream_sha256"], rt.sha256_bytes(stream)
            )
            self.assertEqual(
                retained["packets"][0]["sha256"], rt.sha256_bytes(raw)
            )


if __name__ == "__main__":
    unittest.main()
