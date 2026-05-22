"""Orquestrador: ajusta Dixon-Coles e roda Monte Carlo da Copa 2026."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATA_PROCESSED, RESULTS, GROUPS, all_teams
from src.features.build_features import load_matches, training_set
from src.model.dixon_coles import fit
from src.simulate.tournament import simulate_tournament, aggregate

N_SIMULATIONS = 10_000
HALF_LIFE = 365.0  # dias


def main() -> None:
    print("=" * 70)
    print("COPA DO MUNDO 2026 — PIPELINE DE PREVISÃO")
    print("=" * 70)

    print("\n[1/4] Carregando partidas...")
    df = load_matches()
    train = training_set(df)
    print(f"  Treino: {len(train):,} partidas (2022-2026)")

    print(f"\n[2/4] Ajustando Dixon-Coles (half-life={HALF_LIFE} dias)...")
    t0 = time.time()
    params = fit(train, half_life_days=HALF_LIFE, reference_date="2026-06-10")
    print(f"  OK em {time.time() - t0:.1f}s. Times no modelo: {len(params.teams)}")
    print(f"  Home advantage: {params.home_advantage:.4f}  |  rho: {params.rho:.4f}")

    teams_2026 = all_teams(include_playoff=False)
    missing = [t for t in teams_2026 if t not in params.attack]
    if missing:
        print(f"  AVISO: sem dados suficientes para: {missing}")

    print("\n  Top 10 ataque + defesa (rating combinado = attack - defense):")
    ratings = pd.DataFrame(
        {
            "team": params.teams,
            "attack": [params.attack[t] for t in params.teams],
            "defense": [params.defense[t] for t in params.teams],
        }
    )
    ratings["rating"] = ratings["attack"] - ratings["defense"]
    ratings_wc = ratings[ratings["team"].isin(teams_2026)].sort_values(
        "rating", ascending=False
    )
    print(ratings_wc.head(15).to_string(index=False))

    RESULTS.mkdir(parents=True, exist_ok=True)
    ratings_wc.to_csv(RESULTS / "team_ratings.csv", index=False)

    print(f"\n[3/4] Rodando {N_SIMULATIONS:,} simulações Monte Carlo...")
    rng = np.random.default_rng(42)
    fixtures = pd.read_csv(DATA_PROCESSED / "wc2026_fixtures.csv")
    sims = []
    t0 = time.time()
    for i in range(N_SIMULATIONS):
        sims.append(simulate_tournament(params, rng, fixtures))
        if (i + 1) % 1000 == 0:
            elapsed = time.time() - t0
            eta = elapsed / (i + 1) * (N_SIMULATIONS - i - 1)
            print(f"  {i + 1:>5} / {N_SIMULATIONS}  ({elapsed:.1f}s, eta {eta:.0f}s)")
    print(f"  OK em {time.time() - t0:.1f}s")

    print("\n[4/4] Agregando resultados...")
    probs = aggregate(sims)
    probs.to_csv(RESULTS / "world_cup_probabilities.csv", index=False)

    print("\n" + "=" * 70)
    print("PROBABILIDADES DE TÍTULO (top 20)")
    print("=" * 70)
    cols = ["team", "P_advance_group", "P_R16", "P_QF", "P_SF", "P_F", "P_Champion"]
    print(probs[cols].head(20).to_string(index=False))

    print("\nFavoritos por grupo (probabilidade de avançar):")
    for letter, teams in GROUPS.items():
        sub = probs[probs["team"].isin(teams)].sort_values(
            "P_advance_group", ascending=False
        )
        print(f"\n  Grupo {letter}:")
        for _, r in sub.iterrows():
            print(
                f"    {r['team']:<25} avança={r['P_advance_group'] * 100:5.1f}%  título={r['P_Champion'] * 100:5.2f}%"
            )


if __name__ == "__main__":
    main()
