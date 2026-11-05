"""Descobre o número da sua conversa com o bot (o TELEGRAM_CHAT_ID).

Antes de rodar: mande qualquer mensagem para o seu bot no Telegram.
Para rodar: python -m src.pipeline.descobrir_chat
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    token = os.environ["TELEGRAM_TOKEN"]
    resposta = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=30).json()
    conversas = {m["message"]["chat"]["id"]: m["message"]["chat"].get("first_name", "")
                 for m in resposta.get("result", []) if "message" in m}
    if not conversas:
        print("Nenhuma mensagem encontrada. Mande um 'oi' para o bot no Telegram e rode de novo.")
    for chat_id, nome in conversas.items():
        print(f"TELEGRAM_CHAT_ID={chat_id}   (conversa com {nome})")
