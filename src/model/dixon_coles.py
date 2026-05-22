"""Modelo Dixon-Coles para previsão de placares.

Estima força de ataque/defesa por seleção via MLE com pesos exponenciais
por idade do jogo. Aplica correção para resultados de baixo placar (0-0, 1-0, 0-1, 1-1).

Referência: Dixon & Coles (1997), "Modelling Association Football Scores
and Inefficiencies in the Football Betting Market".
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson


@dataclass
class DixonColesParams:
    teams: list[str]
    attack: dict[str, float]
    defense: dict[str, float]
    home_advantage: float
    rho: float

    def predict_lambdas(
        self, home: str, away: str, neutral: bool = True
    ) -> tuple[float, float]:
        ha = 0.0 if neutral else self.home_advantage
        lam_h = np.exp(self.attack.get(home, 0.0) + self.defense.get(away, 0.0) + ha)
        lam_a = np.exp(self.attack.get(away, 0.0) + self.defense.get(home, 0.0))
        return float(lam_h), float(lam_a)


def _dc_correction(x: int, y: int, lam_h: float, lam_a: float, rho: float) -> float:
    if x == 0 and y == 0:
        return 1.0 - lam_h * lam_a * rho
    if x == 0 and y == 1:
        return 1.0 + lam_h * rho
    if x == 1 and y == 0:
        return 1.0 + lam_a * rho
    if x == 1 and y == 1:
        return 1.0 - rho
    return 1.0


def _neg_log_likelihood(
    params: np.ndarray,
    home_idx: np.ndarray,
    away_idx: np.ndarray,
    home_goals: np.ndarray,
    away_goals: np.ndarray,
    weights: np.ndarray,
    neutral_mask: np.ndarray,
    n_teams: int,
    prior_attack: np.ndarray | None = None,
    prior_defense: np.ndarray | None = None,
    prior_lambda: float = 0.0,
) -> float:
    attack = params[:n_teams]
    defense = params[n_teams : 2 * n_teams]
    home_advantage = params[-2]
    rho = params[-1]

    ha = np.where(neutral_mask, 0.0, home_advantage)
    lam_h = np.exp(attack[home_idx] + defense[away_idx] + ha)
    lam_a = np.exp(attack[away_idx] + defense[home_idx])

    log_p_h = home_goals * np.log(lam_h) - lam_h
    log_p_a = away_goals * np.log(lam_a) - lam_a

    # correção de Dixon-Coles para placares baixos
    correction = np.ones_like(lam_h)
    mask_00 = (home_goals == 0) & (away_goals == 0)
    mask_01 = (home_goals == 0) & (away_goals == 1)
    mask_10 = (home_goals == 1) & (away_goals == 0)
    mask_11 = (home_goals == 1) & (away_goals == 1)
    correction[mask_00] = 1.0 - lam_h[mask_00] * lam_a[mask_00] * rho
    correction[mask_01] = 1.0 + lam_h[mask_01] * rho
    correction[mask_10] = 1.0 + lam_a[mask_10] * rho
    correction[mask_11] = 1.0 - rho

    correction = np.clip(correction, 1e-10, None)
    log_lik = weights * (log_p_h + log_p_a + np.log(correction))
    nll = -log_lik.sum()

    # Regularização bayesiana: puxa attack/defense em direção ao prior.
    # Termo MAP: -log p(θ) = (λ/2) Σ (θ_i - μ_i)²
    if prior_lambda > 0.0 and prior_attack is not None and prior_defense is not None:
        nll += 0.5 * prior_lambda * np.sum((attack - prior_attack) ** 2)
        nll += 0.5 * prior_lambda * np.sum((defense - prior_defense) ** 2)
    return nll


def fit(
    matches: pd.DataFrame,
    half_life_days: float = 365.0,
    reference_date: str | None = None,
    priors: dict[str, tuple[float, float]] | None = None,
    prior_lambda: float = 0.0,
) -> DixonColesParams:
    """Ajusta o modelo. `matches` precisa de: date, home_team, away_team,
    home_score, away_score, neutral.

    Args:
        priors: dict opcional team -> (prior_attack, prior_defense).
        prior_lambda: força do prior (0 = sem prior; 5-20 = moderado;
            >50 = forte). Equivale ao inverso da variância do prior.
    """
    df = matches.dropna(subset=["home_score", "away_score"]).copy()
    df["date"] = pd.to_datetime(df["date"])
    ref = pd.to_datetime(reference_date) if reference_date else df["date"].max()

    age_days = (ref - df["date"]).dt.days.clip(lower=0).to_numpy()
    weights = 0.5 ** (age_days / half_life_days)

    teams = sorted(set(df["home_team"]).union(df["away_team"]))
    idx = {t: i for i, t in enumerate(teams)}
    n = len(teams)

    home_idx = df["home_team"].map(idx).to_numpy()
    away_idx = df["away_team"].map(idx).to_numpy()
    hg = df["home_score"].astype(int).to_numpy()
    ag = df["away_score"].astype(int).to_numpy()
    neutral = df["neutral"].astype(bool).to_numpy()

    prior_attack = np.zeros(n)
    prior_defense = np.zeros(n)
    if priors is not None:
        for t, (a, d) in priors.items():
            if t in idx:
                prior_attack[idx[t]] = a
                prior_defense[idx[t]] = d

    x0 = np.concatenate([prior_attack.copy(), prior_defense.copy(), [0.25, -0.05]])

    # restrição: soma de ataques = 0 (identifiabilidade)
    constraints = [{"type": "eq", "fun": lambda p: p[:n].sum()}]

    res = minimize(
        _neg_log_likelihood,
        x0,
        args=(
            home_idx,
            away_idx,
            hg,
            ag,
            weights,
            neutral,
            n,
            prior_attack,
            prior_defense,
            prior_lambda,
        ),
        method="SLSQP",
        constraints=constraints,
        options={"maxiter": 300, "ftol": 1e-7},
    )

    attack = dict(zip(teams, res.x[:n]))
    defense = dict(zip(teams, res.x[n : 2 * n]))
    return DixonColesParams(
        teams=teams,
        attack=attack,
        defense=defense,
        home_advantage=float(res.x[-2]),
        rho=float(res.x[-1]),
    )


def score_matrix(
    lam_h: float, lam_a: float, rho: float, max_goals: int = 10
) -> np.ndarray:
    """Distribuição conjunta de gols com correção Dixon-Coles."""
    ph = poisson.pmf(np.arange(max_goals + 1), lam_h)
    pa = poisson.pmf(np.arange(max_goals + 1), lam_a)
    mat = np.outer(ph, pa)
    mat[0, 0] *= 1.0 - lam_h * lam_a * rho
    mat[0, 1] *= 1.0 + lam_h * rho
    mat[1, 0] *= 1.0 + lam_a * rho
    mat[1, 1] *= 1.0 - rho
    mat = np.clip(mat, 0.0, None)
    mat /= mat.sum()
    return mat


def match_probs(
    params: DixonColesParams, home: str, away: str, neutral: bool = True
) -> dict[str, float]:
    lam_h, lam_a = params.predict_lambdas(home, away, neutral)
    mat = score_matrix(lam_h, lam_a, params.rho)
    p_home = float(np.tril(mat, -1).sum())
    p_draw = float(np.trace(mat))
    p_away = float(np.triu(mat, 1).sum())
    return {
        "home_win": p_home,
        "draw": p_draw,
        "away_win": p_away,
        "exp_home_goals": lam_h,
        "exp_away_goals": lam_a,
    }
