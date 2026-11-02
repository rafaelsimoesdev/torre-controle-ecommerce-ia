import numpy as np
import pandas as pd

from src.demanda.anomalias import detectar


def _serie_com_salto():
    rng = np.random.default_rng(0)
    dias = pd.date_range("2025-01-01", "2026-10-28")
    nivel = np.linspace(60, 240, len(dias))
    pedidos = rng.normal(nivel, nivel * 0.05)
    pedidos[-6:] = pedidos[-6:] * np.array([1.5, 2, 2.5, 3.5, 4.5, 7])  # o salto artificial
    return pd.DataFrame({"dia": dias, "pedidos": pedidos})


def test_pega_o_salto():
    df = detectar(_serie_com_salto())
    assert df["anomalia"].iloc[-6:].all()


def test_dias_normais_quase_nunca_sao_anomalia():
    df = detectar(_serie_com_salto())
    normais = df.iloc[40:-6]
    assert normais["anomalia"].mean() < 0.01  # menos de 1% de alarme falso
