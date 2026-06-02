"""
Unit tests for the cleanliness (ICM contamination) channel.

Run:  python3 -m pytest tests/test_cleanliness.py -q
(or:  python3 -m unittest tests.test_cleanliness)

Hardware-free: the live Modbus driver is exercised only through its pure decode
helpers and a tiny fake client. British English throughout.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cleanliness import (  # noqa: E402
    ICM_NULL,
    CleanlinessChannel,
    CleanlinessLimit,
    CleanlinessReading,
    IcmModbusDriver,
    IcmStatus,
    SimulatedIcmDriver,
    decode_status,
    parse_iso_code,
    scaled_or_none,
    signed16,
    u32_from_pair,
)


# ---------------------------------------------------------------------------
# Pure decode helpers
# ---------------------------------------------------------------------------

class TestDecodeHelpers(unittest.TestCase):
    def test_signed16_positive_and_negative(self) -> None:
        self.assertEqual(signed16(0x0064), 100)
        self.assertEqual(signed16(0xFFFF), -1)        # "cleaner than class 0" sentinel
        self.assertEqual(signed16(0x8000), ICM_NULL)  # -32768

    def test_u32_from_pair_handles_counts_over_16_bit(self) -> None:
        self.assertEqual(u32_from_pair(0, 0), 0)
        self.assertEqual(u32_from_pair(0, 65535), 65535)
        self.assertEqual(u32_from_pair(1, 0), 65536)   # one above 16-bit range
        self.assertEqual(u32_from_pair(2, 3), 2 * 65536 + 3)

    def test_decode_status_known_and_unknown(self) -> None:
        self.assertEqual(decode_status(1), IcmStatus.READY)
        self.assertEqual(decode_status(2), IcmStatus.TESTING)
        self.assertEqual(decode_status(129), IcmStatus.FAULT_FLOW_LOW)
        self.assertEqual(decode_status(999), IcmStatus.NOT_READY)  # unknown → safe default

    def test_scaled_or_none_applies_factor_and_honours_null(self) -> None:
        self.assertAlmostEqual(scaled_or_none(1234, 100.0), 12.34)
        self.assertAlmostEqual(scaled_or_none(5678, 100.0), 56.78)
        self.assertIsNone(scaled_or_none(0x8000, 100.0))          # null, not -327.68

    def test_parse_iso_code(self) -> None:
        self.assertEqual(parse_iso_code("18/16/13"), (18, 16, 13))
        self.assertEqual(parse_iso_code(" 22 / 20 / 17 "), (22, 20, 17))
        with self.assertRaises(ValueError):
            parse_iso_code("18/16")


# ---------------------------------------------------------------------------
# Reading value object
# ---------------------------------------------------------------------------

class TestCleanlinessReading(unittest.TestCase):
    def test_iso_string(self) -> None:
        self.assertEqual(CleanlinessReading(iso_code=(18, 16, 13)).iso_string, "18/16/13")

    def test_valid_reading(self) -> None:
        self.assertTrue(CleanlinessReading(iso_code=(18, 16, 13)).is_valid)

    def test_null_band_is_invalid(self) -> None:
        self.assertFalse(CleanlinessReading(iso_code=(ICM_NULL, 16, 13)).is_valid)

    def test_fault_status_is_invalid(self) -> None:
        r = CleanlinessReading(iso_code=(18, 16, 13), status=IcmStatus.FAULT_FLOW_LOW)
        self.assertFalse(r.is_valid)

    def test_bad_sample_point_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CleanlinessReading(iso_code=(18, 16, 13), sample_point="nonsense")


# ---------------------------------------------------------------------------
# Acceptance — cleanliness_code grading
# ---------------------------------------------------------------------------

class TestCleanlinessGrading(unittest.TestCase):
    def setUp(self) -> None:
        self.limit = CleanlinessLimit.from_toml_section(
            {"mode": "cleanliness_code", "standard": "ISO4406:1999", "target": "18/16/13"}
        )

    def test_cleaner_than_target_passes(self) -> None:
        v = self.limit.grade(CleanlinessReading(iso_code=(17, 15, 12)))
        self.assertTrue(v.passed)
        self.assertEqual(v.per_band, (True, True, True))

    def test_equal_to_target_passes(self) -> None:
        # <= target, so exactly on the limit is a pass.
        self.assertTrue(self.limit.grade(CleanlinessReading(iso_code=(18, 16, 13))).passed)

    def test_one_dirty_band_fails(self) -> None:
        v = self.limit.grade(CleanlinessReading(iso_code=(18, 17, 13)))  # 2nd band over
        self.assertFalse(v.passed)
        self.assertEqual(v.per_band, (True, False, True))

    def test_invalid_reading_not_graded(self) -> None:
        v = self.limit.grade(CleanlinessReading(iso_code=(ICM_NULL, 16, 13)))
        self.assertIsNone(v.passed)
        self.assertIn("invalid", v.note)

    def test_from_toml_accepts_list_target(self) -> None:
        lim = CleanlinessLimit.from_toml_section({"target": [18, 16, 13]})
        self.assertEqual(lim.target, (18, 16, 13))

    def test_from_toml_rejects_wrong_mode(self) -> None:
        with self.assertRaises(ValueError):
            CleanlinessLimit.from_toml_section({"mode": "polyline", "target": "18/16/13"})


# ---------------------------------------------------------------------------
# Simulated driver + channel (end-to-end, hardware-free)
# ---------------------------------------------------------------------------

class TestSimulatedChannel(unittest.TestCase):
    def test_run_completes_immediately_and_tags_sample_point(self) -> None:
        scripted = CleanlinessReading(iso_code=(17, 15, 12))
        ch = CleanlinessChannel(driver=SimulatedIcmDriver(scripted))
        reading = ch.run(sample_point="unit_outlet")
        self.assertEqual(reading.sample_point, "unit_outlet")
        self.assertEqual(reading.iso_string, "17/15/12")

    def test_run_polls_through_testing_then_finishes(self) -> None:
        scripted = CleanlinessReading(iso_code=(17, 15, 12))
        driver = SimulatedIcmDriver(scripted, testing_polls=3)
        reading = CleanlinessChannel(driver=driver).run(sample_point="incoming_fluid")
        self.assertEqual(reading.sample_point, "incoming_fluid")
        self.assertEqual(driver.completion(), 1.0)

    def test_as_found_fails_as_left_passes(self) -> None:
        limit = CleanlinessLimit(target=(18, 16, 13))
        as_found = CleanlinessChannel(SimulatedIcmDriver(
            CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")), limit)
        as_left = CleanlinessChannel(SimulatedIcmDriver(
            CleanlinessReading(iso_code=(17, 15, 12))), limit)
        self.assertFalse(as_found.grade(as_found.run(sample_point="incoming_fluid")).passed)
        self.assertTrue(as_left.grade(as_left.run()).passed)


# ---------------------------------------------------------------------------
# Live Modbus driver via a fake client (decode path only — no real hardware)
# ---------------------------------------------------------------------------

class _FakeModbusClient:
    """Minimal stand-in exposing the adapter IcmModbusDriver expects."""

    def __init__(self, registers: dict[int, int]):
        self._r = registers

    def read_register(self, addr: int, node: int) -> int:
        return self._r.get(addr, 0)

    def read_registers(self, start: int, end: int, node: int) -> list[int]:
        return [self._r.get(a, 0) for a in range(start, end + 1)]

    def write_register(self, addr: int, value: int, node: int) -> None:
        self._r[addr] = value


class TestModbusDriverDecode(unittest.TestCase):
    def _registers(self) -> dict[int, int]:
        regs: dict[int, int] = {}
        # Result codes 56-63: ISO triple 18/16/13 then extra bands.
        for off, code in enumerate((18, 16, 13, 11, 9, 7, 5, 2)):
            regs[56 + off] = code
        # Counts 40-55: 8 pairs; make the 4µm count exceed 16-bit to exercise u32.
        regs[40], regs[41] = 2, 3          # = 2*65536 + 3
        regs[33] = 4400                     # 44.00 °C
        regs[34] = 1200                     # 12.00 % RH
        regs[37] = 250                      # flow ml/min
        regs[30] = 1                        # READY
        return regs

    def test_read_result_decodes_full_reading(self) -> None:
        client = _FakeModbusClient(self._registers())
        driver = IcmModbusDriver(client)
        r = driver.read_result(sample_point="unit_outlet")
        self.assertEqual(r.iso_code, (18, 16, 13))
        self.assertEqual(r.extra_codes, (11, 9, 7, 5, 2))
        self.assertEqual(r.counts_per_100ml[0], 2 * 65536 + 3)
        self.assertEqual(len(r.counts_per_100ml), 8)
        self.assertAlmostEqual(r.temperature_c, 44.0)
        self.assertAlmostEqual(r.water_rh_pct, 12.0)
        self.assertEqual(r.status, IcmStatus.READY)
        self.assertTrue(r.is_valid)

    def test_start_test_writes_command_register(self) -> None:
        client = _FakeModbusClient(self._registers())
        IcmModbusDriver(client).start_test(duration_s=120)
        self.assertEqual(client.read_register(21, 204), 1)    # COMMAND = start
        self.assertEqual(client.read_register(18, 204), 120)  # TEST_DURATION_S


if __name__ == "__main__":
    unittest.main()
