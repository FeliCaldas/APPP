import requests
import pandas as pd
import logging
from cachetools import TTLCache, cached
from time import sleep
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuração do logger com mais detalhes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "https://parallelum.com.br/fipe/api/v1/carros"

# Cache com TTL menor para testes
cache = TTLCache(maxsize=100, ttl=1800)  # 30 minutos

def create_session():
    session = requests.Session()
    retry = Retry(
        total=5,  # Aumentado número de tentativas
        backoff_factor=1,  # Aumentado tempo entre tentativas
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

@cached(cache)
def get_fipe_brands():
    try:
        logger.info("Tentando obter marcas da tabela FIPE...")
        session = create_session()
        response = session.get(f"{BASE_URL}/marcas")
        
        # Rate limiting mais suave
        sleep(0.5)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Obtidas {len(data)} marcas com sucesso")
            return pd.DataFrame(data)
            
        # Se não conseguir dados da API, retorna algumas marcas padrão
        if response.status_code in [429, 503, 504]:
            logger.warning("API com limitação. Usando dados fallback...")
            return pd.DataFrame([
                {'codigo': '1', 'nome': 'FIAT'},
                {'codigo': '2', 'nome': 'VOLKSWAGEN'},
                {'codigo': '3', 'nome': 'CHEVROLET'},
                {'codigo': '4', 'nome': 'FORD'}
            ])
            
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Erro ao obter marcas da tabela FIPE: {e}")
        # Retorna marcas padrão em caso de erro
        return pd.DataFrame([
            {'codigo': '1', 'nome': 'FIAT'},
            {'codigo': '2', 'nome': 'VOLKSWAGEN'},
            {'codigo': '3', 'nome': 'CHEVROLET'},
            {'codigo': '4', 'nome': 'FORD'}
        ])

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
