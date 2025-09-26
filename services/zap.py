import os
import requests
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("ZAPI_INSTANCE")
TOKEN = os.getenv("ZAPI_TOKEN")
CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")


def enviar_mensagem(numero: str, texto: str):
    """
    Envia uma mensagem de texto pelo WhatsApp usando a Z-API.
    """

    if not INSTANCE or not TOKEN:
        print("❌ ERRO: Variáveis ZAPI_INSTANCE e ZAPI_TOKEN não configuradas no .env")
        return None

    url = f"https://api.z-api.io/instances/{INSTANCE}/token/{TOKEN}/send-text"

    headers = {
        "Content-Type": "application/json"
    }

    # Se o Client-Token estiver definido, adiciona
    if CLIENT_TOKEN:
        headers["Client-Token"] = CLIENT_TOKEN

    payload = {
        "phone": numero,
        "message": texto
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print("📤 Enviando mensagem para:", numero)
        print("➡️ Conteúdo:", texto)
        print("📡 Status:", response.status_code)
        print("📨 Resposta:", response.text)

        # Retorna JSON se deu certo
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print("❌ Erro na requisição para Z-API:", str(e))
        return None
