import requests
import pandas as pd
import logging
from cachetools import TTLCache, cached
from time import sleep
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuração do logger
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://parallelum.com.br/fipe/api/v1/carros"

# Cache configuration (TTL = 1 hora)
cache = TTLCache(maxsize=100, ttl=3600)

# Configurar sessão com retry
def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

@cached(cache)
def get_fipe_brands():
    try:
        session = create_session()
        response = session.get(f"{BASE_URL}/marcas")
        
        # Rate limiting - espera 1 segundo entre requisições
        sleep(1)
        
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Erro ao obter marcas da tabela FIPE: {e}")
        raise Exception(f"Erro ao obter marcas da tabela FIPE: {str(e)}")

@cached(cache)
def get_fipe_models(brand_code):
    try:
        session = create_session()
        response = session.get(f"{BASE_URL}/marcas/{brand_code}/modelos")
        sleep(1)
        
        if response.status_code == 200:
            return pd.DataFrame(response.json()['modelos'])
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Erro ao obter modelos da tabela FIPE: {e}")
        raise Exception("Erro ao obter modelos da tabela FIPE")

@cached(cache)
def get_fipe_years(brand_code, model_code):
    try:
        session = create_session()
        response = session.get(f"{BASE_URL}/marcas/{brand_code}/modelos/{model_code}/anos")
        sleep(1)
        
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Erro ao obter anos da tabela FIPE: {e}")
        raise Exception("Erro ao obter anos da tabela FIPE")

@cached(cache)
def get_fipe_price(brand_code, model_code, year_code):
    try:
        session = create_session()
        response = session.get(f"{BASE_URL}/marcas/{brand_code}/modelos/{model_code}/anos/{year_code}")
        sleep(1)
        
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Erro ao obter preço da tabela FIPE: {e}")
        raise Exception("Erro ao obter preço da tabela FIPE")
