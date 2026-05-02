# BenchVision — Project Agent Context

> **Last updated:** 2026-04-24
> **Session tool:** Cowork (Claude desktop). File tools use host paths.
> **Bash paths:** `/sessions/amazing-epic-davinci/mnt/ai-recruiter/hydraulic testbench software/bench-vision/`

---

## 1  Project Identity

### Brand hierarchy

| Level | Name | Description |
|---|---|---|
| Platform / suite | **TestVision** | Overarching software platform brand — a suite of testing products |
| First product | **BenchVision** | The first product being built under the TestVision platform |
| Repo / code name | `bench-vision` | Kebab-case used in file names, repo, design system |
| Domain | `benchvision.io` | Purchased — not yet hosted |

### Product details

| Property | Value |
|---|---|
| Product | **BenchVision** (part of the TestVision suite) |
| Tagline | Hydraulic test bench software |
| Owner / IP | Design Develop Host (Pixie / piDev) |
| Primary audience | Hydraulic engineers, test technicians, operations managers |
| Reference installation | Specialised Steering (Pty) Ltd — Devon Abbot |
| Remote repo | `git@github.com:SPH73/bench-vision.git` |

> **Naming rule:** Always refer to the suite as **TestVision** and the product as **BenchVision**.
> In code, file names, and CSS classes use `bench-vision` (kebab-case).
> Never conflate the two — TestVision is the umbrella; BenchVision is the product.

---

## 2  Project Status

**Phase:** Discovery / MVP — pre-Milestone 1
**Stage:** HTML prototypes live (Vercel). Python source not yet started.

| Deliverable | Status |
|---|---|
| HTML prototypes (portal, HMI, overview, roadmap, for-devon) | ✅ Live on Vercel |
| Design system v1.1 | ✅ Complete |
| Business Setup Reference v1.5 (TestVision) | ✅ Complete (April 2026) |
| Hydraulic bench proposal (v5) | ✅ Complete |
| Hydraulic bench questionnaire (v1) | ✅ Complete |
| Python src/ (DAQ, simulator, HMI, safety, reports) | ⏳ Milestone 1 — not started |
| Formal spec (docs/spec.md) | ⏳ Discovery phase |
| Architecture diagrams (docs/architecture.md) | ⏳ Discovery phase |

---

## 3  Workspace Folder Map

The parent folder on disk is `hydraulic testbench software/`. Key files:

```
hydraulic testbench software/
├── bench-vision/                        ← Active repo (this file lives here)
│   ├── CLAUDE.md                        ← This file
│   ├── index.html                       ← Project portal
│   ├── for-devon.html                   ← Partnership overview for Devon
│   ├── hmi.html                         ← HMI reference mockup (pump bench, Install #1)
│   ├── overview.html                    ← Platform overview & architecture
│   ├── roadmap.html                     ← Milestone progress tracker
│   ├── vercel.json                      ← Vercel routing (canonical — see §6)
│   └── bench-vision-design-system.md   ← Canonical design tokens & brand (Section 10 = docx truth)
├── TestVision_Business_Setup_Reference_v1.5_2026-04-22.docx   ← Latest business reference
├── BenchVision_Business_Setup_Reference_v1.1_2026-04-21.pdf   ← Prior version (archived)
├── COMPONENT-ARCHITECTURE.md           ← ⚠️ Belongs to Charitable Events Platform, not TestVision
├── project-overview.md                 ← ⚠️ Belongs to Charitable Events Platform, not TestVision
├── bench-vision-design-system.md       ← Copy of design system (canonical is in bench-vision/)
├── hydraulic-bench-project.html        ← Standalone reference page
├── hydraulic_bench_proposal_v5.docx.pdf
├── hydraulic_bench_questionnaire_v1.docx.pdf
├── discovery/                          ← Proposal version history
│   ├── hydraulic_bench_proposal_v2.1.docx
│   ├── hydraulic_bench_proposal_v2.docx
│   ├── hydraulic_bench_reference_v1.1.docx
│   └── ...
├── research/                           ← Research materials
├── recordings/                         ← Session recordings
├── prototypes/                         ← Prototype assets
├── legal/                              ← Legal documents
├── claude-support/                     ← Claude session support files
├── devon-reference/                    ← Devon-specific reference materials
└── archive/                            ← Archived documents
```

> ⚠️ `COMPONENT-ARCHITECTURE.md` and `project-overview.md` in the parent folder belong to the
> **Charitable Events Platform** (St Benedict's raffle), not TestVision. Do not modify them as
> part of TestVision work. They should be moved to an `archive/` subfolder when convenient.

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
- **Canonical file:** `bench-vision/bench-vision-design-system.md`
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

---

## 9  IP and Confidentiality

- All software, architecture, documentation, and IP is the sole property of **Design Develop Host (Pixie / piDev)**
- Specialised Steering (Pty) Ltd holds a perpetual licence for their installation only
- Never expose this repository publicly or share access without authorisation
- Never commit customer data, test results, or calibration records

---

## 10  Cross-Project Context

This project sits alongside **AI Recruiter** (`ai-r-v1/`) in the same workspace folder.
Shared task tracking is in `/Users/sueholder/Development/ai-recruiter/TASKS.md`.
Do not conflate the two projects. They share the same workspace but are independent products.
