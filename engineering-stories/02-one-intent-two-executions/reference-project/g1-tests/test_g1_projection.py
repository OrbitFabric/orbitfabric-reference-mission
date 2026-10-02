from __future__ import annotations

import copy
import importlib.util
import shutil
import struct
import sys
import tempfile
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
    def _current_inputs(self):
        profile, _ = g1.load_profile()
        baseline = g1.load_json(g1.TARGET_BASELINE_PATH)
        g1.validate_target_baseline(baseline)
        projection = g1.resolve_profile_projection(profile, baseline)
        return profile, baseline, projection

    def test_pinned_target_baseline_is_exact(self):
        value = g1.load_json(g1.TARGET_BASELINE_PATH)
        g1.validate_target_baseline(value)
        self.assertEqual(value["repository"], "Pwnsat/FlatSat")
        self.assertEqual(
            value["commit_sha"],
            "b5ac0f2ba5e7bd60fbb6994f681c28053777628e",
        )
        self.assertEqual(
            {(item["path"], item["blob_sha"]) for item in value["source_files"]},
            {
                ("Firmware/mission.h", "13dd456f26f83ac3b186065c3f7d12e60234afa0"),
                ("Firmware/worker.cpp", "1c3b7e9db506732f77c3214a38b297c0d8625323"),
                ("Firmware/spp.h", "ebd15fc88edcd9c77d2d421eeb890a700c291dc9"),
                ("Firmware/spp.cpp", "a5ec274e7f3b2fd72da432ff4211d30c809e6131"),
                ("Firmware/secure_link.cpp", "a02de14460d41961f0acaf40178bfd68fae686be"),
            },
        )

    def test_source_baseline_does_not_own_fixed_sequence_count(self):
        profile, baseline, projection = self._current_inputs()
        packet = baseline["packet_projection"]
        self.assertNotIn("sequence_count", packet)
        self.assertEqual(
            packet["sequence_counter"],
            {
                "field_bits": 14,
                "initial_value": 0,
                "increment": "before_packet_construction",
                "stateful": True,
                "fixed_source_constant": False,
            },
        )
        self.assertEqual(
            projection["sequence_count"],
            profile["settings"]["sequence_count"],
        )
        self.assertEqual(projection["sequence_count"], 1)

    def test_retained_artifacts_bind_exact_source_baseline_identity(self):
        source_sha = g1.sha256_file(g1.TARGET_BASELINE_PATH)
        self.assertEqual(
            source_sha,
            "b6e5a6d04a37d1fb29dd2c00f1c81d22cfae65626564160b2fa11dd80cc4ca5e",
        )
        mapping = g1.load_json(g1.RETAINED_DIR / g1.MAPPING_FILENAME)
        result = g1.load_json(g1.RETAINED_DIR / g1.RESULT_FILENAME)
        self.assertEqual(
            mapping["target_baseline"]["source_baseline_sha256"],
            source_sha,
        )
        self.assertEqual(
            result["evidence"][0]["source_baseline_sha256"],
            source_sha,
        )
        self.assertEqual(
            result["resolutions"][0]["source_baseline_sha256"],
            source_sha,
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

    def test_current_profile_resolves_all_packet_projection_choices(self):
        profile, baseline, projection = self._current_inputs()
        self.assertEqual(profile["settings"]["sequence_count"], 1)
        self.assertEqual(projection["sequence_count"], 1)
        self.assertEqual(projection["sequence_flags_name"], "unsegmented")
        self.assertEqual(projection["sequence_flags"], 3)
        self.assertFalse(projection["secondary_header"])
        self.assertEqual(
            projection["secure_link_intent"], "firmware_default_enabled"
        )
        self.assertTrue(projection["secure_link_enabled"])
        self.assertEqual(
            baseline["packet_projection"]["secure_link"]["enabled"], True
        )

    def test_stimulus_is_exact_and_deterministic_for_current_profile(self):
        _, baseline, projection = self._current_inputs()
        first = g1.build_stimulus(baseline, projection)
        second = g1.build_stimulus(baseline, projection)
        self.assertEqual(first, second)
        self.assertEqual(
            first.hex(),
            "100cc001000f7d6f6618f78734329b9c5fefd2cb969a",
        )
        self.assertEqual(
            g1.sha256_bytes(first),
            "db676bb1c080b87cc0bab375f5d2a170a57c4ff2134d41edc31bf37278f8813e",
        )

    def test_retained_stimulus_is_exact_current_profile_projection(self):
        _, baseline, projection = self._current_inputs()
        retained = g1.RETAINED_DIR / g1.STIMULUS_FILENAME
        self.assertEqual(
            retained.read_bytes(),
            g1.build_stimulus(baseline, projection),
        )

    def test_sequence_count_change_changes_projected_stimulus(self):
        profile, baseline, current = self._current_inputs()
        changed = copy.deepcopy(profile)
        changed["settings"]["sequence_count"] = 2
        resolved = g1.resolve_profile_projection(changed, baseline)
        current_bytes = g1.build_stimulus(baseline, current)
        changed_bytes = g1.build_stimulus(baseline, resolved)
        self.assertNotEqual(changed_bytes, current_bytes)
        _, sequence, _ = struct.unpack(">HHH", changed_bytes[:6])
        self.assertEqual(sequence & 0x3FFF, 2)

    def test_unsupported_sequence_flags_fail_closed(self):
        profile, baseline, _ = self._current_inputs()
        changed = copy.deepcopy(profile)
        changed["settings"]["sequence_flags"] = "continuation"
        with self.assertRaisesRegex(g1.G1Error, "sequence_flags"):
            g1.resolve_profile_projection(changed, baseline)

    def test_unsupported_secondary_header_choice_fails_closed(self):
        profile, baseline, _ = self._current_inputs()
        changed = copy.deepcopy(profile)
        changed["settings"]["secondary_header"] = True
        with self.assertRaisesRegex(g1.G1Error, "secondary_header"):
            g1.resolve_profile_projection(changed, baseline)

    def test_secure_link_intent_cannot_disagree_with_pinned_default(self):
        profile, baseline, _ = self._current_inputs()
        changed = copy.deepcopy(profile)
        changed["settings"]["secure_link"] = "disabled"
        with self.assertRaisesRegex(g1.G1Error, "secure_link"):
            g1.resolve_profile_projection(changed, baseline)

    def test_missing_packet_projection_setting_fails_closed(self):
        profile, baseline, _ = self._current_inputs()
        changed = copy.deepcopy(profile)
        changed["settings"].pop("sequence_count")
        original = g1.PROFILE_PATH
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "profile.yaml"
            import yaml
            candidate.write_text(
                yaml.safe_dump(changed, sort_keys=False),
                encoding="utf-8",
            )
            g1.PROFILE_PATH = candidate
            try:
                with self.assertRaisesRegex(g1.G1Error, "missing required settings"):
                    g1.load_profile()
            finally:
                g1.PROFILE_PATH = original

    def test_mapping_uses_same_resolved_profile_packet_choices(self):
        _, baseline, projection = self._current_inputs()
        retained = g1.load_json(g1.RETAINED_DIR / g1.MAPPING_FILENAME)
        target = retained["target"]
        self.assertEqual(target["sequence_count"], projection["sequence_count"])
        self.assertEqual(target["sequence_flags"], projection["sequence_flags"])
        self.assertEqual(
            target["secondary_header"], projection["secondary_header"]
        )
        self.assertEqual(
            target["secure_link"], projection["secure_link_label"]
        )

    def test_stimulus_is_raw_spp_not_usb_framed(self):
        _, baseline, projection = self._current_inputs()
        raw = g1.build_stimulus(baseline, projection)
        self.assertFalse(raw.startswith(b"\xaa\x55"))
        packet_id, sequence, length = struct.unpack(">HHH", raw[:6])
        self.assertEqual(packet_id & 0x07FF, 0x0C)
        self.assertEqual((packet_id >> 12) & 1, 1)
        self.assertEqual((packet_id >> 11) & 1, 0)
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
        self.assertEqual(by_id["atom-0003"]["disposition"], "projected")
        self.assertEqual(by_id["atom-0003"]["mapping_ids"], [g1.MAPPING_ID])
        self.assertEqual(by_id["atom-0001"]["disposition"], "not_projected")
        self.assertEqual(by_id["atom-0002"]["disposition"], "not_projected")

    def test_retained_mapping_makes_no_runtime_claim(self):
        mapping = g1.load_json(g1.RETAINED_DIR / g1.MAPPING_FILENAME)
        self.assertFalse(mapping["runtime_claim"])
        self.assertEqual(
            mapping["boundary"],
            "PROJECTED != TRANSMITTED != EXECUTED != OBSERVED",
        )

    def test_wrong_target_baseline_fails_closed(self):
        value = g1.load_json(g1.TARGET_BASELINE_PATH)
        value["commit_sha"] = "0" * 40
        with self.assertRaises(g1.G1Error):
            g1.validate_target_baseline(value)

    def test_wrong_profile_command_fails_closed(self):
        original = g1.PROFILE_PATH
        raw = original.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "profile.yaml"
            candidate.write_text(
                raw.replace("obc.request_health_check", "obc.other"),
                encoding="utf-8",
            )
            g1.PROFILE_PATH = candidate
            try:
                with self.assertRaises(g1.G1Error):
                    g1.load_profile()
            finally:
                g1.PROFILE_PATH = original

    def test_retained_byte_change_fails_closed(self):
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left = Path(left_dir)
            right = Path(right_dir)
            for name in [
                g1.STIMULUS_FILENAME,
                g1.MAPPING_FILENAME,
                g1.ACCOUNTING_FILENAME,
                g1.RESULT_FILENAME,
            ]:
                shutil.copyfile(g1.RETAINED_DIR / name, left / name)
                shutil.copyfile(g1.RETAINED_DIR / name, right / name)
            (right / g1.STIMULUS_FILENAME).write_bytes(
                (right / g1.STIMULUS_FILENAME).read_bytes() + b"\x00"
            )
            with self.assertRaises(g1.G1Error):
                g1.compare_dirs(left, right)


if __name__ == "__main__":
    unittest.main()
