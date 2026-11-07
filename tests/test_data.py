import os

import pandas as pd
import pytest

from irr.curve import MATURITY_YEARS, curve_on
from irr.data import parse_treasury_csv

SAMPLE = '''Date,"1 Mo","1.5 Month","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"
12/31/2025,3.74,3.75,3.67,3.67,3.63,3.59,3.48,3.47,3.55,3.73,3.94,4.18,4.79,4.84
12/30/2025,3.65,3.71,3.65,3.65,3.63,3.59,3.47,3.45,3.50,3.68,3.89,4.14,4.76,4.81
'''


def test_parse_converts_percent_to_decimal_and_keeps_our_tenors():
    df = parse_treasury_csv(SAMPLE)
    assert list(df.columns) == list(MATURITY_YEARS)
    assert df.loc["2025-12-31", "10Y"] == pytest.approx(0.0418)
    assert df.loc["2025-12-30", "1M"] == pytest.approx(0.0365)


def test_curve_on_uses_last_trading_day(yields):
    saturday = pd.Timestamp("2019-03-09")
    asof, _ = curve_on(yields, saturday)
    assert asof == pd.Timestamp("2019-03-08")


@pytest.mark.skipif(not os.getenv("IRR_NETWORK_TESTS"), reason="set IRR_NETWORK_TESTS=1 to hit home.treasury.gov")
def test_live_download():
    from irr.data import download_year
    df = download_year(2024)
    assert len(df) > 240 and df.notna().all().all()
