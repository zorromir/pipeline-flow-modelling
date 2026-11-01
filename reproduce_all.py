from dataclasses import replace
import numpy as np
import pytest
from pipeline_flow.dry_demo import DrySettings, simulate_dry_demo
from pipeline_flow.rinse_demo import RinseToDryTransfer
from pipeline_flow.stage_handoff import run_rinse_to_dry_demo


def input_state(water=12.,gas=.06):
    return RinseToDryTransfer(time_s=60.,water_in_pipe_l=water,
        wall_product_by_segment_l=(.3,.2),mobile_product_by_segment_l=(.1,.05),
        gas_mass_flow_kg_s=gas)


def test_dry_exact_endpoint_and_conservation():
    tr=input_state();s=DrySettings()
    r=simulate_dry_demo(tr,s)
    assert r.stop_reason=='target_reached'
    assert r.water_remaining_l[0]==tr.water_in_pipe_l
    assert r.water_remaining_l[-1]==pytest.approx(tr.water_in_pipe_l*(1-s.target_removed_fraction))
    assert np.max(np.abs(r.water_balance_residual_l))<1e-12
    assert np.allclose(r.water_remaining_l+r.water_removed_l,tr.water_in_pipe_l)


def test_product_metadata_unchanged():
    tr=input_state();r=simulate_dry_demo(tr)
    assert r.remaining_product_l==pytest.approx(.65)
    assert r.gas_mass_flow_kg_s==tr.gas_mass_flow_kg_s
    assert r.total_time_s[0]==60


def test_nonnegative_and_monotonic_dry():
    r=simulate_dry_demo(input_state())
    assert np.all(r.water_remaining_l>=0)
    assert np.all(np.diff(r.water_remaining_l)<=0)
    assert np.all(np.diff(r.water_removed_l)>=0)


def test_zero_water_immediate_stop():
    r=simulate_dry_demo(input_state(water=0))
    assert r.stop_reason=='target_reached'
    assert np.all(r.local_time_s==0)
    assert np.all(r.water_remaining_l==0)


def test_zero_target_immediate_stop():
    r=simulate_dry_demo(input_state(),DrySettings(target_removed_fraction=0))
    assert r.stop_reason=='target_reached'
    assert r.local_time_s[-1]==0


def test_zero_rate_times_out_and_conserves():
    r=simulate_dry_demo(input_state(),DrySettings(water_removal_rate_per_s=0))
    assert r.stop_reason=='time_limit'
    assert r.water_remaining_l[-1]==pytest.approx(12.)


def test_positive_rate_time_limit():
    r=simulate_dry_demo(input_state(),DrySettings(water_removal_rate_per_s=.001,max_duration_s=10))
    assert r.stop_reason=='time_limit'
    assert r.local_time_s[-1]==10
    assert r.water_remaining_l[-1]>1.2


def test_sample_count_and_time_origin():
    r=simulate_dry_demo(input_state(),samples=19)
    assert len(r.local_time_s)==19
    assert np.allclose(r.total_time_s-r.local_time_s,60)


@pytest.mark.parametrize('fields',[
 dict(water_removal_rate_per_s=-.01),dict(water_removal_rate_per_s=float('nan')),
 dict(target_removed_fraction=-.1),dict(target_removed_fraction=1),
 dict(target_removed_fraction=float('inf')),dict(max_duration_s=0)
])
def test_invalid_dry_inputs(fields):
    with pytest.raises(ValueError):simulate_dry_demo(input_state(),replace(DrySettings(),**fields))


@pytest.mark.parametrize('samples',[0,1,1.1])
def test_invalid_dry_sampling(samples):
    with pytest.raises(ValueError):simulate_dry_demo(input_state(),samples=samples)


def test_handoff_conservation_both_components():
    result=run_rinse_to_dry_demo()
    assert abs(result.water_transfer_residual_l)<1e-10
    assert abs(result.product_transfer_residual_l)<1e-10
    assert result.rinse.time_s[-1]==pytest.approx(result.dry.total_time_s[0])


def test_handoff_rejects_invalid_source_state():
    with pytest.raises(ValueError):simulate_dry_demo(replace(input_state(),water_in_pipe_l=-.2))


def test_dry_rate_is_explicitly_not_driven_by_gas_metadata():
    a=simulate_dry_demo(input_state(gas=.01))
    b=simulate_dry_demo(input_state(gas=.12))
    assert np.array_equal(a.water_remaining_l,b.water_remaining_l)
