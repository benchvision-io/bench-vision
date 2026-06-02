"""
Integration tests: cleanliness wired into the pump profile and the bench sequence.

Run:  python3 -m pytest tests/test_cleanliness_integration.py -q

These touch ``pump_profile`` (tomllib) and ``bench_simulator`` (numpy), unlike the
pure ``test_cleanliness.py``. British English throughout.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cleanliness import CleanlinessLimit, CleanlinessReading  # noqa: E402
from pump_profile import PumpProfile  # noqa: E402

PROFILE_PATH = Path(__file__).resolve().parents[1] / "profiles" / "pc200-8-hpv95.toml"


class TestProfileCleanliness(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = PumpProfile.from_toml(PROFILE_PATH)

    def test_cleanliness_limit_parsed(self) -> None:
        self.assertIsInstance(self.profile.cleanliness, CleanlinessLimit)
        self.assertEqual(self.profile.cleanliness.target, (18, 16, 13))

    def test_cleanliness_excluded_from_pressure_bands(self) -> None:
        # The polyline acceptance dict must still hold only flow/torque — not cleanliness.
        self.assertIn("flow", self.profile.acceptance)
        self.assertIn("torque", self.profile.acceptance)
        self.assertNotIn("cleanliness", self.profile.acceptance)

    def test_profile_limit_grades(self) -> None:
        passed = self.profile.cleanliness.grade(CleanlinessReading(iso_code=(17, 15, 12)))
        failed = self.profile.cleanliness.grade(CleanlinessReading(iso_code=(19, 16, 13)))
        self.assertTrue(passed.passed)
        self.assertFalse(failed.passed)


class TestBenchSequence(unittest.TestCase):
    def setUp(self) -> None:
        from bench_simulator import BenchSimulator
        self.sim = BenchSimulator(sample_rate_hz=10.0)

    def test_default_cleanliness_test_passes(self) -> None:
        result = self.sim.run_cleanliness_test(sample_point="unit_outlet")
        self.assertTrue(result["passed"])
        self.assertEqual(result["sample_point"], "unit_outlet")

    def test_scripted_dirty_sample_fails(self) -> None:
        dirty = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")
        result = self.sim.run_cleanliness_test(
            sample_point="incoming_fluid", scripted=dirty
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["iso_code"], "22/20/17")

    def test_full_sequence_as_found_dirty_as_left_clean(self) -> None:
        dirty = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")
        seq = self.sim.run_cleanliness_sequence(reference="PO-1", incoming=dirty)
        self.assertEqual(set(seq), {"rig_supply", "incoming_fluid", "unit_outlet"})
        self.assertFalse(seq["incoming_fluid"]["passed"])   # as-found dirty
        self.assertTrue(seq["unit_outlet"]["passed"])        # as-left clean


if __name__ == "__main__":
    unittest.main()
