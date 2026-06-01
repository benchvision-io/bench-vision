# Adversarial Review — Spec Set v0.1

> Captured 2026-05-19 from an independent Plan-agent reviewer per Unlearn Workflow 01 Step 7. Preserved here as the audit trail behind the v0.2 revision pass. The five "biggest" findings are the substantial new findings that prevent the Workflow 01 exit condition from being met by the v0.1 draft.
>
> Companions: `spec.md`, `out-of-scope.md`, `features.md`, `decision-log.md`

---

## The five load-bearing findings

### 1. Success criterion §10.4 is circular and self-flagged

`spec.md` §10.4 uses "an adversarial poke-holes pass returns no substantial new findings" as a gate, but provides no rubric for "substantial". Combined with §10.1's "without rehearsal aids" being undefined, two of the four commissioning criteria are not testable as written.

**Revision direction.** Define "substantial" concretely (anything affecting §10.1–3, anything contradicting the architecture synthesis, anything an operator would discover under demo conditions) or drop §10.4 and let §10.1–3 carry the gate. Define "rehearsal aids" (e.g. allowed: notes app on a personal phone; not allowed: open browser tabs on the demo machine, printed crib sheet visible to audience).

### 2. The "configuration not a fork" rule and feature 12 (discreet operator trigger) are in active tension

The decision-log rule that the simulation is a configuration of BenchVision, not a fork — combined with feature 12's discreet operator scenario trigger — has no architectural home. The mechanism is "deferred to Workflow 02" by both `spec.md` §8 and `features.md` feature 12, but the decision is load-bearing enough that an implementer will invent it during Workflow 02 unless `spec.md` owns it now.

**Revision direction.** Pick an architectural mechanism for the trigger before Workflow 02 starts, or explicitly accept demo-only code in the production codebase and stop claiming "configuration, not a fork". Candidates: scenario schedule in a config file (loses on-demand); REST endpoint on the FastAPI bridge (demo-only code path); separate localhost helper process the simulator driver subscribes to (cleanest separation, most parts).

### 3. Certificate fidelity vs the architecture's open Q-01 (ISO 4409 / 10100 compliance)

The architecture synthesis flags ISO field compliance as critical — "certificates that don't meet the standard are worthless to customers presenting them to OEMs or auditors". The demo certificate is described as a real PDF from the production Reporting Engine path. Either it meets the standard or it doesn't; the spec does not say.

**Revision direction.** Either resolve open architecture Q-01 before commissioning (which means SABS standards purchase), or add an explicit `out-of-scope.md` item noting field-level ISO compliance is not claimed in MVP, plus operator narration guidance for what to say if asked.

### 4. The five-step intervention loop has no time budget and no operator-cognition fallback

`spec.md` §5 defines the intervention loop but doesn't address loop duration, audience-interrupt handling mid-loop, operator forgetting the intervention, abort-certificate template variant, or operator hands-on-keyboard assumption when slides may be sharing the same monitor.

**Revision direction.** Add a time budget per scenario (target end-to-end seconds). Address audience-interrupt: can PAUSED state be held indefinitely while the operator answers a question? Does the simulator continue producing anomalous data, or normalise? Verify the Reporting Engine template renders an ABORTED-state certificate cleanly (if not, that's a new feature, not a configuration). Decide whether scenarios are reachable when slides are on the bench-side monitor or only when BenchVision is.

### 5. Mockups omitted — and features 11 and 12 prove why that matters

Workflow 01 Step 6 calls for mockups as gap-exposure; none exist. Two features — the reset control (feature 11) and the discreet operator scenario trigger (feature 12) — are the highest scope-creep risk in the artefact set because prose lets you describe intent but not surface the design decision.

**Revision direction.** Build textual or sketched mockups for features 11 and 12 before the Workflow 02 handoff. Or downgrade `features.md` entries with "Workflow 02 design decision required before implementation" so it's not silently inherited as an AI invention.

---

## Smaller findings, grouped

### Contradictions with the production architecture

- **UI tab structure**: pre-flight surface (features 4–5) doesn't map to the architecture's four-tab layout (Live / Register / Session / Settings).
- **Pre-flight RED/AMBER/GREEN colours vs channel-identity colours** (pressure light blue, flow teal, etc.) — both are needed; the spec doesn't explicitly separate them.
- **Free tier and certificates**: architecture says FREE tier cannot generate certificates. The demo machine's installed licence tier is not specified; defaulting to no licence file would block certificate generation entirely.

### Unstated assumptions an implementer would invent

- Session history pre-population format (fixture file? seed script? export-import?) and interaction with the architecture's write-once SQLite principle on reset.
- Time, timezone, and locale on the demo machine for certificate timestamps. Pix demos in DE — decimal separator, date format matter.
- The bench profile fixture and test sequence fixture shapes — generic-but-Komatsu-like, or hand-rolled invented?
- Audio: do alarms make noise?

### Demo failure modes not covered

- Monitor disconnection / HDMI cable mid-demo.
- Power blip without UPS.
- N100 thermal throttling in a warm meeting room.
- Operator misfire on the trigger gesture (silent miss vs visible error).
- Wifi on the NUC even though offline-first is claimed.
- Audience language and locale for error states.

### Scope-drift magnets

- A2 (functional licensing tier gating) — "inherits automatically" is true only if the licence file is configured.
- A8 (signed certificates / QR verification) — high prestige for investor demos, very tempting.
- A1 (kiosk loop) — first request from Pix at a trade-stand.
- §C should explicitly add: no audio / sound effects, no signed certificates or QR codes, no auto-loop or self-running mode.

### Operator-experience gaps

- Devon vs Pix UI parity assumes a 5-minute private boot window before the audience arrives — Pix at investor lunch may not have one.
- Licensing reference screen is Pix-oriented; Devon at Komatsu navigating to it in front of workshop personnel is awkward. Should be on a discreet path, not the main UI.
- Reset control needs different baselines for mid-demo reset (instant baseline) vs between-demos reset (potentially different test sequence, different splash, different canned history).

### Legal / partnership concern (structural)

The §10 sign-off line — "Sign-off is by Pix as software owner. Devon's review … is captured separately" — creates structural ambiguity at exactly the gate the partnership signature waits on. Q-D7 (Devon witnesses before or after partnership signature) is the same question. Move from open-question to decision before commissioning, or accept "commissioned" has two definitions (technical by Pix, partnership-acceptance by Devon) and name both.

### Investor-demo translation

Pre-flight gates and the candidate scenarios (pressure spike, calibration drift, sensor disconnect) assume hydraulic-engineer fluency. A Berlin generalist investor reads them less. May warrant an investor-specific scenario candidate (e.g. "audit-trail demonstration: same test, sealed certificate") added to Q-D2.

### Smaller items

- Decision log entry on stochastic anomalies — record the principle (demo wants determinism, training wants stochasticity) more explicitly.
- "Materially stale" describing the full-product spec — borderline-acceptable but worth softening if Devon ever reads the artefacts as part of commissioning. Suggested replacement: "predates the DARCSI rebrand and the architecture synthesis".
- "The simulation looks like a real bench at rest" (feature 2) — define what "at rest" means in simulator data shape (flat with noise? slow drift? step-change idle artefacts?). An implementer will pick one; the pick becomes the demo's signature look.

---

## Exit-condition status

The Workflow 01 exit condition is unmet by v0.1. A v0.2 revision pass that addresses at minimum the five load-bearing findings (and ideally the high-leverage smaller ones too) should be run before the next adversarial pass.
