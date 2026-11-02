"""Métricas de erro usadas para comparar os modelos de demanda."""

import numpy as np


def mae(real, previsto) -> float:
    """Erro médio absoluto: em média, quantos pedidos o modelo erra por dia."""
    real, previsto = np.asarray(real), np.asarray(previsto)
    # TODO 1: média do valor absoluto de (real - previsto)
    # dica: np.abs(...) e np.mean(...)
    return np.mean(np.abs(real - previsto))


def rmse(real, previsto) -> float:
    """Raiz do erro quadrático médio: pune mais os erros grandes."""
    real, previsto = np.asarray(real), np.asarray(previsto)
    # TODO 2: raiz quadrada da média de (real - previsto) ao quadrado
    # dica: np.sqrt(...), np.mean(...) e ** 2
    return np.sqrt(np.mean((real - previsto) ** 2))
