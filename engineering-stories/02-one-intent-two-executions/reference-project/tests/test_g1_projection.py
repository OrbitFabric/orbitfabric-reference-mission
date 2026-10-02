from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location(
    "g1_projection", SCRIPTS / "g1_projection.py"
)
g1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(g1)


class G1ProjectionUnitTests(unittest.TestCase):
    def test_pinned_target_baseline_is_exact(self):
        value = g1.load_json(g1.TARGET_BASELINE_PATH)
        g1.validate_target_baseline(value)
        self.assertEqual(value["repository"], "Pwnsat/FlatSat")
        self.assertEqual(
            value["commit_sha"],
            "b5ac0f2ba5e7bd60fbb6994f681c28053777628e",
        )

    def test_profile_binds_exact_canonical_command(self):
        profile, _ = g1.load_profile()
        binding = profile["bindings"][0]
        self.assertEqual(binding["id"], g1.MAPPING_ID)
        self.assertEqual(
            binding["sources"],
            [{"domain": "commands", "id": "obc.request_health_check"}],
        )
        self.assertEqual(binding["config"]["apid"], 12)

    def test_stimulus_is_exact_and_deterministic(self):
        baseline = g1.load_json(g1.TARGET_BASELINE_PATH)
        first = g1.build_stimulus(baseline)
        second = g1.build_stimulus(baseline)
        self.assertEqual(first, second)
        self.assertEqual(
            first.hex(),
            "100cc001000f7d6f6618f78734329b9c5fefd2cb969a",
        )
        self.assertEqual(
            g1.sha256_bytes(first),
            "db676bb1c080b87cc0bab375f5d2a170a57c4ff2134d41edc31bf37278f8813e",
        )

    def test_stimulus_is_raw_spp_not_usb_framed(self):
        raw = g1.build_stimulus(
            g1.load_json(g1.TARGET_BASELINE_PATH)
        )
        self.assertFalse(raw.startswith(b"\xaa\x55"))
        packet_id, sequence, length = __import__("struct").unpack(
            ">HHH", raw[:6]
        )
        self.assertEqual(packet_id & 0x07FF, 0x0C)
        self.assertEqual((packet_id >> 12) & 1, 1)
        self.assertEqual((sequence >> 14) & 0x03, 3)
        self.assertEqual(sequence & 0x3FFF, 1)
        self.assertEqual(length, 15)

    def test_accounting_marks_only_resolved_command_atom_projected(self):
        declaration = {
            "scenario": {"id": "r2_g0_health_check"},
            "source": {"scenario_sha256": "a" * 64},
            "atoms": [
                {"id": "atom-0001", "kind": "scenario_metadata"},
                {"id": "atom-0002", "kind": "initial_mode"},
                {"id": "atom-0003", "kind": "command"},
            ],
        }
        value = g1.accounting_payload(declaration, "atom-0003")
        by_id = {r["atom_id"]: r for r in value["records"]}
        self.assertEqual(
            by_id["atom-0003"]["disposition"], "projected"
        )
        self.assertEqual(
            by_id["atom-0003"]["mapping_ids"], [g1.MAPPING_ID]
        )
        self.assertEqual(
            by_id["atom-0001"]["disposition"], "not_projected"
        )
        self.assertEqual(
            by_id["atom-0002"]["disposition"], "not_projected"
        )

    def test_wrong_target_baseline_fails_closed(self):
        value = g1.load_json(g1.TARGET_BASELINE_PATH)
        value["commit_sha"] = "0" * 40
        with self.assertRaises(g1.G1Error):
            g1.validate_target_baseline(value)

    def test_wrong_profile_command_fails_closed(self):
        original = g1.PROFILE_PATH
        raw = original.read_text(encoding="utf-8")
        with __import__("tempfile").TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "profile.yaml"
            candidate.write_text(
                raw.replace(
                    "obc.request_health_check", "obc.other"
                ),
                encoding="utf-8",
            )
            g1.PROFILE_PATH = candidate
            try:
                with self.assertRaises(g1.G1Error):
                    g1.load_profile()
            finally:
                g1.PROFILE_PATH = original


if __name__ == "__main__":
    unittest.main()
