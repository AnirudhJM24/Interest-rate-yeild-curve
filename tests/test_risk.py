import numpy as np
import pandas as pd
import pytest

from irr.pricing import price_bond, sample_portfolio
from irr.risk import dv01, key_rate_report


def test_dv01_matches_duration_on_flat_curve():
    flat = pd.Series(0.04, index=[1, 2, 5, 10, 30])
    port = sample_portfolio().iloc[[2]]        # 10Y bond only
    t = np.arange(1, 11)
    cf = np.full(10, 4.0); cf[-1] += 100
    expected = -(cf * t * np.exp(-0.04 * t)).sum() * 1e-4   # -P * D * 1bp
    assert dv01(port, flat) == pytest.approx(expected, rel=1e-3)


def test_key_rates_add_up_to_dv01(portfolio, curve):
    krd = key_rate_report(portfolio, curve)
    assert krd["Dollar Sensitivity"].sum() == pytest.approx(dv01(portfolio, curve), rel=1e-3)
    assert krd["Abs % Contribution"].sum() == pytest.approx(1.0)


def test_nodes_before_first_cashflow_have_no_risk(portfolio, curve):
    krd = key_rate_report(portfolio, curve).set_index("Node (Years)")
    assert (krd.loc[krd.index < 1, "Dollar Sensitivity"] == 0).all()
