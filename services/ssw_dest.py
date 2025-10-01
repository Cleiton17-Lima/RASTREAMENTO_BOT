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
        mensagem = data.get("text", {}).get("message", "")

        if mensagem:
            mensagem = mensagem.strip()

            if ";" in mensagem:
                partes = mensagem.split(";")
                if len(partes) == 2:
                    cnpj = "".join(filter(str.isdigit, partes[0].strip()))
                    nro_nf = partes[1].strip()

                    rastreio = consultar_ssw_doc_nf(cnpj, nro_nf)
                    print("📦 Resposta da SSW DEST:", rastreio)

                    if rastreio and rastreio.get("success"):
                        header = rastreio.get("header", {})
                        tracking = rastreio.get("tracking", [])

                        remetente = header.get("remetente", "---")
                        destinatario = header.get("destinatario", "---")
                        nf = header.get("nro_nf", nro_nf)

                        if tracking:
                            ultimo_evento = tracking[-1]
                            resposta = (
                                f"📦 *Rastreamento da sua carga*\n"
                                f"- NF: {nf}\n"
                                f"- Remetente: {remetente}\n"
                                f"- Destinatário: {destinatario}\n"
                                f"- Último status: {ultimo_evento.get('ocorrencia')}\n"
                                f"- Descrição: {ultimo_evento.get('descricao')}\n"
                                f"- Data/Hora: {ultimo_evento.get('data_hora')}\n"
                                f"- Local: {ultimo_evento.get('cidade')}"
                            )
                        else:
                            resposta = "⚠️ Documento localizado, mas sem eventos de rastreamento."
                    else:
                        resposta = "❌ Não encontrei informações para esse documento/NF."
                else:
                    resposta = "❌ Formato inválido. Use: CNPJ;NF"
            else:
                resposta = "Olá! 👋 Envie o *CNPJ ou CPF + número da NF* no formato:\n`CNPJ;NF`"

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
