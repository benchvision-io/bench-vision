"""
certificate.py

BenchVision — certificate generation: render a :class:`RunRecord` to a PDF
certificate. The headline deliverable BenchVision exists to produce —
"clipboard to PDF, with an audit trail".

Three layers, split so the *judgement* is testable without wrestling a PDF (mirrors
how ``cleanliness.py`` separated pure helpers from the driver):

  * :func:`certificate_context` ``(record) -> dict`` — **pure**. All the honesty and
    judgement live here; the bulk of the tests point at it. No Jinja, no matplotlib,
    no I/O.
  * :func:`render_html` ``(context) -> str`` — Jinja2; one template per
    ``certificate_class`` (acceptance_certificate / test_report / characterisation_record),
    each extending ``templates/base.html``.
  * :func:`render_pdf` ``(html) -> bytes`` — WeasyPrint HTML → PDF.
  * :func:`generate_certificate_pdf` — the composer: builds the characteristic-curve
    image, injects it, renders HTML, renders PDF.

**The single most important rule** (session brief §1): an INCOMPLETE or NOT-GRADED run
must NEVER render as a clean pass. ``overall.is_pass`` is the ONE flag that unlocks any
pass-styled presentation, and it is True only when the run verdict is *exactly* PASS.
Every other state surfaces its own word prominently.

Disciplines honoured (each load-bearing):

  * **Four honest states** surfaced verbatim from ``RunRecord.verdict`` (run_record.py):
    PASS / FAIL / NOT GRADED / INCOMPLETE.
  * **Training mark** (decision-log 2026-05-19): a ``mode == "training"`` run is
    watermarked non-production; it can never read as a real certificate.
  * **Provenance / version-lock** (decision-log 2026-05-27): each derived value carries
    its formula id+version so a historical certificate is reconstructable.
  * **Torque is a monitored reference, not graded** (decision-log 2026-06-01): rendered
    as "monitored reference", never a pass/fail verdict. Flow is the pass/fail truth.
  * **Signature seam** (session brief): ``acceptance_certificate`` implies a signature
    block, but the ceremony / step-up auth / roles model are NOT built. We render a
    clearly-empty placeholder and carry ``accountable_party`` (currently the operator).
    No fabricated signature.
  * **No invented quantities**: a provisional / recorded-only value renders as such;
    nothing is fabricated onto a certified page.

Brand: the certificate is a **Document-theme** output (bench-vision-design-system.md
§3/§4: white A4, navy ``#1B3A5C`` + blue ``#2E75B6``, universal pass/fail colours §5).

British English throughout. Python 3.12+ (``from __future__ import annotations``).
"""

from __future__ import annotations

import base64
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from run_record import Provenance, RunRecord

#: Bumped if the render-model (context) shape changes incompatibly.
CERTIFICATE_SCHEMA_VERSION = "1.0"

#: Where the Jinja2 templates live.
TEMPLATES_DIR = Path(__file__).parent / "templates"

# certificate_class → (title, subtitle, template filename)
_CLASS_TITLE: dict[str, str] = {
    "acceptance_certificate": "Acceptance Certificate",
    "test_report": "Test Report",
    "characterisation_record": "Characterisation Record",
}
_CLASS_SUBTITLE: dict[str, str] = {
    "acceptance_certificate": "Hydraulic pump acceptance — graded against the model profile",
    "test_report": "Hydraulic pump verification — graded against the model profile",
    "characterisation_record": "Hydraulic pump characterisation — data, not a verdict",
}
_CLASS_TEMPLATE: dict[str, str] = {
    "acceptance_certificate": "acceptance_certificate.html",
    "test_report": "test_report.html",
    "characterisation_record": "characterisation_record.html",
}

# Verdict word → CSS state class (drives the banner colour; green ONLY for PASS).
_STATE_CSS: dict[str, str] = {
    "PASS": "pass",
    "FAIL": "fail",
    "NOT GRADED": "notgraded",
    "INCOMPLETE": "incomplete",
}

_SAMPLE_LABELS: dict[str, str] = {
    "incoming_fluid": "Incoming fluid",
    "unit_outlet": "Unit outlet",
    "rig_supply": "Rig supply",
}


# ---------------------------------------------------------------------------
# Small pure helpers
# ---------------------------------------------------------------------------

def _fmt(value: float) -> str:
    """Format a measured value compactly (no trailing-zero noise): 148.5, 627, 12.0."""
    return f"{value:g}"


def _channel_status(result: Any) -> str:
    """The honest one-word/phrase status for a channel result.

    Mirrors ``ChannelResult``'s three legitimate states exactly:
      * monitored reference (``graded=False``, e.g. torque) — never a verdict;
      * not evaluated (``graded=True`` but ``passed is None``) — meant to grade, could not;
      * PASS / FAIL otherwise.
    """
    if not result.graded:
        return "monitored reference"
    if result.passed is None:
        return "not evaluated"
    return "PASS" if result.passed else "FAIL"


def _channel_view(result: Any) -> dict[str, Any]:
    status = _channel_status(result)
    return {
        "channel": result.channel,
        "label": result.channel.replace("_", " ").title(),
        "value": result.value,
        "value_display": _fmt(result.value),
        "unit": result.unit,
        "pressure_bar": result.pressure_bar,
        "pressure_display": (None if result.pressure_bar is None else _fmt(result.pressure_bar)),
        "status": status,
        "graded": result.graded,
        "is_pass": status == "PASS",
        "is_fail": status == "FAIL",
        "is_reference": not result.graded,
        "not_evaluated": result.graded and result.passed is None,
        "provenance": result.provenance,
        "is_derived": result.provenance == Provenance.DERIVED,
        "is_measured": result.provenance == Provenance.MEASURED,
        "formula": result.formula,
    }


def _cleanliness_view(result: Any) -> dict[str, Any]:
    reading = result.reading
    verdict = result.verdict
    if verdict is None:                         # recorded-only — no confirmed target
        status, is_pass, is_fail, graded = "recorded only — not graded", False, False, False
    elif verdict.passed is None:                # meant to grade but reading invalid
        status, is_pass, is_fail, graded = "not graded (invalid reading)", False, False, True
    else:
        status = "PASS" if verdict.passed else "FAIL"
        is_pass, is_fail, graded = bool(verdict.passed), not verdict.passed, True
    return {
        "sample_point": reading.sample_point,
        "sample_point_label": _SAMPLE_LABELS.get(reading.sample_point, reading.sample_point),
        # incoming fluid is the as-found contamination evidence; the unit/rig is as-left.
        "stage": "as-found" if reading.sample_point == "incoming_fluid" else "as-left",
        "iso_code": reading.iso_string,
        "standard": reading.standard,
        "per_band": list(verdict.per_band) if verdict is not None else [],
        "water_rh_pct": reading.water_rh_pct,
        "temperature_c": reading.temperature_c,
        "reference": reading.reference,
        "status": status,
        "is_pass": is_pass,
        "is_fail": is_fail,
        "graded": graded,
        "recorded_only": verdict is None,
        "note": "" if verdict is None else verdict.note,
    }


def _cleanliness_comparison(views: list[dict[str, Any]]) -> dict[str, Any] | None:
    """An as-found vs as-left comparison, only when BOTH stages are present.

    (Devon's incoming-fluid reading is the as-found contamination evidence; the unit
    outlet is the as-left. The comparison turns a failure into evidence —
    test-purpose sketch §7.)
    """
    as_found = next((v for v in views if v["stage"] == "as-found"), None)
    as_left = next((v for v in views if v["stage"] == "as-left"), None)
    if as_found is not None and as_left is not None:
        return {"as_found": as_found, "as_left": as_left}
    return None


# ---------------------------------------------------------------------------
# Layer 1 — the pure render model (where the judgement lives)
# ---------------------------------------------------------------------------

def certificate_context(
    record: RunRecord,
    *,
    generated_at: str | None = None,
    chart_png_data_uri: str | None = None,
    profile_identity: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the render model (a plain dict) from a :class:`RunRecord`. PURE — no Jinja,
    no matplotlib, no I/O — so it is cheap to test and is where every honesty rule is
    encoded.

    ``generated_at`` (a UTC ISO string) and ``chart_png_data_uri`` are injected by the
    caller, never computed here — the brief forbids ``Date.now`` inside the render path,
    and plotting is not judgement. ``profile_identity`` is the optional pump-model
    metadata (manufacturer, part number) the record references but does not itself
    carry; only what is supplied is rendered (no fabricated test-method numbers).
    """
    verdict = record.verdict
    state = verdict.summary                      # PASS | FAIL | NOT GRADED | INCOMPLETE
    purpose = record.purpose
    cert_class = purpose.certificate_class

    channels = [_channel_view(r) for r in record.channel_results]
    cleanliness = [_cleanliness_view(c) for c in record.cleanliness_results]

    return {
        "schema_version": CERTIFICATE_SCHEMA_VERSION,
        "certificate_class": cert_class,
        "title": _CLASS_TITLE.get(cert_class, "Test Record"),
        "subtitle": _CLASS_SUBTITLE.get(cert_class, ""),
        # --- mode / training mark (decision-log 2026-05-19) -------------------
        "mode": record.mode,
        "is_training": record.mode == "training",
        "is_live": record.mode == "live",
        # --- identity --------------------------------------------------------
        "identity": {
            "run_id": record.id,
            "profile": record.profile,
            "dut_serial": record.dut_serial,
            "operator": record.operator,
            "po_number": record.po_number,
            "started_at": record.started_at,
            "finished_at": record.finished_at,
            "model_name": (profile_identity or {}).get("display_name", record.profile),
            "manufacturer": (profile_identity or {}).get("manufacturer", ""),
            "part_number": (profile_identity or {}).get("part_number", ""),
        },
        # --- purpose ---------------------------------------------------------
        "purpose": {
            "intent": purpose.intent,
            "repair_stage": purpose.repair_stage,
            "context": purpose.context,
            "grades_pass_fail": purpose.grades_pass_fail,
            "signoff_required": purpose.signoff_required,
        },
        # --- the verdict, surfaced honestly ----------------------------------
        "overall": {
            "state": state,
            "note": verdict.note,
            # is_pass is the ONLY flag that unlocks pass styling. Never derived from
            # anything but an exact PASS — an INCOMPLETE/NOT GRADED can never set it.
            "is_pass": state == "PASS",
            "is_fail": state == "FAIL",
            "not_graded": state == "NOT GRADED",
            "incomplete": state == "INCOMPLETE",
            "needs_attention": state in {"FAIL", "INCOMPLETE"},
            "state_css": _STATE_CSS.get(state, "notgraded"),
        },
        # --- results ---------------------------------------------------------
        "channels": channels,
        "cleanliness": cleanliness,
        "cleanliness_comparison": _cleanliness_comparison(cleanliness),
        # --- the signature SEAM (not built — see module docstring) -----------
        "signature": {
            "required": purpose.signoff_required,
            "accountable_party": record.operator,
            "captured": False,
            "note": (
                "Signature ceremony not yet implemented — this certificate is "
                "evidence, not an accepted result."
                if purpose.signoff_required else ""
            ),
        },
        # --- supporting ------------------------------------------------------
        "chart_png": chart_png_data_uri,
        "notes": record.notes,
        "generated_at": generated_at,
        "provenance_note": (
            "Derived values carry their formula id and version so this certificate is "
            "reconstructable. Timestamps are contemporaneous UTC (ALCOA+)."
        ),
    }


# ---------------------------------------------------------------------------
# Layer 2 — HTML (Jinja2, one template per certificate_class)
# ---------------------------------------------------------------------------

def _jinja_env():
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_html(context: Mapping[str, Any]) -> str:
    """Render the certificate HTML, selecting the template by ``certificate_class``."""
    cert_class = context["certificate_class"]
    template_name = _CLASS_TEMPLATE.get(cert_class)
    if template_name is None:
        raise ValueError(f"no template for certificate_class {cert_class!r}")
    template = _jinja_env().get_template(template_name)
    return template.render(**context)


# ---------------------------------------------------------------------------
# Layer 3 — PDF (WeasyPrint)
# ---------------------------------------------------------------------------

def render_pdf(html: str, *, base_url: str | None = None) -> bytes:
    """Render certificate HTML to PDF bytes via WeasyPrint."""
    from weasyprint import HTML

    if base_url is None:
        base_url = str(TEMPLATES_DIR)
    return HTML(string=html, base_url=base_url).write_pdf()


# ---------------------------------------------------------------------------
# The characteristic-curve image (reuses the dashboard's plot — drawn once)
# ---------------------------------------------------------------------------

def characteristic_curve_png(record: RunRecord, profile: Any, registry: Any) -> bytes:
    """
    Render the run's characteristic curve as PNG bytes, reusing
    ``bench_dashboard.build_characteristic_figure`` (the shared plot core) rather than
    redrawing it. The run's flow/torque operating points are scattered over the
    profile's acceptance band and the formula-engine reference lines.
    """
    import io

    import matplotlib
    matplotlib.use("Agg")  # headless — no display needed to produce the image
    import matplotlib.pyplot as plt

    from bench_dashboard import build_characteristic_figure

    flow_points = [
        (r.pressure_bar, r.value)
        for r in record.channel_results
        if r.channel == "flow" and r.pressure_bar is not None
    ]
    torque_points = [
        (r.pressure_bar, r.value)
        for r in record.channel_results
        if r.channel == "torque" and r.pressure_bar is not None
    ]
    fig = build_characteristic_figure(
        profile, registry,
        flow_points=flow_points,
        torque_points=torque_points,
        scatter_size=34.0,
        scatter_alpha=0.85,
    )
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()


def characteristic_curve_data_uri(record: RunRecord, profile: Any, registry: Any) -> str:
    """The characteristic curve as a ``data:image/png;base64,…`` URI for embedding."""
    png = characteristic_curve_png(record, profile, registry)
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


# ---------------------------------------------------------------------------
# The composer — RunRecord → PDF bytes
# ---------------------------------------------------------------------------

def generate_certificate_pdf(
    record: RunRecord,
    profile: Any = None,
    registry: Any = None,
    *,
    generated_at: str | None = None,
) -> bytes:
    """
    End-to-end: build the chart (if a profile+registry are supplied), build the
    context, render HTML, render PDF. When no profile/registry is given the chart is
    simply omitted — the certificate still renders honestly without it.
    """
    from run_record import utc_now_iso

    if generated_at is None:
        generated_at = utc_now_iso()

    chart = None
    if profile is not None and registry is not None:
        chart = characteristic_curve_data_uri(record, profile, registry)

    context = certificate_context(
        record,
        generated_at=generated_at,
        chart_png_data_uri=chart,
        profile_identity=(profile.identity if profile is not None else None),
    )
    return render_pdf(render_html(context))


__all__ = [
    "CERTIFICATE_SCHEMA_VERSION",
    "TEMPLATES_DIR",
    "certificate_context",
    "render_html",
    "render_pdf",
    "characteristic_curve_png",
    "characteristic_curve_data_uri",
    "generate_certificate_pdf",
]
