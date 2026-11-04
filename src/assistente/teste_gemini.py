"""Teste rápido: confere se a chave do Gemini no .env funciona."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

# Se o primeiro modelo estiver sobrecarregado (erro 503), tenta o próximo.
MODELOS = ["gemini-flash-latest", "gemini-flash-lite-latest"]

if __name__ == "__main__":
    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for modelo in MODELOS:
        try:
            resposta = cliente.models.generate_content(
                model=modelo,
                contents="Responda em uma frase, em português: o que é uma torre de controle de e-commerce?",
            )
            print(f"[{modelo}] {resposta.text}")
            break
        except errors.ServerError as erro:
            print(f"[{modelo}] indisponível agora ({erro.code}), tentando o próximo...")
