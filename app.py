from fastapi import FastAPI, Request
import os
from services.ssw import consultar_ssw
from services.zap import enviar_mensagem
from services.zap import processar_mensagem
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
    print("Evento recebido:", data)

    # Pega o tipo de evento
    event_type = data.get("type")

    # Se for mensagem recebida
    if event_type == "ReceivedCallback":
        telefone = data.get("phone")
        mensagem = data.get("text", {}).get("message", "")

        if mensagem:
            mensagem = mensagem.strip()

             # Valida se é chave DANFE
           if mensagem.isdigit() and len(mensagem) == 44:
    rastreio = consultar_ssw(mensagem)
    if rastreio and rastreio.get("success"):
        doc = rastreio.get("documento", {})
        header = doc.get("header", {})
        tracking = doc.get("tracking", [])

        remetente = header.get("remetente", "---")
        destinatario = header.get("destinatario", "---")
        nf = header.get("nro_nf", "---")

        if tracking:
            ultimo_evento = tracking[-1]  # pega o último status
            resposta = f"""
📦 *Rastreamento da sua carga*  
- NF: {nf}  
- Remetente: {remetente}  
- Destinatário: {destinatario}  
- Último status: {ultimo_evento.get('ocorrencia')}  
- Descrição: {ultimo_evento.get('descricao')}  
- Data/Hora: {ultimo_evento.get('data_hora')}  
- Local: {ultimo_evento.get('cidade')}  
"""
        else:
            resposta = f"⚠️ Documento localizado, mas sem eventos de rastreamento."
    else:
        resposta = "❌ Não encontrei informações para essa DANFE."

 else:
     resposta = "Olá! 👋 Envie a *chave da DANFE (44 dígitos)* para consultar o rastreio."


            # Envia resposta
            enviar_mensagem(telefone, resposta)

    elif event_type == "Connected":
        print("📡 Instância conectada:", data)

    elif event_type == "Disconnected":
        print("⚠️ Instância desconectada:", data)

    elif event_type == "MessageStatus":
        print("📩 Status da mensagem:", data)

    else:
        print("ℹ️ Evento não tratado:", data)

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))




