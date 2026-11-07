"""DV01 and key rate duration."""
import pandas as pd

from .pricing import portfolio_value

BP = 1e-4


def dv01(portfolio: pd.DataFrame, curve: pd.Series, bp: float = 1.0) -> float:
    """Dollar change in portfolio value for a parallel +bp move in the curve."""
    return portfolio_value(portfolio, curve + bp * BP) - portfolio_value(portfolio, curve)


def key_rate_report(portfolio: pd.DataFrame, curve: pd.Series, bp: float = 1.0) -> pd.DataFrame:
    """Bump each curve node by +bp alone and record the dollar change and KRD."""
    base = portfolio_value(portfolio, curve)
    rows = []
    for node in curve.index:
        bumped = curve.copy()
        bumped.loc[node] += bp * BP
        rows.append({"Node (Years)": node, "Dollar Sensitivity": portfolio_value(portfolio, bumped) - base})

    report = pd.DataFrame(rows)
    sens = report["Dollar Sensitivity"]
    report["Abs % Contribution"] = sens.abs() / sens.abs().sum()
    report["KRD"] = -sens / (base * bp * BP)
    return report
