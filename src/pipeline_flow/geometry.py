"""Original, data-free 1D geometry utilities for consecutive pipe segments.

Definitions follow standard geometric identities: A=pi*D²/4 and
V(a,b)=sum_i A_i * length([a,b] intersection segment_i).

A local K value belongs to the **downstream end** of its original
physical segment. It must not be counted when the interval ends early.
No industrial geometry or employer source code is included.
"""

from dataclasses import dataclass
from math import isfinite, pi, sqrt


def _number(value: float, label: str) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not isfinite(v):
        raise ValueError(f"{label} must be finite")
    return v


@dataclass(frozen=True)
class PipeSegment:
    """A round pipe segment; local_loss_k acts at its downstream end."""

    length_m: float
    diameter_m: float
    start_height_m: float = 0.0
    end_height_m: float = 0.0
    local_loss_k: float = 0.0
    roughness_m: float = 0.0  # metadata; does not select a Darcy factor

    def __post_init__(self) -> None:
        for name in ("length_m", "diameter_m", "start_height_m", "end_height_m",
                     "local_loss_k", "roughness_m"):
            object.__setattr__(self, name, _number(getattr(self, name), name))
        if self.length_m <= 0 or self.diameter_m <= 0:
            raise ValueError("Length and diameter must be strictly positive")
        if self.local_loss_k < 0 or self.roughness_m < 0:
            raise ValueError("K and roughness must be nonnegative")
        if self.roughness_m >= self.diameter_m:
            raise ValueError("Roughness cannot be as large as the diameter")

    @property
    def area_m2(self) -> float:
        return pi * self.diameter_m**2 / 4

    @property
    def volume_m3(self) -> float:
        return self.area_m2 * self.length_m


@dataclass(frozen=True)
class ActivePart:
    """Intersection of a position interval with one physical segment."""
    segment_index: int
    start_position_m: float
    end_position_m: float
    length_m: float
    diameter_m: float
    elevation_change_m: float
    end_loss_k: float

    @property
    def area_m2(self) -> float:
        return pi * self.diameter_m**2 / 4


@dataclass(frozen=True)
class PipeNetwork:
    """One continuous, nonbranching route with sectionwise fixed diameter."""
    segments: tuple[PipeSegment, ...]

    def __post_init__(self) -> None:
        parts = tuple(self.segments)
        if not parts or any(not isinstance(s, PipeSegment) for s in parts):
            raise ValueError("PipeNetwork requires at least one PipeSegment")
        object.__setattr__(self, "segments", parts)
        for before, after in zip(parts, parts[1:]):
            if abs(before.end_height_m-after.start_height_m) > 1e-8:
                raise ValueError("Adjacent pipe elevations must meet at their joint")

    @property
    def length_m(self) -> float:
        return sum(s.length_m for s in self.segments)

    @property
    def volume_m3(self) -> float:
        return sum(s.volume_m3 for s in self.segments)

    @property
    def equivalent_diameter_m(self) -> float:
        """Volume-equivalent D, NOT a pressure-loss-equivalent diameter."""
        return sqrt(4*self.volume_m3/(pi*self.length_m))

    @property
    def boundaries_m(self) -> tuple[float, ...]:
        values = [0.0]
        for s in self.segments:
            values.append(values[-1]+s.length_m)
        return tuple(values)

    def _checked_position(self, pos: float) -> float:
        x = _number(pos,"position")
        if not 0 <= x <= self.length_m:
            raise ValueError("Position outside the pipe route")
        return x

    def section_at(self, position_m: float) -> int:
        """Right-continuous: at an internal joint, select downstream pipe."""
        x=self._checked_position(position_m)
        for i, right in enumerate(self.boundaries_m[1:]):
            if x < right or i == len(self.segments)-1:
                return i
        raise AssertionError("unreachable")

    def area_at(self, position_m: float) -> float:
        return self.segments[self.section_at(position_m)].area_m2

    def height_at(self, position_m: float) -> float:
        x=self._checked_position(position_m)
        i=self.section_at(x)
        s=self.segments[i]
        x0=self.boundaries_m[i]
        return s.start_height_m+(x-x0)/s.length_m*(s.end_height_m-s.start_height_m)

    def active_parts(self, start_m:float=0.0, end_m:float | None=None) -> tuple[ActivePart, ...]:
        a=self._checked_position(start_m)
        b=self.length_m if end_m is None else self._checked_position(end_m)
        if b<a:
            raise ValueError("Expected start <= end")
        result=[]
        bounds=self.boundaries_m
        for i,s in enumerate(self.segments):
            lo=max(a,bounds[i]); hi=min(b,bounds[i+1])
            if hi <= lo:
                continue
            zchange=(hi-lo)/s.length_m*(s.end_height_m-s.start_height_m)
            # A physical local loss belongs only to the original downstream end.
            include_end=hi>=bounds[i+1]-1e-10
            result.append(ActivePart(i,lo,hi,hi-lo,s.diameter_m,zchange,
                                     s.local_loss_k if include_end else 0.0))
        return tuple(result)

    def volume_between(self, start_m: float, end_m:float) -> float:
        return sum(p.area_m2*p.length_m for p in self.active_parts(start_m,end_m))

    def position_from_volume(self, start_m:float, volume_m3:float) -> float:
        """Find x >= start whose enclosed volume equals requested volume."""
        a=self._checked_position(start_m)
        vol=_number(volume_m3,"volume")
        if vol < 0 or vol > self.volume_between(a,self.length_m)+1e-10:
            raise ValueError("Volume cannot fit between starting point and outlet")
        if vol==0:
            return a
        remaining=vol
        for part in self.active_parts(a):
            capacity=part.length_m*part.area_m2
            if remaining<=capacity+1e-12:
                return min(part.end_position_m,part.start_position_m+remaining/part.area_m2)
            remaining-=capacity
        return self.length_m  # roundoff at exact total volume
