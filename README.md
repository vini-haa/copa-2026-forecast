# Copa do Mundo 2026 — Forecast Probabilístico

> Modelagem estatística da Copa do Mundo de 2026 com **Dixon-Coles** e simulação
> **Monte Carlo** (10.000 cenários). Estima probabilidades de classificação por
> grupo, avanço por fase e título.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![Probabilidades de título](results/probabilities_top16.png)

## Por que esse projeto?

Exercício autoral de modelagem probabilística aplicada a um problema real e
verificável: prever a Copa do Mundo de 2026. Combina coleta de dados públicos,
ajuste de modelo estatístico via MLE, simulação Monte Carlo e validação
out-of-sample — o pipeline completo de um problema de previsão.

## Metodologia

- **Coleta**: 49.329 partidas internacionais (1872-2026) do dataset público
  [`martj42/international_results`](https://github.com/martj42/international_results),
  enriquecido com Elo ratings (eloratings.net), valor de mercado dos elencos
  (Transfermarkt) e odds de mercado (ESPN/Polymarket) para validação.
  Filtragem para 4.421 partidas pós-2022 (ciclo atual).

- **Modelo Dixon-Coles** (Dixon & Coles, 1997): extensão do modelo de Poisson
  para resultados de futebol. Estima por MLE um parâmetro de **ataque** e
  **defesa** por seleção, mais um **home advantage** e uma **correção ρ** para
  resultados de baixo placar (0-0, 1-0, 0-1, 1-1) que Poisson independente
  subestima. Aplica decaimento exponencial (half-life de 365 dias) para que
  jogos mais recentes pesem mais.

- **Simulação Monte Carlo**: 10.000 torneios completos. Cada partida tem placar
  amostrado da matriz Dixon-Coles. Mata-mata simula prorrogação como meio tempo
  extra; pênaltis como 50/50. Probabilidades finais = frequência relativa de
  cada seleção avançar/vencer.

- **Validação out-of-sample**: backtest com treino até 2025-12-31 e teste em
  165 partidas das eliminatórias de 2026. Modelo bate baselines (Elo puro,
  uniforme) em Brier score (0,53), log-loss (0,90) e accuracy (55,8%).

## Arquitetura

```
copa-2026-forecast/
├── src/
│   ├── collect/             # coleta de dados
│   │   ├── download_history.py    # baixa dataset histórico (martj42)
│   │   └── build_fixtures.py      # extrai fixtures Copa 2026
│   ├── features/
│   │   └── build_features.py      # base de treino com filtro temporal
│   ├── model/
│   │   ├── dixon_coles.py         # MLE + correção placares baixos
│   │   ├── priors.py              # priors Elo + market value (não usado no final)
│   │   ├── calibration.py         # comparação modelo vs mercado
│   │   └── backtest.py            # validação out-of-sample
│   ├── simulate/
│   │   └── tournament.py          # Monte Carlo do bracket 48 times
│   ├── config.py                  # grupos, sedes, aliases de nomes
│   ├── plots.py                   # gráficos para o README
│   └── main.py                    # orquestrador end-to-end
├── app.py                         # dashboard Streamlit (6 abas)
├── data/
│   ├── raw/                       # CSVs originais (datasets públicos)
│   └── processed/                 # base de treino + fixtures
├── results/                       # probabilidades, ratings, gráfico, relatório
├── requirements.txt
└── LICENSE
```

## Como reproduzir

```bash
git clone https://github.com/vini-haa/copa-2026-forecast
cd copa-2026-forecast
pip install -r requirements.txt

# Pipeline end-to-end
python -m src.collect.download_history   # baixa ~7MB de CSVs
python -m src.features.build_features    # gera base de treino
python -m src.collect.build_fixtures     # extrai jogos Copa 2026
python -m src.main                       # ajusta modelo + simula + reporta
python -m src.plots                      # regenera gráfico do README

# Validação e diagnóstico (opcionais)
python -m src.model.backtest             # backtest out-of-sample
python -m src.model.calibration          # compara com odds de mercado

# Dashboard interativo
streamlit run app.py
```

## Resultados

Top 8 seleções por probabilidade de título (10k simulações Monte Carlo):

| Seleção     | P(Título) | P(Final) | P(Avançar) |
|-------------|----------:|---------:|-----------:|
| Espanha     | 15,90%    | 15,9%    | 99,5%      |
| Argentina   | 14,02%    | 14,0%    | 97,8%      |
| Brasil      |  6,81%    |  6,8%    | 97,7%      |
| Inglaterra  |  6,72%    |  6,7%    | 97,2%      |
| Marrocos    |  6,15%    |  6,2%    | 94,8%      |
| Portugal    |  5,77%    |  5,8%    | 88,7%      |
| França      |  5,26%    |  5,3%    | 91,4%      |
| Colômbia    |  4,97%    |  5,0%    | 87,8%      |

Probabilidades completas em [`results/world_cup_probabilities.csv`](results/world_cup_probabilities.csv).
Análise consolidada em [`results/RELATORIO_FINAL.md`](results/RELATORIO_FINAL.md).

### Backtest out-of-sample

| Modelo                  | Brier ↓ | Log-loss ↓ | Accuracy ↑ |
|-------------------------|--------:|-----------:|-----------:|
| Uniforme (chão teórico) | 0,667   | 1,099      | 43,6%      |
| Elo puro                | 0,657   | 1,152      | 49,1%      |
| **Dixon-Coles (MLE)**   | **0,533** | **0,895** | **55,8%**  |

Testado em 165 partidas reais das eliminatórias jan-mai/2026, com treino até
dez/2025. Detalhes em [`src/model/backtest.py`](src/model/backtest.py).

## Limitações conhecidas

- Modelo assume **independência entre partidas** (não captura "momentum" nem
  efeito psicológico de eliminação em mata-mata).
- Calibrado em **placares históricos**; não incorpora lesões nem escalações
  finais (que serão conhecidas só em 02/06/2026).
- Pesos exponenciais de decaimento temporal usando **half-life de 365 dias**
  (padrão razoável; não tunado por validação).
- Bracket pós-fase de grupos usa **cruzamento simétrico padrão** — a FIFA
  ainda não confirmou cruzamentos oficiais para o formato de 48 times.
- Vantagem de campo modelada apenas para o trio anfitrião (EUA/Canadá/México)
  jogando em seus respectivos países.

## Stack

Python 3.11+ · NumPy · Pandas · SciPy (otimização MLE) · Matplotlib · Streamlit · Plotly

## Referências

- Dixon, M. J., & Coles, S. G. (1997). *Modelling Association Football Scores
  and Inefficiencies in the Football Betting Market*. Journal of the Royal
  Statistical Society: Series C (Applied Statistics), 46(2), 265–280.
- Dataset histórico: [martj42/international_results](https://github.com/martj42/international_results) (CC0)
- Elo ratings: [eloratings.net](https://www.eloratings.net/)

## Autor

**Vinicius Henrique Albino Andrade**
[LinkedIn](https://www.linkedin.com/in/vini-haa/) · [GitHub](https://github.com/vini-haa)
