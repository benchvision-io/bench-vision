"""
generate_sample_certificates.py

Worked example — generate two certificate PDFs from sample :class:`RunRecord`s so the
output can be eyeballed (session brief §5):

  * a PASS live-ish run  — mode="live", flow MEASURED and graded against the band,
    torque a monitored reference, with as-found/as-left cleanliness;
  * a TRAINING run        — mode="training", flow DERIVED (carries the formula id),
    visibly watermarked non-production.

No invented quantities: the flow/torque values come from the formula engine evaluated
on the PC200-8 validation profile, and each flow point is graded against the profile's
digitised acceptance band. Run:

    python3 generate_sample_certificates.py

Writes into ``sample-certificates/``. British English throughout.
"""

from __future__ import annotations

from pathlib import Path

from bench_simulator import build_default_registry
from certificate import generate_certificate_pdf
from cleanliness import CleanlinessReading, CleanlinessVerdict
from pump_profile import PumpProfile
from run_record import (
    ChannelResult,
    CleanlinessResult,
    Provenance,
    RunRecord,
    TestPurpose,
)

OUT_DIR = Path(__file__).parent / "sample-certificates"
PROFILE_PATH = Path(__file__).parent / "profiles" / "pc200-8-hpv95.toml"
SWEEP_PRESSURES = (50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0)

# Fixed UTC stamps so the worked examples are reproducible (no Date.now()).
STARTED = "2026-06-02T08:15:00+00:00"
FINISHED = "2026-06-02T08:41:00+00:00"
GENERATED = "2026-06-02T08:42:00+00:00"


def _engine_points(profile: PumpProfile, registry) -> list[tuple[float, float, float]]:
    """(pressure, flow, torque) from the formula engine at each sweep pressure."""
    flow_ref = profile.channels["flow"].formula
    torque_ref = profile.channels["torque"].formula
    points: list[tuple[float, float, float]] = []
    for p in SWEEP_PRESSURES:
        flow = registry.evaluate(flow_ref, profile.flow_inputs(p))
        torque = registry.evaluate(torque_ref, profile.torque_inputs(p, flow))
        points.append((p, flow, torque))
    return points


def _flow_results(profile, points, *, provenance, formula) -> list[ChannelResult]:
    """Flow results graded against the profile's flow acceptance band."""
    band = profile.acceptance["flow"]
    out: list[ChannelResult] = []
    for p, flow, _t in points:
        lower, upper = band.limits_at(p)
        passed = lower <= flow <= upper
        out.append(ChannelResult("flow", round(flow, 1), "L/min", pressure_bar=p,
                                 passed=passed, graded=True,
                                 provenance=provenance, formula=formula))
    return out


def _torque_results(points, *, provenance, formula) -> list[ChannelResult]:
    """Torque results — always a monitored reference (graded=False)."""
    return [
        ChannelResult("torque", round(t, 1), "Nm", pressure_bar=p, graded=False,
                      provenance=provenance, formula=formula)
        for p, _f, t in points
    ]


def _pass_live_record(profile, points) -> RunRecord:
    flow = _flow_results(profile, points, provenance=Provenance.MEASURED, formula="")
    torque = _torque_results(points, provenance=Provenance.MEASURED, formula="")
    incoming = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid",
                                  temperature_c=41.0, water_rh_pct=38.0, reference="PO-44821")
    outlet = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet",
                                temperature_c=44.0, water_rh_pct=12.0, reference="PO-44821")
    target = CleanlinessVerdict(passed=True, per_band=(True, True, True))
    return RunRecord(
        id="2026-06-02-PC200-8-000123",
        profile="pc200-8-hpv95",
        dut_serial="PC200-8-SN-000123",
        operator="devon",
        po_number="PO-44821",
        purpose=TestPurpose(intent="verification", repair_stage="as_left", context="repair_overhaul"),
        mode="live",
        started_at=STARTED,
        finished_at=FINISHED,
        channel_results=tuple(flow + torque),
        cleanliness_results=(CleanlinessResult(incoming), CleanlinessResult(outlet, target)),
        notes="Worked example — PASS live-ish verification run.",
    )


def _training_record(profile, points) -> RunRecord:
    flow = _flow_results(profile, points, provenance=Provenance.DERIVED,
                         formula="pump_flow_pc_destroke_v1")
    torque = _torque_results(points, provenance=Provenance.DERIVED,
                             formula="absorption_torque_from_flow_v1")
    return RunRecord(
        id="2026-06-02-PC200-8-TRAIN-001",
        profile="pc200-8-hpv95",
        dut_serial="TRAINING-UNIT",
        operator="trainee",
        po_number="N/A-TRAINING",
        purpose=TestPurpose(intent="verification", repair_stage="as_left", context="internal_qa"),
        mode="training",
        started_at=STARTED,
        finished_at=FINISHED,
        channel_results=tuple(flow + torque),
        notes="Worked example — TRAINING run (derived values, watermarked non-production).",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    profile = PumpProfile.from_toml(PROFILE_PATH)
    registry = build_default_registry()
    points = _engine_points(profile, registry)

    for label, record in (
        ("pass-live", _pass_live_record(profile, points)),
        ("training", _training_record(profile, points)),
    ):
        pdf = generate_certificate_pdf(record, profile, registry, generated_at=GENERATED)
        out = OUT_DIR / f"sample-certificate-{label}-{record.id}.pdf"
        out.write_bytes(pdf)
        print(f"  {record.mode:<9} {record.verdict.summary:<11} → {out}  ({len(pdf):,} bytes)")


if __name__ == "__main__":
    main()
