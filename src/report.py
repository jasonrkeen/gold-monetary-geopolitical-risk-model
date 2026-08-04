from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#17233c")
GOLD = colors.HexColor("#c99a2e")
LIGHT = colors.HexColor("#f3f4f6")
GRAY = colors.HexColor("#5b6472")


def _font_candidates() -> list[tuple[Path, Path]]:
    """Return common sans-serif font pairs without assuming an operating system."""
    project_root = Path(__file__).resolve().parents[1]
    windows_root = Path(os.environ.get("WINDIR", "C:/Windows"))
    return [
        (
            project_root / "assets" / "fonts" / "DejaVuSans.ttf",
            project_root / "assets" / "fonts" / "DejaVuSans-Bold.ttf",
        ),
        (windows_root / "Fonts" / "arial.ttf", windows_root / "Fonts" / "arialbd.ttf"),
        (windows_root / "Fonts" / "segoeui.ttf", windows_root / "Fonts" / "segoeuib.ttf"),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        ),
    ]


def _register_report_fonts() -> tuple[str, str]:
    """Register the first available font pair, or use ReportLab core fonts."""
    regular_name = "ReportSans"
    bold_name = "ReportSans-Bold"
    for regular_path, bold_path in _font_candidates():
        if not (regular_path.is_file() and bold_path.is_file()):
            continue
        try:
            pdfmetrics.registerFont(TTFont(regular_name, str(regular_path)))
            pdfmetrics.registerFont(TTFont(bold_name, str(bold_path)))
            pdfmetrics.registerFontFamily(
                regular_name,
                normal=regular_name,
                bold=bold_name,
                italic=regular_name,
                boldItalic=bold_name,
            )
            return regular_name, bold_name
        except Exception:
            continue
    return "Helvetica", "Helvetica-Bold"


REGULAR_FONT, BOLD_FONT = _register_report_fonts()


def _table(data: list[list], widths: list[float] | None = None) -> Table:
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
                ("FONTNAME", (0, 1), (-1, -1), REGULAR_FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d1d5db"))
    canvas.line(0.65 * inch, 0.55 * inch, 7.85 * inch, 0.55 * inch)
    canvas.setFont(REGULAR_FONT, 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(0.65 * inch, 0.36 * inch, "Gold Monetary, Geopolitical & Supply Risk Intelligence Model")
    canvas.drawRightString(7.85 * inch, 0.36 * inch, f"Page {document.page}")
    canvas.restoreState()


def build_report(
    output_path: Path,
    settings: dict,
    mode: str,
    current_scores: pd.DataFrame,
    metrics: pd.DataFrame,
    regressions: pd.DataFrame,
    scenarios: pd.DataFrame,
    data_status: pd.DataFrame,
    chart_dir: Path,
    limitations: dict,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName=BOLD_FONT,
            fontSize=23,
            leading=27,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=15,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading1"],
            fontName=BOLD_FONT,
            fontSize=15,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=8.5,
            leading=11,
            textColor=GRAY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Callout",
            parent=styles["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=11,
            leading=15,
            textColor=NAVY,
            borderColor=GOLD,
            borderWidth=1,
            borderPadding=9,
            backColor=colors.HexColor("#fffaf0"),
        )
    )
    for style_name in ("BodyText", "Heading2"):
        styles[style_name].fontName = REGULAR_FONT
    styles["Heading2"].fontName = BOLD_FONT

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.72 * inch,
        title=settings["project_name"],
        author="Jason Keen",
    )
    story = []
    story.append(Spacer(1, 0.45 * inch))
    story.append(Paragraph("GOLD", ParagraphStyle("Kicker", parent=styles["Heading2"], fontName=BOLD_FONT, textColor=GOLD, fontSize=13)))
    story.append(Paragraph(settings["project_name"], styles["ReportTitle"]))
    story.append(
        Paragraph(
            "A quantitative decision-support study of monetary transmission, geopolitical pressure, market stress, and mining-equity sensitivity.",
            styles["Heading2"],
        )
    )
    story.append(Spacer(1, 0.25 * inch))
    as_of = current_scores["as_of_date"].iloc[0]
    story.append(
        _table(
            [
                ["Model version", "Data mode", "Analysis date"],
                [settings["model_version"], mode.upper(), as_of],
            ],
            [2.25 * inch, 2.25 * inch, 2.25 * inch],
        )
    )
    story.append(Spacer(1, 0.35 * inch))
    mode_note = (
        "This report uses live public data."
        if mode == "live"
        else "DEMONSTRATION DATA: results validate the pipeline and must not be presented as live market findings."
    )
    story.append(Paragraph(mode_note, styles["Callout"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Prepared as an analytical portfolio project by Jason Keen", styles["Small"]))
    story.append(PageBreak())

    story.append(Paragraph("Executive assessment", styles["Section"]))
    score_data = [["Index", "Score", "Level", "As of"]]
    for _, row in current_scores.iterrows():
        score_data.append([row["index"], f"{row['score']:.1f}", row["level"], row["as_of_date"]])
    story.append(_table(score_data, [3.3 * inch, 1.0 * inch, 1.2 * inch, 1.3 * inch]))
    story.append(Spacer(1, 0.2 * inch))
    support = current_scores.loc[current_scores["index"].str.contains("Support"), "score"].iloc[0]
    risk = current_scores.loc[current_scores["index"].str.contains("Risk"), "score"].iloc[0]
    story.append(
        Paragraph(
            f"Current conditions produce a Gold Support Pressure score of <b>{support:.1f}</b> and a Gold Market Risk score of <b>{risk:.1f}</b>. The separation is intentional: conditions that support gold prices can coexist with elevated volatility, crowding, or miner-specific risk.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))
    image_path = chart_dir / "intelligence_indices.png"
    if image_path.exists():
        story.append(Image(str(image_path), width=7.0 * inch, height=3.78 * inch))

    story.append(Paragraph("Research design", styles["Section"]))
    story.append(
        Paragraph(
            "The core test asks whether geopolitical pressure has an independent association with gold returns after controlling for real yields, the broad U.S. dollar, VIX, inflation expectations, and the S&amp;P 500. A second set of models estimates how strongly the gold-mining ETF and major producers transmit changes in gold and the broader market.",
            styles["BodyText"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Market performance", styles["Section"]))
    path = chart_dir / "normalized_performance.png"
    if path.exists():
        story.append(Image(str(path), width=7.0 * inch, height=3.78 * inch))
    selected = metrics[metrics["asset"].isin(["GLD", "GDX", "Newmont", "Barrick", "Agnico Eagle", "AngloGold Ashanti"])]
    metric_data = [["Asset", "CAGR", "Volatility", "Sharpe", "Max drawdown", "Gold beta"]]
    for _, row in selected.iterrows():
        metric_data.append(
            [
                row["asset"],
                f"{row['cagr']:.1%}",
                f"{row['annualized_volatility']:.1%}",
                f"{row['sharpe_ratio']:.2f}",
                f"{row['max_drawdown']:.1%}",
                f"{row['gold_beta']:.2f}",
            ]
        )
    story.append(_table(metric_data, [1.35 * inch, 0.8 * inch, 0.95 * inch, 0.7 * inch, 1.05 * inch, 0.8 * inch]))
    story.append(PageBreak())

    story.append(Paragraph("Factor transmission", styles["Section"]))
    gold_model = regressions[(regressions["model"] == "GLD") & (regressions["factor"] != "Intercept")]
    regression_data = [["Factor", "Coefficient", "t-statistic", "R-squared", "N"]]
    for _, row in gold_model.iterrows():
        regression_data.append(
            [
                row["factor"],
                f"{row['coefficient']:.4f}",
                f"{row['t_statistic']:.2f}",
                f"{row['r_squared']:.3f}",
                int(row["observations"]),
            ]
        )
    story.append(_table(regression_data, [2.3 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 0.7 * inch]))
    story.append(Spacer(1, 0.18 * inch))
    story.append(
        Paragraph(
            "Coefficient signs and t-statistics describe conditional historical relationships. They do not establish that a factor caused a gold-price movement. Collinearity, regime changes, and omitted variables remain material limitations.",
            styles["Small"],
        )
    )
    path = chart_dir / "factor_correlations.png"
    if path.exists():
        story.append(Image(str(path), width=5.8 * inch, height=4.8 * inch))
    story.append(PageBreak())

    story.append(Paragraph("Mining-equity sensitivity", styles["Section"]))
    path = chart_dir / "gold_betas.png"
    if path.exists():
        story.append(Image(str(path), width=7.0 * inch, height=4.2 * inch))
    story.append(
        Paragraph(
            "A gold beta above one indicates that the equity historically moved more than GLD in the same direction on a daily basis. Company performance also reflects operating costs, jurisdiction, capital allocation, currency exposure, hedging, reserve quality, and market beta.",
            styles["Small"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Scenario intelligence", styles["Section"]))
    path = chart_dir / "scenario_impacts.png"
    if path.exists():
        story.append(Image(str(path), width=7.0 * inch, height=4.35 * inch))
    gld_scenarios = scenarios[scenarios["asset"] == "GLD"].sort_values("median_return", ascending=False)
    scenario_data = [["Scenario", "Median", "5th pct.", "95th pct.", "P(positive)"]]
    for _, row in gld_scenarios.iterrows():
        scenario_data.append(
            [
                row["scenario"],
                f"{row['median_return']:.1%}",
                f"{row['p05_return']:.1%}",
                f"{row['p95_return']:.1%}",
                f"{row['probability_positive']:.0%}",
            ]
        )
    story.append(_table(scenario_data, [2.55 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 1.0 * inch]))
    story.append(PageBreak())

    story.append(Paragraph("Data governance and limitations", styles["Section"]))
    status_data = [["Dataset", "Status", "Observations", "Latest date"]]
    for _, row in data_status.iterrows():
        status_data.append([row["dataset"], row["status"], int(row["observations"]), row["latest_date"]])
    story.append(_table(status_data, [2.7 * inch, 1.2 * inch, 1.2 * inch, 1.4 * inch]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Known limitations", styles["Heading2"]))
    limitation_text = [
        "Optional central-bank demand is neutral when no reviewed, reusable time series is supplied.",
        "CFTC positioning and country-level supply concentration are documented extensions and are neutral in version 0.1.1.",
        "Yahoo price data can be revised and is not an institutional market-data feed.",
        "The factor models assume stable linear relationships and may fail during structural breaks.",
        "Scenario intervals reflect model and residual uncertainty, not the full range of possible outcomes.",
        "This research is not investment advice and should not be used as a standalone trading signal.",
    ]
    for item in limitation_text:
        story.append(Paragraph(f"- {item}", styles["BodyText"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(f"Central-bank component: {limitations['central_bank_component']}", styles["Small"]))
    story.append(Paragraph(f"Positioning/supply component: {limitations['positioning_supply_component']}", styles["Small"]))

    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return output_path
