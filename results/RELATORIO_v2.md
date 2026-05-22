# Previsão Copa do Mundo 2026 — Relatório v2 (Bayesiano)

**Data:** 2026-05-22
**Simulações:** 10.000 Monte Carlo
**Modelo:** Dixon-Coles **bayesiano** (prior λ=8.0) com Elo + valor de mercado
**Base de treino:** 4.421 partidas pós-2022

---

## 1. O que mudou da v1 para v2

A v1 estimava ataque/defesa **apenas dos placares históricos** (MLE puro).
A v2 adiciona um **prior bayesiano** que combina:
- **Elo** (eloratings.net) — 244 seleções, sinal estatístico baseado em performance
- **Valor de mercado** (Transfermarkt/GiveMeSport) — 48 seleções da Copa

O prior "puxa" estimativas em direção ao que esperaríamos baseado em qualidade externa,
reduzindo ruído em seleções com poucos jogos no período.

## 2. Top 15 — comparação v1 × v2

| Pos | Seleção        | v1 P(título) | v2 P(título) | Δ |
|----:|----------------|-------------:|-------------:|--:|
| 1  | Espanha         | 15,78% | **15,90%** | +0,12 |
| 2  | Argentina       | 14,67% | **14,02%** | −0,65 |
| 3  | Brasil          |  6,79% |  **6,81%** | +0,02 |
| 4  | Inglaterra      |  6,46% |  **6,72%** | +0,26 |
| 5  | Marrocos        |  5,63% |  **6,15%** | +0,52 |
| 6  | Portugal        |  5,32% |  **5,77%** | +0,45 |
| 7  | França          |  5,33% |  **5,26%** | −0,07 |
| 8  | Colômbia        |  4,80% |  **4,97%** | +0,17 |
| 9  | Japão           |  4,55% |  **4,33%** | −0,22 |
| 10 | Holanda         |  4,13% |  **4,15%** | +0,02 |
| 11 | Suíça           |  4,01% |  **3,59%** | −0,42 |
| 12 | Equador         |  3,47% |  **3,48%** | +0,01 |
| 13 | Alemanha        |  3,42% |  **3,06%** | −0,36 |
| 14 | Noruega         |  3,35% |  **3,16%** | −0,19 |
| 15 | Senegal         |  2,00% |  **1,93%** | −0,07 |

**Interpretação:**
- **Marrocos (+0,52)** e **Portugal (+0,45)** ganharam — o prior reconhece que ambos têm elenco muito acima do que os placares recentes sugerem (Portugal £851M, Marrocos £308M).
- **Argentina (-0,65)** e **Alemanha (-0,36)** caíram — valor de mercado puxa pra baixo (Argentina £631M está atrás de Portugal/Holanda/Itália).
- **Suíça (-0,42)** caiu — Elo era inflado por boa sequência de eliminatórias; valor de mercado real (£231M) é o de uma seleção de meio-tabela europeu.
- Top 4 e estrutura geral preservados — o modelo é estável.

## 3. Top 20 completo

| Pos | Seleção       | Avança | R16  | QF   | SF   | Final | **P(Título)** |
|----:|---------------|-------:|-----:|-----:|-----:|------:|--------------:|
| 1   | Espanha       | 99,5% | 56,3% | 34,8% | 23,6% | 15,9% | **15,90%** |
| 2   | Argentina     | 97,8% | 46,3% | 30,7% | 21,1% | 14,0% | **14,02%** |
| 3   | Brasil        | 97,7% | 46,7% | 27,2% | 14,1% |  6,8% |  **6,81%** |
| 4   | Inglaterra    | 97,2% | 38,3% | 20,6% | 11,9% |  6,7% |  **6,72%** |
| 5   | Marrocos      | 94,8% | 41,5% | 23,5% | 12,2% |  6,2% |  **6,15%** |
| 6   | Portugal      | 88,7% | 35,4% | 22,6% | 11,4% |  5,8% |  **5,77%** |
| 7   | França        | 91,4% | 31,1% | 19,0% | 10,8% |  5,3% |  **5,26%** |
| 8   | Colômbia      | 87,8% | 34,4% | 21,1% | 10,3% |  5,0% |  **4,97%** |
| 9   | Japão         | 90,2% | 28,8% | 16,3% |  9,2% |  4,3% |  **4,33%** |
| 10  | Holanda       | 92,0% | 28,7% | 15,8% |  8,3% |  4,1% |  **4,15%** |
| 11  | Suíça         | 98,3% | 40,2% | 18,3% |  8,7% |  3,6% |  **3,59%** |
| 12  | Equador       | 94,7% | 26,2% | 13,5% |  7,1% |  3,5% |  **3,48%** |
| 13  | Noruega       | 87,3% | 24,5% | 13,2% |  6,8% |  3,2% |  **3,16%** |
| 14  | Alemanha      | 98,1% | 29,0% | 14,6% |  7,2% |  3,1% |  **3,06%** |
| 15  | Senegal       | 81,2% | 19,7% | 10,1% |  4,6% |  1,9% |  **1,93%** |
| 16  | Uruguai       | 86,9% | 24,1% | 10,7% |  3,7% |  1,5% |  **1,53%** |
| 17  | Áustria       | 80,9% | 16,6% |  8,2% |  3,9% |  1,5% |  **1,53%** |
| 18  | Croácia       | 91,1% | 23,1% |  9,9% |  3,6% |  1,3% |  **1,31%** |
| 19  | Bélgica       | 88,0% | 19,1% |  8,5% |  3,2% |  1,0% |  **0,99%** |
| 20  | Canadá        | 93,6% | 19,3% |  6,9% |  2,5% |  0,7% |  **0,70%** |

## 4. Diagnóstico do modelo bayesiano

- **Hiperparâmetro λ=8.0**: tunado empiricamente. λ=0 é v1 puro; λ→∞ ignoraria os dados.
  - λ=4 → quase igual à v1
  - λ=8 → equilibrado (escolhido)
  - λ=20 → reforça Marrocos/Portugal demais e suprime forma recente
- **Top 4** (Espanha + Argentina + Brasil + Inglaterra) = 43,5% das chances combinadas.
- **Top 10** = 73,8%.
- **Probabilidade de zebra (campeão fora do top 10)** = 26,2%.

## 5. Limitações ainda vigentes

| Fator | Status v2 |
|---|---|
| Histórico de placares pós-2022 | ✅ usado |
| Elo (244 seleções) | ✅ usado como prior |
| Valor de mercado (48 seleções) | ✅ usado como prior |
| Vantagem de campo (anfitriões em casa) | ✅ usado |
| Bracket pós-grupos | ⚠️ cruzamento simétrico (FIFA ainda não confirmou) |
| Lesões/dispensas confirmadas | ❌ não modelado |
| Idade média / minutos top-5 ligas | ❌ não modelado |
| Fadiga de viagem (3 países anfitriões) | ❌ não modelado |
| Convocações finais (até 02/06) | ❌ não modelado |

## 6. Arquivos gerados

- `data/raw/market_value_2026.csv` — valores de mercado (Transfermarkt/GiveMeSport + estimativas)
- `data/raw/espn_power_ranking_2026.csv` — ESPN power ranking 1-48
- `src/model/priors.py` — construção do prior Elo + market value
- `src/model/dixon_coles.py` (atualizado) — agora aceita prior bayesiano
- `results/world_cup_probabilities.csv` (v2) — probabilidades atualizadas
- `results/team_ratings.csv` (v2) — ratings ataque/defesa pós-bayesiano

---

**Fontes**
- Histórico de partidas: [martj42/international_results](https://github.com/martj42/international_results) (CC0)
- Elo ratings: [eloratings.net via Wikipedia](https://en.wikipedia.org/wiki/Module:SportsRankings/data/World_Football_Elo_Ratings)
- Market value top 30: [GiveMeSport](https://www.givemesport.com/football-international-teams-ranked/) (cita Transfermarkt)
- Market value pontuais: [beIN Sports](https://www.beinsports.com/en-us/soccer/fifa-world-cup-2026/articles/the-matches-with-the-biggest-squad-value-gaps-at-the-2026-fifa-world-cup-2026-05-14), [ESPN](https://www.espn.com/soccer/story/_/id/48361967/2026-world-cup-squads-ranked-all-48-national-teams-win-tournament)
- Ranking FIFA: [Wikipedia FIFA Men's World Ranking](https://en.wikipedia.org/wiki/FIFA_Men%27s_World_Ranking)
- Dixon, M. J., & Coles, S. G. (1997). *Modelling Association Football Scores and Inefficiencies in the Football Betting Market*. JRSS C.
