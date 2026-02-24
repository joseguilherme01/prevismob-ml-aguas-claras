import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import re
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_ENTRADA = "data/dataset_aguas_claras_features.csv"
ARQUIVO_SAIDA = "data/dataset_com_precos_google.csv"

def configurar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # Truque para parecer um humano real
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extrair_valores(texto):
    # Procura padrões de preço (Ex: R$ 500.000 ou 500.000)
    # Ignora valores muito baixos (aluguel/condominio) ou irreais
    precos = []
    areas = []
    
    # Regex para Preço
    matches_preco = re.findall(r'R\$\s?(\d{1,3}(?:\.\d{3})*)', texto)
    for p in matches_preco:
        valor = int(p.replace('.', ''))
        if 180000 < valor < 5000000: # Filtro: Entre 180k e 5 milhões
            precos.append(valor)
            
    # Regex para Área (ex: 60m², 60 m2)
    matches_area = re.findall(r'(\d{2,3})\s?(?:m²|m2|mts)', texto.lower())
    for a in matches_area:
        valor = int(a)
        if 25 < valor < 400: # Filtro: Entre 25m² e 400m²
            areas.append(valor)
            
    return precos, areas

print("🚀 Iniciando Robô 'Ninja' no Google...")
driver = configurar_driver()

# Carrega dados
if os.path.exists(ARQUIVO_SAIDA):
    df = pd.read_csv(ARQUIVO_SAIDA)
    print("📂 Retomando arquivo existente...")
else:
    df = pd.read_csv(ARQUIVO_ENTRADA)
    if 'Preco_Medio' not in df.columns:
        df['Preco_Medio'] = 0.0
        df['Area_Media'] = 0.0
        df['Amostras'] = 0 # Quantos anuncios achou para fazer a media

# --- FASE 1: Drible Inicial ---
driver.get("https://www.google.com.br")
print("⚠️ ATENÇÃO: Se aparecer um botão 'Aceitar Cookies' ou CAPTCHA agora, resolva manualmente!")
print("⏳ Dando 15 segundos para você preparar o terreno...")
time.sleep(15) 

try:
    total = len(df)
    # Itera sobre os prédios
    for index, row in df.iterrows():
        
        # Se já tem preço, pula (para poder parar e continuar depois)
        if row['Preco_Medio'] > 0:
            continue
            
        predio = row['Nome_Predio']
        query = f"apartamento venda {predio} águas claras preço"
        
        print(f"[{index+1}/{total}] Pesquisando: {predio}...")
        
        # Faz a busca no Google
        driver.get("https://www.google.com/search?q=" + query)
        
        # Coleta os textos dos resultados (Snippets)
        elementos = driver.find_elements(By.CSS_SELECTOR, "div.g") # div.g é o bloco padrão de resultado
        
        todos_precos = []
        todas_areas = []
        
        for elem in elementos:
            texto = elem.text
            p, a = extrair_valores(texto)
            todos_precos.extend(p)
            todas_areas.extend(a)
            
        # Calcula médias
        if todos_precos:
            media_p = sum(todos_precos) / len(todos_precos)
            df.at[index, 'Preco_Medio'] = media_p
            df.at[index, 'Amostras'] = len(todos_precos)
            print(f"   ✅ Preço Médio: R$ {media_p:,.2f} (Baseado em {len(todos_precos)} menções)")
        else:
            print("   ❌ Preço não identificado nos textos.")
            
        if todas_areas:
            media_a = sum(todas_areas) / len(todas_areas)
            df.at[index, 'Area_Media'] = media_a
            
        # Salva parcial a cada 5
        if index % 5 == 0:
            df.to_csv(ARQUIVO_SAIDA, index=False)
            
        # ⚠️ DELAY ALEATÓRIO PARA NÃO SER BLOQUEADO
        # O Google bloqueia se for muito rápido. Vamos devagar.
        tempo_espera = random.uniform(5, 10)
        time.sleep(tempo_espera)

except KeyboardInterrupt:
    print("\n🛑 Parando... salvando o que já foi feito.")

finally:
    df.to_csv(ARQUIVO_SAIDA, index=False)
    driver.quit()
    print("💾 Fim! Arquivo salvo em: " + ARQUIVO_SAIDA)