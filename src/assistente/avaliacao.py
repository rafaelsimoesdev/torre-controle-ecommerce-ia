"""Avaliação do assistente: quantas perguntas do conjunto ele acerta.

Para cada pergunta, roda o SQL certo e o SQL que o assistente escreveu,
e compara os RESULTADOS (não o texto do SQL): duas consultas diferentes
podem chegar ao mesmo número, e isso conta como acerto.
"""

import time
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd

from src.assistente import llm
from src.assistente.assistente import executar, gerar_sql
from src.assistente.guardrails import SQLInseguro, validar
from src.assistente.perguntas_avaliacao import PERGUNTAS

PAUSA_SEGUNDOS = 5  # respeita o limite de chamadas por minuto do plano grátis do Gemini


def _valores(coluna: pd.Series):
    """Valores da coluna prontos para comparar: números ou textos, em ordem."""
    numeros = pd.to_numeric(coluna, errors="coerce")
    if numeros.notna().all():
        return "numero", np.sort(numeros.to_numpy(dtype=float))
    return "texto", sorted(coluna.astype(str).str.strip().str.lower())


def colunas_batem(certa: pd.Series, outra: pd.Series) -> bool:
    tipo_a, a = _valores(certa)
    tipo_b, b = _valores(outra)
    if tipo_a != tipo_b or len(a) != len(b):
        return False
    if tipo_a == "numero":
        return bool(np.allclose(a, b, rtol=0.01, atol=0.01))  # até 1% de diferença (arredondamentos)
    return a == b


def resultado_correto(certo: pd.DataFrame, do_assistente: pd.DataFrame) -> bool:
    """Acerta se cada coluna da resposta certa aparece em alguma coluna do assistente.
    O nome da coluna não importa, só os valores."""
    if do_assistente is None or len(do_assistente) != len(certo):
        return False
    return all(
        any(colunas_batem(certo[c], do_assistente[o]) for o in do_assistente.columns)
        for c in certo.columns
    )


def avaliar_uma(caso: dict) -> dict:
    pergunta = caso["pergunta"]
    try:
        sql = gerar_sql(pergunta)
    except Exception as erro:
        return {"pergunta": pergunta, "acertou": False, "motivo": f"erro no Gemini: {erro}", "sql": ""}

    if caso.get("esperado") == "recusa":
        if not sql:
            return {"pergunta": pergunta, "acertou": True, "motivo": "recusou (SQL vazio)", "sql": ""}
        try:
            validar(sql)
        except SQLInseguro as erro:
            return {"pergunta": pergunta, "acertou": True, "motivo": f"barrado: {erro}", "sql": sql}
        return {"pergunta": pergunta, "acertou": False, "motivo": "deveria ter recusado", "sql": sql}

    if not sql:
        return {"pergunta": pergunta, "acertou": False, "motivo": "recusou uma pergunta válida", "sql": ""}
    try:
        certo = executar(caso["sql"])
    except Exception as erro:
        return {"pergunta": pergunta, "acertou": False, "motivo": f"SQL CERTO com erro (corrija o gabarito): {erro}", "sql": sql}
    try:
        do_assistente = executar(sql)
    except Exception as erro:
        return {"pergunta": pergunta, "acertou": False, "motivo": f"SQL do assistente falhou: {erro}", "sql": sql}

    acertou = resultado_correto(certo, do_assistente)
    return {"pergunta": pergunta, "acertou": acertou,
            "motivo": "resultado igual" if acertou else "resultado diferente", "sql": sql}


if __name__ == "__main__":
    resultados = []
    for i, caso in enumerate(PERGUNTAS, start=1):
        print(f"[{i}/{len(PERGUNTAS)}] {caso['pergunta']}")
        r = avaliar_uma(caso)
        print(f"    {'OK ' if r['acertou'] else 'ERRO'} {r['motivo']}")
        resultados.append(r)
        time.sleep(PAUSA_SEGUNDOS)

    tabela = pd.DataFrame(resultados)
    # erro de disponibilidade (o Gemini não respondeu) é diferente de erro de qualidade
    tabela["indisponivel"] = tabela["motivo"].str.startswith("erro no Gemini")
    acertos = int(tabela["acertou"].sum())
    total = len(tabela)
    respondidas = int((~tabela["indisponivel"]).sum())
    print(f"\nAcertou {acertos} de {total} ({acertos / total:.0%})")
    print(f"Qualidade: {acertos} de {respondidas} perguntas que o Gemini respondeu "
          f"({acertos / max(respondidas, 1):.0%})")
    print(f"Disponibilidade: {respondidas} de {total} perguntas respondidas ({respondidas / total:.0%})")

    Path("dados").mkdir(exist_ok=True)
    tabela.to_csv("dados/avaliacao_assistente.csv", index=False)

    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("assistente-sql")
    with mlflow.start_run(run_name="avaliacao"):
        mlflow.log_param("modelos", ", ".join(llm.MODELOS))
        mlflow.log_param("perguntas", total)
        mlflow.log_metric("acuracia", acertos / total)
        mlflow.log_metric("acuracia_respondidas", acertos / max(respondidas, 1))
        mlflow.log_metric("disponibilidade", respondidas / total)
        mlflow.log_artifact("dados/avaliacao_assistente.csv")

    erros = tabela[~tabela["acertou"]]
    if len(erros):
        print("\nErros para investigar:")
        for _, linha in erros.iterrows():
            print(f"- {linha['pergunta']}\n  motivo: {linha['motivo']}\n  sql: {linha['sql']}")
