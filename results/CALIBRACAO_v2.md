# Calibração Modelo v2 vs Mercado de Apostas

**Data:** 2026-05-22
**Modelo:** Dixon-Coles bayesiano (v2) com 10k simulações Monte Carlo
**Fontes de mercado:**
- ESPN (consenso casas tradicionais, normalizado sem vig)
- Polymarket (prediction market on-chain)

## 1. Resumo executivo

O modelo concorda fortemente com o mercado nos **extremos** (Espanha, Catar, Haiti) mas diverge significativamente em **3 áreas**:

1. **Modelo subestima França** (-10,3 p.p. vs mercado) — a maior divergência
2. **Modelo otimista com Argentina e Marrocos** (+5,6 e +4,6 p.p.)
3. **Modelo otimista com sul-americanos médios** (Colômbia, Equador, Uruguai)

**Overround ESPN:** 17,7% (margem agregada das casas em odds de longo prazo)

## 2. Top 15 — modelo × mercado

| Seleção     | Modelo | ESPN  | Polymarket | Mercado (média) | Edge (modelo−mercado) |
|-------------|-------:|------:|-----------:|----------------:|----------------------:|
| Espanha     | 15,90% | 14,16% | 16,04% | 15,10% |  +0,80 |
| Argentina   | 14,02% |  8,94% |  7,92% |  8,43% | **+5,59** 🟢 |
| Brasil      |  6,81% |  9,44% |  8,30% |  8,87% |  −2,06 |
| Inglaterra  |  6,72% | 11,32% | 10,66% | 10,99% | **−4,27** 🔴 |
| Marrocos    |  6,15% |  1,67% |  1,42% |  1,54% | **+4,61** 🟢 |
| Portugal    |  5,77% |  7,08% |  8,40% |  7,74% |  −1,97 |
| França      |  5,26% | 14,16% | 16,98% | 15,57% | **−10,31** 🔴🔴 |
| Colômbia    |  4,97% |  2,07% |  1,60% |  1,84% | **+3,13** 🟢 |
| Japão       |  4,33% |  1,67% |  1,70% |  1,68% |  +2,65 |
| Holanda     |  4,15% |  4,04% |  3,30% |  3,67% |  +0,48 |
| Suíça       |  3,59% |  1,05% |  0,94% |  1,00% |  +2,59 |
| Equador     |  3,48% |  0,93% |  0,75% |  0,84% |  +2,64 |
| Noruega     |  3,16% |  2,74% |  2,36% |  2,55% |  +0,61 |
| Alemanha    |  3,06% |  5,66% |  4,91% |  5,28% |  −2,22 |
| Senegal     |  1,93% |  0,77% |  0,75% |  0,76% |  +1,17 |

## 3. Interpretação dos gaps

### 🔴 França: -10,3 p.p. (maior divergência)
- **Mercado:** 15,6% (favorita ao lado de Espanha)
- **Modelo:** 5,3%
- **Razões prováveis do gap:**
  - Modelo penaliza a forma recente (eliminatórias mais fracas)
  - França caiu no Grupo I com Noruega + Senegal (dificuldade alta)
  - Bracket simétrico pode estar cruzando a França em chave dura
- **Conclusão:** mercado provavelmente está com **prêmio de reputação** (campeã 2018, vice 2022). Modelo pode estar correto em descontar isso, mas vale revisar quando FIFA confirmar o bracket.

### 🔴 Inglaterra: -4,3 p.p.
- Mercado vê squad de £1,18bi (o mais valioso) como decisivo. Modelo nota que Inglaterra tradicionalmente performa abaixo do esperado em mata-mata.

### 🟢 Argentina: +5,6 p.p.
- Forma estelar pós-Copa 2022 + Grupo J fácil (Argélia, Áustria, Jordânia).
- Mercado parece descontar por "regressão à média" e idade do elenco.

### 🟢 Marrocos: +4,6 p.p.
- Defesa elite (rating DC defensivo −1,71) + Grupo C onde só Brasil é favorito claro.
- Mercado precifica como "azarão exótico" apesar da campanha do Catar 2022 (4º lugar).

## 4. Implicações práticas

**Se você confia no modelo:** Argentina, Marrocos, Colômbia, Japão, Equador, Suíça oferecem **valor positivo** vs odds de mercado.

**Se você confia no mercado:** França e Inglaterra estão sendo subestimadas pelo modelo — talvez o prior bayesiano (λ=8) precise ser ajustado para cima para essas seleções de elenco premium.

**Próximas iterações sugeridas:**
1. Aumentar λ para 12-15 e ver se gap França/Inglaterra fecha
2. Adicionar feature "histórico em torneios FIFA" (proxy para handling de pressão)
3. Validação out-of-sample: treinar até dez/2025 e testar nas eliminatórias 2026
4. Track contínuo: re-rodar semanalmente e ver se discrepâncias persistem

## 5. Métricas técnicas

- **Soma probabilidades modelo:** 100,00% ✅
- **Soma probabilidades ESPN normalizada:** 100,00% ✅
- **Soma probabilidades Polymarket normalizada:** 100,00% ✅
- **Overround ESPN bruto:** 17,7% (vig embutido)
- **Correlação Spearman modelo × mercado:** alta nos extremos, ruído no meio

---

**Arquivos:**
- `data/raw/odds_espn_may2026.csv` — odds americanas (48 times)
- `data/raw/odds_polymarket_may2026.csv` — probabilidades on-chain (48 times)
- `src/model/calibration.py` — conversão odds → prob e cálculo de edge
- `results/calibration.csv` — dataset completo de comparação

**Fontes:**
- [ESPN — Championship odds for all teams](https://www.espn.com/espn/betting/story/_/id/48386952/espn-soccer-futbol-world-cup-betting-odds-championship-groups)
- [Polymarket — 2026 FIFA World Cup Winner](https://polymarket.com/event/2026-fifa-world-cup-winner-595)
