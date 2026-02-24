import requests
import pandas as pd
import time
import math
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# Tenta carregar o .env da pasta atual ou da pasta pai (raiz)
load_dotenv() 

# Tenta pegar a chave
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# VERIFICAÇÃO RIGOROSA
if API_KEY:
    print(f"✅ CHAVE ENCONTRADA: {API_KEY[:5]}... (Pronto para usar)")
else:
    print("\n❌ ERRO CRÍTICO: O Python não achou a chave no arquivo .env")
    print("DICA: Verifique se o arquivo se chama exatamente '.env' e se está salvo na pasta Prevismob.")
    exit() # Para o código imediatamente para não gerar dados vazios
# ---------------------------------

# ... O resto do código (funções def geocode_address etc) continua igual abaixo ...
# ---------- FUNÇÕES ----------
def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    try:
        response = requests.get(url, params=params).json()
        if response["status"] != "OK": return None, None
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    except: return None, None

def nearby_places(lat, lng, place_type, radius):
    if lat is None: return 0
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {"location": f"{lat},{lng}", "radius": radius, "type": place_type, "key": API_KEY}
    try:
        response = requests.get(url, params=params).json()
        return len(response.get("results", []))
    except: return 0

def haversine(lat1, lon1, lat2, lon2):
    if lat1 is None or lat2 is None: return 9999
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def nearest_metro(lat, lng):
    if lat is None: return 9999, "Nenhum"
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {"location": f"{lat},{lng}", "radius": 3000, "type": "subway_station", "key": API_KEY}
    try:
        results = requests.get(url, params=params).json().get("results", [])
        if not results: return 9999, "Nenhum"
        
        nearest_name = "Nenhum"
        min_dist = float("inf")
        
        for station in results:
            slat = station["geometry"]["location"]["lat"]
            slng = station["geometry"]["location"]["lng"]
            dist = haversine(lat, lng, slat, slng)
            if dist < min_dist:
                min_dist = dist
                nearest_name = station["name"]
        return round(min_dist, 2), nearest_name
    except: return 9999, "Erro"

# ---------- EXECUÇÃO PRINCIPAL ----------
def coletar_dados():
    arquivo_entrada = "data/dataset_aguas_claras_ml.csv"
    arquivo_saida = "data/dataset_aguas_claras_features.csv"
    
    print(f"Lendo: {arquivo_entrada}...")
    try:
        # AQUI ESTÃO OS AJUSTES CRITICOS:
        # sep=';' -> Para ler o formato da sua imagem
        # encoding='utf-8-sig' -> Para ignorar a assinatura BOM do Excel
        df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8-sig')
    except FileNotFoundError:
        print(f"❌ ERRO: O arquivo não está na pasta 'data'.")
        return

    # Limpeza extra nos nomes
    if 'Nome_Predio' in df.columns:
        df['Nome_Predio'] = df['Nome_Predio'].astype(str).str.strip()
    
    results = []
    total = len(df)
    print(f"Processando {total} imóveis...")

    for i, row in df.iterrows():
        print(f"[{i+1}/{total}] {row['Nome_Predio']}...", end='\r')
        
        # Usa o endereço oficial para buscar o GPS
        lat, lng = geocode_address(row["Endereco_Oficial"])
        
        mercados = nearby_places(lat, lng, "supermarket", 500)
        escolas = nearby_places(lat, lng, "school", 1000)
        parques = nearby_places(lat, lng, "park", 800)
        dist_metro, nome_metro = nearest_metro(lat, lng)

        results.append({
            "Nome_Predio": row["Nome_Predio"],
            "Endereco_Oficial": row["Endereco_Oficial"],
            "Latitude": lat,
            "Longitude": lng,
            "Distancia_Metro_km": dist_metro,
            "Nome_Metro": nome_metro,
            "Mercados_500m": mercados,
            "Escolas_1000m": escolas,
            "Parques_800m": parques
        })

    # Salva o resultado
    pd.DataFrame(results).to_csv(arquivo_saida, index=False, sep=';', encoding='utf-8-sig')
    print(f"\n\n✅ Sucesso! Arquivo salvo em: {arquivo_saida}")

if __name__ == "__main__":
    coletar_dados()