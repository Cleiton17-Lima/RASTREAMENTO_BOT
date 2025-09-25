import requests 
import os 
from dotenv import load_dotenv

load_dotenv()

SSW_API = os.getenv("SSW_API")

def consultar_ssw(chave_nfe: str):
    try:
        response = requests.post(
            SSW_API,
            json={"chave_nfe": chave_nfe},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json() #aqui você adapta para os campos certos
        return None
    except Exception as e:
        print("Erro na consulta SSW:", e)
        return None