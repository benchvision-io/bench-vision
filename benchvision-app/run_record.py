"""
run_record.py

BenchVision — the test-run record: the spine that ties together which pump *model*
(profile), which physical *unit* (``dut_serial``), *why* (purpose), and the resulting
*verdicts* (flow/torque + cleanliness).

Three identities meet here and nowhere else (see
``docs/test-purpose-schema-sketch.md`` §1):

  * the engine/bench is **model-agnostic** (one install tests any pump model);
  * a **profile** is per pump *model* (``profiles/pc200-8-hpv95.toml`` — the grading
    reference for one model);
  * a **run** is one test of one physical *unit* of one model, for one reason, on one
    day, by one operator.

So purpose and results are **per-run** metadata that *reference* a profile by id; they
never live inside the profile ``.toml`` (that would pin a per-run concept to a per-model
artefact). ``RunRecord`` is the only place all three identities are joined.

Design constraints honoured here:

  * **Source-agnostic results.** On a real bench, flow/torque are *measured*, not
    *derived* (the live-mode inversion, ``forward-requirements`` §1; Devon's pump-agnostic
    principle, decision-log 2026-06-01). Each result therefore carries a *value*, a
    *pass/fail*, and a *provenance* — so the same record serves a simulated run
    (``derived``) and a live run (``measured``) identically.
  * **"Not meant to grade" vs "meant to grade but couldn't".** A monitored reference
    (torque) and a recorded-only cleanliness reading (target unconfirmed) are *legitimately
    excluded* from the pass/fail gate. An expected-to-grade result that could not be
    evaluated (an invalid/missing reading) is *not* excluded — it forces
    ``overall_passed = None`` with a note, so a silently-wrong pass cannot slip through.
  * **Contemporaneous time (ALCOA+).** Timestamps are timezone-aware **UTC** ISO 8601
    strings; naive or non-UTC values are rejected at construction.

Cleanliness types are **reused** from ``cleanliness.py`` (never duplicated).
``TestPurpose`` is deliberately self-contained — it imports nothing from the result types,
``RunRecord``, or ``cleanliness`` — so it can be lifted into its own module later (for the
caution layer and certificate) with no untangling.

Persistence: a per-run **JSON sidecar**. A run record is generated per-run *data*, not
hand-authored *config*, so the profiles' TOML choice does not carry over; stdlib
``tomllib`` is read-only (emitting TOML would need a new third-party writer), whereas
stdlib ``json`` round-trips natively and is the natural staging format ahead of the
SQLite layer. The :class:`RunRecordRepository` Protocol is the seam for that future
SQLite layer; only the JSON-file implementation is built here.

British English throughout. Python 3.12+ (``from __future__ import annotations``).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from cleanliness import CleanlinessReading, CleanlinessVerdict

#: Bumped when the persisted JSON shape changes. 1.1 adds the optional
#: uncertainty / decision-regime fields to ``ChannelResult`` (see
#: ``docs/uncertainty-integration-plan.md`` §7); the change is forward- and
#: backward-compatible — new keys are additive and old records read with defaults.
RUN_RECORD_SCHEMA_VERSION = "1.1"


# ---------------------------------------------------------------------------
# Why a run exists — self-contained value object (imports nothing below it)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TestPurpose:
    """
    Why a run exists. Per-run metadata that references a pump profile; never lives
    inside the profile ``.toml``. Two orthogonal axes plus a context tag
    (``docs/test-purpose-schema-sketch.md`` §2):

      * ``intent``       — the V/V/Q/A dialect (what question the test answers).
      * ``repair_stage`` — where in an overhaul the run sits (the axis the four dialects
                           cannot express); ``not_applicable`` for new-build / OEM.
      * ``context``      — who the run is for / which programme (drives labelling).

    ``intent`` and ``repair_stage`` are strictly validated. ``context`` is deliberately
    left as free text (sketch §2 / open-question 3 mark it "open-ish, not yet formalised"
    pending the Komatsu OEM-rig conversation) — a closed vocabulary is not invented here.

    NOTE on the word "validation": the codebase already uses it for *software* validation
    (the PC200-8 profile is "the validation case for the formula engine"). The ``intent``
    value ``validation`` is *test-purpose* validation (did we design the right thing?).
    The two meanings are distinct.
    """

    intent: str
    repair_stage: str = "not_applicable"
    context: str = "unspecified"

    _INTENTS = frozenset({"validation", "verification", "qualification", "acceptance"})
    _STAGES = frozenset({"as_found", "as_left", "not_applicable"})

    def __post_init__(self) -> None:
        if self.intent not in self._INTENTS:
            raise ValueError(
                f"purpose.intent must be one of {sorted(self._INTENTS)}, got {self.intent!r}"
            )
        if self.repair_stage not in self._STAGES:
            raise ValueError(
                f"purpose.repair_stage must be one of {sorted(self._STAGES)}, "
                f"got {self.repair_stage!r}"
            )

    # -- behaviour this field is meant to DRIVE --------------------------------

    @property
    def deviations_expected(self) -> bool:
        """Validation, and any as-found run, expect to wander outside the band:
        out-of-envelope points are DATA, not alarms. Verification/acceptance treat the
        same points as failures."""
        return self.intent == "validation" or self.repair_stage == "as_found"

    @property
    def grades_pass_fail(self) -> bool:
        """Verification & acceptance produce a pass/fail verdict against the profile's
        flow acceptance band. Validation characterises; it does not grade. (Torque stays
        a monitored reference regardless — decision-log 2026-06-01.)"""
        return self.intent in {"verification", "acceptance"}

    @property
    def signoff_required(self) -> bool:
        """Acceptance is a transaction act — it needs a named signatory. The MVP does NOT
        build that ceremony yet: if ``signoff_required`` is True and no signature is
        captured, the certificate is *evidence*, not an *accepted result*."""
        return self.intent == "acceptance"

    @property
    def certificate_class(self) -> str:
        """Which template/marking the run produces."""
        if self.intent == "acceptance":
            return "acceptance_certificate"   # needs a signature block
        if self.intent in {"verification", "qualification"}:
            return "test_report"
        return "characterisation_record"      # validation / as-found: data, not a verdict

    # -- (de)serialisation -----------------------------------------------------

    def to_dict(self) -> dict[str, str]:
        return {
            "intent": self.intent,
            "repair_stage": self.repair_stage,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "TestPurpose":
        return cls(
            intent=str(raw["intent"]),
            repair_stage=str(raw.get("repair_stage", "not_applicable")),
            context=str(raw.get("context", "unspecified")),
        )


# ---------------------------------------------------------------------------
# Contemporaneous time (ALCOA+): timezone-aware UTC ISO 8601 only
# ---------------------------------------------------------------------------

def utc_now_iso() -> str:
    """Return the current instant as a timezone-aware UTC ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _assert_utc_iso(value: str, field_name: str) -> None:
    """Reject naive or non-UTC timestamps — ALCOA+ wants unambiguous time."""
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO 8601 string, got {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(
            f"{field_name} must be timezone-aware (UTC), got naive {value!r}"
        )
    if parsed.utcoffset() != timedelta(0):
        raise ValueError(
            f"{field_name} must be in UTC (offset +00:00), got {value!r}"
        )


# ---------------------------------------------------------------------------
# Source-agnostic results (the live-mode inversion)
# ---------------------------------------------------------------------------

class Provenance:
    """Where a result *value* came from. The single field that lets one record serve a
    simulated run and a live run identically."""
    MEASURED = "measured"   # live: read off a real sensor (formula is a reference only)
    DERIVED = "derived"     # training/simulator: computed by a named formula
    MANUAL = "manual"       # operator-entered


_PROVENANCES = frozenset({Provenance.MEASURED, Provenance.DERIVED, Provenance.MANUAL})


# ---------------------------------------------------------------------------
# Measurement-uncertainty decision rules (GUM / ILAC-G8)
# ---------------------------------------------------------------------------
# The method canon is ``docs/uncertainty-budget-methodology-2026-06-09.md`` and
# the seam this schema opens is ``docs/uncertainty-integration-plan.md`` §2. The
# fields these enums type are all optional on :class:`ChannelResult`, defaulting
# to "no uncertainty data" so a record written before this patch behaves exactly
# as it did under the original four-state model.

class MarginState:
    """Where a channel reading sits relative to its acceptance limits, *after* the
    guard band is applied (ILAC-G8:09/2019 §4).

      * ``INSIDE``   — ``value ± U`` lies wholly inside the limits → PASS.
      * ``MARGINAL`` — ``value ± U`` straddles a limit → indeterminate; only reachable
        under ``guarded_acceptance``, and always paired with ``passed=None``.
      * ``OUTSIDE``  — ``value`` is beyond a limit → FAIL.
      * ``UNKNOWN``  — no reading, or no uncertainty budget → reverts to the existing
        ``passed=None`` "could not evaluate" behaviour. This is the default, so a
        record written before the field existed grades identically to today.
    """

    INSIDE = "inside"
    MARGINAL = "marginal"
    OUTSIDE = "outside"
    UNKNOWN = "unknown"


_MARGIN_STATES = frozenset({
    MarginState.INSIDE, MarginState.MARGINAL,
    MarginState.OUTSIDE, MarginState.UNKNOWN,
})


class VerdictRegime:
    """Which decision rule applies to a channel (ILAC-G8 §4)."""

    SIMPLE_ACCEPTANCE = "simple_acceptance"      # TUR >= 4: guard band w = 0
    GUARDED_ACCEPTANCE = "guarded_acceptance"    # TUR < 4 (the default for graded channels)
    GUARDED_REJECTION = "guarded_rejection"      # safety-critical only


_VERDICT_REGIMES = frozenset({
    VerdictRegime.SIMPLE_ACCEPTANCE,
    VerdictRegime.GUARDED_ACCEPTANCE,
    VerdictRegime.GUARDED_REJECTION,
})


@dataclass(frozen=True)
class ChannelResult:
    """
    One analogue-channel outcome (flow, torque, …), at an operating point.

    The pass/fail model deliberately separates two states that look alike but must not be
    conflated:

      * ``graded=False`` — a **monitored reference** (e.g. torque, decision-log
        2026-06-01): not meant to produce a verdict, legitimately excluded from the gate.
        ``passed`` must be ``None``.
      * ``graded=True`` with ``passed is None`` — **meant to grade but could not be
        evaluated** (an invalid/missing reading): NOT excluded; it forces the run verdict
        to ``None`` so a silently-wrong pass cannot occur.
      * ``graded=True`` with ``passed`` True/False — an ordinary pass/fail.

    ``provenance`` keeps the value source-agnostic: ``derived`` (+ ``formula``) for the
    simulator, ``measured`` (``formula=""``) for a live sensor.
    """

    channel: str
    value: float
    unit: str
    pressure_bar: float | None = None     # operating point; None for non-pressure-domain
    passed: bool | None = None            # see class docstring
    graded: bool = True                   # False == monitored reference
    provenance: str = Provenance.MEASURED
    formula: str = ""                     # registry id+version when derived; "" when measured

    # --- uncertainty + decision-regime fields (GUM / ILAC-G8) ----------------
    # All optional; the defaults ("no uncertainty data", simple acceptance,
    # UNKNOWN margin) preserve the original four-state behaviour exactly, so a
    # ChannelResult — or a JSON record — written before this patch is unchanged.
    # See docs/uncertainty-integration-plan.md §2.
    combined_standard_uncertainty: float | None = None   # u_c
    expanded_uncertainty: float | None = None            # U = k · u_c
    coverage_factor: float = 2.0                          # k (default 2 ≈ 95 %)
    tolerance_lower: float | None = None                 # acceptance LSL
    tolerance_upper: float | None = None                 # acceptance USL
    tur: float | None = None                             # test-uncertainty ratio (USL−LSL)/(2·U)
    verdict_regime: str = VerdictRegime.SIMPLE_ACCEPTANCE
    guard_band_multiplier: float = 1.0                   # r in w = r · U
    margin_state: str = MarginState.UNKNOWN              # set at grading time

    def __post_init__(self) -> None:
        if self.provenance not in _PROVENANCES:
            raise ValueError(
                f"provenance must be one of {sorted(_PROVENANCES)}, got {self.provenance!r}"
            )
        if not self.graded and self.passed is not None:
            raise ValueError(
                f"channel {self.channel!r}: a monitored reference (graded=False) must have "
                f"passed=None, got {self.passed!r}"
            )
        if self.margin_state not in _MARGIN_STATES:
            raise ValueError(
                f"margin_state must be one of {sorted(_MARGIN_STATES)}, "
                f"got {self.margin_state!r}"
            )
        if self.verdict_regime not in _VERDICT_REGIMES:
            raise ValueError(
                f"verdict_regime must be one of {sorted(_VERDICT_REGIMES)}, "
                f"got {self.verdict_regime!r}"
            )
        # A MARGINAL reading is indeterminate by construction: it carries the same
        # passed=None "could not be evaluated" semantics, so a pass/fail on it is a bug.
        if self.margin_state == MarginState.MARGINAL and self.passed is not None:
            raise ValueError(
                f"channel {self.channel!r}: margin_state=MARGINAL requires passed=None "
                f"(indeterminate), got passed={self.passed!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "value": self.value,
            "unit": self.unit,
            "pressure_bar": self.pressure_bar,
            "passed": self.passed,
            "graded": self.graded,
            "provenance": self.provenance,
            "formula": self.formula,
            "combined_standard_uncertainty": self.combined_standard_uncertainty,
            "expanded_uncertainty": self.expanded_uncertainty,
            "coverage_factor": self.coverage_factor,
            "tolerance_lower": self.tolerance_lower,
            "tolerance_upper": self.tolerance_upper,
            "tur": self.tur,
            "verdict_regime": self.verdict_regime,
            "guard_band_multiplier": self.guard_band_multiplier,
            "margin_state": self.margin_state,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ChannelResult":
        # ``.get`` with the field default throughout, so a payload that pre-dates the
        # uncertainty fields deserialises to today's behaviour (backward-compat gate).
        return cls(
            channel=str(raw["channel"]),
            value=float(raw["value"]),
            unit=str(raw.get("unit", "")),
            pressure_bar=(None if raw.get("pressure_bar") is None else float(raw["pressure_bar"])),
            passed=raw.get("passed"),
            graded=bool(raw.get("graded", True)),
            provenance=str(raw.get("provenance", Provenance.MEASURED)),
            formula=str(raw.get("formula", "")),
            combined_standard_uncertainty=(
                None if raw.get("combined_standard_uncertainty") is None
                else float(raw["combined_standard_uncertainty"])
            ),
            expanded_uncertainty=(
                None if raw.get("expanded_uncertainty") is None
                else float(raw["expanded_uncertainty"])
            ),
            coverage_factor=float(raw.get("coverage_factor", 2.0)),
            tolerance_lower=(
                None if raw.get("tolerance_lower") is None else float(raw["tolerance_lower"])
            ),
            tolerance_upper=(
                None if raw.get("tolerance_upper") is None else float(raw["tolerance_upper"])
            ),
            tur=(None if raw.get("tur") is None else float(raw["tur"])),
            verdict_regime=str(raw.get("verdict_regime", VerdictRegime.SIMPLE_ACCEPTANCE)),
            guard_band_multiplier=float(raw.get("guard_band_multiplier", 1.0)),
            margin_state=str(raw.get("margin_state", MarginState.UNKNOWN)),
        )


@dataclass(frozen=True)
class CleanlinessResult:
    """
    One cleanliness outcome: a :class:`CleanlinessReading` paired with its
    :class:`CleanlinessVerdict`. ``verdict is None`` means **recorded-only** — no target
    confirmed yet (an open Devon question), so this reading is legitimately excluded from
    the pass/fail gate. A present verdict whose ``passed is None`` is *meant to grade but
    could not* (an invalid reading) and forces the run verdict to ``None``.
    """

    reading: CleanlinessReading
    verdict: CleanlinessVerdict | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "reading": _reading_to_dict(self.reading),
            "verdict": None if self.verdict is None else _verdict_to_dict(self.verdict),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CleanlinessResult":
        verdict_raw = raw.get("verdict")
        return cls(
            reading=_reading_from_dict(raw["reading"]),
            verdict=None if verdict_raw is None else _verdict_from_dict(verdict_raw),
        )


# -- local (de)serialisation for the reused cleanliness types -----------------
# Kept here so cleanliness.py stays untouched (and its 46-test baseline undisturbed).

def _reading_to_dict(r: CleanlinessReading) -> dict[str, Any]:
    return {
        "iso_code": list(r.iso_code),
        "extra_codes": list(r.extra_codes),
        "counts_per_100ml": list(r.counts_per_100ml),
        "temperature_c": r.temperature_c,
        "water_rh_pct": r.water_rh_pct,
        "flow_ml_min": r.flow_ml_min,
        "status": r.status,
        "sample_point": r.sample_point,
        "reference": r.reference,
        "standard": r.standard,
    }


def _reading_from_dict(raw: Mapping[str, Any]) -> CleanlinessReading:
    iso = tuple(int(x) for x in raw["iso_code"])
    return CleanlinessReading(
        iso_code=iso,  # type: ignore[arg-type]
        extra_codes=tuple(int(x) for x in raw.get("extra_codes", [])),
        counts_per_100ml=tuple(int(x) for x in raw.get("counts_per_100ml", [])),
        temperature_c=raw.get("temperature_c"),
        water_rh_pct=raw.get("water_rh_pct"),
        flow_ml_min=raw.get("flow_ml_min"),
        status=str(raw.get("status", "ready")),
        sample_point=str(raw.get("sample_point", "unit_outlet")),
        reference=str(raw.get("reference", "")),
        standard=str(raw.get("standard", "ISO4406:1999")),
    )


def _verdict_to_dict(v: CleanlinessVerdict) -> dict[str, Any]:
    return {"passed": v.passed, "per_band": list(v.per_band), "note": v.note}


def _verdict_from_dict(raw: Mapping[str, Any]) -> CleanlinessVerdict:
    return CleanlinessVerdict(
        passed=raw.get("passed"),
        per_band=tuple(bool(x) for x in raw.get("per_band", [])),
        note=str(raw.get("note", "")),
    )


# ---------------------------------------------------------------------------
# The run verdict — the four honest states
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunVerdict:
    """
    The run's overall outcome, computed from its results gated by the purpose.

    Five states, kept distinct on purpose:

      * ``graded=False``                   → NOT GRADED — the purpose doesn't grade
                                            (characterisation/as-found), or nothing was
                                            meant to be graded.
      * ``graded=True``,  ``passed=True``  → PASS.
      * ``graded=True``,  ``passed=False`` → FAIL.
      * ``graded=True``,  ``marginal=True``→ MARGINAL — a graded reading sits within the
                                            guard band of its limit; the verdict is
                                            indeterminate (ILAC-G8 §4, uncertainty-
                                            integration-plan §3). ``passed`` is ``None``.
      * ``graded=True``,  ``passed=None``  → INCOMPLETE — something *meant* to grade could
                                            not be evaluated (see ``note``).

    MARGINAL sits between FAIL and INCOMPLETE: a FAIL still kills the run, but a knife-edge
    reading is reported as indeterminate rather than masquerading as either a pass or a
    clean failure.
    """

    passed: bool | None
    graded: bool
    marginal: bool = False
    note: str = ""

    @property
    def summary(self) -> str:
        if not self.graded:
            return "NOT GRADED"
        if self.marginal:
            return "MARGINAL"
        if self.passed is None:
            return "INCOMPLETE"
        return "PASS" if self.passed else "FAIL"


# ---------------------------------------------------------------------------
# The run record
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunRecord:
    """
    One test of one physical unit. References a profile by id; carries the purpose, the
    identity fields, and the accumulated results. Frozen — an audit artefact, not a live
    buffer. (Forward note, decision-log 2026-06-02: when the sequencer arrives, a run will
    accumulate results as it executes, so there will need to be a build-up-then-freeze
    step in front of this frozen shape; deliberately out of scope here.)
    """

    id: str
    profile: str                          # profile id reference -> profiles/<id>.toml
    dut_serial: str
    operator: str
    po_number: str
    purpose: TestPurpose
    mode: str = "training"                # training | live — the live-vs-training cert mark
    started_at: str | None = None         # UTC ISO 8601
    finished_at: str | None = None        # UTC ISO 8601
    channel_results: tuple[ChannelResult, ...] = ()
    cleanliness_results: tuple[CleanlinessResult, ...] = ()
    notes: str = ""

    _MODES = frozenset({"training", "live"})

    def __post_init__(self) -> None:
        if self.mode not in self._MODES:
            raise ValueError(f"mode must be one of {sorted(self._MODES)}, got {self.mode!r}")
        if self.started_at is not None:
            _assert_utc_iso(self.started_at, "started_at")
        if self.finished_at is not None:
            _assert_utc_iso(self.finished_at, "finished_at")
        # Coerce result sequences to tuples (frozen-friendly, and forgiving of list input).
        if not isinstance(self.channel_results, tuple):
            object.__setattr__(self, "channel_results", tuple(self.channel_results))
        if not isinstance(self.cleanliness_results, tuple):
            object.__setattr__(self, "cleanliness_results", tuple(self.cleanliness_results))

    # -- the verdict -----------------------------------------------------------

    @property
    def verdict(self) -> RunVerdict:
        """
        Combine the results into one verdict, gated by the purpose. Crucially separates
        results that are *not meant to grade* (excluded) from results that are *meant to
        grade but could not be evaluated* (force INCOMPLETE, never excluded).
        """
        if not self.purpose.grades_pass_fail:
            return RunVerdict(
                passed=None, graded=False,
                note="purpose does not grade (characterisation / as-found)",
            )

        # Results that are MEANT to grade.
        expected_channels = [r for r in self.channel_results if r.graded]
        expected_clean = [c for c in self.cleanliness_results if c.verdict is not None]
        if not expected_channels and not expected_clean:
            return RunVerdict(passed=None, graded=False, note="no gradeable result present")

        ungradeable: list[str] = []
        outcomes: list[bool] = []
        any_outside = False
        any_marginal = False
        for r in expected_channels:
            if r.margin_state == MarginState.OUTSIDE:
                any_outside = True
            if r.margin_state == MarginState.MARGINAL:
                any_marginal = True
                continue                                   # indeterminate, not "could not evaluate"
            if r.passed is None:
                ungradeable.append(r.channel)              # meant to grade, could not
            else:
                outcomes.append(r.passed)
        for c in expected_clean:
            assert c.verdict is not None                   # guarded by expected_clean filter
            if c.verdict.passed is None:
                ungradeable.append(f"cleanliness[{c.reading.sample_point}]")
            else:
                outcomes.append(c.verdict.passed)

        # Precedence (uncertainty-integration-plan §3): a reading OUTSIDE its limits fails
        # the run; a MARGINAL (guard-band-straddling) reading makes it indeterminate; an
        # expected channel that could not be evaluated forces INCOMPLETE; otherwise the
        # collected pass/fail outcomes decide. The OUTSIDE and MARGINAL branches only fire
        # once a channel carries uncertainty data — with the defaults (margin_state=UNKNOWN)
        # this reduces *exactly* to the original four-state behaviour: a legacy passed=False
        # still falls through to FAIL, and a legacy ungradeable still takes precedence over
        # it as INCOMPLETE.
        if any_outside:
            return RunVerdict(
                passed=False, graded=True,
                note="channel reading outside acceptance limits",
            )
        if any_marginal:
            return RunVerdict(
                passed=None, graded=True, marginal=True,
                note="channel reading within the guard band of its limit (indeterminate)",
            )
        if ungradeable:
            return RunVerdict(
                passed=None, graded=True,
                note="meant to grade but could not evaluate: " + ", ".join(ungradeable),
            )
        return RunVerdict(passed=all(outcomes), graded=True)

    @property
    def overall_passed(self) -> bool | None:
        """Convenience: the verdict's pass/fail (``None`` = not graded or incomplete)."""
        return self.verdict.passed

    # -- (de)serialisation -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": RUN_RECORD_SCHEMA_VERSION,
            "record_type": "run_record",
            "id": self.id,
            "profile": self.profile,
            "dut_serial": self.dut_serial,
            "operator": self.operator,
            "po_number": self.po_number,
            "purpose": self.purpose.to_dict(),
            "mode": self.mode,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "channel_results": [r.to_dict() for r in self.channel_results],
            "cleanliness_results": [c.to_dict() for c in self.cleanliness_results],
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RunRecord":
        return cls(
            id=str(raw["id"]),
            profile=str(raw["profile"]),
            dut_serial=str(raw["dut_serial"]),
            operator=str(raw["operator"]),
            po_number=str(raw["po_number"]),
            purpose=TestPurpose.from_dict(raw["purpose"]),
            mode=str(raw.get("mode", "training")),
            started_at=raw.get("started_at"),
            finished_at=raw.get("finished_at"),
            channel_results=tuple(
                ChannelResult.from_dict(r) for r in raw.get("channel_results", [])
            ),
            cleanliness_results=tuple(
                CleanlinessResult.from_dict(c) for c in raw.get("cleanliness_results", [])
            ),
            notes=str(raw.get("notes", "")),
        )

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, text: str) -> "RunRecord":
        return cls.from_dict(json.loads(text))


# ---------------------------------------------------------------------------
# The mutable build-up half (build-up-then-freeze)
# ---------------------------------------------------------------------------

@dataclass
class RunRecordBuilder:
    """
    The mutable build-up half of the **build-up-then-freeze** pattern flagged in the
    2026-06-02 forward note: a real run *accumulates* results as the sequencer executes,
    but the audit artefact must end up frozen. This builder collects results during a
    run, then :meth:`finish` seals the immutable :class:`RunRecord`.

    It holds **no judgement of its own**. Grading is decided upstream (the sequencer
    knows flow-vs-band, torque-as-monitored-reference, which cleanliness stage grades)
    and the honest four-state verdict still falls out of the frozen ``RunRecord``. The
    builder only accumulates and freezes — so a silently-wrong pass cannot originate
    here. ``mark_aborted`` records *why* a run stopped (the audited abort); it does not
    fabricate a verdict — the sequencer appends an ungradeable graded result so the
    sealed record reads INCOMPLETE, never a clean pass.
    """

    id: str
    profile: str
    dut_serial: str
    operator: str
    po_number: str
    purpose: TestPurpose
    mode: str = "training"
    started_at: str | None = None
    notes: str = ""
    channel_results: list[ChannelResult] = field(default_factory=list)
    cleanliness_results: list[CleanlinessResult] = field(default_factory=list)
    _aborted: bool = field(default=False, init=False)

    def start(self, started_at: str | None = None) -> "RunRecordBuilder":
        """Stamp the (contemporaneous, UTC) start time. Returns ``self`` for chaining."""
        self.started_at = started_at or utc_now_iso()
        return self

    def add_channel_result(self, result: ChannelResult) -> None:
        self.channel_results.append(result)

    def add_cleanliness_result(self, result: CleanlinessResult) -> None:
        self.cleanliness_results.append(result)

    def mark_aborted(self, reason: str) -> None:
        """Record that the run stopped before completing (an audited abort is a real
        outcome). Appends the reason to ``notes``; the verdict stays the record's call."""
        self._aborted = True
        entry = f"ABORTED: {reason}"
        self.notes = f"{self.notes}\n{entry}".strip() if self.notes else entry

    @property
    def aborted(self) -> bool:
        return self._aborted

    def finish(self, finished_at: str | None = None) -> RunRecord:
        """Seal the accumulated results into the frozen :class:`RunRecord`."""
        return RunRecord(
            id=self.id,
            profile=self.profile,
            dut_serial=self.dut_serial,
            operator=self.operator,
            po_number=self.po_number,
            purpose=self.purpose,
            mode=self.mode,
            started_at=self.started_at,
            finished_at=finished_at or utc_now_iso(),
            channel_results=tuple(self.channel_results),
            cleanliness_results=tuple(self.cleanliness_results),
            notes=self.notes,
        )


# ---------------------------------------------------------------------------
# Persistence seam (no SQLite this session — Protocol is the seam)
# ---------------------------------------------------------------------------

@runtime_checkable
class RunRecordRepository(Protocol):
    """The persistence seam. A future ``SqliteRunRecordRepository`` implements this same
    interface; nothing above it changes. Only the JSON-file implementation is built now."""

    def save(self, record: RunRecord) -> None: ...
    def load(self, run_id: str) -> RunRecord: ...


class JsonFileRunRecordRepository:
    """One JSON sidecar per run, named ``<run_id>.json`` under ``directory``. The thin
    interim store ahead of the SQLite layer."""

    def __init__(self, directory: str | Path):
        self._dir = Path(directory)

    def _path(self, run_id: str) -> Path:
        return self._dir / f"{run_id}.json"

    def save(self, record: RunRecord) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path(record.id).write_text(record.to_json(), encoding="utf-8")

    def load(self, run_id: str) -> RunRecord:
        return RunRecord.from_json(self._path(run_id).read_text(encoding="utf-8"))


__all__ = [
    "RUN_RECORD_SCHEMA_VERSION",
    "TestPurpose",
    "utc_now_iso",
    "Provenance",
    "MarginState",
    "VerdictRegime",
    "ChannelResult",
    "CleanlinessResult",
    "RunVerdict",
    "RunRecord",
    "RunRecordBuilder",
    "RunRecordRepository",
    "JsonFileRunRecordRepository",
]


# ---------------------------------------------------------------------------
# Tiny runnable demo (training mode, no hardware): python3 run_record.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    purpose = TestPurpose(intent="verification", repair_stage="as_left", context="repair_overhaul")
    incoming = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")
    outlet = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet")
    target = CleanlinessVerdict(passed=True, per_band=(True, True, True))

    record = RunRecord(
        id="2026-06-02-PC200-8-000142",
        profile="pc200-8-hpv95",
        dut_serial="PC200-8-SN-PROVISIONAL",
        operator="devon",
        po_number="PO-PROVISIONAL",
        purpose=purpose,
        mode="training",
        started_at=utc_now_iso(),
        finished_at=utc_now_iso(),
        channel_results=(
            ChannelResult("flow", 148.5, "L/min", pressure_bar=236.0, passed=True,
                          provenance=Provenance.DERIVED, formula="pump_flow_pc_destroke_v1"),
            ChannelResult("torque", 627.0, "Nm", pressure_bar=236.0, graded=False,
                          provenance=Provenance.DERIVED, formula="absorption_torque_from_flow_v1"),
        ),
        cleanliness_results=(
            CleanlinessResult(incoming),                  # recorded-only (no target) → excluded
            CleanlinessResult(outlet, target),            # graded
        ),
    )

    print(f"Run {record.id}  ({record.mode}, {record.purpose.certificate_class})")
    print(f"  purpose: {record.purpose.intent}/{record.purpose.repair_stage}")
    print(f"  verdict: {record.verdict.summary}  {record.verdict.note}")
    round_tripped = RunRecord.from_json(record.to_json())
    print(f"  round-trip equal: {round_tripped == record}")
