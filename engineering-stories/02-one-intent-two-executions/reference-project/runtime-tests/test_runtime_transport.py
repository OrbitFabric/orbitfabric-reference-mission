from __future__ import annotations

import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import runtime_transport as rt


class FakeClock:
    def __init__(self, step_ns: int = 100_000_000):
        self.value = 0
        self.step = step_ns

    def __call__(self):
        current = self.value
        self.value += self.step
        return current


class FakeSerial:
    def __init__(self, reads=None):
        self.reads = list(reads or [])
        self.writes = []
        self.flush_count = 0

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return len(data)

    def flush(self) -> None:
        self.flush_count += 1

    def read(self, size: int) -> bytes:
        if self.reads:
            return self.reads.pop(0)
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
    logical[0] = 0x01
    logical[1] = 0x02
    logical[12:16] = uptime.to_bytes(4, "little")
    data = encrypt_secure_payload(bytes(logical))
    packet_id = rt.SPP_APID_STATUS
    sequence = (3 << 14) | sequence_count
    length_field = len(data) - 1
    return (
        packet_id.to_bytes(2, "big")
        + sequence.to_bytes(2, "big")
        + length_field.to_bytes(2, "big")
        + data
    )


class RuntimeTransportTests(unittest.TestCase):
    def test_frozen_g1_stimulus_identity_is_unchanged(self):
        raw = (
            ROOT / "artifacts" / "g1" / "pwnsat-health-check.tc.bin"
        ).read_bytes()
        rt.verify_frozen_stimulus(raw)
        self.assertEqual(rt.sha256_bytes(raw), rt.FROZEN_STIMULUS_SHA256)

    def test_usb_ingress_framing_wraps_but_does_not_modify_raw_spp(self):
        raw = (
            ROOT / "artifacts" / "g1" / "pwnsat-health-check.tc.bin"
        ).read_bytes()
        framed = rt.frame_usb_ingress(raw)
        self.assertEqual(framed[:2], b"\xAA\x55")
        self.assertEqual(int.from_bytes(framed[2:4], "big"), len(raw))
        self.assertEqual(framed[4:], raw)
        self.assertEqual(rt.sha256_bytes(raw), rt.FROZEN_STIMULUS_SHA256)

    def test_usb_egress_parser_uses_asymmetric_sync_plus_spp_length(self):
        first = build_status_tm(7, 100)
        second = build_status_tm(9, 101)
        stream = b"noise" + b"\xAA" + first + b"\xAA" + second + b"\xAA"
        packets, trailing = rt.iter_usb_egress_packets(stream)
        self.assertEqual(packets, [first, second])
        self.assertEqual(trailing, b"\xAA")

    def test_status_validation_extracts_native_sequence_and_uptime(self):
        raw = build_status_tm(321, 123456)
        status = rt.decode_status_tm(raw)
        self.assertEqual(status.sequence_count, 321)
        self.assertEqual(status.sequence_flags, 3)
        self.assertEqual(status.uptime_seconds, 123456)
        self.assertEqual(status.raw_spp_sha256, rt.sha256_bytes(raw))

    def test_status_validation_rejects_tc_even_with_status_apid(self):
        raw = bytearray(build_status_tm(1, 10))
        packet_id = int.from_bytes(raw[0:2], "big") | (1 << 12)
        raw[0:2] = packet_id.to_bytes(2, "big")
        with self.assertRaisesRegex(rt.RuntimeTransportError, "not telemetry"):
            rt.decode_status_tm(bytes(raw))

    def test_status_validation_rejects_secondary_header(self):
        raw = bytearray(build_status_tm(1, 10))
        packet_id = int.from_bytes(raw[0:2], "big") | (1 << 11)
        raw[0:2] = packet_id.to_bytes(2, "big")
        with self.assertRaisesRegex(rt.RuntimeTransportError, "secondary-header"):
            rt.decode_status_tm(bytes(raw))

    def test_present_primitive_uses_exact_framed_frozen_stimulus(self):
        stimulus = (
            ROOT / "artifacts" / "g1" / "pwnsat-health-check.tc.bin"
        ).read_bytes()
        reply = build_status_tm(10, 1000)
        fake = FakeSerial([b"\xAA" + reply])
        clock = FakeClock(step_ns=250_000_000)
        framed, capture = rt.present_frozen_stimulus(
            fake,
            stimulus,
            window_seconds=0.5,
            clock_ns=clock,
            sleep=lambda _: None,
        )
        self.assertEqual(fake.writes, [rt.frame_usb_ingress(stimulus)])
        self.assertEqual(fake.flush_count, 1)
        self.assertEqual(framed, fake.writes[0])
        self.assertEqual(capture.packets, (reply,))

    def test_present_primitive_fails_closed_on_changed_stimulus(self):
        stimulus = bytearray(
            (ROOT / "artifacts" / "g1" / "pwnsat-health-check.tc.bin").read_bytes()
        )
        stimulus[-1] ^= 0x01
        with self.assertRaisesRegex(rt.RuntimeTransportError, "identity differs"):
            rt.present_frozen_stimulus(
                FakeSerial(),
                bytes(stimulus),
                window_seconds=0.5,
                clock_ns=FakeClock(),
                sleep=lambda _: None,
            )

    def test_drain_until_quiet_retains_drained_bytes(self):
        fake = FakeSerial([b"abc", b""])
        clock = FakeClock(step_ns=100_000_000)
        drained = rt.drain_until_quiet(
            fake,
            0.1,
            max_seconds=1.0,
            clock_ns=clock,
            sleep=lambda _: None,
        )
        self.assertEqual(drained, b"abc")


if __name__ == "__main__":
    unittest.main()
