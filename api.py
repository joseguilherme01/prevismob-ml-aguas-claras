"""
API Backend para PrevIsmob - Sistema de Previsão de Preços de Imóveis
Utiliza FastAPI com modelo Scikit-Learn treinado (joblib)
Integração com dataset CSV para dados de proximidade georreferenciada
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import os
from typing import List
import time

# novas dependências para Google Maps e dotenv
import googlemaps
from dotenv import load_dotenv
from geopy.distance import geodesic

# ============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ============================================================================

app = FastAPI(
    title="PrevIsmob API",
    description="API para previsão de preços de imóveis em Águas Claras",
    version="2.0.0"
)

# ============================================================================
# CONFIGURAÇÃO DE CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Aceita requisições de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) # <-- O parêntese do middleware fecha aqui!

# ============================================================================
# CARREGAMENTO DO DATASET CSV
# ============================================================================

# Caminho para o arquivo CSV (ainda usado por /condominio)
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset_aguas_claras_completo.csv")

# DataFrame global que armazena todos os dados (pode ser None se não houver)
df_condominios = None

try:
    df_condominios = pd.read_csv(CSV_PATH)
    print(f"✓ Dataset carregado com sucesso de: {CSV_PATH}")
    print(f"  - Total de imóveis: {len(df_condominios)}")
    print(f"  - Colunas: {list(df_condominios.columns)}")
except FileNotFoundError:
    print(f"✗ ERRO: Dataset não encontrado em {CSV_PATH}")
    df_condominios = None
except Exception as e:
    print(f"✗ ERRO ao carregar dataset: {e}")
    df_condominios = None

# ============================================================================
# CARREGAMENTO DO MODELO ML
# ============================================================================

MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_imoveis.pkl")

try:
    modelo_ml = joblib.load(MODEL_PATH)
    print(f"✓ Modelo ML carregado com sucesso de: {MODEL_PATH}")
except FileNotFoundError:
    print(f"✗ ERRO: Modelo não encontrado em {MODEL_PATH}")
    modelo_ml = None
except Exception as e:
    print(f"✗ ERRO ao carregar modelo: {e}")
    modelo_ml = None

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class DadosImovelUsuario(BaseModel):
    """
    Modelo Pydantic para dados do usuário (entrada simplificada).
    O backend enriquecerá com dados do dataset.
    """
    Nome_Predio: str = Field(..., description="Nome do edifício/condomínio")
    Area_Util: float = Field(..., description="Área útil do imóvel em m²")
    Valor_Condominio: float = Field(..., description="Valor total do condomínio em R$")
    Quartos: int = Field(..., description="Número de quartos")
    Vagas: int = Field(..., description="Número de vagas de garagem")

    class Config:
        schema_extra = {
            "example": {
                "Nome_Predio": "Residencial Portal Das Araucarias",
                "Area_Util": 68.0,
                "Valor_Condominio": 650.0,
                "Quartos": 2,
                "Vagas": 1
            }
        }


class RespostaPrevicao(BaseModel):
    """Modelo Pydantic para resposta de previsão"""
    preco_m2_minimo: float = Field(..., description="Preço mínimo por m²")
    preco_m2_sugerido: float = Field(..., description="Preço sugerido por m²")
    preco_m2_maximo: float = Field(..., description="Preço máximo por m²")
    Distancia_Metro_km: float = Field(..., description="Distância até o metrô (km)")
    metro_nome: str = Field(..., description="Nome da estação de metrô mais próxima")
    Mercados_500m: float = Field(..., description="Número de mercados em 500m")
    Escolas_1000m: float = Field(..., description="Número de escolas em 1000m")
    Parques_800m: float = Field(..., description="Número de parques em 800m")
    Latitude: float = Field(..., description="Latitude do prédio")
    Longitude: float = Field(..., description="Longitude do prédio")
    status: str = Field(default="sucesso", description="Status da previsão")

# carregar variáveis de ambiente e inicializar cliente Google Maps
load_dotenv()
GOOGLE_MAPS_KEY = os.getenv("Maps_API_KEY")
if not GOOGLE_MAPS_KEY:
    print("⚠️ Maps_API_KEY não encontrada em .env. Algumas rotas podem falhar.")

# inicializa cliente gmaps (pode ser None se chave faltante)
gmaps = googlemaps.Client(key=GOOGLE_MAPS_KEY) if GOOGLE_MAPS_KEY else None

# ============================================================================
# ROTAS / ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Rota raiz - informações da API"""
    return {
        "nome": "PrevIsmob API",
        "descricao": "Sistema de previsão de preços de imóveis",
        "versao": "2.0.0",
        "dataset_carregado": df_condominios is not None,
        "modelo_carregado": modelo_ml is not None,
        "endpoints_principais": ["/condominio", "/prever"]
    }


@app.get("/condominio", response_model=List[str], tags=["Dados"])
async def obter_condominio():
    """
    Retorna lista de nomes únicos de prédios/condomínios ordenados alfabeticamente.
    Usada para popular o dropdown no frontend.
    """
    
    if df_condominios is None:
        raise HTTPException(
            status_code=500,
            detail="Dataset não foi carregado"
        )
    
    try:
        # Obter lista única de nomes: remover nulos, extrair únicos, ordenar e converter para list
        nomes_unicos = sorted(df_condominios["Nome_Predio"].dropna().unique().tolist())
        return nomes_unicos
    except Exception as e:
        print(f"✗ Erro ao obter lista de condomínios: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar data: {str(e)}"
        )


@app.post("/prever", response_model=RespostaPrevicao, tags=["Previsão"])
async def prever_preco(dados: DadosImovelUsuario):
    """
    Endpoint para previsão de preço do imóvel.
    
    Recebe dados básicos do usuário e Nome_Predio. A partir do endereço
    faz geocoding usando Google Maps para obter coordenadas e métricas de
    proximidade dinamicamente (metrô, parques, escolas, mercados). Não
    depende mais de um dataset local. Calcula Condominio_m2, monta o DataFrame
    com as 7 variáveis esperadas e faz a previsão.
    
    Args:
        dados (DadosImovelUsuario): Dados do usuário (5 campos)
        
    Returns:
        RespostaPrevicao: Preço por m² predito
    """
    
    # ========== VALIDAÇÕES ==========
    
    if modelo_ml is None:
        raise HTTPException(
            status_code=500,
            detail="Modelo ML não foi carregado"
        )
    
    # o dataset não é necessário nesta rota; só usamos Google Maps para localizar o imóvel
    
    try:
        # ========== PASSO 1: OBTER COORDENADAS E PROXIMIDADES VIA GOOGLE MAPS ==========
        if not gmaps:
            raise HTTPException(
                status_code=500,
                detail="Google Maps client não foi inicializado. Verifique a chave em .env"
            )

        endereco_completo = f"{dados.Nome_Predio}, Águas Claras, Distrito Federal, Brasil"
        try:
            geocode_res = gmaps.geocode(endereco_completo)
        except Exception as e:
            print(f"✗ Erro na requisição de geocode: {e}")
            raise HTTPException(status_code=500, detail="Erro ao consultar Google Maps")

        if not geocode_res:
            raise HTTPException(
                status_code=404,
                detail=f"Endereço '{dados.Nome_Predio}' não encontrado pelo Google Maps"
            )

        location = geocode_res[0]["geometry"]["location"]
        latitude = location["lat"]
        longitude = location["lng"]
        print(f"✓ Coordenadas obtidas via Google Maps: Lat {latitude}, Lon {longitude}")

        # inicializa valores padrão
        distancia_metro_km = 0.0
        mercados_500m = 0.0
        escolas_1000m = 0.0
        parques_800m = 0.0

        # buscar estações de metrô próximas e extrair nome
        metro_nome = "Nenhuma estação próxima"
        try:
            metro_resp = gmaps.places_nearby(location=(latitude, longitude), radius=1500, type="subway_station")
            metros = metro_resp.get("results", [])
            if metros:
                # encontrar a estação mais próxima calculando distância para cada
                menor = None
                for m in metros:
                    lat_m = m["geometry"]["location"]["lat"]
                    lng_m = m["geometry"]["location"]["lng"]
                    dist = geodesic((latitude, longitude), (lat_m, lng_m)).km
                    if menor is None or dist < menor[0]:
                        menor = (dist, m)
                if menor:
                    distancia_metro_km = menor[0]
                    metro_nome = menor[1].get("name", metro_nome)
        except Exception as e:
            print(f"⚠️ Falha ao buscar metrô: {e}")

        # parques (raio 800m, paginar resultados)
        try:
            total_parques = 0
            park_resp = gmaps.places_nearby(location=(latitude, longitude), radius=800, type="park")
            while park_resp:
                total_parques += len(park_resp.get("results", []))
                token = park_resp.get("next_page_token")
                if token:
                    time.sleep(2)
                    park_resp = gmaps.places_nearby(page_token=token)
                else:
                    break
            parques_800m = total_parques
        except Exception as e:
            print(f"⚠️ Falha ao buscar parques: {e}")

        # escolas (raio 1000m, paginar resultados)
        try:
            total_escolas = 0
            school_resp = gmaps.places_nearby(location=(latitude, longitude), radius=1000, type="school")
            while school_resp:
                total_escolas += len(school_resp.get("results", []))
                token = school_resp.get("next_page_token")
                if token:
                    time.sleep(2)
                    school_resp = gmaps.places_nearby(page_token=token)
                else:
                    break
            escolas_1000m = total_escolas
        except Exception as e:
            print(f"⚠️ Falha ao buscar escolas: {e}")

        # mercados filtrados (raio 500m)
        try:
            market_resp = gmaps.places_nearby(location=(latitude, longitude), radius=500, type="supermarket")
            lista = market_resp.get("results", [])
            termos = [
                "mercado", "supermercado", "atacadão", "big box",
                "dona de casa", "pão de açúcar", "carrefour"
            ]
            mercados_500m = sum(
                1 for r in lista
                if any(term in r.get("name", "").lower() for term in termos)
            )
        except Exception as e:
            print(f"⚠️ Falha ao buscar mercados: {e}")
        
        # ========== PASSO 2: CALCULAR CONDOMINIO_M2 ==========
        condominio_m2 = dados.Valor_Condominio / dados.Area_Util
        
        # ========== PASSO 3: MONTAR DATAFRAME COM 7 VARIÁVEIS ==========
        
        dados_modelo = {
            "Quartos": dados.Quartos,
            "Vagas": dados.Vagas,
            "Condominio_m2": condominio_m2,
            "Distancia_Metro_km": distancia_metro_km,
            "Mercados_500m": mercados_500m,
            "Escolas_1000m": escolas_1000m,
            "Parques_800m": parques_800m
        }
        
        df_entrada = pd.DataFrame([dados_modelo])
        
        # Garantir ordem exata das colunas
        colunas_esperadas = [
            "Quartos", "Vagas", "Condominio_m2",
            "Distancia_Metro_km", "Mercados_500m",
            "Escolas_1000m", "Parques_800m"
        ]
        df_entrada = df_entrada[colunas_esperadas]
        
        # ========== PASSO 4: FAZER PREVISÃO ==========
        predicao = modelo_ml.predict(df_entrada)
        preco_m2_sugerido = float(predicao[0])
        
        print(f"✓ Previsão realizada para {dados.Nome_Predio}")
        print(f"  - R$/m²: {preco_m2_sugerido:.2f}")

        # Calcular margem +/-5%
        preco_m2_minimo = round(preco_m2_sugerido * 0.95, 6)
        preco_m2_maximo = round(preco_m2_sugerido * 1.05, 6)

        # ========== PASSO 5: RETORNAR RESPOSTA (inclui localização) ==========
        return RespostaPrevicao(
            preco_m2_minimo=preco_m2_minimo,
            preco_m2_sugerido=preco_m2_sugerido,
            preco_m2_maximo=preco_m2_maximo,
            Distancia_Metro_km=distancia_metro_km,
            metro_nome=metro_nome,
            Mercados_500m=mercados_500m,
            Escolas_1000m=escolas_1000m,
            Parques_800m=parques_800m,
            Latitude=latitude,
            Longitude=longitude,
            status="sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Erro na previsão: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar previsão: {str(e)}"
        )


@app.get("/status", tags=["Info"])
async def status():
    """Verifica status da API, dataset e modelo"""
    return {
        "api_ativa": True,
        "dataset_carregado": df_condominios is not None,
        "dataset_registros": len(df_condominios) if df_condominios is not None else 0,
        "modelo_carregado": modelo_ml is not None,
        "caminho_dataset": CSV_PATH,
        "caminho_modelo": MODEL_PATH,
        "endpoints_disponiveis": [
            "/", "/status", "/condominio", "/prever", "/docs"
        ]
    }


# ============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🚀 Iniciando PrevIsmob API v2.0 (Geocoding em tempo real com Google Maps)")
    print("=" * 70)
    print(f"📍 URL: http://localhost:8000")
    print(f"📚 Documentação: http://localhost:8000/docs")
    print(f"📊 Status: http://localhost:8000/status")
    print("=" * 70)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )