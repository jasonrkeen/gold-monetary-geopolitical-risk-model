from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


NAVY = "#17233c"
GOLD = "#c99a2e"
TEAL = "#2d7f7a"
RED = "#b6504b"
GRAY = "#6b7280"


def _style(ax: plt.Axes, title: str, ylabel: str = "") -> None:
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)


def create_charts(
    daily: pd.DataFrame,
    index_history: pd.DataFrame,
    metrics: pd.DataFrame,
    scenario_summary: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    normalized = daily[["GLD", "GDX", "S&P 500"]].dropna()
    normalized = normalized / normalized.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for column, color in zip(normalized.columns, [GOLD, TEAL, NAVY]):
        ax.plot(normalized.index, normalized[column], label=column, color=color, linewidth=1.8)
    _style(ax, "Gold, miners, and broad-market performance", "Start = 100")
    ax.legend(frameon=False, ncol=3)
    fig.tight_layout()
    path = output_dir / "normalized_performance.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)

    returns = np.log(daily[["GLD", "GDX"]]).diff()
    vol = returns.rolling(63).std() * np.sqrt(252) * 100
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(vol.index, vol["GLD"], label="GLD", color=GOLD, linewidth=1.6)
    ax.plot(vol.index, vol["GDX"], label="GDX", color=TEAL, linewidth=1.6)
    _style(ax, "Rolling 63-day annualized volatility", "Percent")
    ax.legend(frameon=False)
    fig.tight_layout()
    path = output_dir / "rolling_volatility.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(index_history.index, index_history.iloc[:, 0], color=GOLD, label=index_history.columns[0])
    ax.plot(index_history.index, index_history.iloc[:, 1], color=RED, label=index_history.columns[1])
    ax.axhspan(65, 100, color=RED, alpha=0.06)
    ax.axhspan(0, 35, color=TEAL, alpha=0.06)
    ax.set_ylim(0, 100)
    _style(ax, "Gold intelligence indices", "Score (0-100)")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    path = output_dir / "intelligence_indices.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)

    betas = metrics[metrics["asset"].isin(["GDX", "Newmont", "Barrick", "Agnico Eagle", "AngloGold Ashanti"])].copy()
    betas = betas.sort_values("gold_beta")
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.barh(betas["asset"], betas["gold_beta"], color=TEAL)
    _style(ax, "Historical sensitivity to GLD daily returns", "Gold beta")
    fig.tight_layout()
    path = output_dir / "gold_betas.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)

    subset = scenario_summary[scenario_summary["asset"].isin(["GLD", "GDX"])].copy()
    pivot = subset.pivot(index="scenario", columns="asset", values="median_return") * 100
    fig, ax = plt.subplots(figsize=(10, 6.2))
    pivot.plot(kind="barh", ax=ax, color=[TEAL, GOLD])
    _style(ax, "Scenario median monthly return", "Percent")
    ax.axvline(0, color=GRAY, linewidth=0.8)
    ax.legend(frameon=False)
    fig.tight_layout()
    path = output_dir / "scenario_impacts.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)

    factor_frame = pd.DataFrame(
        {
            "GLD return": np.log(daily["GLD"]).diff(),
            "Real yield": daily["Real Yield"].diff(),
            "Dollar": np.log(daily["Broad Dollar"]).diff(),
            "VIX": np.log(daily["VIX"]).diff(),
            "GPR": np.log(daily["GPR"].clip(lower=1)).diff(),
            "Breakeven": daily["Breakeven Inflation"].diff(),
        }
    )
    correlations = factor_frame.corr()
    fig, ax = plt.subplots(figsize=(7.5, 6.2))
    image = ax.imshow(correlations, cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_xticks(range(len(correlations)), correlations.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(correlations)), correlations.index)
    for i in range(len(correlations)):
        for j in range(len(correlations)):
            ax.text(j, i, f"{correlations.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("Daily factor correlations", loc="left", fontsize=13, fontweight="bold", color=NAVY)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    path = output_dir / "factor_correlations.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)
    return paths

