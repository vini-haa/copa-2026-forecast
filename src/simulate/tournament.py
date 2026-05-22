"""Simulação Monte Carlo da Copa 2026 (48 times).

Formato:
  - 12 grupos de 4. Cada time joga 3 partidas.
  - Avançam: 1º e 2º de cada grupo (24) + 8 melhores 3º colocados = 32.
  - Mata-mata: 32 → 16 → 8 → 4 → 2 (final).

Critérios de desempate dentro do grupo: pontos > saldo > gols pró > sorteio.
Ranking dos 3º colocados: pontos > saldo > gols pró.

Bracket do mata-mata: a FIFA ainda não divulgou cruzamentos definitivos
até a publicação deste pipeline. Adotamos uma estrutura simétrica baseada
nas posições dos grupos (seed-by-group). Quando a FIFA confirmar, basta
ajustar BRACKET_R32.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import GROUPS, HOST_COUNTRIES
from src.model.dixon_coles import DixonColesParams, score_matrix


# Bracket simétrico para Round of 32:
# Posições do grupo: "1A" = 1º do grupo A; "2B" = 2º do grupo B; "3X" = 3º que se classificou
# Estrutura inspirada em torneios anteriores (1ºs enfrentam 2ºs/3ºs de outros grupos).
# Os 8 melhores 3º colocados são alocados nos slots 3X1..3X8.
BRACKET_R32 = [
    ("1A", "2B"),
    ("1C", "3X1"),
    ("1E", "2F"),
    ("1G", "3X2"),
    ("1I", "2J"),
    ("1K", "3X3"),
    ("1B", "2A"),
    ("1D", "3X4"),
    ("1F", "2E"),
    ("1H", "3X5"),
    ("1J", "2I"),
    ("1L", "3X6"),
    ("2C", "2D"),
    ("2G", "2H"),
    ("2K", "2L"),
    ("3X7", "3X8"),
]


@dataclass
class TeamStanding:
    team: str
    group: str
    points: int = 0
    gf: int = 0
    ga: int = 0
    gd: int = 0


def simulate_match(
    home: str,
    away: str,
    params: DixonColesParams,
    rng: np.random.Generator,
    neutral: bool = True,
    knockout: bool = False,
) -> tuple[int, int, str]:
    """Retorna (gols_home, gols_away, vencedor). Em mata-mata, sem empate."""
    lam_h, lam_a = params.predict_lambdas(home, away, neutral)
    mat = score_matrix(lam_h, lam_a, params.rho, max_goals=10)
    flat = mat.flatten()
    idx = rng.choice(flat.size, p=flat / flat.sum())
    n = mat.shape[0]
    gh, ga = divmod(idx, n)
    winner = home if gh > ga else away if ga > gh else None
    if knockout and winner is None:
        # prorrogação simplificada: meia-partida, depois pênaltis 50/50
        lam_h_ot, lam_a_ot = lam_h * 0.33, lam_a * 0.33
        gh_ot = rng.poisson(lam_h_ot)
        ga_ot = rng.poisson(lam_a_ot)
        gh += int(gh_ot)
        ga += int(ga_ot)
        if gh > ga:
            winner = home
        elif ga > gh:
            winner = away
        else:
            winner = home if rng.random() < 0.5 else away
    return int(gh), int(ga), winner or "draw"


def simulate_group(
    teams: list[str],
    group_letter: str,
    params: DixonColesParams,
    rng: np.random.Generator,
    fixtures: pd.DataFrame | None = None,
) -> list[TeamStanding]:
    standings = {t: TeamStanding(team=t, group=group_letter) for t in teams}
    matchups = [
        (teams[i], teams[j])
        for i in range(len(teams))
        for j in range(i + 1, len(teams))
    ]
    for home, away in matchups:
        neutral = _is_neutral(home, away, fixtures)
        gh, ga, _ = simulate_match(
            home, away, params, rng, neutral=neutral, knockout=False
        )
        s_h, s_a = standings[home], standings[away]
        s_h.gf += gh
        s_h.ga += ga
        s_a.gf += ga
        s_a.ga += gh
        if gh > ga:
            s_h.points += 3
        elif ga > gh:
            s_a.points += 3
        else:
            s_h.points += 1
            s_a.points += 1
    for s in standings.values():
        s.gd = s.gf - s.ga
    return sorted(
        standings.values(),
        key=lambda s: (s.points, s.gd, s.gf, rng.random()),
        reverse=True,
    )


def _is_neutral(home: str, away: str, fixtures: pd.DataFrame | None) -> bool:
    """Para fase de grupos, o anfitrião joga em casa quando em seu país."""
    if home in HOST_COUNTRIES:
        return False
    return True


def select_best_thirds(
    group_standings: dict[str, list[TeamStanding]],
) -> list[TeamStanding]:
    thirds = [g[2] for g in group_standings.values()]
    return sorted(thirds, key=lambda s: (s.points, s.gd, s.gf), reverse=True)[:8]


def run_knockout(
    qualified: dict[str, TeamStanding],
    thirds_top8: list[TeamStanding],
    params: DixonColesParams,
    rng: np.random.Generator,
) -> dict[str, str]:
    """Roda R32 → final. Retorna progressão por rodada."""
    slots: dict[str, str] = {}
    for letter in GROUPS:
        slots[f"1{letter}"] = qualified[f"1{letter}"].team
        slots[f"2{letter}"] = qualified[f"2{letter}"].team
    for i, t in enumerate(thirds_top8, 1):
        slots[f"3X{i}"] = t.team

    progression: dict[str, list[str]] = {
        "R32": [],
        "R16": [],
        "QF": [],
        "SF": [],
        "F": [],
        "Champion": [],
    }

    current = [(slots[a], slots[b]) for a, b in BRACKET_R32]
    for round_name in ["R32", "R16", "QF", "SF", "F"]:
        winners = []
        for home, away in current:
            _, _, w = simulate_match(
                home, away, params, rng, neutral=True, knockout=True
            )
            winners.append(w)
            progression[round_name].append(w)
        if round_name != "F":
            current = [(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]
        else:
            progression["Champion"].append(winners[0])
    return progression


def simulate_tournament(
    params: DixonColesParams,
    rng: np.random.Generator,
    fixtures: pd.DataFrame | None = None,
) -> dict:
    group_standings = {}
    qualified = {}
    for letter, teams in GROUPS.items():
        standings = simulate_group(teams, letter, params, rng, fixtures)
        group_standings[letter] = standings
        qualified[f"1{letter}"] = standings[0]
        qualified[f"2{letter}"] = standings[1]
    thirds = select_best_thirds(group_standings)
    progression = run_knockout(qualified, thirds, params, rng)
    return {
        "groups": group_standings,
        "thirds_top8": [t.team for t in thirds],
        "progression": progression,
    }


def aggregate(results: list[dict]) -> pd.DataFrame:
    """Agrega N simulações em probabilidades por seleção."""
    rounds = ["R32", "R16", "QF", "SF", "F", "Champion"]
    counts: dict[str, dict[str, int]] = {}
    advanced_groups: dict[str, int] = {}
    n = len(results)
    for sim in results:
        groups = sim["groups"]
        for g in groups.values():
            for pos, s in enumerate(g):
                if pos < 2:
                    advanced_groups[s.team] = advanced_groups.get(s.team, 0) + 1
        for team in sim["thirds_top8"]:
            advanced_groups[team] = advanced_groups.get(team, 0) + 1
        prog = sim["progression"]
        for r in rounds:
            for team in prog[r]:
                counts.setdefault(team, {}).setdefault(r, 0)
                counts[team][r] += 1
    rows = []
    for team, d in counts.items():
        row = {"team": team, "P_advance_group": advanced_groups.get(team, 0) / n}
        for r in rounds:
            row[f"P_{r}"] = d.get(r, 0) / n
        rows.append(row)
    df = pd.DataFrame(rows).fillna(0.0)
    df = df.sort_values("P_Champion", ascending=False).reset_index(drop=True)
    return df
