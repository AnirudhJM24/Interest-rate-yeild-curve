"""Load Treasury yield data and build a yield curve indexed by maturity in years."""
from pathlib import Path

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


def load_yields(csv_path: str | Path) -> pd.DataFrame:
    """Read daily yields (decimal) with dates as the index and tenor labels as columns."""
    yields = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    missing = set(MATURITY_YEARS) - set(yields.columns)
    if missing:
        raise ValueError(f"CSV is missing tenor columns: {sorted(missing)}")
    return yields[list(MATURITY_YEARS)].sort_index()


def to_years(curve_by_label: pd.Series) -> pd.Series:
    """Convert a curve indexed by tenor label ('2Y') into one indexed by years (2.0)."""
    return curve_by_label.rename(index=MATURITY_YEARS).sort_index().astype(float)


def curve_on(yields: pd.DataFrame, date=None) -> tuple[pd.Timestamp, pd.Series]:
    """Return (as-of date, curve in years) for a date. Defaults to the latest date."""
    asof = yields.index[-1] if date is None else pd.Timestamp(date)
    return asof, to_years(yields.loc[asof])
