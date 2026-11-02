import pandas as pd
import pytest

from src.demanda.tendencia import coluna_tendencia, prever_tendencia


def test_reta_perfeita_e_prevista_exatamente():
    historico = [10 + 2 * x for x in range(28)]  # 10, 12, 14, ... (sobe 2 por dia)
    # último valor é 64 (posição 27); 7 dias depois: 64 + 7 * 2 = 78
    assert prever_tendencia(historico, horizonte=7) == pytest.approx(78)


def test_serie_parada_preve_o_mesmo_valor():
    assert prever_tendencia([50] * 28, horizonte=7) == pytest.approx(50)


def test_coluna_nao_usa_o_futuro():
    serie = pd.DataFrame({"pedidos": [10 + 2 * x for x in range(60)]})
    prev = coluna_tendencia(serie, janela=28, horizonte=7)
    assert prev.iloc[:34].isna().all()  # sem 28 dias conhecidos, não há previsão
    assert prev.iloc[40] == pytest.approx(serie["pedidos"].iloc[40])
