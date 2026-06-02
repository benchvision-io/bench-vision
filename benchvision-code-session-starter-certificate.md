# BenchVision — Claude Code session-starter prompt: Certificate generation

> ✅ COMPLETED 2026-06-02 — do not relaunch. Certificate generation built on branch
> `feat/certificate` (`certificate.py` + `templates/` + `tests/test_certificate.py`;
> suite 77 → 107 green; worked examples in `benchvision-app/sample-certificates/`).
> See `TASKS.md` (Active) and `demo-simulation/decision-log.md` 2026-06-02 for the record.

> Copy everything below the line into a fresh Claude Code session at the repo root
> (`/Users/sueholder/Development/darcsi/benchvision`). Second task in the roadmap, after
> the run record. Written 2026-06-02 in Cowork. Assumes the run-record branch (and its
> cleanliness dependency) is committed and the suite is green.

---

You are continuing **BenchVision** (DAQ software for hydraulic test benches; validation
case is the Komatsu PC200-8 main pump). This session builds **certificate generation** —
the headline deliverable the product exists to produce ("clipboard to PDF, with an audit
trail"). I come from web development; you are the engineer.

## 0. Read these first (in order)

1. `docs/forward-requirements-2026-06-02.md` §2 — your task is certificate generation.
2. `benchvision-app/run_record.py` — the **input**. A certificate renders a `RunRecord`:
   identity, `purpose` (incl. `certificate_class`), `mode`, `ChannelResult`s,
   `cleanliness_results`, and `overall_passed` with its four honest states.
3. `benchvision-app/cleanliness.py` — `CleanlinessReading` / `CleanlinessVerdict`
   (ISO codes, per-band pass/fail, water/temp, sample_point).
4. `docs/test-purpose-schema-sketch.md` — `certificate_class` and what each intent means.
5. `benchvision-app/bench_dashboard.py` — there is already a characteristic-curve plot
   (`save_characteristic_curve`) drawing flow/torque vs pressure with the acceptance band.
   **Reuse it**, don't redraw from scratch.
6. `demo-simulation/decision-log.md` — note especially: live-vs-training certificate
   marking (2026-05-19), custom-formula provenance stamp + version-lock (2026-05-27),
   torque is a **monitored reference, not graded** (2026-06-01).
7. `benchvision-app/pump_profile.py` and the PC200-8 profile (for chart/acceptance data),
   and the project `CLAUDE.md` / `docs/spec.md` if present (spec names Jinja2 + WeasyPrint;
   spec is partially stale — decision log and sketches win on conflict).

## 1. Project disciplines (follow strictly)

- **British English** throughout.
- **No invented quantities.** A provisional or recorded-only value renders *as such*
  ("recorded, not graded"); never fabricate a number or a verdict onto a certified page.
- **Honour the four honest states.** `overall_passed` is PASS / FAIL / NOT GRADED /
  INCOMPLETE. An INCOMPLETE or NOT-GRADED run must **never** render as a clean pass. This
  is the single most important rule of this session — a certificate that overstates a pass
  is the worst output BenchVision can produce.
- **Training mode must be unmistakable.** A `mode == "training"` run must be visibly
  marked non-production (watermark/banner), per the 2026-05-19 decision — never present a
  training run as a real certificate.
- **Reconstructability / provenance.** Show (or carry) the `provenance` of each result
  (measured vs derived) and, for derived values, the **formula id + version**, so a
  historical certificate is reconstructable (version-lock principle).
- **Torque is a monitored reference, not a pass/fail line.** Render it as a plotted
  reference curve; do not draw a torque pass/fail verdict. Flow is the pass/fail truth.
- **Decision-log discipline** (append-only, newest at top) and **ask-devon discipline**
  (check existing transcripts/log before drafting any Devon question; don't re-ask settled
  items). Never overwrite a `-duplicate` file.
- **Conventions:** match `run_record.py` / `cleanliness.py` — `from __future__ import
  annotations`, frozen dataclasses where apt, `__all__`, `unittest` tests under `tests/`.

## 2. Environment

- Work in `benchvision-app/`, project venv `.venv` (Python 3.14). Verify tests with
  `python -m unittest discover -s tests` (pytest is **not** installed; the suite is
  `unittest`-based — do not add pytest).
- **WeasyPrint has system dependencies** (Pango/Cairo). Before building anything, confirm
  WeasyPrint installs into the venv *and* renders a one-line "hello world" HTML→PDF in this
  environment. If it cannot (missing system libs), **stop and report** rather than
  switching libraries unilaterally — the HTML→PDF engine is a decision to make with me.
- Work on a branch (`feat/certificate`), small reviewable commits, keep the suite green
  (currently 77). Never mark done with failing tests.

## 3. Task: certificate generation

Render a certificate **from a `RunRecord`**. Split the work into three layers so the logic
is testable without wrestling a PDF (mirrors how `cleanliness.py` separated pure helpers
from the driver):

1. **`certificate_context(record: RunRecord) -> dict`** — a **pure** function building the
   render model from a `RunRecord`. This is where all the judgement lives and where the
   bulk of the tests point. It must encode:
   - identity: run id, profile id, `dut_serial`, `operator`, `po_number`, UTC timestamps;
   - purpose + `certificate_class` (selects template/title) + the `mode` mark;
   - per-channel results: value, unit, **pass/fail or "monitored reference"** (torque),
     provenance, formula id+version when derived;
   - cleanliness: ISO code(s), per-band pass/fail, **as-found vs as-left comparison** when
     both exist, water/temperature; recorded-only when the verdict is `None`;
   - the **overall state** (PASS / FAIL / NOT GRADED / INCOMPLETE) — surfaced honestly.
2. **`render_html(context: dict) -> str`** — Jinja2 template(s), one per `certificate_class`
   (`acceptance_certificate` / `test_report` / `characterisation_record`). Includes the
   characteristic curve (reuse `bench_dashboard`'s plot, embedded as an image), the
   training watermark when applicable, and the provenance/ALCOA+ footer.
3. **`render_pdf(html: str) -> bytes`** — WeasyPrint HTML→PDF.

### Signature handling (a seam, not a build)
`acceptance_certificate` implies a signature block, but the signature ceremony / step-up
auth and the roles model are **not built yet** (see `docs/profile-authoring-sketch.md`).
Render a clearly-empty **signature placeholder** and carry an `accountable_party` field
that is currently just the operator. Do **not** fabricate a signature. Leave the seam.

### Tests (mirroring house style)
Point most tests at `certificate_context` (pure): each of the four overall states renders
honestly; a training run is marked; torque appears as monitored-reference not pass/fail; a
recorded-only cleanliness result shows "not graded"; as-found/as-left comparison appears
when both present; derived values carry formula id+version; INCOMPLETE never becomes PASS.
For `render_html`, assert key strings are present (verdict word, watermark, ISO code,
formula id). For `render_pdf`, a smoke test: output is non-empty and starts with `%PDF`.

## 4. Explicitly OUT of scope

- The signature ceremony, step-up auth, roles/permissions (leave the seam only).
- Live HAL drivers, the SQLite persistence layer, the sequencer, the Nuxt UI, the
  profile-authoring wizard.
- Any new pump profile or formula. Don't change the engine; only read from it.

If you finish early, improve certificate tests and template polish — not the next roadmap
item.

## 5. Definition of done

- New module(s) + templates + tests under `benchvision-app/`, house conventions.
- `python -m unittest discover -s tests` fully green, including the pre-existing 77.
- A worked example: generate a certificate PDF from a sample `RunRecord` (one PASS live-ish
  run and one training run) and save them so I can eyeball them.
- A top-of-file `decision-log.md` entry: the HTML→PDF engine confirmation, the
  context/render/pdf split, how the four states + training mark + signature seam are
  handled, and any new Devon questions (don't re-ask settled ones).
- Provisional/Devon-dependent items clearly marked, not fabricated.
- A short summary of what you built, what's a seam, and the recommended next step, for
  review back in the planning thread.

Begin by reading §0, confirming WeasyPrint renders in this env, then **propose your design**
(module layout, the context schema, template-per-class approach, how you'll handle the four
states + training mark + signature seam) and wait for my go-ahead before implementing.
After that one checkpoint, implement through to green tests.
