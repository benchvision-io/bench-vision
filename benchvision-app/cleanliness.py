"""
cleanliness.py

BenchVision — fluid cleanliness (contamination) channel for the MP Filtri ICM.

This is the first real slice of the contamination thread sketched in
``docs/contamination-channel-sketch.md``. Cleanliness is a *different kind* of
channel from flow/torque/power: it is **acquired** from a physical instrument (not
**derived** by a formula), it arrives as a **discrete** result per commanded test
(not a continuous per-tick waveform), it is **vector-valued** (an ISO 4406 code
triple plus extra bands, raw counts, fluid temperature and water content), and it is
graded by a **code threshold** per size band (not a pressure-domain polyline).

Because of that it deliberately does NOT use the ``FormulaRegistry`` (which is for
derived physics) and does NOT subclass ``SensorChannel`` (which models a ticking
analogue gauge). It talks to an :class:`IcmDriver` — live mode binds the Modbus
implementation, training/demo mode binds the simulated one (HAL substitution, not a
code branch — consistent with the 2026-05-19 decisions).

Device facts grounded in MP Filtri ``200.061 MP ICM Modbus User Guide [EN].pdf``
(model ICM-WMKR).

British English throughout. Python 3.12+ (``from __future__ import annotations``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# Constants from the ICM Modbus manual
# ---------------------------------------------------------------------------

#: "No result" sentinel used by the ICM for any register (manual §3.4.1).
ICM_NULL: int = -32768  # 0x8000

#: Comms-check value expected in register 0 (manual §3.2).
ICM_PRODUCT_ID: int = 54237  # 0xD3DD

#: Modbus permanent node address — always answers here (manual Appendix A).
ICM_PERMANENT_NODE: int = 204


class IcmStatus:
    """Decoded TEST STATUS register 30 values (manual Table 3)."""
    NOT_READY = "not_ready"
    READY = "ready"
    TESTING = "testing"
    WAITING = "waiting"
    FAULT_OPTICAL = "fault_optical"
    FAULT_FLOW_LOW = "fault_flow_low"
    FAULT_FLOW_HIGH = "fault_flow_high"
    FAULT_LOGGING = "fault_logging"
    FAULT_WATER = "fault_water_sensor"


_STATUS_MAP: dict[int, str] = {
    0: IcmStatus.NOT_READY,
    1: IcmStatus.READY,
    2: IcmStatus.TESTING,
    3: IcmStatus.WAITING,
    128: IcmStatus.FAULT_OPTICAL,
    129: IcmStatus.FAULT_FLOW_LOW,
    130: IcmStatus.FAULT_FLOW_HIGH,
    131: IcmStatus.FAULT_LOGGING,
    132: IcmStatus.FAULT_WATER,
}


class IcmRegisters:
    """ICM Modbus register map (manual Appendix A). The single home for these numbers."""
    PRODUCT_ID = 0
    TEST_REFERENCE = (10, 17)     # 16 packed characters
    TEST_DURATION_S = 18
    TEST_FORMAT = 19              # 0 = ISO 4406:1999 (default)
    COMMAND = 21                 # write 1 = start/restart test
    STATUS = 30
    TEMPERATURE = 33             # value / 100, signed °C
    RH = 34                      # value / 100, signed %
    TEST_COMPLETION = 36         # 0..1000
    FLOW_ML_MIN = 37
    COUNTS = (40, 55)            # 8 x 32-bit (hi, lo) cumulative counts per 100 ml
    RESULT_CODES = (56, 63)      # 8 signed-int codes
    LIMIT_UPPER = (64, 71)
    LIMIT_LOWER = (72, 79)


# ---------------------------------------------------------------------------
# Pure decode helpers (no hardware — unit-testable in isolation)
# ---------------------------------------------------------------------------

def signed16(raw: int) -> int:
    """Interpret a 16-bit Modbus register as a signed two's-complement integer."""
    raw &= 0xFFFF
    return raw - 0x10000 if raw >= 0x8000 else raw


def u32_from_pair(hi: int, lo: int) -> int:
    """Combine two consecutive registers into a 32-bit unsigned integer (manual §3.9)."""
    return (hi & 0xFFFF) * 65536 + (lo & 0xFFFF)


def decode_status(raw: int) -> str:
    """Map a raw STATUS register value to an :class:`IcmStatus`; unknown → NOT_READY."""
    return _STATUS_MAP.get(raw, IcmStatus.NOT_READY)


def scaled_or_none(raw: int, factor: float) -> float | None:
    """Apply a ``/factor`` scale to a signed register, or ``None`` for the null sentinel."""
    s = signed16(raw)
    return None if s == ICM_NULL else s / factor


def parse_iso_code(text: str) -> tuple[int, int, int]:
    """Parse an ISO 4406 string like ``'18/16/13'`` into a 3-tuple of codes."""
    parts = [p.strip() for p in text.split("/")]
    if len(parts) != 3:
        raise ValueError(f"ISO 4406 code must have three parts, got {text!r}")
    return tuple(int(p) for p in parts)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# The reading
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CleanlinessReading:
    """
    One ICM result. Vector-valued so the certificate can show the graded code *and*
    its supporting evidence (raw counts, fluid temperature, water content). Read
    straight off the register map; nothing here is derived.
    """
    iso_code: tuple[int, int, int]                 # (>=4, >=6, >=14 µm) ISO 4406 codes
    extra_codes: tuple[int, ...] = ()              # >=21,25,38,50,70 µm — recorded, not graded
    counts_per_100ml: tuple[int, ...] = ()         # 8 cumulative 32-bit counts (regs 40-55)
    temperature_c: float | None = None             # reg 33 / 100
    water_rh_pct: float | None = None              # reg 34 / 100
    flow_ml_min: float | None = None               # reg 37 (test validity)
    status: str = IcmStatus.READY                  # decoded reg 30
    sample_point: str = "unit_outlet"              # rig_supply | unit_outlet | incoming_fluid
    reference: str = ""                            # PO / serial written to regs 10-17
    standard: str = "ISO4406:1999"

    _SAMPLE_POINTS = {"rig_supply", "unit_outlet", "incoming_fluid"}

    def __post_init__(self) -> None:
        if len(self.iso_code) != 3:
            raise ValueError(f"iso_code must be a 3-tuple, got {self.iso_code!r}")
        if self.sample_point not in self._SAMPLE_POINTS:
            raise ValueError(
                f"sample_point must be one of {sorted(self._SAMPLE_POINTS)}, "
                f"got {self.sample_point!r}"
            )

    @property
    def iso_string(self) -> str:
        """e.g. ``'18/16/13'`` — the human code for the certificate."""
        return "/".join(str(c) for c in self.iso_code)

    @property
    def is_valid(self) -> bool:
        """A reading with a null band or a non-ok status cannot be graded."""
        return self.status in (IcmStatus.READY, "ok") and ICM_NULL not in self.iso_code


# ---------------------------------------------------------------------------
# Acceptance — the third mode: cleanliness_code
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CleanlinessVerdict:
    """Result of grading a reading against a limit."""
    passed: bool | None                            # None = not gradeable
    per_band: tuple[bool, ...] = ()
    note: str = ""

    @property
    def summary(self) -> str:
        if self.passed is None:
            return f"NOT GRADED ({self.note})"
        return "PASS" if self.passed else "FAIL"


@dataclass(frozen=True)
class CleanlinessLimit:
    """
    Per-band ISO 4406 code ceiling. Lower code == cleaner, so a reading PASSES when
    every graded band's measured code is **<=** its target. This is the third
    acceptance mode (alongside the polyline / formula_tolerance bands used for the
    pressure-domain channels); it has no pressure axis and no interpolation.
    """
    target: tuple[int, int, int]                   # (>=4, >=6, >=14) max allowable codes
    standard: str = "ISO4406:1999"

    def __post_init__(self) -> None:
        if len(self.target) != 3:
            raise ValueError(f"target must be a 3-tuple of ISO codes, got {self.target!r}")

    @classmethod
    def from_toml_section(cls, section: Mapping[str, object]) -> "CleanlinessLimit":
        """
        Build from an ``[acceptance.cleanliness]`` table, e.g.::

            [acceptance.cleanliness]
            mode     = "cleanliness_code"
            standard = "ISO4406:1999"
            target   = "18/16/13"
        """
        mode = str(section.get("mode", "cleanliness_code"))
        if mode != "cleanliness_code":
            raise ValueError(f"expected mode 'cleanliness_code', got {mode!r}")
        raw_target = section["target"]
        target = (
            parse_iso_code(raw_target) if isinstance(raw_target, str)
            else tuple(int(x) for x in raw_target)  # also accept a [18,16,13] list
        )
        return cls(target=target, standard=str(section.get("standard", "ISO4406:1999")))

    def grade(self, reading: CleanlinessReading) -> CleanlinessVerdict:
        if not reading.is_valid:
            return CleanlinessVerdict(passed=None, note=f"invalid reading ({reading.status})")
        per_band = tuple(m <= t for m, t in zip(reading.iso_code, self.target))
        return CleanlinessVerdict(passed=all(per_band), per_band=per_band)


# ---------------------------------------------------------------------------
# HAL driver seam
# ---------------------------------------------------------------------------

@runtime_checkable
class IcmDriver(Protocol):
    """
    The seam between BenchVision and the ICM. Live mode binds :class:`IcmModbusDriver`;
    training/demo mode binds :class:`SimulatedIcmDriver`. Same interface, so nothing
    above this line knows or cares which is wired in.
    """
    def start_test(self, duration_s: int, reference: str = "") -> None: ...
    def status(self) -> str: ...
    def completion(self) -> float: ...              # 0.0 .. 1.0
    def read_result(self, sample_point: str) -> CleanlinessReading: ...


class IcmModbusDriver:
    """
    Live driver. Wraps a Modbus RTU client connected to the ICM (default node 204).

    The ``client`` is expected to expose a minimal adapter:
        * ``read_register(addr, node) -> int``
        * ``read_registers(start, end, node) -> list[int]``   (inclusive range)
        * ``write_register(addr, value, node) -> None``
    Wiring a concrete Modbus library (e.g. pymodbus) to that adapter is out of scope
    for this slice — but every value it decodes goes through the pure helpers above,
    which ARE unit-tested.
    """

    def __init__(self, client: object, node: int = ICM_PERMANENT_NODE):
        self._c = client
        self._node = node

    def _read_reference(self) -> str:
        return ""  # decode regs 10-17 packed chars — elided for this slice

    def _write_reference(self, reference: str) -> None:
        pass  # pack reference into regs 10-17 — elided for this slice

    def start_test(self, duration_s: int, reference: str = "") -> None:
        self._c.write_register(IcmRegisters.TEST_DURATION_S, int(duration_s), self._node)  # type: ignore[attr-defined]
        if reference:
            self._write_reference(reference)
        self._c.write_register(IcmRegisters.COMMAND, 1, self._node)  # type: ignore[attr-defined]

    def status(self) -> str:
        return decode_status(self._c.read_register(IcmRegisters.STATUS, self._node))  # type: ignore[attr-defined]

    def completion(self) -> float:
        raw = self._c.read_register(IcmRegisters.TEST_COMPLETION, self._node)  # type: ignore[attr-defined]
        return min(1.0, max(0.0, raw / 1000.0))

    def read_result(self, sample_point: str) -> CleanlinessReading:
        codes = self._c.read_registers(*IcmRegisters.RESULT_CODES, self._node)  # type: ignore[attr-defined]
        raw = self._c.read_registers(*IcmRegisters.COUNTS, self._node)          # type: ignore[attr-defined]
        temp = self._c.read_register(IcmRegisters.TEMPERATURE, self._node)      # type: ignore[attr-defined]
        rh = self._c.read_register(IcmRegisters.RH, self._node)                 # type: ignore[attr-defined]
        flow = self._c.read_register(IcmRegisters.FLOW_ML_MIN, self._node)      # type: ignore[attr-defined]
        codes = [signed16(c) for c in codes]
        return CleanlinessReading(
            iso_code=(codes[0], codes[1], codes[2]),
            extra_codes=tuple(codes[3:]),
            counts_per_100ml=tuple(u32_from_pair(raw[i], raw[i + 1]) for i in range(0, 16, 2)),
            temperature_c=scaled_or_none(temp, 100.0),
            water_rh_pct=scaled_or_none(rh, 100.0),
            flow_ml_min=float(flow),
            status=self.status(),
            sample_point=sample_point,
            reference=self._read_reference(),
        )


class SimulatedIcmDriver:
    """
    Training/demo driver — scripted, hardware-free. Bound in place of
    :class:`IcmModbusDriver` in training mode. ``testing_polls`` lets a caller exercise
    the in-progress loop deterministically (0 = completes immediately).
    """

    def __init__(self, scripted: CleanlinessReading, testing_polls: int = 0):
        self._scripted = scripted
        self._testing_polls = max(0, testing_polls)
        self._polls = 0
        self._started = False

    def start_test(self, duration_s: int, reference: str = "") -> None:
        self._started = True
        self._polls = 0

    def status(self) -> str:
        if not self._started:
            return IcmStatus.NOT_READY
        if self._polls < self._testing_polls:
            self._polls += 1
            return IcmStatus.TESTING
        return IcmStatus.READY

    def completion(self) -> float:
        if self._testing_polls == 0:
            return 1.0
        return min(1.0, self._polls / self._testing_polls)

    def read_result(self, sample_point: str) -> CleanlinessReading:
        return replace(self._scripted, sample_point=sample_point)


# ---------------------------------------------------------------------------
# The channel — a commanded discrete test
# ---------------------------------------------------------------------------

@dataclass
class CleanlinessChannel:
    """
    An ICM contamination test: a commanded discrete measurement, NOT a per-tick
    analogue channel (hence it does not subclass ``SensorChannel``). It commands one
    test, polls to completion, reads the result, and optionally grades it against the
    profile's ``cleanliness_code`` limit.
    """
    driver: IcmDriver
    limit: CleanlinessLimit | None = None
    duration_s: int = 120
    name: str = "Cleanliness"
    unit: str = "ISO 4406"

    def run(self, sample_point: str = "unit_outlet", reference: str = "") -> CleanlinessReading:
        """
        Command one test and poll to completion. The real live sequencer yields to the
        UI between polls (and times out on FAULT/WAITING); this synchronous form is the
        readable core. Returns the reading regardless of pass/fail — grading is separate.
        """
        self.driver.start_test(self.duration_s, reference)
        while self.driver.status() == IcmStatus.TESTING:
            pass  # sequencer: await completion()/status(); honour fault + timeout here
        return self.driver.read_result(sample_point)

    def grade(self, reading: CleanlinessReading) -> CleanlinessVerdict | None:
        """Grade against the profile limit, or ``None`` if this run is recorded-only."""
        return self.limit.grade(reading) if self.limit is not None else None


__all__ = [
    "ICM_NULL",
    "ICM_PRODUCT_ID",
    "ICM_PERMANENT_NODE",
    "IcmStatus",
    "IcmRegisters",
    "signed16",
    "u32_from_pair",
    "decode_status",
    "scaled_or_none",
    "parse_iso_code",
    "CleanlinessReading",
    "CleanlinessVerdict",
    "CleanlinessLimit",
    "IcmDriver",
    "IcmModbusDriver",
    "SimulatedIcmDriver",
    "CleanlinessChannel",
]


# ---------------------------------------------------------------------------
# Tiny runnable demo (training mode, no hardware): python3 cleanliness.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    limit = CleanlinessLimit.from_toml_section(
        {"mode": "cleanliness_code", "standard": "ISO4406:1999", "target": "18/16/13"}
    )

    incoming = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid",
                                  temperature_c=41.0, water_rh_pct=38.0, reference="PO-12345")
    outgoing = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet",
                                  temperature_c=44.0, water_rh_pct=12.0, reference="PO-12345")

    print("ICM cleanliness demo (target", limit.target, ")")
    for label, reading in (("AS-FOUND  (incoming)", incoming), ("AS-LEFT   (unit)", outgoing)):
        ch = CleanlinessChannel(driver=SimulatedIcmDriver(reading), limit=limit)
        result = ch.run(sample_point=reading.sample_point, reference=reading.reference)
        verdict = ch.grade(result)
        print(f"  {label}: {result.iso_string:<10} -> {verdict.summary:<5} "
              f"(per-band {verdict.per_band}, water {result.water_rh_pct}% RH)")
