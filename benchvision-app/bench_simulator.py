"""
bench_simulator.py

Realistic DAQ sensor simulator for BenchVision hydraulic test bench.
Produces 4-20 mA equivalent signals with ramps, noise, and fault injection.

Python 3.13+, type hints, numpy for noise generation.

From: BenchVision Layer 1 - Sensor Simulator
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
import logging
import math
import time
import numpy as np
from datetime import datetime

from formula_registry import FormulaRegistry, build_default_registry
from pump_profile import PumpProfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)


class ChannelState(Enum):
    """Sensor channel operational state."""
    IDLE = "idle"
    RAMP_UP = "ramp_up"
    HOLD = "hold"
    RAMP_DOWN = "ramp_down"
    FAULT = "fault"


@dataclass
class SensorChannel:
    """
    Base class for a single sensor channel.
    Produces engineering-unit values (bar, L/min, °C, etc.) with realistic noise.
    DAQ hardware will convert these to 4-20 mA or 0-10 V for actual I/O.
    """
    name: str
    unit: str
    min_value: float
    max_value: float
    noise_std_dev: float
    sample_rate_hz: float = 10.0  # Typical DAQ sample rate

    # Internal state
    current_value: float = field(default=0.0, init=False)
    state: ChannelState = field(default=ChannelState.IDLE, init=False)
    timestamp: float = field(default=0.0, init=False)
    rng: np.random.Generator = field(
        default_factory=lambda: np.random.default_rng(), init=False
    )

    def __post_init__(self) -> None:
        if self.min_value >= self.max_value:
            raise ValueError(f"{self.name}: min_value must be < max_value")
        if self.noise_std_dev < 0:
            raise ValueError(f"{self.name}: noise_std_dev must be >= 0")
        if self.sample_rate_hz <= 0:
            raise ValueError(f"{self.name}: sample_rate_hz must be > 0")
        self.current_value = self.min_value

    def get_dt(self) -> float:
        """Time step per sample (seconds)."""
        return 1.0 / self.sample_rate_hz

    def apply_noise(self, value: float) -> float:
        """Apply Gaussian noise to a value."""
        if self.noise_std_dev > 0:
            noise = self.rng.normal(0, self.noise_std_dev)
            return float(np.clip(value + noise, self.min_value, self.max_value))
        return value

    def clamp(self, value: float) -> float:
        """Clamp value to valid range."""
        return float(np.clip(value, self.min_value, self.max_value))

    def to_4_20ma(self, value: float) -> float:
        """
        Convert engineering unit to 4-20 mA equivalent.
        Formula: mA = 4 + (value - min) / (max - min) * 16
        """
        normalized = (self.clamp(value) - self.min_value) / (self.max_value - self.min_value)
        return 4.0 + normalized * 16.0

    def tick(self, dt: float) -> None:
        """
        Advance sensor by one time step.
        Override in subclasses to implement specific test cycle behaviour.
        """
        self.timestamp += dt
        self.current_value = self.apply_noise(self.current_value)

    def __repr__(self) -> str:
        ma = self.to_4_20ma(self.current_value)
        return (
            f"{self.name}: {self.current_value:.2f} {self.unit} "
            f"({ma:.2f} mA) [{self.state.value}]"
        )


# ============================================================================
# PRESSURE CHANNEL
# ============================================================================

@dataclass
class PressureChannel(SensorChannel):
    """
    Pressure transducer (0-500 bar, 4-20 mA).
    Simulates pump startup ramp, pressure hold, and unload.
    """
    ramp_up_time: float = 30.0      # Seconds to reach target pressure
    ramp_down_time: float = 20.0    # Seconds to unload
    target_pressure: float = 350.0  # Bar, typical operating setpoint
    hold_time: float = 60.0         # Seconds at target before ramp down

    cycle_start_time: float = field(default=0.0, init=False)
    cycle_phase: str = field(default="idle", init=False)

    def __post_init__(self) -> None:
        if not (0 < self.target_pressure < 500):
            raise ValueError(
                f"{self.name}: target_pressure must be 0-500 bar, got {self.target_pressure}"
            )
        super().__post_init__()

    def start_test_cycle(self) -> None:
        """Begin a pressure ramp-up from idle."""
        self.cycle_start_time = self.timestamp
        self.cycle_phase = "ramp_up"
        self.state = ChannelState.RAMP_UP
        logger.info(
            f"{self.name}: Starting test cycle, ramping to "
            f"{self.target_pressure} bar over {self.ramp_up_time}s"
        )

    def inject_fault_overpressure(self) -> None:
        """Simulate pressure overshoot (pump cavitation or relief valve failure)."""
        self.current_value = min(self.current_value + 50, self.max_value)
        self.state = ChannelState.FAULT
        logger.warning(
            f"{self.name}: FAULT — Overpressure spike to {self.current_value:.1f} bar"
        )

    def tick(self, dt: float) -> None:
        """Advance pressure sensor through test cycle."""
        super().tick(dt)
        elapsed = self.timestamp - self.cycle_start_time

        if self.cycle_phase == "ramp_up":
            if elapsed < self.ramp_up_time:
                self.current_value = (elapsed / self.ramp_up_time) * self.target_pressure
            else:
                self.current_value = self.target_pressure
                self.cycle_phase = "hold"
                self.cycle_start_time = self.timestamp
                self.state = ChannelState.HOLD
                logger.info(f"{self.name}: Reached target pressure {self.target_pressure} bar")

        elif self.cycle_phase == "hold":
            if elapsed < self.hold_time:
                self.current_value = self.apply_noise(self.target_pressure)
            else:
                self.cycle_phase = "ramp_down"
                self.cycle_start_time = self.timestamp
                self.state = ChannelState.RAMP_DOWN
                logger.info(f"{self.name}: Unloading pressure")

        elif self.cycle_phase == "ramp_down":
            if elapsed < self.ramp_down_time:
                self.current_value = self.target_pressure * (1 - elapsed / self.ramp_down_time)
            else:
                self.current_value = 0
                self.cycle_phase = "idle"
                self.state = ChannelState.IDLE
                logger.info(f"{self.name}: Cycle complete")

        self.current_value = self.clamp(self.current_value)
        if self.state != ChannelState.FAULT:
            self.current_value = self.apply_noise(self.current_value)


# ============================================================================
# FLOW CHANNEL
# ============================================================================

@dataclass
class FlowChannel(SensorChannel):
    """
    Flow meter (0-605 L/min, 4-20 mA) — FORMULA-DRIVEN (refactored 2026-05-30).

    Flow is NOT independent and is NO LONGER hard-coded. It is computed by a
    named, version-tagged formula resolved from the formula registry and
    parameterised entirely by the loaded ``PumpProfile``. The channel holds no
    pump-specific constants of its own — displacement-derived no-load flow, the
    PC cut-in knee and the constant-power term all arrive from config.

    For the PC200-8 HPV95 the profile selects ``pump_flow_pc_destroke_v1``:
    flat at ~224 L/min to the ~130 bar PC cut-in, then a constant-power
    hyperbola ``Q = 29120 / P``. That shape matches the digitised manufacturer
    chart and is the shape that lets torque plateau emerge from live flow.
    (The earlier linear ``Q = 245 − 0.5·P`` model is still available in the
    registry as ``pump_flow_linear_v1`` for genuinely linear pumps and for the
    faithful-refactor test — see ``validate_flow_refactor.py``.)

    Another pump is a different profile, not different code.

    The pressure channel reference is injected at start_test_cycle() so tick()
    can read live pressure for each derivation. Channel state mirrors pressure.
    """
    profile: Optional[PumpProfile] = None
    registry: Optional[FormulaRegistry] = None

    _pressure_ref: Optional[object] = field(default=None, init=False, repr=False)
    _formula_ref: str = field(default="", init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.profile is None:
            raise ValueError(f"{self.name}: a PumpProfile is required (formula-driven channel)")
        if self.registry is None:
            self.registry = build_default_registry()
        self._formula_ref = self.profile.channels["flow"].formula
        # Fail fast at construction if the config names a formula we don't have,
        # or omits an input the formula needs (probed at a representative pressure).
        probe = self.profile.flow_inputs(pressure_bar=0.0)
        self.registry.evaluate(self._formula_ref, probe)

    @property
    def no_load_flow(self) -> float:
        """No-load flow, read from the profile (for init / logging only)."""
        return float(self.profile.channels["flow"].inputs.get("no_load_flow", self.min_value))

    def start_test_cycle(self, pressure_channel=None) -> None:
        """
        Begin the flow cycle.  Pass in the pressure channel instance so
        tick() can derive flow continuously from live pressure readings.
        """
        self._pressure_ref = pressure_channel
        self.state = ChannelState.RAMP_UP
        self.current_value = self._derive_flow()   # high flow at zero load
        logger.info(
            f"{self.name}: Starting formula-driven flow cycle "
            f"(formula={self._formula_ref}, profile={self.profile.identity.get('id', '?')})"
        )

    def _derive_flow(self) -> float:
        """
        Compute flow for the live pressure via the registry-resolved formula,
        parameterised by the pump profile. No pump constants live here.
        Falls back to no-load flow if the pressure reference is not yet wired.
        """
        p = self._pressure_ref.current_value if self._pressure_ref is not None else 0.0
        value = self.registry.evaluate(self._formula_ref, self.profile.flow_inputs(pressure_bar=p))
        return max(self.min_value, value)

    def inject_fault_cavitation(self) -> None:
        """Simulate cavitation: flow drops erratically toward zero."""
        self.current_value = max(self.current_value - 80, 0)
        self.state = ChannelState.FAULT
        logger.warning(
            f"{self.name}: FAULT — Cavitation, flow dropped to {self.current_value:.1f} L/min"
        )

    def tick(self, dt: float) -> None:
        super().tick(dt)

        if self.state == ChannelState.FAULT:
            # Fault state: hold the fault value, do not derive
            self.current_value = self.clamp(self.current_value)
            return

        if self._pressure_ref is not None:
            # Mirror the pressure channel's state
            self.state = self._pressure_ref.state

        # Derive flow from current pressure at all non-fault phases
        self.current_value = self.apply_noise(self._derive_flow())
        self.current_value = self.clamp(self.current_value)


# ============================================================================
# TEMPERATURE CHANNEL
# ============================================================================

@dataclass
class TemperatureChannel(SensorChannel):
    """
    Temperature sensor (0-120°C, 4-20 mA).
    Models slow exponential warm-up and cool-down due to thermal lag.
    """
    ambient_temp: float = 20.0
    warm_up_time_constant: float = 300.0  # Seconds (5 min to reach 63% of target)
    target_temp: float = 75.0             # °C, typical operating temperature
    hold_time: float = 60.0

    cycle_start_time: float = field(default=0.0, init=False)
    cycle_phase: str = field(default="idle", init=False)

    def __post_init__(self) -> None:
        super().__post_init__()

    def start_test_cycle(self) -> None:
        self.current_value = self.ambient_temp
        self.cycle_start_time = self.timestamp
        self.cycle_phase = "warm_up"
        self.state = ChannelState.RAMP_UP
        logger.info(
            f"{self.name}: Starting warm-up from {self.ambient_temp}°C to {self.target_temp}°C"
        )

    def inject_fault_overheat(self) -> None:
        """Simulate overheating — temperature climbs rapidly toward limit."""
        self.current_value = min(self.current_value + 30, self.max_value)
        self.state = ChannelState.FAULT
        logger.warning(
            f"{self.name}: FAULT — Overheat, temperature at {self.current_value:.1f}°C"
        )

    def tick(self, dt: float) -> None:
        super().tick(dt)
        elapsed = self.timestamp - self.cycle_start_time

        if self.cycle_phase == "warm_up":
            # Exponential approach: T(t) = Ambient + (Target - Ambient) * (1 - e^(-t/τ))
            fraction = 1 - math.exp(-elapsed / self.warm_up_time_constant)
            self.current_value = (
                self.ambient_temp + (self.target_temp - self.ambient_temp) * fraction
            )
            if self.current_value >= self.target_temp - 1:
                self.cycle_phase = "hold"
                self.cycle_start_time = self.timestamp
                self.state = ChannelState.HOLD
                # FIX: guide had self.current_temp here (typo) — should be self.current_value
                logger.debug(
                    f"{self.name}: Reached target temperature {self.current_value:.1f}°C"
                )

        elif self.cycle_phase == "hold":
            if elapsed < self.hold_time:
                self.current_value = self.apply_noise(self.target_temp)
            else:
                self.cycle_phase = "cool_down"
                self.cycle_start_time = self.timestamp
                self.state = ChannelState.RAMP_DOWN

        elif self.cycle_phase == "cool_down":
            fraction = math.exp(-elapsed / self.warm_up_time_constant)
            self.current_value = (
                self.ambient_temp + (self.target_temp - self.ambient_temp) * fraction
            )
            if self.current_value <= self.ambient_temp + 2:
                self.current_value = self.ambient_temp
                self.cycle_phase = "idle"
                self.state = ChannelState.IDLE

        self.current_value = self.clamp(self.current_value)


# ============================================================================
# TORQUE CHANNEL
# ============================================================================

@dataclass
class TorqueChannel(SensorChannel):
    """
    Input-shaft absorption torque (0-2500 Nm) — FORMULA-DRIVEN (refactored 2026-05-30).

    Torque is not independently measured and is NO LONGER hard-coded. It is
    derived from *live flow* (not a frozen displacement) via the registry formula
    the profile selects — for the PC200-8, ``absorption_torque_from_flow_v1``:

        Vg_eff = Q·1000 / n                    (effective displacement, cc/rev per section)
        T      = P·Vg_eff·sections / (20π·η)

    Because flow follows the power-controlled destroke curve, Vg_eff falls as
    pressure rises, so torque rises through the full-stroke region then PLATEAUS
    once the pump is on its constant-power line — the Video-3 plateau, emerging
    from the physics rather than being special-cased. No pump constants live here:
    section count, mechanical efficiency and rated speed come from the profile;
    pressure and flow are read live.

    The rated speed is taken from the profile (consistent with the flow model's
    basis) rather than the live SpeedChannel — see decision-log 2026-05-30 on why
    speed-fault coupling is a deferred refinement.

    Pressure and flow channel references are injected at start_test_cycle().
    """
    profile: Optional[PumpProfile] = None
    registry: Optional[FormulaRegistry] = None

    _pressure_ref: Optional[object] = field(default=None, init=False, repr=False)
    _flow_ref: Optional[object] = field(default=None, init=False, repr=False)
    _formula_ref: str = field(default="", init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.profile is None:
            raise ValueError(f"{self.name}: a PumpProfile is required (formula-driven channel)")
        if self.registry is None:
            self.registry = build_default_registry()
        self._formula_ref = self.profile.channels["torque"].formula
        # Fail fast if the config names a missing formula or omits an input.
        self.registry.evaluate(self._formula_ref, self.profile.torque_inputs(0.0, 0.0))

    def start_test_cycle(self, pressure_channel=None, flow_channel=None) -> None:
        """Pass in the pressure and flow channels so tick() can derive torque live."""
        self._pressure_ref = pressure_channel
        self._flow_ref = flow_channel
        self.state = ChannelState.RAMP_UP
        self.current_value = self._derive_torque()
        logger.info(
            f"{self.name}: Starting formula-driven torque cycle "
            f"(formula={self._formula_ref}, derived from live flow)"
        )

    def _derive_torque(self) -> float:
        """Compute torque from live pressure + flow via the registry-resolved formula."""
        p = self._pressure_ref.current_value if self._pressure_ref is not None else 0.0
        q = self._flow_ref.current_value if self._flow_ref is not None else 0.0
        value = self.registry.evaluate(self._formula_ref, self.profile.torque_inputs(p, q))
        return max(self.min_value, value)

    def inject_fault_loss_of_load(self) -> None:
        """Simulate sudden pump unload — torque collapses toward zero."""
        self.current_value = max(self.current_value - 500, 0)
        self.state = ChannelState.FAULT
        logger.warning(
            f"{self.name}: FAULT — Loss of load, torque at {self.current_value:.1f} Nm"
        )

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.state == ChannelState.FAULT:
            self.current_value = self.clamp(self.current_value)
            return
        if self._pressure_ref is not None:
            self.state = self._pressure_ref.state    # mirror the pressure cycle
        self.current_value = self.apply_noise(self._derive_torque())
        self.current_value = self.clamp(self.current_value)


# ============================================================================
# POWER CHANNEL
# ============================================================================

@dataclass
class PowerChannel(SensorChannel):
    """
    Hydraulic power (0-100 kW) — FORMULA-DRIVEN (added 2026-05-30).

    Derived live from pressure and flow via the profile's selected formula —
    for the PC200-8, ``power_from_flow_pressure_v1`` (P_hyd[kW] = P·Q/600). In the
    pump's constant-power region this is, by construction, flat — the "power
    curve" Devon names in Video 2. No pump constants here; pressure and flow are
    read live and the unit conversion is physics, held in the registry.

    Surfaced on the characteristic / power curve rather than as a sixth live
    gauge, to keep the demo's live-panel layout stable (decision-log 2026-05-30).
    """
    profile: Optional[PumpProfile] = None
    registry: Optional[FormulaRegistry] = None

    _pressure_ref: Optional[object] = field(default=None, init=False, repr=False)
    _flow_ref: Optional[object] = field(default=None, init=False, repr=False)
    _formula_ref: str = field(default="", init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.profile is None:
            raise ValueError(f"{self.name}: a PumpProfile is required (formula-driven channel)")
        if self.registry is None:
            self.registry = build_default_registry()
        self._formula_ref = self.profile.channels["power"].formula
        self.registry.evaluate(self._formula_ref, self.profile.power_inputs(0.0, 0.0))

    def start_test_cycle(self, pressure_channel=None, flow_channel=None) -> None:
        """Pass in the pressure and flow channels so tick() can derive power live."""
        self._pressure_ref = pressure_channel
        self._flow_ref = flow_channel
        self.state = ChannelState.RAMP_UP
        self.current_value = self._derive_power()
        logger.info(
            f"{self.name}: Starting formula-driven power cycle (formula={self._formula_ref})"
        )

    def _derive_power(self) -> float:
        p = self._pressure_ref.current_value if self._pressure_ref is not None else 0.0
        q = self._flow_ref.current_value if self._flow_ref is not None else 0.0
        value = self.registry.evaluate(self._formula_ref, self.profile.power_inputs(p, q))
        return max(self.min_value, value)

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.state == ChannelState.FAULT:
            self.current_value = self.clamp(self.current_value)
            return
        if self._pressure_ref is not None:
            self.state = self._pressure_ref.state
        self.current_value = self.apply_noise(self._derive_power())
        self.current_value = self.clamp(self.current_value)


# ============================================================================
# SPEED CHANNEL
# ============================================================================

@dataclass
class SpeedChannel(SensorChannel):
    """
    Rotary encoder / tachometer (0-3000 RPM, pulse-based).
    In simulation, we produce RPM values directly; DAQ converts to frequency (Hz).
    Conversion: RPM = Hz * 60 (for 1 pulse per revolution)
    """
    ramp_up_time: float = 35.0
    ramp_down_time: float = 25.0
    target_rpm: float = 2000.0  # RPM, typical operating speed
    hold_time: float = 60.0

    cycle_start_time: float = field(default=0.0, init=False)
    cycle_phase: str = field(default="idle", init=False)

    def __post_init__(self) -> None:
        super().__post_init__()

    def start_test_cycle(self) -> None:
        self.cycle_start_time = self.timestamp
        self.cycle_phase = "ramp_up"
        self.state = ChannelState.RAMP_UP
        logger.info(f"{self.name}: Starting ramp to {self.target_rpm} RPM")

    def to_frequency_hz(self, rpm: float) -> float:
        """Convert RPM to frequency (Hz) for pulse output."""
        return rpm / 60.0  # 1 pulse per revolution

    def inject_fault_shaft_slip(self) -> None:
        """Simulate belt/coupling failure — speed drops suddenly."""
        self.current_value = max(self.current_value - 600, 0)
        self.state = ChannelState.FAULT
        logger.warning(
            f"{self.name}: FAULT — Shaft slip, speed dropped to {self.current_value:.0f} RPM"
        )

    def tick(self, dt: float) -> None:
        super().tick(dt)
        elapsed = self.timestamp - self.cycle_start_time

        if self.cycle_phase == "ramp_up":
            if elapsed < self.ramp_up_time:
                self.current_value = (elapsed / self.ramp_up_time) * self.target_rpm
            else:
                self.current_value = self.target_rpm
                self.cycle_phase = "hold"
                self.cycle_start_time = self.timestamp
                self.state = ChannelState.HOLD

        elif self.cycle_phase == "hold":
            if elapsed < self.hold_time:
                self.current_value = self.apply_noise(self.target_rpm)
            else:
                self.cycle_phase = "ramp_down"
                self.cycle_start_time = self.timestamp
                self.state = ChannelState.RAMP_DOWN

        elif self.cycle_phase == "ramp_down":
            if elapsed < self.ramp_down_time:
                self.current_value = self.target_rpm * (1 - elapsed / self.ramp_down_time)
            else:
                self.current_value = 0
                self.cycle_phase = "idle"
                self.state = ChannelState.IDLE

        self.current_value = self.clamp(self.current_value)


# ============================================================================
# BENCH SIMULATOR
# ============================================================================

class BenchSimulator:
    """
    Orchestrates all sensor channels on the hydraulic test bench.
    Advances time in discrete steps; all channels tick together.
    """

    DEFAULT_PROFILE_PATH = Path(__file__).parent / "profiles" / "pc200-8-hpv95.toml"

    def __init__(
        self,
        sample_rate_hz: float = 10.0,
        profile: Optional[PumpProfile] = None,
        registry: Optional[FormulaRegistry] = None,
    ):
        self.sample_rate_hz = sample_rate_hz
        self.dt = 1.0 / sample_rate_hz
        self.elapsed_time = 0.0
        self.sample_count = 0

        # Formula engine: load the pump profile and the curated formula registry.
        # Derived channels (flow, torque, power) read constants + formula from these.
        self.profile = profile or PumpProfile.from_toml(self.DEFAULT_PROFILE_PATH)
        self.registry = registry or build_default_registry()

        self.pressure = PressureChannel(
            name="Pressure", unit="bar",
            min_value=0, max_value=500,
            noise_std_dev=1.5,
            sample_rate_hz=sample_rate_hz,
            target_pressure=380, ramp_up_time=30, hold_time=60
        )
        self.flow = FlowChannel(
            name="Flow", unit="L/min",
            min_value=0, max_value=605,
            noise_std_dev=3.0,
            sample_rate_hz=sample_rate_hz,
            profile=self.profile,     # no-load flow, PC cut-in, power const all from config
            registry=self.registry,  # formula resolved by name from the profile
        )
        self.temperature = TemperatureChannel(
            name="Temperature", unit="°C",
            min_value=0, max_value=120,
            noise_std_dev=0.8,
            sample_rate_hz=sample_rate_hz,
            ambient_temp=20, target_temp=45,
            warm_up_time_constant=300, hold_time=60
        )
        self.torque = TorqueChannel(
            name="Torque", unit="Nm",
            min_value=0, max_value=2500,
            noise_std_dev=10.0,
            sample_rate_hz=sample_rate_hz,
            profile=self.profile,     # sections, efficiency, rated rpm from config
            registry=self.registry,  # absorption_torque_from_flow_v1, derived from live flow
        )
        self.speed = SpeedChannel(
            name="Speed", unit="RPM",
            min_value=0, max_value=3000,
            noise_std_dev=15,
            sample_rate_hz=sample_rate_hz,
            target_rpm=self.profile.rated_rpm,   # 2000 rpm from profile (was hard-coded 1000)
            ramp_up_time=35, hold_time=60
        )
        # Power is a derived analysis channel (the "power curve"); surfaced on the
        # characteristic curve rather than as a sixth live gauge to keep the demo's
        # live-panel layout stable. Ticked alongside the displayed channels.
        self.power = PowerChannel(
            name="Power", unit="kW",
            min_value=0, max_value=100,
            noise_std_dev=0.3,
            sample_rate_hz=sample_rate_hz,
            profile=self.profile,
            registry=self.registry,
        )

        # Channels shown as live gauges/panels (unchanged five).
        self.channels = [
            self.pressure, self.flow, self.temperature, self.torque, self.speed
        ]
        # Derived channels carried for analysis/readings but not in the gauge layout.
        self.derived_channels = [self.power]
        logger.info(
            f"BenchSimulator initialized: {len(self.channels)} gauges "
            f"+ {len(self.derived_channels)} derived @ {sample_rate_hz} Hz"
        )

    def start_test(self) -> None:
        """Begin a full test cycle (all channels ramp up together)."""
        logger.info("=== TEST CYCLE START ===")
        for ch in self.channels + self.derived_channels:
            if isinstance(ch, TorqueChannel):
                # Torque derives from live flow (absorption_torque_from_flow_v1)
                ch.start_test_cycle(pressure_channel=self.pressure, flow_channel=self.flow)
            elif isinstance(ch, PowerChannel):
                # Power derives from live pressure × flow (power_from_flow_pressure_v1)
                ch.start_test_cycle(pressure_channel=self.pressure, flow_channel=self.flow)
            elif isinstance(ch, FlowChannel):
                # Flow derives from live pressure via the profile's flow formula
                ch.start_test_cycle(pressure_channel=self.pressure)
            else:
                ch.start_test_cycle()

    def tick(self) -> None:
        """Advance simulator by one time step."""
        for ch in self.channels + self.derived_channels:
            ch.tick(self.dt)
        self.elapsed_time += self.dt
        self.sample_count += 1

    def get_readings(self) -> dict:
        """Return current readings from all channels (gauges + derived) as engineering units."""
        return {
            ch.name: {
                "value": ch.current_value,
                "unit": ch.unit,
                "ma": ch.to_4_20ma(ch.current_value),
                "state": ch.state.value,
            }
            for ch in self.channels + self.derived_channels
        }

    def log_readings(self) -> None:
        """Log current sensor readings."""
        readings = self.get_readings()
        msg = f"[{self.elapsed_time:7.1f}s #{self.sample_count:5d}] "
        parts = []
        for name, data in readings.items():
            parts.append(
                f"{name}: {data['value']:7.1f} {data['unit']} ({data['ma']:5.2f} mA)"
                + (" *** FAULT ***" if data['state'] == 'fault' else "")
            )
        logger.info(msg + " | ".join(parts))


# ============================================================================
# DEMO SCRIPT — Basic run (no faults)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("BenchVision Hydraulic Test Bench — Sensor Simulator Demo")
    print("=" * 80 + "\n")

    sim = BenchSimulator(sample_rate_hz=10.0)
    sim.start_test()

    log_interval = 10       # Log every 10 ticks = 1 Hz output
    target_duration = 120   # seconds

    print(f"Running 120-second test cycle @ {sim.sample_rate_hz} Hz...")
    print(f"Logging every {log_interval} ticks (1 Hz output)\n")

    target_samples = int(target_duration * sim.sample_rate_hz)

    while sim.sample_count < target_samples:
        sim.tick()
        time.sleep(sim.dt)   # Pause 0.1s per tick — matches real 10 Hz DAQ rate
        if sim.sample_count % log_interval == 0:
            sim.log_readings()

    print("\n" + "=" * 80)
    print("Test cycle complete!")
    print("=" * 80 + "\n")
