import pytest
from pipeline_flow import product_volume_balance


@pytest.mark.parametrize("beta", [0.0, 0.2, 0.5, 0.99])
def test_exact_volume_bookkeeping(beta):
    row = product_volume_balance(5, 2, beta)
    assert row.full_column_m3 == 3
    assert row.discharged_m3 == pytest.approx(2*(1-beta))
    assert row.holdup_m3 == pytest.approx(2*beta)
    assert row.residual_m3 == pytest.approx(0, abs=1e-12)


@pytest.mark.parametrize("v0,swept,beta", [(0,0,0), (1,2,0), (1,-.1,0), (1,0,1)])
def test_invalid_balance_rejected(v0, swept, beta):
    with pytest.raises(ValueError):
        product_volume_balance(v0, swept, beta)
