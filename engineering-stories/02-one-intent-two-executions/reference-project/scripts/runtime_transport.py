#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Protocol

import serial

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

USB_INGRESS_SYNC = b"\xAA\x55"
USB_EGRESS_SYNC = 0xAA
SPP_PRIMARY_HEADER_LEN = 6
SPP_APID_STATUS = 0x0C
SPP_PACKET_TYPE_TM = 0
SPP_PACKET_TYPE_TC = 1
SERIAL_BAUD = 921600
SECURE_LINK_KEY = b"PWNsatLabKey1234"
FROZEN_STIMULUS_SHA256 = (
    "db676bb1c080b87cc0bab375f5d2a170"
    "a57c4ff2134d41edc31bf37278f8813e"
)


class RuntimeTransportError(ValueError):
    pass


class SerialLike(Protocol):
    def write(self, data: bytes) -> int: ...
    def flush(self) -> None: ...
    def read(self, size: int) -> bytes: ...


@dataclass(frozen=True)
class SPPPacket:
    raw: bytes
    version: int
    packet_type: int
    secondary_header: bool
    apid: int
    sequence_flags: int
    sequence_count: int
    length_field: int
    data: bytes

    @property
    def packet_type_name(self) -> str:
        return "TM" if self.packet_type == SPP_PACKET_TYPE_TM else "TC"


@dataclass(frozen=True)
class StatusTelemetry:
    raw_spp_sha256: str
    sequence_count: int
    sequence_flags: int
    uptime_seconds: int
    logical_payload: bytes


@dataclass(frozen=True)
class CaptureResult:
    raw_stream: bytes
    packets: tuple[bytes, ...]
    trailing: bytes
    window_start_ns: int
    window_end_ns: int


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify_frozen_stimulus(raw_spp: bytes) -> None:
    actual = sha256_bytes(raw_spp)
    if actual != FROZEN_STIMULUS_SHA256:
        raise RuntimeTransportError(
            "raw SPP stimulus identity differs from accepted G1 frozen stimulus"
        )


def frame_usb_ingress(raw_spp: bytes) -> bytes:
    if not raw_spp:
        raise RuntimeTransportError("raw SPP stimulus is empty")
    if len(raw_spp) > 0xFFFF:
        raise RuntimeTransportError("raw SPP stimulus is too large for USB ingress frame")
    return USB_INGRESS_SYNC + len(raw_spp).to_bytes(2, "big") + raw_spp


def iter_usb_egress_packets(stream: bytes) -> tuple[list[bytes], bytes]:
    """Mirror FlatSat/PWNSAT host parser semantics for USB telemetry egress.

    Firmware egress is asymmetric with ingress: one 0xAA sync byte is followed
    directly by raw SPP. Packet size is recovered from the SPP primary-header
    length field.
    """
    packets: list[bytes] = []
    offset = 0

    while offset < len(stream):
        if stream[offset] != USB_EGRESS_SYNC:
            offset += 1
            continue
        if len(stream) - offset < 7:
            break

        length_field = int.from_bytes(stream[offset + 5 : offset + 7], "big")
        total = 1 + SPP_PRIMARY_HEADER_LEN + length_field + 1
        if len(stream) - offset < total:
            break

        packets.append(stream[offset + 1 : offset + total])
        offset += total

    return packets, stream[offset:]


def parse_spp(raw: bytes) -> SPPPacket:
    if len(raw) < SPP_PRIMARY_HEADER_LEN:
        raise RuntimeTransportError("raw SPP packet is shorter than primary header")

    packet_id = int.from_bytes(raw[0:2], "big")
    sequence = int.from_bytes(raw[2:4], "big")
    length_field = int.from_bytes(raw[4:6], "big")
    data_len = length_field + 1
    expected_total = SPP_PRIMARY_HEADER_LEN + data_len
    if len(raw) != expected_total:
        raise RuntimeTransportError(
            f"raw SPP length mismatch: expected {expected_total}, got {len(raw)}"
        )

    version = (packet_id >> 13) & 0x07
    if version != 0:
        raise RuntimeTransportError(f"unsupported CCSDS SPP version {version}")

    packet_type = (packet_id >> 12) & 0x01
    secondary_header = bool((packet_id >> 11) & 0x01)
    apid = packet_id & 0x07FF
    sequence_flags = (sequence >> 14) & 0x03
    sequence_count = sequence & 0x3FFF

    return SPPPacket(
        raw=raw,
        version=version,
        packet_type=packet_type,
        secondary_header=secondary_header,
        apid=apid,
        sequence_flags=sequence_flags,
        sequence_count=sequence_count,
        length_field=length_field,
        data=raw[SPP_PRIMARY_HEADER_LEN:],
    )


def decrypt_secure_payload(ciphertext: bytes) -> bytes:
    if not ciphertext or len(ciphertext) % 16:
        raise RuntimeTransportError(
            "secure-link payload must be a non-empty AES block multiple"
        )
    decryptor = Cipher(
        algorithms.AES(SECURE_LINK_KEY), modes.ECB()
    ).decryptor()
    plain = decryptor.update(ciphertext) + decryptor.finalize()
    if len(plain) < 2:
        raise RuntimeTransportError("secure-link plaintext is too short")
    payload_len = int.from_bytes(plain[0:2], "big")
    if payload_len > len(plain) - 2:
        raise RuntimeTransportError(
            "secure-link logical payload length exceeds decrypted bytes"
        )
    return plain[2 : 2 + payload_len]


def decode_status_tm(raw_spp: bytes) -> StatusTelemetry:
    packet = parse_spp(raw_spp)
    if packet.packet_type != SPP_PACKET_TYPE_TM:
        raise RuntimeTransportError("STATUS evidence is not telemetry")
    if packet.apid != SPP_APID_STATUS:
        raise RuntimeTransportError(
            f"telemetry APID 0x{packet.apid:03X} is not TM_STATUS"
        )
    if packet.secondary_header:
        raise RuntimeTransportError(
            "current R2 STATUS criterion does not accept a secondary-header packet"
        )

    logical = decrypt_secure_payload(packet.data)
    if len(logical) < 26:
        raise RuntimeTransportError(
            "TM_STATUS logical payload is shorter than pinned source layout"
        )
    uptime = int.from_bytes(logical[12:16], "little")

    return StatusTelemetry(
        raw_spp_sha256=sha256_bytes(raw_spp),
        sequence_count=packet.sequence_count,
        sequence_flags=packet.sequence_flags,
        uptime_seconds=uptime,
        logical_payload=logical,
    )


def capture_window(
    serial_link: SerialLike,
    window_seconds: float,
    *,
    clock_ns=time.monotonic_ns,
    sleep=time.sleep,
    read_size: int = 4096,
    poll_seconds: float = 0.01,
) -> CaptureResult:
    if window_seconds <= 0:
        raise RuntimeTransportError("observation window must be positive")
    start = clock_ns()
    deadline = start + int(window_seconds * 1_000_000_000)
    received = bytearray()
    now = start
    while now < deadline:
        chunk = serial_link.read(read_size)
        if chunk:
            received.extend(chunk)
        else:
            sleep(poll_seconds)
        now = clock_ns()

    packets, trailing = iter_usb_egress_packets(bytes(received))
    return CaptureResult(
        raw_stream=bytes(received),
        packets=tuple(packets),
        trailing=trailing,
        window_start_ns=start,
        window_end_ns=now,
    )


def drain_until_quiet(
    serial_link: SerialLike,
    quiet_seconds: float,
    *,
    max_seconds: float,
    clock_ns=time.monotonic_ns,
    sleep=time.sleep,
    read_size: int = 4096,
    poll_seconds: float = 0.01,
) -> bytes:
    if quiet_seconds <= 0 or max_seconds <= 0 or quiet_seconds > max_seconds:
        raise RuntimeTransportError("invalid quiescence timing")

    started = clock_ns()
    hard_deadline = started + int(max_seconds * 1_000_000_000)
    quiet_deadline = started + int(quiet_seconds * 1_000_000_000)
    drained = bytearray()

    while True:
        now = clock_ns()
        if now >= hard_deadline:
            raise RuntimeTransportError(
                "observation channel did not become quiescent before timeout"
            )
        chunk = serial_link.read(read_size)
        if chunk:
            drained.extend(chunk)
            quiet_deadline = clock_ns() + int(quiet_seconds * 1_000_000_000)
            continue
        if now >= quiet_deadline:
            return bytes(drained)
        sleep(poll_seconds)


def present_frozen_stimulus(
    serial_link: SerialLike,
    raw_spp: bytes,
    *,
    window_seconds: float,
    clock_ns=time.monotonic_ns,
    sleep=time.sleep,
) -> tuple[bytes, CaptureResult]:
    """Live boundary primitive.

    This function is intentionally not called by offline CI. The caller must
    first establish the Story preconditions and channel quiescence.
    """
    verify_frozen_stimulus(raw_spp)
    framed = frame_usb_ingress(raw_spp)
    written = serial_link.write(framed)
    if written != len(framed):
        raise RuntimeTransportError(
            f"short USB presentation write: {written}/{len(framed)} bytes"
        )
    serial_link.flush()
    capture = capture_window(
        serial_link,
        window_seconds,
        clock_ns=clock_ns,
        sleep=sleep,
    )
    return framed, capture


def initialize_live_serial_dependency(timeout_seconds: float = 0.05):
    """Initialize pyserial without opening or probing any hardware."""
    link = serial.Serial(
        port=None,
        baudrate=SERIAL_BAUD,
        timeout=timeout_seconds,
    )
    if link.is_open:
        link.close()
        raise RuntimeTransportError(
            "pyserial dependency check unexpectedly opened a serial port"
        )
    return link


def open_serial_link(port: str, timeout_seconds: float = 0.05):
    """Open the authorized wired CDC link only when explicitly invoked live."""
    if not port:
        raise RuntimeTransportError("explicit serial port is required")
    return serial.Serial(
        port=port,
        baudrate=SERIAL_BAUD,
        timeout=timeout_seconds,
    )
