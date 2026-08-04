from __future__ import annotations

import numpy as np
import pandas as pd

from .transform import drawdown


def rolling_percentile(series: pd.Series, window: int = 756, minimum: int = 126) -> pd.Series:
    def rank_last(values: np.ndarray) -> float:
        valid = values[np.isfinite(values)]
        if len(valid) == 0:
            return np.nan
        return float((valid <= valid[-1]).mean() * 100.0)

    return series.rolling(window, min_periods=minimum).apply(rank_last, raw=True)


def _central_bank_component(index: pd.DatetimeIndex, series: pd.Series | None) -> tuple[pd.Series, str]:
    if series is None or len(series.dropna()) < 4:
        return pd.Series(50.0, index=index), "neutral fallback: no reviewed series"
    expanded = series.reindex(index.union(series.index)).sort_index().ffill().reindex(index)
    score = rolling_percentile(expanded, window=min(40, max(8, len(series))), minimum=4)
    return score.fillna(50.0), "manual reviewed series"


def build_intelligence_indices(
    daily: pd.DataFrame,
    support_weights: dict[str, float],
    risk_weights: dict[str, float],
    central_bank_demand: pd.Series | None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    gold_return = np.log(daily["GLD"]).diff()
    gdx_return = np.log(daily["GDX"]).diff()
    miner_names = ["Newmont", "Barrick", "Agnico Eagle", "AngloGold Ashanti"]
    miner_returns = np.log(daily[miner_names]).diff()

    support_components = pd.DataFrame(index=daily.index)
    support_components["Real-yield decline"] = rolling_percentile(-daily["Real Yield"].diff(63))
    support_components["Dollar weakness"] = rolling_percentile(-np.log(daily["Broad Dollar"]).diff(63))
    support_components["Geopolitical pressure"] = rolling_percentile(
        daily["GPR"].rolling(21, min_periods=5).mean()
    )
    support_components["Market stress"] = rolling_percentile(
        daily["VIX"].rolling(21, min_periods=5).mean()
    )
    support_components["Inflation expectations"] = rolling_percentile(
        daily["Breakeven Inflation"].diff(63)
    )
    support_components["Gold momentum"] = rolling_percentile(np.log(daily["GLD"]).diff(63))
    cb_score, cb_status = _central_bank_component(daily.index, central_bank_demand)
    support_components["Central-bank demand"] = cb_score

    risk_components = pd.DataFrame(index=daily.index)
    risk_components["Gold volatility"] = rolling_percentile(
        gold_return.rolling(21).std() * np.sqrt(252)
    )
    risk_components["Miner volatility"] = rolling_percentile(
        gdx_return.rolling(21).std() * np.sqrt(252)
    )
    risk_components["Gold drawdown"] = rolling_percentile(-drawdown(daily["GLD"]))
    risk_components["Cross-miner dispersion"] = rolling_percentile(
        miner_returns.rolling(21).std().mean(axis=1) * np.sqrt(252)
    )
    factor_z = pd.concat(
        [
            daily["Real Yield"].diff(21),
            np.log(daily["Broad Dollar"]).diff(21),
            np.log(daily["VIX"]).diff(21),
            np.log(daily["GPR"].clip(lower=1)).diff(21),
        ],
        axis=1,
    )
    z = (factor_z - factor_z.rolling(252, min_periods=126).mean()) / factor_z.rolling(
        252, min_periods=126
    ).std()
    risk_components["Factor instability"] = rolling_percentile(z.abs().mean(axis=1))
    risk_components["Positioning and supply"] = 50.0

    support_score = sum(
        support_components[name].fillna(50.0) * weight for name, weight in support_weights.items()
    )
    risk_score = sum(
        risk_components[name].fillna(50.0) * weight for name, weight in risk_weights.items()
    )
    history = pd.DataFrame(
        {
            "Gold Support Pressure Index": support_score.clip(0, 100),
            "Gold Market Risk Index": risk_score.clip(0, 100),
        }
    )
    latest_date = history.dropna(how="all").index.max()
    current_rows = []
    for index_name in history.columns:
        value = float(history.loc[latest_date, index_name])
        level = "Low" if value < 35 else "Moderate" if value < 65 else "High"
        current_rows.append(
            {"as_of_date": latest_date.date().isoformat(), "index": index_name, "score": value, "level": level}
        )
    metadata = {
        "central_bank_component": cb_status,
        "positioning_supply_component": "neutral fallback: extension not yet connected",
    }
    components = pd.concat(
        {"support": support_components, "risk": risk_components}, axis=1
    )
    return history, pd.DataFrame(current_rows), {"metadata": metadata, "components": components}

