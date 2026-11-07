# Interest Rate Risk & Yield Curve Stress Testing

Measures how a Treasury bond portfolio's value changes when the yield curve moves. Uses daily U.S. Treasury yields from 2018 to 2026.

The analysis covers:

1. **Pricing**: values each bond off the current yield curve.
2. **DV01**: dollar change in portfolio value for a +1bp parallel move.
3. **Key rate duration (KRD)**: moves one curve point at a time to show which maturities hold the risk.
4. **Stress scenarios**: parallel +100bp, steepener, flattener, and twist.
5. **PCA**: finds the three main ways the curve moves (level, slope, curvature) from history, then prices a 2-sigma move in each one.

## Run it

```bash
pip install -r requirements.txt
python run.py                         # latest date in the data
python run.py --date 2024-06-28       # any other date
python run.py --pc-std 3 --out results
python -m pytest                      # 12 tests
```

Tables (CSV) and charts (PNG) go to `outputs/`.

## Project layout

```
irr/
  curve.py       load yields, map tenors (1M..30Y) to years
  pricing.py     bond and portfolio pricing
  risk.py        DV01 and key rate durations
  scenarios.py   curve shocks and scenario P&L
  pca.py         PCA on daily yield changes, PCA shocks
  plots.py       charts
run.py           runs everything from the command line
tests/           pytest checks
```

## Method

**Data.** Daily par yields for 11 tenors: 1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y (decimal, e.g. 0.0426 = 4.26%).

**Portfolio.** Four Treasuries with $100 face each: 2Y (3.5%), 5Y (3.7%), 10Y (4.0%), 30Y (4.5%). Annual coupons.

**Pricing.** Each cash flow is discounted at the curve yield for its date, using linear interpolation between tenors and continuous compounding:

$$P = \sum_{t=1}^{T} CF_t \, e^{-y_t t}$$

**DV01 and KRD.** DV01 is the value change for a +1bp shift of the whole curve. KRD bumps one tenor by +1bp and leaves the others alone. The sum of the 11 key rate changes should equal DV01 (check below).

**Stress scenarios.**

| Scenario | Short end | Long end |
|---|---|---|
| Parallel +100bp | +100bp | +100bp |
| Steepener | −50bp (≤5Y) | +50bp (>5Y) |
| Flattener | +50bp (≤5Y) | −50bp (>5Y) |
| Twist | +25bp (<2Y), 0 for 2Y–10Y | −25bp (>10Y) |

**PCA.** PCA runs on standardized daily yield changes. Signs are fixed so PC1 is "all rates up" and PC2 is "long end up, short end down", so results do not flip between runs. Each shock is 2 standard deviations of that PC's daily score, converted back to yield changes.

## Results (as of 2026-01-22)

| Metric | Value |
|---|---|
| Portfolio value | $391.79 |
| DV01 | −$0.3034 |
| Sum of key rate DV01s | −$0.3034 (difference 2.5e-5) |
| Largest key rate exposures | 10Y (30%), 30Y (29%), 5Y (17%) |

| Scenario | P&L |
|---|---|
| Parallel +100bp | −$28.21 |
| Steepener | −$6.74 |
| Twist | +$3.13 |
| Flattener | +$7.90 |

| PCA factor | Variance explained | 2σ daily P&L |
|---|---|---|
| PC1 (Level) | 65.4% | −$3.05 |
| PC2 (Slope) | 14.3% | −$0.86 |
| PC3 (Curvature) | 9.0% | +$0.23 |

The first three factors explain 88.7% of daily curve moves. Level is the main risk; the portfolio loses when rates rise and when the curve steepens.

![Key rate durations](outputs/key_rate_durations.png)
![Stress scenarios](outputs/stress_scenarios.png)
![PCA loadings](outputs/pca_loadings.png)

## Limits

- Coupons are annual. Real Treasuries pay semiannually.
- Par yields are used as zero rates (no bootstrapping).
- Daily changes, so PCA shocks are 1-day moves.
