"""Conexão com o BigQuery usada por todo o projeto."""

import os

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()


def cliente() -> bigquery.Client:
    return bigquery.Client(project=os.environ["GCP_PROJECT"])


def consultar(sql: str):
    """Roda uma consulta e devolve um DataFrame."""
    return cliente().query(sql).to_dataframe()
