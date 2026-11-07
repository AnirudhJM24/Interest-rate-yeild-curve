from irr.scenarios import default_scenarios, scenario_pnl, shock_twist


def test_scenario_signs_for_long_only_portfolio(portfolio, curve):
    pnl = scenario_pnl(portfolio, curve, default_scenarios(curve)).set_index("Scenario")["PnL"]
    assert pnl["Parallel +100bp"] < pnl["Steepener"] < 0 < pnl["Flattener"]


def test_twist_leaves_belly_unchanged(curve):
    shocked = shock_twist(curve)
    belly = (curve.index >= 2) & (curve.index <= 10)
    assert (shocked[belly] == curve[belly]).all()


def test_shocks_do_not_change_input(curve):
    before = curve.copy()
    default_scenarios(curve)
    assert curve.equals(before)
