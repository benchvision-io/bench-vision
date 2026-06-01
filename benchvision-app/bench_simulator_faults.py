"""
bench_simulator_faults.py

Part 3 Exercise: Fault injection at 80 seconds.

Step 1: Pressure fault at t=80s (guide's exact next action)
Step 2: All five channels fault at t=80s

Run with:  python3 bench_simulator_faults.py
"""

import logging
import time
from bench_simulator import BenchSimulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)

FAULT_TIME = 80.0   # seconds — inject all faults at this timestamp


def run_with_faults():
    print("\n" + "=" * 80)
    print("BenchVision — Fault Injection Demo (t=80s)")
    print("=" * 80)
    print(f"\nAll five channels will have faults injected at t={FAULT_TIME}s")
    print("Watch the log for *** FAULT *** markers and WARNING lines.\n")

    sim = BenchSimulator(sample_rate_hz=10.0)
    sim.start_test()

    log_interval = 10       # Log every 10 ticks = 1 Hz output
    target_duration = 120   # seconds
    target_samples = int(target_duration * sim.sample_rate_hz)

    fault_injected = False

    while sim.sample_count < target_samples:
        sim.tick()
        time.sleep(sim.dt)   # Pause 0.1s per tick — runs at real 10 Hz DAQ rate

        # ----------------------------------------------------------------
        # FAULT INJECTION — fires once when elapsed time crosses 80 seconds
        # ----------------------------------------------------------------
        if not fault_injected and sim.elapsed_time >= FAULT_TIME:
            print(f"\n{'!'*60}")
            print(f"  INJECTING FAULTS at t={sim.elapsed_time:.1f}s")
            print(f"{'!'*60}\n")

            # Each channel has its own realistic fault type:
            sim.pressure.inject_fault_overpressure()    # Pressure spikes +50 bar → ~430 bar
            sim.flow.inject_fault_cavitation()          # Flow drops -80 L/min → ~120 L/min
            sim.temperature.inject_fault_overheat()     # Temp jumps +30°C → ~75°C
            sim.torque.inject_fault_loss_of_load()      # Torque collapses -500 Nm → ~75 Nm
            sim.speed.inject_fault_shaft_slip()         # Speed drops -600 RPM → ~400 RPM

            fault_injected = True
        # ----------------------------------------------------------------

        if sim.sample_count % log_interval == 0:
            sim.log_readings()

    print("\n" + "=" * 80)
    print("Run complete. Review the WARNING lines above to see each fault event.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_with_faults()
