# PC200-8 Main Pump — Chart-Digitised Values (drop-in for the simulator)

> **⚠ Correction (2026-05-27, after Devon's reply — read before using §1/§4):**
> This doc repeatedly calls 112 cc/rev "the displacement". That label is **wrong**.
> Per Devon: the pump's **theoretical displacement is 95** (base spec of the HPV95
> series, shared across machines); the **112** on the sheet is the **machine-adjusted
> flow** for the PC200-8 application; on the bench, adjusted to spec, he reads ~127.
> Chain: theoretical 95 → adjusted 112 → measured ~127. So do **not** simply set
> `PUMP_DISPLACEMENT_CC_PER_REV = 112`. The wider steer (see `spec.md` §8A and the
> 2026-05-27 `decision-log.md` entries) is that none of these numbers should be
> hard-coded at all — they belong in a per-test config pump profile feeding a formula
> engine. **What still holds:** the destroke/plateau physics and deriving torque from
> *live flow* (§2) — those align with Devon's formula-based approach. Exact 95→112→127
> mechanics confirm after Devon's Excel video (expected 2026-05-28). Treat §1's "112"
> as machine-adjusted flow, and this whole sheet as a **validation case**, not the model.

> Source: `docs/PC200-8 Main Pump Testing criteria.pdf`, **page 14**, *Fig. 1 Pump Assembly
> Performance Specification Chart (Standard Value: PC200 series-8)*.
> Komatsu document EEN00038-00. Pump part number **708-2L-00500**.
> Digitised 2026-05-27 from Devon's test sheet (the same chart he read out in the
> WhatsApp clips of 2026-05-25). All three of his spoken readings sit on this chart.

This is the manufacturer reference the demo simulation was waiting on. It does two
things: it pins down the constants, and — more importantly — it tells us the *shape*
of both curves is wrong in the current code, not just the numbers.

> **✅ Update (2026-06-01) — torque curve read from the clean PDF; open point 4 resolved.**
> Working from the original vector PDF (page 14, Fig. 1) rather than the WhatsApp photo,
> the printed callout boxes on the absorption-torque curve are now legible and each
> cross-checks against its printed `{kgm}` value. Findings:
> 1. The ~629 Nm line is the **nominal** absorption-torque curve (the main solid trace),
>    **not** an upper limit. The sheet carries a *separate* dotted "Upper limit
>    (Reference value)" line and a "Torque Upper Limit" line, so nominal and limit are
>    distinct. This answers the long-standing "is 590 the nominal or the upper limit?"
>    question: 590 is neither a plateau nor a limit — it is simply the nominal curve's
>    value at ~170 bar.
> 2. Nominal absorption torque **plateaus at ~627 Nm** (240–400 bar), not ~590.
>    Devon's spoken "590 at 250 bar" was an eyeball read one gridline low.
> 3. The engine (`absorption_torque_from_flow_v1`) holds a **flat 515 Nm** plateau and so
>    under-reads by ~18%. It *agrees with the chart at the 130-bar knee* (515 vs 519);
>    the gap opens only above the knee. Cause: the pump's mechanical efficiency **falls as
>    it destrokes** — implied η drops from ~0.85 at the knee to ~0.74 at full pressure —
>    whereas the profile assumes a single fixed `mech_efficiency = 0.90`.
> 4. Fix (mirrors the flow approach): treat the digitised torque curve as the reference of
>    record via an `[acceptance.torque]` polyline, rather than trusting the formula's flat
>    plateau. Added to `profiles/pc200-8-hpv95.toml`, flagged "chart-read, calibration
>    pending". §3 torque column below updated to the chart-read values.

---

## 1. Confirmed nameplate constants

| Quantity | Value from sheet | Current code | Action |
|---|---|---|---|
| Pump type | HPV95+95 | — | "95" is the **model name**, not displacement |
| Displacement (per section) | **112 cc/rev** | `PUMP_DISPLACEMENT_CC_PER_REV = 95.0` | replace 95 → 112 |
| Sections on one input shaft | 2 (tandem, 112 + 112) | treated as single | torque sees **both** = 224 cc/rev |
| Input shaft speed | **2000 rpm** standard (1400 rpm conversion) | — | use 2000 rpm |
| Rotation | Right-handed | — | — |
| Curve direction | "Values at pressure **rise** are applied"; hysteresis 1.96 MPa on drop | — | model the pressure-*rising* sweep |
| Test pressure axis | 0 → 39.2 MPa (0 → 400 bar) | — | — |

**The 112 cc/rev value validates itself against the no-load flow.**
Single-section flow at full stroke = 112 cc/rev × 2000 rpm ÷ 1000 = **224 L/min**, which
is exactly the chart's no-load envelope (226 upper / 222 lower). The old 95 figure cannot
reproduce that. This is strong corroboration the sheet matches Devon's bench.

---

## 2. The shape problem (this is the real finding)

The HPV95 is a **variable-displacement, power-controlled (PC) pump**. It runs at full
stroke at low pressure, then *destrokes* once it hits its constant-power line. That single
fact reshapes both derived channels:

**Flow** is not a straight line. It is flat at ~224 L/min until the PC cut-in (~130 bar),
then follows a constant-power hyperbola `Q ≈ 29 120 / P`. The current linear model
`Q = 245 − 0.5·P` happens to pass through Devon's two points but is wrong at both ends:
it claims 245 L/min at no load (real value 224) and keeps falling linearly where the real
curve is hyperbolic.

**Torque** is the one that bites. The code derives `T = P × Vg / 62.8` with **Vg fixed at
95**. Because the pump destrokes, the effective displacement *falls* as pressure rises —
so torque rises with pressure while at full stroke, then **plateaus** in the constant-power
region. That plateau is exactly what Devon pointed out in Video 3. Swapping 95 → 112 will
**not** fix this; it just rescales a straight line that should be bending over. The code's
own docstring already hints at the fix: `Vg = Q × 1000 / n`. Deriving torque from **live
flow** rather than a fixed constant makes the plateau emerge for free, because in the
constant-power region `P × Q` is constant.

Reconciliation against Devon's readings (input shaft = both sections, with ~10% mechanical
loss):

- 100 bar, full stroke → `100 × 224 / 62.8 ≈ 357 Nm`, +losses ≈ **~395 Nm** → Devon's "400 and above" ✓
- 250 bar, destroked → constant-power plateau ≈ **515 Nm** in the formula → Devon's "590" was an
  approximate read of the chart's **nominal** curve (~620 Nm at 250 bar), see the 2026-06-01 update.

A fixed-Vg formula can match *one* of those two points but never both. The destroking is the whole story —
**but** the formula's flat plateau is itself only an approximation: the real nominal torque keeps climbing
above the knee (to ~627 Nm) because efficiency falls on destroke. See §3 and the 2026-06-01 update.

---

## 3. Digitised points (pressure-rising sweep, single-section flow, 2000 rpm)

Flow nominal with acceptance envelope; torque is **input-shaft absorption torque (both
sections)**. Values at and below 130 bar are flat-region; above are constant-power.
Confidence: flow ★★★ (anchored on nameplate + Devon + envelope); torque now **★★★** — the
absorption-torque column is read **directly** from the printed callout boxes on the clean
PDF (2026-06-01), each cross-checked against its printed `{kgm}` value (agreement to within
rounding). The torque values marked "chart" below are printed callouts; the rest are
interpolated between them.

Flow **upper/lower** columns are now the chart's printed **limit lines** (transcribed
2026-06-01, see below); `‹c›` flags a value read directly from a printed callout box, the
rest are the straight-line reading between callouts. Flow nominal is the constant-power
formula (`Q≈29120/P`) and the no-load envelope.

| Pressure (bar) | Pressure (MPa) | Flow nominal (L/min) | Flow upper | Flow lower | Absorption torque (Nm) |
|---:|---:|---:|---:|---:|---:|
| 0   | 0.0  | 224 | 226 | 222 | ~0 |
| 50  | 4.9  | 223 | 226 | 220 | **269** (chart) |
| 100 | 9.8  | 222 | 226 | 217.1 ‹c› | ~425 (interp) |
| 130 | 12.7 | 224→ (PC cut-in) | 226 | 196 | ~519 (knee) |
| 138 | 13.5 | — | 226 ‹c› | ~190 | **544** (chart) |
| 150 | 14.7 | 194 | 217 | 181 | ~565 (interp) |
| 170 | 16.7 | — | 202 | 166 | **589** (chart) |
| 200 | 19.6 | 146 | 179 | 145 | ~610 (interp) |
| 240 | 23.6 | — | 148.5 ‹c› | 116 | **621** (chart) |
| 250 | 24.5 | 116 | 144 | 108.5 ‹c› | ~622 (interp) |
| 270 | 26.5 | — | 136 | 101 | **632** (chart) |
| 300 | 29.4 | 97  | 123 | 90  | **630** (chart) |
| 350 | 34.3 | 83  | 103 | 71  | ~627 (interp) |
| 358 | 35.2 | — | 99.2 ‹c› | 68 | **626** (chart) |
| 380 | 37.3 | — | 94 ‹c› | 59.3 ‹c› | **630** (chart) |
| 400 | 39.2 | 73  | — (lines end at 380) | — | ~630 (plateau) |

> **Torque** rises steeply to the knee, then bends to a **plateau of ~627 Nm** by ~240 bar
> (printed callouts: 50→269, 138→544, 170→589, 240→621, 270→632, 300→630, 358→626, 380→630).
> These are the **nominal** absorption-torque curve, not a limit line.
>
> **Flow limit lines — TRANSCRIBED 2026-06-01.** The two printed flow lines on Fig.1 were read
> from the clean vector PDF (render p.14, the torque-callout method). The **dotted "Upper limit
> (Reference value)"** line carries callouts (round brackets, MPa : L/min {kgf/cm²}):
> `(13.6:226){138.2}`, `(23.6:148.5){240.2}`, `(35.2:99.2){358.6}`, `(37.3:94){380}`. The
> **solid "Lower limit"** line: `(10:217.1){102.2}`, `(24.2:108.5){249.2}`, `(37.3:59.3){380}`.
> Each MPa value cross-checks against its {kgf/cm²} pair to within rounding (the chart's pressure
> gridlines are the {kgf/cm²} marks — i.e. this project's "bar"). Both lines are straight between
> their callouts (verified by reading line positions at every gridline off the render). The band
> is **far wider above the knee** than the earlier interpolated guess — the upper line is an
> explicit *Reference value*, so it sits well above the lower limit on destroke. Lines terminate
> at **380 bar** (the lower trace ends at the `(37.3:59.3)` marker) — the **certified maximum**;
> there is no 400-bar limit point, so 380→400 in the profile is a flat extrapolation, not data.
>
> **Knee (tidied 2026-06-01).** Re-read the lower limit below the knee off the render, anchored on
> `(10:217.1){102.2}`. The lower line's destroke knee sits **at that callout (~102 bar, not 130)**:
> it slopes gently 222→217 (0→100), then descends straight to `(24.2:108.5)`. So lower(100)=217.1
> (printed) and lower(130)=196 (chart-read, on the `(10:217.1)→(24.2:108.5)` segment; measured
> 196.5). The earlier 130→150 kink is gone. The **upper** line legitimately stays ~226 through the
> knee and is unchanged.
>
> **One loose callout:** `(24.2:108.5){249.2}` is internally ~1% inconsistent — 24.2 MPa = 246.8
> kgf/cm², but `{249.2}` is printed (every other flow callout cross-checks to <0.5%). Likely a
> source typo (24.2 for ~24.5 MPa). The flow value 108.5 is not in doubt and the marker sits on the
> 250 kgf/cm² gridline, so it is recorded at the 250-bar row.
>
> The **torque upper/lower limit lines** remain un-transcribed (the §3 torque column is the
> nominal curve). Transcribe them only if torque pass/fail — not just a reference — is wanted.

---

## 4. Drop-in code changes (`bench_simulator.py`)

**TorqueChannel** — replace the fixed constant and derive from live flow:

```python
# Nameplate, not a guess: HPV95+95 = 112 cc/rev per section, tandem on one shaft.
PUMP_DISPLACEMENT_CC_PER_REV: float = 112.0   # was 95.0 (model name, not displacement)
N_SECTIONS: int = 2                            # both sections load the input shaft
MECH_EFFICIENCY: float = 0.90                  # ⚠ 2026-06-01: a SINGLE fixed η is too high
                                               # AND too rigid — chart implies η falls
                                               # ~0.85 (knee) → ~0.74 (400 bar) on destroke.
                                               # This flat 0.90 is why the plateau reads 515
                                               # not ~627. Calibrate per the chart curve.

def _derive_torque(self) -> float:
    if self._pressure_ref is None or self._speed_ref is None:
        return self.target_torque
    p = self._pressure_ref.current_value      # bar
    n = self._speed_ref.current_value         # rpm
    if n < 1.0:
        return 0.0
    q = self._flow_ref.current_value          # L/min  <-- inject flow channel ref
    # Effective displacement per section follows the live flow (pump destrokes
    # under PC control); this is what produces the plateau Devon described.
    vg_eff = (q * 1000.0) / n                  # cc/rev, per section
    return (p * vg_eff * self.N_SECTIONS) / (62.8 * self.MECH_EFFICIENCY)
```

(Inject the flow-channel reference at `start_test_cycle()` alongside pressure/speed.)

**FlowChannel** — replace the linear model with flat-then-constant-power:

```python
no_load_flow: float = 224.0      # was 245.0  (112 cc/rev x 2000 rpm / 1000)
pc_cutin_bar: float = 130.0      # PC control destroke begins
power_const: float = 29120.0     # bar.L/min  (= 130 x 224)

def _derive_flow(self) -> float:
    if self._pressure_ref is None:
        return self.no_load_flow
    p = self._pressure_ref.current_value
    if p <= self.pc_cutin_bar:
        return self.no_load_flow
    return max(self.min_value, self.power_const / p)
```

**Acceptance envelope** (replaces the ±15 L/min placeholder in `bench_dashboard.py`):
no-load band 226 / 222; widen per the table above. Final limit lines to be lifted from
the chart's printed upper/lower callouts.

---

## 5. Still open

- ✅ **Plateau absolute value** — RESOLVED 2026-06-01. The nominal absorption-torque curve
  plateaus at **~627 Nm** (printed callouts, §3), not the 588 gridline and not 590. The
  engine's flat 515 Nm under-reads by ~18%; calibrate by treating the digitised curve as the
  reference (`[acceptance.torque]` polyline now in the profile) or by replacing the fixed
  `mech_efficiency = 0.90` with an efficiency that falls on destroke (~0.85 at the knee →
  ~0.74 at 400 bar). Pure-formula plateau alone cannot reproduce the climb above the knee.
- ✅ **Flow envelope limit lines** — TRANSCRIBED 2026-06-01. The printed dotted "Upper limit
  (Reference value)" and solid "Lower limit" flow lines were read from the clean PDF and now
  populate `[acceptance.flow]`, replacing the interpolated widths. Printed callouts
  (each MPa↔{kgf/cm²} cross-checked): UPPER `(13.6:226){138.2}`, `(23.6:148.5){240.2}`,
  `(35.2:99.2){358.6}`, `(37.3:94){380}`; LOWER `(10:217.1){102.2}`, `(24.2:108.5){249.2}`,
  `(37.3:59.3){380}`. See §3 and the profile. **Knee tidied 2026-06-01:** the ≤130 lower band was
  re-read off the render — the lower-limit knee sits at `(10:217.1){102.2}` (~102 bar), so
  lower(100)=217.1 and lower(130)=196 now descend smoothly into the post-knee band (no kink); the
  upper line stays ~226 through the knee, unchanged. Lines end at **380 bar (certified maximum)**;
  380→400 is a flat extrapolation, not data. The one loose callout `(24.2:108.5){249.2}` is ~1%
  inconsistent MPa↔kgf (likely a source typo for ~24.5 MPa); anchored on its {249.2} kgf/cm² =
  the 250-bar gridline, flow 108.5 unaffected.
- **Torque limit lines** — if torque pass/fail (not just nominal reference) is wanted, the
  "Torque Upper Limit" line and its lower counterpart need transcribing; the §3 column is the
  nominal curve, which currently fills the `[acceptance.torque]` band as a placeholder.
- Devon's serial range is **PC200-8 (#300001-)** — the one remaining genuine Devon question:
  a one-line confirm that his actual pump falls in that block, since an earlier serial uses a
  different chart. (Values themselves no longer need him — they're read from the sheet.)
