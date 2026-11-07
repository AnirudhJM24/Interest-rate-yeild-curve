import numpy as np
import pandas as pd
import pytest

from irr.pricing import price_bond, portfolio_value

FLAT = pd.Series(0.04, index=[1 / 12, 1, 2, 5, 10, 30])


def test_zero_rate_price_is_sum_of_cashflows():
    assert price_bond(100, 0.05, 5, FLAT * 0) == pytest.approx(125)


def test_flat_curve_matches_closed_form():
    t = np.arange(1, 11)
    expected = (4 * np.exp(-0.04 * t)).sum() + 100 * np.exp(-0.4)
    assert price_bond(100, 0.04, 10, FLAT) == pytest.approx(expected)


def test_price_falls_when_rates_rise(portfolio, curve):
    assert portfolio_value(portfolio, curve + 0.01) < portfolio_value(portfolio, curve)
