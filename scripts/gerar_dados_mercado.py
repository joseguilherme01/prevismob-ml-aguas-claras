import pandas as pd
import random
import os

# --- 1. PARÂMETROS BASEADOS NA REALIDADE ---
# Valor que você minerou dos anúncios reais (Média Venda/m²)
PRECO_VENDA_BASE_M2 = 8259.51   

# Valor médio de mercado para Condomínio em Águas Claras (R$/m²)
# Isso gera condomínios entre R$ 400 (kitnet) e R$ 1.200 (4 quartos)
TAXA_CONDOMINIO_M2 = 8.50       

# --- 2. FATORES DE VALORIZAÇÃO ---
FATOR_METRO = 1.15      # Imóveis perto do metrô valem 15% mais
DISTANCIA_VIP = 0.6     # 600 metros é considerado "perto"

# --- ARQUIVOS ---
# Certifique-se que o nome do arquivo de entrada está correto
ARQUIVO_ENTRADA = "data/dataset_aguas_claras_features.csv"
ARQUIVO_SAIDA = "data/dataset_aguas_claras_completo.csv"

print("🏗️  Iniciando a Geração do Dataset Final...")

if not os.path.exists(ARQUIVO_ENTRADA):
    print(f"❌ Erro: Não encontrei o arquivo de entrada: {ARQUIVO_ENTRADA}")
    print("   Verifique se você rodou o 'google_maps_collector.py' antes.")
    exit()

try:
    df = pd.read_csv(ARQUIVO_ENTRADA)
    print(f"📊  Lendo dados de {len(df)} empreendimentos...")

    # Listas para guardar os dados gerados
    areas = []
    quartos_lista = []
    vagas_lista = []
    precos_venda = []
    precos_condo = []

    for index, row in df.iterrows():
        # --- A. Definir Tamanho e Perfil do Imóvel ---
        # Probabilidades baseadas no perfil de Águas Claras
        # 30% Pequenos, 45% Médios, 25% Grandes
        tipo = random.choices(['P', 'M', 'G'], weights=[30, 45, 25])[0]
        
        if tipo == 'P': # Pequeno (1 quarto/studio)
            area = random.randint(32, 55)
            quartos = 1
            vagas = 1
        elif tipo == 'M': # Médio (2 e 3 quartos)
            area = random.randint(56, 105)
            quartos = random.choice([2, 3])
            vagas = random.choice([1, 2])
        else: # Grande (Alto padrão)
            area = random.randint(106, 220)
            quartos = random.choice([3, 4])
            vagas = random.choice([2, 3, 4])
            
        # --- B. Calcular Preço de Venda ---
        valor_m2_venda = PRECO_VENDA_BASE_M2
        
        # Valoriza se for perto do metrô (< 600m)
        # Verifica se a coluna existe, senão usa padrão
        distancia = row.get('Distancia_Metro_km', 1.0) 
        if distancia < DISTANCIA_VIP:
            valor_m2_venda *= FATOR_METRO
            
        # Variação natural de mercado (+/- 10%)
        # (Estado de conservação, andar, vista livre, nascente/poente)
        variacao = random.uniform(0.90, 1.10)
        valor_m2_final = valor_m2_venda * variacao
        
        # Calcula preço final e arredonda para parecer anúncio (ex: 455.000)
        preco_final = area * valor_m2_final
        preco_final = round(preco_final / 1000) * 1000
        
        # --- C. Calcular Condomínio ---
        # A taxa base é R$ 8.50, mas varia de prédio para prédio (R$ 7 a R$ 11)
        taxa_random = random.uniform(TAXA_CONDOMINIO_M2 - 1.5, TAXA_CONDOMINIO_M2 + 1.5)
        
        # Prédios mais caros tendem a ter condomínio mais caro (lazer completo)
        if valor_m2_final > PRECO_VENDA_BASE_M2:
            taxa_random += 1.0
            
        valor_condominio = area * taxa_random
        valor_condominio = round(valor_condominio / 10) * 10 # Arredonda (ex: R$ 560,00)
        
        # Salva nas listas
        areas.append(area)
        quartos_lista.append(quartos)
        vagas_lista.append(vagas)
        precos_venda.append(int(preco_final))
        precos_condo.append(int(valor_condominio))

    # --- Consolidação ---
    df['Preco_Venda'] = precos_venda
    df['Valor_Condominio'] = precos_condo
    df['Area_Util'] = areas
    df['Quartos'] = quartos_lista
    df['Vagas'] = vagas_lista

    # Métricas calculadas para referência
    df['Preco_m2'] = round(df['Preco_Venda'] / df['Area_Util'], 2)
    df['Condominio_m2'] = round(df['Valor_Condominio'] / df['Area_Util'], 2)

    # Organiza as colunas numa ordem lógica
    # Organiza as colunas numa ordem lógica
    colunas_desejadas = [
        'Nome_Predio', 'Preco_Venda', 'Valor_Condominio', 'Area_Util', 
        'Preco_m2', 'Condominio_m2', 'Quartos', 'Vagas', 
        'Distancia_Metro_km', 'Mercados_500m', 'Escolas_1000m', 'Parques_800m',
        'Latitude', 'Longitude'
    ]
    
    # Filtra apenas as colunas que realmente existem no DataFrame
    colunas_finais = [c for c in colunas_desejadas if c in df.columns]
    df_final = df[colunas_finais]

    # Salva o arquivo final
    df_final.to_csv(ARQUIVO_SAIDA, index=False)

    print("\n✅ DATASET COMPLETO GERADO COM SUCESSO!")
    print("="*50)
    print(f"📁 Arquivo salvo em: {ARQUIVO_SAIDA}")
    print("-" * 30)
    print("📊 Estatísticas do Dataset Gerado:")
    print(f"   💰 Preço Médio de Venda: R$ {df_final['Preco_Venda'].mean():,.2f}")
    print(f"   🏢 Condomínio Médio:     R$ {df_final['Valor_Condominio'].mean():,.2f}")
    print(f"   📏 Tamanho Médio:        {df_final['Area_Util'].mean():.0f} m²")
    print("="*50)

except Exception as e:
    print(f"\n❌ Ocorreu um erro: {e}")
    print("Dica: Verifique se o arquivo 'dataset_aguas_claras_features.csv' existe na pasta data.")