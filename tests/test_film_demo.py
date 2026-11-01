from dataclasses import replace
import numpy as np
import pytest
from pipeline_flow.film_demo import FilmScenario, simulate_film_demo


def test_inventory_conserved_and_monotone():
    cfg = FilmScenario()
    result = simulate_film_demo(cfg)
    assert np.allclose(result.remaining_volume_l + result.removed_volume_l, cfg.initial_volume_l)
    assert np.all(np.diff(result.remaining_volume_l) <= 0)
    assert np.all(result.remaining_volume_l >= 0)


def test_exact_exponential_and_initial_conditions():
    cfg=FilmScenario(removal_rate_per_s=.03, horizon_s=90)
    r=simulate_film_demo(cfg)
    assert r.remaining_volume_l[0] == cfg.initial_volume_l
    assert r.removed_volume_l[0] == 0
    assert r.remaining_volume_l[-1] == pytest.approx(cfg.initial_volume_l*np.exp(-.03*90))


def test_zero_rate_means_no_film_removal():
    result=simulate_film_demo(FilmScenario(removal_rate_per_s=0))
    assert np.all(result.removed_volume_l==0)


def test_higher_assumed_rate_reduces_inventory():
    slow=simulate_film_demo(FilmScenario(removal_rate_per_s=.01))
    fast=simulate_film_demo(FilmScenario(removal_rate_per_s=.04))
    assert fast.remaining_volume_l[-1] < slow.remaining_volume_l[-1]


@pytest.mark.parametrize("values", [
    {"initial_volume_l":0}, {"initial_volume_l":float("nan")},
    {"removal_rate_per_s":-1}, {"removal_rate_per_s":float("inf")},
    {"horizon_s":0}, {"horizon_s":-1}
])
def test_invalid_scenario(values):
    with pytest.raises(ValueError):
        simulate_film_demo(replace(FilmScenario(),**values))


def test_invalid_sampling():
    with pytest.raises(ValueError):
        simulate_film_demo(samples=1)
