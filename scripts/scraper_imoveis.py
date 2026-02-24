import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import re

# --- CONFIGURAÇÕES ---
ARQUIVO_ENTRADA = "data/dataset_aguas_claras_features.csv"
ARQUIVO_SAIDA = "data/dataset_com_precos.csv"

# Vamos usar um site agregador ou busca direta. 
# Para evitar bloqueios pesados, vamos simular um humano lento.
# OBS: Sites de imóveis mudam os "Selectores" (nomes das classes) toda semana.
# Este script tenta uma abordagem genérica buscando no Google/Portal.

def configurar_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Tire o # se quiser rodar sem ver a janela (não recomendado agora)
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extrair_numeros(texto):
    # Funçãozinha para limpar "R$ 500.000" virar 500000
    if not texto: return 0
    nums = re.findall(r'\d+', texto.replace('.', ''))
    if nums:
        return int(nums[0])
    return 0

def buscar_dados_predio(driver, nome_predio):
    # Vamos usar uma busca direta no Google filtrando por site de imoveis para ser mais certeiro
    # Ex: "site:wimoveis.com.br Residencial X Aguas Claras venda"
    termo_busca = f"apartamento venda {nome_predio} águas claras"
    
    # URL de busca genérica (vamos usar o Google pois ele indexa os portais)
    # Mas para garantir dados estruturados, vamos tentar navegar direto num portal se possível.
    # Pela complexidade, vamos tentar uma busca direta no Google e pegar o primeiro snippet ou entrar no link.
    
    # ESTRATÉGIA SIMPLIFICADA PARA ESTUDO:
    # Vamos buscar no portal "WImoveis" através da URL de busca deles.
    nome_formatado = nome_predio.replace(" ", "-").lower()
    url = f"https://www.wimoveis.com.br/apartamentos-venda-aguas-claras-df-q-{nome_formatado}.html"
    
    driver.get(url)
    time.sleep(random.uniform(3, 6)) # Espera aleatória para parecer humano

    try:
        # Tenta pegar os cards de resultado
        # ATENÇÃO: Essas classes (sc-...) mudam sempre. Se der erro, teremos que atualizar.
        # Estamos procurando cards genéricos.
        
        # Tentativa de pegar o PREÇO do primeiro imóvel da lista
        # Geralmente é um h3 ou span com cifrão
        cards = driver.find_elements(By.CLASS_NAME, "postingCardContent") # Nome comum no Wimoveis (pode ter mudado)
        
        if not cards:
            # Tenta outro seletor genérico se o site mudou
            cards = driver.find_elements(By.CSS_SELECTOR, "div[data-qa='posting DATA']")
        
        if len(cards) > 0:
            print(f"   --> Encontrei {len(cards)} anúncios. Pegando média dos 3 primeiros...")
            
            soma_preco = 0
            soma_area = 0
            count = 0
            
            for i in range(min(3, len(cards))):
                texto_card = cards[i].text
                
                # Procura preço no texto do card
                try:
                    # Regex busca R$ seguido de números
                    preco_match = re.search(r'R\$\s*([\d\.]+)', texto_card)
                    area_match = re.search(r'(\d+)\s*m²', texto_card)
                    
                    if preco_match:
                        p = extrair_numeros(preco_match.group(1))
                        if p > 100000: # Filtro para evitar aluguel ou erro
                            soma_preco += p
                            count += 1
                            
                            # Tenta pegar área também
                            if area_match:
                                soma_area += int(area_match.group(1))
                except:
                    pass

            if count > 0:
                media_preco = soma_preco / count
                media_area = soma_area / count if soma_area > 0 else 0
                return media_preco, media_area
            
    except Exception as e:
        print(f"   Erro ao ler página: {e}")

    return None, None

# --- FLUXO PRINCIPAL ---
print("🚀 Iniciando o Robô de Preços...")
df = pd.read_csv(ARQUIVO_ENTRADA)

# Cria colunas novas se não existirem
if 'Preco_Medio' not in df.columns:
    df['Preco_Medio'] = 0.0
    df['Area_Media'] = 0.0

driver = configurar_driver()

try:
    # Vamos rodar apenas nos primeiros 5 para teste! Depois tiramos o limite.
    total = len(df)
    
    for index, row in df.iterrows():
        predio = row['Nome_Predio']
        
        # Pula se já tiver preço (caso rode de novo)
        if row['Preco_Medio'] > 0:
            continue

        print(f"[{index+1}/{total}] Buscando: {predio}...")
        
        preco, area = buscar_dados_predio(driver, predio)
        
        if preco:
            df.at[index, 'Preco_Medio'] = preco
            df.at[index, 'Area_Media'] = area
            print(f"   ✅ Preço Médio: R$ {preco:,.2f} | Área: {area} m²")
        else:
            print("   ❌ Não encontrado ou sem anúncios.")
        
        # Salva a cada 10 buscas para não perder nada se travar
        if index % 10 == 0:
            df.to_csv(ARQUIVO_SAIDA, index=False)

except KeyboardInterrupt:
    print("\n🛑 Interrompido pelo usuário. Salvando...")

finally:
    df.to_csv(ARQUIVO_SAIDA, index=False)
    driver.quit()
    print("💾 Arquivo final salvo!")