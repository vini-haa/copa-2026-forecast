"""Gera o gráfico de probabilidades de título (top 16) para o README."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import RESULTS


def plot_top16() -> Path:
    df = pd.read_csv(RESULTS / "world_cup_probabilities.csv")
    top = df.sort_values("P_Champion", ascending=False).head(16).iloc[::-1]

    fig, ax = plt.subplots(figsize=(10, 8), dpi=130)
    colors = plt.cm.viridis(top["P_Champion"] / top["P_Champion"].max())
    bars = ax.barh(
        top["team"], top["P_Champion"] * 100, color=colors, edgecolor="white"
    )

    for bar, val in zip(bars, top["P_Champion"] * 100):
        ax.text(
            val + 0.2,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}%",
            va="center",
            fontsize=10,
            color="#222",
        )

    ax.set_xlabel("Probabilidade de título (%)", fontsize=12)
    ax.set_title(
        "Copa do Mundo 2026 — Top 16 favoritos ao título\n"
        "Modelo Dixon-Coles + 10.000 simulações Monte Carlo",
        fontsize=13,
        pad=15,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    plt.tight_layout()
    out = RESULTS / "probabilities_top16.png"
    plt.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Gráfico salvo em: {out}")
    return out


if __name__ == "__main__":
    plot_top16()
