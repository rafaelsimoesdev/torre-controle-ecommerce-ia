# Torre de Controle de E-commerce com IA

**Status:** em construção. Fase 0 de 5.

Sistema que acompanha a operação de uma loja online todo dia: carrega os pedidos novos, calcula indicadores, prevê atrasos de entrega, segmenta clientes, detecta anomalias e escreve um relatório diário com IA. Inclui um assistente que responde perguntas em português consultando o banco de dados.

**Base de dados:** `bigquery-public-data.thelook_ecommerce` (base pública e sintética do Google, com pedidos até a data atual).

## Fases

- [ ] 0. Fundação: Git, repositório, acesso ao BigQuery, esqueleto e CI
- [ ] 1. Dados e SQL: consultas de exploração, tabelas de indicadores, dashboard
- [ ] 2. ML: previsão de atraso, segmentação de clientes, anomalias (MLflow)
- [ ] 3. IA generativa: assistente texto-para-SQL com avaliação e guardrails
- [ ] 4. Automação e MLOps: pipeline diário, drift, relatório no Telegram
- [ ] 5. Vitrine: diagrama, demo, post

## Estrutura

```
├── sql/          # consultas versionadas
├── src/          # código do pipeline, modelos e assistente
├── tests/        # testes automáticos
├── docs/         # gráficos, métricas e diagramas
└── .github/      # CI
```

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # preencha com o seu projeto do GCP
pytest
```
