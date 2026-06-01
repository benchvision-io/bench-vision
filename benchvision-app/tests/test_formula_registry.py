"""
Unit tests for the formula engine: registry, pure formulas, and profile loading.

Run:  python3 -m pytest tests/test_formula_registry.py -q
(or:  python3 -m unittest tests.test_formula_registry)

British English throughout.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from formula_registry import (  # noqa: E402
    FormulaNotFoundError,
    FormulaSpec,
    MissingInputError,
    build_default_registry,
)
from pump_profile import PumpProfile  # noqa: E402

PROFILE_PATH = Path(__file__).resolve().parents[1] / "profiles" / "pc200-8-hpv95.toml"


class TestRegistryMechanics(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = build_default_registry()

    def test_resolves_three_reference_styles(self) -> None:
        for ref in ("pump_flow_linear", "pump_flow_linear_v1", "pump_flow_linear@v1"):
            self.assertEqual(self.reg.resolve(ref).name, "pump_flow_linear")

    def test_missing_formula_raises(self) -> None:
        with self.assertRaises(FormulaNotFoundError):
            self.reg.resolve("does_not_exist_v9")

    def test_missing_input_raises(self) -> None:
        with self.assertRaises(MissingInputError):
            self.reg.evaluate("pump_flow_linear_v1", {"pressure_bar": 100.0})  # no constants

    def test_refuses_silent_overwrite_of_different_fn(self) -> None:
        spec = FormulaSpec(
            name="pump_flow_linear", version="v1", summary="x",
            required_inputs=(), output_unit="L/min", fn=lambda i: 0.0,
        )
        with self.assertRaises(ValueError):
            self.reg.register(spec)


class TestPumpFlowFormulas(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = build_default_registry()

    def test_linear_matches_old_hardcoded(self) -> None:
        inp = {"no_load_flow": 245.0, "flow_pressure_slope": 0.5}
        for p in (0, 100, 200, 400, 600):
            expected = max(0.0, 245.0 - 0.5 * p)
            got = self.reg.evaluate("pump_flow_linear_v1", {**inp, "pressure_bar": float(p)})
            self.assertAlmostEqual(got, expected, places=9)

    def test_destroke_is_flat_below_cutin(self) -> None:
        inp = {"no_load_flow": 224.0, "pc_cutin_bar": 130.0, "power_const": 29120.0}
        for p in (0, 50, 100, 130):
            got = self.reg.evaluate("pump_flow_pc_destroke_v1", {**inp, "pressure_bar": float(p)})
            self.assertAlmostEqual(got, 224.0, places=6)

    def test_destroke_is_constant_power_above_cutin(self) -> None:
        inp = {"no_load_flow": 224.0, "pc_cutin_bar": 130.0, "power_const": 29120.0}
        # Q·P should be ~constant in the destroke region.
        for p in (150, 200, 250, 300, 400):
            q = self.reg.evaluate("pump_flow_pc_destroke_v1", {**inp, "pressure_bar": float(p)})
            self.assertAlmostEqual(q * p, 29120.0, delta=1.0)

    def test_destroke_matches_chart_within_2lpm(self) -> None:
        profile = PumpProfile.from_toml(PROFILE_PATH)
        chart = {0: 224, 150: 194, 200: 146, 250: 116, 300: 97, 350: 83, 400: 73}
        for p, q_chart in chart.items():
            q = self.reg.evaluate(
                profile.channels["flow"].formula, profile.flow_inputs(float(p))
            )
            self.assertLess(abs(q - q_chart), 2.0, f"at {p} bar: {q:.1f} vs chart {q_chart}")


class TestTorqueAndPower(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = build_default_registry()

    def test_absorption_torque_plateaus_from_live_flow(self) -> None:
        # Feed the destroke flow into the torque formula; torque should rise then plateau.
        flow_inp = {"no_load_flow": 224.0, "pc_cutin_bar": 130.0, "power_const": 29120.0}
        shared = {"rpm": 2000.0, "n_sections": 2.0, "mech_efficiency": 0.90}
        torques = []
        for p in (50, 100, 150, 200, 250, 300, 350, 400):
            q = self.reg.evaluate("pump_flow_pc_destroke_v1", {**flow_inp, "pressure_bar": float(p)})
            t = self.reg.evaluate(
                "absorption_torque_from_flow_v1",
                {**shared, "pressure_bar": float(p), "flow_lpm": q},
            )
            torques.append(t)
        # Rises through the full-stroke region…
        self.assertLess(torques[0], torques[2])
        # …then flat in the constant-power region (250→400 bar within a few Nm).
        plateau = torques[4:]
        self.assertLess(max(plateau) - min(plateau), 5.0)

    def test_torque_tracks_chart_in_full_stroke_region(self) -> None:
        # ≤130 bar the engine should track the digitised chart NOMINAL torque closely.
        # (Corrected 2026-06-01: the old {50:190,100:395,130:510} were the engine's own
        # constant-η outputs mislabelled as "chart". The real digitised callouts are
        # 269/426/519; the [efficiency] curve makes the engine reproduce them.)
        profile = PumpProfile.from_toml(PROFILE_PATH)
        chart = {50: 269, 100: 426, 130: 519}
        for p, t_chart in chart.items():
            q = self.reg.evaluate(profile.channels["flow"].formula, profile.flow_inputs(float(p)))
            t = self.reg.evaluate(profile.channels["torque"].formula, profile.torque_inputs(float(p), q))
            self.assertLess(abs(t - t_chart), 12.0, f"at {p} bar: {t:.0f} vs chart {t_chart}")

    def test_torque_tracks_chart_in_destroke_region(self) -> None:
        # Above the PC knee the engine must climb to the chart's ~627 Nm plateau, NOT
        # sit flat at the constant-power ~515 Nm. This is what the [efficiency] curve buys
        # (2026-06-01): the formula is unchanged; only the per-pressure η differs.
        profile = PumpProfile.from_toml(PROFILE_PATH)
        chart = {170: 589, 240: 621, 270: 632, 300: 630, 400: 630}
        for p, t_chart in chart.items():
            q = self.reg.evaluate(profile.channels["flow"].formula, profile.flow_inputs(float(p)))
            t = self.reg.evaluate(profile.channels["torque"].formula, profile.torque_inputs(float(p), q))
            self.assertLess(abs(t - t_chart), 15.0, f"at {p} bar: {t:.0f} vs chart {t_chart}")

    def test_efficiency_curve_supersedes_scalar(self) -> None:
        # With the curve, η at 50 bar is the friction-dominated low value (~0.66), not 0.90.
        profile = PumpProfile.from_toml(PROFILE_PATH)
        self.assertIsNotNone(profile.efficiency)
        self.assertAlmostEqual(profile.efficiency.eta_at(50.0), 0.6627, places=3)
        self.assertAlmostEqual(profile.efficiency.eta_at(130.0), 0.8930, places=3)
        # torque_inputs feeds the curve value, not the scalar fallback
        self.assertAlmostEqual(profile.torque_inputs(50.0, 224.0)["mech_efficiency"], 0.6627, places=3)

    def test_zero_speed_gives_zero_torque(self) -> None:
        t = self.reg.evaluate(
            "absorption_torque_from_flow_v1",
            {"pressure_bar": 200.0, "flow_lpm": 100.0, "rpm": 0.0,
             "n_sections": 2.0, "mech_efficiency": 0.9},
        )
        self.assertEqual(t, 0.0)

    def test_radial_torque_sin90_collapses(self) -> None:
        t = self.reg.evaluate(
            "radial_torque_sin90_v1",
            {"force_n": 1000.0, "shaft_diameter_mm": 50.0, "angle_deg": 90.0},
        )
        self.assertAlmostEqual(t, 1000.0 * 0.025, places=9)  # r = 25 mm = 0.025 m, sin90 = 1

    def test_power_formula(self) -> None:
        kw = self.reg.evaluate(
            "power_from_flow_pressure_v1", {"pressure_bar": 300.0, "flow_lpm": 100.0}
        )
        self.assertAlmostEqual(kw, 300.0 * 100.0 / 600.0, places=9)


class TestProfileLoading(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = PumpProfile.from_toml(PROFILE_PATH)

    def test_displacement_kept_separate(self) -> None:
        d = self.profile.displacement
        self.assertEqual(d.theoretical_cc_per_rev, 95.0)
        self.assertEqual(d.machine_adjusted_flow_cc_per_rev, 112.0)
        self.assertEqual(d.active_cc_per_rev, 112.0)  # mode = machine_adjusted

    def test_acceptance_band_interpolates(self) -> None:
        lo, hi = self.profile.acceptance["flow"].limits_at(175.0)
        # between the 150 (181–217) and 200 (145–179) rows of the chart-read band
        self.assertTrue(145 < lo < 181)
        self.assertTrue(179 < hi < 217)

    def test_flow_band_tracks_chart_limits(self) -> None:
        # The flow acceptance band is the chart's printed Upper/Lower limit lines,
        # transcribed 2026-06-01 from Fig.1 (mirrors test_torque_tracks_chart_*).
        # limits_at returns (lower, upper). Assert the printed callouts land exactly
        # on the band vertices, each cross-checked against its {kgf/cm²} pair on read.
        band = self.profile.acceptance["flow"]
        # UPPER = dotted "Upper limit (Reference value)" printed callouts.
        upper = {240: 148.5, 358: 99.2, 380: 94.0}
        for p, u_chart in upper.items():
            _lo, hi = band.limits_at(float(p))
            self.assertAlmostEqual(hi, u_chart, places=1,
                                   msg=f"upper at {p} bar: {hi} vs chart {u_chart}")
        # LOWER = solid "Lower limit" printed callouts.
        lower = {250: 108.5, 380: 59.3}
        for p, l_chart in lower.items():
            lo, _hi = band.limits_at(float(p))
            self.assertAlmostEqual(lo, l_chart, places=1,
                                   msg=f"lower at {p} bar: {lo} vs chart {l_chart}")
        # Band is ordered (upper strictly above lower) across the whole sweep,
        # and widens on destroke (the upper line is a generous "Reference value").
        for p in (0, 50, 100, 130, 150, 200, 250, 300, 350, 380):
            lo, hi = band.limits_at(float(p))
            self.assertGreater(hi, lo, f"band inverted at {p} bar")
        self.assertGreater(band.limits_at(380.0)[1] - band.limits_at(380.0)[0],
                           band.limits_at(0.0)[1] - band.limits_at(0.0)[0])

    def test_shaft_prompts_operator(self) -> None:
        self.assertTrue(self.profile.shaft.operator_prompt)


if __name__ == "__main__":
    unittest.main()
