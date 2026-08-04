from __future__ import annotations

import io
import json
import math
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .config import ROOT


YAHOO_CHART = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
AI_GPR_CSV = "https://www.matteoiacoviello.com/ai_gpr_files/ai_gpr_data_daily.csv"


@dataclass
class LoadResult:
    data: pd.DataFrame
    status: list[dict]
    mode: str


def _download(url: str, attempts: int = 3, timeout: int = 45) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 gold-risk-intelligence-research/0.1",
            "Accept": "text/csv,application/json,*/*",
        },
    )
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except Exception as exc:  # network errors vary by platform
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Download failed after {attempts} attempts: {url}") from last_error


def _epoch(value: str) -> int:
    parsed = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


def load_yahoo_price(symbol: str, start_date: str, end_date: str) -> pd.Series:
    params = urllib.parse.urlencode(
        {
            "period1": _epoch(start_date),
            "period2": _epoch(end_date) + 86400,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        }
    )
    url = YAHOO_CHART.format(symbol=urllib.parse.quote(symbol, safe="")) + "?" + params
    payload = json.loads(_download(url).decode("utf-8"))
    result = payload.get("chart", {}).get("result")
    if not result:
        error = payload.get("chart", {}).get("error")
        raise RuntimeError(f"Yahoo returned no data for {symbol}: {error}")
    item = result[0]
    timestamps = item.get("timestamp", [])
    indicators = item.get("indicators", {})
    adjusted = indicators.get("adjclose", [{}])[0].get("adjclose")
    if adjusted is None:
        adjusted = indicators.get("quote", [{}])[0].get("close", [])
    series = pd.Series(
        adjusted,
        index=pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None).normalize(),
        name=symbol,
        dtype="float64",
    )
    return series.dropna().sort_index()


def load_fred_series(series_id: str) -> pd.Series:
    raw = _download(FRED_CSV.format(series=urllib.parse.quote(series_id)))
    frame = pd.read_csv(io.BytesIO(raw))
    date_column = "observation_date" if "observation_date" in frame else frame.columns[0]
    value_column = series_id if series_id in frame else frame.columns[-1]
    frame[date_column] = pd.to_datetime(frame[date_column], errors="coerce")
    values = pd.to_numeric(frame[value_column], errors="coerce")
    return pd.Series(values.values, index=frame[date_column], name=series_id).dropna().sort_index()


def load_ai_gpr() -> pd.Series:
    raw = _download(AI_GPR_CSV)
    frame = pd.read_csv(io.BytesIO(raw), usecols=["Date", "GPR_AI"])
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame["GPR_AI"] = pd.to_numeric(frame["GPR_AI"], errors="coerce")
    return frame.dropna().set_index("Date")["GPR_AI"].sort_index()


def load_optional_central_bank_demand(path: Path | None = None) -> pd.Series | None:
    path = path or ROOT / "data" / "manual" / "central_bank_demand.csv"
    if not path.exists() or path.stat().st_size == 0:
        return None
    frame = pd.read_csv(path)
    if frame.empty or not {"date", "net_purchases_tonnes"}.issubset(frame.columns):
        return None
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["net_purchases_tonnes"] = pd.to_numeric(
        frame["net_purchases_tonnes"], errors="coerce"
    )
    series = frame.dropna(subset=["date", "net_purchases_tonnes"]).set_index("date")[
        "net_purchases_tonnes"
    ]
    return series.sort_index() if not series.empty else None


def _status_row(name: str, source: str, series: pd.Series, status: str = "live") -> dict:
    return {
        "dataset": name,
        "source": source,
        "status": status,
        "observations": int(series.notna().sum()),
        "first_date": series.dropna().index.min().date().isoformat(),
        "latest_date": series.dropna().index.max().date().isoformat(),
    }


def load_live_data(settings: dict, start_date: str, end_date: str) -> LoadResult:
    columns: list[pd.Series] = []
    status: list[dict] = []
    for name, symbol in settings["assets"].items():
        series = load_yahoo_price(symbol, start_date, end_date).rename(name)
        columns.append(series)
        status.append(_status_row(name, "Yahoo Finance", series))

    for name, series_id in settings["fred_series"].items():
        series = load_fred_series(series_id).rename(name)
        series = series.loc[pd.Timestamp(start_date) : pd.Timestamp(end_date)]
        columns.append(series)
        status.append(_status_row(name, f"FRED:{series_id}", series))

    gpr = load_ai_gpr().loc[pd.Timestamp(start_date) : pd.Timestamp(end_date)].rename("GPR")
    columns.append(gpr)
    status.append(_status_row("GPR", "Iacoviello AI-GPR", gpr))

    frame = pd.concat(columns, axis=1).sort_index()
    return LoadResult(frame, status, "live")


def generate_demo_data(settings: dict, start_date: str, end_date: str) -> LoadResult:
    """Create correlated deterministic data for offline validation, never live findings."""
    seed = int(settings.get("random_seed", 42))
    rng = np.random.default_rng(seed)
    index = pd.bdate_range(start_date, end_date)
    n = len(index)
    if n < 260:
        raise ValueError("Demo mode requires at least one year of business days")

    real_yield = np.clip(0.7 + np.cumsum(rng.normal(0, 0.025, n)), -1.5, 3.5)
    dollar_r = rng.normal(0.00005, 0.003, n)
    dollar = 105 * np.exp(np.cumsum(dollar_r))
    gpr = np.maximum(15, 100 + rng.normal(0, 18, n))
    shock_days = rng.choice(np.arange(30, n), size=max(8, n // 250), replace=False)
    gpr[shock_days] += rng.uniform(80, 220, len(shock_days))
    gpr = pd.Series(gpr, index=index).rolling(5, min_periods=1).mean().values
    vix = np.clip(17 + 0.045 * (gpr - 100) + rng.normal(0, 3.2, n), 9, 65)
    breakeven = np.clip(2.2 + np.cumsum(rng.normal(0, 0.009, n)), 1.0, 4.0)
    spy_r = 0.00035 - 0.00002 * (vix - 17) + rng.normal(0, 0.010, n)

    real_change = np.r_[0, np.diff(real_yield)]
    gpr_change = np.r_[0, np.diff(np.log(gpr))]
    vix_change = np.r_[0, np.diff(np.log(vix))]
    gold_r = (
        0.00018
        - 0.008 * real_change
        - 0.38 * dollar_r
        + 0.025 * vix_change
        + 0.018 * gpr_change
        + rng.normal(0, 0.0075, n)
    )
    gold = 115 * np.exp(np.cumsum(gold_r))
    futures = 118 * np.exp(np.cumsum(gold_r + rng.normal(0, 0.0012, n)))

    data: dict[str, np.ndarray] = {
        "Gold Futures": futures,
        "GLD": gold,
        "S&P 500": 200 * np.exp(np.cumsum(spy_r)),
        "Real Yield": real_yield,
        "Broad Dollar": dollar,
        "VIX": vix,
        "Breakeven Inflation": breakeven,
        "GPR": gpr,
    }
    miner_specs = {
        "GDX": (1.25, 0.35, 0.012),
        "Newmont": (1.10, 0.30, 0.014),
        "Barrick": (1.18, 0.25, 0.015),
        "Agnico Eagle": (1.05, 0.32, 0.013),
        "AngloGold Ashanti": (1.32, 0.22, 0.017),
    }
    for name, (gold_beta, market_beta, noise) in miner_specs.items():
        returns = gold_beta * gold_r + market_beta * spy_r + rng.normal(0, noise, n)
        data[name] = 35 * np.exp(np.cumsum(returns))

    frame = pd.DataFrame(data, index=index)
    ordered = list(settings["assets"].keys()) + list(settings["fred_series"].keys()) + ["GPR"]
    frame = frame[ordered]
    status = []
    for column in frame:
        status.append(_status_row(column, "Deterministic demo generator", frame[column], "demo"))
    return LoadResult(frame, status, "demo")


def load_all_data(settings: dict, start_date: str, end_date: str, mode: str) -> LoadResult:
    if mode == "demo":
        return generate_demo_data(settings, start_date, end_date)
    try:
        return load_live_data(settings, start_date, end_date)
    except Exception:
        if mode == "live":
            raise
        result = generate_demo_data(settings, start_date, end_date)
        result.status.append(
            {
                "dataset": "live_pipeline",
                "source": "network connectors",
                "status": "fallback",
                "observations": 0,
                "first_date": "",
                "latest_date": "",
            }
        )
        return result

