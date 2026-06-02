"""
Unit tests for the test-run record (``run_record.py``).

Run:  python3 -m unittest discover -s tests
(or:  python3 -m unittest tests.test_run_record)

Hardware-free. British English throughout. Mirrors the style of
``tests/test_cleanliness.py`` / ``tests/test_formula_registry.py``.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cleanliness import CleanlinessLimit, CleanlinessReading, CleanlinessVerdict  # noqa: E402
from run_record import (  # noqa: E402
    ChannelResult,
    CleanlinessResult,
    JsonFileRunRecordRepository,
    Provenance,
    RunRecord,
    TestPurpose,
    utc_now_iso,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _purpose(intent: str = "verification", **kw: str) -> TestPurpose:
    return TestPurpose(intent=intent, **kw)


def _record(**overrides: object) -> RunRecord:
    base: dict[str, object] = dict(
        id="2026-06-02-PC200-8-000001",
        profile="pc200-8-hpv95",
        dut_serial="PC200-8-SN-PROVISIONAL",
        operator="devon",
        po_number="PO-PROVISIONAL",
        purpose=_purpose("verification", repair_stage="as_left", context="repair_overhaul"),
    )
    base.update(overrides)
    return RunRecord(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# TestPurpose — validation
# ---------------------------------------------------------------------------

class TestPurposeValidation(unittest.TestCase):
    def test_rejects_unknown_intent(self) -> None:
        with self.assertRaises(ValueError):
            TestPurpose(intent="bogus")

    def test_rejects_unknown_repair_stage(self) -> None:
        with self.assertRaises(ValueError):
            TestPurpose(intent="verification", repair_stage="midway")

    def test_context_is_free_text_not_validated(self) -> None:
        # Deliberately open (sketch §2 / open-question 3) — any string is accepted.
        self.assertEqual(TestPurpose(intent="verification", context="komatsu_oem").context,
                         "komatsu_oem")

    def test_defaults(self) -> None:
        p = TestPurpose(intent="validation")
        self.assertEqual(p.repair_stage, "not_applicable")
        self.assertEqual(p.context, "unspecified")


# ---------------------------------------------------------------------------
# TestPurpose — each derived property
# ---------------------------------------------------------------------------

class TestPurposeDerivedProperties(unittest.TestCase):
    def test_deviations_expected(self) -> None:
        self.assertTrue(TestPurpose("validation").deviations_expected)         # validation
        self.assertTrue(TestPurpose("verification", "as_found").deviations_expected)  # any as_found
        self.assertFalse(TestPurpose("verification", "as_left").deviations_expected)
        self.assertFalse(TestPurpose("acceptance").deviations_expected)

    def test_grades_pass_fail(self) -> None:
        self.assertTrue(TestPurpose("verification").grades_pass_fail)
        self.assertTrue(TestPurpose("acceptance").grades_pass_fail)
        self.assertFalse(TestPurpose("validation").grades_pass_fail)
        self.assertFalse(TestPurpose("qualification").grades_pass_fail)

    def test_signoff_required(self) -> None:
        self.assertTrue(TestPurpose("acceptance").signoff_required)
        self.assertFalse(TestPurpose("verification").signoff_required)

    def test_certificate_class(self) -> None:
        self.assertEqual(TestPurpose("acceptance").certificate_class, "acceptance_certificate")
        self.assertEqual(TestPurpose("verification").certificate_class, "test_report")
        self.assertEqual(TestPurpose("qualification").certificate_class, "test_report")
        self.assertEqual(TestPurpose("validation").certificate_class, "characterisation_record")


# ---------------------------------------------------------------------------
# ChannelResult — validation + the graded/monitored distinction
# ---------------------------------------------------------------------------

class TestChannelResult(unittest.TestCase):
    def test_rejects_unknown_provenance(self) -> None:
        with self.assertRaises(ValueError):
            ChannelResult("flow", 1.0, "L/min", provenance="guessed")

    def test_monitored_reference_must_have_passed_none(self) -> None:
        # torque is a monitored reference (graded=False); a verdict on it is a bug.
        with self.assertRaises(ValueError):
            ChannelResult("torque", 627.0, "Nm", graded=False, passed=True)

    def test_monitored_reference_with_none_is_fine(self) -> None:
        r = ChannelResult("torque", 627.0, "Nm", graded=False, passed=None)
        self.assertFalse(r.graded)


# ---------------------------------------------------------------------------
# RunRecord — construction + timestamp discipline
# ---------------------------------------------------------------------------

class TestRunRecordConstruction(unittest.TestCase):
    def test_minimal_construction(self) -> None:
        rec = _record()
        self.assertEqual(rec.profile, "pc200-8-hpv95")
        self.assertEqual(rec.channel_results, ())
        self.assertEqual(rec.mode, "training")

    def test_rejects_unknown_mode(self) -> None:
        with self.assertRaises(ValueError):
            _record(mode="hybrid")

    def test_rejects_naive_timestamp(self) -> None:
        with self.assertRaises(ValueError):
            _record(started_at="2026-06-02T11:00:00")        # no tzinfo

    def test_rejects_non_utc_timestamp(self) -> None:
        with self.assertRaises(ValueError):
            _record(started_at="2026-06-02T11:00:00+02:00")  # tz-aware but not UTC

    def test_accepts_utc_timestamp(self) -> None:
        rec = _record(started_at="2026-06-02T11:00:00+00:00", finished_at="2026-06-02T11:05:00Z")
        self.assertEqual(rec.started_at, "2026-06-02T11:00:00+00:00")

    def test_utc_now_iso_is_tz_aware_and_accepted(self) -> None:
        # The helper's output must satisfy the record's own validation.
        rec = _record(started_at=utc_now_iso())
        self.assertIn("+00:00", rec.started_at or "")

    def test_list_results_coerced_to_tuple(self) -> None:
        rec = _record(channel_results=[ChannelResult("flow", 1.0, "L/min", passed=True)])
        self.assertIsInstance(rec.channel_results, tuple)


# ---------------------------------------------------------------------------
# RunRecord.verdict — the load-bearing distinction
# ---------------------------------------------------------------------------

class TestRunVerdict(unittest.TestCase):
    def _flow(self, passed: bool | None, graded: bool = True) -> ChannelResult:
        return ChannelResult("flow", 148.5, "L/min", pressure_bar=236.0,
                             passed=passed, graded=graded, provenance=Provenance.DERIVED,
                             formula="pump_flow_pc_destroke_v1")

    def _torque_reference(self) -> ChannelResult:
        return ChannelResult("torque", 627.0, "Nm", pressure_bar=236.0, graded=False,
                             provenance=Provenance.DERIVED)

    def test_characterisation_purpose_is_not_graded(self) -> None:
        rec = _record(purpose=_purpose("validation"),
                      channel_results=(self._flow(True),))
        v = rec.verdict
        self.assertFalse(v.graded)
        self.assertIsNone(v.passed)
        self.assertEqual(v.summary, "NOT GRADED")

    def test_pass_when_all_graded_results_pass(self) -> None:
        rec = _record(channel_results=(self._flow(True), self._torque_reference()))
        self.assertTrue(rec.overall_passed)
        self.assertEqual(rec.verdict.summary, "PASS")

    def test_fail_when_a_graded_result_fails(self) -> None:
        rec = _record(channel_results=(self._flow(False), self._torque_reference()))
        self.assertFalse(rec.overall_passed)
        self.assertEqual(rec.verdict.summary, "FAIL")

    def test_monitored_reference_alone_is_not_graded(self) -> None:
        # Only a monitored reference present → nothing meant to grade → NOT GRADED.
        rec = _record(channel_results=(self._torque_reference(),))
        self.assertFalse(rec.verdict.graded)
        self.assertIsNone(rec.overall_passed)

    def test_meant_to_grade_but_could_not_forces_incomplete(self) -> None:
        # THE distinction: a graded channel whose reading could not be evaluated
        # (passed=None) must NOT be excluded — it forces an incomplete (None) verdict
        # with a note, so a silently-wrong pass cannot slip through.
        rec = _record(channel_results=(self._flow(passed=None), self._torque_reference()))
        v = rec.verdict
        self.assertTrue(v.graded)
        self.assertIsNone(v.passed)
        self.assertEqual(v.summary, "INCOMPLETE")
        self.assertIn("flow", v.note)

    def test_one_ungradeable_among_passes_still_incomplete(self) -> None:
        # A genuine pass must not mask an ungradeable expected channel.
        flow_pass = self._flow(True)
        flow_unknown = ChannelResult("flow_second_section", 0.0, "L/min", passed=None,
                                     provenance=Provenance.MEASURED)
        rec = _record(channel_results=(flow_pass, flow_unknown))
        self.assertIsNone(rec.overall_passed)
        self.assertEqual(rec.verdict.summary, "INCOMPLETE")


# ---------------------------------------------------------------------------
# Cleanliness wiring — recorded-only excluded vs graded counted vs ungradeable
# ---------------------------------------------------------------------------

class TestCleanlinessWiring(unittest.TestCase):
    def setUp(self) -> None:
        self.limit = CleanlinessLimit(target=(18, 16, 13))
        self.incoming = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")
        self.outlet = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet")

    def test_as_found_recorded_only_is_excluded_from_gate(self) -> None:
        # Incoming (as-found) reading with NO verdict = recorded-only (target unconfirmed):
        # legitimately excluded. The as-left graded pass should stand alone as PASS.
        as_left_verdict = self.limit.grade(self.outlet)
        rec = _record(
            purpose=_purpose("verification", repair_stage="as_left"),
            cleanliness_results=(
                CleanlinessResult(self.incoming),                 # recorded-only → excluded
                CleanlinessResult(self.outlet, as_left_verdict),  # graded → counts
            ),
        )
        self.assertTrue(as_left_verdict.passed)
        self.assertTrue(rec.overall_passed)
        self.assertEqual(rec.verdict.summary, "PASS")

    def test_graded_cleanliness_fail_fails_the_run(self) -> None:
        verdict = self.limit.grade(self.incoming)   # 22/20/17 vs 18/16/13 → fail
        rec = _record(cleanliness_results=(CleanlinessResult(self.incoming, verdict),))
        self.assertFalse(verdict.passed)
        self.assertFalse(rec.overall_passed)

    def test_invalid_graded_cleanliness_forces_incomplete(self) -> None:
        # A reading meant to grade but invalid (e.g. ICM fault) → verdict.passed is None.
        # That is "meant to grade but couldn't" — must force INCOMPLETE, not be excluded.
        invalid = CleanlinessReading(iso_code=(17, 15, 12), sample_point="unit_outlet",
                                     status="fault_optical")
        verdict = self.limit.grade(invalid)
        self.assertIsNone(verdict.passed)               # cleanliness.py returns None-verdict
        rec = _record(cleanliness_results=(CleanlinessResult(invalid, verdict),))
        v = rec.verdict
        self.assertTrue(v.graded)
        self.assertIsNone(v.passed)
        self.assertEqual(v.summary, "INCOMPLETE")
        self.assertIn("cleanliness", v.note)


# ---------------------------------------------------------------------------
# Serialisation — JSON round-trip + repository
# ---------------------------------------------------------------------------

class TestSerialisation(unittest.TestCase):
    def _full_record(self) -> RunRecord:
        limit = CleanlinessLimit(target=(18, 16, 13))
        outlet = CleanlinessReading(
            iso_code=(17, 15, 12), extra_codes=(11, 9, 7), counts_per_100ml=(70000, 0, 0),
            temperature_c=44.0, water_rh_pct=12.0, flow_ml_min=250.0,
            sample_point="unit_outlet", reference="PO-PROVISIONAL",
        )
        incoming = CleanlinessReading(iso_code=(22, 20, 17), sample_point="incoming_fluid")
        return _record(
            mode="training",
            started_at="2026-06-02T11:00:00+00:00",
            finished_at="2026-06-02T11:05:00+00:00",
            channel_results=(
                ChannelResult("flow", 148.5, "L/min", pressure_bar=236.0, passed=True,
                              provenance=Provenance.DERIVED, formula="pump_flow_pc_destroke_v1"),
                ChannelResult("torque", 627.0, "Nm", pressure_bar=236.0, graded=False,
                              provenance=Provenance.DERIVED),
            ),
            cleanliness_results=(
                CleanlinessResult(incoming),
                CleanlinessResult(outlet, limit.grade(outlet)),
            ),
            notes="round-trip fixture",
        )

    def test_json_round_trip_is_equal(self) -> None:
        rec = self._full_record()
        restored = RunRecord.from_json(rec.to_json())
        self.assertEqual(restored, rec)

    def test_round_trip_preserves_tuple_types(self) -> None:
        rec = self._full_record()
        restored = RunRecord.from_json(rec.to_json())
        self.assertIsInstance(restored.channel_results, tuple)
        self.assertIsInstance(restored.cleanliness_results[1].reading.iso_code, tuple)
        # verdict preserved through the round-trip
        self.assertEqual(restored.cleanliness_results[1].verdict, rec.cleanliness_results[1].verdict)

    def test_recorded_only_verdict_survives_as_none(self) -> None:
        rec = self._full_record()
        restored = RunRecord.from_json(rec.to_json())
        self.assertIsNone(restored.cleanliness_results[0].verdict)  # incoming = recorded-only

    def test_repository_save_and_load(self) -> None:
        import tempfile

        rec = self._full_record()
        with tempfile.TemporaryDirectory() as tmp:
            repo = JsonFileRunRecordRepository(tmp)
            repo.save(rec)
            self.assertEqual(repo.load(rec.id), rec)
            self.assertTrue((Path(tmp) / f"{rec.id}.json").exists())


if __name__ == "__main__":
    unittest.main()
