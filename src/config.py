"""Configuração central do projeto: grupos da Copa 2026, sedes, datas."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_FEATURES = ROOT / "data" / "features"
RESULTS = ROOT / "results"

GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

PLAYOFF_CANDIDATES = ["Bolivia", "Iraq"]

TEAM_NAME_ALIASES = {
    "USA": "United States",
    "Korea Republic": "South Korea",
    "Cote d'Ivoire": "Ivory Coast",
    "Côte d'Ivoire": "Ivory Coast",
    "Czechia": "Czech Republic",
    "Türkiye": "Turkey",
    "Turkiye": "Turkey",
    "Cabo Verde": "Cape Verde",
    "DR Congo": "DR Congo",
    "Congo DR": "DR Congo",
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "Curaçao": "Curacao",
}

HOST_COUNTRIES = ["United States", "Canada", "Mexico"]

TOURNAMENT_START = "2026-06-11"
TOURNAMENT_END = "2026-07-19"


def all_teams(include_playoff: bool = True) -> list[str]:
    teams = [t for group in GROUPS.values() for t in group]
    if not include_playoff:
        teams = [t for t in teams if "Playoff" not in t]
    return teams


def normalize_team(name: str) -> str:
    return TEAM_NAME_ALIASES.get(name.strip(), name.strip())
