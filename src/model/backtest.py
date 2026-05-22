"""Validação out-of-sample do modelo Dixon-Coles.

Treina com dados até CUTOFF_TRAIN, prevê partidas em [CUTOFF_TRAIN, TODAY]
e compara contra os resultados reais.

Métricas:
- Brier score (multi-classe: home/draw/away). Menor = melhor. Range [0, 2].
- Log-loss. Menor = melhor.
- Accuracy (predição = classe de maior probabilidade).

Baselines comparados:
- Modelo Dixon-Coles bayesiano (com prior)
- Modelo Dixon-Coles MLE puro (sem prior)
- Predição uniforme (1/3, 1/3, 1/3) — chão teórico
- Elo puro: vitória da equipe com maior Elo
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DATA_RAW, RESULTS, normalize_team
from src.features.build_features import load_matches
from src.model.dixon_coles import DixonColesParams, fit, score_matrix
from src.model.priors import compute_prior_strength, load_priors, prior_attack_defense


CUTOFF_TRAIN = "2025-12-31"
TRAIN_START = "2022-01-01"


def split_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    train_mask = (
        (df["date"] >= TRAIN_START)
        & (df["date"] <= CUTOFF_TRAIN)
        & df["home_score"].notna()
        & df["away_score"].notna()
    )
    test_mask = (
        (df["date"] > CUTOFF_TRAIN)
        & (df["date"] <= pd.Timestamp("today"))
        & df["home_score"].notna()
        & df["away_score"].notna()
    )
    return df.loc[train_mask].reset_index(drop=True), df.loc[test_mask].reset_index(
        drop=True
    )


def predict_match(
    params: DixonColesParams,
    home: str,
    away: str,
    neutral: bool,
) -> tuple[float, float, float]:
    """Retorna (P_home_win, P_draw, P_away_win)."""
    lam_h, lam_a = params.predict_lambdas(home, away, neutral)
    mat = score_matrix(lam_h, lam_a, params.rho)
    p_home = float(np.tril(mat, -1).sum())
    p_draw = float(np.trace(mat))
    p_away = float(np.triu(mat, 1).sum())
    return p_home, p_draw, p_away


def predict_elo(
    elo: dict[str, float], home: str, away: str, neutral: bool
) -> tuple[float, float, float]:
    """Baseline simples: Elo + vantagem de mando ~70 pontos, sem empate explícito."""
    if home not in elo or away not in elo:
        return 1 / 3, 1 / 3, 1 / 3
    ha = 0 if neutral else 70
    diff = (elo[home] + ha) - elo[away]
    p_home = 1.0 / (1.0 + 10 ** (-diff / 400))
    # alocar prob de empate proporcional à proximidade
    p_draw = 0.25 * np.exp(-((diff / 200) ** 2))
    p_home_adj = (1 - p_draw) * p_home
    p_away_adj = (1 - p_draw) * (1 - p_home)
    return p_home_adj, p_draw, p_away_adj


def result_class(home_goals: int, away_goals: int) -> int:
    if home_goals > away_goals:
        return 0  # home win
    if home_goals == away_goals:
        return 1  # draw
    return 2  # away win


def brier_score(probs: np.ndarray, actuals: np.ndarray) -> float:
    """Brier multi-classe: Σ_i Σ_k (p_ik - y_ik)². Médio."""
    one_hot = np.eye(3)[actuals]
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))


def log_loss(probs: np.ndarray, actuals: np.ndarray) -> float:
    probs = np.clip(probs, 1e-10, 1.0)
    return float(-np.mean(np.log(probs[np.arange(len(actuals)), actuals])))


def accuracy(probs: np.ndarray, actuals: np.ndarray) -> float:
    return float(np.mean(np.argmax(probs, axis=1) == actuals))


def evaluate(probs: np.ndarray, actuals: np.ndarray, label: str) -> dict:
    return {
        "model": label,
        "n_matches": len(actuals),
        "brier": brier_score(probs, actuals),
        "log_loss": log_loss(probs, actuals),
        "accuracy": accuracy(probs, actuals),
    }


def run_backtest(
    prior_lambdas: list[float] = [0.0, 4.0, 8.0, 12.0, 20.0],
) -> pd.DataFrame:
    df = load_matches()
    train, test = split_data(df)
    print(f"Treino: {len(train):,} partidas até {CUTOFF_TRAIN}")
    print(f"Teste: {len(test):,} partidas após {CUTOFF_TRAIN}")
    if len(test) == 0:
        raise SystemExit("Sem partidas no período de teste.")

    # carrega priors uma vez
    priors_df = compute_prior_strength(load_priors())
    priors = {
        row["team"]: prior_attack_defense(row["prior_strength"])
        for _, row in priors_df.iterrows()
    }

    actuals = np.array(
        [result_class(int(r.home_score), int(r.away_score)) for r in test.itertuples()]
    )

    # ── baseline uniforme
    uniform_probs = np.tile([1 / 3, 1 / 3, 1 / 3], (len(test), 1))

    # ── baseline Elo
    elo_df = pd.read_csv(DATA_RAW / "elo_ratings_2026.csv")
    elo_df["team"] = elo_df["team"].map(normalize_team)
    elo_map = dict(zip(elo_df["team"], elo_df["elo"]))
    elo_probs = np.array(
        [
            predict_elo(elo_map, r.home_team, r.away_team, bool(r.neutral))
            for r in test.itertuples()
        ]
    )

    results = [
        evaluate(uniform_probs, actuals, "Uniforme (1/3, 1/3, 1/3)"),
        evaluate(elo_probs, actuals, "Elo puro"),
    ]

    # ── varredura de λ no Dixon-Coles
    for lam in prior_lambdas:
        print(f"\n  Treinando Dixon-Coles com lambda={lam}...")
        params = fit(
            train,
            half_life_days=365.0,
            reference_date=CUTOFF_TRAIN,
            priors=priors if lam > 0 else None,
            prior_lambda=lam,
        )
        probs = []
        skipped = 0
        for r in test.itertuples():
            if r.home_team not in params.attack or r.away_team not in params.attack:
                probs.append([1 / 3, 1 / 3, 1 / 3])
                skipped += 1
                continue
            probs.append(
                predict_match(params, r.home_team, r.away_team, bool(r.neutral))
            )
        probs = np.array(probs)
        label = "DC MLE puro (lambda=0)" if lam == 0 else f"DC Bayes (lambda={lam:.0f})"
        m = evaluate(probs, actuals, label)
        m["skipped"] = skipped
        results.append(m)

    res_df = pd.DataFrame(results)
    print("\n" + "=" * 70)
    print("RESULTADOS DO BACKTEST")
    print("=" * 70)
    print(res_df.to_string(index=False))
    res_df.to_csv(RESULTS / "backtest.csv", index=False)
    return res_df


if __name__ == "__main__":
    run_backtest()
