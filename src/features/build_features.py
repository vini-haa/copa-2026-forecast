"""Prepara o dataset de treino e ajusta o modelo Dixon-Coles."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DATA_RAW, DATA_PROCESSED, normalize_team

CUTOFF_DATE = "2022-01-01"
WC2026_DATE = "2026-06-11"


def load_matches() -> pd.DataFrame:
    df = pd.read_csv(DATA_RAW / "results.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["home_team"] = df["home_team"].map(normalize_team)
    df["away_team"] = df["away_team"].map(normalize_team)
    return df


def training_set(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra partidas com placar conhecido, desde CUTOFF_DATE até início da Copa."""
    mask = (
        (df["date"] >= CUTOFF_DATE)
        & (df["date"] < WC2026_DATE)
        & df["home_score"].notna()
        & df["away_score"].notna()
    )
    # excluir amistosos antigos pode até ajudar, mas mantemos tudo para volume
    return df.loc[mask].reset_index(drop=True)


if __name__ == "__main__":
    df = load_matches()
    train = training_set(df)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    train.to_csv(DATA_PROCESSED / "training_matches.csv", index=False)
    print(f"Total partidas de treino (>= {CUTOFF_DATE}): {len(train):,}")
    print(
        f"Times únicos: {train['home_team'].nunique() + train['away_team'].nunique()}"
    )
    print(train.tail(5).to_string())
