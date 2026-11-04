"""Guardrails: conferem se o SQL escrito pelo Gemini é seguro antes de rodar.

A IA pode errar ou ser enganada por uma pergunta maliciosa. Por isso o
SQL nunca vai direto para o banco: ele passa por estas travas primeiro.
"""

import re

from src.assistente.contexto import TABELAS

LIMITE_LINHAS = 1000

# TODO 1: complete a lista com os comandos que alteram ou apagam dados.
# Já tem 3; acrescente pelo menos estes: UPDATE, DROP, ALTER, TRUNCATE, CREATE
PALAVRAS_PROIBIDAS = ["INSERT", "DELETE", "MERGE","UPDATE","DROP","ALTER","TRUNCATE","CREATE"]


class SQLInseguro(Exception):
    """O SQL foi barrado por uma das travas."""


def _sem_comentarios(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", " ", sql)          # comentários de uma linha
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)  # comentários de várias linhas
    return sql.strip()


def tabelas_usadas(sql: str) -> set[str]:
    """Nomes de tabela que aparecem depois de FROM ou JOIN."""
    nomes = re.findall(r"\b(?:FROM|JOIN)\s+`?([\w.-]+)`?", sql, flags=re.I)
    return {n.lower() for n in nomes}


def validar(sql: str) -> str:
    """Devolve o SQL pronto para rodar, ou levanta SQLInseguro explicando o motivo."""
    limpo = _sem_comentarios(sql).rstrip(";").strip()
    maiusculo = limpo.upper()

    # Trava 1: só leitura
    # TODO 2: se o SQL não começar com "SELECT" nem com "WITH", barre.
    # dica: if not (maiusculo.startswith("SELECT") or maiusculo.startswith("WITH")):
    #           raise SQLInseguro("só consultas de leitura (SELECT) são permitidas")
    if not (maiusculo.startswith("SELECT") or maiusculo.startswith("WITH")):
        raise SQLInseguro("só consultas de leitura (SELECT) são permitidas")

    # Trava 2: nenhum comando perigoso
    for palavra in PALAVRAS_PROIBIDAS:
        if re.search(rf"\b{palavra}\b", maiusculo):
            raise SQLInseguro(f"o comando {palavra} não é permitido")

    # Trava 3: um comando só
    if ";" in limpo:
        raise SQLInseguro("só um comando por vez")

    # Trava 4: só as tabelas permitidas (os nomes do WITH contam como permitidos)
    permitidas = {t.lower() for t in TABELAS}
    apelidos_with = {a.lower() for a in re.findall(r"(\w+)\s+AS\s*\(", limpo, flags=re.I)}
    for tabela in tabelas_usadas(limpo):
        if tabela not in permitidas and tabela not in apelidos_with:
            raise SQLInseguro(f"a tabela {tabela} não está liberada para o assistente")

    # Trava 5: limite de linhas
    return f"SELECT * FROM (\n{limpo}\n) LIMIT {LIMITE_LINHAS}"
