"""Charts. Each function saves one PNG and returns its path."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def _save(fig, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_curve(curve, asof, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(curve.index, curve.values * 100, marker="o")
    ax.set(xlabel="Maturity (years)", ylabel="Yield (%)", title=f"U.S. Treasury Yield Curve ({asof.date()})")
    ax.grid(True, alpha=0.3)
    return _save(fig, path)


def plot_krd(krd, path):
    fig, ax = plt.subplots(figsize=(9, 4))
    labels = [f"{n:g}" for n in krd["Node (Years)"]]
    ax.bar(labels, krd["Dollar Sensitivity"])
    ax.set(xlabel="Key rate node (years)", ylabel="$ per +1bp", title="Key Rate Dollar Sensitivities")
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, path)


def plot_scenarios(pnl, path, title="Portfolio P&L Under Yield Curve Stress Scenarios"):
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["tab:red" if v < 0 else "tab:green" for v in pnl["PnL"]]
    ax.bar(pnl["Scenario"], pnl["PnL"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(ylabel="P&L ($)", title=title)
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, path)


def plot_loadings(loadings, path):
    fig, ax = plt.subplots(figsize=(9, 4))
    for col in loadings.columns:
        ax.plot(loadings.index, loadings[col], marker="o", label=col)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(xlabel="Maturity", ylabel="Loading", title="PCA Loadings on Daily Yield Changes")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return _save(fig, path)


def plot_explained_variance(ev, path, top=6):
    ev = ev.iloc[:top]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(ev.index, ev.values * 100)
    ax.set(ylabel="Variance explained (%)", title="Explained Variance by Principal Component")
    ax.grid(axis="y", alpha=0.3)
    return _save(fig, path)
