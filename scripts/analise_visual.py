import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuração visual
sns.set_theme(style="whitegrid")
ARQUIVO_DADOS = "data/dataset_aguas_claras_completo.csv"
PASTA_IMAGENS = "analise_imagens"

# Cria pasta para salvar os gráficos
if not os.path.exists(PASTA_IMAGENS):
    os.makedirs(PASTA_IMAGENS)

print("🎨 Iniciando Geração de Gráficos...")

# 1. Carrega os Dados
df = pd.read_csv(ARQUIVO_DADOS)

# --- GRÁFICO 1: O Mapa de Calor (Onde é mais caro?) ---
plt.figure(figsize=(10, 8))
plt.title("Mapa de Preços: Quanto mais vermelho, mais caro o m²", fontsize=14)
sns.scatterplot(
    data=df, x="Longitude", y="Latitude", 
    hue="Preco_m2", size="Preco_m2",
    palette="RdYlGn_r", sizes=(20, 200), alpha=0.7
)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(title="Preço m²")
plt.savefig(f"{PASTA_IMAGENS}/1_mapa_calor_precos.png")
print("✅ Gráfico 1 salvo: Mapa de Calor.")

# --- GRÁFICO 2: Relação Metrô vs Preço (CORRIGIDO) ---
# Filtra apenas imóveis com distância menor que 5km para tirar erros
df_limpo = df[df['Distancia_Metro_km'] < 5]

plt.figure(figsize=(10, 6))
plt.title("Impacto do Metrô no Preço (Dados Limpos)", fontsize=14)

# Desenha a linha de tendência
sns.regplot(
    data=df_limpo, 
    x="Distancia_Metro_km", 
    y="Preco_m2", 
    scatter_kws={'alpha':0.5, 's': 20}, # Pontos menores e transparentes
    line_kws={'color':'red'}
)

plt.xlabel("Distância do Metrô (km)")
plt.ylabel("Preço por Metro Quadrado (R$)")
plt.grid(True, linestyle='--', alpha=0.6) # Adiciona grade para facilitar leitura
plt.savefig(f"{PASTA_IMAGENS}/2_metro_vs_preco_v2.png")
print("✅ Gráfico 2 salvo: Regressão Metrô (Corrigido).")

# --- GRÁFICO 3: Distribuição de Condomínio ---
plt.figure(figsize=(10, 6))
plt.title("Distribuição dos Valores de Condomínio", fontsize=14)
sns.histplot(data=df, x="Valor_Condominio", bins=30, kde=True, color="purple")
plt.xlabel("Valor do Condomínio (R$)")
plt.ylabel("Quantidade de Imóveis")
plt.savefig(f"{PASTA_IMAGENS}/3_distribuicao_condominio.png")
print("✅ Gráfico 3 salvo: Histograma.")

print(f"\n✨ FIM! Verifique a pasta '{PASTA_IMAGENS}' para ver as imagens.")