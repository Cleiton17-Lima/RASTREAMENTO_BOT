import requests
import os 
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("ZAPI_INSTANCE")
TOKEN = os.getenv("ZAPI_TOKEN")

def enviar_mensagem(numero: str, texto: str):
    url = f"https://api.z-api.io/instances/{INSTANCE}/token/{TOKEN}/send-text"


    payload = {
        "phone": numero,
        "message": texto
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Erro ao enviar mensagem Z-API:", e)