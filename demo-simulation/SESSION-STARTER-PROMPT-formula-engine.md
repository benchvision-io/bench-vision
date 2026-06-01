# BenchVision Demo Simulation — Session Starter (Formula Engine refactor)

> Paste the body below into a new Cowork session (or Claude Code) to continue the simulation work, this time replacing the hard-coded pump curves with a parameterised formula engine.
>
> Created: 2026-05-29. Builds on Devon's WhatsApp walkthrough of 2026-05-25 (v1–v4) and the **Excel-method follow-up** of 2026-05-27 (v5 — the clip the 2026-05-27 decision-log entries were waiting on).

---

## Goal of this session

Lift the BenchVision demo simulation from **hard-coded pump curves** to a **formula-driven engine** that:

1. Holds derived channels (flow, pressure, torque, power, etc.) as **named formulas in a registry**, selected and parameterised by a per-test **config file** ("pump profile").
2. Carries pump-specific constants (theoretical displacement, machine-adjusted flow, rated RPM, pressure sweep, acceptance limits, shaft diameter, units) in **config**, never in channel code.
3. Auto-plots curves live from the equations as data is logged — Devon's mental model is his Excel sheet: change an input cell, the graph regenerates. Same here.
4. Validates against the **PC200-8 HPV95 chart as a test case for the engine**, not as the engine itself. Any other pump should be a config change, not a code change.

This refactor is the load-bearing prerequisite for the Founding Partner Proposal v9.x being thawed — until the simulation is convincing on Devon's own bench, the proposal stays paused.

## Mandatory constraints

- **British English** throughout — licence/organisation/colour/centre/favour, etc.
- **No hard-coded pump constants** in channel code. If a value depends on the pump (displacement, rated RPM, acceptance band, shaft diameter), it lives in config.
- **No invented quantities.** Devon's worked numbers in v5 are **illustrative** (he said twice on camera that he "mixed up" the values). Use the digitised PC200-8 chart as the source of truth for the validation case, not the spoken numbers.
- **Provenance discipline.** The custom-formula mode decisions are already logged — do not regress the gated/named-author/sandboxed design recorded in `decision-log.md` 2026-05-27.
- **Append-only `decision-log.md`** for any change of approach. Two-minute habit, newest at top.
- Candid, in-depth analysis preferred over softened summaries. If a choice looks shaky, say so.

## Reference files — read these before writing any code

In the project directory `/Users/sueholder/Development/darcsi/benchvision/`:

- `demo-simulation/spec.md` — living spec for the simulation.
- `demo-simulation/features.md` — implementation-ordered feature list.
- `demo-simulation/out-of-scope.md` — things AI is explicitly not to build.
- `demo-simulation/decision-log.md` — particularly the **2026-05-27 entries** on the formula engine and gated custom-formula mode. Those decisions stand; this session implements them.
- `demo-simulation/pc200-8-chart-digitised-values.md` — the validation dataset.
- `demo-simulation/adversarial-review-0.1.md` — pre-existing critique to fold in.
- `demo-simulation/devon-videos/devon-graph-walkthrough-notes.md` — written summary of v1–v4.
- `demo-simulation/devon-videos/transcripts/video1_17-28-04.txt` … `video5_17-01-47.txt` — verbatim Devon, timestamped.
- `demo-simulation/devon-videos/stills/v1_*.jpg` … `v5_*.jpg` — the screen at the moments Devon names values or axes.
- `legal/benchvision-founding-partner-proposal-v9.3.docx` — the paused proposal; useful to know what the simulation has to support before the proposal can move.

## Source-of-truth summary from Devon's videos

**v1 (flow vs pressure, acceptance envelope).** Y-axis = flow (L/min, gridded in 50s). X-axis = pump discharge pressure (bar). Curve bounded by upper/lower limit lines forming an acceptance band; pump passes if the operating point sits inside it. Worked readings: 50 bar → ~220 L/min, 200 bar → ~145 L/min.

**v2 (torque vs pressure).** Axes pressure × torque (Nm). Torque rises with pressure because shaft effort grows with pressure. Worked readings: 250 bar → ~590 Nm, 100 bar → ~400 Nm-plus.

**v3 (auto-plot principle).** The software should hold the equations and plot as it logs. Torque curve eventually **plateaus** — model that explicitly.

**v4 (radial torque = F × r × sin θ).** Measurement at 90°, so sin term collapses to 1. Radius is shaft-centre distance. **Shaft diameter varies per pump** — add it as an operator input feeding the formula.

**v5 (the Excel walkthrough — axis confirmation + sample-rate question).** This is the Excel-method clip the 2026-05-27 decision-log entries were waiting on. Devon walks through how he'd log values in Excel — formula in a cell, inputs in a column, graph regenerates — which is the mental model the formula engine is meant to mirror. He re-states **flow on Y, pressure on X**, with each plotted point being a paired (flow, pressure) reading taken at the same instant. He raises but does **not** resolve the sample-rate question — "every second… or every point one of a second" (1 Hz vs 10 Hz). This needs a decision and a defended entry in `decision-log.md`. His specific numbers in v5 (85 L/min at 0 bar, 80 L at 225 bar, 50 L at 175 bar) are deliberately illustrative — do not fit to them. v5 confirms the **approach**; it does not name 95 cc/rev vs 112 cc/rev, so that specific constants question stays open.

## Concrete tasks for this session

In order:

1. **Read** the reference files above, plus `bench_simulator.py` (or whatever the channel implementation file is currently named — confirm by `ls demo-simulation`). Surface anything that looks like a pump-specific constant baked into the channel logic.
2. **Draft a config schema** for a "pump profile". Cover at minimum: identifier, theoretical displacement (cc/rev), machine-adjusted flow value, rated RPM, pressure sweep range, sample rate (1 Hz vs 10 Hz — propose a default with reasoning), acceptance-band upper/lower curves (as polylines or formula references), shaft diameter, units for each quantity.
3. **Propose the formula registry shape** — a small, named, version-tagged set: e.g. `flow_pressure_v1`, `torque_pressure_v1`, `radial_torque_sin90_v1`, `power_from_flow_pressure_v1`. Each formula declares its required inputs (by config key) and its output units. Pure functions, side-effect free, easy to unit-test.
4. **Refactor one channel end-to-end** — pick FlowChannel — to (a) read constants from a loaded `PumpProfile`, (b) compute via a registry-resolved formula, (c) keep the existing graph output identical for the PC200-8 case. Confirm by diffing the PC200-8 plot against the digitised chart before and after.
5. **Decide sample rate** — 1 Hz vs 10 Hz vs configurable per test. Defend in `decision-log.md` with a rationale (operator cognitive load, file size, what's needed to see plateau behaviour cleanly, what Devon's bench can drive).
6. **Stop and check in** before refactoring TorqueChannel/PowerChannel. The FlowChannel pattern is the load-bearing decision — better to confirm it works than to refactor three channels into a shape that needs unpicking.

## Open questions worth raising before coding

- Is the formula registry **in-process Python only** for MVP, or already designed for the future custom-formula sandbox (see `decision-log.md` 2026-05-27 second entry)? The custom-mode work isn't this session, but the registry interface should not preclude it.
- Acceptance band as **two polylines** (digitised) vs **formula + tolerance** (parameterised). Devon's chart looks polyline-y; his preferred mental model is formula-y. Either is fine — choose and defend.
- Theoretical displacement 95 cc/rev vs machine-adjusted 112 cc/rev — when does each apply? v5 (the Excel walkthrough) does **not** resolve this — it confirms the formula-engine approach but does not name those constants. Treat both as config inputs (`displacement_theoretical_cc_per_rev` and `displacement_machine_adjusted_cc_per_rev`), make the formula pick which one by an explicit `displacement_mode` field, and surface the choice in `decision-log.md` for Devon to confirm on his next pass.
- Shaft diameter — operator input at test setup, or part of the pump profile? v4 implies it can vary per unit even within a pump model, so leaning towards a per-test input, but the profile should carry a default.

## What "done" looks like

- FlowChannel reads only from `PumpProfile` + formula registry; the PC200-8 plot is bit-for-bit (or close-enough-to-justify) identical to the current hard-coded output.
- The config file for PC200-8 HPV95 exists, is documented, and another pump could be added by writing a sibling config without touching channel code.
- `decision-log.md` has a fresh entry covering: sample rate, formula-registry shape, acceptance-band representation, and (if relevant) anything Devon's still-unwatched Excel video changes.
- `features.md` and `spec.md` reflect the formula-engine architecture.

---

## Observations from the previous session that should improve this one

Picked these up while working through the videos — worth carrying in:

- **Take Devon's numbers as shape, not values.** v5 is explicit on this; v1/v2 were not, so the digitised chart wins ties.
- **Y-axis is flow, X-axis is pressure** — re-confirmed twice in v5. The simulator currently respects this; don't let an LLM "tidy it up" the other way round.
- **Acceptance envelope is a load-bearing visual.** v1 makes pass/fail entirely dependent on it. It deserves first-class status in the data model, not a cosmetic overlay.
- **Plateau is a real behaviour, not a glitch.** v3 names it for torque. The model has to produce it intentionally, not approximate it accidentally.
- **Shaft-diameter input is a real UX gap.** v4 turns it into an operator question. The simulation should surface it the same way — an explicit prompt at test setup, not a hidden config field.
- **Sample-rate decision is unresolved.** v5 raises it and stops. Don't let it stay unresolved through another session.
- **Custom-formula mode is decided, not built.** `decision-log.md` 2026-05-27 covers it. Don't re-litigate the gated/named-author/sandboxed design — implement the hooks; defer the UI.
- **Transcription quality.** Whisper "tiny" was used last session for speed; a couple of words came through wrong (notably "like for like" → "luck for luck", "sin" → "Sun" in earlier videos). If a phrase looks nonsensical, listen to the audio before treating it as a Devon-ism.
- **Pace.** Per workflow pacing preference, prefer scheduling follow-on work for tomorrow via TASKS.md over piling more into this session.
