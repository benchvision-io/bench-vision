# BenchVision — Python application

**BenchVision** is the first product of the **DARCSI** platform (Data Acquisition,
Reporting, Compliance, Security Interface) — compliance-grade software for hydraulic
test benches. This folder, `benchvision-app/`, is the **Python application**: a
profile-driven **formula engine**, a **DAQ sensor simulator**, and a **live terminal
dashboard** that validates the engine against a real manufacturer chart.

> **Naming:** *DARCSI* is the platform, *BenchVision* is the product, and `bench-vision`
> is the code name used in file names and CSS. Don't conflate them.

This is early-MVP / discovery work. What's here is the **measurement core** — the maths
that turns raw sensor readings into graded, certifiable test channels — proven out
against a known-good chart before any real hardware or production UI is built. See
[Status](#status--whats-not-here-yet) for an honest line on what does and doesn't exist.

---

## The core idea: formulas + profiles, not hard-coded pumps

Derived test channels (flow, torque, power) are **not** hard-coded per pump. They are
computed by a small library of **named, version-locked, pure formulas**
([`formula_registry.py`](formula_registry.py)) that are **selected and parameterised by a
per-pump TOML profile** ([`pump_profile.py`](pump_profile.py)). The driving principle:
*the formula for a test type is stable; what varies pump-to-pump is the inputs.*

```
                pump_profile.py                         formula_registry.py
   ┌──────────────────────────────────┐        ┌────────────────────────────────┐
   │ profiles/pc200-8-hpv95.toml       │  names │  pump_flow_pc_destroke@v1       │
   │  • displacement, rated rpm        │ ─────▶ │  absorption_torque_from_flow@v1 │
   │  • pressure sweep, efficiency     │ feeds  │  power_from_flow_pressure@v1    │
   │  • acceptance bands (limit lines) │ inputs │  … pure (inputs) -> float       │
   └──────────────────────────────────┘        └────────────────────────────────┘
                          │                                   │
                          └─────────► engine evaluates ◄──────┘
                                      live channel value
```

**Adding a pump is a new `.toml`, not new code.** No pump-specific constant lives in
channel code — displacement, rated RPM, the destroke knee, acceptance limits and units
all arrive through the profile.

**Why version-locking matters.** Each formula carries a version tag (`@v1`) and the
registry refuses to silently overwrite a version with a different function — a changed
formula must get a new version. Once a formula has produced a result, it is **frozen**,
so any historical test certificate stays **reconstructable**: you can always re-run the
exact maths that produced it. The registry also validates that every required input is
present before evaluating — a single choke point where a future range-/unit-check
"caution layer" will attach.

The curated formulas currently registered (all `@v1`):

| Formula | What it computes |
|---|---|
| `pump_flow_linear` | Legacy linear `Q = Q0 − slope·P` (kept for a byte-identical refactor proof and genuinely linear fixed-displacement pumps) |
| `pump_flow_pc_destroke` | Power-controlled flow: flat to the PC cut-in, then a constant-power hyperbola `Q = power_const / P` |
| `absorption_torque_from_flow` | Input-shaft absorption torque derived from **live flow**, so the plateau emerges under power control |
| `radial_torque_sin90` | Radial torque `T = F·r·sin θ`; shaft radius from the **operator-supplied** diameter |
| `power_from_flow_pressure` | Hydraulic power `P_hyd[kW] = P·Q / 600` |

Design notes live in [`../demo-simulation/spec.md`](../demo-simulation/spec.md) §8A.

---

## The PC200-8 validation case

The bundled profile, [`profiles/pc200-8-hpv95.toml`](profiles/pc200-8-hpv95.toml),
is the **validation case** — a Komatsu **PC200-8** main pump (HPV95+95, part
`708-2L-00500`). It is **digitised from the manufacturer chart**: Komatsu document
**EEN00038-00**, *Fig. 1 Pump Assembly Performance Specification Chart*, **page 14**.

- **The chart PDF is the external source of truth and is NOT in this repo** (`docs/` is
  git-ignored). The full digitisation — every callout, every cross-check — is recorded in
  [`../demo-simulation/pc200-8-chart-digitised-values.md`](../demo-simulation/pc200-8-chart-digitised-values.md).
- **Flow acceptance band = the chart's printed limit lines.** The `[acceptance.flow]`
  polyline is the chart's dotted *Upper limit (Reference value)* and solid *Lower limit*
  lines, read directly from the PDF (each callout's MPa value cross-checked against its
  `{kgf/cm²}` pair). The lower-limit destroke knee sits at ~102 bar; the band fans out
  after it (e.g. ~144 / 108.5 L/min at 250 bar). Data ends at the certified maximum of
  **380 bar**; 380→400 is a flat extrapolation, not chart data.
- **Torque traces the chart's ~627 Nm nominal curve** via an **empirical efficiency
  curve** `η(P)` in the profile (`[efficiency]`). Because the pump destrokes under power
  control, real mechanical efficiency falls (~0.85 at the PC knee → ~0.74 at 400 bar);
  feeding that per-pressure η to the **unchanged** `absorption_torque_from_flow@v1`
  formula bends its flat constant-power plateau up to match the printed curve. Only the
  *input supply* changed, not the function — so **no formula version bump**.
- **Torque is a monitored reference, not graded pass/fail.** `[acceptance.torque]` holds
  the nominal curve as a deliberate **zero-width placeholder** (`upper == lower ==
  nominal`) pending a decision on whether torque becomes a graded channel; the dashboard
  renders it as a reference line, never an envelope that would "fail" every sample.

---

## Operator-variable inputs

Some quantities the software **cannot** know and must **not** hard-code — they vary
unit-to-unit even within a pump model. Shaft diameter is the worked example: the profile
marks it `operator_prompt = true` and carries only a fallback default. The engine
**formulates from the operator's input** (`radial_torque_sin90` derives the shaft radius
from the supplied `shaft_diameter_mm`) rather than assuming a value. Pump-specific *chart*
values belong in the profile; operator-variable quantities stay operator-prompted.

---

## Getting started

**Requirements.** The formula engine and its test suite are **standard-library only**
(Python **3.12+** floor; the demo machine targets Python **3.14**). The simulator,
dashboard and validation overlay need the dev/demo tooling pinned in
[`requirements-dev.txt`](requirements-dev.txt) (`pymupdf`, `matplotlib`, `rich`,
`plotext`; `numpy`, used by the simulator, is pulled in with `matplotlib`).

All commands below are run **from the repository root** (the `.venv` lives there, one
level up from this folder).

```bash
# one-time: create the venv and install the dev/demo tooling
python3 -m venv .venv
.venv/bin/python -m pip install -r benchvision-app/requirements-dev.txt
```

### Run the live dashboard (the main demo)

A 120-second test cycle rendered live in the terminal (rich gauges, sparklines, an
in-terminal trend graph), with post-run waveform and characteristic-curve plots. Ctrl-C
stops cleanly and still draws the plots.

```bash
# full demo — all five channels fault-inject at t = 80 s
.venv/bin/python benchvision-app/bench_dashboard.py

# clean run — no fault injection, pure operating cycle
.venv/bin/python benchvision-app/bench_dashboard.py --clean
```

### Run the tests (stdlib-only — no venv needed)

```bash
cd benchvision-app && python3 -m unittest discover -s tests -p "test_*.py"
# Ran 19 tests ... OK
```

### Run the chart-vs-engine validation overlay

Compares the engine's flow/torque/power against the digitised chart and writes overlay
PNGs to `../demo-simulation/`.

```bash
.venv/bin/python benchvision-app/validate_flow_refactor.py
# … flow chart RMS ~0.74 L/min; overlays saved to demo-simulation/
```

**Other entry points.** [`bench_simulator.py`](bench_simulator.py) and
[`bench_simulator_faults.py`](bench_simulator_faults.py) are the lower-level headless
demos — they run the same 120 s cycle and log readings at 1 Hz (the faults variant injects
at t = 80 s). They run to completion on their own; unlike the dashboard they don't trap
Ctrl-C, so interrupting them early prints a stack trace. Prefer the dashboard for an
interactive view.

---

## Project layout

```
benchvision-app/
├── README.md                  ← this file
├── formula_registry.py        ← named, version-locked pure formulas + the registry
├── pump_profile.py            ← per-pump TOML profile loader (profile → engine inputs)
├── bench_simulator.py         ← DAQ sensor simulator; derived channels via the engine
├── bench_simulator_faults.py  ← headless fault-injection demo (faults at t = 80 s)
├── bench_dashboard.py         ← live terminal dashboard + post-run matplotlib plots
├── validate_flow_refactor.py  ← chart-vs-engine validation (overlays → ../demo-simulation/)
├── profiles/
│   └── pc200-8-hpv95.toml      ← Komatsu PC200-8 validation profile (chart-digitised)
├── tests/
│   └── test_formula_registry.py← unittest suite (engine, formulas, profile loading)
└── requirements-dev.txt        ← pinned dev/demo tooling (pymupdf, matplotlib, rich, plotext)
```

---

## Status — what's not here yet

This is early **Milestone 1 / discovery**. Be honest about the boundary:

**Built and validated**
- ✅ Formula engine (`formula_registry.py`, `pump_profile.py`) — profile-driven,
  version-locked, **19 unit tests passing**.
- ✅ PC200-8 validation profile — flow + torque digitised from the chart; flow band is the
  printed limit lines; torque traces the ~627 Nm nominal curve via the η(P) efficiency
  curve.
- ✅ Sensor simulator — five live channels (pressure, flow, temperature, torque, speed)
  plus a derived power channel, with realistic noise and fault injection; derived channels
  computed live through the engine.
- ✅ Live terminal dashboard — reads acceptance bands from the profile (flow graded, torque
  monitored-reference).

**Not started**
- ⏳ Real DAQ I/O (no hardware driver; the simulator is the only data source today).
- ⏳ Production operator HMI, safety/interlock layer, certificate/report generation.

> **The terminal dashboard is an engine-validation harness, not the product UI.** The
> production HMI is a separate stack — **Nuxt 4 / Vue 3 / TypeScript** frontend over a
> **FastAPI + SSE** bridge (Python **3.14** backend) — described in
> [`../demo-simulation/spec.md`](../demo-simulation/spec.md). This dashboard exists to
> prove the maths in the terminal, not to ship.

---

## Conventions

- **British English** throughout (code comments, docs, identifiers where natural).
- **Latest stable tooling** per the project standard: Python 3.12+ (3.14 deployment
  target), type hints on all signatures, `pathlib` over `os.path`, `logging` over `print`,
  `ruff` for lint/format.
- **Safety-critical code needs human sign-off.** Any code touching **alarm limits, E-stop
  logic, interlock conditions, or sensor threshold checking** must be flagged for human
  review and signed off before committing. None of the current engine is on that path, but
  the safety layer (when built) will be.

---

## Further reading

- [`../CLAUDE.md`](../CLAUDE.md) — project context: brand hierarchy, status, technology
  standards, safety rules, IP.
- [`../demo-simulation/spec.md`](../demo-simulation/spec.md) — the demo specification,
  including **§8A** (the parameterised formula engine: rationale, version-locking, the
  gated custom-formula direction).
- [`../demo-simulation/pc200-8-chart-digitised-values.md`](../demo-simulation/pc200-8-chart-digitised-values.md)
  — the digitisation record: every chart callout, the flow limit-line transcription, and
  the torque-plateau resolution.
- The formal full-product spec (`docs/spec.md` §14A) covers the formula engine for the
  shipping product, but `docs/` is **git-ignored / local-only** — treat it as
  supplementary, not a primary pointer.

---

## IP and confidentiality

All software, architecture and IP is the sole property of **Design Develop Host**
(piDev). This is a **private** repository (its remote is `benchvision-io/bench-vision`).
Do not commit secrets, customer data, test results, or calibration records, and do not
expose the repository publicly without authorisation.
