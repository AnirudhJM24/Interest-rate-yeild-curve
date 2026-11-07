"""Bond and portfolio pricing off a zero curve."""
import numpy as np
import pandas as pd


def price_bond(face: float, coupon: float, maturity: float, curve: pd.Series) -> float:
    """Price an annual-coupon bond.

    Each cash flow is discounted with the curve yield at its time, linearly
    interpolated between curve nodes, using continuous compounding: exp(-y * t).
    """
    times = np.arange(1, int(maturity) + 1, dtype=float)
    cashflows = np.full(len(times), face * coupon)
    cashflows[-1] += face
    y = np.interp(times, curve.index.values, curve.values)
    return float(np.sum(cashflows * np.exp(-y * times)))


def price_portfolio(portfolio: pd.DataFrame, curve: pd.Series) -> pd.Series:
    """Price every bond in the portfolio. Returns one price per row."""
    return portfolio.apply(
        lambda r: price_bond(r.Face, r.Coupon, r.Maturity, curve), axis=1
    )


def portfolio_value(portfolio: pd.DataFrame, curve: pd.Series) -> float:
    return float(price_portfolio(portfolio, curve).sum())


def sample_portfolio() -> pd.DataFrame:
    """The four-bond Treasury portfolio used in the analysis."""
    return pd.DataFrame(
        {
            "Bond": ["UST_2Y", "UST_5Y", "UST_10Y", "UST_30Y"],
            "Maturity": [2, 5, 10, 30],
            "Coupon": [0.035, 0.037, 0.040, 0.045],
            "Face": [100, 100, 100, 100],
        }
    )
