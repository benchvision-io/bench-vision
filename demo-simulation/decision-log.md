# BenchVision Demo Simulation — Decision Log

> Running record of *why* the spec changed at each iteration. The two-minute habit Workflow 01 Step 10 mandates; the only thing that prevents future-you from second-guessing a choice and silently reverting it.
>
> Created: 2026-05-19 (Unlearn Workflow 01 — Step 10)
> Companions: `spec.md`, `out-of-scope.md`, `features.md`

---

## How to read this document

Entries are append-only, newest at the top. Each entry records:

- **Date** — when the decision was taken.
- **Decision** — what was chosen.
- **Alternatives considered** — what was rejected and why.
- **Rationale** — the reason. This is the load-bearing part — without it, a future session may revert silently.
- **Source** — where the decision came from (conversation, document, observation).
- **Affects** — which of `spec.md`, `out-of-scope.md`, `features.md` carries the consequence.

---

## 2026-06-08 — Positioning: the certificate is the DARCSI layer, not the BenchVision MVP demo

**Context.** Repeated attempts to get Devon to see the compliance certificate as *the product* (rather than "his report") keep failing, for two structural reasons: (a) every conversation frames the cert from the workshop / "your customer" angle, which re-anchors him as the owner of a personal report; and (b) the cert sits inside the MVP, so the framing argument lands squarely on the commissioning critical path. Devon's own words capture the block: *"if the customer doesn't believe my report they can go elsewhere"* — credibility-as-personal-reputation, at workshop scale. He has been shown both sample certificates (training + production) and still reads them as his, not BenchVision's.

**Decision 1 — The certificate is the DARCSI platform layer, not BenchVision MVP demo scope.** To Devon, the MVP is the acquisition-and-grading bench (the live graph, pass/fail — the thing he actually wants). The certificate-as-recognised-standard is reframed as the **DARCSI** compliance layer that comes *later*. This is the existing brand hierarchy made explicit, not a new split: BenchVision = the product Devon commissions; DARCSI = the compliance standard that scales. **Cert engineering continues internally** — this is a framing/sequencing decision, not a descope. The cert leaves the *Devon-facing MVP demo*, never the codebase. Effect: the commissioning gate (and therefore signing) rests on the bench Devon values, not on him accepting the cert philosophy.

**Decision 2 — Language: drop "your customer"; speak at industry scale.** "Your customer" is workshop-scale and competitive — it invites the "they can go elsewhere" reflex (true at that scale) and re-anchors Devon as owner. The certificate is industry infrastructure (cf. MOT testing station, hallmark / assay office, UKAS-accredited test report). Vocabulary moves up a level: *the sector / the industry / a recognised standard / the market*. Competitors holding BenchVision then stops being a threat and becomes the point — a standard only has value if it is widely adopted.

**Decision 3 — The reveal is trigger-based, and the trigger is named: Komatsu.** You cannot argue Devon into the industry view (the "passport in the living room" problem — a passport looks like pointless bureaucracy until you hit a border). A real border teaches it. Devon has stated he wants to **approach Komatsu** — an OEM that will require documented, verifiable compliance evidence a personal report cannot supply. That is the moment he realises the cert's value (this also echoes the 2026-05-11 reframe, where his Komatsu ambition is what prompted "you're talking like a founding partner"). Prepare the cert reveal to land at/around that approach; do not spend it earlier trying to win the argument cold.

**Decision 4 — Sequencing: investors before Komatsu; the MVP-sans-cert is baseline, not pitch.** Pix must approach **investors before Devon reaches his Komatsu moment.** Implication: the full DARCSI compliance-standard story has to be **mapped out now**, so the investor narrative *starts where the MVP ends* — the MVP-without-cert is "in the rear-view mirror" (assumed, behind us, proof-of-build), and the pitch leads with the DARCSI compliance standard (cert-as-product + verification portal + standard positioning). Pitching the bench/logger to investors would commoditise the story; the company *is* the standard.

**Two-audience guard.** "Not MVP for Devon" must not bleed into "not central." Keep the cert **loud in the vision / investor layer** (proposal vision sections + investor narrative) and **quiet in the Devon MVP demo layer**. If it goes quiet in both, the product is commoditised. This also protects against Devon later feeling the goalposts moved — the standard was always in the stated vision; he simply was not required to swallow it to commission a bench. (Note the prior "built exclusively for Devon" misread that Amy raised — the same exclusivity drift; keep the standard explicitly non-exclusive in the vision layer.)

**Alternatives considered.** (a) Keep pushing the cert-as-product argument with Devon now — rejected: it is failing, it entrenches his ownership frame, and it risks the commissioning gate. (b) Descope the cert from the build — rejected: it is the commercial heart and most of what is built; the issue is framing, not engineering. (c) Wait for time to change his mind — rejected: realisation is occasion-based (Komatsu), not time-based.

**Source.** Pix ↔ Claude strategy conversation 2026-06-08, building on Devon's 2026-06-05 voice note and the 2026-06-03 privacy-of-evidence / portal decisions.

**Affects.** `TASKS.md` (new investor-prep mapping action; cert-reveal-timed-to-Komatsu action; "drop 'your customer'" language note). Proposal rework — keep the DARCSI compliance vision loud in the vision sections. Investor / pitch materials — lead with the standard, MVP as baseline. No code change.

---

## 2026-06-05 — Cleanliness traceability code on the cert + calibration cadence (Devon voice note)

Source: Devon **voice note** dated 2026-06-05 17:43 (received 2026-06-03, flood week; hand-transcribed by Pix later — full text in `devon-videos/transcripts/voicenote_2026-06-05_17-43.txt`). Two threads.

### 1. Cleanliness on the cert = a traceability *code*, resolved to the day

**Decision.** The certificate carries a **cleanliness code** (Devon: "a code of sorts on the bottom … cleanliness code x"), not an attempt to print an instantaneous cleanliness figure pinned to the exact second of test. The code resolves to a **date (day / month / year)**; the authoritative cleanliness reading is held in the **particle-counter's own history log** (Devon's instrument is an **ICM particle counter**), retrievable by that date. Granularity is whatever the counter supports — "to the day should be fine."

**Rationale (Devon's, quoted).** "It's difficult to be a hundred percent accurate to how clean the oil was at that exact point in time … but I think to the day, it should be fine. I mean, let's say I tested ten pumps within that day, that does narrow it down. So should we have any warranties, it could be ruled right down to … so we've got traceability **on our side**, which then we trace back to a date." The driver is **warranty-dispute traceability**: the code is the pointer that lets the workshop reconstruct the cleanliness evidence for a given pump if a claim arises. He is explicitly comfortable with day-level (not instant-level) resolution.

**Why this fits the existing design.** Aligns cleanly with the 2026-06-03 (PM) privacy-of-evidence split: the **face** carries the lightweight pointer (code → date), the **supporting document / particle-counter history** carries the detailed cleanliness numbers, released on request. No conflict with "water/temp/cleanliness → supporting only" — the *code* is a face-legal pointer, the *values* stay in supporting.

**Implementation seam.** Cleanliness code becomes a face element (short alphanumeric resolving to run date + counter-history key). Candidate: reuse the QR/run-id identity already going on the face rather than minting a second code — confirm with Devon whether he wants a *separate* human-readable cleanliness code or is happy for the existing run-id/QR to be the single traceability handle. **Do not invent the code format unilaterally** — sample-and-confirm.

### 2. Calibration cadence — flow meter yearly; "what else?" tossed back to Pix

**Decision (partial).** Flow-meter calibration cadence ≈ **annual** — Devon: "that's a standard, that should be done yearly, I would assume" (note the hedge — assumption, not a cited standard). This feeds the `[sensor.<channel>]` `cal_due` logic (decision-log 2026-06-03 (c) §2): a one-year default interval is a reasonable starting assumption for the flow channel, **configurable per sensor**, not hard-coded.

**Genuinely open — back to Pix, not Devon.** Devon explicitly handed the scope question back: "what else would require calibration? You can inform me, I don't know." This is **ours to answer**, not his — the metrology question of which channels in the registry need scheduled calibration (pressure transducer, torque/speed sensing, temperature, the particle counter itself, etc.) and at what interval. Tracked as a new open item in `TASKS.md` (reframed as a Pix/Claude action, since Devon deferred it).

### Affects

- `devon-videos/transcripts/voicenote_2026-06-05_17-43.txt` (new, untracked working transcript).
- `TASKS.md` — cleanliness-code thread captured; new "which channels need calibration + intervals" action (ours, not Devon's); flow-meter annual default noted against the sensor-registry item.
- Sensor registry work (decision-log 2026-06-03 (c) §2): `cal_due` default interval + the cleanliness-code face element fold into that scope.
- **Not yet settled:** whether the cleanliness code is a *separate* code or the existing run-id/QR handle — sample-and-confirm with Devon next contact.

---

## 2026-06-03 (c) — Architectural principles surfaced by the cal/portal brainstorm

Three threads from the post-Devon brainstorm captured as principles. Full scope sketches in `docs/forward-requirements-2026-06-03.md`.

### 1. Offline-first is a product principle, not a workaround

**Decision.** The bench is fully usable without network connectivity. Every run record, certificate PDF, supporting PDF, and audit event is written to local persistent storage the moment it exists, with no network call required to finalise. Network availability is required only for *downstream* surfaces (the customer portal, OEM telemetry push, profile-update pull) — never to complete a test or release a cert.

**Rationale.** Industrial test environments (workshops in metal buildings, mine-site depots, locked-down corporate networks) cannot be assumed online. ALCOA+ requires records to be *Available* — which means eventually retrievable, not always-online. Framing this as a principle (rather than a workaround) makes "the bench is offline-first by design" part of the product story.

**Implementation seam.** All persistence goes through a local store first; an `outbox/` queue of pending uploads is drained by a separate sync daemon when connectivity exists. Sync conflicts are impossible by construction because sealed run records are immutable.

**Affects.** Spec.md (add offline-first to §1 principles when next touched), `forward-requirements-2026-06-03.md` §1, future outbox-sync engine (P2). README touch (added today).

### 2. Sensor registry + calibration tracking is MVP scope (Tier 1)

**Decision.** Each channel in the pump profile carries a `[sensor.<channel>]` block with manufacturer, model, serial, range, signal type, cal cert id, cal lab, cal date, cal due, traceability chain, and an optional local path to the cal cert PDF. The bench reads this at sequencer start; expired cal **refuses to start a graded test by default** (configurable, but the deliberate-setting requirement is not negotiable). Cert rendering:

- **Main face** carries a single-line traceability statement, populated from the registry.
- **Supporting document** carries the per-channel cal reference table.
- **Cal cert PDFs** (when locally available) are attachable to the supporting document, releasable on request.

**Why this earns MVP space.** Without a cal-traceability statement on the face, what we print is a *test report*, not a *certificate*. The pushback to Devon on calibration-on-the-cert (drafted but not sent at time of writing) hinges on this. Building the registry resolves the issue mechanically: the block is generated, not editorial. Setup cost is ~2 hours per bench at commissioning (one-time transcription from existing cal certs); per-test cost is zero.

**Out of scope explicitly:** the bench does not perform calibration (Tier 4 — that's a cal lab function). Smart-sensor self-read (Tier 2) and in-situ verification runs (Tier 3) are P3, not MVP.

**Affects.** `pump_profile.py` (new `SensorRegistryEntry` per channel), `sequencer.py` (startup cal-expiry check; new `ABORTED — CAL_EXPIRED` reason), `certificate.py` (face traceability statement + supporting cal table), `templates/*.html` (face block + supporting table). New tests for the cal-expiry refuse/warn matrix.

### 3. DARCSI customer portal is the long-game online surface (P2/P3)

**Decision (commitment to direction, not scope).** When BenchVision eventually goes online, the first customer-facing surface on `darcsi.io` is a **cert verification reading room** — a public-ish page at `darcsi.io/verify/<run-id>` (or shorter, decided before any URL is committed) reached by scanning the QR on a printed cert. It renders the same `certificate_context()` that built the PDF, tiered as: public verify view (verdict + identity + traceability statement) vs authenticated supporting view (cal details, water, temp, cleanliness, raw trace). The same privacy-of-evidence rule Devon set this morning maps directly onto the portal's two tiers.

**Why decide direction now.** The QR payload decision (this morning, decision-log entry 2 §2) defaults to encoding the run-id today and migrates to a URL when the portal lands. Committing to the URL pattern *now* (even though the portal won't be built for many months) prevents the printed-QR-in-the-field backwards-compatibility headache later.

**Out of scope of THIS decision.** When to build, whether to ship a hash-anchor on the cert face alongside the QR, the exact URL pattern (`/verify/`, `/cert/`, `/c/`), customer auth model. Listed in the priority table in the forward-requirements doc; not committed.

### Source

Conversation between Pix and Claude, 2026-06-03 PM, following Devon's WhatsApp answers earlier the same day. No external source documents — these decisions are derivative of (a) Devon's privacy-of-evidence rule established this morning, (b) the metrology-integrity reasoning behind the calibration-on-the-cert pushback, and (c) the QR payload decision.

### Affects

- `docs/forward-requirements-2026-06-03.md` (new — full scope sketches).
- `TASKS.md` — three new MVP-tier items added (sensor registry + cal check + cert render); three Phase 4+ items added (outbox sync, customer portal, hash anchor).
- `benchvision-app/README.md` — short principles section added (offline-first; cal tracking as foundation; two-layer cert).
- Spec.md — minor touch when next opened to fold offline-first into §1 principles (not done in this session).

---

## 2026-06-03 (PM) — Devon answers (WhatsApp 11:22–11:26): supporting-data privacy, three-number id, cadence "naive POV"

Three follow-up answers to the trimmed batched message of the same morning. Captured verbatim phrases below so the source is traceable.

### 1. Water / temperature / cleanliness / calibration on the cert face — RESOLVED: SUPPORTING ONLY

**Devon (11:22–11:23):**
> "Supporting document. You can add ISO standard to main test certificate but. Oil cleanliness. Calibration certificate. Etc etc should not be available to the customer unless requested."

**Decision.** Two layers on the cert artefact:

- **Main test certificate (face)** — verdict, identity block, characteristic curve, per-band flow, torque (monitored reference). **ISO standard reference** (e.g. ISO 4413 / chart part number) may appear on the face as a method citation.
- **Supporting document** — water content, fluid temperature, oil cleanliness (ISO 4406 code + per-band counts), calibration-certificate references, raw point trace, anything else. **Not shipped to the customer by default; provided only on request.**

This is a privacy-of-evidence rule: the customer gets a clean acceptance certificate; the audit trail exists and is releasable on demand, not pushed by default. It also resolves the ambiguity in the current renderer — water + fluid temp are presently on the face; they move to the supporting document.

**Schema/render consequences (logged, not built):**
- `generate_certificate_pdf` produces **two** outputs per run: `main_certificate.pdf` (face only) and `supporting_document.pdf` (everything else). Both share the same `RunRecord`; the split lives in `certificate_context()` which already separates `channels`, `cleanliness`, `chart_png`, etc.
- ISO-method block on the face is a new optional `method_reference` field on the identity strip (Devon called out "ISO standard" specifically — title plus number).
- Defaults: cleanliness + water + temperature stay rendered into the supporting doc; the face never carries them. No conditional logic — supporting always exists, gating is at the **distribution layer**, not the render layer (we always produce both; the operator chooses what to release).

### 2. Run-id / job-numbering — three numbers, two existing + one new (QR)

**Devon (11:25):**
> "Job number / Test number / QR number / Along with other customer details, example attached."

**Pix clarification 2026-06-03 PM.** The "example attached" Devon referred to **is the morning's SDR-header photo** — no second image. With that constraint the three numbers map cleanly:

- **Job number** = `customer_job_no` (existing on the SDR header, e.g. `JV558563`).
- **Test number** = `assembly_job_no` (existing on the SDR header, e.g. `SSP9710`).
- **QR number** = **new face element to be added.** Not present on Devon's existing SDR header; he is asking for it to appear on the BenchVision certificate. No semantic content specified — i.e. Devon has not said what the QR should encode.

**Decision.** Adopt the two existing job numbers as already captured (no schema change). Add a **single new field** for the QR slot:

- `RunRecord.qr_payload: str` — the string the QR encodes.
- `qr_image_data_uri` rendered at certificate-render time, not stored on the record (deterministic from `qr_payload`).
- **Default QR payload (recommended, pending Devon's confirmation in the next exchange):** the system-internal record id — i.e. the demoted `YYYY-MM-DD-<PROFILE>-NNNNNN` — because (i) it is globally unique within DARCSI, (ii) it round-trips back to the exact run-record if scanned into a future portal lookup, and (iii) it gives the `YYYY-MM-DD-<PROFILE>-NNNNNN` format a clean job (the human-facing numbers being Devon's two) without inventing a fourth number.

**Alternative QR payloads considered:**
- A portal URL (e.g. `https://darcsi.io/cert/<run-id>`) — better customer UX (scan → page) but requires the portal to exist; defer until the portal lands and re-confirm with Devon then.
- `Job number` or `Test number` plain — rejected, not globally unique across customers.
- A composite of `Job + Test + SDR Date` — rejected, brittle and longer than necessary.

**Schema consequences (one line added to the morning capture):**
- `RunRecord` gains: `qr_payload` (str, defaults to `record.id`).
- `certificate_context()` gains: `qr_image_data_uri` (rendered from `qr_payload` at render time, like the characteristic chart).
- Templates: face block adds a small QR cell adjacent to the identity strip. Position/size to be sketched, low-risk.

**Re-confirm-don't-re-ask.** On the next Devon contact, show him a sample with the QR rendered against the run-id and let him object if he wants a portal URL or job-number-pair instead. Do not re-ask cold.

### 3. Certificate point-table cadence — soft signal; settle on band-gridpoints (face) + full trace (supporting)

**Devon (11:26):**
> "If a transducers is 10Hz / I would calibrate it that 0.001Hz = 1 bar / Taking that ratio into account will allow for 1000 readings per test / - I am saying this from a nieve point of view / - not sure if that is how it works."

**Reading of the answer.** Devon is reasoning about acquisition resolution, not the printed point-table — and is explicitly flagging he isn't sure how it works ("naive point of view, not sure if that is how it works"). The numbers don't quite line up as a calibration formula (Hz and bar are different units), but the intent is legible: he wants enough resolution that fine pressure changes are captured (~1000 readings per test). That is **already what we acquire** (10 Hz × a ~100 s test → ~1000 samples) — so the acquisition cadence settled 2026-05-30 already satisfies the resolution he's reaching for.

**Decision.** No change to acquisition cadence. For the **printed face**, default to **band-gridpoint rows only** (option (a) from the batched draft) because (i) Devon expressed no preference for the printed cadence, (ii) 1000 rows on a customer-facing PDF is unreadable, and (iii) it fits the privacy-of-evidence rule from §1 above — the full trace exists, just not on the cert. The **supporting document** carries the full 1 Hz operator-display series (≈100 rows) and the per-tick 10 Hz trace is available on request.

**Re-confirm rather than re-ask.** When the example image (§2) arrives, surface the gridpoint-only face layout in passing so Devon can object if he wants something denser — but do not re-ask the cadence question cold.

### Source

Devon WhatsApp screenshot, 2026-06-03 11:22–11:26 (single screenshot capturing four message bubbles, sent in reply to the trimmed batched draft). Verbatim phrases quoted above.

### Affects

- `run_record.py` — `test_number`, `qr_payload`, `qr_image_data_uri` provisional fields (do not build until "example attached" arrives).
- `certificate.py` — split into `main_certificate` + `supporting_document` render paths sharing one `certificate_context()`; optional `method_reference` block on the face; QR rendering (provisional).
- `benchvision-app/templates/` — new `supporting_document.html` template; face templates drop water/temp/cleanliness, gain method-reference + QR slot.
- `TASKS.md` Devon open points — water/temp **closed** (supporting only); cadence **closed** (face = gridpoints, supporting = full trace); run-id **narrowed** (waiting on example).

### Still open

- QR payload semantics — provisionally the system-internal run-id; confirm with Devon by showing a sample, not by asking cold. May upgrade to a portal URL once the DARCSI customer portal lands.

---

## 2026-06-03 — Devon answer (SDR header photo): job-numbering scheme + customer/DUT face fields

**Decision.** Adopt Devon's existing SDR header block verbatim as the certificate-face identity strip. Two outcomes:

1. **Run-id / job numbering — RESOLVED.** Devon's shop uses **two** alphanumeric job numbers, both of which belong on the face as first-class fields:
   - `customer_job_no` — customer-side reference, free-form alphanumeric (e.g. `JV558563`)
   - `assembly_job_no` — internal repair-shop assembly reference (e.g. `SSP9710`)
   The provisional `YYYY-MM-DD-<PROFILE>-NNNNNN` format is **demoted to a system-internal record id only** — it remains the unique key for storage and audit lookup but is **not** the human-facing number on the certificate. The two job numbers carry the human-facing identity.

2. **Certificate face — customer + DUT block confirmed.** The header fields Devon expects, in his order:
   - **Job side:** SDR Date · Customer · Customer Job No · Assembly Job No · Name of Inspector
   - **DUT side:** Machine Model · Component Model · Component Part Nr.
   "Machine Model" is the **parent machine** the unit came out of (e.g. `Liebherr – LTM1050-1` mobile crane); "Component Model" + "Component Part Nr." identify the unit under test (e.g. `LPV 140 Hydraulic pump`). Both must render even when blank — the layout is a fixed block, not conditional. Date format is `YYYY/MM/DD`. "Inspector" is Devon's term for the operator role.

**Schema consequences** (recorded; not built this entry):
- `RunRecord` adds: `customer` (str), `customer_job_no` (str), `assembly_job_no` (str), `sdr_date` (date, `YYYY/MM/DD` render), `machine_model` (str), `component_model` (str), `component_part_no` (str).
- `RunRecord.operator` keeps its name in code but the **certificate face** label reads `Name of Inspector` (label-level rename, not a schema rename).
- `RunRecord.po_number` — keep optional; Devon's header has no PO field, so do **not** put it on the face. Customer Job No carries the customer-side reference.
- `certificate_context()` adds an `identity_header` group exposing all eight fields in Devon's order; templates render the two-table header block before the verdict strip. Blank fields render as blank cells (Devon's sheet does this).

**Still genuinely open (do NOT close yet):**
- **Water content and fluid temperature** — on the face, or supporting only? (Devon's "so far" suggests more to come; not in the header block he sent.)
- **Component serial number** — Devon's header shows Part Nr. but no serial slot; need to confirm whether serial belongs on the face elsewhere or only in supporting data.
- **Point-table cadence (Q1)** — per-band, per-second, or per-step. Still awaiting.

**Alternatives considered.** Keeping `YYYY-MM-DD-PROFILE-NNNNNN` as the face id (rejected — Devon's two-number scheme is what his paperwork carries; matching it removes the cross-reference friction). Inferring a single "job number" by concatenation (rejected — they have different meanings; customer-side vs internal-assembly traceability).

**Source.** Devon WhatsApp photo of SDR header, 2026-06-03 (sent in reply to the cadence/run-id/face-fields batched question of the same day; draft at `docs/devon-batched-questions-2026-06-03.md`). Caption: "Customer details and job number."

**Affects.** `run_record.py` (schema additions per consequences above — not yet built), `benchvision-app/certificate.py` `certificate_context()` (identity_header group), `benchvision-app/templates/*.html` (header block render), `TASKS.md` (Devon open points: Q2 closed, Q3 narrowed to water/temp + serial, Q1 still open). No change to verdict logic, no change to formula engine.

---

## 2026-06-02 — Branch consolidation: M1 + §9A hygiene merged to `main`, strays retired

**Decision.** Consolidated the unmerged stack and stray refs into a single clean `main` carrying all reviewed M1 work **plus** the §9A repo-hygiene, with no commit or stash lost and **no force-push anywhere**. Final `main` tip: **`d64276c`** (suite green, 127 tests).

- **M1 onto `main` by fast-forward.** `main` (`9eec3b8`) was a linear ancestor of `feat/m1-sequencer` (`98e0b2e`), so a plain `--ff-only` advanced it — cleanliness → run-record → certificate → sequencer all land linearly. Chose ff over `--no-ff` because the feature commits are individually reviewed and named; the hygiene merge below already gives the one visible consolidation marker.
- **§9A hygiene reconciled by a real `--no-ff` merge** of `chore/repo-hygiene` (`286ecbc`, which was based on the *old* `main`). `.gitignore` and the new `DARCSI_OVERVIEW.md` auto-merged; **CLAUDE.md conflicted and was hand-resolved**. The chore commit itself shipped *stray conflict markers* committed into CLAUDE.md (empty "Updated upstream" side around an §8A-DRY block) — these were stripped, not carried. Resolution **kept both sides**: feature-line base (§2 deliverable table + the 4-item §8A "close the loop on finished work") **+** the chore's §9A publishing policy **+** the chore's §10/§10A tracking model (which corrects the stale "shared task tracking in `ticketrr/TASKS.md`" line and the project naming → per-project `TASKS.md` is authoritative). One internal tension surfaced and then **resolved same day** (commit `4fda2c8`): the restored §2 table was a hand-maintained status overview, which §10A says to *generate*, not hand-maintain — Pix's call was to defer §2 to `TASKS.md` (keeping only the stable phase/stage), making the doc consistent with the convention it now carries.
- **`.gitignore` gap closed.** The chore's `*.pdf` rule caught the certificate but not the run-record JSON / PNGs under `benchvision-app/demo-output/`; added `benchvision-app/demo-output/` so all generated demo run artefacts stay untracked (brief §5).
- **Branches retired** (each only after `git branch --contains` confirmed its tip reachable from `main`): the stray `feat/sequencer` (= `286ecbc`, local + origin), `feat/run-record`, `feat/certificate` (local + origin), `feat/m1-sequencer`, `docs/2026-06-01-tracker-catchup`, and `chore/repo-hygiene`. `origin` now carries **only `main`**. This closes the "stray `feat/sequencer` left for separate reconciliation" note from the sequencer entry below.
- **Stashes resolved, both dropped after inspection.** `stash@{1}` ("repo-hygiene: gitignore + §9A + overview") — its `.gitignore` was byte-identical to `286ecbc` and its §9A is now on `main`; nothing unique → dropped. `stash@{0}` ("stray CLAUDE.md") — its only hygiene content (§9A) is already on `main`, and applying it would *regress* CLAUDE.md (strip the 4-item §8A, revert §10 to the stale tracking line); nothing unique → dropped.
- **Safety net.** Lightweight local tags `backup/pre-consolidation-m1` (`98e0b2e`) and `backup/pre-consolidation-hygiene` (`286ecbc`) preserve both retired tips for revert; not pushed. `main` pushed to `origin` by plain fast-forward (`9eec3b8..d64276c`).

**Alternatives considered.** `--no-ff` for the M1 advance (rejected — redundant merge bubble; ff keeps the reviewed chain linear). Clobbering one CLAUDE.md side (rejected — brief required keeping both the §9A policy and the feature-line notes). History scrub / `git rm --cached` of already-committed IP docs (rejected — out of scope and contrary to §9A's "no history scrub").

**Rationale.** A single `main` that carries every reviewed commit + the forward `.gitignore` guard, with strays and stashes gone, makes the repo state legible again and prevents finished work being re-dispatched off a stale branch. No history was rewritten, so `origin` stays append-only.

**Source.** Branch-tidy brief (Cowork, 2026-06-02) + read-only audit of the ref graph, stash blobs, and the chore's committed CLAUDE.md.

**Affects.** `CLAUDE.md` (§9A + §10/§10A now on `main`), `.gitignore`, `TASKS.md`; no `spec.md` / `features.md` / `out-of-scope.md` consequence.

---

## 2026-06-02 — The test sequencer: state machine + RunRecordBuilder + end-to-end demo

**Decision.** Built the **test sequencer** — the connective tissue that turns the pieces already built (channels, run record, cleanliness, certificate) into one runnable end-to-end flow. New `benchvision-app/sequencer.py` + a `RunRecordBuilder` in `run_record.py` + `benchvision-app/run_demo.py` + `tests/test_sequencer.py` (**20 tests; suite 107 → 127, green**). Built on branch **`feat/m1-sequencer`** off `feat/certificate` (see the branch-hygiene note below). One `run_demo.py --fast` now produces, from a single run: the graphs, the assembled `RunRecord` JSON, and a training-marked certificate PDF.

- **State-machine shape.** `IDLE → PRE_FLIGHT → RAMP → MEASURE → COOLDOWN → CLEANLINESS → COMPLETE`, with **ABORT** reachable from any active state on a fault (curriculum Day 17). The sequencer **orchestrates, never re-implements physics**: phase transitions are keyed off the simulator's own `pressure.cycle_phase`, and it drives the existing `start_test` / `tick` / discrete `run_cleanliness_*` steps rather than replacing them.
- **`RunRecordBuilder` lives in `run_record.py`**, next to the frozen `RunRecord` it seals — this resolves the 2026-06-02 *build-up-then-freeze* forward note. The builder is mutable, accumulates `ChannelResult`s + `CleanlinessResult`s during the run, and `finish()` emits the frozen record. It holds **no judgement of its own**: grading is decided in the sequencer and the honest four-state verdict still falls out of the frozen `RunRecord` (verdict logic untouched — its 31 tests undisturbed).
- **Provenance / live-mode seam kept clean (forward-requirements §1).** Values are read through a `ChannelSource` that **declares its own provenance**; the sequencer records *whatever the source declares* and never hard-codes `derived`. `SimulatedChannelSource` reads a sim channel and declares `provenance="derived"` + the formula id **taken from the profile (public)** — no reach into the channel's private `_formula_ref`, no edit to `bench_simulator.py`. A future `LiveChannelSource` declares `measured` with no formula; the sequencer is unchanged. A test proves it: swapping in a measured source makes the recorded results carry `provenance="measured"`, `formula=""`. Grading *policy* (flow-vs-band, torque-as-reference) stays in the sequencer, where it belongs.
- **Flow grades; torque is a monitored reference** (2026-06-01). Each captured operating point records a graded flow result (`passed` vs `band.limits_at(p)`) and a `graded=False` torque result. The run PASSes only if every flow point passes; the verdict ANDs them.
- **Gridpoint capture, smoothed.** Graded points are captured at the **flow band's own gridpoint pressures** (excluding 0; up to the 380-bar certified ceiling) — chart-faithful and bounded, vs a fixed time cadence that invites spurious near-edge fails. Each point is the **median over a short window of ticks** straddling the gridpoint, so the DAQ's ~3 L/min Gaussian noise can't flukily fail a good pump. The full-resolution waveform for the plots is captured separately, **un-smoothed**, via the demo's `on_tick` hook.
- **Stepped vs real-time = one loop, one flag.** A single `realtime` bool gates one `time.sleep(dt)` per tick; the state logic is identical either way. Stepped (default) runs instantly for tests and quick generation; real-time (~110 s) paces the screen recording. **No test enters the sleep path** — one test makes `time.sleep` raise to prove it.
- **Honest abort → INCOMPLETE (no new verdict machinery).** A fault stops the run safely and still emits a `RunRecord`: the captured points are kept as evidence and one **graded-but-unevaluated** flow result (`graded=True, passed=None`) is appended, so the existing verdict logic reads **INCOMPLETE** with a note, never a silent pass. The abort reason is recorded in `notes`. An audited abort is a real outcome (the five-step intervention story).
- **Cleanliness staging.** Only the as-left **`unit_outlet`** reading grades toward the verdict; the pre-flight **`rig_supply`** and the as-found **`incoming_fluid`** are recorded-only context/evidence (`verdict=None`), matching the certificate's as-found/as-left comparison logic.
- **Pinned demo seed.** `run_demo.py` defaults to `--seed 1000`, **verified to yield an all-points-pass run** so the shared artefact is reliably a clean PASS; `--seed`/an injected fault produce a FAIL/abort for contrast.

**Alternatives considered.** (a) A fixed time-cadence capture — rejected for gridpoint capture (chart-faithful, bounded, no spurious near-edge fails). (b) Putting the builder in `sequencer.py` — rejected: it belongs beside the frozen type it seals (DRY, and it's the documented forward note's home). (c) Hard-coding `provenance="derived"` in the sequencer or reaching into `_formula_ref` — rejected: that would defeat the live-mode inversion; the source declares provenance, the profile supplies the formula id. (d) Teaching `RunRecord.verdict` an "aborted" state — rejected: the existing INCOMPLETE machinery already models "meant to grade but couldn't", so an abort reuses it without touching tested logic. (e) Grading `incoming_fluid` against the unit's target — rejected: as-found is evidence, not the unit's pass/fail (it would fail a dirty-in/clean-out repair that is exactly the success story).

**Provisional / not fabricated.** No quantities invented; flow is graded only against the profile's digitised band, torque stays recorded-as-reference, cleanliness grades only against the profile's (provisional) cleanliness target and degrades to recorded-only where appropriate. The pinned seed changes *noise realisation only*, not the physics. **No new Devon questions** — cadence, run-id numbering and certificate face-fields remain the queued items; **rig-supply-as-hard-gate** is treated as a *documented design assumption* (advisory/recorded-only until he says otherwise), deliberately **not** a re-ask.

**Branch hygiene note (non-destructive).** The intended `feat/sequencer` name was already taken by a pre-existing remote branch sitting on the divergent repo-hygiene lineage (`286ecbc`, the §9A chore) with no sequencer work. Rather than force-push over it mid-build, this work was branched as **`feat/m1-sequencer`** off `feat/certificate` (`0a15981`). The stray `feat/sequencer` and `chore/repo-hygiene` are left untouched for a separate, deliberate reconciliation; a stray working-tree CLAUDE.md edit from that other session was stashed, not discarded. Reconciliation should confirm `286ecbc` lives on `chore/repo-hygiene` before anyone deletes/force-pushes the stray branch.

**Out of scope (unchanged):** live HAL drivers (seam kept clean for them), the SQLite layer (the `RunRecordRepository` Protocol is the seam; `JsonFileRunRecordRepository` used), the Nuxt UI, the signature ceremony/roles model, and any change to the formula engine / profiles / acceptance values (read-only).

**Source.** Session 2026-06-02 (Pix as engineer-of-record); session-starter `benchvision-code-session-starter-sequencer.md`; `docs/forward-requirements-2026-06-02.md` §1/§2; decision-log 2026-05-19 / 2026-05-30 / 2026-06-01 / 2026-06-02 (run record + certificate).

**Affects.** New `benchvision-app/sequencer.py`, `benchvision-app/run_demo.py`, `tests/test_sequencer.py`; `run_record.py` gains `RunRecordBuilder` (+ `__all__`). Generated artefacts (`demo-output/` JSON+PDF, waveform/characteristic PNGs) are left in the working tree for eyeballing, not committed (on this branch the §9A `.gitignore` PDF guard is absent — so they were deliberately not staged). `TASKS.md` — sequencer/state-machine item (forward-requirements §2) closed. **Next:** the first live HAL driver (P0) — even one real sensor proves the substitution architecture the sequencer's `ChannelSource` seam was built for.

---

## 2026-06-02 — Certificate generation: Jinja2 + WeasyPrint, context/render/pdf split, honesty-first

**Decision.** Built **certificate generation** (`benchvision-app/certificate.py` + `templates/` + `tests/test_certificate.py`, 30 tests; suite **77 → 107**, green) — the headline deliverable ("clipboard to PDF, with an audit trail"). A certificate renders a `RunRecord`. Built on branch `feat/certificate`.

- **HTML→PDF engine = Jinja2 + WeasyPrint, confirmed working in this env.** The spec names them and nothing in the decision log/sketches conflicts. WeasyPrint's Python wheel installs cleanly but needs native libraries (Pango/Cairo/GObject) that were absent; resolved with `brew install pango` (pulls glib, cairo, harfbuzz, fontconfig, gdk-pixbuf). A hello-world HTML→PDF then rendered (and the full `render_pdf` smoke test passes). Pinned `jinja2==3.1.6` + `weasyprint==68.1` in `requirements-dev.txt` with the brew note. Engine choice was put to Pix as a checkpoint, not switched unilaterally.
- **Three-layer split** (mirrors how `cleanliness.py` separated pure helpers from the driver): `certificate_context(record) -> dict` is **pure** — no Jinja, no matplotlib, no I/O — and is where *all* the judgement lives (the bulk of the tests point at it); `render_html(context) -> str` is Jinja2 with **one template per `certificate_class`** (acceptance_certificate / test_report / characterisation_record, each extending `base.html`); `render_pdf(html) -> bytes` is WeasyPrint. A `generate_certificate_pdf` composer builds the chart, injects it, and runs the chain.
- **The four honest states are surfaced verbatim from `RunRecord.verdict`** (PASS / FAIL / NOT GRADED / INCOMPLETE). The load-bearing rule — *an INCOMPLETE or NOT-GRADED run must never render as a clean pass* — is enforced by a single `overall.is_pass` flag that is True only for an exact PASS; every pass-styled element in the templates (green banner, ✓ glyph) is gated behind it. Tests assert INCOMPLETE/NOT-GRADED never set it.
- **Training mark** (2026-05-19): a `mode == "training"` run gets a diagonal "TRAINING · NOT FOR PRODUCTION USE" watermark on every page plus a header chip — visibly non-production.
- **Torque renders as "monitored reference", never a verdict** (2026-06-01): driven by `ChannelResult.graded == False`. Flow is the pass/fail truth.
- **Provenance / version-lock** (2026-05-27): each derived value shows its formula id+version; measured values carry none — a historical certificate is reconstructable.
- **Signature seam left, not built.** `acceptance_certificate` renders a clearly-empty signature placeholder with a visible caveat ("evidence, not an accepted result") and carries `accountable_party` (= the operator). No signature is ever fabricated. The ceremony / step-up auth / roles model remain out of scope (profile-authoring sketch).
- **Plot reused, not redrawn.** `bench_dashboard.save_characteristic_curve` was refactored to extract a shared `build_characteristic_figure(...)` core (band + engine reference lines + the existing torque-as-reference logic); the certificate calls it with the run's operating points and embeds the PNG as a base64 data URI. The dashboard's behaviour is unchanged.
- **Cleanliness** shows ISO code + per-band + water/temperature; a recorded-only reading (`verdict is None`) renders "recorded only — not graded"; an as-found (`incoming_fluid`) vs as-left (`unit_outlet`) comparison appears only when both are present.

**Alternatives considered.** (a) A different HTML→PDF engine (headless Chromium, ReportLab) — rejected: the spec names WeasyPrint, the only blocker was a one-line system install, and switching was offered as a checkpoint rather than taken unilaterally. (b) Building the chart inside `certificate_context` — rejected: plotting is not judgement, and keeping the context pure (no matplotlib) makes the bulk of the tests fast and hardware-free; the chart is injected by the composer. (c) A single template with class conditionals — rejected in favour of one template per `certificate_class` extending a shared `base.html`, matching the brief and keeping the class-specific framing (acceptance signature vs PO-anchored report vs "data, not a verdict") legible.

**Provisional / not fabricated.** No quantities invented. The worked-example values (`generate_sample_certificates.py` → `sample-certificates/`) come from the formula engine on the PC200-8 profile, each flow point graded against the digitised band. Water content and fluid temperature are rendered **on the certificate face** as a provisional default — this is the forward-requirements §2 🔧 ("which fields Devon wants on the face; water/temperature shown or supporting-only"), now a queued Devon question, not a settled choice.

**New Devon question (queued, not a re-ask).** Certificate **face fields** — which fields Devon wants on the certificate face, and whether water/temperature are shown there or kept supporting-only (forward-requirements §2 🔧). Batch with the existing cadence + run-id-numbering questions per the ask-devon discipline. (Settled items — serial block, displacement mode, torque-not-graded — are **not** re-asked.)

**Forward note (out of scope now).** Signature ceremony + step-up auth + roles model; measurement-uncertainty (±) per channel and test-method metadata block (ISO 4413 / chart part no.) — only what the record/profile already carry is rendered; calibration/uncertainty fields are a later certificate-trust item (forward-requirements §3).

**Source.** Session 2026-06-02 (Pix as engineer-of-record); session-starter `benchvision-code-session-starter-certificate.md`; `docs/forward-requirements-2026-06-02.md` §2, `docs/test-purpose-schema-sketch.md`, decision-log 2026-05-19 / 2026-05-27 / 2026-06-01 / 2026-06-02.

**Affects.** New `benchvision-app/certificate.py`, `templates/{base,acceptance_certificate,test_report,characterisation_record}.html`, `tests/test_certificate.py`, `generate_sample_certificates.py`, `sample-certificates/` (worked examples). Refactored `bench_dashboard.py` (shared `build_characteristic_figure`). `requirements-dev.txt` gains Jinja2 + WeasyPrint. `TASKS.md` — certificate-generation P1 item closed; cert-face-fields added to Devon open points. **Next:** the real test sequencer / state machine (forward-requirements §2), or the first live HAL driver (P0).

---

## 2026-06-02 — The run record: per-run spine, JSON sidecar, source-agnostic results

**Decision.** Built the **test-run record** (`benchvision-app/run_record.py` + `tests/test_run_record.py`, 31 tests) — the spine that joins which *model* (profile id), which *unit* (`dut_serial`), *why* (purpose), and the resulting *verdicts*. Implements the `test-purpose-schema-sketch` as-is: a self-contained `TestPurpose` value object (`intent` / `repair_stage` / `context`, string-enums validated in `__post_init__`) with the four derived properties (`deviations_expected`, `grades_pass_fail`, `signoff_required`, `certificate_class`); a frozen `RunRecord` carrying the identity fields, `purpose`, a `mode` (training | live), UTC timestamps, and the results. Cleanliness types are **reused** from `cleanliness.py`, not duplicated. Several deliberate design choices, each load-bearing:

- **Serialisation = JSON sidecar, one file per run** (not TOML). A run record is *generated per-run data*, not hand-authored *config*, so the profiles' TOML choice does not carry over. Decisive: stdlib `tomllib` is **read-only** — emitting TOML would need a new third-party writer dependency — whereas stdlib `json` round-trips natively, maps the nested result vectors cleanly (tuples↔lists), and is the natural staging format ahead of the SQLite layer. The sketch's TOML block is kept as a human-readable illustration of the *shape*; the persisted artefact is JSON.
- **Results are source-agnostic** (the live-mode inversion, forward-requirements §1). `ChannelResult` carries *value + pass/fail + provenance* (`measured` | `derived` | `manual`), so the **same** record serves a simulated run (`derived`, with a formula id) and a live run (`measured`, no formula) identically. The record never assumes a value was formula-generated.
- **"Not meant to grade" vs "meant to grade but couldn't" are kept distinct** — this is where a silently-wrong pass would hide. A *monitored reference* (torque, `graded=False`) and a *recorded-only* cleanliness reading (no confirmed target → `verdict is None`) are **legitimately excluded** from the pass/fail gate. An *expected-to-grade* result that could not be evaluated (invalid/missing reading → `passed is None` / `verdict.passed is None`) is **not** excluded — it forces `overall_passed = None` (`RunVerdict` summary `INCOMPLETE`) with a note naming the offending channel. Four honest states: PASS / FAIL / NOT GRADED / INCOMPLETE.
- **Timestamps are timezone-aware UTC ISO 8601** (ALCOA+ contemporaneous); naive or non-UTC values are rejected at construction. `utc_now_iso()` helper provided.
- **Persistence seam left, SQLite not built.** A `RunRecordRepository` Protocol (`save` / `load`) is the seam; only `JsonFileRunRecordRepository` is implemented this session. The SQLite layer is a separate roadmap item.

**Alternatives considered.** (a) Run record as TOML to match the profiles — rejected: read-only `tomllib` would force a new writer dependency for *machine* output, and run records are data, not config. (b) A single `passed: bool | None` with `None` overloaded for both "monitored reference" and "couldn't evaluate" — rejected: that overload is exactly the silent-pass trap; split into an explicit `graded` flag + the verdict evaluator's excluded-vs-ungradeable branch. (c) Embedding `intent`/results in the pump `.toml` — rejected (category error, sketch §1: per-run concept on a per-model artefact). (d) Adding serialisation to `cleanliness.py` — rejected for this slice to keep its 46-test baseline undisturbed; the reading/verdict (de)serialisers live locally in `run_record.py`.

**Provisional / not fabricated.** No acceptance limits or target codes were invented. The **run-id format** (`YYYY-MM-DD-<PROFILE>-NNNNNN`) is adopted from the sketch as a documented default but is **provisional** — flagged as a new Devon question (does his existing process impose a numbering scheme?). Cleanliness `target` remains an open Devon question; the record degrades honestly to recorded-only when no target is confirmed.

**Forward note (out of scope now, recorded so it isn't a surprise).** `RunRecord` is frozen — correct for an audit artefact — but a real run *accumulates* results as the sequencer executes. When the sequencer lands there will need to be a **build-up-then-freeze** step in front of this frozen shape (a mutable builder that seals into the frozen record). Deliberately not built this session.

**Source.** Session 2026-06-02 (Pix as engineer-of-record); `docs/test-purpose-schema-sketch.md`, `docs/contamination-channel-sketch.md`, `docs/forward-requirements-2026-06-02.md` §1/§7. Built on branch `feat/run-record`.

**Affects.** New `benchvision-app/run_record.py` + `tests/test_run_record.py` (suite 46 → 77, green). `TASKS.md` — run-record P0 item closed, run-id-format question added to Devon open points, certificate generation flagged as the recommended next item. No change to existing modules (`cleanliness.py`, `pump_profile.py`, profiles untouched). **Next:** certificate generation (Jinja2/WeasyPrint, forward-requirements §2) — the run record is the spine it renders.

---

## 2026-06-01 — Pump serial block is immaterial; the engine is pump-agnostic (Devon V6)

**Question put to Devon.** Confirm his pump falls in the PC200-8 **#300001–** serial block — the concern being that an earlier serial uses a different performance chart, so the wrong chart could invalidate the acceptance envelope.

**Devon's answer (voice note / Video 6, 2026-06-01).** The chart is "**merely an example**"; "**you can't build a model off an example.**" If the formulation is correct, the software plots *any* pump live from logged **flow / pressure / torque**, so the serial number is "**immaterial**."

**Decision.** Serial-block confirmation is **NOT required**. The PC200-8 Fig.1 chart is a **validation case** — the reference the formula engine was tuned against — **not the model**. The engine is **pump-agnostic**: it derives the live curves from logged sensor data, not from a serial-specific chart. The "which serial / which chart" question is closed for good and must not be re-queued (this is the exact loop the ask-devon discipline exists to stop — he has now answered it in principle more than once).

**Nuance for the record (not a Devon question).** Certifying a *specific* pump still means giving that pump its **own profile / chart** at real-bench commissioning time — a per-profile data point captured when the real bench runs, not a blocker on the engine now. The PC200-8 profile remains the validation profile; further pumps get their own profiles as they are certified.

**Alternatives considered.** Batch the serial-block confirm into the next Devon message (rejected — already answered; re-asking erodes trust and makes the project look disorganised).

**Source.** Devon WhatsApp voice note / Video 6, 2026-06-01; synthesis in `devon-videos/devon-graph-walkthrough-notes.md`.

**Affects.** `TASKS.md` — serial-block item retired from Devon open points; `displacement.mode` is **settled by chart-match, reinforced by Devon's pump-agnostic principle**: machine-adjusted **112 cc/rev × 2000 rpm = 224 L/min** no-load matches the chart's printed **226 / 222** (already validated in the profile and the flow tests), so the profile's `machine_adjusted` setting is confirmed against the sheet. Devon's "displacement is immaterial" principle and the fact that flow is *measured* (not derived) on a real bench are reinforcement, not the primary reason. The only genuinely-open Devon item now is **sample rate / certificate cadence**. No profile or formula change — this confirms the existing pump-agnostic design.

---

## 2026-06-01 — Torque is a monitored reference, not a graded pass/fail channel (Devon V2/V3)

**Decision.** Torque does **not** grade pass/fail. The pump is judged on the **flow** acceptance envelope; the torque curve is a **monitored reference** — the second characteristic plotted against pressure, watched for its rise-then-plateau shape. The chart's separate "Torque Upper Limit" line is therefore **not** transcribed into a pass/fail band, and the zero-width `[acceptance.torque]` (upper==lower==nominal) is the correct, settled design — reframed from "calibration pending" to "monitored reference by design".

**Alternatives considered.** (a) Make torque a graded channel by transcribing the chart's "Torque Upper Limit" + lower line into `[acceptance.torque]` (rejected — the manufacturer sheet carries the line, but Devon, the reference operator, does not grade on it; this is a question of *channel role*, which is his call, not a value tie the chart breaks). (b) Leave the band flagged "pending" (rejected — it isn't pending; it's decided, and the "fails everything by design" label misread as unfinished work, which is precisely the stale-tracker failure §8A now guards against).

**Rationale.** Devon narrates the two channels differently, and the difference *is* the answer. **Flow (V1):** *"here's my lower limit. Here's my upper limit. So as long as I'm falling in between this region, I know I'm good."* — an explicit pass/fail envelope. **Torque (V2):** *"250 bar... roughly 590 Newton meters... 100 bar... about 400 Newton meters plus."* — single readings, one value per pressure, no band. **Torque (V3):** *"as your pressure is increasing, so is your torque, eventually it's going to get to a plateau."* — a characteristic curve, not a tolerance region. The committed walkthrough notes capture the same asymmetry (flow: "the acceptance band is what determines pass/fail"; torque: "the second characteristic on the results view").

**Source.** Devon WhatsApp clips 2026-05-25 — `devon-videos/transcripts/video1_17-28-04.txt`, `video2_17-30-21.txt`, `video3_17-31-48.txt`; synthesis in `devon-videos/devon-graph-walkthrough-notes.md`.

**Affects.** `profiles/pc200-8-hpv95.toml` (`[acceptance.torque]` comment reframed; band unchanged — still zero-width by design), `TASKS.md` (graded-vs-reference item closed). The nominal torque curve and its `[efficiency]`-driven calibration (entry below) are unaffected — they remain the reference being plotted.

---

## 2026-06-01 — Flow acceptance band is the chart's printed limit lines (transcribed + independently re-verified)

**Decision.** The `[acceptance.flow]` polyline above the PC cut-in is no longer interpolated. The two printed flow limit lines on Fig.1 — the dotted **"Upper limit (Reference value)"** and the solid **"Lower limit"** — were transcribed from the clean vector PDF (p.14, rendered at 12–18× via pymupdf, the same method as the 2026-06-01 torque callouts). The band vertices are now the printed round-bracket callouts (MPa : L/min {kgf/cm²}): **UPPER** `(13.6:226){138.2}`, `(23.6:148.5){240.2}`, `(35.2:99.2){358.6}`, `(37.3:94){380}`; **LOWER** `(10:217.1){102.2}`, `(24.2:108.5){249.2}`, `(37.3:59.3){380}`. Rows between callouts are straight-line readings (both lines are straight between their printed points). Lines terminate at **380 bar** (certified maximum); 380→400 is a flat extrapolation, not data.

**Alternatives considered.** (a) Keep the interpolated widths flagged "to confirm" (rejected — the printed lines exist on the chart and are the certificate's pass/fail truth; interpolation was only a placeholder). (b) Invent a symmetric ±tolerance around nominal (rejected — the upper line is an explicit generous "Reference value" that sits well above the lower limit on destroke; a symmetric band would misrepresent the envelope and the brief forbids invented quantities).

**Rationale / validation.** Every callout's MPa value cross-checks against its printed {kgf/cm²} pair to within rounding (1 MPa = 10.197 kgf/cm²); all seven pass, with one documented ~1% loose callout `(24.2:108.5){249.2}` (likely a source typo for ~24.5 MPa — flow 108.5 not in doubt, anchored on its {249.2}=250 gridline). `test_flow_band_tracks_chart_limits` asserts the printed callouts land on the band vertices; 19 unit tests pass. Overlay `demo-simulation/flow_refactor_validation.png` refreshed — printed upper/lower callout markers sit exactly on the shaded band edges, engine destroke curve inside the band across the whole sweep (flow chart RMS 0.74 L/min). **Independently re-verified this session**: page 14 re-rendered and all seven callouts read directly off the chart rather than trusted from the prior transcription.

**Source.** `docs/PC200-8 Main Pump Testing criteria.pdf` p.14 Fig.1 (EEN00038-00, part 708-2L-00500); transcription + verification 2026-06-01; see `pc200-8-chart-digitised-values.md` §3/§5.

**Affects.** `profiles/pc200-8-hpv95.toml` (`[acceptance.flow]`), `tests/test_formula_registry.py` (`test_flow_band_tracks_chart_limits`), `validate_flow_refactor.py` (overlay callouts), `pc200-8-chart-digitised-values.md` §3/§5. No formula version bump (data/profile change only). **Open:** torque pass/fail band is still a deliberate zero-width placeholder — see the follow-on below; Devon serial-block confirm (#300001–) still outstanding.

---

## 2026-06-01 — Torque plateau resolved: nominal reads from printed callouts (~627 Nm), efficiency-vs-pressure curve added

**Decision.** The 2026-05-30 "candid gap" (engine plateau ~515 Nm vs chart) is closed. Working from the clean vector PDF, the printed absorption-torque callout boxes are now legible and each cross-checks against its `{kgm}` pair. Findings: (1) the ~629 Nm trace is the **nominal** curve, **not** an upper limit — the sheet carries separate "Upper limit (Reference value)" / "Torque Upper Limit" lines; (2) nominal **plateaus at ~627 Nm** (240–400 bar), not ~590 — Devon's spoken "590 at 250 bar" was an eyeball read one gridline low. The flat `mech_efficiency = 0.90` is too high and too rigid: a destroking pump's efficiency falls (~0.85 at the knee → ~0.74 at 400 bar). An empirical `[efficiency]` per-pressure curve was fitted so `absorption_torque_from_flow_v1`, fed live flow, reproduces the printed nominal to within ~14 Nm (<2.5%), 0–400 bar. The scalar `mech_efficiency` is retained as fallback only.

**Alternatives considered.** (a) Replace the formula with a digitised torque polyline as the source of record (kept as `[acceptance.torque]` nominal reference, but the efficiency-curve route was preferred so the **formula still generates** the trace from operator-known inputs rather than a lookup table). (b) Force-fit 590 with a single tweaked η (rejected — would miss the climb above the knee and the chart shows ~627, not 590). (c) Bump the formula version (rejected — the function is unchanged; only the per-pressure η it is fed changed, which is profile data).

**Rationale / validation.** `validate_flow_refactor.py` CHECK C now tracks the chart across the whole sweep; `test_torque_tracks_chart_in_full_stroke_region` (50/100/130 → 269/426/519) and `test_torque_tracks_chart_in_destroke_region` (170/240/270/300/400 → 589/621/632/630/630) both pass. The efficiency curve is labelled in the profile as empirical (absorbs Coulomb + viscous friction the ideal P·Vg/2π model omits), **not** physics.

**Source.** `docs/PC200-8 Main Pump Testing criteria.pdf` p.14 Fig.1; torque-callout read 2026-06-01; `pc200-8-chart-digitised-values.md` 2026-06-01 update + §3/§5.

**Affects.** `profiles/pc200-8-hpv95.toml` (`[efficiency]` curve, `[acceptance.torque]` nominal), `tests/` (two torque-tracks-chart tests), `pc200-8-chart-digitised-values.md`. **Open:** whether torque becomes a **graded** channel (transcribe the separate "Torque Upper Limit" + lower line and replace the zero-width `[acceptance.torque]` placeholder) or stays a monitored reference — needs Pix's call.

---

## 2026-05-30 — TorqueChannel onto the engine (derive from live flow), PowerChannel added; dashboard curve de-hard-coded

**Decision.** `TorqueChannel` now derives torque from **live flow** via `absorption_torque_from_flow_v1` — `T = P·(Q·1000/n)·sections / (20π·η)` — with sections, efficiency and rated speed from the profile and pressure/flow read live. The fixed `Vg=95`, `target_torque=575` and the ramp-fraction scaling are gone; the channel now mirrors the pressure cycle and derives every tick, exactly like FlowChannel. A new `PowerChannel` derives `P_hyd = P·Q/600` via `power_from_flow_pressure_v1`. `SpeedChannel`'s rated speed is lifted from the hard-coded 1000 rpm to the profile's `rated_rpm` (2000). `bench_dashboard.py::save_characteristic_curve` no longer hard-codes `245−0.5P`, `P×95/62.8` or the ±15 band — it draws the flow/torque lines from the registry and the acceptance band from the profile's digitised polyline.

**Alternatives considered.** (a) Keep deriving torque from a fixed `Vg` and just swap 95→112 (rejected 2026-05-27 — rescales a straight line that should bend over; can match one of Devon's two torque reads but never both). (b) Feed the torque formula the *live SpeedChannel* rpm rather than the profile's rated rpm (rejected — the flow model is parameterised on a 2000 rpm basis, so during the speed ramp `vg_eff = Q/n` blows up at low n and produces nonsense torque; using rated rpm keeps flow and torque on the same basis). (c) Add Power as a sixth live gauge (deferred — would disturb the demo's fixed five-panel layout and needs a design-system colour Power doesn't yet have; Power is surfaced on the characteristic/"power" curve instead, which is where Devon names it in V2).

**Rationale / validation.** `validate_flow_refactor.py` CHECK C/D + 16 unit tests (all pass). Deriving torque from live flow makes the **plateau emerge from the physics**, not a special case: torque rises linearly through the full-stroke region and lands on the digitised chart at 50/100/130 bar (errors +8/+1/+5 Nm), then plateaus once the pump is on its constant-power line. Power confirms the mechanism — flat at **48.5 kW** for every pressure ≥150 bar (spread 0.00 kW). Overlay: `demo-simulation/torque_power_validation.png`.

> **⚠ SUPERSEDED 2026-06-01 — see the two 2026-06-01 entries above.** The gap is now closed: the printed nominal plateau reads **~627 Nm** (not ~590 — that was an eyeball read one gridline low), and an empirical `[efficiency]` curve in the profile makes the engine track it to <2.5%. The original text is kept below for the record.
>
> **Candid gap — plateau absolute value.** The engine plateaus at **~515 Nm** (the constant-hydraulic-power value); the chart's nominal torque keeps climbing to **~590 Nm** through 130→250 bar before truly flattening. That ~75 Nm (≈13%) gap is real and **expected**: in the constant-power region hydraulic power is flat, so input torque is only flat if efficiency is constant — but a destroking pump's total efficiency *falls* at partial displacement, so absorption torque creeps up. Reproducing that needs an **efficiency-vs-displacement curve**, which is **not in the digitised chart**, so I did **not** invent one to force-fit 590 (per the brief's "no invented quantities"). This is the `pc200-8-chart-digitised-values.md` §5 "plateau absolute value to be calibrated" item, now quantified. Options for Devon's next pass: (a) transcribe the chart's printed torque reference line and add an `efficiency_curve`/`torque_plateau_nm` field to the profile; (b) confirm whether his spoken "590" is the nominal trace or the chart's upper-limit reference line (the digitised doc suspected the latter).

**Source.** Implementation 2026-05-30; physics + digitised torque column from `pc200-8-chart-digitised-values.md` §2–3.

**Affects.** `bench_simulator.py` (TorqueChannel rewrite, new PowerChannel, SpeedChannel rated rpm, BenchSimulator wiring + `derived_channels`), `bench_dashboard.py` (characteristic curve), `validate_flow_refactor.py`, `tests/`. **Open:** plateau calibration (above); flow/torque are modelled at rated speed, so speed-fault coupling (shaft-slip dropping torque) is a deferred refinement — flagged because the fault scenario injects a speed drop the derived torque won't currently follow.

---

## 2026-05-30 — FlowChannel refactored to the formula engine (constants → config, body → registry)

**Decision.** `FlowChannel` no longer holds any pump constants or formula body. It reads a `PumpProfile` (`pump_profile.py`, loaded from `profiles/pc200-8-hpv95.toml`) and computes flow by resolving a named formula from a `FormulaRegistry` (`formula_registry.py`). For the PC200-8 the profile selects `pump_flow_pc_destroke_v1` (flat to the ~130 bar PC cut-in, then constant-power hyperbola `Q = 29120/P`). Adding another pump is now a sibling `.toml`, not a code change. **Torque/Speed/Temperature/Pressure are deliberately untouched this session** — the FlowChannel pattern is the load-bearing decision and is being confirmed before the same shape is applied to Torque/Power.

**Alternatives considered.** (a) Refactor all derived channels at once (rejected — if the FlowChannel pattern needs unpicking, three channels is three times the rework; explicit check-in gate first). (b) Switch FlowChannel straight to the destroke formula with no faithful-refactor baseline (rejected — could not then distinguish "the refactor changed behaviour" from "the physics changed"; see validation below).

**Rationale / validation.** The refactor is proven on two independent axes by `validate_flow_refactor.py` + `tests/test_formula_registry.py` (15 tests, all pass): (1) **Faithful** — the registry's `pump_flow_linear_v1` reproduces the *old* hard-coded `Q = 245 − 0.5·P` **byte-identically** (max abs error 0.0 L/min across 0–400 bar), so the engine is a behaviour-preserving substitution. (2) **Correct** — the destroke model selected for the PC200-8 tracks the digitised chart to **RMS 0.74 L/min**, against **21.6 L/min** for the old linear model (≈29× closer). Overlay: `demo-simulation/flow_refactor_validation.png`.

> **Candid note on the brief's "keep the PC200-8 plot identical" wording.** Taken literally this conflicts with the already-logged 2026-05-27 decision to change the flow *shape* from linear to destroke. Resolved by separating the two claims: the engine is *byte-identical to the old code when given the old formula* (faithful-refactor proof), and the PC200-8 profile *ships the corrected destroke formula* (validated against the chart). The plot therefore changes **on purpose and visibly**, not silently — which is the outcome the decision-log discipline wants.

**Source.** Implementation session 2026-05-30; physics from `pc200-8-chart-digitised-values.md`; approach from the 2026-05-27 entries below.

**Affects.** `bench_simulator.py` (FlowChannel + BenchSimulator), new `pump_profile.py`, `formula_registry.py`, `profiles/pc200-8-hpv95.toml`, `validate_flow_refactor.py`, `tests/`. **Open / next session:** TorqueChannel still hard-codes `Vg=95` and `target_torque=575`; `bench_dashboard.py::save_characteristic_curve` still hard-codes `245−0.5P`, `P×95/62.8` and the ±15 placeholder band — all to be moved onto the profile after the Torque refactor is confirmed.

---

## 2026-05-30 — Sample rate: acquire at 10 Hz, decimate to ~1 Hz for the operator view (configurable per test)

**Decision.** Resolves Devon's open v5 question ("every second… or point one of a second"). Acquire derived channels at **10 Hz**; present a **~1 Hz decimated** trend to the operator. Both live in the pump profile (`[acquisition] sample_rate_hz`, `operator_log_hz`) so a test can override per pump/bench. This formalises what the code already did informally (10 Hz internal tick, 1 Hz history) rather than inventing a new cadence.

**Alternatives considered.** (a) 1 Hz everywhere (rejected — a 30 s pressure ramp at 1 Hz gives ~30 points across 0–400 bar ≈ 13 bar/point; the PC cut-in knee, ~30 bar wide, gets only 2–3 points and renders as a corner-cut, and the torque plateau is read from too few samples to be convincing). (b) 10 Hz everywhere including the operator view (rejected — 300 points across a ramp is past what an operator tracks live and clutters Devon's Excel-style point table; fidelity the eye doesn't use). (c) Fixed, non-configurable (rejected — real benches and pumps differ; a slow thermal test and a fast pressure sweep want different rates).

**Rationale.** What needs resolution is **pressure resolution through the knee and plateau**, which is an acquisition concern, not a display one — so acquire high, display low. 10 Hz gives ~20 points through the cut-in knee (clean curvature) and a well-sampled plateau; ~1 Hz display matches Devon's mental model (one row per reading) and reduces cognitive load. Cost is negligible: 10 Hz × ~6 channels × minutes is kilobytes in SQLite on the NUC, and the LabJack T7 path drives well above 10 Hz, so neither storage nor the real bench is a constraint. **For Devon to confirm:** that 10 Hz acquisition / 1 Hz display matches how he'd want the certificate's point table to read.

**Source.** Devon v5 (`transcripts/video5_17-01-47.txt`, 02:00–02:10); design call Pix ↔ Claude 2026-05-30.

**Affects.** `profiles/*.toml` (`[acquisition]`); `bench_simulator.py`/`bench_dashboard.py` (already 10 Hz tick / 1 Hz history — now config-driven); `features.md` (acquisition-rate note); certificate point-table rendering (later).

---

## 2026-05-30 — Formula registry shape: named, version-tagged, pure functions; custom-mode interface preserved

**Decision.** The curated registry is a `name → FormulaSpec` map. Each `FormulaSpec` carries `name`, `version`, `summary`, `required_inputs`, `output_unit`, a pure `fn(inputs) -> float`, and `provenance`/`author` fields. Configs reference a formula three equivalent ways (`pump_flow_pc_destroke`, `…_v1`, `…@v1`); a versioned reference is encouraged so a certificate's maths is pinned. `registry.evaluate()` validates `required_inputs` are present before calling `fn` — the single choke point the future caution layer (range/unit/monotonicity checks) attaches to. Re-registering a qualified name with a *different* function is refused (bump the version instead). MVP is **in-process Python only.**

**Alternatives considered.** (a) Bare `dict[str, Callable]` (rejected — no version pin, no declared inputs/units, no place for provenance; can't support the certificate-reconstruction or caution-layer requirements). (b) Designing the live sandbox now (rejected — out of scope this session; but see below).

**Rationale.** The signature `(inputs: Mapping[str, float]) -> float` is deliberately what a *custom* user-authored formula would also present, so the registry interface **does not preclude** the gated/named-author/sandboxed custom-formula mode decided 2026-05-27 — a custom formula is just a `FormulaSpec` with `provenance="custom"` and an `author`, version-locked once it has produced a result. This honours that decision without building its UI now (the hooks are present: `provenance`, `author`, version-lock semantics). The unit-conversion constant `62.8` is documented as `TORQUE_BAR_CC_TO_NM = 20π` (physics, not pump nameplate) and stays in code.

**Source.** Implementation session 2026-05-30, against the 2026-05-27 custom-formula and caution-layer entries below.

**Affects.** `formula_registry.py`; `spec.md` §8A; later: caution-layer validators hang off `evaluate()`, custom-mode persistence reuses `provenance`/`author`.

---

## 2026-05-30 — Acceptance band represented as a digitised polyline (per pump), formula+tolerance also supported

**Decision.** For the PC200-8 the flow acceptance band is a **polyline** of digitised `(pressure, upper, lower)` points carried in the profile (`[acceptance.flow]`), interpolated linearly between gridlines. The schema also supports a `formula_tolerance` mode (nominal formula ± tolerance) for pumps specified that way.

**Alternatives considered.** A single global formula+tolerance for all pumps (rejected for PC200-8 — the printed envelope is asymmetric and varies in width across the sweep; a symmetric ±x band would misstate pass/fail). Polyline only, no formula option (rejected — some pump specs genuinely are "nominal ± x" and shouldn't be forced into hand-digitised points).

**Rationale.** Devon's *mental model* is formula-y, but the PC200-8 *certificate is judged against the printed chart envelope* — so for this validation case the digitised points ARE the truth, and approximating them with a formula would inject error into a pass/fail decision. Keeping both representations in the schema lets each pump use whichever matches its manufacturer spec. **Still open:** envelope widths above the PC cut-in are interpolated and flagged in `pc200-8-chart-digitised-values.md` §5 for transcription against the chart's printed limit callouts before pass/fail goes live.

**Source.** Devon v1 (envelope is load-bearing for pass/fail); `pc200-8-chart-digitised-values.md`; design 2026-05-30.

**Affects.** `pump_profile.py` (`AcceptanceBand`); `profiles/*.toml`; `bench_dashboard.py` (replaces the ±15 placeholder, after Torque refactor); `features.md` (acceptance band as first-class data).

---

> **Note (2026-05-27):** The four entries below this line capture a design discussion held *before* Devon's Excel walkthrough video arrives (expected 2026-05-28). The architecture and reasoning are recorded now while fresh — Pix's call, on the basis that editing is cheap and the reasoning is the expensive thing to reconstruct. Exact formula mechanics (the 95→112→127 chain) are confirmed only after the video; these entries are decisions of *shape and approach*, open to refinement on the specifics.

## 2026-05-27 — Test characteristics are a parameterised formula engine, not hard-coded curves

**Decision.** BenchVision computes derived channels (flow, torque, power, etc.) from a **library of named, tested formulas** selected and parameterised by the per-test **configuration file**. The config carries a "pump profile" — theoretical displacement, machine-adjusted flow, rated RPM, pressure sweep, acceptance limits, units — and names which formula each derived channel uses. No pump-specific constants live in channel code. The PC200-8 chart becomes a **validation case** for the engine, not the model itself.

**Alternatives considered.** (a) Hard-coding the formula *and* constants per pump in Python (current state — every pump needs code changes; the trap that produced the 95/112 error). (b) Full free-text formula-in-config evaluated by the engine for *all* tests (rejected as the default — see liability/sandbox entry below). The chosen middle path keeps the maths curated and auditable while making any pump a config change, not a code change.

**Rationale.** Devon's steer (2026-05-27): "it should make zero difference what the displacement is — the graph should formulate itself." His Excel method (formula in a cell, inputs in a column, graph regenerates) is the mental model. Crucially, the *formula* is stable per test type; only the *inputs* vary test-to-test — so parameterisation, not formula-authoring, satisfies the real need. A curated registry also protects the certificate's trustworthiness, which is BenchVision's commercial foundation. Awaiting the video to confirm whether Devon ever changes the formula itself between pump *types* (handled by multiple named formulas) vs only the inputs.

**Source.** Devon's WhatsApp reply 2026-05-27; design discussion Pix ↔ Claude 2026-05-27. See [[BenchVision formula-engine principle]] in memory.

**Affects.** `spec.md` §8A (new); `bench_simulator.py` (FlowChannel/TorqueChannel — lift constants to config, then formula selection to a registry keyed by config); `features.md` (config-driven derived channels); config-file schema design.

---

## 2026-05-27 — Gated "advanced" custom-formula mode with liability on the named editor

**Decision.** A free-text custom-formula capability is offered as an **advanced option**, but gated and bounded so liability sits with the editor, not DARCSI: (a) tied to a **named user account with an advanced/engineer permission** — *not* a shared password, because identity is what makes liability land; (b) an **explicit at-save responsibility acknowledgement**, recorded with name + timestamp; (c) outputs/certificates produced with a custom formula carry a **provenance stamp** ("computed using a custom formula authored by [name], not a BenchVision-verified relationship"); (d) the formula is **version-locked** once it has produced a result, so any historical certificate is reconstructable; (e) it still runs in a **maths-only sandbox** (whitelisted functions, no file/system access).

**Alternatives considered.** A single shared password (rejected — cannot attribute authorship, so liability cannot transfer). No custom mode at all (rejected — Devon/advanced users want Excel-style freedom; also a commercial differentiator). Letting the liability acknowledgement substitute for the sandbox (rejected — see rationale).

**Rationale.** A password gates *access* but does not transfer liability; naming the author + recorded acceptance does. The provenance stamp prevents a custom result being passed off as BenchVision-certified, protecting DARCSI downstream, and reuses the live-vs-training certificate-marking boundary already designed (§8). The sandbox is a **separate** concern from liability: editor accepts "is the formula correct?"; a defect that let a formula touch the filesystem or crash the bench would still be DARCSI's. Good custom formulas can later "graduate" into the verified registry after review. **Caveat (not legal advice):** disclaimers reduce but do not eliminate vendor exposure, especially given an engine/sandbox defect — the acknowledgement wording needs professional legal review before commercial launch; plain-language is acceptable for MVP/discovery.

**Source.** Pix's proposal + design discussion Pix ↔ Claude 2026-05-27.

**Affects.** `out-of-scope.md` (advanced-mode UI is fast-follow, not MVP — but design the hooks now: named-user permission, provenance stamp, audit record); `spec.md` §8A; user/permission model; certificate render path.

---

## 2026-05-27 — Explainable caution layer over formula edits (guardrail, not gate)

**Decision.** Editing a formula triggers an **explainable, deterministic caution layer** that shows the anticipated outcome before commit: (1) **forward-preview** the resulting curve across the pressure sweep, ideally beside the previous one; (2) **range-check against the pump profile** (e.g. "predicts 1900 Nm at 250 bar; reference ~590 Nm — check displacement units?"); (3) **unit/dimensional check**; (4) **physical-plausibility check** (flow non-negative and falling/flat with pressure, torque rises-then-plateaus, power bounded). It **warns, it does not block** — the named editor may proceed. Any shown-and-overridden caution is written to the **audit record**. ML-style "this curve is an outlier vs known-good pumps" is post-MVP and strictly advisory; it must never decide pass/fail.

**Alternatives considered.** A hard gate that blocks non-conforming formulas (rejected — conflicts with liability-on-editor and with legitimate edge cases). An opaque "AI thinks this is wrong" judgement (rejected — erodes trust in a certification tool; cautions must be explainable). No caution at all (rejected — re-opens the silent-wrong-result risk the gating was meant to close).

**Rationale.** The caution is what stops a well-intentioned edit producing nonsense, and the range-check specifically would have caught the 95/112 error automatically. Keeping it explainable and deterministic builds trust; keeping it a guardrail (not a gate) is consistent with liability sitting on the editor — and recording "editor was warned X, acknowledged, proceeded" *reinforces* the liability shift rather than competing with it. The same validator engine later sanity-checks **live** test runs, bridging toward the edge-AI / calibration adjacent-market directions. Build cautions as pluggable validators; the cheap high-value ones (preview, range, units, monotonicity) belong in MVP.

**Source.** Pix's "intelligence/caution" proposal + design discussion Pix ↔ Claude 2026-05-27.

**Affects.** `spec.md` §8A; `features.md` (formula-edit preview + validator set); audit-record schema; intelligence/validator module shared with live-run monitoring.

---

## 2026-05-27 — Pump displacement semantics corrected: theoretical 95, adjusted 112 (Devon)

**Decision.** Correcting the two entries immediately below. Per Devon (2026-05-27), the pump's **theoretical displacement is 95** (the base spec of the HPV95 series, shared across machines — e.g. PC1250-9 is also 95 theoretical). The **112** printed on the PC200-8 sheet is the **machine-adjusted flow** figure for this application, not the theoretical displacement; on the bench, adjusted to machine spec, Devon actually reads ~127. Chain: theoretical 95 → adjusted target 112 → measured ~127. The label "displacement = 112" in the entries below is therefore **wrong**; 112 is a flow-derived figure.

**Alternatives considered.** Silently editing the entries below (rejected — the log is append-only; corrections are recorded, not overwritten). Waiting for the video before recording anything (rejected — the *direction* of the correction is already clear from Devon; only the exact 95→112→127 mechanics await the video).

**Rationale.** My arithmetic (112 × 2000 rpm ÷ 1000 = 224 L/min ≈ no-load envelope) was sound but mislabelled — it confirms 112 is a *flow* figure, exactly as Devon says. **What survives:** the destroke/plateau physics and the decision to derive torque from *live flow* rather than a frozen constant (entry "torque/flow are PC-controlled curves" below) both stand — and in fact align with Devon's formula-based steer, since deriving from live flow is the formula doing the work rather than a baked-in number. Exact mechanics pending Devon's Excel video (expected 2026-05-28).

**Source.** Devon's WhatsApp reply 2026-05-27, cross-checked against the PC200-8 sheet.

**Affects.** `bench_simulator.py` (`PUMP_DISPLACEMENT_CC_PER_REV` — do not simply set 112; model theoretical vs adjusted as profile inputs); `pc200-8-chart-digitised-values.md` (annotated); supersedes the "112 not 95" framing in the two entries below.

---

## 2026-05-27 — PC200-8 manufacturer test sheet located; pump is 112 cc/rev, not 95

**Decision.** The test sheet Devon read out in the 2026-05-25 clips is `docs/PC200-8 Main Pump Testing criteria.pdf` p.14 (Komatsu EEN00038, *Fig. 1 Pump Assembly Performance Specification Chart*, part 708-2L-00500). It was already in the repo. Confirmed as the same chart: all three of Devon's spoken readings (50 bar→220 L/min, 200 bar→145 L/min, 250 bar→590 Nm) sit on it. The pump is **HPV95+95, displacement 112+112 cc/rev** — "95" is the model name, not the displacement. `PUMP_DISPLACEMENT_CC_PER_REV` should be **112**, not 95. Test speed is **2000 rpm** standard.

**Alternatives considered.** Continuing to wait for Devon to send a sheet (unnecessary — it was on disk). Trusting the earlier inference that the sheet would yield ~148 cc/rev (it did not; see below).

**Rationale.** 112 cc/rev validates against the chart independently: 112 cc/rev × 2000 rpm ÷ 1000 = 224 L/min, exactly the chart's no-load envelope (226 upper / 222 lower). The 95 value cannot reproduce that. Full digitisation and drop-in code in `pc200-8-chart-digitised-values.md`.

**Source.** PC200-8 test sheet p.14, read 2026-05-27; cross-checked against `devon-videos/devon-graph-walkthrough-notes.md`.

**Affects.** `spec.md` (pump constants), `bench_simulator.py` (`PUMP_DISPLACEMENT_CC_PER_REV`, FlowChannel model), `bench_dashboard.py` (acceptance envelope). Supersedes the "awaiting Devon's spec sheet" entry of 2026-05-25.

---

## 2026-05-27 — Torque/flow are PC-controlled curves, not linear; a fixed Vg can never fit

**Decision.** Both derived channels must change *shape*, not just constants. The HPV95 is a variable-displacement, power-controlled pump: full stroke at low pressure, destroking past the PC cut-in (~130 bar). Flow is therefore flat (~224 L/min) then a constant-power hyperbola `Q ≈ 29120 / P`, not the current linear `Q = 245 − 0.5·P`. Torque must be derived from **live flow** (`T = P × (Q×1000/n) × N_sections / 62.8 / η_m`), not a fixed `Vg`, so it rises then **plateaus** — the plateau Devon flagged in Video 3.

**Alternatives considered.** Just replacing the torque constant 95 → 112 (rejected: rescales a straight line that should bend over — matches one of Devon's two torque points but never both). Keeping the linear flow fit (rejected: wrong no-load value and wrong high-pressure tail, even though it passes through the two anchor points).

**Rationale.** Fixed-Vg torque gives 178 Nm at 100 bar (single) / 357 (both) and grows linearly; Devon read ~400 at 100 bar **and** ~590 at 250 bar. Only a destroking model reconciles both: full-stroke rise to the PC knee, then constant-power plateau. The code's own docstring already noted `Vg = Q×1000/n` — deriving from live flow makes the plateau emerge for free. This corrects the 2026-05-25 entry's assumption that the gap meant a wrong Vg (~148 cc/rev); the real gap is the destroke, and the nameplate is 112.

**Source.** Physics reconciliation against PC200-8 chart + Devon's video readings, 2026-05-27. Detail and drop-in snippets in `pc200-8-chart-digitised-values.md`.

**Affects.** `bench_simulator.py` (TorqueChannel `_derive_torque` + inject flow ref; FlowChannel `_derive_flow`), `bench_dashboard.py` (envelope + plateau on torque plot). Open: transcribe the chart's printed limit callouts for exact envelope/plateau values.

---

## 2026-05-19 — Devon question logged: legitimate operator diagnostic actions (pending resolution)

**Decision.** A question is open with Devon: *"Are there legitimate operator diagnostic actions in standard hydraulic-test practice that aren't sensor overrides but might look similar — e.g., force-recalibrate of a specific channel, force-zero at a known state, bypass non-safety-critical sensor (like ambient temperature) when broken and the test doesn't require it? If those exist, how are they handled today, and which need to be in BenchVision MVP?"*

**Alternatives considered.** Pre-empting Devon's answer based on general DAQ practice. Conflating these actions with the safety-boundary "operator override" concern (settled in the entry below).

**Rationale.** The safety boundary is settled (no live-mode override of real sensor logic). But standard hydraulic-test practice may include legitimate operator diagnostic actions that aren't overrides and that should be features in their own right. Devon is the domain expert; ask him rather than guess.

**Source.** Pix's escalation during Item 2 review of v0.1, 2026-05-19.

**Affects.** Pending. Resolution may add features to `features.md` (force-recalibrate, force-zero, bypass-non-safety-critical) **or** add an out-of-scope entry if Devon confirms these belong to future BenchVision editions rather than MVP.

---

## 2026-05-19 — Safety boundary: operators cannot override real sensor logic in live mode

**Decision.** Operators must never be able to override real sensor logic in live mode. The architecture enforces this **by construction, not by policy**: the discreet operator trigger (feature 12) feeds the simulator module only; the simulator is only connected in training / demo mode; live mode reads exclusively from real-sensor HAL drivers. A live-mode session and a training-mode session cannot be active simultaneously.

**Alternatives considered.** Allowing operator override gated by license tier or admin role. Allowing override inside a "calibration mode" sub-state of live mode.

**Rationale.** Operator override of real sensors in live mode would violate ISO 4413 safety-integrity principles, bypass real fault conditions (operator decides "that pressure reading is wrong" and overrides, missing a real fault), and create audit / liability problems. Architectural enforcement (the trigger has no live-mode wiring to drive) is more robust than policy enforcement (rules operators are trusted to follow). Pix's instinct check during Item 2 review surfaced and confirmed this concern.

**Source.** Pix's instinct check and Item 2 resolution during v0.1 review, 2026-05-19.

**Affects.** `spec.md` §8 (safety-boundary statement); `out-of-scope.md` §C (new rule "do not implement live-mode operator override of real sensor logic"); `features.md` feature 12 (trigger is mode-scoped).

---

## 2026-05-19 — Simulator reframed as first-class BenchVision module with operator-selectable modes

**Decision.** The simulator is no longer a demo-only artefact. It ships as a first-class part of the BenchVision product and exposes two operator-selectable runtime modes: **live test** (real sensors, production audit trail, real certificates) and **training / demo test** (simulator-driven, runs tagged non-production, certificates marked accordingly or suppressed). The demo simulation is BenchVision running in training / demo mode with scripted scenarios pre-loaded.

This **extends, does not contradict**, the earlier "Simulation is a configuration of BenchVision, not a fork" decision. The configuration boundary moves from "the simulator is opt-in at build / route configuration" to "the simulator is always shipped, mode is selectable at runtime".

**Alternatives considered.** Keeping the simulator as a demo-only configuration with the trigger UI omitted from production builds. Adding a `demo_mode` runtime flag without exposing modes to operators.

**Rationale.** Pix's reframe during v0.1 Item 2 review: if the simulator is a first-class shipping module, BenchVision gains a built-in operator-training capability — a meaningful commercial differentiator (Germany values training credentials heavily; Komatsu benefits from on-bench training without real-hardware risk; the *Getting Calibrated* educational vertical reuses the same engine). The architecture also becomes more honest — no "secret feature only Devon knows about", documented training mode any operator can enter. The *demo's* MVP scope does not expand materially; the *productised* training-mode UX (production-side mode-switcher UI, structured curriculum content, training-completion certification logic) is post-MVP and lives in `out-of-scope.md` §A14. The architectural seam, however, is locked here.

**Source.** Pix's reframe during v0.1 Item 2 review, 2026-05-19.

**Affects.** `spec.md` §5, §8; `features.md` feature 12; `out-of-scope.md` §A14; carries commercial implications for FF27 / *Getting Calibrated* product positioning.

---

## 2026-05-19 — Adversarial-review "substantial finding" rubric defined

**Decision.** A finding from the Workflow 01 Step 7 adversarial review is "substantial" — and therefore blocks commissioning — if it would: (a) change a feature in `features.md`, or (b) change an entry in `out-of-scope.md`, or (c) change a section heading in `spec.md`. Minor copy edits, phrasing improvements, and stylistic adjustments are not substantial.

**Alternatives considered.** Leaving "substantial" undefined and relying on reviewer judgement. Using a different rubric (e.g., effort-estimate threshold, or a numeric severity score).

**Rationale.** The v0.1 §10.4 used "no substantial new findings" as a gate without defining "substantial", making the gate circular and unverifiable. The (a)/(b)/(c) rubric ties the substantial threshold to durable artefact changes — review findings that would force edits to load-bearing documents — which is both objective and aligned with the workflow's structural commitments.

**Source.** Item 1 resolution during v0.1 review with Pix, 2026-05-19.

**Affects.** `spec.md` §10.2.

---

## 2026-05-19 — Commissioning checklist replaces circular success criteria

**Decision.** §10's four success criteria are replaced with a six-item commissioning checklist of independently testable outcomes (§10.1). The checklist is the gate for commissioning; the adversarial-review pass becomes a separate quality gate (§10.2) with its own explicit rubric (see entry above).

**Alternatives considered.** Refining the existing four criteria in place. Keeping the "adversarial pass returns no substantial new findings" framing without defining "substantial".

**Rationale.** Two of the four v0.1 criteria were not testable as written — the "adversarial pass" gate was circular without defining "substantial", and the "rehearsal aids" reference was undefined. Replacing them with concrete, observable outcomes (e.g., "all four must-show capabilities trigger without errors", "zero placeholder strings in audience-facing UI", "15-minute solo end-to-end run") makes the commissioning gate verifiable by a third party rather than by subjective judgement.

**Source.** Item 1 resolution during v0.1 review with Pix, 2026-05-19.

**Affects.** `spec.md` §10.1.

---

## 2026-05-19 — Rehearsal aids removed from success criteria

**Decision.** §10's "without rehearsal aids" reference is removed. Rehearsal aids are not a deliverable of the demo simulation; Devon's domain expertise plus a few self-driven practice runs is sufficient for either operator to drive the demo confidently.

**Alternatives considered.** Defining "rehearsal aids" concretely (e.g., speaker notes, printed operator playbook, in-UI prompts) and keeping them as a deliverable. Rejected as unjustified scope.

**Rationale.** Devon is the domain expert and Pix is the software owner; neither needs formal rehearsal aids to drive a demo of software they each know. The undefined term in v0.1 was a placeholder that masked the absence of a real requirement.

**Source.** Item 1 resolution during v0.1 review with Pix, 2026-05-19.

**Affects.** `spec.md` §10.

---

## 2026-05-19 — Stack reference corrected from Nuxt 3 to Nuxt 4

**Decision.** All references to the frontend framework in `spec.md` are corrected from "Nuxt 3" to "Nuxt 4". Recruitrr and the broader stack are already on Nuxt 4 in production.

**Alternatives considered.** Leaving "Nuxt 3" as written.

**Rationale.** The v0.1 draft inherited a stale framework version from the agent's training data. Nuxt 4 shipped widely fairly recently and the existing project stack is already running it; the spec should reflect actual project state.

**Source.** Pix's correction during v0.1 review, 2026-05-19.

**Affects.** `spec.md` §4, §8.

**Note for future sessions:** framework versions are a category of stale-model-data error worth double-checking against actual project state before locking technical-direction sections.

---

## 2026-05-19 — Workflow 01 Step 1 initial draft

**Decision.** Demo simulation artefact set established: `spec.md`, `out-of-scope.md`, `features.md`, `decision-log.md` at `bench-vision/demo-simulation/`.

**Alternatives considered.** None — this is the workflow's mandated output structure.

**Rationale.** Per `learning/Unlearn/workflow-01-spec.md` revised recipe. The four-document set is the basis Workflow 02 will pick up.

**Source.** Workflow 01 brief from Pix, 2026-05-19.

**Affects.** All four artefacts created.

---

## 2026-05-19 — Operator-driven walkthrough chosen over self-running showcase loop

**Decision.** The demo is operator-driven. The simulation does not run itself in MVP.

**Alternatives considered.** Self-running kiosk loop; interactive sandbox; hybrid launcher. All three rejected for MVP.

**Rationale.** Two operator profiles exist — Devon at Komatsu, Pix at UK / DE investor and distributor demos — each needing narrative control. A self-running loop dilutes that. An interactive sandbox creates demo-failure risk when a prospect explores corners. A hybrid launcher is unjustified scope for MVP. The self-running showcase loop *is* anticipated for trade-show and unattended-investor contexts, but post-MVP.

**Source.** Pix's answer to clarifying Q1, 2026-05-19.

**Affects.** `spec.md` §3; `out-of-scope.md` §A1; `features.md` implementation order.

---

## 2026-05-19 — Three non-negotiable demo properties locked in

**Decision.** The demo must be (1) forgiving, (2) resettable in under five seconds from any state without restart, and (3) modular across three sections (operator view, test execution, reporting).

**Alternatives considered.** Implicit handling of these properties through "good UX" — rejected as too vague to act on.

**Rationale.** Each property maps to a concrete demo-failure mode either Devon or Pix would face in front of a paying-prospect audience. Naming them as non-negotiable forces them into the features list and the commissioning success criteria rather than leaving them aspirational.

**Source.** Pix's answer to clarifying Q1, 2026-05-19.

**Affects.** `spec.md` §3; `features.md` features 11–12; `spec.md` §10 success criteria.

---

## 2026-05-19 — Must-show capability set fixed at four surfaces

**Decision.** MVP demonstrates: pre-flight gate + live operator UI + test sequence execution + certificate generation, plus the session history browser. This is the credibility-gate operator loop.

**Alternatives considered.** Adding functional licence-tier gating; adding functional white-label theme swap. Both rejected for MVP.

**Rationale.** These four surfaces together are the "clipboard to PDF, with an audit trail" story BenchVision exists to tell. Adding either rejected feature into MVP would handicap the demo's clarity without adding new surfaces the credibility audience needs to see.

**Source.** Pix's answer to clarifying Q2, 2026-05-19.

**Affects.** `spec.md` §4; `features.md` features 4–9.

---

## 2026-05-19 — Licensing tier as static reference screen, not functional gating

**Decision.** A static FREE / PROFESSIONAL / ENTERPRISE comparison surface is in scope for the simulation, for investor-demo conversational use. Functional tier gating inside the simulation is out of scope.

**Alternatives considered.** No licensing surface in the demo at all; full functional gating mirroring the production Licensing Layer.

**Rationale.** Investor and distributor audiences benefit from seeing the commercial structure. Implementing functional gating duplicates production Licensing Layer work that will reach the demo automatically once the production layer ships into the shared codebase. A static reference screen gets the commercial-story value without the duplication.

**Source.** Pix's answer to clarifying Q2, 2026-05-19.

**Affects.** `spec.md` §4; `out-of-scope.md` §A2; `features.md` feature 16.

---

## 2026-05-19 — White-label deferred entirely; token-based theming constraint added now

**Decision.** Functional white-label / branding swap is out of scope for MVP. The design system must use token-based theming throughout the simulation and avoid hardcoded brand strings, so functional white-label can be added post-MVP without architectural rework.

**Alternatives considered.** Building a minimal white-label swap as part of MVP; deferring white-label without the token-based constraint.

**Rationale.** Building white-label now is unjustified scope. *Not* enforcing token-based theming now is a load-bearing mistake — it would force a rewrite later instead of a configuration swap. The two halves of this decision are inseparable: defer the feature, but lock in the architectural readiness for it.

**Source.** Pix's answer to clarifying Q2, 2026-05-19.

**Affects.** `spec.md` §6; `out-of-scope.md` §A3; `features.md` feature 17.

---

## 2026-05-19 — Full-drama scripted scenarios via discreet operator trigger

**Decision.** The simulation defaults to a nominal clean run. The operator has a discreet, audience-invisible trigger that fires one of several scripted anomaly scenarios on demand. MVP ships with at least two scenarios — one dramatic, one quieter — for tonal range.

**Alternatives considered.** Nominal only; soft drama only; stochastic random anomalies.

**Rationale.** Operator-controlled drama matches the conversation in the room, which neither nominal-only nor stochastic can do. The five-step intervention loop (detection → alarm → automatic pause → operator notification → intervention → resumed test or audited abort with certificate) is the value-demonstrating story; it needs to be reachable on demand, not by chance. Stochastic anomalies deferred to a separable future training-mode product, where unpredictability is the point of the product rather than a demo risk.

**Source.** Pix's answer to clarifying Q3, 2026-05-19.

**Affects.** `spec.md` §5; `out-of-scope.md` §A4; `features.md` features 12–14.

---

## 2026-05-19 — Hardware spec path corrected; spec anchored on existing `demo-machine-build.md`

**Decision.** The canonical hardware reference for the demo simulation is `bench-vision/hardware/demo-machine-build.md` — at the top level of `bench-vision/`, **not** under `hydraulic testbench software/bench-vision/hardware/` as the session-starter prompt listed. The demo simulation spec is anchored on this existing document. Key extracted constraints: Ubuntu 26.04 LTS, Python 3.14, Node 22+ LTS, NUC-class form factor (target Intel N100 mini PC), 16 GB RAM, 512 GB NVMe SSD, bench-side 1080p monitor.

**Alternatives considered.** Writing a placeholder hardware section in the spec and treating the hardware build as TBC. Rejected once the existing document was located.

**Rationale.** A canonical reference already exists. Re-creating it in the demo-simulation directory would create two sources of truth. The session-starter prompt's path was wrong; the document is at the higher-level `bench-vision/hardware/` path.

**Source.** Pix's correction to clarifying Q4, 2026-05-19.

**Affects.** `spec.md` §7; session-starter prompt at `/Users/sueholder/Development/learning/Unlearn/` references (worth correcting separately).

---

## 2026-05-19 — OS divergence between full-product spec and demo machine acknowledged

**Decision.** The demo simulation runs on Linux (Ubuntu 26.04 LTS) per the demo-machine spec. The full-product `docs/spec.md` §13 lists Windows 10/11 as the production PC target. This divergence is acknowledged but not resolved here — the demo follows Linux, the production OS decision is deferred to a future full-product spec rewrite.

**Alternatives considered.** Forcing OS alignment now by either updating the full-product spec to Linux or constraining the demo to Windows.

**Rationale.** Forcing alignment now is premature. The full-product spec is otherwise materially stale (see next entry); resolving OS as part of a spec rewrite is more efficient than resolving it in isolation. In practical terms, BenchVision is OS-portable — Python 3.14, Nuxt 3, FastAPI, SQLite, Jinja2, and WeasyPrint all run on both — so the divergence is not a blocker for either path.

**Source.** Reading `docs/spec.md` §13 against `hardware/demo-machine-build.md` §2, 2026-05-19.

**Affects.** `spec.md` §7 (notes the demo OS choice); recommends a follow-on TASKS.md item for full-product spec OS resolution.

---

## 2026-05-19 — Demo spec anchored on architecture synthesis, not the stale full-product spec

**Decision.** Where the architecture synthesis (`bench-vision/benchvision-architecture-synthesis-2026-05-12.md`) and the full-product `docs/spec.md` (last updated 2026-04-24) disagree, the demo spec follows the architecture synthesis.

**Alternatives considered.** Anchoring on the full-product spec; producing the demo spec without resolving the conflict.

**Rationale.** The full-product spec is materially stale — it names PyQt for the HMI (architecture says Nuxt 3 / Vue 3), it lists "Software licensing / activation system" as out of scope (architecture has a complete Licensing Layer with FREE / PROFESSIONAL / ENTERPRISE tiers), and predates the DARCSI rebrand. The architecture synthesis is 18 days newer and reflects the design-reference docs that have been read in full. Producing a demo spec against the older full-product spec would amplify staleness; producing it against the architecture synthesis aligns with where the product actually is.

**Source.** Direct comparison of the two documents, 2026-05-19.

**Affects.** `spec.md` §8 (technical direction); also recommends logging full-product spec rewrite as a follow-on TASKS.md item.

---

## 2026-05-19 — Simulation is a configuration of BenchVision, not a fork

**Decision.** The demo simulation uses the production BenchVision software stack unchanged at the layer boundary. The only substitution is the HAL driver registry — configured with a simulator driver instead of NI-DAQmx or Modbus drivers. No `if demo_mode:` branch lives in the production code.

**Alternatives considered.** A separate `bench-vision-demo` codebase; a `demo_mode` flag in the production codebase that toggles behaviour.

**Rationale.** A fork drifts. A `demo_mode` flag scatters demo-only behaviour across production code. Configuration / driver substitution keeps the demo honest — the demo is the production code path with one driver swapped, which is also the precise behaviour the production HAL abstraction was designed to enable. This decision is what makes the demo simulation simultaneously a demo *and* the end-to-end integration test the production stack would otherwise lack until Phase 3 hardware arrives.

**Source.** Pix's framing in the Workflow 01 brief plus the production architecture synthesis HAL design notes.

**Affects.** `spec.md` §8; `out-of-scope.md` §C (the explicit "do not branch the codebase" rule); `features.md` feature 2.

---

## 2026-05-19 — Generic data only; no real Komatsu IP or customer data

**Decision.** All canned content in the demo — session history, performance curves, certificate worked examples, sample test sequences — uses generic synthetic data. No real Komatsu component identifiers, no real customer job numbers, no real prospect data is embedded in the demo machine.

**Alternatives considered.** Using obfuscated versions of real data for credibility; using real Komatsu-style curves with serial numbers masked.

**Rationale.** Confidentiality and the personal-capacity structure of the founding partnership. Devon's father runs Specialised Steering; the partnership documents structurally exclude associated companies from accessing partnership IP. A touring demo machine carrying real workshop data is the worst possible breach surface. Generic data that looks real is achievable; the credibility gap relative to real data is small in front of audiences who do not have a Komatsu testing background.

**Source.** Reading of `DARCSI_OVERVIEW.md` §8 (founding partnership structure) plus `bench-vision/CLAUDE.md` §9 (IP and confidentiality).

**Affects.** `spec.md` §9; `out-of-scope.md` §B2; `features.md` feature 10.

---

## 2026-05-19 — FF27 / commercial-vision content excluded from the demo simulation

**Decision.** FF27 and the commercial-vision framing are not in scope of the demo simulation surface.

**Alternatives considered.** Including FF27 markers in the licensing reference screen or splash.

**Rationale.** Per the Workflow 01 brief and the prior moog-willie call notes. Commercial-vision content lives in commercial conversations, not in the demo simulation surface that any prospect, distributor, or investor sees.

**Source.** Workflow 01 brief from Pix, 2026-05-19; `bench-vision/.../moog-willie-call-notes.md` line 56.

**Affects.** `out-of-scope.md` §B1; brand-identity decisions in `spec.md` §6.

---

## 2026-05-25 — Torque pump displacement (Vg) flag: awaiting Devon's spec sheet

**Decision.** The `TorqueChannel` formula (T = P × Vg / 62.8) uses Vg = 95 cc/rev, extrapolated from Devon's estimate "95 litres/min at 1000 RPM". Devon's V2 reference point (250 bar → 590 Nm) places the required Vg at ~148 cc/rev — a significant gap. The 95 cc/rev value is left in place as a placeholder. **This value must be replaced once Devon provides the manufacturer test sheet.**

**Alternatives considered.** Adjusting Vg upward to fit the reference point without confirmation from Devon. Rejected — the reference point may be from a different pump than the most common unit Devon uses.

**Rationale.** Devon's flow reference points (V1) sit exactly on the theoretical line with the current slope, giving high confidence in the flow model. The torque gap is large enough to indicate a wrong Vg rather than noise. Waiting for the spec sheet is preferable to guessing; the change is a one-line update (`PUMP_DISPLACEMENT_CC_PER_REV`).

**Source.** Visual inspection of the clean-run characteristic curve PNG, 2026-05-25. Devon has been asked for the test sheet.

**Affects.** `bench_simulator.py` `TorqueChannel.PUMP_DISPLACEMENT_CC_PER_REV`; characteristic curve `t_theory` line in `bench_dashboard.py`.

---

## 2026-05-25 — `--clean` CLI flag added for fault-free demo runs

**Decision.** `bench_dashboard.py` accepts a `--clean` flag that disables fault injection and runs a full 120-second nominal cycle. Default (no flag) retains the fault-injection demo at t=80s. Both post-run plots are generated in both modes; in clean mode the waveform has no fault shading and the characteristic curve uses the full 120s of data.

**Alternatives considered.** A `NO_FAULT` constant in the file requiring a manual edit. Rejected — a CLI flag lets the operator choose mode at run time without touching source.

**Rationale.** The clean run is needed for sharing smooth characteristic curves with Devon before the acceptance envelope is confirmed. The fault-injection run remains the demo default. Both modes need to co-exist without code changes between runs.

**Source.** Pix's request, 2026-05-25.

**Affects.** `bench_dashboard.py` `run_dashboard()`; post-run plots.

---

## 2026-05-25 — Per-channel identity colours replace state-derived border styles

**Decision.** Each sensor channel has a fixed identity colour (Pressure=blue, Flow=green, Temperature=magenta, Torque=cyan, Speed=yellow) applied consistently to panel border, panel title, engineering value, sparkline, and history graph line. Fault state overrides all to red. The former `STATE_BORDER` dict is replaced by `CHANNEL_COLORS`.

**Alternatives considered.** State-only colour coding (border changes colour with state). Retained only for fault override; clean states now carry channel identity instead of a generic "running" green.

**Rationale.** Identity colours let an operator instantly locate a specific channel's data across every surface — panel, sparkline, and history graph — without reading labels. The history graph is particularly improved: five colour-coded lines are distinguishable at a glance. Dark terminal background required for full colour fidelity.

**Source.** Pix's feedback after initial fault-only panel colouring, 2026-05-25.

**Affects.** `bench_dashboard.py` `CHANNEL_COLORS`, `channel_panel()`, `sparkline()`, `history_graph()`, `save_waveform_plot()`.

---

## 2026-05-25 — FlowChannel redesigned as pressure-derived channel

**Decision.** `FlowChannel` no longer runs an independent ramp cycle. Flow is derived continuously from live pressure readings using the inverse pump characteristic confirmed by Devon (Video 1): Q(P) = 245 − 0.5 × P (L/min). Channel state mirrors the pressure channel. A `_pressure_ref` is injected at `start_test_cycle()`. The architecture mirrors `TorqueChannel`.

**Alternatives considered.** Keeping flow as an independent ramp (previous model). Rejected — it produced flow rising simultaneously with pressure, which is physically wrong for a hydraulic pump and immediately apparent to any domain expert.

**Rationale.** Devon's walkthrough (Video 1, 2026-05-25) confirmed that flow falls as pressure increases — the fundamental pump volumetric-efficiency characteristic. The extrapolated model (245 L/min at zero load, 0.5 L/min/bar slope) fits both of Devon's reference readings: 50 bar → 220 L/min ✓ and 200 bar → 145 L/min ✓. The resulting waveform and characteristic curve correctly show the inverse X-shape Devon described.

**Source.** Devon's video walkthroughs (WhatsApp, 2026-05-25); notes in `devon-videos/devon-graph-walkthrough-notes.md`.

**Affects.** `bench_simulator.py` `FlowChannel` (complete rewrite); `BenchSimulator.start_test()`; characteristic curve plot.

---

## 2026-05-25 — Pump characteristic curve added as second post-run plot

**Decision.** After each run, `bench_dashboard.py` generates a second matplotlib figure: the pump characteristic curve with pressure on the X axis, flow (green, downward) on the left Y axis, and torque (cyan, upward) on the right Y axis. Theoretical lines are overlaid; Devon's reference data points are plotted as diamonds; a ±15 L/min acceptance envelope is drawn as a placeholder pending Devon's actual manufacturer spec limits.

**Alternatives considered.** Including the characteristic curve in the waveform figure as a sixth subplot. Rejected — different axis types (time-series vs pressure-domain) do not share an X axis and would be misleading together.

**Rationale.** The characteristic curve is the primary quality-assessment graph Devon described (Videos 1–2). It shows pass/fail against the acceptance envelope at a glance and directly matches the manufacturer test sheet format Devon's customers use. The ±15 L/min band is an explicit placeholder; a `TODO` comment in the code and this log entry ensure it is replaced when Devon provides the spec sheet.

**Source.** Devon's video walkthroughs (WhatsApp, 2026-05-25); Pix's request, 2026-05-25.

**Affects.** `bench_dashboard.py` `save_characteristic_curve()`; `run_dashboard()` post-run block.

---

## Pending decisions (open questions in `spec.md` §11)

These are recorded in the spec's Open Questions table and will move into this log as they resolve. Listed here as a shortcut:

- Q-D1 — reset semantics (manual-only vs auto-idle)
- Q-D2 — scenario count beyond the two-minimum
- Q-D3 — session history depth (count of pre-populated past runs)
- Q-D4 — licensing reference screen content source of truth
- Q-D5 — certificate worked-example data choice (generic vs obfuscated real)
- Q-D6 — DARCSI logomark commissioning
- Q-D7 — Devon witnessing demo before or after founding partnership signature
- Q-D8 — full-product spec rewrite sequencing

---

## Version history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-05-19 | Initial Workflow 01 Step 10 draft. Captures the twelve decisions taken during Steps 1, 4, and 5 plus the open-questions pointer to `spec.md`. |
