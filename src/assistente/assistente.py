"""Assistente da Torre de Controle: pergunta em português -> SQL -> BigQuery -> resposta.

Fluxo:
1. o Gemini lê o contexto das tabelas e escreve o SQL
2. os guardrails conferem se o SQL é seguro
3. o BigQuery estima o custo (dry run) e, se estiver ok, roda a consulta
4. o Gemini lê o resultado e responde em português
"""

import sys

import pandas as pd
from google.cloud import bigquery
from pydantic import BaseModel

from src.assistente import llm
from src.assistente.contexto import montar_contexto
from src.assistente.guardrails import SQLInseguro, validar
from src.bq import cliente

MAXIMO_BYTES = 1_000_000_000  # 1 GB por pergunta: barra consultas caras demais


class ConsultaSQL(BaseModel):
    sql: str


def gerar_sql(pergunta: str) -> str:
    prompt = f"""Você é um analista de dados que escreve SQL para o BigQuery (GoogleSQL).

{montar_contexto()}

Escreva UMA consulta SELECT que responda à pergunta abaixo.
- Use só as tabelas e colunas listadas acima, com os nomes completos entre crases.
- Datas em formato 'AAAA-MM-DD'.
- Arredonde valores em dinheiro e taxas com ROUND(..., 2).
- Se a pergunta não puder ser respondida com essas tabelas, devolva sql vazio.

Pergunta: {pergunta}"""
    return llm.gerar(prompt, esquema=ConsultaSQL).sql.strip()


def executar(sql: str) -> pd.DataFrame:
    """Passa pelos guardrails, estima o custo e só então roda."""
    seguro = validar(sql)
    bq = cliente()
    estimativa = bq.query(seguro, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
    if estimativa.total_bytes_processed > MAXIMO_BYTES:
        gb = estimativa.total_bytes_processed / 1e9
        raise SQLInseguro(f"a consulta leria {gb:.1f} GB, acima do limite de 1 GB")
    return bq.query(seguro).to_dataframe()


def responder(pergunta: str, sql: str, resultado: pd.DataFrame) -> str:
    tabela = resultado.head(30).to_string(index=False) if len(resultado) else "(nenhuma linha)"
    prompt = f"""Você é o assistente da torre de controle de um e-commerce.
Responda à pergunta em português, com uma ou duas frases completas, usando SÓ os números do resultado.
- Não invente números nem faça contas que não estão no resultado.
- Escreva números no formato brasileiro: 1.234,56.
- Dinheiro sempre com US$ na frente. Taxas de 0 a 1 viram porcentagem (0,153 vira 15,3%).
- Exemplo de resposta: "A receita de setembro de 2026 foi de US$ 360.788,19."

Pergunta: {pergunta}
SQL usado: {sql}
Resultado:
{tabela}"""
    return llm.gerar(prompt)


def perguntar(pergunta: str) -> dict:
    """Junta as 3 etapas. Devolve a resposta, o SQL usado e o resultado (para conferência)."""
    sql = gerar_sql(pergunta)
    if not sql:
        return {"resposta": "Não consigo responder isso com os dados disponíveis.", "sql": "", "resultado": None}

    try:
        resultado = executar(sql)
    except SQLInseguro as erro:
        return {"resposta": f"Consulta barrada pela segurança: {erro}", "sql": sql, "resultado": None}

    resposta = responder(pergunta, sql, resultado)
    return {"resposta": resposta, "sql": sql, "resultado": resultado}
    

if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or "Qual foi a receita total de setembro de 2026?"
    saida = perguntar(pergunta)
    print(f"Pergunta: {pergunta}\n")
    print(f"SQL:\n{saida['sql']}\n")
    print(f"Resposta: {saida['resposta']}")
