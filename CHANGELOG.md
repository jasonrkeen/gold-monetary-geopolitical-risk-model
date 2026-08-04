# Changelog

All notable project changes are documented here.

## [0.1.1] - 2026-08-04

### Added

- Live public-data connectors for market, monetary, volatility, and
  geopolitical series.
- Separate Gold Support Pressure and Gold Market Risk indices.
- Monthly OLS transmission models and 5,000-run scenario simulations.
- Streamlit dashboard and seven-page executive PDF report.
- Cross-platform PDF font discovery and fallback tests.
- Windows and Linux continuous integration on Python 3.12 and 3.14.

### Fixed

- Aligned daily sources on a market-aware observation calendar.
- Escaped the S&P 500 label in ReportLab narrative text.
- Replaced Streamlit's retired `use_container_width` argument.

### Governance

- Preserved explicit live, auto, and demo mode labeling.
- Assigned disclosed neutral scores to missing optional series.
- Recorded run dates, data status, limitations, and model version in every
  manifest.

## [0.1.0] - 2026-08-03

- Initial analytical model, dashboard, reporting pipeline, and documentation.
