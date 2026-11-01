"""Bookkeeping for a one-dimensional product-removal illustration.

No industrial composition, measurements or calibration are used here.
This is a geometric balance only; it does not describe film cleaning kinetics.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ProductVolumeBalance:
    initial_m3: float
    full_column_m3: float
    discharged_m3: float
    holdup_m3: float

    @property
    def residual_m3(self) -> float:
        return self.initial_m3 - (
            self.full_column_m3 + self.discharged_m3 + self.holdup_m3
        )


def product_volume_balance(
    initial_m3: float, swept_m3: float, holdup_fraction: float
) -> ProductVolumeBalance:
    """Divide initial liquid into full column, outlet volume and wall holdup.

    Constant-beta bookkeeping, for a pipe with uniform area:
    V_full=V0-V_pass; V_out=(1-beta)*V_pass; V_holdup=beta*V_pass.
    """
    v0, swept, beta = map(float, (initial_m3, swept_m3, holdup_fraction))
    if not all(isfinite(x) for x in (v0, swept, beta)):
        raise ValueError("All inputs must be finite")
    if v0 <= 0 or not (0 <= swept <= v0) or not (0 <= beta < 1):
        raise ValueError("Require V0>0, 0<=swept<=V0, and 0<=beta<1")
    return ProductVolumeBalance(
        initial_m3=v0,
        full_column_m3=v0-swept,
        discharged_m3=(1-beta)*swept,
        holdup_m3=beta*swept,
    )
