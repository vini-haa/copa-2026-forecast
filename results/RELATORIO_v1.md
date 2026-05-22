# Previsão Copa do Mundo 2026 — Relatório v1

**Data:** 2026-05-22
**Simulações:** 10.000 Monte Carlo
**Base de treino:** 4.421 partidas internacionais (2022-01-01 a 2026-03-31)
**Modelo:** Dixon-Coles com pesos exponenciais (half-life 365 dias) + correção para placares baixos

---

## 1. Metodologia em uma página

1. **Coleta**: dataset público `martj42/international_results` (49.329 partidas desde 1872, atualizado até 2026), Elo ratings de eloratings.net (244 seleções), ranking FIFA de abril/2026 (top 20).
2. **Filtro de treino**: apenas partidas desde 2022 (ciclo da Copa do Catar até agora). Jogos mais recentes pesam mais via decaimento exponencial (`half_life=365` dias).
3. **Modelo Dixon-Coles**: estima por MLE um parâmetro de **ataque** e **defesa** por seleção, mais um **home advantage** (γ=0.21) e um parâmetro **ρ** (-0.08) que corrige a correlação de placares baixos (0-0, 1-0, 0-1, 1-1) que Poisson independente subestima.
4. **Simulação Monte Carlo**: 10.000 torneios completos:
   - Cada partida de grupo: amostra (gols casa, gols fora) da matriz Dixon-Coles
   - Critério grupo: pontos → saldo → gols pró → sorteio
   - 8 melhores 3º colocados via mesma régua
   - Mata-mata (R32 → R16 → QF → SF → F): prorrogação simulada como meio tempo extra; pênaltis = 50/50
5. **Limitações conhecidas**:
   - Bracket pós-grupos usa um cruzamento simétrico padrão — a FIFA ainda não divulgou cruzamento oficial; quando confirmar, basta editar `BRACKET_R32`.
   - Não inclui lesões, escalações nem fadiga de viagem.
   - Não modela explicitamente vantagem de campo do trio anfitrião (México/EUA/Canadá) além do `home_advantage` quando jogam no próprio país.

---

## 2. Top 20 — Probabilidades de título

| Pos | Seleção        | Avança grupo | R16   | Quartas | Semis | Final | **Título** |
|----:|----------------|-------------:|------:|--------:|------:|------:|-----------:|
| 1  | Espanha         | 99,5% | 56,2% | 34,9% | 23,9% | 15,8% | **15,78%** |
| 2  | Argentina       | 97,7% | 46,4% | 30,9% | 21,7% | 14,7% | **14,67%** |
| 3  | Brasil          | 97,6% | 46,6% | 27,8% | 14,1% |  6,8% |  **6,79%** |
| 4  | Inglaterra      | 97,3% | 38,0% | 20,9% | 12,0% |  6,5% |  **6,46%** |
| 5  | Marrocos        | 94,8% | 41,0% | 23,7% | 11,6% |  5,6% |  **5,63%** |
| 6  | França          | 91,1% | 30,9% | 18,8% | 10,6% |  5,3% |  **5,33%** |
| 7  | Portugal        | 88,7% | 35,8% | 22,2% | 11,2% |  5,3% |  **5,32%** |
| 8  | Colômbia        | 88,0% | 34,8% | 20,9% | 10,0% |  4,8% |  **4,80%** |
| 9  | Japão           | 90,2% | 29,7% | 16,4% |  9,4% |  4,6% |  **4,55%** |
| 10 | Holanda         | 92,3% | 28,8% | 15,8% |  8,3% |  4,1% |  **4,13%** |
| 11 | Suíça           | 98,4% | 40,3% | 18,5% |  9,4% |  4,0% |  **4,01%** |
| 12 | Equador         | 94,6% | 26,2% | 13,6% |  7,0% |  3,5% |  **3,47%** |
| 13 | Alemanha        | 98,4% | 29,4% | 15,3% |  7,7% |  3,4% |  **3,42%** |
| 14 | Noruega         | 87,8% | 24,5% | 13,5% |  6,8% |  3,4% |  **3,35%** |
| 15 | Senegal         | 81,2% | 20,2% | 10,2% |  4,8% |  2,0% |  **2,00%** |
| 16 | Uruguai         | 86,2% | 22,7% | 10,1% |  3,7% |  1,6% |  **1,63%** |
| 17 | Croácia         | 91,1% | 23,3% | 10,0% |  3,6% |  1,3% |  **1,34%** |
| 18 | Áustria         | 81,2% | 16,3% |  7,8% |  3,3% |  1,2% |  **1,22%** |
| 19 | Bélgica         | 87,5% | 18,9% |  8,1% |  3,0% |  1,1% |  **1,05%** |
| 20 | Argélia         | 72,6% | 12,4% |  5,2% |  1,9% |  0,7% |  **0,66%** |

**Probabilidade combinada do "top 4" levar o título: ~43,7%**
**Sul-Americanos (Argentina + Brasil + Colômbia + Uruguai + Equador + Paraguai): ~28,8%**
**Europeus: ~58,3%**

---

## 3. Análise por grupo — quem avança

### Grupo A (Fácil — México grande favorito)
- **México 90,8%** — anfitrião joga em casa, ataque sólido (CDMX).
- **Coreia do Sul 71,0%** — segunda vaga provável.
- **Tchéquia 63,6%** — repescada com elenco competitivo.
- **África do Sul 45,7%** — pode brigar pela 3ª vaga.

### Grupo B (Suíça com folga)
- **Suíça 98,4%** — a mais sólida defensivamente fora do top 10.
- **Canadá 93,9%** — manda em casa.
- **Bósnia 60,0%** vs **Catar 12,3%** — Bósnia bem cotada.

### Grupo C ("Grupo da morte" sul-americano)
- **Brasil 97,6%** e **Marrocos 94,8%** quase certos.
- **Escócia 68,6%** disputa 3ª vaga com **Haiti (8,8%)**.
- Marrocos pode ser pedra no sapato do Brasil no R16 se trocarem posições.

### Grupo D (O mais aberto do torneio)
- Todos com avanço entre 58% e 74%. **Turquia 74,0%**, **Austrália 71,4%**, **Paraguai 71,1%**, **EUA 58,1%**.
- EUA decepciona pelo modelo — Elo dos últimos amistosos cobrou caro.

### Grupo E (Alemanha vs Equador)
- **Alemanha 98,4%** e **Equador 94,6%** — Equador é a maior surpresa do top 15.
- **Costa do Marfim 83,8%** briga forte pela 3ª vaga.
- **Curaçao 3,6%** — improvável avançar.

### Grupo F (Holanda x Japão pela ponta)
- **Holanda 92,3%** e **Japão 90,2%** quase empatados.
- **Tunísia 41,4%** vs **Suécia 40,9%** — disputa apertada pela 3ª vaga.

### Grupo G (Bélgica favorita; Irã pode surpreender)
- **Bélgica 87,5%**, **Irã 75,0%**, **Egito 70,7%**, **Nova Zelândia 34,3%**.

### Grupo H (Espanha esmagadora)
- **Espanha 99,5%** — passe garantido.
- **Uruguai 86,2%** — segunda vaga praticamente sua.
- **Cabo Verde 31,4%** vs **Arábia Saudita 30,0%** disputam 3ª vaga.

### Grupo I (Trio europeu pesado)
- **França 91,1%**, **Noruega 87,8%**, **Senegal 81,2%** — três fortes para duas vagas + provável melhor 3º.
- **Iraque 13,4%** — pouco competitivo.

### Grupo J (Argentina dominando)
- **Argentina 97,7%** lidera o grupo mais "amigável" entre os favoritos.
- **Áustria 81,2%** e **Argélia 72,6%** disputam 2ª vaga.

### Grupo K (Quarteto equilibrado)
- **Portugal 88,7%** e **Colômbia 88,0%** quase empatados na ponta.
- **RD Congo 46,6%** vs **Uzbequistão 37,3%** disputam 3ª vaga.

### Grupo L (Inglaterra ampla favorita)
- **Inglaterra 97,3%**, **Croácia 91,1%**.
- **Gana 38,2%** vs **Panamá 30,2%** brigam pela 3ª vaga.

---

## 4. Conclusões

- **Top 4 favoritos** (Espanha, Argentina, Brasil, Inglaterra) somam ~44% das chances de título. Modelo é sensível ao caminho do bracket — Espanha e Argentina caíram nos grupos mais favoráveis.
- **Marrocos** continua a ser o "azarão de elite": defesa entre as melhores do mundo (rating defensivo ~-1.71) e ataque competitivo o coloca à frente da França nas simulações.
- **Equador surpresa**: defesa elite (-1.80) compensa ataque modesto. Pode ser a melhor aposta de valor para fase final.
- **EUA decepciona**: apesar de ser anfitrião, modelo penaliza forma recente. Vantagem de campo modesta no Grupo D.

---

## 5. Arquivos gerados

- `results/team_ratings.csv` — força ataque/defesa Dixon-Coles de todos os times
- `results/world_cup_probabilities.csv` — probabilidades por rodada para cada seleção
- `data/processed/training_matches.csv` — base de treino
- `data/processed/wc2026_fixtures.csv` — 72 jogos da fase de grupos

## 6. Próximas iterações sugeridas

1. **Adicionar features de elenco**: valor de mercado, idade média, % minutos em ligas top-5 europeias.
2. **Modelar lesões**: penalizar atributos de seleções com lesão de jogador-chave (pesquisar Transfermarkt + listas de convocados).
3. **Calibrar contra mercados de apostas**: comparar P(título) com odds implícitas (Bet365/Pinnacle) para detectar valor.
4. **Bracket oficial**: substituir `BRACKET_R32` quando a FIFA confirmar os cruzamentos.
5. **Análise por jogador**: top scorer, melhor goleiro, time da copa — necessita scraping de dados individuais.

---

**Fontes**
- [Dataset histórico (martj42)](https://github.com/martj42/international_results)
- [Elo ratings (eloratings.net via Wikipedia)](https://en.wikipedia.org/wiki/Module:SportsRankings/data/World_Football_Elo_Ratings)
- [FIFA Men's World Ranking](https://en.wikipedia.org/wiki/FIFA_Men%27s_World_Ranking)
- Dixon, M. J., & Coles, S. G. (1997). *Modelling Association Football Scores and Inefficiencies in the Football Betting Market*. JRSS Series C.
