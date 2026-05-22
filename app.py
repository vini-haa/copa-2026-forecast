"""Dashboard Streamlit para o pipeline de previsão da Copa 2026.

Execução:
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.config import GROUPS, DATA_PROCESSED, RESULTS
from src.features.build_features import load_matches, training_set
from src.model.dixon_coles import fit, match_probs, score_matrix

st.set_page_config(page_title="Copa 2026 — Previsão", layout="wide", page_icon="🏆")


@st.cache_data
def load_probabilities() -> pd.DataFrame:
    return pd.read_csv(RESULTS / "world_cup_probabilities.csv")


@st.cache_data
def load_ratings() -> pd.DataFrame:
    return pd.read_csv(RESULTS / "team_ratings.csv")


@st.cache_data
def load_fixtures() -> pd.DataFrame:
    return pd.read_csv(DATA_PROCESSED / "wc2026_fixtures.csv")


@st.cache_resource
def fit_model():
    df = load_matches()
    train = training_set(df)
    return fit(train, half_life_days=365.0, reference_date="2026-06-10")


probs = load_probabilities()
ratings = load_ratings()
fixtures = load_fixtures()

st.title("🏆 Copa do Mundo 2026 — Previsão")
st.caption(
    "Dixon-Coles + Monte Carlo (10.000 simulações) · base: 4.421 partidas pós-2022"
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏅 Favoritos ao título",
        "🎯 Análise por grupo",
        "⚔️ Simulador de partida",
        "📊 Ataque × Defesa",
    ]
)

# ----------------------------- TAB 1: FAVORITOS ------------------------------
with tab1:
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Probabilidade de ser campeão")
        top_n = st.slider("Quantas seleções mostrar", 5, 30, 15)
        top = probs.head(top_n).sort_values("P_Champion")
        fig = px.bar(
            top,
            x="P_Champion",
            y="team",
            orientation="h",
            text=top["P_Champion"].apply(lambda v: f"{v * 100:.2f}%"),
            color="P_Champion",
            color_continuous_scale="Viridis",
            labels={"P_Champion": "P(título)", "team": ""},
            height=500,
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_tickformat=".1%")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Progressão esperada (heatmap)")
        cols_round = ["P_advance_group", "P_R16", "P_QF", "P_SF", "P_F", "P_Champion"]
        labels_round = ["Grupo", "R16", "Quartas", "Semis", "Final", "Campeão"]
        heat = probs.head(top_n).set_index("team")[cols_round]
        heat.columns = labels_round
        fig2 = px.imshow(
            heat,
            color_continuous_scale="YlOrRd",
            aspect="auto",
            labels=dict(x="Rodada", y="", color="Prob."),
            height=500,
            text_auto=".0%",
        )
        fig2.update_xaxes(side="top")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Tabela completa")
    show = probs.copy()
    for c in show.columns:
        if c.startswith("P_"):
            show[c] = (show[c] * 100).round(2)
    st.dataframe(show, use_container_width=True, height=400)


# ----------------------------- TAB 2: GRUPOS --------------------------------
with tab2:
    st.subheader("Análise grupo a grupo")
    group_letter = st.selectbox(
        "Selecione o grupo",
        options=list(GROUPS.keys()),
        format_func=lambda g: f"Grupo {g} — {', '.join(GROUPS[g])}",
    )
    teams = GROUPS[group_letter]
    sub = probs[probs["team"].isin(teams)].sort_values(
        "P_advance_group", ascending=False
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Probabilidade de avançar — Grupo {group_letter}**")
        fig = px.bar(
            sub.sort_values("P_advance_group"),
            x="P_advance_group",
            y="team",
            orientation="h",
            text=sub.sort_values("P_advance_group")["P_advance_group"].apply(
                lambda v: f"{v * 100:.1f}%"
            ),
            color="P_advance_group",
            color_continuous_scale="Blues",
            labels={"P_advance_group": "P(avançar)", "team": ""},
            height=350,
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"**Probabilidade de chegar à final — Grupo {group_letter}**")
        fig = px.bar(
            sub.sort_values("P_F"),
            x="P_F",
            y="team",
            orientation="h",
            text=sub.sort_values("P_F")["P_F"].apply(lambda v: f"{v * 100:.2f}%"),
            color="P_F",
            color_continuous_scale="Reds",
            labels={"P_F": "P(final)", "team": ""},
            height=350,
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_tickformat=".1%")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Jogos do Grupo {group_letter}**")
    fx_group = fixtures[
        fixtures["home_team"].isin(teams) & fixtures["away_team"].isin(teams)
    ]
    st.dataframe(
        fx_group[["date", "home_team", "away_team", "city", "country"]],
        use_container_width=True,
        hide_index=True,
    )


# --------------------------- TAB 3: SIMULADOR -------------------------------
with tab3:
    st.subheader("Simulador de partida individual")
    st.caption(
        "Use o modelo Dixon-Coles para prever placar e probabilidades de qualquer confronto."
    )

    params = fit_model()
    available = sorted(params.teams)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        home = st.selectbox(
            "Time A",
            available,
            index=available.index("Brazil") if "Brazil" in available else 0,
        )
    with col2:
        away = st.selectbox(
            "Time B",
            available,
            index=available.index("Argentina") if "Argentina" in available else 1,
        )
    with col3:
        neutral = st.checkbox("Campo neutro", value=True)

    if home == away:
        st.warning("Selecione times diferentes.")
    else:
        mp = match_probs(params, home, away, neutral=neutral)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"Vitória {home}", f"{mp['home_win'] * 100:.1f}%")
        col2.metric("Empate", f"{mp['draw'] * 100:.1f}%")
        col3.metric(f"Vitória {away}", f"{mp['away_win'] * 100:.1f}%")
        col4.metric(
            "Gols esperados", f"{mp['exp_home_goals']:.2f} × {mp['exp_away_goals']:.2f}"
        )

        st.markdown("**Distribuição de placares mais prováveis**")
        mat = score_matrix(
            mp["exp_home_goals"], mp["exp_away_goals"], params.rho, max_goals=6
        )
        scores = []
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                scores.append(
                    {
                        "placar": f"{i}-{j}",
                        f"{home}": i,
                        f"{away}": j,
                        "prob": mat[i, j],
                    }
                )
        sdf = pd.DataFrame(scores).sort_values("prob", ascending=False).head(15)
        fig = px.bar(
            sdf,
            x="placar",
            y="prob",
            text=sdf["prob"].apply(lambda v: f"{v * 100:.1f}%"),
            labels={"placar": f"Placar ({home} × {away})", "prob": "Probabilidade"},
            color="prob",
            color_continuous_scale="Teal",
            height=350,
        )
        fig.update_layout(coloraxis_showscale=False, yaxis_tickformat=".1%")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Matriz completa de placares**")
        mat_df = pd.DataFrame(
            (mat * 100).round(2),
            index=[f"{home} {i}" for i in range(mat.shape[0])],
            columns=[f"{away} {j}" for j in range(mat.shape[1])],
        )
        fig = px.imshow(
            mat_df,
            color_continuous_scale="Greens",
            text_auto=".1f",
            aspect="auto",
            labels=dict(color="% prob"),
        )
        st.plotly_chart(fig, use_container_width=True)


# --------------------------- TAB 4: ATAQUE x DEFESA -------------------------
with tab4:
    st.subheader("Força ofensiva × defensiva (Dixon-Coles)")
    st.caption(
        "Quanto mais à direita, melhor o ataque. Quanto mais para baixo, melhor a defesa "
        "(valores menores = sofre menos gol). Times no quadrante inferior-direito são os mais fortes."
    )

    all_wc_teams = [t for g in GROUPS.values() for t in g]
    rating_wc = ratings[ratings["team"].isin(all_wc_teams)].copy()
    rating_wc["grupo"] = rating_wc["team"].apply(
        lambda t: next(g for g, ts in GROUPS.items() if t in ts)
    )
    fig = px.scatter(
        rating_wc,
        x="attack",
        y="defense",
        text="team",
        color="grupo",
        size=(rating_wc["rating"] - rating_wc["rating"].min() + 0.1) * 5,
        labels={"attack": "Força ofensiva (>) ", "defense": "Força defensiva (<)"},
        height=650,
    )
    fig.update_traces(textposition="top center", textfont=dict(size=10))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Top 15 por rating combinado (ataque − defesa)**")
    st.dataframe(
        rating_wc.sort_values("rating", ascending=False)
        .head(15)[["team", "grupo", "attack", "defense", "rating"]]
        .round(3),
        use_container_width=True,
        hide_index=True,
    )


st.divider()
st.caption(
    "Fontes: martj42/international_results · eloratings.net · FIFA. "
    "Modelo: Dixon-Coles (1997). Pipeline em [src/](src/) · [Relatório completo](results/RELATORIO_v1.md)."
)
