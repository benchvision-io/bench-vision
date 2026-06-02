"""
Unit tests for the test sequencer (``sequencer.py``) and the ``RunRecordBuilder``.

Run:  python3 -m unittest discover -s tests
(or:  python3 -m unittest tests.test_sequencer)

Hardware-free; every run is stepped (``realtime=False``) so **no test ever enters the
real-time sleep path** — one test proves it by making ``time.sleep`` raise. Channel RNGs
are seeded so grading outcomes are deterministic. British English throughout; mirrors the
style of ``tests/test_run_record.py``.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sequencer as sequencer_mod  # noqa: E402
from bench_simulator import BenchSimulator  # noqa: E402
from cleanliness import CleanlinessReading  # noqa: E402
from run_record import (  # noqa: E402
    ChannelResult,
    Provenance,
    RunRecord,
    RunRecordBuilder,
    TestPurpose,
)
from sequencer import (  # noqa: E402
    SequenceState,
    SimulatedChannelSource,
    TestSequencer,
    default_grid_pressures,
    simulated_sources,
)

#: A seed verified to yield an all-points-pass run on the PC200-8 profile.
CLEAN_PASS_SEED = 1000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed(sim: BenchSimulator, base: int = CLEAN_PASS_SEED) -> None:
    for i, ch in enumerate(sim.channels + sim.derived_channels):
        ch.rng = np.random.default_rng(base + i)


def _builder(purpose: TestPurpose) -> RunRecordBuilder:
    return RunRecordBuilder(
        id="TEST-0001", profile="pc200-8-hpv95", dut_serial="SN-TEST",
        operator="tester", po_number="PO-TEST", purpose=purpose, mode="training",
    )


def _sequencer(
    *,
    intent: str = "verification",
    seed: int = CLEAN_PASS_SEED,
    incoming: CleanlinessReading | None = None,
) -> TestSequencer:
    sim = BenchSimulator(sample_rate_hz=10.0)
    _seed(sim, seed)
    purpose = TestPurpose(intent=intent, repair_stage="as_left", context="repair_overhaul")
    return TestSequencer(
        sim, _builder(purpose), simulated_sources(sim),
        realtime=False, incoming_sample=incoming, reference="PO-TEST",
    )


def _inject_cavitation_at(t_seconds: float):
    """An ``on_tick`` hook that injects a cavitation fault once ``t`` is reached."""
    fired = {"done": False}

    def hook(sim: BenchSimulator) -> None:
        if not fired["done"] and sim.elapsed_time >= t_seconds:
            sim.flow.inject_fault_cavitation()
            fired["done"] = True

    return hook


class _MeasuredFlowSource:
    """A test double standing in for a live (measured) flow source. Returns a fixed
    value; declares ``measured`` provenance and no formula — proving the sequencer records
    what the source declares rather than hard-coding ``derived``."""

    channel = "flow"
    unit = "L/min"
    provenance = Provenance.MEASURED
    formula = ""

    def __init__(self, value: float) -> None:
        self._value = value

    def read(self) -> float:
        return self._value


# ---------------------------------------------------------------------------
# default_grid_pressures
# ---------------------------------------------------------------------------

class TestGridPressures(unittest.TestCase):
    def test_excludes_zero_and_is_sorted(self) -> None:
        sim = BenchSimulator(sample_rate_hz=10.0)
        grid = default_grid_pressures(sim.profile)
        self.assertNotIn(0.0, grid)
        self.assertEqual(list(grid), sorted(grid))
        self.assertEqual(grid[-1], 380.0)   # certified ceiling, last band point


# ---------------------------------------------------------------------------
# State-machine transitions
# ---------------------------------------------------------------------------

class TestStateMachine(unittest.TestCase):
    def test_happy_path_transitions(self) -> None:
        seq = _sequencer()
        seq.run()
        self.assertEqual(
            seq.history,
            [
                SequenceState.IDLE,
                SequenceState.PRE_FLIGHT,
                SequenceState.RAMP,
                SequenceState.MEASURE,
                SequenceState.COOLDOWN,
                SequenceState.CLEANLINESS,
                SequenceState.COMPLETE,
            ],
        )

    def test_abort_branch_stops_at_abort(self) -> None:
        seq = _sequencer()
        seq.run(on_tick=_inject_cavitation_at(5.0))
        self.assertEqual(seq.state, SequenceState.ABORT)
        # Reaches ABORT during the run, and never proceeds to cleanliness/complete.
        self.assertIn(SequenceState.ABORT, seq.history)
        self.assertNotIn(SequenceState.CLEANLINESS, seq.history)
        self.assertNotIn(SequenceState.COMPLETE, seq.history)

    def test_no_realtime_sleep_in_stepped_mode(self) -> None:
        seq = _sequencer()
        with mock.patch.object(sequencer_mod.time, "sleep",
                               side_effect=AssertionError("real-time sleep must not run")):
            record = seq.run()      # would raise if the sleep path were entered
        self.assertEqual(record.verdict.summary, "PASS")


# ---------------------------------------------------------------------------
# Assembled record — values, provenance, grading roles
# ---------------------------------------------------------------------------

class TestAssembledRecord(unittest.TestCase):
    def setUp(self) -> None:
        self.record = _sequencer().run()

    def test_returns_frozen_run_record(self) -> None:
        self.assertIsInstance(self.record, RunRecord)
        with self.assertRaises(Exception):
            self.record.id = "mutated"      # frozen dataclass

    def test_flow_results_are_graded_derived_with_formula(self) -> None:
        flow = [r for r in self.record.channel_results if r.channel == "flow"]
        self.assertTrue(flow)
        for r in flow:
            self.assertTrue(r.graded)
            self.assertEqual(r.provenance, Provenance.DERIVED)
            self.assertEqual(r.formula, "pump_flow_pc_destroke_v1")
            self.assertIsNotNone(r.pressure_bar)
            self.assertEqual(r.unit, "L/min")

    def test_torque_is_monitored_reference(self) -> None:
        torque = [r for r in self.record.channel_results if r.channel == "torque"]
        self.assertTrue(torque)
        for r in torque:
            self.assertFalse(r.graded)              # never graded pass/fail
            self.assertIsNone(r.passed)
            self.assertEqual(r.provenance, Provenance.DERIVED)
            self.assertEqual(r.formula, "absorption_torque_from_flow_v1")

    def test_one_flow_and_one_torque_per_gridpoint(self) -> None:
        flow = [r for r in self.record.channel_results if r.channel == "flow"]
        torque = [r for r in self.record.channel_results if r.channel == "torque"]
        grid = default_grid_pressures(BenchSimulator(sample_rate_hz=10.0).profile)
        self.assertEqual(len(flow), len(grid))
        self.assertEqual(len(torque), len(grid))

    def test_clean_run_grades_pass(self) -> None:
        self.assertEqual(self.record.verdict.summary, "PASS")
        self.assertIs(self.record.overall_passed, True)


# ---------------------------------------------------------------------------
# Cleanliness staging
# ---------------------------------------------------------------------------

class TestCleanlinessStaging(unittest.TestCase):
    def test_outlet_graded_others_recorded_only(self) -> None:
        incoming = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid",
                                      water_rh_pct=38.0)
        record = _sequencer(incoming=incoming).run()
        by_point = {c.reading.sample_point: c for c in record.cleanliness_results}
        # rig_supply (pre-flight) and incoming (as-found) are recorded-only context.
        self.assertIsNone(by_point["rig_supply"].verdict)
        self.assertIsNone(by_point["incoming_fluid"].verdict)
        # unit_outlet (as-left) is the graded result for the certificate.
        self.assertIsNotNone(by_point["unit_outlet"].verdict)

    def test_incoming_optional(self) -> None:
        record = _sequencer(incoming=None).run()
        points = {c.reading.sample_point for c in record.cleanliness_results}
        self.assertEqual(points, {"rig_supply", "unit_outlet"})


# ---------------------------------------------------------------------------
# The four honest verdict states
# ---------------------------------------------------------------------------

class TestHonestVerdicts(unittest.TestCase):
    def test_pass(self) -> None:
        self.assertEqual(_sequencer(intent="verification").run().verdict.summary, "PASS")

    def test_not_graded_for_validation_purpose(self) -> None:
        # Validation characterises; it does not grade — NOT GRADED regardless of values.
        self.assertEqual(_sequencer(intent="validation").run().verdict.summary, "NOT GRADED")

    def test_fail_when_flow_out_of_band(self) -> None:
        seq = _sequencer(intent="verification")
        seq.sources["flow"] = _MeasuredFlowSource(0.0)     # absurdly low → below every band
        record = seq.run()
        self.assertEqual(record.verdict.summary, "FAIL")

    def test_incomplete_on_abort(self) -> None:
        seq = _sequencer(intent="verification")
        record = seq.run(on_tick=_inject_cavitation_at(5.0))
        self.assertEqual(record.verdict.summary, "INCOMPLETE")
        self.assertIn("flow", record.verdict.note)
        self.assertIn("ABORTED", record.notes)
        self.assertTrue(seq.builder.aborted)


# ---------------------------------------------------------------------------
# The provenance / live-mode seam (not hard-coded)
# ---------------------------------------------------------------------------

class TestProvenanceSeam(unittest.TestCase):
    def test_measured_source_records_measured_no_formula(self) -> None:
        seq = _sequencer(intent="verification")
        # A within-band fixed reading so it PASSES — the point is the provenance tagging,
        # which must follow the source, not the sequencer.
        seq.sources["flow"] = _MeasuredFlowSource(150.0)
        record = seq.run()
        flow = [r for r in record.channel_results if r.channel == "flow"]
        self.assertTrue(flow)
        for r in flow:
            self.assertEqual(r.provenance, Provenance.MEASURED)
            self.assertEqual(r.formula, "")

    def test_simulated_source_reads_through_interface(self) -> None:
        sim = BenchSimulator(sample_rate_hz=10.0)
        src = SimulatedChannelSource("flow", sim.flow,
                                     formula=sim.profile.channels["flow"].formula)
        sim.flow.current_value = 123.4
        self.assertEqual(src.read(), 123.4)
        self.assertEqual(src.unit, "L/min")
        self.assertEqual(src.provenance, Provenance.DERIVED)


# ---------------------------------------------------------------------------
# RunRecordBuilder
# ---------------------------------------------------------------------------

class TestRunRecordBuilder(unittest.TestCase):
    def test_accumulates_then_freezes(self) -> None:
        b = _builder(TestPurpose(intent="verification", repair_stage="as_left"))
        b.start()
        b.add_channel_result(ChannelResult("flow", 150.0, "L/min", pressure_bar=200.0,
                                            passed=True, provenance=Provenance.DERIVED,
                                            formula="pump_flow_pc_destroke_v1"))
        record = b.finish()
        self.assertIsInstance(record, RunRecord)
        self.assertEqual(len(record.channel_results), 1)
        self.assertIsInstance(record.channel_results, tuple)   # frozen-friendly
        self.assertIsNotNone(record.started_at)
        self.assertIsNotNone(record.finished_at)

    def test_mark_aborted_records_reason(self) -> None:
        b = _builder(TestPurpose(intent="verification"))
        b.mark_aborted("fault detected on Flow")
        self.assertTrue(b.aborted)
        self.assertIn("ABORTED: fault detected on Flow", b.finish().notes)


# ---------------------------------------------------------------------------
# End-to-end smoke: run → record → certificate PDF
# ---------------------------------------------------------------------------

class TestEndToEndSmoke(unittest.TestCase):
    def test_run_to_certificate_pdf(self) -> None:
        from certificate import generate_certificate_pdf

        seq = _sequencer(intent="verification")
        record = seq.run()
        pdf = generate_certificate_pdf(record, seq.sim.profile, seq.sim.registry)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1000)


if __name__ == "__main__":
    unittest.main()
