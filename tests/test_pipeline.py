from datetime import date

from src.pipeline import diario, telegram
from src.pipeline.frescor import dias_de_atraso


def test_em_dia():
    assert dias_de_atraso(date(2026, 11, 4), hoje=date(2026, 11, 5)) == 0


def test_base_parada_desde_29_10():
    assert dias_de_atraso(date(2026, 10, 29), hoje=date(2026, 11, 5)) == 6


def test_dados_de_hoje_nao_dao_atraso_negativo():
    assert dias_de_atraso(date(2026, 11, 5), hoje=date(2026, 11, 5)) == 0


DIA_NORMAL = {"dia": date(2026, 10, 22), "dias_de_atraso": 0, "pedidos": 237.0,
              "esperado": 236.0, "desvio": 0.004, "anomalia": False, "receita": 15000.5}


def test_status():
    assert diario.status(DIA_NORMAL) == "OK"
    assert diario.status({**DIA_NORMAL, "anomalia": True}) == "ALERTA"
    assert diario.status({**DIA_NORMAL, "dias_de_atraso": 6}) == "ALERTA"


def test_texto_padrao_avisa_atraso_e_anomalia():
    texto = diario.texto_padrao({**DIA_NORMAL, "dias_de_atraso": 6, "anomalia": True, "desvio": -0.85})
    assert texto.startswith("Torre de Controle | ALERTA")
    assert "faltam 6 dia(s)" in texto
    assert "-85%" in texto
    assert "US$ 15.000,50" in texto


def test_relatorio_sai_mesmo_sem_gemini(monkeypatch):
    def gemini_fora(*args, **kwargs):
        raise RuntimeError("503")
    monkeypatch.setattr(diario.llm, "gerar", gemini_fora)
    assert diario.montar_relatorio(DIA_NORMAL).startswith("Torre de Controle | OK")


def test_telegram_em_modo_ensaio(monkeypatch, capsys):
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    assert telegram.enviar("oi") is False
    assert "modo ensaio" in capsys.readouterr().out
