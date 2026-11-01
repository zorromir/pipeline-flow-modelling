"""Single-phase constant-density, fixed-Darcy-factor pressure losses.

For section i: dp_i = f_D,i (L_i/D_i) rho v_i |v_i| / 2
                     + rho*g*dz_i + K_i rho v_i |v_i| / 2.
This is a steady incompressible hydraulic illustration, *not* a transient
multiphase momentum solver. Local K is attached to its section's outlet.
"""

from dataclasses import dataclass
from math import isfinite

from .geometry import PipeNetwork


@dataclass(frozen=True)
class SectionLoss:
    index: int
    start_position_m: float
    end_position_m: float
    friction_pa: float
    elevation_pa: float
    local_pa: float

    @property
    def total_pa(self) -> float:
        return self.friction_pa+self.elevation_pa+self.local_pa


@dataclass(frozen=True)
class PressureLossResult:
    sections: tuple[SectionLoss,...]
    flow_m3_s: float
    density_kg_m3: float
    reference_outlet_pa: float | None

    @property
    def friction_pa(self) -> float:
        return sum(x.friction_pa for x in self.sections)

    @property
    def elevation_pa(self) -> float:
        return sum(x.elevation_pa for x in self.sections)

    @property
    def local_pa(self) -> float:
        return sum(x.local_pa for x in self.sections)

    @property
    def total_pa(self) -> float:
        return self.friction_pa+self.elevation_pa+self.local_pa

    @property
    def upstream_pressure_pa(self) -> float | None:
        return (None if self.reference_outlet_pa is None
                else self.reference_outlet_pa+self.total_pa)

    @property
    def junction_pressures_pa(self) -> tuple[float,...]:
        """Pressures from inlet to outlet, if an outlet reference is supplied."""
        if self.reference_outlet_pa is None:
            raise ValueError("Set reference_outlet_pa to calculate pressures")
        values=[float(self.reference_outlet_pa)]
        for part in reversed(self.sections):
            values.append(values[-1]+part.total_pa)
        return tuple(reversed(values))


def pressure_losses(network:PipeNetwork, flow_m3_s:float, density_kg_m3:float,
                    darcy_factors:float | tuple[float,...], *,
                    gravitational_acceleration_m_s2:float=9.80665,
                    reference_outlet_pa:float | None=None,
                    start_m:float=0., end_m:float | None=None) -> PressureLossResult:
    """Return contributions over physical active parts in the forward direction.

    flow>=0 is required: the sign/location of local losses under flow reversal
    is not modelled. No acceleration or entrance/contraction term is automatically
    included. Pressure reference must be absolute if absolute output is desired.
    """
    if not isinstance(network,PipeNetwork):
        raise TypeError("network must be PipeNetwork")
    q=float(flow_m3_s);rho=float(density_kg_m3);g=float(gravitational_acceleration_m_s2)
    if not (isfinite(q) and q>=0 and isfinite(rho) and rho>0 and isfinite(g) and g>0):
        raise ValueError("Use finite nonnegative forward flow, positive density and gravity")
    if isinstance(darcy_factors, (float,int)):
        factors=(float(darcy_factors),)*len(network.segments)
    else:
        factors=tuple(float(x) for x in darcy_factors)
    if len(factors)!=len(network.segments) or any(not isfinite(x) or x<0 for x in factors):
        raise ValueError("Provide one finite nonnegative Darcy factor per segment")
    if reference_outlet_pa is not None and not isfinite(float(reference_outlet_pa)):
        raise ValueError("Reference outlet pressure must be finite")
    parts=network.active_parts(start_m,end_m)
    sections=[]
    for part in parts:
        speed=q/part.area_m2
        head=rho*speed*speed/2
        sections.append(SectionLoss(part.segment_index,part.start_position_m,part.end_position_m,
                                    factors[part.segment_index]*(part.length_m/part.diameter_m)*head,
                                    rho*g*part.elevation_change_m,
                                    part.end_loss_k*head))
    return PressureLossResult(tuple(sections),q,rho,
                              None if reference_outlet_pa is None else float(reference_outlet_pa))
