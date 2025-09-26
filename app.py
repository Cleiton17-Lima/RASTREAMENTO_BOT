from fastapi import FastAPI, Request
import os
from services.ssw import consultar_ssw
from services.zap import enviar_mensagem
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("ZAPI_INSTANCE")
TOKEN = os.getenv("ZAPI_TOKEN")

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Evento recebido:", data)  # log para debug

    # Detecta tipo de evento
    event = data.get("event")

    # Caso seja mensagem recebida
    if event == "message" or "message" in data:
        mensagem = (
            data.get("message", {}).get("text", "")
            or data.get("data", {}).get("message", {}).get("text", "")
        )
        telefone = (
            data.get("message", {}).get("from", "")
            or data.get("data", {}).get("from", "")
        )

        if mensagem:
            mensagem = mensagem.strip()

            # Valida se é chave DANFE (44 dígitos)
            if mensagem.isdigit() and len(mensagem) == 44:
                rastreio = consultar_ssw(mensagem)
                if rastreio:
                    resposta = f"""
📦 *Rastreamento da sua carga*  
- Status: {rastreio.get('status', 'Indisponível')}  
- Última atualização: {rastreio.get('data', '---')}  
- Local: {rastreio.get('local', '---')}  
"""
                else:
                    resposta = "❌ Não encontrei informações para essa DANFE."
            else:
                resposta = "Olá! 👋 Envie a *chave da DANFE (44 dígitos)* para consultar o rastreio."

            # Envia resposta
            enviar_mensagem(telefone, resposta)

    # Caso seja evento de conexão
    elif event == "connected":
        print("📡 Instância conectada:", data)

    elif event == "disconnected":
        print("⚠️ Instância desconectada:", data)

    # Caso seja status de mensagem
    elif event == "message-status":
        print("📩 Status da mensagem:", data)

    else:
        print("ℹ️ Evento não tratado:", data)

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
