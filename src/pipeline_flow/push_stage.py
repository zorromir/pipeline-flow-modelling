"""Simulate a moving liquid column under two air-pressure assumptions.

This AI-assisted public example is based on the published one-dimensional
moving-column balance of Tijsseling et al. (2016). It uses hypothetical inputs.

States: Q = outlet liquid volume flow [m^3/s]; x = interface advance [m].
With a constant holdup fraction beta and area A:

  v = Q / ((1-beta)*A),       d(x)/dt = v,       L = L0-x.

The signed quadratic resistance form agrees with the published v^2 form
for forward motion. The example assumes a horizontal, uniform-diameter pipe.
"""

from dataclasses import dataclass
from math import isfinite, pi
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from .pressure import polytropic_pressure

PressureMode = Literal["constant", "isolated_expansion"]
StopReason = Literal["product_target", "minimum_length", "flow_stall", "time_limit"]


@dataclass(frozen=True)
class PushStageSettings:
    # Invented example parameters. These MUST NOT be replaced by company settings.
    column_length_m: float = 100.0
    pipe_diameter_m: float = 0.20
    density_kg_m3: float = 1000.0
    initial_air_pressure_pa_abs: float = 500_000.0
    outlet_pressure_pa_abs: float = 101_325.0
    air_initial_volume_m3: float = 2.0
    gas_polytropic_exponent: float = 1.2
    pressure_mode: PressureMode = "isolated_expansion"
    darcy_factor: float = 0.020
    exit_loss_k: float = 4.0
    holdup_beta: float = 0.20
    target_discharged_fraction: float | None = 0.50
    minimum_column_m: float = 5.0
    max_time_s: float = 120.0

    @property
    def area_m2(self) -> float:
        return pi * self.pipe_diameter_m**2 / 4.0

    @property
    def initial_liquid_volume_m3(self) -> float:
        return self.column_length_m * self.area_m2

    def validate(self) -> None:
        positive = (
            self.column_length_m, self.pipe_diameter_m, self.density_kg_m3,
            self.initial_air_pressure_pa_abs, self.outlet_pressure_pa_abs,
            self.air_initial_volume_m3, self.gas_polytropic_exponent,
            self.max_time_s,
        )
        if any(not isfinite(a) or a <= 0 for a in positive):
            raise ValueError("Positive finite geometry, pressures, time, gas volume and properties required")
        if any(not isfinite(a) or a < 0 for a in (self.darcy_factor, self.exit_loss_k)):
            raise ValueError("Resistance coefficients must be finite and nonnegative")
        if not isfinite(self.holdup_beta) or not 0 <= self.holdup_beta < 1:
            raise ValueError("holdup_beta must lie in [0, 1)")
        if not isfinite(self.minimum_column_m) or not 0 < self.minimum_column_m < self.column_length_m:
            raise ValueError("minimum_column_m must be inside the initial column")
        if self.pressure_mode not in ("constant", "isolated_expansion"):
            raise ValueError("pressure_mode must be constant or isolated_expansion")
        if self.initial_air_pressure_pa_abs <= self.outlet_pressure_pa_abs:
            raise ValueError("Initial air pressure must exceed outlet pressure to start from rest")
        if self.target_discharged_fraction is not None:
            target = self.target_discharged_fraction
            if not isfinite(target) or not 0 < target < 1:
                raise ValueError("Target must be a fraction strictly between 0 and 1")
            max_reachable = (1 - self.holdup_beta) * (
                1 - self.minimum_column_m / self.column_length_m
            )
            if target > max_reachable + 1e-12:
                raise ValueError("Product target cannot be reached before the minimum column length")


@dataclass(frozen=True)
class PushStageResult:
    time_s: NDArray[np.float64]
    outlet_flow_m3_s: NDArray[np.float64]
    interface_position_m: NDArray[np.float64]
    interface_velocity_m_s: NDArray[np.float64]
    remaining_column_m: NDArray[np.float64]
    air_pressure_pa_abs: NDArray[np.float64]
    air_volume_m3: NDArray[np.float64]
    discharged_volume_m3: NDArray[np.float64]
    holdup_volume_m3: NDArray[np.float64]
    full_column_volume_m3: NDArray[np.float64]
    volume_residual_m3: NDArray[np.float64]
    pressure_balance_residual_pa: NDArray[np.float64]
    stop_reason: StopReason
    stop_time_s: float

    @property
    def max_absolute_volume_residual_m3(self) -> float:
        return float(np.max(np.abs(self.volume_residual_m3)))

    @property
    def max_absolute_pressure_residual_pa(self) -> float:
        return float(np.max(np.abs(self.pressure_balance_residual_pa)))


def pressure_from_interface(settings: PushStageSettings, advance_m: float | NDArray[np.float64]):
    """Air pressure with absolute units. Added gas volume = pipe area * advance."""
    x = np.asarray(advance_m, dtype=float)
    if np.any(~np.isfinite(x)) or np.any(x < -1e-7) or np.any(x > settings.column_length_m + 1e-7):
        raise ValueError("Interface advance must be within the initial pipe length")
    if settings.pressure_mode == "constant":
        values = np.full_like(x, settings.initial_air_pressure_pa_abs)
    else:
        values = polytropic_pressure(
            settings.initial_air_pressure_pa_abs, settings.air_initial_volume_m3,
            settings.area_m2 * x, settings.gas_polytropic_exponent,
        )
    return float(values) if np.asarray(values).ndim == 0 else np.asarray(values)


def momentum_terms(settings: PushStageSettings, q_m3_s: float, x_m: float):
    """Terms in m^2/s^2 (pressure terms divided by liquid density).

    The model deliberately omits vertical elevation, pipe segmentation, tank
    replenishment and waterhammer. Separate pressure and model validation is
    needed before considering a real installation.
    """
    s = settings
    beta, area = s.holdup_beta, s.area_m2
    L = s.column_length_m - x_m
    if L <= 0:
        raise ValueError("Column length must be strictly positive")
    v = q_m3_s / ((1-beta)*area)
    p_air = pressure_from_interface(s, max(0.0, x_m))
    driving = (p_air - s.outlet_pressure_pa_abs) / s.density_kg_m3
    mass_loss = beta*(1-beta)*v*v
    friction = (s.darcy_factor/(2*s.pipe_diameter_m) *
                (1-beta+beta*beta/3)*L*v*abs(v))
    exit_loss = (s.exit_loss_k/2) * ((1-beta)*v)*abs((1-beta)*v)
    inertial_coefficient = (1-beta/2)*L
    accel = (mass_loss + driving - friction - exit_loss)/inertial_coefficient
    return accel, mass_loss, driving, friction, exit_loss, inertial_coefficient


def simulate_push_stage(settings: PushStageSettings, *, samples: int = 350,
                        rtol: float = 2e-9, max_step_s: float = .08) -> PushStageResult:
    """Integrate Q and x until the first event or a finite time limit.

    The stop target, when set, is *discharged* product / initial product.
    It is not the fraction of pipe distance traversed. Events use root finding.
    """
    settings.validate()
    if not isinstance(samples, int) or samples < 3:
        raise ValueError("samples must be an integer >= 3")
    if not isfinite(rtol) or rtol <= 0 or not isfinite(max_step_s) or max_step_s <= 0:
        raise ValueError("Positive finite solver tolerances and steps are required")

    beta, area = settings.holdup_beta, settings.area_m2
    x_stop = settings.column_length_m - settings.minimum_column_m
    target_x = None
    if settings.target_discharged_fraction is not None:
        target_x = settings.target_discharged_fraction * settings.column_length_m / (1-beta)

    def rhs(_t, state):
        q, x = map(float, state)
        # Stop events prevent physically invalid column lengths. During an
        # integrator's trial step, the smooth RHS must still be defined.
        safe_x = min(max(x, 0.0), settings.column_length_m - 1e-8)
        accel, *_ = momentum_terms(settings, q, safe_x)
        return [(1-beta)*area*accel, q/((1-beta)*area)]

    def length_event(_t, state):
        return state[1] - x_stop
    length_event.direction, length_event.terminal = 1, True

    def target_event(_t, state):
        return state[1] - target_x  # only registered when target is not None
    target_event.direction, target_event.terminal = 1, True

    def stall_event(_t, state):
        return state[0]
    stall_event.direction, stall_event.terminal = -1, True

    events = [length_event]
    labels: list[StopReason] = ["minimum_length"]
    if target_x is not None:
        events.append(target_event)
        labels.append("product_target")
    events.append(stall_event)
    labels.append("flow_stall")

    sol = solve_ivp(rhs, (0.0, settings.max_time_s), [0.0, 0.0],
                    events=events, method="DOP853", dense_output=True,
                    max_step=max_step_s, rtol=rtol, atol=rtol*1e-2)
    if not sol.success:
        raise RuntimeError(f"Push integration failed: {sol.message}")
    candidates = [(float(times[0]), labels[i]) for i, times in enumerate(sol.t_events) if len(times)]
    if candidates:
        stop_time, reason = min(candidates, key=lambda x: x[0])
    else:
        stop_time, reason = float(sol.t[-1]), "time_limit"
    times = np.linspace(0.0, stop_time, samples)
    q, x = sol.sol(times)
    x = np.asarray(x)
    q = np.asarray(q)
    L = settings.column_length_m - x
    if np.any(~np.isfinite(q)) or np.any(~np.isfinite(x)) or np.min(L) < settings.minimum_column_m - 1e-5:
        raise RuntimeError("Nonphysical state or solver overrun")
    if np.min(q) < -1e-7 or np.min(x) < -1e-7:
        raise RuntimeError("Liquid flow or interface reversed outside the model's scope")
    gas_v = settings.air_initial_volume_m3 + area*x
    gas_p = np.asarray(pressure_from_interface(settings, np.maximum(x, 0.0)))
    swept = area*x
    discharged = (1-beta)*swept
    holdup = beta*swept
    full = area*L
    volume_residual = settings.initial_liquid_volume_m3 - (discharged + holdup + full)

    pressure_residual = np.empty_like(q)
    for i, (qi, xi) in enumerate(zip(q, x)):
        a, mass, drive, friction, exit_loss, inertia = momentum_terms(
            settings, float(qi), float(min(max(xi, 0), x_stop)))
        pressure_residual[i] = settings.density_kg_m3 * (
            inertia*a - mass - drive + friction + exit_loss
        )

    return PushStageResult(
        time_s=times, outlet_flow_m3_s=q,
        interface_position_m=x, interface_velocity_m_s=q/((1-beta)*area),
        remaining_column_m=L, air_pressure_pa_abs=gas_p, air_volume_m3=gas_v,
        discharged_volume_m3=discharged, holdup_volume_m3=holdup,
        full_column_volume_m3=full, volume_residual_m3=volume_residual,
        pressure_balance_residual_pa=pressure_residual,
        stop_reason=reason, stop_time_s=stop_time,
    )
