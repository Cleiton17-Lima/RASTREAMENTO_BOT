import requests
import os 
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("ZAPI_INSTANCE")
TOKEN = os.getenv("ZAPI_TOKEN")
DEFAULT_PHONE = os.getenv("ZAPI_PHONE")

def enviar_mensagem(numero: str = DEFAULT_PHONE, texto: str = "🚚 Teste de rastreio"):
    url = f"https://api.z-api.io/instances/{INSTANCE}/token/{TOKEN}/send-text"

    payload = {
        "phone": numero,
        "message": texto
    }

    try:
        response = requests.post(url, json=payload)
        print("Status:", response.status_code)
        print("Resposta:", response.text)
    except Exception as e:
        print("Erro ao enviar mensagem Z-API:", e)
