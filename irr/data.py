"""Download daily U.S. Treasury par yield curve rates from home.treasury.gov.

Source: U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates.
No API key is needed. Data is published per calendar year as CSV.
"""
import io
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

from .curve import MATURITY_YEARS

URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve"
    "&field_tdr_date_value={year}&page&_format=csv"
)

# Treasury column name -> our tenor label
COLUMNS = {
    "1 Mo": "1M", "3 Mo": "3M", "6 Mo": "6M", "1 Yr": "1Y", "2 Yr": "2Y", "3 Yr": "3Y",
    "5 Yr": "5Y", "7 Yr": "7Y", "10 Yr": "10Y", "20 Yr": "20Y", "30 Yr": "30Y",
}


def parse_treasury_csv(text: str) -> pd.DataFrame:
    """Turn one Treasury CSV into a date-indexed frame of decimal yields (4.26 -> 0.0426)."""
    raw = pd.read_csv(io.StringIO(text))
    raw["Date"] = pd.to_datetime(raw["Date"], format="%m/%d/%Y")
    df = raw.set_index("Date")[list(COLUMNS)].rename(columns=COLUMNS) / 100
    return df[list(MATURITY_YEARS)]


def download_year(year: int, timeout: float = 30) -> pd.DataFrame:
    req = urllib.request.Request(URL.format(year=year), headers={"User-Agent": "irr-yield-curve/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return parse_treasury_csv(resp.read().decode("utf-8"))


def fetch_treasury_yields(start_year: int = 2018, end_year: int | None = None) -> pd.DataFrame:
    """Download all years from start_year to end_year (default: this year), oldest first.

    Days with any missing tenor are dropped.
    """
    end_year = end_year or date.today().year
    frames = [download_year(y) for y in range(start_year, end_year + 1)]
    yields = pd.concat(frames).sort_index()
    yields = yields[~yields.index.duplicated(keep="last")]
    return yields.dropna()


def load_or_fetch(cache: Path, start_year: int = 2018, refresh: bool = True) -> pd.DataFrame:
    """Download fresh data and save it to `cache`. With refresh=False, reuse the cache if it exists."""
    if not refresh and cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    yields = fetch_treasury_yields(start_year)
    cache.parent.mkdir(parents=True, exist_ok=True)
    yields.to_csv(cache)
    return yields
