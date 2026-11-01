"""A deliberately narrow published constant-pressure rigid-column example.

Based on Tijsseling et al. (2016), Eq. (9), with flat geometry,
constant driving pressure, constant Darcy factor, and stationary holdup.
It is not the original industrial Push solver and is not a validated predictor.
"""

from dataclasses import dataclass
from math import isfinite, pi

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class PushParameters:
    initial_column_length_m: float = 100.0
    diameter_m: float = 0.20
    liquid_density_kg_m3: float = 1000.0
    pressure_difference_pa: float = 40_000.0
    darcy_friction_factor: float = 0.020
    exit_loss_coefficient: float = 4.0
    holdup_fraction: float = 0.20
    min_column_length_m: float = 5.0

    def validate(self) -> None:
        positive = (self.initial_column_length_m, self.diameter_m,
                    self.liquid_density_kg_m3, self.pressure_difference_pa)
        nonnegative = (self.darcy_friction_factor, self.exit_loss_coefficient)
        if any(not isfinite(x) or x <= 0 for x in positive):
            raise ValueError("Geometry, density and driving pressure must be positive")
        if any(not isfinite(x) or x < 0 for x in nonnegative):
            raise ValueError("Loss coefficients must be nonnegative")
        if not isfinite(self.holdup_fraction) or not 0 <= self.holdup_fraction < 1:
            raise ValueError("Holdup fraction must lie in [0, 1)")
        if not (isfinite(self.min_column_length_m) and
                0 < self.min_column_length_m < self.initial_column_length_m):
            raise ValueError("Stop length must be inside (0, initial length)")


@dataclass(frozen=True)
class PushResult:
    time_s: np.ndarray
    interface_velocity_m_s: np.ndarray
    outlet_velocity_m_s: np.ndarray
    remaining_column_m: np.ndarray
    discharged_flow_m3_s: np.ndarray
    swept_volume_m3: np.ndarray
    holdup_volume_m3: np.ndarray
    discharged_volume_m3: np.ndarray


def simulate_push(p: PushParameters = PushParameters(), *, samples: int = 300) -> PushResult:
    """Integrate velocity and remaining length, stopping before the L=0 singularity.

    The calculation uses imaginary inputs; do not extrapolate results to facilities.
    """
    p.validate()
    if samples < 3:
        raise ValueError("At least three output samples are required")
    b, d, rho = p.holdup_fraction, p.diameter_m, p.liquid_density_kg_m3
    area = pi*(d/2)**2

    def rhs(_time, state):
        v, length = state
        if length <= 0:
            return [0.0, 0.0]  # event below prevents this physical state
        friction = p.darcy_friction_factor/(2*d)*(1-b+b*b/3)*length*v*abs(v)
        exit_loss = p.exit_loss_coefficient/2*(1-b)**2*v*abs(v)
        acceleration = (b*(1-b)*v*v + p.pressure_difference_pa/rho
                        - friction - exit_loss) / ((1-b/2)*length)
        return [acceleration, -v]

    def stop(_time, state):
        return state[1] - p.min_column_length_m
    stop.terminal = True
    stop.direction = -1

    sol = solve_ivp(rhs, (0.0, 120.0), [0.0, p.initial_column_length_m],
                    events=stop, dense_output=True, max_step=.04,
                    rtol=1e-9, atol=1e-11)
    if not sol.success or len(sol.t_events[0]) != 1:
        raise RuntimeError("The solver did not reach the safe stopping event")
    t = np.linspace(0, float(sol.t_events[0][0]), int(samples))
    v, length = sol.sol(t)
    if (np.min(length) < p.min_column_length_m-1e-5 or
            np.any(~np.isfinite(v))):
        raise RuntimeError("Unphysical or nonfinite solver result")
    swept = (p.initial_column_length_m - length) * area
    return PushResult(
        time_s=t,
        interface_velocity_m_s=v,
        outlet_velocity_m_s=(1-b)*v,
        remaining_column_m=length,
        discharged_flow_m3_s=area*(1-b)*v,
        swept_volume_m3=swept,
        holdup_volume_m3=b*swept,
        discharged_volume_m3=(1-b)*swept,
    )
