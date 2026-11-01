"""Show a simple decrease in residual water after Rinse.

The model starts from the water inventory passed over from Rinse and uses
an assumed first-order removal rate. The rate is not derived from airflow,
humidity or an industrial drying experiment.
"""
from dataclasses import dataclass
from math import isfinite, log

import numpy as np
from numpy.typing import NDArray
from .rinse_demo import RinseToDryTransfer


@dataclass(frozen=True)
class DrySettings:
    water_removal_rate_per_s: float = 0.026
    target_removed_fraction: float = 0.90
    max_duration_s: float = 125.0

    def validate(self) -> None:
        vals = (self.water_removal_rate_per_s, self.target_removed_fraction,
                self.max_duration_s)
        if any(not isfinite(v) for v in vals):
            raise ValueError('Dry settings must be finite')
        if (self.water_removal_rate_per_s < 0 or self.max_duration_s <= 0
                or not 0 <= self.target_removed_fraction < 1):
            raise ValueError('Require nonnegative rate, positive duration, 0<=target<1')


@dataclass(frozen=True)
class DryResult:
    local_time_s: NDArray[np.float64]
    total_time_s: NDArray[np.float64]
    water_remaining_l: NDArray[np.float64]
    water_removed_l: NDArray[np.float64]
    remaining_product_l: float
    gas_mass_flow_kg_s: float
    water_balance_residual_l: NDArray[np.float64]
    stop_reason: str


def simulate_dry_demo(transfer: RinseToDryTransfer,
                      settings: DrySettings | None = None, *, samples: int = 451) -> DryResult:
    transfer.validate()
    s = settings or DrySettings()
    s.validate()
    if not isinstance(samples, int) or samples < 2:
        raise ValueError('samples must be at least two')
    w0 = transfer.water_in_pipe_l
    if w0 == 0 or s.target_removed_fraction == 0:
        duration, stop_reason = 0., 'target_reached'
    elif s.water_removal_rate_per_s == 0:
        duration, stop_reason = s.max_duration_s, 'time_limit'
    else:
        desired_time = -log(1-s.target_removed_fraction) / s.water_removal_rate_per_s
        if desired_time <= s.max_duration_s:
            duration, stop_reason = desired_time, 'target_reached'
        else:
            duration, stop_reason = s.max_duration_s, 'time_limit'
    t = np.linspace(0., duration, samples)
    remaining = w0 * np.exp(-s.water_removal_rate_per_s*t)
    removed = w0 - remaining
    residue = w0-remaining-removed
    if np.max(np.abs(residue)) > 1e-10:
        raise RuntimeError('Dry water conservation failed')
    return DryResult(
        local_time_s=t, total_time_s=t+transfer.time_s,
        water_remaining_l=remaining, water_removed_l=removed,
        remaining_product_l=(sum(transfer.wall_product_by_segment_l)
                             + sum(transfer.mobile_product_by_segment_l)),
        gas_mass_flow_kg_s=transfer.gas_mass_flow_kg_s,
        water_balance_residual_l=residue, stop_reason=stop_reason)
