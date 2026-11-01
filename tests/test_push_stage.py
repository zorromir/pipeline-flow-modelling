"""Model verification with hypothetical inputs only (no measured validation)."""

from dataclasses import replace
from math import pi

import numpy as np
import pytest

from pipeline_flow.push_stage import (
    PushStageSettings, momentum_terms, pressure_from_interface, simulate_push_stage,
)


def test_initial_and_goal_states():
    p = PushStageSettings()
    r = simulate_push_stage(p)
    assert r.stop_reason == "product_target"
    assert r.time_s[0] == 0
    assert r.interface_position_m[0] == pytest.approx(0)
    assert r.outlet_flow_m3_s[0] == pytest.approx(0)
    assert r.discharged_volume_m3[-1] == pytest.approx(0.5 * p.initial_liquid_volume_m3, abs=1e-8)
    assert r.interface_position_m[-1] == pytest.approx(0.5*p.column_length_m/(1-p.holdup_beta))
    assert np.all(np.diff(r.interface_position_m) >= -1e-8)
    assert np.all(r.remaining_column_m >= p.minimum_column_m-1e-8)


def test_volume_bookkeeping_and_integrated_flow():
    p = PushStageSettings()
    r = simulate_push_stage(p, samples=700)
    assert r.max_absolute_volume_residual_m3 < 1e-11
    assert np.allclose(r.full_column_volume_m3+r.holdup_volume_m3+r.discharged_volume_m3,
                       p.initial_liquid_volume_m3, atol=1e-11)
    numerical_integral = np.trapezoid(r.outlet_flow_m3_s, r.time_s)
    assert numerical_integral == pytest.approx(r.discharged_volume_m3[-1], rel=3e-5)


def test_two_pressure_modes_and_polytropic_invariant():
    p = PushStageSettings()
    trapped = simulate_push_stage(p)
    constant = simulate_push_stage(replace(p, pressure_mode="constant"))
    assert trapped.stop_time_s > constant.stop_time_s
    assert np.all(np.diff(trapped.air_pressure_pa_abs) < 1e-5)
    assert np.allclose(constant.air_pressure_pa_abs, p.initial_air_pressure_pa_abs)
    k = trapped.air_pressure_pa_abs * trapped.air_volume_m3**p.gas_polytropic_exponent
    assert np.max(abs(k / k[0]-1)) < 1e-10


def test_at_start_tail_and_outlet_pressures_are_absolute():
    p = PushStageSettings()
    assert pressure_from_interface(p, 0) == p.initial_air_pressure_pa_abs
    assert pressure_from_interface(p, p.column_length_m/2) < p.initial_air_pressure_pa_abs
    assert pressure_from_interface(replace(p, pressure_mode="constant"), 20) == p.initial_air_pressure_pa_abs
    with pytest.raises(ValueError):
        pressure_from_interface(p, -1)


def test_momentum_is_consistent_with_independent_numerical_derivative():
    p = PushStageSettings()
    r = simulate_push_stage(p, samples=1000)
    # Away from the first and last points, central differencing approximates dQ/dt.
    dqdt = np.gradient(r.outlet_flow_m3_s, r.time_s, edge_order=2)
    acceleration_numerical = dqdt / ((1-p.holdup_beta)*p.area_m2)
    acceleration_model = np.array([
        momentum_terms(p, float(q), float(x))[0]
        for q,x in zip(r.outlet_flow_m3_s, r.interface_position_m)
    ])
    np.testing.assert_allclose(acceleration_numerical[10:-10],acceleration_model[10:-10],atol=3e-3,rtol=7e-3)
    assert r.max_absolute_pressure_residual_pa < 1e-7


def test_numerical_step_convergence():
    p = PushStageSettings()
    coarse = simulate_push_stage(p, max_step_s=.16, rtol=1e-7)
    fine = simulate_push_stage(p, max_step_s=.025, rtol=1e-10)
    assert coarse.stop_reason == fine.stop_reason == "product_target"
    assert abs(coarse.stop_time_s-fine.stop_time_s) < 2e-4
    time = 4.0
    assert abs(np.interp(time,coarse.time_s,coarse.outlet_flow_m3_s)
               -np.interp(time,fine.time_s,fine.outlet_flow_m3_s)) < 2e-5


def test_safety_stop_when_no_removal_target():
    p = replace(PushStageSettings(), target_discharged_fraction=None)
    r = simulate_push_stage(p)
    assert r.stop_reason == "minimum_length"
    assert r.remaining_column_m[-1] == pytest.approx(p.minimum_column_m,abs=2e-6)


def test_zero_holdup_means_no_residual_liquid():
    p = replace(PushStageSettings(), holdup_beta=0.0, target_discharged_fraction=.5)
    r = simulate_push_stage(p)
    assert np.all(r.holdup_volume_m3 == 0)
    assert r.interface_position_m[-1] == pytest.approx(.5*p.column_length_m)


def test_time_limit_status_when_short_horizon():
    p = replace(PushStageSettings(), max_time_s=.1)
    r = simulate_push_stage(p)
    assert r.stop_reason == "time_limit"
    assert r.stop_time_s == pytest.approx(.1)


def test_stall_event_under_small_initial_gas_volume():
    p = replace(PushStageSettings(), initial_air_pressure_pa_abs=150000,
                air_initial_volume_m3=0.10, target_discharged_fraction=None)
    r = simulate_push_stage(p)
    assert r.stop_reason == "flow_stall"
    assert r.outlet_flow_m3_s[-1] == pytest.approx(0, abs=1e-8)
    assert np.min(r.outlet_flow_m3_s) >= -1e-7


@pytest.mark.parametrize("changes", [
    dict(pressure_mode="measured"),
    dict(initial_air_pressure_pa_abs=80000),
    dict(outlet_pressure_pa_abs=-1000),
    dict(holdup_beta=1),
    dict(target_discharged_fraction=.95),
    dict(target_discharged_fraction=-.3),
    dict(gas_polytropic_exponent=0),
    dict(minimum_column_m=0),
    dict(darcy_factor=-.01),
    dict(air_initial_volume_m3=0),
])
def test_input_rejection(changes):
    with pytest.raises(ValueError):
        simulate_push_stage(replace(PushStageSettings(), **changes))


def test_invalid_integration_arguments():
    with pytest.raises(ValueError):
        simulate_push_stage(PushStageSettings(), samples=1)
    with pytest.raises(ValueError):
        simulate_push_stage(PushStageSettings(), max_step_s=-1)
