# DARCSI — Platform & Product Overview

> **Living document.** Update this file whenever the vision, product scope, business structure,
> or roadmap changes. It is the single source of truth for what DARCSI is and where it is going.
> Created: 2026-04-24 (as TESTVISION_OVERVIEW.md) · Renamed and reworked: 2026-05-12 · Last updated: 2026-05-12

> **Brand-hierarchy note (2026-05-12).** This document supersedes `TESTVISION_OVERVIEW.md`. **DARCSI** is the over-arching brand, registered to Susan Holder (trading as Design Develop Host / piDev). The earlier "TestVision" framing of the parent brand, and the still-earlier "Calibrated" framing, are historical and no longer current. The *Vision product naming convention (BenchVision, HydroVision, etc.) is retained as the convention for products under the DARCSI platform.

---

## Contents

1. [What is DARCSI?](#1-what-is-darcsi)
2. [The *Vision Product Family](#2-the-vision-product-family)
3. [Design Principles](#3-design-principles)
4. [Business Structure](#4-business-structure)
5. [BenchVision — First Product](#5-benchvision--first-product)
6. [BenchVision Technical Architecture](#6-benchvision-technical-architecture)
7. [BenchVision Development Roadmap](#7-benchvision-development-roadmap)
8. [The Founding Partnership](#8-the-founding-partnership)
9. [Market Context](#9-market-context)
10. [Key Decisions Log](#10-key-decisions-log)

---

## 1  What is DARCSI?

**DARCSI** — Data Acquisition, Reporting, Compliance, Security, Interface — is the over-arching brand and platform under which a family of industrial testing software products is delivered. BenchVision is the first product. Future products will follow the same *Vision naming convention, each targeting a distinct testing vertical, and all sharing the DARCSI compliance and certification framework.

**Headline positioning:** *Now everyone gets to participate.*
**Subhead:** *The compliance standard that scales from repair shop to enterprise. Same certificate. Same authority. You decide how much you need.*
**Domain:** `darcsi.io` (registered)

DARCSI is a software and DAQ platform — hardware agnostic by design. It integrates with any hardware vendor rather than building or selling hardware itself. This keeps the business asset-light, scalable, and free from the manufacturing and supply-chain constraints of hardware businesses.

The strategic insight that distinguishes DARCSI from a conventional DAQ platform: **the certificate is the product.** Every product under DARCSI produces a digitally verifiable, tamper-evident test certificate as its primary commercial output. The bench operator (or whoever runs the testing instrument) is the delivery mechanism. The receiver of the certificate — auditor, insurer, OEM procurement department, regulator, supply-chain manager — is the market. The mechanism that scales DARCSI is the supply-chain mandate: as soon as one major enterprise tells its approved hydraulic suppliers (or pneumatic, or thermal, or any verticalised testing) "going forward, we accept only DARCSI-verified certificates", every operator in that supply chain needs a DARCSI product to stay on the approved list. That is a compliance-standard adoption curve, not a software sales funnel.

The long-term vision is a commercially viable, multi-product compliance platform that gives industrial test engineers and operators real-time acquisition, control, logging, and certified reporting — without expensive proprietary software licences or vendor lock-in — and gives certificate receivers something they can defend.

---

## 2  The *Vision Product Family

All products share the same core DAQ engine and DARCSI compliance framework but are tailored to their domain. The naming convention is consistent: `[Domain]Vision`.

| Product | Domain | Status |
|---|---|---|
| **BenchVision** | Hydraulic test benches | ✅ MVP — first to market |
| HydroVision | Hydraulic systems (broader scope) | Planned |
| AirVision | Pneumatic test benches | Planned |
| ThermoVision | Thermal / temperature testing | Planned |
| ElectroVision | Electrical / electronic test benches | Planned |
| LoadVision | Load / stress testing | Planned |
| *Vision | Any future testing vertical | Extensible |

### Why this architecture works

The *Vision family is both a brand strategy and a software architecture decision — they mirror each other intentionally.

From a **brand** perspective: DARCSI is broad enough to cover all industrial testing verticals without being tied to any single industry, while each *Vision product speaks the language of its specific audience. The DARCSI certificate carries the same authority regardless of which *Vision product produced it.

From a **software** perspective: all products share a common core DAQ engine and certificate-generation pipeline. Adding a new *Vision product means extending the platform, not rebuilding it. The modular architecture — sensor-agnostic acquisition, independent safety layer, YAML-defined test sequences, templated reporting, and (Edition 2+) cryptographically signed certificates — is designed from day one to be replicated across domains.

From a **commercial** perspective: the platform model creates a compelling story for investors and enterprise clients. It is not one product; it is a scalable compliance ecosystem. Each new *Vision product adds revenue with lower marginal development cost than the one before it, and contributes to a single growing certificate-verification network.

> **Investor narrative note (2026-05-27).** The Edition 2/3 verifiable certificate story — QR code → verification URL, tamper-evidence, cryptographic signing — is the same trust play that defines Dimensions AI (Digital Science) as a platform: *trusted, linked, verifiable data*. Dimensions is a substantial enterprise platform built entirely on that credential. Our verifiable certificate is that play applied to industrial compliance. When presenting the Edition 2/3 roadmap to investors, lead with this parallel: the category exists, it scales, and nobody has built it for industrial test certification yet. That is the whitespace.

---

## 3  Design Principles

These principles apply to every *Vision product and to the DARCSI platform itself.

**Safety first, always.**
On an industrial test bench, software failure can cause equipment damage or physical harm. Every *Vision product must treat safety as the highest-priority architectural concern, not an afterthought. Safety logic runs independently of all other systems. Licensing failures degrade to free tier silently — they never crash a live test.

**Modular by design.**
Each layer has a single responsibility. Each layer can be built, tested, and replaced independently. No layer depends on the implementation of another — only on its interface. All inter-layer communication flows through a single Event Bus.

**Hardware agnostic.**
The acquisition layer presents a consistent interface regardless of the underlying DAQ hardware or protocol (NI-DAQmx, Modbus, serial, etc.). Swapping hardware means changing a driver, not rewriting the system.

**Certificate as artefact, not byproduct.**
The certificate every *Vision product produces is the commercial point of the platform. Certificate quality (visual design, ISO field compliance, digital verifiability, white-label support, tamper-evidence) is a first-class product concern, not a downstream report-generation step.

**Open-source stack.**
No proprietary tooling, no vendor licence fees baked into the cost of ownership. Python and TypeScript throughout.

**Complete something every session.**
A working sensor simulator is more valuable than half a complete system. Progress is measured in things that run and can be demonstrated, not in lines written.

**Configuration over code.**
Test procedures, alarm limits, certificate layouts, and licence capabilities are defined in configuration files. Adding a new test type or adapting to a new bench configuration should require no code changes.

---

## 4  Business Structure

### Current status

Operating as a **Sole Proprietor** under Design Develop Host (Susan Holder, trading as piDev). Appropriate for the discovery and early build phase.

### Planned structure

Register a **(Pty) Ltd when first revenue is 3–6 months away.** This is the right moment — early enough to own the IP properly from the first client, late enough to avoid carrying compliance overhead through the build phase.

| Reason for (Pty) Ltd | Detail |
|---|---|
| Limited liability | Personal assets protected |
| Investor ready | Ability to issue shares |
| Credibility | Required by corporate and industrial clients |
| IP protection | DARCSI brand and software owned by the company |
| Tax efficiency | Company rate 27% vs potentially higher personal income tax |
| VAT | Cleaner registration path when threshold reached |

### How to register

- CIPC online at cipc.co.za — approximately R175
- Open a dedicated business bank account on registration
- Transfer DARCSI IP (brand, software, market research and competitive gap-analysis) to the company from day one
- Keep all IP, brand, and structure **completely independent** from hardware partners

### Annual compliance (pre-revenue)

| Obligation | Notes | Cost |
|---|---|---|
| CIPC Annual Return | Due every year | ~R100–R450 |
| SARS ITR14 (company tax) | File even as nil return via efiling.sars.gov.za | Free to file |
| **Total pre-revenue cost** | | ~R500/yr or less |

### When to bring in an accountant

At first client invoice, when applying for funding, when VAT threshold is reached (R1M turnover), when taking on employees, or when distributing profit.

### B-BBEE positioning

DARCSI / Design Develop Host is not currently positioned for public-sector tender work; BenchVision's primary commercial channels are private-sector industrial OEMs and workshops. If public-sector or B-BBEE-driven opportunities arise, a separate verification path (or supplier arrangement with a B-BBEE-rated partner) will be required. Specialised Steering's Level 2 B-BBEE status is decoupled from the founding-partner arrangement (see §8) and would be engaged via narrow, deal-specific supplier agreements rather than partnership restructuring.

---

## 5  BenchVision — First Product

### What it is

**BenchVision** is the first product under the DARCSI platform — a data acquisition, monitoring, and reporting platform for hydraulic test benches. It acquires real-time sensor data, controls proportional valves via PID, monitors safety interlocks independently, logs all test data, and generates a certified PDF test report on completion — automatically, without a technician touching a spreadsheet.

**Product domain:** `benchvision.io` (purchased — not yet hosted)

The first installation is the reference installation operated by Devon Abbot. Devon is the founding partner in a personal capacity (see §8). The reference installation is the first BenchVision-licensed bench; further reference installations may be designated in future as Devon scales the demonstration capability.

### Who it is for

- **Primary users:** Hydraulic engineers and test technicians operating test benches
- **Decision makers:** Operations managers, quality managers, and procurement officers who need certified test records
- **Certificate receivers:** OEM procurement departments, insurers, auditors, supply-chain managers, regulators
- **Initial market:** South Africa (Y1), United Kingdom (Y2), Germany (Y3), opportunistic Italy / Australia / India thereafter

### What it replaces

Manual test recording — clipboards, stopwatches, spreadsheets, and hand-signed certificates. Most hydraulic-testing environments today issue paper or basic-PDF certificates that rely on trust as the acceptance criterion. BenchVision will continue to produce paper and PDF certificates — those are the formats customers, auditors, and procurement systems already operate with — and adds the verifiable layer underneath: digital signature, QR-coded verification link, cryptographic confirmation that the certificate corresponds to this specific test on this specific bench by this specific operator.

### Core capabilities

| Capability | Description |
|---|---|
| Real-time acquisition | 10–500 samples/sec; all configured channels simultaneously |
| Engineering unit scaling | Calibrated conversion from raw signals to bar, L/min, °C, RPM, Nm |
| PID control | Automatic pressure/flow setpoint tracking via proportional valve |
| Safety monitoring | Independent thread, multi-level alarms, E-stop, hardware watchdog, plausibility-bound channel evaluation |
| Test sequences | YAML-defined procedures: Ramp Up → Hold → Ramp Down → Report |
| Live HMI | Nuxt/Vue browser interface (SSE-streamed) — gauges, trend charts, alarm indicators, Start/Stop |
| Data logging | SQLite session files (WAL mode), batched 500 ms writes, fully replayable audit trail |
| Test certificate | Auto-generated PDF — component details, results, pass/fail, calibration refs, signature blocks, performance curve. White-label and DARCSI-branded variants. |

### Technology stack

| Layer | Technology |
|---|---|
| Core logic, acquisition, safety, control, logging, reporting | Python 3.12+ |
| Frontend (live operator UI) | Nuxt 4 / Vue 3 / Pinia / SSE |
| Backend bridge | FastAPI with EventBusBridge (SSE) + REST control endpoints |
| Configuration | YAML (PyYAML + pydantic v2) |
| Data storage | SQLite (WAL-mode session files) — queryable, transactional |
| Reports | HTML+CSS via Jinja2 → WeasyPrint → PDF; matplotlib Agg for performance curves |
| Licensing | RSA-signed JWT, offline-first, node-locked (MVP); Cryptlex migration target at scale |
| Web — marketing pages | TypeScript, HTML5, CSS |
| Hosting (prototypes) | Vercel |

---

## 6  BenchVision Technical Architecture

The system is organised into independent layers with a shared Event Bus as the single transport for runtime data. Each layer has a single responsibility and a defined interface. No layer is built until the contracts it depends on are agreed.

```
┌─────────────────────────────────────────────────────┐
│  UI Layer — Nuxt 4 / Vue 3 frontend                  │
│  SSE-streamed live data, operator control endpoints │
├─────────────────────────────────────────────────────┤
│  Reporting Engine                                    │
│  Jinja2 → WeasyPrint PDF + CSV export                │
│  Operator-triggered (not automatic) on session close│
├─────────────────────────────────────────────────────┤
│  Data Recorder — SQLite session files (WAL mode)     │
│  Batched 500 ms writes; immutable after close       │
├─────────────────────────────────────────────────────┤
│  Test Engine + Pre-flight Module                     │
│  State machine, step evaluation, safety monitor,    │
│  two-gate readiness (digital + physical)            │
├─────────────────────────────────────────────────────┤
│  Hardware Abstraction Layer (HAL)                    │
│  Driver registry, normalised SensorReading stream,  │
│  per-channel watchdog, plausibility bounds          │
├─────────────────────────────────────────────────────┤
│  Configuration System                                │
│  Typed bench profiles, sequences, templates, settings│
├─────────────────────────────────────────────────────┤
│  Event Bus — pub/sub                                 │
│  Single transport; no direct inter-layer imports    │
├─────────────────────────────────────────────────────┤
│  Licensing Layer (cross-cutting)                     │
│  Capability gates, offline-first JWT, FREE default  │
└─────────────────────────────────────────────────────┘
```

### Key architectural decisions

**Event Bus as the single nervous system.** No layer imports another for runtime data. The bus is what enables Edition 2+ features (analysis modules, plugin marketplace, remote test runners) to be additive rather than architectural surgery.

**Licensing degrades silently to FREE.** A bad licence file, an expired licence, a clock-drift bug — none of these are permitted to crash or interrupt a live test. Safety beats commercial enforcement.

**Simulator-first development.** The entire software stack is built and proven against a sensor simulator before any real hardware is connected. Devon's bench is not required until Phase 3.

**Driver abstraction.** The acquisition module presents the same interface whether talking to NI-DAQmx, Modbus, a serial instrument, or the simulator. Changing hardware means changing a driver, not the system.

**YAML-defined sequences.** Test procedures are configuration, not code. A new bench type or test type requires a new YAML file, not a code change. (Future TOML adoption is open for the Edition 2+ Procedure Marketplace where signability and diffability of marketplace-sourced sequences matter.)

**Operator-triggered certificate.** Devon's workflow review is the certificate gate — the system does not auto-emit a certificate on test completion; the operator reviews the live data and requests generation via REST.

> Full layer-by-layer design references live in `claude chats/design-refs/`. The architecture-dependencies tracker (`benchvision-architecture-dependencies.md`) records every cross-layer contract by ARCH-ID and is the canonical source for what each layer expects from each other layer.

---

## 7  BenchVision Development Roadmap

**Estimated effort:** 220–406 hours (midpoint ~313 hours)
**Working pace:** 5–8 hours/week part-time
**Target delivery:** End of 2026

### Phase 1 — Foundation (Milestones 1–4)

| Milestone | Deliverable | Est. hours |
|---|---|---|
| M1 — Sensor Simulator | Realistic fake sensor data: ramps, noise, fault injection. Enables all dev without hardware. | 4–8 |
| M2 — Acquisition & Scaling | DAQ read loop, linear scaling raw → engineering units. Console verification. | 6–12 |
| M3 — Live Display | Web HMI (Nuxt/Vue) with SSE streaming, numeric gauges, live trend chart at 10 Hz. | 10–20 |
| M4 — Data Logging | SQLite session writer with batched 500 ms flush, replay-ready audit trail. | 6–10 |

### Phase 2 — Core (Milestones 5–8)

| Milestone | Deliverable | Est. hours |
|---|---|---|
| M5 — State Machine | Full test sequence: Idle → Pre-flight → Ready → Running → Complete/Aborted. | 16–28 |
| M6 — PID Control | PID with anti-windup, simulated valve output, setpoint tracking, YAML-tunable gains. | 12–24 |
| M7 — Safety Logic | Dedicated thread, YAML alarm limits, multi-level alarms, E-stop, fault snapshot logging. | 16–30 |
| M8 — Reporting | PDF certificate, SQLite-driven query API, pass/fail signatures, CSV export, full traceability. | 10–20 |

### Phase 3 — Integration (Milestones 9–10)

| Milestone | Deliverable | Est. hours |
|---|---|---|
| M9 — Hardware Integration | Replace simulator with real DAQ hardware. Commission all channels. PID tuned on live circuit. | 20–40 |
| M10 — Validation | Full test sequences on reference components. Witnessed safety sign-off. Git release. Docs complete. | 16–30 |

### Phase 4 — Launch

- Reference installation fully commissioned, safety signed off, operator trained
- Founding Partner Agreement signed (see §8)
- Product to market: South Africa first, UK and Germany subsequently
- Commercial licensing model activated; first paying customers

### Current status

> **Discovery / pre-Milestone 1.** HTML prototypes live on Vercel. Proposal and requirements questionnaire complete. Founding-partner arrangement under negotiation as a Proposal (v9.2, in `bench-vision/legal/`) and as a Concept Discussion document (v1, in `bench-vision/`). Formal agreement to be signed only after Phase 3 simulation milestones are demonstrably working.

---

## 8  The Founding Partnership

**Susan Holder** (in personal capacity, trading as Design Develop Host / piDev) and **Devon Abbot** (in personal capacity) are the founding parties to the partnership. Specialised Steering (Pty) Ltd is not a party to the arrangement; the founding work is performed by individuals and the rights and obligations are personal.

The partnership is currently captured in two complementary documents:

- **Founding Partnership Concept (v1)** — `bench-vision/benchvision-founding-partnership-proposal-v1.md`. A less formal, project-proposal-style discussion document leading with the DARCSI positioning and the "certificate is the product" framing. Designed as the entry document for the Devon/Amy conversation.
- **Founding Partner Agreement Proposal (v9.2)** — `bench-vision/legal/benchvision-founding-partner-proposal-v9.2.docx`. The formal legal expression of the proposed terms. Becomes the binding agreement only upon (a) successful simulation commissioning, and (b) execution by both parties of a finalised mutual version.

### Headline structure

**Symmetric IP.** Susan owns BenchVision and all DARCSI IP (code, brand, market research, design rationale, all current and future brand associations). Devon owns any bench designs he develops outside any third-party engagement, as his personal IP estate. Contributions made by either party are in-kind and do not convert into ownership of the other party's product.

**Reference Installation Licence.** Devon receives a personal, royalty-free, non-exclusive, non-transferable licence to use BenchVision on any bench he operates as a Reference Installation, for so long as that bench retains Reference Installation status (i.e., remains available for demonstrations on reasonable notice). Multiple reference installations supported, including multi-bench networked-suite installations.

**Commission economics (strategic-tilt opening positions in v9.2).** Devon earns 15% of net new ARR on BenchVision deals he originates, capped at a 3-year tail with Active Engagement requirement. Susan earns 8% of net invoice on bench-design sales she originates (if Devon pursues a bench-design business), with origination-based aftermarket. A 2% bench-design royalty applies to designs Susan has provided material input to, bounded at 5 years or 50 units. Rates are commercial-range midpoints and intended to settle through negotiation.

**Personal-capacity protection.** Mark Abbot (owner of Specialised Steering, Devon's father) is structurally excluded from the partnership. The agreement bars disclosure of confidential information to employers, family members, or associated companies. Devon indemnifies Susan against any third-party claim arising from his use of resources from any associated entity.

**Pre-product-market-fit asymmetry recognised.** Susan has invested substantial pre-launch resources — extensive market research, competitive gap-analysis, development time, and capital — which Devon is not expected to invest. This is acknowledged in the proposal as foundational to the commission and IP structure.

### Note on the *Calibrated* and *TestVision* references in older documents

Devon previously expressed interest in the brand name *Calibrated* for a separate venture; that interest pre-dates the DARCSI rebrand and is now historical. DARCSI supersedes both *Calibrated* (Devon's earlier suggestion) and *TestVision* (Susan's earlier parent-brand framing). Older documents referring to either are stale and being updated systematically.

---

## 9  Market Context

### The educational vs. industrial gap

The hydraulic bench market spans two very different segments, and BenchVision sits firmly in the industrial one.

**Educational benches** (e.g. TecQuipment H1F Digital Hydraulic Bench) are designed for university fluid mechanics labs. They operate at low pressures (~450 mbar) and low flow rates (~50 L/min), with digital displays for teaching measurement concepts. TecQuipment is the dominant global supplier of this segment. These benches have had integrated digital DAQ for years.

**Industrial test benches** (Devon's reference installation, Komatsu-class clients) operate at pressures up to 500 bar and flow rates up to 300 L/min, testing production hydraulic components — pumps, motors, cylinders — to certifiable standards. Despite the far higher stakes, this segment still largely relies on manual recording: a graph printout from legacy software, followed by hand-produced PDF certificates. That is the gap BenchVision closes.

**What this confirms:**
- The market moved to digital DAQ at the educational level long ago. The industrial end is the laggard.
- BenchVision is not competing with TecQuipment — different segment, different customer, different purpose entirely.
- The H1F's flow resolution spec (0.001 L/s) provides a useful lower-bound reference for BenchVision's own sensor specifications.

### Market sizing (Y3 SOM)

Global TAM for DAQ software ≈ US$1.6B. SAM for hydraulic-bench DAQ specifically ≈ US$160M. Realistic Y3 obtainable: US$1.65M ARR across 37 named accounts in four regions — South Africa (primary, ~$720K), United Kingdom (~$300K), Germany (~$240K), and opportunistic RoW (~$389K combined). See `bench-vision/discovery/market-sizing/` for the full sizing exercise.

### Competitive whitespace

BenchVision targets the upper-left quadrant of modern UX × low TCO — empty among credible commercial products. Open-source DAQ projects (Flojoy, PyView, itom) sit in the same quadrant philosophically but lack domain expertise and commercial support; incumbents (LabVIEW, Dewesoft, HBK Catman, MTS, Moog) fight in the right half over specialisation and breadth. The wedge is "post-LabVIEW modernisation for SMB / mid-market hydraulic test in price-sensitive geographies" — not aerospace certification, not 500-channel structural fatigue. See `bench-vision/discovery/market-sizing/deliverables/03-competitive-positioning.md` for the full positioning map.

---

## 10  Key Decisions Log

Track significant decisions here as they are made. Add a row whenever something that was open is closed.

| Date | Decision | Rationale |
|---|---|---|
| April 2026 | Product name confirmed as **BenchVision** (first product) | Distinguishes product from suite |
| April 2026 | Parent brand confirmed as **TestVision** | Broad enough for all verticals (now superseded — see May 2026 entry) |
| April 2026 | *Vision naming convention adopted for all future products | Mirrors software architecture |
| April 2026 | Domain `benchvision.io` purchased | First product domain secured |
| April 2026 | Business structure: remain Sole Prop, register (Pty) Ltd when revenue is 3–6 months away | Avoids premature compliance overhead |
| April 2026 | Open-source Python stack confirmed | No proprietary licence fees, aligns with target market |
| April 2026 | Simulator-first development confirmed | Removes hardware dependency from build timeline |
| 8 May 2026 | "The certificate is the product" positioning crystallised | Reframes go-to-market from software-sales-funnel to compliance-standard adoption curve |
| 12 May 2026 | **DARCSI confirmed as over-arching brand**, domain `darcsi.io` registered to Susan Holder | Replaces TestVision parent-brand framing and the earlier Calibrated working name |
| 12 May 2026 | Founding-partner arrangement restructured to **personal capacity** (Susan ↔ Devon, not company ↔ company) | Protects against third-party (Specialised Steering owner) claim on partnership IP and rights |
| 12 May 2026 | Founding-partner Reference Installation Licence reframed as **personal, perpetual-contingent on demonstration availability** | Ties licence value to active demonstration contribution; supports multi-bench networked-suite installations for enterprise demos |
| 12 May 2026 | **Concept Proposal** approach adopted alongside formal Founding Partner Agreement | Reframes the conversation with Devon from "sign these terms" to "let's align on principles first"; formal terms follow alignment |
| — | Founding Partner Agreement signed | Open — gate is successful Phase 3 simulation commissioning |
| — | First paying BenchVision customer | Open — Phase 4 |
| — | (Pty) Ltd registered | Open — when first revenue is 3–6 months away |
| — | Revenue share percentages finalised | Open — within ranges; settling through proposal negotiation with Devon |

---

## Appendix — Document supersedence

This document supersedes `TESTVISION_OVERVIEW.md` in this folder. The original is retained temporarily for reference; archive when convenient. Other documents containing TestVision references (the v1.5 Business Setup Reference, the bench-vision design-system "Suite" entry, the bench-vision and claude-chats CLAUDE.md files, the spec.md, the TASKS.md) have been updated as of 2026-05-12 or are queued for update — see `bench-vision/TASKS.md` for the active rework list.
