import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

INSTANCE = os.getenv("ZAPI_INSTANCE")
TOKEN = os.getenv("ZAPI_TOKEN")
CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

app = Flask(__name__)


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

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print("❌ Erro na requisição para Z-API:", str(e))
        return None


def processar_mensagem(mensagem: str) -> str:
    """
    Valida a chave da DANFE e retorna a resposta.
    """
    mensagem = mensagem.strip()

    # Verifica se é um número e tem 44 dígitos
    if mensagem.isdigit() and len(mensagem) == 44:
        return f"✅ DANFE recebida: {mensagem}\nEstamos consultando o rastreio..."
    else:
        return "⚠️ A chave da DANFE deve conter *44 dígitos numéricos*. Tente novamente."


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Recebe mensagens do WhatsApp (via Z-API) e responde conforme a lógica.
    """
    dados = request.json
    print("📩 Evento recebido:", dados)

    # Verifica se é mensagem recebida
    if dados.get("type") == "ReceivedCallback":
        numero = dados.get("phone")
        texto = dados.get("text", {}).get("message", "")

        if numero and texto:
            resposta = processar_mensagem(texto)
            enviar_mensagem(numero, resposta)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

