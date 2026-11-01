"""Invented, compartment-based Rinse mass-balance demonstration.

This is NOT a validated two-phase flow or industrial cleaning solver.
Three successive, well-mixed *effective* compartments exchange water and mobile
product; wall product detaches at an invented first-order rate. There is no
inference of physical film shapes, pressure, microbiological cleaning or flow
regime. Model relationships are general conservation bookkeeping only.
"""
from dataclasses import dataclass
from math import isfinite

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class RinseSettings:
    mixing_volumes_l: tuple[float, ...] = (12.0, 12.0, 12.0)
    initial_wall_product_l: tuple[float, ...] = (0.8, 0.6, 0.4)
    initial_mobile_product_l: tuple[float, ...] = (0.05, 0.03, 0.02)
    water_flow_l_s: float = 0.8
    water_goal_l: float = 48.0
    detachment_rate_per_s: float = 0.025
    gas_mass_flow_kg_s: float = 0.06  # carried as metadata, not a modeled forcing
    max_duration_s: float = 150.0

    def validate(self) -> None:
        n = len(self.mixing_volumes_l)
        if n < 1 or len(self.initial_wall_product_l) != n or len(self.initial_mobile_product_l) != n:
            raise ValueError('All compartment vectors must have equal nonzero length')
        all_values = (*self.mixing_volumes_l, *self.initial_wall_product_l,
                      *self.initial_mobile_product_l, self.water_flow_l_s,
                      self.water_goal_l, self.detachment_rate_per_s,
                      self.gas_mass_flow_kg_s, self.max_duration_s)
        if any(not isfinite(v) for v in all_values):
            raise ValueError('All inputs must be finite')
        if any(v <= 0 for v in self.mixing_volumes_l):
            raise ValueError('Mixing reference volumes must be positive')
        if any(v < 0 for v in (*self.initial_wall_product_l, *self.initial_mobile_product_l)):
            raise ValueError('Inventories must be nonnegative')
        if (self.water_flow_l_s <= 0 or self.water_goal_l <= 0
                or self.max_duration_s <= 0 or self.detachment_rate_per_s < 0
                or self.gas_mass_flow_kg_s < 0):
            raise ValueError('Flow, target and duration positive; rates nonnegative')
        if self.water_goal_l / self.water_flow_l_s > self.max_duration_s:
            raise ValueError('Water target cannot be achieved before the safety time limit')


@dataclass(frozen=True)
class RinseToDryTransfer:
    """Only measured-in-model inventories and metadata needed by a Dry surrogate."""
    time_s: float
    water_in_pipe_l: float
    wall_product_by_segment_l: tuple[float, ...]
    mobile_product_by_segment_l: tuple[float, ...]
    gas_mass_flow_kg_s: float

    def validate(self) -> None:
        vals = (self.time_s, self.water_in_pipe_l, self.gas_mass_flow_kg_s,
                *self.wall_product_by_segment_l, *self.mobile_product_by_segment_l)
        if len(self.wall_product_by_segment_l) == 0 or len(self.wall_product_by_segment_l) != len(self.mobile_product_by_segment_l):
            raise ValueError('Product vectors must match')
        if any(not isfinite(v) or v < 0 for v in vals):
            raise ValueError('Transfer inventories and times must be finite and nonnegative')


@dataclass(frozen=True)
class RinseResult:
    time_s: NDArray[np.float64]
    water_by_segment_l: NDArray[np.float64]
    mobile_product_by_segment_l: NDArray[np.float64]
    wall_product_by_segment_l: NDArray[np.float64]
    injected_water_l: NDArray[np.float64]
    discharged_water_l: NDArray[np.float64]
    discharged_product_l: NDArray[np.float64]
    water_balance_residual_l: NDArray[np.float64]
    product_balance_residual_l: NDArray[np.float64]
    transfer: RinseToDryTransfer


def simulate_rinse_demo(settings: RinseSettings | None = None, *, samples: int = 451) -> RinseResult:
    s = settings or RinseSettings()
    s.validate()
    if not isinstance(samples, int) or samples < 2:
        raise ValueError('samples must be at least two')
    n = len(s.mixing_volumes_l)
    rates = s.water_flow_l_s / np.asarray(s.mixing_volumes_l, dtype=float)
    wall0 = np.array(s.initial_wall_product_l, dtype=float)
    mobile0 = np.array(s.initial_mobile_product_l, dtype=float)
    start = np.concatenate([np.zeros(n), mobile0, wall0, [0., 0., 0.]])
    stop_time = s.water_goal_l / s.water_flow_l_s

    def rhs(_t: float, y: NDArray[np.float64]) -> NDArray[np.float64]:
        water = y[:n]
        mobile = y[n:2*n]
        wall = y[2*n:3*n]
        out_w = rates * water
        out_m = rates * mobile
        detach = s.detachment_rate_per_s * wall
        dwater = np.r_[s.water_flow_l_s, out_w[:-1]] - out_w
        dmobile = np.r_[0.0, out_m[:-1]] - out_m + detach
        dwall = -detach
        return np.concatenate([dwater, dmobile, dwall,
                               [s.water_flow_l_s, out_w[-1], out_m[-1]]])

    t = np.linspace(0., stop_time, samples)
    sol = solve_ivp(rhs, (0., stop_time), start, t_eval=t,
                    method='DOP853', rtol=1e-10, atol=1e-12)
    if not sol.success:
        raise RuntimeError(f'Numerical integration failed: {sol.message}')
    y = sol.y
    if np.min(y) < -1e-8:
        raise RuntimeError('Negative conserved inventory')
    # Avoid floating roundoff underflow leaking into public charts.
    wat = np.maximum(y[:n].T, 0.)
    mob = np.maximum(y[n:2*n].T, 0.)
    wall = np.maximum(y[2*n:3*n].T, 0.)
    inj, discharge_water, discharge_product = y[3*n:3*n+3]
    wb = inj - discharge_water - wat.sum(axis=1)
    pb = (wall0.sum() + mobile0.sum() - discharge_product
          - wall.sum(axis=1) - mob.sum(axis=1))
    if max(np.max(np.abs(wb)), np.max(np.abs(pb))) > 1e-7:
        raise RuntimeError('Conservation tolerance exceeded')
    transfer = RinseToDryTransfer(
        time_s=stop_time, water_in_pipe_l=float(wat[-1].sum()),
        wall_product_by_segment_l=tuple(float(v) for v in wall[-1]),
        mobile_product_by_segment_l=tuple(float(v) for v in mob[-1]),
        gas_mass_flow_kg_s=s.gas_mass_flow_kg_s)
    transfer.validate()
    return RinseResult(t, wat, mob, wall, inj, discharge_water,
                       discharge_product, wb, pb, transfer)
