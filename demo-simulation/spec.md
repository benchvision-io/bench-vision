# BenchVision Demo Simulation — Spec

> Living document. Iterate as questions surface and decisions land. The companion `out-of-scope.md`, `features.md`, and `decision-log.md` are the rest of the Workflow 01 artefact set.
>
> Created: 2026-05-19 (Unlearn Workflow 01 — Step 1)
> Last updated: 2026-06-01

---

## Contents

1. [Purpose](#1-purpose)
2. [Audience](#2-audience)
3. [Demo experience](#3-demo-experience)
4. [What the demo demonstrates](#4-what-the-demo-demonstrates)
5. [Scripted scenarios](#5-scripted-scenarios)
6. [Brand identity in the simulation](#6-brand-identity-in-the-simulation)
7. [Hardware target](#7-hardware-target)
8. [Technical direction](#8-technical-direction)
8A. [Parameterised formula engine (derived channels)](#8a-parameterised-formula-engine-derived-channels)
9. [Non-stack constraints](#9-non-stack-constraints)
10. [Success criteria — what "commissioned" means](#10-success-criteria--what-commissioned-means)
11. [Open questions](#11-open-questions)
12. [Version history](#12-version-history)

---

## 1  Purpose

The demo simulation is a self-contained running instance of BenchVision used to demonstrate the product to founding partner Devon Abbot and to future prospects, investors, and distributors **before any production DAQ hardware is committed**. It runs on a dedicated NUC-class Linux machine using BenchVision's production software stack, with the Hardware Abstraction Layer pointed at a simulator driver in place of real DAQ devices.

Successful commissioning of the demo simulation is **Clause 0 of the founding partnership** — the gate the founding partner agreement signature waits on. Commissioning means the simulation is demonstrable end-to-end on the dedicated machine by both operator profiles, with the success criteria in §10 met.

---

## 2  Audience

Two operator profiles are first-class. The simulation must be operable by either without retraining.

| Operator | Context | Audience the operator presents to |
|---|---|---|
| **Devon Abbot** | Solo, bench-side, Specialised Steering / Komatsu installation | Hydraulic engineers, workshop managers, OEM procurement personnel — domain-fluent |
| **Pix** | Off-site meetings in the UK and Germany | Mixed — distributor sales leaders, prospect engineers, investors. Not uniformly domain-fluent. |

The simulation reads clearly to both audience types without operator-side adjustment. Operator-side narration adapts; the on-screen content does not need to.

---

## 3  Demo experience

Operator-driven walkthrough. The operator chooses which sections to show, in what order, and at what depth. The simulation does not run itself.

Three properties are non-negotiable.

**Forgiving.** No misclick, stray input, or out-of-order action can break the demo or leave the simulation in a state the operator cannot recover from in front of an audience. Out-of-scope actions are disabled or behave as quiet no-ops; never thrown errors, never stack traces, never a crashed window.

**Resettable.** From any state, the operator can return the simulation to a known clean baseline in under five seconds without restarting the machine or the application. Reset is a single discoverable control accessible to the operator and not to the audience.

**Modular.** The three demonstrable sections — operator view, test execution, reporting — are each meaningful when shown in isolation. The operator decides depth and order per room. A demo can credibly be three minutes (one section) or twenty minutes (all three plus a scripted anomaly), driven by the conversation in the room.

A self-running showcase loop for trade-show and unattended-investor-demo contexts is **anticipated for post-MVP** but is explicitly out of scope here.

---

## 4  What the demo demonstrates

Four capability surfaces are in scope, all anchored on BenchVision's production architecture (see `bench-vision/benchvision-architecture-synthesis-2026-05-12.md`).

**Pre-flight gate.** Two-gate readiness — software channel health (RED / AMBER / GREEN) plus an operator checklist — behaving exactly as the production Pre-flight Module. The audience sees BenchVision refuse to start a test until both gates are green, and sees the operator complete the human gate by walking the bench (in the demo, by acknowledging on-screen items).

**Live operator UI.** Real-time gauges, trend chart, alarm indicators, and current test state. Channel colours follow the design system — pressure light blue, flow teal, temperature lavender, torque amber, RPM green. Same Nuxt 4 / Vue 3 / SSE frontend the production product uses.

**Test sequence execution.** Full state-machine progression from READY through RUNNING to a terminal state. Steps advance, are evaluated against pass / fail criteria, and the operator can pause, resume, or abort. Safety thresholds are monitored on every reading regardless of test state, mirroring the production Test Engine — the audience sees that safety logic does not pause when the test pauses.

**Certificate generation and session history.** Operator-triggered PDF certificate from the Reporting Engine using a real render path (no mock PDF). A persistent session history is pre-populated on the demo machine so the audience can also browse past runs, open a prior session, and re-render its certificate.

Two further surfaces are demoable but **non-functional in this MVP**, explicitly:

- **Licensing tier overview.** A static reference screen accessible from the simulation showing FREE / PROFESSIONAL / ENTERPRISE features side-by-side. Built for investor and commercial conversations. The reference screen is on-message but does **not** functionally gate behaviour inside the simulation.

- **DARCSI parent-brand presence.** Visible enough that the audience registers BenchVision as a DARCSI-platform product. Splash, certificate footer, and licensing reference screen carry DARCSI marks; the rest of the UI stays BenchVision-led.

---

## 5  Scripted scenarios

The simulation defaults to a clean, nominal test run. The operator has a **discreet trigger control — not visible to the audience** — that fires one of several scripted anomaly scenarios on demand.

MVP ships with at least two scenarios — one dramatic, one quieter — so the operator has tonal range. Candidate scenarios:

- **Pressure spike during hold** — dramatic. Triggers safety pause and intervention loop.
- **Calibration drift detected mid-test** — quieter. Operator-judgement moment; audience sees the flag, not a fail.
- **Sensor disconnect / channel goes RED during run** — medium. Shows that pre-flight monitoring continues during a running test, not only before start.
- **Emergency-stop simulation** — dramatic. Full intervention loop ending in an audited abort with certificate.
- **Out-of-spec step result** — quieter. Pass / fail boundary; audited continuation with the failing step recorded.

Each scenario shows the same five-step intervention loop:

> Detection → alarm → automatic pause → operator notification → intervention → resumed test or audited abort with certificate.

The audience leaves with a clear mental model of how BenchVision behaves when things go wrong, not only when they go right.

Stochastic / probabilistic anomalies are out of scope. The demo simulation and the broader training mode (see §8) both use deterministic, operator-triggered scenarios — unpredictability is a separable future product surface (e.g., an operator-examination / certification mode), not part of the demo or training-mode MVP.

---

## 6  Brand identity in the simulation

DARCSI is the over-arching platform brand; BenchVision is the product. Both names appear in the simulation, in the right surfaces:

- **Splash screen** — DARCSI mark plus "BenchVision — a DARCSI platform product" subhead.
- **Operator UI** — BenchVision-led. DARCSI does not intrude on the working surface.
- **Certificate footer** — "Generated by BenchVision · DARCSI platform" or equivalent agreed wording.
- **Licensing reference screen** — DARCSI-platform framing; tier badges are platform-level.

**Token-based theming is mandatory** across all UI surfaces. No hardcoded colour values, no hardcoded brand strings in component code. A functional white-label theme swap is deferred to post-MVP, but the architectural constraint to enable it sits at the demo simulation level: get this wrong now and white-label becomes a rework, not a swap.

The design system (`bench-vision/bench-vision-design-system.md`) is authoritative for colour, typography, and component appearance.

---

## 7  Hardware target

Dedicated NUC-class Linux mini PC, bench-side single 1080p monitor. The canonical hardware reference is `bench-vision/hardware/demo-machine-build.md` (Ubuntu 26.04 LTS, Python 3.14, Node 22+ LTS, 16 GB RAM, 512 GB NVMe SSD, USB 3.2 reserved for future LabJack T7 path).

The demo simulation itself does not constrain hardware further. The relationship runs the other way — the hardware spec defines the floor the simulation runs against. If the hardware spec changes, the simulation must continue to run within the new floor.

---

## 8  Technical direction

The simulation uses **the production BenchVision software stack unchanged at the layer boundary**, with one substitution: the HAL driver registry is configured with a simulator driver in place of NI-DAQmx and Modbus drivers. Every other layer — Event Bus, Configuration System, Test Engine, Data Recorder, Pre-flight Module, Reporting Engine, UI Layer — runs the production code path.

This is the most important architectural decision in this spec. Three reasons.

First, the demo is not a parallel codebase. The simulation is a configuration of BenchVision, not a fork of it. Any improvement to the production stack reaches the demo automatically; any work done to make the demo more credible feeds back into the production product.

Second, **the demo simulation is also the proof that the architecture works**. Wiring the simulator driver to the production HAL and watching `SensorReading` events flow through the Event Bus to the Test Engine to the Data Recorder to the certificate is the end-to-end integration test the production stack would otherwise lack until Phase 3 hardware arrives. A working demo is a working architecture.

Third, **the simulator module is itself a first-class part of the BenchVision product, not a demo-only artefact.** It ships with the production stack and exposes two operator-selectable runtime modes:

- **Live test** — real sensors via the production HAL drivers (LabJack T7, NI-DAQmx, Modbus), production audit trail, real certificates.
- **Training / demo test** — simulator-driven, runs tagged as non-production, certificates marked accordingly or suppressed.

This means BenchVision ships with a built-in operator-training capability — new operators can train against simulated benches before working real hardware, expanding BenchVision's addressable use case beyond pure production testing and creating a re-usable engine for the *Getting Calibrated* educational direction. The demo simulation is operating that same training mode with scripted scenarios pre-loaded. The discreet operator trigger (`features.md` feature 12) is the UI control wired to the simulator's scenario-switching interface within training / demo mode; in live mode the simulator module is not connected and the trigger has nothing to drive.

**This is the safety boundary.** Operators cannot override real sensor logic in live mode — the architecture makes that impossible by construction rather than by policy. The trigger feeds the simulator; the simulator only runs in training / demo mode; live mode reads exclusively from real-sensor HAL drivers. A live-mode test session and a training-mode session cannot be active simultaneously.

The demo machine itself is permanently configured to training / demo mode (no real sensors are attached) and the mode-switcher UI is not exercised in the demo's audience-facing flow. The architectural decision is locked here; the polished training-mode user experience (mode-switcher UI in production, structured training curriculum, training-mode certification logic) is post-MVP and lives in `out-of-scope.md` §A14.

Languages, frameworks, and libraries follow the production stack: Python 3.14 throughout the backend, TypeScript and Nuxt 4 / Vue 3 on the frontend, FastAPI bridge with SSE for live data and REST for control endpoints, SQLite (WAL mode) for session persistence, Jinja2 + WeasyPrint for the certificate render.

Two surfaces in the demo configuration:

- **Simulator driver.** Registered against the production HAL driver registry. Produces plausibly-shaped pressure, flow, temperature, torque, and encoder data conforming to the bench profile's plausibility bounds and calibration. Drives nominal behaviour by default; accepts scenario-injection commands from the operator trigger. Now a first-class shipping module (see "third" above), not a demo-only artefact.

- **Operator scenario trigger.** A discreet UI surface (mechanism in `features.md` feature 12) that lets the operator fire any of the scripted scenarios from §5 without the audience noticing. Wired to the simulator's scenario-switching interface; only present and active in training / demo mode.

> *Pending Devon's input:* a clarifying question is open with Devon on whether standard hydraulic-test operator practice includes legitimate diagnostic actions that look similar to but are distinct from sensor override — force-recalibrate of a specific channel, force-zero at a known state, bypass non-safety-critical sensor (e.g. ambient temperature) when it's broken and the test doesn't require it. These are not "overrides" in the unsafe sense (the safety boundary above stands); they may be features in their own right if they exist in standard practice. See `decision-log.md` for the question text; resolution will add features to `features.md` or out-of-scope entries as appropriate.

---

## 8A  Parameterised formula engine (derived channels)

> **Status:** design direction agreed 2026-05-27; **Flow, Torque and Power implemented on the engine 2026-05-30** and the **torque-plateau calibration resolved 2026-06-01** (`benchvision-app/formula_registry.py`, `benchvision-app/pump_profile.py`, `benchvision-app/profiles/pc200-8-hpv95.toml`). All three derived channels read constants from the pump profile and compute via registry-resolved formulas; the dashboard characteristic curve draws from the engine too. Validated against the manufacturer chart (19 unit tests passing): flow byte-identical to the old code on the linear formula and within 2 L/min of the digitised destroke curve; torque now traces the chart across the **whole** sweep — it agrees at the 130-bar PC knee and climbs to the printed **~627 Nm** nominal plateau (the earlier "~590" was an eyeball read one gridline low; the true nominal callouts run 269→~630 Nm); power flat at 48.5 kW in the constant-power region. **How the plateau was resolved:** the `absorption_torque_from_flow_v1` formula is *unchanged* — an empirical per-pump efficiency curve η(P) was added to the profile (`[efficiency]`) and resolved per-pressure in `pump_profile.torque_inputs()`, so η falls from ~0.85 at the knee to ~0.74 at 400 bar and the constant-power formula's flat plateau bends up to match the chart. Because only the *input supply* changed and not the function, there is **no formula version bump**. The flow acceptance band is now the chart's **printed Upper/Lower limit lines** (read from the clean PDF; the lower destroke knee sits at ~102 bar, the band fanning out after it — e.g. ~144/108.5 at 250 bar — certified to 380 bar, with 380→400 a flat extrapolation). The torque band holds the **nominal reference curve** as a zero-width placeholder (upper==lower==nominal), and torque is shown as a **monitored reference, not graded pass/fail**, pending Devon's "is torque a graded channel?" decision. The one remaining open item is confirming the `displacement.mode` / 95→112→127 mechanics with Devon. Full reasoning in `decision-log.md` (2026-05-27 and 2026-05-30 entries) and the 2026-06-01 update in `pc200-8-chart-digitised-values.md`.

Derived test channels — flow, torque, power, and the like — are **computed from a parameterised formula engine, not hard-coded per pump**. The driving principle (Devon, 2026-05-27): *"it should make zero difference what the displacement is — the graph should formulate itself."* The formula for a given test type is stable; what varies test-to-test is the **inputs**. So the configurability lives in parameters, not in formula-authoring.

**Pump profile in the config file.** Each test's configuration carries a pump profile — theoretical displacement, machine-adjusted flow, rated RPM, pressure sweep, acceptance limits, and units — and names which formula each derived channel uses. No pump-specific constants live in channel code. A new pump is a config change, not a code change. (Note the deliberate separation of *theoretical displacement* from *machine-adjusted flow* in the profile — collapsing them into one "displacement" field is what produced the 95/112 confusion of 2026-05-27.)

**Curated formula registry, not free-text by default.** The engine ships a library of named, tested formulas (`pump_flow`, `absorption_torque`, `radial_torque`, `power_curve`, …); the config selects one by name per derived channel and supplies its inputs. This delivers Devon's "works for any pump" outcome while keeping the maths curated, version-pinned, and auditable — which matters because the trustworthiness of the pass/fail certificate is BenchVision's commercial foundation. The PC200-8 chart is a **validation case** for the engine, not the model itself.

**Advanced custom-formula mode (gated, liability on the named editor).** A free-text formula capability is offered as an advanced option, bounded so responsibility sits with the editor rather than DARCSI:

- Tied to a **named user account** with an advanced/engineer permission — not a shared password (identity is what makes liability land).
- An **explicit at-save responsibility acknowledgement**, recorded with name and timestamp.
- Outputs/certificates carry a **provenance stamp** — "computed using a custom formula authored by [name], not a BenchVision-verified relationship" — reusing the live-vs-training certificate-marking boundary in §8.
- The formula is **version-locked** once it has produced a result, so any historical certificate is reconstructable.
- It still runs in a **maths-only sandbox** (whitelisted functions, no file/system access). The sandbox is a *separate* concern from liability: the editor owns "is the formula correct?"; a defect letting a formula touch the system would still be DARCSI's.

Good custom formulas can later **graduate** into the verified registry after review. The advanced-mode *UI* is a fast-follow rather than MVP, but the **hooks are designed in now** — named-user permission, provenance stamp, audit record. *(Not legal advice: a disclaimer reduces but does not eliminate vendor exposure; the acknowledgement wording needs professional legal review before commercial launch.)*

**Explainable caution layer (guardrail, not gate).** Editing a formula triggers a deterministic, explainable caution that shows the anticipated outcome before commit:

- **Forward-preview** the resulting curve across the pressure sweep, ideally beside the previous one.
- **Range-check against the pump profile** (e.g. "predicts 1900 Nm at 250 bar; reference ~627 Nm — check displacement units?"). This specific check would have caught the 95/112 error automatically.
- **Unit / dimensional check** (does the result resolve to the channel's expected unit?).
- **Physical-plausibility check** (flow non-negative and falling/flat with pressure; torque rises then plateaus; power bounded).

It **warns; it does not block** — the named editor may proceed, consistent with liability sitting on them. A shown-and-overridden caution is written to the **audit record** ("editor was warned X, acknowledged, proceeded"), which *reinforces* the liability shift. Cautions must stay explainable — an opaque "the AI thinks this is wrong" erodes trust in a certification tool. ML-style outlier detection is post-MVP and strictly advisory; it never decides pass/fail. Build cautions as **pluggable validators**; the cheap high-value ones (preview, range, units, monotonicity) are MVP. The same validator engine later sanity-checks **live** test runs, bridging toward the edge-AI / calibration adjacent-market directions.

**Migration path** (incremental, low-risk): (1) ✅ **done 2026-05-30** — Flow, Torque and Power lifted into `benchvision-app/profiles/pc200-8-hpv95.toml`, formula bodies replaced by registry lookups keyed by each channel's `formula`; torque derives from live flow so the plateau emerges; the dashboard characteristic curve and acceptance band now come from the profile/registry. (2) ✅ **done 2026-06-01** — torque plateau calibrated via an empirical η(P) efficiency curve in the profile (resolved per-pressure in `torque_inputs()`), so the *unchanged* `absorption_torque_from_flow_v1` now traces the chart's climbing-then-plateau nominal curve to ~627 Nm; the flow acceptance band was replaced with the chart's printed Upper/Lower limit lines. Still open: confirm the `displacement.mode` / 95-112-127 mechanics with Devon, decide whether torque becomes a graded channel (its band is a monitored nominal reference for now), and optionally couple derived torque to live speed for fault realism. (3) add the gated custom-formula mode and caution layer once the registry path is solid (interface hooks — `provenance`, `author`, version-lock, `evaluate()` choke point — are already in place).

---

## 9  Non-stack constraints

Things that shape the spec beyond language and framework choice:

- **Offline first.** The demo must run with no network connection. A prospect's site network is not a precondition.
- **Single-user, no authentication.** Mirrors the production MVP posture (`docs/spec.md` §15) — adding auth here would be both scope creep and unrepresentative of the product.
- **Quiet failure.** Any internal error surfaces as quiet recoverable state, never as a stack trace or a crashed window. The demo is in front of paying-prospect eyes.
- **Reset under five seconds.** From any state, the operator can return to a clean baseline without restarting the machine or the application.
- **No external data dependencies at demo time.** Pre-populated session history ships with the machine. Certificate generation does not require fetching anything live.
- **Generic test data only.** No real Komatsu IP, no real customer bench data, no real prospect-confidential information embedded in the canned content. Generic worked examples that look real without *being* real.

---

## 10  Success criteria — what "commissioned" means

Per Workflow 01's explicit-exit-condition requirement, the demo simulation is "commissioned" when both the **commissioning checklist** (§10.1) and the **adversarial-review quality gate** (§10.2) are satisfied. Anything short is not yet commissioned.

### 10.1  Commissioning checklist

Each item is independently testable. A third party walking through the list should be able to tick each box yes / no without subjective judgement.

1. **All four must-show capability surfaces trigger from the operator-driven walkthrough without errors** — pre-flight (channel health + checklist), live operator UI, test sequence execution end-to-end, certificate generation, and session history browse. No stack traces, no error dialogs, no missing screens.

2. **At least one scripted anomaly scenario plays end-to-end** from operator trigger through detection → alarm → automatic pause → operator notification → intervention → resumed test or audited abort with certificate. No crashes, no lost state, no stuck UI.

3. **The reset control returns the simulation to a known clean baseline in under five seconds from any point in any scenario**, with no application or machine restart required, and with pre-populated session history preserved.

4. **The full demo runs unmodified on the canonical demo machine** (Ubuntu 26.04 LTS plus the components specified in `bench-vision/hardware/demo-machine-build.md`) without requiring developer intervention beyond the operator's discreet trigger.

5. **Audience-facing UI contains zero placeholder strings** — no "Lorem Ipsum", no "TODO", no "Sample Customer Ltd", no `__placeholder__` tokens visible anywhere in the operator UI, the certificate, or the session history detail surfaces.

6. **Either operator can complete a 15-minute end-to-end demo solo**, starting from a fresh boot, without external help and without consulting external aids.

### 10.2  Adversarial-review quality gate

A Workflow 01 Step 7 adversarial poke-holes pass over the spec, the features list, and the running demo returns no **substantial** new findings — including from a reviewer who has not previously seen BenchVision.

A finding is **substantial** if it would:

- (a) change a feature in `features.md`, or
- (b) change an entry in `out-of-scope.md`, or
- (c) change a section heading in `spec.md`.

Minor copy edits, phrasing improvements, and stylistic adjustments are not substantial and do not block commissioning.

### 10.3  Sign-off

Sign-off is by Pix as software owner. Devon's review of the demo at commissioning is captured separately as part of the founding partnership conversation, not as a gating criterion of the demo simulation itself.

> *Open structural question:* Pix unilaterally signing off a milestone that gates the founding partnership signature is a structural conflict of interest worth resolving — possibly co-sign by Amy, possibly an alternative sign-off mechanism in v9.3 of the Concept Proposal. Flagged in `adversarial-review-0.1.md`; resolution gated on a focused founding-partnership session with Devon. Does not block v0.2 of this spec; does need resolving before commissioning actually happens.

---

## 11  Open questions

Items that need a decision but are not blocking the first draft. Resolve as iteration proceeds.

| # | Question | Who answers | Bearing on spec |
|---|---|---|---|
| Q-D1 | Reset semantics — manual-only, or also auto-reset after an idle period? | Pix | Affects features.md operator-controls feature |
| Q-D2 | Scenario count beyond the two-minimum — which of the five candidate scenarios in §5 are MVP, which are reserved for v1.1? | Pix + Devon | Affects features.md scope and timeline |
| Q-D3 | Session history depth — how many pre-populated past runs ship with the demo? Five reads as "a demo"; twenty reads as "an installation". | Pix | Affects canned-data effort and storytelling |
| Q-D4 | Licensing tier reference screen — where does its content live as a single source of truth? Currently no commercial pricing document exists. | Pix | Affects out-of-scope.md note and future commercial work |
| Q-D5 | Certificate worked-example data — generic synthetic, or based on a real Komatsu-class performance curve with values obfuscated? | Pix + Devon | Confidentiality vs. credibility tradeoff |
| Q-D6 | DARCSI mark in the splash — text-only as today, or does this trigger commissioning a DARCSI logomark? | Pix | Affects brand-identity surfaces and possibly a separate design task |
| Q-D7 | Demo-machine commissioning sign-off — beyond §10 above, does Devon witness the demo before the founding partnership signature, or after? | Pix + Devon | Affects sequencing of Clause 0 around the formal agreement |
| Q-D8 | ✅ Largely resolved. `docs/spec.md` v2.0 (2026-05-27) corrected the stale items this row flagged — the operator HMI is now Nuxt 4 / Vue 3 / FastAPI / SSE (not PyQt) and licensing is an MVP layer (not out of scope) — and v2.1 (2026-06-01) folds in the parameterised formula engine (§14A), so the two specs are now reconciled on derived channels. Residual: keep the full-product spec and this demo spec in step as decisions land. | Pix | No longer blocking; routine currency upkeep |

---

## 12  Version history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-05-19 | Initial Workflow 01 Step 1 draft. Captures Pix's answers to the four clarifying questions of 2026-05-19. Anchored on architecture synthesis (2026-05-12), `demo-machine-build.md`, and the design system v1.2. |
| 0.2 | 2026-05-27 | Added §8A Parameterised formula engine — derived channels computed from a named-formula registry + config pump profile (not hard-coded), gated advanced custom-formula mode with liability-on-named-editor mechanics, and an explainable caution layer. Recorded ahead of Devon's Excel video; exact pump-formula mechanics confirm after. |
| 0.3 | 2026-06-01 | §8A currency refresh (no structural change). Torque-plateau calibration resolved via an empirical η(P) efficiency curve in the profile — the `absorption_torque_from_flow_v1` formula is unchanged, so no version bump; the engine now traces the chart to its ~627 Nm nominal plateau (corrected from the stale "~590" eyeball read). Flow acceptance band repointed to the chart's printed Upper/Lower limit lines; torque recorded as a monitored nominal reference, not graded pass/fail. Profile/engine paths repointed to `benchvision-app/`. Q-D8 refreshed — `docs/spec.md` is no longer materially stale (v2.0 fixed PyQt/licensing; v2.1 adds the §14A formula engine). |

---

*Next: this spec feeds Workflow 01 Steps 4–11 — boundary-setting, out-of-scope, mockups, adversarial poke-holes, gap-find, features list, decision-log, scaffold. The `out-of-scope.md`, `features.md`, and `decision-log.md` companions are the immediate next artefacts.*
