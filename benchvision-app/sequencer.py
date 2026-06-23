"""
sequencer.py

BenchVision — the test sequencer: the connective tissue that drives one end-to-end run.
A test sequence is a **state machine** (curriculum Day 17) that orchestrates the existing
``BenchSimulator`` channels through a cycle, accumulates results in a ``RunRecordBuilder``
as it goes, and freezes a ``RunRecord`` at the end — from which the honest four-state
verdict and the certificate fall out.

  IDLE → PRE_FLIGHT → RAMP → MEASURE → COOLDOWN → CLEANLINESS → COMPLETE
                 └──────────── (any active state, on fault) ──────────→ ABORT

Design commitments (each load-bearing, each traceable to a decision):

  * **Driven by the test DEFINITION, not the sim's physics (the sequence-intent seam,
    decision-log 2026-06-18 / 2026-06-22).** Progression is decided by an explicit
    :class:`~test_definition.TestDefinition` — the ordered operating points and a per-point
    **settle condition in observable channel terms** — never by reading the simulator's
    ``pressure.cycle_phase``. The sequencer advances to each declared point, waits until the
    pure :func:`~test_definition.is_settled` test says the point has *measurably settled*,
    captures, and moves on. A live bench has no ``cycle_phase`` to borrow; the same settle
    test reads a real transducer identically. It still orchestrates ``start_test`` / ``tick``
    / the discrete cleanliness steps — it does not re-implement the physics.
  * **The provenance / live-mode seam (forward-requirements §1).** Values are read through
    a :class:`ChannelSource`, which *declares* its own provenance. The simulator's
    formula-driven channels are ``derived`` (it has no sensors) and carry their formula id;
    a future ``LiveChannelSource`` would declare ``measured`` with no formula. The sequencer
    records *whatever the source declares* — it never hard-codes ``derived``. Swap the
    source, not the sequencer, to go live. Grading *policy* (flow-vs-band, torque-as-
    reference) stays here, in the sequencer, where it belongs.
  * **Flow is the pass/fail truth; torque is a monitored reference** (decision-log
    2026-06-01). Each captured flow point is graded against the profile's flow band; torque
    is recorded ``graded=False``.
  * **Settle-gated, smoothed grading capture.** A point is captured only once it has
    measurably *settled* (target pressure reached and the settle channel stable for a dwell —
    ``is_settled``), never on the way up the ramp. The DAQ adds Gaussian noise, so each graded
    point is also the *median* over the smoothing window so a single noisy sample cannot push
    a good pump outside a tight band. (The full-resolution waveform for the plots is captured
    separately, un-smoothed, by the caller's ``on_tick`` hook.)
  * **Honest abort.** A fault aborts the run and seals an honest INCOMPLETE ``RunRecord``: the
    captured points are kept as evidence and one graded-but-unevaluated flow result is
    appended so the sealed record reads **INCOMPLETE** (never a silent pass). An audited
    abort is a real outcome.
  * **Cleanliness staging.** Only the as-left ``unit_outlet`` reading is graded toward the
    verdict; the pre-flight ``rig_supply`` and the as-found ``incoming_fluid`` are recorded
    as context/evidence (``verdict=None``), matching the certificate's as-found/as-left
    logic.

**Stepped vs real-time.** One loop, identical logic; a single ``realtime`` flag gates one
``time.sleep(dt)`` per tick. Stepped (the default) runs instantly for tests and quick
certificate generation; real-time paces the on-screen recording. Tests construct with
``realtime=False`` and so never enter the sleep path.

British English throughout. Python 3.12+ (``from __future__ import annotations``).
"""

from __future__ import annotations

import logging
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from statistics import median
from typing import Protocol, runtime_checkable

from bench_simulator import BenchSimulator, ChannelState
from cleanliness import CleanlinessReading
from pump_profile import PumpProfile
from run_record import (
    ChannelResult,
    CleanlinessResult,
    Provenance,
    RunRecord,
    RunRecordBuilder,
    utc_now_iso,
)
from test_definition import (
    TestDefinition,
    derive_gridpoints,
    is_settled,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# The state machine's states
# ---------------------------------------------------------------------------

class SequenceState(Enum):
    """The states of one test run (curriculum Day 17). ``ABORT`` is reachable from any
    active state on a fault; ``COMPLETE`` is the clean terminal."""
    IDLE = "idle"
    PRE_FLIGHT = "pre_flight"
    RAMP = "ramp"
    MEASURE = "measure"          # the HOLD/MEASURE operating-point window
    COOLDOWN = "cooldown"
    CLEANLINESS = "cleanliness"
    COMPLETE = "complete"
    ABORT = "abort"


# ---------------------------------------------------------------------------
# The reading-source seam (the live-mode inversion)
# ---------------------------------------------------------------------------

@runtime_checkable
class ChannelSource(Protocol):
    """A source of one channel's value, read *through the channel interface*, that
    declares the **provenance** of that value. This is the substitution seam for the
    live-mode inversion: the sequencer records whatever the source declares and so never
    assumes a value was derived. A future ``LiveChannelSource`` reads a real sensor and
    declares ``measured`` with no formula; the sequencer is unchanged."""
    channel: str
    unit: str
    provenance: str
    formula: str

    def read(self) -> float: ...


@dataclass
class SimulatedChannelSource:
    """Wraps one simulator ``SensorChannel``. Training/demo values are formula-**derived**
    (the simulator has no sensors), so this source declares ``provenance='derived'`` and
    carries the channel's formula id (taken from the profile, not reached out of a private
    field). It answers only *what value, and where from* — the grading policy lives in the
    sequencer, never here."""
    channel: str
    sensor: object                       # a SensorChannel: reads .current_value / .unit
    formula: str = ""
    provenance: str = Provenance.DERIVED

    @property
    def unit(self) -> str:
        return self.sensor.unit

    def read(self) -> float:
        return float(self.sensor.current_value)


def simulated_sources(sim: BenchSimulator) -> dict[str, ChannelSource]:
    """Build the derived-channel sources for a simulator run. Flow and torque are the two
    channels recorded as results; the formula ids come from the profile (public), so the
    seam never reaches into the channel's private ``_formula_ref``."""
    return {
        "flow": SimulatedChannelSource(
            "flow", sim.flow, formula=sim.profile.channels["flow"].formula
        ),
        "torque": SimulatedChannelSource(
            "torque", sim.torque, formula=sim.profile.channels["torque"].formula
        ),
    }


def default_grid_pressures(profile: PumpProfile) -> tuple[float, ...]:
    """The pressures to grade at: the flow band's own gridpoint pressures (excluding the
    no-load 0-bar point). Grading at the same pressures the band is defined at is chart-
    faithful and bounded, and avoids the spurious near-edge fails a fixed time cadence
    invites.

    Routed through the **test definition** when the profile carries one, so the points come
    from a single source of truth (the definition itself derives them from the flow band).
    Falls back to deriving straight from the band for profiles without a ``[test]`` section."""
    if profile.test is not None:
        return profile.test.point_pressures
    return derive_gridpoints(profile.acceptance["flow"])


# ---------------------------------------------------------------------------
# The sequencer
# ---------------------------------------------------------------------------

@dataclass
class TestSequencer:
    """Drives one run of the ``BenchSimulator`` through the state machine, accumulating
    results into ``builder`` and returning the frozen ``RunRecord`` at the end."""

    sim: BenchSimulator
    builder: RunRecordBuilder
    sources: dict[str, ChannelSource]
    grid_pressures: tuple[float, ...] = ()
    test_def: TestDefinition | None = None   # the sequence intent; from the profile if None
    realtime: bool = False
    smoothing_window: int = 7            # ticks per graded-point median (~0.7 s at 10 Hz)
    incoming_sample: CleanlinessReading | None = None   # as-found evidence (optional)
    reference: str = ""                  # PO / serial written alongside cleanliness reads
    cooldown_done_bar: float = 5.0       # observed pressure below this = unloaded → run ends

    state: SequenceState = field(default=SequenceState.IDLE, init=False)
    history: list[SequenceState] = field(default_factory=list, init=False)
    _captures: list[dict[str, float]] = field(default_factory=list, init=False)
    _captured_targets: set[float] = field(default_factory=set, init=False)
    _window: deque = field(default=None, init=False, repr=False)   # type: ignore[assignment]

    def __post_init__(self) -> None:
        # Resolve the sequence intent: the profile's [test] definition, else a default
        # synthesised from the flow band. The sequencer reads the run from THIS, not from the
        # simulator's cycle_phase — the seam this whole change closes.
        if self.test_def is None:
            self.test_def = (
                self.sim.profile.test
                or TestDefinition.default_for_band(self.sim.profile.acceptance["flow"])
            )
        if not self.grid_pressures:
            self.grid_pressures = self.test_def.point_pressures
        if self.smoothing_window < 1:
            raise ValueError("smoothing_window must be >= 1")
        # The settle test reads the last ``for_ticks`` of the smoothing window, so the window
        # must be at least as long as the longest dwell any point asks for.
        max_dwell = max((p.settle.for_ticks for p in self.test_def.points), default=1)
        if max_dwell > self.smoothing_window:
            raise ValueError(
                f"smoothing_window ({self.smoothing_window}) must be >= the longest settle "
                f"dwell ({max_dwell} ticks)"
            )
        self._window = deque(maxlen=self.smoothing_window)
        self.history.append(self.state)   # IDLE is the initial state

    # -- transitions -----------------------------------------------------------

    def _transition(self, new_state: SequenceState) -> None:
        if new_state is self.state:
            return
        logger.info("%s -> %s", self.state.value, new_state.value)
        self.state = new_state
        self.history.append(new_state)

    # -- the run ---------------------------------------------------------------

    def run(self, on_tick: Callable[[BenchSimulator], None] | None = None) -> RunRecord:
        """Execute the sequence end-to-end and return the frozen ``RunRecord``.

        ``on_tick`` (if given) is called once per tick after the simulator advances and
        before the fault check — the demo uses it to collect the un-smoothed full-rate
        waveform for the plots, and a test/demo may use it to inject a fault to exercise
        the ABORT branch.
        """
        self.builder.start(utc_now_iso())
        self._transition(SequenceState.PRE_FLIGHT)
        self._preflight()

        # Drive the run from the test DEFINITION, not the simulator's physics. Configure the
        # sim to park at each declared operating point (a genuine settled hold at each); the
        # progression below is decided by the measured-settle test, never by ``cycle_phase``.
        self._configure_sim_sequence()
        self.sim.start_test()
        self._transition(SequenceState.RAMP)

        cap = self._tick_cap()

        while True:
            self.sim.tick()
            if self.realtime:
                time.sleep(self.sim.dt)
            if on_tick is not None:
                on_tick(self.sim)

            if self._fault_present():
                self._abort(
                    "fault detected on " + ", ".join(self._faulted_channels())
                )
                return self.builder.finish(utc_now_iso())

            self._observe()          # push this sample onto the smoothing window
            self._maybe_capture()    # settle-gated capture; RAMP → MEASURE on the first

            # All declared points captured → cooldown, then end the loop once the bench has
            # UNLOADED. Termination is an observable condition (pressure near zero), not the
            # sim's cycle_phase — a real bench has no phase string to read.
            if self._all_points_captured():
                if self.state in (SequenceState.RAMP, SequenceState.MEASURE):
                    self._transition(SequenceState.COOLDOWN)
                if self.sim.pressure.current_value <= self.cooldown_done_bar:
                    break

            if self.sim.sample_count >= cap:
                logger.warning("tick cap %d reached; ending loop", cap)
                break

        # --- clean finalisation ---------------------------------------------
        self._record_channel_results()
        self._transition(SequenceState.CLEANLINESS)
        self._run_cleanliness()
        self._transition(SequenceState.COMPLETE)
        return self.builder.finish(utc_now_iso())

    # -- phases ----------------------------------------------------------------

    def _preflight(self) -> None:
        """Rig-supply cleanliness is read as advisory **context** (recorded-only), not a
        hard gate yet — treating rig-supply-as-gate as a documented assumption until Devon
        says otherwise (not a re-ask). Stored ``verdict=None``."""
        res = self.sim.run_cleanliness_test("rig_supply", self.reference)
        self.builder.add_cleanliness_result(CleanlinessResult(res["reading"], verdict=None))

    def _configure_sim_sequence(self) -> None:
        """Tell the simulator to park at each declared operating point in turn (a genuine
        flat hold at each), so a measured-settle capture is honest at every point — not just
        the top one a single ramp would hold at. This is the sim *source* realising the test
        definition; it is the only sim-specific step. A live source needs no equivalent — the
        operator brings the bench to each point — and the rest of the loop is identical."""
        press = getattr(self.sim, "pressure", None)
        if press is not None and hasattr(press, "set_hold_sequence"):
            press.set_hold_sequence(self.grid_pressures, hold_time=self.test_def.hold_seconds)

    def _observe(self) -> None:
        """Push this tick's (pressure, flow, torque) onto the rolling smoothing window. Flow
        and torque are read *through the source* (provenance seam); pressure is the swept
        independent variable, read directly."""
        self._window.append({
            "pressure": self.sim.pressure.current_value,
            "flow": self.sources["flow"].read(),
            "torque": self.sources["torque"].read(),
        })

    def _maybe_capture(self) -> None:
        """Capture an operating point ONLY when it has measurably **settled** — the point's
        target pressure reached and the settle channel stable for the dwell (``is_settled``,
        pure channel terms). This is the gate that retires the old rising-ramp capture: a
        point is recorded as the median of the smoothing window, gated on *settled*, never on
        merely crossing the target. ``RAMP → MEASURE`` on the first capture."""
        if len(self._window) < self.smoothing_window:
            return
        pressure_window = [s["pressure"] for s in self._window]
        for target in self.grid_pressures:
            if target in self._captured_targets:
                continue
            cond = self.test_def.settle_at(target)
            channel_window = (
                [s[cond.channel] for s in self._window]
                if cond.channel in self._window[0]
                else pressure_window
            )
            if not is_settled(
                cond,
                target_bar=target,
                pressure_window=pressure_window,
                channel_window=channel_window,
                dt=self.sim.dt,
            ):
                continue
            self._captures.append({
                "pressure": median(s["pressure"] for s in self._window),
                "flow": median(s["flow"] for s in self._window),
                "torque": median(s["torque"] for s in self._window),
            })
            self._captured_targets.add(target)
            if self.state is SequenceState.RAMP:
                self._transition(SequenceState.MEASURE)

    def _all_points_captured(self) -> bool:
        return len(self._captured_targets) >= len(self.grid_pressures)

    def _record_channel_results(self) -> None:
        """Turn the captured operating points into graded flow + monitored-reference torque
        ``ChannelResult``s. Provenance/formula come from the *source*, not hard-coded."""
        flow_src = self.sources["flow"]
        tq_src = self.sources["torque"]
        band = self.sim.profile.acceptance["flow"]
        for c in self._captures:
            p, fv, tv = c["pressure"], c["flow"], c["torque"]
            lower, upper = band.limits_at(p)
            self.builder.add_channel_result(ChannelResult(
                channel="flow", value=fv, unit=flow_src.unit, pressure_bar=p,
                passed=(lower <= fv <= upper), graded=True,
                provenance=flow_src.provenance, formula=flow_src.formula,
            ))
            self.builder.add_channel_result(ChannelResult(
                channel="torque", value=tv, unit=tq_src.unit, pressure_bar=p,
                passed=None, graded=False,           # monitored reference, never a verdict
                provenance=tq_src.provenance, formula=tq_src.formula,
            ))

    def _run_cleanliness(self) -> None:
        """The discrete cleanliness steps. Only the as-left ``unit_outlet`` reading grades
        toward the verdict; the as-found ``incoming_fluid`` is recorded-only evidence."""
        if self.incoming_sample is not None:
            res = self.sim.run_cleanliness_test(
                "incoming_fluid", self.reference, scripted=self.incoming_sample
            )
            self.builder.add_cleanliness_result(CleanlinessResult(res["reading"], verdict=None))
        reading = self.sim.cleanliness.run(sample_point="unit_outlet", reference=self.reference)
        verdict = self.sim.cleanliness.grade(reading)   # None if no confirmed target
        self.builder.add_cleanliness_result(CleanlinessResult(reading, verdict))

    def _abort(self, reason: str) -> None:
        """Abort on a fault and seal an honest INCOMPLETE record (a record outcome — not a
        physical-safety action; the software does not bring the bench to a safe state). The
        captured points so far are real evidence and are kept; one graded-but-unevaluated flow
        result is then appended so the run reads INCOMPLETE, never a silent pass."""
        self._transition(SequenceState.ABORT)
        self.builder.mark_aborted(reason)
        self._record_channel_results()
        flow_src = self.sources["flow"]
        self.builder.add_channel_result(ChannelResult(
            channel="flow", value=flow_src.read(), unit=flow_src.unit,
            pressure_bar=self.sim.pressure.current_value,
            passed=None, graded=True,                # meant to grade, could not evaluate
            provenance=flow_src.provenance, formula=flow_src.formula,
        ))

    # -- small helpers ---------------------------------------------------------

    def _fault_present(self) -> bool:
        return any(ch.state == ChannelState.FAULT for ch in self.sim.channels)

    def _faulted_channels(self) -> list[str]:
        return [ch.name for ch in self.sim.channels if ch.state == ChannelState.FAULT]

    def _tick_cap(self) -> int:
        """A generous upper bound on ticks, derived from the pressure cycle's planned
        duration (staircase or legacy), so the loop can never spin forever if settle never
        fires or the bench never unloads."""
        secs = self.sim.pressure.planned_duration() + 20.0
        return int(secs * self.sim.sample_rate_hz)


__all__ = [
    "SequenceState",
    "ChannelSource",
    "SimulatedChannelSource",
    "simulated_sources",
    "default_grid_pressures",
    "TestSequencer",
]
