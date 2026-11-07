import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from irr.curve import MATURITY_YEARS, to_years  # noqa: E402
from irr.pricing import sample_portfolio  # noqa: E402

TENORS = list(MATURITY_YEARS)
YEARS = np.array(list(MATURITY_YEARS.values()))


@pytest.fixture(scope="session")
def yields():
    """Synthetic daily yields built from level, slope and curvature moves (no network needed)."""
    rng = np.random.default_rng(0)
    n = 1500
    level = np.ones_like(YEARS)
    slope = np.log1p(YEARS) - np.log1p(YEARS).mean()
    curv = -(np.log1p(YEARS) - 1.5) ** 2 + 1
    moves = (
        rng.normal(0, 6e-4, (n, 1)) * level
        + rng.normal(0, 3e-4, (n, 1)) * slope
        + rng.normal(0, 1.5e-4, (n, 1)) * curv
        + rng.normal(0, 3e-5, (n, len(YEARS)))
    )
    start = 0.03 + 0.005 * np.log1p(YEARS)
    dates = pd.bdate_range("2019-01-01", periods=n)
    return pd.DataFrame(start + moves.cumsum(axis=0), index=dates, columns=TENORS)


@pytest.fixture(scope="session")
def curve():
    """A fixed upward-sloping curve indexed by years."""
    return to_years(pd.Series(0.03 + 0.005 * np.log1p(YEARS), index=TENORS))


@pytest.fixture
def portfolio():
    return sample_portfolio()
