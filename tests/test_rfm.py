import numpy as np
import pandas as pd

from src.segmentacao.rfm import escolher_k, preparar


def _rfm():
    rng = np.random.default_rng(0)
    # dois grupos bem diferentes: recentes e gastadores x antigos e econômicos
    a = pd.DataFrame({"recencia": rng.normal(15, 3, 200), "frequencia": 3,
                      "valor": rng.normal(600, 30, 200)})
    b = pd.DataFrame({"recencia": rng.normal(700, 30, 200), "frequencia": 1,
                      "valor": rng.normal(50, 3, 200)})
    return pd.concat([a, b], ignore_index=True)


def test_preparar_deixa_tudo_na_mesma_escala():
    x = preparar(_rfm())
    assert x.shape == (400, 3)
    assert np.allclose(x.mean(axis=0), 0, atol=1e-9)
    assert np.allclose(x.std(axis=0), 1, atol=1e-9)


def test_escolher_k_acha_os_dois_grupos():
    notas = escolher_k(preparar(_rfm()))
    assert set(notas) == set(range(2, 9))
    assert max(notas, key=notas.get) == 2


def test_nomear_grupos():
    import pandas as pd
    from src.segmentacao.rfm import nomear_grupos
    tabela = pd.DataFrame({"recencia": [360, 1500, 360], "valor": [230, 95, 78]}, index=[1, 0, 2])
    assert nomear_grupos(tabela) == {1: "Fiéis", 0: "Inativos", 2: "Ocasionais"}
