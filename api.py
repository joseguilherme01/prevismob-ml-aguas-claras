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

# A classe começa em uma linha nova, sem espaços no começo da linha:
class RespostaPrevicao(BaseModel):
    preco_m2_minimo: float = Field(..., description="Preço mínimo por m²")
    preco_m2_sugerido: float = Field(..., description="Preço sugerido por m²")
    preco_m2_maximo: float = Field(..., description="Preço máximo por m²")
    Distancia_Metro_km: float = Field(..., description="Distância até o metrô (km)")
    Mercados_500m: float = Field(..., description="Número de mercados em 500m")
    Escolas_1000m: float = Field(..., description="Número de escolas em 1000m")
    Parques_800m: float = Field(..., description="Número de parques em 800m")
    Latitude: float = Field(..., description="Latitude do prédio")
    Longitude: float = Field(..., description="Longitude do prédio")
    status: str = Field(default="sucesso", description="Status da previsão")

# ============================================================================
# CARREGAMENTO DO DATASET CSV
# ============================================================================

# Caminho para o arquivo CSV
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset_aguas_claras_completo.csv")

# DataFrame global que armazena todos os dados
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
    Mercados_500m: float = Field(..., description="Número de mercados em 500m")
    Escolas_1000m: float = Field(..., description="Número de escolas em 1000m")
    Parques_800m: float = Field(..., description="Número de parques em 800m")
    Latitude: float = Field(..., description="Latitude do prédio")
    Longitude: float = Field(..., description="Longitude do prédio")
    status: str = Field(default="sucesso", description="Status da previsão")

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
        # Obter lista única de nomes, ordenar alfabeticamente
        nomes_unicos = sorted(df_condominios["Nome_Predio"].unique().tolist())
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
    
    Recebe dados básicos do usuário e Nome_Predio, procura no dataset
    para extrair as distâncias (proximidades), calcula Condominio_m2,
    monta o DataFrame com as 7 variáveis esperadas e faz a previsão.
    
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
    
    if df_condominios is None:
        raise HTTPException(
            status_code=500,
            detail="Dataset não foi carregado"
        )
    
    try:
        # ========== PASSO 1: BUSCAR PRÉDIO NO DATASET ==========
        
        # Procurar a linha correspondente ao Nome_Predio
        predio_encontrado = df_condominios[
            df_condominios["Nome_Predio"] == dados.Nome_Predio
        ]
        
        if predio_encontrado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Prédio '{dados.Nome_Predio}' não encontrado no dataset"
            )
        
        # Pegar primeira linha (caso haja duplicatas)
        predio_row = predio_encontrado.iloc[0]
        
        # ========== PASSO 2: CALCULAR CONDOMINIO_M2 ==========
        condominio_m2 = dados.Valor_Condominio / dados.Area_Util
        
        # ========== PASSO 3: EXTRAIR DISTÂNCIAS DO DATASET ==========
        distancia_metro_km = float(predio_row["Distancia_Metro_km"])
        mercados_500m = float(predio_row["Mercados_500m"])
        escolas_1000m = float(predio_row["Escolas_1000m"])
        parques_800m = float(predio_row["Parques_800m"])
        latitude = float(predio_row.get("Latitude", 0.0))
        longitude = float(predio_row.get("Longitude", 0.0))
        
        # ========== PASSO 4: MONTAR DATAFRAME COM 7 VARIÁVEIS ==========
        
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
        
        # ========== PASSO 5: FAZER PREVISÃO ==========
        predicao = modelo_ml.predict(df_entrada)
        preco_m2_sugerido = float(predicao[0])
        
        print(f"✓ Previsão realizada para {dados.Nome_Predio}")
        print(f"  - R$/m²: {preco_m2_sugerido:.2f}")

        # Calcular margem +/-5%
        preco_m2_minimo = round(preco_m2_sugerido * 0.95, 6)
        preco_m2_maximo = round(preco_m2_sugerido * 1.05, 6)

        # ========== PASSO 6: RETORNAR RESPOSTA (inclui localização) ==========
        return RespostaPrevicao(
            preco_m2_minimo=preco_m2_minimo,
            preco_m2_sugerido=preco_m2_sugerido,
            preco_m2_maximo=preco_m2_maximo,
            Distancia_Metro_km=distancia_metro_km,
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
    print("🚀 Iniciando PrevIsmob API v2.0 (Com Dataset CSV)")
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