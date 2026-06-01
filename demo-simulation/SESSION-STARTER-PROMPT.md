# BenchVision Demo Simulation — Session Starter Prompt

> Paste the body below into a new Cowork (or Claude Code) session to apply Unlearn Workflow 01 to the BenchVision Demo Simulation. Saved here so future sessions can locate it.
>
> Created: 2026-05-19

---

# BenchVision Demo Simulation — Spec Workflow (Unlearn WF01 applied)

## Goal

Produce a complete, demo-ready spec for the **BenchVision Demo Simulation** by applying Unlearn Workflow 01.

The simulation is a prospect-facing demonstration of BenchVision that runs on a dedicated Linux machine. Its purpose is to show Devon (founding partner) and future prospects what BenchVision looks and feels like, before committing to production hardware. Commissioning of this simulation is a **Clause 0 gate** on the founding partnership agreement being signed (ref: `bench-vision/TASKS.md` line 12).

## Method

Follow Unlearn Workflow 01 — *Spec a Product Before AI Builds It* — exactly as described in:

- `/Users/sueholder/Development/learning/Unlearn/workflow-01-spec.md` — revised recipe; 11 steps
- `/Users/sueholder/Development/learning/Unlearn/unlearn-prompts-spec-workflow.md` — per-step prompts captured from the Unlearn video lessons

Use the Unlearn prompts file as the actual command set; use the revised workflow file as the structural recipe. Where the two differ, the **revised workflow takes precedence** — it folds in the agreed additions (explicit `out-of-scope.md`, mockup gap-exposure, adversarial poke-holes framing, decision-log discipline, exit condition).

## Output artefacts

Produce all four into a new directory at this path:

`/Users/sueholder/Development/bench-vision/hydraulic testbench software/bench-vision/demo-simulation/`

- `spec.md` — living spec for the demo simulation
- `out-of-scope.md` — explicit list of things AI is NOT allowed to build (Step 5 / Lesson 5)
- `features.md` — implementation-ordered feature list, with the explicit do-NOT-include constraint from Lesson 9 (no schemas, file names, file paths, class names, API endpoints, implementation details)
- `decision-log.md` — running record of *why* the spec changed at each iteration

## Reference files to load before starting

Read these for context **before** producing the rough spec (Workflow 01 Step 1):

- `/Users/sueholder/Development/bench-vision/hydraulic testbench software/bench-vision/benchvision-architecture-synthesis-2026-05-12.md` — single-document architecture summary (HAL, Event Bus, Configuration, Test Engine, Data Recorder, Pre-flight, Reporting, UI Layer, Licensing)
- `/Users/sueholder/Development/bench-vision/hydraulic testbench software/bench-vision/DARCSI_OVERVIEW.md` — DARCSI = parent brand; BenchVision = first vertical product
- `/Users/sueholder/Development/bench-vision/hydraulic testbench software/bench-vision/docs/spec.md` — existing BenchVision spec (the **full product**, not the demo)
- `/Users/sueholder/Development/bench-vision/hydraulic testbench software/bench-vision/bench-vision-design-system.md` — design system for visual consistency in the demo
- `/Users/sueholder/Development/bench-vision/hydraulic testbench software/bench-vision/CLAUDE.md` — project-level instructions
- `/Users/sueholder/Development/bench-vision/hydraulic testbench software/bench-vision/TASKS.md` — current task list including the demo machine and partnership gate
- `/Users/sueholder/Development/bench-vision/hardware/demo-machine-build.md` — Linux machine spec the simulation will run on (note: lives at top-level `bench-vision/hardware/`, NOT inside `hydraulic testbench software/bench-vision/hardware/`)
- `/Users/sueholder/Development/learning/project-context.md` — multi-project naming/branding context
- `/Users/sueholder/Development/benchvision/memory/design-principles.md` — durable BenchVision design rules accumulated to date

## Scope boundaries

- This is the **demo simulation**, not the full BenchVision product. The full-product spec already exists at `bench-vision/docs/spec.md`; the demo simulation is a tightly-scoped subset designed for prospect demonstrations.
- It runs on a dedicated Linux machine **without real sensor hardware**. All sensor data is simulated.
- Audience: Devon (founding partner) plus future prospects. The simulation must be convincing enough to show *what BenchVision does* without overstating capability that doesn't yet exist.
- **Do NOT include FF27 / commercial-vision content.** This is technical/product scope only. Reference: `bench-vision/.../moog-willie-call-notes.md` line 56 — "Don't mention FF27 or the commercial vision."
- DARCSI is the parent brand; BenchVision is the product. Use both names correctly throughout.

## How to start

1. **Read the reference files listed above** — especially the architecture synthesis and the existing full-product spec — so you understand what BenchVision is and what the demo needs to convey.
2. **Ask me clarifying questions** before producing any spec. Questions worth surfacing include (but are not limited to):
   - Which BenchVision capabilities does the demo simulation need to demonstrate? (subset of the full product)
   - What's the target session length for a typical prospect demo? (5 min walkthrough? 30 min interactive?)
   - Which sensor types should the simulation fake — pressure, flow, temperature, vibration, position, others?
   - Does the demo need to show test-run *history* (past runs, reports) or only *live operation*?
   - Does the demo include the reporting layer / certificate generation, or just the operator view?
   - Should the demo include any deliberate "broken" moments (anomaly detection in action) or stay nominal?
   - Is the simulation single-user only, or does it need to show the multi-user / role separation BenchVision will eventually have?
3. **Only after those are clarified**, produce the rough `spec.md` into `demo-simulation/spec.md` (Workflow 01 Step 1).

Do NOT skip the clarifying-questions phase. Workflow 01 Step 2 explicitly frames the agent's clarifying questions as the *primary work output*, not just a courtesy. If you don't have a clarifying question, ask yourself what you're assuming and surface that as a question instead.
