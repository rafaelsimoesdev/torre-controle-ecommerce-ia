"""Modelo de tendência linear: traça uma reta pelas últimas 4 semanas e prolonga."""

import numpy as np
import pandas as pd

JANELA = 28     # quantos dias conhecidos a reta usa
HORIZONTE = 7   # quantos dias à frente a previsão é feita


def prever_tendencia(historico, horizonte: int = HORIZONTE) -> float:
    """Recebe os pedidos dos últimos dias conhecidos e prevê o dia que fica
    `horizonte` dias depois do último deles."""
    y = np.asarray(historico, dtype=float)
    x = np.arange(len(y))  # 0, 1, 2, ... (a posição de cada dia)
    # TODO 1: ajuste uma reta y = a*x + b aos dados
    # dica: a, b = np.polyfit(x, y, 1)   (o 1 quer dizer "reta", grau 1)
    a, b = np.polyfit(x, y, 1)
    # TODO 2: devolva o valor da reta no dia que queremos prever
    # o último dia conhecido está na posição len(y) - 1; some o horizonte
    return a * (len(y) - 1 + horizonte) + b


def coluna_tendencia(serie: pd.DataFrame, janela: int = JANELA,
                     horizonte: int = HORIZONTE) -> pd.Series:
    """Previsão de tendência para cada dia, usando só dados de `horizonte` dias antes."""
    pedidos = serie["pedidos"].to_numpy()
    previsoes = [np.nan] * len(pedidos)
    for i in range(len(pedidos)):
        fim = i - horizonte          # último dia que já seria conhecido
        inicio = fim - janela + 1
        if inicio >= 0:
            previsoes[i] = prever_tendencia(pedidos[inicio:fim + 1], horizonte)
    return pd.Series(previsoes, index=serie.index)
