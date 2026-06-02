# Tasks

> **Single source of truth for BenchVision live status** — what's open, done, and next.
> Stable identity/architecture facts live in `CLAUDE.md`; anything that changes lives here.
> Per `CLAUDE.md` §8A: finishing a task updates this file + `demo-simulation/decision-log.md`
> + retires its session-starter — and nothing else duplicates status.

## Build status — app & deliverables

_Deliverable-level snapshot. Moved here from CLAUDE.md §2's status table 2026-06-01 so that
build status has exactly one home._

- [x] **HTML prototypes** (portal, HMI, overview, roadmap, for-devon) — live on Vercel
- [x] **Design system v1.1** — complete
- [x] **Hydraulic bench proposal v5** — complete
- [x] **Hydraulic bench questionnaire v1** — complete
- [x] **Business Setup Reference v1.5** (TestVision-era) — complete (Apr 2026); superseded by the DARCSI rebrand → new-version status is the .docx-rework item under Active
- [x] **Formula engine + sensor simulator + live dashboard** — built, unit-tested, profile-driven, validated against the PC200-8 chart (`benchvision-app/`; detail in the Formula-engine items under Active)
- [ ] **Real DAQ I/O, HMI, safety layer, report generation** — Milestone 1, not started
- [ ] **Formal spec** (`docs/spec.md`, `demo-simulation/spec.md`) — drafted, evolving
- [ ] **Architecture diagrams** (`docs/architecture.md`) — discovery phase

## Active

- [x] **Run record (P0)** DONE 2026-06-02. Built `benchvision-app/run_record.py` + `tests/test_run_record.py` (suite 46 → 77, green). The per-run spine: `TestPurpose` (intent/repair_stage/context + the four derived properties) and a frozen `RunRecord` joining profile-id / `dut_serial` / operator / `po_number` / purpose / mode (training|live) / UTC timestamps / results. Results are **source-agnostic** (value + pass/fail + provenance) so one record serves a simulated *and* a live run; cleanliness types reused from `cleanliness.py`. Verdict keeps "not meant to grade" (monitored reference, recorded-only cleanliness → excluded) distinct from "meant to grade but couldn't" (invalid reading → forces INCOMPLETE, never a silent pass). Serialised as a **JSON sidecar** (run data, not config; `tomllib` is read-only); `RunRecordRepository` Protocol left as the SQLite seam (SQLite not built). See decision-log 2026-06-02. **Next: certificate generation.**
- [x] **Formula engine — refactor TorqueChannel + add PowerChannel onto the engine** DONE 2026-05-30. All four steps complete: rated_rpm confirmed 2000 in profile (SpeedChannel now reads it, was hardcoded 1000); TorqueChannel derives from live flow (`absorption_torque_from_flow_v1`, plateau emerges, fixed Vg/target dropped); PowerChannel added (`power_from_flow_pressure_v1`); dashboard characteristic curve + acceptance band now profile/registry-driven (hard-coded `245−0.5P` / `P×95/62.8` / ±15 band removed). 16 unit tests pass; validation in `validate_flow_refactor.py`; overlays `demo-simulation/{flow_refactor,torque_power}_validation.png`. See decision-log 2026-05-30.
- [x] **Formula engine — calibrate the torque plateau** RESOLVED 2026-06-01. Printed absorption-torque callouts read from the clean Fig.1 PDF: nominal **plateaus at ~627 Nm** (not ~590 — that was an eyeball read one gridline low); the ~629 trace is the nominal curve, not a limit line. Added an empirical `[efficiency]` per-pressure curve to the profile (η ~0.85 at the knee → ~0.74 at 400 bar) so `absorption_torque_from_flow_v1`, fed live flow, tracks the printed nominal to <2.5% across 0–400 bar. No formula version bump (function unchanged; only the η it's fed). See decision-log 2026-06-01 + `pc200-8-chart-digitised-values.md` §5. Deferred companion: couple derived torque to live speed so the shaft-slip fault drops torque realistically (still modelled at rated speed).
- [x] **Transcribe the printed FLOW limit lines** DONE 2026-06-01 (was Devon open-point (c)). Dotted "Upper limit (Reference value)" + solid "Lower limit" read off Fig.1 and now populate `[acceptance.flow]`, replacing the interpolated widths above the PC cut-in. All seven callouts MPa↔{kgf/cm²} cross-checked (one ~1% loose callout documented); `test_flow_band_tracks_chart_limits` added; overlay refreshed; independently re-verified against the chart 2026-06-01. See decision-log 2026-06-01.
- [x] **Torque pass/fail — graded channel or monitored reference?** DECIDED 2026-06-01: **monitored reference, not graded** — Devon-backed. He grades the pump on the **flow** envelope (V1: "as long as I'm falling in between this region, I know I'm good"); torque he reads as a single characteristic curve that plateaus (V2: 250 bar→~590 Nm, 100 bar→~400+ Nm; V3: "eventually it's going to get to a plateau"), with no upper/lower band. So the chart's "Torque Upper Limit" line is **not** transcribed; the zero-width `[acceptance.torque]` is the correct settled design (reframed in the profile from "calibration pending" to "monitored reference by design"). See decision-log 2026-06-01 + `devon-videos/devon-graph-walkthrough-notes.md`.
- [x] **Devon open points — serial block & displacement mode resolved** 2026-06-01. (c) **Serial-block confirm — RESOLVED:** Devon (V6) — the chart is "merely an example," "you can't build a model off an example," and the engine plots any pump from logged flow/pressure/torque, so the serial is "immaterial." Confirmation NOT required; the PC200-8 Fig.1 chart is a validation case, not the model; the engine is pump-agnostic. (a) **`displacement.mode` — settled by chart-match, reinforced by Devon's pump-agnostic principle:** machine-adjusted 112 cc/rev × 2000 rpm = 224 L/min no-load matches the chart's printed 226/222 (already validated in the profile + flow tests), so `machine_adjusted` is confirmed against the sheet; the measured-flow / pump-agnostic principle reinforces it, it isn't the primary reason. See decision-log 2026-06-01. The one genuinely-open Devon item — (b) sample rate / certificate cadence — now lives under **Waiting On → Devon open points**. [(c) flow-callout transcription and (d) torque-plateau value from the original list were done/resolved earlier 2026-06-01 — see above.]
- [x] **Concept Proposal v1 drafted** 2026-05-12. Saved as `bench-vision/benchvision-founding-partnership-proposal-v1.md`. Eight sections, ~3,400 words. Three corrections applied after Pix's first read: (1) removed "Most people meet BenchVision" claim (factually wrong — idea hasn't been broadly shown), (2) rewrote certificate-system paragraph to be factual rather than condescending and acknowledge BenchVision continues to produce paper/PDF in addition to digital signing, (3) reframed bench-design business as Devon's idea-in-conversation rather than confirmed venture.
- [x] **Read design-reference docs in `claude chats/design-refs/`** COMPLETED 2026-05-12. Nine layer design references read and synthesised — saved as `bench-vision/benchvision-architecture-synthesis-2026-05-12.md`. Single-document summary of HAL, Event Bus, Configuration System, Test Engine, Data Recorder, Pre-flight Module, Reporting Engine, UI Layer, Licensing Layer.
- [x] **TestVision → DARCSI rework — plain-text files** COMPLETED 2026-05-12. Updated: `bench-vision/CLAUDE.md`, `bench-vision/bench-vision-design-system.md`, `bench-vision/docs/spec.md`, `claude chats/CLAUDE.md`. Created new `bench-vision/DARCSI_OVERVIEW.md` (substantial rewrite of the former `TESTVISION_OVERVIEW.md`); the old file is marked as superseded but retained for reference until Pix archives it.
- [ ] **TestVision → DARCSI rework — .docx/.pages files** REMAINING. `TestVision_Business_Setup_Reference_v1.5_2026-04-22.docx` + `.pages` + the PDF in `signature-ready/` were NOT edited — these are version-numbered formal documents and editing them in place risks corrupting the historical record. The clean approach is producing a new `DARCSI_Business_Setup_Reference_v1.0_2026-05-12.docx` as a fresh-version successor. Defer until Pix decides whether to (a) rewrite the v1.5 content as DARCSI v1.0 or (b) wait for a more substantial refresh. Same applies to any branded materials in `legal/signature-ready/`, `marketing/`, etc.
- [ ] **Concept Proposal v1.1 refinement pass** - after Pix's read of the v1 corrections (the three factual fixes from 2026-05-12) and any further input, refine the concept proposal with architectural detail (now available in the synthesis) and any other adjustments. Output v1.1.
- [ ] **Draft Investor Participation Policy as companion document** - short principles-based doc (~4–6 pages) drawn from the existing investor research (05-investor-research.md). Covers funding path (SA pre-seed → UK Seed → UK/DE follow-on), acceptable investor categories, acceptable instruments, valuation methodology, information/voting rights, founder protection, conflict-of-interest rules for partners who become investors, process. Devon's interest in investing becomes the Devon-specific appendix. Anchors response policy independent of relationship dynamics.
- [ ] **Devon & Amy review of Concept Proposal** - share once drafted, collect comments and reactions. Aim is alignment on principles, not markup of clauses.
- [ ] **Convert Concept Proposal back into formal terms once principles agreed** - v9.2 (or refined v9.3) becomes the formal expression of the aligned principles, signed only after BenchVision simulation commissioning per Clause 0 / Nature of this Document. South African attorney review at that point, not before.
- [ ] **Request prospects list from Devon** - the list of customers/leads Devon intends to approach. Will be Appendix A to the formal agreement; not needed for the Concept Proposal stage but worth requesting now so Devon has time to compile.
- [ ] **Review signature-ready document set and revert with corrections** - legal/signature-ready/ (FPA v5, Proposal v2.1, Brand Reference v1.5) — note: v9.2 supersedes most of this, but the brand-reference content may still need a refresh independently

## Recently completed

- [x] **v9.2 generated** 2026-05-12. Brand, independence, and research-IP pass. Final formal-document version pending Concept Proposal re-framing of the conversation with Devon.
- [x] **Decision 7 reservation mechanics** LOCKED 2026-05-11
- [x] **Personal-capacity reframe** (v9.0+) — no companies in operative text; Mark Abbot kept structurally out
- [x] **Matrimonial / third-party succession** (v9.1) — category-level "by operation of law" language; accrual covered without naming
- [x] **Earnings research synthesis** — `legal/founders-agreement-earnings-research-2026-05-11.md`

## Waiting On

### Devon open points

- [ ] **Sample rate / certificate cadence** — confirm **10 Hz acquire / 1 Hz operator display** matches how Devon wants the certificate point-table to read. The single remaining genuinely-open Devon question; batch with any future visual-context message per the ask-devon discipline. (Serial-block and `displacement.mode` resolved 2026-06-01 — see Active + decision-log.)
- [ ] **Run-id numbering scheme** (surfaced 2026-06-02 by the run record) — the run record uses `YYYY-MM-DD-<PROFILE>-NNNNNN` as a provisional default. Does Devon's existing repair-shop process already impose a job/run numbering scheme the certificate should reuse (so BenchVision's id matches his paperwork)? Not a blocker; batch with the cadence question. Run the ask-devon check before queueing.

## Someday

## Done
