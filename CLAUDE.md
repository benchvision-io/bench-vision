# BenchVision — Project Agent Context

> **Last updated:** 2026-06-01
> **Session tool:** Cowork (Claude desktop). File tools use host paths.
> **Repo path:** `/Users/sueholder/Development/darcsi/benchvision/`

---

## 1  Project Identity

### Brand hierarchy

| Level | Name | Description |
|---|---|---|
| Over-arching brand / platform | **DARCSI** | Data Acquisition Reporting Compliance Security Interface — the compliance platform under which BenchVision and future products are delivered. Registered. Domain: `darcsi.io`. |
| First product | **BenchVision** | The first product being built under the DARCSI platform |
| Repo / code name | `bench-vision` | Kebab-case used in file names, repo, design system |
| Product domain | `benchvision.io` | Purchased — not yet hosted |
| GitHub organisations | `github.com/darcsi-io`, `github.com/benchvision-io` | Code-ownership and brand-control evidence |

> **Brand update 2026-05-12:** DARCSI replaces the earlier "TestVision" parent-brand framing. References to TestVision in older documents are stale. The change is not yet reflected in every legacy doc — see `TASKS.md` for the rework list.

### Product details

| Property | Value |
|---|---|
| Product | **BenchVision** (a product of the DARCSI platform) |
| Tagline | Hydraulic test bench software · The compliance standard that scales from repair shop to enterprise |
| Owner / IP | Design Develop Host (Susan Holder, trading as piDev) |
| Primary audience | Hydraulic engineers, test technicians, operations managers |
| Reference installation | Devon Abbot (in personal capacity — see legal/ proposal v9.2 onwards) |
| Remote repo | `git@github.com:benchvision-io/bench-vision.git` |

> **Naming rule:** **DARCSI** is the over-arching brand and platform. **BenchVision** is the first product under DARCSI.
> In code, file names, and CSS classes use `bench-vision` (kebab-case).
> Never conflate the two — DARCSI is the platform; BenchVision is the product. References to TestVision in older documents pre-date the brand-hierarchy decision of 2026-05-12 and should be treated as historical.

---

## 2  Project Status

**Phase:** Discovery / MVP — early Milestone 1
**Stage:** HTML prototypes live (Vercel). Python formula engine + sensor simulator + live
dashboard built and validated against the PC200-8 manufacturer chart (in `benchvision-app/`).

| Deliverable | Status |
|---|---|
| HTML prototypes (portal, HMI, overview, roadmap, for-devon) | ✅ Live on Vercel |
| Design system v1.1 | ✅ Complete |
| Business Setup Reference v1.5 (TestVision-era) | ✅ Complete (April 2026) — superseded by DARCSI rebrand; see `TASKS.md` for new-version status |
| Hydraulic bench proposal (v5) | ✅ Complete |
| Hydraulic bench questionnaire (v1) | ✅ Complete |
| Formula engine (`formula_registry.py`, `pump_profile.py`) | ✅ Built + unit-tested; profile-driven, version-tagged formulas |
| PC200-8 validation case (`profiles/pc200-8-hpv95.toml`) | ✅ Flow + torque digitised from chart Fig.1; flow acceptance band = printed limit lines |
| Sensor simulator (`bench_simulator.py`) | ✅ Built — channels derived live via the formula engine + profile |
| Live dashboard (`bench_dashboard.py`) | ✅ Built — reads acceptance bands from the profile; flow graded, torque monitored-reference |
| Real DAQ I/O, HMI, safety layer, report generation | ⏳ Milestone 1 — not started |
| Formal spec (`docs/spec.md`, `demo-simulation/spec.md`) | 🚧 Drafted, evolving |
| Architecture diagrams (docs/architecture.md) | ⏳ Discovery phase |

---

## 3  Workspace Folder Map

The repo lives at `Development/darcsi/benchvision/`. Raw working materials are in the sibling folder `Development/darcsi/benchvision-working/`.

```
Development/
└── darcsi/                              ← DARCSI platform root
    ├── benchvision/                     ← Git repo (this file lives here) · deployed to Vercel
│   ├── CLAUDE.md                        ← This file
│   ├── TASKS.md                         ← Project-level task notes
│   ├── DARCSI_OVERVIEW.md               ← Master brand & architecture overview
│   ├── bench-vision-design-system.md    ← Canonical design tokens & brand (Section 10 = docx truth)
│   ├── index.html                       ← Project portal
│   ├── for-devon.html                   ← Partnership overview for Devon
│   ├── hmi.html                         ← HMI reference mockup (pump bench, Install #1)
│   ├── overview.html                    ← Platform overview & architecture
│   ├── roadmap.html                     ← Milestone progress tracker
│   ├── vercel.json                      ← Vercel routing (canonical — see §6)
│   ├── benchvision-app/                 ← Python application (formula engine, simulator, dashboard)
│   │   ├── formula_registry.py          ←   named, version-tagged pure formulas
│   │   ├── pump_profile.py              ←   per-pump profile loader (TOML → engine inputs)
│   │   ├── bench_simulator.py           ←   DAQ sensor simulator (profile-driven channels)
│   │   ├── bench_simulator_faults.py    ←   fault-injection helpers
│   │   ├── bench_dashboard.py           ←   live terminal dashboard + post-run plots
│   │   ├── validate_flow_refactor.py    ←   chart-vs-engine validation (overlays → demo-simulation/)
│   │   ├── profiles/                    ←   pump profiles (pc200-8-hpv95.toml = validation case)
│   │   ├── tests/                       ←   unittest suite (run: cd benchvision-app && python3 -m unittest …)
│   │   └── requirements-dev.txt         ←   pinned dev/demo tooling (pymupdf, matplotlib, rich, plotext)
│   ├── discovery/                       ← Market-sizing and discovery outputs
│   ├── demo-simulation/                 ← Digitisation record, validation overlays, decision log, media
│   ├── docs/                            ← Formal spec, architecture, learning PDFs, source chart PDFs
│   ├── legal/                           ← Partner agreement versions
│   ├── marketing/                       ← Marketing materials
│   └── adjacent-markets/               ← Adjacent market research
│
    ├── benchvision-working/             ← Raw working materials (NOT in git)
    │   ├── claude chats/               ← Session notes, design refs, prompts
    │   ├── devon-reference/            ← Devon hardware docs, USB contents
    │   ├── research/                   ← General research + B-BBEE, Brian notes
    │   ├── proposals/                  ← Proposal version history (v2, v2.1, ref v1.1)
    │   ├── sensors-literature/         ← Sensor PDFs and calibration certificates
    │   ├── hardware/                   ← Demo machine build notes
    │   ├── bench-observation/          ← Bench observation stills + transcriber eval
    │   ├── recordings/                 ← Session recordings
    │   ├── prototypes/                 ← Prototype assets
    │   ├── claude-support/             ← Claude session support files
    │   └── archive/                    ← Archived documents
    ├── benchvision-docs-mcp/           ← MCP documentation server
    └── memory/                         ← design-principles.md
```

---

## 4  Technology Standards — MANDATORY

**Use the latest stable version of every language, library, and tool. No exceptions.**

### Python
- Python **3.12+**; `pyproject.toml` for config; `uv` for dependency management
- Type hints on all signatures; `from __future__ import annotations` for forward refs
- `pathlib.Path` — never `os.path`; f-strings only; `asyncio` for I/O; `logging` not `print()`
- PEP 8; `ruff` for linting and formatting

### JavaScript / TypeScript
- TypeScript by default; ESM only; ES2022+ target
- `const`/`let` only; `?.` and `??`; `async/await`; native `fetch`

### HTML / CSS
- Valid HTML5 with semantic elements
- CSS custom properties for all design tokens (see design system)
- CSS Grid + Flexbox; mobile-first; `clamp()`/`min()`/`max()` for fluid sizing
- No inline styles except dynamic JS; `rem`/`em` for font sizes

### Design System
- **Canonical file:** `benchvision/bench-vision-design-system.md`
- **Section 10 is the single source of truth for all `.docx` outputs**
- All web tokens (colours, type, spacing, components) defined in Sections 1–9
- Never hardcode design values — always reference the design system

---

## 5  Safety-Critical Code Rules

**Any code in `src/safety/` or touching alarm limits, E-stop logic, interlock conditions,
or sensor threshold checking MUST be flagged for human review before committing.**
Do not commit safety-critical code without explicit sign-off from Pix.

---

## 6  Vercel Deployment Config (Canonical)

Keep `vercel.json` exactly as below. Update when new pages are added.

```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    { "source": "/for-devon", "destination": "/for-devon.html" },
    { "source": "/hmi",        "destination": "/hmi.html" },
    { "source": "/overview",   "destination": "/overview.html" },
    { "source": "/roadmap",    "destination": "/roadmap.html" },
    { "source": "/",           "destination": "/index.html" }
  ]
}
```

---

## 7  Git Conventions

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Branch naming: `milestone/m1-sensor-simulator`, `fix/pressure-gauge-overflow`
- Never commit: secrets, API keys, calibration data, `.env`, `__pycache__/`, `.DS_Store`
- Maintain `example.env` with dummy values only

---

## 8  Agent Responsibilities on Invocation

When starting a session on this project:

1. **Audit** — verify all files in §3 exist and are non-empty; report missing files
2. **Validate HTML** — check DOCTYPE, semantic structure, internal links, no broken hrefs
3. **Verify vercel.json** — must match canonical in §6 exactly; replace if not
4. **Check design system compliance** — no hardcoded colours or sizes in HTML/CSS
5. **Safety check** — flag any safety-critical code before staging
6. **Git status** — report staged/unstaged; suggest conventional commit message
7. **Suggest** framework migration when HTML prototype phase is outgrown

### 8A  Definition of Done — close the loop on finished work

A task is **not** finished when the code/profile changes land. Before reporting it done,
update the trackers so finished work cannot be silently re-dispatched (this is how a
completed task got relaunched on 2026-06-01):

1. **Decision-log** — add an entry to `demo-simulation/decision-log.md` (Decision /
   Alternatives / Rationale / Source / Affects), newest at top. Annotate any earlier
   entry the new work supersedes with a `⚠ SUPERSEDED <date>` note rather than deleting it.
2. **TASKS.md** — tick the item(s) the work completed; correct any now-stale figures;
   split out what genuinely remains as fresh open items.
3. **Session-starter** — if the work came from a `SESSION_START_*.md` block, mark that
   file `✅ COMPLETED <date> — do not relaunch` at the top. Never leave a starter that
   re-dispatches finished work.
4. **Digitisation record / profile** — keep `pc200-8-chart-digitised-values.md` and the
   relevant profile in step with what was actually read from the chart.

When verifying transcribed chart values, **re-read the source** (render the PDF, read the
callouts) rather than trusting an existing transcription — the brief's "be true and real,
don't invent values" applies to confirming prior work too.

---

## 9  IP and Confidentiality

- All software, architecture, documentation, and IP is the sole property of **Design Develop Host (Pixie / piDev)**
- Specialised Steering (Pty) Ltd holds a perpetual licence for their installation only
- Never expose this repository publicly or share access without authorisation
- Never commit customer data, test results, or calibration records

### 9A  Repo hygiene & publishing policy (decided 2026-06-02 — do not re-litigate)

**This private repo is the full working store.** IP, planning, design, architecture,
specs, and the decision-log all belong here and stay tracked. "Only what's needed to run"
is a **publishing** concern, *not* a tracking one — do not strip working docs out of this
repo to chase that goal.

- **`.gitignore` is the forward guard.** It keeps *new* non-runnable / IP material out of the
  repo and its history: design system, architecture-synthesis, `bv-hardware-audit/`,
  `demo-simulation/devon-videos/`, `memory/`, `legal/`, `marketing/`, `research/`, binary
  business docs (`*.pdf/.docx/.pages/.numbers`), and session-starter / `SESSION_*` scaffolding.
  Kept on purpose: `DARCSI_OVERVIEW.md`, the site HTML, `vercel.json`, `benchvision-app/`.
- **No history scrub.** As of 2026-06-02 there are no collaborators but Pix + Claude and the
  remote is private, so already-committed docs (`CLAUDE.md`, `TASKS.md`, `demo-simulation/*.md`
  incl. `pc200-8-chart-digitised-values.md`) **stay as they are**. Do not `git rm --cached`
  them and do not rewrite history — without a scrub it gains nothing, and several are core
  working files (e.g. the decision-log per §8A).
- **If the app is ever made public:** publish only the runnable cut (site HTML, `vercel.json`,
  `benchvision-app/`, plus the overview) to a **separate public repo**. Never make *this* repo
  public and never force-push a history rewrite onto it.
- **Revisit on onboarding:** the day a collaborator joins or the project goes public, re-open
  the access / history-scrub question — until then it is settled.

---

## 10  Cross-Project Context

This project sits alongside **AI Recruiter / Recruitrr** (`ai-recruiter/`), **Ticketrr**
(`ticketrr/`) and **FF27** in the same workspace folder.
Do not conflate the projects. They share the same workspace but are independent products.

### 10A  Tracking model — BenchVision is the template

The ownership model established here (§8A) is the **template for every project**:

- Each project owns **one tracked `TASKS.md`** as its single source of live status (open /
  done / next). Stable identity/architecture facts live in that project's `CLAUDE.md`.
- A cross-project `Development/TASKS.md` is a thin **router** only — it links to each
  project's `TASKS.md` and **never duplicates** their contents. (This supersedes the earlier
  "shared task tracking in `ticketrr/TASKS.md`" arrangement; the per-project file is
  authoritative.)
- Status overviews are **generated** from the owners, never hand-maintained alongside them.

(Recorded here as the convention; the other repos are not edited from this one.)
