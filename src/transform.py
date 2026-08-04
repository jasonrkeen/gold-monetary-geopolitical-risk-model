from __future__ import annotations

import numpy as np
import pandas as pd


PRICE_COLUMNS = [
    "Gold Futures",
    "GLD",
    "GDX",
    "Newmont",
    "Barrick",
    "Agnico Eagle",
    "AngloGold Ashanti",
    "S&P 500",
]


def clean_daily_data(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy().sort_index()
    result = result[~result.index.duplicated(keep="last")]
    result = result.replace([np.inf, -np.inf], np.nan)
    # Use the core gold proxy as the master trading calendar. This prevents
    # weekend-only macro/GPR rows from creating artificial neutral score days.
    if "GLD" in result:
        result = result.loc[result["GLD"].notna()].copy()
    macro = [column for column in result.columns if column not in PRICE_COLUMNS]
    result[macro] = result[macro].ffill(limit=10)
    return result


def build_daily_features(frame: pd.DataFrame) -> pd.DataFrame:
    clean = clean_daily_data(frame)
    features = clean.copy()
    for column in PRICE_COLUMNS:
        if column in clean:
            features[f"{column} return"] = np.log(clean[column]).diff()
    features["Dollar return"] = np.log(clean["Broad Dollar"]).diff()
    features["VIX change"] = np.log(clean["VIX"]).diff()
    features["GPR change"] = np.log(clean["GPR"].clip(lower=1)).diff()
    features["Real-yield change"] = clean["Real Yield"].diff()
    features["Breakeven change"] = clean["Breakeven Inflation"].diff()
    return features


def build_monthly_model_frame(daily: pd.DataFrame) -> pd.DataFrame:
    month_end = daily.resample("ME").last()
    monthly = pd.DataFrame(index=month_end.index)
    for column in PRICE_COLUMNS:
        if column in month_end:
            monthly[f"{column} return"] = np.log(month_end[column]).diff()
    monthly["Dollar return"] = np.log(month_end["Broad Dollar"]).diff()
    monthly["VIX change"] = np.log(month_end["VIX"]).diff()
    monthly["GPR change"] = np.log(month_end["GPR"].clip(lower=1)).diff()
    monthly["Real-yield change"] = month_end["Real Yield"].diff()
    monthly["Breakeven change"] = month_end["Breakeven Inflation"].diff()
    return monthly.replace([np.inf, -np.inf], np.nan)


def drawdown(price: pd.Series) -> pd.Series:
    return price / price.cummax() - 1.0
