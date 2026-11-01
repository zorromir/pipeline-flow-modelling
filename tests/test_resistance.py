"""Independent closed-form Darcy–Weisbach and hydrostatic benchmarks."""
from math import pi
import numpy as np
import pytest
from pipeline_flow.geometry import PipeNetwork,PipeSegment
from pipeline_flow.resistance import pressure_losses


def test_single_horizontal_pipe_closed_form():
    p=PipeNetwork((PipeSegment(10,.1,local_loss_k=1.5),))
    q=.005;rho=1000;f=.03
    v=q/(pi*.1**2/4)
    dynamic=.5*rho*v*v
    r=pressure_losses(p,q,rho,f,reference_outlet_pa=101325)
    assert r.friction_pa==pytest.approx(f*10/.1*dynamic)
    assert r.local_pa==pytest.approx(1.5*dynamic)
    assert r.elevation_pa==0
    assert r.total_pa==pytest.approx((f*10/.1+1.5)*dynamic)
    assert r.upstream_pressure_pa==pytest.approx(101325+r.total_pa)
    assert r.junction_pressures_pa==(r.upstream_pressure_pa,101325)


def test_segments_add_and_junction_profile():
    p=PipeNetwork((PipeSegment(15,.2,0,2,local_loss_k=3),
                   PipeSegment(8,.1,2,1,local_loss_k=2)))
    q=.01;rho=900
    r=pressure_losses(p,q,rho,(.02,.04),reference_outlet_pa=101325)
    assert len(r.sections)==2
    assert r.total_pa==pytest.approx(sum(s.total_pa for s in r.sections))
    assert r.elevation_pa==pytest.approx(rho*9.80665*(1-0))
    assert r.junction_pressures_pa[0]-r.junction_pressures_pa[1]==pytest.approx(r.sections[0].total_pa)
    assert r.junction_pressures_pa[1]-r.junction_pressures_pa[2]==pytest.approx(r.sections[1].total_pa)


def test_downhill_can_raise_pressure():
    p=PipeNetwork((PipeSegment(10,.1,5,0,local_loss_k=0),))
    r=pressure_losses(p,0,1000,0,reference_outlet_pa=101325)
    assert r.total_pa==pytest.approx(-1000*9.80665*5)
    assert r.upstream_pressure_pa<r.reference_outlet_pa
    assert r.friction_pa==0 and r.local_pa==0


def test_local_k_counts_only_when_original_end_is_crossed():
    p=PipeNetwork((PipeSegment(10,.1,0,0,local_loss_k=5),))
    part=pressure_losses(p,.01,1000,0,start_m=0,end_m=9)
    full=pressure_losses(p,.01,1000,0,start_m=0,end_m=10)
    assert part.local_pa==0
    assert full.local_pa>0


def test_zero_flow_hydrostatic_only():
    p=PipeNetwork((PipeSegment(30,.2,0,10,local_loss_k=100),))
    r=pressure_losses(p,0,999,.03)
    assert r.friction_pa==0 and r.local_pa==0
    assert r.total_pa==pytest.approx(999*9.80665*10)


def test_split_uniform_pipe_preserves_pressure_loss_without_local_k():
    full=PipeNetwork((PipeSegment(100,.12,0,10),))
    split=PipeNetwork((PipeSegment(40,.12,0,4),PipeSegment(60,.12,4,10)))
    a=pressure_losses(full,.008,1000,.025)
    b=pressure_losses(split,.008,1000,.025)
    assert a.total_pa==pytest.approx(b.total_pa)
    assert a.elevation_pa==pytest.approx(b.elevation_pa)
    assert a.friction_pa==pytest.approx(b.friction_pa)


def test_quadratic_flow_dependence_of_losses():
    p=PipeNetwork((PipeSegment(10,.15,local_loss_k=3),))
    a=pressure_losses(p,.01,1000,.02)
    b=pressure_losses(p,.02,1000,.02)
    assert b.friction_pa==pytest.approx(4*a.friction_pa)
    assert b.local_pa==pytest.approx(4*a.local_pa)


def test_roughness_does_not_automatically_change_friction():
    p1=PipeNetwork((PipeSegment(5,.1,roughness_m=0),))
    p2=PipeNetwork((PipeSegment(5,.1,roughness_m=.0001),))
    assert pressure_losses(p1,.001,1000,.02).total_pa==pressure_losses(p2,.001,1000,.02).total_pa


def test_incorrect_Darcy_inputs_are_rejected():
    p=PipeNetwork((PipeSegment(5,.1),PipeSegment(6,.2)))
    for f in [-1,float('nan'),float('inf'),(0.02,),(.02,-.1)]:
        with pytest.raises(ValueError):
            pressure_losses(p,.002,1000,f)
    for q,rho in [(-1,1000),(.01,0),(float('nan'),1000),(.01,float('inf'))]:
        with pytest.raises(ValueError):
            pressure_losses(p,q,rho,.02)
    with pytest.raises(ValueError):
        pressure_losses(p,.001,1000,.02,reference_outlet_pa=float('nan'))


def test_profile_needs_outlet_reference():
    p=PipeNetwork((PipeSegment(5,.1),))
    with pytest.raises(ValueError):
        _=pressure_losses(p,.001,1000,.02).junction_pressures_pa
