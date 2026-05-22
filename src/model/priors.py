"""Constrói priors para ataque/defesa do Dixon-Coles a partir de Elo + market value.

Lógica:
- Elo é uma medida estatística baseada em performance real e cobre todas as
  seleções (244 disponíveis). É o sinal principal.
- Market value (Transfermarkt) cobre só ~48 e é uma medida de qualidade
  individual. É usado como modulador onde disponível.
- O prior é normalizado para a mesma escala dos parâmetros estimados pelo DC.
"""

from __future__ import annotations


import numpy as np
import pandas as pd

from src.config import DATA_RAW, normalize_team


def load_priors() -> pd.DataFrame:
    elo = pd.read_csv(DATA_RAW / "elo_ratings_2026.csv")
    elo["team"] = elo["team"].map(normalize_team)
    mv = pd.read_csv(DATA_RAW / "market_value_2026.csv")
    mv["team"] = mv["team"].map(normalize_team)
    return elo.merge(mv[["team", "market_value_gbp_m"]], on="team", how="left")


def compute_prior_strength(df: pd.DataFrame) -> pd.DataFrame:
    """Gera coluna `prior_strength` ∈ ℝ com escala compatível com attack/defense
    estimados (range típico [-1.5, 1.5])."""
    df = df.copy()
    # Elo normalizado: Z-score, depois escala para amplitude ~3
    elo_z = (df["elo"] - df["elo"].mean()) / df["elo"].std()
    # Market value (log) — só onde disponível
    mv = df["market_value_gbp_m"].copy()
    log_mv = np.log1p(mv)
    log_mv_z = (log_mv - log_mv.mean(skipna=True)) / log_mv.std(skipna=True)
    # Combinar: 70% Elo + 30% market value (quando disponível); senão só Elo
    combined = np.where(
        mv.notna(),
        0.7 * elo_z + 0.3 * log_mv_z,
        elo_z,
    )
    df["prior_strength"] = combined * 0.4  # ajusta amplitude para ~[-1.5, 1.5]
    return df[["team", "elo", "market_value_gbp_m", "prior_strength"]]


def prior_attack_defense(prior_strength: float) -> tuple[float, float]:
    """Divide a força total em prior de ataque e defesa.
    Convenção do DC: attack alto = bom, defense baixo (negativo) = bom.
    Times fortes têm ataque + |defesa| alto. Dividimos 50/50."""
    attack = prior_strength * 0.5
    defense = -prior_strength * 0.5
    return attack, defense


if __name__ == "__main__":
    df = load_priors()
    df = compute_prior_strength(df)
    print("Top 15 priors:")
    print(
        df.sort_values("prior_strength", ascending=False)
        .head(15)
        .to_string(index=False)
    )
    print("\nBottom 10 (entre seleções da Copa):")
    from src.config import all_teams

    wc = all_teams(include_playoff=False)
    df_wc = df[df["team"].isin(wc)]
    print(df_wc.sort_values("prior_strength").head(10).to_string(index=False))
