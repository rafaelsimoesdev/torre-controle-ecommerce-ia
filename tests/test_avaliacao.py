import pandas as pd

from src.assistente.avaliacao import colunas_batem, resultado_correto
from src.assistente.perguntas_avaliacao import PERGUNTAS


def test_nome_da_coluna_nao_importa():
    certo = pd.DataFrame({"f0_": [360788.19]})
    assistente = pd.DataFrame({"receita_total": [360788.19]})
    assert resultado_correto(certo, assistente)


def test_arredondamento_pequeno_e_aceito():
    assert colunas_batem(pd.Series([360788.1934]), pd.Series([360788.19]))


def test_numero_errado_e_recusado():
    assert not colunas_batem(pd.Series([360788.19]), pd.Series([300000.0]))


def test_ordem_das_linhas_nao_importa():
    certo = pd.DataFrame({"category": ["Jeans", "Swim"], "receita": [302204.19, 152911.84]})
    assistente = pd.DataFrame({"categoria": ["Swim", "Jeans"], "total": [152911.84, 302204.19], "extra": [1, 2]})
    assert resultado_correto(certo, assistente)


def test_quantidade_de_linhas_diferente_e_erro():
    assert not resultado_correto(pd.DataFrame({"a": [1, 2]}), pd.DataFrame({"a": [1]}))


def test_conjunto_de_perguntas_completo():
    assert len(PERGUNTAS) == 25
    for caso in PERGUNTAS:
        assert caso.get("esperado") == "recusa" or "SELECT" in caso["sql"], caso["pergunta"]
