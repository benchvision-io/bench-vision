#!/usr/bin/env python3
"""
run_demo.py

BenchVision — the end-to-end demo entry point. One run of the ``BenchSimulator`` produces,
in a single go:

  1. the graphs (the dashboard's waveform + characteristic-curve plots),
  2. the assembled :class:`RunRecord` saved as JSON (via ``JsonFileRunRecordRepository``),
  3. the training-marked certificate PDF (via ``generate_certificate_pdf``).

The sequencer (``sequencer.py``) is what ties these together: it drives the simulator
through the state machine, grades flow against the profile band, records torque as a
monitored reference, runs the cleanliness steps, and freezes the ``RunRecord`` the
certificate renders.

Run it::

    python run_demo.py            # real-time (~110 s) — for screen recording
    python run_demo.py --fast     # stepped/instant — the reproducible artefact path

The default seed is **pinned to a verified all-points-pass run** so the shared artefact is
reliably a clean PASS; vary ``--seed`` to show a fail or (with a fault) an abort for
contrast.

British English throughout. Python 3.12+.
"""

from __future__ import annotations

import argparse
import logging
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")            # headless: save the artefacts, never block on show()

import numpy as np

from bench_dashboard import save_characteristic_curve, save_waveform_plot
from bench_simulator import BenchSimulator
from certificate import generate_certificate_pdf
from cleanliness import CleanlinessReading
from run_record import (
    JsonFileRunRecordRepository,
    RunRecordBuilder,
    TestPurpose,
)
from sequencer import TestSequencer, simulated_sources

#: Pinned default — verified to yield an all-points-pass run on the PC200-8 profile, so the
#: shared demo certificate is reliably a clean PASS. Vary --seed for a fail/abort contrast.
DEFAULT_SEED = 1000


def _seed_channels(sim: BenchSimulator, base: int) -> None:
    """Seed each channel's RNG deterministically so the demo run is reproducible."""
    for i, ch in enumerate(sim.channels + sim.derived_channels):
        ch.rng = np.random.default_rng(base + i)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="BenchVision end-to-end demo: one run → graphs + run-record JSON "
                    "+ training certificate PDF.",
    )
    ap.add_argument("--fast", action="store_true",
                    help="stepped/instant path (no real-time pacing) — the reproducible "
                         "artefact path; default is real-time for screen recording")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED,
                    help=f"RNG seed (default {DEFAULT_SEED}, verified clean PASS)")
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "demo-output",
                    help="output directory for the run-record JSON and certificate PDF")
    ap.add_argument("--serial", default="PC200-8-SN-DEMO", help="device-under-test serial")
    ap.add_argument("--po", default="PO-DEMO-0001", help="purchase order / reference")
    args = ap.parse_args()

    logging.basicConfig(level=logging.WARNING)      # keep the demo's own output readable
    warnings.filterwarnings("ignore")               # silence Agg's non-GUI show() notice
    args.out.mkdir(parents=True, exist_ok=True)

    # --- build the simulator + a graded, source-agnostic sequencer ----------------
    sim = BenchSimulator(sample_rate_hz=10.0)
    _seed_channels(sim, args.seed)

    purpose = TestPurpose(intent="verification", repair_stage="as_left",
                          context="repair_overhaul")     # verification → grades pass/fail
    profile_id = sim.profile.identity.get("id", "pc200-8-hpv95")
    builder = RunRecordBuilder(
        id=f"DEMO-{args.serial}", profile=profile_id, dut_serial=args.serial,
        operator="demo-operator", po_number=args.po, purpose=purpose, mode="training",
    )
    incoming = CleanlinessReading(                       # the as-found contamination evidence
        iso_code=(22, 20, 17), sample_point="incoming_fluid",
        water_rh_pct=38.0, reference=args.po,
    )
    seq = TestSequencer(
        sim, builder, simulated_sources(sim),
        realtime=not args.fast, incoming_sample=incoming, reference=args.po,
    )

    # --- collect the full-resolution, un-smoothed waveform for the plots ----------
    times: list[float] = []
    data: dict[str, list[float]] = {ch.name: [] for ch in sim.channels}

    def on_tick(s: BenchSimulator) -> None:
        times.append(round(s.elapsed_time, 2))
        for ch in s.channels:
            data[ch.name].append(ch.current_value)
        if s.sample_count % 10 == 0:                     # 1 Hz progress line
            print(f"  t={s.elapsed_time:6.1f}s  P={s.pressure.current_value:6.1f} bar  "
                  f"Q={s.flow.current_value:6.1f} L/min  T={s.torque.current_value:6.1f} Nm  "
                  f"[{seq.state.value}]")

    print(f"BenchVision end-to-end demo  ·  "
          f"{'FAST (stepped)' if args.fast else 'REAL-TIME'}  ·  seed={args.seed}\n")
    record = seq.run(on_tick=on_tick)
    print(f"\nRun complete: {' → '.join(st.value for st in seq.history)}")
    note = f"  ({record.verdict.note})" if record.verdict.note else ""
    print(f"Verdict: {record.verdict.summary}{note}\n")

    # --- 1) graphs (reuse the dashboard plotters; Agg → saved, no blocking show) ---
    no_fault = float("inf")                              # clean run: no fault marker
    save_waveform_plot(times, data, sim.channels, no_fault)
    save_characteristic_curve(times, data, no_fault, sim.profile, sim.registry)

    # --- 2) the assembled run record, as JSON -------------------------------------
    JsonFileRunRecordRepository(args.out).save(record)
    json_path = args.out / f"{record.id}.json"

    # --- 3) the training-marked certificate PDF -----------------------------------
    pdf = generate_certificate_pdf(record, sim.profile, sim.registry)
    pdf_path = args.out / f"{record.id}-certificate.pdf"
    pdf_path.write_bytes(pdf)
    pdf_ok = pdf[:4] == b"%PDF"

    print("Artefacts:")
    print(f"  run-record JSON : {json_path}")
    print(f"  certificate PDF : {pdf_path}  "
          f"({'%PDF' if pdf_ok else '??'}, {len(pdf):,} bytes, training-watermarked)")
    print(f"  graphs (PNG)    : saved alongside {Path(__file__).parent} "
          f"(dashboard waveform + characteristic curve)")


if __name__ == "__main__":
    main()
