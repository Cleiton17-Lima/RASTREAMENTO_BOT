import requests
import os
from dotenv import load_dotenv

load_dotenv()

SSW_API_DEST = os.getenv("SSW_API_DEST")

def consultar_ssw_doc_nf(cnpj: str, nro_nf: str):
    """
    Consulta a API Tracking Destinatário da SSW pelo número da NF,
    podendo ser CPF ou CNPJ no campo 'cnpj'.
    """
    payload = {
        "cnpj": cnpj,   # a API usa sempre o campo 'cnpj', mas aceita CPF ou CNPJ
        "nro_nf": nro_nf
    }

    try:
        response = requests.post(
            SSW_API_DEST,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
        else:
            print("Erro SSW DEST:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Erro na consulta SSW DEST:", e)
        return None
