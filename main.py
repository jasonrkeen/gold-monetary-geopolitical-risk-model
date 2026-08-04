from __future__ import annotations

import argparse

from src.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Gold Monetary, Geopolitical & Supply Risk Intelligence Model."
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "live", "demo"],
        default="auto",
        help="auto attempts live data and falls back to labeled demo data",
    )
    parser.add_argument("--start", default=None, help="analysis start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="analysis end date (YYYY-MM-DD)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_pipeline(mode=args.mode, start_date=args.start, end_date=args.end)
    print("=" * 72)
    print("Gold Monetary, Geopolitical & Supply Risk Intelligence Model")
    print("=" * 72)
    print(f"Data mode: {result.mode.upper()}")
    print(f"Report: {result.report_path}")
    print(f"Scores: {result.score_path}")
    print(f"Scenarios: {result.scenario_path}")
    print(f"Manifest: {result.manifest_path}")


if __name__ == "__main__":
    main()

