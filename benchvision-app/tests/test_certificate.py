"""
Unit tests for certificate generation (``certificate.py``).

Run:  python3 -m unittest discover -s tests
(or:  python3 -m unittest tests.test_certificate)

Most tests point at the PURE ``certificate_context`` — that is where every honesty
rule lives (the four states surfaced honestly, the training mark, torque as a
monitored reference, recorded-only cleanliness, as-found/as-left, derived-value
provenance, and the load-bearing rule that INCOMPLETE / NOT GRADED can never become a
clean pass). ``render_html`` gets key-string assertions; ``render_pdf`` gets a smoke
test.

Hardware-free. British English throughout. Mirrors the style of
``tests/test_run_record.py`` / ``tests/test_cleanliness.py``.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cleanliness import CleanlinessReading, CleanlinessVerdict  # noqa: E402
from certificate import (  # noqa: E402
    certificate_context,
    render_html,
    render_pdf,
)
from run_record import (  # noqa: E402
    ChannelResult,
    CleanlinessResult,
    Provenance,
    RunRecord,
    TestPurpose,
)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def _flow(value: float = 148.5, *, pressure: float = 236.0, passed: bool | None = True,
          graded: bool = True, provenance: str = Provenance.DERIVED,
          formula: str = "pump_flow_pc_destroke_v1") -> ChannelResult:
    return ChannelResult("flow", value, "L/min", pressure_bar=pressure, passed=passed,
                         graded=graded, provenance=provenance, formula=formula)


def _torque(value: float = 627.0, *, pressure: float = 236.0) -> ChannelResult:
    # Torque is always a monitored reference (graded=False) — decision-log 2026-06-01.
    return ChannelResult("torque", value, "Nm", pressure_bar=pressure, graded=False,
                         provenance=Provenance.DERIVED, formula="absorption_torque_from_flow_v1")


def _record(*, intent: str = "verification", repair_stage: str = "as_left",
            mode: str = "live", channels=None, cleanliness=()) -> RunRecord:
    if channels is None:
        channels = (_flow(), _torque())
    return RunRecord(
        id="2026-06-02-PC200-8-000123",
        profile="pc200-8-hpv95",
        dut_serial="PC200-8-SN-000123",
        operator="devon",
        po_number="PO-44821",
        purpose=TestPurpose(intent=intent, repair_stage=repair_stage, context="repair_overhaul"),
        mode=mode,
        channel_results=tuple(channels),
        cleanliness_results=tuple(cleanliness),
    )


def _ctx(**kw):
    return certificate_context(_record(**kw))


# ---------------------------------------------------------------------------
# The four honest states — surfaced honestly
# ---------------------------------------------------------------------------

class TestFourStates(unittest.TestCase):
    def test_pass(self) -> None:
        ctx = _ctx(channels=(_flow(passed=True), _torque()))
        self.assertEqual(ctx["overall"]["state"], "PASS")
        self.assertTrue(ctx["overall"]["is_pass"])
        self.assertFalse(ctx["overall"]["needs_attention"])

    def test_fail(self) -> None:
        ctx = _ctx(channels=(_flow(passed=False), _torque()))
        self.assertEqual(ctx["overall"]["state"], "FAIL")
        self.assertFalse(ctx["overall"]["is_pass"])
        self.assertTrue(ctx["overall"]["is_fail"])
        self.assertTrue(ctx["overall"]["needs_attention"])

    def test_not_graded_for_characterisation(self) -> None:
        # validation intent does not grade → NOT GRADED by construction.
        ctx = _ctx(intent="validation", repair_stage="as_found",
                   channels=(_flow(passed=None, graded=True),))
        self.assertEqual(ctx["overall"]["state"], "NOT GRADED")
        self.assertFalse(ctx["overall"]["is_pass"])

    def test_incomplete(self) -> None:
        # meant to grade (graded=True) but could not evaluate (passed=None).
        ctx = _ctx(channels=(_flow(passed=None, graded=True), _torque()))
        self.assertEqual(ctx["overall"]["state"], "INCOMPLETE")
        self.assertFalse(ctx["overall"]["is_pass"])
        self.assertTrue(ctx["overall"]["needs_attention"])

    def test_incomplete_never_becomes_pass(self) -> None:
        # The single most important rule of the session.
        ctx = _ctx(channels=(_flow(passed=None, graded=True), _torque()))
        self.assertNotEqual(ctx["overall"]["state"], "PASS")
        self.assertFalse(ctx["overall"]["is_pass"])

    def test_not_graded_never_becomes_pass(self) -> None:
        ctx = _ctx(intent="validation", channels=(_flow(passed=None, graded=True),))
        self.assertFalse(ctx["overall"]["is_pass"])

    def test_state_css_only_pass_is_pass(self) -> None:
        self.assertEqual(_ctx()["overall"]["state_css"], "pass")
        self.assertEqual(_ctx(channels=(_flow(passed=False), _torque()))["overall"]["state_css"], "fail")


# ---------------------------------------------------------------------------
# Training mark
# ---------------------------------------------------------------------------

class TestTrainingMark(unittest.TestCase):
    def test_training_flagged(self) -> None:
        ctx = _ctx(mode="training")
        self.assertTrue(ctx["is_training"])
        self.assertFalse(ctx["is_live"])

    def test_live_not_flagged_training(self) -> None:
        ctx = _ctx(mode="live")
        self.assertFalse(ctx["is_training"])
        self.assertTrue(ctx["is_live"])


# ---------------------------------------------------------------------------
# Torque — monitored reference, never a verdict
# ---------------------------------------------------------------------------

class TestTorqueIsReference(unittest.TestCase):
    def test_torque_renders_as_monitored_reference(self) -> None:
        ctx = _ctx()
        torque = next(c for c in ctx["channels"] if c["channel"] == "torque")
        self.assertEqual(torque["status"], "monitored reference")
        self.assertTrue(torque["is_reference"])
        self.assertFalse(torque["is_pass"])
        self.assertFalse(torque["is_fail"])

    def test_flow_is_the_graded_truth(self) -> None:
        ctx = _ctx()
        flow = next(c for c in ctx["channels"] if c["channel"] == "flow")
        self.assertEqual(flow["status"], "PASS")
        self.assertFalse(flow["is_reference"])


# ---------------------------------------------------------------------------
# Provenance / version-lock — derived values carry formula id+version
# ---------------------------------------------------------------------------

class TestProvenance(unittest.TestCase):
    def test_derived_channel_carries_formula(self) -> None:
        ctx = _ctx()
        flow = next(c for c in ctx["channels"] if c["channel"] == "flow")
        self.assertTrue(flow["is_derived"])
        self.assertEqual(flow["formula"], "pump_flow_pc_destroke_v1")

    def test_measured_channel_has_no_formula(self) -> None:
        ctx = _ctx(channels=(_flow(provenance=Provenance.MEASURED, formula=""), _torque()))
        flow = next(c for c in ctx["channels"] if c["channel"] == "flow")
        self.assertTrue(flow["is_measured"])
        self.assertEqual(flow["formula"], "")


# ---------------------------------------------------------------------------
# Cleanliness — recorded-only and as-found/as-left
# ---------------------------------------------------------------------------

class TestCleanliness(unittest.TestCase):
    def test_recorded_only_shows_not_graded(self) -> None:
        reading = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")
        ctx = _ctx(cleanliness=(CleanlinessResult(reading),))   # verdict None
        c = ctx["cleanliness"][0]
        self.assertIn("not graded", c["status"])
        self.assertTrue(c["recorded_only"])
        self.assertFalse(c["is_pass"])
        self.assertFalse(c["graded"])

    def test_graded_clean_pass(self) -> None:
        reading = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet")
        verdict = CleanlinessVerdict(passed=True, per_band=(True, True, True))
        ctx = _ctx(cleanliness=(CleanlinessResult(reading, verdict),))
        c = ctx["cleanliness"][0]
        self.assertEqual(c["status"], "PASS")
        self.assertTrue(c["is_pass"])

    def test_invalid_reading_not_graded(self) -> None:
        reading = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet")
        verdict = CleanlinessVerdict(passed=None, note="invalid reading (fault_optical)")
        ctx = _ctx(cleanliness=(CleanlinessResult(reading, verdict),))
        c = ctx["cleanliness"][0]
        self.assertIn("not graded", c["status"])
        self.assertFalse(c["is_pass"])

    def test_as_found_as_left_comparison_present_when_both(self) -> None:
        incoming = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")
        outlet = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet")
        target = CleanlinessVerdict(passed=True, per_band=(True, True, True))
        ctx = _ctx(cleanliness=(CleanlinessResult(incoming), CleanlinessResult(outlet, target)))
        comp = ctx["cleanliness_comparison"]
        self.assertIsNotNone(comp)
        self.assertEqual(comp["as_found"]["sample_point"], "incoming_fluid")
        self.assertEqual(comp["as_left"]["sample_point"], "unit_outlet")

    def test_no_comparison_when_only_one_stage(self) -> None:
        outlet = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet")
        target = CleanlinessVerdict(passed=True, per_band=(True, True, True))
        ctx = _ctx(cleanliness=(CleanlinessResult(outlet, target),))
        self.assertIsNone(ctx["cleanliness_comparison"])


# ---------------------------------------------------------------------------
# certificate_class → template selection + signature seam
# ---------------------------------------------------------------------------

class TestClassAndSignature(unittest.TestCase):
    def test_verification_is_test_report(self) -> None:
        ctx = _ctx(intent="verification")
        self.assertEqual(ctx["certificate_class"], "test_report")
        self.assertEqual(ctx["title"], "Test Report")
        self.assertFalse(ctx["signature"]["required"])

    def test_acceptance_is_certificate_with_signature_seam(self) -> None:
        ctx = _ctx(intent="acceptance", repair_stage="not_applicable")
        self.assertEqual(ctx["certificate_class"], "acceptance_certificate")
        self.assertEqual(ctx["title"], "Acceptance Certificate")
        self.assertTrue(ctx["signature"]["required"])
        self.assertFalse(ctx["signature"]["captured"])           # never fabricated
        self.assertEqual(ctx["signature"]["accountable_party"], "devon")

    def test_validation_is_characterisation_record(self) -> None:
        ctx = _ctx(intent="validation", repair_stage="as_found")
        self.assertEqual(ctx["certificate_class"], "characterisation_record")
        self.assertEqual(ctx["title"], "Characterisation Record")


# ---------------------------------------------------------------------------
# Identity + profile metadata (only what is supplied — nothing invented)
# ---------------------------------------------------------------------------

class TestIdentity(unittest.TestCase):
    def test_identity_fields_carried(self) -> None:
        ctx = _ctx()
        ident = ctx["identity"]
        self.assertEqual(ident["run_id"], "2026-06-02-PC200-8-000123")
        self.assertEqual(ident["dut_serial"], "PC200-8-SN-000123")
        self.assertEqual(ident["po_number"], "PO-44821")
        self.assertEqual(ident["operator"], "devon")

    def test_profile_identity_used_when_supplied(self) -> None:
        ctx = certificate_context(
            _record(),
            profile_identity={"display_name": "Komatsu PC200-8 Main Pump", "part_number": "708-2L-00500"},
        )
        self.assertEqual(ctx["identity"]["model_name"], "Komatsu PC200-8 Main Pump")
        self.assertEqual(ctx["identity"]["part_number"], "708-2L-00500")

    def test_model_name_falls_back_to_profile_id(self) -> None:
        ctx = _ctx()
        self.assertEqual(ctx["identity"]["model_name"], "pc200-8-hpv95")
        self.assertEqual(ctx["identity"]["part_number"], "")


# ---------------------------------------------------------------------------
# render_html — key strings present
# ---------------------------------------------------------------------------

class TestRenderHtml(unittest.TestCase):
    def test_pass_report_strings(self) -> None:
        ctx = certificate_context(_record(), generated_at="2026-06-02T10:00:00+00:00")
        html = render_html(ctx)
        self.assertIn("PASS", html)
        self.assertIn("2026-06-02-PC200-8-000123", html)        # run id
        self.assertIn("pump_flow_pc_destroke_v1", html)         # derived formula id
        self.assertIn("monitored reference", html)              # torque
        self.assertNotIn("TRAINING · NOT FOR PRODUCTION", html)

    def test_training_watermark_present(self) -> None:
        html = render_html(certificate_context(_record(mode="training")))
        self.assertIn("TRAINING", html)
        self.assertIn("watermark", html)

    def test_incomplete_does_not_render_pass_glyph(self) -> None:
        ctx = certificate_context(_record(channels=(_flow(passed=None, graded=True), _torque())))
        html = render_html(ctx)
        self.assertIn("INCOMPLETE", html)
        self.assertNotIn("✓", html)                             # pass glyph gated on is_pass

    def test_acceptance_signature_seam_text(self) -> None:
        ctx = certificate_context(_record(intent="acceptance", repair_stage="not_applicable"))
        html = render_html(ctx)
        self.assertIn("evidence, not an accepted result", html)
        self.assertIn("No signature captured", html)

    def test_cleanliness_iso_and_recorded_only_in_html(self) -> None:
        incoming = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")
        ctx = certificate_context(_record(cleanliness=(CleanlinessResult(incoming),)))
        html = render_html(ctx)
        self.assertIn("22/20/17", html)                         # ISO code
        self.assertIn("not graded", html)


# ---------------------------------------------------------------------------
# render_pdf — smoke test
# ---------------------------------------------------------------------------

class TestRenderPdf(unittest.TestCase):
    def test_pdf_is_non_empty_and_starts_with_magic(self) -> None:
        ctx = certificate_context(_record(), generated_at="2026-06-02T10:00:00+00:00")
        pdf = render_pdf(render_html(ctx))
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1000)


if __name__ == "__main__":
    unittest.main()
