"""Variáveis (features) que o modelo de demanda usa para prever.

Regra de ouro: toda informação do histórico é deslocada em pelo menos
7 dias. Assim o modelo só usa o que já seria conhecido uma semana antes,
e pode prever a semana inteira de uma vez, sem "colar" do futuro.
"""

import pandas as pd

FEATURES = [
    "dia_semana", "dia_mes", "mes",
    "lag_7_rel", "lag_14_rel", "media_7_rel",
]


def criar_features(serie: pd.DataFrame) -> pd.DataFrame:
    df = serie.copy()

    # Calendário
    # TODO 1: dia da semana (0 = segunda ... 6 = domingo)
    # dica: df["dia"].dt.dayofweek
    df["dia_semana"] = df["dia"].dt.dayofweek
    # TODO 2: mês do ano (1 a 12)
    # dica: igual ao de cima, mas com .dt.month
    df["mes"] = df["dia"].dt.month
    df["dia_mes"] = df["dia"].dt.day

    # Histórico, sempre com pelo menos 7 dias de atraso
    passado = df["pedidos"].shift(7)
    df["lag_7"] = passado
    df["lag_14"] = df["pedidos"].shift(14)
    df["media_7"] = passado.rolling(7).mean()
    df["media_28"] = passado.rolling(28).mean()

    # Árvores (como o LightGBM) não sabem prever valores maiores do que
    # viram no treino. Como os pedidos crescem, o modelo aprende o tamanho
    # do dia em relação à média das últimas 4 semanas, e não o número bruto.
    df["lag_7_rel"] = df["lag_7"] / df["media_28"]
    df["lag_14_rel"] = df["lag_14"] / df["media_28"]
    df["media_7_rel"] = df["media_7"] / df["media_28"]
    df["alvo"] = df["pedidos"] / df["media_28"]
    return df
