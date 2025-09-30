import requests
import os
from dotenv import load_dotenv

load_dotenv()

SSW_API = os.getenv("SSW_API")

def consultar_ssw(chave_nfe: str):
    """
    Consulta o rastreio da nota fiscal na API da SSW usando a chave da DANFE.
    """
    payload = {"chave_nfe": chave_nfe}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(SSW_API, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            try:
                return response.json()  # retorna o JSON com o rastreio
            except Exception:
                print("⚠️ Resposta não veio em JSON:", response.text)
                return None
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print("❌ Erro na consulta SSW:", e)
        return None
