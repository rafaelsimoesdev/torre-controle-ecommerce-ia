import pandas as pd

from src.demanda.features import criar_features


def _serie():
    return pd.DataFrame({
        "dia": pd.date_range("2026-01-05", periods=60),  # 05/01/2026 é segunda
        "pedidos": range(100, 160),
    })


def test_calendario():
    df = criar_features(_serie())
    assert df["dia_semana"].iloc[0] == 0  # segunda
    assert df["dia_semana"].iloc[6] == 6  # domingo
    assert df["mes"].iloc[0] == 1


def test_lag_nao_usa_o_futuro():
    df = criar_features(_serie())
    # o lag_7 do dia 10 tem que ser exatamente os pedidos do dia 3
    assert df["lag_7"].iloc[10] == df["pedidos"].iloc[3]
