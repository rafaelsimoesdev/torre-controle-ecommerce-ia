"""Envio do relatório para o Telegram.

Sem TELEGRAM_TOKEN e TELEGRAM_CHAT_ID no ambiente, o texto só é mostrado
na tela (modo ensaio). Assim dá para testar o pipeline sem mandar mensagem.
"""

import os

import requests


def enviar(texto: str) -> bool:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[modo ensaio: sem TELEGRAM_TOKEN/TELEGRAM_CHAT_ID]\n" + texto)
        return False
    resposta = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": texto},
        timeout=30,
    )
    resposta.raise_for_status()
    return True
