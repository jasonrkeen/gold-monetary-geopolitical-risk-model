# Copilot instructions: Gold Monetary, Geopolitical & Supply Risk Intelligence Model

## Purpose
Quantitative gold risk intelligence model integrating monetary conditions, geopolitical pressure, market stress, mining equities, Monte Carlo scenarios, PDF reporting, and Streamlit.

## Tech stack
- Python; dependencies in `requirements.txt`
- Key libraries: `numpy`, `pandas`, `matplotlib`, `reportlab`, `streamlit`

## Folder structure
- `.github/` (1 files)
- `config/` (1 files)
- `data/` (2 files)
- `docs/` (2 files)
- `outputs/` (7 files)
- `src/` (10 files)
- `tests/` (5 files)
- `.env.example`
- `CHANGELOG.md`
- `CITATION.cff`
- `CONTRIBUTING.md`
- `README.md`
- `app.py`
- `main.py`
- `requirements.txt`

## Setup, run, test
Commands documented in README.md (referenced files exist):
```bash
python -m venv .venv
pip install -r requirements.txt
python main.py --mode auto
streamlit run app.py
python main.py --mode live
python main.py --mode demo
python -m unittest discover -s tests -v
```
- Tests: 5 Python test file(s) under `tests/`; framework appears to be unittest. Add/update tests with any logic change.
- CI workflows exist in `.github/workflows/`; keep them passing.

## Conventions observed
- Functions use type hints; keep annotating new code.
- Uses `dataclasses` for structured config/results.
- Config lives in: `src/config.py`; avoid hardcoding parameters elsewhere.
- Random seeds are set for reproducibility (Monte Carlo/simulation); keep seeded, deterministic runs.
- Credentials/API keys come from environment variables (see `.env.example`); never hardcode them.
- Raw data (`data/raw/`) is gitignored; download/fetch it via the pipeline, do not commit it.
- Public data sources referenced: FRED.
- Write paths relative to the repo root (no absolute local paths).

## Output artifacts
- Generated outputs go to: `outputs/charts/`, `outputs/reports/`
- A PDF report is produced with `reportlab`; keep it in sync with model changes.
- Streamlit dashboard: `app.py` (run with `streamlit run <file>`).
- Charts are generated with matplotlib.

## Guardrails
- Never commit secrets, API keys, tokens, or `.env` files.
- Do not commit large raw datasets or binaries; keep data fetched or documented with its source.
- Keep analysis source-backed: cite data sources and assumptions; label scenario/forecast outputs as model estimates, not facts.
- Preserve reproducibility: no unseeded randomness, no hidden manual steps.
