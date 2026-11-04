"""Conexão com o BigQuery usada por todo o projeto."""

import os
import warnings

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

# Sem o pacote opcional de leitura rápida, o BigQuery avisa a cada consulta.
# Para as tabelas pequenas deste projeto o caminho normal basta, então o aviso só polui a tela.
warnings.filterwarnings("ignore", message="BigQuery Storage module not found")


def cliente() -> bigquery.Client:
    return bigquery.Client(project=os.environ["GCP_PROJECT"])


def consultar(sql: str):
    """Roda uma consulta e devolve um DataFrame."""
    return cliente().query(sql).to_dataframe()
