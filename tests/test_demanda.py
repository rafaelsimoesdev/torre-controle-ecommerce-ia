import pandas as pd

from src.demanda.dados import separar_treino_teste


def test_teste_sao_os_ultimos_dias():
    df = pd.DataFrame({
        "dia": pd.date_range("2026-01-01", periods=100),
        "pedidos": range(100),
    })
    treino, teste = separar_treino_teste(df, dias_teste=28)

    assert len(treino) == 72
    assert len(teste) == 28
    # nenhum dia do treino pode vir depois do teste
    assert treino["dia"].max() < teste["dia"].min()
