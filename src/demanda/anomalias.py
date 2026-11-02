"""Detecção de anomalias nos pedidos por dia.

A tendência linear diz quantos pedidos eram esperados em cada dia. Quando
o número real se afasta demais do esperado, o dia vira anomalia.

"Demais" é medido em relação ao ruído normal da série: calculamos quanto
os dias costumam se desviar do esperado e marcamos só quem foge muito
desse padrão. Usamos a mediana em vez da média porque ela não é puxada
pelas próprias anomalias.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.bq import consultar
from src.demanda.tendencia import coluna_tendencia

LIMITE = 3.5   # quantos "desvios normais" um dia precisa fugir para ser anomalia
INICIO_REFERENCIA = "2025-03-01"
FIM_REFERENCIA = "2026-10-22"  # período usado para medir o ruído normal

SQL_SERIE_COMPLETA = """
SELECT DATE(created_at) AS dia, COUNT(*) AS pedidos
FROM `bigquery-public-data.thelook_ecommerce.orders`
WHERE DATE(created_at) >= '2025-01-01'
  AND DATE(created_at) < CURRENT_DATE()
GROUP BY dia
ORDER BY dia
"""


def carregar_serie_completa() -> pd.DataFrame:
    """Série até ontem, sem cortar o salto: aqui ele é justamente o que queremos achar."""
    df = consultar(SQL_SERIE_COMPLETA)
    df["dia"] = pd.to_datetime(df["dia"])
    return df


def detectar(serie: pd.DataFrame, limite: float = LIMITE) -> pd.DataFrame:
    df = serie.copy()
    df["esperado"] = coluna_tendencia(df)

    # TODO 1: desvio relativo = quanto o real fugiu do esperado, em proporção
    # exemplo: real 120 e esperado 100 dá 0.2 (20% acima)
    # dica: df["pedidos"] / df["esperado"] - 1
    df["desvio"] = df["pedidos"] / df["esperado"] - 1

    referencia = df[(df["dia"] >= INICIO_REFERENCIA) & (df["dia"] <= FIM_REFERENCIA)]
    centro = referencia["desvio"].median()
    # MAD: a mediana das distâncias até o centro. O 1.4826 deixa na mesma escala do desvio padrão.
    escala = 1.4826 * (referencia["desvio"] - centro).abs().median()
    df["nota"] = (df["desvio"] - centro) / escala

    # TODO 2: é anomalia quando a nota, sem sinal, passa do limite
    # dica: df["nota"].abs() > limite
    df["anomalia"] = df["nota"].abs() > limite
    return df


def grafico(df: pd.DataFrame, caminho: str) -> None:
    ultimos = df[df["dia"] >= df["dia"].max() - pd.Timedelta(days=120)]
    marcados = ultimos[ultimos["anomalia"]]
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
    ax.plot(ultimos["dia"], ultimos["pedidos"], color="#9AA7B4", lw=1.2, label="Pedidos reais")
    ax.plot(ultimos["dia"], ultimos["esperado"], color="#F2A900", lw=2, label="Esperado (tendência)")
    ax.scatter(marcados["dia"], marcados["pedidos"], color="#FF5D5D", s=40, zorder=3, label="Anomalia")
    ax.set_yscale("log")
    ax.set_title("Detecção de anomalias: últimos 120 dias (escala logarítmica)", loc="left")
    ax.set_ylabel("Pedidos por dia")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    Path(caminho).parent.mkdir(exist_ok=True)
    fig.savefig(caminho)


if __name__ == "__main__":
    resultado = detectar(carregar_serie_completa())
    anomalias = resultado[resultado["anomalia"]]

    print(f"{len(anomalias)} dias marcados como anomalia:\n")
    print(anomalias[["dia", "pedidos", "esperado", "desvio", "nota"]]
          .assign(dia=lambda d: d["dia"].dt.strftime("%d/%m/%Y"),
                  esperado=lambda d: d["esperado"].round(0),
                  desvio=lambda d: (d["desvio"] * 100).round(0).astype(int).astype(str) + "%",
                  nota=lambda d: d["nota"].round(1))
          .to_string(index=False))

    grafico(resultado, "docs/anomalias.png")
    print("\nGráfico salvo em docs/anomalias.png")
