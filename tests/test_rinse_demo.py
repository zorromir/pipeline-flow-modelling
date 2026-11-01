from dataclasses import replace
import numpy as np
import pytest
from pipeline_flow.rinse_demo import RinseSettings, RinseToDryTransfer, simulate_rinse_demo


def test_rinse_water_conservation():
    s=RinseSettings(); r=simulate_rinse_demo(s)
    assert np.max(np.abs(r.water_balance_residual_l)) < 1e-8
    assert r.injected_water_l[-1] == pytest.approx(s.water_goal_l,abs=1e-8)
    assert r.water_by_segment_l[-1].sum()+r.discharged_water_l[-1] == pytest.approx(s.water_goal_l,abs=1e-8)


def test_rinse_product_conservation():
    s=RinseSettings();r=simulate_rinse_demo(s)
    initial=sum(s.initial_mobile_product_l)+sum(s.initial_wall_product_l)
    assert np.max(np.abs(r.product_balance_residual_l)) < 1e-8
    assert (r.mobile_product_by_segment_l[-1].sum()+r.wall_product_by_segment_l[-1].sum()+r.discharged_product_l[-1])==pytest.approx(initial)


def test_nonnegative_inventories_and_monotonic_discharge():
    r=simulate_rinse_demo()
    for a in (r.water_by_segment_l,r.mobile_product_by_segment_l,r.wall_product_by_segment_l,r.injected_water_l,r.discharged_water_l,r.discharged_product_l):
        assert np.min(a) >= -1e-10
    assert np.all(np.diff(r.injected_water_l)>=-1e-12)
    assert np.all(np.diff(r.discharged_water_l)>=-1e-12)
    assert np.all(np.diff(r.discharged_product_l)>=-1e-12)


def test_wall_product_nonincreasing_and_mobile_can_increase():
    r=simulate_rinse_demo()
    assert np.all(np.diff(r.wall_product_by_segment_l,axis=0)<=1e-10)
    assert r.mobile_product_by_segment_l[:,0].max()>r.mobile_product_by_segment_l[0,0]


def test_zero_detachment_keeps_wall_constant():
    s=RinseSettings(detachment_rate_per_s=0)
    r=simulate_rinse_demo(s)
    assert np.allclose(r.wall_product_by_segment_l,r.wall_product_by_segment_l[0])


def test_zero_initial_product_no_product_outflow():
    s=RinseSettings(initial_wall_product_l=(0.,)*3,initial_mobile_product_l=(0.,)*3)
    r=simulate_rinse_demo(s)
    assert np.all(r.wall_product_by_segment_l==0)
    assert np.all(r.mobile_product_by_segment_l==0)
    assert np.all(r.discharged_product_l==0)


def test_different_number_of_segments_supported():
    s=RinseSettings(mixing_volumes_l=(3.,),initial_wall_product_l=(.4,),initial_mobile_product_l=(.1,))
    r=simulate_rinse_demo(s)
    assert r.water_by_segment_l.shape==(451,1)
    assert len(r.transfer.wall_product_by_segment_l)==1


def test_time_and_injection_stop_exact():
    s=RinseSettings(water_flow_l_s=2.,water_goal_l=10.)
    r=simulate_rinse_demo(s,samples=23)
    assert r.time_s[-1]==pytest.approx(5)
    assert r.transfer.time_s==pytest.approx(5)
    assert r.injected_water_l[-1]==pytest.approx(10)


def test_transfer_matches_final_inventory():
    r=simulate_rinse_demo()
    assert r.transfer.water_in_pipe_l==pytest.approx(r.water_by_segment_l[-1].sum())
    assert r.transfer.wall_product_by_segment_l==pytest.approx(r.wall_product_by_segment_l[-1])
    assert r.transfer.mobile_product_by_segment_l==pytest.approx(r.mobile_product_by_segment_l[-1])


@pytest.mark.parametrize('fields',[
    dict(mixing_volumes_l=()),dict(mixing_volumes_l=(1.,2.)),
    dict(initial_wall_product_l=(1.,)),dict(initial_mobile_product_l=(0.,)),
    dict(mixing_volumes_l=(0.,1.,1.)),dict(mixing_volumes_l=(-1.,1.,1.)),
    dict(initial_wall_product_l=(0.,-1.,0.)),
    dict(initial_mobile_product_l=(0.,float('nan'),0.)),
    dict(water_flow_l_s=0),dict(water_goal_l=-1),
    dict(detachment_rate_per_s=-.1),dict(gas_mass_flow_kg_s=-1),
    dict(max_duration_s=0),dict(water_goal_l=1000.),
    dict(water_flow_l_s=float('inf')),
])
def test_invalid_rinse_inputs(fields):
    with pytest.raises(ValueError):simulate_rinse_demo(replace(RinseSettings(),**fields))


@pytest.mark.parametrize('samples',[0,1,1.5])
def test_invalid_rinse_sampling(samples):
    with pytest.raises(ValueError):simulate_rinse_demo(samples=samples)


@pytest.mark.parametrize('fields',[dict(time_s=-1),dict(water_in_pipe_l=-1),
 dict(gas_mass_flow_kg_s=float('inf')),
 dict(mobile_product_by_segment_l=(.2,)),dict(wall_product_by_segment_l=())])
def test_invalid_transfer(fields):
    base=RinseToDryTransfer(2,1.,(.1,.2),(.3,.4),.06)
    with pytest.raises(ValueError):replace(base,**fields).validate()
