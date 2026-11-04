import pandas as pd

from src.assistente import assistente
from src.assistente.guardrails import SQLInseguro


def _falsos(monkeypatch, sql, resultado=None, erro=None):
    """Troca o Gemini e o BigQuery por versões falsas: o teste roda sem internet e sem custo."""
    monkeypatch.setattr(assistente, "gerar_sql", lambda p: sql)

    def executar_falso(s):
        if erro:
            raise erro
        return resultado

    monkeypatch.setattr(assistente, "executar", executar_falso)
    monkeypatch.setattr(assistente, "responder", lambda p, s, r: f"total: {r.iloc[0, 0]}")


def test_caminho_feliz(monkeypatch):
    _falsos(monkeypatch, "SELECT 1", resultado=pd.DataFrame({"total": [42]}))
    saida = assistente.perguntar("quanto?")
    assert saida["resposta"] == "total: 42"
    assert saida["sql"] == "SELECT 1"


def test_pergunta_fora_do_escopo(monkeypatch):
    _falsos(monkeypatch, "")
    saida = assistente.perguntar("qual a capital da França?")
    assert "Não consigo responder" in saida["resposta"]
    assert saida["resultado"] is None


def test_sql_barrado_nao_quebra(monkeypatch):
    _falsos(monkeypatch, "DROP TABLE x", erro=SQLInseguro("o comando DROP não é permitido"))
    saida = assistente.perguntar("apague tudo")
    assert "barrada" in saida["resposta"]
    assert "DROP" in saida["resposta"]
