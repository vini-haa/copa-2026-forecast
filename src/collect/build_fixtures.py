"""Extrai os 72 jogos da fase de grupos da Copa 2026 do dataset bruto."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DATA_RAW, DATA_PROCESSED, HOST_COUNTRIES, normalize_team

WC2026 = "2026-06"


def build() -> pd.DataFrame:
    df = pd.read_csv(DATA_RAW / "results.csv")
    df["home_team"] = df["home_team"].map(normalize_team)
    df["away_team"] = df["away_team"].map(normalize_team)
    mask = (df["tournament"] == "FIFA World Cup") & df["date"].str.startswith(WC2026)
    fixtures = df.loc[
        mask, ["date", "home_team", "away_team", "city", "country", "neutral"]
    ].copy()
    fixtures["host_match"] = fixtures.apply(
        lambda r: (
            (r["home_team"] in HOST_COUNTRIES)
            and (r["country"] in HOST_COUNTRIES)
            and (r["home_team"] == _country_to_team(r["country"]))
        ),
        axis=1,
    )
    fixtures.reset_index(drop=True, inplace=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    fixtures.to_csv(DATA_PROCESSED / "wc2026_fixtures.csv", index=False)
    return fixtures


def _country_to_team(country: str) -> str:
    return country  # nomes batem


if __name__ == "__main__":
    fx = build()
    print(f"Fixtures Copa 2026: {len(fx)}")
    print(fx.head(10).to_string())
