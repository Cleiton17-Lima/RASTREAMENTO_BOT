from fastapi import FastAPI, Request
import os
from services.ssw import consultar_ssw
from services.zap import enviar_mensagem
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


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