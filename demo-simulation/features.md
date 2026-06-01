# BenchVision Demo Simulation — Features

> Product-level feature list in implementation order. This is the handoff artefact for Workflow 02.
>
> Created: 2026-05-19 (Unlearn Workflow 01 — Step 9)
> Last updated: 2026-05-19
> Companions: `spec.md`, `out-of-scope.md`, `decision-log.md`

---

## Critical constraint

This document is **product-focused, not technical**. Per Unlearn Workflow 01 Step 9, it must NOT include any of:

- database schemas
- file names
- file paths
- class names
- API endpoints
- implementation details

Each feature is described in terms of what the operator and the audience experience. Implementation belongs to Workflow 02.

---

## How to read this document

Features are listed in **implementation order**: dependencies first, foundational features before features that build on them. A team picking this up should be able to work top-to-bottom without backtracking.

Each entry has four parts:

- **What it is** — one or two sentences.
- **User flow** — step-by-step interaction.
- **UI overview** — what the operator and the audience see.
- **Why this position in the order** — what depends on it being present.

---

## 1. Bootable demo machine running the BenchVision stack

**What it is.** The dedicated NUC-class Linux machine, configured per the canonical hardware spec, with the BenchVision production stack installed and runnable end-to-end.

**User flow.**
1. Operator powers on the machine.
2. The machine boots into a desktop showing a BenchVision launcher or auto-starts the BenchVision UI in the bench-side monitor.
3. Operator confirms the UI is reachable, the trend chart is rendering, and the simulator is producing data.

**UI overview.** Standard Linux boot, no kiosk lock, then the BenchVision UI. The audience does not see the boot — operators boot before the demo starts.

**Why this position.** Everything else depends on this. The demo cannot exist without a machine that runs the stack.

---

## 2. Simulator driver producing nominal sensor data

**What it is.** A driver that the production hardware abstraction layer recognises, which produces realistic-looking nominal data on every channel the bench profile defines — pressure, flow, temperature, torque, and encoder / RPM.

**User flow.**
1. Operator starts the BenchVision UI.
2. Within seconds, all configured channels show steady, plausibly-noisy values within their plausibility bounds.
3. Operator confirms each gauge is alive and each channel is GREEN.

**Per-pump behaviour comes from configuration, not software.** The pump's characteristics — how flow falls with pressure, how torque rises and plateaus, the pass/fail acceptance band — are read from a per-test **pump profile**, so demonstrating a different pump is a setup change, not a code change, and each result is judged against that pump's own manufacturer acceptance envelope. For the demo this is the Komatsu PC200-8, whose simulated flow curve matches the manufacturer chart.

**UI overview.** All channel gauges read live values. The trend chart shows steady traces. No alarms. No RED channels. The simulation looks like a real bench at rest.

**Why this position.** Live data is the foundation of every operator-visible feature. Without this, no UI surface has anything to show.

---

## 3. Live operator view — gauges and trend chart

**What it is.** The Live tab of the operator UI, showing each channel as a numeric value, a gauge, and a continuously-updating trend chart.

**User flow.**
1. Operator opens the simulation; the Live tab is the default landing surface.
2. Audience sees the current value of each channel, the trend over the most recent rolling window, and a colour-coded state indicator per channel.
3. Operator narrates what each gauge represents.

**UI overview.** Top of the screen: channel gauges in design-system colours (pressure light blue, flow teal, temperature lavender, torque amber, RPM green). Middle: a trend chart with one line per channel. Bottom or side: a status strip showing current test state.

**Why this position.** This is the surface the audience spends the most time looking at. It needs to be solid before any test-execution feature is layered on.

---

## 4. Pre-flight readiness — channel health gate

**What it is.** A surface that shows the current readiness state of every channel against the bench profile's plausibility bounds, with each channel marked RED, AMBER, or GREEN. RED blocks test start; AMBER does not.

**User flow.**
1. Operator opens the pre-flight surface.
2. Audience sees each channel listed with a colour indicator.
3. With the simulator at nominal, every channel reads GREEN.
4. Operator narrates that RED would prevent the test from starting and AMBER would not.

**UI overview.** A list of channels with colour-coded readiness indicators. A summary banner reads "Ready — all channels green" or equivalent. Test-start controls are visible but disabled until the second gate (the checklist) is also satisfied.

**Why this position.** First half of the two-gate readiness story. Channel health is the easier half to demonstrate first.

---

## 5. Pre-flight readiness — operator checklist gate

**What it is.** A list of checklist items the operator must confirm before the simulation will let a test start. Mirrors the production Pre-flight Module's human-gate behaviour.

**User flow.**
1. Operator opens the pre-flight surface (already showing channel health).
2. Below the channel health surface, a checklist of items appears (e.g. "Component installed", "Guards in place", "Operator briefing complete" — exact items configurable).
3. Operator confirms each item in turn.
4. Once all items are confirmed and all channels are GREEN, the test-start control becomes enabled.

**UI overview.** Checklist items as confirmable rows. A summary indicator showing how many items remain. A clear visual transition when the test-start control unlocks.

**Why this position.** Second half of the readiness story. Layers on top of channel health. Demonstrating channel-health-without-checklist first lets the audience see *why* the gate exists before the operator-acknowledgement part of it appears.

---

## 6. Test sequence execution — nominal end-to-end

**What it is.** A full happy-path test run from a ready state to a clean completion. The state machine progresses through every documented state; steps advance; the operator can pause, resume, or abort; the audience sees test progress on the live UI.

**User flow.**
1. With pre-flight green and checklist complete, operator starts the test.
2. The simulation moves into the running state. Channel values follow the simulated test profile — for example, pressure ramps to a target, holds, ramps down.
3. Steps advance through the sequence. Each step shows its setpoint, current measurement, and pass / fail status.
4. Operator demonstrates pause and resume mid-run.
5. The test completes; the state changes to complete.

**UI overview.** Live tab shows ongoing data. A test-progress surface shows the current step, step duration, and pass / fail of completed steps. State badge reads "Running", then "Complete".

**Why this position.** Requires the simulator (feature 2), live UI (feature 3), and pre-flight (features 4–5). Test execution is the core of the demo and must work in nominal form before any anomaly scenario is layered on.

---

## 7. Certificate generation — operator-triggered

**What it is.** A control the operator presses after a completed test to generate a PDF certificate from the production Reporting Engine. The certificate is a real PDF rendered from the same template path the production product uses.

**User flow.**
1. After a test completes, operator navigates to the session surface.
2. Operator reviews the captured live data and test results.
3. Operator presses the certificate-generate control.
4. A short progress indicator appears; within a few seconds the certificate is generated.
5. Operator opens the certificate — the audience sees a real PDF with bench identification, component details, test results, performance curve, pass / fail status, and signature blocks.

**UI overview.** Session surface with test summary, performance curve preview, and a prominent "Generate Certificate" control. After generation, a "View Certificate" control opens the PDF.

**Why this position.** Closes the credibility-gate operator loop — clipboard to PDF. Depends on a completed test run (feature 6).

---

## 8. Session persistence

**What it is.** Completed test sessions are persisted to the demo machine and remain available across application restarts. Each session retains its full run data so a certificate can be re-rendered later.

**User flow.**
1. After a test completes (feature 6), the session is written to persistent storage.
2. On next application start, the session is still discoverable from the session history surface (feature 9).

**UI overview.** Invisible to the audience; surfaces as continuity between demos.

**Why this position.** Feature 9 (session history) requires this to exist.

---

## 9. Session history browser

**What it is.** A surface listing past test sessions, browsable by date or by component. The operator can open any past session, view its summary, and re-render its certificate.

**User flow.**
1. Operator navigates to the session history surface.
2. Audience sees a list of pre-populated past sessions — enough that the list looks like a real installation's history, not a demo with one entry.
3. Operator opens one historical session.
4. The session detail surface shows the same elements as a freshly-completed test (data summary, performance curve, results, pass / fail).
5. Operator can re-render the certificate for that past session.

**UI overview.** A list of past sessions with date, component identifier, and pass / fail badge. Detail view matches the live-session detail view.

**Why this position.** Requires session persistence (feature 8). Builds the "audit trail" half of the credibility-gate story.

---

## 10. Pre-populated session history content

**What it is.** A set of canned historical sessions — generic-data only — shipped with the demo machine so the session history surface looks populated from the first demo.

**User flow.** Operator does not interact with this directly. It exists so the session history surface (feature 9) is meaningful on first run.

**UI overview.** None of its own. Visible through feature 9.

**Why this position.** Independent of the scripted-scenario work; can be assembled in parallel once feature 9 is functional.

---

## 11. Resettable demo state

**What it is.** A single, discoverable control accessible to the operator (and not surfaced to the audience) that returns the simulation to a known clean baseline in under five seconds from any state, without restarting the machine or the application.

**User flow.**
1. After a demo, or mid-demo if the operator wants a clean restart, operator triggers the reset.
2. The simulation returns to the standard pre-demo baseline within five seconds.
3. The session history (feature 9) retains its pre-populated content; only the in-progress / freshly-completed state is cleared.

**UI overview.** A small, low-visibility control in a known location. Not in the audience's natural eye line. No confirmation dialogue (a five-second reset is faster than a confirmation dialogue).

**Why this position.** Must be in place before either operator can comfortably run repeat demos. Reset semantics depend on persistent state (feature 8) being clearly separable from in-flight state.

---

## 12. Discreet operator scenario trigger

**What it is.** A control that lets the operator fire any of the scripted scenarios at any time, without the audience seeing the trigger. Architecturally, it is the operator-side UI surface over the simulator module's scenario-switching interface, and is only present and active when the simulation is in training / demo mode (see `spec.md` §8). In live mode the simulator module is not connected; the trigger has nothing to wire to and is not rendered. This is the safety-boundary mechanism — operators cannot use the trigger to alter real sensor readings in live mode because the simulator simply isn't running.

**User flow.**
1. During a nominal demo, operator decides the conversation calls for an anomaly.
2. Operator accesses the trigger control discreetly — through a known key combination, an off-canvas surface, or another mechanism that does not draw audience attention.
3. Operator selects a scenario.
4. The chosen scenario begins; from the audience's perspective the demo continues unaltered until the scenario manifests.

**UI overview.** Deliberately understated — closest analogue is a presentation remote that the speaker uses without breaking flow. Not a visible button. The exact mechanism (key combination vs off-canvas surface vs other) is a Workflow 02 design decision.

**Why this position.** Required before any individual scenario can be implemented. Scenarios depend on the trigger surface to fire them. The training / demo mode itself is a configuration of the simulator module (per `spec.md` §8), not a separate feature in this list — the simulator driver (feature 2) is its implementation surface.

---

## 13. Scripted scenario — dramatic (Scenario A)

**What it is.** The first of the at-least-two MVP scenarios. Candidate: pressure spike during hold, or emergency-stop simulation. Triggers safety pause, alarm, and operator notification; shows the full intervention loop.

**User flow.**
1. During a running test (feature 6), operator fires this scenario via the trigger (feature 12).
2. The simulator produces an anomalous data event matching the chosen scenario.
3. The system detects the anomaly, fires an alarm, and pauses the test automatically.
4. Operator UI shows a clear notification of what happened and why.
5. Operator acknowledges, takes a scripted intervention action, and either resumes the test or aborts.
6. On abort, a certificate is still generated marking the audited abort with the reason.

**UI overview.** During the scenario: alarm banner in the design-system fail colour, paused-state indicator, clear notification text. After intervention: a state transition the audience can see. After certificate: the audited abort appears in the session history.

**Why this position.** First scenario can be built once features 6 and 12 are functional.

---

## 14. Scripted scenario — quieter (Scenario B)

**What it is.** The second of the at-least-two MVP scenarios. Candidate: calibration drift detected, or out-of-spec step result. Quieter intervention loop — flag, judgement, audited continuation rather than automatic pause.

**User flow.**
1. During a running test, operator fires this scenario via the trigger.
2. The system detects the soft anomaly and surfaces it as a flag rather than an alarm.
3. Operator acknowledges the flag, narrates the judgement call to the audience, and chooses to continue.
4. The test continues; the flag is recorded in the session.
5. On certificate generation, the flag appears in the audit trail.

**UI overview.** During the scenario: warning banner in the design-system warning colour (not the danger colour), flag indicator on the affected channel or step. Less visually loud than Scenario A.

**Why this position.** Builds on the same trigger and intervention pattern as Scenario A. Gives the operator tonal range.

---

## 15. Splash screen and brand identity surfaces

**What it is.** The visible brand-identity surfaces of the simulation — splash on app start, certificate footer, brand placements per `spec.md` §6.

**User flow.**
1. On application start, a DARCSI / BenchVision splash is briefly visible.
2. Within the operator UI, BenchVision-led branding is consistent on every surface.
3. The certificate footer carries the DARCSI-platform attribution.

**UI overview.** Splash uses the design system. No bespoke brand work; tokens only.

**Why this position.** Late in the order because the operator can run end-to-end demos without it. But required before commissioning is complete (per `spec.md` §10).

---

## 16. Licensing tier reference screen — static

**What it is.** A static screen, accessible from a known surface in the operator UI, showing FREE / PROFESSIONAL / ENTERPRISE features side-by-side. Non-functional — does not gate behaviour.

**User flow.**
1. Operator (typically Pix in investor-demo context) navigates to the licensing reference surface.
2. Audience sees the three tiers presented as a comparison.
3. Operator narrates the commercial story.

**UI overview.** A clean three-column comparison surface in the design system's information-density style. Tier labels, feature checkmarks, brief explanatory text.

**Why this position.** Independent of the credibility-gate operator loop. Can be built in parallel with the scenario work.

---

## 17. Token-based theming audit

**What it is.** A pass over the entire demo-simulation UI confirming that every colour value and every brand string is referenced through the design system, with no hardcoded literals in component code.

**User flow.** None — this is a code-review activity.

**UI overview.** No UI surface; the audit confirms the constraint from `out-of-scope.md` §A3 has been met.

**Why this position.** Late in the order because it is a verification step over completed UI work. Must be done before commissioning is signed off, because failing this audit means white-label is a rework rather than a swap when it lands post-MVP.

---

## Implementation order summary

For the team picking this up — the order above is the dependency-respecting order. Two parallel tracks are available once the foundation is in place:

**Foundation (sequential).** Features 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9.

**Parallel tracks once feature 9 is functional:**

- *Operator-trigger track:* 11 → 12 → 13 → 14
- *Polish-and-commercial track:* 10, 15, 16

**Verification (last).** Feature 17 (token-based theming audit), plus the adversarial poke-holes pass per Workflow 01 Step 7 and the success criteria in `spec.md` §10.

---

## Version history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-05-19 | Initial Workflow 01 Step 9 draft. Implementation-ordered. Honours the explicit do-NOT-include constraint from Lesson 9. |
| 0.2 | 2026-05-30 | Feature 2: added the per-pump-profile note — derived channels are parameterised per pump, results judged against that pump's manufacturer acceptance band (formula-engine architecture; Flow, Torque and Power channels implemented and the characteristic curve drawn from the engine). |
