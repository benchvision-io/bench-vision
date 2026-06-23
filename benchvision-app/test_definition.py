"""
test_definition.py

BenchVision — the **test definition**: the test's *intent* as explicit data.

This closes the **sequence-intent seam** (decision-log 2026-06-18 / 2026-06-22), the
second of the two orthogonal seams. The first — the *provenance* seam — is already
built (``ChannelSource`` in ``sequencer.py``: *where a value comes from*, derived vs
measured). This one answers the other question: *what does the test intend* — the
ordered operating points, and **when is each one settled**.

Until now that intent was *borrowed from the simulator's physics*: the sequencer keyed
its progression off ``pressure.cycle_phase`` and captured the instant rising pressure
crossed a gridpoint — settled or not. A real bench has no ``cycle_phase`` string to
read, so the live sequencer would have nothing to key off; manual and automated modes
were secretly two products. Lifting the intent into data, read by one definition, makes
them one.

**The load-bearing constraint — settle is expressed only in OBSERVABLE CHANNEL TERMS.**
A point is "settled" when an *observed channel* is stable (spread within a tolerance, or
``|d/dt|`` below a threshold) for a dwell of N samples, at the target pressure. Never in
sim-internal terms: if "settled" meant ``cycle_phase == "hold"`` the live sequencer still
could not read it and we would have three products, not one. The same condition is
evaluable by a simulator source and a real transducer alike — that is the whole point.
(Same shape as the de-energisation measured-band work — ``safe_below`` + ``settle_seconds``:
a measured fact, not a modelled phase.)

One definition feeds **three consumers**: the manual checklist (a human follows the
points + settle conditions), the sim sequencer (drives the sim toward each point and
judges settled from the definition), and a future live sequencer (the same loop). This
module owns the *data* and the *pure settle test*; the grading bands stay where they live
(``profile.acceptance``) — the points are **derived from** the flow band's gridpoints so
there is one source of truth, never a duplicated list.

British English throughout. Python 3.12+ (``from __future__ import annotations``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Deriving the operating points from the flow band — one source of truth
# ---------------------------------------------------------------------------

#: The token a profile uses to say "derive the operating points from the flow band's
#: own gridpoints" rather than listing them again. Grading at the same pressures the
#: band is defined at is chart-faithful and means the points are never duplicated.
OPERATING_POINTS_FROM_FLOW_BAND = "acceptance.flow"


def derive_gridpoints(band: object) -> tuple[float, ...]:
    """The pressures to grade/visit: the flow band's own gridpoint pressures, rising,
    excluding the no-load 0-bar point. ``band`` is a ``PumpProfile.AcceptanceBand`` (duck-
    typed on ``.points`` so this module need not import the profile and risk a cycle)."""
    points = getattr(band, "points", ())
    return tuple(sorted({float(p) for p, *_ in points if float(p) > 0.0}))


# ---------------------------------------------------------------------------
# The settle condition — observable channel terms only
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SettleCondition:
    """When is an operating point "settled" — stated only in **observable channel terms**.

    A point counts as settled when, over the last ``for_ticks`` samples (the dwell):

      * the **pressure** has reached the point — every recent pressure reading is within
        ``at_target_bar`` of the target (so we are parked *at* the point, not just passing
        through it on the way up the ramp); **and**
      * the settle **channel** is stable — its window spread (max−min) is within
        ``stable_within`` and/or its sample-to-sample rate ``|Δ/dt|`` is within
        ``max_abs_rate``.

    At least one stability test (``stable_within`` or ``max_abs_rate``) must be set, else
    every window would trivially "settle".

    *Why the default settle channel is pressure, not flow:* the settle channel must be one
    that genuinely **moves while approaching the point**, so that "stable" really means
    "arrived". Pressure always changes on the approach. Flow does **not** below the PC
    cut-in knee (it sits at no-load ~224 L/min regardless of pressure), so a flow-stability
    test would *falsely* settle mid-ramp for the sub-knee points. Pressure is the swept,
    always-moving variable — the honest choice for a pressure-swept test. (Flow-stability is
    still fully expressible here for benches where flow tracks pressure throughout.)
    """
    channel: str = "pressure"
    at_target_bar: float = 5.0
    stable_within: float | None = 6.0     # window spread tolerance on ``channel``
    max_abs_rate: float | None = None     # |Δchannel/dt| tolerance (channel-unit / second)
    for_ticks: int = 7

    def __post_init__(self) -> None:
        if self.for_ticks < 1:
            raise ValueError("settle.for_ticks must be >= 1")
        if self.at_target_bar <= 0:
            raise ValueError("settle.at_target_bar must be > 0")
        if self.stable_within is None and self.max_abs_rate is None:
            raise ValueError(
                "a settle condition needs at least one stability test "
                "(stable_within or max_abs_rate)"
            )
        if self.stable_within is not None and self.stable_within <= 0:
            raise ValueError("settle.stable_within must be > 0 when set")
        if self.max_abs_rate is not None and self.max_abs_rate <= 0:
            raise ValueError("settle.max_abs_rate must be > 0 when set")

    def describe(self) -> str:
        """A one-line human description, for the manual checklist."""
        tests = []
        if self.stable_within is not None:
            tests.append(f"{self.channel} stable within ±{self.stable_within:g}")
        if self.max_abs_rate is not None:
            tests.append(f"|Δ{self.channel}/dt| ≤ {self.max_abs_rate:g}/s")
        return (
            f"pressure within ±{self.at_target_bar:g} bar of target and "
            f"{' and '.join(tests)} for {self.for_ticks} consecutive samples"
        )

    @classmethod
    def from_raw(cls, raw: Mapping[str, Any] | None, *, base: "SettleCondition | None" = None) -> "SettleCondition":
        """Build from a TOML ``[test.settle]`` (or per-point override) table, layered onto
        ``base`` (the global default) so a per-point override need only state what changes."""
        base = base or cls()
        if not raw:
            return base
        return replace(
            base,
            channel=str(raw.get("channel", base.channel)),
            at_target_bar=float(raw.get("at_target_bar", base.at_target_bar)),
            stable_within=(
                None if raw.get("stable_within", base.stable_within) is None
                else float(raw["stable_within"]) if "stable_within" in raw
                else base.stable_within
            ),
            max_abs_rate=(
                float(raw["max_abs_rate"]) if "max_abs_rate" in raw and raw["max_abs_rate"] is not None
                else base.max_abs_rate
            ),
            for_ticks=int(raw.get("for_ticks", base.for_ticks)),
        )


def is_settled(
    condition: SettleCondition,
    *,
    target_bar: float,
    pressure_window: Sequence[float],
    channel_window: Sequence[float],
    dt: float,
) -> bool:
    """Pure settle test — **no simulator types in the signature**. Given the recent
    observed readings (pressure, plus the settle channel) and a point's settle condition,
    return whether the point is settled.

    The same function is fed by a simulated source today and a real-transducer source
    tomorrow; it never sees a ``cycle_phase``. ``pressure_window`` and ``channel_window``
    are the most-recent-last readings (e.g. the sequencer's smoothing window); ``dt`` is the
    sample interval in seconds (for the optional rate test).
    """
    n = condition.for_ticks
    if len(channel_window) < n or len(pressure_window) < n:
        return False  # not enough dwell yet

    p_recent = list(pressure_window)[-n:]
    c_recent = list(channel_window)[-n:]

    # 1) Reached and parked at the point — every recent pressure near the target. This is
    #    what stops a capture on the *rising* ramp: passing through the target for an instant
    #    does not satisfy "within tolerance for the whole dwell".
    if max(abs(p - target_bar) for p in p_recent) > condition.at_target_bar:
        return False

    # 2) The settle channel is stable across the dwell (spread and/or rate).
    if condition.stable_within is not None:
        if (max(c_recent) - min(c_recent)) > condition.stable_within:
            return False
    if condition.max_abs_rate is not None:
        rates = [abs(c_recent[i + 1] - c_recent[i]) / dt for i in range(len(c_recent) - 1)]
        if rates and max(rates) > condition.max_abs_rate:
            return False

    return True


# ---------------------------------------------------------------------------
# The operating points and the whole definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OperatingPoint:
    """One declared step of the test: a target pressure and how to know it has settled."""
    pressure_bar: float
    settle: SettleCondition


@dataclass(frozen=True)
class TestDefinition:
    """The ordered test intent — points + per-point settle — as explicit, declarative data.

    ``hold_seconds`` is a **sim-source hint only** (how long the simulator parks at each
    point so the settle window has time to form). A live run ignores it: the operator brings
    the bench to each point and holds; the sequencer's *settle* logic — not this hint — is
    what decides when to capture, identically in sim and live.
    """
    points: tuple[OperatingPoint, ...]
    hold_seconds: float = 4.0
    source: str = ""              # provenance note (e.g. the profile id / token used)

    @property
    def point_pressures(self) -> tuple[float, ...]:
        return tuple(p.pressure_bar for p in self.points)

    def settle_at(self, pressure_bar: float) -> SettleCondition:
        for p in self.points:
            if p.pressure_bar == pressure_bar:
                return p.settle
        raise KeyError(f"no operating point at {pressure_bar} bar")

    # -- loading ------------------------------------------------------------

    @classmethod
    def from_raw(
        cls,
        raw: Mapping[str, Any] | None,
        *,
        flow_band: object,
        source: str = "",
    ) -> "TestDefinition | None":
        """Build from a profile's ``[test]`` table. ``flow_band`` is the parsed flow
        ``AcceptanceBand`` the operating points are derived from (one source of truth).
        Returns ``None`` when the profile carries no ``[test]`` section — callers then
        synthesise a default (see :func:`default_for_band`)."""
        if raw is None:
            return None

        global_settle = SettleCondition.from_raw(raw.get("settle"))

        # Per-point settle overrides, keyed by pressure, layered onto the global default.
        overrides: dict[float, SettleCondition] = {}
        for ov in raw.get("point_settle", []):
            p = float(ov["pressure"])
            overrides[p] = SettleCondition.from_raw(ov, base=global_settle)

        # Operating points: derive from the flow band (default / token), or take an
        # explicit list if the profile gives one.
        op = raw.get("operating_points", OPERATING_POINTS_FROM_FLOW_BAND)
        if isinstance(op, str):
            if op != OPERATING_POINTS_FROM_FLOW_BAND:
                raise ValueError(
                    f"test.operating_points: unknown token {op!r} "
                    f"(use {OPERATING_POINTS_FROM_FLOW_BAND!r} or an explicit list)"
                )
            pressures = derive_gridpoints(flow_band)
        else:
            pressures = tuple(sorted(float(p) for p in op))

        points = tuple(
            OperatingPoint(pressure_bar=p, settle=overrides.get(p, global_settle))
            for p in pressures
        )
        return cls(
            points=points,
            hold_seconds=float(raw.get("hold_seconds", 4.0)),
            source=source or "profile [test] section",
        )

    @classmethod
    def default_for_band(cls, flow_band: object, *, source: str = "") -> "TestDefinition":
        """A sensible default definition when a profile carries no ``[test]`` section:
        the flow band's gridpoints with the default settle condition. Keeps older profiles
        runnable through the definition-driven sequencer without a silent special case."""
        settle = SettleCondition()
        points = tuple(
            OperatingPoint(pressure_bar=p, settle=settle)
            for p in derive_gridpoints(flow_band)
        )
        return cls(points=points, source=source or "synthesised default (no [test] section)")


# ---------------------------------------------------------------------------
# Consumer 1 of 3 — the manual checklist (same data, the human path)
# ---------------------------------------------------------------------------

def render_manual_checklist(test_def: TestDefinition, profile: object) -> str:
    """Render the *same* test definition as a human checklist (Markdown).

    This proves the one definition feeds the manual path too: a technician follows these
    ordered points and settle conditions by hand, recording the same flow (graded against
    the band) and torque (monitored reference) the automated sequencer captures. ``profile``
    is a ``PumpProfile`` (duck-typed on ``.identity`` and ``.acceptance``)."""
    identity = getattr(profile, "identity", {}) or {}
    name = identity.get("display_name") or identity.get("id") or "pump"
    flow_band = getattr(profile, "acceptance", {}).get("flow")

    lines: list[str] = []
    lines.append(f"# Manual test checklist — {name}")
    lines.append("")
    lines.append(
        f"{len(test_def.points)} operating points, in order. At each point: bring the bench "
        "to the target pressure, confirm it has **settled** (the condition below — the same "
        "measured settle the software uses), then record the readings."
    )
    lines.append("")
    lines.append("> Flow is the pass/fail truth (graded against the band). Torque is a "
                 "monitored reference — recorded, never graded.")
    lines.append("")
    for i, pt in enumerate(test_def.points, start=1):
        band_note = ""
        if flow_band is not None:
            try:
                lower, upper = flow_band.limits_at(pt.pressure_bar)
                band_note = f"  ·  flow accept band: {lower:g}–{upper:g} L/min"
            except Exception:
                band_note = ""
        lines.append(f"- [ ] **Point {i} — {pt.pressure_bar:g} bar**{band_note}")
        lines.append(f"      settle: {pt.settle.describe()}")
        lines.append("      record: flow (graded), torque (monitored reference)")
    lines.append("")
    lines.append(f"_Source: {test_def.source}._")
    return "\n".join(lines)


__all__ = [
    "OPERATING_POINTS_FROM_FLOW_BAND",
    "derive_gridpoints",
    "SettleCondition",
    "is_settled",
    "OperatingPoint",
    "TestDefinition",
    "render_manual_checklist",
]


# ---------------------------------------------------------------------------
# Tiny CLI — print the checklist for a profile (consumer 1, runnable)
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover - thin CLI wrapper
    import argparse

    from pump_profile import PumpProfile

    parser = argparse.ArgumentParser(description="Render the manual test checklist for a pump profile.")
    parser.add_argument(
        "profile",
        nargs="?",
        default=str(Path(__file__).parent / "profiles" / "pc200-8-hpv95.toml"),
        help="path to a pump profile .toml",
    )
    args = parser.parse_args()

    prof = PumpProfile.from_toml(args.profile)
    test_def = prof.test or TestDefinition.default_for_band(prof.acceptance["flow"])
    print(render_manual_checklist(test_def, prof))
