"""Scrambled-Sobol uncertainty study for the *illustrative* public Push solver.

The parameter intervals below are invented for educational numerical experiments.
They are NOT calibrated distributions, measurement uncertainties, or confidence
intervals for any real pipeline. All quantities and their units are explicit.

The run treats these inputs as independent Uniform(a, b) assumptions. It reports
sample quantiles; the sensitivity diagnostics are Spearman rank correlations,
NOT Sobol sensitivity indices. A scrambled Sobol design is a sampling METHOD,
not a statistical validation of these invented inputs.
"""

from dataclasses import dataclass, replace
from math import isfinite
from typing import Mapping

import numpy as np
from numpy.typing import NDArray
from scipy.stats import qmc, spearmanr

from .push_stage import PushStageSettings, simulate_push_stage


PARAMETERS = (
    "initial_air_pressure_pa_abs",
    "darcy_factor",
    "exit_loss_k",
    "holdup_beta",
)

# Example-only bounds, not reported specifications or measured distributions.
EXAMPLE_BOUNDS = {
    "initial_air_pressure_pa_abs": (370_000.0, 620_000.0),
    "darcy_factor": (0.015, 0.035),
    "exit_loss_k": (2.0, 6.0),
    "holdup_beta": (0.10, 0.30),
}

LABELS = {
    "initial_air_pressure_pa_abs": "Initial air pressure",
    "darcy_factor": "Darcy friction factor",
    "exit_loss_k": "Outlet loss K",
    "holdup_beta": "Holdup fraction",
}


@dataclass(frozen=True)
class QMCSettings:
    """Number of samples must be 2**power for balance in Sobol designs."""

    power: int = 8
    seed: int = 20261101
    pressure_mode: str = "isolated_expansion"
    target_discharged_fraction: float = 0.50
    solver_max_step_s: float = 0.18
    solver_rtol: float = 2e-7
    trajectory_samples: int = 75
    progress_points: int = 51

    def validate(self):
        if type(self.power) is not int or not 1 <= self.power <= 13:
            raise ValueError("power must be an integer in [1, 13]")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("seed must be a nonnegative integer")
        if self.pressure_mode not in ("constant", "isolated_expansion"):
            raise ValueError("Unknown pressure mode")
        if not isfinite(self.target_discharged_fraction) or not 0 < self.target_discharged_fraction < 1:
            raise ValueError("Target must be strictly between 0 and 1")
        if not isfinite(self.solver_max_step_s) or self.solver_max_step_s <= 0:
            raise ValueError("max_step must be positive and finite")
        if not isfinite(self.solver_rtol) or self.solver_rtol <= 0:
            raise ValueError("rtol must be positive and finite")
        if type(self.trajectory_samples) is not int or self.trajectory_samples < 3:
            raise ValueError("trajectory_samples must be at least 3")
        if type(self.progress_points) is not int or self.progress_points < 3:
            raise ValueError("progress_points must be at least 3")


@dataclass(frozen=True)
class QMCResult:
    names: tuple[str, ...]
    parameter_samples: NDArray[np.float64]   # shape (N, d), native parameter units
    completion_times_s: NDArray[np.float64]  # (N,)
    peak_flows_lps: NDArray[np.float64]       # (N,)
    progress_fraction: NDArray[np.float64]   # (M,), fraction of discharge TARGET
    aligned_flows_lps: NDArray[np.float64]   # (N, M), at fixed fraction of target
    stop_reasons: tuple[str, ...]
    seed: int
    bounds: dict[str, tuple[float, float]]

    def quantiles(self, values: NDArray[np.float64]) -> NDArray[np.float64]:
        """Sample 10th, 50th and 90th percentiles (not calibrated coverage)."""
        return np.quantile(values, [0.1, 0.5, 0.9], axis=0)

    @property
    def rank_correlations(self) -> NDArray[np.float64]:
        """Descriptive marginal correlations with completion time, not Sobol indices."""
        return np.asarray([spearmanr(self.parameter_samples[:, j], self.completion_times_s).statistic
                           for j in range(self.parameter_samples.shape[1])])

    @property
    def success_fraction(self) -> float:
        return float(np.mean([x == "product_target" for x in self.stop_reasons]))


def validate_bounds(bounds: Mapping[str, tuple[float, float]], base: PushStageSettings, target: float):
    if set(bounds) != set(PARAMETERS):
        raise ValueError("Use exactly the four documented parameter keys")
    for name, value in bounds.items():
        if len(value) != 2 or not all(isfinite(x) for x in value):
            raise ValueError(f"Nonfinite or missing interval for {name}")
        low, high = value
        if low >= high:
            raise ValueError(f"Bounds must satisfy low < high for {name}")
    if bounds["initial_air_pressure_pa_abs"][0] <= base.outlet_pressure_pa_abs:
        raise ValueError("Pressure must exceed outlet pressure")
    if bounds["darcy_factor"][0] < 0 or bounds["exit_loss_k"][0] < 0:
        raise ValueError("Resistance cannot be negative")
    if not 0 <= bounds["holdup_beta"][0] < bounds["holdup_beta"][1] < 1:
        raise ValueError("Holdup must lie in [0,1)")
    max_beta = bounds["holdup_beta"][1]
    max_target = (1-max_beta)*(1-base.minimum_column_m/base.column_length_m)
    if target > max_target:
        raise ValueError("Requested discharge is unreachable for some parameter samples")


def run_qmc(
    settings: QMCSettings = QMCSettings(),
    *,
    bounds: Mapping[str, tuple[float, float]] | None = None,
    baseline: PushStageSettings | None = None,
) -> QMCResult:
    """Run independent uniform-input Sobol scenarios through the existing Push solver.

    Every trajectory must reach its target; a stall or time limit is reported as an
    error rather than silently excluding failures from an uncertainty interval.
    """
    settings.validate()
    baseline = PushStageSettings() if baseline is None else baseline
    baseline = replace(baseline, pressure_mode=settings.pressure_mode,
                       target_discharged_fraction=settings.target_discharged_fraction)
    baseline.validate()
    chosen = dict(EXAMPLE_BOUNDS if bounds is None else bounds)
    validate_bounds(chosen, baseline, settings.target_discharged_fraction)

    sampler = qmc.Sobol(d=len(PARAMETERS), scramble=True, seed=settings.seed)
    unit = sampler.random_base2(m=settings.power)
    lows = np.asarray([chosen[p][0] for p in PARAMETERS], dtype=float)
    highs = np.asarray([chosen[p][1] for p in PARAMETERS], dtype=float)
    samples = lows + unit*(highs-lows)
    n = len(samples)
    progress = np.linspace(0, 1, settings.progress_points)
    aligned = np.empty((n, settings.progress_points), dtype=float)
    times = np.empty(n, dtype=float)
    peaks = np.empty(n, dtype=float)
    reasons: list[str] = []

    for i, row in enumerate(samples):
        p = replace(baseline, **dict(zip(PARAMETERS, map(float, row))))
        result = simulate_push_stage(
            p, samples=settings.trajectory_samples,
            rtol=settings.solver_rtol, max_step_s=settings.solver_max_step_s,
        )
        reasons.append(result.stop_reason)
        if result.stop_reason != "product_target":
            raise RuntimeError(f"Scenario {i} stopped at {result.stop_reason}; "
                               "do not compute conditional intervals from successful runs only")
        times[i] = result.stop_time_s
        peaks[i] = float(np.max(result.outlet_flow_m3_s))*1000
        progress_run = result.discharged_volume_m3 / (
            settings.target_discharged_fraction * p.initial_liquid_volume_m3)
        # Discharge progress is non-decreasing. A common progress grid prevents
        # misleading time-domain quantiles when scenarios finish at different times.
        if np.any(np.diff(progress_run) < -1e-9) or progress_run[-1] < 1 - 1e-5:
            raise RuntimeError(f"Non-monotone or incomplete discharge in scenario {i}")
        aligned[i] = np.interp(progress, progress_run, result.outlet_flow_m3_s*1000)
    return QMCResult(
        names=PARAMETERS, parameter_samples=samples,
        completion_times_s=times, peak_flows_lps=peaks,
        progress_fraction=progress, aligned_flows_lps=aligned,
        stop_reasons=tuple(reasons), seed=settings.seed, bounds=chosen,
    )


def convergence_medians(settings: QMCSettings, *, bounds=None, baseline=None):
    """Successive prefixes of one scrambled Sobol design; heuristic stability check.

    Prefix curves reuse the same sample, so their differences are not independent
    standard errors. Repeat with independent scrambles for robust error assessment.
    """
    result = run_qmc(settings, bounds=bounds, baseline=baseline)
    counts = np.array([2**k for k in range(2, settings.power+1)], dtype=int)
    medians = np.array([np.median(result.completion_times_s[:n]) for n in counts])
    return counts, medians, result
