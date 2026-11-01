"""Pressure boundary examples using standard polytropic gas expansion.

For an isolated gas volume, p * V**n is constant (absolute pressure).
The source term is not a fitted compressor curve or industrial measurement.
"""

import numpy as np


def polytropic_pressure(
    initial_absolute_pressure_pa: float,
    initial_gas_volume_m3: float,
    expanded_volume_m3: float | np.ndarray,
    exponent: float,
) -> float | np.ndarray:
    """Return absolute pressure after the initial gas volume expands.

    `expanded_volume_m3` is the added volume, not the final volume.
    For no additional air inflow, p = p0 * (V0/(V0 + dV))**exponent.
    This illustrative boundary omits gas temperature evolution and tank supply.
    """
    p0 = float(initial_absolute_pressure_pa)
    v0 = float(initial_gas_volume_m3)
    n = float(exponent)
    delta = np.asarray(expanded_volume_m3, dtype=float)
    if not (np.isfinite(p0) and p0 > 0 and np.isfinite(v0) and v0 > 0):
        raise ValueError("Initial absolute pressure and gas volume must be positive and finite")
    if not np.isfinite(n) or n <= 0:
        raise ValueError("Polytropic exponent must be positive and finite")
    if not np.all(np.isfinite(delta)) or np.any(delta < 0):
        raise ValueError("Expanded volume must be nonnegative and finite")
    output = p0 * (v0 / (v0 + delta)) ** n
    return float(output) if output.ndim == 0 else output
