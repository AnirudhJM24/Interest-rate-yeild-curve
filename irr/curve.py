"""Tenor mapping and yield curve helpers."""
import pandas as pd

MATURITY_YEARS = {
    "1M": 1 / 12,
    "3M": 3 / 12,
    "6M": 6 / 12,
    "1Y": 1,
    "2Y": 2,
    "3Y": 3,
    "5Y": 5,
    "7Y": 7,
    "10Y": 10,
    "20Y": 20,
    "30Y": 30,
}



def to_years(curve_by_label: pd.Series) -> pd.Series:
    """Convert a curve indexed by tenor label ('2Y') into one indexed by years (2.0)."""
    return curve_by_label.rename(index=MATURITY_YEARS).sort_index().astype(float)


def curve_on(yields: pd.DataFrame, date=None) -> tuple[pd.Timestamp, pd.Series]:
    """Return (as-of date, curve in years). Defaults to the latest date.

    If the date is not a trading day, the last trading day before it is used.
    """
    asof = yields.index[-1] if date is None else yields.index[yields.index <= pd.Timestamp(date)][-1]
    return asof, to_years(yields.loc[asof])
