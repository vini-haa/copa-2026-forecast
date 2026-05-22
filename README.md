# Copa 2026 — Pipeline de Previsão

Pipeline reproduzível para prever o campeão da Copa do Mundo 2026 via modelo Dixon-Coles + simulação Monte Carlo de 10.000 torneios.

## Setup

```bash
pip install -r requirements.txt
```

## Execução

```bash
python -m src.collect.download_history     # baixa dataset histórico
python -m src.features.build_features      # prepara base de treino
python -m src.collect.build_fixtures       # extrai fixtures Copa 2026
python -m src.main                         # ajusta modelo + simula + relatório
```

Saída em `results/`:
- `world_cup_probabilities.csv` — probabilidades por rodada
- `team_ratings.csv` — força ataque/defesa estimada
- `RELATORIO_v1.md` — análise consolidada

## Estrutura

```
src/
├── collect/    # download de dados (histórico + fixtures)
├── features/   # construção da base de treino
├── model/      # Dixon-Coles (MLE + correção placares baixos)
├── simulate/   # Monte Carlo do bracket
├── config.py   # grupos da Copa 2026, sedes, aliases
└── main.py     # orquestrador
```

## Resultado v1 (top 10)

| Pos | Seleção    | P(título) |
|-----|------------|----------:|
| 1   | Espanha    | 15,78%    |
| 2   | Argentina  | 14,67%    |
| 3   | Brasil     |  6,79%    |
| 4   | Inglaterra |  6,46%    |
| 5   | Marrocos   |  5,63%    |
| 6   | França     |  5,33%    |
| 7   | Portugal   |  5,32%    |
| 8   | Colômbia   |  4,80%    |
| 9   | Japão      |  4,55%    |
| 10  | Holanda    |  4,13%    |

Detalhes completos em [results/RELATORIO_v1.md](results/RELATORIO_v1.md).
