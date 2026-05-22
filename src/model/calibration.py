"""Comparação entre o modelo Dixon-Coles e as odds de mercado.

- Converte odds americanas → probabilidade implícita
- Remove o overround (vig) das casas dividindo pela soma das probs
- Calcula edge (model_prob - market_prob) e Kelly fraction sugerida
- Reporta log-loss e Brier score esperados sob o modelo
"""

from __future__ import annotations


import numpy as np
import pandas as pd

from src.config import DATA_RAW, RESULTS, normalize_team


def american_to_prob(odds: str | int | float) -> float:
    """Converte odds americanas (+500, -150) para probabilidade implícita.
    Aceita também int/float (pandas pode parsear "+500" como 500)."""
    if isinstance(odds, (int, float)):
        value = int(odds)
        if value >= 0:
            return 100.0 / (100.0 + value)
        return -value / (100.0 - value)
    s = str(odds).strip().lstrip("+")
    value = int(s)
    if value >= 0:
        return 100.0 / (100.0 + value)
    return -value / (100.0 - value)


def load_market_probs() -> pd.DataFrame:
    """Carrega odds ESPN e Polymarket, retorna DataFrame com prob de mercado
    normalizada (sem vig)."""
    espn = pd.read_csv(DATA_RAW / "odds_espn_may2026.csv")
    espn["team"] = espn["team"].map(normalize_team)
    espn["espn_raw_prob"] = espn["odds_american"].map(american_to_prob)
    # remove overround: divide pela soma para garantir Σ=1
    espn["espn_prob"] = espn["espn_raw_prob"] / espn["espn_raw_prob"].sum()

    poly = pd.read_csv(DATA_RAW / "odds_polymarket_may2026.csv")
    poly["team"] = poly["team"].map(normalize_team)
    poly["poly_prob"] = poly["implied_prob"] / poly["implied_prob"].sum()

    merged = espn[["team", "espn_raw_prob", "espn_prob"]].merge(
        poly[["team", "poly_prob"]], on="team", how="outer"
    )
    merged["market_prob"] = merged[["espn_prob", "poly_prob"]].mean(axis=1)
    return merged


def compare_to_model() -> pd.DataFrame:
    market = load_market_probs()
    model = pd.read_csv(RESULTS / "world_cup_probabilities.csv")[["team", "P_Champion"]]
    model.columns = ["team", "model_prob"]
    df = market.merge(model, on="team", how="outer").fillna(0.0)
    df["edge"] = df["model_prob"] - df["market_prob"]
    df["edge_ratio"] = np.where(
        df["market_prob"] > 0,
        df["model_prob"] / df["market_prob"],
        np.nan,
    )
    return df.sort_values("model_prob", ascending=False).reset_index(drop=True)


def kelly_fraction(
    model_prob: float, decimal_odds: float, kelly_cap: float = 0.05
) -> float:
    """Kelly fraction = (bp - q) / b, onde b = odds-1, p = prob modelo, q = 1-p.
    Limita a `kelly_cap` (5% por padrão) para evitar volatilidade."""
    if decimal_odds <= 1.0 or model_prob <= 0:
        return 0.0
    b = decimal_odds - 1.0
    q = 1.0 - model_prob
    f = (b * model_prob - q) / b
    return float(max(0.0, min(f, kelly_cap)))


def report() -> pd.DataFrame:
    df = compare_to_model()
    df["overround_espn"] = df["espn_raw_prob"].sum() - 1.0
    overround = df["overround_espn"].iloc[0]
    print(f"Overround ESPN (vig total): {overround * 100:.1f}%")
    print("\nTop 15 — modelo vs mercado (médio):\n")
    show = df.head(15)[
        ["team", "model_prob", "espn_prob", "poly_prob", "market_prob", "edge"]
    ].copy()
    for c in ["model_prob", "espn_prob", "poly_prob", "market_prob"]:
        show[c] = (show[c] * 100).round(2)
    show["edge"] = (show["edge"] * 100).round(2)
    print(show.to_string(index=False))

    print("\nMaiores edges positivos (modelo > mercado, possível valor):")
    pos = df[df["market_prob"] > 0.005].sort_values("edge", ascending=False).head(10)
    pos_show = pos[["team", "model_prob", "market_prob", "edge"]].copy()
    for c in ["model_prob", "market_prob", "edge"]:
        pos_show[c] = (pos_show[c] * 100).round(2)
    print(pos_show.to_string(index=False))

    print("\nMaiores edges negativos (modelo < mercado, modelo cético):")
    neg = df[df["market_prob"] > 0.01].sort_values("edge").head(10)
    neg_show = neg[["team", "model_prob", "market_prob", "edge"]].copy()
    for c in ["model_prob", "market_prob", "edge"]:
        neg_show[c] = (neg_show[c] * 100).round(2)
    print(neg_show.to_string(index=False))

    df.to_csv(RESULTS / "calibration.csv", index=False)
    return df


if __name__ == "__main__":
    report()
