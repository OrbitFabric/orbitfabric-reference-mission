from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import runtime_bundle as rb
import runtime_evidence as ev
import runtime_phase as rp
import runtime_transport as rt


class FakeClock:
    def __init__(self, step_ns: int = 50_000_000):
        self.value = 0
        self.step = step_ns

    def __call__(self):
        current = self.value
        self.value += self.step
        return current


class ScriptedSerial:
    def __init__(self, responses_by_write):
        self.responses_by_write = list(responses_by_write)
        self.pending = []
        self.writes = []
        self.flush_count = 0

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        response = self.responses_by_write.pop(0) if self.responses_by_write else b""
        if response:
            self.pending.append(response)
        return len(data)

    def flush(self) -> None:
        self.flush_count += 1

    def read(self, size: int) -> bytes:
        if self.pending:
            return self.pending.pop(0)
        return b""


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


def egress(*packets: bytes) -> bytes:
    return b"".join(b"\xAA" + packet for packet in packets)


def definition():
    return ev.build_experiment_definition(
        window_seconds=0.2,
        pre_quiet_seconds=0.05,
    )


class RuntimePhaseTests(unittest.TestCase):
    def test_two_distinct_status_occurrences_truthfully_assess_diverged(self):
        link = ScriptedSerial(
            [
                egress(build_status_tm(20, 1000)),
                egress(build_status_tm(21, 1001)),
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = rp.run_attempt(
                serial_link=link,
                output_dir=Path(tmp),
                execution_attempt_id="attempt-diverged",
                definition=definition(),
                controlled_runtime_authorized=True,
                exclusive_command_source=True,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )
            report = result["report"]
            self.assertEqual(report["assessment"], "DIVERGED")
            self.assertEqual(report["evidence_status"], "complete")
            self.assertEqual(report["observed_execution_count"], 2)
            self.assertEqual(len(report["execution_occurrences"]), 2)
            self.assertEqual([p["id"] for p in report["presentations"]], ["P1", "P2"])
            self.assertEqual(len(link.writes), 2)
            self.assertEqual(result["identities"], result["verified"])

    def test_no_second_status_truthfully_assesses_conformant(self):
        link = ScriptedSerial(
            [
                egress(build_status_tm(20, 1000)),
                b"",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = rp.run_attempt(
                serial_link=link,
                output_dir=Path(tmp),
                execution_attempt_id="attempt-conformant",
                definition=definition(),
                controlled_runtime_authorized=True,
                exclusive_command_source=True,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )
            report = result["report"]
            self.assertEqual(report["assessment"], "CONFORMANT")
            self.assertEqual(report["evidence_status"], "complete")
            self.assertEqual(report["observed_execution_count"], 1)
            self.assertEqual(len(report["execution_occurrences"]), 1)
            self.assertEqual(len(link.writes), 2)

    def test_ambiguous_p1_is_inconclusive_and_does_not_present_p2(self):
        link = ScriptedSerial(
            [
                egress(
                    build_status_tm(20, 1000),
                    build_status_tm(21, 1000),
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = rp.run_attempt(
                serial_link=link,
                output_dir=Path(tmp),
                execution_attempt_id="attempt-ambiguous",
                definition=definition(),
                controlled_runtime_authorized=True,
                exclusive_command_source=True,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )
            report = result["report"]
            self.assertEqual(report["assessment"], "INCONCLUSIVE")
            self.assertEqual(report["evidence_status"], "ambiguous")
            self.assertIsNone(report["observed_execution_count"])
            self.assertEqual(len(report["presentations"]), 1)
            self.assertEqual(len(link.writes), 1)
            self.assertTrue(
                any(
                    d["code"] == "g2_nominal_occurrence_not_established"
                    for d in report["diagnostics"]
                )
            )

    def test_missing_runtime_control_precondition_is_invalid_without_write(self):
        link = ScriptedSerial([])
        with tempfile.TemporaryDirectory() as tmp:
            result = rp.run_attempt(
                serial_link=link,
                output_dir=Path(tmp),
                execution_attempt_id="attempt-invalid",
                definition=definition(),
                controlled_runtime_authorized=False,
                exclusive_command_source=True,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )
            report = result["report"]
            self.assertEqual(report["assessment"], "INVALID_RUN")
            self.assertEqual(report["runtime"]["status"], "ABORTED")
            self.assertEqual(link.writes, [])

    def test_evidence_set_contains_runtime_and_accepted_g1_bytes(self):
        link = ScriptedSerial(
            [
                egress(build_status_tm(20, 1000)),
                b"",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = rp.run_attempt(
                serial_link=link,
                output_dir=root,
                execution_attempt_id="attempt-bundle",
                definition=definition(),
                controlled_runtime_authorized=True,
                exclusive_command_source=True,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )
            manifest = ev.load_json(root / "evidence-set.json")
            record_ids = {record["id"] for record in manifest["records"]}
            self.assertIn("experiment-definition", record_ids)
            self.assertIn("execution-observation", record_ids)
            self.assertIn("runtime-trace", record_ids)
            self.assertIn("accepted-g1-integration-result", record_ids)
            self.assertIn("accepted-g1-scenario-accounting", record_ids)
            self.assertIn("accepted-g1-frozen-stimulus", record_ids)
            self.assertEqual(
                result["identities"]["evidence_set_sha256"],
                ev.sha256_file(root / "evidence-set.json"),
            )

    def test_clean_fake_repeat_reproduces_exact_bundle_identities(self):
        responses = [
            egress(build_status_tm(20, 1000)),
            egress(build_status_tm(21, 1001)),
        ]
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first = rp.run_attempt(
                serial_link=ScriptedSerial(list(responses)),
                output_dir=Path(a),
                execution_attempt_id="attempt-repeat",
                definition=definition(),
                controlled_runtime_authorized=True,
                exclusive_command_source=True,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )
            second = rp.run_attempt(
                serial_link=ScriptedSerial(list(responses)),
                output_dir=Path(b),
                execution_attempt_id="attempt-repeat",
                definition=definition(),
                controlled_runtime_authorized=True,
                exclusive_command_source=True,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )
            self.assertEqual(first["identities"], second["identities"])
            self.assertEqual(
                (Path(a) / "SHA256SUMS").read_bytes(),
                (Path(b) / "SHA256SUMS").read_bytes(),
            )

    def test_bundle_verifier_rejects_mutated_raw_occurrence_packet(self):
        link = ScriptedSerial(
            [
                egress(build_status_tm(20, 1000)),
                b"",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rp.run_attempt(
                serial_link=link,
                output_dir=root,
                execution_attempt_id="attempt-tamper",
                definition=definition(),
                controlled_runtime_authorized=True,
                exclusive_command_source=True,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )
            packet = next((root / "captures" / "P1").glob("packet-*.spp.bin"))
            packet.write_bytes(packet.read_bytes() + b"\x00")
            with self.assertRaises(Exception):
                rb.verify_runtime_bundle(root)


if __name__ == "__main__":
    unittest.main()
