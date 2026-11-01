import numpy as np
import pytest
from pipeline_flow import polytropic_pressure


def test_original_pressure_is_returned_without_expansion():
    assert polytropic_pressure(200_000, 0.5, 0, 1.2) == 200_000


def test_expansion_reduces_pressure_and_preserves_shape():
    volumes = np.array([0, 0.1, 0.3])
    p = polytropic_pressure(200_000, 0.5, volumes, 1.2)
    assert p.shape == volumes.shape
    assert np.all(np.diff(p) < 0)


@pytest.mark.parametrize("p0,v0,dv,n", [
    (0, 1, 1, 1.2), (1, 0, 1, 1.2), (1, 1, -0.1, 1.2), (1, 1, 1, 0),
])
def test_invalid_inputs_rejected(p0, v0, dv, n):
    with pytest.raises(ValueError):
        polytropic_pressure(p0, v0, dv, n)
