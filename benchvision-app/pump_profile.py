"""
pump_profile.py

BenchVision — per-test "pump profile" configuration loader.

A pump profile is the parameterised half of the formula engine (spec §8A). It
carries every pump-specific quantity that used to be baked into channel code —
displacement, rated RPM, pressure sweep, acceptance band, shaft diameter, units —
plus a per-derived-channel selection of which named formula computes it. Adding a
new pump is then a sibling ``.toml`` file, not a code change.

The deliberate separation of *theoretical displacement* from *machine-adjusted
flow* (rather than a single "displacement" field) is what prevents a repeat of the
95/112 confusion of 2026-05-27.

British English throughout. Python 3.12+ (``tomllib`` is stdlib from 3.11; a
``tomli`` fallback is provided so the loader also runs on older interpreters used
for ad-hoc validation).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - validation on older interpreters
    import tomli as tomllib  # type: ignore[no-redef]


# ---------------------------------------------------------------------------
# Sub-structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Displacement:
    """
    Pump displacement semantics (Devon, 2026-05-27): theoretical → machine-adjusted
    flow → measured form a chain, NOT a single number. ``mode`` records which figure
    the flow formula's no-load value derives from, and is surfaced for Devon to
    confirm on his next pass.
    """
    theoretical_cc_per_rev: float
    machine_adjusted_flow_cc_per_rev: float
    measured_cc_per_rev: float | None
    mode: str                       # "theoretical" | "machine_adjusted"
    n_sections: int
    mech_efficiency: float

    def __post_init__(self) -> None:
        if self.mode not in {"theoretical", "machine_adjusted"}:
            raise ValueError(
                f"displacement.mode must be 'theoretical' or 'machine_adjusted', "
                f"got {self.mode!r}"
            )

    @property
    def active_cc_per_rev(self) -> float:
        """The displacement figure selected by ``mode``."""
        return (
            self.theoretical_cc_per_rev
            if self.mode == "theoretical"
            else self.machine_adjusted_flow_cc_per_rev
        )


@dataclass(frozen=True)
class PressureSweep:
    unit: str
    min: float
    max: float
    direction: str = "rising"       # chart applies values on the pressure-rising sweep


@dataclass(frozen=True)
class Acquisition:
    sample_rate_hz: float           # acquisition fidelity
    operator_log_hz: float          # operator-facing decimation (Devon's Excel cadence)


@dataclass(frozen=True)
class Shaft:
    diameter_mm: float              # default; operator may override at test setup
    operator_prompt: bool           # v4: ask the operator the shaft diameter


@dataclass(frozen=True)
class ChannelFormula:
    """A derived channel's chosen formula plus its profile-supplied inputs."""
    formula: str                    # registry reference, e.g. "pump_flow_pc_destroke_v1"
    output_unit: str
    inputs: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class AcceptanceBand:
    """
    Pass/fail envelope for a channel. Two representations are supported:

      * ``polyline`` — explicit (pressure, upper, lower) points lifted from the
        manufacturer chart. Used for PC200-8: the printed envelope is what the
        certificate is judged against, so the digitised points ARE the truth.
      * ``formula_tolerance`` — a nominal formula plus a ± tolerance, for pumps
        whose spec is given as "nominal ± x".
    """
    mode: str                                   # "polyline" | "formula_tolerance"
    points: tuple[tuple[float, float, float], ...] = ()   # (pressure, upper, lower)
    tolerance: float | None = None

    def limits_at(self, pressure: float) -> tuple[float, float]:
        """Linear-interpolated (lower, upper) limits at a pressure (polyline mode)."""
        if self.mode != "polyline" or not self.points:
            raise ValueError("limits_at requires polyline mode with points")
        pts = self.points
        if pressure <= pts[0][0]:
            return pts[0][2], pts[0][1]
        if pressure >= pts[-1][0]:
            return pts[-1][2], pts[-1][1]
        for (p0, u0, l0), (p1, u1, l1) in zip(pts, pts[1:]):
            if p0 <= pressure <= p1:
                f = (pressure - p0) / (p1 - p0)
                return l0 + f * (l1 - l0), u0 + f * (u1 - u0)
        return pts[-1][2], pts[-1][1]


@dataclass(frozen=True)
class EfficiencyCurve:
    """
    Total mechanical efficiency as a function of discharge pressure.

    This is an *empirical* per-pump map, NOT a derived physical constant. It is
    fitted (2026-06-01) so that the curated ``absorption_torque_from_flow`` formula,
    fed the pump's live flow, reproduces the manufacturer chart's nominal absorption-
    torque curve. It absorbs every mechanical loss the ideal ``P·Vg/2π`` model omits —
    chiefly Coulomb + viscous friction, which dominate at light load (so η is low at
    low pressure), peak near the PC knee, then take a growing share as the pump
    destrokes (so η falls again across the constant-power region).

    A single scalar ``mech_efficiency`` (in [displacement]) is the fallback when no
    curve is supplied; a curve supersedes it for the pump that has one. Because the
    efficiency is resolved at the operating point and passed to the formula as an
    ordinary input, the formula itself stays pure and version-stable — only the input
    supply changes, which is *not* a formula-function change (so no new version tag).
    """
    points: tuple[tuple[float, float], ...] = ()   # (pressure_bar, mech_efficiency)
    fallback: float = 0.90

    def eta_at(self, pressure: float) -> float:
        """Linear-interpolated mechanical efficiency at a pressure."""
        pts = self.points
        if not pts:
            return self.fallback
        if pressure <= pts[0][0]:
            return pts[0][1]
        if pressure >= pts[-1][0]:
            return pts[-1][1]
        for (p0, e0), (p1, e1) in zip(pts, pts[1:]):
            if p0 <= pressure <= p1:
                f = (pressure - p0) / (p1 - p0)
                return e0 + f * (e1 - e0)
        return pts[-1][1]


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PumpProfile:
    """A fully-parsed pump profile. Construct via ``PumpProfile.from_toml``."""

    schema_version: str
    identity: Mapping[str, Any]
    displacement: Displacement
    rated_rpm: float
    pressure_sweep: PressureSweep
    acquisition: Acquisition
    shaft: Shaft
    channels: Mapping[str, ChannelFormula]
    acceptance: Mapping[str, AcceptanceBand]
    efficiency: EfficiencyCurve | None = None
    source_path: Path | None = None

    # -- loading ------------------------------------------------------------

    @classmethod
    def from_toml(cls, path: str | Path) -> "PumpProfile":
        path = Path(path)
        with path.open("rb") as fh:
            raw = tomllib.load(fh)
        return cls.from_dict(raw, source_path=path)

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any], *, source_path: Path | None = None) -> "PumpProfile":
        disp_raw = raw["displacement"]
        displacement = Displacement(
            theoretical_cc_per_rev=float(disp_raw["theoretical_cc_per_rev"]),
            machine_adjusted_flow_cc_per_rev=float(disp_raw["machine_adjusted_flow_cc_per_rev"]),
            measured_cc_per_rev=(
                float(disp_raw["measured_cc_per_rev"])
                if "measured_cc_per_rev" in disp_raw else None
            ),
            mode=str(disp_raw["mode"]),
            n_sections=int(disp_raw["n_sections"]),
            mech_efficiency=float(disp_raw["mech_efficiency"]),
        )

        ps = raw["pressure_sweep"]
        pressure_sweep = PressureSweep(
            unit=str(ps["unit"]), min=float(ps["min"]), max=float(ps["max"]),
            direction=str(ps.get("direction", "rising")),
        )

        acq = raw["acquisition"]
        acquisition = Acquisition(
            sample_rate_hz=float(acq["sample_rate_hz"]),
            operator_log_hz=float(acq["operator_log_hz"]),
        )

        sh = raw["shaft"]
        shaft = Shaft(
            diameter_mm=float(sh["diameter_mm"]),
            operator_prompt=bool(sh.get("operator_prompt", True)),
        )

        channels: dict[str, ChannelFormula] = {}
        for ch_name, ch_raw in raw.get("channels", {}).items():
            channels[ch_name] = ChannelFormula(
                formula=str(ch_raw["formula"]),
                output_unit=str(ch_raw.get("output_unit", "")),
                inputs={k: float(v) for k, v in ch_raw.get("inputs", {}).items()},
            )

        acceptance: dict[str, AcceptanceBand] = {}
        for ch_name, acc_raw in raw.get("acceptance", {}).items():
            mode = str(acc_raw["mode"])
            points = tuple(
                (float(p), float(u), float(l)) for p, u, l in acc_raw.get("points", [])
            )
            acceptance[ch_name] = AcceptanceBand(
                mode=mode,
                points=points,
                tolerance=(
                    float(acc_raw["tolerance"]) if "tolerance" in acc_raw else None
                ),
            )

        efficiency: EfficiencyCurve | None = None
        if "efficiency" in raw:
            eff_raw = raw["efficiency"]
            efficiency = EfficiencyCurve(
                points=tuple(
                    (float(p), float(e)) for p, e in eff_raw.get("points", [])
                ),
                fallback=float(eff_raw.get("fallback", displacement.mech_efficiency)),
            )

        return cls(
            schema_version=str(raw.get("schema_version", "1.0")),
            identity=dict(raw.get("identity", {})),
            displacement=displacement,
            rated_rpm=float(raw["speed"]["rated_rpm"]),
            pressure_sweep=pressure_sweep,
            acquisition=acquisition,
            shaft=shaft,
            channels=channels,
            acceptance=acceptance,
            efficiency=efficiency,
            source_path=source_path,
        )

    # -- input assembly for the formula engine ------------------------------

    def flow_inputs(self, pressure_bar: float) -> dict[str, float]:
        """
        Build the input mapping the flow formula needs: its profile-declared
        inputs plus the live pressure reading. Pure data assembly — no maths here.
        """
        return {**self.channels["flow"].inputs, "pressure_bar": pressure_bar}

    def torque_inputs(self, pressure_bar: float, flow_lpm: float) -> dict[str, float]:
        """
        Inputs for the absorption-torque formula (shared profile constants + live values).

        Mechanical efficiency is resolved at the *live pressure* from the profile's
        efficiency curve when one is supplied (the operating-point η is what the formula
        needs), falling back to the single scalar ``displacement.mech_efficiency`` for
        pumps without a curve. This is the layer where the empirical efficiency map turns
        the constant-power formula's flat plateau into the chart's climbing-then-plateau
        nominal curve — without the formula knowing anything about it.
        """
        eta = (
            self.efficiency.eta_at(pressure_bar)
            if self.efficiency is not None
            else self.displacement.mech_efficiency
        )
        base = {
            "pressure_bar": pressure_bar,
            "flow_lpm": flow_lpm,
            "rpm": self.rated_rpm,
            "n_sections": float(self.displacement.n_sections),
            "mech_efficiency": eta,
        }
        base.update(self.channels.get("torque", ChannelFormula("", "", {})).inputs)
        return base

    def power_inputs(self, pressure_bar: float, flow_lpm: float) -> dict[str, float]:
        """Inputs for the hydraulic-power formula (live pressure + flow, plus any profile inputs)."""
        base = {"pressure_bar": pressure_bar, "flow_lpm": flow_lpm}
        base.update(self.channels.get("power", ChannelFormula("", "", {})).inputs)
        return base


__all__ = [
    "PumpProfile",
    "Displacement",
    "PressureSweep",
    "Acquisition",
    "Shaft",
    "ChannelFormula",
    "AcceptanceBand",
    "EfficiencyCurve",
]
