from __future__ import annotations

import numpy as np
import pandas as pd

from .models import OLSResult


SCENARIOS: dict[str, dict] = {
    "Baseline": {
        "Real-yield change": 0.00,
        "Dollar return": 0.00,
        "VIX change": 0.00,
        "GPR change": 0.00,
        "Breakeven change": 0.00,
        "S&P 500 return": 0.00,
        "gold_overlay": 0.00,
        "miner_overlay": 0.00,
    },
    "Real-Yield Decline": {
        "Real-yield change": -0.50,
        "Dollar return": -0.03,
        "VIX change": 0.10,
        "GPR change": 0.05,
        "Breakeven change": 0.10,
        "S&P 500 return": 0.02,
        "gold_overlay": 0.00,
        "miner_overlay": 0.00,
    },
    "Dollar Strength Shock": {
        "Real-yield change": 0.25,
        "Dollar return": 0.07,
        "VIX change": 0.20,
        "GPR change": 0.05,
        "Breakeven change": -0.10,
        "S&P 500 return": -0.04,
        "gold_overlay": 0.00,
        "miner_overlay": 0.00,
    },
    "Global Risk-Off": {
        "Real-yield change": -0.35,
        "Dollar return": 0.02,
        "VIX change": 0.80,
        "GPR change": 0.50,
        "Breakeven change": -0.10,
        "S&P 500 return": -0.12,
        "gold_overlay": 0.00,
        "miner_overlay": 0.00,
    },
    "Central-Bank Accumulation": {
        "Real-yield change": -0.10,
        "Dollar return": -0.01,
        "VIX change": 0.05,
        "GPR change": 0.10,
        "Breakeven change": 0.05,
        "S&P 500 return": 0.00,
        "gold_overlay": 0.04,
        "miner_overlay": 0.02,
    },
    "Mining Supply Disruption": {
        "Real-yield change": 0.00,
        "Dollar return": 0.00,
        "VIX change": 0.20,
        "GPR change": 0.25,
        "Breakeven change": 0.10,
        "S&P 500 return": -0.03,
        "gold_overlay": 0.03,
        "miner_overlay": -0.02,
    },
    "Geopolitical Inflation Escalation": {
        "Real-yield change": 0.25,
        "Dollar return": 0.03,
        "VIX change": 0.50,
        "GPR change": 0.75,
        "Breakeven change": 0.40,
        "S&P 500 return": -0.08,
        "gold_overlay": 0.02,
        "miner_overlay": -0.01,
    },
    "Monetary Normalization": {
        "Real-yield change": 0.50,
        "Dollar return": 0.04,
        "VIX change": -0.30,
        "GPR change": -0.30,
        "Breakeven change": -0.20,
        "S&P 500 return": 0.05,
        "gold_overlay": 0.00,
        "miner_overlay": 0.00,
    },
}


def _linear_prediction(model: OLSResult, values: dict[str, float]) -> float:
    prediction = float(model.coefficients.get("Intercept", 0.0))
    for factor, coefficient in model.coefficients.items():
        if factor != "Intercept":
            prediction += float(coefficient) * float(values.get(factor, 0.0))
    return prediction


def run_scenarios(
    models: dict[str, OLSResult], runs: int = 5000, seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    summary_rows = []
    draw_rows = []
    gold_model = models["GLD"]
    assets = list(models)

    for scenario_name, shocks in SCENARIOS.items():
        shock_factors = {key: value for key, value in shocks.items() if key in gold_model.coefficients}
        gold_base = _linear_prediction(gold_model, shock_factors) + shocks["gold_overlay"]
        gold_scale = max(gold_model.residual_std, 0.005)
        gold_draws = rng.normal(gold_base, gold_scale, runs)

        for asset in assets:
            if asset == "GLD":
                asset_draws = gold_draws
            else:
                model = models[asset]
                beta_gold = float(model.coefficients.get("GLD return", 0.0))
                non_gold_values = {
                    "S&P 500 return": shocks["S&P 500 return"],
                    "Dollar return": shocks["Dollar return"],
                    "Real-yield change": shocks["Real-yield change"],
                    "GPR change": shocks["GPR change"],
                }
                base = _linear_prediction(model, non_gold_values)
                base -= float(model.coefficients.get("GLD return", 0.0)) * 0.0
                asset_draws = (
                    base
                    + beta_gold * gold_draws
                    + shocks["miner_overlay"]
                    + rng.normal(0, max(model.residual_std, 0.008), runs)
                )
            summary_rows.append(
                {
                    "scenario": scenario_name,
                    "asset": asset,
                    "median_return": float(np.median(asset_draws)),
                    "p05_return": float(np.quantile(asset_draws, 0.05)),
                    "p95_return": float(np.quantile(asset_draws, 0.95)),
                    "probability_positive": float((asset_draws > 0).mean()),
                }
            )
            if asset in {"GLD", "GDX"}:
                draw_rows.extend(
                    {
                        "scenario": scenario_name,
                        "asset": asset,
                        "run": int(i + 1),
                        "return": float(value),
                    }
                    for i, value in enumerate(asset_draws)
                )
    return pd.DataFrame(summary_rows), pd.DataFrame(draw_rows)

