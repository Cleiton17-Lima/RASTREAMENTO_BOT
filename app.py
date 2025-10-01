from fastapi import FastAPI, Request
import os
from services.ssw_dest import consultar_ssw_doc_nf
from services.zap import enviar_mensagem
from dotenv import load_dotenv
import logging


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

    event_type = data.get("type")

    if event_type == "ReceivedCallback":
        telefone = data.get("phone")
        mensagem = data.get("text", {}).get("message", "")

        if not mensagem:
            return {"status": "ok"}

        mensagem = mensagem.strip()
        resposta = "⚠️ Envie no formato: *CNPJ;NF* (ex: 00850257000132;359983)."

        # Verifica se usuário enviou CNPJ;NF
        if ";" in mensagem:
            try:
                cnpj, nf = mensagem.split(";", 1)
                cnpj, nf = cnpj.strip(), nf.strip()

                if cnpj.isdigit() and nf.isdigit():
                    rastreio = consultar_ssw_nf(cnpj, nf)
                    print("📦 Resposta da SSW DEST:", rastreio)

                    if rastreio and rastreio.get("success"):
                        doc = rastreio.get("documento", {})
                        header = doc.get("header", {})
                        tracking = doc.get("tracking", [])

                        if tracking:
                            ultimo_evento = tracking[-1]
                            resposta = f"""
📦 *Rastreamento via NF*  
NF: {header.get('nro_nf', '---')}  
Remetente: {header.get('remetente', '---')}  
Destinatário: {header.get('destinatario', '---')}  

➡️ Último status: {ultimo_evento.get('ocorrencia')}  
📍 Local: {ultimo_evento.get('cidade')}  
🕒 Data: {ultimo_evento.get('data_hora')}  
"""
                        else:
                            resposta = "⚠️ NF localizada, mas sem eventos de rastreamento."
                    else:
                        resposta = "❌ Não encontrei informações para essa NF."
                else:
                    resposta = "⚠️ O formato está incorreto. Use: *CNPJ;NF*"

            except Exception:
                resposta = "⚠️ O formato está incorreto. Use: *CNPJ;NF*"

        enviar_mensagem(telefone, resposta)

    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))





