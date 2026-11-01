"""Elementary illustrative film inventory model, NOT an annular solver.

We demonstrate first-order decay of invented film inventories using fixed,
user-supplied removal rates. This does not implement or validate the
Cioncolini--Thome correlations, wall-shear transfer, product rheology or
company-specific stripping dynamics. No Blow transition output is passed
into this model automatically.
"""
from dataclasses import dataclass
from math import isfinite, exp

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class FilmScenario:
    initial_volume_l: float = 2.0
    removal_rate_per_s: float = 0.02
    horizon_s: float = 120.0

    def validate(self) -> None:
        if any(not isfinite(v) for v in (self.initial_volume_l, self.removal_rate_per_s,
                                          self.horizon_s)):
            raise ValueError("Film parameters must be finite")
        if self.initial_volume_l <= 0 or self.removal_rate_per_s < 0 or self.horizon_s <= 0:
            raise ValueError("Positive inventory/time and nonnegative removal rate required")


@dataclass(frozen=True)
class FilmResult:
    time_s: NDArray[np.float64]
    remaining_volume_l: NDArray[np.float64]
    removed_volume_l: NDArray[np.float64]


def simulate_film_demo(scenario: FilmScenario | None = None, *, samples: int = 241) -> FilmResult:
    cfg = scenario or FilmScenario()
    cfg.validate()
    if samples < 2:
        raise ValueError("At least two time samples required")
    t = np.linspace(0, cfg.horizon_s, samples)
    remaining = cfg.initial_volume_l * np.exp(-cfg.removal_rate_per_s * t)
    removed = cfg.initial_volume_l - remaining
    if not np.allclose(remaining + removed, cfg.initial_volume_l, atol=1e-12):
        raise RuntimeError("Film inventory balance violated")
    return FilmResult(time_s=t, remaining_volume_l=remaining, removed_volume_l=removed)
