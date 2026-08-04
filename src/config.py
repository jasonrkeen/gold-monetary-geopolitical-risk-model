from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_settings() -> dict:
    with (ROOT / "config" / "settings.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def ensure_directories() -> None:
    for relative in (
        "data/raw",
        "data/processed",
        "outputs/charts",
        "outputs/tables",
        "outputs/reports",
    ):
        (ROOT / relative).mkdir(parents=True, exist_ok=True)

