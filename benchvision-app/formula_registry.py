"""
formula_registry.py

BenchVision — named, version-tagged formula registry for derived test channels.

This is the curated half of the parameterised formula engine described in
`demo-simulation/spec.md` §8A and the 2026-05-27 decision-log entries. Derived
channels (flow, torque, power, …) are *not* hard-coded per pump; they are computed
by a small library of named, version-tagged, pure formulas, selected and
parameterised by a per-test pump profile (see `pump_profile.py`).

Design constraints carried from the decision log:

  * Pure functions, side-effect free, easy to unit-test. Every formula is a plain
    callable ``(inputs: Mapping[str, float]) -> float`` — no I/O, no globals, no
    channel state. The same signature is what a *custom* (user-authored) formula
    would present, so the registry interface does **not** preclude the gated
    custom-formula sandbox (decision-log 2026-05-27, second entry). A custom
    formula is just another ``FormulaSpec`` whose ``provenance`` is "custom" and
    whose ``author`` names the responsible editor.

  * No pump-specific constants live here. Displacement, rated RPM, the destroke
    knee, acceptance limits, shaft diameter — all arrive through ``inputs`` from
    the pump profile. The only literals in this file are genuine *unit-conversion*
    constants (e.g. bar·cc/rev → Nm), which are physics, not pump nameplate.

British English throughout, per project convention.

Python 3.12+ (uses ``from __future__ import annotations`` for forward refs).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Genuine unit-conversion constants (physics, not pump nameplate)
# ---------------------------------------------------------------------------

# Torque from pressure × displacement.
#   T[Nm] = P[Pa] · Vg[m³/rev] / (2π)
# Converting P from bar (×1e5 Pa) and Vg from cc/rev (×1e-6 m³):
#   T[Nm] = P[bar] · Vg[cc/rev] · 1e5 · 1e-6 / (2π)
#         = P[bar] · Vg[cc/rev] / (20π)
# 20π ≈ 62.8319 — the "62.8" that was an unexplained magic number in the old
# TorqueChannel. It is a unit conversion, so it stays in code; it is not a pump
# constant.
TORQUE_BAR_CC_TO_NM: float = 20.0 * math.pi  # ≈ 62.8319

# Hydraulic power.
#   P_hyd[kW] = P[bar] · Q[L/min] / 600
# Derivation: 1 bar·L/min = 1e5 Pa · (1e-3 m³ / 60 s) = 1.6667 W → /600 gives kW.
POWER_BAR_LPM_TO_KW: float = 600.0


# ---------------------------------------------------------------------------
# Formula specification
# ---------------------------------------------------------------------------

# A formula is a pure callable over a flat mapping of named inputs.
FormulaFn = Callable[[Mapping[str, float]], float]


@dataclass(frozen=True)
class FormulaSpec:
    """
    One named, version-tagged, pure formula.

    Attributes
    ----------
    name : str
        Stable identifier, e.g. ``"pump_flow_pc_destroke"``.
    version : str
        Version tag, e.g. ``"v1"``. A formula is *version-locked* once it has
        produced a certified result (decision-log 2026-05-27), so historical
        certificates remain reconstructable — versioning is how that lands.
    summary : str
        One-line human description (shown in caution-layer previews later).
    required_inputs : tuple[str, ...]
        Input keys the formula reads. The engine checks these are present before
        evaluating; this is also the hook the future caution layer's range / unit
        / dimensional checks attach to.
    output_unit : str
        Engineering unit of the result, e.g. ``"L/min"``, ``"Nm"``, ``"kW"``.
    fn : FormulaFn
        The pure callable. MUST be side-effect free.
    provenance : str
        ``"verified"`` for the curated registry; ``"custom"`` for a user-authored
        formula (reserved — the custom-formula mode is decided but not built).
    author : str
        Responsible author. For verified formulas this is BenchVision; for custom
        formulas it is the named engineer who accepts liability.
    """

    name: str
    version: str
    summary: str
    required_inputs: tuple[str, ...]
    output_unit: str
    fn: FormulaFn
    provenance: str = "verified"
    author: str = "BenchVision (verified registry)"

    @property
    def qualified_name(self) -> str:
        """e.g. ``"pump_flow_pc_destroke@v1"`` — what a config or certificate cites."""
        return f"{self.name}@{self.version}"


class MissingInputError(KeyError):
    """Raised when a formula is evaluated without all its required inputs."""


class FormulaNotFoundError(KeyError):
    """Raised when a config names a formula the registry does not hold."""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

@dataclass
class FormulaRegistry:
    """
    A name → FormulaSpec lookup with required-input validation on evaluate().

    The registry is deliberately small and explicit. Resolution is by either the
    bare name (``"pump_flow_pc_destroke"``, latest registered version) or the
    qualified name (``"pump_flow_pc_destroke@v1"``). Configs are encouraged to use
    a versioned reference such as ``pump_flow_pc_destroke_v1`` (see ``_split_ref``)
    so the maths behind a certificate is pinned.
    """

    _by_qualified: dict[str, FormulaSpec] = field(default_factory=dict)
    _latest_version: dict[str, str] = field(default_factory=dict)

    # -- registration -------------------------------------------------------

    def register(self, spec: FormulaSpec) -> None:
        """
        Add a formula. Re-registering the *same* qualified name with a *different*
        function is refused — version tags exist precisely so a changed formula
        gets a new version rather than silently mutating an old certificate's maths.
        """
        existing = self._by_qualified.get(spec.qualified_name)
        if existing is not None and existing.fn is not spec.fn:
            raise ValueError(
                f"Refusing to overwrite {spec.qualified_name}: a different function "
                f"is already registered under that version. Bump the version tag."
            )
        self._by_qualified[spec.qualified_name] = spec
        # Track latest version per bare name (string compare is fine for v1, v2, …).
        prev = self._latest_version.get(spec.name)
        if prev is None or spec.version > prev:
            self._latest_version[spec.name] = spec.version

    # -- resolution ---------------------------------------------------------

    @staticmethod
    def _split_ref(ref: str) -> tuple[str, str | None]:
        """
        Accept the three reference styles a config might use:
          * ``"pump_flow_pc_destroke@v1"`` → ("pump_flow_pc_destroke", "v1")
          * ``"pump_flow_pc_destroke_v1"``  → ("pump_flow_pc_destroke", "v1")
          * ``"pump_flow_pc_destroke"``     → ("pump_flow_pc_destroke", None)
        """
        if "@" in ref:
            name, version = ref.split("@", 1)
            return name, version
        # Trailing _v<NN> is treated as a version suffix.
        if "_v" in ref:
            head, tail = ref.rsplit("_v", 1)
            if tail.isdigit():
                return head, f"v{tail}"
        return ref, None

    def resolve(self, ref: str) -> FormulaSpec:
        """Return the FormulaSpec for a config reference, or raise FormulaNotFoundError."""
        name, version = self._split_ref(ref)
        if version is None:
            version = self._latest_version.get(name)
            if version is None:
                raise FormulaNotFoundError(f"No formula registered under name '{name}'")
        qualified = f"{name}@{version}"
        try:
            return self._by_qualified[qualified]
        except KeyError as exc:
            raise FormulaNotFoundError(
                f"No formula '{qualified}' in registry "
                f"(have: {sorted(self._by_qualified)})"
            ) from exc

    # -- evaluation ---------------------------------------------------------

    def evaluate(self, ref: str, inputs: Mapping[str, float]) -> float:
        """
        Resolve ``ref`` and evaluate it against ``inputs``.

        Validates that every ``required_inputs`` key is present *before* calling
        the formula — this is the single choke point where the future caution
        layer (range-check, unit-check, monotonicity) will also run.
        """
        spec = self.resolve(ref)
        missing = [k for k in spec.required_inputs if k not in inputs]
        if missing:
            raise MissingInputError(
                f"{spec.qualified_name} requires {list(spec.required_inputs)}; "
                f"missing {missing}"
            )
        return float(spec.fn(inputs))

    def __contains__(self, ref: str) -> bool:
        try:
            self.resolve(ref)
            return True
        except FormulaNotFoundError:
            return False


# ---------------------------------------------------------------------------
# Curated formulas (pure functions)
# ---------------------------------------------------------------------------
#
# Each is a module-level pure function so it is trivially unit-testable and could
# later be diffed against a custom re-implementation in the caution layer.

def _pump_flow_linear(i: Mapping[str, float]) -> float:
    """
    Legacy linear pump characteristic: ``Q = Q0 − slope · P``.

    This is the *original* hard-coded model. It is kept in the registry for two
    reasons: (1) it lets the refactor prove byte-identical behaviour against the
    pre-refactor code (faithful-refactor test); (2) a genuinely linear fixed-
    displacement pump is a legitimate config that should not need new code.
    It is NOT the right model for the power-controlled HPV95 — see destroke below.
    """
    q = i["no_load_flow"] - i["flow_pressure_slope"] * i["pressure_bar"]
    return max(0.0, q)


def _pump_flow_pc_destroke(i: Mapping[str, float]) -> float:
    """
    Power-controlled, variable-displacement pump flow.

    Flat at ``no_load_flow`` up to the PC cut-in pressure, then a constant-power
    hyperbola ``Q = power_const / P``. This is the shape Devon described (full
    stroke at low pressure, destroke past the knee) and the shape that makes the
    torque plateau emerge for free when torque is derived from *live* flow.
    """
    p = i["pressure_bar"]
    q0 = i["no_load_flow"]
    if p <= i["pc_cutin_bar"]:
        return q0
    return max(0.0, i["power_const"] / p)


def _absorption_torque_from_flow(i: Mapping[str, float]) -> float:
    """
    Input-shaft absorption torque, derived from *live* flow (not a frozen Vg):

        Vg_eff = Q · 1000 / n           (effective displacement per section, cc/rev)
        T      = P · Vg_eff · sections / (20π · η_mech)

    Because the pump destrokes under power control, Vg_eff falls as pressure
    rises, so torque rises to the PC knee then plateaus — the Video-3 behaviour —
    without any special-casing. Needs the live flow and speed as inputs.
    """
    n = i["rpm"]
    if n < 1.0:
        return 0.0
    vg_eff = i["flow_lpm"] * 1000.0 / n          # cc/rev per section
    return (
        i["pressure_bar"] * vg_eff * i["n_sections"]
        / (TORQUE_BAR_CC_TO_NM * i["mech_efficiency"])
    )


def _radial_torque_sin90(i: Mapping[str, float]) -> float:
    """
    Radial torque from a force at a radius: ``T = F · r · sin(θ)`` (Video 4).

    Measurement is taken at 90°, so ``sin(θ)`` collapses to 1, but the angle is
    kept as an input so the formula stays general. Radius is derived from the
    operator-supplied shaft diameter (mm → m).
    """
    radius_m = (i["shaft_diameter_mm"] / 2.0) / 1000.0
    return i["force_n"] * radius_m * math.sin(math.radians(i["angle_deg"]))


def _power_from_flow_pressure(i: Mapping[str, float]) -> float:
    """Hydraulic power: ``P_hyd[kW] = P[bar] · Q[L/min] / 600``."""
    return i["pressure_bar"] * i["flow_lpm"] / POWER_BAR_LPM_TO_KW


# ---------------------------------------------------------------------------
# Default registry assembly
# ---------------------------------------------------------------------------

def build_default_registry() -> FormulaRegistry:
    """Return a registry pre-loaded with the curated, verified formulas."""
    reg = FormulaRegistry()
    reg.register(FormulaSpec(
        name="pump_flow_linear",
        version="v1",
        summary="Linear fixed-displacement flow: Q = Q0 − slope·P",
        required_inputs=("pressure_bar", "no_load_flow", "flow_pressure_slope"),
        output_unit="L/min",
        fn=_pump_flow_linear,
    ))
    reg.register(FormulaSpec(
        name="pump_flow_pc_destroke",
        version="v1",
        summary="Power-controlled flow: flat to PC cut-in, then constant-power hyperbola",
        required_inputs=("pressure_bar", "no_load_flow", "pc_cutin_bar", "power_const"),
        output_unit="L/min",
        fn=_pump_flow_pc_destroke,
    ))
    reg.register(FormulaSpec(
        name="absorption_torque_from_flow",
        version="v1",
        summary="Input-shaft absorption torque from live flow; plateaus under power control",
        required_inputs=("pressure_bar", "flow_lpm", "rpm", "n_sections", "mech_efficiency"),
        output_unit="Nm",
        fn=_absorption_torque_from_flow,
    ))
    reg.register(FormulaSpec(
        name="radial_torque_sin90",
        version="v1",
        summary="Radial torque T = F·r·sin(θ); shaft radius from operator diameter input",
        required_inputs=("force_n", "shaft_diameter_mm", "angle_deg"),
        output_unit="Nm",
        fn=_radial_torque_sin90,
    ))
    reg.register(FormulaSpec(
        name="power_from_flow_pressure",
        version="v1",
        summary="Hydraulic power P_hyd[kW] = P[bar]·Q[L/min]/600",
        required_inputs=("pressure_bar", "flow_lpm"),
        output_unit="kW",
        fn=_power_from_flow_pressure,
    ))
    return reg


__all__ = [
    "FormulaSpec",
    "FormulaRegistry",
    "FormulaNotFoundError",
    "MissingInputError",
    "build_default_registry",
    "TORQUE_BAR_CC_TO_NM",
    "POWER_BAR_LPM_TO_KW",
]
