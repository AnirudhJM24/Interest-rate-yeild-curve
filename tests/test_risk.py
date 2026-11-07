import pytest

from irr.risk import dv01, key_rate_report


def test_dv01_matches_notebook(portfolio, curve):
    assert dv01(portfolio, curve) == pytest.approx(-0.303399, abs=1e-6)


def test_key_rates_add_up_to_dv01(portfolio, curve):
    krd = key_rate_report(portfolio, curve)
    assert krd["Dollar Sensitivity"].sum() == pytest.approx(dv01(portfolio, curve), rel=1e-3)
    assert krd["Abs % Contribution"].sum() == pytest.approx(1.0)


def test_nodes_before_first_cashflow_have_no_risk(portfolio, curve):
    krd = key_rate_report(portfolio, curve).set_index("Node (Years)")
    assert (krd.loc[krd.index < 1, "Dollar Sensitivity"] == 0).all()
