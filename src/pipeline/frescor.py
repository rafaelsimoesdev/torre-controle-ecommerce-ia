"""Checagem de frescor: os dados de ontem chegaram?

Um pipeline que roda com dados velhos produz relatórios errados sem
ninguém perceber. Por isso a primeira coisa do dia é conferir a data
mais recente que existe na base.
"""

from datetime import date

from src.bq import consultar

SQL_ULTIMO_DIA = """
SELECT MAX(DATE(created_at)) AS ultimo_dia
FROM `bigquery-public-data.thelook_ecommerce.orders`
"""


def ultimo_dia_com_dados() -> date:
    return consultar(SQL_ULTIMO_DIA)["ultimo_dia"].iloc[0]


def dias_de_atraso(ultimo_dia: date, hoje: date) -> int:
    """Quantos dias faltam na base. O esperado é ter dados até ontem.

    Exemplos: hoje 05/11 e último dia 04/11 -> 0 (em dia)
              hoje 05/11 e último dia 29/10 -> 6 (faltam 30/10 a 04/11)
    """
    # TODO: calcule os dias de atraso.
    # dica: (hoje - ultimo_dia).days dá a distância em dias entre as datas.
    #       Como o esperado é ter dados até ONTEM, desconte 1.
    #       Se a base tiver até hoje (distância 0), não pode dar negativo: use max(..., 0).
    return max((hoje - ultimo_dia).days - 1, 0)
