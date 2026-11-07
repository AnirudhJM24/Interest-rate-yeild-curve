import pytest

from irr.scenarios import default_scenarios, scenario_pnl, shock_twist


def test_scenario_pnl_matches_notebook(portfolio, curve):
    pnl = scenario_pnl(portfolio, curve, default_scenarios(curve)).set_index("Scenario")["PnL"]
    assert pnl["Parallel +100bp"] == pytest.approx(-28.207008, abs=1e-5)
    assert pnl["Steepener"] == pytest.approx(-6.744711, abs=1e-5)
    assert pnl["Flattener"] == pytest.approx(7.898676, abs=1e-5)
    assert pnl["Twist"] == pytest.approx(3.126468, abs=1e-5)


def test_twist_leaves_belly_unchanged(curve):
    shocked = shock_twist(curve)
    belly = (curve.index >= 2) & (curve.index <= 10)
    assert (shocked[belly] == curve[belly]).all()


def test_shocks_do_not_change_input(curve):
    before = curve.copy()
    default_scenarios(curve)
    assert curve.equals(before)
