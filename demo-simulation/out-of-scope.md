# BenchVision Demo Simulation — Out of Scope

> First-class scope document, not a footnote. Every future session — Cowork, Claude Code, or human — reads this before touching `spec.md` or `features.md`. This is the forcing function against silent scope drift.
>
> Created: 2026-05-19 (Unlearn Workflow 01 — Step 5)
> Last updated: 2026-05-19
> Companion: `spec.md`, `features.md`, `decision-log.md`

---

## Reading order

Items below are grouped by reason. **The constraint, the reason, and the post-MVP path** are stated for every item so a future session can tell which deferrals are scoped to time and which are scoped to product strategy.

---

## A. Out of scope — deferred to post-MVP

These belong to the BenchVision product family but are not in the demo simulation MVP. They have known successor paths.

### A1. Self-running showcase loop / kiosk mode

**Not in MVP.** The simulation does not run itself; the operator drives it.

**Why:** The two operator profiles in scope (Devon at Komatsu, Pix at UK/DE investor demos) need narrative control. An always-on demo would dilute that. The audience also benefits from the operator's pacing.

**Post-MVP path:** A "showcase mode" launcher option, anticipated for trade-show and unattended-investor-demo contexts. Layers on top of the operator-driven walkthrough; does not replace it.

### A2. Functional licensing tier gating

**Not in MVP.** The simulation does not enforce FREE / PROFESSIONAL / ENTERPRISE behaviour internally — every demonstrable surface runs at full capability inside the demo, regardless of what the licensing reference screen displays.

**Why:** Tier-gating logic exists in the production Licensing Layer (per architecture synthesis). Re-implementing it inside the demo for commercial-narrative purposes is scope creep that hands non-trivial complexity to the demo machine without changing what prospects see.

**Post-MVP path:** Tier gating is a production-Licensing-Layer concern, not a demo concern. When the production Licensing Layer ships (per `bench-vision/benchvision-architecture-synthesis-2026-05-12.md`), it ships into the same codebase the demo uses; the demo will inherit functional gating automatically if the demo's installed licence file is set accordingly.

**In scope (related):** A *static* FREE / PROFESSIONAL / ENTERPRISE reference screen, accessible from the simulation, for investor-demo use. See `spec.md` §4.

### A3. White-label / branding swap

**Not in MVP.** No functional theme swap, no prospect-logo certificate variant, no per-prospect cosmetic configuration.

**Why:** Functional white-label is a commercial feature, not a demo feature. Building it now would force premature decisions about which customers get which theme, when no customer-specific branding is needed for the demo audience.

**Post-MVP path:** White-label is a first-class production product feature (per architecture synthesis, `ARCH-08`). It ships against the production Reporting Engine and design system.

> **Hard architectural constraint that is in scope NOW, even though the feature is not:**
>
> **The demo must use token-based theming throughout.** No hardcoded colour values in component code; no hardcoded brand strings in component code. Colour and text token references go through the design system. Get this wrong now and white-label becomes a rework instead of a swap.

### A4. Stochastic / probabilistic anomaly injection

**Not in MVP.** Scripted scenarios in `spec.md` §5 are operator-triggered, fully deterministic, and rehearsable. No anomalies fire randomly during a demo.

**Why:** Demo predictability matters more than realism in front of paying-prospect eyes. An unexpected anomaly five seconds into a Pix-led investor demo in Berlin is a worse outcome than a slightly less authentic-feeling simulation.

**Post-MVP path:** Stochastic anomalies make sense in a future operator-training mode where the trainee should be tested under realistic conditions. That is a separable product (likely a separate licensable mode), not a demo feature.

### A5. Multi-user / role separation

**Not in MVP.** Single operator, single session, no role concept.

**Why:** Mirrors the production MVP posture (`docs/spec.md` §15). Adding role separation here would both creep scope and misrepresent the product to the audience.

**Post-MVP path:** Multi-user and role separation is an Edition 2+ production feature. Not a demo concern until then.

### A6. Authentication

**Not in MVP.** No login screen, no session expiry, no user identity.

**Why:** Production MVP has no authentication (per architecture synthesis, UI Layer notes). The demo matches.

**Post-MVP path:** Production authentication when it lands.

### A7. Real DAQ hardware drivers

**Not in MVP.** The demo runs against the simulator driver only. No NI-DAQmx, no Modbus, no real LabJack T7 connection.

**Why:** The demo machine has no real sensors attached. Loading real hardware drivers would be either ineffective (no hardware to read) or actively confusing (drivers in a fail-loop on a demo machine).

**Post-MVP path:** Real drivers exist already in the production HAL driver registry (per architecture synthesis). Switching the demo machine to a real hardware setup is a configuration change, not a code change — exactly the value of the production HAL abstraction. This is also the upgrade path for any prospect who wants to run BenchVision against their own bench post-purchase.

### A8. Cryptographically signed certificates / QR-code verification

**Not in MVP.** The demo PDF certificate is generated by the production Reporting Engine using the same Jinja2 + WeasyPrint path the production product uses, but with no digital signature, no QR-coded verification URL, no public verification endpoint.

**Why:** Cryptographic signing and verification is an Edition 2+ feature per the architecture synthesis (open Q-01, Q-02). Showing a "verified by QR" badge that doesn't resolve to anything would mislead the audience about the current state of the product.

**Post-MVP path:** Edition 2+ Reporting Engine work. The DARCSI-platform certificate-verification network depends on this and is a strategic commercial cornerstone.

### A9. Anomaly-detection AI / Edition 2 Analysis Module

**Not in MVP.** No machine-learning-based anomaly detection, no fault classification, no LLM-based diagnostics in the demo path.

**Why:** Architecturally the Analysis Module is an Edition 2 layer subscribed to the Event Bus (per `bench-vision/memory/design-principles.md` items 8–11). The scripted scenarios in §5 of the spec show *the operator response loop*, not AI-driven detection — and that is the right framing for the demo audience anyway.

**Post-MVP path:** Edition 2 Analysis Module work. May be demonstrated in a future "AI features" demo expansion, separately from the credibility-gate operator loop.

### A10. Plugin marketplace / Procedure Marketplace

**Not in MVP.** No third-party plugins, no sequence library exchange, no remote-test-runner concept.

**Why:** All Edition 2+ per architecture synthesis. Showing these as live in the demo would overstate the platform's current scope.

**Post-MVP path:** Edition 2+ platform work.

### A11. Multi-bench networked installation

**Not in MVP.** Single machine, single bench-side display. No remote test runner, no multi-bench dashboard, no investor-tier installation aggregation.

**Why:** Single-bench is the production MVP shape and the Devon-at-Komatsu shape. Multi-bench is an Enterprise-tier feature with separate architecture.

**Post-MVP path:** Reference Installation Licence (per founding partnership documents) explicitly supports multi-bench networked-suite installations as a future capability. Architectural seam already exists via the Event Bus.

### A12. Mobile / tablet UI

**Not in MVP.** 1920×1080 minimum (1366×768 floor) on a bench-side desktop monitor. No responsive design for phone or tablet form factors.

**Why:** Production UI Layer explicitly defers mobile to Edition 2+ (per architecture synthesis). The demo machine has a fixed-resolution monitor; no responsive work is justified for that surface.

**Post-MVP path:** Mobile UI is a separate product surface in the production roadmap.

### A13. Cloud sync / off-machine data dependencies

**Not in MVP.** No cloud storage, no off-machine backup, no remote data dependencies during a demo session. Offline first.

**Why:** Prospect site networks are unreliable. The demo machine should run identically in a workshop with no internet, in a co-working space with patchy wifi, and in a hotel meeting room in Munich.

**Post-MVP path:** Cloud storage features are a production-product concern, not a demo concern.

### A14. Polished training-mode UX (mode-switcher UI, curriculum content, certification logic)

**Not in MVP.** Within training / demo mode (see `spec.md` §8), the *productised* user experience for general operator training — a user-facing mode-switcher in production BenchVision, a structured training curriculum, a scenario library browser, progress tracking, training-mode completion certificates — is out of scope. The demo machine is permanently configured to training / demo mode and the audience never sees a mode switcher.

**Why:** The architectural decision to ship the simulator as a first-class operator-training capability is locked in MVP (`spec.md` §8); the *productised* training-mode UX is a separable product surface that doesn't serve the demo audience. Building it now would expand demo MVP scope without changing what Komatsu, investors, or distributors see.

**Post-MVP path:** Productised training-mode UX is its own roadmap item and likely intersects with the *Getting Calibrated* commercial direction. The architectural seam is in place — the simulator module is already a first-class shipping component — so the future productised work is additive, not a re-architect.

---

## B. Out of scope — explicit product-strategy exclusions

These are not "deferred to post-MVP" — they are deliberately not in scope of the demo conversation, full stop.

### B1. FF27 / commercial-vision content

**Not in scope, full stop, for the demo simulation.**

**Why:** Per the framing of this workflow brief and the prior moog-willie call-notes (`bench-vision/.../moog-willie-call-notes.md` line 56). Commercial-vision content lives in commercial conversations, not in the demo simulation surface.

**Post-MVP path:** Not applicable. This is a strategy boundary, not a timing one.

### B2. Real Komatsu IP, real customer bench data, real prospect-confidential information

**Not in scope.** No real bench identifiers, no real test-job-numbers, no real performance curves traceable to real component serials, no real prospect names in canned content.

**Why:** Confidentiality and the founding-partnership personal-capacity protection (Devon's father runs Specialised Steering; the partnership documents structurally exclude associated companies from access). Embedding real workshop data in a touring demo machine is the worst possible breach surface.

**Post-MVP path:** Not applicable. Generic worked-example data only, in perpetuity.

### B3. Hardware safety claims beyond what the architecture provides

**Not in scope.** The demo simulation does not claim, demonstrate, or imply hardware-safety guarantees beyond what the production safety layer provides on real hardware.

**Why:** Production safety-monitor responsibilities and boundaries are clearly defined in the full-product `docs/spec.md` §7 and the architecture synthesis. The demo runs against simulated data; it cannot demonstrate *hardware* interlock behaviour. Suggesting otherwise misrepresents the product.

**Post-MVP path:** Not applicable. Safety claims are made about the production system on real hardware; the demo demonstrates the *software* safety layer's response to anomalous data.

### B4. Pricing commitments

**Not in scope.** Specific tier pricing, support tier inclusions, and per-installation contract terms do not appear in the simulation, in the licensing reference screen, or on the certificate.

**Why:** Commercial-pricing decisions are not yet made and are not the demo's job. Showing prices that change later is worse than not showing them.

**Post-MVP path:** Pricing decisions live in commercial-strategy documents, not in the demo.

---

## C. Things to specifically NOT let AI build during demo simulation work

A short list of patterns AI tends to add unprompted, made explicit here so future sessions can recognise and resist them.

- **Do not add user accounts.** Even "just a sign-in stub" — out per A6.
- **Do not add cloud sync.** Even "just an export to email" — out per A13.
- **Do not add a settings page beyond what the production UI Layer already defines.** Demo settings are not a product surface.
- **Do not add analytics or telemetry.** No prospect-demo machine phones home; that is a confidentiality breach.
- **Do not add inline help, tutorials, or guided walkthroughs.** The operator narrates; the UI does not.
- **Do not implement deep PDF customisation.** The Reporting Engine's existing template path is the path; customising it for the demo creates a parallel template that drifts from production.
- **Do not introduce a "demo mode" code branch in the production codebase.** The demo is a *configuration* of BenchVision, not a fork. If you find yourself writing `if demo_mode:`, stop and re-architect via configuration / driver substitution instead.
- **Do not implement a live-mode operator override of real sensor logic.** Operators must never be able to override real sensor readings in live mode — that is a safety violation (ISO 4413 safety-integrity, audit / liability concerns, real-fault-bypass risk). The discreet operator trigger (feature 12) feeds the simulator module only, and the simulator module is only connected in training / demo mode. If you find yourself writing code that lets a live-mode operator alter what a real sensor returns, stop and re-architect via the mode boundary. See `spec.md` §8 for the safety-boundary rationale.
- **Do not add a second design system, theme, or component library "just for the demo".** Token-based theming on the existing design system is the constraint; adding a second one defeats the white-label readiness goal in §A3.

---

## Version history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-05-19 | Initial Workflow 01 Step 5 draft. Captures the explicit out-of-scope structure mandated by Pix's clarifying-question answers and adds Section C as a forcing function against patterns AI tends to invent unprompted. |
