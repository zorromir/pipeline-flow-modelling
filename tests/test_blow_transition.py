from dataclasses import replace
import numpy as np
import pytest
from pipeline_flow.blow_transition import BlowTransitionSettings, simulate_blow_transition


def test_conservation_and_nonnegative_states():
    cfg = BlowTransitionSettings()
    r = simulate_blow_transition(cfg)
    assert r.stop_reason == "minimum_column_length"
    assert r.liquid_column_length_m[-1] == pytest.approx(cfg.stop_column_length_m, abs=1e-6)
    assert np.max(np.abs(r.volume_residual_m3)) < 1e-8
    assert np.all(r.outlet_flow_m3_s >= -1e-10)
    assert np.all(np.diff(r.discharged_volume_m3) >= -1e-9)
    assert np.all(np.diff(r.tail_holdup_volume_m3) >= -1e-9)
    assert np.all(np.diff(r.liquid_column_length_m) <= 1e-9)


def test_alpha_one_no_tail_leakage():
    r = simulate_blow_transition(BlowTransitionSettings(alpha=1))
    assert np.max(np.abs(r.tail_holdup_volume_m3)) < 1e-12


def test_volume_split_matches_alpha():
    cfg = BlowTransitionSettings(alpha=.7)
    r = simulate_blow_transition(cfg)
    swept = cfg.area_m2 * (cfg.length_m - r.liquid_column_length_m)
    assert np.max(np.abs(r.discharged_volume_m3 - cfg.alpha*swept)) < 1e-8
    assert np.max(np.abs(r.tail_holdup_volume_m3 - (1-cfg.alpha)*swept)) < 1e-8


def test_zero_time_derivative_positive():
    r = simulate_blow_transition()
    assert r.outlet_velocity_m_s[0] == pytest.approx(0)
    assert r.outlet_velocity_m_s[1] > 0


def test_step_refinement_consistent():
    cfg = BlowTransitionSettings()
    coarse = simulate_blow_transition(cfg,max_step_s=.12)
    fine = simulate_blow_transition(cfg,max_step_s=.025)
    assert coarse.final_time_s == pytest.approx(fine.final_time_s, rel=3e-5)
    assert coarse.outlet_velocity_m_s[-1] == pytest.approx(fine.outlet_velocity_m_s[-1],rel=3e-5)


def test_time_limit_is_explicit():
    r = simulate_blow_transition(BlowTransitionSettings(max_time_s=.015))
    assert r.stop_reason == "time_limit"
    assert r.liquid_column_length_m[-1] > .3


@pytest.mark.parametrize("change", [
    {"alpha":0}, {"alpha":-0.1}, {"alpha":1.1},
    {"residual_momentum_beta":-0.01},{"residual_momentum_beta":1.1},
    {"local_loss_k":-1}, {"darcy_factor":-1},
    {"length_m":0}, {"stop_column_length_m":0},
    {"stop_column_length_m":25}, {"upstream_pressure_pa_abs":100_000},
    {"outlet_pressure_pa_abs":200_000},
    {"density_kg_m3":float("nan")}, {"max_time_s":float("inf")}
])
def test_invalid_parameters_rejected(change):
    with pytest.raises(ValueError):
        simulate_blow_transition(replace(BlowTransitionSettings(), **change))


@pytest.mark.parametrize("opts",[{"samples":2},{"max_step_s":0},{"rtol":.5}])
def test_invalid_controls_rejected(opts):
    with pytest.raises(ValueError):
        simulate_blow_transition(**opts)
