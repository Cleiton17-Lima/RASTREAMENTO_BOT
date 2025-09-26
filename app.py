from fastapi import FastAPI, Request
import os

print("Iniciando aplicação FastAPI...")
print("Importando serviços...")

from services.ssw import consultar_ssw
from services.zap import enviar_mensagem

print("Serviços importados com sucesso.")



INSTANCE = os.getenv("ZAPI_INSTANCE")
TOKEN = os.getenv("ZAPI_TOKEN")



app = FastAPI()


@app.get("/env")
def verificar_env():
    return {
        "ZAPI_INSTANCE": os.getenv("ZAPI_INSTANCE"),
        "ZAPI_TOKEN": os.getenv("ZAPI_TOKEN"),
        "SSW_API": os.getenv("SSW_API")
    }


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    mensagem = data.get("message", {}).get("text", "").strip()
    telefone = data.get("message", {}).get("from", "")

    #valida se é chave DANFE (44 dígitos)
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
            resposta = " ❌ Não encontrei informações para essa DANFE."
    else:
        resposta = "Olá! 👋 Envie a *chave da DANFE (44 dígitos)* para consultar o rastreio. "

    #responde via Z-API
    enviar_mensagem(telefone, resposta)

    return {"status":"ok"}

def root():
    return {"status": "ok"}

if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))




