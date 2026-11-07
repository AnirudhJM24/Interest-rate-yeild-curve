"""Deterministic yield curve stress scenarios. All shocks are in basis points."""
import pandas as pd

from .pricing import portfolio_value
from .risk import BP


def shock_parallel(curve: pd.Series, bp: float) -> pd.Series:
    return curve + bp * BP


def shock_two_segment(curve: pd.Series, short_bp: float, long_bp: float, split_year: float = 5) -> pd.Series:
    """Nodes <= split_year move by short_bp, nodes > split_year move by long_bp."""
    shocked = curve.copy()
    shocked[shocked.index <= split_year] += short_bp * BP
    shocked[shocked.index > split_year] += long_bp * BP
    return shocked


def shock_steepener(curve, short_bp=-50, long_bp=50, split_year=5):
    return shock_two_segment(curve, short_bp, long_bp, split_year)


def shock_flattener(curve, short_bp=50, long_bp=-50, split_year=5):
    return shock_two_segment(curve, short_bp, long_bp, split_year)


def shock_twist(curve, short_bp=25, mid_bp=0, long_bp=-25, mid_range=(2, 10)):
    """Short (< mid_range[0]), middle (inside mid_range), and long (> mid_range[1]) move separately."""
    lo, hi = mid_range
    shocked = curve.copy()
    shocked[shocked.index < lo] += short_bp * BP
    shocked[(shocked.index >= lo) & (shocked.index <= hi)] += mid_bp * BP
    shocked[shocked.index > hi] += long_bp * BP
    return shocked


def default_scenarios(curve: pd.Series) -> dict[str, pd.Series]:
    return {
        "Parallel +100bp": shock_parallel(curve, 100),
        "Steepener": shock_steepener(curve),
        "Flattener": shock_flattener(curve),
        "Twist": shock_twist(curve),
    }


def scenario_pnl(portfolio: pd.DataFrame, curve: pd.Series, scenarios: dict[str, pd.Series]) -> pd.DataFrame:
    """Full revaluation P&L for each shocked curve."""
    base = portfolio_value(portfolio, curve)
    rows = []
    for name, shocked in scenarios.items():
        value = portfolio_value(portfolio, shocked)
        rows.append({"Scenario": name, "Portfolio Value": value, "PnL": value - base})
    return pd.DataFrame(rows).sort_values("PnL").reset_index(drop=True)
