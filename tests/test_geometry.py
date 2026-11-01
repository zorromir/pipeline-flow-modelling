"""Geometry properties are independently checked against elementary formulas."""

from dataclasses import replace
from math import pi,sqrt

import numpy as np
import pytest

from pipeline_flow.geometry import PipeNetwork,PipeSegment


def test_one_segment_volume_and_inverse():
    s=PipeSegment(10,.2,0,2)
    p=PipeNetwork((s,))
    assert p.volume_m3==pytest.approx(pi*.1**2*10)
    assert p.volume_between(2,7)==pytest.approx(5*pi*.1**2)
    assert p.position_from_volume(2,p.volume_between(2,7))==pytest.approx(7)
    assert p.height_at(5)==pytest.approx(1)


def test_two_diameters_and_equivalent_volume():
    p=PipeNetwork((PipeSegment(7,.1),PipeSegment(3,.2)))
    target=pi/4*(.1**2*7+.2**2*3)
    assert p.volume_m3==pytest.approx(target)
    assert p.equivalent_diameter_m==pytest.approx(sqrt(4*target/(10*pi)))
    assert p.volume_between(4,10)==pytest.approx(pi/4*(3*.1**2+3*.2**2))
    assert p.volume_between(7,7)==0
    assert p.volume_between(0,10)==pytest.approx(target)


def test_inverse_crosses_segment_joint():
    p=PipeNetwork((PipeSegment(10,.1),PipeSegment(10,.2)))
    v=p.volume_between(0,12)
    assert p.position_from_volume(0,v)==pytest.approx(12)
    assert p.position_from_volume(10,2*p.segments[1].area_m2)==pytest.approx(12)
    assert p.position_from_volume(10,0)==10


def test_volume_inversion_round_trip_random_positions():
    p=PipeNetwork((PipeSegment(7,.10),PipeSegment(12,.20),PipeSegment(18,.16)))
    for a in np.linspace(0,p.length_m,11):
        for b in np.linspace(a,p.length_m,12):
            assert p.position_from_volume(a,p.volume_between(a,b))==pytest.approx(b,abs=1e-8)


def test_active_part_height_and_local_losses_only_at_terminal():
    p=PipeNetwork((PipeSegment(10,.1,0,3,local_loss_k=2),
                   PipeSegment(15,.2,3,-1,local_loss_k=4)))
    parts=p.active_parts(4,16)
    assert len(parts)==2
    assert parts[0].length_m==pytest.approx(6)
    assert parts[0].end_loss_k==pytest.approx(2)
    assert parts[1].length_m==pytest.approx(6)
    assert parts[1].end_loss_k==0
    assert sum(x.elevation_change_m for x in parts)==pytest.approx(p.height_at(16)-p.height_at(4))
    assert p.active_parts(1,9)[0].end_loss_k==0
    assert p.active_parts(10,25)[0].end_loss_k==4


def test_section_at_internal_joint_uses_downstream_area():
    p=PipeNetwork((PipeSegment(5,.1),PipeSegment(5,.2)))
    assert p.section_at(4.999)==0
    assert p.section_at(5)==1
    assert p.area_at(5)==p.segments[1].area_m2
    assert p.section_at(10)==1


@pytest.mark.parametrize("segment", [
    dict(length_m=0,diameter_m=.1),dict(length_m=1,diameter_m=0),
    dict(length_m=float('nan'),diameter_m=.1),
    dict(length_m=1,diameter_m=.1,local_loss_k=-.3),
    dict(length_m=1,diameter_m=.1,roughness_m=.2),
    dict(length_m=1,diameter_m=.1,roughness_m=float('inf')),
])
def test_invalid_segment_rejected(segment):
    with pytest.raises(ValueError):
        PipeSegment(**segment)


def test_discontinuous_section_elevation_rejected():
    with pytest.raises(ValueError, match="elevations"):
        PipeNetwork((PipeSegment(1,.1,0,1),PipeSegment(1,.1,2,3)))


@pytest.mark.parametrize("a,b",[(-.1,1),(1,11),(5,2),(float('nan'),1)])
def test_invalid_geometry_interval(a,b):
    p=PipeNetwork((PipeSegment(10,.1),))
    with pytest.raises(ValueError):
        p.volume_between(a,b)


def test_invalid_requested_volume():
    p=PipeNetwork((PipeSegment(10,.1),))
    with pytest.raises(ValueError):
        p.position_from_volume(2,p.volume_m3)
    with pytest.raises(ValueError):
        p.position_from_volume(0,-1)


def test_empty_or_invalid_network():
    with pytest.raises(ValueError):
        PipeNetwork(())
    with pytest.raises(ValueError):
        PipeNetwork(("pipe",))
