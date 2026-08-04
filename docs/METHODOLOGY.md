# Methodology

## Research question

Does geopolitical risk affect gold directly, or is its influence transmitted
through real yields, the U.S. dollar, inflation expectations, and general
market stress?

## Analytical design

Daily market and macroeconomic observations are aligned on a business-day
calendar. Prices are converted to log returns. Yield and index factors are
converted to changes or log changes as appropriate. Daily observations are
then aggregated to month-end for factor regressions.

The gold model is:

`GLD return = alpha + real-yield change + dollar return + VIX change + GPR change + breakeven change + S&P 500 return + error`

Each mining-equity model adds the GLD return as the principal commodity factor.
Ordinary least squares is estimated with a Moore-Penrose inverse. The pipeline
reports coefficients, t-statistics, R-squared, observation count, and residual
standard deviation. Results are explanatory associations, not causal proof.

## Intelligence indices

The project deliberately separates supportive conditions from risk:

- **Gold Support Pressure Index:** real-yield decline, dollar weakness,
  geopolitical pressure, market stress, inflation expectations, gold momentum,
  and optional central-bank purchases.
- **Gold Market Risk Index:** gold and miner volatility, drawdown, cross-miner
  dispersion, factor instability, and an optional positioning/supply overlay.

Each component is converted to a trailing percentile from 0 to 100 and combined
using the weights in `config/settings.json`. A missing optional series receives
a neutral value of 50 and is disclosed; it is never silently treated as zero.

## Scenario analysis

Scenarios apply coherent monthly shocks to the fitted factor models. Monte
Carlo simulations perturb each shock and add regression residual uncertainty.
Outputs show the median and 5th/95th percentiles. Scenario results are
conditional model estimates, not forecasts or investment advice.

## Validation boundaries

- Data freshness and coverage are recorded on every run.
- Live mode fails visibly when a required core series is unavailable.
- Auto mode can fall back to deterministic demonstration data.
- Demo results are labeled and must not be presented as live findings.
- No score should be used as a standalone trading signal.

