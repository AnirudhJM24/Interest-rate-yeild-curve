"""Run the full interest rate risk analysis and write tables and charts to an output folder.

Usage:
    python run.py
    python run.py --csv treasury_yields.csv --date 2025-06-30 --out outputs
"""
import argparse
from pathlib import Path

import pandas as pd

from irr import plots
from irr.curve import curve_on, load_yields
from irr.pca import fit_pca, pc_shocked_curves
from irr.pricing import price_portfolio, sample_portfolio
from irr.risk import dv01, key_rate_report
from irr.scenarios import default_scenarios, scenario_pnl


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", default=Path(__file__).parent / "treasury_yields.csv", type=Path)
    p.add_argument("--date", default=None, help="As-of date (YYYY-MM-DD). Default: latest in file.")
    p.add_argument("--out", default="outputs", type=Path)
    p.add_argument("--pc-std", default=2.0, type=float, help="Size of PCA shocks in std devs.")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 120)

    yields = load_yields(args.csv)
    asof, curve = curve_on(yields, args.date)

    portfolio = sample_portfolio()
    portfolio["Price"] = price_portfolio(portfolio, curve)
    base = portfolio["Price"].sum()

    port_dv01 = dv01(portfolio, curve)
    krd = key_rate_report(portfolio, curve)
    stress = scenario_pnl(portfolio, curve, default_scenarios(curve))

    model = fit_pca(yields.loc[:asof])
    pca_pnl = scenario_pnl(portfolio, curve, pc_shocked_curves(model, yields.loc[asof], args.pc_std))

    print(f"As-of date: {asof.date()}\n")
    print(portfolio.to_string(index=False), "\n")
    print(f"Portfolio value:       {base:,.4f}")
    print(f"DV01 (parallel +1bp):  {port_dv01:,.6f}")
    print(f"Sum of key rate DV01s: {krd['Dollar Sensitivity'].sum():,.6f}")
    print(f"Difference:            {port_dv01 - krd['Dollar Sensitivity'].sum():.2e}\n")
    print("Key rate durations:\n", krd.round(6).to_string(index=False), "\n")
    print("Stress scenarios:\n", stress.round(4).to_string(index=False), "\n")
    ev = model.explained_variance
    print(f"PCA explained variance: PC1 {ev['PC1']:.1%}, PC2 {ev['PC2']:.1%}, PC3 {ev['PC3']:.1%} "
          f"(top 3: {ev.iloc[:3].sum():.1%})")
    print(f"PCA {args.pc_std:g}-sigma shocks:\n", pca_pnl.round(4).to_string(index=False))

    portfolio.to_csv(args.out / "portfolio.csv", index=False)
    krd.to_csv(args.out / "key_rate_durations.csv", index=False)
    stress.to_csv(args.out / "stress_scenarios.csv", index=False)
    pca_pnl.to_csv(args.out / "pca_scenarios.csv", index=False)
    model.loadings.to_csv(args.out / "pca_loadings.csv")

    plots.plot_curve(curve, asof, args.out / "yield_curve.png")
    plots.plot_krd(krd, args.out / "key_rate_durations.png")
    plots.plot_scenarios(stress, args.out / "stress_scenarios.png")
    plots.plot_scenarios(pca_pnl, args.out / "pca_scenarios.png", title=f"Portfolio P&L Under {args.pc_std:g}σ PCA Shocks")
    plots.plot_loadings(model.loadings, args.out / "pca_loadings.png")
    plots.plot_explained_variance(ev, args.out / "pca_explained_variance.png")
    print(f"\nTables and charts saved to {args.out.resolve()}")


if __name__ == "__main__":
    main()
