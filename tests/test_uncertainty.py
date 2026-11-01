"""Phase 5: synthetic-input QMC design and numerical verification."""
from dataclasses import replace

import numpy as np
import pytest

from pipeline_flow.uncertainty import (
    EXAMPLE_BOUNDS, PARAMETERS, QMCSettings,
    convergence_medians, run_qmc,
)
from pipeline_flow.push_stage import PushStageSettings


def test_qmc_reproducible_and_within_bounds():
    setup = QMCSettings(power=3, seed=19)
    a, b = run_qmc(setup), run_qmc(setup)
    np.testing.assert_array_equal(a.parameter_samples, b.parameter_samples)
    np.testing.assert_allclose(a.completion_times_s, b.completion_times_s)
    assert a.parameter_samples.shape == (8,4)
    assert a.success_fraction == 1.
    for j, name in enumerate(PARAMETERS):
        lo,hi = EXAMPLE_BOUNDS[name]
        assert np.min(a.parameter_samples[:, j]) >= lo
        assert np.max(a.parameter_samples[:, j]) <= hi


def test_independent_scrambles_change_design():
    a = run_qmc(QMCSettings(power=2, seed=11))
    b = run_qmc(QMCSettings(power=2, seed=12))
    assert not np.array_equal(a.parameter_samples,b.parameter_samples)


def test_quantile_order_and_finite_outputs():
    result = run_qmc(QMCSettings(power=3))
    q = result.quantiles(result.completion_times_s)
    assert np.all(np.diff(q) >= 0)
    assert np.all(np.isfinite(result.aligned_flows_lps))
    assert np.all(np.diff(result.progress_fraction) >= 0)
    assert np.all(result.aligned_flows_lps[:, 0] == 0)
    assert np.all(result.completion_times_s > 0)
    assert np.all(result.peak_flows_lps > 0)


def test_progress_alignment_and_rank_correlations():
    result=run_qmc(QMCSettings(power=4))
    low, med, high = result.quantiles(result.aligned_flows_lps)
    assert np.all(low <= med)
    assert np.all(med <= high)
    assert len(result.rank_correlations) == 4
    assert np.max(np.abs(result.rank_correlations)) <= 1 + 1e-12


def test_convergence_prefixes():
    counts, medians, result = convergence_medians(QMCSettings(power=4))
    np.testing.assert_array_equal(counts, [4,8,16])
    np.testing.assert_allclose(medians, [np.median(result.completion_times_s[:n]) for n in counts])


@pytest.mark.parametrize("arg",[
    QMCSettings(power=0), QMCSettings(power=3.1), QMCSettings(seed=-1),
    QMCSettings(pressure_mode="measured"),
    QMCSettings(trajectory_samples=2), QMCSettings(progress_points=2),
    QMCSettings(solver_max_step_s=-1),QMCSettings(solver_rtol=0),
    QMCSettings(target_discharged_fraction=0),
])
def test_invalid_config_rejected(arg):
    with pytest.raises(ValueError):
        run_qmc(arg)


@pytest.mark.parametrize("changes",[
    {"bad_input": (1,2)},
    {"holdup_beta": (-0.1,0.4)},
    {"holdup_beta": (0.1,0.99)},
    {"initial_air_pressure_pa_abs": (85000.,400000.)},
    {"darcy_factor": (0.04,0.01)},
    {"darcy_factor": (-.04,.02)},
    {"exit_loss_k": (np.nan,3)},
    {"exit_loss_k": (-1.,3)},
])
def test_invalid_bounds_rejected(changes):
    bounds=dict(EXAMPLE_BOUNDS)
    bounds.update(changes)
    with pytest.raises(ValueError):
        run_qmc(QMCSettings(power=2), bounds=bounds)


def test_censored_scenarios_rejected_not_hidden():
    baseline=replace(PushStageSettings(), max_time_s=.15)
    with pytest.raises(RuntimeError, match="do not compute conditional intervals"):
        run_qmc(QMCSettings(power=2), baseline=baseline)
