"""
Unit tests for the test-definition data format, the pure settle evaluator, and the manual
checklist (``test_definition.py``) — the *sequence-intent* seam.

Run:  python3 -m unittest tests.test_test_definition

These prove the load-bearing properties:
  * settle is honest — it settles on a genuinely stable window and does **not** settle on an
    unsettled (bouncing) window even when the target pressure is crossed (today's real-bench
    failure mode the rising-ramp capture had);
  * the definition is **one source of truth** — its operating points are the flow band's own
    gridpoints, and the SAME definition object feeds both the sequencer and the checklist.

British English throughout; mirrors the style of ``tests/test_sequencer.py``.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bench_simulator import BenchSimulator  # noqa: E402
from pump_profile import PumpProfile  # noqa: E402
from sequencer import default_grid_pressures  # noqa: E402
from test_definition import (  # noqa: E402
    SettleCondition,
    TestDefinition,
    derive_gridpoints,
    is_settled,
    render_manual_checklist,
)

PROFILE_PATH = Path(__file__).resolve().parents[1] / "profiles" / "pc200-8-hpv95.toml"


# ---------------------------------------------------------------------------
# The pure settle evaluator — the honesty guarantee
# ---------------------------------------------------------------------------

class TestIsSettled(unittest.TestCase):
    def setUp(self) -> None:
        # Default: pressure within ±5 bar of target, window spread ≤ 6 bar, for 7 ticks.
        self.cond = SettleCondition(
            channel="pressure", at_target_bar=5.0, stable_within=6.0, for_ticks=7
        )

    def test_settles_on_a_stable_window_at_target(self) -> None:
        win = [200.4, 199.6, 200.1, 199.8, 200.2, 200.0, 199.9]   # flat at 200, spread < 6
        self.assertTrue(
            is_settled(self.cond, target_bar=200.0,
                       pressure_window=win, channel_window=win, dt=0.1)
        )

    def test_does_not_settle_on_an_unsettled_window_even_at_target(self) -> None:
        # The real-bench failure mode: pressure is hovering AROUND the target (so a naive
        # "p >= target" crossing test would capture) but is still BOUNCING — spread 16 bar,
        # well over the 6 bar tolerance. Must NOT settle.
        win = [196.0, 204.0, 195.0, 205.0, 197.0, 203.0, 200.0]   # mean ≈ 200, spread = 10
        self.assertFalse(
            is_settled(self.cond, target_bar=200.0,
                       pressure_window=win, channel_window=win, dt=0.1)
        )

    def test_does_not_settle_when_not_at_target(self) -> None:
        # Perfectly stable, but parked 30 bar away from the declared point — not this point.
        win = [170.0] * 7
        self.assertFalse(
            is_settled(self.cond, target_bar=200.0,
                       pressure_window=win, channel_window=win, dt=0.1)
        )

    def test_does_not_settle_before_the_dwell_is_met(self) -> None:
        win = [200.0] * 5   # only 5 samples; needs 7
        self.assertFalse(
            is_settled(self.cond, target_bar=200.0,
                       pressure_window=win, channel_window=win, dt=0.1)
        )

    def test_rising_ramp_window_does_not_settle(self) -> None:
        # A rising ramp through the target (≈1.2 bar/tick): the window straddling 200 spans
        # ~8 bar and the early samples are >5 bar from target → not settled. This is exactly
        # the capture-on-the-way-up that the seam retires.
        win = [196.4, 197.6, 198.8, 200.0, 201.2, 202.4, 203.6]
        self.assertFalse(
            is_settled(self.cond, target_bar=200.0,
                       pressure_window=win, channel_window=win, dt=0.1)
        )

    def test_max_abs_rate_variant(self) -> None:
        cond = SettleCondition(
            channel="flow", at_target_bar=5.0, stable_within=None,
            max_abs_rate=20.0, for_ticks=5,
        )
        pressure = [200.0] * 5
        slow = [120.0, 120.5, 119.8, 120.2, 120.0]              # |Δ/dt| ≈ 5/s ≤ 20
        fast = [120.0, 125.0, 118.0, 127.0, 119.0]              # big jumps → |Δ/dt| ≫ 20
        self.assertTrue(is_settled(cond, target_bar=200.0,
                                   pressure_window=pressure, channel_window=slow, dt=0.1))
        self.assertFalse(is_settled(cond, target_bar=200.0,
                                    pressure_window=pressure, channel_window=fast, dt=0.1))

    def test_settle_condition_needs_a_stability_test(self) -> None:
        with self.assertRaises(ValueError):
            SettleCondition(stable_within=None, max_abs_rate=None)


# ---------------------------------------------------------------------------
# The data format — loading + one source of truth
# ---------------------------------------------------------------------------

class TestTestDefinitionLoading(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = PumpProfile.from_toml(PROFILE_PATH)

    def test_profile_carries_a_test_definition(self) -> None:
        self.assertIsNotNone(self.profile.test)
        self.assertEqual(len(self.profile.test.points), 11)

    def test_points_are_the_flow_band_gridpoints_one_source_of_truth(self) -> None:
        # The operating points are DERIVED from the flow band — not a duplicated list.
        from_band = derive_gridpoints(self.profile.acceptance["flow"])
        self.assertEqual(self.profile.test.point_pressures, from_band)
        # And the sequencer's grid helper routes through the same definition.
        self.assertEqual(default_grid_pressures(self.profile), from_band)

    def test_every_point_has_a_settle_condition_in_channel_terms(self) -> None:
        for pt in self.profile.test.points:
            self.assertIsInstance(pt.settle, SettleCondition)
            self.assertIn(pt.settle.channel, {"pressure", "flow", "torque"})
            # At least one stability test is present (enforced by SettleCondition).
            self.assertTrue(pt.settle.stable_within is not None or pt.settle.max_abs_rate is not None)

    def test_per_point_override_layers_onto_the_global_default(self) -> None:
        raw = {
            "operating_points": "acceptance.flow",
            "settle": {"channel": "pressure", "at_target_bar": 5.0,
                       "stable_within": 6.0, "for_ticks": 7},
            "point_settle": [{"pressure": 380.0, "stable_within": 3.0}],
        }
        td = TestDefinition.from_raw(raw, flow_band=self.profile.acceptance["flow"])
        self.assertEqual(td.settle_at(380.0).stable_within, 3.0)   # overridden
        self.assertEqual(td.settle_at(380.0).for_ticks, 7)         # inherited from global
        self.assertEqual(td.settle_at(200.0).stable_within, 6.0)   # global default elsewhere

    def test_default_for_band_when_no_test_section(self) -> None:
        td = TestDefinition.from_raw(None, flow_band=self.profile.acceptance["flow"])
        self.assertIsNone(td)   # no [test] → None; caller synthesises
        synth = TestDefinition.default_for_band(self.profile.acceptance["flow"])
        self.assertEqual(synth.point_pressures, derive_gridpoints(self.profile.acceptance["flow"]))


# ---------------------------------------------------------------------------
# Consumer surfaces — same definition feeds the checklist AND the sequencer
# ---------------------------------------------------------------------------

class TestConsumers(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = PumpProfile.from_toml(PROFILE_PATH)
        self.test_def = self.profile.test

    def test_manual_checklist_renders_every_point_and_its_settle(self) -> None:
        text = render_manual_checklist(self.test_def, self.profile)
        # One checklist item per operating point, each carrying its settle condition.
        for pt in self.test_def.points:
            self.assertIn(f"{pt.pressure_bar:g} bar", text)
        self.assertEqual(text.count("settle:"), len(self.test_def.points))
        # Torque is named as a monitored reference (never graded) on the human path too.
        self.assertIn("monitored reference", text)

    def test_sequencer_and_checklist_consume_the_same_definition(self) -> None:
        # The single source of truth: the pressures the sequencer would visit are exactly the
        # pressures the checklist lists — both come from the one TestDefinition.
        from run_record import RunRecordBuilder, TestPurpose
        from sequencer import TestSequencer, simulated_sources

        sim = BenchSimulator(sample_rate_hz=10.0)
        purpose = TestPurpose(intent="verification", repair_stage="as_left")
        builder = RunRecordBuilder(
            id="T", profile="pc200-8-hpv95", dut_serial="SN", operator="t",
            po_number="PO", purpose=purpose, mode="training",
        )
        seq = TestSequencer(sim, builder, simulated_sources(sim), realtime=False)
        self.assertEqual(seq.grid_pressures, self.test_def.point_pressures)
        self.assertIs(seq.test_def, sim.profile.test)

        checklist = render_manual_checklist(seq.test_def, sim.profile)
        for p in seq.grid_pressures:
            self.assertIn(f"{p:g} bar", checklist)


if __name__ == "__main__":
    unittest.main()
