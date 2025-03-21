import requests
import pandas as pd
import logging

BASE_URL = "https://parallelum.com.br/fipe/api/v1/carros"

# Configuração do logger
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_fipe_brands():
    try:
        response = requests.get(f"{BASE_URL}/marcas")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Erro ao obter marcas da tabela FIPE: {e}")
        raise Exception("Erro ao obter marcas da tabela FIPE")

def get_fipe_models(brand_code):
    response = requests.get(f"{BASE_URL}/marcas/{brand_code}/modelos")
    if response.status_code == 200:
        return pd.DataFrame(response.json()['modelos'])
    raise Exception("Erro ao obter modelos da tabela FIPE")

def get_fipe_years(brand_code, model_code):
    response = requests.get(f"{BASE_URL}/marcas/{brand_code}/modelos/{model_code}/anos")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    raise Exception("Erro ao obter anos da tabela FIPE")

def get_fipe_price(brand_code, model_code, year_code):
    response = requests.get(f"{BASE_URL}/marcas/{brand_code}/modelos/{model_code}/anos/{year_code}")
    if response.status_code == 200:
        return response.json()
    raise Exception("Erro ao obter preço da tabela FIPE")
