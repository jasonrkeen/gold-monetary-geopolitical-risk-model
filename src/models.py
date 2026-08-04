from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .transform import drawdown


@dataclass
class OLSResult:
    dependent: str
    coefficients: pd.Series
    standard_errors: pd.Series
    t_statistics: pd.Series
    r_squared: float
    adjusted_r_squared: float
    observations: int
    residual_std: float
    condition_number: float


def fit_ols(frame: pd.DataFrame, dependent: str, predictors: list[str]) -> OLSResult:
    data = frame[[dependent, *predictors]].dropna()
    if len(data) <= len(predictors) + 2:
        raise ValueError(f"Insufficient observations for {dependent}: {len(data)}")
    y = data[dependent].to_numpy(dtype=float)
    x_values = data[predictors].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(data)), x_values])
    names = ["Intercept", *predictors]
    xtx_inverse = np.linalg.pinv(x.T @ x)
    beta = xtx_inverse @ x.T @ y
    fitted = x @ beta
    residuals = y - fitted
    n, k = x.shape
    degrees = max(1, n - k)
    sse = float(residuals.T @ residuals)
    sigma2 = sse / degrees
    standard_errors = np.sqrt(np.clip(np.diag(xtx_inverse) * sigma2, 0, None))
    with np.errstate(divide="ignore", invalid="ignore"):
        t_stats = np.divide(beta, standard_errors, out=np.zeros_like(beta), where=standard_errors > 0)
    total = float(((y - y.mean()) ** 2).sum())
    r_squared = 1.0 - sse / total if total > 0 else 0.0
    adjusted = 1.0 - (1.0 - r_squared) * (n - 1) / degrees
    return OLSResult(
        dependent=dependent,
        coefficients=pd.Series(beta, index=names),
        standard_errors=pd.Series(standard_errors, index=names),
        t_statistics=pd.Series(t_stats, index=names),
        r_squared=float(r_squared),
        adjusted_r_squared=float(adjusted),
        observations=n,
        residual_std=float(np.sqrt(sigma2)),
        condition_number=float(np.linalg.cond(x)),
    )


def fit_factor_models(monthly: pd.DataFrame) -> dict[str, OLSResult]:
    gold_predictors = [
        "Real-yield change",
        "Dollar return",
        "VIX change",
        "GPR change",
        "Breakeven change",
        "S&P 500 return",
    ]
    results = {"GLD": fit_ols(monthly, "GLD return", gold_predictors)}
    miner_predictors = [
        "GLD return",
        "S&P 500 return",
        "Dollar return",
        "Real-yield change",
        "GPR change",
    ]
    for asset in ("GDX", "Newmont", "Barrick", "Agnico Eagle", "AngloGold Ashanti"):
        results[asset] = fit_ols(monthly, f"{asset} return", miner_predictors)
    return results


def regression_table(results: dict[str, OLSResult]) -> pd.DataFrame:
    rows = []
    for model, result in results.items():
        for factor in result.coefficients.index:
            rows.append(
                {
                    "model": model,
                    "dependent": result.dependent,
                    "factor": factor,
                    "coefficient": result.coefficients[factor],
                    "standard_error": result.standard_errors[factor],
                    "t_statistic": result.t_statistics[factor],
                    "r_squared": result.r_squared,
                    "adjusted_r_squared": result.adjusted_r_squared,
                    "observations": result.observations,
                    "residual_std": result.residual_std,
                    "condition_number": result.condition_number,
                }
            )
    return pd.DataFrame(rows)


def performance_metrics(daily: pd.DataFrame, risk_free_rate: float) -> pd.DataFrame:
    rows = []
    price_columns = [
        "Gold Futures",
        "GLD",
        "GDX",
        "Newmont",
        "Barrick",
        "Agnico Eagle",
        "AngloGold Ashanti",
        "S&P 500",
    ]
    gold_returns = np.log(daily["GLD"]).diff().dropna()
    for asset in price_columns:
        prices = daily[asset].dropna()
        returns = np.log(prices).diff().dropna()
        years = max((prices.index[-1] - prices.index[0]).days / 365.25, 1 / 252)
        cagr = (prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1
        volatility = returns.std(ddof=1) * np.sqrt(252)
        sharpe = (returns.mean() * 252 - risk_free_rate) / volatility if volatility else np.nan
        aligned = pd.concat([returns, gold_returns], axis=1).dropna()
        beta = np.nan
        if len(aligned) > 2 and aligned.iloc[:, 1].var() > 0:
            beta = aligned.cov().iloc[0, 1] / aligned.iloc[:, 1].var()
        rows.append(
            {
                "asset": asset,
                "start_date": prices.index[0].date().isoformat(),
                "end_date": prices.index[-1].date().isoformat(),
                "total_return": prices.iloc[-1] / prices.iloc[0] - 1,
                "cagr": cagr,
                "annualized_volatility": volatility,
                "sharpe_ratio": sharpe,
                "max_drawdown": drawdown(prices).min(),
                "gold_beta": beta,
                "observations": len(prices),
            }
        )
    return pd.DataFrame(rows)

