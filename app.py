from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "outputs" / "tables"
CHARTS = ROOT / "outputs" / "charts"
REPORT = ROOT / "outputs" / "reports" / "gold_risk_intelligence_report.pdf"

st.set_page_config(page_title="Gold Risk Intelligence", page_icon="◉", layout="wide")
st.title("Gold Monetary, Geopolitical & Supply Risk Intelligence")
st.caption("Decision support for gold, mining equities, and macro-geopolitical transmission")

scores_path = TABLES / "current_intelligence_scores.csv"
if not scores_path.exists():
    st.warning("Run `python main.py --mode auto` before opening the dashboard.")
    st.stop()

scores = pd.read_csv(scores_path)
columns = st.columns(len(scores))
for column, (_, row) in zip(columns, scores.iterrows()):
    column.metric(row["index"], f"{row['score']:.1f}/100", row["level"])

tab_overview, tab_factors, tab_scenarios, tab_governance = st.tabs(
    ["Executive overview", "Factor transmission", "Scenarios", "Governance"]
)

with tab_overview:
    left, right = st.columns(2)
    left.image(str(CHARTS / "intelligence_indices.png"), width="stretch")
    right.image(str(CHARTS / "normalized_performance.png"), width="stretch")
    st.image(str(CHARTS / "rolling_volatility.png"), width="stretch")

with tab_factors:
    st.image(str(CHARTS / "factor_correlations.png"), width="stretch")
    st.image(str(CHARTS / "gold_betas.png"), width="stretch")
    regressions = pd.read_csv(TABLES / "factor_regressions.csv")
    selected_model = st.selectbox("Model", regressions["model"].unique())
    st.dataframe(
        regressions.loc[regressions["model"] == selected_model],
        width="stretch",
        hide_index=True,
    )

with tab_scenarios:
    st.image(str(CHARTS / "scenario_impacts.png"), width="stretch")
    scenarios = pd.read_csv(TABLES / "scenario_summary.csv")
    selected_scenario = st.selectbox("Scenario", scenarios["scenario"].unique())
    view = scenarios.loc[scenarios["scenario"] == selected_scenario].copy()
    for column in ["median_return", "p05_return", "p95_return", "probability_positive"]:
        view[column] = view[column].map(lambda value: f"{value:.1%}")
    st.dataframe(view, width="stretch", hide_index=True)

with tab_governance:
    st.subheader("Data status")
    st.dataframe(pd.read_csv(TABLES / "data_status.csv"), width="stretch", hide_index=True)
    st.subheader("Source register")
    st.dataframe(pd.read_csv(TABLES / "source_register.csv"), width="stretch", hide_index=True)
    st.info(
        "Support and risk are separate measures. Missing optional central-bank, positioning, "
        "or supply series are assigned a disclosed neutral value—not silently treated as zero."
    )

if REPORT.exists():
    st.download_button(
        "Download executive report",
        data=REPORT.read_bytes(),
        file_name=REPORT.name,
        mime="application/pdf",
    )

st.caption("Research and portfolio demonstration only. Not investment advice.")
