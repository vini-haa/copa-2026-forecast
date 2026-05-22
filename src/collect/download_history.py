"""Baixa o dataset histórico de partidas internacionais (martj42/international_results)."""

from __future__ import annotations

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DATA_RAW

FILES = {
    "results.csv": "https://raw.githubusercontent.com/martj42/international_results/master/results.csv",
    "goalscorers.csv": "https://raw.githubusercontent.com/martj42/international_results/master/goalscorers.csv",
    "shootouts.csv": "https://raw.githubusercontent.com/martj42/international_results/master/shootouts.csv",
    "former_names.csv": "https://raw.githubusercontent.com/martj42/international_results/master/former_names.csv",
}


def download_all() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    for fname, url in FILES.items():
        dest = DATA_RAW / fname
        print(f"-> baixando {fname} ...", flush=True)
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        size_kb = dest.stat().st_size / 1024
        print(f"   ok ({size_kb:,.1f} KB)")


if __name__ == "__main__":
    download_all()
