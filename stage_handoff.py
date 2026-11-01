"""Public, independently written control-volume transition for air-driven emptying.

This is a teaching-level, constant-pressure, uniform-pipe demonstration of
published control-volume relationships. It does not reproduce any private
implementation, its calibration, or an industrial compressor/film model.

The column leaves liquid behind when 0 < alpha < 1. If U is the outlet
liquid speed and A the area, dL/dt=-U/alpha, Qout=A*U,
Qtail=A*U*(1/alpha - 1). The signs are fixed for nonnegative U.

Scientific context: published pipeline-emptying control-volume models.
No internal report, proprietary simulation or calibration is included.
"""
from dataclasses import dataclass
from math import isfinite, pi

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class BlowTransitionSettings:
    length_m: float = 24.0
    diameter_m: float = 0.15
    density_kg_m3: float = 1000.0
    upstream_pressure_pa_abs: float = 175_000.0
    outlet_pressure_pa_abs: float = 101_325.0
    darcy_factor: float = 0.026
    local_loss_k: float = 2.5
    alpha: float = 0.84
    residual_momentum_beta: float = 0.35
    stop_column_length_m: float = 0.30
    max_time_s: float = 60.0

    @property
    def area_m2(self) -> float:
        return pi * self.diameter_m**2 / 4

    def validate(self) -> None:
        finite = (
            self.length_m, self.diameter_m, self.density_kg_m3,
            self.upstream_pressure_pa_abs, self.outlet_pressure_pa_abs,
            self.darcy_factor, self.local_loss_k, self.alpha,
            self.residual_momentum_beta, self.stop_column_length_m,
            self.max_time_s,
        )
        if any(not isfinite(v) for v in finite):
            raise ValueError("All Blow transition parameters must be finite")
        if any(v <= 0 for v in (self.length_m, self.diameter_m, self.density_kg_m3,
                                self.upstream_pressure_pa_abs, self.outlet_pressure_pa_abs,
                                self.max_time_s)):
            raise ValueError("Lengths, density, absolute pressures and time must be positive")
        if self.upstream_pressure_pa_abs <= self.outlet_pressure_pa_abs:
            raise ValueError("Example requires positive driving pressure")
        if self.darcy_factor < 0 or self.local_loss_k < 0:
            raise ValueError("Loss factors cannot be negative")
        if not (0 < self.alpha <= 1):
            raise ValueError("0 < alpha <= 1 required for nonnegative tail leakage")
        if not (0 <= self.residual_momentum_beta <= 1):
            raise ValueError("Residual momentum beta must lie in [0,1]")
        if not (0 < self.stop_column_length_m < self.length_m):
            raise ValueError("Stop length must lie strictly inside the column")


@dataclass(frozen=True)
class BlowTransitionResult:
    time_s: NDArray[np.float64]
    outlet_velocity_m_s: NDArray[np.float64]
    liquid_column_length_m: NDArray[np.float64]
    outlet_flow_m3_s: NDArray[np.float64]
    discharged_volume_m3: NDArray[np.float64]
    tail_holdup_volume_m3: NDArray[np.float64]
    volume_residual_m3: NDArray[np.float64]
    stop_reason: str

    @property
    def final_time_s(self) -> float:
        return float(self.time_s[-1])


def simulate_blow_transition(
    settings: BlowTransitionSettings | None = None,
    *, samples: int = 450, max_step_s: float = 0.05,
    rtol: float = 1e-9,
) -> BlowTransitionResult:
    """Integrate [U, L, Vout, Vtail] until the remaining column is small.

    This simplified model excludes gravity, branching, pressure feedback,
    any fluid-film hydrodynamics and company-specific physical parameters.
    """
    cfg = settings or BlowTransitionSettings()
    cfg.validate()
    if samples < 3 or max_step_s <= 0 or not np.isfinite(max_step_s):
        raise ValueError("Need >=3 samples and a positive finite integration step")
    if not 0 < rtol <= 1e-3:
        raise ValueError("Relative tolerance outside supported range")

    A = cfg.area_m2
    delta_p = cfg.upstream_pressure_pa_abs - cfg.outlet_pressure_pa_abs
    C_R = cfg.residual_momentum_beta * (1.0 / cfg.alpha - 1.0) - 1.0

    def rhs(_t: float, y: NDArray[np.float64]) -> list[float]:
        U, L = y[:2]
        # ODE is intentionally evaluated only while L is safely positive.
        Lsafe = max(L, cfg.stop_column_length_m * 0.5)
        head = delta_p / cfg.density_kg_m3
        drag = 0.5 * (cfg.darcy_factor * Lsafe / cfg.diameter_m + cfg.local_loss_k) * U * abs(U)
        dUdt = (head - drag + C_R * U * abs(U)) / Lsafe
        dLdt = -U / cfg.alpha
        dVoutdt = A * U
        dVtaildt = A * U * (1 / cfg.alpha - 1)
        return [dUdt, dLdt, dVoutdt, dVtaildt]

    def small_column(_t: float, y: NDArray[np.float64]) -> float:
        return float(y[1] - cfg.stop_column_length_m)
    small_column.terminal = True
    small_column.direction = -1

    solution = solve_ivp(
        rhs, (0, cfg.max_time_s), [0, cfg.length_m, 0, 0],
        method="DOP853", events=[small_column], dense_output=True,
        max_step=max_step_s, rtol=rtol, atol=rtol * 1e-2,
    )
    if not solution.success:
        raise RuntimeError("Blow transition solver failed: " + solution.message)
    event_hit = len(solution.t_events[0]) > 0
    end = float(solution.t_events[0][0]) if event_hit else float(solution.t[-1])
    t = np.linspace(0, end, samples)
    U, L, Vout, Vtail = solution.sol(t)
    Vfull = A * L
    residual = A * cfg.length_m - (Vfull + Vout + Vtail)
    if (np.any(~np.isfinite(solution.y)) or np.min(L) < cfg.stop_column_length_m - 1e-6
            or np.min(U) < -1e-7 or np.min(Vtail) < -1e-8
            or np.max(np.abs(residual)) > 1e-5 * A * cfg.length_m):
        raise RuntimeError("Blow transition produced an invalid physical or volume state")
    return BlowTransitionResult(
        time_s=np.asarray(t), outlet_velocity_m_s=np.asarray(U),
        liquid_column_length_m=np.asarray(L), outlet_flow_m3_s=np.asarray(A * U),
        discharged_volume_m3=np.asarray(Vout), tail_holdup_volume_m3=np.asarray(Vtail),
        volume_residual_m3=np.asarray(residual),
        stop_reason="minimum_column_length" if event_hit else "time_limit",
    )
