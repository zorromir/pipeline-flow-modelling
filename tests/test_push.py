from dataclasses import replace
import numpy as np
import pytest
from pipeline_flow import PushParameters, simulate_push


def test_push_stops_before_singular_column_length():
    p = PushParameters()
    r = simulate_push(p)
    assert r.time_s[0] == 0
    assert r.remaining_column_m[0] == p.initial_column_length_m
    assert r.remaining_column_m[-1] == pytest.approx(p.min_column_length_m, abs=1e-6)
    assert np.all(np.diff(r.remaining_column_m) <= 1e-8)
    assert np.all(r.remaining_column_m > 0)


def test_push_volume_and_flow_are_consistent():
    p = PushParameters()
    r = simulate_push(p)
    swept = r.swept_volume_m3
    assert np.max(np.abs(r.holdup_volume_m3 + r.discharged_volume_m3 - swept)) < 1e-10
    assert np.allclose(r.discharged_flow_m3_s, r.outlet_velocity_m_s*np.pi*(p.diameter_m/2)**2)
    assert np.all(r.discharged_volume_m3 >= 0)


def test_added_resistance_reduces_discharge_near_first_common_time():
    lo = simulate_push(PushParameters(exit_loss_coefficient=2))
    hi = simulate_push(PushParameters(exit_loss_coefficient=8))
    t = min(lo.time_s[-1], hi.time_s[-1], 10.0)
    assert np.interp(t, lo.time_s, lo.discharged_flow_m3_s) > np.interp(t, hi.time_s, hi.discharged_flow_m3_s)


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        simulate_push(replace(PushParameters(), holdup_fraction=1))
    with pytest.raises(ValueError):
        simulate_push(PushParameters(), samples=2)
