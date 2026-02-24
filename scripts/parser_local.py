import pandas as pd
from bs4 import BeautifulSoup
import re
import os
import glob

# --- CONFIGURAÇÃO ---
PASTA_DATA = "data"
ARQUIVO_SAIDA = "data/dataset_dados_reais_amostra.csv"

def extrair_numeros(texto):
    if not texto: return 0
    # Remove pontos de milhar e pega apenas dígitos
    nums = re.findall(r'\d+', texto.replace('.', ''))
    if nums:
        return int(nums[0])
    return 0

print(f"📂 Procurando arquivos HTML na pasta '{PASTA_DATA}'...")

arquivos_html = glob.glob(os.path.join(PASTA_DATA, "*.html"))

if not arquivos_html:
    print("❌ Nenhum arquivo HTML encontrado!")
    exit()

dados_totais = []

for arquivo in arquivos_html:
    print(f"   📖 Lendo: {os.path.basename(arquivo)}...")
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        # Busca genérica de cards de imóveis
        cards = soup.find_all('div', attrs={'data-qa': 'posting PROPERTY'}) 
        if not cards: cards = soup.find_all('div', attrs={'data-type': 'listing'})
        
        for card in cards:
            try:
                texto = card.get_text(" | ", strip=True)
                
                # 1. Extrair Preço de Venda (O mais importante)
                preco = 0
                match_preco = re.search(r'(?:R\$|BRL)\s*([\d\.]+)', texto)
                if match_preco:
                    preco = extrair_numeros(match_preco.group(1))
                
                # 2. Extrair Área
                area = 0
                match_area = re.search(r'(\d+)\s*m²', texto)
                if match_area:
                    area = int(match_area.group(1))
                
                # 3. Extrair Quartos
                quartos = 0
                match_quartos = re.search(r'(\d+)\s*quarto', texto)
                if match_quartos:
                    quartos = int(match_quartos.group(1))

                # Filtro de Qualidade: Só aceita se tiver Preço e Área válidos
                if preco > 150000 and area > 18:
                    dados_totais.append({
                        'Preco_Venda': preco,
                        'Area_Util': area,
                        'Quartos': quartos,
                        'Preco_m2': round(preco/area, 2)
                    })
            except:
                continue
        
    except Exception as e:
        print(f"      ⚠️ Erro ao ler arquivo: {e}")

# Consolidação Final
if dados_totais:
    df = pd.DataFrame(dados_totais)
    
    # Remove outliers (preços muito absurdos para cima ou para baixo)
    q_low = df["Preco_m2"].quantile(0.05)
    q_high = df["Preco_m2"].quantile(0.95)
    df = df[(df["Preco_m2"] < q_high) & (df["Preco_m2"] > q_low)]
    
    media_venda = df['Preco_m2'].mean()
    
    print("\n" + "="*40)
    print("📊 DADOS REAIS EXTRAÍDOS (LIMPO)")
    print("="*40)
    print(f"Amostras Válidas: {len(df)}")
    print("-" * 30)
    print(f"💰 Média de Mercado (m²): R$ {media_venda:,.2f}")
    print("="*40)
    print(f"💾 Salvo em: {ARQUIVO_SAIDA}")
    
    df.to_csv(ARQUIVO_SAIDA, index=False)
else:
    print("\n❌ Não consegui extrair dados válidos.")