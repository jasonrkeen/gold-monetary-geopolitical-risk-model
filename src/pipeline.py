from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from .charts import create_charts
from .config import ROOT, ensure_directories, load_settings
from .indices import build_intelligence_indices
from .loaders import load_all_data, load_optional_central_bank_demand
from .models import fit_factor_models, performance_metrics, regression_table
from .report import build_report
from .scenarios import run_scenarios
from .transform import build_monthly_model_frame, clean_daily_data


@dataclass
class PipelineResult:
    mode: str
    report_path: Path
    score_path: Path
    scenario_path: Path
    manifest_path: Path


def _write_source_register(path: Path) -> None:
    rows = [
        ["Yahoo market prices", "Yahoo Finance", "daily", "public endpoint", "market returns and volatility"],
        ["DFII10", "Federal Reserve via FRED", "daily", "public CSV", "real-yield channel"],
        ["DTWEXBGS", "Federal Reserve via FRED", "daily", "public CSV", "broad-dollar channel"],
        ["VIXCLS", "CBOE via FRED", "daily", "public CSV", "market-stress channel"],
        ["T10YIE", "FRED", "daily", "public CSV", "inflation-expectations channel"],
        ["AI-GPR", "Matteo Iacoviello", "daily", "public CSV", "geopolitical-risk channel"],
        ["Central-bank purchases", "reviewed manual source", "monthly/quarterly", "optional", "official-sector demand"],
        ["Mineral Commodity Summaries", "USGS", "annual", "documented context", "supply-security extension"],
        ["Commitments of Traders", "CFTC", "weekly", "documented extension", "positioning/crowding extension"],
    ]
    pd.DataFrame(rows, columns=["dataset", "provider", "frequency", "access", "model_use"]).to_csv(path, index=False)


def run_pipeline(
    mode: str = "auto",
    start_date: str | None = None,
    end_date: str | None = None,
) -> PipelineResult:
    ensure_directories()
    settings = load_settings()
    start_date = start_date or settings["start_date"]
    end_date = end_date or date.today().isoformat()
    loaded = load_all_data(settings, start_date, end_date, mode)
    daily = clean_daily_data(loaded.data)
    daily.to_csv(ROOT / "data" / "processed" / "market_and_factor_data.csv", index_label="date")

    monthly = build_monthly_model_frame(daily)
    monthly.to_csv(ROOT / "data" / "processed" / "monthly_model_data.csv", index_label="date")
    models = fit_factor_models(monthly)
    regressions = regression_table(models)
    metrics = performance_metrics(daily, float(settings["risk_free_rate"]))
    central_bank = load_optional_central_bank_demand()
    history, current_scores, index_detail = build_intelligence_indices(
        daily,
        settings["support_weights"],
        settings["risk_weights"],
        central_bank,
    )
    scenarios, draws = run_scenarios(
        models,
        runs=int(settings["monte_carlo_runs"]),
        seed=int(settings["random_seed"]),
    )

    table_dir = ROOT / "outputs" / "tables"
    regressions.to_csv(table_dir / "factor_regressions.csv", index=False)
    metrics.to_csv(table_dir / "performance_metrics.csv", index=False)
    history.to_csv(table_dir / "intelligence_index_history.csv", index_label="date")
    current_scores.to_csv(table_dir / "current_intelligence_scores.csv", index=False)
    scenarios.to_csv(table_dir / "scenario_summary.csv", index=False)
    draws.to_csv(table_dir / "scenario_draws_gld_gdx.csv", index=False)
    status_frame = pd.DataFrame(loaded.status)
    status_frame.to_csv(table_dir / "data_status.csv", index=False)
    _write_source_register(table_dir / "source_register.csv")

    components = index_detail["components"]
    components.columns = [f"{group}__{name}" for group, name in components.columns]
    components.to_csv(table_dir / "index_components.csv", index_label="date")

    chart_dir = ROOT / "outputs" / "charts"
    chart_paths = create_charts(daily, history, metrics, scenarios, chart_dir)
    report_path = ROOT / "outputs" / "reports" / "gold_risk_intelligence_report.pdf"
    build_report(
        report_path,
        settings,
        loaded.mode,
        current_scores,
        metrics,
        regressions,
        scenarios,
        status_frame,
        chart_dir,
        index_detail["metadata"],
    )

    manifest = {
        "project": settings["project_name"],
        "model_version": settings["model_version"],
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "requested_mode": mode,
        "effective_mode": loaded.mode,
        "analysis_start": daily.index.min().date().isoformat(),
        "analysis_end": daily.index.max().date().isoformat(),
        "observations": int(len(daily)),
        "monte_carlo_runs": int(settings["monte_carlo_runs"]),
        "charts": [str(path.relative_to(ROOT)) for path in chart_paths],
        "report": str(report_path.relative_to(ROOT)),
        "limitations": index_detail["metadata"],
    }
    manifest_path = ROOT / "outputs" / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return PipelineResult(
        mode=loaded.mode,
        report_path=report_path,
        score_path=table_dir / "current_intelligence_scores.csv",
        scenario_path=table_dir / "scenario_summary.csv",
        manifest_path=manifest_path,
    )

