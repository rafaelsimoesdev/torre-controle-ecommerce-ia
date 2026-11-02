"""Segmentação de clientes com RFM + K-Means.

Cada cliente vira 3 números (Recência, Frequência e Valor) e o K-Means
encontra grupos de clientes parecidos. O número de grupos é escolhido
pelo silhouette score, que mede o quanto os grupos ficaram bem separados.
"""

from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.bq import consultar

COLUNAS = ["recencia", "frequencia", "valor"]
K_TESTADOS = range(2, 9)


def carregar_rfm() -> pd.DataFrame:
    return consultar("SELECT * FROM torre_controle.rfm_clientes")


def preparar(rfm: pd.DataFrame) -> np.ndarray:
    """Deixa as 3 colunas na mesma escala antes do K-Means.

    O K-Means mede distância. Sem esse passo, o valor (que vai até ~1.700)
    pesaria muito mais que a frequência (que vai de 1 a 4).
    """
    dados = rfm[COLUNAS].astype(float).copy()
    # poucos clientes gastam muito: o log "encolhe" os valores extremos
    dados["valor"] = np.log1p(dados["valor"])
    return StandardScaler().fit_transform(dados)


def escolher_k(x: np.ndarray) -> dict:
    """Testa vários números de grupos e devolve o silhouette de cada um."""
    resultados = {}
    for k in K_TESTADOS:
        # TODO 1: crie o K-Means com k grupos e já treine e preveja os grupos
        # dica: KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(x)
        grupos = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(x)
        # TODO 2: calcule o silhouette com uma amostra de 10.000 clientes
        # dica: silhouette_score(x, grupos, sample_size=10_000, random_state=42)
        resultados[k] = silhouette_score(x, grupos, sample_size=10_000, random_state=42)
    return resultados


def perfil(rfm: pd.DataFrame) -> pd.DataFrame:
    """Resumo de cada grupo: tamanho e médias de R, F e M."""
    tabela = rfm.groupby("grupo").agg(
        clientes=("user_id", "count"),
        recencia=("recencia", "mean"),
        frequencia=("frequencia", "mean"),
        valor=("valor", "mean"),
    )
    tabela["% clientes"] = tabela["clientes"] / tabela["clientes"].sum() * 100
    return tabela.round(1).sort_values("valor", ascending=False)


def nomear_grupos(tabela: pd.DataFrame) -> dict:
    """Dá nome aos grupos olhando o perfil de cada um (vale para k = 3).

    O K-Means só numera os grupos. O nome vem da leitura do perfil:
    quem gasta mais são os fiéis, quem sumiu há mais tempo são os inativos
    e o resto comprou uma vez só e ainda pode voltar.
    """
    if len(tabela) != 3:
        return {g: f"Grupo {g}" for g in tabela.index}
    fieis = tabela["valor"].idxmax()
    inativos = tabela["recencia"].idxmax()
    nomes = {g: "Ocasionais" for g in tabela.index}
    nomes[fieis] = "Fiéis"
    nomes[inativos] = "Inativos"
    return nomes


if __name__ == "__main__":
    rfm = carregar_rfm()
    x = preparar(rfm)

    notas = escolher_k(x)
    for k, nota in notas.items():
        print(f"k = {k}: silhouette {nota:.3f}")
    melhor_k = max(notas, key=notas.get)
    print(f"\nMelhor número de grupos: {melhor_k}\n")

    modelo = KMeans(n_clusters=melhor_k, n_init=10, random_state=42)
    rfm["grupo"] = modelo.fit_predict(x)
    tabela = perfil(rfm)
    nomes = nomear_grupos(tabela)
    rfm["segmento"] = rfm["grupo"].map(nomes)
    print(tabela.rename(index=nomes).to_string())

    Path("dados").mkdir(exist_ok=True)
    rfm.to_parquet("dados/rfm_grupos.parquet", index=False)

    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("segmentacao-clientes")
    with mlflow.start_run(run_name=f"kmeans-k{melhor_k}"):
        mlflow.log_param("k", melhor_k)
        mlflow.log_param("colunas", ", ".join(COLUNAS))
        mlflow.log_metric("silhouette", notas[melhor_k])
        for k, nota in notas.items():
            mlflow.log_metric("silhouette_por_k", nota, step=k)
