"""Baseline: a previsão de cada dia é o mesmo dia da semana anterior.

É o "modelo" mais simples que faz sentido. Qualquer modelo de verdade
precisa errar menos que ele, senão não vale a complexidade.
"""

import pandas as pd

from src.demanda.dados import separar_treino_teste
from src.demanda.metricas import mae, rmse


def prever_semana_passada(serie: pd.DataFrame) -> pd.Series:
    """Para cada dia, devolve os pedidos de 7 dias antes."""
    return serie["pedidos"].shift(7)


if __name__ == "__main__":
    serie = pd.read_parquet("dados/serie_pedidos.parquet")
    serie["previsao"] = prever_semana_passada(serie)
    _, teste = separar_treino_teste(serie)

    erro_mae = mae(teste["pedidos"], teste["previsao"])
    erro_rmse = rmse(teste["pedidos"], teste["previsao"])
    media = teste["pedidos"].mean()

    print(f"Média de pedidos por dia no teste: {media:.0f}")
    print(f"Baseline | MAE: {erro_mae:.1f} pedidos/dia ({erro_mae / media:.1%} da média)")
    print(f"Baseline | RMSE: {erro_rmse:.1f}")
