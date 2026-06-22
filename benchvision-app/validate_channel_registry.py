"""
validate_channel_registry.py

A quick integrity check for a bench channel-registry TOML
(e.g. profiles/devon-bench-channels.toml). Confirms the structural invariants
hold and surfaces the two things an operator needs to see before a graded run:
expired calibrations and channels still carrying `tbc` placeholders.

Not the full cal-expiry sequencer guard (which, per the 2026-06-15 policy, lets the
operator acknowledge an expired cal and proceed, recording that no certificate can
be issued for that run) — this is the standalone, read-only sanity check it builds
on. Run it after editing the registry, or as a pre-flight report.

Usage:  python validate_channel_registry.py [path-to-registry.toml]
British English throughout. Python 3.11+ (tomllib) or `pip install tomli`.
"""

from __future__ import annotations

import sys
from datetime import date

try:
    import tomllib as toml
except ModuleNotFoundError:  # pragma: no cover
    import tomli as toml  # type: ignore

ALLOWED_UNITS = {"bar", "L/min", "kW", "RPM"}
DEFAULT_PATH = "profiles/devon-bench-channels.toml"


def validate(path: str) -> int:
    with open(path, "rb") as fh:
        reg = toml.load(fh)

    problems: list[str] = []        # structural errors — fix before use (exit 1)
    cal_warnings: list[str] = []    # expired cals — acknowledge to run; block cert later
    notes: list[str] = []           # informational (open items / tbc)
    today = date.today()

    channels = reg.get("channel", {})
    declared = reg.get("meta", {}).get("channel_count")
    if declared is not None and declared != len(channels):
        problems.append(f"meta.channel_count={declared} but {len(channels)} channels defined")

    safety = reg.get("safety", {})

    for name, ch in sorted(channels.items()):
        unit = ch.get("unit")
        if unit not in ALLOWED_UNITS:
            problems.append(f"{name}: unit {unit!r} not in convention set {sorted(ALLOWED_UNITS)}")

        rng = ch.get("eng_range")
        if not (isinstance(rng, list) and len(rng) == 2 and rng[0] < rng[1]):
            problems.append(f"{name}: eng_range {rng!r} is not [min, max] with min < max")

        # A de-energisation gate must have a safe band to test against.
        if ch.get("is_deenergisation_gate"):
            kind = "speed" if unit == "RPM" else "pressure"
            key = "speed_safe_below_rpm" if kind == "speed" else "pressure_safe_below_bar"
            if key not in safety:
                problems.append(f"{name}: gate channel but [safety].{key} is missing")

        # Calibration expiry. POLICY (Pix 2026-06-15): an expired cal does NOT
        # block the run — the operator may proceed after an explicit
        # acknowledgement that states the expiry and recommends recalibration.
        # The real consequence is that a certificate cannot be issued for that
        # run (relevant once the cert rejoins the product). So an expired cal is
        # a WARNING-to-acknowledge here, never a structural error.
        cal = ch.get("calibration", {})
        due = cal.get("cal_due")
        if due:
            try:
                if date.fromisoformat(due) < today:
                    days = (today - date.fromisoformat(due)).days
                    cal_warnings.append(
                        f"{name}: calibration expired {days} day(s) ago (due {due}) — "
                        f"run allowed with operator acknowledgement; no certificate issuable until recal"
                    )
            except ValueError:
                notes.append(f"{name}: cal_due {due!r} not ISO yyyy-mm-dd — cannot check expiry")

        # Outstanding placeholders.
        sensor = ch.get("sensor", {})
        if ch.get("signal") == "tbc":
            notes.append(f"{name}: signal type still tbc")
        if sensor.get("manufacturer") == "tbc":
            notes.append(f"{name}: sensor identity still tbc")

    # Report --------------------------------------------------------------
    print(f"Registry: {path}")
    print(f"  schema {reg.get('schema_version','?')} | {len(channels)} channels | checked {today.isoformat()}")
    gates = [c for c, ch in channels.items() if ch.get("is_deenergisation_gate")]
    print(f"  de-energisation gates: {', '.join(sorted(gates)) or '(none)'}")

    if problems:
        print(f"\n  ✗ {len(problems)} structural error(s) — fix before use:")
        for p in problems:
            print(f"      - {p}")
    else:
        print("\n  ✓ no structural errors")

    if cal_warnings:
        print(f"\n  ⚠ {len(cal_warnings)} calibration warning(s) — operator acknowledges; run NOT blocked, cert is:")
        for w in cal_warnings:
            print(f"      - {w}")

    if notes:
        print(f"\n  • {len(notes)} note(s) (open items, not blocking):")
        for n in notes:
            print(f"      - {n}")

    return 1 if problems else 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    raise SystemExit(validate(target))
