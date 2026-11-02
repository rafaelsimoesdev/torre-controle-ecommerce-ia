"""Compara os modelos de demanda em vários períodos (backtest) e registra no MLflow.

Em vez de avaliar só no último mês, o backtest repete o teste em 6 períodos
de 28 dias. Cada modelo é avaliado como se estivesse no passado, treinando
só com o que já era conhecido. Assim, um resultado bom não é sorte.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd

from src.demanda.features import criar_features
from src.demanda.metricas import mae, rmse
from src.demanda.modelo import PARAMETROS, prever, treinar
from src.demanda.tendencia import coluna_tendencia

PERIODOS = 6
DIAS = 28
NOMES = {
    "baseline": "Semana passada (baseline)",
    "media_7": "Média dos últimos 7 dias",
    "lightgbm": "LightGBM",
    "tendencia": "Tendência linear (4 semanas)",
}


def rodar_backtest(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for k in range(PERIODOS):
        fim = len(df) - DIAS * k
        teste = df.iloc[fim - DIAS:fim]
        treino = df.iloc[:fim - DIAS]
        previsoes = {
            "baseline": teste["lag_7"],
            "media_7": teste["media_7"],
            "lightgbm": prever(treinar(treino), teste),
            "tendencia": teste["tendencia"],
        }
        for modelo, prev in previsoes.items():
            linhas.append({
                "periodo": f"{teste['dia'].min():%d/%m} a {teste['dia'].max():%d/%m/%Y}",
                "modelo": modelo,
                "mae": mae(teste["pedidos"], prev),
                "rmse": rmse(teste["pedidos"], prev),
            })
    return pd.DataFrame(linhas)


def grafico(df: pd.DataFrame, caminho: str) -> None:
    ultimos = df.iloc[-90:]
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
    ax.plot(ultimos["dia"], ultimos["pedidos"], color="#9AA7B4", lw=1.2, label="Pedidos reais")
    ax.plot(ultimos["dia"], ultimos["lag_7"], color="#5B7A99", lw=1, ls="--", label=NOMES["baseline"])
    ax.plot(ultimos["dia"], ultimos["tendencia"], color="#F2A900", lw=2, label=NOMES["tendencia"])
    ax.axvspan(ultimos["dia"].iloc[-DIAS], ultimos["dia"].iloc[-1], color="#F2A900", alpha=0.08)
    ax.set_title("Previsão de pedidos por dia: últimos 90 dias (faixa = período de teste)", loc="left")
    ax.set_ylabel("Pedidos por dia")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    Path(caminho).parent.mkdir(exist_ok=True)
    fig.savefig(caminho)


if __name__ == "__main__":
    serie = pd.read_parquet("dados/serie_pedidos.parquet")
    df = criar_features(serie)
    df["tendencia"] = coluna_tendencia(df)
    df = df.dropna().reset_index(drop=True)

    resultados = rodar_backtest(df)
    resumo = (resultados.groupby("modelo")[["mae", "rmse"]].mean()
              .sort_values("mae").rename(index=NOMES).round(1))

    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("previsao-demanda")
    for modelo, grupo in resultados.groupby("modelo"):
        with mlflow.start_run(run_name=f"backtest-{modelo}"):
            mlflow.log_param("modelo", NOMES[modelo])
            mlflow.log_param("periodos", PERIODOS)
            if modelo == "lightgbm":
                mlflow.log_params(PARAMETROS)
            mlflow.log_metric("mae_medio", grupo["mae"].mean())
            mlflow.log_metric("rmse_medio", grupo["rmse"].mean())

    grafico(df, "docs/previsao_demanda.png")

    print(f"Backtest em {PERIODOS} períodos de {DIAS} dias (erro médio em pedidos por dia)\n")
    print(resumo.to_string())
    print("\nGráfico salvo em docs/previsao_demanda.png")
