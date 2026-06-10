"""
Unit tests for the first ``LiveChannelSource`` wiring (``sequencer.py``).

Run:  python3 -m unittest discover -s tests
(or:  python3 -m unittest tests.test_live_source)

This is the end-to-end proof of the ``ChannelSource`` substitution seam (forward-
requirements §1; decision-log "first live HAL driver"): a source that declares
``provenance='measured'`` flows through the **unchanged** sequencer and lands as
``measured`` in the frozen ``RunRecord``, while the still-simulated torque channel stays
``derived``.

Hardware-free — no hardware library is imported and the fake transport returns the
simulator's *own* flow value, so a live-wired run grades identically to a fully simulated
one and only the declared provenance differs. Every run is stepped (``realtime=False``);
channel RNGs are seeded for determinism. British English throughout; mirrors the style of
``tests/test_sequencer.py``.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bench_simulator import BenchSimulator  # noqa: E402
from run_record import Provenance, RunRecord, RunRecordBuilder, TestPurpose  # noqa: E402
from sequencer import (  # noqa: E402
    LiveChannelSource,
    SensorTransport,
    SimulatedChannelSource,
    TestSequencer,
    live_flow_sources,
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
        id="TEST-LIVE-0001", profile="pc200-8-hpv95", dut_serial="SN-TEST",
        operator="tester", po_number="PO-TEST", purpose=purpose, mode="training",
    )


class _MirrorFlowTransport:
    """A deterministic, hardware-free :class:`SensorTransport` test double. It returns the
    simulator's *own* current flow value, so a run wired through it grades identically to a
    fully simulated run — the only thing that changes is the declared provenance. Stands in
    for the real serial/USB/Modbus transport that is injected at the edge later."""

    def __init__(self, sim: BenchSimulator) -> None:
        self._sim = sim

    def read_value(self) -> float:
        return float(self._sim.flow.current_value)


def _live_sequencer(*, intent: str = "verification", seed: int = CLEAN_PASS_SEED) -> TestSequencer:
    sim = BenchSimulator(sample_rate_hz=10.0)
    _seed(sim, seed)
    purpose = TestPurpose(intent=intent, repair_stage="as_left", context="repair_overhaul")
    return TestSequencer(
        sim, _builder(purpose), live_flow_sources(sim, _MirrorFlowTransport(sim)),
        realtime=False, reference="PO-TEST",
    )


def _simulated_sequencer(*, intent: str = "verification", seed: int = CLEAN_PASS_SEED) -> TestSequencer:
    sim = BenchSimulator(sample_rate_hz=10.0)
    _seed(sim, seed)
    purpose = TestPurpose(intent=intent, repair_stage="as_left", context="repair_overhaul")
    return TestSequencer(
        sim, _builder(purpose), simulated_sources(sim),
        realtime=False, reference="PO-TEST",
    )


# ---------------------------------------------------------------------------
# The transport / source seam in isolation
# ---------------------------------------------------------------------------

class TestLiveSourceUnit(unittest.TestCase):
    def test_transport_double_satisfies_protocol(self) -> None:
        sim = BenchSimulator(sample_rate_hz=10.0)
        self.assertIsInstance(_MirrorFlowTransport(sim), SensorTransport)

    def test_live_source_declares_measured_no_formula(self) -> None:
        sim = BenchSimulator(sample_rate_hz=10.0)
        src = LiveChannelSource("flow", sim.flow.unit, _MirrorFlowTransport(sim))
        self.assertEqual(src.provenance, Provenance.MEASURED)
        self.assertEqual(src.formula, "")
        self.assertEqual(src.unit, "L/min")

    def test_live_source_reads_through_transport(self) -> None:
        sim = BenchSimulator(sample_rate_hz=10.0)
        src = LiveChannelSource("flow", sim.flow.unit, _MirrorFlowTransport(sim))
        sim.flow.current_value = 123.4
        self.assertEqual(src.read(), 123.4)

    def test_live_flow_sources_mixes_measured_and_derived(self) -> None:
        sim = BenchSimulator(sample_rate_hz=10.0)
        sources = live_flow_sources(sim, _MirrorFlowTransport(sim))
        self.assertIsInstance(sources["flow"], LiveChannelSource)
        self.assertEqual(sources["flow"].provenance, Provenance.MEASURED)
        # Torque is left simulated — the per-channel substitution proof.
        self.assertIsInstance(sources["torque"], SimulatedChannelSource)
        self.assertEqual(sources["torque"].provenance, Provenance.DERIVED)


# ---------------------------------------------------------------------------
# End-to-end: substitution alone flips flow's recorded provenance
# ---------------------------------------------------------------------------

class TestLiveRunRecord(unittest.TestCase):
    def setUp(self) -> None:
        self.record = _live_sequencer().run()

    def test_returns_frozen_run_record(self) -> None:
        self.assertIsInstance(self.record, RunRecord)

    def test_flow_results_are_measured_with_no_formula(self) -> None:
        flow = [r for r in self.record.channel_results if r.channel == "flow"]
        self.assertTrue(flow)
        for r in flow:
            self.assertTrue(r.graded)
            self.assertEqual(r.provenance, Provenance.MEASURED)
            self.assertEqual(r.formula, "")
            self.assertEqual(r.unit, "L/min")

    def test_torque_stays_derived(self) -> None:
        torque = [r for r in self.record.channel_results if r.channel == "torque"]
        self.assertTrue(torque)
        for r in torque:
            self.assertFalse(r.graded)
            self.assertEqual(r.provenance, Provenance.DERIVED)
            self.assertEqual(r.formula, "absorption_torque_from_flow_v1")


class TestSubstitutionIsTransparent(unittest.TestCase):
    """The proof that the sequencer was *not* special-cased for live mode: a live-wired run
    and a fully simulated run on the same seed grade identically — same verdict, same graded
    flow values — and *only* the declared provenance differs. Substitution alone flips it."""

    def test_identical_grading_only_provenance_differs(self) -> None:
        live = _live_sequencer().run()
        sim = _simulated_sequencer().run()

        self.assertEqual(live.verdict.summary, sim.verdict.summary)
        self.assertEqual(live.verdict.summary, "PASS")

        live_flow = [r for r in live.channel_results if r.channel == "flow"]
        sim_flow = [r for r in sim.channel_results if r.channel == "flow"]
        self.assertEqual(len(live_flow), len(sim_flow))
        self.assertTrue(live_flow)

        for lr, sr in zip(live_flow, sim_flow, strict=True):
            # Same value and verdict at the same gridpoint...
            self.assertEqual(lr.value, sr.value)
            self.assertEqual(lr.pressure_bar, sr.pressure_bar)
            self.assertEqual(lr.passed, sr.passed)
            # ...but the provenance follows the source, not the sequencer.
            self.assertEqual(sr.provenance, Provenance.DERIVED)
            self.assertEqual(lr.provenance, Provenance.MEASURED)
            self.assertEqual(lr.formula, "")


if __name__ == "__main__":
    unittest.main()
