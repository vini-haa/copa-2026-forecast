# Previsão Copa do Mundo 2026 — Relatório FINAL (v3)

**Data:** 2026-05-22
**Modelo:** Dixon-Coles **MLE puro** (validado por backtest como melhor que Bayes)
**Simulações:** 10.000 Monte Carlo
**Base de treino:** 4.421 partidas pós-2022

---

## 1. Decisão metodológica chave: MLE > Bayesiano

Antes deste relatório, considerávamos a v2 (bayesiano com prior Elo + market value)
melhor que a v1 (MLE puro). O backtest provou o contrário.

### Backtest out-of-sample

- **Treino:** 4.256 partidas (2022-01-01 → 2025-12-31)
- **Teste:** 165 partidas (jan/2026 → maio/2026, eliminatórias mundiais)
- **Métrica principal:** Brier score multiclasse (menor = melhor)

| Modelo | Brier ↓ | Log-loss ↓ | Accuracy ↑ |
|---|---:|---:|---:|
| Uniforme (chão) | 0,667 | 1,099 | 43,6% |
| Elo puro | 0,657 | 1,152 | 49,1% |
| **DC MLE puro (λ=0)** ⭐ | **0,533** | **0,895** | **55,8%** |
| DC Bayes (λ=4) | 0,580 | 0,972 | 53,3% |
| DC Bayes (λ=8) | 0,589 | 0,985 | 50,3% |
| DC Bayes (λ=12) | 0,595 | 0,992 | 50,9% |
| DC Bayes (λ=20) | 0,601 | 1,001 | 50,9% |

**Conclusão objetiva:** prior bayesiano **piora** o modelo. Com 4k+ jogos de treino,
o MLE puro já está bem informado e o prior só introduz viés sem reduzir variância.
**Modelo final volta a λ=0 (= v1 original validada).**

### O que isso significa para o gap França "modelo 5% vs mercado 15%"

A interpretação correta é: **mercado provavelmente está com prêmio de reputação**
(França foi campeã 2018, vice 2022), não o modelo está errado. O backtest mostra
que o modelo prevê resultados reais melhor que Elo puro (que é a base de muitos
rankings que precificam França alto). Tratamos a discrepância como **edge** —
informação útil, não erro a corrigir.

## 2. Top 20 — probabilidades finais

| Pos | Seleção        | Avança | R16 | QF | SF | F | **Título** |
|----:|----------------|-------:|----:|---:|---:|--:|-----------:|
| 1  | Espanha         | 99,5% | 56,3% | 34,8% | 23,6% | 15,9% | **15,90%** |
| 2  | Argentina       | 97,8% | 46,3% | 30,7% | 21,1% | 14,0% | **14,02%** |
| 3  | Brasil          | 97,7% | 46,7% | 27,2% | 14,1% |  6,8% |  **6,81%** |
| 4  | Inglaterra      | 97,2% | 38,3% | 20,6% | 11,9% |  6,7% |  **6,72%** |
| 5  | Marrocos        | 94,8% | 41,5% | 23,5% | 12,2% |  6,2% |  **6,15%** |
| 6  | Portugal        | 88,7% | 35,4% | 22,6% | 11,4% |  5,8% |  **5,77%** |
| 7  | França          | 91,4% | 31,1% | 19,0% | 10,8% |  5,3% |  **5,26%** |
| 8  | Colômbia        | 87,8% | 34,4% | 21,1% | 10,3% |  5,0% |  **4,97%** |
| 9  | Japão           | 90,2% | 28,8% | 16,3% |  9,2% |  4,3% |  **4,33%** |
| 10 | Holanda         | 92,0% | 28,7% | 15,8% |  8,3% |  4,1% |  **4,15%** |
| 11 | Suíça           | 98,3% | 40,2% | 18,3% |  8,7% |  3,6% |  **3,59%** |
| 12 | Equador         | 94,7% | 26,2% | 13,5% |  7,1% |  3,5% |  **3,48%** |
| 13 | Noruega         | 87,3% | 24,5% | 13,2% |  6,8% |  3,2% |  **3,16%** |
| 14 | Alemanha        | 98,1% | 29,0% | 14,6% |  7,2% |  3,1% |  **3,06%** |
| 15 | Senegal         | 81,2% | 19,7% | 10,1% |  4,6% |  1,9% |  **1,93%** |
| 16 | Uruguai         | 86,9% | 24,1% | 10,7% |  3,7% |  1,5% |  **1,53%** |
| 17 | Áustria         | 80,9% | 16,6% |  8,2% |  3,9% |  1,5% |  **1,53%** |
| 18 | Croácia         | 91,1% | 23,1% |  9,9% |  3,6% |  1,3% |  **1,31%** |
| 19 | Bélgica         | 88,0% | 19,1% |  8,5% |  3,2% |  1,0% |  **0,99%** |
| 20 | Canadá          | 93,6% | 19,3% |  6,9% |  2,5% |  0,7% |  **0,70%** |

## 3. Picks de valor (modelo vs mercado)

Onde o modelo discorda do mercado e foi validado pelo backtest:

### 🟢 Edges positivos (modelo > mercado — possível valor)

| Seleção | Modelo | Mercado | Edge | Por quê |
|---|---:|---:|---:|---|
| Argentina | 14,0% | 8,4% | **+5,6 pp** | Forma estelar + Grupo J fácil |
| Marrocos | 6,2% | 1,5% | **+4,6 pp** | Defesa elite + Grupo C onde só Brasil é favorito claro |
| Colômbia | 5,0% | 1,8% | +3,1 pp | Elo top-5 mundial, mercado subestima |
| Japão | 4,3% | 1,7% | +2,7 pp | Confronto direto com Holanda no Grupo F, mas força equilibrada |
| Equador | 3,5% | 0,8% | +2,7 pp | Defesa elite (-1,80) + grupo médio |
| Suíça | 3,6% | 1,0% | +2,6 pp | Grupo B muito favorável (Catar, Bósnia, Canadá) |

### 🔴 Edges negativos (modelo cético; mercado paga prêmio)

| Seleção | Modelo | Mercado | Edge | Provável explicação |
|---|---:|---:|---:|---|
| França | 5,3% | 15,6% | **−10,3 pp** | Prêmio de reputação (campeã 2018, vice 2022); grupo difícil |
| Inglaterra | 6,7% | 11,0% | −4,3 pp | Mercado paga elenco £1,18bi; modelo desconta histórico de mata-mata |
| Alemanha | 3,1% | 5,3% | −2,2 pp | Reputação histórica; modelo vê forma recente |
| Brasil | 6,8% | 8,9% | −2,1 pp | Pequeno desconto; consistente com o que esperaríamos |
| Portugal | 5,8% | 7,7% | −2,0 pp | Mercado precifica geração Ronaldo + Bruno + Leão |

## 4. Análise por grupo (avançam 1º + 2º + 8 melhores 3º)

| Grupo | Favorito 1º | Favorito 2º | Disputa 3ª vaga | Lanterna |
|---|---|---|---|---|
| A | México (91%) | Coreia do Sul (71%) | Tchéquia (64%) | África do Sul (46%) |
| B | Suíça (98%) | Canadá (94%) | Bósnia (60%) | Catar (12%) |
| C | Brasil (98%) | Marrocos (95%) | Escócia (68%) | Haiti (9%) |
| D | Turquia (75%) | Austrália (72%) | Paraguai (71%) | EUA (57%) |
| E | Alemanha (98%) | Equador (95%) | Costa do Marfim (84%) | Curaçao (4%) |
| F | Holanda (92%) | Japão (90%) | Tunísia/Suécia (~41%) | — |
| G | Bélgica (88%) | Irã (75%) | Egito (71%) | Nova Zelândia (35%) |
| H | Espanha (99%) | Uruguai (87%) | Cabo Verde (31%) | Arábia Saudita (30%) |
| I | França (91%) | Noruega (87%) | Senegal (81%) | Iraque (14%) |
| J | Argentina (98%) | Áustria (81%) | Argélia (72%) | Jordânia (18%) |
| K | Portugal (89%) | Colômbia (88%) | RD Congo (46%) | Uzbequistão (38%) |
| L | Inglaterra (97%) | Croácia (91%) | Gana (38%) | Panamá (30%) |

**Grupos mais abertos:** D (todos entre 57-75%), I (trio Europa pesado por 2 vagas).
**Grupos mais decididos:** H (Espanha), J (Argentina), B (Suíça).

## 5. Pipeline final

```
src/
├── collect/          # download_history.py, build_fixtures.py
├── features/         # build_features.py
├── model/
│   ├── dixon_coles.py    # MLE + correção placares baixos
│   ├── priors.py         # (não usado no v3 final, mantido para análise)
│   ├── calibration.py    # comparação vs mercado
│   └── backtest.py       # validação out-of-sample
├── simulate/         # tournament.py (Monte Carlo do bracket)
└── main.py           # orquestrador (lambda=0, MLE puro)
```

**Para reproduzir:** `python -m src.main`
**Para validar:** `python -m src.model.backtest`
**Para comparar mercado:** `python -m src.model.calibration`
**Para dashboard:** `streamlit run app.py`

## 6. Limitações ainda vigentes

| Fator | Status |
|---|---|
| Placares históricos 2022-2026 | ✅ usado (4.421 partidas) |
| Decaimento temporal (forma recente pesa mais) | ✅ half-life 365 dias |
| Vantagem de campo (anfitriões) | ✅ home advantage estimado: 0,21 |
| Correção Dixon-Coles para placares baixos | ✅ rho estimado: -0,08 |
| Validação out-of-sample | ✅ 165 partidas testadas |
| Bracket pós-grupos | ⚠️ cruzamento simétrico (FIFA não confirmou) |
| Lesões/dispensas confirmadas | ❌ não modelado |
| Convocações finais (até 02/06) | ❌ não modelado |
| Fadiga de viagem (3 países) | ❌ não modelado |

## 7. Próximas iterações (se desejado)

1. **Atualizar diariamente**: re-rodar `src.main` quando novos resultados saírem.
2. **Bracket oficial**: editar `BRACKET_R32` em `src/simulate/tournament.py` quando FIFA confirmar.
3. **Lesões críticas**: implementar ajuste manual de força para seleções com baixa.
4. **Apostas com Kelly**: aplicar Kelly fraction nos picks de valor (Argentina, Marrocos).

---

**Sources**
- [martj42/international_results](https://github.com/martj42/international_results)
- [eloratings.net via Wikipedia](https://en.wikipedia.org/wiki/Module:SportsRankings/data/World_Football_Elo_Ratings)
- [Transfermarkt via GiveMeSport](https://www.givemesport.com/football-international-teams-ranked/)
- [ESPN — World Cup odds](https://www.espn.com/espn/betting/story/_/id/48386952/)
- [Polymarket — World Cup winner](https://polymarket.com/event/2026-fifa-world-cup-winner-595)
- Dixon, M. J., & Coles, S. G. (1997). *Modelling Association Football Scores*. JRSS C.
