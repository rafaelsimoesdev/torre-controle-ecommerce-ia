"""Série de pedidos por dia usada pelo modelo de previsão de demanda."""

from pathlib import Path

import pandas as pd

from src.bq import consultar

# A partir de 23/10/2026 o gerador da base criou um salto artificial de pedidos
# (de ~240 para 1.625 por dia). Esses dias ficam fora do treino e do teste.
DATA_FIM = "2026-10-22"
DIAS_TESTE = 28     # 4 semanas guardadas para avaliar o modelo

SQL_SERIE = f"""
SELECT DATE(created_at) AS dia, COUNT(*) AS pedidos
FROM `bigquery-public-data.thelook_ecommerce.orders`
WHERE DATE(created_at) >= '2025-01-01'
  AND DATE(created_at) <= '{DATA_FIM}'
GROUP BY dia
ORDER BY dia
"""


def carregar_serie() -> pd.DataFrame:
    """Busca no BigQuery a quantidade de pedidos de cada dia."""
    df = consultar(SQL_SERIE)
    df["dia"] = pd.to_datetime(df["dia"])
    return df


def separar_treino_teste(df: pd.DataFrame, dias_teste: int = DIAS_TESTE):
    """Os últimos `dias_teste` dias viram teste e o resto vira treino.

    Em série temporal não se embaralha os dados: o teste é sempre o futuro,
    porque é isso que o modelo vai enfrentar de verdade.
    """
    # TODO 1: treino = todas as linhas, menos as últimas `dias_teste`
    treino = df.iloc[:-dias_teste]
    # TODO 2: teste = só as últimas `dias_teste` linhas
    teste = df.iloc[-dias_teste:]
    return treino, teste


if __name__ == "__main__":
    serie = carregar_serie()
    Path("dados").mkdir(exist_ok=True)
    serie.to_parquet("dados/serie_pedidos.parquet", index=False)

    treino, teste = separar_treino_teste(serie)
    print(f"Série: {len(serie)} dias, de {serie['dia'].min():%d/%m/%Y} a {serie['dia'].max():%d/%m/%Y}")
    print(f"Treino: {len(treino)} dias | Teste: {len(teste)} dias")
    print(f"Teste começa em {teste['dia'].min():%d/%m/%Y}")
