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

# Cache para 24 horas para reduzir chamadas à API
cache = TTLCache(maxsize=100, ttl=86400)  # 24 horas

# Dados de fallback para quando a API falhar
FALLBACK_BRANDS = pd.DataFrame([
    {'codigo': '21', 'nome': 'FIAT'},
    {'codigo': '59', 'nome': 'VOLKSWAGEN'},
    {'codigo': '23', 'nome': 'CHEVROLET'},
    {'codigo': '22', 'nome': 'FORD'},
    {'codigo': '44', 'nome': 'HYUNDAI'},
    {'codigo': '25', 'nome': 'HONDA'},
    {'codigo': '48', 'nome': 'TOYOTA'}
])

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
        response = session.get(f"{BASE_URL}/marcas", timeout=5)  # Timeout de 5 segundos
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Obtidas {len(data)} marcas com sucesso")
            return pd.DataFrame(data)
            
        logger.warning(f"API retornou status {response.status_code}. Usando dados fallback...")
        return FALLBACK_BRANDS
            
    except Exception as e:
        logger.error(f"Erro ao obter marcas da tabela FIPE: {e}")
        return FALLBACK_BRANDS

@cached(cache)
def get_fipe_models(brand_code):
    try:
        session = create_session()
        response = session.get(f"{BASE_URL}/marcas/{brand_code}/modelos", timeout=5)
        sleep(0.5)  # Reduzido tempo de espera
        
        if response.status_code == 200:
            return pd.DataFrame(response.json()['modelos'])
        return pd.DataFrame([{'codigo': '0', 'nome': 'Erro ao carregar modelos'}])
    except Exception as e:
        logging.error(f"Erro ao obter modelos da tabela FIPE: {e}")
        return pd.DataFrame([{'codigo': '0', 'nome': 'Erro ao carregar modelos'}])

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
