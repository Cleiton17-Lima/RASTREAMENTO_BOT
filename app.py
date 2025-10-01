from fastapi import FastAPI, Request
import os
from services.ssw_dest import consultar_ssw_doc_nf
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
    print("📩 Evento recebido:", data)

    event_type = data.get("type")

    if event_type == "ReceivedCallback":
        telefone = data.get("phone")
        mensagem = data.get("text", {}).get("message", "").strip()

        resposta = "⚠️ Envie no formato: *CNPJ/CPF;NF* (ex: 00850257000132;123456)."

        if ";" in mensagem:
            try:
                doc, nf = mensagem.split(";", 1)
                doc, nf = doc.strip(), nf.strip()

                if doc.isdigit() and nf.isdigit():
                    rastreio = consultar_ssw_doc_nf(doc, nf)
                    print("📦 Resposta da SSW DEST:", rastreio)

                    if rastreio and rastreio.get("success"):
                        doc_info = rastreio.get("documento", {})
                        header = doc_info.get("header", {})
                        tracking = doc_info.get("tracking", [])

                        remetente = header.get("remetente", "---")
                        destinatario = header.get("destinatario", "---")
                        nf_num = header.get("nro_nf", nf)

                        if tracking:
                            ultimo_evento = tracking[-1]
                            resposta = f"""
📦 *Rastreamento da sua carga*  
- NF: {nf_num}  
- Remetente: {remetente}  
- Destinatário: {destinatario}  
- Último status: {ultimo_evento.get('ocorrencia')}  
- Data/Hora: {ultimo_evento.get('data_hora')}  
- Local: {ultimo_evento.get('cidade')}  
"""
                        else:
                            resposta = "⚠️ NF localizada, mas sem eventos de rastreamento."
                    else:
                        resposta = "❌ Não encontrei informações para esse documento/NF."
                else:
                    resposta = "⚠️ Formato inválido. Use: *CNPJ/CPF;NF*"

            except Exception as e:
                print("❌ Erro no processamento:", e)
                resposta = "⚠️ Erro ao processar a sua solicitação. Verifique o formato."

        enviar_mensagem(telefone, resposta)

    elif event_type == "Connected":
        print("📡 Instância conectada:", data)

    elif event_type == "Disconnected":
        print("⚠️ Instância desconectada:", data)

    elif event_type == "MessageStatus":
        print("📨 Status da mensagem:", data)

    else:
        print("ℹ️ Evento não tratado:", data)

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
