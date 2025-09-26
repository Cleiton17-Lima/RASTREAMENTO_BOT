import requests
import os
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("ZAPI_INSTANCE")
TOKEN = os.getenv("ZAPI_TOKEN")
CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

def enviar_mensagem(numero: str, texto: str):
    url = f"https://api.z-api.io/instances/{INSTANCE}/token/{TOKEN}/send-text"

    headers = {
        "Content-Type": "application/json",
        "Client-Token": CLIENT_TOKEN
    }

    payload = {
        "phone": numero,
        "message": texto
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print("📡 Status:", response.status_code)
        print("📨 Resposta:", response.text)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)
