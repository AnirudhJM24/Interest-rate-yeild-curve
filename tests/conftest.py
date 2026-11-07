import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from irr.curve import curve_on, load_yields  # noqa: E402
from irr.pricing import sample_portfolio  # noqa: E402


@pytest.fixture(scope="session")
def yields():
    return load_yields(ROOT / "treasury_yields.csv")


@pytest.fixture(scope="session")
def curve(yields):
    return curve_on(yields)[1]


@pytest.fixture
def portfolio():
    return sample_portfolio()
