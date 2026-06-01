"""
bench_dashboard.py

BenchVision — Live Sensor Dashboard
Real-time terminal UI using the `rich` library.

Requires:  pip install rich plotext

Runs the full 120-second fault-injection demo:
  • 0–80s  — normal test cycle (ramp up → hold at operating values)
  • t=80s  — all five channels receive fault injection simultaneously
  • 80–120s — fault state maintained; history graph shows the event clearly

Run with:  python3 bench_dashboard.py
"""

import argparse
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from bench_simulator import BenchSimulator, ChannelState

# ── Config ────────────────────────────────────────────────────────────────────

FAULT_TIME   = 80.0   # seconds — inject all faults at this timestamp
SAMPLE_RATE  = 10.0   # Hz
DURATION     = 120    # seconds
BAR_WIDTH    = 22     # characters for the live gauge bar
HISTORY_LEN  = 120    # data points stored (sampled at 1 Hz = 120s of history)
SPARKLINE_W  = 40     # characters wide for the in-panel sparkline

SPARK_CHARS  = "▁▂▃▄▅▆▇█"

# ── State styles ──────────────────────────────────────────────────────────────
# border_style must NOT be "dim" — it makes Panel titles invisible.

STATE_STYLE: dict[str, tuple[str, str]] = {
    "idle":       ("bright_black", "○  IDLE"),
    "ramp_up":    ("cyan",         "↑  RAMP UP"),
    "hold":       ("bold green",   "●  HOLD"),
    "ramp_down":  ("yellow",       "↓  RAMP DOWN"),
    "fault":      ("bold red",     "⚠  FAULT"),
}

# ── Per-channel identity colours ──────────────────────────────────────────────
# Used for panel border, title, sparkline, and history graph line.
# Must be valid in both `rich` and `plotext`.  Fault overrides all to red.

CHANNEL_COLORS: dict[str, str] = {
    "Pressure":    "blue",
    "Flow":        "green",
    "Temperature": "magenta",
    "Torque":      "cyan",
    "Speed":       "yellow",
}

# ── Rendering helpers ─────────────────────────────────────────────────────────

def gauge_bar(value: float, lo: float, hi: float, fault: bool) -> Text:
    """Horizontal block-character bar scaled to channel range."""
    frac   = max(0.0, min(1.0, (value - lo) / (hi - lo)))
    filled = round(frac * BAR_WIDTH)
    bar    = "█" * filled + "░" * (BAR_WIDTH - filled)
    return Text(bar, style="bold red" if fault else "green")


def sparkline(
    values: list[float], lo: float, hi: float, fault: bool, color: str = "green"
) -> Text:
    """
    Mini time-series built from Unicode block characters.
    Shows the last SPARKLINE_W data points — builds left to right as the
    test runs, giving Devon the 'graph forming' effect inside each panel.
    """
    display = list(values)[-SPARKLINE_W:]          # most recent N points
    pad     = SPARKLINE_W - len(display)
    chars   = " " * pad                            # blank until data arrives
    for v in display:
        frac = max(0.0, min(1.0, (v - lo) / (hi - lo)))
        idx  = min(int(frac * len(SPARK_CHARS)), len(SPARK_CHARS) - 1)
        chars += SPARK_CHARS[idx]
    return Text(chars, style=f"bold red" if fault else f"bold {color}")


def channel_panel(ch, history: deque) -> Panel:
    """Render one sensor channel as a bordered Panel with value, gauge, sparkline."""
    state    = ch.state.value
    is_fault = state == "fault"
    style, label = STATE_STYLE.get(state, ("white", state))
    ch_color = CHANNEL_COLORS.get(ch.name, "white")
    border   = "red" if is_fault else ch_color

    grid = Table.grid(padding=(0, 1))
    grid.add_column(min_width=14, justify="right")
    grid.add_column()

    # Engineering value
    grid.add_row(
        Text(f"{ch.current_value:8.1f}", style="bold red" if is_fault else f"bold {ch_color}"),
        Text(ch.unit, style="dim" if not is_fault else "dim red"),
    )
    # 4-20 mA
    grid.add_row(
        Text(f"{ch.to_4_20ma(ch.current_value):.2f} mA", style="dim white" if not is_fault else "dim red"),
        Text(""),
    )
    # Live gauge bar
    grid.add_row(
        gauge_bar(ch.current_value, ch.min_value, ch.max_value, is_fault),
        Text(""),
    )
    # Sparkline — builds over time (channel colour, red on fault)
    grid.add_row(
        sparkline(list(history), ch.min_value, ch.max_value, is_fault, ch_color),
        Text(""),
    )
    # State label
    grid.add_row(
        Text(label, style=style),
        Text(""),
    )

    title = Text(f" {ch.name} ", style=f"bold {border}")
    return Panel(grid, title=title, border_style=border, padding=(0, 1))


def history_graph(
    times: deque,
    by_channel: dict[str, deque],
    channels: list,
) -> Panel:
    """
    Full-width line graph using plotext — shows all five channels as
    percentage of operating range so they're comparable on one axis.
    Falls back to a plain-text sparkline table if plotext isn't installed.
    """
    try:
        import plotext as plt

        plt.clf()
        plt.canvas_color("default")
        plt.axes_color("default")
        plt.ticks_color("default")
        plt.plotsize(None, 14)     # auto-width, 14 rows tall
        plt.ylim(0, 110)
        plt.xlabel("Time (s)")
        plt.ylabel("% of range")

        if times:
            t = list(times)
            for ch in channels:
                hist = list(by_channel[ch.name])
                if hist:
                    pct = [
                        (v - ch.min_value) / (ch.max_value - ch.min_value) * 100
                        for v in hist
                    ]
                    plt.plot(t, pct, label=ch.name, color=CHANNEL_COLORS.get(ch.name, "white"))

        content = Text.from_ansi(plt.build())

    except ImportError:
        # Graceful fallback — simple sparkline table, no extra dependency needed
        grid = Table.grid(padding=(0, 1))
        grid.add_column(min_width=12, style="dim white")
        grid.add_column()
        for ch in channels:
            hist     = list(by_channel[ch.name])
            is_fault = ch.state == ChannelState.FAULT
            ch_color = CHANNEL_COLORS.get(ch.name, "white")
            grid.add_row(
                Text(ch.name, style="bold red" if is_fault else f"bold {ch_color}"),
                sparkline(hist, ch.min_value, ch.max_value, is_fault, ch_color),
            )
        content = grid

    return Panel(
        content,
        title=" Sensor History — all channels as % of operating range ",
        border_style="bright_black",
        padding=(0, 1),
    )


def make_display(
    sim: BenchSimulator,
    fault_injected: bool,
    history_times: deque,
    history_by_channel: dict[str, deque],
    no_fault: bool = False,
) -> Group:
    """Compose the full dashboard for one render frame."""
    any_fault = any(ch.state == ChannelState.FAULT for ch in sim.channels)

    # ── Header ────────────────────────────────────────────────────────────────
    if any_fault:
        status = Text("⚠  FAULT ACTIVE", style="bold red")
    elif sim.elapsed_time < 1:
        status = Text("◌  INITIALISING", style="dim white")
    else:
        status = Text("●  RUNNING", style="bold green")

    header = Panel(
        Align.center(Text.assemble(
            Text("BenchVision", style="bold white"),
            Text("  ·  Hydraulic Test Bench  ·  ", style="dim white"),
            Text(f"t = {sim.elapsed_time:6.1f}s  ", style="bold cyan"),
            status,
        )),
        border_style="red" if any_fault else "white",
        padding=(0, 2),
    )

    # ── Channel panels ─────────────────────────────────────────────────────────
    panels = [channel_panel(ch, history_by_channel[ch.name]) for ch in sim.channels]
    row1   = Columns([panels[0], panels[1]], equal=True, expand=True)
    row2   = Columns([panels[2], panels[3]], equal=True, expand=True)
    row3   = panels[4]

    # ── History graph ──────────────────────────────────────────────────────────
    graph  = history_graph(history_times, history_by_channel, sim.channels)

    # ── Footer ────────────────────────────────────────────────────────────────
    if no_fault:
        footer = Panel(
            Align.center(Text(
                "◌  CLEAN RUN — no fault injection",
                style="dim white",
            )),
            border_style="bright_black",
            padding=(0, 1),
        )
    elif fault_injected and any_fault:
        footer = Panel(
            Align.center(Text(
                "⚠  FAULT EVENT DETECTED  —  "
                "Overpressure · Cavitation · Overheat · Loss of Load · Shaft Slip",
                style="bold red",
            )),
            border_style="red",
            padding=(0, 1),
        )
    else:
        remaining = max(0.0, FAULT_TIME - sim.elapsed_time)
        footer = Panel(
            Align.center(Text(
                f"Fault injection in {remaining:.0f}s",
                style="bold yellow" if remaining < 15 else "white",
            )),
            border_style="bright_black",
            padding=(0, 1),
        )

    return Group(header, row1, row2, row3, graph, footer)


# ── Waveform plot ─────────────────────────────────────────────────────────────

def save_waveform_plot(
    times: list[float],
    by_channel: dict[str, list[float]],
    channels: list,
    fault_time: float,
) -> None:
    """
    Generate a full-run waveform figure using matplotlib.

    • One subplot per channel, each in its matching CHANNEL_COLORS colour.
    • Dashed red vertical line marks the fault injection moment.
    • Red-shaded region covers the fault period through end of test.
    • Figure is saved as a timestamped PNG and opened in a window.

    Requires:  pip install matplotlib
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        print("\n  matplotlib not installed — skipping waveform plot.")
        print("  Install with:  pip install matplotlib\n")
        return

    t      = list(times)
    n      = len(channels)
    max_t  = t[-1] if t else fault_time + 40

    fig, axes = plt.subplots(
        n, 1,
        figsize=(14, 2.6 * n),
        sharex=True,
    )
    fig.suptitle(
        f"BenchVision  ·  Hydraulic Test Bench\n"
        f"{datetime.now().strftime('%Y-%m-%d   %H:%M:%S')}",
        fontsize=12,
        fontweight="bold",
        y=1.01,
    )
    fig.patch.set_facecolor("#faf8f2")

    for ax, ch in zip(axes, channels):
        color  = CHANNEL_COLORS.get(ch.name, "steelblue")
        values = list(by_channel[ch.name])
        t_trim = t[: len(values)]

        ax.set_facecolor("#faf8f2")

        # ── Fault shading ──────────────────────────────────────────────────
        if fault_time <= max_t:
            ax.axvspan(fault_time, max_t, color="red", alpha=0.07, zorder=0)
            ax.axvline(
                x=fault_time,
                color="red",
                linewidth=1.2,
                linestyle="--",
                alpha=0.75,
                zorder=2,
            )

        # ── Waveform ───────────────────────────────────────────────────────
        ax.plot(t_trim, values, color=color, linewidth=1.6, zorder=3)

        # ── Axes cosmetics ─────────────────────────────────────────────────
        ax.set_ylabel(f"{ch.name}\n({ch.unit})", fontsize=8.5, labelpad=6)
        ax.tick_params(labelsize=8)
        ax.grid(True, color="#cccccc", linewidth=0.5, alpha=0.6)
        ax.set_xlim(0, max_t)
        for spine in ax.spines.values():
            spine.set_edgecolor("#cccccc")

        # ── Fault label (first channel only) ──────────────────────────────
        if ch is channels[0] and fault_time <= max_t:
            ymin, ymax = ax.get_ylim()
            ax.text(
                fault_time + 0.8,
                ymax - (ymax - ymin) * 0.12,
                "⚠ FAULT",
                color="red",
                fontsize=8,
                fontweight="bold",
                va="top",
            )

    axes[-1].set_xlabel("Time (s)", fontsize=9)
    plt.tight_layout()

    # ── Save ───────────────────────────────────────────────────────────────
    stamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(__file__).parent / f"benchvision_{stamp}.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())

    print(f"\n  Waveform saved → {out_path}")
    print("  Close the waveform window to continue to the characteristic curve.")
    try:
        plt.show()
    except KeyboardInterrupt:
        plt.close("all")
        print("\n  Window closed — continuing.")


# ── Characteristic curve ──────────────────────────────────────────────────────

def save_characteristic_curve(
    times: list[float],
    by_channel: dict[str, list[float]],
    fault_time: float,
    profile=None,
    registry=None,
) -> None:
    """
    Generate the pump characteristic curve: pressure on the X axis,
    flow (downward) and torque (upward) on dual Y axes.

    • Only pre-fault data is used — the clean operating characteristic.
    • Raw scatter shows the real DAQ noise.
    • Theoretical lines come from the FORMULA ENGINE — the same registry-resolved
      formulas the live channels use, parameterised by the pump profile. Nothing
      pump-specific is hard-coded here any more (was Q=245−0.5P, T=P×95/62.8,
      ±15 band — all now read from the profile / registry).
    • The acceptance band is the profile's digitised envelope, not a placeholder.

    Requires:  pip install matplotlib
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("\n  matplotlib not installed — skipping characteristic curve.")
        return

    if profile is None or registry is None:
        from bench_simulator import BenchSimulator
        _s = BenchSimulator()
        profile, registry = _s.profile, _s.registry

    # ── Filter to pre-fault clean data ────────────────────────────────────────
    pre = [(t, i) for i, t in enumerate(times) if t <= fault_time]
    if len(pre) < 10:
        print("\n  Not enough pre-fault data for characteristic curve — skipping.")
        return

    idx       = [i for _, i in pre]
    pressure  = np.array([by_channel["Pressure"][i] for i in idx])
    flow      = np.array([by_channel["Flow"][i]     for i in idx])
    torque    = np.array([by_channel["Torque"][i]   for i in idx])

    # Sort by ascending pressure for clean curve lines
    order    = np.argsort(pressure)
    p_s      = pressure[order]
    f_s      = flow[order]
    t_s      = torque[order]

    # ── Theoretical lines — straight from the formula engine ───────────────────
    flow_ref   = profile.channels["flow"].formula
    torque_ref = profile.channels["torque"].formula
    p_theory   = np.linspace(0, max(p_s.max(), profile.pressure_sweep.max), 300)
    f_theory   = np.array([registry.evaluate(flow_ref, profile.flow_inputs(p)) for p in p_theory])
    # Torque uses the engine flow at each pressure (live-flow derivation).
    t_theory   = np.array([
        registry.evaluate(torque_ref, profile.torque_inputs(p, registry.evaluate(flow_ref, profile.flow_inputs(p))))
        for p in p_theory
    ])

    # Acceptance band — the profile's digitised polyline (not a ± placeholder).
    band     = profile.acceptance["flow"]
    f_lower  = np.array([band.limits_at(p)[0] for p in p_theory])
    f_upper  = np.array([band.limits_at(p)[1] for p in p_theory])

    # ── Figure ─────────────────────────────────────────────────────────────────
    fig, ax1 = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#faf8f2")
    ax1.set_facecolor("#faf8f2")
    fig.suptitle(
        f"BenchVision  ·  {profile.identity.get('display_name', 'Pump')}  ·  Characteristic Curve\n"
        f"{datetime.now().strftime('%Y-%m-%d   %H:%M:%S')}",
        fontsize=12, fontweight="bold", y=1.01,
    )

    # ── Flow (left Y axis, green) ──────────────────────────────────────────────
    ax1.scatter(p_s, f_s, color="green", s=4, alpha=0.35, label="Flow — measured")
    ax1.plot(p_theory, f_theory, color="green", linewidth=2.0,
             label=f"Flow — engine ({flow_ref})")
    ax1.fill_between(p_theory, f_lower, f_upper,
                     color="green", alpha=0.12, label="Flow acceptance band (chart-read limits)")
    ax1.plot(p_theory, f_upper, color="green", linewidth=0.8, linestyle="--", alpha=0.5)
    ax1.plot(p_theory, f_lower, color="green", linewidth=0.8, linestyle="--", alpha=0.5)

    ax1.set_xlabel("Pump discharge pressure (bar)", fontsize=10)
    ax1.set_ylabel("Flow (L/min)", color="green", fontsize=10)
    ax1.tick_params(axis="y", labelcolor="green", labelsize=8)
    ax1.tick_params(axis="x", labelsize=8)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    ax1.grid(True, color="#cccccc", linewidth=0.5, alpha=0.6)
    for spine in ax1.spines.values():
        spine.set_edgecolor("#cccccc")

    # ── Torque (right Y axis, cyan) ────────────────────────────────────────────
    ax2 = ax1.twinx()
    ax2.scatter(p_s, t_s, color="cyan", s=4, alpha=0.35, label="Torque — measured")

    # Torque is a MONITORED REFERENCE curve, not a graded pass/fail channel. The
    # profile's [acceptance.torque] band is a zero-width placeholder on purpose
    # (upper == lower == nominal) until the chart's torque limit lines are transcribed.
    # Read the band from the profile and decide how to render: a zero-width band must
    # NOT be drawn as an envelope (it would "fail" every sample) — show torque as a
    # reference line. If a real graded band (upper > lower) is ever added, shade it.
    tq_band   = profile.acceptance.get("torque")
    tq_graded = (
        tq_band is not None
        and tq_band.mode == "polyline"
        and tq_band.points
        and max(u - l for _p, u, l in tq_band.points) > 1e-6
    )
    if tq_graded:
        t_lower = np.array([tq_band.limits_at(p)[0] for p in p_theory])
        t_upper = np.array([tq_band.limits_at(p)[1] for p in p_theory])
        ax2.fill_between(p_theory, t_lower, t_upper, color="cyan", alpha=0.12,
                         label="Torque acceptance band")
        torque_label = f"Torque — engine ({torque_ref})"
    else:
        torque_label = f"Torque — engine ({torque_ref}) · reference (monitored, not graded)"
    ax2.plot(p_theory, t_theory, color="cyan", linewidth=2.0, label=torque_label)
    ax2.set_ylabel("Torque (Nm)  ·  reference", color="cyan", fontsize=10)
    ax2.tick_params(axis="y", labelcolor="cyan", labelsize=8)
    ax2.set_ylim(bottom=0)
    ax2.set_facecolor("#faf8f2")

    # ── Devon's spoken reference reads (illustrative — his eyeball values) ──────
    ax1.plot([50, 200], [220, 145], "gD", markersize=7,
             label="Devon's flow reads (V1)", zorder=5)
    ax2.plot([100, 250], [400, 590], "cD", markersize=7,
             label="Devon's torque reads (V2)", zorder=5)

    # ── Combined legend ────────────────────────────────────────────────────────
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2, labels1 + labels2,
        loc="center right", fontsize=8, framealpha=0.9,
    )

    plt.tight_layout()

    # ── Save ───────────────────────────────────────────────────────────────────
    stamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(__file__).parent / f"benchvision_characteristic_{stamp}.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\n  Characteristic curve saved → {out_path}")
    try:
        plt.show()
    except KeyboardInterrupt:
        plt.close("all")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_dashboard() -> None:
    parser = argparse.ArgumentParser(description="BenchVision live dashboard")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Run without fault injection — full clean test cycle",
    )
    args       = parser.parse_args()
    no_fault   = args.clean
    fault_time = float("inf") if no_fault else FAULT_TIME

    console        = Console()
    sim            = BenchSimulator(sample_rate_hz=SAMPLE_RATE)
    target         = int(DURATION * SAMPLE_RATE)
    fault_injected = False

    # Per-channel history, sampled at 1 Hz (every 10 ticks) — for the live graph
    h_times = deque(maxlen=HISTORY_LEN)
    h_data  = {ch.name: deque(maxlen=HISTORY_LEN) for ch in sim.channels}

    # Full-resolution history at 10 Hz — for the post-run waveform plot
    full_times: list[float]              = []
    full_data:  dict[str, list[float]]   = {ch.name: [] for ch in sim.channels}

    sim.start_test()

    # Ctrl-C stops the run cleanly (no traceback on the recording) and still draws
    # the post-run plots from whatever data was collected.
    stopped_early = False
    try:
        with Live(
            make_display(sim, fault_injected, h_times, h_data, no_fault),
            console=console,
            refresh_per_second=10,
            screen=True,
        ) as live:
            while sim.sample_count < target:
                sim.tick()
                time.sleep(sim.dt)

                # Record full-resolution history at 10 Hz (every tick)
                full_times.append(round(sim.elapsed_time, 2))
                for ch in sim.channels:
                    full_data[ch.name].append(ch.current_value)

                # Record history at 1 Hz (for live graph)
                if sim.sample_count % 10 == 0:
                    h_times.append(round(sim.elapsed_time, 1))
                    for ch in sim.channels:
                        h_data[ch.name].append(ch.current_value)

                # Fault injection — skipped entirely in --clean mode
                if not no_fault and not fault_injected and sim.elapsed_time >= fault_time:
                    sim.pressure.inject_fault_overpressure()   # +50 bar  → ~430 bar
                    sim.flow.inject_fault_cavitation()          # -80 L/min → ~120 L/min
                    sim.temperature.inject_fault_overheat()     # +30°C    → ~75°C
                    sim.torque.inject_fault_loss_of_load()      # -500 Nm  → ~75 Nm
                    sim.speed.inject_fault_shaft_slip()         # -600 RPM → ~400 RPM
                    fault_injected = True

                live.update(make_display(sim, fault_injected, h_times, h_data, no_fault))
    except KeyboardInterrupt:
        stopped_early = True

    console.print()
    if stopped_early:
        console.rule("[bold yellow]BenchVision — Stopped early (Ctrl-C)[/]")
    else:
        console.rule("[bold white]BenchVision — Test Complete[/]")
    console.print(
        f"  Duration: {sim.elapsed_time:.0f}s  ·  "
        f"Samples: {sim.sample_count}  ·  "
        f"Rate: {SAMPLE_RATE:.0f} Hz",
        style="dim",
    )
    console.print()

    # ── Post-run plots ────────────────────────────────────────────────────
    save_waveform_plot(full_times, full_data, sim.channels, fault_time)
    save_characteristic_curve(full_times, full_data, fault_time, sim.profile, sim.registry)


if __name__ == "__main__":
    run_dashboard()
