"""Chamada ao Gemini com fallback: se um modelo estiver fora do ar, tenta o próximo."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

MODELOS = ["gemini-flash-latest", "gemini-flash-lite-latest"]
TEMPO_MAXIMO_MS = 60_000  # desiste de um modelo depois de 60 segundos

# Por padrão a biblioteca tenta de novo várias vezes, esperando cada vez mais.
# Com o modelo sobrecarregado isso podia travar por minutos. Aqui são no máximo
# 2 tentativas rápidas por modelo, e depois o fallback assume.
OPCOES_HTTP = types.HttpOptions(
    timeout=TEMPO_MAXIMO_MS,
    retry_options=types.HttpRetryOptions(attempts=2, initial_delay=1, max_delay=4),
)


def gerar(prompt: str, esquema=None):
    """Manda o prompt ao Gemini. Com `esquema` (uma classe pydantic), a resposta
    volta já como objeto com os campos certos, em vez de texto solto."""
    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=OPCOES_HTTP)
    config = types.GenerateContentConfig(temperature=0)
    if esquema is not None:
        config.response_mime_type = "application/json"
        config.response_schema = esquema

    ultimo_erro = None
    for modelo in MODELOS:
        print(f"  ... chamando {modelo}", flush=True)
        try:
            resposta = cliente.models.generate_content(model=modelo, contents=prompt, config=config)
            return resposta.parsed if esquema is not None else resposta.text
        except (errors.ServerError, errors.ClientError) as erro:  # 503 sobrecarga, 429 limite
            print(f"  ... {modelo} indisponível ({erro.code}), tentando o próximo", flush=True)
            ultimo_erro = erro
    raise RuntimeError(f"nenhum modelo do Gemini respondeu: {ultimo_erro}")
